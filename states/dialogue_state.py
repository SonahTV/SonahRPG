"""NPC dialogue state -- conversation, shop access, healing, quests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game
    from entities.npc import NPC


class DialogueState(GameState):
    """Multi-phase NPC interaction.

    Phases:
    - dialogue: cycle through NPC dialogue lines with Enter
    - options: choose an action (Shop, Heal, Quests, Leave)
    """

    def __init__(self, game: Game, npc: NPC) -> None:
        super().__init__(game)
        self.npc = npc
        self.dialogue_index = 0
        self.options: list[tuple[str, str]] = []  # [(display_label, action_key)]
        self.selected_option = 0
        self.phase = "dialogue"  # "dialogue" or "options"

    def on_enter(self) -> None:
        if self.npc.dialogue:
            self.phase = "dialogue"
        else:
            self.phase = "options"
        self._build_options()

    def _build_options(self) -> None:
        self.options = []
        if self.npc.role == "merchant":
            self.options.append(("Shop", "browse_shop"))
        if self.npc.role == "healer":
            self.options.append(("Heal (50g)", "heal"))
        if self.npc.role == "quest_giver" and self.npc.quests:
            self.options.append(("Quests", "quests"))
        self.options.append(("Leave", "leave"))

    # -- input ---------------------------------------------------------

    def handle_input(self, key: str) -> None:
        if self.phase == "dialogue":
            if key == "enter":
                self.dialogue_index += 1
                if self.dialogue_index >= len(self.npc.dialogue):
                    self.phase = "options"
            elif key == "escape":
                self.game.state_manager.pop()
        elif self.phase == "options":
            if key == "up":
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif key == "down":
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif key == "enter":
                self._select_option()
            elif key == "escape":
                self.game.state_manager.pop()

    def _select_option(self) -> None:
        action = self.options[self.selected_option][1]

        if action == "leave":
            self.game.state_manager.pop()

        elif action == "browse_shop":
            from states.shop_state import ShopState

            self.game.state_manager.push(
                ShopState(
                    self.game,
                    self.npc.shop_inventory,
                    f"{self.npc.name}'s Shop",
                )
            )

        elif action == "heal":
            player = self.game.player
            if player.gold >= 50:
                player.gold -= 50
                player.current_hp = player.max_hp
                player.current_mp = player.max_mp
                self.game.add_log("[bold green]Fully healed![/bold green]")
            else:
                self.game.add_log("[red]Not enough gold![/red]")

        elif action == "quests":
            if self.npc.quests:
                quest = self.npc.quests[0]
                self.game.player.active_quests.append(quest)
                self.npc.quests.remove(quest)
                self.game.add_log(
                    f"Accepted quest: [bold]{quest.get('name', 'Unknown')}[/bold]"
                )

    # -- update / render -----------------------------------------------

    def update(self, dt: float) -> None:
        pass

    def render(self) -> RenderableType:
        from ui.dialogue_view import DialogueView
        from ui.hotbar import Hotbar
        from ui.renderer import GameRenderer

        view = DialogueView()

        if self.phase == "dialogue" and self.dialogue_index < len(self.npc.dialogue):
            dialogue_text = self.npc.dialogue[self.dialogue_index]
            panel = view.render(self.npc.name, self.npc.ascii_art, dialogue_text)
        else:
            option_names = [o[0] for o in self.options]
            panel = view.render(
                self.npc.name,
                self.npc.ascii_art,
                "What would you like?",
                option_names,
                self.selected_option,
            )

        hotbar = Hotbar()
        if self.phase == "dialogue":
            hotbar_panel = hotbar.render([("Enter", "Continue"), ("Esc", "Leave")])
        else:
            hotbar_panel = hotbar.render(
                [("Up/Down", "Select"), ("Enter", "Choose"), ("Esc", "Leave")]
            )

        return GameRenderer().create_fullscreen_layout(panel, hotbar_panel)

    def render_pygame(self, screen, font, renderer) -> None:
        from pygame_ui.pg_dialogue_view import PgDialogueView
        from pygame_ui.pg_hotbar import PgHotbar

        view = PgDialogueView()
        if self.phase == "dialogue" and self.dialogue_index < len(self.npc.dialogue):
            text = self.npc.dialogue[self.dialogue_index]
            responses = None
            sel = 0
        else:
            text = "What would you like?"
            responses = [o[0] for o in self.options]
            sel = self.selected_option

        content = view.render(
            self.npc.name, self.npc.ascii_art, text, responses, sel,
            font, renderer.screen_width, renderer.screen_height - renderer.hotbar_height,
        )
        hotbar = PgHotbar()
        if self.phase == "dialogue":
            actions = [("Enter", "Continue"), ("Esc", "Leave")]
        else:
            actions = [("U/D", "Select"), ("Enter", "Choose"), ("Esc", "Leave")]
        hotbar_surf = hotbar.render(actions, font, renderer.hotbar_rect.width, renderer.hotbar_rect.height)
        renderer.draw_fullscreen_layout(screen, content, hotbar_surf)
