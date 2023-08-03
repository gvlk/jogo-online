from pygame.sprite import Group
from pygame import display
from pygame.surface import Surface
from pygame.math import Vector2
from pygame.draw import rect
from typing import Optional


class CameraGroup(Group):
    def __init__(self, player) -> None:
        super().__init__()
        self.display_surface = display.get_surface()
        self.half_width = self.display_surface.get_width() // 2
        self.half_height = self.display_surface.get_height() // 2
        self.offset = Vector2()

        self.player = player

    def draw(self, surface: Surface, debug=False, bgsurf: Optional[Surface] = None) -> None:
        self.update_offset()
        for sprite in sorted(self.sprites(), key=lambda sprite_: sprite_.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

            if debug and hasattr(sprite, "melee_radius_surface"):
                offset_hitbox = sprite.hitbox.copy()
                offset_rect = sprite.rect.copy()
                offset_melee_radius = sprite.melee_radius_rect.copy()

                offset_hitbox.topleft -= self.offset
                offset_rect.topleft -= self.offset
                offset_melee_radius.topleft -= self.offset

                rect(self.display_surface, (255, 255, 0), offset_hitbox, 1)
                rect(self.display_surface, (255, 0, 0), offset_rect, 1)
                self.display_surface.blit(sprite.melee_radius_surface, offset_melee_radius)

    def update_offset(self) -> Vector2:
        self.offset.x = self.player.rect.centerx - self.half_width
        self.offset.y = self.player.rect.centery - self.half_height
        return self.offset
