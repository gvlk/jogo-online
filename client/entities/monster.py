from client.entities.baseentity import BaseEntity


class Monster(BaseEntity):
    def __init__(self, monster_id: str, pos: tuple) -> None:
        super().__init__(monster_id, pos, "client/assets/images/sprites/monster_spritesheet.png")