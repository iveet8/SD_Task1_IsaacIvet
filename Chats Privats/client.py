import grpc
import chat_pb2
import chat_pb2_grpc
from concurrent.futures import ThreadPoolExecutor
import threading

class ChatClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.channel = grpc.insecure_channel(server_address)
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self.is_running = True

    def SendMessage(self, message, recipient_username):
        message = str(message)
        recipient_username = str(recipient_username)

        request = chat_pb2.MessageRequest(message=message, recipient_username=recipient_username)
        try:

            response = self.stub.SendMessage(request)
            return response.message

        except grpc.RpcError as e:
            print(f"Send --> Error en la comunicación gRPC: {e}")
            return None

    def ReceiveMessage(self):
        try:
            response = self.stub.ReceiveMessage(chat_pb2.Empty())
            return response.message
        except grpc.RpcError as e:
            
            return None

    def start_server(self):
        # Start a new thread to handle incoming messages
        threading.Thread(target=self.handle_incoming_messages).start()

    def handle_incoming_messages(self):
        while self.is_running:
            message = self.ReceiveMessage()
            if message:
                print("Mensaje recibido:", message)

    def stop_server(self):
        self.is_running = False

    def ConnectToServer(self, username):
        # Construir el objeto request utilizando la clase generada por protobuf
        request = chat_pb2.ChatConnectionRequest(username=username)
        try:
            # Llamar al método ConnectToChat utilizando la función de serialización de gRPC
            response = self.stub.ConnectToChat(request)
            return response
        except grpc.RpcError as e:
            # Manejar errores de gRPC
            print(f"Error en la comunicación gRPC: {e}")
            return None

    def ConnectToChatById(self, username, chat_id):
        # Construir el objeto request utilizando la clase generada por protobuf
        request = chat_pb2.ConnectToChatRequest(username=username, chat_id=chat_id)
        try:
            # Llamar al método ConnectToChatById utilizando la función de serialización de gRPC
            response = self.stub.ConnectToChatById(request)
            return response
        except grpc.RpcError as e:
            # Manejar errores de gRPC
            print(f"Error en la comunicación gRPC: {e}")
            return None

def start_grpc_server(port):
    print("Starting server (port %d"%(port))
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServer(), server)
    server.add_insecure_port('[::]:%d'%(port))
    server.start()
    server.wait_for_termination()

class ChatServer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.messages = []

    def SendMessage(self, request, context):
        print("HOLA")
        self.messages.append(request.message)
        return chat_pb2.MessageResponse(message="Mensaje enviado")

    def ReceiveMessage(self, request, context):
        print("\nMensaje recibido:", request.message)
        print("Ingrese su mensaje: ", end="", flush=True)
        return chat_pb2.MessageResponse(message=request.message)

if __name__ == "__main__":
    server_address = "localhost:50051"
    client = ChatClient(server_address)
    username = input("Ingrese su nombre de usuario: ")
    response = client.ConnectToServer(username)
    # Start the gRPC server in a new thread
    threading.Thread(target=start_grpc_server, args=[response.port]).start()
    if response:
        print("Conectado al servidor.")
        client.start_server()  # Start the server to handle incoming messages

        recipient_username = input("Ingrese el nombre de usuario del destinatario: ")
        while True:
            message = input("Ingrese su mensaje: ")
            response = client.SendMessage(message, recipient_username)
            if response:
                print("Mensaje enviado:", response)
