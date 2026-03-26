"""Parse Rich markup text into (text, rgb_color) segments for Pygame rendering.

Handles Rich-style markup like:
  [bold red]text[/bold red]
  [bright_cyan]text[/bright_cyan]
  [bold bright_white]Name[/bold bright_white] the [bold]Class[/bold]
"""

from __future__ import annotations
import re
from pygame_ui.colors import get_rgb

# Pattern to match Rich markup tags
_TAG_PATTERN = re.compile(r'\[(/?)([^\]]*)\]')

# Default text color
DEFAULT_COLOR = (200, 200, 200)


def parse_markup(text: str) -> list[tuple[str, tuple[int, int, int]]]:
    """Parse Rich markup text into a list of (text, rgb_color) tuples.

    Example:
        parse_markup("[red]Hello[/red] world")
        → [("Hello", (170, 0, 0)), (" world", (200, 200, 200))]
    """
    segments: list[tuple[str, tuple[int, int, int]]] = []
    style_stack: list[str] = []
    last_end = 0

    for match in _TAG_PATTERN.finditer(text):
        # Add text before this tag
        before_text = text[last_end:match.start()]
        if before_text:
            current_style = style_stack[-1] if style_stack else ""
            color = get_rgb(current_style) if current_style else DEFAULT_COLOR
            segments.append((before_text, color))

        is_closing = match.group(1) == "/"
        tag_content = match.group(2)

        if is_closing:
            if style_stack:
                style_stack.pop()
        else:
            style_stack.append(tag_content)

        last_end = match.end()

    # Add remaining text after last tag
    remaining = text[last_end:]
    if remaining:
        current_style = style_stack[-1] if style_stack else ""
        color = get_rgb(current_style) if current_style else DEFAULT_COLOR
        segments.append((remaining, color))

    # If no tags were found, return the whole text with default color
    if not segments:
        segments.append((text, DEFAULT_COLOR))

    return segments


def strip_markup(text: str) -> str:
    """Remove all Rich markup tags, returning plain text."""
    return _TAG_PATTERN.sub('', text)


def render_markup_to_surface(
    text: str, font_manager, max_width: int = 0,
) -> "pygame.Surface":
    """Render Rich markup text to a Pygame surface.

    Args:
        text: Rich markup text
        font_manager: FontManager instance
        max_width: Maximum width in pixels (0 = no limit)

    Returns:
        Pygame surface with rendered text
    """
    import pygame

    segments = parse_markup(text)
    if not segments:
        return pygame.Surface((0, font_manager.char_height))

    # Calculate total width
    total_chars = sum(len(s) for s, _ in segments)
    width = font_manager.char_width * total_chars
    if max_width > 0:
        width = min(width, max_width)

    surface = pygame.Surface((max(1, width), font_manager.char_height))
    surface.fill((0, 0, 0))

    x = 0
    for segment_text, color in segments:
        for char in segment_text:
            if max_width > 0 and x >= max_width:
                break
            glyph = font_manager.render_glyph(char, color)
            surface.blit(glyph, (x, 0))
            x += font_manager.char_width

    return surface
