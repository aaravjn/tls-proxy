import socket
import threading
from Connectors.server_socket_manager import ServerSocketManager
from OpenSSL import SSL
from utils.certificate import create_domain_certificate
import time


class ClientSocketManager:
    def __init__(self, client_socket: socket, client_address, client_port, destination_port):
        self.socket: socket = client_socket

        self.ssl_socket = None

        self.socket_open = True
        self.ip = client_address
        self.port = client_port
        self.destination_port = destination_port
        self.server_socket_obj: ServerSocketManager = None
        threading.Thread(target=self.handle_client, daemon=True).start()

    def close_socket(self):
        self.socket_open = False
        self.ssl_socket.shutdown()
        print(f"Disconnected with client {self.ip} and port {self.port}")

    def handle_client(self):
        def sni_callback(sock: SSL.Connection):
            server_name = sock.get_servername().decode('ascii')

            # while self.server_socket_obj is None:
            #     time.sleep(0.1)
            
            # self.server_socket_obj.perform_tls_handshake(server_name)
            # time.sleep(2)

            file_name = create_domain_certificate(server_name, "issuer-ca.crt", "issuer-ca.key")
            
            new_ctx = SSL.Context(SSL.TLS_SERVER_METHOD)
            
            new_ctx.use_certificate_file(f"./certs/{file_name}.crt")
            new_ctx.use_privatekey_file(f"./certs/{file_name}.key")

            sock.set_context(new_ctx)

        context = SSL.Context(SSL.TLS_SERVER_METHOD)
        context.set_tlsext_servername_callback(sni_callback)
        context.set_options(SSL.OP_NO_TICKET)

        self.ssl_socket = SSL.Connection(context, self.socket)
        self.ssl_socket.set_accept_state()

        try:
            self.ssl_socket.do_handshake()
        except:
            self.close_socket()
            self.server_socket_obj.close_socket()
            print("SSL handshake failed")
            return

        while self.socket_open:
            message = self.ssl_socket.recv(4096)
            if not message:
                self.close_socket()
                self.server_socket_obj.close_socket()
                return
            self.server_socket_obj.send_message(message)
    
    def send_message(self, message):
        try:
            self.ssl_socket.sendall(message)
        except:
            self.close_socket()
            self.server_socket_obj.close_socket()
            print("Some error occurred in sending message to client")
