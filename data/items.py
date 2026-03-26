from dataclasses import dataclass, field
from enum import Enum


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    BOOTS = "boots"
    RING = "ring"
    AMULET = "amulet"
    POTION = "potion"
    SCROLL = "scroll"


class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


RARITY_COLORS = {
    Rarity.COMMON: "white",
    Rarity.UNCOMMON: "green",
    Rarity.RARE: "blue",
    Rarity.EPIC: "magenta",
    Rarity.LEGENDARY: "yellow",
}


@dataclass
class ItemTemplate:
    name: str
    item_type: ItemType
    base_stats: dict[str, int]
    level_requirement: int
    description: str
    slot: str


# ==================== WEAPONS ====================

WEAPON_TEMPLATES = [
    ItemTemplate(
        name="Rusty Shortsword",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 4},
        level_requirement=1,
        description="A dull, chipped blade. Better than bare fists.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Iron Dagger",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 5, "crit_chance": 5},
        level_requirement=1,
        description="A simple iron dagger, light and fast.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Wooden Staff",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 3, "mp_bonus": 10},
        level_requirement=1,
        description="A gnarled wooden staff humming with faint energy.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Iron Mace",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 6},
        level_requirement=2,
        description="A heavy iron mace that crushes bone on impact.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Hunting Bow",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 5, "crit_chance": 3},
        level_requirement=2,
        description="A sturdy shortbow made for hunting game.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Steel Longsword",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 10},
        level_requirement=4,
        description="A well-forged longsword with a keen edge.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Battle Axe",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 12, "crit_chance": 5},
        level_requirement=5,
        description="A brutal double-headed axe that cleaves through armor.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Assassin's Stiletto",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 8, "crit_chance": 15},
        level_requirement=5,
        description="A needle-thin blade designed for finding gaps in armor.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Oak Wand",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 6, "mp_bonus": 20, "INT": 2},
        level_requirement=4,
        description="A wand carved from ancient oak, channeling arcane power.",
        slot="weapon",
    ),
    ItemTemplate(
        name="War Hammer",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 14, "stun_chance": 5},
        level_requirement=7,
        description="A devastating hammer that shatters shields and skulls.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Elven Longbow",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 13, "crit_chance": 10, "DEX": 2},
        level_requirement=7,
        description="An elegantly crafted bow of incredible range and accuracy.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Runic Blade",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 16, "mp_bonus": 10},
        level_requirement=8,
        description="Ancient runes glow along this blade's fuller.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Crystal Staff",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 10, "mp_bonus": 35, "INT": 4},
        level_requirement=9,
        description="A staff crowned with a pulsing crystal of pure magic.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Obsidian Greatsword",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 22, "crit_chance": 8},
        level_requirement=12,
        description="A massive two-handed sword of volcanic glass, razor sharp.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Shadowfang Dagger",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 15, "crit_chance": 20, "life_steal": 5},
        level_requirement=12,
        description="This cursed dagger drinks the blood of its victims.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Holy Avenger",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 20, "WIS": 4, "hp_bonus": 20},
        level_requirement=14,
        description="A blessed greatsword that glows with divine radiance.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Archmage's Scepter",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 12, "mp_bonus": 50, "INT": 6},
        level_requirement=15,
        description="The scepter of a long-dead archmage, thrumming with power.",
        slot="weapon",
    ),
    ItemTemplate(
        name="Doom Blade",
        item_type=ItemType.WEAPON,
        base_stats={"attack": 30, "crit_chance": 12, "life_steal": 8},
        level_requirement=18,
        description="A blade forged in the abyss, whispering of destruction.",
        slot="weapon",
    ),
]

# ==================== ARMOR ====================

