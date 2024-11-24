import socket
import threading

class ServerSocketManager:
    def __init__(self, port, client_socket, destination_ip, destination_port):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cs = client_socket
        threading.Thread(target=self.recv_and_forward_message, args=(destination_ip, destination_port), daemon=True)

    def send_message(self, message):
        self.server_socket.send(message.encode('utf-8'))
    
    def recv_and_forward_message(self, destination_ip, destination_port):
        self.server_socket.connect((destination_ip, destination_port))
        while True:
            data = self.server_socket.recv(4096)
            if not data:
                break
            self.cs.send(data)
    
