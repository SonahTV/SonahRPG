"""Turn-based combat state with initiative, skills, items, and flee mechanics."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from effects.animation import AnimationManager, FlashAnimation, ShakeAnimation, FloatingTextAnimation, PulseAnimation
from effects.particles import ParticleSystem
from effects.transitions import TransitionManager, FlashTransition
from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game
    from entities.enemy import Enemy


class CombatState(GameState):
    """Manages turn-based combat between the player and a group of enemies.

    Phases:
    - player_turn: choose attack / skills / items / flee
    - skill_select: pick a skill from the known list
    - item_select: pick a consumable from inventory
    - enemy_turn: enemies act with a short delay for readability
    - victory / defeat: end screens waiting for [Enter]
    """

    def __init__(self, game: Game, enemies: list[Enemy]) -> None:
        super().__init__(game)
        self.enemies = enemies
        self.combat_system = None
        self.combat_view = None
        self.renderer = None
        self.stats_panel = None
        self.log_panel = None
        self.hotbar = None

        self.selected_action = "attack"
        self.selected_target = 0
        self.phase = "player_turn"
        self.action_delay: float = 0.0
        self.skill_menu = None
        self.item_menu = None
        self.animation_manager = AnimationManager()
        self.particles = ParticleSystem()
        self.transition_manager = TransitionManager()

    # -- lifecycle -----------------------------------------------------

    def on_enter(self) -> None:
        from systems.combat import CombatSystem
        from ui.combat_view import CombatView
        from ui.hotbar import Hotbar
        from ui.log_panel import LogPanel
        from ui.renderer import GameRenderer
        from ui.stats_panel import StatsPanel

        self.combat_system = CombatSystem(self.game)
        self.combat_view = CombatView()
        self.renderer = GameRenderer()
        self.stats_panel = StatsPanel()
        self.log_panel = LogPanel()
        self.hotbar = Hotbar()

        self.combat_system.start_combat(self.game.player, self.enemies)
        self.game.add_log(
            f"[bold red]Combat begins! Round {self.combat_system.round_number}[/bold red]"
        )
        self.game.event_bus.emit("combat_start", enemies=self.enemies)
        self.transition_manager.start(FlashTransition(duration=0.2, color="bright_red"))
        self._check_turn()

    # -- turn flow -----------------------------------------------------

    def _check_turn(self) -> None:
        """Determine what happens next: player turn, enemy turn, or combat end."""
        result = self.combat_system.check_combat_end()
        if result == "victory":
            self.phase = "victory"
            self._handle_victory()
            return
        if result == "defeat":
            self.phase = "defeat"
            self._handle_defeat()
            return

        if self.combat_system.is_player_turn():
            self.phase = "player_turn"
            self.selected_action = "attack"
            # Process player status effects at start of turn
            messages = self.combat_system.process_status_effects(self.game.player)
            for msg in messages:
                self.game.add_log(msg)
            # Check if crowd-controlled
            from systems.status_effects import is_crowd_controlled

            if is_crowd_controlled(self.game.player):
                self.game.add_log(
                    "[yellow]You are stunned and cannot act![/yellow]"
                )
                self.combat_system.advance_turn()
                self.action_delay = 0.8
                self.phase = "enemy_turn"
        else:
            self.phase = "enemy_turn"
            self.action_delay = 0.5

    # -- input ---------------------------------------------------------

    def handle_input(self, key: str) -> None:
        if self.phase == "player_turn":
            self._handle_player_input(key)
        elif self.phase == "skill_select":
            self._handle_skill_input(key)
        elif self.phase == "item_select":
            self._handle_item_input(key)
        elif self.phase in ("victory", "defeat"):
            if key == "enter":
                self._finish_combat()

    def _handle_player_input(self, key: str) -> None:
        actions = ["attack", "skills", "items", "flee"]
        if key in ("left", "a"):
            idx = actions.index(self.selected_action)
            self.selected_action = actions[(idx - 1) % len(actions)]
        elif key in ("right", "d"):
            idx = actions.index(self.selected_action)
            self.selected_action = actions[(idx + 1) % len(actions)]
        elif key in ("up", "w"):
            self._change_target(-1)
        elif key in ("down", "s"):
            self._change_target(1)
        elif key == "enter":
            self._execute_action()
        elif key == "f":
            self.selected_action = "flee"
            self._execute_action()

    def _handle_skill_input(self, key: str) -> None:
        if key == "up" and self.skill_menu:
            self.skill_menu.move_up()
        elif key == "down" and self.skill_menu:
            self.skill_menu.move_down()
        elif key == "enter" and self.skill_menu:
            self._use_skill(self.skill_menu.get_selected())
        elif key == "escape":
            self.phase = "player_turn"

    def _handle_item_input(self, key: str) -> None:
        if key == "up" and self.item_menu:
            self.item_menu.move_up()
        elif key == "down" and self.item_menu:
            self.item_menu.move_down()
        elif key == "enter" and self.item_menu:
            self._use_combat_item(self.item_menu.selected_index)
        elif key == "escape":
            self.phase = "player_turn"

    # -- target selection ----------------------------------------------

    def _change_target(self, direction: int) -> None:
        alive_indices = [i for i, e in enumerate(self.enemies) if e.is_alive()]
        if not alive_indices:
            return
        try:
            current_idx = alive_indices.index(self.selected_target)
        except ValueError:
            current_idx = 0
        current_idx = (current_idx + direction) % len(alive_indices)
        self.selected_target = alive_indices[current_idx]

    # -- player actions ------------------------------------------------

    def _execute_action(self) -> None:
        if self.selected_action == "attack":
            result = self.combat_system.player_attack(self.selected_target)
            self.game.add_log(result["message"])

            # Boss mid-fight dialogue at 50% HP
            if self.selected_target < len(self.enemies):
                target = self.enemies[self.selected_target]
                if (getattr(target, "is_boss", False)
                        and target.is_alive()
                        and target.current_hp <= target.max_hp * 0.5
                        and not getattr(self, "_boss_dialogue_shown", False)):
                    self._boss_dialogue_shown = True
                    nm = getattr(self.game, "narrative_manager", None)
                    if nm:
                        lines = nm.get_boss_mid_fight_dialogue(target.name)
                        if lines:
                            for line in lines:
                                self.game.add_log(f"[bold bright_yellow]{line}[/bold bright_yellow]")

            if result.get("damage", 0) > 0:
                self.animation_manager.add(
                    FloatingTextAnimation(
                        duration=0.8, text=f"-{result['damage']}",
                        color="bright_red", start_x=15, start_y=2,
                    )
                )
                self.particles.emit_damage(15, 3)
            if result.get("critical"):
                self.animation_manager.add(
                    FlashAnimation(duration=0.3, color="bright_yellow")
                )
                self.animation_manager.add(ShakeAnimation(duration=0.3, intensity=2))
            if result.get("killed"):
                self.particles.emit_death(15, 3)
            self.combat_system.advance_turn()
            self.action_delay = 0.6
            self._check_turn()

        elif self.selected_action == "skills":
            self._open_skill_menu()

        elif self.selected_action == "items":
            self._open_item_menu()

        elif self.selected_action == "flee":
            if random.random() < 0.5:
                self.game.add_log("[green]You fled successfully![/green]")
                self.game.state_manager.pop()
            else:
                self.game.add_log("[red]Failed to flee![/red]")
                self.combat_system.advance_turn()
                self.action_delay = 0.6
                self._check_turn()

    def _open_skill_menu(self) -> None:
        from data.classes import CLASSES
        from ui.menu import Menu

        player = self.game.player
        cls_def = CLASSES.get(player.player_class)
        if not cls_def:
            self.game.add_log("[dim]No class data![/dim]")
            return

        usable_names: list[str] = []
        descriptions: list[str] = []
        for s in cls_def.skills:
            if s["name"] in player.known_skills:
                can_use, reason = player.can_use_skill(s["name"])
                status = "" if can_use else f"({reason})"
                usable_names.append(s["name"])
                descriptions.append(f"MP:{s['mp_cost']} {status}")

        if usable_names:
            self.skill_menu = Menu("Skills", usable_names, descriptions)
            self.phase = "skill_select"
        else:
            self.game.add_log("[dim]No skills available![/dim]")

    def _open_item_menu(self) -> None:
        from ui.menu import Menu

        consumables = [
            (i, it)
            for i, it in enumerate(self.game.player.inventory)
            if it.get("type") == "consumable"
        ]
        if consumables:
            names = [it.get("name", "Unknown") for _, it in consumables]
            self.item_menu = Menu("Items", names)
            self.item_menu._inventory_indices = [i for i, _ in consumables]
            self.phase = "item_select"
        else:
            self.game.add_log("[dim]No usable items![/dim]")

    def _use_skill(self, skill_name: str) -> None:
        player = self.game.player
        can_use, reason = player.can_use_skill(skill_name)
        if not can_use:
            self.game.add_log(f"[red]{reason}[/red]")
            return

        # Use CombatSystem's skill execution for proper targeting
        target_idx = self.selected_target if self.selected_target < len(self.enemies) else None
        result = self.combat_system.player_use_skill(skill_name, target_idx)

        if result.get("message"):
            self.game.add_log(result["message"])

        self.animation_manager.add(
            FlashAnimation(duration=0.3, color="bright_cyan")
        )

        # Particle effects based on skill result
        if result.get("heal", 0) > 0:
            self.particles.emit_heal(15, 5)
            self.animation_manager.add(
                FloatingTextAnimation(
                    duration=0.8, text=f"+{result['heal']}",
                    color="bright_green", start_x=15, start_y=5,
                )
            )
        if result.get("damage", 0) > 0:
            self.animation_manager.add(
                FloatingTextAnimation(
                    duration=0.8, text=f"-{result['damage']}",
                    color="bright_red", start_x=15, start_y=2,
                )
            )
        self.particles.emit_magic(15, 3, color="bright_cyan")

        self.phase = "player_turn"
        self.combat_system.advance_turn()
        self.action_delay = 0.6
        self._check_turn()

    def _use_combat_item(self, menu_index: int) -> None:
        inv_idx = menu_index
        if hasattr(self.item_menu, "_inventory_indices"):
            inv_idx = self.item_menu._inventory_indices[menu_index]

        from systems.inventory import InventorySystem

        inv_sys = InventorySystem(self.game)
        success, msg = inv_sys.use_item(self.game.player, inv_idx)
        self.game.add_log(msg)

        if success:
            self.particles.emit_heal(15, 5)
            self.animation_manager.add(
                FloatingTextAnimation(
                    duration=0.8, text="Healed!",
                    color="bright_green", start_x=15, start_y=5,
                )
            )
            self.phase = "player_turn"
            self.combat_system.advance_turn()
            self.action_delay = 0.6
            self._check_turn()
        else:
            self.phase = "player_turn"

    # -- combat resolution ---------------------------------------------

    def _handle_victory(self) -> None:
        rewards = self.combat_system.get_combat_rewards()
        player = self.game.player

        # Check for boss defeat narrative
        nm = getattr(self.game, "narrative_manager", None)
        for enemy in self.enemies:
            if nm and getattr(enemy, "is_boss", False):
                boss_name = getattr(enemy, "name", "")
                epilogue = nm.on_boss_defeated(boss_name)
                if epilogue:
                    self._pending_boss_epilogue = epilogue

        self.game.add_log("[bold bright_green]Victory![/bold bright_green]")
        self.game.add_log(
            f"Gained [bold]{rewards['xp']}[/bold] XP and [yellow]{rewards['gold']}g[/yellow]!"
        )

        player.gold += rewards["gold"]
        self.particles.emit_gold(15, 5)

        from systems.leveling import LevelingSystem

        level_sys = LevelingSystem(self.game)
        if level_sys.award_xp(player, rewards["xp"]):
            gains = level_sys.process_level_up(player)
            self.game.add_log(
                f"[bold bright_yellow]LEVEL UP! Now level {gains['level']}![/bold bright_yellow]"
            )
            self.particles.emit_level_up(15, 4)
            if gains.get("new_skills_available"):
                for sn in gains["new_skills_available"]:
                    self.game.add_log(
                        f"[bold cyan]New skill available: {sn}[/bold cyan]"
                    )

        for item in rewards.get("items", []):
            if player.add_item(item):
                self.game.add_log(
                    f"Obtained [bold]{item.get('name', 'item')}[/bold]!"
                )
            else:
                self.game.add_log(
                    f"[dim]Inventory full, couldn't pick up {item.get('name', 'item')}[/dim]"
                )

        self.game.event_bus.emit("combat_end")

    def _handle_defeat(self) -> None:
        self.game.add_log("[bold red]You have been defeated...[/bold red]")

    def _finish_combat(self) -> None:
        if self.phase == "defeat":
            self.game.state_manager.pop()
            from states.game_over_state import GameOverState

            self.game.state_manager.push(GameOverState(self.game))
        else:
            self.game.state_manager.pop()

            # Show boss epilogue cinematic if available
            epilogue = getattr(self, "_pending_boss_epilogue", None)
            if epilogue:
                from states.cinematic_state import CinematicState

                self.game.state_manager.push(
                    CinematicState(self.game, epilogue, title="The Aftermath")
                )

            # Check if this was the final boss → trigger ending
            nm = getattr(self.game, "narrative_manager", None)
            if nm and "Demon Lord" in nm.bosses_defeated and not nm.ending_shown:
                nm.ending_shown = True
                from states.ending_state import EndingState

                self.game.state_manager.push(EndingState(self.game))

    # -- update --------------------------------------------------------

    def update(self, dt: float) -> None:
        self.animation_manager.tick(dt)
        self.particles.tick(dt)
        self.transition_manager.tick(dt)

        if self.action_delay > 0:
            self.action_delay -= dt
            if self.action_delay <= 0 and self.phase == "enemy_turn":
                self._execute_enemy_turn()

    def _execute_enemy_turn(self) -> None:
        current = self.combat_system.get_current_entity()
        if current and current is not self.game.player and current.is_alive():
            # Process enemy status effects
            messages = self.combat_system.process_status_effects(current)
            for msg in messages:
                self.game.add_log(msg)

            from systems.status_effects import is_crowd_controlled

            if not is_crowd_controlled(current):
                result = self.combat_system.enemy_turn(current)
                self.game.add_log(result["message"])

                if result.get("damage", 0) > 0:
                    self.animation_manager.add(
                        FlashAnimation(duration=0.2, color="bright_red")
                    )
                    self.animation_manager.add(
                        FloatingTextAnimation(
                            duration=0.8, text=f"-{result['damage']}",
                            color="bright_red", start_x=15, start_y=8,
                        )
                    )
                    self.particles.emit_damage(15, 8)

        self.combat_system.advance_turn()
        self._check_turn()

        # If still enemy turn, queue next enemy with a delay
        if self.phase == "enemy_turn":
            self.action_delay = 0.5

    # -- render --------------------------------------------------------

    def render(self) -> RenderableType:
        from rich.console import Group
        from rich.text import Text

        player = self.game.player

        combat_panel = self.combat_view.render(
            player, self.enemies, self.combat_system, self.selected_action,
            animation_manager=self.animation_manager,
            particles=self.particles,
        )
        stats_panel = self.stats_panel.render(player)
        log_panel = self.log_panel.render(self.game.combat_log, max_lines=8)

        # Build hotbar based on phase
        if self.phase == "player_turn":
            actions = [
                ("Left/Right", "Action"),
                ("Up/Down", "Target"),
                ("Enter", "Confirm"),
            ]
        elif self.phase == "skill_select":
            actions = [("Up/Down", "Select"), ("Enter", "Use"), ("Esc", "Back")]
        elif self.phase == "item_select":
            actions = [("Up/Down", "Select"), ("Enter", "Use"), ("Esc", "Back")]
        else:
            actions = [("Enter", "Continue")]

        hotbar_panel = self.hotbar.render(actions)

        # Overlay skill/item menu on combat panel when selecting
        display_panel = combat_panel
        if self.phase == "skill_select" and self.skill_menu:
            display_panel = Group(combat_panel, self.skill_menu.render())
        elif self.phase == "item_select" and self.item_menu:
            display_panel = Group(combat_panel, self.item_menu.render())

        # Overlay transition effect if active
        render_parts = [display_panel]
        if self.transition_manager.is_active():
            transition_overlay = self.transition_manager.render(60, 3)
            if transition_overlay:
                render_parts.append(transition_overlay)
        display_panel = Group(*render_parts)

        return self.renderer.create_combat_layout(
            display_panel, stats_panel, log_panel, hotbar_panel
        )

    def render_pygame(self, screen, font, renderer) -> None:
        """Render combat state to Pygame screen."""
        from pygame_ui.pg_combat_view import PgCombatView
        from pygame_ui.pg_hotbar import PgHotbar
        from pygame_ui.pg_log_panel import PgLogPanel
        from pygame_ui.pg_stats_panel import PgStatsPanel

        if not hasattr(self, "_pg_combat"):
            self._pg_combat = PgCombatView()
            self._pg_stats = PgStatsPanel()
            self._pg_log = PgLogPanel()
            self._pg_hotbar = PgHotbar()

        self._pg_combat.selected_target = self.selected_target
        player = self.game.player

        combat_surf = self._pg_combat.render(
            player, self.enemies, self.combat_system, self.selected_action,
            font, renderer.map_rect.width, renderer.map_rect.height,
            animation_manager=self.animation_manager,
            particles=self.particles,
        )
        stats_surf = self._pg_stats.render(
            player, font, renderer.stats_rect.width, renderer.main_height,
        )
        log_surf = self._pg_log.render(
            self.game.combat_log, font,
            renderer.log_rect.width, renderer.log_rect.height, max_lines=8,
        )

        if self.phase == "player_turn":
            actions = [("L/R", "Action"), ("U/D", "Target"), ("Enter", "Confirm")]
        elif self.phase in ("skill_select", "item_select"):
            actions = [("U/D", "Select"), ("Enter", "Use"), ("Esc", "Back")]
        else:
            actions = [("Enter", "Continue")]

        hotbar_surf = self._pg_hotbar.render(
            actions, font, renderer.hotbar_rect.width, renderer.hotbar_rect.height,
        )
        renderer.draw_combat_layout(screen, combat_surf, stats_surf, log_surf, hotbar_surf)
