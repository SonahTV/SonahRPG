from dataclasses import dataclass, field


@dataclass
class EnemyTemplate:
    name: str
    level_range: tuple[int, int]
    base_hp: int
    base_attack: int
    base_defense: int
    xp_reward: int
    gold_range: tuple[int, int]
    loot_table: list[dict]
    abilities: list[str]
    ascii_art: str
    flavor_text: str
    is_boss: bool = False


ENEMY_TEMPLATES = {
    # ==================== Level 1-3 ====================
    "Rat": EnemyTemplate(
        name="Rat",
        level_range=(1, 3),
        base_hp=15,
        base_attack=4,
        base_defense=2,
        xp_reward=10,
        gold_range=(1, 5),
        loot_table=[
            {"item_type": "potion", "rarity": "common", "chance": 0.3},
            {"item_type": "junk", "rarity": "common", "chance": 0.5},
        ],
        abilities=["Bite", "Scratch"],
        ascii_art=(
            "       .--.\n"
            "      /    \\\n"
            "     | •  • |\n"
            "      \\ -- /\n"
            "    ~--'||'--~\n"
            "       /  \\\n"
            "      '    '"
        ),
        flavor_text="A mangy rat with beady red eyes. It hisses at you from the shadows.",
    ),
    "Goblin": EnemyTemplate(
        name="Goblin",
        level_range=(1, 3),
        base_hp=22,
        base_attack=6,
        base_defense=3,
        xp_reward=18,
        gold_range=(3, 10),
        loot_table=[
            {"item_type": "weapon", "rarity": "common", "chance": 0.2},
            {"item_type": "potion", "rarity": "common", "chance": 0.3},
            {"item_type": "armor", "rarity": "common", "chance": 0.1},
        ],
        abilities=["Stab", "Throw Rock"],
        ascii_art=(
            "     /\\_/\\\n"
            "    ( o.o )\n"
            "     > ^ <\n"
            "    /| ~ |\\\n"
            "   / |   | \\\n"
            "      | |\n"
            "     _| |_"
        ),
        flavor_text="A small green-skinned creature clutching a rusty knife.",
    ),
    "Skeleton": EnemyTemplate(
        name="Skeleton",
        level_range=(1, 3),
        base_hp=18,
        base_attack=7,
        base_defense=4,
        xp_reward=15,
        gold_range=(2, 8),
        loot_table=[
            {"item_type": "weapon", "rarity": "common", "chance": 0.25},
            {"item_type": "armor", "rarity": "common", "chance": 0.15},
        ],
        abilities=["Bone Slash", "Rattle"],
        ascii_art=(
            "      .---.\n"
            "     / o o \\\n"
            "     |  ^  |\n"
            "      \\===/ \n"
            "     /|   |\\\n"
            "    / |   | \\\n"
            "      || ||\n"
            "     _|| ||_"
        ),
        flavor_text="Bones clatter as this animated skeleton raises its rusted blade.",
    ),
    "Slime": EnemyTemplate(
        name="Slime",
        level_range=(1, 3),
        base_hp=25,
        base_attack=3,
        base_defense=1,
        xp_reward=12,
        gold_range=(1, 4),
        loot_table=[
            {"item_type": "potion", "rarity": "common", "chance": 0.4},
            {"item_type": "scroll", "rarity": "uncommon", "chance": 0.1},
        ],
        abilities=["Acid Splash", "Absorb"],
        ascii_art=(
            "      .-\"\"\"\"\".\n"
            "     /  o  o  \\\n"
            "    |    __    |\n"
            "    |   /  \\   |\n"
            "     \\        /\n"
            "      '------'"
        ),
        flavor_text="A quivering blob of translucent green ooze inches toward you.",
    ),
    # ==================== Level 3-6 ====================
    "Orc": EnemyTemplate(
        name="Orc",
        level_range=(3, 6),
        base_hp=45,
        base_attack=12,
        base_defense=8,
        xp_reward=35,
        gold_range=(8, 20),
        loot_table=[
            {"item_type": "weapon", "rarity": "common", "chance": 0.3},
            {"item_type": "armor", "rarity": "common", "chance": 0.25},
            {"item_type": "weapon", "rarity": "uncommon", "chance": 0.1},
        ],
        abilities=["Cleave", "War Cry", "Headbutt"],
        ascii_art=(
            "     ,---.  \n"
            "    / o o \\ \n"
            "   |  \\_/  |\n"
            "    \\_____/ \n"
            "   /| = = |\\\n"
            "  / |     | \\\n"
            "    |     |\n"
            "    |_   _|"
        ),
        flavor_text="A hulking green brute with tusks protruding from its lower jaw.",
    ),
    "Spider": EnemyTemplate(
        name="Spider",
        level_range=(3, 6),
        base_hp=30,
        base_attack=10,
        base_defense=5,
        xp_reward=28,
        gold_range=(5, 12),
        loot_table=[
            {"item_type": "potion", "rarity": "uncommon", "chance": 0.2},
            {"item_type": "ring", "rarity": "uncommon", "chance": 0.08},
        ],
        abilities=["Venomous Bite", "Web Shot", "Skitter"],
        ascii_art=(
            "    /\\ () /\\\n"
            "   /  \\||/  \\\n"
            "  /  / oo \\  \\\n"
            " /  / |  | \\  \\\n"
            "    \\  \\/  /\n"
            "     '----'"
        ),
        flavor_text="Eight glistening eyes stare at you from the web-choked darkness.",
    ),
    "Zombie": EnemyTemplate(
        name="Zombie",
        level_range=(3, 6),
        base_hp=55,
        base_attack=8,
        base_defense=4,
        xp_reward=30,
        gold_range=(3, 10),
        loot_table=[
            {"item_type": "armor", "rarity": "common", "chance": 0.2},
            {"item_type": "potion", "rarity": "common", "chance": 0.3},
        ],
        abilities=["Bite", "Grab", "Infectious Strike"],
        ascii_art=(
            "      .---.\n"
            "     / x _ \\\n"
            "     | ___ |\n"
            "      \\   / \n"
            "    --|   |--\n"
            "   /  |   |  \n"
            "      |   |\n"
            "     _|   |_"
        ),
        flavor_text="A shambling corpse lurches forward, arms outstretched, moaning.",
    ),
    "Bat Swarm": EnemyTemplate(
        name="Bat Swarm",
        level_range=(3, 6),
        base_hp=35,
        base_attack=11,
        base_defense=3,
        xp_reward=25,
        gold_range=(4, 9),
        loot_table=[
            {"item_type": "potion", "rarity": "common", "chance": 0.35},
            {"item_type": "amulet", "rarity": "uncommon", "chance": 0.05},
        ],
        abilities=["Swarm", "Screech", "Life Drain"],
        ascii_art=(
            "   ^  ^   ^  ^\n"
            "  /|  |\\ /|  |\\\n"
            "   \\  /   \\  /\n"
            "  ^  ^  ^  ^ \n"
            " /|  |\\/ | |\\\n"
            "  \\  /  \\  / \n"
            "    vv    vv"
        ),
        flavor_text="A cloud of screeching bats fills the corridor, blocking out the light.",
    ),
    # ==================== Level 6-10 ====================
    "Dark Knight": EnemyTemplate(
        name="Dark Knight",
        level_range=(6, 10),
        base_hp=80,
        base_attack=18,
        base_defense=16,
        xp_reward=65,
        gold_range=(15, 35),
        loot_table=[
            {"item_type": "weapon", "rarity": "uncommon", "chance": 0.3},
            {"item_type": "armor", "rarity": "uncommon", "chance": 0.25},
            {"item_type": "weapon", "rarity": "rare", "chance": 0.08},
        ],
        abilities=["Dark Slash", "Shield Block", "Unholy Aura", "Execute"],
        ascii_art=(
            "     .---.  \n"
            "    |=====| \n"
            "    | >.< | \n"
            "    |=====| \n"
            "   /|  T  |\\\n"
            "  / |  |  | \\\n"
            "    |__|__|\n"
            "    |  ||  |"
        ),
        flavor_text="An armored knight wreathed in dark energy blocks your path.",
    ),
    "Wraith": EnemyTemplate(
        name="Wraith",
        level_range=(6, 10),
        base_hp=50,
        base_attack=20,
        base_defense=8,
        xp_reward=55,
        gold_range=(12, 28),
        loot_table=[
            {"item_type": "ring", "rarity": "uncommon", "chance": 0.15},
            {"item_type": "amulet", "rarity": "uncommon", "chance": 0.12},
            {"item_type": "scroll", "rarity": "rare", "chance": 0.1},
        ],
        abilities=["Life Drain", "Wail", "Phase Shift", "Soul Rend"],
        ascii_art=(
            "     .-.   \n"
            "    ( o o) \n"
            "     |O|   \n"
            "   __|_|__ \n"
            "  /  ~~~  \\\n"
            " /  ~~~~~  \\\n"
            "   ~~~~~~~ \n"
            "    ~~~~~  "
        ),
        flavor_text="A translucent figure hovers before you, cold emanating from its form.",
    ),
    "Troll": EnemyTemplate(
        name="Troll",
        level_range=(6, 10),
        base_hp=100,
        base_attack=16,
        base_defense=10,
        xp_reward=70,
        gold_range=(18, 40),
        loot_table=[
            {"item_type": "weapon", "rarity": "uncommon", "chance": 0.2},
            {"item_type": "armor", "rarity": "uncommon", "chance": 0.2},
            {"item_type": "potion", "rarity": "uncommon", "chance": 0.3},
        ],
        abilities=["Slam", "Regenerate", "Boulder Throw", "Roar"],
        ascii_art=(
            "    ___     \n"
            "   /. .\\    \n"
            "  | \\_/ |   \n"
            "   \\___/    \n"
            "  /|   |\\   \n"
            " | | O | |  \n"
            "   |   |    \n"
            "  _|   |_   "
        ),
        flavor_text="A massive troll lumbers forward, its wounds knitting shut before your eyes.",
    ),
    "Basilisk": EnemyTemplate(
        name="Basilisk",
        level_range=(6, 10),
        base_hp=70,
        base_attack=22,
        base_defense=12,
        xp_reward=60,
        gold_range=(14, 32),
        loot_table=[
            {"item_type": "ring", "rarity": "rare", "chance": 0.1},
            {"item_type": "potion", "rarity": "uncommon", "chance": 0.25},
            {"item_type": "scroll", "rarity": "uncommon", "chance": 0.15},
        ],
        abilities=["Petrifying Gaze", "Venomous Bite", "Tail Whip", "Stone Breath"],
        ascii_art=(
            "       /\\_    \n"
            "    __/ o \\   \n"
            "   /      |   \n"
            "  | ~~~~~~~ |\n"
            "   \\  ~~~~  / \n"
            "    \\______/  \n"
            "    /||  ||\\\n"
            "   / ||  || \\"
        ),
        flavor_text="A serpentine beast with deadly eyes. Do not meet its gaze.",
    ),
    # ==================== Level 10-15 ====================
    "Demon": EnemyTemplate(
        name="Demon",
        level_range=(10, 15),
        base_hp=120,
        base_attack=28,
        base_defense=18,
        xp_reward=120,
        gold_range=(30, 60),
        loot_table=[
            {"item_type": "weapon", "rarity": "rare", "chance": 0.2},
            {"item_type": "armor", "rarity": "rare", "chance": 0.15},
            {"item_type": "ring", "rarity": "rare", "chance": 0.1},
            {"item_type": "amulet", "rarity": "epic", "chance": 0.05},
        ],
        abilities=["Hellfire", "Corruption", "Shadow Bolt", "Demonic Fury", "Fear"],
        ascii_art=(
            "   \\\\  //   \n"
            "    \\\\//    \n"
            "   ( o  o ) \n"
            "    | \\/ |  \n"
            "    |_/\\_|  \n"
            "   /| || |\\ \n"
            "  / | || | \\\n"
            "    |_||_|  "
        ),
        flavor_text="A creature of hellfire and shadow, its eyes burn with malice.",
    ),
    "Dragon Whelp": EnemyTemplate(
        name="Dragon Whelp",
        level_range=(10, 15),
        base_hp=110,
        base_attack=25,
        base_defense=20,
        xp_reward=130,
        gold_range=(35, 70),
        loot_table=[
            {"item_type": "weapon", "rarity": "rare", "chance": 0.15},
            {"item_type": "armor", "rarity": "rare", "chance": 0.15},
            {"item_type": "amulet", "rarity": "rare", "chance": 0.1},
            {"item_type": "ring", "rarity": "epic", "chance": 0.05},
        ],
        abilities=["Fire Breath", "Claw Swipe", "Wing Buffet", "Tail Slam"],
        ascii_art=(
            "       /\\_/\\ \n"
            "      / o o \\\n"
            "     (  W    )\n"
            "    __\\ -- /  \n"
            "   /   \\  / \\ \n"
            "  |  ^  \\/  |\n"
            "   \\_/\\____/ \n"
            "     ||  ||  "
        ),
        flavor_text="A young dragon, barely the size of a horse, but no less deadly.",
    ),
    "Lich Apprentice": EnemyTemplate(
        name="Lich Apprentice",
        level_range=(10, 15),
        base_hp=85,
        base_attack=30,
        base_defense=14,
        xp_reward=140,
        gold_range=(40, 75),
        loot_table=[
            {"item_type": "scroll", "rarity": "rare", "chance": 0.3},
            {"item_type": "ring", "rarity": "rare", "chance": 0.15},
            {"item_type": "weapon", "rarity": "epic", "chance": 0.05},
        ],
        abilities=["Death Bolt", "Raise Dead", "Frost Nova", "Dark Pact", "Soul Cage"],
        ascii_art=(
            "     .---.  \n"
            "    / x x \\ \n"
            "    | _=_ | \n"
            "     \\   /  \n"
            "   __|---|__\n"
            "  /  *   *  \\\n"
            "     |   |  \n"
            "    _|   |_ "
        ),
        flavor_text="A robed figure crackling with necrotic energy, its phylactery glowing.",
    ),
    # ==================== Bosses ====================
    "Goblin King": EnemyTemplate(
        name="Goblin King",
        level_range=(3, 3),
        base_hp=80,
        base_attack=14,
        base_defense=10,
        xp_reward=100,
        gold_range=(30, 50),
        loot_table=[
            {"item_type": "weapon", "rarity": "uncommon", "chance": 0.5},
            {"item_type": "armor", "rarity": "uncommon", "chance": 0.4},
            {"item_type": "ring", "rarity": "rare", "chance": 0.15},
        ],
        abilities=["Royal Decree", "Summon Goblins", "Golden Slam", "Cowardly Retreat"],
        ascii_art=(
            "     .---.\n"
            "    /|0 0|\\\n"
            "   |  \\_/  |\n"
            "   |  ___  |\n"
            "   \\_|   |_/\n"
            "    /|   |\\\n"
            "   / | $ | \\\n"
            "     |___|  \n"
            "    _|| ||_ "
        ),
        flavor_text="The fat goblin king sits on a throne of stolen goods, crown askew.",
        is_boss=True,
    ),
    "Spider Queen": EnemyTemplate(
        name="Spider Queen",
        level_range=(6, 6),
        base_hp=140,
        base_attack=22,
        base_defense=14,
        xp_reward=200,
        gold_range=(40, 70),
        loot_table=[
            {"item_type": "weapon", "rarity": "rare", "chance": 0.4},
            {"item_type": "armor", "rarity": "rare", "chance": 0.3},
            {"item_type": "amulet", "rarity": "rare", "chance": 0.2},
            {"item_type": "ring", "rarity": "epic", "chance": 0.1},
        ],
        abilities=["Venom Spray", "Web Cocoon", "Spawn Broodlings", "Enrage", "Devour"],
        ascii_art=(
            "    /\\ /\\ /\\ /\\\n"
            "   /  X  X  X  \\\n"
            "  /  / \\/ \\/ \\  \\\n"
            " /  /  (@@)  \\  \\\n"
            "    \\  |  |  /\n"
            "     \\ |  | /\n"
            "      \\|  |/\n"
            "       '  '"
        ),
        flavor_text="A monstrous spider the size of an ox, dripping venom from its fangs.",
        is_boss=True,
    ),
    "Bone Dragon": EnemyTemplate(
        name="Bone Dragon",
        level_range=(10, 10),
        base_hp=250,
        base_attack=35,
        base_defense=22,
        xp_reward=400,
        gold_range=(80, 150),
        loot_table=[
            {"item_type": "weapon", "rarity": "epic", "chance": 0.3},
            {"item_type": "armor", "rarity": "epic", "chance": 0.25},
            {"item_type": "ring", "rarity": "epic", "chance": 0.2},
            {"item_type": "weapon", "rarity": "legendary", "chance": 0.05},
        ],
        abilities=["Necrotic Breath", "Bone Storm", "Raise Undead", "Tail Sweep", "Death Roar"],
        ascii_art=(
            "            __===___\n"
            "        .--'  / /  '.\n"
            "       / /   / /    |\n"
            "      | X   / /  X  |\n"
            "       \\   / /   __/\n"
            "    ___/\\_/ /  _/\n"
            "   /      \\/  /\n"
            "  /___________/\n"
            "    ||    ||"
        ),
        flavor_text="An enormous skeletal dragon rises, unholy fire blazing in its empty sockets.",
        is_boss=True,
    ),
    "Demon Lord": EnemyTemplate(
        name="Demon Lord",
        level_range=(15, 15),
        base_hp=400,
        base_attack=45,
        base_defense=28,
        xp_reward=800,
        gold_range=(150, 300),
        loot_table=[
            {"item_type": "weapon", "rarity": "legendary", "chance": 0.3},
            {"item_type": "armor", "rarity": "legendary", "chance": 0.2},
            {"item_type": "ring", "rarity": "legendary", "chance": 0.15},
            {"item_type": "amulet", "rarity": "legendary", "chance": 0.15},
        ],
        abilities=[
            "Infernal Nova", "Doom", "Chaos Bolt", "Summon Demons",
            "Dark Pact", "Hellfire Rain", "Soul Harvest",
        ],
        ascii_art=(
            "    \\\\    //  \n"
            "     \\\\  //   \n"
            "    (( o  o ))\n"
            "     | \\/ |   \n"
            "     | /\\ |   \n"
            "    /| || |\\  \n"
            "   //| || |\\\\  \n"
            "  // |_||_| \\\\\n"
            "     /    \\   \n"
            "    /______\\  "
        ),
        flavor_text="The lord of the abyss materializes, reality warping around his massive form.",
        is_boss=True,
    ),
}


