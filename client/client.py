import socket
import json
import threading
import platform
from encryption import AESHandler
from tun_handler import TUNHandler

# Load client configuration
with open("./config.json", "r") as config_file:
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
        self.tun = self.create_tun_handler()  # TUN device handler
        self.cleaned_up = False  # Flag to track cleanup

    def create_tun_handler(self):
        """Creates and configures the TUN/TAP device handler based on the OS"""
        if platform.system() == "Windows":
            return TUNHandler(dev_name="tap1")  # Use TAP device for Windows
        else:
            return TUNHandler(dev_name="tun1")  # Use TUN device for Linux

    def connect_to_server(self):
        """Connects to the server and handles errors in connection"""
        try:
            self.sock.connect(self.server_address)
            print(f"Connected to server at {self.server_address}")
        except socket.error as e:
            print(f"Error connecting to server: {e}")
            self.cleanup()

    def handle_server(self):
        """Handles communication with the server"""
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    print("No data received from server, closing connection")
                    break
                decrypted_data = self.aes_handler.decrypt(data)
                self.tun.write(decrypted_data)
                response = self.tun.read()
                encrypted_response = self.aes_handler.encrypt(response)
                self.sock.sendall(encrypted_response)
        except Exception as e:
            print(f"Error handling server: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleans up resources"""
        if not self.cleaned_up:
            self.sock.close()
            self.tun.close()
            self.cleaned_up = True
            print("Cleaned up resources")

    def run(self):
        """Main method to run the VPN client"""
        self.connect_to_server()
        self.handle_server()

if __name__ == "__main__":
    client = VPNClient()
    client.run()