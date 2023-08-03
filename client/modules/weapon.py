from pygame.sprite import Sprite
from pygame.surface import Surface
from pygame.rect import Rect
from pygame.math import Vector2
from json import loads
from pygame.image import load



class Weapon(Sprite):
    def __init__(self, weapon_id) -> None:
        super().__init__()
        self.info = self.get_info(weapon_id)
        self.attributes = self.info.copy()
        del self.attributes["graphic"]

        self.image = Surface((40, 40))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()

    @staticmethod
    def get_info(weapon_id: int) -> dict:
        with open("common/weapons.json", "r") as weapons_file:
            weapons: dict = loads(weapons_file.read())
        return weapons[f"00{weapon_id}"]
