from pickle import loads, dumps, UnpicklingError
from threading import Thread

from common.messagecode import MessageCode
from server.clientstatus import ClientStatus


class ClientThread(Thread):
    def __init__(self, client_socket, address, players_pos) -> None:
        super().__init__()
        self.tcp_socket = client_socket
        self.address = address
        self.status = ClientStatus.NEW

        self.player_pos = (0, 0)
        self.player_size = (0, 0)
        self.player_id = str()

        self.run = self.handle_client_communication

        self.players_pos = players_pos

    def __str__(self) -> str:
        return f"ID: {self.player_id} | PORT: {self.address[1]} | STATUS: {self.status}"

    # TODA INICIALIZAÇÃO É COM O TCP
    def initialize(self, current_players) -> None:
        response = {
            'code': MessageCode.PLAYER_UPDATE_INFO,
            'data': None
        }
        response_bytes = dumps(response)
        self.tcp_socket.send(response_bytes)
        self.handle_client_messages(self.tcp_socket.recv(512))

        response = {
            'code': MessageCode.NEW_PLAYER,
            'data': current_players
        }
        response_bytes = dumps(response)
        self.tcp_socket.send(response_bytes)
        self.handle_client_messages(self.tcp_socket.recv(128), current_players)

        self.status = ClientStatus.OK

    # ISSO AQUI VAI SER UDP
    def handle_client_communication(self) -> None:
        while True:

            try:
                self.handle_client_messages(self.tcp_socket.recv(128))

                response = {
                    'code': MessageCode.PLAYERS_POSITIONS,
                    'data': self.players_pos
                }
                response_bytes = dumps(response)
                self.tcp_socket.send(response_bytes)

            except UnpicklingError as e:
                print(f"Error occurred while unpickling data: {e}")
            except ConnectionResetError:
                print(f"Client '{self.player_id}' disconnected abruptly.")
                break

    def handle_client_messages(self, response_bytes, current_players=()) -> None:
        message = loads(response_bytes)

        if message['code'] == MessageCode.PLAYER_UPDATE:
            self.player_pos, self.player_size = message['data']

        elif message['code'] == MessageCode.PLAYER_UPDATE_INFO:
            self.player_id = message['data']['player_id']

        elif message['code'] == MessageCode.CHECK_CURRENT_PLAYERS:
            known_players = message['data']
            while not all(player in known_players for player in current_players):
                response = {
                    'code': MessageCode.NEW_PLAYER,
                    'data': current_players
                }
                response_bytes = dumps(response)
                self.tcp_socket.send(response_bytes)
                message = loads(self.tcp_socket.recv(128))
                if message['code'] == MessageCode.CHECK_CURRENT_PLAYERS:
                    known_players = message['data']

    def add_new_player(self, player_id) -> None:
        response = {
            'code': MessageCode.NEW_PLAYER,
            'data': (player_id,)
        }
        response_bytes = dumps(response)
        self.tcp_socket.send(response_bytes)
        self.handle_client_messages(self.tcp_socket.recv(128), (player_id,))
