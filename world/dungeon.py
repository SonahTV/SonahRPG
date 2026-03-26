"""Dungeon map class and floor management."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from world.tile import Tile, TileType


@dataclass
class Room:
    """Axis-aligned rectangular room defined by its top-left corner and size."""

    x: int  # top-left x
    y: int  # top-left y
    width: int
    height: int

    @property
    def center(self) -> tuple[int, int]:
        """Return the center coordinate of the room."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def intersects(self, other: Room, margin: int = 1) -> bool:
        """Check whether this room overlaps *other* (with an optional margin)."""
        return (
            self.x - margin < other.x + other.width
            and self.x + self.width + margin > other.x
            and self.y - margin < other.y + other.height
            and self.y + self.height + margin > other.y
        )

    def inner(self) -> tuple[int, int, int, int]:
        """Return ``(x1, y1, x2, y2)`` of the interior (1 tile inset from edges)."""
        return (self.x + 1, self.y + 1, self.x + self.width - 1, self.y + self.height - 1)


class DungeonFloor:
    """A single floor of the dungeon, holding the tile grid and metadata."""

    def __init__(
        self,
        width: int,
        height: int,
        floor_number: int,
        theme_name: str,
    ) -> None:
        self.width = width
        self.height = height
        self.floor_number = floor_number
        self.theme_name = theme_name
        self.tiles: list[list[Tile]] = []  # [y][x] indexing
        self.rooms: list[Room] = []
        self.spawn_point: tuple[int, int] = (0, 0)
        self.stairs_down: tuple[int, int] | None = None
        self.stairs_up: tuple[int, int] | None = None
        self.enemy_spawns: list[tuple[int, int]] = []
        self.chest_positions: list[tuple[int, int]] = []
        self.trap_positions: list[tuple[int, int]] = []

    # ------------------------------------------------------------------
    # Tile access helpers
    # ------------------------------------------------------------------

    def get_tile(self, x: int, y: int) -> Tile | None:
        """Return the tile at ``(x, y)`` or ``None`` if out of bounds."""
        if not self.is_in_bounds(x, y):
            return None
        return self.tiles[y][x]

    def is_walkable(self, x: int, y: int) -> bool:
        """Return whether the tile at ``(x, y)`` is walkable."""
        tile = self.get_tile(x, y)
        return tile is not None and tile.walkable

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Return whether ``(x, y)`` is inside the grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_random_floor_tile(self) -> tuple[int, int]:
        """Return a random walkable floor tile coordinate."""
        floor_tiles: list[tuple[int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[y][x].tile_type == TileType.FLOOR:
                    floor_tiles.append((x, y))
        if not floor_tiles:
            raise RuntimeError("No floor tiles available on this dungeon floor.")
        return random.choice(floor_tiles)

    # ------------------------------------------------------------------
    # Initialisation helpers (used by generators)
    # ------------------------------------------------------------------

    def fill_with_walls(self) -> None:
        """Fill the entire grid with wall tiles."""
        self.tiles = [
            [Tile.wall() for _ in range(self.width)] for _ in range(self.height)
        ]

    def carve_room(self, room: Room) -> None:
        """Carve the interior of a *room* into floor tiles."""
        x1, y1, x2, y2 = room.inner()
        for y in range(y1, y2):
            for x in range(x1, x2):
                if self.is_in_bounds(x, y):
                    self.tiles[y][x] = Tile.floor()

    def carve_h_tunnel(self, x1: int, x2: int, y: int) -> None:
        """Carve a horizontal tunnel of floor tiles between *x1* and *x2* at row *y*."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if self.is_in_bounds(x, y):
                self.tiles[y][x] = Tile.floor()

    def carve_v_tunnel(self, y1: int, y2: int, x: int) -> None:
        """Carve a vertical tunnel of floor tiles between *y1* and *y2* at column *x*."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if self.is_in_bounds(x, y):
                self.tiles[y][x] = Tile.floor()

    def carve_l_corridor(
        self, ax: int, ay: int, bx: int, by: int, rng: random.Random
    ) -> None:
        """Carve an L-shaped corridor between two points.

        Randomly chooses whether to go horizontal-first or vertical-first.
        """
        if rng.random() < 0.5:
            self.carve_h_tunnel(ax, bx, ay)
            self.carve_v_tunnel(ay, by, bx)
        else:
            self.carve_v_tunnel(ay, by, ax)
            self.carve_h_tunnel(ax, bx, by)
