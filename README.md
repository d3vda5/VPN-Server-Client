# 🚀 **VPN-Server-Client**

A lightweight and secure VPN implementation using Python. This project leverages TUN/TAP devices and AES encryption for secure communication in a client-server architecture.

---

## ✨ **Features**

- 🔒 **Encryption**: Uses AES (CBC mode) for secure communication.
- 🌐 **TUN/TAP Support**: Utilizes Linux TUN devices for packet forwarding.
- 🖥️ **Client-Server Architecture**: Dynamically assigns IPs to clients.
- ❤️ **Heartbeat Mechanism**: Keeps connections alive and monitors client health.
- ⚙️ **Cross-Platform Compatibility**: Designed to work on Linux environments with Python 3.8+.

---

## 📂 **Project Structure**

```plaintext
VPN-Server-Client/
├── client/
│   ├── client.py            # Main client logic
│   ├── tun_handler.py       # Manages TUN device for the client
│   ├── encryption.py        # AES encryption/decryption module
│   ├── config.json          # Client configuration
│   ├── vpn-client-setup.ps1 # PowerShell script to set up the client on Windows
│   ├── vpn-client-setup.sh  # Shell script to set up the client on Linux
├── server/
│   ├── server.py            # Main server logic
│   ├── tun_handler.py       # Manages TUN device for the server
│   ├── encryption.py        # AES encryption/decryption module
│   ├── config.json          # Server configuration
│   ├── setup-vpn-firewall.ps1 # PowerShell script to set up firewall rules on Windows
│   ├── setup-vpn-firewall.sh  # Shell script to set up firewall rules on Linux
├── requirements.txt         # Python dependencies
├── README.md                # Project overview and instructions
├── INSTALL.md               # Installation guide
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
└── .gitignore               # Files and directories to exclude from Git
```

---

## 🛠️ **Getting Started**

### **Prerequisites**

1. 🖥️ **Operating System**: Linux or Windows with TUN/TAP support.
2. 🐍 **Python**: Version 3.8 or higher.
3. ⚙️ **Required Tools**:
   - `iproute2` for managing TUN/TAP devices on Linux.
   - Build tools (`build-essential`, `libssl-dev`, `python3-dev`) for compiling dependencies on Linux.
   - OpenVPN TAP driver for Windows.

Install the system dependencies:
```bash
sudo apt update
sudo apt install -y iproute2 build-essential libssl-dev python3-dev
```

### **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/d3vda5/VPN-Server-Client.git
   cd VPN-Server-Client
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### **Configuration**

Update the `config.json` files in the `server/` and `client/` directories with your settings:

**Example `config.json` for Server:**
```json
{
    "server_ip": "0.0.0.0",
    "server_port": 1194,
    "encryption_key": "your-secure-32-byte-key-here1234"
}
```

**Example `config.json` for Client:**
```json
{
    "server_ip": "192.168.1.100",
    "server_port": 1194,
    "encryption_key": "your-secure-32-byte-key-here1234"
}
```

Make sure the `encryption_key` matches on both server and client.

---

## 🖥️ **Usage**

### **Starting the Server**

#### On Linux:
Run the server with elevated privileges (to configure the TUN device):
```bash
sudo python3 server/server.py
```

#### On Windows:
Run the server with administrator privileges:
```sh
python server/server.py
```

Monitor the logs to ensure the server is running and waiting for connections.

### **Starting the Client**

#### On Linux:
1. **Run Shell Scripts**:
   - Open a terminal.
   - Run the client setup script:
     ```bash
     sudo ./client/vpn-client-setup.sh
     ```
   - Run the firewall setup script:
     ```bash
     sudo ./server/setup-vpn-firewall.sh
     ```

2. **Start the Client**:
   - Run the client with elevated privileges:
     ```bash
     sudo python3 client/client.py
     ```

#### On Windows:
1. **Install OpenVPN TAP Driver**:
   - Download the OpenVPN TAP driver from [OpenVPN's official website](https://openvpn.net/community-downloads/).
   - Run the installer and follow the instructions to install the TAP driver.

2. **Run PowerShell Scripts**:
   - Open PowerShell as Administrator.
   - Run the client setup script:
     ```powershell
     .\client\vpn-client-setup.ps1
     ```
   - Run the firewall setup script:
     ```powershell
     .\server\setup-vpn-firewall.ps1
     ```

3. **Start the Client**:
   - Run the client with administrator privileges:
     ```sh
     python client/client.py
     ```

The client will connect to the server, receive an IP address, and establish the VPN connection.

### **Verify the Connection**
1. Check the TUN device configuration:
   ```bash
   ip addr show tun0  # Server-side on Linux
   ip addr show tun1  # Client-side on Linux
   ```
   On Windows, use:
   ```sh
   ipconfig /all
   ```

2. Use tools like `ping` or `tcpdump` to verify traffic flow.

---

### **IP Route Configuration**
The project automatically configures IP routes after connecting:

- **Server**: Runs the `setup-vpn-firewall.sh` script with `sudo` to configure routing.
- **Client**: Runs the `vpn-client-setup.sh` without `sudo` for client-specific routes.

Ensure the script is executable and located in the `scripts/` directory.


## ⚙️ **How It Works**

1. 🔒 **Encryption**: 
   - All traffic is encrypted using AES with a shared secret key.

2. 🌐 **TUN/TAP Devices**:
   - The server and client configure TUN devices for packet forwarding.
   - Packets are sent over the encrypted connection.

3. ❤️ **Heartbeat Mechanism**:
   - The client periodically sends heartbeat messages to ensure the connection is alive.
   - The server monitors heartbeats and disconnects inactive clients.

---

## 🛠️ **Troubleshooting**

### Common Issues
1. ❌ **TUN Device Not Found**:
   - Ensure `/dev/net/tun` exists and has proper permissions on Linux:
     ```bash
     sudo chmod 666 /dev/net/tun
     ```
   - Ensure the TAP driver is installed on Windows.

2. ❌ **Connection Timeout**:
   - Verify the `server_ip` and `server_port` in the client configuration.

3. ❌ **Decryption Errors**:
   - Ensure the `encryption_key` is identical on both server and client.

### Debugging
- 🪵 Check logs on both server and client for detailed information.
- 🔧 Increase logging verbosity in `logging.basicConfig()` if needed.

---

## 🤝 **Contributing**

Contributions are welcome! See the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to get involved.

---

## 📜 **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

## 💡 **Acknowledgements**

- Developed using the Python programming language.
- Inspired by Linux TUN/TAP devices and secure networking principles.
