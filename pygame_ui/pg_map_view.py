"""Pygame map view — tile-based dungeon renderer."""

import math
import time
import pygame
from pygame_ui.colors import get_rgb
from pygame_ui.font_manager import FontManager

# Same glyph mappings as ui/map_view.py
_PLAYER_GLYPHS = {"up": "^", "down": "v", "left": "<", "right": ">", "idle": "@"}
_ENEMY_GLYPHS = {"R": "r", "G": "g", "S": "s", "B": "b", "W": "w", "Z": "z", "O": "o", "D": "d", "T": "t"}


class PgMapView:
    def __init__(self):
        self.camera_x = 0
        self.camera_y = 0
        self.player_facing = "idle"
        self._start_time = time.time()
        self._footprints: list[tuple[int, int, float]] = []

    def record_move(self, old_x, old_y, dx, dy):
        if dy < 0: self.player_facing = "up"
        elif dy > 0: self.player_facing = "down"
        elif dx < 0: self.player_facing = "left"
        elif dx > 0: self.player_facing = "right"
        self._footprints.append((old_x, old_y, time.time()))
        if len(self._footprints) > 6:
            self._footprints = self._footprints[-6:]

    def update_camera(self, px, py):
        self.camera_x = px
        self.camera_y = py

    def render(self, dungeon_floor, player, enemies, items_on_ground,
               font: FontManager, width: int, height: int,
               npcs=None) -> pygame.Surface:
        """Render visible map area to a surface."""
        surface = pygame.Surface((width, height))
        surface.fill((0, 0, 0))

        if dungeon_floor is None or player is None:
            return surface

        cw, ch = font.char_width, font.char_height
        cols = width // cw
        rows = height // ch

        self.update_camera(player.x, player.y)
        start_x = self.camera_x - cols // 2
        start_y = self.camera_y - rows // 2

        # Build lookup maps
        enemy_map = {}
        for e in (enemies or []):
            if hasattr(e, "is_alive") and not e.is_alive(): continue
            enemy_map[(getattr(e, "x", -1), getattr(e, "y", -1))] = e

        item_positions = set()
        for it in (items_on_ground or []):
            ix = it.get("x", -1) if isinstance(it, dict) else getattr(it, "x", -1)
            iy = it.get("y", -1) if isinstance(it, dict) else getattr(it, "y", -1)
            item_positions.add((ix, iy))

        npc_map = {}
        for npc in (npcs or []):
            npc_map[(getattr(npc, "x", -1), getattr(npc, "y", -1))] = npc

        t = time.time() - self._start_time

        for vy in range(rows):
            for vx in range(cols):
                mx, my = start_x + vx, start_y + vy
                px_x, px_y = vx * cw, vy * ch

                # Player
                if mx == player.x and my == player.y:
                    glyph = _PLAYER_GLYPHS.get(self.player_facing, "@")
                    pulse = math.sin(t * 3.0)
                    fg = (255, 255, 255) if pulse > 0.3 else (255, 255, 85) if pulse > -0.3 else (170, 170, 0)
                    bg = (28, 28, 28)
                    surface.blit(font.render_glyph(glyph, fg, bg), (px_x, px_y))
                    continue

                tile = dungeon_floor.get_tile(mx, my)
                if tile is None or not getattr(tile, "explored", False):
                    continue

                is_visible = getattr(tile, "visible", False)
                pos = (mx, my)

                if is_visible:
                    if pos in enemy_map:
                        enemy = enemy_map[pos]
                        letter = getattr(enemy, "name", "E")[0].upper()
                        glyph = _ENEMY_GLYPHS.get(letter, letter.lower())
                        epulse = math.sin(t * 4.0 + hash(id(enemy)) * 0.7)
                        fg = (255, 85, 85) if epulse > 0.2 else (170, 0, 0) if epulse > -0.2 else (128, 0, 0)
                        surface.blit(font.render_glyph(glyph, fg, (18, 18, 18)), (px_x, px_y))
                        continue
                    if pos in npc_map:
                        # NPCs: friendly cyan, pulsing
                        npulse = math.sin(t * 2.0)
                        nc = (85, 255, 255) if npulse > 0 else (0, 200, 200)
                        surface.blit(font.render_glyph("@", nc, (18, 18, 18)), (px_x, px_y))
                        continue
                    if pos in item_positions:
                        sparkle = math.sin(t * 5.0 + mx * 3.1 + my * 7.7)
                        glyph = "*" if sparkle > 0.3 else "+" if sparkle > -0.3 else "."
                        surface.blit(font.render_glyph(glyph, (255, 255, 85), (0, 0, 0)), (px_x, px_y))
                        continue

                # Tile rendering
                tile_type_val = ""
                if hasattr(tile, "tile_type"):
                    tile_type_val = tile.tile_type.value if hasattr(tile.tile_type, "value") else str(tile.tile_type)
                tile_char = getattr(tile, "char", " ")

                if is_visible:
                    if tile_type_val == "stairs_down":
                        fg = (85, 255, 85) if math.sin(t * 2.5) > 0.2 else (0, 170, 0)
                        surface.blit(font.render_glyph(">", fg, (18, 18, 18)), (px_x, px_y))
                    elif tile_type_val == "water":
                        shimmer = math.sin(t * 3.0 + mx * 0.7 + my * 1.3)
                        glyph = "~"
                        fg = (85, 255, 255) if shimmer > 0.3 else (0, 170, 170) if shimmer > -0.3 else (0, 128, 128)
                        surface.blit(font.render_glyph(glyph, fg), (px_x, px_y))
                    elif tile_char == "#":
                        surface.blit(font.render_glyph("#", (94, 94, 94)), (px_x, px_y))
                    else:
                        color = get_rgb(getattr(tile, "color", "white"))
                        surface.blit(font.render_glyph(tile_char, color), (px_x, px_y))
                else:
                    # Fog of war
                    dim = (77, 77, 77)
                    if tile_char == "#":
                        surface.blit(font.render_glyph("#", (50, 50, 55)), (px_x, px_y))
                    else:
                        surface.blit(font.render_glyph(tile_char, dim), (px_x, px_y))

        # Border and title
        pygame.draw.rect(surface, get_rgb("green"), surface.get_rect(), 1)
        floor_num = getattr(dungeon_floor, "floor_number", getattr(dungeon_floor, "level", "?"))
        title = font.render_text(f" Floor {floor_num} ", (255, 255, 255), (0, 0, 0))
        surface.blit(title, (width // 2 - title.get_width() // 2, 0))

        return surface
