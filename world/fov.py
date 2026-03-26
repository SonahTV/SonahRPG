"""Field of view using recursive shadowcasting algorithm.

Implements the 8-octant recursive shadowcasting algorithm for efficient
field-of-view computation on a 2D tile grid.
"""

from __future__ import annotations

from world.tile import Tile

# Multiplier tables for transforming coordinates into each of the 8 octants.
# Each octant is defined by 4 multipliers: (xx, xy, yx, yy)
# These transform (col, row) in octant-space into (dx, dy) in map-space.
_OCTANT_MULTIPLIERS: list[tuple[int, int, int, int]] = [
    (1, 0, 0, 1),
    (0, 1, 1, 0),
    (0, -1, 1, 0),
    (-1, 0, 0, 1),
    (-1, 0, 0, -1),
    (0, -1, -1, 0),
    (0, 1, -1, 0),
    (1, 0, 0, -1),
]


def compute_fov(
    tiles: list[list[Tile]],
    origin_x: int,
    origin_y: int,
    radius: int,
) -> None:
    """Compute FOV using recursive shadowcasting.

    Sets ``tile.visible = True`` for every tile visible from the origin,
    and also marks those tiles as ``explored``.  All tiles are first reset
    to ``visible = False`` before the computation begins.

    Args:
        tiles: 2-D grid indexed ``[y][x]``.
        origin_x: X coordinate of the viewer.
        origin_y: Y coordinate of the viewer.
        radius: Maximum sight radius.
    """
    height = len(tiles)
    width = len(tiles[0]) if height else 0

    # Reset visibility for all tiles
    for row in tiles:
        for tile in row:
            tile.visible = False

    # The origin is always visible
    tiles[origin_y][origin_x].visible = True
    tiles[origin_y][origin_x].explored = True

    # Cast light in each of the 8 octants
    for xx, xy, yx, yy in _OCTANT_MULTIPLIERS:
        _cast_light(
            tiles,
            width,
            height,
            origin_x,
            origin_y,
            radius,
            1,  # start at row 1 (row 0 is the origin)
            1.0,  # start slope
            0.0,  # end slope
            xx,
            xy,
            yx,
            yy,
        )


def _cast_light(
    tiles: list[list[Tile]],
    width: int,
    height: int,
    ox: int,
    oy: int,
    radius: int,
    row: int,
    start_slope: float,
    end_slope: float,
    xx: int,
    xy: int,
    yx: int,
    yy: int,
) -> None:
    """Recursively cast light for a single octant.

    Scans row by row (in octant-space), tracking which portions of each row
    are illuminated vs. shadowed.  When a transition from open-to-wall is
    found, we recurse to handle the remaining illuminated portion before the
    wall.  When a wall-to-open transition is found, we narrow the start slope.
    """
    if start_slope < end_slope:
        return

    radius_sq = radius * radius

    for current_row in range(row, radius + 1):
        dx = -current_row - 1
        dy = -current_row

        blocked = False
        new_start_slope = start_slope

        while dx <= 0:
            dx += 1

            # Translate octant-local (dx, dy) into map coordinates
            map_x = ox + dx * xx + dy * xy
            map_y = oy + dx * yx + dy * yy

            # Slopes for this cell
            left_slope = (dx - 0.5) / (dy + 0.5)
            right_slope = (dx + 0.5) / (dy - 0.5)

            if start_slope < right_slope:
                continue
            if end_slope > left_slope:
                break

            # Check bounds and distance
            if 0 <= map_x < width and 0 <= map_y < height:
                dist_sq = dx * dx + dy * dy
                if dist_sq <= radius_sq:
                    tiles[map_y][map_x].visible = True
                    tiles[map_y][map_x].explored = True

            if blocked:
                # We are scanning through a wall from a previous iteration
                if (
                    0 <= map_x < width
                    and 0 <= map_y < height
                    and not tiles[map_y][map_x].transparent
                ):
                    # Still in wall – narrow the start slope for the next row
                    new_start_slope = right_slope
                else:
                    # Emerged from the wall
                    blocked = False
                    start_slope = new_start_slope
            else:
                if (
                    0 <= map_x < width
                    and 0 <= map_y < height
                    and not tiles[map_y][map_x].transparent
                    and current_row < radius
                ):
                    # Hit a wall – recurse to handle the illuminated band
                    # *before* this wall, then mark us as blocked.
                    blocked = True
                    _cast_light(
                        tiles,
                        width,
                        height,
                        ox,
                        oy,
                        radius,
                        current_row + 1,
                        start_slope,
                        left_slope,
                        xx,
                        xy,
                        yx,
                        yy,
                    )
                    new_start_slope = right_slope

        if blocked:
            break
