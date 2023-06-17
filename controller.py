import pygame as pg
import pygame.freetype
from pygame.math import Vector2

from entities.player import Player
from modules.debug import Debug
from modules.mouse import Mouse


class GameController:
    def __init__(self, width: int, height: int):
        # setup game parameters
        pg.init()
        pg.freetype.init()
        pg.event.set_grab(True)
        pg.display.set_caption(f'Window Size ({width}x{height})')
        pg.freetype.Font('assets/fonts/AlumniSansPinstripe-Regular.ttf', 24)
        pg.mouse.set_visible(False)

        # setup game
        self.screen = pg.display.set_mode((width, height), pg.RESIZABLE)
        self.clock = pg.time.Clock()

        # setup game modules
        self.player = Player((width // 2, height // 2))
        self.player_group = pg.sprite.GroupSingle(self.player)
        self.mouse = Mouse()
        self.mouse_group = pg.sprite.GroupSingle(self.mouse)
        self.debug = Debug()

        # setup game variables

        # initialize game
        self.run = True
        self.run_game()

    def run_game(self) -> None:
        while self.run:
            self.catch_events()
            self.tick_world()
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

            # mouse movement
            elif event.type == pg.MOUSEMOTION:
                self.mouse.pos = Vector2(pg.mouse.get_pos())
                self.mouse.rect.center = self.mouse.pos

    def tick_world(self) -> None:

        # update background
        self.screen.fill((235, 235, 235))

        # display player
        self.player_group.update()
        self.player_group.draw(self.screen)

        # mouse
        self.mouse_group.draw(self.screen)

        # debug
        self.debug.display(f'FPS {int(self.clock.get_fps())}', 1)

        # run tick
        pg.display.update()
        self.clock.tick(30)
