import os
import platform
import struct
import subprocess
import ctypes
from ctypes import wintypes

if platform.system() != "Windows":
    import fcntl

class TUNHandler:
    TUNSETIFF = 0x400454ca
    IFF_TUN = 0x0001
    IFF_NO_PI = 0x1000

    def __init__(self, dev_name="tun0"):
        self.dev_name = dev_name
        self.tun_fd = None
        try:
            self.tun_fd = self.create_tun_device()
        except Exception as e:
            print(f"Error initializing TUN device: {e}")
            self.close()

    def create_tun_device(self):
        if platform.system() == "Windows":
            return self.create_tap_device_windows()
        else:
            return self.create_tun_device_linux()

    def create_tun_device_linux(self):
        try:
            tun_fd = os.open("/dev/net/tun", os.O_RDWR)
            ifr = struct.pack("16sH", self.dev_name.encode(), self.IFF_TUN | self.IFF_NO_PI)
            fcntl.ioctl(tun_fd, self.TUNSETIFF, ifr)
            print(f"TUN device {self.dev_name} created")
            return tun_fd
        except Exception as e:
            print(f"Error creating TUN device: {e}")
            raise

    def create_tap_device_windows(self):
        try:
            # Ensure you have installed the TAP driver from OpenVPN
            os.system(f'netsh interface ip set address name="{self.dev_name}" static 10.0.0.2 255.255.255.0')
            print(f"TAP device {self.dev_name} created and configured with IP 10.0.0.2")
            return None  # Windows TAP device does not use a file descriptor
        except Exception as e:
            print(f"Error creating TAP device: {e}")
            raise

    def configure_tun_device(self, ip, netmask="255.255.255.0"):
        if platform.system() == "Windows":
            self.configure_tun_device_windows(ip, netmask)
        else:
            self.configure_tun_device_linux(ip, netmask)

    def configure_tun_device_windows(self, ip, netmask):
        try:
            os.system(f'netsh interface ip set address name="{self.dev_name}" static {ip} {netmask}')
            print(f"TAP device {self.dev_name} configured with IP {ip}")
        except Exception as e:
            print(f"Error configuring TAP device: {e}")
            raise

    def configure_tun_device_linux(self, ip, netmask):
        try:
            subprocess.run(["ip", "addr", "add", f"{ip}/24", "dev", self.dev_name], check=True)
            subprocess.run(["ip", "link", "set", "dev", self.dev_name, "up"], check=True)
            print(f"TUN device {self.dev_name} configured with IP {ip}")
        except subprocess.CalledProcessError as e:
            print(f"Error configuring TUN device: {e}")
            raise

    def read(self, buffer_size=4096):
        if self.tun_fd:
            return os.read(self.tun_fd, buffer_size)
        else:
            raise NotImplementedError("Read operation is not implemented for Windows TAP device")

    def write(self, data):
        if self.tun_fd:
            os.write(self.tun_fd, data)
        else:
            raise NotImplementedError("Write operation is not implemented for Windows TAP device")

    def close(self):
        try:
            if self.tun_fd:
                os.close(self.tun_fd)
                print(f"TUN device {self.dev_name} closed")
        except Exception as e:
            print(f"Error closing TUN device: {e}")