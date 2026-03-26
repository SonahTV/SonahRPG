"""Inventory management system for SonahRPG."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game import Game
    from entities.player import Player


# Rarity colors for Rich markup
RARITY_COLORS: dict[str, str] = {
    "common": "white",
    "uncommon": "green",
    "rare": "dodger_blue1",
    "epic": "medium_purple",
    "legendary": "bright_yellow",
}

# Sort order for item types
TYPE_ORDER: dict[str, int] = {
    "equipment": 0,
    "consumable": 1,
    "scroll": 2,
    "junk": 3,
}

RARITY_ORDER: dict[str, int] = {
    "legendary": 0,
    "epic": 1,
    "rare": 2,
    "uncommon": 3,
    "common": 4,
}


class InventorySystem:
    def __init__(self, game: Game) -> None:
        self.game = game

    def add_item(self, player: Player, item: dict) -> bool:
        """Add item to player inventory. Returns True on success, False if full."""
        if len(player.inventory) >= player.max_inventory:
            return False
        player.inventory.append(item)
        return True

    def remove_item(self, player: Player, index: int) -> dict | None:
        """Remove and return item at index, or None if invalid."""
        if 0 <= index < len(player.inventory):
            return player.inventory.pop(index)
        return None

    def equip_item(self, player: Player, inventory_index: int) -> tuple[bool, str]:
        """Equip item from inventory slot.

        Returns (success, message). Handles swapping the old item back to
        inventory and recomputing derived stats.
        """
        if inventory_index < 0 or inventory_index >= len(player.inventory):
            return False, "Invalid inventory slot."

        item = player.inventory[inventory_index]
        if item.get("type") != "equipment":
            return False, f"{item.get('name', 'Item')} is not equippable."

        slot = item.get("slot", "weapon")
        valid_slots = ("weapon", "armor", "helmet", "boots", "ring", "amulet")
        if slot not in valid_slots:
            return False, f"Unknown equipment slot: {slot}"

        # Check level requirement if present
        item_level = item.get("level", 1)
        if item_level > player.level:
            return False, f"Requires level {item_level} (you are level {player.level})."

        # Remove item from inventory first
        player.inventory.pop(inventory_index)

        # Equip; previous item returned
        previous = player.equipment.equip(item)

        # Put old item back in inventory if there was one
        if previous is not None:
            player.inventory.append(previous)

        # Recompute stats with new gear
        player.compute_derived_stats()

        item_name = item.get("name", "Item")
        msg = f"Equipped {item_name}."
        if previous:
            msg += f" Unequipped {previous.get('name', 'old item')}."
        return True, msg

    def unequip_item(self, player: Player, slot: str) -> tuple[bool, str]:
        """Unequip item from equipment slot back to inventory.

        Returns (success, message).
        """
        valid_slots = ("weapon", "armor", "helmet", "boots", "ring", "amulet")
        if slot not in valid_slots:
            return False, f"Unknown slot: {slot}"

        current_item = player.equipment.get_slot(slot)
        if current_item is None:
            return False, f"Nothing equipped in {slot} slot."

        if len(player.inventory) >= player.max_inventory:
            return False, "Inventory is full. Cannot unequip."

        removed = player.equipment.unequip(slot)
        if removed:
            player.inventory.append(removed)
            player.compute_derived_stats()
            return True, f"Unequipped {removed.get('name', 'item')}."
        return False, "Failed to unequip."

    def use_item(self, player: Player, inventory_index: int) -> tuple[bool, str]:
        """Use a consumable item from inventory.

        Returns (success, message).
        Handles: potions (heal HP/MP), scrolls (buffs), antidotes (cleanse).
        """
        if inventory_index < 0 or inventory_index >= len(player.inventory):
            return False, "Invalid inventory slot."

        item = player.inventory[inventory_index]
        item_type = item.get("type", "")

        if item_type == "equipment":
            return False, f"{item.get('name', 'Item')} is equipment — press [E] to equip it."

        if item_type == "junk":
            # Auto-sell junk for gold
            gold = item.get("gold_value", 1)
            player.gold += gold
            player.inventory.pop(inventory_index)
            return True, f"Sold {item.get('name', 'Item')} for {gold} gold."

        if item_type == "gold":
            # Gold somehow in inventory — absorb it
            gold = item.get("value", item.get("gold_value", 0))
            player.gold += gold
            player.inventory.pop(inventory_index)
            return True, f"Added {gold} gold to your purse."

        if item_type not in ("consumable",):
            return False, f"Can't use {item.get('name', 'Item')}."

        effect = item.get("effect", "")
        value = item.get("value", 0)
        name = item.get("name", "Unknown Item")

        if effect == "heal":
            actual = player.heal(value)
            player.inventory.pop(inventory_index)
            return True, f"Used {name}. Restored {actual} HP."

        elif effect == "restore_mp":
            actual = player.restore_mp(value)
            player.inventory.pop(inventory_index)
            return True, f"Used {name}. Restored {actual} MP."

        elif effect == "cure":
            # Remove all negative status effects
            negative_names = {"poison", "bleed", "burn", "stun", "freeze", "slow", "weaken"}
            removed_count = 0
            remaining = []
            for se in player.status_effects:
                se_name = se.get("name", "") if isinstance(se, dict) else getattr(se, "name", "")
                if se_name in negative_names:
                    removed_count += 1
                else:
                    remaining.append(se)
            player.status_effects = remaining
            player.inventory.pop(inventory_index)
            return True, f"Used {name}. Cleansed {removed_count} negative effect(s)."

        elif effect.startswith("buff_"):
            # Buff consumable: add status effect
            duration = item.get("duration", 3)
            player.status_effects.append({
                "name": effect,
                "duration": duration,
                "effect": effect,
                "value": value,
            })
            player.inventory.pop(inventory_index)
            return True, f"Used {name}. Gained {effect} for {duration} turns."

        else:
            # Generic use: just apply value as healing fallback
            if value > 0:
                actual = player.heal(value)
                player.inventory.pop(inventory_index)
                return True, f"Used {name}. Restored {actual} HP."
            player.inventory.pop(inventory_index)
            return True, f"Used {name}."

    def compare_items(self, current: dict | None, new_item: dict) -> dict:
        """Compare two items and return stat differences.

        Returns: {stat_name: (current_val, new_val, diff)} for all relevant stats.
        """
        result: dict[str, tuple[int, int, int]] = {}

        current_bonuses = current.get("bonuses", {}) if current else {}
        new_bonuses = new_item.get("bonuses", {})

        # Collect all stat keys from both items
        all_stats = set(list(current_bonuses.keys()) + list(new_bonuses.keys()))
        for stat in sorted(all_stats):
            cur_val = current_bonuses.get(stat, 0)
            new_val = new_bonuses.get(stat, 0)
            diff = new_val - cur_val
            result[stat] = (cur_val, new_val, diff)

        # Compare gold value
        cur_gold = current.get("gold_value", 0) if current else 0
        new_gold = new_item.get("gold_value", 0)
        if cur_gold or new_gold:
            result["gold_value"] = (cur_gold, new_gold, new_gold - cur_gold)

        # Compare level requirement
        cur_level = current.get("level", 0) if current else 0
        new_level = new_item.get("level", 0)
        if cur_level or new_level:
            result["level_req"] = (cur_level, new_level, new_level - cur_level)

        return result

    def sort_inventory(self, player: Player, sort_by: str = "type") -> None:
        """Sort player inventory by 'type', 'rarity', or 'level'."""
        if sort_by == "type":
            player.inventory.sort(
                key=lambda item: (
                    TYPE_ORDER.get(item.get("type", "junk"), 99),
                    RARITY_ORDER.get(item.get("rarity", "common"), 99),
                    item.get("name", ""),
                )
            )
        elif sort_by == "rarity":
            player.inventory.sort(
                key=lambda item: (
                    RARITY_ORDER.get(item.get("rarity", "common"), 99),
                    TYPE_ORDER.get(item.get("type", "junk"), 99),
                    item.get("name", ""),
                )
            )
        elif sort_by == "level":
            player.inventory.sort(
                key=lambda item: (
                    -item.get("level", 0),
                    RARITY_ORDER.get(item.get("rarity", "common"), 99),
                    item.get("name", ""),
                )
            )

    def get_item_display_name(self, item: dict) -> str:
        """Get Rich-markup colored display name based on rarity."""
        name = item.get("name", "Unknown Item")
        rarity = item.get("rarity", "common")
        color = RARITY_COLORS.get(rarity, "white")
        return f"[{color}]{name}[/{color}]"
