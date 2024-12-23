import socket
import json
import threading
from encryption import AESHandler
from tun_handler import TUNHandler

# Load client configuration
with open("client/config.json", "r") as config_file:
    config = json.load(config_file)

SERVER_IP = config["server_ip"]
SERVER_PORT = config["server_port"]
ENCRYPTION_KEY = config["encryption_key"]

class VPNClient:
    def __init__(self):
        self.server_address = (SERVER_IP, SERVER_PORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(100000)  # Set a socket timeout
        self.aes_handler = AESHandler(ENCRYPTION_KEY)  # AES encryption handler
        self.tun = TUNHandler()  # TUN device handler
        self.cleaned_up = False  # Flag to track cleanup

    def connect_to_server(self):
        """Connects to the server and handles errors in connection"""
        try:
            self.sock.connect(self.server_address)
            print(f"Connected to server at {self.server_address}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.cleanup()  # Perform cleanup on error
            exit(1)

    def handle_server_traffic(self):
        """Handles receiving encrypted traffic from the server, decrypts and writes to TUN device"""
        try:
            while True:
                encrypted_data = self.sock.recv(4096)
                if not encrypted_data:
                    print("Disconnected from server")
                    break
                decrypted_data = self.aes_handler.decrypt(encrypted_data)
                if decrypted_data:
                    self.tun.write(decrypted_data)  # Write decrypted data to the TUN device
        except Exception as e:
            print(f"Error receiving data from server: {e}")
        finally:
            self.cleanup()

    def handle_tun_traffic(self):
        """Handles reading traffic from the TUN device, encrypts it and sends it to the server"""
        try:
            while True:
                packet = self.tun.read()  # Read data from TUN device
                encrypted_packet = self.aes_handler.encrypt(packet)  # Encrypt data
                if encrypted_packet:
                    self.sock.send(encrypted_packet)  # Send encrypted data to server
        except Exception as e:
            print(f"Error sending data to server: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Closes resources and cleans up"""
        if self.cleaned_up:
            return  # Avoid cleaning up twice
        self.cleaned_up = True  # Set the flag to True

        try:
            if self.tun:
                self.tun.close()
            if self.sock:
                self.sock.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        print("Resources cleaned up")

    def start(self):
        """Initializes connection and starts threads for handling traffic"""
        self.connect_to_server()

        # Start threads for handling server communication and TUN traffic
        server_thread = threading.Thread(target=self.handle_server_traffic, daemon=True)
        tun_thread = threading.Thread(target=self.handle_tun_traffic, daemon=True)

        server_thread.start()
        tun_thread.start()

        server_thread.join()
        tun_thread.join()

if __name__ == "__main__":
    client = VPNClient()
    client.start()