ENEMY_MODIFIERS = {
    "Frenzied": {
        "attack_mult": 1.5,
        "defense_mult": 0.8,
        "hp_mult": 1.0,
        "xp_mult": 1.3,
        "prefix": "Frenzied",
        "special": None,
        "dodge_bonus": 0,
        "initiative_bonus": 0,
    },
    "Armored": {
        "attack_mult": 0.9,
        "defense_mult": 1.8,
        "hp_mult": 1.2,
        "xp_mult": 1.4,
        "prefix": "Armored",
        "special": None,
        "dodge_bonus": 0,
        "initiative_bonus": 0,
    },
    "Elder": {
        "attack_mult": 1.2,
        "defense_mult": 1.2,
        "hp_mult": 2.0,
        "xp_mult": 2.0,
        "prefix": "Elder",
        "special": None,
        "dodge_bonus": 0,
        "initiative_bonus": 0,
    },
    "Cursed": {
        "attack_mult": 1.1,
        "defense_mult": 1.0,
        "hp_mult": 1.1,
        "xp_mult": 1.5,
        "prefix": "Cursed",
        "special": "life_drain",
        "dodge_bonus": 0,
        "initiative_bonus": 0,
    },
    "Swift": {
        "attack_mult": 1.2,
        "defense_mult": 1.0,
        "hp_mult": 0.9,
        "xp_mult": 1.3,
        "prefix": "Swift",
        "special": None,
        "dodge_bonus": 10,
        "initiative_bonus": 5,
    },
    "Venomous": {
        "attack_mult": 1.0,
        "defense_mult": 1.0,
        "hp_mult": 1.0,
        "xp_mult": 1.4,
        "prefix": "Venomous",
        "special": "poison_attack",
        "dodge_bonus": 0,
        "initiative_bonus": 0,
    },
    "Ethereal": {
        "attack_mult": 1.1,
        "defense_mult": 0.5,
        "hp_mult": 0.8,
        "xp_mult": 1.6,
        "prefix": "Ethereal",
        "special": None,
        "dodge_bonus": 30,
        "initiative_bonus": 3,
    },
    "Enraged": {
        "attack_mult": 1.8,
        "defense_mult": 0.6,
        "hp_mult": 1.3,
        "xp_mult": 1.7,
        "prefix": "Enraged",
        "special": None,
        "dodge_bonus": 0,
        "initiative_bonus": 2,
    },
    "Ancient": {
        "attack_mult": 1.4,
        "defense_mult": 1.4,
        "hp_mult": 2.5,
        "xp_mult": 2.5,
        "prefix": "Ancient",
        "special": None,
        "dodge_bonus": 0,
        "initiative_bonus": 0,
    },
    "Shadow": {
        "attack_mult": 1.3,
        "defense_mult": 0.7,
        "hp_mult": 0.9,
        "xp_mult": 1.5,
        "prefix": "Shadow",
        "special": "shadow_strike",
        "dodge_bonus": 20,
        "initiative_bonus": 4,
    },
}
