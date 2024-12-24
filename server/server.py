import socket
import threading
import json
import signal
import sys
import platform
from encryption import AESHandler
from tun_handler import TUNHandler

# Load server configuration
with open("./config.json", "r") as config_file:
    config = json.load(config_file)

SERVER_IP = config["server_ip"]
SERVER_PORT = config["server_port"]
ENCRYPTION_KEY = config["encryption_key"]

class VPNServer:
    def __init__(self):
        self.server_address = (SERVER_IP, SERVER_PORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.bind(self.server_address)
        except OSError as e:
            print(f"Error binding to {self.server_address}: {e}")
            sys.exit(1)
        self.sock.listen(5)
        self.aes_handler = AESHandler(ENCRYPTION_KEY)  # AES encryption handler
        self.tun = self.create_tun_handler()  # TUN device handler
        self.cleaned_up = False  # Flag to track cleanup

    def create_tun_handler(self):
        """Creates and configures the TUN/TAP device handler based on the OS"""
        if platform.system() == "Windows":
            return TUNHandler(dev_name="tap0")  # Use TAP device for Windows
        else:
            return TUNHandler(dev_name="tun0")  # Use TUN device for Linux

    def handle_client(self, client_socket):
        """Handles client connections"""
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    print("No data received from client, closing connection")
                    break
                decrypted_data = self.aes_handler.decrypt(data)
                self.tun.write(decrypted_data)
                response = self.tun.read()
                encrypted_response = self.aes_handler.encrypt(response)
                client_socket.sendall(encrypted_response)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def run(self):
        """Main method to run the VPN server"""
        print(f"Server listening on {self.server_address}")
        while True:
            client_socket, client_address = self.sock.accept()
            print(f"Accepted connection from {client_address}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def cleanup(self):
        """Cleans up resources"""
        if not self.cleaned_up:
            self.sock.close()
            self.tun.close()
            self.cleaned_up = True
            print("Cleaned up resources")

def signal_handler(sig, frame):
    server.cleanup()
    sys.exit(0)

if __name__ == "__main__":
    server = VPNServer()
    signal.signal(signal.SIGINT, signal_handler)
    server.run()