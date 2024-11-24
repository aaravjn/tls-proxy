#!/bin/bash

# Function to get the machine's primary IP address
get_machine_ip() {
    ip -4 addr show scope global | grep inet | awk '{print $2}' | cut -d'/' -f1 | head -n 1
}

MACHINE_IP=$(get_machine_ip)

sudo iptables -A PREROUTING -t nat -p tcp ! -d $MACHINE_IP -j REDIRECT

