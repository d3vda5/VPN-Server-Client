# Define variables (modify according to your setup)
$VPN_INTERFACE = "tap0"              # VPN interface name
$VPN_NETWORK = "10.0.0.0/24"         # VPN network
$LOCAL_INTERFACE = "Ethernet"        # Local network interface name
$LOCAL_NETWORK = "192.168.18.0/24"   # Local network

# Enable IP forwarding
Write-Output "Enabling IP forwarding..."
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "IPEnableRouter" -Value 1

# Set up firewall rules
Write-Output "Setting up firewall rules..."

# Allow established and related connections
Write-Output "Allowing established and related connections..."
netsh advfirewall firewall add rule name="Allow Established Connections" dir=in action=allow protocol=any state=established,related

# Allow local loopback traffic
Write-Output "Allowing local loopback traffic..."
netsh advfirewall firewall add rule name="Allow Loopback Traffic" dir=in action=allow protocol=any localip=127.0.0.1 remoteip=127.0.0.1
netsh advfirewall firewall add rule name="Allow Loopback Traffic" dir=out action=allow protocol=any localip=127.0.0.1 remoteip=127.0.0.1

# Allow VPN traffic on the VPN interface
Write-Output "Allowing VPN traffic on $VPN_INTERFACE..."
netsh advfirewall firewall add rule name="Allow VPN Traffic In" dir=in action=allow interface=$VPN_INTERFACE
netsh advfirewall firewall add rule name="Allow VPN Traffic Out" dir=out action=allow interface=$VPN_INTERFACE

# Allow traffic between VPN network and local network
Write-Output "Allowing traffic between VPN network and local network..."
netsh advfirewall firewall add rule name="Allow VPN to Local Network" dir=in action=allow protocol=any localip=$LOCAL_NETWORK remoteip=$VPN_NETWORK
netsh advfirewall firewall add rule name="Allow Local Network to VPN" dir=out action=allow protocol=any localip=$VPN_NETWORK remoteip=$LOCAL_NETWORK

Write-Output "VPN firewall setup completed successfully."