from pygame.sprite import Sprite
from pygame.image import load
from pygame.math import Vector2


class Mouse(Sprite):
	def __init__(self) -> None:
		super().__init__()
		self.image = load('client/assets/images/extras/mouse.png').convert_alpha()
		self.rect = self.image.get_rect()
		self.pos = Vector2()
		self.rel_rect = self.rect.copy()

	def __str__(self) -> str:
		return f"POSITION{self.rect.center} RELATIVE POSITION{self.rel_rect.center}"

	def update(self) -> None:
		self.rect.center = Vector2(self.pos)
