"""Pygame dialogue view — NPC portrait and dialogue text."""

import pygame
from pygame_ui.colors import get_rgb
from pygame_ui.font_manager import FontManager


class PgDialogueView:
    def render(self, npc_name: str, npc_art: str, dialogue_text: str,
               responses: list[str] | None, selected_response: int,
               font: FontManager, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill((10, 10, 20))

        # NPC portrait (ASCII art)
        y = 8
        if npc_art:
            for line in npc_art.split("\n"):
                art_surf = font.render_text(line, get_rgb("bright_cyan"))
                surface.blit(art_surf, (8, y))
                y += font.char_height

        # Name
        y += 4
        name_surf = font.render_text(f" {npc_name}", get_rgb("bright_yellow"))
        surface.blit(name_surf, (8, y))
        y += font.char_height * 2

        # Dialogue text (word-wrapped)
        max_chars = (width - 32) // font.char_width
        words = dialogue_text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 > max_chars:
                lines.append(current_line)
                current_line = word
            else:
                current_line = f"{current_line} {word}" if current_line else word
        if current_line:
            lines.append(current_line)

        for line in lines:
            line_surf = font.render_text(f"  {line}", get_rgb("bright_white"))
            surface.blit(line_surf, (8, y))
            y += font.char_height

        # Response options
        if responses:
            y += font.char_height
            for i, resp in enumerate(responses):
                if i == selected_response:
                    prefix = "► "
                    color = get_rgb("bright_yellow")
                else:
                    prefix = "  "
                    color = get_rgb("white")
                resp_surf = font.render_text(f"  {prefix}{resp}", color)
                surface.blit(resp_surf, (8, y))
                y += font.char_height

        pygame.draw.rect(surface, get_rgb("bright_cyan"), surface.get_rect(), 1)
        return surface
