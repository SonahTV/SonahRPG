import math
import time
import random
from rich.text import Text


class AmbientEffects:
    """Manages ambient visual effects like torch flicker, water shimmer."""

    def __init__(self):
        self._start_time = time.time()

    def get_torch_style(self, base_color: str = "yellow") -> str:
        """Get flickering torch style based on time.
        Alternates between bright and dim yellow/orange."""
        t = time.time() - self._start_time
        # Use multiple sine waves for organic flicker
        flicker = (math.sin(t * 5.0) * 0.3 +
                   math.sin(t * 7.3) * 0.2 +
                   math.sin(t * 11.1) * 0.1)

        if flicker > 0.2:
            return "bold bright_yellow"
        elif flicker > -0.1:
            return "bold yellow"
        else:
            return "dark_orange3"

    def get_water_style(self) -> str:
        """Get shimmering water style."""
        t = time.time() - self._start_time
        shimmer = math.sin(t * 3.0 + random.random() * 0.3)
        if shimmer > 0.3:
            return "bold bright_cyan"
        elif shimmer > -0.3:
            return "cyan"
        else:
            return "dark_cyan"

    def get_cursor_style(self) -> str:
        """Blinking cursor/selection style."""
        t = time.time() - self._start_time
        if int(t * 2) % 2 == 0:
            return "bold bright_white"
        return "bold bright_yellow"

    def get_magic_style(self, base_color: str = "bright_magenta") -> str:
        """Magical glow effect."""
        t = time.time() - self._start_time
        colors = ["bright_magenta", "bright_blue", "bright_cyan"]
        idx = int(t * 2) % len(colors)
        return f"bold {colors[idx]}"

    def apply_atmospheric_variation(self, char: str, x: int, y: int) -> tuple[str, str]:
        """Apply subtle ambient variation to dungeon tiles.
        Occasionally show dust motes, drips, etc."""
        t = time.time() - self._start_time

        # Very occasional ambient particles
        noise = math.sin(x * 7.13 + y * 11.31 + t * 0.5)
        if noise > 0.95:
            return ("\u00b7", "dim grey50")  # dust mote
        if noise < -0.95 and char == ".":
            return (",", "dim grey42")  # floor variation

        return (char, "")  # no change
