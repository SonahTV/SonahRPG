"""Inventory management overlay state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game


class InventoryState(GameState):
    """Fullscreen inventory browser with equip, use, and drop actions."""

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.inventory_view = None
        self.selected_index = 0

    def on_enter(self) -> None:
        from ui.inventory_view import InventoryView

        self.inventory_view = InventoryView()

    def handle_input(self, key: str) -> None:
        player = self.game.player
        inv_len = len(player.inventory)

        if key == "up":
            if self.selected_index > 0:
                self.selected_index -= 1
        elif key == "down":
            if inv_len > 0 and self.selected_index < inv_len - 1:
                self.selected_index += 1
        elif key == "e":
            self._equip_selected()
        elif key == "u":
            self._use_selected()
        elif key == "d":
            self._drop_selected()
        elif key in ("escape", "i"):
            self.game.state_manager.pop()

    def _equip_selected(self) -> None:
        player = self.game.player
        if not player.inventory or not (0 <= self.selected_index < len(player.inventory)):
            return
        from systems.inventory import InventorySystem

        inv_sys = InventorySystem(self.game)
        success, msg = inv_sys.equip_item(player, self.selected_index)
        self.game.add_log(msg)
        # Clamp index after inventory change
        self._clamp_index()

    def _use_selected(self) -> None:
        player = self.game.player
        if not player.inventory or not (0 <= self.selected_index < len(player.inventory)):
            return
        from systems.inventory import InventorySystem

        inv_sys = InventorySystem(self.game)
        success, msg = inv_sys.use_item(player, self.selected_index)
        self.game.add_log(msg)
        if success:
            self._clamp_index()

    def _drop_selected(self) -> None:
        player = self.game.player
        if not player.inventory or not (0 <= self.selected_index < len(player.inventory)):
            return
        item = player.remove_item(self.selected_index)
        if item:
            self.game.add_log(f"Dropped {item.get('name', 'item')}")
            self._clamp_index()

    def _clamp_index(self) -> None:
        inv_len = len(self.game.player.inventory)
        self.selected_index = min(self.selected_index, max(0, inv_len - 1))

    def update(self, dt: float) -> None:
        pass

    def render(self) -> RenderableType:
        from ui.hotbar import Hotbar
        from ui.renderer import GameRenderer

        inv_panel = self.inventory_view.render(self.game.player, self.selected_index)
        hotbar = Hotbar()
        hotbar_panel = hotbar.render(
            [
                ("Up/Down", "Navigate"),
                ("E", "Equip"),
                ("U", "Use"),
                ("D", "Drop"),
                ("Esc", "Back"),
            ]
        )

        return GameRenderer().create_fullscreen_layout(inv_panel, hotbar_panel)

    def render_pygame(self, screen, font, renderer) -> None:
        from pygame_ui.pg_hotbar import PgHotbar
        from pygame_ui.pg_inventory_view import PgInventoryView

        inv_view = PgInventoryView()
        inv_surf = inv_view.render(
            self.game.player.inventory, self.selected_index, self.game.player.equipment,
            font, renderer.screen_width, renderer.screen_height - renderer.hotbar_height,
        )
        hotbar = PgHotbar()
        hotbar_surf = hotbar.render(
            [("U/D", "Nav"), ("E", "Equip"), ("U", "Use"), ("D", "Drop"), ("Esc", "Back")],
            font, renderer.hotbar_rect.width, renderer.hotbar_rect.height,
        )
        renderer.draw_fullscreen_layout(screen, inv_surf, hotbar_surf)
