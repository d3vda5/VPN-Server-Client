#!/bin/bash

# Set default policies
echo "Setting default policies..."
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow established and related connections
echo "Allowing established and related connections..."
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow local loopback traffic
echo "Allowing local loopback traffic..."
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow VPN traffic (Assume tun0 is your VPN interface)
echo "Allowing VPN traffic on tun0..."
iptables -A INPUT -i tun0 -j ACCEPT
iptables -A OUTPUT -o tun0 -j ACCEPT

# Allow traffic between VPN network (10.0.0.0/24) and local network (eth0)
echo "Allowing traffic between VPN network and local network..."
iptables -A FORWARD -i tun0 -o eth0 -s 10.0.0.0/24 -j ACCEPT
iptables -A FORWARD -i eth0 -o tun0 -d 10.0.0.0/24 -j ACCEPT

# Allow specific services (e.g., SSH, HTTP, HTTPS)
echo "Allowing SSH, HTTP, and HTTPS..."
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Enable NAT (Masquerading) for VPN clients (Assuming eth0 is your internet interface)
echo "Enabling NAT (Masquerading) for VPN clients..."
iptables -t nat -A POSTROUTING -o eth0 -s 10.0.0.0/24 -j MASQUERADE

# Block all other incoming traffic
echo "Blocking all other incoming traffic..."
iptables -A INPUT -j DROP

# Enable IP forwarding
echo "Enabling IP forwarding..."
sysctl -w net.ipv4.ip_forward=1

# Make the IP forwarding change permanent
echo "Making IP forwarding permanent..."
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
sysctl -p

# Save iptables rules
echo "Saving iptables rules..."
iptables-save > /etc/iptables/rules.v4

# Done
echo "Firewall and VPN configuration complete!"
