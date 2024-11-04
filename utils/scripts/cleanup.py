import os
import shutil
import logging
import boto3
from botocore.exceptions import ClientError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# AWS S3 Cleanup class for cloud resources
class S3Cleaner:
    def __init__(self, bucket_name):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

    def empty_bucket(self):
        logging.info(f'Starting cleanup for S3 bucket: {self.bucket_name}')
        try:
            objects = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in objects:
                for obj in objects['Contents']:
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
                    logging.info(f'Deleted {obj["Key"]} from {self.bucket_name}')
            else:
                logging.info(f'No objects found in bucket: {self.bucket_name}')
        except ClientError as e:
            logging.error(f'Error during S3 bucket cleanup: {e}')

    def delete_bucket(self):
        try:
            self.s3_client.delete_bucket(Bucket=self.bucket_name)
            logging.info(f'Successfully deleted S3 bucket: {self.bucket_name}')
        except ClientError as e:
            logging.error(f'Failed to delete bucket {self.bucket_name}: {e}')

# Local file system cleanup class
class LocalCleaner:
    def __init__(self, paths):
        self.paths = paths

    def remove_files(self):
        for path in self.paths:
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    logging.info(f'Deleted file: {path}')
                except OSError as e:
                    logging.error(f'Error deleting file {path}: {e}')
            else:
                logging.warning(f'{path} is not a file')

    def remove_directories(self):
        for path in self.paths:
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                    logging.info(f'Deleted directory: {path}')
                except OSError as e:
                    logging.error(f'Error deleting directory {path}: {e}')
            else:
                logging.warning(f'{path} is not a directory')

# Docker container cleanup
class DockerCleaner:
    def __init__(self):
        self.client = None
        try:
            import docker
            self.client = docker.from_env()
            logging.info('Docker client initialized')
        except ImportError:
            logging.error('Docker SDK for Python is not installed. Skipping Docker cleanup.')

    def stop_containers(self):
        if self.client:
            containers = self.client.containers.list()
            for container in containers:
                container.stop()
                logging.info(f'Stopped container: {container.name}')

    def remove_containers(self):
        if self.client:
            containers = self.client.containers.list(all=True)
            for container in containers:
                container.remove(force=True)
                logging.info(f'Removed container: {container.name}')

    def remove_images(self):
        if self.client:
            images = self.client.images.list()
            for image in images:
                try:
                    self.client.images.remove(image.id, force=True)
                    logging.info(f'Removed image: {image.id}')
                except Exception as e:
                    logging.error(f'Failed to remove image {image.id}: {e}')

# Kubernetes resources cleanup
class K8sCleaner:
    def __init__(self, namespace=None):
        try:
            from kubernetes import client, config
            config.load_kube_config()
            self.v1 = client.CoreV1Api()
            self.namespace = namespace if namespace else 'default'
            logging.info(f'Kubernetes client initialized for namespace: {self.namespace}')
        except ImportError:
            logging.error('Kubernetes Python client is not installed. Skipping K8s cleanup.')

    def delete_pods(self):
        if self.v1:
            pods = self.v1.list_namespaced_pod(self.namespace)
            for pod in pods.items:
                self.v1.delete_namespaced_pod(pod.metadata.name, self.namespace)
                logging.info(f'Deleted pod: {pod.metadata.name}')

    def delete_services(self):
        if self.v1:
            services = self.v1.list_namespaced_service(self.namespace)
            for svc in services.items:
                self.v1.delete_namespaced_service(svc.metadata.name, self.namespace)
                logging.info(f'Deleted service: {svc.metadata.name}')

# Main Cleanup Runner
class CleanupRunner:
    def __init__(self, local_paths, s3_buckets, docker_cleanup=False, k8s_cleanup=False):
        self.local_cleaner = LocalCleaner(local_paths)
        self.s3_cleaners = [S3Cleaner(bucket) for bucket in s3_buckets]
        self.docker_cleaner = DockerCleaner() if docker_cleanup else None
        self.k8s_cleaner = K8sCleaner() if k8s_cleanup else None

    def run(self):
        logging.info('Starting cleanup process...')

        # Clean local files and directories
        logging.info('Cleaning local file system...')
        self.local_cleaner.remove_files()
        self.local_cleaner.remove_directories()

        # Clean up S3 buckets
        logging.info('Cleaning S3 buckets...')
        for s3_cleaner in self.s3_cleaners:
            s3_cleaner.empty_bucket()
            s3_cleaner.delete_bucket()

        # Clean up Docker containers and images
        if self.docker_cleaner:
            logging.info('Cleaning Docker resources...')
            self.docker_cleaner.stop_containers()
            self.docker_cleaner.remove_containers()
            self.docker_cleaner.remove_images()

        # Clean up Kubernetes resources
        if self.k8s_cleaner:
            logging.info('Cleaning Kubernetes resources...')
            self.k8s_cleaner.delete_pods()
            self.k8s_cleaner.delete_services()

        logging.info('Cleanup process completed.')

if __name__ == '__main__':
    # Define resources to clean
    local_paths = ['/tmp/temp_file.txt', '/var/log/temp_logs/']
    s3_buckets = ['bucket-1', 'bucket-2']

    # Initialize Cleanup Runner
    runner = CleanupRunner(local_paths=local_paths, s3_buckets=s3_buckets, docker_cleanup=True, k8s_cleanup=True)

    # Run the cleanup process
    runner.run()