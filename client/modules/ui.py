from settings import *
from pygame import display
from pygame.font import Font
from pygame.rect import Rect
from pygame.draw import rect


class UI:
    def __init__(self, player) -> None:
        self.display_surface = display.get_surface()
        self.font = Font(UI_FONT, UI_FONT_SIZE)

        self.player = player
        self.bars = {
            "health": Rect(10, 10, 200, 20),
            "mana": Rect(10, 34, 140, 20),
            "experience": Rect((WIDTH - 400) // 2, HEIGHT - 20, 400, 10)
        }

    def show_bar(self, stat, color) -> None:
        bar = self.bars[stat]
        rect(self.display_surface, "#222222", bar)

        stat_bar = bar.copy()
        stat_bar.width = bar.width * (self.player.current_stats[stat] / self.player.stats[stat])

        rect(self.display_surface, color, stat_bar)
        rect(self.display_surface, "#111111", bar, 3)

    def display(self) -> None:
        self.show_bar("health", "red")
        self.show_bar("mana", "blue")
        self.show_bar("experience", "purple")
