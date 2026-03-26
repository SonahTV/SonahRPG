"""Cinematic text crawl state with typewriter effect and CYOA choices."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game


class CinematicState(GameState):
    """Displays narrative pages with typewriter effect and branching choices.

    Pages format:
    - {"type": "text", "text": "..."} - typewriter text, press any key to advance
    - {"type": "choice", "text": "...", "choices": [
        {"label": "...", "response": "...", "flag": "...", "effect": {...}}
      ]}

    Args:
        game: Game instance
        pages: List of page dicts
        on_complete: Optional callback when all pages are done
        title: Optional title for the panel border
    """

    def __init__(
        self,
        game: Game,
        pages: list[dict],
        on_complete: Callable[[], None] | None = None,
        title: str = "The Depths",
    ) -> None:
        super().__init__(game)
        self.pages = pages
        self.on_complete = on_complete
        self.title = title

        self.current_page = 0
        self.char_index = 0  # For typewriter effect
        self.typewriter_speed = 30  # chars per second
        self.typewriter_timer = 0.0
        self.page_complete = False  # True when full text is revealed
        self.skip_typewriter = False  # True when player hits key to skip

        # Choice state
        self.is_choice_page = False
        self.selected_choice = 0
        self.choice_made = False
        self.choice_response = ""
        self.showing_response = False

    # -- input ---------------------------------------------------------

    def handle_input(self, key: str) -> None:
        if self.showing_response:
            # After seeing choice response, advance to next page
            if key in ("enter", "space"):
                self._advance_page()
            return

        if self.is_choice_page and self.page_complete:
            if not self.choice_made:
                if key in ("up", "w"):
                    self.selected_choice = max(0, self.selected_choice - 1)
                elif key in ("down", "s"):
                    choices = self.pages[self.current_page].get("choices", [])
                    self.selected_choice = min(
                        len(choices) - 1, self.selected_choice + 1
                    )
                elif key == "enter":
                    self._make_choice()
        else:
            # Text page
            if not self.page_complete:
                # Skip typewriter - reveal full text immediately
                self.skip_typewriter = True
                self.page_complete = True
            else:
                # Advance to next page
                if key in ("enter", "space"):
                    self._advance_page()

    def _make_choice(self) -> None:
        page = self.pages[self.current_page]
        choices = page.get("choices", [])
        if not choices:
            return
        choice = choices[self.selected_choice]
        self.choice_made = True
        self.choice_response = choice.get("response", "")
        self.showing_response = True

        # Set story flag if specified
        flag = choice.get("flag")
        if flag and hasattr(self.game, "narrative_manager"):
            self.game.narrative_manager.set_flag(flag)

        # Apply effect if specified
        effect = choice.get("effect")
        if effect and hasattr(self.game, "narrative_manager"):
            msg = self.game.narrative_manager.apply_choice_effect(effect)
            if msg:
                self.game.add_log(msg)

    def _advance_page(self) -> None:
        # Stop any ongoing narration when skipping ahead
        sound = getattr(self.game, "sound", None)
        if sound and hasattr(sound, "stop_speaking"):
            sound.stop_speaking()

        self.current_page += 1
        if self.current_page >= len(self.pages):
            self._finish()
            return
        self._reset_page_state()

    def _reset_page_state(self) -> None:
        self.char_index = 0
        self.page_complete = False
        self.skip_typewriter = False
        self.is_choice_page = (
            self.pages[self.current_page].get("type") == "choice"
        )
        self.selected_choice = 0
        self.choice_made = False
        self.choice_response = ""
        self.showing_response = False

        # Voice narration: read the page text aloud
        sound = getattr(self.game, "sound", None)
        if sound and hasattr(sound, "speak"):
            page_text = self.pages[self.current_page].get("text", "")
            if page_text:
                sound.speak(page_text)

    def _finish(self) -> None:
        if self.on_complete:
            self.on_complete()
        else:
            self.game.state_manager.pop()

    # -- lifecycle -----------------------------------------------------

    def on_enter(self) -> None:
        if self.pages:
            self._reset_page_state()

    # -- update --------------------------------------------------------

    def update(self, dt: float) -> None:
        if self.page_complete or self.skip_typewriter:
            return

        page = self.pages[self.current_page]
        full_text = page.get("text", "")

        self.typewriter_timer += dt
        chars_to_add = int(self.typewriter_timer * self.typewriter_speed)
        if chars_to_add > 0:
            self.char_index = min(self.char_index + chars_to_add, len(full_text))
            self.typewriter_timer = 0.0

        if self.char_index >= len(full_text):
            self.page_complete = True

    # -- render --------------------------------------------------------

    def render(self) -> RenderableType:
        from rich.align import Align
        from rich.console import Group
        from rich.panel import Panel
        from rich.text import Text

        from ui.hotbar import Hotbar

        if not self.pages or self.current_page >= len(self.pages):
            return Panel(Text("..."), title=f"[bold]{self.title}[/bold]")

        page = self.pages[self.current_page]
        parts: list[RenderableType] = []

        # Progress indicator
        progress = Text(
            f"\n  [{self.current_page + 1}/{len(self.pages)}]\n",
            style="dim",
        )
        parts.append(progress)

        # Main text (with typewriter effect)
        full_text = page.get("text", "")
        if self.skip_typewriter or self.page_complete:
            display_text = full_text
        else:
            display_text = full_text[: self.char_index]

        text_display = Text(
            f"\n  {display_text}\n", style="italic bright_white"
        )
        parts.append(text_display)

        # Show choices if this is a choice page and text is fully revealed
        if self.is_choice_page and self.page_complete:
            if self.showing_response:
                response = Text(
                    f"\n  {self.choice_response}\n", style="bold bright_cyan"
                )
                parts.append(response)
                parts.append(Text("\n  [Enter] Continue", style="dim"))
            elif not self.choice_made:
                choices = page.get("choices", [])
                parts.append(Text("\n"))
                for i, choice in enumerate(choices):
                    if i == self.selected_choice:
                        choice_text = Text(
                            f"  > {choice['label']}\n",
                            style="bold bright_yellow",
                        )
                    else:
                        choice_text = Text(
                            f"    {choice['label']}\n", style="dim"
                        )
                    parts.append(choice_text)
                parts.append(
                    Text("\n  [Up/Down] Choose  [Enter] Select", style="dim")
                )
        elif self.page_complete and not self.is_choice_page:
            parts.append(Text("\n  [Enter] Continue...", style="dim blink"))

        border_style = (
            "bright_yellow" if self.is_choice_page else "bright_cyan"
        )

        content = Panel(
            Align.center(Group(*parts)),
            title=f"[bold bright_cyan]{self.title}[/bold bright_cyan]",
            border_style=border_style,
            padding=(1, 3),
        )

        # Build hotbar
        hotbar = Hotbar()
        if self.is_choice_page and self.page_complete and not self.choice_made:
            hotbar_panel = hotbar.render(
                [("Up/Down", "Choose"), ("Enter", "Select")]
            )
        elif self.showing_response or self.page_complete:
            hotbar_panel = hotbar.render([("Enter", "Continue")])
        else:
            hotbar_panel = hotbar.render(
                [("Any Key", "Skip")],
                context=f"Page {self.current_page + 1}/{len(self.pages)}",
            )

        from ui.renderer import GameRenderer

        return GameRenderer().create_fullscreen_layout(content, hotbar_panel)

    def render_pygame(self, screen, font, renderer) -> None:
        """Render cinematic to Pygame screen."""
        import pygame
        from pygame_ui.colors import get_rgb
        from pygame_ui.pg_hotbar import PgHotbar

        w, h = renderer.screen_width, renderer.screen_height - renderer.hotbar_height
        surface = pygame.Surface((w, h))
        surface.fill((5, 5, 15))

        if not self.pages or self.current_page >= len(self.pages):
            renderer.draw_fullscreen_layout(screen, surface)
            return

        page = self.pages[self.current_page]
        y = 40
        margin = 60

        # Progress
        prog_text = f"[{self.current_page + 1}/{len(self.pages)}]"
        prog_surf = font.render_text(prog_text, get_rgb("grey50"))
        surface.blit(prog_surf, (w // 2 - prog_surf.get_width() // 2, y))
        y += font.char_height * 2

        # Title
        title_surf = font.render_text(self.title, get_rgb("bright_cyan"))
        surface.blit(title_surf, (w // 2 - title_surf.get_width() // 2, y))
        y += font.char_height * 3

        # Main text with typewriter
        full_text = page.get("text", "")
        if self.skip_typewriter or self.page_complete:
            display_text = full_text
        else:
            display_text = full_text[: self.char_index]

        # Word-wrap text
        max_chars = (w - margin * 2) // font.char_width
        words = display_text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 > max_chars:
                lines.append(current_line)
                current_line = word
            else:
                current_line = f"{current_line} {word}" if current_line else word
        if current_line:
            lines.append(current_line)

        for line in lines:
            line_surf = font.render_text(line, get_rgb("bright_white"))
            surface.blit(line_surf, (margin, y))
            y += font.char_height

        y += font.char_height

        # Choices
        if self.is_choice_page and self.page_complete:
            if self.showing_response:
                resp_surf = font.render_text(self.choice_response, get_rgb("bright_cyan"))
                surface.blit(resp_surf, (margin, y))
            elif not self.choice_made:
                choices = page.get("choices", [])
                for i, choice in enumerate(choices):
                    if i == self.selected_choice:
                        prefix = "> "
                        color = get_rgb("bright_yellow")
                    else:
                        prefix = "  "
                        color = get_rgb("grey50")
                    choice_surf = font.render_text(f"{prefix}{choice['label']}", color)
                    surface.blit(choice_surf, (margin + 20, y))
                    y += font.char_height + 4
        elif self.page_complete:
            hint = font.render_text("[Enter] Continue...", get_rgb("grey50"))
            surface.blit(hint, (w // 2 - hint.get_width() // 2, h - 40))

        # Border
        border_color = get_rgb("bright_yellow") if self.is_choice_page else get_rgb("bright_cyan")
        pygame.draw.rect(surface, border_color, surface.get_rect(), 1)

        hotbar = PgHotbar()
        if self.is_choice_page and self.page_complete and not self.choice_made:
            actions = [("U/D", "Choose"), ("Enter", "Select")]
        elif self.showing_response or self.page_complete:
            actions = [("Enter", "Continue")]
        else:
            actions = [("Any", "Skip")]
        hotbar_surf = hotbar.render(actions, font, renderer.hotbar_rect.width, renderer.hotbar_rect.height)
        renderer.draw_fullscreen_layout(screen, surface, hotbar_surf)
