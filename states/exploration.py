"""Exploration state -- dungeon crawling, movement, FOV, encounters."""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

from engine.config import FOV_RADIUS
from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game
    from entities.enemy import Enemy


class ExplorationState(GameState):
    """Main gameplay loop: move through the dungeon, encounter enemies, loot items."""

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        # UI components (lazily initialised in on_enter)
        self.map_view = None
        self.stats_panel = None
        self.log_panel = None
        self.hotbar = None
        self.minimap = None
        self.renderer = None
        self.ambient = None

        # Floor entities
        self.enemies_on_floor: list[Enemy] = []
        self.items_on_ground: list[dict] = []  # [{item, x, y}]
        self.npcs_on_floor: list = []
        self.enemy_ai = None

        self.ambient_timer: float = 0.0

    # -- lifecycle -----------------------------------------------------

    def on_enter(self) -> None:
        from effects.ambient import AmbientEffects
        from systems.enemy_ai import EnemyAI
        from ui.hotbar import Hotbar
        from ui.log_panel import LogPanel
        from ui.map_view import MapView
        from ui.minimap import Minimap
        from ui.renderer import GameRenderer
        from ui.stats_panel import StatsPanel

        self.map_view = MapView()
        self.stats_panel = StatsPanel()
        self.log_panel = LogPanel()
        self.hotbar = Hotbar()
        self.minimap = Minimap()
        self.renderer = GameRenderer()
        self.ambient = AmbientEffects()
        self.enemy_ai = EnemyAI()

        if self.game.current_map is None:
            self._generate_floor()

    def on_resume(self) -> None:
        """Called when returning from overlay states (inventory, combat, etc.)."""
        # Remove dead enemies
        self.enemies_on_floor = [e for e in self.enemies_on_floor if e.is_alive()]
        # Recompute FOV
        if self.game.current_map and self.game.player:
            from world.fov import compute_fov

            compute_fov(
                self.game.current_map.tiles,
                self.game.player.x,
                self.game.player.y,
                FOV_RADIUS,
            )

    # -- floor generation ----------------------------------------------

    def _generate_floor(self) -> None:
        from data.themes import get_theme_for_floor
        from entities.enemy import Enemy
        from world.fov import compute_fov
        from world.generators.bsp import generate_bsp

        player = self.game.player
        theme = get_theme_for_floor(player.floor)
        # generate_bsp expects theme_name as a string key
        theme_key = self._resolve_theme_key(player.floor)
        floor = generate_bsp(80, 40, player.floor, theme_key)
        self.game.current_map = floor

        # Place player at spawn
        player.x, player.y = floor.spawn_point

        # Spawn enemies
        self.enemies_on_floor = []
        enemy_pool = theme.enemy_pool if theme.enemy_pool else ["Rat", "Goblin"]

        for spawn_pos in floor.enemy_spawns:
            template_name = random.choice(enemy_pool)
            # Random chance for modifier
            modifier = None
            if random.random() < 0.15:
                from data.enemies import ENEMY_MODIFIERS

                modifier = random.choice(list(ENEMY_MODIFIERS.keys()))

            enemy = Enemy.from_template(
                template_name, level=player.floor, modifier=modifier
            )
            enemy.x, enemy.y = spawn_pos
            self.enemies_on_floor.append(enemy)

        # Place items on ground at chest positions
        from systems.loot import LootSystem

        loot_sys = LootSystem(self.game)
        self.items_on_ground = []
        for chest_pos in floor.chest_positions:
            items = loot_sys.generate_chest_loot(player.floor)
            for item in items:
                self.items_on_ground.append(
                    {"item": item, "x": chest_pos[0], "y": chest_pos[1]}
                )

        # Spawn NPCs in safe rooms (not enemy rooms, not spawn/stairs)
        from entities.npc import NPC

        self.npcs_on_floor = []
        used_positions = set(floor.enemy_spawns)
        used_positions.add(floor.spawn_point)
        if floor.stairs_down:
            used_positions.add(floor.stairs_down)

        npc_rooms = [r for r in floor.rooms if r.center not in used_positions]
        random.shuffle(npc_rooms)

        # Always spawn a merchant and a healer; quest giver on odd floors
        npc_types = ["merchant", "healer"]
        if player.floor % 2 == 1:
            npc_types.append("quest_giver")

        for npc_type in npc_types:
            if not npc_rooms:
                break
            room = npc_rooms.pop()
            cx, cy = room.center
            # Make sure the center is walkable
            if not floor.is_walkable(cx, cy):
                continue
            if npc_type == "merchant":
                npc = NPC.create_merchant(player.floor)
            elif npc_type == "healer":
                npc = NPC.create_healer(player.floor)
            else:
                npc = NPC.create_quest_giver(player.floor)
            npc.x, npc.y = cx, cy
            self.npcs_on_floor.append(npc)

        # Compute initial FOV
        compute_fov(floor.tiles, player.x, player.y, FOV_RADIUS)

        self.game.add_log(f"[bold]Floor {player.floor}[/bold] -- {theme.name}")

        # Reset enemy AI state for the new floor
        if self.enemy_ai:
            self.enemy_ai.reset()

        # Trigger floor narrative if available
        nm = getattr(self.game, "narrative_manager", None)
        if nm:
            pages = nm.on_floor_entered(player.floor)
            if pages:
                from states.cinematic_state import CinematicState

                self.game.state_manager.push(
                    CinematicState(self.game, pages, title="The Depths")
                )

    @staticmethod
    def _resolve_theme_key(floor_number: int) -> str:
        """Map floor number to the theme dict key string."""
        from data.themes import _FLOOR_THEME_RANGES

        for low, high, key in _FLOOR_THEME_RANGES:
            if low <= floor_number <= high:
                return key
        return "crypt"

    # -- input ---------------------------------------------------------

    def handle_input(self, key: str) -> None:
        player = self.game.player
        dx, dy = 0, 0

        if key in ("w", "up"):
            dy = -1
        elif key in ("s", "down"):
            dy = 1
        elif key in ("a", "left"):
            dx = -1
        elif key in ("d", "right"):
            dx = 1
        elif key == "i":
            from states.inventory_state import InventoryState

            self.game.state_manager.push(InventoryState(self.game))
            return
        elif key == "c":
            from states.character_state import CharacterState

            self.game.state_manager.push(CharacterState(self.game))
            return
        elif key == "escape":
            self.game.state_manager.push(PauseMenuState(self.game))
            return
        elif key == "g":
            self._try_pickup()
            return
        elif key == ">":
            self._try_stairs()
            return

        if dx != 0 or dy != 0:
            self._try_move(player, dx, dy)

    # -- movement & interactions ---------------------------------------

    def _try_move(self, player, dx: int, dy: int) -> None:
        new_x = player.x + dx
        new_y = player.y + dy
        floor = self.game.current_map

        if not floor or not floor.is_walkable(new_x, new_y):
            return

        # Check for NPC collision -> open dialogue
        for npc in self.npcs_on_floor:
            if npc.x == new_x and npc.y == new_y:
                from states.dialogue_state import DialogueState

                self.game.state_manager.push(DialogueState(self.game, npc))
                return

        # Check for enemy collision -> start combat
        for enemy in self.enemies_on_floor:
            if enemy.x == new_x and enemy.y == new_y and enemy.is_alive():
                self._start_combat([enemy])
                return

        # Record movement for directional glyph and footprint trail
        if self.map_view:
            self.map_view.record_move(player.x, player.y, dx, dy)

        # Move player
        player.x = new_x
        player.y = new_y

        # Update FOV
        from world.fov import compute_fov

        compute_fov(floor.tiles, player.x, player.y, FOV_RADIUS)

        # Check for items at feet
        items_here = [
            it
            for it in self.items_on_ground
            if it["x"] == new_x and it["y"] == new_y
        ]
        if items_here:
            self.game.add_log(
                "[dim italic]You see something on the ground. Press [G] to pick up.[/dim italic]"
            )

        # Check stairs
        tile = floor.get_tile(new_x, new_y)
        if tile and tile.tile_type.value == "stairs_down":
            self.game.add_log(
                "[dim italic]Stairs leading down. Press [>] to descend.[/dim italic]"
            )

        # Check for random CYOA exploration events
        nm = getattr(self.game, "narrative_manager", None)
        if nm:
            event_pages = nm.check_exploration_event(player.floor)
            if event_pages:
                from states.cinematic_state import CinematicState

                self.game.state_manager.push(
                    CinematicState(self.game, event_pages, title="An Encounter")
                )

        # Tick enemy AI — enemies move after the player
        if self.enemy_ai and floor:
            ai_messages = self.enemy_ai.tick(
                floor, player.x, player.y, self.enemies_on_floor
            )
            for msg in ai_messages:
                self.game.add_log(msg)

            # Check if an enemy walked adjacent — no auto-combat, but warn
            for enemy in self.enemies_on_floor:
                if not enemy.is_alive():
                    continue
                dist = abs(enemy.x - player.x) + abs(enemy.y - player.y)
                if dist == 1:
                    self.game.add_log(
                        f"[bold red]{enemy.name} is right next to you![/bold red]"
                    )
                    break

    def _try_pickup(self) -> None:
        player = self.game.player
        items_here = [
            it
            for it in self.items_on_ground
            if it["x"] == player.x and it["y"] == player.y
        ]
        if not items_here:
            self.game.add_log("[dim]Nothing to pick up here.[/dim]")
            return

        picked_up: list = []
        for it in items_here:
            item = it["item"]
            # Handle gold items — absorb directly, never goes to inventory
            item_type = item.get("type", "")
            item_name = item.get("name", "item")

            if item_type == "gold" or "gold" in item_name.lower():
                gold_amount = item.get("value", item.get("gold_value", 0))
                if gold_amount > 0:
                    player.gold += gold_amount
                    picked_up.append(it)
                    self.game.add_log(
                        f"[yellow]+{gold_amount} gold[/yellow] picked up!"
                    )
                else:
                    picked_up.append(it)  # Remove worthless gold
            elif player.add_item(item):
                picked_up.append(it)
                rarity = item.get("rarity", "common")
                rarity_colors = {
                    "common": "white", "uncommon": "green", "rare": "bright_blue",
                    "epic": "bright_magenta", "legendary": "bright_yellow",
                }
                color = rarity_colors.get(rarity, "white")
                self.game.add_log(
                    f"Picked up [{color}]{item_name}[/{color}]!"
                )
            else:
                self.game.add_log("[red]Inventory full![/red]")
                break

        # Remove all picked-up items from the ground
        for it in picked_up:
            if it in self.items_on_ground:
                self.items_on_ground.remove(it)

    def _try_lore_pickup(self, lore_id: str) -> None:
        """Handle discovering a lore collectible."""
        nm = getattr(self.game, "narrative_manager", None)
        if not nm:
            return
        entry = nm.on_lore_found(lore_id)
        if entry:
            from states.lore_state import LoreState

            self.game.state_manager.push(LoreState(self.game, entry))
            found, total = nm.get_lore_progress()
            self.game.add_log(f"[bold cyan]Lore discovered! ({found}/{total})[/bold cyan]")

    def _try_stairs(self) -> None:
        player = self.game.player
        floor = self.game.current_map
        if floor is None:
            return
        tile = floor.get_tile(player.x, player.y)
        if tile and tile.tile_type.value == "stairs_down":
            player.floor += 1
            self.game.current_map = None
            self._generate_floor()

    def _start_combat(self, enemies: list[Enemy]) -> None:
        from states.combat_state import CombatState

        names = ", ".join(e.name for e in enemies)
        self.game.add_log(f"[bold red]Combat! Enemies: {names}[/bold red]")
        self.game.state_manager.push(CombatState(self.game, enemies))

    # -- update --------------------------------------------------------

    def update(self, dt: float) -> None:
        # Expire old footprints
        if self.map_view and self.map_view._footprints:
            import time as _time
            now = _time.time()
            self.map_view._footprints = [
                (x, y, t) for x, y, t in self.map_view._footprints if now - t < 2.0
            ]

        self.ambient_timer += dt
        if self.ambient_timer > 15.0:
            self.ambient_timer = 0.0
            msg = self._get_proximity_message()
            if msg:
                self.game.add_log(f"[dim italic]{msg}[/dim italic]")

    # -- proximity ambient messages ------------------------------------

    _ENEMY_MESSAGES = [
        "You hear something shuffling in the darkness...",
        "A low growl echoes from nearby...",
        "The hairs on the back of your neck stand up...",
        "You sense hostile eyes watching you...",
    ]
    _WATER_MESSAGES = [
        "Water drips steadily somewhere nearby...",
        "You hear the gentle trickle of water...",
        "The air feels damp and cold...",
    ]
    _STAIRS_MESSAGES = [
        "A draft of air rises from somewhere below...",
        "You feel a breeze from deeper in the dungeon...",
    ]
    _ITEM_MESSAGES = [
        "Something glints in the dim light...",
        "You notice something on the ground nearby...",
    ]
    _ATMOSPHERIC_MESSAGES = [
        "Silence presses in around you...",
        "Your footsteps echo in the empty corridor...",
        "Dust motes drift in the still air...",
    ]

    def _get_proximity_message(self) -> str | None:
        """Return a contextual ambient message based on what's near the player."""
        player = self.game.player
        if player is None:
            return None
        px, py = player.x, player.y

        # --- Check enemies within 8 tiles ---
        for enemy in self.enemies_on_floor:
            if not enemy.is_alive():
                continue
            dist = math.hypot(enemy.x - px, enemy.y - py)
            if dist <= 8.0:
                return random.choice(self._ENEMY_MESSAGES)

        floor = self.game.current_map
        if floor is not None:
            # --- Check water tiles within 3 tiles ---
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    if math.hypot(dx, dy) > 3.0:
                        continue
                    tx, ty = px + dx, py + dy
                    if not floor.is_in_bounds(tx, ty):
                        continue
                    from world.tile import TileType

                    if floor.tiles[ty][tx].tile_type == TileType.WATER:
                        return random.choice(self._WATER_MESSAGES)

            # --- Check stairs within 4 tiles ---
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    if math.hypot(dx, dy) > 4.0:
                        continue
                    tx, ty = px + dx, py + dy
                    if not floor.is_in_bounds(tx, ty):
                        continue
                    from world.tile import TileType

                    if floor.tiles[ty][tx].tile_type in (
                        TileType.STAIRS_DOWN,
                        TileType.STAIRS_UP,
                    ):
                        return random.choice(self._STAIRS_MESSAGES)

        # --- Check items on ground within 4 tiles ---
        for it in self.items_on_ground:
            dist = math.hypot(it["x"] - px, it["y"] - py)
            if dist <= 4.0:
                return random.choice(self._ITEM_MESSAGES)

        # --- Fallback: atmospheric ---
        return random.choice(self._ATMOSPHERIC_MESSAGES)

    # -- render --------------------------------------------------------

    def render(self) -> RenderableType:
        player = self.game.player
        floor = self.game.current_map

        self.map_view.update_camera(player.x, player.y)

        map_panel = self.map_view.render(
            floor, player, self.enemies_on_floor, self.items_on_ground,
            npcs=self.npcs_on_floor,
        )
        stats_panel = self.stats_panel.render(player)
        minimap_panel = self.minimap.render(
            floor, player.x, player.y,
            enemies=self.enemies_on_floor,
            items_on_ground=self.items_on_ground,
        )
        log_panel = self.log_panel.render(self.game.combat_log)
        hotbar_panel = self.hotbar.render(
            [
                ("W/A/S/D", "Move"),
                ("G", "Pickup"),
                ("I", "Inventory"),
                ("C", "Character"),
                (">", "Stairs"),
                ("ESC", "Menu"),
            ]
        )

        return self.renderer.create_exploration_layout(
            map_panel, stats_panel, minimap_panel, log_panel, hotbar_panel
        )

    def render_pygame(self, screen, font, renderer) -> None:
        """Render exploration state to Pygame screen."""
        from pygame_ui.pg_hotbar import PgHotbar
        from pygame_ui.pg_log_panel import PgLogPanel
        from pygame_ui.pg_map_view import PgMapView
        from pygame_ui.pg_minimap import PgMinimap
        from pygame_ui.pg_stats_panel import PgStatsPanel

        player = self.game.player
        floor = self.game.current_map

        # Lazy-init Pygame UI components
        if not hasattr(self, "_pg_map"):
            self._pg_map = PgMapView()
            self._pg_stats = PgStatsPanel()
            self._pg_log = PgLogPanel()
            self._pg_hotbar = PgHotbar()
            self._pg_minimap = PgMinimap()

        # Sync facing from Rich map view
        if self.map_view:
            self._pg_map.player_facing = self.map_view.player_facing
            self._pg_map._footprints = self.map_view._footprints

        map_surf = self._pg_map.render(
            floor, player, self.enemies_on_floor, self.items_on_ground,
            font, renderer.map_rect.width, renderer.map_rect.height,
        )
        stats_surf = self._pg_stats.render(
            player, font, renderer.stats_rect.width, renderer.stats_rect.height,
        )
        minimap_surf = self._pg_minimap.render(
            floor, player.x, player.y,
            enemies=self.enemies_on_floor,
            items_on_ground=self.items_on_ground,
            width=renderer.minimap_rect.width,
            height=renderer.minimap_rect.height,
        )
        log_surf = self._pg_log.render(
            self.game.combat_log, font,
            renderer.log_rect.width, renderer.log_rect.height,
        )
        hotbar_surf = self._pg_hotbar.render(
            [("WASD", "Move"), ("G", "Pickup"), ("I", "Inv"),
             ("C", "Char"), (">", "Stairs"), ("Esc", "Menu")],
            font, renderer.hotbar_rect.width, renderer.hotbar_rect.height,
        )
        renderer.draw_exploration_layout(
            screen, map_surf, stats_surf, minimap_surf, log_surf, hotbar_surf,
        )


