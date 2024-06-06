import grpc
from concurrent import futures
import chat_pb2
import chat_pb2_grpc
import random
import pika
import threading
from collections import defaultdict, deque

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.clients = {}
        self.chat_sessions = {}
        self.group_subscriptions = defaultdict(list)
        self.group_messages = defaultdict(deque)
        self.rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.rabbitmq_channel = self.rabbitmq_connection.channel()
        self.rabbitmq_channel.exchange_declare(exchange='chat_discovery', exchange_type='fanout')
        self.rabbitmq_channel.queue_declare(queue='discovery_responses', durable=True)
        self.rabbitmq_channel.queue_declare(queue='insult_channel', durable=True)

    def ConnectToChat(self, request, context):
        username = request.username
        if username in self.clients:
            client_info = self.clients[username]
            ip = client_info['ip']
            port = client_info['port']
            message = "Conexión ya existente"
        else:
            ip = "localhost"
            port = random.randint(1024, 65535)
            self.clients[username] = {'ip': ip, 'port': port, 'subscribed_groups': []}
            chat_id = f"{username}"
            self.chat_sessions[chat_id] = {'ip': ip, 'port': port}
            print(f"Sesión de chat registrada: {chat_id} - IP={ip}, Puerto={port}")
            message = "Conexión establecida"
        
        # Enviar missatges pendents dels grups als que està subscrit
        pending_messages = []
        for group_id in self.clients[username]['subscribed_groups']:
            while self.group_messages[group_id]:
                pending_message = self.group_messages[group_id].popleft()
                pending_messages.append((group_id, pending_message))
        
        return chat_pb2.ChatConnectionResponse(ip=ip, port=port, message=message)


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

    def GetClientInfo(self, request, context):
        username = request.username
        if username in self.clients:
            client_info = self.clients[username]
            return chat_pb2.ClientInfo(ip=client_info['ip'], port=client_info['port'])
        else:
            return chat_pb2.ClientInfo(ip="", port="")

    def SubscribeToPersistentGroupChat(self, request, context):
        group_id = request.group_id
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=group_id, exchange_type='fanout', durable=True)
        return chat_pb2.GroupChatResponse(message=f"Subscribed to persistent group chat {group_id}")

    def SendMessageToPersistentGroupChat(self, request, context):
        group_id = request.group_id
        message = request.message
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.basic_publish(exchange=group_id, routing_key='', body=message, properties=pika.BasicProperties(delivery_mode=2))
        return chat_pb2.GroupChatResponse(message=f"Message sent to persistent group chat {group_id}")

    def DiscoverChats(self, request, context):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.basic_publish(exchange='chat_discovery', routing_key='', body='discover')
        return chat_pb2.DiscoveryResponse(message="Discovery event published")

    def InsultChannel(self, request, context):
        self.rabbitmq_channel.queue_declare(queue='insult_channel', durable=True)
        insult = "You are a dummy!"
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.basic_publish(exchange='', routing_key='insult_channel', body=insult, properties=pika.BasicProperties(delivery_mode=2))
        return chat_pb2.InsultResponse(message="Insult sent to the insult channel")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Servidor de chat en ejecución en el puerto 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

