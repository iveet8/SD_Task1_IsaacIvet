import grpc
import uuid
import chat_pb2
import chat_pb2_grpc
import asyncio

class ChatClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.channel = grpc.insecure_channel(server_address)
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self.username = None
        self.ip = None
        self.port = None
        self.client_id = str(uuid.uuid4())  

    def connect_to_server(self):
        self.username = input("Ingrese su nombre de usuario: ")
        request = chat_pb2.ChatConnectionRequest(username=self.username, client_id=self.client_id)  
        response = self.stub.connectToChat(request)
        self.ip = response.ip
        self.port = response.port
        if self.ip and self.port:
            print(f"Se le ha asignado la IP {self.ip} y el puerto {self.port}")
        else:
            print("No se pudo establecer la conexión al chat.")

    def connect_to_chat_by_id(self, chat_id):
        request = chat_pb2.ConnectToChatRequest(username=self.username, chat_id=chat_id)
        response = self.stub.connectToChatById(request)
        self.ip = response.ip
        self.port = response.port
        if self.ip and self.port:
            print(f"Conectado al chat {chat_id} con la IP {self.ip} y el puerto {self.port}")
            self.connect_to_client(self.ip, self.port)  # Llama a la función para conectar directamente al otro cliente
        else:
            print(f"No se pudo conectar al chat {chat_id}")

    def connect_to_client(self, ip, port):
        # Conexión directa al otro cliente
        other_client_channel = grpc.insecure_channel(f"{ip}:{port}")
        other_client_stub = chat_pb2_grpc.ChatServiceStub(other_client_channel)
        print("Conexión directa al otro cliente establecida.")

# Ejemplo de uso
if __name__ == "__main__":
    server_address = "localhost:50051"  
    client = ChatClient(server_address)
    client.connect_to_server()
    
    chat_id = input("Ingrese el ID del chat al que desea conectarse: ")
    client.connect_to_chat_by_id(chat_id)
