from client.entities.baseentity import BaseEntity
from client.entities.player import Player
from pygame.math import Vector2
from math import degrees, atan2


class Monster(BaseEntity):
    def __init__(self, monster_id: str, pos: tuple, player: Player) -> None:
        super().__init__(monster_id, pos, "client/assets/images/sprites/monster_spritesheet.png")
        self.level = 0
        self.attributes = {
            "stamina": 5,
            "strength": 0,
            "agility": 1,
            "intellect": 0,
            "critical_strike": 0,
            "haste": 1,
            "mastery": 0,
            "versatility": 0,
            "avoidance": 0,
            "indestructible": 0,
            "leech": 0,
            "speed": 4,
        }
        self.stats = {
            "health": round(self.attributes["stamina"] * 1.5),
            "mana": round(((self.level ** 2) * 5) + 15),
            "attack_power": round((self.attributes["strength"] + self.attributes["agility"]) / 2),
            "attack_speed": round(self.attributes["speed"] * self.attributes["haste"]),
            "melee_critical_strike": self.attributes["critical_strike"],
            "ranged_critical_strike": self.attributes["critical_strike"],
            "spell_power": round(self.attributes["intellect"] * 1),
            "mana_regeneration": 5,  # 5% of base mana per 5 seconds
            "spell_critical_strike": self.attributes["critical_strike"],
            "armor": 0,  # comes from gear
            "dodge": round(self.attributes["agility"] * 0.1),
            "parry": round(self.attributes["agility"] * 0.1),
            "block": 0,
            "experience": 1
        }
        self.current_stats = self.stats.copy()
        self.abilities = self.get_abilities(("001", "002", "003"))
        self.player = player
        self.status = "idle"
        self.notice_radius = 400

    def input(self) -> None:
        distance = self.get_distance_to_center(self.player)

        if distance <= self.melee_radius:
            self.direction = self.get_direction(self.player)
            self.status = "attack"
        elif distance <= self.notice_radius:
            self.direction = self.get_direction(self.player)
            self.status = "move"
        else:
            self.direction = Vector2()
            self.status = "idle"

        self.update_facing()

    def update_facing(self) -> None:
        angle = degrees(atan2(-self.direction.y, self.direction.x))

        if -45 <= angle < 45:
            self.facing = 3
        elif 45 <= angle < 135:
            self.facing = 1
        elif 135 <= angle < 225:
            self.facing = 2
        else:
            self.facing = 0

    def move(self, speed: int, obstacles) -> None:
        if self.status != "idle":
            super().move(self.attributes["speed"], obstacles)
