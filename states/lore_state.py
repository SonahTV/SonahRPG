"""Lore display state -- shows discovered lore entries in a parchment style."""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game

# ASCII-friendly category icons for terminal rendering
CATEGORY_ICONS: dict[str, str] = {
    "history": "[H]",
    "entity": "[E]",
    "consortium": "[A]",
    "condemned": "[C]",
    "prophecy": "[P]",
}

CATEGORY_STYLES: dict[str, str] = {
    "history": "bright_yellow",
    "entity": "bright_red",
    "consortium": "bright_green",
    "condemned": "bright_magenta",
    "prophecy": "bright_cyan",
}


class LoreState(GameState):
    """Parchment-style display for viewing discovered lore entries.

    Two modes:
    - ``"display"`` -- shows a single lore entry (pushed when lore is found)
    - ``"journal"`` -- lists all discovered lore (accessible from pause menu)

    Args:
        game: Game instance
        mode: ``"display"`` or ``"journal"``
        entry: Single lore entry dict (required for display mode).
               Expected keys: ``id``, ``title``, ``category``, ``text``
    """

    LINES_PER_PAGE = 14  # visible text lines before scrolling

    def __init__(
        self,
        game: Game,
        mode: str = "journal",
        entry: dict | None = None,
    ) -> None:
        super().__init__(game)
        self.mode = mode  # "display" or "journal"
        self.entry = entry  # single entry for display mode

        # Journal mode state
        self.journal_entries: list[dict] = []
        self.selected_index = 0

        # Scroll state (used in display mode for long text)
        self.scroll_offset = 0
        self.wrapped_lines: list[str] = []

    # -- lifecycle -----------------------------------------------------

    def on_enter(self) -> None:
        if self.mode == "journal":
            self._load_journal_entries()
        elif self.mode == "display" and self.entry:
            self._prepare_display(self.entry)

    def _load_journal_entries(self) -> None:
        """Load all lore entries the player has found."""
        if not hasattr(self.game, "narrative_manager"):
            self.journal_entries = []
            return

        found_ids = self.game.narrative_manager.lore_found
        try:
            from data.lore import LORE_COLLECTIBLES
        except ImportError:
            self.journal_entries = []
            return

        self.journal_entries = [
            e for e in LORE_COLLECTIBLES if e["id"] in found_ids
        ]
        self.selected_index = 0

    def _prepare_display(self, entry: dict) -> None:
        """Split entry text into lines for scroll support."""
        text = entry.get("text", "")
        # Rough word-wrap at ~60 chars
        self.wrapped_lines = _word_wrap(text, width=60)
        self.scroll_offset = 0

    # -- input ---------------------------------------------------------

    def handle_input(self, key: str) -> None:
        if self.mode == "journal":
            self._handle_journal_input(key)
        elif self.mode == "display":
            self._handle_display_input(key)

    def _handle_journal_input(self, key: str) -> None:
        if key == "escape":
            self.game.state_manager.pop()
        elif key in ("up", "w"):
            if self.journal_entries:
                self.selected_index = (
                    (self.selected_index - 1) % len(self.journal_entries)
                )
        elif key in ("down", "s"):
            if self.journal_entries:
                self.selected_index = (
                    (self.selected_index + 1) % len(self.journal_entries)
                )
        elif key == "enter":
            if self.journal_entries:
                selected = self.journal_entries[self.selected_index]
                self.game.state_manager.push(
                    LoreState(self.game, mode="display", entry=selected)
                )

    def _handle_display_input(self, key: str) -> None:
        if key in ("escape", "enter", "space"):
            self.game.state_manager.pop()
        elif key in ("up", "w"):
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif key in ("down", "s"):
            max_scroll = max(
                0, len(self.wrapped_lines) - self.LINES_PER_PAGE
            )
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

    # -- update --------------------------------------------------------

    def update(self, dt: float) -> None:
        pass  # No animations needed

    # -- render --------------------------------------------------------

    def render(self) -> RenderableType:
        if self.mode == "journal":
            return self._render_journal()
        return self._render_display()

    def _render_journal(self) -> RenderableType:
        from rich.align import Align
        from rich.console import Group
        from rich.panel import Panel
        from rich.text import Text

        from ui.hotbar import Hotbar
        from ui.renderer import GameRenderer

        parts: list[RenderableType] = []

        # Header with completion percentage
        if hasattr(self.game, "narrative_manager"):
            found, total = self.game.narrative_manager.get_lore_progress()
            pct = int((found / total) * 100) if total > 0 else 0
            header = Text(
                f"\n  Lore Collected: {found}/{total} ({pct}%)\n\n",
                style="bold bright_cyan",
            )
        else:
            header = Text("\n  Lore Journal\n\n", style="bold bright_cyan")
        parts.append(header)

        if not self.journal_entries:
            parts.append(
                Text(
                    "  No lore entries discovered yet.\n"
                    "  Explore the depths to uncover hidden knowledge.\n",
                    style="dim italic",
                )
            )
        else:
            for i, entry in enumerate(self.journal_entries):
                category = entry.get("category", "history")
                icon = CATEGORY_ICONS.get(category, "[?]")
                style = CATEGORY_STYLES.get(category, "white")

                if i == self.selected_index:
                    line = Text(f"  > {icon} {entry['title']}\n")
                    line.stylize("bold bright_white")
                else:
                    line = Text(f"    {icon} {entry['title']}\n")
                    line.stylize(style)
                parts.append(line)

        # Category legend
        parts.append(Text("\n"))
        legend_parts: list[str] = []
        for cat, icon in CATEGORY_ICONS.items():
            legend_parts.append(f"{icon}={cat.title()}")
        parts.append(
            Text(f"  {' | '.join(legend_parts)}\n", style="dim")
        )

        content = Panel(
            Align.center(Group(*parts)),
            title="[bold bright_yellow]~~ Lore Journal ~~[/bold bright_yellow]",
            border_style="bright_yellow",
            padding=(1, 2),
        )

        hotbar = Hotbar()
        actions = [("Up/Down", "Navigate"), ("Enter", "Read"), ("Esc", "Close")]
        hotbar_panel = hotbar.render(actions)

        return GameRenderer().create_fullscreen_layout(content, hotbar_panel)

    def _render_display(self) -> RenderableType:
        from rich.align import Align
        from rich.console import Group
        from rich.panel import Panel
        from rich.text import Text

        from ui.hotbar import Hotbar
        from ui.renderer import GameRenderer

        if not self.entry:
            return Panel(Text("  No entry to display."))

        parts: list[RenderableType] = []

        # Title and category
        category = self.entry.get("category", "history")
        icon = CATEGORY_ICONS.get(category, "[?]")
        cat_style = CATEGORY_STYLES.get(category, "white")

        title_text = Text(f"\n  {icon} ", style=cat_style)
        title_text.append(self.entry.get("title", "Unknown"), style="bold bright_white")
        title_text.append(f"  ({category.title()})\n", style=f"dim {cat_style}")
        parts.append(title_text)

        # Separator
        parts.append(Text("  " + "-" * 50 + "\n", style="dim bright_yellow"))

        # Entry text with scroll
        visible = self.wrapped_lines[
            self.scroll_offset : self.scroll_offset + self.LINES_PER_PAGE
        ]
        for line in visible:
            parts.append(Text(f"  {line}\n", style="bright_white"))

        # Scroll indicator
        total = len(self.wrapped_lines)
        if total > self.LINES_PER_PAGE:
            pos = self.scroll_offset + 1
            end = min(self.scroll_offset + self.LINES_PER_PAGE, total)
            parts.append(
                Text(
                    f"\n  -- lines {pos}-{end} of {total} --\n",
                    style="dim italic",
                )
            )

        # Bottom separator
        parts.append(Text("  " + "-" * 50 + "\n", style="dim bright_yellow"))

        content = Panel(
            Align.center(Group(*parts)),
            title=f"[bold bright_yellow]~~ {self.entry.get('title', 'Lore')} ~~[/bold bright_yellow]",
            border_style="bright_yellow",
            padding=(1, 2),
        )

        hotbar = Hotbar()
        actions: list[tuple[str, str]] = [("Esc/Enter", "Close")]
        if total > self.LINES_PER_PAGE:
            actions.insert(0, ("Up/Down", "Scroll"))
        hotbar_panel = hotbar.render(actions)

        return GameRenderer().create_fullscreen_layout(content, hotbar_panel)

    def render_pygame(self, screen, font, renderer) -> None:
        """Render lore display to Pygame."""
        import pygame
        from pygame_ui.colors import get_rgb
        from pygame_ui.pg_hotbar import PgHotbar

        w, h = renderer.screen_width, renderer.screen_height - renderer.hotbar_height
        surface = pygame.Surface((w, h))
        surface.fill((10, 10, 5))

        y = 20
        margin = 40

        if self.mode == "journal":
            title = font.render_text("Lore Journal", get_rgb("bright_yellow"))
            surface.blit(title, (w // 2 - title.get_width() // 2, y))
            y += font.char_height * 2

            nm = getattr(self.game, "narrative_manager", None)
            entries = nm.lore_found if nm else []
            from data.lore import LORE_COLLECTIBLES
            progress = f"Discovered: {len(entries)}/{len(LORE_COLLECTIBLES)}"
            surface.blit(font.render_text(progress, get_rgb("grey50")), (margin, y))
            y += font.char_height * 2

            for i, lore_id in enumerate(entries):
                # Find entry
                entry_data = None
                for e in LORE_COLLECTIBLES:
                    if e["id"] == lore_id:
                        entry_data = e
                        break
                if not entry_data:
                    continue
                prefix = ">" if i == self.selected_index else " "
                color = get_rgb("bright_yellow") if i == self.selected_index else get_rgb("white")
                text = f"  {prefix} {entry_data.get('title', lore_id)}"
                surface.blit(font.render_text(text, color), (margin, y))
                y += font.char_height + 2
        else:
            # Display mode
            if self.entry:
                title_text = self.entry.get("title", "Lore")
                title_surf = font.render_text(title_text, get_rgb("bright_yellow"))
                surface.blit(title_surf, (w // 2 - title_surf.get_width() // 2, y))
                y += font.char_height * 2

                visible = self.wrapped_lines[self.scroll_offset:self.scroll_offset + self.LINES_PER_PAGE]
                for line in visible:
                    surface.blit(font.render_text(f"  {line}", get_rgb("bright_white")), (margin, y))
                    y += font.char_height

        pygame.draw.rect(surface, get_rgb("bright_yellow"), surface.get_rect(), 1)
        hotbar = PgHotbar()
        actions = [("U/D", "Scroll"), ("Esc", "Close")]
        hotbar_surf = hotbar.render(actions, font, renderer.hotbar_rect.width, renderer.hotbar_rect.height)
        renderer.draw_fullscreen_layout(screen, surface, hotbar_surf)


# -- helpers -----------------------------------------------------------

def _word_wrap(text: str, width: int = 60) -> list[str]:
    """Simple word-wrap that respects existing newlines."""
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        words = paragraph.split()
        current: list[str] = []
        length = 0
        for word in words:
            if length + len(word) + (1 if current else 0) > width:
                lines.append(" ".join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += len(word) + (1 if len(current) > 1 else 0)
        if current:
            lines.append(" ".join(current))
    return lines
