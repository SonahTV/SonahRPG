import math
import time

from rich.text import Text
from rich.panel import Panel

# Directional player glyphs — facing direction changes on movement
_PLAYER_GLYPHS = {
    "up": "▲",
    "down": "▼",
    "left": "◄",
    "right": "►",
    "idle": "@",
}

# Enemy display glyphs by first letter (fallback to uppercase letter)
_ENEMY_GLYPHS = {
    "R": "♦",  # Rat
    "G": "☠",  # Goblin
    "S": "§",  # Skeleton / Spider
    "B": "ß",  # Bat / Boss
    "W": "Ω",  # Wolf / Wraith
    "Z": "¤",  # Zombie
    "O": "Θ",  # Ogre / Orc
    "D": "Ð",  # Dragon / Demon
    "T": "†",  # Troll
}


class MapView:
    """Renders the dungeon map with fog of war, entities, and items."""

    def __init__(self):
        self.camera_x: int = 0
        self.camera_y: int = 0
        self.viewport_width: int = 60
        self.viewport_height: int = 25
        self._start_time: float = time.time()
        self.player_facing: str = "idle"
        self._footprints: list[tuple[int, int, float]] = []  # (x, y, timestamp)
        self._max_footprints: int = 6

    def record_move(self, old_x: int, old_y: int, dx: int, dy: int) -> None:
        """Record a player movement for directional glyph and footprint trail."""
        if dy < 0:
            self.player_facing = "up"
        elif dy > 0:
            self.player_facing = "down"
        elif dx < 0:
            self.player_facing = "left"
        elif dx > 0:
            self.player_facing = "right"

        # Leave a footprint at the old position
        now = time.time()
        self._footprints.append((old_x, old_y, now))
        # Trim oldest footprints
        if len(self._footprints) > self._max_footprints:
            self._footprints = self._footprints[-self._max_footprints:]

    def _get_status_style(self, player) -> str | None:
        """Return a tinted style if the player has an active status effect.

        Priority order: poison > stun > burn > shield/protect.
        Returns None when no recognised status effect is active so the
        caller can fall back to the normal pulse animation.
        """
        effects = getattr(player, "status_effects", None)
        if not effects:
            return None

        for se in effects:
            name = ""
            if isinstance(se, dict):
                name = se.get("name", "").lower()
            elif hasattr(se, "name"):
                name = se.name.lower()
            else:
                name = str(se).lower()

            if "poison" in name:
                return "bold bright_green on grey11"
            if "stun" in name:
                return "bold bright_yellow on grey11"
            if "burn" in name or "fire" in name:
                return "bold bright_red on grey11"
            if "shield" in name or "protect" in name:
                return "bold bright_cyan on grey11"

        return None

    def _get_player_style(self) -> str:
        """Animated player glow — pulses between white and gold."""
        t = time.time() - self._start_time
        pulse = math.sin(t * 3.0)
        if pulse > 0.3:
            return "bold bright_white on grey11"
        elif pulse > -0.3:
            return "bold bright_yellow on grey11"
        else:
            return "bold yellow on grey11"

    def _get_footprint(self, x: int, y: int) -> tuple[str, str] | None:
        """Return footprint char and style if one exists at (x,y)."""
        now = time.time()
        for fx, fy, stamp in reversed(self._footprints):
            if fx == x and fy == y:
                age = now - stamp
                if age > 2.0:
                    return None  # expired
                if age < 0.5:
                    return ("·", "bold cyan")
                elif age < 1.2:
                    return ("·", "cyan")
                else:
                    return ("·", "dim grey50")
        return None

    def update_camera(self, player_x: int, player_y: int, map_width: int = 0, map_height: int = 0) -> None:
        """Center camera on player, clamped to map bounds."""
        self.camera_x = player_x
        self.camera_y = player_y

        if map_width > 0:
            half_w = self.viewport_width // 2
            self.camera_x = max(half_w, min(player_x, map_width - half_w))
        if map_height > 0:
            half_h = self.viewport_height // 2
            self.camera_y = max(half_h, min(player_y, map_height - half_h))

    def render(
        self,
        dungeon_floor,
        player,
        enemies: list = None,
        items_on_ground: list = None,
        npcs: list = None,
    ) -> Panel:
        """Render the visible portion of the map as a Rich Panel.

        Visibility rules:
        - Not explored: render as space (black)
        - Explored but not visible: render in dim/grey (fog of war)
        - Visible: render in full color

        Entity rendering (only if tile is visible):
        - Player: @ in bold bright_white
        - Enemies: first letter of name in red
        - Items on ground: * in yellow
        - NPCs: ? in bright_cyan
        - Stairs down: > in bright_green
        - Stairs up: < in bright_green
        - Chests: $ in bright_yellow
        """
        enemies = enemies or []
        items_on_ground = items_on_ground or []
        npcs = npcs or []

        # Pre-build lookup sets for entity positions (only alive enemies)
        enemy_map: dict[tuple[int, int], object] = {}
        for e in enemies:
            if hasattr(e, "is_alive") and not e.is_alive():
                continue
            enemy_map[(getattr(e, "x", -1), getattr(e, "y", -1))] = e

        item_positions: set[tuple[int, int]] = set()
        for item in items_on_ground:
            ix = getattr(item, "x", item.get("x", -1) if isinstance(item, dict) else -1)
            iy = getattr(item, "y", item.get("y", -1) if isinstance(item, dict) else -1)
            item_positions.add((ix, iy))

        npc_map: dict[tuple[int, int], object] = {}
        for npc in npcs:
            npc_map[(getattr(npc, "x", -1), getattr(npc, "y", -1))] = npc

        # Update camera
        map_w = getattr(dungeon_floor, "width", 0)
        map_h = getattr(dungeon_floor, "height", 0)
        self.update_camera(player.x, player.y, map_w, map_h)

        start_x = self.camera_x - self.viewport_width // 2
        start_y = self.camera_y - self.viewport_height // 2

        text = Text()

        for vy in range(self.viewport_height):
            for vx in range(self.viewport_width):
                map_x = start_x + vx
                map_y = start_y + vy

                # Player always visible at their position
                if map_x == player.x and map_y == player.y:
                    glyph = _PLAYER_GLYPHS.get(self.player_facing, "@")
                    style = self._get_status_style(player) or self._get_player_style()
                    text.append(glyph, style=style)
                    continue

                # Get tile at this map position
                tile = dungeon_floor.get_tile(map_x, map_y)

                if tile is None or not getattr(tile, "explored", False):
                    text.append(" ")
                    continue

                is_visible = getattr(tile, "visible", False)

                # Render entities only on visible tiles
                if is_visible:
                    pos = (map_x, map_y)
                    if pos in enemy_map:
                        enemy = enemy_map[pos]
                        first_letter = getattr(enemy, "name", "E")[0].upper()
                        glyph = _ENEMY_GLYPHS.get(first_letter, first_letter)
                        # Enemies pulse between red shades for menace
                        t = time.time() - self._start_time
                        epulse = math.sin(t * 4.0 + hash(id(enemy)) * 0.7)
                        if epulse > 0.2:
                            estyle = "bold bright_red on grey7"
                        elif epulse > -0.2:
                            estyle = "bold red on grey7"
                        else:
                            estyle = "bold dark_red on grey7"
                        text.append(glyph, style=estyle)
                        continue
                    if pos in npc_map:
                        # NPCs get a friendly cyan pulse
                        t = time.time() - self._start_time
                        npulse = math.sin(t * 2.0)
                        nstyle = "bold bright_cyan on grey7" if npulse > 0 else "bold cyan on grey7"
                        text.append("☺", style=nstyle)
                        continue
                    if pos in item_positions:
                        # Items sparkle
                        t = time.time() - self._start_time
                        sparkle = math.sin(t * 5.0 + map_x * 3.1 + map_y * 7.7)
                        if sparkle > 0.3:
                            text.append("✦", style="bold bright_yellow on black")
                        elif sparkle > -0.3:
                            text.append("✧", style="bold yellow on black")
                        else:
                            text.append("·", style="bold bright_yellow on black")
                        continue

                    # Check for footprints on visible floor tiles
                    fp = self._get_footprint(map_x, map_y)
                    if fp:
                        text.append(fp[0], style=fp[1])
                        continue

                # Render the tile itself
                tile_type_val = ""
                if hasattr(tile, "tile_type"):
                    tile_type_val = tile.tile_type.value if hasattr(tile.tile_type, "value") else str(tile.tile_type)

                tile_char = getattr(tile, "char", " ")
                tile_color = getattr(tile, "color", "white")

                if is_visible:
                    # Special tile type coloring
                    if tile_type_val == "stairs_down":
                        # Stairs pulse with inviting green glow
                        t = time.time() - self._start_time
                        spulse = math.sin(t * 2.5)
                        if spulse > 0.2:
                            text.append("≡", style="bold bright_green on grey7")
                        else:
                            text.append("≡", style="bold green on grey7")
                    elif tile_type_val == "stairs_up":
                        text.append("≡", style="bold bright_green on black")
                    elif tile_type_val == "chest":
                        text.append("◊", style="bold bright_yellow on black")
                    elif tile_type_val == "water":
                        # Animated water
                        t = time.time() - self._start_time
                        shimmer = math.sin(t * 3.0 + map_x * 0.7 + map_y * 1.3)
                        if shimmer > 0.3:
                            text.append("≈", style="bold bright_cyan")
                        elif shimmer > -0.3:
                            text.append("~", style="cyan")
                        else:
                            text.append("~", style="dark_cyan")
                    elif tile_type_val == "door":
                        text.append("▪", style="bold yellow")
                    elif tile_type_val == "trap":
                        # Traps flicker ominously
                        t = time.time() - self._start_time
                        tpulse = math.sin(t * 6.0)
                        text.append("▲", style="bold bright_red" if tpulse > 0 else "bold red")
                    else:
                        # Apply subtle atmospheric variation to floor tiles
                        t = time.time() - self._start_time
                        noise = math.sin(map_x * 7.13 + map_y * 11.31 + t * 0.5)
                        if tile_char == "." and noise > 0.92:
                            text.append("·", style="dim grey42")
                        elif tile_char == "#":
                            # Walls get subtle depth shading near visible edges
                            text.append("█", style="grey37")
                        else:
                            text.append(tile_char, style=tile_color)
                else:
                    # Fog of war - explored but not currently visible
                    if tile_char == "#":
                        text.append("░", style="dim grey30")
                    else:
                        text.append(tile_char, style="dim grey30")

            if vy < self.viewport_height - 1:
                text.append("\n")

        floor_num = getattr(dungeon_floor, "floor_number", getattr(dungeon_floor, "level", "?"))
        return Panel(text, title=f"[bold]Dungeon - Floor {floor_num}[/bold]", border_style="green")
