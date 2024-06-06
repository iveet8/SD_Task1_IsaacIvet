import grpc
from concurrent import futures
import chat_pb2
import chat_pb2_grpc
import random

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.clients = {}
        self.chat_sessions = {}  # Mantener un registro de las sesiones de chat por ID
        self.next_ip_suffix = 1

    def assign_ip(self):
        ip_prefix = "192.168.1."
        ip = ip_prefix + str(self.next_ip_suffix)
        self.next_ip_suffix += 1
        return ip

    def connectToChat(self, request, context):
        username = request.username
        ip =  self.assign_ip() #"localhost"
        port = random.randint(1024, 65535)  # Asigna un puerto aleatorio
        self.clients[username] = {'ip': ip, 'port': port}
        # Registra la sesión de chat
        chat_id = f"{username}"
        self.chat_sessions[chat_id] = {'ip': ip, 'port': port}
        print(f"Sesión de chat registrada: {chat_id} - IP={ip}, Puerto={port}")
        return chat_pb2.ChatConnectionResponse(ip=ip, port=port, message="Conexión establecida")

    def getClientInfo(self, request, context):
        username = request.username
        if username in self.clients:
            client_info = self.clients[username]
            return chat_pb2.ClientInfo(ip=client_info['ip'], port=client_info['port'])
        else:
            return chat_pb2.ClientInfo(ip="", port="")

    def connectToChatById(self, request, context):
        username = request.username
        chat_id = request.chat_id
        if chat_id in self.chat_sessions:
            session_info = self.chat_sessions[chat_id]
            ip = session_info['ip']
            port = session_info['port']
            message = f"Conectado al chat {chat_id}"
        else:
            ip = ""
            port = 0
            message = f"No se pudo encontrar el chat {chat_id}"
        print(f"Solicitud de conexión al chat por {username} para el chat {chat_id}")
        print(f"Respuesta: IP={ip}, Puerto={port}, Mensaje={message}")
        return chat_pb2.ConnectToChatResponse(ip=ip, port=port, message=message)

# Ejemplo de uso
if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port("[::]:50051")  # Puerto en el que el servidor escucha
    server.start()
    print("Servidor de chat en ejecución en el puerto 50051")
    server.wait_for_termination()
