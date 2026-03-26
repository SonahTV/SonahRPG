"""Enemy AI system — patrol and chase behavior for dungeon enemies."""

from __future__ import annotations

import math
import random
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.enemy import Enemy
    from world.dungeon import DungeonFloor


# Detection range (tiles) — must be less than player FOV (8) for fair gameplay
DETECTION_RANGE = 6

# Patrol frequency: enemies move every N player moves (slower than player)
PATROL_INTERVAL = 2


def _manhattan(ax: int, ay: int, bx: int, by: int) -> int:
    return abs(ax - bx) + abs(ay - by)


def _can_see(floor: DungeonFloor, ex: int, ey: int, px: int, py: int, max_dist: int) -> bool:
    """Simple line-of-sight check using Bresenham-like ray.

    Returns True if there's an unblocked transparent path from (ex,ey) to (px,py)
    within max_dist tiles.
    """
    if _manhattan(ex, ey, px, py) > max_dist * 2:
        return False
    dist = math.hypot(px - ex, py - ey)
    if dist > max_dist:
        return False

    # Walk along the line and check transparency
    steps = max(abs(px - ex), abs(py - ey))
    if steps == 0:
        return True

    for i in range(1, steps):
        t = i / steps
        cx = int(round(ex + (px - ex) * t))
        cy = int(round(ey + (py - ey) * t))
        tile = floor.get_tile(cx, cy)
        if tile is None or not tile.transparent:
            return False
    return True


def _bfs_step(
    floor: DungeonFloor,
    start_x: int,
    start_y: int,
    goal_x: int,
    goal_y: int,
    occupied: set[tuple[int, int]],
    max_search: int = 200,
) -> tuple[int, int] | None:
    """BFS pathfinding: return the next tile to step to, or None if no path.

    Returns only the first step (not the full path) for efficiency.
    """
    if start_x == goal_x and start_y == goal_y:
        return None

    queue: deque[tuple[int, int, int, int]] = deque()  # (x, y, first_x, first_y)
    visited: set[tuple[int, int]] = {(start_x, start_y)}

    # Seed BFS with the 4 cardinal neighbors
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        nx, ny = start_x + dx, start_y + dy
        if (nx, ny) in visited:
            continue
        if not floor.is_walkable(nx, ny):
            continue
        if nx == goal_x and ny == goal_y:
            return (nx, ny)
        if (nx, ny) in occupied:
            continue
        visited.add((nx, ny))
        queue.append((nx, ny, nx, ny))

    steps = 0
    while queue and steps < max_search:
        x, y, first_x, first_y = queue.popleft()
        steps += 1
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            if not floor.is_walkable(nx, ny):
                continue
            if nx == goal_x and ny == goal_y:
                return (first_x, first_y)
            if (nx, ny) in occupied:
                continue
            visited.add((nx, ny))
            queue.append((nx, ny, first_x, first_y))

    return None


class EnemyAI:
    """Manages enemy patrol and chase behavior on the exploration map."""

    def __init__(self) -> None:
        self._move_counter: int = 0  # counts player moves
        self._chasing: set[int] = set()  # ids of enemies currently chasing

    def tick(
        self,
        floor: DungeonFloor,
        player_x: int,
        player_y: int,
        enemies: list[Enemy],
    ) -> list[str]:
        """Called once per player move. Returns list of log messages to display."""
        self._move_counter += 1
        messages: list[str] = []

        # Build occupied set (player + all alive enemies)
        occupied: set[tuple[int, int]] = {(player_x, player_y)}
        for e in enemies:
            if e.is_alive():
                occupied.add((e.x, e.y))

        for enemy in enemies:
            if not enemy.is_alive():
                continue

            eid = id(enemy)
            dist = math.hypot(enemy.x - player_x, enemy.y - player_y)

            # Check if enemy can see the player
            can_see_player = (
                dist <= DETECTION_RANGE
                and _can_see(floor, enemy.x, enemy.y, player_x, player_y, DETECTION_RANGE)
            )

            if can_see_player:
                if eid not in self._chasing:
                    self._chasing.add(eid)
                    messages.append(
                        f"[bold red]{enemy.name}[/bold red] [dim italic]spots you![/dim italic]"
                    )
                # Chase: move toward player every tick
                self._move_enemy_toward(
                    floor, enemy, player_x, player_y, occupied
                )
            elif eid in self._chasing:
                # Lost sight — stop chasing after a short pursuit
                if dist > DETECTION_RANGE + 3:
                    self._chasing.discard(eid)
                else:
                    # Still pursuing last known direction
                    self._move_enemy_toward(
                        floor, enemy, player_x, player_y, occupied
                    )
            else:
                # Patrol: wander randomly every PATROL_INTERVAL moves
                if self._move_counter % PATROL_INTERVAL == 0:
                    self._patrol(floor, enemy, occupied)

            # Update occupied set after enemy moves
            occupied.discard((enemy.x, enemy.y))
            occupied.add((enemy.x, enemy.y))

        return messages

    def _move_enemy_toward(
        self,
        floor: DungeonFloor,
        enemy: Enemy,
        target_x: int,
        target_y: int,
        occupied: set[tuple[int, int]],
    ) -> None:
        """Move enemy one step toward target using BFS pathfinding."""
        # Remove self from occupied so BFS can work
        own_pos = (enemy.x, enemy.y)
        search_occupied = occupied - {own_pos}

        # Don't path INTO the player — stop one tile away
        next_step = _bfs_step(
            floor, enemy.x, enemy.y, target_x, target_y, search_occupied
        )
        if next_step:
            nx, ny = next_step
            # Don't walk onto the player's tile
            if (nx, ny) != (target_x, target_y):
                enemy.x = nx
                enemy.y = ny

    def _patrol(
        self,
        floor: DungeonFloor,
        enemy: Enemy,
        occupied: set[tuple[int, int]],
    ) -> None:
        """Random 1-tile wander in a cardinal direction."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = enemy.x + dx, enemy.y + dy
            if (nx, ny) not in occupied and floor.is_walkable(nx, ny):
                enemy.x = nx
                enemy.y = ny
                return

    def reset(self) -> None:
        """Reset AI state (e.g. when generating a new floor)."""
        self._move_counter = 0
        self._chasing.clear()
