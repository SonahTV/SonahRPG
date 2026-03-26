from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.console import Group


# Rarity color mapping
RARITY_COLORS: dict[str, str] = {
    "common": "white",
    "uncommon": "green",
    "rare": "bright_blue",
    "epic": "bright_magenta",
    "legendary": "bright_yellow",
}

# Item type icons
TYPE_ICONS: dict[str, str] = {
    "weapon": "Wpn",
    "armor": "Arm",
    "helmet": "Hlm",
    "shield": "Shd",
    "ring": "Rng",
    "amulet": "Amu",
    "potion": "Pot",
    "scroll": "Scr",
    "consumable": "Con",
    "material": "Mat",
    "key": "Key",
}


class InventoryView:
    """Full inventory screen with item list, detail view, and stat comparison."""

    def __init__(self):
        self.selected_index: int = 0
        self.show_comparison: bool = True

    def render(self, player, selected_index: int = 0) -> Panel:
        """Render inventory screen with item list + detail view.

        Left side: Scrollable list of items with selection cursor
        Right side: Selected item details + comparison with equipped gear
        Bottom: Action hints

        Items are colored by rarity. Shows item type icon, name, level requirement.
        """
        self.selected_index = selected_index

        inventory = getattr(player, "inventory", [])
        max_inv = getattr(player, "max_inventory", 20)

        parts = []

        # Item list (left panel)
        item_text = Text()
        if not inventory:
            item_text.append("\n  Inventory is empty\n", style="dim italic")
            item_text.append("  Find loot in the dungeon!\n", style="dim")
        else:
            for i, item in enumerate(inventory):
                cursor = " > " if i == selected_index else "   "
                style = "bold" if i == selected_index else ""

                # Get item properties (support both dict and object)
                item_name = self._get_prop(item, "name", "Unknown")
                item_type = self._get_prop(item, "type", "?")
                rarity = self._get_prop(item, "rarity", "common")
                level_req = self._get_prop(item, "level", 1)

                rarity_color = RARITY_COLORS.get(rarity, "white")
                type_icon = TYPE_ICONS.get(item_type, "???")

                item_text.append(cursor, style="bright_yellow" if i == selected_index else "")
                item_text.append(f"{item_name}", style=f"{style} {rarity_color}")
                item_text.append(f" [{type_icon}]", style="dim")
                if level_req > 1:
                    player_level = getattr(player, "level", 1)
                    lvl_style = "dim red" if player_level < level_req else "dim"
                    item_text.append(f" Lv.{level_req}", style=lvl_style)
                item_text.append("\n")

        item_panel = Panel(
            item_text,
            title=f"[bold]Inventory ({len(inventory)}/{max_inv})[/bold]",
            border_style="cyan",
        )

        # Detail view (right panel)
        if inventory and 0 <= selected_index < len(inventory):
            item = inventory[selected_index]
            detail = self._render_item_detail(item, player)
        else:
            detail_text = Text("\n  No item selected\n", style="dim")
            detail_text.append("  Use UP/DOWN to browse\n", style="dim italic")
            detail = Panel(detail_text, title="[bold]Details[/bold]", border_style="dim")

        # Combine left and right using a grid table
        layout_table = Table.grid(expand=True)
        layout_table.add_column(ratio=1)
        layout_table.add_column(ratio=1)
        layout_table.add_row(item_panel, detail)
        parts.append(layout_table)

        # Action hints at bottom
        action_text = Text("\n  ")
        action_text.append("[E]", style="bold bright_yellow")
        action_text.append("quip  ")
        action_text.append("[U]", style="bold bright_yellow")
        action_text.append("se  ")
        action_text.append("[D]", style="bold bright_yellow")
        action_text.append("rop  ")
        action_text.append("[ESC]", style="bold bright_yellow")
        action_text.append(" Back")
        parts.append(action_text)

        return Panel(
            Group(*parts),
            title="[bold yellow]Inventory[/bold yellow]",
            border_style="yellow",
        )

    def _render_item_detail(self, item, player) -> Panel:
        """Render detailed item info with stat comparison against equipped gear."""
        text = Text()

        item_name = self._get_prop(item, "name", "Unknown")
        rarity = self._get_prop(item, "rarity", "common")
        item_type = self._get_prop(item, "type", "item")
        level_req = self._get_prop(item, "level", 1)
        description = self._get_prop(item, "description", "")
        value = self._get_prop(item, "value", 0)
        stats = self._get_prop(item, "bonuses", self._get_prop(item, "stats", {}))

        rarity_color = RARITY_COLORS.get(rarity, "white")

        text.append(f" {item_name}\n", style=f"bold {rarity_color}")
        text.append(f" {rarity.title()} {item_type.title()}\n", style="dim")
        text.append(f" Level Req: {level_req}\n\n")

        if description:
            text.append(f" {description}\n\n", style="italic")

        # Item stats
        if stats:
            if isinstance(stats, dict):
                stat_items = stats.items()
            else:
                stat_items = [(k, getattr(stats, k)) for k in dir(stats)
                              if not k.startswith("_") and isinstance(getattr(stats, k, None), (int, float))]

            for stat_name, val in stat_items:
                sign = "+" if val > 0 else ""
                color = "green" if val > 0 else "red"
                text.append(f" {stat_name}: ", style="bold")
                text.append(f"{sign}{val}\n", style=color)

        # Comparison with currently equipped item
        if self.show_comparison and item_type in ("weapon", "armor", "helmet", "shield"):
            equipped = self._get_equipped_for_slot(player, item_type)
            if equipped is not None:
                text.append("\n --- vs Equipped ---\n", style="dim")
                eq_name = self._get_prop(equipped, "name", "Unknown")
                text.append(f" {eq_name}\n", style="dim italic")

                eq_stats = self._get_prop(equipped, "bonuses", self._get_prop(equipped, "stats", {}))
                if isinstance(eq_stats, dict) and isinstance(stats, dict):
                    all_keys = set(list(stats.keys()) + list(eq_stats.keys()))
                    for key in sorted(all_keys):
                        new_val = stats.get(key, 0)
                        old_val = eq_stats.get(key, 0)
                        diff = new_val - old_val
                        if diff != 0:
                            sign = "+" if diff > 0 else ""
                            color = "bright_green" if diff > 0 else "bright_red"
                            text.append(f" {key}: {sign}{diff}\n", style=color)

        if value:
            text.append(f"\n Value: {value}g\n", style="yellow")

        return Panel(text, title="[bold]Details[/bold]", border_style="bright_cyan")

    def _get_equipped_for_slot(self, player, item_type: str):
        """Get the currently equipped item for a given slot type."""
        equipment = getattr(player, "equipment", None)
        if equipment is None:
            return None

        slot_map = {
            "weapon": "weapon",
            "armor": "armor",
            "helmet": "helmet",
            "shield": "shield",
        }
        slot = slot_map.get(item_type)
        if slot is None:
            return None

        if isinstance(equipment, dict):
            return equipment.get(slot)
        return getattr(equipment, slot, None)

    @staticmethod
    def _get_prop(obj, key: str, default=None):
        """Get a property from either a dict or an object."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)
