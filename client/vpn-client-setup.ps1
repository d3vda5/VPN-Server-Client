# Define variables (modify according to your setup)
$VPN_INTERFACE = "tap1"              # VPN interface name
$VPN_SERVER_IP = "10.0.0.1"          # VPN server's IP address on the VPN network
$VPN_SUBNET = "10.0.0.0/24"          # VPN subnet
$LOCAL_NETWORK = "192.168.18.0/24"   # Local network or server network
$DEFAULT_GATEWAY = "192.168.18.1"    # Default gateway
$DEFAULT_ROUTE_METRIC = 100          # Metric for the VPN route to give it higher priority

# Enable IP forwarding
Write-Output "Enabling IP forwarding..."
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "IPEnableRouter" -Value 1

# Bring up the VPN interface
Write-Output "Bringing up the VPN interface..."
netsh interface set interface $VPN_INTERFACE admin=enabled

# Flush existing routing rules and tables
Write-Output "Flushing existing routing tables..."
netsh interface ip delete arpcache

# Remove the existing default route
Write-Output "Removing existing default route..."
route delete 0.0.0.0

# Add the default route via the VPN interface
Write-Output "Adding default route via VPN interface..."
route add 0.0.0.0 mask 0.0.0.0 $VPN_SERVER_IP metric $DEFAULT_ROUTE_METRIC if $VPN_INTERFACE

# Enable NAT for internet access through the VPN
Write-Output "Enabling NAT for internet access..."
netsh interface portproxy add v4tov4 listenport=80 listenaddress=0.0.0.0 connectport=80 connectaddress=$VPN_SERVER_IP

# Allow forwarding traffic from the VPN subnet to the local network
Write-Output "Allowing traffic forwarding between VPN and local network..."
netsh advfirewall firewall add rule name="Allow VPN Traffic" dir=in action=allow protocol=any localport=any remoteport=any

# Ensure that traffic to the local network is routed through the local gateway
Write-Output "Ensuring traffic to local network goes through the local gateway..."
route add $LOCAL_NETWORK mask 255.255.255.0 $DEFAULT_GATEWAY

Write-Output "VPN routing setup completed successfully."