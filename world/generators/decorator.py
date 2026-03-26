"""Post-generation decoration for dungeon floors.

Applies theme-specific characters, colours, and minor cosmetic touches
after the structural generation pass is complete.
"""

from __future__ import annotations

import random

from data.themes import THEMES, DungeonTheme
from world.tile import TileType

# Avoid circular import at module level — DungeonFloor is only used for type
# hints so we import it inside functions or use TYPE_CHECKING.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.dungeon import DungeonFloor


# Mapping from TileType to the (char_attr, color_attr) names on DungeonTheme.
_TILE_THEME_MAP: dict[TileType, tuple[str, str]] = {
    TileType.WALL: ("wall_char", "wall_color"),
    TileType.FLOOR: ("floor_char", "floor_color"),
    TileType.DOOR: ("door_char", "door_color"),
    TileType.STAIRS_DOWN: ("stairs_down_char", "stairs_color"),
    TileType.STAIRS_UP: ("stairs_up_char", "stairs_color"),
    TileType.WATER: ("water_char", "water_color"),
    TileType.CHEST: ("chest_char", "chest_color"),
    TileType.TRAP: ("trap_char", "trap_color"),
}


def decorate_floor(floor: DungeonFloor, theme_name: str) -> None:
    """Apply theme-specific decorations after structural generation.

    This function:
    - Sets tile characters and colours from the theme.
    - Adds water tiles near cave edges (for cave themes).
    - Adds decorative wall character variations.
    - Validates that all rooms are reachable (logs a warning if not).

    Args:
        floor: The generated dungeon floor to decorate.
        theme_name: Key into ``THEMES``.
    """
    theme = THEMES.get(theme_name)
    if theme is None:
        theme = THEMES.get("dungeon")
    if theme is None:
        return  # no themes available at all

    # ---- Apply theme chars and colors to every tile ----
    for y in range(floor.height):
        for x in range(floor.width):
            tile = floor.tiles[y][x]
            mapping = _TILE_THEME_MAP.get(tile.tile_type)
            if mapping:
                char_attr, color_attr = mapping
                tile.char = getattr(theme, char_attr)
                tile.color = getattr(theme, color_attr)

    # ---- Decorative wall variations ----
    # Occasionally use a slightly different shade for wall tiles to break
    # up visual monotony (only a colour tweak, keeps the same character).
    _WALL_VARIATION_COLORS: dict[str, list[str]] = {
        "dungeon": ["grey50", "grey46", "grey54"],
        "catacombs": ["grey42", "grey39", "grey46"],
        "caves": ["dark_olive_green3", "dark_olive_green2", "grey35"],
        "ruins": ["rosy_brown", "dark_salmon", "indian_red"],
        "abyss": ["purple4", "purple3", "dark_magenta"],
    }

    rng = random.Random(floor.floor_number * 7919 + hash(theme_name))
    variations = _WALL_VARIATION_COLORS.get(theme_name, [])
    if variations:
        for y in range(floor.height):
            for x in range(floor.width):
                tile = floor.tiles[y][x]
                if tile.tile_type == TileType.WALL and rng.random() < 0.15:
                    tile.color = rng.choice(variations)

    # ---- Add water pools near cave edges (cave theme) ----
    if theme_name == "caves":
        _add_water_pools(floor, theme, rng)

    # ---- Accessibility check ----
    _verify_connectivity(floor)


def _add_water_pools(floor: DungeonFloor, theme: DungeonTheme, rng: random.Random) -> None:
    """Scatter small water pools on floor tiles adjacent to walls."""
    for y in range(1, floor.height - 1):
        for x in range(1, floor.width - 1):
            tile = floor.tiles[y][x]
            if tile.tile_type != TileType.FLOOR:
                continue

            # Count adjacent walls
            adj_walls = 0
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if floor.is_in_bounds(nx, ny) and floor.tiles[ny][nx].tile_type == TileType.WALL:
                    adj_walls += 1

            # Higher chance near walls
            if adj_walls >= 2 and rng.random() < 0.08:
                from world.tile import Tile as _Tile

                water = _Tile.water()
                water.char = theme.water_char
                water.color = theme.water_color
                floor.tiles[y][x] = water


def _verify_connectivity(floor: DungeonFloor) -> None:
    """Check that all rooms are connected via walkable tiles.

    If a disconnected room is found, carve a tunnel to the nearest connected
    tile to fix it.  This is a safety net — generators should produce
    connected layouts, but this guarantees it.
    """
    if not floor.rooms:
        return

    from collections import deque

    # BFS from spawn to find all reachable walkable tiles
    sx, sy = floor.spawn_point
    if not floor.is_in_bounds(sx, sy):
        return

    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque([(sx, sy)])
    visited.add((sx, sy))

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if (
                floor.is_in_bounds(nx, ny)
                and (nx, ny) not in visited
                and floor.tiles[ny][nx].walkable
            ):
                visited.add((nx, ny))
                queue.append((nx, ny))

    # Check each room center is reachable
    for room in floor.rooms:
        rcx, rcy = room.center
        if not floor.is_in_bounds(rcx, rcy):
            continue
        if (rcx, rcy) in visited:
            continue

        # Room center not reachable — find the nearest visited tile and tunnel
        best_dist = float("inf")
        best_target: tuple[int, int] = (sx, sy)
        for vx, vy in visited:
            d = abs(vx - rcx) + abs(vy - rcy)
            if d < best_dist:
                best_dist = d
                best_target = (vx, vy)

        # Carve an L-corridor to reconnect
        import random as _rand

        floor.carve_l_corridor(rcx, rcy, best_target[0], best_target[1], _rand.Random())

        # Add newly carved tiles to visited set
        re_queue: deque[tuple[int, int]] = deque([(rcx, rcy)])
        if floor.tiles[rcy][rcx].walkable:
            visited.add((rcx, rcy))
        while re_queue:
            cx2, cy2 = re_queue.popleft()
            for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nnx, nny = cx2 + ddx, cy2 + ddy
                if (
                    floor.is_in_bounds(nnx, nny)
                    and (nnx, nny) not in visited
                    and floor.tiles[nny][nnx].walkable
                ):
                    visited.add((nnx, nny))
                    re_queue.append((nnx, nny))
