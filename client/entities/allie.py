import pygame as pg
from fileio import get_sheet


class Allie(pg.sprite.Sprite):
    def __init__(self, player_id: str, player_pos: tuple) -> None:
        super().__init__()
        self.id = player_id
        self.sheet = get_sheet("000" + self.id)
        self.image = self.get_sprite()
        self.rect = self.image.get_rect(topleft=player_pos)

    def __str__(self) -> str:
        return f"{self.id}{self.rect.topleft}"

    def get_sprite(self, i: int = 0) -> pg.Surface:
        sprite = pg.Surface((16, 28), pg.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (0 + (i * 16), 0, 16 + (i * 16), 28))
        return pg.transform.scale(sprite, (16 * 3, 28 * 3))

    # def update(self) -> None:
    #     pass
