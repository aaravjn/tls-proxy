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
