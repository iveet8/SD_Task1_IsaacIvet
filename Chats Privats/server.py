import grpc
from concurrent import futures
import chat_pb2
import chat_pb2_grpc
import random

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.clients = {}
        self.chat_sessions = {}  # Agregar el atributo chat_sessions

    def SendMessage(self, request, context):

        print("ADINS")
        recipient_username = request.recipient_username
        print(recipient_username)

        
        
        if recipient_username in self.clients:
            recipient_peer = self.clients[recipient_username]

            print(recipient_peer)

            ip = recipient_peer["ip"]
            port = recipient_peer["port"]


            recipient_channel = grpc.insecure_channel(f"{ip}:{port}")
            recipient_stub = chat_pb2_grpc.ChatServiceStub(recipient_channel)
            
            print("stub created")

            resp = chat_pb2.MessageRequest(message=request.message, recipient_username=recipient_username)
            
            response = recipient_stub.ReceiveMessage(resp)
            print("Sending response")
            return response
        else:
            return chat_pb2.MessageResponse(message=f"El destinatario {recipient_username} no está conectado.")

    def ConnectToChat(self, request, context):
        username = request.username
        ip = "localhost"  # Establecer la dirección IP como localhost
        port = random.randint(1024, 65535)  # Asigna un puerto aleatorio
        self.clients[username] = {'ip': ip, 'port': port}
        # Registra la sesión de chat
        chat_id = f"{username}"
        self.chat_sessions[chat_id] = {'ip': ip, 'port': port}
        print(f"Sesión de chat registrada: {chat_id} - IP={ip}, Puerto={port}")
        return chat_pb2.ChatConnectionResponse(ip=ip, port=port, message="Conexión establecida")

    def GetClientInfo(self, request, context):
        username = request.username
        if username in self.clients:
            client_info = self.clients[username]
            return chat_pb2.ClientInfo(ip=client_info['ip'], port=client_info['port'])
        else:
            return chat_pb2.ClientInfo(ip="", port="")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port("[::]:50051")  # Puerto en el que el servidor escucha
    server.start()
    print("Servidor de chat en ejecución en el puerto 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
