from client.entities.baseentity import BaseEntity
from client.modules.weapon import Weapon
from pygame import key, K_w, K_a, K_s, K_d, K_1, K_2


class Player(BaseEntity):
    def __init__(self, player_id: str, pos: tuple) -> None:
        super().__init__("000" + player_id, pos)
        self.weapon = Weapon(1)
        self.level = 0
        self.attributes = {
            "stamina": 25,
            "strength": 5,
            "agility": 5,
            "intellect": 5,
            "critical_strike": 1,
            "haste": 1,
            "mastery": 0,
            "versatility": 0,
            "avoidance": 0,
            "indestructible": 0,
            "leech": 0,
            "speed": 6,
        }
        self.stats = {
            "health": round(self.attributes["stamina"] * 1.5),
            "mana": round(((self.level ** 2) * 5) + 15),
            "attack_power": round((self.attributes["strength"] + self.attributes["agility"]) / 2),
            "attack_speed": round(self.weapon.attributes["speed"] * self.attributes["haste"]),
            "melee_critical_strike": self.attributes["critical_strike"] + (self.attributes["agility"] / 2),
            "ranged_critical_strike": self.attributes["critical_strike"] + (self.attributes["agility"] / 2),
            "spell_power": round(self.attributes["intellect"] * 1),
            "mana_regeneration": 5,  # 5% of base mana per 5 seconds
            "spell_critical_strike": self.attributes["critical_strike"],
            "armor": 3,  # comes from gear
            "dodge": round(self.attributes["agility"] * 0.1),
            "parry": round(self.attributes["agility"] * 0.1),
            "block": 0,
            "experience": 1
        }
        self.fixed_stats = self.stats.copy()
        self.abilities = self.get_abilities(("001", "002", "003"))
        self.ability_methods = self.get_ability_methods()
        self.selected_entity: BaseEntity | None = None
        self.set_melee_radius(80)

    def input(self) -> None:
        keys = key.get_pressed()

        if keys[K_w]:
            self.direction.y = -1
            self.facing = 1
        elif keys[K_s]:
            self.direction.y = 1
            self.facing = 0
        else:
            self.direction.y = 0

        if keys[K_a]:
            self.direction.x = -1
            self.facing = 2
        elif keys[K_d]:
            self.direction.x = 1
            self.facing = 3
        else:
            self.direction.x = 0

        # mouse_buttons = mouse.get_pressed(3)
        # if mouse_buttons[0]:
        #     print("CLICK BOTAO ESQUERDO")
        # elif mouse_buttons[2]:
        #     print("CLICK BOTAO DIREITO")
        # elif mouse_buttons[1]:
        #     print("CLICK BOTAO MEIO")

        if keys[K_1] and not self.abilities["002"]["using"]:
            self.use_ability("002", self.selected_entity)
        elif keys[K_2] and not self.abilities["003"]["using"]:
            self.use_ability("003", self.selected_entity)

    def act(self) -> None:
        if self.selected_entity and not self.abilities["001"]["using"]:
            self.use_ability("001", self.selected_entity)

    def frostbolt_002(self) -> tuple:
        pass

    def fire_blast_003(self) -> tuple:
        pass
