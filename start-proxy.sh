sudo iptables -A PREROUTING -t nat -p tcp ! -d 10.0.2.4 -j REDIRECT
