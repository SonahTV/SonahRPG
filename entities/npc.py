from __future__ import annotations

import random
from dataclasses import dataclass, field


# --- Fallback data for NPC generation when data modules don't exist yet ---

_MERCHANT_NAMES = [
    "Grimble the Trader", "Old Nan's Goods", "Fizzwick's Emporium",
    "Draven's Arms", "Silken Thread", "Ironhide Outfitters",
]

_QUEST_GIVER_NAMES = [
    "Elder Morath", "Captain Voss", "Mystic Alara",
    "Scout Fenwick", "Priestess Delyn", "Warden Thorne",
]

_HEALER_NAMES = [
    "Sister Maren", "Brother Aldric", "Sage Luminara",
]

_MERCHANT_ART = (
    "   ___   \n"
    "  / _ \\  \n"
    " | (_) | \n"
    "  > $ <  \n"
    " | | | | \n"
    " |_| |_| \n"
)

_QUEST_GIVER_ART = (
    "   _!_   \n"
    "  / | \\  \n"
    " |  O  | \n"
    "  \\   /  \n"
    "  | | |  \n"
    "  |_|_|  \n"
)

_HEALER_ART = (
    "   _+_   \n"
    "  / | \\  \n"
    " |  O  | \n"
    "  \\   /  \n"
    "  | | |  \n"
    "  |_|_|  \n"
)


def _floor_to_tier(floor: int) -> str:
    """Map floor number to narrative tier key."""
    if floor <= 3:
        return "upper_depths"
    elif floor <= 6:
        return "fungal_caves"
    elif floor <= 9:
        return "bone_warrens"
    elif floor <= 12:
        return "abyssal_rift"
    return "binding_chamber"


def _get_tier_dialogue(floor: int, role: str, name: str) -> list[str]:
    """Get narrative dialogue for an NPC based on floor tier.

    Falls back to generic dialogue if narrative data isn't available.
    """
    try:
        from data.narrative import NPC_LORE_DIALOGUE

        tier = _floor_to_tier(floor)
        tier_data = NPC_LORE_DIALOGUE.get(tier, {})
        lines = tier_data.get(role)
        if lines:
            return [line.replace("{name}", name) for line in lines]
    except (ImportError, AttributeError):
        pass

    # Fallback generic dialogue
    fallback = {
        "merchant": [
            f"Welcome, adventurer! I'm {name}.",
            "Take a look at my wares. Everything's priced fair... mostly.",
            "Need supplies? You've come to the right place.",
        ],
        "quest_giver": [
            f"Hail, brave soul. I am {name}.",
            "These halls grow more dangerous by the day.",
            "I have tasks that need a capable hand. Interested?",
        ],
        "healer": [
            f"Peace be with you. I am {name}.",
            "Let me tend to your wounds.",
            "The light shall mend what darkness has broken.",
        ],
    }
    return fallback.get(role, [f"{name} nods silently."])


