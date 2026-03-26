"""A* pathfinding for entity movement on dungeon grids."""

from __future__ import annotations

import heapq

from world.tile import Tile

# 4-directional movement offsets (no diagonals)
_DIRS: list[tuple[int, int]] = [(0, -1), (0, 1), (-1, 0), (1, 0)]


def _heuristic(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Manhattan distance heuristic."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(
    tiles: list[list[Tile]],
    start: tuple[int, int],
    end: tuple[int, int],
    max_steps: int = 100,
) -> list[tuple[int, int]] | None:
    """Find the shortest path between *start* and *end* using A*.

    Args:
        tiles: 2-D grid indexed ``[y][x]``.
        start: ``(x, y)`` start position.
        end: ``(x, y)`` goal position.
        max_steps: Maximum number of nodes to evaluate before giving up.

    Returns:
        A list of ``(x, y)`` positions from *start* (exclusive) to *end*
        (inclusive), or ``None`` if no path exists within *max_steps*.
    """
    height = len(tiles)
    width = len(tiles[0]) if height else 0

    if start == end:
        return []

    # Validate bounds
    sx, sy = start
    ex, ey = end
    if not (0 <= sx < width and 0 <= sy < height):
        return None
    if not (0 <= ex < width and 0 <= ey < height):
        return None
    if not tiles[ey][ex].walkable:
        return None

    # Priority queue: (f_cost, tie_breaker, (x, y))
    counter = 0
    open_set: list[tuple[int, int, tuple[int, int]]] = []
    heapq.heappush(open_set, (_heuristic(start, end), counter, start))

    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score: dict[tuple[int, int], int] = {start: 0}

    steps = 0

    while open_set and steps < max_steps:
        _, _, current = heapq.heappop(open_set)
        steps += 1

        if current == end:
            # Reconstruct path
            path: list[tuple[int, int]] = []
            node = current
            while node != start:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        cx, cy = current
        for dx, dy in _DIRS:
            nx, ny = cx + dx, cy + dy
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if not tiles[ny][nx].walkable:
                continue

            neighbor = (nx, ny)
            tentative_g = g_score[current] + 1

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + _heuristic(neighbor, end)
                counter += 1
                heapq.heappush(open_set, (f, counter, neighbor))

    return None


def move_towards(
    tiles: list[list[Tile]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> tuple[int, int]:
    """Return the next position to move toward *end*.

    If the target is within 15 tiles (Manhattan), uses A* for an optimal
    first step.  Otherwise falls back to simple directional preference
    (move along the axis with the greatest distance first).

    Returns *start* if no valid move is available.
    """
    if start == end:
        return start

    distance = _heuristic(start, end)

    # Use A* when close enough for it to be cheap
    if distance <= 15:
        path = astar(tiles, start, end, max_steps=200)
        if path:
            return path[0]

    # Fallback: greedy directional movement
    sx, sy = start
    ex, ey = end
    height = len(tiles)
    width = len(tiles[0]) if height else 0

    # Build candidate moves sorted by how much they reduce distance
    candidates: list[tuple[int, tuple[int, int]]] = []
    for dx, dy in _DIRS:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < width and 0 <= ny < height and tiles[ny][nx].walkable:
            new_dist = _heuristic((nx, ny), end)
            candidates.append((new_dist, (nx, ny)))

    if not candidates:
        return start

    candidates.sort(key=lambda c: c[0])
    return candidates[0][1]
