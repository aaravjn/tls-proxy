import socket
import threading
from OpenSSL import SSL
import time

class ServerSocketManager:
    def __init__(self, destination_ip, destination_port, client_socket_obj):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_open = True
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.client_socket_obj = client_socket_obj
        self.ssl_socket = None

        try:
            self.server_socket.settimeout(5)
            self.server_socket.connect((self.destination_ip, self.destination_port))
            self.server_socket.settimeout(None)
            
            print("Connection established successfully with the server:", self.destination_ip)
            threading.Thread(target=self.handle_server, daemon=True).start()
        except Exception as e:
            print("Error connecting to the server:", self.destination_ip, e)
            raise

    def perform_tls_handshake(self, server_name):
        try:
            context = SSL.Context(SSL.TLS_CLIENT_METHOD)
            self.ssl_socket = SSL.Connection(context, self.server_socket)
            self.ssl_socket.set_tlsext_host_name(server_name.encode('utf-8'))
            self.ssl_socket.set_connect_state()

            self.ssl_socket.do_handshake()
            print("TLS handshake completed with server:", server_name)
        except Exception as e:
            print("Error during TLS handshake with the server:", self.destination_ip, e)
            self.close_socket()
            raise

    def send_message(self, message):
        try:
            self.ssl_socket.sendall(message)
        except Exception as e:
            self.close_socket()
            self.client_socket_obj.close_socket()
            print("Some error occurred in sending message to server:", e)

    def close_socket(self):
        self.socket_open = False
        self.ssl_socket.shutdown()
        print(f"Disconnected with server {self.destination_ip} and port: {self.destination_port}")

    def handle_server(self):
        while self.ssl_socket is None:
            time.sleep(0.5)
        
        while self.socket_open:
            try:
                data = self.ssl_socket.recv(4096)
                if not data:
                    self.close_socket()
                    self.client_socket_obj.close_socket()
                    return
                self.client_socket_obj.send_message(data)
            except Exception as e:
                print("Error receiving data from server:", e)
                self.close_socket()
                self.client_socket_obj.close_socket()
                return