ARMOR_TEMPLATES = [
    ItemTemplate(
        name="Tattered Rags",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 2},
        level_requirement=1,
        description="Barely qualifies as clothing, let alone armor.",
        slot="armor",
    ),
    ItemTemplate(
        name="Leather Vest",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 4, "dodge": 2},
        level_requirement=1,
        description="A simple leather vest offering modest protection.",
        slot="armor",
    ),
    ItemTemplate(
        name="Padded Armor",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 6},
        level_requirement=3,
        description="Thick quilted padding that softens incoming blows.",
        slot="armor",
    ),
    ItemTemplate(
        name="Chain Mail",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 10},
        level_requirement=5,
        description="Interlocking metal rings forming a sturdy shirt of mail.",
        slot="armor",
    ),
    ItemTemplate(
        name="Studded Leather",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 8, "dodge": 5},
        level_requirement=4,
        description="Leather reinforced with metal studs for added protection.",
        slot="armor",
    ),
    ItemTemplate(
        name="Scale Mail",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 14, "hp_bonus": 10},
        level_requirement=7,
        description="Overlapping metal scales riveted to a leather backing.",
        slot="armor",
    ),
    ItemTemplate(
        name="Mage Robes",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 5, "mp_bonus": 25, "INT": 3},
        level_requirement=5,
        description="Enchanted robes woven with threads of mana.",
        slot="armor",
    ),
    ItemTemplate(
        name="Plate Armor",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 20, "hp_bonus": 15},
        level_requirement=10,
        description="Full steel plate armor, heavy but nearly impenetrable.",
        slot="armor",
    ),
    ItemTemplate(
        name="Dragonhide Armor",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 18, "dodge": 5, "hp_bonus": 20},
        level_requirement=12,
        description="Armor fashioned from the hide of a slain dragon.",
        slot="armor",
    ),
    ItemTemplate(
        name="Arcane Vestments",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 10, "mp_bonus": 40, "INT": 5, "WIS": 3},
        level_requirement=12,
        description="Grand vestments pulsing with barely contained magical energy.",
        slot="armor",
    ),
    ItemTemplate(
        name="Adamantine Plate",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 28, "hp_bonus": 30},
        level_requirement=16,
        description="Armor forged from the rarest metal, nearly indestructible.",
        slot="armor",
    ),
    ItemTemplate(
        name="Shadow Cloak",
        item_type=ItemType.ARMOR,
        base_stats={"defense": 12, "dodge": 15, "crit_chance": 8},
        level_requirement=13,
        description="A cloak woven from living shadow, hard to see and harder to hit.",
        slot="armor",
    ),
]

# ==================== HELMETS ====================

HELMET_TEMPLATES = [
    ItemTemplate(
        name="Leather Cap",
        item_type=ItemType.HELMET,
        base_stats={"defense": 2},
        level_requirement=1,
        description="A simple leather cap.",
        slot="helmet",
    ),
    ItemTemplate(
        name="Iron Helm",
        item_type=ItemType.HELMET,
        base_stats={"defense": 4, "hp_bonus": 5},
        level_requirement=3,
        description="A sturdy iron helmet with a nose guard.",
        slot="helmet",
    ),
    ItemTemplate(
        name="Wizard Hat",
        item_type=ItemType.HELMET,
        base_stats={"defense": 1, "mp_bonus": 15, "INT": 2},
        level_requirement=4,
        description="A pointed hat that enhances magical focus.",
        slot="helmet",
    ),
    ItemTemplate(
        name="Steel Great Helm",
        item_type=ItemType.HELMET,
        base_stats={"defense": 8, "hp_bonus": 10},
        level_requirement=8,
        description="A full-face great helm offering excellent protection.",
        slot="helmet",
    ),
    ItemTemplate(
        name="Crown of Thorns",
        item_type=ItemType.HELMET,
        base_stats={"defense": 3, "WIS": 5, "mp_bonus": 20},
        level_requirement=10,
        description="A painful crown that deepens spiritual connection.",
        slot="helmet",
    ),
    ItemTemplate(
        name="Dragon Skull Helm",
        item_type=ItemType.HELMET,
        base_stats={"defense": 12, "hp_bonus": 20, "STR": 3},
        level_requirement=14,
        description="A helm carved from a dragon's skull, radiating dread.",
        slot="helmet",
    ),
]

# ==================== BOOTS ====================

BOOTS_TEMPLATES = [
    ItemTemplate(
        name="Worn Sandals",
        item_type=ItemType.BOOTS,
        base_stats={"dodge": 1},
        level_requirement=1,
        description="Barely-held-together sandals.",
        slot="boots",
    ),
    ItemTemplate(
        name="Leather Boots",
        item_type=ItemType.BOOTS,
        base_stats={"defense": 2, "dodge": 3},
        level_requirement=2,
        description="Sturdy leather boots with good grip.",
        slot="boots",
    ),
    ItemTemplate(
        name="Iron Greaves",
        item_type=ItemType.BOOTS,
        base_stats={"defense": 5, "hp_bonus": 5},
        level_requirement=5,
        description="Heavy iron greaves that protect the shins.",
        slot="boots",
    ),
    ItemTemplate(
        name="Boots of Swiftness",
        item_type=ItemType.BOOTS,
        base_stats={"dodge": 10, "DEX": 2},
        level_requirement=7,
        description="Feather-light boots that quicken your step.",
        slot="boots",
    ),
    ItemTemplate(
        name="Plated Sabatons",
        item_type=ItemType.BOOTS,
        base_stats={"defense": 8, "hp_bonus": 10},
        level_requirement=10,
        description="Full plate boots with reinforced soles.",
        slot="boots",
    ),
    ItemTemplate(
        name="Shadowstep Boots",
        item_type=ItemType.BOOTS,
        base_stats={"dodge": 15, "crit_chance": 5, "DEX": 3},
        level_requirement=13,
        description="Boots that let you step between shadows.",
        slot="boots",
    ),
]

