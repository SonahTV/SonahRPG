"""Main menu state -- immersive title screen, character creation, and game loading."""

from __future__ import annotations

import math
import random
import time
from typing import TYPE_CHECKING

from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from engine.state import GameState
from ui.menu import Menu

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game


# ---------------------------------------------------------------------------
# Animated particle system for the Pygame menu background
# ---------------------------------------------------------------------------

class _Ember:
    """A single floating ember/ash particle."""

    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color")

    def __init__(self, x: float, y: float, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-15, 15)
        self.vy = random.uniform(-40, -10)
        self.max_life = random.uniform(2.0, 5.0)
        self.life = self.max_life
        self.size = random.randint(1, 3)
        self.color = color

    def tick(self, dt: float) -> bool:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx += random.uniform(-5, 5) * dt  # drift
        self.life -= dt
        return self.life > 0


class _MenuParticles:
    """Manages background particles for the menu screen."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.embers: list[_Ember] = []
        self.spawn_timer = 0.0
        self._colors = [
            (255, 100, 30),   # orange ember
            (255, 60, 20),    # red ember
            (200, 50, 10),    # dark ember
            (255, 140, 50),   # bright ember
            (100, 40, 140),   # purple wisp
            (60, 30, 100),    # dark purple
        ]

    def tick(self, dt: float) -> None:
        self.spawn_timer += dt
        # Spawn embers from bottom
        while self.spawn_timer > 0.05:
            self.spawn_timer -= 0.05
            x = random.uniform(0, self.width)
            y = self.height + 5
            color = random.choice(self._colors)
            self.embers.append(_Ember(x, y, color))

        self.embers = [e for e in self.embers if e.tick(dt)]

    def draw(self, screen) -> None:
        import pygame
        for e in self.embers:
            alpha = e.life / e.max_life
            r = int(e.color[0] * alpha)
            g = int(e.color[1] * alpha)
            b = int(e.color[2] * alpha)
            if r > 0 or g > 0 or b > 0:
                pygame.draw.circle(screen, (r, g, b), (int(e.x), int(e.y)), e.size)


# ---------------------------------------------------------------------------
# Title art lines for Pygame (drawn char by char with glow)
# ---------------------------------------------------------------------------

_PYGAME_TITLE_LINES = [
    r"  ____                    _       ____  ____   ____ ",
    r" / ___|  ___  _ __   __ _| |__   |  _ \|  _ \ / ___|",
    r" \___ \ / _ \| '_ \ / _` | '_ \  | |_) | |_) | |  _ ",
    r"  ___) | (_) | | | | (_| | | | | |  _ <|  __/| |_| |",
    r" |____/ \___/|_| |_|\__,_|_| |_| |_| \_\_|    \____|",
]

_SUBTITLE_LINES = [
    r"         _____ _            ____             _   _",
    r"        |_   _| |__   ___  |  _ \  ___ _ __ | |_| |__  ___",
    r"          | | | '_ \ / _ \ | | | |/ _ \ '_ \| __| '_ \/ __|",
    r"          | | | | | |  __/ | |_| |  __/ |_) | |_| | | \__ \\",
    r"          |_| |_| |_|\___| |____/ \___| .__/ \__|_| |_|___/",
    r"                                       |_|",
]

_TAGLINE = "No one has returned from The Depths."


class MainMenuState(GameState):
    """Immersive title menu with animated effects, character creation flow.

    Phases:
    - menu: New Game / Load Game / Quit
    - name_input: type hero name
    - class_select: pick a class with full preview
    """

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.menu = Menu("Main Menu", ["New Game", "Load Game", "Quit"])
        self.title_art = ""
        self.phase = "menu"  # "menu", "name_input", "class_select"
        self.player_name = ""
        self.class_menu: Menu | None = None

        # Animation state
        self._time = 0.0
        self._particles: _MenuParticles | None = None
        self._whisper_text = ""
        self._whisper_timer = 0.0
        self._whisper_alpha = 0.0
        self._whisper_phase = "idle"  # idle, fade_in, hold, fade_out
        self._cursor_blink = 0.0

    # -- lifecycle -----------------------------------------------------

    def on_enter(self) -> None:
        from data.ascii_art import TITLE_ART

        self.title_art = TITLE_ART
        self._pick_new_whisper()

    def _pick_new_whisper(self) -> None:
        """Select a random entity whisper for the background."""
        try:
            from data.lore import ENTITY_WHISPERS
            self._whisper_text = random.choice(ENTITY_WHISPERS)
        except (ImportError, IndexError):
            self._whisper_text = "...the darkness stirs beneath Ashenmere..."
        self._whisper_timer = 0.0
        self._whisper_alpha = 0.0
        self._whisper_phase = "fade_in"

    # -- input ---------------------------------------------------------

    def handle_input(self, key: str) -> None:
        if self.phase == "menu":
            self._handle_menu_input(key)
        elif self.phase == "name_input":
            self._handle_name_input(key)
        elif self.phase == "class_select":
            self._handle_class_select(key)

    def _handle_menu_input(self, key: str) -> None:
        if key == "up":
            self.menu.move_up()
        elif key == "down":
            self.menu.move_down()
        elif key == "enter":
            selected = self.menu.get_selected()
            if selected == "New Game":
                self.phase = "name_input"
                self.player_name = ""
            elif selected == "Load Game":
                self._try_load()
            elif selected == "Quit":
                self.game.quit()

    def _handle_name_input(self, key: str) -> None:
        if key == "enter" and len(self.player_name) >= 1:
            self.phase = "class_select"
            from data.classes import CLASSES

            class_names = list(CLASSES.keys())
            descriptions = [CLASSES[c].description for c in class_names]
            self.class_menu = Menu("Choose Your Class", class_names, descriptions)
        elif key == "escape":
            self.phase = "menu"
        elif key == "backspace":
            self.player_name = self.player_name[:-1]
        elif len(key) == 1 and key.isalnum() and len(self.player_name) < 20:
            self.player_name += key

    def _handle_class_select(self, key: str) -> None:
        if self.class_menu is None:
            return
        if key == "up":
            self.class_menu.move_up()
        elif key == "down":
            self.class_menu.move_down()
        elif key == "enter":
            self._start_new_game(self.player_name, self.class_menu.get_selected())
        elif key == "escape":
            self.phase = "name_input"

    # -- actions -------------------------------------------------------

    def _start_new_game(self, name: str, player_class: str) -> None:
        from entities.player import Player

        player = Player.create(name, player_class)
        self.game.new_game(player)
        self.game.add_log(
            f"[bold bright_white]{name}[/bold bright_white] the "
            f"[bold]{player_class}[/bold] enters the dungeon..."
        )

        # Show intro cinematic with class backstory before exploration
        if hasattr(self.game, "narrative_manager") and self.game.narrative_manager:
            from states.cinematic_state import CinematicState

            pages = self.game.narrative_manager.get_intro_pages()
            if pages:
                from states.exploration import ExplorationState

                def on_intro_complete():
                    self.game.narrative_manager.intro_shown = True
                    self.game.state_manager.replace(ExplorationState(self.game))

                self.game.state_manager.replace(
                    CinematicState(
                        self.game, pages,
                        on_complete=on_intro_complete,
                        title="The Condemned",
                    )
                )
                return

        # Fallback: skip straight to exploration if no narrative
        from states.exploration import ExplorationState

        self.game.state_manager.replace(ExplorationState(self.game))

    def _try_load(self) -> None:
        from engine.save_manager import SaveManager

        saves = SaveManager.list_saves()
        if saves:
            data = SaveManager.load(saves[0]["slot"])
            if data and "player" in data:
                from entities.player import Player
                from states.exploration import ExplorationState

                self.game.player = Player.from_dict(data["player"])

                # Restore narrative state
                from systems.narrative_manager import NarrativeManager

                if "narrative" in data:
                    self.game.narrative_manager = NarrativeManager.from_dict(
                        data["narrative"], self.game
                    )
                else:
                    self.game.narrative_manager = NarrativeManager(self.game)

                self.game.add_log("[bold green]Game loaded successfully![/bold green]")
                self.game.state_manager.replace(ExplorationState(self.game))
            else:
                self.game.add_log("[dim]Save file is corrupted.[/dim]")
        else:
            self.game.add_log("[dim]No save files found.[/dim]")

    # -- update --------------------------------------------------------

    def update(self, dt: float) -> None:
        self._time += dt
        self._cursor_blink += dt

        # Animate particles
        if self._particles:
            self._particles.tick(dt)

        # Animate whisper text
        self._whisper_timer += dt
        if self._whisper_phase == "fade_in":
            self._whisper_alpha = min(1.0, self._whisper_timer / 2.0)
            if self._whisper_alpha >= 1.0:
                self._whisper_phase = "hold"
                self._whisper_timer = 0.0
        elif self._whisper_phase == "hold":
            if self._whisper_timer > 4.0:
                self._whisper_phase = "fade_out"
                self._whisper_timer = 0.0
        elif self._whisper_phase == "fade_out":
            self._whisper_alpha = max(0.0, 1.0 - self._whisper_timer / 2.0)
            if self._whisper_alpha <= 0.0:
                self._whisper_phase = "idle"
                self._whisper_timer = 0.0
        elif self._whisper_phase == "idle":
            if self._whisper_timer > 2.0:
                self._pick_new_whisper()

    # -- Rich terminal render ------------------------------------------

    def render(self) -> RenderableType:
        parts: list[RenderableType] = []

        # Title art
        title = Text(self.title_art, style="bold bright_cyan")
        parts.append(Align.center(title))
        parts.append(Text("\n"))

        if self.phase == "menu":
            parts.append(Align.center(self.menu.render()))

        elif self.phase == "name_input":
            name_text = Text()
            name_text.append("\n  Enter your name: ", style="bold")
            name_text.append(self.player_name, style="bold bright_white underline")
            name_text.append("_", style="blink bold bright_white")
            name_text.append("\n\n  [Enter] Confirm  [Esc] Back\n", style="dim")
            parts.append(
                Align.center(
                    Panel(
                        name_text,
                        title="[bold]Hero Name[/bold]",
                        border_style="bright_blue",
                    )
                )
            )

        elif self.phase == "class_select" and self.class_menu is not None:
            parts.append(self._render_class_select())

        return Panel(
            Group(*parts),
            title="[bold bright_cyan]SonahRPG[/bold bright_cyan]",
            border_style="bright_cyan",
        )

    # -- Pygame render -------------------------------------------------

    def render_pygame(self, screen, font, renderer) -> None:
        """Render immersive animated main menu to Pygame screen."""
        import pygame
        from pygame_ui.colors import get_rgb

        w, h = screen.get_size()

        # Initialize particles on first render
        if self._particles is None:
            self._particles = _MenuParticles(w, h)

        # --- Background: dark gradient with vignette ---
        screen.fill((8, 4, 12))

        # Subtle animated gradient bands
        for y_band in range(0, h, 2):
            progress = y_band / h
            noise = math.sin(self._time * 0.3 + progress * 5.0) * 0.15
            r = int((8 + 20 * progress + 8 * noise))
            g = int((4 + 6 * progress))
            b = int((12 + 25 * progress + 12 * noise))
            r = max(0, min(40, r))
            g = max(0, min(15, g))
            b = max(0, min(50, b))
            pygame.draw.line(screen, (r, g, b), (0, y_band), (w, y_band))

        # Draw particles behind everything
        self._particles.draw(screen)

        # --- Phase-specific content ---
        if self.phase == "menu":
            self._render_pygame_menu(screen, font, w, h)
        elif self.phase == "name_input":
            self._render_pygame_name_input(screen, font, w, h)
        elif self.phase == "class_select":
            self._render_pygame_class_select(screen, font, w, h)

    def _render_pygame_menu(self, screen, font, w: int, h: int) -> None:
        import pygame
        from pygame_ui.colors import get_rgb

        t = self._time
        cx = w // 2

        # --- Animated title with per-character color cycling ---
        title_y = 60
        for line_idx, line in enumerate(_PYGAME_TITLE_LINES):
            line_w = font.char_width * len(line)
            start_x = cx - line_w // 2
            for ci, ch in enumerate(line):
                if ch == " ":
                    continue
                # Color wave: cyan → white → cyan
                phase = math.sin(t * 2.0 + ci * 0.15 + line_idx * 0.5)
                if phase > 0.3:
                    color = (85, 255, 255)   # bright cyan
                elif phase > -0.3:
                    color = (200, 240, 255)  # white-cyan
                else:
                    color = (30, 160, 180)   # dim cyan
                glyph = font.render_glyph(ch, color)
                screen.blit(glyph, (start_x + ci * font.char_width, title_y))
            title_y += font.char_height

        # Subtitle: "The Depths" with purple fade
        title_y += font.char_height
        for line_idx, line in enumerate(_SUBTITLE_LINES):
            line_w = font.char_width * len(line)
            start_x = cx - line_w // 2
            for ci, ch in enumerate(line):
                if ch == " ":
                    continue
                phase = math.sin(t * 1.5 + ci * 0.1 + line_idx * 0.8)
                r = int(120 + 60 * max(0, phase))
                g = int(40 + 30 * max(0, phase))
                b = int(180 + 60 * max(0, phase))
                glyph = font.render_glyph(ch, (r, g, b))
                screen.blit(glyph, (start_x + ci * font.char_width, title_y))
            title_y += font.char_height

        # --- Tagline ---
        tagline_y = title_y + font.char_height * 2
        pulse = 0.5 + 0.5 * math.sin(t * 1.2)
        tag_r = int(120 * pulse)
        tag_g = int(80 * pulse)
        tag_b = int(60 * pulse)
        tag_surf = font.render_text(_TAGLINE, (tag_r, tag_g, tag_b))
        screen.blit(tag_surf, (cx - tag_surf.get_width() // 2, tagline_y))

        # --- Menu options ---
        menu_y = h // 2 + 30
        for i, option in enumerate(self.menu.options):
            is_selected = i == self.menu.selected_index

            if is_selected:
                # Animated highlight bar
                bar_pulse = 0.7 + 0.3 * math.sin(t * 4.0)
                bar_w = font.char_width * (len(option) + 8)
                bar_h = font.char_height + 8
                bar_x = cx - bar_w // 2
                bar_surface = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
                bar_surface.fill((
                    int(40 * bar_pulse),
                    int(30 * bar_pulse),
                    int(60 * bar_pulse),
                    180,
                ))
                screen.blit(bar_surface, (bar_x, menu_y - 4))

                # Selection arrow
                arrow_x = cx - font.char_width * (len(option) // 2 + 3)
                arrow_bob = int(math.sin(t * 5.0) * 3)
                arrow = font.render_glyph(">", (255, 200, 50))
                screen.blit(arrow, (arrow_x + arrow_bob, menu_y))

                text_surf = font.render_text(f"  {option}  ", (255, 220, 100))
            else:
                text_surf = font.render_text(f"  {option}  ", (120, 110, 130))

            screen.blit(text_surf, (cx - text_surf.get_width() // 2, menu_y))
            menu_y += font.char_height * 2 + 4

        # --- Whisper text at bottom ---
        if self._whisper_alpha > 0.01 and self._whisper_text:
            alpha = self._whisper_alpha
            wr = int(80 * alpha)
            wg = int(50 * alpha)
            wb = int(100 * alpha)
            whisper_surf = font.render_text(self._whisper_text, (wr, wg, wb))
            whisper_y = h - 60
            screen.blit(whisper_surf, (cx - whisper_surf.get_width() // 2, whisper_y))

        # --- Bottom hint ---
        hint_surf = font.render_text(
            "[Up/Down] Navigate   [Enter] Select", (50, 45, 60)
        )
        screen.blit(hint_surf, (cx - hint_surf.get_width() // 2, h - 25))

    def _render_pygame_name_input(self, screen, font, w: int, h: int) -> None:
        import pygame
        from pygame_ui.colors import get_rgb

        cx = w // 2
        t = self._time

        # Small title at top
        title = font.render_text("SonahRPG", (30, 160, 180))
        screen.blit(title, (cx - title.get_width() // 2, 30))

        # Name input box
        box_w = 500
        box_h = 200
        box_x = cx - box_w // 2
        box_y = h // 2 - box_h // 2 - 30

        # Glowing border
        border_pulse = 0.6 + 0.4 * math.sin(t * 2.0)
        border_color = (
            int(40 * border_pulse),
            int(100 * border_pulse),
            int(200 * border_pulse),
        )
        pygame.draw.rect(screen, (12, 8, 20), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, border_color, (box_x, box_y, box_w, box_h), 2)

        # "What is your name, Condemned?"
        prompt_text = "What is your name, Condemned?"
        prompt_surf = font.render_text(prompt_text, (160, 140, 180))
        screen.blit(prompt_surf, (cx - prompt_surf.get_width() // 2, box_y + 30))

        # Name with cursor
        cursor_visible = int(self._cursor_blink * 2.5) % 2 == 0
        display_name = self.player_name + ("|" if cursor_visible else " ")
        name_surf = font.render_text(display_name, (255, 240, 200))
        # Underline
        name_w = font.char_width * len(self.player_name)
        line_x = cx - name_w // 2
        name_y = box_y + 80
        screen.blit(name_surf, (line_x, name_y))
        pygame.draw.line(
            screen, (80, 70, 120),
            (line_x, name_y + font.char_height + 2),
            (line_x + max(name_w, 200), name_y + font.char_height + 2),
        )

        # Hint
        hint = font.render_text("[Enter] Accept your fate   [Esc] Return", (60, 55, 75))
        screen.blit(hint, (cx - hint.get_width() // 2, box_y + box_h - 40))

        # Flavor text below
        flavor = font.render_text(
            "Your name will be remembered... or forgotten.", (40, 35, 55)
        )
        screen.blit(flavor, (cx - flavor.get_width() // 2, box_y + box_h + 30))

    def _render_pygame_class_select(self, screen, font, w: int, h: int) -> None:
        import pygame
        from pygame_ui.colors import get_rgb
        from data.classes import CLASSES

        if self.class_menu is None:
            return

        cx = w // 2
        t = self._time

        # Header
        header = font.render_text("Choose Your Condemnation", (160, 140, 180))
        screen.blit(header, (cx - header.get_width() // 2, 20))

        selected_class = self.class_menu.get_selected()
        cls = CLASSES[selected_class]

        # --- Left panel: class list ---
        list_x = 40
        list_y = 70

        for i, class_name in enumerate(self.class_menu.options):
            is_sel = i == self.class_menu.selected_index
            class_def = CLASSES[class_name]

            if is_sel:
                # Highlight bar
                bar_w = 300
                bar_pulse = 0.7 + 0.3 * math.sin(t * 3.0)
                bar_surface = pygame.Surface((bar_w, font.char_height * 3 + 10), pygame.SRCALPHA)
                bar_surface.fill((int(30 * bar_pulse), int(25 * bar_pulse), int(50 * bar_pulse), 160))
                screen.blit(bar_surface, (list_x - 5, list_y - 3))

                # Arrow
                arrow_bob = int(math.sin(t * 5.0) * 2)
                screen.blit(
                    font.render_glyph(">", (255, 200, 50)),
                    (list_x + arrow_bob, list_y),
                )
                name_color = (255, 220, 100)
            else:
                name_color = (100, 90, 110)

            # Class name
            name_surf = font.render_text(f"  {class_name}", name_color)
            screen.blit(name_surf, (list_x + font.char_width, list_y))

            # Short role description
            role_map = {
                "Warrior": "Strength & Steel",
                "Rogue": "Shadow & Venom",
                "Mage": "Arcane & Destruction",
                "Cleric": "Faith & Restoration",
            }
            role = role_map.get(class_name, "")
            role_color = (70, 65, 85) if not is_sel else (120, 110, 140)
            role_surf = font.render_text(f"    {role}", role_color)
            screen.blit(role_surf, (list_x + font.char_width, list_y + font.char_height))

            # Stat bar preview
            primary = class_def.primary_stat
            primary_val = class_def.base_stats.get(primary, 10)
            stat_text = f"    {primary}: {primary_val}"
            stat_color = (60, 55, 75) if not is_sel else (100, 160, 100)
            screen.blit(font.render_text(stat_text, stat_color), (list_x + font.char_width, list_y + font.char_height * 2))

            list_y += font.char_height * 3 + 16

        # --- Right panel: class detail ---
        panel_x = 370
        panel_y = 60
        panel_w = w - panel_x - 30
        panel_h = h - 80

        # Panel background
        pygame.draw.rect(screen, (12, 8, 18), (panel_x, panel_y, panel_w, panel_h))

        # Animated border for selected class
        border_colors = {
            "Warrior": (200, 120, 40),
            "Rogue": (100, 200, 100),
            "Mage": (100, 100, 255),
            "Cleric": (200, 200, 100),
        }
        bc = border_colors.get(selected_class, (100, 100, 100))
        pulse = 0.5 + 0.5 * math.sin(t * 2.5)
        bc_anim = (int(bc[0] * pulse), int(bc[1] * pulse), int(bc[2] * pulse))
        pygame.draw.rect(screen, bc_anim, (panel_x, panel_y, panel_w, panel_h), 2)

        # Class name large
        py = panel_y + 15
        class_title = font.render_text(f"  {selected_class}", (255, 240, 200))
        screen.blit(class_title, (panel_x + 10, py))
        py += font.char_height + 4

        # Separator
        sep_w = panel_w - 30
        pygame.draw.line(screen, (40, 35, 55), (panel_x + 15, py), (panel_x + sep_w, py))
        py += 10

        # ASCII art with class-themed color
        art_colors = {
            "Warrior": (220, 160, 60),
            "Rogue": (60, 200, 80),
            "Mage": (120, 140, 255),
            "Cleric": (240, 220, 80),
        }
        art_color = art_colors.get(selected_class, (180, 180, 180))
        for line in cls.ascii_art.split("\n"):
            if line.strip():
                # Slight glow effect per char
                for ci, ch in enumerate(line):
                    if ch != " ":
                        glow = math.sin(t * 3.0 + ci * 0.3) * 0.2 + 0.8
                        c = (
                            min(255, int(art_color[0] * glow)),
                            min(255, int(art_color[1] * glow)),
                            min(255, int(art_color[2] * glow)),
                        )
                        screen.blit(
                            font.render_glyph(ch, c),
                            (panel_x + 30 + ci * font.char_width, py),
                        )
            py += font.char_height
        py += 12

        # Description (word-wrapped)
        desc = cls.description
        max_chars = (panel_w - 40) // font.char_width
        words = desc.split()
        lines: list[str] = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 > max_chars:
                lines.append(current)
                current = word
            else:
                current = f"{current} {word}" if current else word
        if current:
            lines.append(current)

        for line in lines:
            screen.blit(
                font.render_text(f"  {line}", (170, 155, 190)),
                (panel_x + 10, py),
            )
            py += font.char_height
        py += 12

        # Stats grid
        pygame.draw.line(screen, (40, 35, 55), (panel_x + 15, py), (panel_x + sep_w, py))
        py += 8

        # Stats in two columns
        stat_names = list(cls.base_stats.keys())
        col_w = (panel_w - 40) // 2
        for i, stat in enumerate(stat_names):
            val = cls.base_stats[stat]
            col = i % 2
            row = i // 2
            sx = panel_x + 20 + col * col_w
            sy = py + row * (font.char_height + 4)

            # Stat name
            stat_colors = {
                "STR": (220, 80, 80), "DEX": (80, 220, 80), "INT": (80, 120, 255),
                "WIS": (80, 220, 220), "CON": (220, 200, 60), "CHA": (200, 80, 200),
            }
            sc = stat_colors.get(stat, (180, 180, 180))
            screen.blit(font.render_text(f"{stat}:", sc), (sx, sy))

            # Stat bar
            bar_x = sx + font.char_width * 5
            bar_max_w = col_w - font.char_width * 8
            bar_fill = int((val / 20.0) * bar_max_w)
            pygame.draw.rect(screen, (25, 20, 35), (bar_x, sy + 3, bar_max_w, font.char_height - 6))
            pygame.draw.rect(screen, sc, (bar_x, sy + 3, bar_fill, font.char_height - 6))

            # Value
            screen.blit(
                font.render_text(f"{val}", (200, 200, 200)),
                (bar_x + bar_max_w + 4, sy),
            )

        py += (len(stat_names) // 2 + 1) * (font.char_height + 4) + 8

        # HP/MP per level
        hp_text = f"HP/Level: +{cls.hp_per_level}"
        mp_text = f"MP/Level: +{cls.mp_per_level}"
        screen.blit(font.render_text(hp_text, (220, 80, 80)), (panel_x + 20, py))
        screen.blit(font.render_text(mp_text, (80, 120, 255)), (panel_x + 20 + col_w, py))
        py += font.char_height + 4

        # Primary stat highlight
        primary_text = f"Primary: {cls.primary_stat}"
        screen.blit(font.render_text(primary_text, (255, 220, 100)), (panel_x + 20, py))
        py += font.char_height + 8

        # Skills preview (first 3)
        pygame.draw.line(screen, (40, 35, 55), (panel_x + 15, py), (panel_x + sep_w, py))
        py += 6
        screen.blit(font.render_text("  Starting Skills:", (140, 130, 160)), (panel_x + 10, py))
        py += font.char_height + 2
        shown = 0
        for skill in cls.skills:
            if skill["level_required"] <= 1 and shown < 3:
                skill_name = skill["name"]
                skill_desc = skill["description"][:40]
                screen.blit(
                    font.render_text(f"  + {skill_name}", (100, 220, 140)),
                    (panel_x + 15, py),
                )
                py += font.char_height
                screen.blit(
                    font.render_text(f"    {skill_desc}...", (70, 65, 85)),
                    (panel_x + 15, py),
                )
                py += font.char_height + 2
                shown += 1

        # Bottom hints
        hint = font.render_text(
            "[Up/Down] Choose   [Enter] Accept   [Esc] Back", (50, 45, 60)
        )
        screen.blit(hint, (cx - hint.get_width() // 2, h - 25))

    def _render_class_select(self) -> RenderableType:
        from data.classes import CLASSES

        selected_class = self.class_menu.get_selected()
        cls = CLASSES[selected_class]

        class_info = Text()
        class_info.append(f"\n{cls.ascii_art}\n", style="bold bright_yellow")
        class_info.append(f"\n  Primary Stat: {cls.primary_stat}\n", style="bold")
        class_info.append(
            f"  HP/Level: +{cls.hp_per_level}  MP/Level: +{cls.mp_per_level}\n"
        )
        stats_str = "  ".join(f"{k}:{v}" for k, v in cls.base_stats.items())
        class_info.append(f"  Stats: {stats_str}\n", style="dim")

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        grid.add_row(
            self.class_menu.render(),
            Panel(
                class_info,
                title="[bold]Preview[/bold]",
                border_style="yellow",
            ),
        )
        return grid
