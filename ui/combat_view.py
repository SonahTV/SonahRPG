import math
import time

from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.console import Group


class CombatView:
    """Renders the combat scene with ASCII art enemies, HP bars, and action menu."""

    def __init__(self):
        self.selected_target: int = 0
        self.player_flash: str | None = None  # for damage flash effect
        self.enemy_flashes: dict[int, str] = {}  # enemy_index -> flash color
        self._pulse_time: float = 0.0  # for pulsing border animation

    def render(
        self,
        player,
        enemies: list,
        combat_system,
        selected_action: str = "attack",
        animation_manager=None,
        particles=None,
    ) -> Panel:
        """Render combat scene.

        Layout within the panel:
        - Top: Enemy ASCII art side by side (or stacked if many)
        - Below art: Enemy name + HP bars
        - Middle: Turn indicator
        - Bottom: Player info and action menu

        Currently selected target gets highlighted border.
        Dead enemies are greyed out with strikethrough.
        """
        parts = []

        # Render enemies
        enemy_displays = []
        for i, enemy in enumerate(enemies):
            alive = enemy.is_alive() if hasattr(enemy, "is_alive") else (getattr(enemy, "current_hp", 0) > 0)

            if not alive:
                art_style = "dim strikethrough"
                border = "dim"
            elif i == self.selected_target:
                art_style = "bold"
                # Pulsing border for selected target
                self._pulse_time = time.time()
                pulse_phase = math.sin(self._pulse_time * 4.0)
                border = "bright_yellow" if pulse_phase > 0 else "yellow"
            else:
                art_style = ""
                border = "red"

            # Apply flash override if present
            if i in self.enemy_flashes:
                art_style = self.enemy_flashes[i]

            # Build enemy display
            enemy_text = Text()
            ascii_art = getattr(enemy, "ascii_art", None) or self._default_enemy_art(enemy)
            enemy_text.append(ascii_art, style=art_style)

            # HP bar
            max_hp = getattr(enemy, "max_hp", 1)
            current_hp = getattr(enemy, "current_hp", 0)
            hp_pct = current_hp / max_hp if max_hp > 0 else 0
            hp_bar = self._make_hp_bar(hp_pct, 20)

            name = getattr(enemy, "name", "Enemy")
            level = getattr(enemy, "level", 1)
            enemy_text.append(f"\n{name} Lv.{level}\n")
            enemy_text.append_text(hp_bar)
            enemy_text.append(f"\n{current_hp}/{max_hp} HP", style="dim")

            enemy_displays.append(Panel(enemy_text, border_style=border, width=30))

        # Show enemies in columns
        if enemy_displays:
            parts.append(Columns(enemy_displays, equal=True, expand=True))

        # Show flavor text for selected target
        if self.selected_target < len(enemies):
            selected_enemy = enemies[self.selected_target]
            flavor = getattr(selected_enemy, "flavor_text", None)
            if flavor and (selected_enemy.is_alive() if hasattr(selected_enemy, "is_alive") else True):
                flavor_display = Text(f"  \"{flavor}\"", style="dim italic")
                parts.append(flavor_display)

        # Render floating text animations
        if animation_manager:
            for ft in animation_manager.floating_texts:
                parts.append(ft.get_styled_text())

        # Render particle overlay
        if particles and particles.has_particles():
            particle_map = particles.render_to_text(width=40, height=10)
            if particle_map:
                particle_line = Text("  ")
                for (px, py), (char, style) in sorted(particle_map.items()):
                    particle_line.append(char, style=style)
                parts.append(particle_line)

        # Player flash indicator
        if self.player_flash:
            flash_text = Text("\n  !! YOU TAKE DAMAGE !!", style=f"bold {self.player_flash}")
            parts.append(flash_text)

        # Turn indicator
        current = None
        if hasattr(combat_system, "get_current_entity"):
            current = combat_system.get_current_entity()

        round_num = getattr(combat_system, "round_number", 1)
        if current:
            turn_text = Text(f"\n  Round {round_num} -- ", style="bold")
            current_name = getattr(current, "name", "???")
            turn_text.append(f"{current_name}'s turn", style="bold bright_yellow")
            parts.append(turn_text)
        else:
            turn_text = Text(f"\n  Round {round_num}", style="bold")
            parts.append(turn_text)

        # Action menu (only show on player's turn)
        is_player_turn = False
        if hasattr(combat_system, "is_player_turn"):
            is_player_turn = combat_system.is_player_turn()

        if is_player_turn:
            actions = Text("\n  ")
            action_items = [
                ("Attack", "A"),
                ("Skills", "S"),
                ("Items", "I"),
                ("Flee", "F"),
            ]
            for action, key in action_items:
                if action.lower() == selected_action.lower():
                    actions.append(f" [{key}]{action} ", style="bold black on white")
                else:
                    actions.append(f" [{key}]{action} ", style="bold")
                actions.append("  ")
            parts.append(actions)

        # Target selection hint
        if is_player_turn and len(enemies) > 1:
            target_hint = Text("\n  ", style="dim")
            target_hint.append("[LEFT/RIGHT]", style="bold bright_yellow")
            target_hint.append(" Switch target  ")
            target_hint.append("[ENTER]", style="bold bright_yellow")
            target_hint.append(" Confirm")
            parts.append(target_hint)

        return Panel(
            Group(*parts),
            title="[bold red]--- Combat ---[/bold red]",
            border_style="red",
        )

    def _make_hp_bar(self, percentage: float, width: int = 20) -> Text:
        """Create a colored HP bar using block characters."""
        percentage = max(0.0, min(1.0, percentage))
        filled = int(percentage * width)
        empty = width - filled

        # Color based on HP percentage
        if percentage > 0.6:
            bar_color = "bold green"
        elif percentage > 0.3:
            bar_color = "bold yellow"
        else:
            bar_color = "bold red"

        bar = Text("  HP [")
        bar.append("█" * filled, style=bar_color)
        bar.append("░" * empty, style="dim")
        bar.append(f"] {int(percentage * 100)}%")
        return bar

    def _default_enemy_art(self, enemy) -> str:
        """Generate a simple default ASCII art if enemy has none."""
        name = getattr(enemy, "name", "Enemy")
        return (
            "  /\\_/\\\n"
            " ( o.o )\n"
            f"  > ^ <  {name[:8]}\n"
        )

    def set_flash(self, target_index: int | None, color: str) -> None:
        """Set a flash effect on an enemy (or player if target_index is None)."""
        if target_index is None:
            self.player_flash = color
        else:
            self.enemy_flashes[target_index] = color

    def clear_flashes(self) -> None:
        """Clear all flash effects."""
        self.player_flash = None
        self.enemy_flashes.clear()

    def select_next_target(self, enemies: list) -> None:
        """Move target selection to the next alive enemy."""
        if not enemies:
            return
        start = self.selected_target
        for _ in range(len(enemies)):
            self.selected_target = (self.selected_target + 1) % len(enemies)
            e = enemies[self.selected_target]
            alive = e.is_alive() if hasattr(e, "is_alive") else (getattr(e, "current_hp", 0) > 0)
            if alive:
                return
        self.selected_target = start

    def select_prev_target(self, enemies: list) -> None:
        """Move target selection to the previous alive enemy."""
        if not enemies:
            return
        start = self.selected_target
        for _ in range(len(enemies)):
            self.selected_target = (self.selected_target - 1) % len(enemies)
            e = enemies[self.selected_target]
            alive = e.is_alive() if hasattr(e, "is_alive") else (getattr(e, "current_hp", 0) > 0)
            if alive:
                return
        self.selected_target = start