# ==================== ACCESSORIES ====================

ACCESSORY_TEMPLATES = [
    ItemTemplate(
        name="Copper Ring",
        item_type=ItemType.RING,
        base_stats={"hp_bonus": 5},
        level_requirement=1,
        description="A plain copper ring, slightly warm to the touch.",
        slot="ring",
    ),
    ItemTemplate(
        name="Silver Ring",
        item_type=ItemType.RING,
        base_stats={"hp_bonus": 10, "mp_bonus": 5},
        level_requirement=3,
        description="A polished silver ring with a faint inscription.",
        slot="ring",
    ),
    ItemTemplate(
        name="Ring of Strength",
        item_type=ItemType.RING,
        base_stats={"STR": 3, "attack": 2},
        level_requirement=5,
        description="A heavy iron ring that empowers the wearer's muscles.",
        slot="ring",
    ),
    ItemTemplate(
        name="Ring of Shadows",
        item_type=ItemType.RING,
        base_stats={"dodge": 8, "crit_chance": 5},
        level_requirement=7,
        description="A dark ring that bends light around the wearer.",
        slot="ring",
    ),
    ItemTemplate(
        name="Bone Amulet",
        item_type=ItemType.AMULET,
        base_stats={"hp_bonus": 10, "defense": 2},
        level_requirement=2,
        description="A crude amulet carved from bone, faintly protective.",
        slot="amulet",
    ),
    ItemTemplate(
        name="Amulet of Wisdom",
        item_type=ItemType.AMULET,
        base_stats={"WIS": 3, "mp_bonus": 15},
        level_requirement=5,
        description="A glowing pendant that sharpens the mind.",
        slot="amulet",
    ),
    ItemTemplate(
        name="Bloodstone Pendant",
        item_type=ItemType.AMULET,
        base_stats={"life_steal": 5, "hp_bonus": 15},
        level_requirement=8,
        description="A deep red gem that drinks the life force of your enemies.",
        slot="amulet",
    ),
    ItemTemplate(
        name="Phoenix Feather Amulet",
        item_type=ItemType.AMULET,
        base_stats={"hp_bonus": 30, "mp_bonus": 20, "all_stats": 2},
        level_requirement=14,
        description="An amulet containing a genuine phoenix feather, radiating warmth.",
        slot="amulet",
    ),
]

# ==================== CONSUMABLES ====================

CONSUMABLE_TEMPLATES = [
    ItemTemplate(
        name="Minor Health Potion",
        item_type=ItemType.POTION,
        base_stats={"heal": 25},
        level_requirement=1,
        description="A small vial of red liquid. Restores 25 HP.",
        slot="",
    ),
    ItemTemplate(
        name="Health Potion",
        item_type=ItemType.POTION,
        base_stats={"heal": 60},
        level_requirement=4,
        description="A flask of crimson liquid. Restores 60 HP.",
        slot="",
    ),
    ItemTemplate(
        name="Greater Health Potion",
        item_type=ItemType.POTION,
        base_stats={"heal": 120},
        level_requirement=8,
        description="A large bottle of deep red elixir. Restores 120 HP.",
        slot="",
    ),
    ItemTemplate(
        name="Supreme Health Potion",
        item_type=ItemType.POTION,
        base_stats={"heal": 250},
        level_requirement=14,
        description="A potent brew that mends even grievous wounds. Restores 250 HP.",
        slot="",
    ),
    ItemTemplate(
        name="Minor Mana Potion",
        item_type=ItemType.POTION,
        base_stats={"restore_mp": 15},
        level_requirement=1,
        description="A small vial of blue liquid. Restores 15 MP.",
        slot="",
    ),
    ItemTemplate(
        name="Mana Potion",
        item_type=ItemType.POTION,
        base_stats={"restore_mp": 40},
        level_requirement=4,
        description="A flask of azure liquid. Restores 40 MP.",
        slot="",
    ),
    ItemTemplate(
        name="Greater Mana Potion",
        item_type=ItemType.POTION,
        base_stats={"restore_mp": 80},
        level_requirement=8,
        description="A large bottle of glowing blue elixir. Restores 80 MP.",
        slot="",
    ),
    ItemTemplate(
        name="Antidote",
        item_type=ItemType.POTION,
        base_stats={"cure": 1},
        level_requirement=1,
        description="Cures poison and other toxins.",
        slot="",
    ),
    ItemTemplate(
        name="Elixir of Power",
        item_type=ItemType.POTION,
        base_stats={"buff_attack": 10, "duration": 5},
        level_requirement=6,
        description="Temporarily boosts attack power for 5 turns.",
        slot="",
    ),
    ItemTemplate(
        name="Elixir of Iron",
        item_type=ItemType.POTION,
        base_stats={"buff_defense": 10, "duration": 5},
        level_requirement=6,
        description="Temporarily boosts defense for 5 turns.",
        slot="",
    ),
    ItemTemplate(
        name="Scroll of Fireball",
        item_type=ItemType.SCROLL,
        base_stats={"fire_damage": 50},
        level_requirement=5,
        description="A charred scroll that unleashes a ball of flame. Hits all enemies.",
        slot="",
    ),
    ItemTemplate(
        name="Scroll of Lightning",
        item_type=ItemType.SCROLL,
        base_stats={"lightning_damage": 65},
        level_requirement=7,
        description="A crackling scroll that calls down a bolt of lightning on one foe.",
        slot="",
    ),
    ItemTemplate(
        name="Scroll of Healing",
        item_type=ItemType.SCROLL,
        base_stats={"heal": 80},
        level_requirement=5,
        description="A blessed scroll that mends wounds with divine light.",
        slot="",
    ),
    ItemTemplate(
        name="Scroll of Teleport",
        item_type=ItemType.SCROLL,
        base_stats={"teleport": 1},
        level_requirement=3,
        description="A scroll that transports you to the dungeon entrance.",
        slot="",
    ),
    ItemTemplate(
        name="Scroll of Identify",
        item_type=ItemType.SCROLL,
        base_stats={"identify": 1},
        level_requirement=1,
        description="Reveals the true properties of an unidentified item.",
        slot="",
    ),
]

