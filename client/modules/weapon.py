from pygame.sprite import Sprite
from pygame.surface import Surface
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

    def create_hitbox(self, player_rect, direction) -> None:
        self.image = Surface((40, 40))
        if direction == 0:
            self.rect = self.image.get_rect(midtop=player_rect.midbottom)
        elif direction == 1:
            self.rect = self.image.get_rect(midbottom=player_rect.midtop)
        elif direction == 2:
            self.rect = self.image.get_rect(midright=player_rect.midleft)
        else:
            self.rect = self.image.get_rect(midleft=player_rect.midright)

    def destroy_hitbox(self):
        self.image = Surface((40, 40))
        self.image.set_alpha(0)

    @staticmethod
    def get_info(weapon_id: int) -> dict:
        with open("common/weapons.json", "r") as weapons_file:
            weapons: dict = loads(weapons_file.read())
        return weapons[f"00{weapon_id}"]
