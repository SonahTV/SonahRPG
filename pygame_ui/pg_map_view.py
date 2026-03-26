"""Pygame map view — atmospheric tile-based dungeon renderer.

Renders the visible dungeon with:
- Theme-aware wall/floor colors that shift per dungeon tier
- Animated player with directional glyph and pulsing glow
- Pulsing enemies with menace colors
- Friendly cyan NPCs
- Sparkling items
- Animated water, stairs, traps, doors
- Fog of war for explored-but-not-visible tiles
- Footprint trail behind player
- Ambient particle effects (dust, embers, spores depending on theme)
- Torch-light falloff gradient from player position
"""

import math
import random
import time

import pygame

from pygame_ui.colors import get_rgb
from pygame_ui.font_manager import FontManager

# Player directional glyphs
_PLAYER_GLYPHS = {"up": "^", "down": "v", "left": "<", "right": ">", "idle": "@"}

# Enemy glyphs — distinct per first letter
_ENEMY_GLYPHS = {
    "R": "r", "G": "g", "S": "s", "B": "b", "W": "w",
    "Z": "z", "O": "o", "D": "D", "T": "t", "L": "L",
}

# Theme-based color palettes for walls and floors
_THEME_COLORS: dict[str, dict] = {
    "crypt":     {"wall": (70, 65, 75),  "floor": (30, 28, 35),  "accent": (90, 80, 60),  "fog": (35, 30, 40)},
    "cave":      {"wall": (55, 70, 50),  "floor": (25, 30, 22),  "accent": (70, 90, 55),  "fog": (30, 35, 25)},
    "dungeon":   {"wall": (80, 80, 85),  "floor": (32, 32, 36),  "accent": (120, 100, 60), "fog": (40, 40, 42)},
    "sewer":     {"wall": (40, 65, 40),  "floor": (20, 35, 20),  "accent": (60, 100, 40), "fog": (25, 35, 25)},
    "catacombs": {"wall": (75, 70, 65),  "floor": (28, 25, 22),  "accent": (100, 90, 70), "fog": (35, 32, 28)},
    "temple":    {"wall": (90, 50, 50),  "floor": (35, 25, 28),  "accent": (140, 80, 40), "fog": (45, 28, 30)},
    "ruins":     {"wall": (85, 75, 65),  "floor": (33, 30, 28),  "accent": (120, 100, 70), "fog": (40, 35, 30)},
    "inferno":   {"wall": (100, 35, 20), "floor": (40, 18, 10),  "accent": (200, 80, 20), "fog": (50, 22, 15)},
    "abyss":     {"wall": (60, 30, 80),  "floor": (15, 10, 25),  "accent": (120, 50, 160), "fog": (30, 18, 40)},
}

# Ambient particle configs per theme
_THEME_PARTICLES: dict[str, dict] = {
    "crypt":     {"color": (140, 130, 100), "rate": 0.3, "name": "dust"},
    "cave":      {"color": (100, 140, 80),  "rate": 0.2, "name": "drip"},
    "dungeon":   {"color": (120, 110, 90),  "rate": 0.2, "name": "dust"},
    "sewer":     {"color": (80, 150, 60),   "rate": 0.5, "name": "spore"},
    "catacombs": {"color": (130, 120, 100), "rate": 0.15, "name": "dust"},
    "temple":    {"color": (180, 100, 40),  "rate": 0.3, "name": "ember"},
    "ruins":     {"color": (140, 120, 80),  "rate": 0.2, "name": "dust"},
    "inferno":   {"color": (255, 100, 30),  "rate": 0.8, "name": "ember"},
    "abyss":     {"color": (120, 50, 180),  "rate": 0.4, "name": "void"},
}


class _AmbientParticle:
    __slots__ = ("x", "y", "vx", "vy", "life", "color", "size")

    def __init__(self, x: float, y: float, color: tuple, kind: str):
        self.x = x
        self.y = y
        self.size = random.randint(1, 2)
        self.life = random.uniform(1.5, 3.5)
        self.color = color

        if kind == "ember":
            self.vx = random.uniform(-8, 8)
            self.vy = random.uniform(-25, -8)
        elif kind == "drip":
            self.vx = 0
            self.vy = random.uniform(15, 30)
        elif kind == "spore":
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-8, 2)
        elif kind == "void":
            self.vx = random.uniform(-12, 12)
            self.vy = random.uniform(-12, 12)
        else:  # dust
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-5, -1)


