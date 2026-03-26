"""Cellular automata cave generator.

Produces organic, cave-like dungeon floors by:
1. Seeding a random grid.
2. Smoothing with cellular automata rules.
3. Flood-filling to keep only the largest connected region.
4. Placing gameplay elements (stairs, enemies, chests, traps).
"""

from __future__ import annotations

import random
from collections import deque

from data.themes import THEMES, get_theme_for_floor
from world.dungeon import DungeonFloor, Room
from world.generators.decorator import decorate_floor
from world.tile import Tile, TileType


def _count_wall_neighbors(grid: list[list[bool]], x: int, y: int, w: int, h: int) -> int:
    """Count how many of the 8 neighbours (and out-of-bounds) are walls."""
    count = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                count += 1  # out of bounds counts as wall
            elif grid[ny][nx]:
                count += 1
    return count


def _automata_step(grid: list[list[bool]], w: int, h: int) -> list[list[bool]]:
    """Run one step of cellular automata: tile becomes wall if 5+ neighbours are walls."""
    new_grid = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            walls = _count_wall_neighbors(grid, x, y, w, h)
            new_grid[y][x] = walls >= 5
    return new_grid


def _flood_fill(
    grid: list[list[bool]], start_x: int, start_y: int, w: int, h: int
) -> set[tuple[int, int]]:
    """BFS flood fill from a non-wall cell, returning all connected open cells."""
    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque()
    queue.append((start_x, start_y))
    visited.add((start_x, start_y))

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited and not grid[ny][nx]:
                visited.add((nx, ny))
                queue.append((nx, ny))

    return visited


def _find_open_areas(
    open_cells: set[tuple[int, int]], min_area: int = 9
) -> list[Room]:
    """Identify rectangular-ish clusters of open cells to serve as 'rooms'.

    This uses a simple approach: scan for open tiles and greedily grow
    bounding boxes that are mostly open.  These aren't perfect rectangles
    but give the rest of the system room references for spawning.
    """
    if not open_cells:
        return []

    remaining = set(open_cells)
    rooms: list[Room] = []

    while remaining:
        # Pick a random seed cell
        seed = next(iter(remaining))
        # BFS a small cluster
        cluster: set[tuple[int, int]] = set()
        queue: deque[tuple[int, int]] = deque([seed])
        cluster.add(seed)

        while queue and len(cluster) < 60:
            cx, cy = queue.popleft()
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in remaining and (nx, ny) not in cluster:
                    cluster.add((nx, ny))
                    queue.append((nx, ny))

        remaining -= cluster

        if len(cluster) < min_area:
            continue

        # Build bounding box
        xs = [c[0] for c in cluster]
        ys = [c[1] for c in cluster]
        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)
        rooms.append(Room(x1, y1, x2 - x1 + 1, y2 - y1 + 1))

    return rooms


