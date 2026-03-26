"""Pygame stats panel — renders player HP/MP/XP bars and stats."""

import pygame
from pygame_ui.colors import get_rgb
from pygame_ui.font_manager import FontManager


class PgStatsPanel:
    def render(self, player, font: FontManager, width: int, height: int) -> pygame.Surface:
        """Render the character stats panel to a surface."""
        surface = pygame.Surface((width, height))
        surface.fill((10, 10, 20))
        y = 4

        # Name and class
        name = getattr(player, "name", "Hero")
        player_class = getattr(player, "player_class", "Adventurer")
        level = getattr(player, "level", 1)

        self._draw_text(surface, font, f" {name}", get_rgb("bright_white"), y); y += font.char_height
        self._draw_text(surface, font, f" {player_class} Lv.{level}", get_rgb("yellow"), y); y += font.char_height * 2

        # HP bar
        current_hp = getattr(player, "current_hp", 0)
        max_hp = getattr(player, "max_hp", 1)
        hp_pct = current_hp / max_hp if max_hp > 0 else 0
        hp_color = get_rgb("bright_green") if hp_pct > 0.6 else get_rgb("yellow") if hp_pct > 0.3 else get_rgb("bright_red")
        self._draw_bar(surface, font, "HP", hp_pct, hp_color, f"{current_hp}/{max_hp}", y, width)
        y += font.char_height + 2

        # MP bar
        current_mp = getattr(player, "current_mp", 0)
        max_mp = getattr(player, "max_mp", 1)
        mp_pct = current_mp / max_mp if max_mp > 0 else 0
        self._draw_bar(surface, font, "MP", mp_pct, get_rgb("bright_blue"), f"{current_mp}/{max_mp}", y, width)
        y += font.char_height + 2

        # XP bar
        xp = getattr(player, "xp", 0)
        xp_next = getattr(player, "xp_to_next", 100)
        xp_pct = xp / xp_next if xp_next > 0 else 0
        self._draw_bar(surface, font, "XP", xp_pct, get_rgb("bright_green"), f"{xp}/{xp_next}", y, width)
        y += font.char_height * 2

        # Core stats
        self._draw_text(surface, font, " --- Stats ---", get_rgb("grey50"), y); y += font.char_height
        stats = getattr(player, "stats", None)
        for stat_name, color_name in [("STR","red"),("DEX","green"),("INT","blue"),("WIS","cyan"),("CON","yellow"),("CHA","magenta")]:
            val = getattr(stats, stat_name, 0) if stats and not isinstance(stats, dict) else (stats or {}).get(stat_name, 0)
            self._draw_text(surface, font, f" {stat_name}: {val:>3}", get_rgb(color_name), y)
            y += font.char_height

        # Combat stats
        y += 4
        atk = getattr(player, "attack", 0)
        dfn = getattr(player, "defense", 0)
        self._draw_text(surface, font, f" ATK:{atk} DEF:{dfn}", get_rgb("bright_white"), y); y += font.char_height
        crit = getattr(player, "crit_chance", 0)
        dodge = getattr(player, "dodge_chance", 0)
        self._draw_text(surface, font, f" CRT:{crit}% DDG:{dodge}%", get_rgb("white"), y); y += font.char_height * 2

        # Gold and floor
        gold = getattr(player, "gold", 0)
        floor = getattr(player, "floor", 1)
        self._draw_text(surface, font, f" Gold: {gold}", get_rgb("yellow"), y); y += font.char_height
        self._draw_text(surface, font, f" Floor: {floor}", get_rgb("white"), y)

        # Draw border
        pygame.draw.rect(surface, get_rgb("cyan"), surface.get_rect(), 1)
        # Title
        title_surf = font.render_text(" Character ", get_rgb("bright_white"), (10, 10, 20))
        surface.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 0))

        return surface

    def _draw_text(self, surface, font, text, color, y, x=0):
        text_surf = font.render_text(text, color)
        surface.blit(text_surf, (x, y))

    def _draw_bar(self, surface, font, label, pct, color, text, y, panel_width):
        # Label
        label_surf = font.render_text(f" {label} ", get_rgb("bright_white"))
        surface.blit(label_surf, (0, y))
        bar_x = label_surf.get_width()
        bar_width = panel_width - bar_x - font.char_width * 8
        # Bar background
        pygame.draw.rect(surface, (30, 30, 30), (bar_x, y + 2, bar_width, font.char_height - 4))
        # Bar fill
        fill_width = int(pct * bar_width)
        if fill_width > 0:
            pygame.draw.rect(surface, color, (bar_x, y + 2, fill_width, font.char_height - 4))
        # Text
        text_surf = font.render_text(f" {text}", get_rgb("bright_white"))
        surface.blit(text_surf, (bar_x + bar_width + 2, y))
