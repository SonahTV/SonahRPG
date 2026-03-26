"""Loot generation system for SonahRPG."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game import Game


# ======================================================================
# Item templates — base items by type and level tier
# ======================================================================

WEAPON_BASES: list[dict] = [
    {"name": "Dagger", "level_range": (1, 5), "base_attack": 3},
    {"name": "Short Sword", "level_range": (1, 6), "base_attack": 5},
    {"name": "Mace", "level_range": (2, 7), "base_attack": 6},
    {"name": "Long Sword", "level_range": (4, 10), "base_attack": 8},
    {"name": "Battle Axe", "level_range": (5, 12), "base_attack": 10},
    {"name": "War Hammer", "level_range": (6, 12), "base_attack": 11},
    {"name": "Great Sword", "level_range": (8, 15), "base_attack": 14},
    {"name": "Runic Blade", "level_range": (10, 18), "base_attack": 16},
    {"name": "Demon Slayer", "level_range": (14, 20), "base_attack": 20},
    {"name": "Void Cleaver", "level_range": (18, 25), "base_attack": 25},
]

ARMOR_BASES: list[dict] = [
    {"name": "Cloth Robe", "level_range": (1, 4), "base_defense": 2},
    {"name": "Leather Armor", "level_range": (1, 6), "base_defense": 4},
    {"name": "Chainmail", "level_range": (3, 8), "base_defense": 6},
    {"name": "Scale Mail", "level_range": (5, 10), "base_defense": 8},
    {"name": "Plate Armor", "level_range": (7, 14), "base_defense": 11},
    {"name": "Dragon Scale", "level_range": (12, 18), "base_defense": 15},
    {"name": "Mythril Plate", "level_range": (16, 25), "base_defense": 20},
]

HELMET_BASES: list[dict] = [
    {"name": "Cloth Hood", "level_range": (1, 5), "base_defense": 1},
    {"name": "Leather Cap", "level_range": (2, 7), "base_defense": 2},
    {"name": "Iron Helm", "level_range": (4, 10), "base_defense": 4},
    {"name": "Steel Helm", "level_range": (8, 14), "base_defense": 6},
    {"name": "Crown of Kings", "level_range": (14, 25), "base_defense": 9},
]

BOOTS_BASES: list[dict] = [
    {"name": "Sandals", "level_range": (1, 4), "base_defense": 1},
    {"name": "Leather Boots", "level_range": (2, 7), "base_defense": 2},
    {"name": "Iron Greaves", "level_range": (5, 11), "base_defense": 4},
    {"name": "Steel Sabatons", "level_range": (9, 16), "base_defense": 6},
    {"name": "Void Walkers", "level_range": (15, 25), "base_defense": 9},
]

RING_BASES: list[dict] = [
    {"name": "Copper Ring", "level_range": (1, 5), "base_bonus": 1},
    {"name": "Silver Ring", "level_range": (3, 8), "base_bonus": 2},
    {"name": "Gold Ring", "level_range": (6, 12), "base_bonus": 3},
    {"name": "Platinum Ring", "level_range": (10, 18), "base_bonus": 5},
    {"name": "Astral Ring", "level_range": (16, 25), "base_bonus": 8},
]

AMULET_BASES: list[dict] = [
    {"name": "Bone Amulet", "level_range": (1, 5), "base_bonus": 2},
    {"name": "Crystal Pendant", "level_range": (3, 9), "base_bonus": 3},
    {"name": "Emerald Amulet", "level_range": (7, 14), "base_bonus": 5},
    {"name": "Ruby Talisman", "level_range": (12, 18), "base_bonus": 7},
    {"name": "Dragon Heart", "level_range": (16, 25), "base_bonus": 10},
]

BASE_TABLES: dict[str, list[dict]] = {
    "weapon": WEAPON_BASES,
    "armor": ARMOR_BASES,
    "helmet": HELMET_BASES,
    "boots": BOOTS_BASES,
    "ring": RING_BASES,
    "amulet": AMULET_BASES,
}

# ======================================================================
# Affixes — prefixes and suffixes that modify item stats
# ======================================================================

PREFIXES: list[dict] = [
    {"name": "Sharp", "stat": "attack", "value": 2, "min_rarity": "uncommon"},
    {"name": "Keen", "stat": "crit_chance", "value": 3, "min_rarity": "uncommon"},
    {"name": "Sturdy", "stat": "defense", "value": 2, "min_rarity": "uncommon"},
    {"name": "Vigorous", "stat": "hp_bonus", "value": 10, "min_rarity": "uncommon"},
    {"name": "Arcane", "stat": "mp_bonus", "value": 8, "min_rarity": "uncommon"},
    {"name": "Swift", "stat": "dodge_chance", "value": 3, "min_rarity": "rare"},
    {"name": "Vicious", "stat": "attack", "value": 5, "min_rarity": "rare"},
    {"name": "Fortified", "stat": "defense", "value": 5, "min_rarity": "rare"},
    {"name": "Titanic", "stat": "hp_bonus", "value": 25, "min_rarity": "epic"},
    {"name": "Devastating", "stat": "attack", "value": 8, "min_rarity": "epic"},
    {"name": "Immortal", "stat": "hp_bonus", "value": 50, "min_rarity": "legendary"},
    {"name": "Godslayer", "stat": "attack", "value": 15, "min_rarity": "legendary"},
]

SUFFIXES: list[dict] = [
    {"name": "of Might", "stat": "attack", "value": 2, "min_rarity": "uncommon"},
    {"name": "of the Bear", "stat": "hp_bonus", "value": 8, "min_rarity": "uncommon"},
    {"name": "of the Fox", "stat": "dodge_chance", "value": 2, "min_rarity": "uncommon"},
    {"name": "of Precision", "stat": "crit_chance", "value": 3, "min_rarity": "rare"},
    {"name": "of the Sage", "stat": "mp_bonus", "value": 12, "min_rarity": "rare"},
    {"name": "of Iron", "stat": "defense", "value": 4, "min_rarity": "rare"},
    {"name": "of Destruction", "stat": "attack", "value": 7, "min_rarity": "epic"},
    {"name": "of the Titan", "stat": "hp_bonus", "value": 30, "min_rarity": "epic"},
    {"name": "of Eternity", "stat": "hp_bonus", "value": 40, "min_rarity": "legendary"},
    {"name": "of the Void", "stat": "attack", "value": 12, "min_rarity": "legendary"},
]

RARITY_TIERS = ("common", "uncommon", "rare", "epic", "legendary")

RARITY_AFFIX_COUNT: dict[str, int] = {
    "common": 0,
    "uncommon": 1,
    "rare": 2,
    "epic": 3,
    "legendary": 4,
}

RARITY_STAT_MULTIPLIER: dict[str, float] = {
    "common": 1.0,
    "uncommon": 1.2,
    "rare": 1.5,
    "epic": 2.0,
    "legendary": 3.0,
}

RARITY_VALUE_MULTIPLIER: dict[str, float] = {
    "common": 1.0,
    "uncommon": 2.0,
    "rare": 5.0,
    "epic": 12.0,
    "legendary": 30.0,
}

# Consumable templates
CONSUMABLE_TEMPLATES: list[dict] = [
    {"name": "Minor Health Potion", "effect": "heal", "base_value": 20, "level_range": (1, 5)},
    {"name": "Health Potion", "effect": "heal", "base_value": 50, "level_range": (4, 10)},
    {"name": "Greater Health Potion", "effect": "heal", "base_value": 100, "level_range": (8, 16)},
    {"name": "Supreme Health Potion", "effect": "heal", "base_value": 200, "level_range": (14, 25)},
    {"name": "Minor Mana Potion", "effect": "restore_mp", "base_value": 15, "level_range": (1, 5)},
    {"name": "Mana Potion", "effect": "restore_mp", "base_value": 40, "level_range": (4, 10)},
    {"name": "Greater Mana Potion", "effect": "restore_mp", "base_value": 80, "level_range": (8, 16)},
    {"name": "Antidote", "effect": "cure", "base_value": 0, "level_range": (1, 25)},
    {"name": "Elixir of Strength", "effect": "buff_str", "base_value": 5, "level_range": (3, 25)},
    {"name": "Elixir of Dexterity", "effect": "buff_dex", "base_value": 5, "level_range": (3, 25)},
    {"name": "Elixir of Intellect", "effect": "buff_int", "base_value": 5, "level_range": (3, 25)},
]


def _rarity_index(rarity: str) -> int:
    try:
        return RARITY_TIERS.index(rarity)
    except ValueError:
        return 0


class LootSystem:
    def __init__(self, game: Game) -> None:
        self.game = game

    def generate_loot(self, enemy_level: int, loot_table: list[dict]) -> list[dict]:
        """Generate loot drops from a loot table.

        Each entry: {item_type: str, rarity: str, chance: float}
        Roll for each entry; generate item if successful.
        """
        drops: list[dict] = []
        for entry in loot_table:
            chance = entry.get("chance", 0.0)
            if random.random() < chance:
                item_type = entry.get("item_type", "potion")
                rarity = entry.get("rarity")
                item = self.generate_item(item_type, enemy_level, rarity)
                if item:
                    drops.append(item)
        return drops

    def generate_item(
        self, item_type: str, level: int, rarity: str | None = None
    ) -> dict:
        """Generate a random item of given type and level.

        If rarity is None, roll for it based on level.
        """
        if rarity is None:
            rarity = self.roll_rarity(level)

        # Handle consumables separately
        if item_type in ("potion", "scroll", "consumable"):
            return self._generate_consumable(level, rarity)

        if item_type == "junk":
            return self._generate_junk(level)

        # Equipment generation
        slot = item_type if item_type in BASE_TABLES else "weapon"
        base_table = BASE_TABLES.get(slot, WEAPON_BASES)

        # Filter bases that match the level
        candidates = [
            b for b in base_table
            if b["level_range"][0] <= level <= b["level_range"][1]
        ]
        if not candidates:
            # Fallback: pick the closest base
            candidates = sorted(
                base_table,
                key=lambda b: abs((b["level_range"][0] + b["level_range"][1]) / 2 - level),
            )
            candidates = candidates[:3]

        base = random.choice(candidates)
        stat_mult = RARITY_STAT_MULTIPLIER.get(rarity, 1.0)

        # Build stats dict from base
        stats: dict[str, int] = {}
        if "base_attack" in base:
            stats["attack"] = int((base["base_attack"] + level) * stat_mult)
        if "base_defense" in base:
            stats["defense"] = int((base["base_defense"] + level * 0.5) * stat_mult)
        if "base_bonus" in base:
            # Rings and amulets: random stat bonus
            bonus_stat = random.choice(
                ["attack", "defense", "hp_bonus", "mp_bonus", "crit_chance", "dodge_chance"]
            )
            stats[bonus_stat] = int((base["base_bonus"] + level * 0.3) * stat_mult)

        # Apply affixes based on rarity
        affix_count = RARITY_AFFIX_COUNT.get(rarity, 0)
        prefix_name = ""
        suffix_name = ""

        if affix_count >= 1:
            # Pick a prefix
            eligible_prefixes = [
                p for p in PREFIXES
                if _rarity_index(p["min_rarity"]) <= _rarity_index(rarity)
            ]
            if eligible_prefixes:
                chosen_prefix = random.choice(eligible_prefixes)
                prefix_name = chosen_prefix["name"]
                pstat = chosen_prefix["stat"]
                pval = int(chosen_prefix["value"] * (1 + level * 0.1))
                stats[pstat] = stats.get(pstat, 0) + pval

        if affix_count >= 2:
            # Pick a suffix
            eligible_suffixes = [
                s for s in SUFFIXES
                if _rarity_index(s["min_rarity"]) <= _rarity_index(rarity)
            ]
            if eligible_suffixes:
                chosen_suffix = random.choice(eligible_suffixes)
                suffix_name = chosen_suffix["name"]
                sstat = chosen_suffix["stat"]
                sval = int(chosen_suffix["value"] * (1 + level * 0.1))
                stats[sstat] = stats.get(sstat, 0) + sval

        if affix_count >= 3:
            # Additional random stat bonus
            extra_stat = random.choice(
                ["hp_bonus", "mp_bonus", "crit_chance", "dodge_chance"]
            )
            extra_val = int((2 + level * 0.5) * stat_mult)
            stats[extra_stat] = stats.get(extra_stat, 0) + extra_val

        if affix_count >= 4:
            # Legendary bonus: another significant stat
            extra_stat = random.choice(["attack", "defense", "hp_bonus"])
            extra_val = int((5 + level) * stat_mult)
            stats[extra_stat] = stats.get(extra_stat, 0) + extra_val

        # Build final name
        item_name = base["name"]
        if prefix_name:
            item_name = f"{prefix_name} {item_name}"
        if suffix_name:
            item_name = f"{item_name} {suffix_name}"

        # Calculate gold value
        total_stat_value = sum(abs(v) for v in stats.values())
        gold_value = int(
            total_stat_value * 3 * RARITY_VALUE_MULTIPLIER.get(rarity, 1.0)
        )

        # Build description
        stat_desc = ", ".join(f"+{v} {k}" for k, v in stats.items() if v > 0)
        description = f"A {rarity} {base['name'].lower()}. {stat_desc}."

        return {
            "name": item_name,
            "type": "equipment",
            "rarity": rarity,
            "level": level,
            "slot": slot,
            "bonuses": stats,
            "description": description,
            "gold_value": max(1, gold_value),
        }

    def roll_rarity(self, level: int) -> str:
        """Roll for item rarity. Higher level = better odds.

        Base rates: Common 60%, Uncommon 25%, Rare 10%, Epic 4%, Legendary 1%
        Each level adds ~0.5% shift from common to higher tiers.
        """
        level_bonus = level * 0.5

        legendary_chance = 1.0 + level_bonus * 0.1
        epic_chance = 4.0 + level_bonus * 0.3
        rare_chance = 10.0 + level_bonus * 0.5
        uncommon_chance = 25.0 + level_bonus * 0.4

        # Clamp legendary
        legendary_chance = min(legendary_chance, 10.0)
        epic_chance = min(epic_chance, 20.0)
        rare_chance = min(rare_chance, 30.0)

        roll = random.uniform(0, 100)
        cumulative = 0.0

        cumulative += legendary_chance
        if roll < cumulative:
            return "legendary"
        cumulative += epic_chance
        if roll < cumulative:
            return "epic"
        cumulative += rare_chance
        if roll < cumulative:
            return "rare"
        cumulative += uncommon_chance
        if roll < cumulative:
            return "uncommon"
        return "common"

    def generate_chest_loot(self, floor_number: int) -> list[dict]:
        """Generate loot for a dungeon chest (1-3 items + gold)."""
        item_count = random.randint(1, 3)
        items: list[dict] = []

        for _ in range(item_count):
            # Chests have slightly better odds — treat level as floor+2
            effective_level = floor_number + 2
            item_type = random.choice(
                ["weapon", "armor", "helmet", "boots", "ring", "amulet", "potion", "potion"]
            )
            item = self.generate_item(item_type, effective_level)
            items.append(item)

        # Add gold as a special entry
        gold_amount = random.randint(
            10 + floor_number * 5,
            30 + floor_number * 15,
        )
        items.append({
            "name": f"{gold_amount} Gold",
            "type": "gold",
            "value": gold_amount,
            "rarity": "common",
            "description": f"A pile of {gold_amount} gold coins.",
            "gold_value": gold_amount,
        })

        return items

    def generate_shop_inventory(self, floor_number: int, count: int = 8) -> list[dict]:
        """Generate shop inventory with level-appropriate items.

        Shop items tend to be slightly better quality than random drops.
        """
        items: list[dict] = []
        # Ensure some variety: at least 1 weapon, 1 armor, 2 consumables
        forced_types = ["weapon", "armor", "potion", "potion"]
        remaining_count = max(0, count - len(forced_types))
        optional_types = [
            random.choice(["weapon", "armor", "helmet", "boots", "ring", "amulet", "potion"])
            for _ in range(remaining_count)
        ]

        all_types = forced_types + optional_types
        random.shuffle(all_types)

        for item_type in all_types:
            # Shop items use floor + 1 as effective level and get a small rarity boost
            effective_level = floor_number + 1
            rarity = self.roll_rarity(effective_level + 2)  # slight quality bump
            item = self.generate_item(item_type, effective_level, rarity)
            # Mark up price by 50% for shop
            item["gold_value"] = int(item.get("gold_value", 10) * 1.5)
            items.append(item)

        return items

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _generate_consumable(self, level: int, rarity: str) -> dict:
        """Generate a consumable item (potion, scroll, etc.)."""
        candidates = [
            c for c in CONSUMABLE_TEMPLATES
            if c["level_range"][0] <= level <= c["level_range"][1]
        ]
        if not candidates:
            candidates = CONSUMABLE_TEMPLATES[:3]

        template = random.choice(candidates)
        mult = RARITY_STAT_MULTIPLIER.get(rarity, 1.0)
        value = int(template["base_value"] * mult * (1 + level * 0.1))

        gold_value = max(1, int(value * 0.5))

        item: dict = {
            "name": template["name"],
            "type": "consumable",
            "effect": template["effect"],
            "value": value,
            "rarity": rarity,
            "description": f"Restores {value} {'HP' if template['effect'] == 'heal' else 'MP'}."
            if template["effect"] in ("heal", "restore_mp")
            else f"Applies {template['effect']}.",
            "gold_value": gold_value,
        }

        # Buff consumables get a duration
        if template["effect"].startswith("buff_") or template["effect"] == "cure":
            item["duration"] = 3
            if template["effect"] == "cure":
                item["description"] = "Cleanses all negative effects."
                item["value"] = 0

        return item

    def _generate_junk(self, level: int) -> dict:
        """Generate a junk/vendor-trash item with atmospheric descriptions."""
        junk_items = [
            ("Rat Tail", 2, "A severed rat tail, still twitching. Alchemists pay for these."),
            ("Goblin Ear", 3, "Proof of a kill. The Warden's Guard pays a bounty per ear."),
            ("Broken Sword Hilt", 5, "The grip is worn smooth by a previous owner's desperate grip."),
            ("Cracked Gemstone", 8, "Flawed, but the color shifts when you tilt it toward The Depths."),
            ("Tarnished Coin", 4, "Old currency from before the Binding. Collectors want these."),
            ("Spider Silk Bundle", 6, "Impossibly strong thread. Weavers and armorers both want it."),
            ("Bone Fragment", 3, "Human? Not human? Best not to think about it. Sell it."),
            ("Rusted Key", 7, "Doesn't fit any lock you've found. Someone might know what it opens."),
            ("Rusted Chain Link", 4, "Part of a Condemned's shackle. A grim souvenir."),
            ("Mysterious Fang", 5, "Too large for any creature you've seen. The tooth pulses faintly."),
            ("Vial of Black Tears", 10, "The mineral oil that seeps from Ashenmere's stone. Alchemists prize it."),
            ("Consortium Signet", 12, "A mage's ring, broken. The symbol is still legible."),
            ("Petrified Eye", 6, "An eye turned to stone. It seems to follow you."),
            ("Warden's Badge", 8, "A guard who didn't make it back. Return it for a reward."),
        ]
        name, base_value, desc = random.choice(junk_items)
        gold_value = base_value + level * 2
        return {
            "name": name,
            "type": "junk",
            "rarity": "common",
            "description": desc,
            "gold_value": gold_value,
        }
