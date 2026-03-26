"""BSP (Binary Space Partition) dungeon generator.

Produces structured dungeon floors with rectangular rooms connected by
L-shaped corridors.  Higher floor numbers yield more rooms, enemies, and traps.
"""

from __future__ import annotations

import random

from data.themes import THEMES, get_theme_for_floor
from world.dungeon import DungeonFloor, Room
from world.generators.decorator import decorate_floor
from world.tile import Tile, TileType


class BSPNode:
    """A node in the binary space partition tree."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left: BSPNode | None = None
        self.right: BSPNode | None = None
        self.room: Room | None = None

    def split(self, min_size: int = 8, rng: random.Random | None = None) -> bool:
        """Recursively split this node into two children.

        Returns ``True`` if the split succeeded (i.e., there was enough space).
        """
        if rng is None:
            rng = random.Random()

        # Already split
        if self.left is not None or self.right is not None:
            return False

        # Decide split direction.  Prefer splitting the longer axis.
        if self.width > self.height and self.width / self.height >= 1.25:
            split_h = False  # split vertically
        elif self.height > self.width and self.height / self.width >= 1.25:
            split_h = True  # split horizontally
        else:
            split_h = rng.random() < 0.5

        max_size = (self.height if split_h else self.width) - min_size
        if max_size < min_size:
            return False  # too small to split

        split_pos = rng.randint(min_size, max_size)

        if split_h:
            self.left = BSPNode(self.x, self.y, self.width, split_pos)
            self.right = BSPNode(
                self.x, self.y + split_pos, self.width, self.height - split_pos
            )
        else:
            self.left = BSPNode(self.x, self.y, split_pos, self.height)
            self.right = BSPNode(
                self.x + split_pos, self.y, self.width - split_pos, self.height
            )

        return True

    def get_leaves(self) -> list[BSPNode]:
        """Return all leaf nodes in this sub-tree."""
        if self.left is None and self.right is None:
            return [self]
        leaves: list[BSPNode] = []
        if self.left:
            leaves.extend(self.left.get_leaves())
        if self.right:
            leaves.extend(self.right.get_leaves())
        return leaves

    def get_room(self) -> Room | None:
        """Return this node's room, or recurse into children to find one."""
        if self.room is not None:
            return self.room
        left_room = self.left.get_room() if self.left else None
        right_room = self.right.get_room() if self.right else None
        if left_room and right_room:
            return left_room  # arbitrary pick for corridor endpoint
        return left_room or right_room


def _build_tree(
    root: BSPNode,
    min_size: int,
    max_depth: int,
    rng: random.Random,
    depth: int = 0,
) -> None:
    """Recursively split the BSP tree up to *max_depth*."""
    if depth >= max_depth:
        return
    if root.split(min_size=min_size, rng=rng):
        if root.left:
            _build_tree(root.left, min_size, max_depth, rng, depth + 1)
        if root.right:
            _build_tree(root.right, min_size, max_depth, rng, depth + 1)


def _place_rooms(leaves: list[BSPNode], rng: random.Random) -> list[Room]:
    """Create a room inside each leaf node."""
    rooms: list[Room] = []
    for leaf in leaves:
        # Room must be at least 4x4, leave 1-tile wall border inside leaf
        min_room = 4
        max_w = leaf.width - 2
        max_h = leaf.height - 2
        if max_w < min_room or max_h < min_room:
            continue

        w = rng.randint(min_room, max_w)
        h = rng.randint(min_room, max_h)
        x = leaf.x + rng.randint(1, leaf.width - w - 1)
        y = leaf.y + rng.randint(1, leaf.height - h - 1)

        room = Room(x, y, w, h)
        leaf.room = room
        rooms.append(room)
    return rooms


def _connect_tree(node: BSPNode, floor: DungeonFloor, rng: random.Random) -> None:
    """Recursively connect sibling rooms through the BSP tree."""
    if node.left is None or node.right is None:
        return

    # Recurse first so children have rooms resolved
    _connect_tree(node.left, floor, rng)
    _connect_tree(node.right, floor, rng)

    left_room = node.left.get_room()
    right_room = node.right.get_room()

    if left_room and right_room:
        lx, ly = left_room.center
        rx, ry = right_room.center
        floor.carve_l_corridor(lx, ly, rx, ry, rng)


