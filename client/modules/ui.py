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
            "h_p": Rect(10, 10, 200, 20),
            "m_p": Rect(10, 34, 140, 20),
            "e_p": Rect((WIDTH - 400) // 2, HEIGHT - 20, 400, 10),
            "h_e": Rect(self.display_surface.get_width() - 210, 10, 200, 20)
        }

    def show_bar(self, entity, stat, bar, color) -> None:
        bar = self.bars[bar]
        rect(self.display_surface, "#222222", bar)

        stat_bar = bar.copy()
        stat_bar.width = bar.width * (entity.stats[stat] / entity.fixed_stats[stat])

        rect(self.display_surface, color, stat_bar)
        rect(self.display_surface, "#111111", bar, 3)

    def display(self) -> None:
        self.show_bar(self.player, "health", "h_p", "green")
        self.show_bar(self.player, "mana", "m_p", "blue")
        self.show_bar(self.player, "experience", "e_p", "purple")
        if self.player.selected_entity:
            self.show_bar(self.player.selected_entity, "health", "h_e", "green")

