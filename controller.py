import pygame as pg
import pygame.freetype
from pygame.math import Vector2

from modules.mouse import Mouse
from modules.debug import Debug


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
        self.mouse = Mouse()
        self.mouse_group = pg.sprite.GroupSingle(self.mouse)
        self.debug = Debug()

        # setup game variables

        # initialize game
        self.initialize_world()

    def initialize_world(self) -> None:
        while True:
            self.catch_events()
            self.tick_world()

    def catch_events(self) -> None:
        for event in pygame.event.get():

            # quit game
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # key press
            elif event.type == pygame.KEYDOWN:
                self.catch_keypress(event)

            # mouse movement
            elif event.type == pygame.MOUSEMOTION:
                self.mouse.pos = Vector2(pg.mouse.get_pos())

    def catch_keypress(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()

    def tick_world(self) -> None:

        self.screen.fill((240, 240, 240))

        # mouse
        self.mouse.rect.center = self.mouse.pos
        self.mouse_group.draw(self.screen)

        # debug
        self.debug.display(f'FPS {int(self.clock.get_fps())}', 1)

        # run tick
        pg.display.update()
        self.clock.tick(60)
