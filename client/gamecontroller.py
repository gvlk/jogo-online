from settings import FPS

from pickle import dumps, loads
from socket import socket, AF_INET6, SOCK_STREAM, SOCK_DGRAM, timeout, gaierror, herror
from threading import Thread
from time import sleep

import pygame as pg
import pygame.freetype

from client.entities.allie import Allie
from client.entities.player import Player
from client.entities.monster import Monster
from client.modules.world import World
from client.modules.camera import CameraGroup
from client.modules.debug import Debug
from client.modules.mouse import Mouse
from client.modules.ui import UI
from common.modules.messagecode import MessageCode


def generate_random_name() -> str:
    from random import choice
    from string import ascii_uppercase, ascii_lowercase
    u_consonants = "".join([c for c in ascii_uppercase if c not in "AEIOU"])
    l_consonants = "".join([c for c in ascii_lowercase if c not in "aeiou"])
    vowels = "aeiou"
    random_string = choice(u_consonants) + choice(vowels) + choice(l_consonants) + choice(vowels)
    return random_string


class GameController:
    # noinspection PyTypeChecker
    def __init__(self, width: int, height: int, ip: str, server_tcp_port: int, logger):
        # setup game parameters
        pg.init()
        pg.freetype.init()
        pg.event.set_grab(True)
        pg.display.set_caption(f"Window Size ({width}x{height})")
        pg.freetype.Font("client/assets/fonts/AlumniSansPinstripe-Regular.ttf", 24)
        pg.mouse.set_visible(False)

        # setup game
        self.screen = pg.display.set_mode((width, height))
        self.clock = pg.time.Clock()
        self.logger = logger

        # setup game modules
        self.world = World(0)
        self.player = Player(generate_random_name(), (1792, 1200))
        self.player_group = pg.sprite.Group((self.player, self.player.weapon))
        self.monster1 = Monster(generate_random_name(), (2150, 790), self.player)
        self.monster2 = Monster(generate_random_name(), (2250, 810), self.player)
        self.monster3 = Monster(generate_random_name(), (2350, 830), self.player)
        self.monster_group = pg.sprite.Group((self.monster1, self.monster2, self.monster3))
        self.camera = CameraGroup(self.player, self.world)
        self.camera.add((self.player_group, self.monster_group))

        self.mouse = Mouse()
        self.mouse_group = pg.sprite.GroupSingle(self.mouse)
        self.ui = UI(self.player)
        self.debug = Debug()

        # setup multiplayer
        self.ip = ip
        self.tcp_port = None
        self.udp_port = None
        self.tcp_socket = None
        self.udp_socket = None
        self.tcp_buffer_size = 1024
        self.udp_buffer_size = 256
        self.server_tcp_port = server_tcp_port
        self.server_udp_port = None
        self.allies_group = pg.sprite.Group()
        self.online = False
        self.tcp_socket_listener = Thread(target=self.listen_tcp_socket)

        # game ready to run
        self.run = True

    def run_game(self) -> None:
        while self.run:
            if self.online:
                self.handle_server_communication()
            self.catch_events()
            self.update_game_state()
            self.draw()
            self.clock.tick(FPS)
        if self.online:
            self.tcp_socket.close()
            self.udp_socket.close()
        pygame.quit()
        exit()

    def catch_events(self) -> None:
        for event in pygame.event.get():

            # quit game
            if event.type == pg.QUIT:
                self.run = False

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.run = False
                elif event.key == pg.K_c:
                    pass
                    # if not self.online:
                    #     self.initialize_server_connection(self.ip, self.server_tcp_port)

            elif event.type == pg.MOUSEMOTION:
                self.mouse.pos = pg.mouse.get_pos()
                self.mouse_group.update()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.select_entity()
                # elif event.button == 2:
                #     print("Middle mouse button clicked")
                # elif event.button == 3:
                #     print("Right mouse button clicked")

    def update_game_state(self) -> None:
        self.player_group.update(self.world.get_chunks, 2, 1)
        self.monster_group.update(self.world.get_chunks, 1, 1)
        self.allies_group.update()
        pg.display.update()

    def handle_server_communication(self) -> None:

        message = {
            "code": MessageCode.PLAYER_POS_UPDATE,
            "data": self.player.rect.topleft
        }
        message_bytes = dumps(message)
        self.udp_socket.sendto(message_bytes, (self.ip, self.server_udp_port))

        response_bytes, address = self.udp_socket.recvfrom(self.udp_buffer_size)
        response = loads(response_bytes)
        self.handle_server_response(response, address)

    # noinspection PyTypeChecker
    def handle_server_response(self, response, address) -> str:
        self.logger.debug(f"SERVER RESPONSE FROM PORT {address[1]}: {response}")

        if response["code"] == MessageCode.ALL_PLAYER_POS_UPDATE:
            for allie in self.allies_group:
                try:
                    allie.rect.topleft = response["data"][allie.id]
                except KeyError:
                    continue

        elif response["code"] == MessageCode.NEW_PLAYER:
            for player in response["data"]:
                player_id = player["id"]
                player_pos = player["pos"]
                self.allies_group.add(Allie(player_id, player_pos))
            message = {
                "code": MessageCode.CHECK_CURRENT_PLAYERS,
                "data": response["data"]
            }
            message_bytes = dumps(message)
            self.tcp_socket.send(message_bytes)

        elif response["code"] == MessageCode.PLAYER_UPDATE_INFO:
            message = {
                "code": MessageCode.PLAYER_UPDATE_INFO,
                "data": {
                    "id": self.player.id,
                    "pos": self.player.rect.topleft,
                    "size": self.player.rect.size
                }
            }
            message_bytes = dumps(message)
            self.tcp_socket.send(message_bytes)

        elif response["code"] == MessageCode.UDP_PORT_UPDATE:
            self.server_udp_port = response["data"]
            message = {
                "code": MessageCode.INFO_CHECK_PASSED,
                "data": None
            }
            message_bytes = dumps(message)
            self.tcp_socket.send(message_bytes)

        elif response["code"] == MessageCode.INFO_CHECK_PASSED:
            # all good
            pass

        else:
            self.logger.error(f"UNEXPECTED RESPONSE RECEIVED FROM PORT {address[1]}: {response}")

        return response["code"]

    def draw(self) -> None:
        self.camera.draw(True)
        self.mouse_group.draw(self.screen)
        self.ui.display()

        self.debug.display_info(f"FPS: {int(self.clock.get_fps())}", 0)
        self.debug.display_info(f"MOUSE: {self.mouse}", 1)
        self.debug.display_info(f"SELF: {self.player}", 2)
        self.debug.display_info(f"SELECTED: {self.player.selected_entity}", 3)
        self.debug.display_info(f"MONSTER: {self.monster1}", 4)
        self.debug.display_info(f"MONSTER: {self.monster2}", 5)

        # self.debug.display_info(f"ONLINE: {self.online}", 3)
        # self.debug.display_info(f"TCP_PORT: {self.tcp_port if self.tcp_socket else None}", 4)
        # self.debug.display_info(f"UDP_PORT: {self.udp_port if self.udp_socket else None}", 5)
        # self.debug.display_info(f"ALLIES: {' | '.join(str(allie) for allie in self.allies_group)}", 6)

    # game will try to connect to server 3 times
    def initialize_server_connection(self, ip, server_tcp_port) -> None:
        try:
            self.tcp_socket = socket(AF_INET6, SOCK_STREAM)
            self.tcp_socket.connect((ip, server_tcp_port))
            self.tcp_port = self.tcp_socket.getsockname()[1]

            response = loads(self.tcp_socket.recv(self.tcp_buffer_size))  # PLAYER_UPDATE_INFO
            self.handle_server_response(response, self.tcp_socket.getpeername())
            while True:
                response = loads(self.tcp_socket.recv(self.tcp_buffer_size))  # NEW_PLAYER or INFO_CHECK_PASSED
                response_code = self.handle_server_response(response, self.tcp_socket.getpeername())
                if response_code == MessageCode.INFO_CHECK_PASSED:
                    break

            response = loads(self.tcp_socket.recv(self.tcp_buffer_size))
            self.handle_server_response(response, self.tcp_socket.getpeername())

            self.udp_socket = socket(AF_INET6, SOCK_DGRAM)
            self.udp_socket.bind((self.ip, 0))
            self.udp_port = self.udp_socket.getsockname()[1]

        except (timeout, gaierror, herror, ConnectionRefusedError) as e:
            self.logger.error(f"Connection error: {e}")

        else:
            self.tcp_socket_listener.start()
            self.online = True

            self.logger.info(
                f"Server communication initiated | "
                f"Player: {self.player.id} | "
                f"Host: {self.ip} | "
                f"Local TCP Port: {self.tcp_port} | "
                f"Local UDP Port: {self.udp_port} | "
                f"Remote TCP Port: {self.tcp_socket.getpeername()[1]} | "
                f"Remote UDP Port: {self.server_udp_port}"
            )

    def listen_tcp_socket(self) -> None:
        while True:
            sleep(2)
            response = loads(self.tcp_socket.recv(self.tcp_buffer_size))
            self.handle_server_response(response, self.tcp_socket.getpeername())

    def select_entity(self) -> None:
        self.mouse.rel_rect.topleft = self.mouse.rect.topleft + self.camera.offset
        for entity in self.monster_group:
            if self.mouse.rel_rect.colliderect(entity.rect):
                self.player.selected_entity = entity
                return
        self.player.selected_entity = None
