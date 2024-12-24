import socket
import threading
import json
import signal
import sys
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
        self.aes_handler = AESHandler(ENCRYPTION_KEY)
        self.tun = TUNHandler(dev_name="tun0")  # The TUN device name

    def accept_client(self):
        print("Waiting for client connection...")
        client_sock, client_address = self.sock.accept()
        print(f"Connection established with {client_address}")
        return client_sock

    def handle_client_traffic(self, client_sock):
        try:
            while True:
                encrypted_data = client_sock.recv(4096)
                if not encrypted_data:
                    print("Client disconnected")
                    break

                # Decrypt the received data from the client
                decrypted_data = self.aes_handler.decrypt(encrypted_data)
                if decrypted_data is None:
                    print("Failed to decrypt data")
                    break

                # Write decrypted data to TUN interface
                self.tun.write(decrypted_data)
        except Exception as e:
            print(f"Error receiving data from client: {e}")
        finally:
            client_sock.close()

    def handle_tun_traffic(self, client_sock):
        try:
            while True:
                # Read data from the TUN interface
                packet = self.tun.read()
                # Encrypt the data from the TUN interface
                encrypted_packet = self.aes_handler.encrypt(packet)
                # Send the encrypted data to the client
                client_sock.send(encrypted_packet)
        except Exception as e:
            print(f"Error sending data to client: {e}")
        finally:
            client_sock.close()

    def start(self):
        self.tun.configure_tun_device(ip="10.0.0.1")  # Server IP
        print("Server started and listening for connections...")
        while True:
            try:
                client_sock = self.accept_client()

                # Start threads for handling client and TUN traffic
                client_thread = threading.Thread(target=self.handle_client_traffic, args=(client_sock,))
                tun_thread = threading.Thread(target=self.handle_tun_traffic, args=(client_sock,))

                client_thread.daemon = True
                tun_thread.daemon = True

                client_thread.start()
                tun_thread.start()
            except KeyboardInterrupt:
                print("Server shutting down...")
                self.cleanup()
                break

    def cleanup(self):
        print("Cleaning up resources...")
        self.sock.close()
        self.tun.close()

if __name__ == "__main__":
    server = VPNServer()

    # Graceful shutdown handling
    def signal_handler(sig, frame):
        print("\nShutting down server...")
        server.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    server.start()