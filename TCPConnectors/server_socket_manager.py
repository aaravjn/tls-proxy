import socket
import threading

class ServerSocketManager:
    def __init__(self, destination_ip, destination_port, client_socket_obj):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_open = True
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.client_socket_obj = client_socket_obj
        
        try:
            self.server_socket.settimeout(5)
            self.server_socket.connect((self.destination_ip, self.destination_port))
            self.server_socket.settimeout(None)
            
            print("Connection established succesfully with the server:", self.destination_ip)
            threading.Thread(target=self.handle_server, daemon=True).start()
        except:
            print("Error connecting to the server:", self.destination_ip)
            raise

    def send_message(self, message):
        print(f"Sending message to server: {self.destination_ip}")
        self.server_socket.send(message)
    
    def close_socket(self):
        self.socket_open = False
        self.server_socket.close()
        print(f"Disconnected with server {self.destination_ip} and port: {self.destination_port}")

    def handle_server(self):
        while self.socket_open:
            data = self.server_socket.recv(4096)
            if not data:
                self.close_socket()
                self.client_socket_obj.close_socket()
                return
            self.client_socket_obj.send_message(data)