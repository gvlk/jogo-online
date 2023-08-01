from pygame.sprite import Sprite
from pygame.image import load
from pygame.transform import scale
from pygame.math import Vector2


class Mouse(Sprite):
	def __init__(self) -> None:
		super().__init__()
		sprite = load('client/assets/images/extras/mouse.png')
		self.image = scale(sprite, Vector2(sprite.get_size()) * 2).convert_alpha()
		self.rect = self.image.get_rect()
		self.pos = Vector2()
		self.offset = Vector2()

	def __str__(self) -> str:
		return f"{self.rect.center}"

	def update(self) -> None:
		self.rect.center = Vector2(self.pos)
