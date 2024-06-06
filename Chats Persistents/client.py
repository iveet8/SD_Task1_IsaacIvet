import grpc
import chat_pb2
import chat_pb2_grpc
from concurrent.futures import ThreadPoolExecutor
import threading
import pika

class ChatClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.channel = grpc.insecure_channel(server_address)
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self.is_running = True
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None

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
        threading.Thread(target=self.handle_incoming_messages).start()

    def handle_incoming_messages(self):
        while self.is_running:
            message = self.ReceiveMessage()
            if message:
                print("Mensaje recibido:", message)

    def stop_server(self):
        self.is_running = False

    def ConnectToServer(self, username):
        request = chat_pb2.ChatConnectionRequest(username=username)
        try:
            response = self.stub.ConnectToChat(request)
            return response
        except grpc.RpcError as e:
            print(f"Error en la comunicación gRPC: {e}")
            return None

    def ConnectToChatById(self, username, chat_id):
        request = chat_pb2.ConnectToChatRequest(username=username, chat_id=chat_id)
        try:
            response = self.stub.ConnectToChatById(request)
            return response
        except grpc.RpcError as e:
            print(f"Error en la comunicación gRPC: {e}")
            return None

    def SubscribeToGroupChat(self, group_id):
        response = self.stub.SubscribeToGroupChat(chat_pb2.GroupChatRequest(group_id=group_id))
        if response.message:
            self.rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.exchange_declare(exchange=group_id, exchange_type='fanout')
            result = self.rabbitmq_channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            self.rabbitmq_channel.queue_bind(exchange=group_id, queue=queue_name)

            def callback(ch, method, properties, body):
                print(f"Mensaje recibido del grupo {group_id}: {body.decode()}")

            self.rabbitmq_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            print(f"\nSuscrito al grupo {group_id}. Esperando mensajes...")
            print(f"\nSeleccione una opción: ")
            self.rabbitmq_channel.start_consuming()
        else:
            print(f"Error al suscribirse al grupo {group_id}")

    def SendMessageToGroupChat(self, group_id, message):
        response = self.stub.SendMessageToGroupChat(chat_pb2.GroupChatRequest(group_id=group_id, message=message))
        if response.message:
            print(f"Mensaje enviado al grupo {group_id}")
        else:
            print(f"Error al enviar el mensaje al grupo {group_id}")

    def SubscribeToPersistentGroupChat(self, group_id):
        response = self.stub.SubscribeToPersistentGroupChat(chat_pb2.GroupChatRequest(group_id=group_id))
        if response.message:
            self.rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.exchange_declare(exchange=group_id, exchange_type='fanout', durable=True)
            result = self.rabbitmq_channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            self.rabbitmq_channel.queue_bind(exchange=group_id, queue=queue_name)

            def callback(ch, method, properties, body):
                print(f"\nMensaje recibido del grupo {group_id}: {body.decode()}")

            self.rabbitmq_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            print(f"\nSuscrito al grupo persistente {group_id}. Esperando mensajes...")
            print(f"\nSeleccione una opción: ")
            self.rabbitmq_channel.start_consuming()
        else:
            print(f"Error al suscribirse al grupo persistente {group_id}")

    def SendMessageToPersistentGroupChat(self, group_id, message):
        response = self.stub.SendMessageToPersistentGroupChat(chat_pb2.GroupChatRequest(group_id=group_id, message=message))
        if response.message:
            print(f"Mensaje enviado al grupo persistente {group_id}")
        else:
            print(f"Error al enviar el mensaje al grupo persistente {group_id}")

    def DiscoverChats(self):
        response = self.stub.DiscoverChats(chat_pb2.Empty())
        if response.message:
            self.rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.exchange_declare(exchange='chat_discovery', exchange_type='fanout')
            result = self.rabbitmq_channel.queue_declare(queue='discovery_responses', durable=True)
            queue_name = result.method.queue

            def callback(ch, method, properties, body):
                print(f"Chat descobert: {body.decode()}")

            self.rabbitmq_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            print(f"\nEsperant respostes de descobriment de xat...")
            print(f"\nSeleccione una opción: ")
            self.rabbitmq_channel.start_consuming()
        else:
            print(f"Error al publicar l'esdeveniment de descobriment")

    def InsultChannel(self):
        response = self.stub.InsultChannel(chat_pb2.Empty())
        if response.message:
            self.rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.queue_declare(queue='insult_channel', durable=True)

            def callback(ch, method, properties, body):
                print(f"Insult rebut: {body.decode()}")

            self.rabbitmq_channel.basic_consume(queue='insult_channel', on_message_callback=callback, auto_ack=True)
            print(f"\nEsperant insults del canal d'insults...")
            print(f"\nSeleccione una opción: ")
            self.rabbitmq_channel.start_consuming()
        else:
            print(f"Error al enviar l'insult")

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
    threading.Thread(target=start_grpc_server, args=[response.port]).start()

    if response:
        print("Conectado al servidor.")
        client.start_server()

        while  True:
            print("\nMenú:")
            print("1. Enviar mensaje privado")
            print("2. Suscribirse a un chat grupal")
            print("3. Enviar mensaje a un chat grupal")
            print("4. Suscribirse a un chat grupal persistente")
            print("5. Enviar mensaje a un chat grupal persistente")
            print("6. Descobrir xats actius")
            print("7. Respondre a un descobriment de xat")
            print("8. Enviar un insult")
            print("9. Suscribirse al canal d'insults")
            print("10. Salir")
            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                recipient_username = input("Ingrese el nombre de usuario del destinatario: ")
                message = input("Ingrese su mensaje (para salir --> Salir): ")
                while message != "Salir":
                    response = client.SendMessage(message, recipient_username)
                    if response:
                        print("Mensaje enviado:", response)
                        message = input("Ingrese su mensaje: ")
            elif opcion == "2":
                group_id = input("Ingrese el ID del grupo: ")
                threading.Thread(target=client.SubscribeToGroupChat, args=(group_id,)).start()
            elif opcion == "3":
                group_id = input("Ingrese el ID del grupo: ")
                message = input("Ingrese su mensaje: ")
                client.SendMessageToGroupChat(group_id, message)
            elif opcion == "4":
                group_id = input("Ingrese el ID del grupo: ")
                threading.Thread(target=client.SubscribeToPersistentGroupChat, args=(group_id,)).start()
            elif opcion == "5":
                group_id = input("Ingrese el ID del grupo: ")
                message = input("Ingrese su mensaje: ")
                client.SendMessageToPersistentGroupChat(group_id, message)
            elif opcion == "6":
                client.DiscoverChats()
            elif opcion == "7":
                client.RespondToDiscovery(username)
            elif opcion == "8":
                client.InsultChannel()
            elif opcion == "9":
                client.SubscribeToInsultChannel()
            elif opcion == "10":
                client.stop_server()
                break
            else:
                print("Opción no válida.")

