"""Pygame hotbar — keybinding hints bar at bottom of screen."""

import pygame
from pygame_ui.colors import get_rgb
from pygame_ui.font_manager import FontManager


class PgHotbar:
    def render(self, actions: list[tuple[str, str]], font: FontManager, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill((15, 15, 25))

        x = 8
        y = (height - font.char_height) // 2
        for key, label in actions:
            # Key in highlight
            key_surf = font.render_text(f"[{key}]", get_rgb("bright_yellow"), (40, 40, 20))
            surface.blit(key_surf, (x, y))
            x += key_surf.get_width() + 2
            # Label
            label_surf = font.render_text(f"{label} ", get_rgb("white"))
            surface.blit(label_surf, (x, y))
            x += label_surf.get_width() + font.char_width * 2

        pygame.draw.rect(surface, (50, 50, 70), surface.get_rect(), 1)
        return surface
