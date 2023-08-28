from pygame.sprite import Sprite
from pygame.surface import Surface
from pygame.rect import Rect

from settings import TILESIZE


def get_random_color() -> str:
    from random import choice
    colors = ("red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "cyan")
    return choice(colors)


class StaticObstacle(Sprite):
    def __init__(self, pos: tuple, surface: Surface) -> None:
        super().__init__()
        self.image = surface
        if self.image.get_height() > TILESIZE:
            pos = (pos[0], pos[1] - TILESIZE)
            self.hitbox_yoffset = self.image.get_height() // 2
        else:
            self.hitbox_yoffset = 0
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = Rect(
            self.rect.left,
            self.rect.top + self.hitbox_yoffset,
            self.image.get_width(),
            self.rect.h - self.hitbox_yoffset
        )


