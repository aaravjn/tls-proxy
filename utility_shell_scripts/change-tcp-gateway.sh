#!/bin/bash

get_machine_ip() {
    ip -4 addr show scope global | grep inet | awk '{print $2}' | cut -d'/' -f1 | head -n 1
}

read -p "Enter the gateway IP address: " GATEWAY_IP

if [[ ! $GATEWAY_IP =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
    echo "Invalid IP address format. Please enter a valid IPv4 address."
    exit 1
fi

MY_IP=$(get_machine_ip)

if [ -z "$MY_IP" ]; then
    echo "No valid source IP address found. Please check your network configuration."
    exit 1
fi

ROUTE_TABLE=200
echo "Using routing table $ROUTE_TABLE..."

if ! grep -q "$ROUTE_TABLE custom_route" /etc/iproute2/rt_tables; then
    echo "$ROUTE_TABLE custom_route" | sudo tee -a /etc/iproute2/rt_tables
fi

sudo ip route add default via "$GATEWAY_IP" table custom_route

sudo ip rule add from "$MY_IP" ipproto tcp table custom_route

echo "Policy-based routing rule added:"
ip rule show | grep "$MY_IP"

echo "Routes in the custom routing table:"
ip route show table custom_route

echo "All TCP packets from $MY_IP are now forwarded to the gateway $GATEWAY_IP."

echo "Importing the latest certifice from the gateway..."

echo "Calculating the hash of the existing certificate..."

if [ -f "$HOME/.issuer-ca.crt" ]; then
    CERT_HASH=$(sha256sum "$HOME/.issuer-ca.crt" | awk '{print $1}')
    RESPONSE=$(curl -k "http://$GATEWAY_IP:5000/certificate?hash=$CERT_HASH")
    if [ "$RESPONSE" == "Hash is the same" ]; then
        echo "Certificate is up-to-date. No changes made."
    else
        echo "$RESPONSE" > "$HOME/.issuer-ca.crt"
        echo "Certificate updated successfully."
    fi
else
    curl -k "http://$GATEWAY_IP:5000/certificate" -o "$HOME/.issuer-ca.crt"
    echo "Certificate downloaded successfully."
fi

CERT_PATH="$HOME/.issuer-ca.crt"
CERT_NAME=$(basename "$CERT_PATH")

if [ -f "/usr/local/share/ca-certificates/$CERT_NAME" ]; then
  echo "Certificate already exists in /usr/local/share/ca-certificates/"
else
  sudo cp "$CERT_PATH" /usr/local/share/ca-certificates/
  sudo update-ca-certificates
fi

openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt "$CERT_PATH"

PROFILE=$(ls ~/.mozilla/firefox/ | grep '\.default-release')
if [ -z "$PROFILE" ]; then
  echo "No firefox profile found"
  exit 1
fi

echo "Found firefox profile: $PROFILE"
echo "Importing root CA to firefox profile"

certutil -A -n "Aarav Root CA" -t "TC,C,C" -i "$CERT_PATH" -d sql:$HOME/.mozilla/firefox/$PROFILE
echo "Successfully imported root CA to firefox profile"

echo "Verifying root CA in firefox profile"
certutil -L -d sql:$HOME/.mozilla/firefox/$PROFILE | grep "Aarav Root CA"