class PgMapView:
    """Atmospheric dungeon map renderer."""

    def __init__(self) -> None:
        self.camera_x = 0
        self.camera_y = 0
        self.player_facing = "idle"
        self._start_time = time.time()
        self._footprints: list[tuple[int, int, float]] = []
        self._particles: list[_AmbientParticle] = []
        self._particle_timer = 0.0

    def record_move(self, old_x: int, old_y: int, dx: int, dy: int) -> None:
        if dy < 0:
            self.player_facing = "up"
        elif dy > 0:
            self.player_facing = "down"
        elif dx < 0:
            self.player_facing = "left"
        elif dx > 0:
            self.player_facing = "right"
        self._footprints.append((old_x, old_y, time.time()))
        if len(self._footprints) > 8:
            self._footprints = self._footprints[-8:]

    def update_camera(self, px: int, py: int) -> None:
        self.camera_x = px
        self.camera_y = py

    def render(
        self,
        dungeon_floor,
        player,
        enemies,
        items_on_ground,
        font: FontManager,
        width: int,
        height: int,
        npcs=None,
    ) -> pygame.Surface:
        surface = pygame.Surface((width, height))

        if dungeon_floor is None or player is None:
            surface.fill((0, 0, 0))
            return surface

        cw, ch = font.char_width, font.char_height
        cols = width // cw
        rows = height // ch
        t = time.time() - self._start_time

        # Resolve theme colors
        theme_name = getattr(dungeon_floor, "theme_name", "crypt")
        palette = _THEME_COLORS.get(theme_name, _THEME_COLORS["crypt"])
        wall_c = palette["wall"]
        floor_c = palette["floor"]
        accent_c = palette["accent"]
        fog_c = palette["fog"]

        # Fill with theme-tinted black
        surface.fill((floor_c[0] // 3, floor_c[1] // 3, floor_c[2] // 3))

        self.update_camera(player.x, player.y)
        start_x = self.camera_x - cols // 2
        start_y = self.camera_y - rows // 2

        # Build entity lookups
        enemy_map: dict[tuple, object] = {}
        for e in (enemies or []):
            if hasattr(e, "is_alive") and not e.is_alive():
                continue
            enemy_map[(getattr(e, "x", -1), getattr(e, "y", -1))] = e

        item_positions: set[tuple] = set()
        for it in (items_on_ground or []):
            ix = it.get("x", -1) if isinstance(it, dict) else getattr(it, "x", -1)
            iy = it.get("y", -1) if isinstance(it, dict) else getattr(it, "y", -1)
            item_positions.add((ix, iy))

        npc_map: dict[tuple, object] = {}
        for npc in (npcs or []):
            npc_map[(getattr(npc, "x", -1), getattr(npc, "y", -1))] = npc

        # Footprint lookup
        now = time.time()
        fp_set: dict[tuple, float] = {}
        for fx, fy, ft in self._footprints:
            age = now - ft
            if age < 3.0:
                fp_set[(fx, fy)] = age

        # --- Render tiles ---
        for vy in range(rows):
            for vx in range(cols):
                mx, my = start_x + vx, start_y + vy
                px_x, px_y = vx * cw, vy * ch

                # Torch-light falloff from player
                dist = math.hypot(mx - player.x, my - player.y)
                light = max(0.0, min(1.0, 1.0 - dist / 10.0))

                # --- Player ---
                if mx == player.x and my == player.y:
                    glyph = _PLAYER_GLYPHS.get(self.player_facing, "@")
                    pulse = math.sin(t * 3.0)
                    if pulse > 0.3:
                        fg = (255, 255, 255)
                    elif pulse > -0.3:
                        fg = (255, 255, 120)
                    else:
                        fg = (200, 200, 60)
                    bg = (floor_c[0] + 15, floor_c[1] + 15, floor_c[2] + 10)
                    surface.blit(font.render_glyph(glyph, fg, bg), (px_x, px_y))
                    continue

                tile = dungeon_floor.get_tile(mx, my)
                if tile is None or not getattr(tile, "explored", False):
                    continue

                is_visible = getattr(tile, "visible", False)
                pos = (mx, my)

                # --- Entities (visible only) ---
                if is_visible:
                    if pos in enemy_map:
                        enemy = enemy_map[pos]
                        letter = getattr(enemy, "name", "E")[0].upper()
                        glyph = _ENEMY_GLYPHS.get(letter, letter)
                        is_boss = getattr(enemy, "is_boss", False)
                        epulse = math.sin(t * 4.0 + hash(id(enemy)) * 0.7)
                        if is_boss:
                            # Boss: bright pulsing magenta/red
                            fg = (255, 60, 200) if epulse > 0 else (200, 30, 150)
                            bg = (40, 10, 30)
                        else:
                            fg = (255, 85, 85) if epulse > 0.2 else (170, 0, 0) if epulse > -0.2 else (128, 0, 0)
                            bg = (25, 8, 8)
                        surface.blit(font.render_glyph(glyph, fg, bg), (px_x, px_y))
                        continue

                    if pos in npc_map:
                        npc = npc_map[pos]
                        role = getattr(npc, "role", "")
                        npulse = math.sin(t * 2.5)
                        if role == "merchant":
                            fg = (255, 220, 80) if npulse > 0 else (200, 170, 50)
                            glyph = "$"
                        elif role == "healer":
                            fg = (100, 255, 100) if npulse > 0 else (50, 200, 50)
                            glyph = "+"
                        else:
                            fg = (85, 255, 255) if npulse > 0 else (40, 200, 200)
                            glyph = "?"
                        surface.blit(font.render_glyph(glyph, fg, (floor_c[0] + 10, floor_c[1] + 10, floor_c[2] + 8)), (px_x, px_y))
                        continue

                    if pos in item_positions:
                        sparkle = math.sin(t * 5.0 + mx * 3.1 + my * 7.7)
                        if sparkle > 0.3:
                            glyph, fg = "*", (255, 255, 100)
                        elif sparkle > -0.3:
                            glyph, fg = "+", (220, 200, 60)
                        else:
                            glyph, fg = ".", (180, 160, 40)
                        surface.blit(font.render_glyph(glyph, fg, (floor_c[0] + 5, floor_c[1] + 5, 0)), (px_x, px_y))
                        continue

                    # Footprints
                    if pos in fp_set:
                        age = fp_set[pos]
                        fade = max(0.0, 1.0 - age / 3.0)
                        fp_color = (int(60 * fade), int(80 * fade), int(70 * fade))
                        surface.blit(font.render_glyph(".", fp_color), (px_x, px_y))
                        continue

                # --- Tile rendering ---
                tile_type_val = ""
                if hasattr(tile, "tile_type"):
                    tile_type_val = tile.tile_type.value if hasattr(tile.tile_type, "value") else str(tile.tile_type)
                tile_char = getattr(tile, "char", " ")

                if is_visible:
                    # Apply light falloff
                    lm = 0.4 + 0.6 * light  # minimum 40% brightness

                    if tile_type_val == "stairs_down":
                        spulse = math.sin(t * 2.5)
                        if spulse > 0.2:
                            fg = (int(85 * lm), int(255 * lm), int(85 * lm))
                        else:
                            fg = (int(40 * lm), int(180 * lm), int(40 * lm))
                        bg = (floor_c[0] + 8, floor_c[1] + 15, floor_c[2] + 8)
                        surface.blit(font.render_glyph(">", fg, bg), (px_x, px_y))

                    elif tile_type_val == "stairs_up":
                        fg = (int(85 * lm), int(200 * lm), int(85 * lm))
                        surface.blit(font.render_glyph("<", fg), (px_x, px_y))

                    elif tile_type_val == "water":
                        shimmer = math.sin(t * 3.0 + mx * 0.7 + my * 1.3)
                        if shimmer > 0.3:
                            fg = (int(70 * lm), int(180 * lm), int(220 * lm))
                        elif shimmer > -0.3:
                            fg = (int(40 * lm), int(130 * lm), int(170 * lm))
                        else:
                            fg = (int(20 * lm), int(90 * lm), int(130 * lm))
                        glyph = "~" if shimmer > 0 else "~"
                        surface.blit(font.render_glyph(glyph, fg), (px_x, px_y))

                    elif tile_type_val == "door":
                        fg = (int(accent_c[0] * lm), int(accent_c[1] * lm), int(accent_c[2] * lm))
                        surface.blit(font.render_glyph("+", fg, (floor_c[0] + 8, floor_c[1] + 6, floor_c[2] + 4)), (px_x, px_y))

                    elif tile_type_val == "trap":
                        tpulse = math.sin(t * 6.0 + mx * 2.0)
                        if tpulse > 0:
                            fg = (int(220 * lm), int(50 * lm), int(30 * lm))
                        else:
                            fg = (int(150 * lm), int(30 * lm), int(20 * lm))
                        surface.blit(font.render_glyph("^", fg), (px_x, px_y))

                    elif tile_type_val == "chest":
                        cpulse = math.sin(t * 3.0 + mx + my)
                        fg = (int(255 * lm), int((200 + 55 * cpulse) * lm), int(50 * lm))
                        surface.blit(font.render_glyph("$", fg, (floor_c[0] + 5, floor_c[1] + 5, 0)), (px_x, px_y))

                    elif tile_char == "#" or tile_type_val == "wall":
                        # Walls with subtle depth shading
                        noise = math.sin(mx * 7.13 + my * 11.31 + t * 0.3) * 0.1
                        wr = int(min(255, wall_c[0] * lm * (1 + noise)))
                        wg = int(min(255, wall_c[1] * lm * (1 + noise)))
                        wb = int(min(255, wall_c[2] * lm * (1 + noise)))
                        surface.blit(font.render_glyph("#", (wr, wg, wb)), (px_x, px_y))

                    else:
                        # Floor tiles with subtle variation
                        noise = math.sin(mx * 5.7 + my * 9.3) * 0.15
                        fr = int(min(255, max(0, floor_c[0] * lm * (1 + noise) + 12 * lm)))
                        fg_val = int(min(255, max(0, floor_c[1] * lm * (1 + noise) + 12 * lm)))
                        fb = int(min(255, max(0, floor_c[2] * lm * (1 + noise) + 10 * lm)))
                        # Occasional floor detail
                        if abs(noise) > 0.12:
                            glyph = "," if noise > 0 else "`"
                        else:
                            glyph = "." if tile_char in (".", " ", "\u00b7", "\u2219", "\u2591") else tile_char
                        surface.blit(font.render_glyph(glyph, (fr, fg_val, fb)), (px_x, px_y))

                else:
                    # Fog of war — explored but not visible
                    if tile_char == "#" or tile_type_val == "wall":
                        surface.blit(font.render_glyph("#", fog_c), (px_x, px_y))
                    elif tile_type_val == "stairs_down":
                        surface.blit(font.render_glyph(">", (fog_c[0] + 10, fog_c[1] + 20, fog_c[2] + 10)), (px_x, px_y))
                    elif tile_type_val == "door":
                        surface.blit(font.render_glyph("+", (fog_c[0] + 10, fog_c[1] + 8, fog_c[2] + 5)), (px_x, px_y))
                    else:
                        dim_color = (fog_c[0] - 5, fog_c[1] - 5, fog_c[2] - 5)
                        dim_color = tuple(max(0, c) for c in dim_color)
                        surface.blit(font.render_glyph(".", dim_color), (px_x, px_y))

        # --- Ambient particles ---
        particle_cfg = _THEME_PARTICLES.get(theme_name, _THEME_PARTICLES["crypt"])
        self._particle_timer += 0.05  # approximate dt
        while self._particle_timer > (1.0 / max(0.1, particle_cfg["rate"])):
            self._particle_timer -= 1.0 / particle_cfg["rate"]
            px = random.uniform(0, width)
            py = random.uniform(0, height) if particle_cfg["name"] != "ember" else height + 5
            self._particles.append(_AmbientParticle(px, py, particle_cfg["color"], particle_cfg["name"]))

        alive = []
        for p in self._particles:
            p.x += p.vx * 0.05
            p.y += p.vy * 0.05
            p.life -= 0.05
            if p.life > 0 and 0 <= p.x < width and 0 <= p.y < height:
                alpha = min(1.0, p.life / 1.5)
                r = max(0, min(255, int(p.color[0] * alpha)))
                g = max(0, min(255, int(p.color[1] * alpha)))
                b = max(0, min(255, int(p.color[2] * alpha)))
                pygame.draw.circle(surface, (r, g, b), (int(p.x), int(p.y)), p.size)
                alive.append(p)
        self._particles = alive[:200]  # cap

        # --- Border and floor title ---
        border_colors = {
            "crypt": (80, 70, 90), "cave": (60, 80, 50), "dungeon": (90, 90, 95),
            "sewer": (50, 80, 40), "catacombs": (80, 70, 60), "temple": (100, 50, 50),
            "ruins": (90, 80, 60), "inferno": (140, 50, 20), "abyss": (80, 40, 120),
        }
        bc = border_colors.get(theme_name, (60, 60, 60))
        pygame.draw.rect(surface, bc, surface.get_rect(), 1)

        # Floor title with theme name
        floor_num = getattr(dungeon_floor, "floor_number", "?")
        theme_display = getattr(dungeon_floor, "theme_name", "").replace("_", " ").title()
        title_text = f" Floor {floor_num} "
        title_surf = font.render_text(title_text, (200, 200, 200), (bc[0] // 2, bc[1] // 2, bc[2] // 2))
        surface.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 0))

        return surface
