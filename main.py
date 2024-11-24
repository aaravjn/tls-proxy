import threading
from client_socket_manager import run_socket

if __name__ == "__main__":

    PORTS = [
        80, # HTTP
        # 443, # HTTPS
        # 21, # FTP
        # 25, # SMTP
        # 853, # DNS-over-TLS
        # 587, # SMTPS
        # 990 # FTPS
    ]

    threads = []
    for port in PORTS:
        thread = threading.Thread(target=run_socket, args=(port,), daemon=True)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