def _generate_shop_inventory(level: int) -> list[dict]:
    """Generate a tier-appropriate shop inventory based on dungeon level."""
    tier = max(1, level // 3 + 1)
    items: list[dict] = []

    # Health potions scale with level
    items.append({
        "name": f"Health Potion {'I' * min(tier, 3)}",
        "type": "consumable",
        "effect": "heal",
        "value": 20 + tier * 15,
        "price": 15 + tier * 10,
        "description": f"Restores {20 + tier * 15} HP.",
    })

    # Mana potions
    items.append({
        "name": f"Mana Potion {'I' * min(tier, 3)}",
        "type": "consumable",
        "effect": "restore_mp",
        "value": 15 + tier * 10,
        "price": 20 + tier * 10,
        "description": f"Restores {15 + tier * 10} MP.",
    })

    # Antidote
    items.append({
        "name": "Antidote",
        "type": "consumable",
        "effect": "cure",
        "value": 0,
        "price": 12 + tier * 5,
        "description": "Removes all negative status effects.",
    })

    # Weapon for the tier
    items.append({
        "name": f"Iron Sword +{tier}",
        "type": "equipment",
        "slot": "weapon",
        "bonuses": {"attack": 3 + tier * 2},
        "price": 50 + tier * 30,
        "description": f"A sturdy blade. +{3 + tier * 2} ATK.",
    })

    # Armor for the tier
    items.append({
        "name": f"Chain Mail +{tier}",
        "type": "equipment",
        "slot": "armor",
        "bonuses": {"defense": 2 + tier * 2, "hp_bonus": tier * 5},
        "price": 60 + tier * 35,
        "description": f"Solid protection. +{2 + tier * 2} DEF, +{tier * 5} HP.",
    })

    # Ring (higher tiers)
    if tier >= 2:
        items.append({
            "name": f"Ring of Fortitude +{tier - 1}",
            "type": "equipment",
            "slot": "ring",
            "bonuses": {"hp_bonus": 10 + tier * 5, "mp_bonus": 5 + tier * 3},
            "price": 80 + tier * 25,
            "description": f"Boosts vitality. +{10 + tier * 5} HP, +{5 + tier * 3} MP.",
        })

    return items


def _generate_quests(floor: int) -> list[dict]:
    """Generate quests appropriate for a dungeon floor."""
    quests: list[dict] = []

    # Kill quest
    kill_count = 3 + floor
    quests.append({
        "name": f"Extermination (Floor {floor})",
        "description": f"Slay {kill_count} monsters on floor {floor}.",
        "type": "kill",
        "target_count": kill_count,
        "current_count": 0,
        "floor": floor,
        "reward_gold": 30 + floor * 20,
        "reward_xp": 40 + floor * 25,
        "completed": False,
    })

    # Explore quest
    quests.append({
        "name": f"Cartographer (Floor {floor})",
        "description": f"Explore at least 80% of floor {floor}.",
        "type": "explore",
        "target_pct": 80,
        "current_pct": 0,
        "floor": floor,
        "reward_gold": 20 + floor * 15,
        "reward_xp": 30 + floor * 20,
        "completed": False,
    })

    # Boss quest (every 3 floors)
    if floor % 3 == 0:
        quests.append({
            "name": f"Slay the Boss (Floor {floor})",
            "description": f"Defeat the boss of floor {floor}.",
            "type": "boss",
            "floor": floor,
            "reward_gold": 100 + floor * 30,
            "reward_xp": 100 + floor * 40,
            "completed": False,
        })

    return quests


@dataclass
class NPC:
    name: str
    role: str  # "merchant", "quest_giver", "blacksmith", "healer"
    x: int = 0
    y: int = 0
    dialogue: list[str] = field(default_factory=list)
    shop_inventory: list[dict] = field(default_factory=list)
    quests: list[dict] = field(default_factory=list)
    ascii_art: str = ""

    @classmethod
    def create_merchant(cls, level: int) -> NPC:
        """Generate a merchant with level-appropriate inventory."""
        name = random.choice(_MERCHANT_NAMES)
        inventory = _generate_shop_inventory(level)
        dialogue = _get_tier_dialogue(level, "merchant", name)
        return cls(
            name=name,
            role="merchant",
            dialogue=dialogue,
            shop_inventory=inventory,
            ascii_art=_MERCHANT_ART,
        )

    @classmethod
    def create_quest_giver(cls, floor: int) -> NPC:
        """Generate an NPC with quests appropriate for the floor."""
        name = random.choice(_QUEST_GIVER_NAMES)
        quests = _generate_quests(floor)
        dialogue = _get_tier_dialogue(floor, "quest_giver", name)
        return cls(
            name=name,
            role="quest_giver",
            dialogue=dialogue,
            quests=quests,
            ascii_art=_QUEST_GIVER_ART,
        )

    @classmethod
    def create_healer(cls, floor: int = 1) -> NPC:
        """Create a healer NPC."""
        name = random.choice(_HEALER_NAMES)
        dialogue = _get_tier_dialogue(floor, "healer", name)
        return cls(
            name=name,
            role="healer",
            dialogue=dialogue,
            ascii_art=_HEALER_ART,
        )

    def get_greeting(self) -> str:
        """Return the first dialogue line as a greeting."""
        if self.dialogue:
            return self.dialogue[0]
        return f"{self.name} nods silently."

    def get_dialogue(self, index: int = 0) -> str:
        """Get a specific dialogue line by index, cycling if out of range."""
        if not self.dialogue:
            return f"{self.name} has nothing to say."
        return self.dialogue[index % len(self.dialogue)]

    def to_dict(self) -> dict:
        """Serialize NPC to dict."""
        return {
            "name": self.name,
            "role": self.role,
            "x": self.x,
            "y": self.y,
            "dialogue": self.dialogue,
            "shop_inventory": self.shop_inventory,
            "quests": self.quests,
            "ascii_art": self.ascii_art,
        }

    @classmethod
    def from_dict(cls, data: dict) -> NPC:
        """Deserialize NPC from dict."""
        return cls(
            name=data.get("name", "Unknown"),
            role=data.get("role", "merchant"),
            x=data.get("x", 0),
            y=data.get("y", 0),
            dialogue=data.get("dialogue", []),
            shop_inventory=data.get("shop_inventory", []),
            quests=data.get("quests", []),
            ascii_art=data.get("ascii_art", ""),
        )
