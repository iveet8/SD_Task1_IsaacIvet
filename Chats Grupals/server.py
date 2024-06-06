import grpc
from concurrent import futures
import chat_pb2
import chat_pb2_grpc
import random
import pika

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.clients = {}
        self.chat_sessions = {}

    def SendMessage(self, request, context):
        recipient_username = request.recipient_username
        if recipient_username in self.clients:
            recipient_peer = self.clients[recipient_username]
            ip = recipient_peer["ip"]
            port = recipient_peer["port"]
            recipient_channel = grpc.insecure_channel(f"{ip}:{port}")
            recipient_stub = chat_pb2_grpc.ChatServiceStub(recipient_channel)
            resp = chat_pb2.MessageRequest(message=request.message, recipient_username=recipient_username)
            response = recipient_stub.ReceiveMessage(resp)
            return response
        else:
            return chat_pb2.MessageResponse(message=f"El destinatario {recipient_username} no está conectado.")

    def ConnectToChat(self, request, context):
        username = request.username
        ip = "localhost"
        port = random.randint(1024, 65535)
        self.clients[username] = {'ip': ip, 'port': port}
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

    def SubscribeToGroupChat(self, request, context):
        group_id = request.group_id
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=group_id, exchange_type='fanout')
        return chat_pb2.GroupChatResponse(message=f"Subscribed to group chat {group_id}")

    def SendMessageToGroupChat(self, request, context):
        group_id = request.group_id
        message = request.message
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.basic_publish(exchange=group_id, routing_key='', body=message)
        return chat_pb2.GroupChatResponse(message=f"Message sent to group chat {group_id}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Servidor de chat en ejecución en el puerto 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
