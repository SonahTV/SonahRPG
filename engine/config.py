"""Game constants and configuration for SonahRPG."""

# Core settings
GAME_TITLE = "SonahRPG"
FPS = 20

# Map dimensions
MAP_WIDTH = 80
MAP_HEIGHT = 40

# Field of view
FOV_RADIUS = 8

# Terminal requirements
MIN_TERMINAL_WIDTH = 100
MIN_TERMINAL_HEIGHT = 30

# UI limits
MAX_LOG_LINES = 50

# Save system
SAVE_DIR = "saves"

# Stat colors
COLOR_HEALTH = "red"
COLOR_MANA = "blue"
COLOR_XP = "green"

# Rarity colors
COLOR_COMMON = "white"
COLOR_UNCOMMON = "green"
COLOR_RARE = "blue"
COLOR_EPIC = "magenta"
COLOR_LEGENDARY = "yellow"

RARITY_COLORS: dict[str, str] = {
    "common": COLOR_COMMON,
    "uncommon": COLOR_UNCOMMON,
    "rare": COLOR_RARE,
    "epic": COLOR_EPIC,
    "legendary": COLOR_LEGENDARY,
}

# Pygame window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILE_SIZE = 16
FONT_SIZE = 16
