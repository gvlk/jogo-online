from pickle import loads, dumps, UnpicklingError
from threading import Thread

from common.modules.logger import logger
from common.modules.messagecode import MessageCode
from server.modules.clientstatus import ClientStatus


class ClientThread(Thread):
    def __init__(self, ip: str, tcp_socket, tcp_port: int, udp_socket, udp_port: int) -> None:
        super().__init__()
        self.ip = ip
        self.tcp_socket = tcp_socket
        self.tcp_port = tcp_port
        self.udp_socket = udp_socket
        self.udp_port = udp_port
        self.tcp_buffer_size = 1024
        self.udp_buffer_size = 256
        self.status = ClientStatus.NEW
        self.logger = logger

        self.player_info = {
            "id": None,
            "pos": (0, 0),
            "size": (0, 0)
        }
        self.players_pos = dict()

        self.run = self.handle_client_communication

    def __str__(self) -> str:
        return f"ID {self.player_info['id']} | STATUS {self.status} | PORT TCP:{self.tcp_port} UDP:{self.udp_port}"

    def __repr__(self) -> str:
        return f"ID {self.player_info['id']} | PORT TCP:{self.tcp_port} UDP:{self.udp_port}"

    # initialization is made with TCP protocol
    def initialize(self, current_players) -> None:
        response = {
            "code": MessageCode.PLAYER_UPDATE_INFO,
            "data": None
        }
        response_bytes = dumps(response)
        self.tcp_socket.send(response_bytes)
        message_bytes = self.tcp_socket.recv(self.tcp_buffer_size)
        message = loads(message_bytes)
        self.handle_client_messages(message, self.tcp_socket.getpeername())

        for player in current_players:
            self.players_pos.update({player["id"]: player["pos"]})

        response = {
            "code": MessageCode.NEW_PLAYER,
            "data": current_players
        }
        response_bytes = dumps(response)
        self.tcp_socket.send(response_bytes)
        message_bytes = self.tcp_socket.recv(self.tcp_buffer_size)
        message = loads(message_bytes)
        self.handle_client_messages(message, self.tcp_socket.getpeername(), current_players)

        response = {
            "code": MessageCode.UDP_PORT_UPDATE,
            "data": self.udp_port
        }
        response_bytes = dumps(response)
        self.tcp_socket.send(response_bytes)
        message_bytes = self.tcp_socket.recv(self.tcp_buffer_size)
        message = loads(message_bytes)
        self.handle_client_messages(message, self.tcp_socket.getpeername())

        self.status = ClientStatus.OK

        # initiate udp communication. here, the Main Thread returns to handling clients.
        self.start()

    # main communication is made with UDP protocol
    def handle_client_communication(self) -> None:
        while True:
            try:
                message_bytes, address = self.udp_socket.recvfrom(self.udp_buffer_size)
                message = loads(message_bytes)
                self.handle_client_messages(message, address)

                response = {
                    "code": MessageCode.ALL_PLAYER_POS_UPDATE,
                    "data": self.players_pos
                }
                response_bytes = dumps(response)
                self.udp_socket.sendto(response_bytes, (self.ip, address[1]))

            except UnpicklingError as e:
                self.logger.warn(f"Error occurred while unpickling data: {e}")
            except ConnectionResetError:
                self.logger.error(f"Client '{self.player_info['id']}' disconnected abruptly.")
                break

    def handle_client_messages(self, message, address, current_players=None) -> str:
        self.logger.debug(f"CLIENT MESSAGE FROM PORT {address[1]}: {message}")

        if message["code"] == MessageCode.PLAYER_POS_UPDATE:
            self.player_info["pos"] = message["data"]

        elif message["code"] == MessageCode.PLAYER_UPDATE_INFO:
            for key, value in message["data"].items():
                self.player_info[key] = value

        elif message["code"] == MessageCode.CHECK_CURRENT_PLAYERS:
            unknown_players = list(current_players)
            while True:
                known_players = list(message["data"])
                for player in current_players:
                    if player in known_players:
                        unknown_players.remove(player)
                if unknown_players:
                    response = {
                        "code": MessageCode.NEW_PLAYER,
                        "data": tuple(unknown_players)
                    }
                    response_bytes = dumps(response)
                    self.tcp_socket.send(response_bytes)
                    message = loads(self.tcp_socket.recv(self.tcp_buffer_size))
                else:
                    response = {
                        "code": MessageCode.INFO_CHECK_PASSED,
                        "data": None
                    }
                    response_bytes = dumps(response)
                    self.tcp_socket.send(response_bytes)
                    break

        elif message["code"] == MessageCode.INFO_CHECK_PASSED:
            # all good
            pass

        else:
            self.logger.error(f"UNEXPECTED MESSAGE RECEIVED FROM PORT {address[1]}: {message}")

        return message["code"]

    def add_new_player(self, player) -> None:
        response = {
            "code": MessageCode.NEW_PLAYER,
            "data": player
        }
        response_bytes = dumps(response)
        self.tcp_socket.send(response_bytes)
        message_bytes = self.tcp_socket.recv(self.tcp_buffer_size)
        message = loads(message_bytes)
        self.handle_client_messages(message, self.tcp_socket.getpeername(), player)
