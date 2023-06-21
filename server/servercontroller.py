from pickle import dumps
from socket import socket, AF_INET6, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SOCK_DGRAM
from threading import Thread, Lock
from time import sleep

from server.clientstatus import ClientStatus
from server.clientthread import ClientThread
from common.messagecode import MessageCode

MAX_CLIENTS = 6


class ServerController:
    # SOCK_STREAM is a constant that represents the tcp_socket type for TCP connection
    # SOCK_DGRAM is a constant that represents the tcp_socket type for UDP connection
    # AF_INET6 is a constant that represents the address family for IPv6
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port

        self.tcp_socket = socket(AF_INET6, SOCK_STREAM)
        self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        self.udp_socket = socket(AF_INET6, SOCK_DGRAM)

        self.max_clients = MAX_CLIENTS
        self.clients = {ClientStatus.OK: list(), ClientStatus.NEW: list()}
        self.players_pos = dict()

        self.clients_lock = Lock()

        self.listener_thread = Thread(target=self.start_listener)
        self.debug_thread = Thread(target=self.debug)

    def run_server(self) -> None:
        self.listener_thread.start()
        self.debug_thread.start()

        while True:
            self.handle_clients()

    def start_listener(self) -> None:
        self.tcp_socket.bind((self.ip, self.port))
        self.tcp_socket.listen(4)

        print(f"Server listening on {self.ip}:{self.port}\n")

        while True:
            client_socket, client_address = self.tcp_socket.accept()

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

            self.clients[ClientStatus.NEW].append(client_thread)
            client_thread.start()

    def handle_clients(self) -> None:
        def handle_connected_client(client_ok) -> None:
            self.players_pos[client_ok.player_id] = client_ok.player_pos

        def handle_pending_clients(client_new, current_clients) -> None:
            client_new.initialize(tuple(c.player_id for c in current_clients))
            for broadcast_client in current_clients:
                broadcast_client.add_new_player(client_new.player_id)
            self.clients[ClientStatus.NEW].remove(client_new)
            self.clients[ClientStatus.OK].append(client_new)

        with self.clients_lock:
            for client in self.clients[ClientStatus.OK]:
                handle_connected_client(client)

            for client in self.clients[ClientStatus.NEW]:
                handle_pending_clients(client, self.clients[ClientStatus.OK])

    def debug(self) -> None:
        while True:
            sleep(3)
            print(
                "CLIENTS:", {k: [str(v) for v in value] for k, value in self.clients.items()}
            )
