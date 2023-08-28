from settings import TILESIZE, CHUNK_SIZE
from pygame.sprite import Group
from pygame import display
from pygame.rect import Rect
from pygame.math import Vector2
from pygame.draw import rect


class CameraGroup(Group):
    def __init__(self, player, world) -> None:
        super().__init__()
        self.display_surface = display.get_surface()
        self.half_width = self.display_surface.get_width() // 2
        self.half_height = self.display_surface.get_height() // 2
        self.offset = Vector2()

        self.player = player
        self.world = world

    def draw(self, debug=False, **kwargs) -> None:
        self.update_offset()
        offset_pos = self.world.ground_rect.topleft - self.offset
        self.display_surface.blit(self.world.ground_surface, offset_pos)
        sprites = Group((self.sprites(), self.player.obstacles))
        for sprite in sorted(sprites, key=lambda sprite_: sprite_.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

            if debug and hasattr(sprite, "melee_radius_surface"):
                self.debug_sprite(sprite)

        if debug:
            self.debug_chunks()

    def update_offset(self) -> Vector2:
        self.offset.x = self.player.rect.centerx - self.half_width
        self.offset.y = self.player.rect.centery - self.half_height
        return self.offset

    def debug_sprite(self, sprite):
        offset_hitbox = sprite.hitbox.copy()
        offset_rect = sprite.rect.copy()
        offset_melee_radius = sprite.melee_radius_rect.copy()

        offset_hitbox.topleft -= self.offset
        offset_rect.topleft -= self.offset
        offset_melee_radius.topleft -= self.offset

        rect(self.display_surface, (255, 0, 0), offset_rect, 1)
        rect(self.display_surface, (255, 255, 0), offset_hitbox, 1)
        self.display_surface.blit(sprite.melee_radius_surface, offset_melee_radius)

    def debug_chunks(self):
        for row_index, row in enumerate(self.world.chunks):
            for col_index, col in enumerate(row):
                offset_chunkbox = Rect(
                    row_index * TILESIZE * CHUNK_SIZE,
                    col_index * TILESIZE * CHUNK_SIZE,
                    TILESIZE * CHUNK_SIZE,
                    TILESIZE * CHUNK_SIZE
                )
                offset_chunkbox.topleft -= self.offset
                rect(self.display_surface, (0, 0, 255), offset_chunkbox, 1)
