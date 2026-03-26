"""Template-based room generator for special rooms.

Provides pre-designed room layouts that can be stamped into a dungeon floor
to create visually distinctive areas such as treasure rooms, altars, etc.
"""

from __future__ import annotations

from world.dungeon import DungeonFloor, Room
from world.tile import Tile, TileType

# Template legend:
#   '#' = wall    '.' = floor    '+' = door     '>' = stairs_down
#   '<' = stairs_up  '~' = water   '$' = chest    '^' = trap
#   ' ' = leave existing tile untouched

ROOM_TEMPLATES: dict[str, list[str]] = {
    "treasure_room": [
        "########",
        "#......#",
        "#.$.$.##",
        "#......+",
        "#.$.$.##",
        "#......#",
        "########",
    ],
    "altar_room": [
        "##########",
        "#........#",
        "#..~..~..#",
        "#........#",
        "#...$$...+",
        "#........#",
        "#..~..~..#",
        "#........#",
        "##########",
    ],
    "library": [
        "##########",
        "#.#.#.#..#",
        "#.#.#.#..#",
        "#........+",
        "#.#.#.#..#",
        "#.#.#.#..#",
        "##########",
    ],
    "prison": [
        "############",
        "#.+.#.+.#..#",
        "#...#...#..#",
        "#####...#..+",
        "#.+.#...#..#",
        "#...#.+.#..#",
        "############",
    ],
    "boss_arena": [
        "##############",
        "#............#",
        "#............#",
        "#..^^....^^..#",
        "#............#",
        "#....~~~~....#",
        "#....~~~~....+",
        "#....~~~~....#",
        "#............#",
        "#..^^....^^..#",
        "#............#",
        "#............#",
        "##############",
    ],
}

_CHAR_TO_TILE: dict[str, type] = {
    "#": Tile.wall,
    ".": Tile.floor,
    "+": Tile.door,
    ">": Tile.stairs_down,
    "<": Tile.stairs_up,
    "~": Tile.water,
    "$": Tile.chest,
    "^": Tile.trap,
}


def place_template_room(
    floor: DungeonFloor,
    room: Room,
    template_name: str,
) -> None:
    """Stamp a pre-designed room template into the dungeon at *room*'s position.

    The template is centered within the room.  If the template is larger than
    the room, it is clipped.  Characters not in the legend (e.g. space) are
    left untouched, allowing the existing tile to show through.

    Args:
        floor: The dungeon floor to modify.
        room: The room whose top-left corner anchors the template placement.
        template_name: Key into ``ROOM_TEMPLATES``.
    """
    template = ROOM_TEMPLATES.get(template_name)
    if template is None:
        return

    tmpl_h = len(template)
    tmpl_w = max(len(row) for row in template) if template else 0

    # Center the template within the room bounds
    offset_x = room.x + max(0, (room.width - tmpl_w) // 2)
    offset_y = room.y + max(0, (room.height - tmpl_h) // 2)

    for ty, row_str in enumerate(template):
        for tx, ch in enumerate(row_str):
            mx = offset_x + tx
            my = offset_y + ty
            if not floor.is_in_bounds(mx, my):
                continue

            factory = _CHAR_TO_TILE.get(ch)
            if factory is None:
                continue  # skip unknown / space characters

            tile = factory()
            floor.tiles[my][mx] = tile

            # Track special positions
            if tile.tile_type == TileType.CHEST:
                floor.chest_positions.append((mx, my))
            elif tile.tile_type == TileType.TRAP:
                floor.trap_positions.append((mx, my))
            elif tile.tile_type == TileType.STAIRS_DOWN:
                floor.stairs_down = (mx, my)
            elif tile.tile_type == TileType.STAIRS_UP:
                floor.stairs_up = (mx, my)


def get_template_size(template_name: str) -> tuple[int, int] | None:
    """Return ``(width, height)`` of a template, or ``None`` if not found."""
    template = ROOM_TEMPLATES.get(template_name)
    if template is None:
        return None
    h = len(template)
    w = max(len(row) for row in template) if template else 0
    return (w, h)
