"""Pygame log panel — scrolling message log with markup support."""

import pygame
from pygame_ui.colors import get_rgb
from pygame_ui.font_manager import FontManager
from pygame_ui.markup_parser import parse_markup


class PgLogPanel:
    def render(self, log_messages: list[str], font: FontManager, width: int, height: int, max_lines: int = 6) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill((10, 10, 15))

        recent = log_messages[-max_lines:] if len(log_messages) > max_lines else list(log_messages)

        y = 4
        for msg in recent:
            x = 4
            segments = parse_markup(f" {msg}")
            for text, color in segments:
                text_surf = font.render_text(text, color)
                surface.blit(text_surf, (x, y))
                x += text_surf.get_width()
            y += font.char_height

        # Border and title
        pygame.draw.rect(surface, get_rgb("yellow"), surface.get_rect(), 1)
        title = font.render_text(" Log ", get_rgb("bright_white"), (10, 10, 15))
        surface.blit(title, (width // 2 - title.get_width() // 2, 0))

        return surface
