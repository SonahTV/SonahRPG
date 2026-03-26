"""Pygame menu — selectable list with keyboard navigation."""

import pygame
from pygame_ui.colors import get_rgb
from pygame_ui.font_manager import FontManager


class PgMenu:
    def __init__(self, title: str, items: list[str], descriptions: list[str] = None):
        self.title = title
        self.items = items
        self.descriptions = descriptions or []
        self.selected_index = 0

    def move_up(self):
        self.selected_index = (self.selected_index - 1) % len(self.items)

    def move_down(self):
        self.selected_index = (self.selected_index + 1) % len(self.items)

    def get_selected(self) -> str:
        return self.items[self.selected_index]

    def render(self, font: FontManager, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill((10, 10, 20))

        # Title
        title_surf = font.render_text(f" {self.title} ", get_rgb("bright_cyan"))
        surface.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 4))

        y = 4 + font.char_height * 2
        for i, item in enumerate(self.items):
            if i == self.selected_index:
                # Highlight bar
                pygame.draw.rect(surface, (40, 40, 60), (4, y, width - 8, font.char_height))
                prefix = "► "
                color = get_rgb("bright_yellow")
            else:
                prefix = "  "
                color = get_rgb("white")

            text = f"{prefix}{item}"
            text_surf = font.render_text(text, color)
            surface.blit(text_surf, (8, y))

            # Description if available
            if i < len(self.descriptions) and self.descriptions[i]:
                desc_surf = font.render_text(f"  {self.descriptions[i]}", get_rgb("grey50"))
                surface.blit(desc_surf, (width // 2, y))

            y += font.char_height + 2

        pygame.draw.rect(surface, get_rgb("bright_cyan"), surface.get_rect(), 1)
        return surface
