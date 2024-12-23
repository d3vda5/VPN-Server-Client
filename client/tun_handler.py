import os
import fcntl
import struct
import subprocess

class TUNHandler:
    TUNSETIFF = 0x400454ca
    IFF_TUN = 0x0001
    IFF_NO_PI = 0x1000

    def __init__(self, dev_name="tun1"):
        self.dev_name = dev_name
        self.tun_fd = self.create_tun_device()
        self.configure_tun_device()

    def create_tun_device(self):
        try:
            tun_fd = os.open("/dev/net/tun", os.O_RDWR)
            ifr = struct.pack("16sH", self.dev_name.encode(), self.IFF_TUN | self.IFF_NO_PI)
            fcntl.ioctl(tun_fd, self.TUNSETIFF, ifr)
            print(f"TUN device {self.dev_name} created")
            return tun_fd
        except Exception as e:
            print(f"Error creating TUN device: {e}")
            raise

    def configure_tun_device(self, ip="10.0.0.2", netmask="255.255.255.0"):
        try:
            subprocess.run(["ip", "addr", "add", f"{ip}/24", "dev", self.dev_name], check=True)
            subprocess.run(["ip", "link", "set", "dev", self.dev_name, "up"], check=True)
            print(f"TUN device {self.dev_name} configured with IP {ip}")
        except subprocess.CalledProcessError as e:
            print(f"Error configuring TUN device: {e}")
            raise

    def read(self, buffer_size=4096):
        return os.read(self.tun_fd, buffer_size)

    def write(self, data):
        os.write(self.tun_fd, data)

    def close(self):
        try:
            os.close(self.tun_fd)
            print(f"TUN device {self.dev_name} closed")
        except Exception as e:
            print(f"Error closing TUN device: {e}")