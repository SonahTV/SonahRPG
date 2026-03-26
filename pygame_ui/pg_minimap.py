"""Pygame minimap — pixel-based dungeon overview."""

import math
import time
import pygame
from pygame_ui.colors import get_rgb


class PgMinimap:
    def __init__(self):
        self.scale = 3  # pixels per tile

    def render(self, dungeon_floor, player_x: int, player_y: int,
               enemies=None, items_on_ground=None,
               width: int = 200, height: int = 150) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill((5, 5, 10))
        enemies = enemies or []
        items_on_ground = items_on_ground or []

        if dungeon_floor is None:
            return surface

        map_w = getattr(dungeon_floor, "width", 80)
        map_h = getattr(dungeon_floor, "height", 40)

        # Center on player
        offset_x = width // 2 - player_x * self.scale
        offset_y = height // 2 - player_y * self.scale

        # Draw explored tiles
        for my in range(map_h):
            for mx in range(map_w):
                tile = dungeon_floor.get_tile(mx, my)
                if tile is None or not getattr(tile, "explored", False):
                    continue
                sx = offset_x + mx * self.scale
                sy = offset_y + my * self.scale
                if sx < 0 or sy < 0 or sx >= width or sy >= height:
                    continue
                tile_type = ""
                if hasattr(tile, "tile_type"):
                    tile_type = tile.tile_type.value if hasattr(tile.tile_type, "value") else str(tile.tile_type)

                if tile_type == "wall":
                    color = (60, 60, 70)
                elif tile_type in ("stairs_down", "stairs_up"):
                    color = (0, 200, 0)
                elif tile_type == "water":
                    color = (0, 100, 170)
                else:
                    color = (35, 35, 45) if not getattr(tile, "visible", False) else (50, 50, 60)

                pygame.draw.rect(surface, color, (sx, sy, self.scale, self.scale))

        # Draw enemies
        for e in enemies:
            if hasattr(e, "is_alive") and not e.is_alive():
                continue
            ex = offset_x + getattr(e, "x", 0) * self.scale
            ey = offset_y + getattr(e, "y", 0) * self.scale
            if 0 <= ex < width and 0 <= ey < height:
                pygame.draw.rect(surface, (255, 50, 50), (ex, ey, self.scale, self.scale))

        # Draw items
        for it in items_on_ground:
            ix = it.get("x", 0) if isinstance(it, dict) else getattr(it, "x", 0)
            iy = it.get("y", 0) if isinstance(it, dict) else getattr(it, "y", 0)
            sx = offset_x + ix * self.scale
            sy = offset_y + iy * self.scale
            if 0 <= sx < width and 0 <= sy < height:
                pygame.draw.rect(surface, (255, 255, 50), (sx, sy, self.scale, self.scale))

        # Draw player (pulsing)
        t = time.time()
        pulse = int(128 + 127 * math.sin(t * 3))
        px = offset_x + player_x * self.scale
        py = offset_y + player_y * self.scale
        player_color = (pulse, 255, pulse)
        if 0 <= px < width and 0 <= py < height:
            pygame.draw.rect(surface, player_color, (px, py, self.scale + 1, self.scale + 1))

        # Border
        pygame.draw.rect(surface, get_rgb("green"), surface.get_rect(), 1)
        return surface
