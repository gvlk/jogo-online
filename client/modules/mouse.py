import pygame as pg
from pygame.math import Vector2


class Mouse(pg.sprite.Sprite):
	def __init__(self) -> None:
		super().__init__()
		sprite = pg.image.load('client/assets/images/extras/mouse.png')
		self.image = pg.transform.scale(sprite, Vector2(sprite.get_size()) * 2).convert_alpha()
		self.rect = self.image.get_rect()
		self.pos = Vector2()
		self.offset = Vector2()
