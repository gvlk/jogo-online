from pickle import loads, dumps, UnpicklingError
from socket import socket, AF_INET6, SOCK_STREAM
from threading import Thread
from time import sleep

# Custom client codes
CLIENT_STATUS_DISCONNECTED = 0
CLIENT_STATUS_NEW = 0
CLIENT_STATUS_CONNECTED = 1

# Custom status codes
STATUS_NEW_PLAYER = 100
STATUS_PLAYERS_POSITIONS = 200

MAX_CLIENTS = 6


class ServerController:
    # SOCK_STREAM is a constant that represents the socket type for TCP connection
    # AF_INET6 is a constant that represents the address family for IPv6
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port
        self.socket: socket | None = None
        self.max_clients = MAX_CLIENTS

        self.clients = set()
        self.players_pos = dict()

        self.listener_thread = Thread(target=self.start_listener)

    def run_server(self) -> None:
        self.listener_thread.start()

        while True:
            sleep(1.0 / 30.0)

            self.handlePendingClients()
            self.handleConnectedClients()

    def start_listener(self):
        with socket(AF_INET6, SOCK_STREAM) as self.socket:
            self.socket.bind((self.ip, self.port))
            self.socket.listen(4)

            print(f"Server listening on {self.ip}:{self.port}\n")

            while True:
                client_socket, client_address = self.socket.accept()

                if len(self.clients) == self.max_clients:
                    print("Maximum number of clients reached. Connection rejected.")
                    client_socket.close()
                    continue

                print(
                    f"New client connected\n"
                    f"Host: {client_address[0]}\n"
                    f"Port: {client_address[1]}\n"
                    f"Flow Info: {client_address[2]}\n"
                    f"Scope ID: {client_address[3]}\n"
                )

                client_thread = ClientThread(
                    client_socket,
                    client_address,
                    self.players_pos
                )

                self.clients.add(client_thread)
                client_thread.start()

    def handlePendingClients(self):
        for newClient in self.clients:
            if newClient.status == CLIENT_STATUS_NEW:
                clients = tuple(client.player_id for client in self.clients)
                message = {
                    'status': STATUS_NEW_PLAYER,
                    'data': clients
                }

                message_bytes = dumps(message)
                newClient.socket.send(message_bytes)

                newClient.status = CLIENT_STATUS_CONNECTED

                for broadcastClient in self.clients:
                    message = {
                        'status': STATUS_NEW_PLAYER,
                        'data': (newClient.player_id,)
                    }

                    message_bytes = dumps(message)
                    broadcastClient.socket.send(message_bytes)
    
    def handleConnectedClients(self):
        for client in self.clients:
            if client.status == CLIENT_STATUS_CONNECTED:
                self.players_pos[client.player_id] = client.player_pos
            else:
                del self.players_pos[client.player_id]

class ClientThread(Thread):
    def __init__(self, client_socket, address, players_pos) -> None:
        super().__init__()
        self.socket = client_socket
        self.address = address
        self.status = CLIENT_STATUS_NEW

        self.player_pos: tuple | None = (0, 0)
        self.player_size: tuple | None = (0, 0)
        self.player_id = str()
        self.get_player_id()

        self.players_pos = players_pos

    def __str__(self) -> str:
        return f"ID: {self.player_id} PORT: {self.address[1]}"

    def update_client_info(self) -> None:
        while self.status == CLIENT_STATUS_CONNECTED:
            try:
                data = self.socket.recv(64)
                if not data:
                    break
                self.player_pos, self.player_size = loads(data)

                self.socket.send(dumps(
                    {
                        'status': STATUS_PLAYERS_POSITIONS,
                        'data': self.players_pos
                    }
                ))

            except UnpicklingError as e:
                print(f"Error occurred while unpickling data: {e}")
            except ConnectionResetError:
                print(f"Client '{self.player_id}' disconnected abruptly.")
                break

    def get_player_id(self) -> None:
        try:
            data = self.socket.recv(64)
            self.player_id = loads(data)

        except UnpicklingError as e:
            print(f"Error occurred while unpickling data: {e}")
