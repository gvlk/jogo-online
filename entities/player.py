import pygame as pg
from pygame.math import Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, pos: tuple) -> None:
        super().__init__()
        self.sheet = pg.image.load("assets/images/sprites/player_spritesheet.png").convert_alpha()
        self.image = self.get_sprite()
        self.rect = self.image.get_rect(center=pos)
        self.direction = Vector2()
        self.attributes = {
            'spd': 5
        }

    def get_sprite(self, i: int = 0) -> pg.Surface:
        sprite = pg.Surface((16, 28), pg.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (0 + (i * 16), 0, 16 + (i * 16), 28))
        return pg.transform.scale(sprite, (16 * 3, 28 * 3))

    def input(self) -> None:
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.direction.y = -1
        elif keys[pg.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pg.K_a]:
            self.direction.x = -1
        elif keys[pg.K_d]:
            self.direction.x = 1
        else:
            self.direction.x = 0

    def update(self) -> None:
        self.input()
        self.rect.center += self.direction * self.attributes['spd']
