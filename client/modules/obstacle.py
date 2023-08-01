from pygame.sprite import Sprite
from pygame import Surface


def get_random_color() -> str:
    from random import choice
    colors = ("red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "cyan")
    return choice(colors)


class StaticObstacle(Sprite):
    def __init__(self, pos: tuple, size: tuple) -> None:
        super().__init__()
        self.image = Surface(size)
        self.image.fill(get_random_color())
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
