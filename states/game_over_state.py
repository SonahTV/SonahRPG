"""Game over state -- shown when the player dies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game


class GameOverState(GameState):
    """Death screen showing run statistics and ASCII tombstone.

    A short delay prevents accidental dismissal; after 1 second the
    player can press Enter to return to the main menu.
    """

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.timer: float = 0.0

    def handle_input(self, key: str) -> None:
        if key == "enter" and self.timer > 1.0:
            from states.main_menu import MainMenuState

            self.game.state_manager.clear()
            self.game.state_manager.push(MainMenuState(self.game))

    def update(self, dt: float) -> None:
        self.timer += dt

    def render(self) -> RenderableType:
        from rich.align import Align
        from rich.panel import Panel
        from rich.text import Text

        from data.ascii_art import DEATH_ART, GAME_OVER_ART

        player = self.game.player
        text = Text()
        text.append(GAME_OVER_ART + "\n", style="bold red")
        text.append(DEATH_ART + "\n", style="dim red")
        text.append("\n  YOU HAVE FALLEN\n\n", style="bold bright_red")

        if player:
            text.append(
                f"  {player.name} the {player.player_class}\n",
                style="bright_white",
            )
            text.append(
                f"  Reached Level {player.level}, Floor {player.floor}\n",
                style="dim",
            )
            text.append(f"  Gold collected: {player.gold}\n", style="yellow")
            text.append(
                f"  Enemies slain: {len(player.completed_quests)} quests completed\n\n",
                style="dim",
            )

        if self.timer > 1.0:
            text.append("  Press [Enter] to return to menu\n", style="dim")

        return Align.center(
            Panel(
                text,
                title="[bold red]Game Over[/bold red]",
                border_style="red",
                width=60,
            ),
            vertical="middle",
        )

    def render_pygame(self, screen, font, renderer) -> None:
        import pygame
        from pygame_ui.colors import get_rgb

        w, h = renderer.screen_width, renderer.screen_height
        surface = pygame.Surface((w, h))
        surface.fill((20, 0, 0))

        player = self.game.player
        y = h // 4
        cx = w // 2

        title = font.render_text("GAME OVER", get_rgb("bright_red"))
        surface.blit(title, (cx - title.get_width() // 2, y))
        y += font.char_height * 3

        msg = font.render_text("YOU HAVE FALLEN", get_rgb("red"))
        surface.blit(msg, (cx - msg.get_width() // 2, y))
        y += font.char_height * 3

        if player:
            info = f"{player.name} the {player.player_class} - Lv.{player.level}, Floor {player.floor}"
            surface.blit(font.render_text(info, get_rgb("bright_white")), (cx - len(info) * font.char_width // 2, y))
            y += font.char_height * 2
            gold_text = f"Gold: {player.gold}"
            surface.blit(font.render_text(gold_text, get_rgb("yellow")), (cx - len(gold_text) * font.char_width // 2, y))
            y += font.char_height * 2

        if self.timer > 1.0:
            hint = "Press [Enter] to return to menu"
            surface.blit(font.render_text(hint, get_rgb("grey50")), (cx - len(hint) * font.char_width // 2, y))

        renderer.draw_fullscreen_layout(screen, surface)