def _distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def generate_bsp(
    width: int,
    height: int,
    floor_number: int,
    theme_name: str,
    seed: int | None = None,
) -> DungeonFloor:
    """Generate a dungeon floor using BSP partitioning.

    1. Build a BSP tree by recursively splitting the map area.
    2. Place rooms in each leaf node.
    3. Connect rooms through the tree with L-shaped corridors.
    4. Place stairs, enemy spawns, chests, and traps.
    5. Apply the theme visuals via the decorator.

    Higher *floor_number* values produce more rooms, enemies, and traps.
    """
    rng = random.Random(seed)
    floor = DungeonFloor(width, height, floor_number, theme_name)
    floor.fill_with_walls()

    # Scale complexity with floor number
    max_depth = min(4 + floor_number // 3, 7)
    min_leaf = max(6, 10 - floor_number // 4)

    root = BSPNode(0, 0, width, height)
    _build_tree(root, min_size=min_leaf, max_depth=max_depth, rng=rng)

    leaves = root.get_leaves()
    rooms = _place_rooms(leaves, rng)

    if not rooms:
        # Fallback: at least one room in the center
        rx, ry = width // 4, height // 4
        rw, rh = width // 2, height // 2
        rooms = [Room(rx, ry, rw, rh)]

    # Carve rooms
    for room in rooms:
        floor.carve_room(room)

    floor.rooms = rooms

    # Connect rooms via BSP tree
    _connect_tree(root, floor, rng)

    # ---- Place stairs ----
    spawn_room = rooms[0]
    floor.spawn_point = spawn_room.center

    # Stairs up at spawn (except floor 1)
    if floor_number > 1:
        sx, sy = spawn_room.center
        floor.tiles[sy][sx] = Tile.stairs_up()
        floor.stairs_up = (sx, sy)

    # Stairs down in the room farthest from spawn
    farthest_room = max(rooms, key=lambda r: _distance(r.center, spawn_room.center))
    if farthest_room is spawn_room and len(rooms) > 1:
        farthest_room = rooms[1]
    dx, dy = farthest_room.center
    floor.tiles[dy][dx] = Tile.stairs_down()
    floor.stairs_down = (dx, dy)

    # ---- Enemy spawns ----
    enemies_per_room_min = 1 + floor_number // 3
    enemies_per_room_max = 2 + floor_number // 2
    for room in rooms:
        x1, y1, x2, y2 = room.inner()
        count = rng.randint(
            min(enemies_per_room_min, 5), min(enemies_per_room_max, 5)
        )
        placed = 0
        attempts = 0
        while placed < count and attempts < count * 10:
            ex = rng.randint(x1, x2 - 1)
            ey = rng.randint(y1, y2 - 1)
            if (
                floor.tiles[ey][ex].tile_type == TileType.FLOOR
                and (ex, ey) != floor.spawn_point
                and (ex, ey) != floor.stairs_down
                and (ex, ey) not in floor.enemy_spawns
            ):
                floor.enemy_spawns.append((ex, ey))
                placed += 1
            attempts += 1

    # ---- Chests ----
    # Place 1-3 chests, preferring rooms far from spawn
    sorted_rooms = sorted(
        rooms, key=lambda r: _distance(r.center, spawn_room.center), reverse=True
    )
    chest_count = rng.randint(1, min(3, len(rooms)))
    for i in range(chest_count):
        room = sorted_rooms[i % len(sorted_rooms)]
        x1, y1, x2, y2 = room.inner()
        for _ in range(20):
            cx = rng.randint(x1, x2 - 1)
            cy = rng.randint(y1, y2 - 1)
            if floor.tiles[cy][cx].tile_type == TileType.FLOOR:
                floor.tiles[cy][cx] = Tile.chest()
                floor.chest_positions.append((cx, cy))
                break

    # ---- Traps ----
    trap_count = min(floor_number // 2, 3)
    # Place traps along corridors (floor tiles adjacent to walls)
    corridor_tiles: list[tuple[int, int]] = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if floor.tiles[y][x].tile_type == TileType.FLOOR:
                # Check if it's a corridor-like tile (narrow passage)
                h_walls = (
                    (not floor.tiles[y][x - 1].walkable)
                    + (not floor.tiles[y][x + 1].walkable)
                )
                v_walls = (
                    (not floor.tiles[y - 1][x].walkable)
                    + (not floor.tiles[y + 1][x].walkable)
                )
                if (h_walls == 2 and v_walls == 0) or (v_walls == 2 and h_walls == 0):
                    corridor_tiles.append((x, y))

    rng.shuffle(corridor_tiles)
    for i in range(min(trap_count, len(corridor_tiles))):
        tx, ty = corridor_tiles[i]
        floor.tiles[ty][tx] = Tile.trap()
        floor.trap_positions.append((tx, ty))

    # ---- Place doors at room entrances ----
    for room in rooms:
        x1, y1 = room.x, room.y
        x2, y2 = room.x + room.width, room.y + room.height
        # Check the border of the room for openings that connect to corridors
        for x in range(x1, x2):
            for y in [y1, y2 - 1]:
                if floor.is_in_bounds(x, y) and floor.tiles[y][x].tile_type == TileType.FLOOR:
                    # Check if this is an entrance (wall on two parallel sides)
                    if _is_door_candidate(floor, x, y):
                        floor.tiles[y][x] = Tile.door()
        for y in range(y1, y2):
            for x in [x1, x2 - 1]:
                if floor.is_in_bounds(x, y) and floor.tiles[y][x].tile_type == TileType.FLOOR:
                    if _is_door_candidate(floor, x, y):
                        floor.tiles[y][x] = Tile.door()

    # Apply theme decorations
    decorate_floor(floor, theme_name)

    return floor


def _is_door_candidate(floor: DungeonFloor, x: int, y: int) -> bool:
    """Return True if (x, y) looks like a doorway (narrow opening between walls)."""
    if not floor.is_in_bounds(x, y):
        return False
    # Horizontal doorway: walls above and below, floor left and right
    h_door = (
        floor.is_in_bounds(x, y - 1)
        and not floor.tiles[y - 1][x].walkable
        and floor.is_in_bounds(x, y + 1)
        and not floor.tiles[y + 1][x].walkable
        and floor.is_in_bounds(x - 1, y)
        and floor.tiles[y][x - 1].walkable
        and floor.is_in_bounds(x + 1, y)
        and floor.tiles[y][x + 1].walkable
    )
    # Vertical doorway: walls left and right, floor above and below
    v_door = (
        floor.is_in_bounds(x - 1, y)
        and not floor.tiles[y][x - 1].walkable
        and floor.is_in_bounds(x + 1, y)
        and not floor.tiles[y][x + 1].walkable
        and floor.is_in_bounds(x, y - 1)
        and floor.tiles[y - 1][x].walkable
        and floor.is_in_bounds(x, y + 1)
        and floor.tiles[y + 1][x].walkable
    )
    return h_door or v_door
