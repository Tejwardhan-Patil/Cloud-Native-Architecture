import boto3
import json
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet
import os
import logging

class SecretsManager:
    def __init__(self, secret_name, region_name="us-east-1"):
        self.secret_name = secret_name
        self.region_name = region_name
        self.client = boto3.client('secretsmanager', region_name=self.region_name)
        self.logger = logging.getLogger('SecretsManager')
        self.logger.setLevel(logging.INFO)

    def get_secret(self):
        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)
            if 'SecretString' in response:
                secret = response['SecretString']
            else:
                secret = base64.b64decode(response['SecretBinary'])
            return json.loads(secret)
        except ClientError as e:
            self.logger.error(f"Error retrieving secret: {e}")
            raise e

    def put_secret(self, secret_value):
        try:
            self.client.put_secret_value(
                SecretId=self.secret_name,
                SecretString=json.dumps(secret_value)
            )
            self.logger.info(f"Secret {self.secret_name} stored successfully.")
        except ClientError as e:
            self.logger.error(f"Error storing secret: {e}")
            raise e

class LocalSecretsManager:
    def __init__(self, encryption_key=None, secrets_file="secrets.json"):
        self.encryption_key = encryption_key or os.getenv("SECRET_ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("Encryption key must be provided.")
        self.secrets_file = secrets_file
        self.cipher = Fernet(self.encryption_key.encode())
        self.logger = logging.getLogger('LocalSecretsManager')
        self.logger.setLevel(logging.INFO)

    def encrypt_secret(self, secret):
        try:
            encrypted_secret = self.cipher.encrypt(secret.encode())
            self.logger.info(f"Secret encrypted successfully.")
            return encrypted_secret
        except Exception as e:
            self.logger.error(f"Error encrypting secret: {e}")
            raise e

    def decrypt_secret(self, encrypted_secret):
        try:
            decrypted_secret = self.cipher.decrypt(encrypted_secret).decode()
            self.logger.info(f"Secret decrypted successfully.")
            return decrypted_secret
        except Exception as e:
            self.logger.error(f"Error decrypting secret: {e}")
            raise e

    def store_secret(self, secret_name, secret_value):
        try:
            secrets = self.load_secrets()
            secrets[secret_name] = self.encrypt_secret(secret_value).decode()
            with open(self.secrets_file, 'w') as f:
                json.dump(secrets, f)
            self.logger.info(f"Secret {secret_name} stored successfully.")
        except Exception as e:
            self.logger.error(f"Error storing secret: {e}")
            raise e

    def retrieve_secret(self, secret_name):
        try:
            secrets = self.load_secrets()
            encrypted_secret = secrets.get(secret_name)
            if not encrypted_secret:
                raise ValueError(f"Secret {secret_name} not found.")
            return self.decrypt_secret(encrypted_secret.encode())
        except Exception as e:
            self.logger.error(f"Error retrieving secret: {e}")
            raise e

    def load_secrets(self):
        try:
            if os.path.exists(self.secrets_file):
                with open(self.secrets_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading secrets: {e}")
            raise e

# Encryption Utilities
class EncryptionUtils:
    def __init__(self, key=None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.logger = logging.getLogger('EncryptionUtils')
        self.logger.setLevel(logging.INFO)

    def encrypt(self, data):
        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            self.logger.info(f"Data encrypted successfully.")
            return encrypted_data
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            raise e

    def decrypt(self, encrypted_data):
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data).decode()
            self.logger.info(f"Data decrypted successfully.")
            return decrypted_data
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            raise e

# Rotating Secrets
class SecretRotator:
    def __init__(self, secret_manager, encryption_utils):
        self.secret_manager = secret_manager
        self.encryption_utils = encryption_utils
        self.logger = logging.getLogger('SecretRotator')
        self.logger.setLevel(logging.INFO)

    def rotate_secret(self, secret_name):
        try:
            # Retrieve the current secret
            old_secret = self.secret_manager.get_secret(secret_name)

            # Generate a new encrypted secret
            new_secret = self.encryption_utils.encrypt(old_secret['password'])

            # Update the secret in the secret manager
            self.secret_manager.put_secret(secret_name, {"password": new_secret})

            self.logger.info(f"Secret for {secret_name} rotated successfully.")
        except Exception as e:
            self.logger.error(f"Error rotating secret: {e}")
            raise e

# AWS KMS Integration
class KMSIntegration:
    def __init__(self, key_id):
        self.client = boto3.client('kms')
        self.key_id = key_id
        self.logger = logging.getLogger('KMSIntegration')
        self.logger.setLevel(logging.INFO)

    def encrypt_with_kms(self, plaintext):
        try:
            response = self.client.encrypt(KeyId=self.key_id, Plaintext=plaintext)
            ciphertext = response['CiphertextBlob']
            self.logger.info(f"Data encrypted using KMS.")
            return ciphertext
        except ClientError as e:
            self.logger.error(f"Error encrypting data with KMS: {e}")
            raise e

    def decrypt_with_kms(self, ciphertext):
        try:
            response = self.client.decrypt(CiphertextBlob=ciphertext)
            plaintext = response['Plaintext']
            self.logger.info(f"Data decrypted using KMS.")
            return plaintext
        except ClientError as e:
            self.logger.error(f"Error decrypting data with KMS: {e}")
            raise e

# Main Execution
if __name__ == "__main__":
    # Initialize Managers
    secret_manager = SecretsManager(secret_name="dbCredentials")
    local_secret_manager = LocalSecretsManager(encryption_key="SOME_KEY_HERE")
    encryption_utils = EncryptionUtils()
    kms_integration = KMSIntegration(key_id="KMS_KEY_ID")

    # Rotate Secret
    secret_rotator = SecretRotator(secret_manager, encryption_utils)
    secret_rotator.rotate_secret("dbCredentials")