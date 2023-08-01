from pygame import Surface, SRCALPHA, key, K_w, K_a, K_s, K_d, K_1
from pygame.image import load
from pygame.transform import scale
from pygame.sprite import Sprite
from pygame.math import Vector2
from pygame.time import get_ticks
from client.modules.weapon import Weapon


class BaseEntity(Sprite):
    def __init__(self, entity_id: str, pos: tuple, spritesheet: str, weapon: str = None) -> None:
        super().__init__()
        self.id = entity_id
        self.sheet = load(spritesheet).convert_alpha()
        self.sprite_w = self.sheet.get_size()[0] // 4
        self.sprite_h = self.sheet.get_size()[1]
        self.image = self.get_sprite(0)
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(0, -14)
        self.weapon = Weapon(pos) if weapon else None
        self.direction = Vector2()
        self.status = {
            "direction": 0
        }
        self.attacking = False
        self.attack_time = 0
        self.attack_cooldown = 400
        self.max_stats = {
            "hp": 100,
            "mp": 60,
            "atk": 10,
            "mgk": 6,
            "spd": 6,
            "exp": 500
        }
        self.stats = self.max_stats.copy()
        self.stats["exp"] = 0

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

    def input(self) -> None:
        keys = key.get_pressed()
        if keys[K_w]:
            self.direction.y = -1
            self.status["direction"] = 1
        elif keys[K_s]:
            self.direction.y = 1
            self.status["direction"] = 0
        else:
            self.direction.y = 0

        if keys[K_a]:
            self.direction.x = -1
            self.status["direction"] = 2
        elif keys[K_d]:
            self.direction.x = 1
            self.status["direction"] = 3
        else:
            self.direction.x = 0

        if keys[K_1] and not self.attacking:
            self.attacking = True
            self.attack_time = get_ticks()
            self.attack()

    def cooldowns(self) -> None:
        current_time = get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False

    def attack(self) -> None:
        print("ATACK!")

    def animate(self) -> None:
        self.image = self.get_sprite(self.status["direction"])
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

    def update(self, obstacles) -> None:
        self.input()
        self.cooldowns()
        self.animate()
        self.move(self.max_stats['spd'], obstacles)
