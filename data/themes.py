"""Dungeon theme definitions for visual styling and content pools."""

from dataclasses import dataclass, field


@dataclass
class DungeonTheme:
    name: str
    wall_char: str
    floor_char: str
    door_char: str
    stairs_down_char: str
    stairs_up_char: str
    water_char: str
    chest_char: str
    trap_char: str
    wall_color: str
    floor_color: str
    door_color: str
    stairs_color: str
    water_color: str
    chest_color: str
    trap_color: str
    ambient_description: str
    enemy_pool: list[str] = field(default_factory=list)
    special_features: list[str] = field(default_factory=list)


THEMES: dict[str, DungeonTheme] = {
    "crypt": DungeonTheme(
        name="Ancient Crypt",
        wall_char="\u2588",
        floor_char=".",
        door_char="+",
        stairs_down_char=">",
        stairs_up_char="<",
        water_char="~",
        chest_char="$",
        trap_char="^",
        wall_color="grey62",
        floor_color="grey35",
        door_color="dark_goldenrod",
        stairs_color="bright_white",
        water_color="dark_cyan",
        chest_color="bright_yellow",
        trap_color="red",
        ambient_description="Dust motes drift through shafts of pale light between crumbling stone sarcophagi.",
        enemy_pool=["Rat", "Skeleton", "Slime", "Bat Swarm"],
        special_features=["coffins", "cobwebs", "bone_piles", "torch_sconces"],
    ),
    "cave": DungeonTheme(
        name="Dark Caverns",
        wall_char="\u2593",
        floor_char="\u2591",
        door_char="\u25cb",
        stairs_down_char="\u25bd",
        stairs_up_char="\u25b3",
        water_char="~",
        chest_char="\u2666",
        trap_char="\u25ab",
        wall_color="dark_olive_green3",
        floor_color="grey27",
        door_color="sandy_brown",
        stairs_color="bright_white",
        water_color="dodger_blue1",
        chest_color="bright_yellow",
        trap_color="indian_red1",
        ambient_description="Water drips from stalactites overhead. The cave walls glisten with moisture.",
        enemy_pool=["Spider", "Bat Swarm", "Slime", "Goblin"],
        special_features=["stalactites", "underground_stream", "mushroom_patch", "crystal_vein"],
    ),
    "dungeon": DungeonTheme(
        name="Stone Dungeon",
        wall_char="#",
        floor_char="\u00b7",
        door_char="+",
        stairs_down_char=">",
        stairs_up_char="<",
        water_char="~",
        chest_char="$",
        trap_char="^",
        wall_color="grey50",
        floor_color="grey30",
        door_color="yellow",
        stairs_color="bright_white",
        water_color="blue",
        chest_color="bright_yellow",
        trap_color="red",
        ambient_description="Iron chains hang from the walls. The air reeks of mildew and despair.",
        enemy_pool=["Goblin", "Orc", "Skeleton", "Zombie"],
        special_features=["prison_cells", "torture_rack", "iron_maiden", "chains"],
    ),
    "sewer": DungeonTheme(
        name="Fetid Sewers",
        wall_char="\u2591",
        floor_char="~",
        door_char="+",
        stairs_down_char=">",
        stairs_up_char="<",
        water_char="\u2248",
        chest_char="$",
        trap_char="^",
        wall_color="dark_green",
        floor_color="green4",
        door_color="grey50",
        stairs_color="bright_white",
        water_color="chartreuse3",
        chest_color="bright_yellow",
        trap_color="dark_red",
        ambient_description="Foul water runs through channels in the floor. The stench is unbearable.",
        enemy_pool=["Rat", "Slime", "Zombie", "Spider"],
        special_features=["water_channels", "rusted_grates", "fungal_growth", "gas_vents"],
    ),
    "catacombs": DungeonTheme(
        name="Catacombs of the Damned",
        wall_char="\u2593",
        floor_char="\u00b7",
        door_char="\u25aa",
        stairs_down_char="\u25bc",
        stairs_up_char="\u25b2",
        water_char="\u2248",
        chest_char="\u25c8",
        trap_char="\u00d7",
        wall_color="grey42",
        floor_color="grey23",
        door_color="dark_goldenrod",
        stairs_color="white",
        water_color="dark_cyan",
        chest_color="gold1",
        trap_color="dark_red",
        ambient_description="Bones line the walls in macabre patterns. The air is stale and cold.",
        enemy_pool=["Skeleton", "Zombie", "Wraith", "Dark Knight"],
        special_features=["bones", "skulls", "sarcophagi", "death_runes"],
    ),
    "temple": DungeonTheme(
        name="Corrupted Temple",
        wall_char="\u2588",
        floor_char="\u00b7",
        door_char="\u256c",
        stairs_down_char=">",
        stairs_up_char="<",
        water_char="\u2248",
        chest_char="\u2726",
        trap_char="\u2297",
        wall_color="dark_red",
        floor_color="grey46",
        door_color="dark_orange",
        stairs_color="bright_white",
        water_color="steel_blue1",
        chest_color="gold1",
        trap_color="bright_red",
        ambient_description="Defaced altars and shattered stained glass litter the once-holy halls.",
        enemy_pool=["Dark Knight", "Wraith", "Demon", "Lich Apprentice"],
        special_features=["broken_altar", "stained_glass", "prayer_alcove", "holy_font"],
    ),
    "ruins": DungeonTheme(
        name="Ancient Ruins",
        wall_char="\u2588",
        floor_char="\u2219",
        door_char="\u25ca",
        stairs_down_char=">",
        stairs_up_char="<",
        water_char="\u224b",
        chest_char="\u229e",
        trap_char="\u2297",
        wall_color="rosy_brown",
        floor_color="grey35",
        door_color="dark_orange",
        stairs_color="bright_white",
        water_color="steel_blue1",
        chest_color="gold1",
        trap_color="bright_red",
        ambient_description="Crumbling pillars and faded murals hint at ancient glory long forgotten.",
        enemy_pool=["Troll", "Basilisk", "Dark Knight", "Wraith"],
        special_features=["pillars", "murals", "rubble", "ancient_mechanisms"],
    ),
    "inferno": DungeonTheme(
        name="Infernal Depths",
        wall_char="\u2588",
        floor_char="\u2591",
        door_char="\u256c",
        stairs_down_char="\u25bb",
        stairs_up_char="\u25b3",
        water_char="\u2240",
        chest_char="\u2726",
        trap_char="\u229b",
        wall_color="red3",
        floor_color="dark_orange3",
        door_color="bright_red",
        stairs_color="bright_magenta",
        water_color="red1",
        chest_color="bright_yellow",
        trap_color="bright_red",
        ambient_description="Lava flows between obsidian platforms. The heat is suffocating.",
        enemy_pool=["Demon", "Dragon Whelp", "Lich Apprentice", "Dark Knight"],
        special_features=["lava_pools", "obsidian_pillars", "hellfire_vents", "demon_sigils"],
    ),
    "abyss": DungeonTheme(
        name="The Abyss",
        wall_char="\u2588",
        floor_char=" ",
        door_char="\u25c6",
        stairs_down_char="\u22bb",
        stairs_up_char="\u22bc",
        water_char="\u2240",
        chest_char="\u2726",
        trap_char="\u229b",
        wall_color="purple4",
        floor_color="grey15",
        door_color="medium_orchid",
        stairs_color="bright_magenta",
        water_color="dark_violet",
        chest_color="bright_yellow",
        trap_color="bright_red",
        ambient_description="Reality warps at the edges. The darkness feels alive and hungry.",
        enemy_pool=["Demon", "Lich Apprentice", "Dragon Whelp"],
        special_features=["void_rifts", "dark_flames", "corruption", "reality_tears"],
    ),
}

# Floor-to-theme mapping
_FLOOR_THEME_RANGES: list[tuple[int, int, str]] = [
    (1, 2, "crypt"),
    (3, 3, "catacombs"),
    (4, 5, "cave"),
    (6, 7, "dungeon"),
    (8, 9, "sewer"),
    (10, 11, "ruins"),
    (12, 13, "temple"),
    (14, 15, "inferno"),
    (16, 99, "abyss"),
]


def get_theme_for_floor(floor_number: int) -> DungeonTheme:
    """Return the DungeonTheme appropriate for the given floor number."""
    for low, high, theme_key in _FLOOR_THEME_RANGES:
        if low <= floor_number <= high:
            return THEMES[theme_key]
    return THEMES["crypt"]
