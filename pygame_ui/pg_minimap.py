"""Pygame minimap — pixel-based dungeon overview with theme colors."""

import math
import time

import pygame

from pygame_ui.colors import get_rgb

# Theme-based minimap wall/floor colors
_MINI_THEMES: dict[str, dict] = {
    "crypt":     {"wall": (55, 50, 60), "floor": (25, 22, 30), "vis": (40, 35, 48)},
    "cave":      {"wall": (45, 55, 40), "floor": (20, 25, 18), "vis": (35, 42, 30)},
    "dungeon":   {"wall": (65, 65, 70), "floor": (28, 28, 32), "vis": (42, 42, 48)},
    "sewer":     {"wall": (35, 55, 35), "floor": (18, 30, 18), "vis": (28, 42, 28)},
    "catacombs": {"wall": (60, 55, 50), "floor": (24, 20, 18), "vis": (38, 34, 30)},
    "temple":    {"wall": (72, 40, 40), "floor": (30, 20, 22), "vis": (48, 30, 32)},
    "ruins":     {"wall": (68, 60, 50), "floor": (28, 25, 22), "vis": (44, 38, 32)},
    "inferno":   {"wall": (80, 30, 15), "floor": (35, 14, 8),  "vis": (55, 22, 12)},
    "abyss":     {"wall": (50, 25, 65), "floor": (12, 8, 20),  "vis": (30, 16, 38)},
}


class PgMinimap:
    def __init__(self) -> None:
        self.scale = 3

    def render(
        self,
        dungeon_floor,
        player_x: int,
        player_y: int,
        enemies=None,
        items_on_ground=None,
        npcs=None,
        width: int = 200,
        height: int = 150,
    ) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill((5, 5, 10))
        enemies = enemies or []
        items_on_ground = items_on_ground or []

        if dungeon_floor is None:
            return surface

        theme_name = getattr(dungeon_floor, "theme_name", "crypt")
        tc = _MINI_THEMES.get(theme_name, _MINI_THEMES["crypt"])

        map_w = getattr(dungeon_floor, "width", 80)
        map_h = getattr(dungeon_floor, "height", 40)

        offset_x = width // 2 - player_x * self.scale
        offset_y = height // 2 - player_y * self.scale

        for my in range(map_h):
            for mx in range(map_w):
                tile = dungeon_floor.get_tile(mx, my)
                if tile is None or not getattr(tile, "explored", False):
                    continue
                sx = offset_x + mx * self.scale
                sy = offset_y + my * self.scale
                if sx < -self.scale or sy < -self.scale or sx >= width or sy >= height:
                    continue

                tile_type = ""
                if hasattr(tile, "tile_type"):
                    tile_type = tile.tile_type.value if hasattr(tile.tile_type, "value") else str(tile.tile_type)

                is_visible = getattr(tile, "visible", False)

                if tile_type == "wall":
                    color = tc["wall"]
                elif tile_type in ("stairs_down", "stairs_up"):
                    color = (40, 200, 40)
                elif tile_type == "water":
                    color = (30, 80, 140)
                elif tile_type == "door":
                    color = (120, 100, 50)
                elif is_visible:
                    color = tc["vis"]
                else:
                    color = tc["floor"]

                pygame.draw.rect(surface, color, (sx, sy, self.scale, self.scale))

        # Enemies (red, bosses brighter)
        for e in enemies:
            if hasattr(e, "is_alive") and not e.is_alive():
                continue
            ex = offset_x + getattr(e, "x", 0) * self.scale
            ey = offset_y + getattr(e, "y", 0) * self.scale
            if 0 <= ex < width and 0 <= ey < height:
                is_boss = getattr(e, "is_boss", False)
                color = (255, 80, 200) if is_boss else (220, 50, 50)
                pygame.draw.rect(surface, color, (ex, ey, self.scale, self.scale))

        # Items (gold sparkle)
        for it in items_on_ground:
            ix = it.get("x", 0) if isinstance(it, dict) else getattr(it, "x", 0)
            iy = it.get("y", 0) if isinstance(it, dict) else getattr(it, "y", 0)
            sx = offset_x + ix * self.scale
            sy = offset_y + iy * self.scale
            if 0 <= sx < width and 0 <= sy < height:
                pygame.draw.rect(surface, (220, 200, 50), (sx, sy, self.scale, self.scale))

        # NPCs (role-colored)
        for npc in (npcs or []):
            role = getattr(npc, "role", "")
            nx = offset_x + getattr(npc, "x", 0) * self.scale
            ny = offset_y + getattr(npc, "y", 0) * self.scale
            if 0 <= nx < width and 0 <= ny < height:
                if role == "merchant":
                    color = (220, 190, 50)
                elif role == "healer":
                    color = (50, 220, 80)
                else:
                    color = (50, 200, 200)
                pygame.draw.rect(surface, color, (nx, ny, self.scale, self.scale))

        # Player (pulsing bright)
        t = time.time()
        pulse = int(128 + 127 * math.sin(t * 3))
        px = offset_x + player_x * self.scale
        py = offset_y + player_y * self.scale
        if 0 <= px < width and 0 <= py < height:
            pygame.draw.rect(surface, (pulse, 255, pulse), (px, py, self.scale + 1, self.scale + 1))

        # Border (theme-tinted)
        border = tc["wall"]
        pygame.draw.rect(surface, border, surface.get_rect(), 1)

        # Legend dots
        legend_y = height - 10
        for color, label_x in [((220, 50, 50), 4), ((220, 200, 50), 20), ((50, 200, 200), 36)]:
            pygame.draw.rect(surface, color, (label_x, legend_y, 4, 4))

        return surface
