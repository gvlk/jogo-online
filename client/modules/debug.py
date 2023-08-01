from settings import *
from pygame import display
from pygame.font import Font


class Debug:
	def __init__(self) -> None:
		self.display_surf = display.get_surface()
		self.font = Font(DEBUG_FONT, DEBUG_FONT_SIZE)

	def display_info(self, info, y: int) -> None:
		debug_surf = self.font.render(str(info), True, 'Black')
		debug_rect = debug_surf.get_rect(topleft=(20, 110 + (y * 20)))
		self.display_surf.blit(debug_surf, debug_rect)