# ==================== AFFIXES ====================

PREFIXES = {
    "Sharp": {"attack": 3},
    "Mighty": {"attack": 5},
    "Keen": {"crit_chance": 10},
    "Sturdy": {"defense": 3},
    "Fortified": {"defense": 5},
    "Hardy": {"hp_bonus": 20},
    "Arcane": {"mp_bonus": 15},
    "Swift": {"dodge": 5},
    "Vampiric": {"life_steal": 5},
    "Blessed": {"all_stats": 1},
    "Thundering": {"attack": 4, "stun_chance": 5},
    "Savage": {"attack": 6, "crit_chance": 5},
    "Guardian": {"defense": 4, "hp_bonus": 10},
    "Mystic": {"mp_bonus": 20, "INT": 2},
    "Radiant": {"attack": 3, "hp_bonus": 10},
    "Brutal": {"attack": 8, "crit_chance": -5},
    "Nimble": {"dodge": 8, "DEX": 1},
    "Resolute": {"defense": 3, "hp_bonus": 15},
    "Frozen": {"attack": 3, "slow_chance": 10},
    "Blazing": {"attack": 4, "burn_chance": 10},
}

SUFFIXES = {
    "of Power": {"STR": 3},
    "of Grace": {"DEX": 3},
    "of Wisdom": {"WIS": 3},
    "of Intellect": {"INT": 3},
    "of Vitality": {"CON": 3},
    "of Charisma": {"CHA": 3},
    "of the Bear": {"CON": 3, "hp_bonus": 10},
    "of the Fox": {"DEX": 2, "crit_chance": 5},
    "of the Owl": {"WIS": 2, "mp_bonus": 10},
    "of the Tiger": {"STR": 2, "attack": 3},
    "of the Turtle": {"defense": 4, "hp_bonus": 5},
    "of Flame": {"fire_damage": 5},
    "of Ice": {"ice_damage": 5, "slow_chance": 10},
    "of Thunder": {"lightning_damage": 5, "stun_chance": 5},
    "of the Vampire": {"life_steal": 8},
    "of the Wind": {"dodge": 6},
    "of the Mountain": {"defense": 6, "CON": 2},
    "of Sorcery": {"INT": 4, "mp_bonus": 15},
    "of Thorns": {"defense": 2, "reflect_damage": 5},
    "of the Phoenix": {"hp_bonus": 25, "fire_damage": 3},
}

RARITY_AFFIX_COUNT = {
    Rarity.COMMON: 0,
    Rarity.UNCOMMON: 1,
    Rarity.RARE: 2,
    Rarity.EPIC: 3,
    Rarity.LEGENDARY: 4,
}

RARITY_STAT_MULTIPLIER = {
    Rarity.COMMON: 1.0,
    Rarity.UNCOMMON: 1.15,
    Rarity.RARE: 1.3,
    Rarity.EPIC: 1.5,
    Rarity.LEGENDARY: 1.8,
}
