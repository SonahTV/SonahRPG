"""Level-up celebration screen with animated stars."""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game


class LevelUpState(GameState):
    """Overlay that celebrates a level up with animated star effects.

    Displayed as a centered panel; press Enter to dismiss.
    """

    def __init__(self, game: Game, gains: dict) -> None:
        super().__init__(game)
        self.gains = gains
        self.animation_timer: float = 0.0

    def handle_input(self, key: str) -> None:
        if key == "enter":
            self.game.state_manager.pop()

    def update(self, dt: float) -> None:
        self.animation_timer += dt

    def render(self) -> RenderableType:
        from rich.align import Align
        from rich.panel import Panel
        from rich.text import Text

        player = self.game.player
        text = Text()

        # Animated stars that alternate colours
        stars = "* + * + * + * + *"
        phase = int(self.animation_timer * 3) % 2
        star_style = "bold bright_yellow" if phase == 0 else "bold bright_cyan"
        text.append(f"\n  {stars}\n", style=star_style)
        text.append("\n  LEVEL UP!\n\n", style="bold bright_yellow")
        text.append(
            f"  {player.name} reached Level {self.gains['level']}!\n\n",
            style="bold bright_white",
        )
        text.append(f"  HP: +{self.gains['hp_gain']}\n", style="bold red")
        text.append(f"  MP: +{self.gains['mp_gain']}\n", style="bold blue")
        text.append("  Skill Points: +1\n\n", style="bold green")

        new_skills = self.gains.get("new_skills_available", [])
        if new_skills:
            text.append("  New skills available:\n", style="bold cyan")
            for sn in new_skills:
                text.append(f"    - {sn}\n", style="bright_cyan")
            text.append("\n")

        text.append(f"  {stars}\n", style=star_style)
        text.append("\n  Press [Enter] to continue\n", style="dim")

        return Align.center(
            Panel(
                text,
                title="[bold bright_yellow]Level Up[/bold bright_yellow]",
                border_style="bright_yellow",
                width=50,
            ),
            vertical="middle",
        )

    def render_pygame(self, screen, font, renderer) -> None:
        import pygame
        from pygame_ui.colors import get_rgb

        w, h = renderer.screen_width, renderer.screen_height
        surface = pygame.Surface((w, h))
        surface.fill((10, 10, 0))

        player = self.game.player
        y = h // 4
        cx = w // 2

        title = font.render_text("* LEVEL UP! *", get_rgb("bright_yellow"))
        surface.blit(title, (cx - title.get_width() // 2, y))
        y += font.char_height * 3

        info = f"{player.name} reached Level {self.gains['level']}!"
        surface.blit(font.render_text(info, get_rgb("bright_white")), (cx - len(info) * font.char_width // 2, y))
        y += font.char_height * 2

        surface.blit(font.render_text(f"  HP: +{self.gains['hp_gain']}", get_rgb("bright_red")), (cx - 80, y))
        y += font.char_height
        surface.blit(font.render_text(f"  MP: +{self.gains['mp_gain']}", get_rgb("bright_blue")), (cx - 80, y))
        y += font.char_height
        surface.blit(font.render_text("  Skill Points: +1", get_rgb("bright_green")), (cx - 80, y))
        y += font.char_height * 2

        hint = "Press [Enter] to continue"
        surface.blit(font.render_text(hint, get_rgb("grey50")), (cx - len(hint) * font.char_width // 2, y))

        renderer.draw_fullscreen_layout(screen, surface)
