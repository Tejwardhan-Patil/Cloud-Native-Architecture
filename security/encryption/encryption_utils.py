from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import utils
import os

class EncryptionUtils:
    def __init__(self, key_size=32):
        self.key_size = key_size

    def generate_symmetric_key(self):
        return os.urandom(self.key_size)

    def encrypt_data(self, key, plaintext):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return iv, ciphertext

    def decrypt_data(self, key, iv, ciphertext):
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    def generate_hmac(self, key, data):
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data)
        return h.finalize()

    def verify_hmac(self, key, data, hmac_value):
        h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(data)
        h.verify(hmac_value)

    def derive_key_pbkdf2(self, password, salt, iterations=100000):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_size,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password)

    def derive_key_scrypt(self, password, salt):
        kdf = Scrypt(
            salt=salt,
            length=self.key_size,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
        )
        return kdf.derive(password)

    def generate_rsa_key_pair(self, key_size=2048):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key

    def serialize_private_key(self, private_key, password=None):
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password)
        else:
            encryption_algorithm = serialization.NoEncryption()
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )

    def serialize_public_key(self, public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def load_private_key(self, pem_data, password=None):
        return serialization.load_pem_private_key(
            pem_data, password=password, backend=default_backend()
        )

    def load_public_key(self, pem_data):
        return serialization.load_pem_public_key(pem_data, backend=default_backend())

    def rsa_encrypt(self, public_key, plaintext):
        return public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def rsa_decrypt(self, private_key, ciphertext):
        return private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def sign_data(self, private_key, data):
        return private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256())
        )

    def verify_signature(self, public_key, data, signature):
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256())
        )

    def encrypt_with_rsa_aes_hybrid(self, public_key, plaintext):
        aes_key = self.generate_symmetric_key()
        iv, ciphertext = self.encrypt_data(aes_key, plaintext)
        encrypted_key = self.rsa_encrypt(public_key, aes_key)
        return encrypted_key, iv, ciphertext

    def decrypt_with_rsa_aes_hybrid(self, private_key, encrypted_key, iv, ciphertext):
        aes_key = self.rsa_decrypt(private_key, encrypted_key)
        return self.decrypt_data(aes_key, iv, ciphertext)

# Utility functions for handling file encryption

def encrypt_file(key, file_path, output_path):
    with open(file_path, 'rb') as file:
        plaintext = file.read()
    iv, ciphertext = EncryptionUtils().encrypt_data(key, plaintext)
    with open(output_path, 'wb') as encrypted_file:
        encrypted_file.write(iv + ciphertext)

def decrypt_file(key, encrypted_file_path, output_path):
    with open(encrypted_file_path, 'rb') as encrypted_file:
        iv = encrypted_file.read(16)
        ciphertext = encrypted_file.read()
    plaintext = EncryptionUtils().decrypt_data(key, iv, ciphertext)
    with open(output_path, 'wb') as decrypted_file:
        decrypted_file.write(plaintext)

# RSA key pair generation and usage
if __name__ == "__main__":
    encryption_util = EncryptionUtils()

    # Generate RSA key pair
    private_key, public_key = encryption_util.generate_rsa_key_pair()

    # Serialize keys
    private_pem = encryption_util.serialize_private_key(private_key)
    public_pem = encryption_util.serialize_public_key(public_key)

    # Save serialized keys to files
    with open('private_key.pem', 'wb') as private_file:
        private_file.write(private_pem)

    with open('public_key.pem', 'wb') as public_file:
        public_file.write(public_pem)

    # Encryption and decryption with hybrid RSA-AES
    message = b"Confidential message for encryption"
    encrypted_key, iv, encrypted_message = encryption_util.encrypt_with_rsa_aes_hybrid(public_key, message)
    decrypted_message = encryption_util.decrypt_with_rsa_aes_hybrid(private_key, encrypted_key, iv, encrypted_message)

    print(f"Original Message: {message}")
    print(f"Decrypted Message: {decrypted_message}")