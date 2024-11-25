import socket
import threading
import time
from TCPConnectors.server_socket_manager import ServerSocketManager

class ClientSocketManager:
    def __init__(self, client_socket: socket, client_address, client_port, destination_port):
        self.socket: socket = client_socket
        self.socket_open = True
        self.ip = client_address
        self.port = client_port
        self.destination_port = destination_port
        self.server_socket_obj = None
        threading.Thread(target=self.handle_client, daemon=True).start()

    def close_socket(self):
        self.socket_open = False
        self.socket.close()
        print(f"Disconnected with client {self.ip} and port {self.port}")

    def handle_client(self):
        while self.socket_open:
            if self.server_socket_obj == None:
                time.sleep(0.5)
                continue
            
            message = self.socket.recv(1024)
            if not message:
                self.close_socket()
                self.server_socket_obj.close_socket()
                return
            print(f"Message from {self.ip} and port {self.port}")
            self.server_socket_obj.send_message(message)
    
    def send_message(self, message):
        self.socket.send(message)
        print("Forwarding message to client:{} and port:{}".format(self.ip, self.port))