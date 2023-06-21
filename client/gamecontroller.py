from pickle import dumps, loads
from socket import socket, AF_INET6, SOCK_STREAM, SOCK_DGRAM, error, timeout, gaierror, herror

import pygame as pg
import pygame.freetype
from pygame.math import Vector2

from client.entities.allie import Allie
from client.entities.player import Player
from client.modules.debug import Debug
from client.modules.mouse import Mouse
from common.messagecode import MessageCode

SERVER_IP = "fe80::9c48:7cda:800:9f84%4"
SERVER_PORT = 5000


def generate_random_name() -> str:
    import random
    import string

    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(4))


class GameController:
    def __init__(self, width: int, height: int):
        # setup game parameters
        pg.init()
        pg.freetype.init()
        pg.event.set_grab(True)
        pg.display.set_caption(f'Window Size ({width}x{height})')
        pg.freetype.Font('client/assets/fonts/AlumniSansPinstripe-Regular.ttf', 24)
        pg.mouse.set_visible(False)

        # setup game
        self.screen = pg.display.set_mode((width, height), pg.RESIZABLE)
        self.clock = pg.time.Clock()

        # setup multiplayer
        self.tcp_socket = None
        self.udp_socket = None
        self.allies_group = pg.sprite.Group()
        self.online = False

        # setup game modules
        self.player = Player(generate_random_name(), (width // 2, height // 2))
        self.player_group = pg.sprite.GroupSingle(self.player)
        self.mouse = Mouse()
        self.mouse_group = pg.sprite.GroupSingle(self.mouse)
        self.debug = Debug()

        # game ready to run
        self.run = True

    def run_game(self) -> None:
        while self.run:
            if self.online:
                self.handle_server_communication()
            self.catch_events()
            self.update_game_state()
            self.draw()
            self.clock.tick(30)
        if self.online:
            self.tcp_socket.close()
        pygame.quit()
        exit()

    def catch_events(self) -> None:
        self.keyboard_control()
        for event in pygame.event.get():

            # quit game
            if event.type == pg.QUIT:
                self.run = False

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.run = False
                elif event.key == pg.K_c:
                    if not self.online:
                        self.initialize_server_connection(SERVER_IP, SERVER_PORT)

            # mouse movement
            elif event.type == pg.MOUSEMOTION:
                self.mouse.pos = Vector2(pg.mouse.get_pos())
                self.mouse.rect.center = self.mouse.pos

    def update_game_state(self) -> None:
        self.player_group.update()
        self.allies_group.update()
        pg.display.update()

    def handle_server_communication(self) -> None:

        message = {
            'code': MessageCode.PLAYER_UPDATE,
            'data': (self.player.rect.topleft, self.player.rect.size)
        }
        message_bytes = dumps(message)
        self.tcp_socket.send(message_bytes)

        self.handle_server_response(self.tcp_socket.recv(256))

    def handle_server_response(self, response_bytes) -> None:
        response = loads(response_bytes)

        if response['code'] == MessageCode.PLAYERS_POSITIONS:
            for allie in self.allies_group:
                allie.rect.x = response['data'][allie.id][0]
                allie.rect.y = response['data'][allie.id][1]

        elif response['code'] == MessageCode.NEW_PLAYER:
            for player in response['data']:
                new_player = Allie(player)
                self.allies_group.add(new_player)
            message = {
                'code': MessageCode.CHECK_CURRENT_PLAYERS,
                'data': tuple(p.id for p in self.allies_group)
            }
            message_bytes = dumps(message)
            self.tcp_socket.send(message_bytes)

        elif response['code'] == MessageCode.PLAYER_UPDATE_INFO:
            message = {
                'code': MessageCode.PLAYER_UPDATE_INFO,
                'data': {'player_id': self.player.id}
            }
            message_bytes = dumps(message)
            self.tcp_socket.send(message_bytes)

    def draw(self) -> None:
        self.screen.fill((235, 235, 235))
        self.player_group.draw(self.screen)
        self.allies_group.draw(self.screen)
        self.mouse_group.draw(self.screen)
        self.debug.display_info(f"FPS {int(self.clock.get_fps())}", 0)
        self.debug.display_info(f"PORT {self.tcp_socket.getsockname()[1] if self.tcp_socket else None}", 1)
        self.debug.display_info(f"SELF {self.player}", 2)
        self.debug.display_info(f"ALLIES {' | '.join(str(allie) for allie in self.allies_group)}", 3)

    def keyboard_control(self) -> None:
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.player.direction.y = -1
        elif keys[pg.K_s]:
            self.player.direction.y = 1
        else:
            self.player.direction.y = 0

        if keys[pg.K_a]:
            self.player.direction.x = -1
        elif keys[pg.K_d]:
            self.player.direction.x = 1
        else:
            self.player.direction.x = 0

    def initialize_server_connection(self, ip, port) -> None:
        try:
            tcp_socket = socket(AF_INET6, SOCK_STREAM)
            tcp_socket.connect((ip, port))

            udp_socket = socket(AF_INET6, SOCK_DGRAM)
            udp_socket.bind(('', 0))

        except (error, timeout, gaierror, herror, ConnectionRefusedError) as e:
            print("Connection error:", e)
        except Exception as e:
            print("Unexpected error:", e)
        else:
            self.tcp_socket = tcp_socket
            self.udp_socket = udp_socket
            self.online = True

