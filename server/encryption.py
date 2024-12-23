from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

class AESHandler:
    def __init__(self, key):
        self.key = key.encode()  # Ensure the key is in bytes
        if len(self.key) not in [16, 24, 32]:
            raise ValueError(f"Invalid key size: {len(self.key)}. Key must be 16, 24, or 32 bytes long.")
        self.backend = default_backend()

    def encrypt(self, data):
        try:
            iv = os.urandom(16)  # Generate a random 16-byte IV
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            return iv + encrypted_data  # Concatenate IV and encrypted data for transmission
        except Exception as e:
            print(f"Error during encryption: {e}")
            return None

    def decrypt(self, encrypted_data):
        try:
            iv = encrypted_data[:16]  # First 16 bytes are the IV
            encrypted_data = encrypted_data[16:]  # The rest is the encrypted data
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(decrypted_data) + unpadder.finalize()
            return data
        except ValueError as e:
            print(f"Decryption error (possibly invalid padding): {e}")
            return None
        except Exception as e:
            print(f"Error during decryption: {e}")
            return None
