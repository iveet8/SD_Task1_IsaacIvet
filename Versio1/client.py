# client.py

import socket

class Client:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = None

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))
        print("Connected to server.")

    def send_message(self, message):
        self.client_socket.send(message.encode())

    def receive_message(self):
        message = self.client_socket.recv(1024).decode()
        return message

    def start_chat(self):
        while True:
            message = input("Enter message: ")
            self.send_message(message)
            if message.lower() == "exit":
                break
            received_message = self.receive_message()
            print("Received:", received_message)

    def close_connection(self):
        self.client_socket.close()

if __name__ == "__main__":
    client = Client("127.0.0.1", 12345)  # Change IP and port accordingly
    client.connect_to_server()
    client.start_chat()
    client.close_connection()
