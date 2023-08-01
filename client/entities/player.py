from client.entities.baseentity import BaseEntity


class Player(BaseEntity):
    def __init__(self, player_id: str, pos: tuple) -> None:
        super().__init__(player_id, pos, "client/assets/images/sprites/player_spritesheet.png")
