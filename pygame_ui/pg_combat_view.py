"""Pygame combat view — enemy display, HP bars, and action menu."""

import math
import time
import pygame
from pygame_ui.colors import get_rgb
from pygame_ui.font_manager import FontManager


class PgCombatView:
    def __init__(self):
        self.selected_target = 0

    def render(self, player, enemies, combat_system, selected_action,
               font: FontManager, width: int, height: int,
               animation_manager=None, particles=None) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill((15, 5, 5))

        y = 8
        t = time.time()

        # Render enemies side by side
        enemy_width = min(width // max(len(enemies), 1) - 8, 250)
        x_offset = 8

        for i, enemy in enumerate(enemies):
            alive = enemy.is_alive() if hasattr(enemy, "is_alive") else True
            ex = x_offset + i * (enemy_width + 8)
            ey = y

            # Enemy panel background
            bg_color = (30, 30, 15) if i == self.selected_target and alive else (20, 10, 10)
            border_color = (255, 255, 85) if i == self.selected_target and alive else (170, 0, 0)
            if not alive:
                bg_color = (15, 15, 15)
                border_color = (60, 60, 60)

            pygame.draw.rect(surface, bg_color, (ex, ey, enemy_width, 120))
            pygame.draw.rect(surface, border_color, (ex, ey, enemy_width, 120), 1)

            # ASCII art
            ascii_art = getattr(enemy, "ascii_art", None) or "  /\\_/\\\n ( o.o )\n  > ^ <"
            art_color = (60, 60, 60) if not alive else get_rgb("bright_white")
            art_y = ey + 4
            for line in ascii_art.split("\n"):
                art_surf = font.render_text(line, art_color)
                surface.blit(art_surf, (ex + 4, art_y))
                art_y += font.char_height

            # Name and HP
            name = getattr(enemy, "name", "Enemy")
            level = getattr(enemy, "level", 1)
            name_surf = font.render_text(f"{name} Lv.{level}", get_rgb("bright_white") if alive else (60,60,60))
            surface.blit(name_surf, (ex + 4, ey + 80))

            # HP bar
            max_hp = getattr(enemy, "max_hp", 1)
            current_hp = max(0, getattr(enemy, "current_hp", 0))
            hp_pct = current_hp / max_hp if max_hp > 0 else 0
            bar_w = enemy_width - 16
            bar_y = ey + 96
            pygame.draw.rect(surface, (30, 30, 30), (ex + 8, bar_y, bar_w, 10))
            fill_color = (85, 255, 85) if hp_pct > 0.6 else (255, 255, 85) if hp_pct > 0.3 else (255, 85, 85)
            if not alive: fill_color = (60, 60, 60)
            fill_w = int(hp_pct * bar_w)
            if fill_w > 0:
                pygame.draw.rect(surface, fill_color, (ex + 8, bar_y, fill_w, 10))
            hp_text = font.render_text(f"{current_hp}/{max_hp}", (200, 200, 200))
            surface.blit(hp_text, (ex + 8, bar_y + 12))

        # Turn indicator
        y = 140
        round_num = getattr(combat_system, "round_number", 1)
        current = combat_system.get_current_entity() if hasattr(combat_system, "get_current_entity") else None
        turn_name = getattr(current, "name", "???") if current else "???"
        turn_surf = font.render_text(f" Round {round_num} -- {turn_name}'s turn", get_rgb("bright_yellow"))
        surface.blit(turn_surf, (8, y))

        # Action menu
        is_player_turn = combat_system.is_player_turn() if hasattr(combat_system, "is_player_turn") else False
        if is_player_turn:
            y += font.char_height * 2
            actions = [("Attack", "attack"), ("Skills", "skills"), ("Items", "items"), ("Flee", "flee")]
            ax = 8
            for label, action_id in actions:
                if action_id == selected_action:
                    bg = (200, 200, 200)
                    fg = (0, 0, 0)
                else:
                    bg = None
                    fg = get_rgb("bright_white")
                btn = font.render_text(f" {label} ", fg, bg)
                surface.blit(btn, (ax, y))
                ax += btn.get_width() + font.char_width * 2

        pygame.draw.rect(surface, (170, 0, 0), surface.get_rect(), 1)
        title = font.render_text(" Combat ", get_rgb("bright_red"), (15, 5, 5))
        surface.blit(title, (width // 2 - title.get_width() // 2, 0))

        return surface
