# SD_Task1_IsaacIvet

# Chat Application with gRPC and RabbitMQ

## Descripció general del projecte

Aquest projecte és una aplicació de xat que permet la comunicació tant privada com grupal utilitzant gRPC per la comunicació de serveis i RabbitMQ per la gestió de missatges en grup. L'aplicació ofereix funcions avançades com descobrir xats actius i un canal d'insults. Aquesta solució combina patrons de publicació/subscripció amb cues persistents per assegurar que els missatges es lliuren de manera fiable, fins i tot quan els usuaris no estan en línia.

## Funcionalitats Principals

1. **Xats Privats:** Permet enviar missatges privats entre usuaris connectats.
2. **Xats Grupal:** Permet enviar missatges a grups persistents i temporals.
3. **Descobriment de Xats:** Publica esdeveniments per descobrir altres xats actius.
4. **Canal d'Insults:** Envia i rep insults de manera divertida a través d'un canal dedicat.
5. **Persistència de Missatges:** Gestiona missatges persistents per a xats grupals.

## Arxius del Projecte

- `chat.proto`: Definició del servei gRPC.
- `chat_pb2.py` i `chat_pb2_grpc.py`: Fitxers generats a partir de `chat.proto`.
- `server.py`: Implementació del servidor gRPC, que inclou la lògica del servidor de noms i el message broker. Gestiona les connexions dels usuaris, envia missatges, subscriu usuaris a grups i gestiona la persistència.
- `client.py`: Implementació del client gRPC per interactuar amb el servidor i altres clients.  Permet als usuaris enviar i rebre missatges, subscriure's a grups i descobrir xats.

## Requisits

Abans de començar hem de tenir aquests components instal·lats:

- Python 3.6 o superior
- `grpcio` i `grpcio-tools`
- `pika`
- Un servidor RabbitMQ en execució

## Passos per executar el projecte

### 1. Instal·la dependències

```sh
pip3 install grpcio grpcio-tools pika
```

### 2. Compila els Arxius Proto

Abans de poder executar el servidor i el client, heu de generar els fitxers gRPC a partir de la definició del servei `chat.proto`. Executeu la següent comanda:

```sh
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. chat.proto
```

### 3. Executa el Servidor gRPC

Inicia el servidor gRPC per gestionar les connexions i els missatges dels usuaris.

```sh
python server.py
```

El servidor començarà a escoltar al port 50051.

### 4. Executa el Client gRPC

Executa el client gRPC per començar a enviar i rebre missatges.
```sh
python client.py
```
Se us demanarà que introduïu el vostre nom d'usuari per iniciar sessió. Després, podeu seleccionar una de les opcions disponibles:

1. Connectar-se a un xat privat
2. Subscriure’s a un xat grupal persistent
3. Enviar un missatge a un xat grupal persistent
4. Descobrir xats actius
5. Enviar un insult
6. Subscriure’s al canal d'insults
7. Sortir

#### Opcions del Client

- **Connectar-se a un Xat Privat**: Introduïu el nom d'usuari del destinatari al qual voleu enviar un missatge privat. Si l'usuari està disponible, es connectarà i podreu començar a enviar missatges privats.
- **Subscriure’s i enviar missatge a un Xat Grupal**: Introduïu l'ID del grup al qual voleu subscriure-vos. Un cop subscrits, podreu enviar i rebre missatges grupals.
- **Descobrir Xats Actius**: El client enviarà una sol·licitud per descobrir altres xats actius. Els resultats es mostraran en la terminal.
- **Subscriure’s i enviar insult a Canal d’Insults**: El client es connectarà a una cua de RabbitMQ per rebre insults. Els insults es distribueixen de manera que cada missatge arribi a un client diferent.
- **Sortir**: Finalitza l'execució del client i tanca la connexió amb el servidor.


python3 client.py

## Conclusió

Aquesta aplicació de xat és un exemple robust de com utilitzar gRPC i RabbitMQ per construir una aplicació de missatgeria amb funcions avançades com la persistència de missatges i la comunicació en grup. Amb una configuració adequada, es pot escalar per suportar una gran quantitat d'usuaris i missatges, oferint una experiència de xat rica i fiable.
