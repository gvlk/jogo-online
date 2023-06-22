from socket import socket, AF_INET6, SOCK_STREAM, SOCK_DGRAM
from threading import Thread, Lock
from time import sleep

from common.modules.logger import logger
from server.modules.clientstatus import ClientStatus
from server.modules.clientthread import ClientThread

MAX_CLIENTS = 6


class ServerController:
    # SOCK_STREAM is a constant that represents the tcp_socket type for TCP connection
    # SOCK_DGRAM is a constant that represents the tcp_socket type for UDP connection
    # AF_INET6 is a constant that represents the address family for IPv6
    def __init__(self, ip: str, tcp_port: int) -> None:
        self.ip = ip
        self.tcp_port = tcp_port
        self.tcp_socket = socket(AF_INET6, SOCK_STREAM)

        self.max_clients = MAX_CLIENTS
        self.clients = {ClientStatus.OK: list(), ClientStatus.NEW: list()}
        self.rooms = set()

        self.clients_lock = Lock()

        self.listener_thread = Thread(target=self.start_listener)
        self.debug_thread = Thread(target=self.current_clients_debug)

        self.logger = logger

    def run_server(self) -> None:
        self.listener_thread.start()
        self.debug_thread.start()

        while True:
            self.handle_clients()

    def start_listener(self) -> None:
        self.tcp_socket.bind((self.ip, self.tcp_port))
        self.tcp_socket.listen(4)

        self.logger.info(f"Server listening on {self.ip}:{self.tcp_port}")

        udp_sockets = set()

        try:

            for _ in range(self.max_clients):
                udp_socket = socket(AF_INET6, SOCK_DGRAM)
                udp_socket.bind((self.ip, 0))
                udp_sockets.add(udp_socket)

            while True:
                client_tcp_socket, client_address = self.tcp_socket.accept()

                if self.get_client_n() >= self.max_clients:
                    self.logger.warn("Maximum number of clients reached. Connection rejected.")
                    client_tcp_socket.close()
                    continue

                client_udp_socket = udp_sockets.pop()

                ip = client_address[0]
                client_tcp_port = client_address[1]
                server_udp_port = client_udp_socket.getsockname()[1]

                client_thread = ClientThread(
                    ip,
                    client_tcp_socket,
                    client_tcp_port,
                    client_udp_socket,
                    server_udp_port,
                )
                self.clients[ClientStatus.NEW].append(client_thread)

                self.logger.info(
                    f"New client connected | "
                    f"Host: {ip} | "
                    f"Client TCP Port: {client_tcp_port} | "
                    f"Client UDP Port: To be received | "
                    f"Server TCP Port: {self.tcp_port} | "
                    f"Server UDP Port: {server_udp_port} | "
                    f"Flow Info: {client_address[2]} | "
                    f"Scope ID: {client_address[3]}"
                )

        finally:
            self.tcp_socket.close()
            for udp_socket in udp_sockets:
                udp_socket.close()

    def handle_clients(self) -> None:
        def handle_connected_client(client_ok) -> None:
            for other_client in self.clients[ClientStatus.OK]:
                if other_client != client_ok:
                    client_ok.players_pos[other_client.player_info["id"]] = other_client.player_info["pos"]

        def handle_pending_clients(client_new, current_clients) -> None:
            client_new.initialize(tuple(c.player_info for c in current_clients))
            for broadcast_client in current_clients:
                broadcast_client.add_new_player((client_new.player_info,))
            self.clients[ClientStatus.NEW].remove(client_new)
            self.clients[ClientStatus.OK].append(client_new)

        with self.clients_lock:
            try:
                for client in self.clients[ClientStatus.OK]:
                    handle_connected_client(client)

                for client in self.clients[ClientStatus.NEW]:
                    handle_pending_clients(client, tuple(self.clients[ClientStatus.OK]))
            except EOFError as e:
                self.logger.error(f"EOFError {e.args}")

    def get_client_n(self) -> int:
        n = int()
        for status in self.clients:
            for _ in status:
                n += 1
        return n

    def current_clients_debug(self) -> None:
        while True:
            sleep(2)
            self.logger.debug(f"CLIENTS: {self.clients}")
