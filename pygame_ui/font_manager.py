"""Monospace font manager with glyph caching for Pygame rendering."""

from __future__ import annotations
import os
import pygame

# Default font settings
DEFAULT_FONT_SIZE = 16
FALLBACK_FONTS = ["Consolas", "Courier New", "monospace"]


class FontManager:
    """Manages font loading and glyph rendering with surface caching.

    Caches pre-rendered (char, fg_rgb, bg_rgb) → Surface lookups
    for fast tile-based rendering.
    """

    def __init__(self, font_size: int = DEFAULT_FONT_SIZE) -> None:
        self.font_size = font_size
        self.font: pygame.font.Font | None = None
        self.char_width: int = 0
        self.char_height: int = 0
        self._glyph_cache: dict[tuple, pygame.Surface] = {}
        self._max_cache_size = 4096

    def init(self) -> None:
        """Initialize the font. Must be called after pygame.init()."""
        # Try bundled font first
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")
        bundled_font = os.path.join(assets_dir, "ProggyClean.ttf")

        if os.path.exists(bundled_font):
            self.font = pygame.font.Font(bundled_font, self.font_size)
        else:
            # Fallback to system fonts
            for font_name in FALLBACK_FONTS:
                font_path = pygame.font.match_font(font_name)
                if font_path:
                    self.font = pygame.font.Font(font_path, self.font_size)
                    break
            if self.font is None:
                self.font = pygame.font.Font(None, self.font_size)  # pygame default

        # Measure character dimensions (monospace assumption)
        metrics = self.font.size("M")
        self.char_width = metrics[0]
        self.char_height = metrics[1]

    def render_glyph(
        self, char: str, fg: tuple[int, int, int], bg: tuple[int, int, int] | None = None
    ) -> pygame.Surface:
        """Render a single character glyph with caching.

        Returns a Surface of size (char_width, char_height).
        """
        cache_key = (char, fg, bg)
        cached = self._glyph_cache.get(cache_key)
        if cached is not None:
            return cached

        # Evict oldest entries if cache is full
        if len(self._glyph_cache) >= self._max_cache_size:
            # Remove first quarter of cache
            keys = list(self._glyph_cache.keys())
            for k in keys[:len(keys) // 4]:
                del self._glyph_cache[k]

        # Render the glyph
        if bg:
            surface = pygame.Surface((self.char_width, self.char_height))
            surface.fill(bg)
            text_surface = self.font.render(char, True, fg)
            surface.blit(text_surface, (0, 0))
        else:
            surface = self.font.render(char, True, fg)

        self._glyph_cache[cache_key] = surface
        return surface

    def render_text(
        self, text: str, fg: tuple[int, int, int],
        bg: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        """Render a string of text as a single surface."""
        if not text:
            return pygame.Surface((0, self.char_height))

        width = self.char_width * len(text)
        surface = pygame.Surface((width, self.char_height))
        if bg:
            surface.fill(bg)
        else:
            surface.fill((0, 0, 0))
            surface.set_colorkey((0, 0, 0))

        x = 0
        for char in text:
            glyph = self.render_glyph(char, fg, bg)
            surface.blit(glyph, (x, 0))
            x += self.char_width

        return surface

    def get_grid_size(self, cols: int, rows: int) -> tuple[int, int]:
        """Return pixel dimensions for a character grid of given size."""
        return cols * self.char_width, rows * self.char_height

    def clear_cache(self) -> None:
        """Clear the glyph cache."""
        self._glyph_cache.clear()
