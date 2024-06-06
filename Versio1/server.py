# server.py

import socket
import threading

class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = None
        self.clients = []

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        print("Server started. Waiting for connections...")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        self.clients.append(client_socket)
        while True:
            message = client_socket.recv(1024).decode()
            if message.lower() == "exit":
                self.clients.remove(client_socket)
                client_socket.close()
                break
            print("Received message:", message)
            # Broadcast message to all clients
            for client in self.clients:
                if client != client_socket:
                    client.send(message.encode())

    def close_server(self):
        for client_socket in self.clients:
            client_socket.close()
        self.server_socket.close()

if __name__ == "__main__":
    server = Server("127.0.0.1", 12345)  # Change IP and port accordingly
    server.start_server()
