import grpc
import chat_pb2
import chat_pb2_grpc

class ChatClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.channel = grpc.insecure_channel(server_address)
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)

    def SendMessage(self, message, recipient_username):
        # Crear un objeto de tipo MessageRequest
        request = chat_pb2.MessageRequest(message=message, recipient_username=recipient_username)
        try:
            response = self.stub.SendMessage(request)  # Pasar el objeto request
            return response.message
        except grpc.RpcError as e:
            print(f"Error en la comunicación gRPC: {e}")
            return None

    def ReceiveMessage(self):
        try:
            response = self.stub.ReceiveMessage(chat_pb2.Empty())
            return response.message
        except grpc.RpcError as e:
            print(f"Error en la comunicación gRPC: {e}")
            return None




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

    
if __name__ == "__main__":
    server_address = "localhost:50051"
    client = ChatClient(server_address)
    username = input("Ingrese su nombre de usuario: ")
    response = client.ConnectToServer(username)
    if response:
        print("Conectado al servidor.")

        recipient_username = input("Ingrese el nombre de usuario del destinatario: ")
        message = input("Ingrese su mensaje: ")
        response = client.SendMessage(message, recipient_username)
        if response:
            print("Mensaje enviado:", response)

        response = client.ReceiveMessage()
        if response:
            print("Mensaje recibido:", response)
