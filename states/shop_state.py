"""Shop state -- buy and sell items from merchants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game


class ShopState(GameState):
    """Two-tab shop interface: Buy items from the merchant or Sell your own.

    Prices:
    - Buy: item's ``gold_value`` or ``price`` field
    - Sell: half the buy price (minimum 1g)
    """

    def __init__(
        self, game: Game, shop_inventory: list[dict], shop_name: str = "Shop"
    ) -> None:
        super().__init__(game)
        self.shop_inventory = shop_inventory
        self.shop_name = shop_name
        self.selected_index = 0
        self.tab = "buy"  # "buy" or "sell"

    # -- input ---------------------------------------------------------

    def handle_input(self, key: str) -> None:
        if key == "up":
            self.selected_index = max(0, self.selected_index - 1)
        elif key == "down":
            max_idx = self._max_index()
            self.selected_index = min(max_idx, self.selected_index + 1)
        elif key == "enter":
            if self.tab == "buy":
                self._buy_item()
            else:
                self._sell_item()
        elif key == "tab":
            self.tab = "sell" if self.tab == "buy" else "buy"
            self.selected_index = 0
        elif key in ("escape", "q"):
            self.game.state_manager.pop()

    def _max_index(self) -> int:
        if self.tab == "buy":
            return max(0, len(self.shop_inventory) - 1)
        return max(0, len(self.game.player.inventory) - 1)

    # -- buy / sell ----------------------------------------------------

    def _buy_item(self) -> None:
        if not self.shop_inventory or self.selected_index >= len(self.shop_inventory):
            return
        item = self.shop_inventory[self.selected_index]
        cost = item.get("price", item.get("gold_value", 10))
        player = self.game.player
        if player.gold >= cost:
            if player.add_item(item.copy()):
                player.gold -= cost
                self.game.add_log(
                    f"Bought [bold]{item.get('name', 'item')}[/bold] "
                    f"for [yellow]{cost}g[/yellow]"
                )
            else:
                self.game.add_log("[red]Inventory full![/red]")
        else:
            self.game.add_log("[red]Not enough gold![/red]")

    def _sell_item(self) -> None:
        player = self.game.player
        if not player.inventory or self.selected_index >= len(player.inventory):
            return
        item = player.inventory[self.selected_index]
        sell_price = max(
            1, item.get("gold_value", item.get("price", 10)) // 2
        )
        player.remove_item(self.selected_index)
        player.gold += sell_price
        self.game.add_log(
            f"Sold [bold]{item.get('name', 'item')}[/bold] "
            f"for [yellow]{sell_price}g[/yellow]"
        )
        self.selected_index = min(
            self.selected_index, max(0, len(player.inventory) - 1)
        )

    # -- update / render -----------------------------------------------

    def update(self, dt: float) -> None:
        pass

    def render(self) -> RenderableType:
        from rich.console import Group
        from rich.panel import Panel
        from rich.text import Text
        from ui.hotbar import Hotbar
        from ui.renderer import GameRenderer

        player = self.game.player
        text = Text()

        # Tab header
        text.append("  ")
        for tab_id, label in [("buy", "Buy"), ("sell", "Sell")]:
            if self.tab == tab_id:
                text.append(f" {label} ", style="bold black on white")
            else:
                text.append(f" {label} ", style="dim")
            text.append("  ")
        text.append(f"  Gold: {player.gold}\n\n", style="yellow")

        # Item listing
        items = self.shop_inventory if self.tab == "buy" else player.inventory
        if not items:
            text.append("  Nothing here.\n", style="dim italic")
        else:
            for i, item in enumerate(items):
                cursor = "> " if i == self.selected_index else "  "
                style = "bold bright_white" if i == self.selected_index else ""
                if self.tab == "buy":
                    price = item.get("price", item.get("gold_value", 10))
                else:
                    price = max(1, item.get("gold_value", item.get("price", 10)) // 2)
                text.append(f"  {cursor}{item.get('name', 'Unknown')}", style=style)
                text.append(f"  {price}g", style="yellow")
                # Show description for selected item
                if i == self.selected_index:
                    desc = item.get("description", "")
                    if desc:
                        text.append(f"\n      {desc}", style="dim italic")
                text.append("\n")

        main_panel = Panel(
            text,
            title=f"[bold yellow]{self.shop_name}[/bold yellow]",
            border_style="yellow",
        )

        hotbar = Hotbar()
        hotbar_panel = hotbar.render(
            [
                ("Up/Down", "Select"),
                ("Enter", "Buy/Sell"),
                ("Tab", "Switch"),
                ("Esc", "Leave"),
            ]
        )

        return GameRenderer().create_fullscreen_layout(main_panel, hotbar_panel)

    def render_pygame(self, screen, font, renderer) -> None:
        import pygame
        from pygame_ui.colors import get_rgb
        from pygame_ui.pg_hotbar import PgHotbar

        w, h = renderer.screen_width, renderer.screen_height - renderer.hotbar_height
        surface = pygame.Surface((w, h))
        surface.fill((10, 10, 20))

        player = self.game.player
        y = 8

        # Tab header
        x = 20
        for tab_id, label in [("buy", "Buy"), ("sell", "Sell")]:
            if self.tab == tab_id:
                surf = font.render_text(f" {label} ", (0, 0, 0), (200, 200, 200))
            else:
                surf = font.render_text(f" {label} ", get_rgb("grey50"))
            surface.blit(surf, (x, y))
            x += surf.get_width() + 16
        gold_surf = font.render_text(f"Gold: {player.gold}", get_rgb("yellow"))
        surface.blit(gold_surf, (w - gold_surf.get_width() - 20, y))
        y += font.char_height * 2

        # Item list
        items = self.shop_inventory if self.tab == "buy" else player.inventory
        if not items:
            surface.blit(font.render_text("  Nothing here.", get_rgb("grey50")), (20, y))
        else:
            for i, item in enumerate(items):
                prefix = ">" if i == self.selected_index else " "
                color = get_rgb("bright_yellow") if i == self.selected_index else get_rgb("white")
                name = item.get("name", "Unknown")
                if self.tab == "buy":
                    price = item.get("price", item.get("gold_value", 10))
                else:
                    price = max(1, item.get("gold_value", item.get("price", 10)) // 2)
                text = f"  {prefix} {name}  {price}g"
                surface.blit(font.render_text(text, color), (20, y))
                y += font.char_height + 1

        pygame.draw.rect(surface, get_rgb("yellow"), surface.get_rect(), 1)
        title = font.render_text(f" {self.shop_name} ", get_rgb("bright_yellow"), (10, 10, 20))
        surface.blit(title, (w // 2 - title.get_width() // 2, 0))

        hotbar = PgHotbar()
        hotbar_surf = hotbar.render(
            [("U/D", "Select"), ("Enter", "Buy/Sell"), ("Tab", "Switch"), ("Esc", "Leave")],
            font, renderer.hotbar_rect.width, renderer.hotbar_rect.height,
        )
        renderer.draw_fullscreen_layout(screen, surface, hotbar_surf)
