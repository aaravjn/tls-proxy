#!/bin/bash

# Function to get the machine's primary IP address
get_machine_ip() {
    ip -4 addr show scope global | grep inet | awk '{print $2}' | cut -d'/' -f1 | head -n 1
}

MACHINE_IP=$(get_machine_ip)

# Check if the rule already exists
if ! sudo iptables -t nat -C PREROUTING -p tcp ! -d $MACHINE_IP -j REDIRECT 2>/dev/null; then
    # Add the rule if it does not exist
    sudo iptables -A PREROUTING -t nat -p tcp ! -d $MACHINE_IP -j REDIRECT
else
    echo "Rule already exists"
fi

sudo python3 main.py