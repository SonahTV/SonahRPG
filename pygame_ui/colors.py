"""Rich color name → RGB tuple lookup table for Pygame rendering."""

# Map Rich/CSS color names to RGB tuples
# Covers all colors used in SonahRPG's Rich markup
RICH_TO_RGB: dict[str, tuple[int, int, int]] = {
    # Standard colors
    "black": (0, 0, 0),
    "red": (170, 0, 0),
    "green": (0, 170, 0),
    "yellow": (170, 170, 0),
    "blue": (0, 0, 170),
    "magenta": (170, 0, 170),
    "cyan": (0, 170, 170),
    "white": (170, 170, 170),

    # Bright variants
    "bright_red": (255, 85, 85),
    "bright_green": (85, 255, 85),
    "bright_yellow": (255, 255, 85),
    "bright_blue": (85, 85, 255),
    "bright_magenta": (255, 85, 255),
    "bright_cyan": (85, 255, 255),
    "bright_white": (255, 255, 255),

    # Greys used in map rendering
    "grey7": (18, 18, 18),
    "grey11": (28, 28, 28),
    "grey30": (77, 77, 77),
    "grey37": (94, 94, 94),
    "grey42": (107, 107, 107),
    "grey50": (128, 128, 128),

    # Dark variants
    "dark_red": (128, 0, 0),
    "dark_cyan": (0, 128, 128),
    "dark_green": (0, 128, 0),

    # Default
    "default": (200, 200, 200),
}

def get_rgb(color_name: str) -> tuple[int, int, int]:
    """Look up a Rich color name and return an RGB tuple.

    Handles modifiers like 'bold', 'dim', 'italic' by stripping them.
    Falls back to white for unknown colors.
    """
    # Strip modifiers
    parts = color_name.lower().split()
    rgb = None
    for part in parts:
        if part in RICH_TO_RGB:
            rgb = RICH_TO_RGB[part]
            break

    if rgb is None:
        rgb = RICH_TO_RGB.get("default", (200, 200, 200))

    # Apply dim modifier
    if "dim" in parts:
        rgb = tuple(max(0, c // 2) for c in rgb)

    return rgb


def get_bg_rgb(style_str: str) -> tuple[int, int, int] | None:
    """Extract background color from a Rich style string like 'bold red on grey11'.

    Returns None if no background specified.
    """
    if " on " not in style_str:
        return None
    bg_part = style_str.split(" on ")[-1].strip()
    return get_rgb(bg_part)
