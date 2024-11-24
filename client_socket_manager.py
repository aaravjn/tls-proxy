import socket
import threading
from pyroute2 import IPRoute # type: ignore
import subprocess
import re

def get_conntrack_entry(ip, port):
    command = f"sudo conntrack -L | agrep 'dst={ip};sport={port}'"
    print(command)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        output = result.stdout
        print(output)  # Print the full output for debugging
        
        # Use regular expression to extract the dst value
        match = re.search(r'dst=([\d\.]+)', output)
        if match:
            dst_ip = match.group(1)
            print(f"Extracted dst IP: {dst_ip}")
        else:
            print("No dst IP found in the output")


def run_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    
    print(f"Socket listening on port {port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} on port {port}")
        threading.Thread(target=handle_client, args=(client_socket, addr[0], addr[1]), daemon=True).start()

def handle_client(client_socket, client_address, port):
    destination_addr = get_conntrack_entry(client_address, port)
    # print("Original destination IP address:", destination_addr)

    # Try to connect to the original destination address
        # If connection is not successful, terminate the connection from client
    # Build a connection object

    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Message from {client_address} on port {port}: {message}")
            client_socket.send(f"Server on port {port} received: {message}".encode('utf-8'))
    except Exception as e:
        print(f"Error with client {client_address} on port {port}: {e}")