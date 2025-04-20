import threading
import socket

from Connectors.client_socket_manager import ClientSocketManager
from Connectors.server_socket_manager import ServerSocketManager
from utils.conntrack import get_conntrack_entry

def run_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    
    print(f"Socket listening on port {port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} on port {port}")
        initiate_connection(client_socket, addr[0], addr[1], port)

def initiate_connection(client_socket: socket, client_address, client_port, destination_port):
    client_socket_obj = ClientSocketManager(client_socket, client_address, client_port, destination_port)
    destination_addr = get_conntrack_entry(client_address, client_port)
    try:
        client_socket_obj.server_socket_obj = ServerSocketManager(destination_addr, destination_port, client_socket_obj)
        print("Both the connections established")
    except:
        print("Some error occured, aborting connection")
        client_socket_obj.close_socket()


if __name__ == "__main__":

    PORTS = [
        # 80, # HTTP
        443, # HTTPS
        # 21, # FTP
        # 25, # SMTP
        # 853, # DNS-over-TLS
        # 587, # SMTPS
        # 990 # FTPS
        465,
        587
    ]

    threads = []
    for port in PORTS:
        thread = threading.Thread(target=run_socket, args=(port,), daemon=True)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()