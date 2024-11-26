#!/bin/bash

get_machine_ip() {
    ip -4 addr show scope global | grep inet | awk '{print $2}' | cut -d'/' -f1 | head -n 1
}

MACHINE_IP=$(get_machine_ip)

if ! sudo iptables -t nat -C PREROUTING -p tcp ! -d $MACHINE_IP -j REDIRECT 2>/dev/null; then
    sudo iptables -A PREROUTING -t nat -p tcp ! -d $MACHINE_IP -j REDIRECT
else
    echo "Rule already exists"
fi

sudo python3 main.py
