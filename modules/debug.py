import pygame as pg


class Debug:
	def __init__(self) -> None:
		self.display_surf = pg.display.get_surface()
		self.font = pg.font.Font('assets/fonts/IBMPlexMono-Regular.ttf', 12)

	def display_info(self, info, y: int) -> None:
		debug_surf = self.font.render(str(info), True, 'Black')
		debug_rect = debug_surf.get_rect(topleft=(20, 110 + (y * 20)))
		self.display_surf.blit(debug_surf, debug_rect)
