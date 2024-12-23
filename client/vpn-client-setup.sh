#!/bin/bash

# Define variables (modify according to your setup)
VPN_INTERFACE="tun1"              # VPN interface name
VPN_SERVER_IP="10.0.0.1"          # VPN server's IP address on the VPN network
VPN_SUBNET="10.0.0.0/24"          # VPN subnet
LOCAL_NETWORK="192.168.18.0/24"   # Local network or server network
DEFAULT_GATEWAY="192.168.18.1"    # Default gateway (could be eth0 interface or something else)
DEFAULT_ROUTE_METRIC=100          # Metric for the VPN route to give it higher priority

# Enable IP forwarding (in case it's not already enabled)
echo "Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1

# Make the IP forwarding change permanent
echo "Making IP forwarding permanent..."
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
sysctl -p

# Bring up the VPN interface (tun1)
echo "Bringing up the VPN interface..."
ip link set $VPN_INTERFACE up

# Flush existing routing rules and tables
echo "Flushing existing routing tables..."
ip route flush table main

# Remove the existing default route
echo "Removing existing default route..."
ip route del default

# Add the default route via the VPN interface with the specified metric
echo "Adding default route via VPN interface..."
ip route add default via $VPN_SERVER_IP dev $VPN_INTERFACE metric $DEFAULT_ROUTE_METRIC
sudo ip route add default dev tun1

# Check routing table after changes
echo "Current routing table:"
ip route show

# Enable iptables NAT/masquerading for internet access through the VPN
echo "Enabling NAT (Masquerading) for internet access..."
iptables -t nat -A POSTROUTING -o $VPN_INTERFACE -s $VPN_SUBNET -j MASQUERADE

# Allow forwarding traffic from the VPN subnet to the local network
echo "Allowing traffic forwarding between VPN and local network..."
iptables -A FORWARD -i $VPN_INTERFACE -o eth0 -s $VPN_SUBNET -j ACCEPT
iptables -A FORWARD -i eth0 -o $VPN_INTERFACE -d $VPN_SUBNET -j ACCEPT

# Ensure that traffic to the local network is routed through the local gateway
echo "Ensuring traffic to local network goes through the local gateway..."
ip route add $LOCAL_NETWORK via $DEFAULT_GATEWAY

# Save iptables rules to make them persistent across reboots
echo "Saving iptables rules..."
iptables-save > /etc/iptables/rules.v4

# Verify iptables and routing table
echo "Verifying iptables and routing configuration..."
iptables -t nat -L -v
iptables -L -v
ip route show

echo "VPN routing setup completed successfully."