class PauseMenuState(GameState):
    """Simple pause overlay with resume, save, and quit-to-menu options."""

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        from ui.menu import Menu

        self.menu = Menu("Paused", ["Resume", "Save Game", "Quit to Menu"])

    def handle_input(self, key: str) -> None:
        if key == "up":
            self.menu.move_up()
        elif key == "down":
            self.menu.move_down()
        elif key == "escape":
            self.game.state_manager.pop()
        elif key == "enter":
            selected = self.menu.get_selected()
            if selected == "Resume":
                self.game.state_manager.pop()
            elif selected == "Save Game":
                from engine.save_manager import SaveManager

                SaveManager.save(self.game)
                self.game.add_log("[bold green]Game saved![/bold green]")
                self.game.state_manager.pop()
            elif selected == "Quit to Menu":
                from states.main_menu import MainMenuState

                self.game.state_manager.clear()
                self.game.state_manager.push(MainMenuState(self.game))

    def update(self, dt: float) -> None:
        pass

    def render(self) -> RenderableType:
        from rich.align import Align

        return Align.center(self.menu.render(), vertical="middle")

    def render_pygame(self, screen, font, renderer) -> None:
        from pygame_ui.pg_menu import PgMenu

        pg_menu = PgMenu(self.menu.title, self.menu.options)
        pg_menu.selected_index = self.menu.selected_index
        w, h = renderer.screen_width, renderer.screen_height
        menu_surf = pg_menu.render(font, w // 2, h // 2)
        screen.fill((0, 0, 0))
        screen.blit(menu_surf, (w // 4, h // 4))
