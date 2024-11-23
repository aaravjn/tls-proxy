import socket
import threading

def run_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Socket listening on port {port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} on port {port}")
        client_socket.close()

def handle_client(client_socket, client_address, port):
    """Handle communication with a single client."""
    print(f"New connection from {client_address} on port {port}")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Client disconnected
            print(f"Message from {client_address} on port {port}: {message}")
            # Echo back the message
            client_socket.send(f"Server on port {port} received: {message}".encode('utf-8'))
    except Exception as e:
        print(f"Error with client {client_address} on port {port}: {e}")

if __name__ == "__main__":

    PORTS = [
        80, # HTTP
        443, # HTTPS
        21, # FTP
        25, # SMTP
        853, # DNS-over-TLS
        587, # SMTPS
        990 # FTPS
    ]

    threads = []
    for port in PORTS:
        thread = threading.Thread(target=run_socket, args=(port,), daemon=True).start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()