from pygame import Surface, SRCALPHA
from pygame.rect import Rect
from pygame.image import load
from pygame.transform import scale
from pygame.sprite import Sprite
from pygame.math import Vector2
from pygame.time import get_ticks
from pygame.draw import circle
from pygame.mask import from_surface, Mask
from client.modules.weapon import Weapon
from json import loads


class BaseEntity(Sprite):
    def __init__(self, entity_id: str, pos: tuple, spritesheet: str) -> None:
        super().__init__()
        self.id = entity_id
        self.sheet = load(spritesheet).convert_alpha()
        self.sprite_w = self.sheet.get_size()[0] // 4
        self.sprite_h = self.sheet.get_size()[1]
        self.image = self.get_sprite(0)
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, -14)

        self.melee_radius = 80
        self.melee_radius_surface: Surface | None = None
        self.melee_radius_rect: Rect | None = None
        self.melee_radius_mask: Mask | None = None
        self.melee_box_surface: Surface | None = None
        self.melee_box_rect: Rect | None = None
        self.melee_box_mask: Mask | None = None
        self.set_melee_radius(self.melee_radius)

        self.direction = Vector2()
        self.facing = 0

        self.attributes = dict()
        self.abilities = dict()
        self.stats = dict()
        self.weapon: Weapon | None = None

    def __str__(self) -> str:
        return f"{self.id} {self.rect.topleft} {self.direction}"

    def get_sprite(self, i: int) -> Surface:
        sprite = Surface((self.sprite_w, self.sprite_h), SRCALPHA)
        sprite.blit(
            self.sheet,
            (0, 0),
            (0 + (i * self.sprite_w), 0, self.sprite_w + (i * self.sprite_w), self.sprite_h)
        )
        return scale(sprite, (self.sprite_w * 2, self.sprite_h * 2))

    @staticmethod
    def get_abilities(abilities: tuple) -> dict:
        entity_abilities = dict()
        with open("common/abilities.json", "r") as abilities_file:
            abilities_data: dict = loads(abilities_file.read())
        for ability in abilities:
            entity_abilities[ability] = abilities_data[ability].copy()
            entity_abilities[ability]["using"] = False
            entity_abilities[ability]["use_time"] = 0

        return entity_abilities

    def cooldowns(self, ability) -> None:
        if get_ticks() - self.abilities[ability]["use_time"] >= self.abilities[ability]["cooldown"]:
            self.abilities[ability]["using"] = False
            if self.weapon:
                self.weapon.destroy_hitbox()

    def use_ability(self, ability) -> None:
        self.abilities[ability]["using"] = True
        self.abilities[ability]["use_time"] = get_ticks()

    def input(self) -> None:
        pass

    def animate(self) -> None:
        self.image = self.get_sprite(self.facing)
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def move(self, speed: int, obstacles) -> None:
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.obstacle_collision(0, obstacles)
        self.hitbox.y += self.direction.y * speed
        self.obstacle_collision(1, obstacles)
        self.rect.center = self.hitbox.center

    def obstacle_collision(self, direction: int, sprites):
        for sprite in sprites:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 0:
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    elif self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right

                elif direction == 1:
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    elif self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def in_melee_range(self, entity) -> bool:
        self.melee_radius_rect.center = self.rect.center
        entity.melee_box_rect.center = entity.rect.center
        offset = (
            entity.melee_box_rect.left - self.melee_radius_rect.left,
            entity.melee_box_rect.top - self.melee_radius_rect.top
        )
        return bool(self.melee_radius_mask.overlap(entity.melee_box_mask, offset))

    def set_melee_radius(self, radius) -> None:
        self.melee_radius_surface = Surface((radius * 2, radius * 2), SRCALPHA)
        circle(self.melee_radius_surface, (255, 0, 0, 128), (radius, radius), radius)
        self.melee_box_surface = Surface(self.hitbox.size, SRCALPHA)
        self.melee_box_surface.fill((0, 0, 255, 128))

        self.melee_radius_mask = from_surface(self.melee_radius_surface)
        self.melee_box_mask = from_surface(self.melee_box_surface)

        self.melee_radius_rect = self.melee_radius_surface.get_rect(center=(0, 0))
        self.melee_box_rect = self.melee_box_surface.get_rect(center=(0, 0))

    def get_distance_to_center(self, entity) -> float:
        return (Vector2(self.rect.center) - Vector2(entity.rect.center)).magnitude()

    def get_direction(self, entity) -> Vector2:
        if self.get_distance_to_center(entity) > 0:
            return (Vector2(entity.rect.center - Vector2(self.rect.center))).normalize()
        return Vector2()

    def update(self, obstacles) -> None:
        self.input()
        for ability in self.abilities:
            if self.abilities[ability]["using"]:
                self.cooldowns(ability)
        self.animate()
        self.move(self.attributes["speed"], obstacles)
