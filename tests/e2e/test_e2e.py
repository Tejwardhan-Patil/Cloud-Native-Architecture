import requests
import time
import unittest
from kubernetes import client, config

class TestE2E(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load Kubernetes configuration
        config.load_kube_config()
        cls.api_instance = client.CoreV1Api()

        # Set base URLs for microservices
        cls.service_a_url = "http://service-a.website.com/api"
        cls.service_b_url = "http://service-b.website.com/api"
        cls.api_gateway_url = "http://api-gateway.website.com"

        # Wait for services to be ready
        cls.wait_for_service(cls.service_a_url)
        cls.wait_for_service(cls.service_b_url)
        cls.wait_for_service(cls.api_gateway_url)

    @staticmethod
    def wait_for_service(url, retries=10, delay=5):
        """Wait until a service becomes available."""
        for _ in range(retries):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(delay)
        raise Exception(f"Service at {url} not ready")

    def test_service_a_health(self):
        """Test the health endpoint of Service A"""
        response = requests.get(f"{self.service_a_url}/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "healthy")

    def test_service_b_health(self):
        """Test the health endpoint of Service B"""
        response = requests.get(f"{self.service_b_url}/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "healthy")

    def test_api_gateway_routing(self):
        """Test routing via API Gateway"""
        response = requests.get(f"{self.api_gateway_url}/route_to_service_a")
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())

        response = requests.get(f"{self.api_gateway_url}/route_to_service_b")
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())

    def test_data_flow_between_services(self):
        """Test interaction and data flow between Service A and B through API Gateway"""
        # Step 1: Post data to Service A via API Gateway
        post_data = {"input": "test_data"}
        response = requests.post(f"{self.api_gateway_url}/service_a/process", json=post_data)
        self.assertEqual(response.status_code, 200)
        processed_data = response.json().get("processed_data")
        self.assertIsNotNone(processed_data)

        # Step 2: Pass the processed data from Service A to Service B
        response = requests.post(f"{self.api_gateway_url}/service_b/consume", json={"data": processed_data})
        self.assertEqual(response.status_code, 200)
        result = response.json().get("result")
        self.assertEqual(result, "success")

    def test_service_a_database_connection(self):
        """Test Service A database connection"""
        response = requests.get(f"{self.service_a_url}/database_status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("db_status"), "connected")

    def test_service_b_external_api(self):
        """Test Service B interaction with an external API"""
        response = requests.get(f"{self.service_b_url}/external_api_status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("external_api"), "reachable")

    def test_kubernetes_pods_running(self):
        """Test if all Kubernetes pods are running in the namespace"""
        pods = self.api_instance.list_namespaced_pod(namespace="default")
        for pod in pods.items:
            self.assertEqual(pod.status.phase, "Running")

    def test_service_scaling(self):
        """Test if Service A scales based on traffic"""
        # Simulate load on Service A
        for _ in range(100):
            response = requests.get(f"{self.api_gateway_url}/service_a/health")
            self.assertEqual(response.status_code, 200)

        # Check the number of pods for Service A
        pods = self.api_instance.list_namespaced_pod(namespace="default")
        service_a_pods = [pod for pod in pods.items if "service-a" in pod.metadata.name]
        self.assertGreaterEqual(len(service_a_pods), 3)

    def test_observability_metrics(self):
        """Test if Prometheus metrics are available for services"""
        prometheus_url = "http://prometheus.website.com/api/v1/query"
        query = {"query": "up"}
        response = requests.get(prometheus_url, params=query)
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())

    def test_alert_manager_integration(self):
        """Test if Prometheus AlertManager integration is working"""
        alertmanager_url = "http://alertmanager.website.com/api/v1/alerts"
        response = requests.get(alertmanager_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())

    def test_service_a_logs(self):
        """Test if logs for Service A are retrievable"""
        logs = self.api_instance.read_namespaced_pod_log(
            name="service-a-pod", namespace="default"
        )
        self.assertIn("INFO", logs)

    def test_service_b_logs(self):
        """Test if logs for Service B are retrievable"""
        logs = self.api_instance.read_namespaced_pod_log(
            name="service-b-pod", namespace="default"
        )
        self.assertIn("INFO", logs)

    @classmethod
    def tearDownClass(cls):
        # Clean up operations
        print("End-to-end tests completed.")

if __name__ == '__main__':
    unittest.main()