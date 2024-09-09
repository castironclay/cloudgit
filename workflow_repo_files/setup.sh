#!/bin/bash

# Variables
WG_DIR="/etc/wireguard"
WG_CONF="${WG_DIR}/wg0.conf"
WG_CLIENT_CONF="${WG_DIR}/client.conf"
SERVER_IP="10.0.0.1"
SERVER_PORT="51820"
CLIENT_IP="10.0.0.2"
PSK=$(wg genpsk)

# Install WireGuard if not installed
if ! command -v wg >/dev/null 2>&1; then
    echo "WireGuard not found. Installing..."
    sudo apt update
    sudo apt install -y wireguard
fi

# Create WireGuard directory if it doesn't exist
sudo mkdir -p $WG_DIR

# Generate server keys
echo "Generating server keys..."
umask 077
wg genkey | sudo tee $WG_DIR/server_private.key | wg pubkey | sudo tee $WG_DIR/server_public.key

# Generate client keys
echo "Generating client keys..."
wg genkey | sudo tee $WG_DIR/client_private.key | wg pubkey | sudo tee $WG_DIR/client_public.key

# Create server configuration
echo "Creating server configuration..."
sudo tee $WG_CONF > /dev/null <<EOF
[Interface]
Address = $SERVER_IP/24
ListenPort = $SERVER_PORT
PrivateKey = $(sudo cat $WG_DIR/server_private.key)


[Peer]
PublicKey = $(sudo cat $WG_DIR/client_public.key)
PresharedKey = $PSK
AllowedIPs = $CLIENT_IP/32
EOF

# Create client configuration
echo "Creating client configuration..."
sudo tee $WG_CLIENT_CONF > /dev/null <<EOF
[Interface]
PrivateKey = $(sudo cat $WG_DIR/client_private.key)
ListenPort = 52820
Address = $CLIENT_IP/32
MTU = 1300

[Peer]
PublicKey = $(sudo cat $WG_DIR/server_public.key)
PresharedKey = $PSK
AllowedIPs = 10.0.0.1/32
Endpoint = 127.0.0.1:51820
EOF

# Enable IP forwarding
echo "Enabling IP forwarding..."
sudo sysctl -w net.ipv4.ip_forward=1
sudo sh -c 'echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf'

# Start WireGuard
echo "Starting WireGuard..."
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0

# Display keys and configuration
echo "WireGuard setup complete!"

sudo cp /etc/wireguard/client.conf /tmp/
sudo chmod 755 /tmp/client.conf