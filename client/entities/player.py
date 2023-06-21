import pygame as pg
from pygame.math import Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, player_id: str, pos: tuple) -> None:
        super().__init__()
        self.id = player_id
        self.sheet = pg.image.load("client/assets/images/sprites/player_spritesheet.png").convert_alpha()
        self.image = self.get_sprite()
        self.rect = self.image.get_rect(center=pos)
        self.direction = Vector2()
        self.attributes = {
            'spd': 5
        }

    def __str__(self) -> str:
        return f"{self.id}: {self.rect.topleft}"

    def get_sprite(self, i: int = 0) -> pg.Surface:
        sprite = pg.Surface((16, 28), pg.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (0 + (i * 16), 0, 16 + (i * 16), 28))
        return pg.transform.scale(sprite, (16 * 3, 28 * 3))

    def update(self) -> None:
        self.rect.center += self.direction * self.attributes['spd']
