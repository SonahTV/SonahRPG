"""Ending cinematic state -- displays the appropriate ending based on narrative choices."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game

# -- Ending narrative data ---------------------------------------------

ENDING_NARRATIVES: dict[str, dict] = {
    "binding_restored": {
        "title": "The Binding Restored",
        "pages": [
            {
                "type": "text",
                "text": (
                    "With the Demon Lord vanquished, the ancient seals flare "
                    "to life once more. The rift between worlds shudders and "
                    "begins to close, darkness receding like a tide."
                ),
            },
            {
                "type": "text",
                "text": (
                    "The dungeon groans around you as its purpose is fulfilled. "
                    "Stones shift and corridors collapse behind you, urging you "
                    "upward. The binding holds — for now."
                ),
            },
            {
                "type": "text",
                "text": (
                    "You emerge into sunlight for the first time in what feels "
                    "like an eternity. The world is safe, though you carry the "
                    "weight of everything you witnessed in the depths."
                ),
            },
        ],
    },
    "liberator": {
        "title": "The Liberator",
        "pages": [
            {
                "type": "text",
                "text": (
                    "You showed mercy where others would have shown steel. The "
                    "creatures of the deep remember. As the Demon Lord falls, "
                    "the Goblin King, Spider Queen, and Bone Dragon rise not "
                    "as enemies — but as allies."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Together, you forge a new pact. The dungeon will not be "
                    "sealed — it will be governed. The monsters of the deep "
                    "will guard the rift willingly, bound by gratitude rather "
                    "than chains."
                ),
            },
            {
                "type": "text",
                "text": (
                    "You are named Liberator, the one who broke the cycle of "
                    "endless slaughter. Peace, fragile and unprecedented, "
                    "settles over the depths. Perhaps it will last."
                ),
            },
        ],
    },
    "truth_seeker": {
        "title": "The Truth Seeker",
        "pages": [
            {
                "type": "text",
                "text": (
                    "Through scattered fragments of lore, you have pieced "
                    "together the true history of this place. The dungeon was "
                    "not built to contain evil — it was built to hide a truth "
                    "the surface world could not accept."
                ),
            },
            {
                "type": "text",
                "text": (
                    "The Consortium created the rift deliberately, feeding it "
                    "with condemned souls to power their great works above. "
                    "Every adventurer sent below was a sacrifice, their "
                    "suffering converted to energy."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Armed with this knowledge, you ascend not as a hero "
                    "but as a witness. The world will learn what was done "
                    "in its name. The Consortium's reign of secrets ends today."
                ),
            },
        ],
    },
    "hollow_victory": {
        "title": "A Hollow Victory",
        "pages": [
            {
                "type": "text",
                "text": (
                    "You defeated the Demon Lord, but at what cost? Rushing "
                    "through the depths, you barely understood what you fought "
                    "or why. The rift is sealed, but its secrets die with it."
                ),
            },
            {
                "type": "text",
                "text": (
                    "The surface celebrates your return, but something feels "
                    "wrong. Hollow. You won, and yet the nightmares continue. "
                    "The dungeon's whispers follow you, unresolved."
                ),
            },
            {
                "type": "text",
                "text": (
                    "Perhaps if you had delved deeper, fought harder, listened "
                    "more carefully... but it is too late now. The binding holds, "
                    "and nobody asks what it truly binds."
                ),
            },
        ],
    },
}


class EndingState(GameState):
    """Ending cinematic shown after the final boss is defeated.

    Determines the ending type from the narrative manager, plays the
    ending text with a typewriter crawl (via CinematicState internally),
    then displays a stats summary and allows returning to the main menu.

    Args:
        game: Game instance
    """

    # Phases: "cinematic" -> "stats" -> "done"
    PHASE_CINEMATIC = "cinematic"
    PHASE_STATS = "stats"
    PHASE_DONE = "done"

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.ending_type = "binding_restored"
        self.ending_data: dict = ENDING_NARRATIVES["binding_restored"]
        self.phase = self.PHASE_CINEMATIC
        self.stats_timer = 0.0  # delay before "return to menu" is active
        self._start_time = time.time()

    # -- lifecycle -----------------------------------------------------

    def on_enter(self) -> None:
        # Determine ending
        if hasattr(self.game, "narrative_manager"):
            self.ending_type = self.game.narrative_manager.determine_ending()
            self.game.narrative_manager.ending_shown = True

        self.ending_data = ENDING_NARRATIVES.get(
            self.ending_type, ENDING_NARRATIVES["binding_restored"]
        )

        # Push cinematic state for the ending text crawl
        from states.cinematic_state import CinematicState

        pages = self.ending_data.get("pages", [])
        self.game.state_manager.push(
            CinematicState(
                self.game,
                pages=pages,
                on_complete=self._on_cinematic_done,
                title=self.ending_data.get("title", "The End"),
            )
        )

    def _on_cinematic_done(self) -> None:
        """Callback after the cinematic text pages are finished."""
        # Pop the cinematic state — we are the state beneath it
        self.game.state_manager.pop()
        self.phase = self.PHASE_STATS
        self.stats_timer = 0.0

    # -- input ---------------------------------------------------------

    def handle_input(self, key: str) -> None:
        if self.phase == self.PHASE_CINEMATIC:
            # Input is handled by the CinematicState on top of the stack
            return

        if self.phase == self.PHASE_STATS:
            if key == "enter" and self.stats_timer > 2.0:
                self.phase = self.PHASE_DONE
                self._return_to_menu()

    def _return_to_menu(self) -> None:
        from states.main_menu import MainMenuState

        self.game.state_manager.clear()
        self.game.state_manager.push(MainMenuState(self.game))

    # -- update --------------------------------------------------------

    def update(self, dt: float) -> None:
        if self.phase == self.PHASE_STATS:
            self.stats_timer += dt

    # -- render --------------------------------------------------------

    def render(self) -> RenderableType:
        if self.phase == self.PHASE_CINEMATIC:
            # The CinematicState on top handles rendering; this is a
            # fallback in case render is called during transition.
            from rich.text import Text

            return Text("")

        return self._render_stats_screen()

    def _render_stats_screen(self) -> RenderableType:
        from rich.align import Align
        from rich.console import Group
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        from ui.hotbar import Hotbar
        from ui.renderer import GameRenderer

        parts: list[RenderableType] = []

        # Ending title
        title = self.ending_data.get("title", "The End")
        parts.append(Text(f"\n  {title}\n", style="bold bright_cyan"))
        parts.append(Text("  " + "=" * 40 + "\n\n", style="dim bright_cyan"))

        # Stats table
        stats = Table(
            show_header=False,
            show_edge=False,
            box=None,
            padding=(0, 2),
        )
        stats.add_column("label", style="bright_yellow", min_width=20)
        stats.add_column("value", style="bright_white")

        player = self.game.player

        if player:
            stats.add_row("Name", f"{player.name} the {player.player_class}")
            stats.add_row("Level", str(player.level))
            stats.add_row(
                "Floor Reached", str(getattr(player, "floor", "?"))
            )
            stats.add_row("Gold", str(player.gold))

        if hasattr(self.game, "narrative_manager"):
            nm = self.game.narrative_manager
            stats.add_row(
                "Bosses Defeated", str(len(nm.bosses_defeated))
            )
            stats.add_row("Bosses Spared", str(len(nm.bosses_spared)))
            found, total = nm.get_lore_progress()
            stats.add_row("Lore Discovered", f"{found}/{total}")
            stats.add_row("Story Flags Set", str(len(nm.story_flags)))

        # Play time
        elapsed = time.time() - self._start_time
        # Use session start as rough proxy; ideally game tracks total time
        if hasattr(self.game, "play_time"):
            elapsed = self.game.play_time
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        stats.add_row("Time Played", f"{minutes}m {seconds}s")

        parts.append(stats)

        # Ending badge
        ending_style = {
            "binding_restored": "bright_white",
            "liberator": "bright_green",
            "truth_seeker": "bright_cyan",
            "hollow_victory": "dim bright_red",
        }.get(self.ending_type, "white")

        parts.append(
            Text(f"\n\n  Ending: {title}\n", style=f"bold {ending_style}")
        )

        # The End
        parts.append(Text("\n"))
        parts.append(
            Text(
                "  ~~~ THE END ~~~\n",
                style="bold bright_yellow",
            )
        )

        # Prompt
        if self.stats_timer > 2.0:
            parts.append(
                Text(
                    "\n  Press [Enter] to return to the main menu\n",
                    style="dim",
                )
            )

        content = Panel(
            Align.center(Group(*parts)),
            title=f"[bold bright_yellow]~~ {title} ~~[/bold bright_yellow]",
            border_style="bright_yellow",
            padding=(1, 3),
        )

        hotbar = Hotbar()
        if self.stats_timer > 2.0:
            hotbar_panel = hotbar.render([("Enter", "Main Menu")])
        else:
            hotbar_panel = hotbar.render([], context="...")

        return GameRenderer().create_fullscreen_layout(content, hotbar_panel)

    def render_pygame(self, screen, font, renderer) -> None:
        """Render ending stats screen to Pygame."""
        import pygame
        from pygame_ui.colors import get_rgb
        from pygame_ui.pg_hotbar import PgHotbar

        if self.phase == self.PHASE_CINEMATIC:
            return  # CinematicState on top handles it

        w, h = renderer.screen_width, renderer.screen_height - renderer.hotbar_height
        surface = pygame.Surface((w, h))
        surface.fill((5, 5, 15))

        title = self.ending_data.get("title", "The End")
        y = 40
        cx = w // 2

        # Title
        title_surf = font.render_text(title, get_rgb("bright_cyan"))
        surface.blit(title_surf, (cx - title_surf.get_width() // 2, y))
        y += font.char_height * 3

        # Stats
        player = self.game.player
        stats_lines = []
        if player:
            stats_lines.append(f"Name: {player.name} the {player.player_class}")
            stats_lines.append(f"Level: {player.level}")
            stats_lines.append(f"Floor: {getattr(player, 'floor', '?')}")
            stats_lines.append(f"Gold: {player.gold}")

        nm = getattr(self.game, "narrative_manager", None)
        if nm:
            stats_lines.append(f"Bosses Defeated: {len(nm.bosses_defeated)}")
            stats_lines.append(f"Bosses Spared: {len(nm.bosses_spared)}")
            found, total = nm.get_lore_progress()
            stats_lines.append(f"Lore: {found}/{total}")

        for line in stats_lines:
            surface.blit(font.render_text(f"  {line}", get_rgb("bright_white")), (cx - 150, y))
            y += font.char_height + 2

        y += font.char_height * 2
        end_surf = font.render_text("~~~ THE END ~~~", get_rgb("bright_yellow"))
        surface.blit(end_surf, (cx - end_surf.get_width() // 2, y))

        if self.stats_timer > 2.0:
            y += font.char_height * 3
            hint = font.render_text("Press [Enter] to return to menu", get_rgb("grey50"))
            surface.blit(hint, (cx - hint.get_width() // 2, y))

        pygame.draw.rect(surface, get_rgb("bright_yellow"), surface.get_rect(), 1)

        hotbar = PgHotbar()
        actions = [("Enter", "Menu")] if self.stats_timer > 2.0 else []
        hotbar_surf = hotbar.render(actions, font, renderer.hotbar_rect.width, renderer.hotbar_rect.height)
        renderer.draw_fullscreen_layout(screen, surface, hotbar_surf)