def _distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def generate_caves(
    width: int,
    height: int,
    floor_number: int,
    theme_name: str,
    seed: int | None = None,
) -> DungeonFloor:
    """Generate an organic cave-like dungeon floor.

    Algorithm:
        1. Fill grid with random walls (45% wall chance).
        2. Run 5 iterations of cellular automata (wall if >= 5 neighbours).
        3. Flood-fill to find connected regions.
        4. Keep the largest region; wall off the rest.
        5. Derive room-like areas for spawn placement.
        6. Place stairs, enemies, chests, traps.
        7. Apply theme decoration.
    """
    rng = random.Random(seed)
    floor = DungeonFloor(width, height, floor_number, theme_name)

    wall_chance = 0.45

    # Step 1: random fill (borders are always walls)
    grid: list[list[bool]] = []  # True = wall
    for y in range(height):
        row: list[bool] = []
        for x in range(width):
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                row.append(True)
            else:
                row.append(rng.random() < wall_chance)
        grid.append(row)

    # Step 2: cellular automata smoothing (5 iterations)
    for _ in range(5):
        grid = _automata_step(grid, width, height)

    # Ensure border is solid wall
    for y in range(height):
        grid[y][0] = True
        grid[y][width - 1] = True
    for x in range(width):
        grid[0][x] = True
        grid[height - 1][x] = True

    # Step 3: flood fill to find connected regions
    visited_global: set[tuple[int, int]] = set()
    regions: list[set[tuple[int, int]]] = []

    for y in range(height):
        for x in range(width):
            if not grid[y][x] and (x, y) not in visited_global:
                region = _flood_fill(grid, x, y, width, height)
                regions.append(region)
                visited_global |= region

    if not regions:
        # Fallback: carve a small room in the center
        cx, cy = width // 2, height // 2
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if 0 < cx + dx < width - 1 and 0 < cy + dy < height - 1:
                    grid[cy + dy][cx + dx] = False
        regions = [_flood_fill(grid, cx, cy, width, height)]

    # Step 4: keep largest region, wall off the rest
    largest = max(regions, key=len)
    for y in range(height):
        for x in range(width):
            if not grid[y][x] and (x, y) not in largest:
                grid[y][x] = True  # wall off disconnected areas

    # Build the tile grid from the boolean grid
    floor.tiles = []
    for y in range(height):
        row: list[Tile] = []
        for x in range(width):
            if grid[y][x]:
                row.append(Tile.wall())
            else:
                row.append(Tile.floor())
        floor.tiles.append(row)

    # Step 5: identify room-like areas
    rooms = _find_open_areas(largest, min_area=9)
    if not rooms:
        # Create at least one pseudo-room from the cave center
        cells = list(largest)
        cx = sum(c[0] for c in cells) // len(cells)
        cy = sum(c[1] for c in cells) // len(cells)
        rooms = [Room(cx - 2, cy - 2, 5, 5)]
    floor.rooms = rooms

    # Step 6: place gameplay elements
    open_list = list(largest)
    rng.shuffle(open_list)

    # Spawn point: center of the first room
    spawn_room = rooms[0]
    # Find the closest actual open cell to the room center
    scx, scy = spawn_room.center
    floor.spawn_point = min(open_list, key=lambda c: _distance(c, (scx, scy)))

    # Stairs up (except floor 1)
    if floor_number > 1:
        sx, sy = floor.spawn_point
        floor.tiles[sy][sx] = Tile.stairs_up()
        floor.stairs_up = floor.spawn_point

    # Stairs down: farthest open cell from spawn
    farthest = max(open_list, key=lambda c: _distance(c, floor.spawn_point))
    fx, fy = farthest
    floor.tiles[fy][fx] = Tile.stairs_down()
    floor.stairs_down = farthest

    # Enemy spawns
    enemies_count = min(len(rooms) * (1 + floor_number // 3), len(open_list) // 4)
    enemies_count = max(enemies_count, 3)
    placed_enemies = 0
    for pos in open_list:
        if placed_enemies >= enemies_count:
            break
        if (
            pos != floor.spawn_point
            and pos != floor.stairs_down
            and floor.tiles[pos[1]][pos[0]].tile_type == TileType.FLOOR
        ):
            floor.enemy_spawns.append(pos)
            placed_enemies += 1

    # Chests: 1-3 in far corners
    rng.shuffle(open_list)
    far_cells = sorted(open_list, key=lambda c: _distance(c, floor.spawn_point), reverse=True)
    chest_count = rng.randint(1, 3)
    placed_chests = 0
    for pos in far_cells:
        if placed_chests >= chest_count:
            break
        px, py = pos
        if floor.tiles[py][px].tile_type == TileType.FLOOR:
            floor.tiles[py][px] = Tile.chest()
            floor.chest_positions.append(pos)
            placed_chests += 1

    # Traps: along narrow passages
    trap_count = min(floor_number // 2, 3)
    placed_traps = 0
    for pos in open_list:
        if placed_traps >= trap_count:
            break
        px, py = pos
        if floor.tiles[py][px].tile_type != TileType.FLOOR:
            continue
        # Narrow passage: walls on two opposing sides
        h_walls = (
            (grid[py][px - 1] if px > 0 else True)
            + (grid[py][px + 1] if px < width - 1 else True)
        )
        v_walls = (
            (grid[py - 1][px] if py > 0 else True)
            + (grid[py + 1][px] if py < height - 1 else True)
        )
        if (h_walls == 2 and v_walls == 0) or (v_walls == 2 and h_walls == 0):
            floor.tiles[py][px] = Tile.trap()
            floor.trap_positions.append(pos)
            placed_traps += 1

    # Step 7: apply theme
    decorate_floor(floor, theme_name)

    return floor
