from pygame.sprite import Sprite
from pygame.surface import Surface


class Weapon(Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.image = Surface((40, 40))
        self.rect = self.image.get_rect(center=pos)
