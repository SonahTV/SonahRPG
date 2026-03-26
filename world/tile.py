"""Tile definitions for the dungeon map."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TileType(Enum):
    WALL = "wall"
    FLOOR = "floor"
    DOOR = "door"
    STAIRS_DOWN = "stairs_down"
    STAIRS_UP = "stairs_up"
    WATER = "water"
    CHEST = "chest"
    TRAP = "trap"


@dataclass
class Tile:
    tile_type: TileType
    walkable: bool
    transparent: bool  # for FOV
    explored: bool = False  # has player seen this tile?
    visible: bool = False  # is currently in FOV?
    char: str = ""  # display character (set from theme)
    color: str = ""  # Rich color
    entity_id: int | None = None  # entity standing on this tile
    item_ids: list[int] = field(default_factory=list)  # items on ground

    @staticmethod
    def wall() -> Tile:
        return Tile(
            tile_type=TileType.WALL,
            walkable=False,
            transparent=False,
            char="#",
            color="grey50",
        )

    @staticmethod
    def floor() -> Tile:
        return Tile(
            tile_type=TileType.FLOOR,
            walkable=True,
            transparent=True,
            char=".",
            color="grey30",
        )

    @staticmethod
    def door() -> Tile:
        return Tile(
            tile_type=TileType.DOOR,
            walkable=True,
            transparent=False,
            char="+",
            color="yellow",
        )

    @staticmethod
    def stairs_down() -> Tile:
        return Tile(
            tile_type=TileType.STAIRS_DOWN,
            walkable=True,
            transparent=True,
            char=">",
            color="bright_white",
        )

    @staticmethod
    def stairs_up() -> Tile:
        return Tile(
            tile_type=TileType.STAIRS_UP,
            walkable=True,
            transparent=True,
            char="<",
            color="bright_white",
        )

    @staticmethod
    def water() -> Tile:
        return Tile(
            tile_type=TileType.WATER,
            walkable=False,
            transparent=True,
            char="~",
            color="blue",
        )

    @staticmethod
    def chest() -> Tile:
        return Tile(
            tile_type=TileType.CHEST,
            walkable=True,
            transparent=True,
            char="$",
            color="bright_yellow",
        )

    @staticmethod
    def trap() -> Tile:
        return Tile(
            tile_type=TileType.TRAP,
            walkable=True,
            transparent=True,
            char="^",
            color="red",
        )
