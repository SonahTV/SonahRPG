import math
import time

from rich.panel import Panel
from rich.text import Text


class Minimap:
    """Small overview minimap showing explored areas at reduced scale."""

    # Player marker cycle: (character, style)
    _PLAYER_FRAMES = [
        ("@", "bold bright_white"),
        ("◉", "bold bright_yellow"),
        ("●", "bold bright_cyan"),
    ]

    def render(
        self,
        dungeon_floor,
        player_x: int,
        player_y: int,
        scale: int = 3,
        enemies=None,
        items_on_ground=None,
    ) -> Panel:
        """Render a scaled-down minimap showing explored areas.

        Each minimap pixel represents a scale x scale block of tiles.
        Player shown as animated pulsing marker.
        Stairs pulse between bright_green and green.
        Enemies shown as red dots, items as yellow dots.
        Only explored tiles are displayed; unexplored areas are blank.

        Args:
            dungeon_floor: The dungeon floor object with width, height, and get_tile().
            player_x: Player's x position in map coordinates.
            player_y: Player's y position in map coordinates.
            scale: How many map tiles each minimap cell represents.
            enemies: Optional list of enemy objects with .x, .y and .is_alive().
            items_on_ground: Optional list of item objects with .x, .y attributes.
        """
        floor_w = getattr(dungeon_floor, "width", 80)
        floor_h = getattr(dungeon_floor, "height", 40)

        mini_w = floor_w // scale
        mini_h = floor_h // scale

        # Cap minimap size to fit the sidebar
        max_w, max_h = 24, 12
        mini_w = min(mini_w, max_w)
        mini_h = min(mini_h, max_h)

        # Player cell in minimap coordinates
        px_cell = player_x // scale
        py_cell = player_y // scale

        # Current time for animations
        t = time.time()

        # Player marker: cycle through frames using sine wave
        # sin oscillates -1..1, map to index 0..2
        player_phase = (math.sin(t * 3.0) + 1.0) / 2.0  # 0.0 .. 1.0
        player_idx = int(player_phase * len(self._PLAYER_FRAMES)) % len(
            self._PLAYER_FRAMES
        )
        player_char, player_style = self._PLAYER_FRAMES[player_idx]

        # Stairs animation: pulse between bright_green and green
        stairs_bright = (math.sin(t * 2.5) + 1.0) / 2.0 > 0.5

        # Build lookup sets for enemies and items in minimap coords
        enemy_cells: set[tuple[int, int]] = set()
        if enemies:
            for e in enemies:
                if hasattr(e, "is_alive") and not e.is_alive():
                    continue
                ex = getattr(e, "x", None)
                ey = getattr(e, "y", None)
                if ex is not None and ey is not None:
                    enemy_cells.add((ex // scale, ey // scale))

        item_cells: set[tuple[int, int]] = set()
        if items_on_ground:
            for item in items_on_ground:
                if isinstance(item, dict):
                    ix = item.get("x")
                    iy = item.get("y")
                else:
                    ix = getattr(item, "x", None)
                    iy = getattr(item, "y", None)
                if ix is not None and iy is not None:
                    item_cells.add((ix // scale, iy // scale))

        text = Text()

        for my in range(mini_h):
            for mx in range(mini_w):
                # Sample the center tile of this minimap cell
                tx = mx * scale + scale // 2
                ty = my * scale + scale // 2

                # Player marker (always on top)
                if mx == px_cell and my == py_cell:
                    text.append(player_char, style=player_style)
                    continue

                tile = dungeon_floor.get_tile(tx, ty)

                if tile is None or not getattr(tile, "explored", False):
                    text.append(" ")
                    continue

                # Enemies layer (only on explored tiles)
                if (mx, my) in enemy_cells:
                    text.append("·", style="bold bright_red")
                    continue

                # Items layer (only on explored tiles)
                if (mx, my) in item_cells:
                    text.append("·", style="bold bright_yellow")
                    continue

                # Determine tile type
                tile_type_val = ""
                if hasattr(tile, "tile_type"):
                    tile_type_val = (
                        tile.tile_type.value
                        if hasattr(tile.tile_type, "value")
                        else str(tile.tile_type)
                    )

                if tile_type_val == "wall":
                    text.append("█", style="dim grey30")
                elif tile_type_val == "stairs_down":
                    stairs_style = "bright_green" if stairs_bright else "green"
                    text.append(">", style=stairs_style)
                elif tile_type_val == "stairs_up":
                    stairs_style = "bright_green" if stairs_bright else "green"
                    text.append("<", style=stairs_style)
                elif tile_type_val == "door":
                    text.append("+", style="bright_yellow")
                elif tile_type_val == "chest":
                    text.append("$", style="bright_yellow")
                else:
                    # Floor or corridor
                    text.append("·", style="dim grey50")

            if my < mini_h - 1:
                text.append("\n")

        return Panel(text, title="[bold]Map[/bold]", border_style="dim green")
