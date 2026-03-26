"""Boss cutscene state — dramatic cinematic intro before boss fights.

Phases:
1. DARKNESS: Screen goes black, rumbling text fades in
2. ART_REVEAL: Boss ASCII art draws character by character with glow
3. TITLE_CARD: Boss name slams in with screen shake
4. LORE_TEXT: Atmospheric lore typewriters in with voice narration
5. READY: "PREPARE FOR BATTLE" pulses, any key starts the fight
"""

from __future__ import annotations

import math
import random
import time
from typing import TYPE_CHECKING, Callable

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game


# Large dramatic boss ASCII art for cutscenes
BOSS_CUTSCENE_ART = {
    "Goblin King": [
        r"                    ___________                    ",
        r"                   /     $     \                   ",
        r"                  / ___________\                  ",
        r"                 | /   \   /   \ |                 ",
        r"                 ||  O  | |  O  ||                 ",
        r"                 | \___/   \___/ |                 ",
        r"                  \   /\___/\   /                  ",
        r"                   \ |       | /                   ",
        r"                    \|  ===  |/                    ",
        r"               _____|\_____/|_____               ",
        r"              /  |  |       |  |  \              ",
        r"             /   |  | $$$$$ |  |   \             ",
        r"            /    |  |  $$$  |  |    \            ",
        r"           |     |  |       |  |     |           ",
        r"           |    /|__|_______|__|\_   |           ",
        r"            \  /     \     /     \  /            ",
        r"             \/       \   /       \/             ",
        r"                       \_/                       ",
    ],
    "Spider Queen": [
        r"                  .  *  .  *  .                   ",
        r"             .  /|\  *  /|\  .                    ",
        r"           *  //| \\___// |\\  *                  ",
        r"          . //  |  (@@)  |  \\ .                  ",
        r"         . //   | / || \ |   \\ .                 ",
        r"        .//    /  /  \  \    \\.                  ",
        r"       ://____/  / /\ \  \____\\:                ",
        r"       ||       / /  \ \       ||                ",
        r"       ||      / /    \ \      ||                ",
        r"       ||     / /  ()  \ \     ||                ",
        r"       ::    / /  (==)  \ \    ::                ",
        r"        \\  / /   |  |   \ \  //                 ",
        r"         \\/ /    |  |    \ \//                  ",
        r"          \\/     |  |     \//                   ",
        r"           \\_____/  \_____//                    ",
        r"            \______________/                     ",
        r"              |    ||    |                        ",
        r"              |____||____|                        ",
    ],
    "Bone Dragon": [
        r"                          ______________          ",
        r"                    _____/      X       \___      ",
        r"               ____/     \    X   X    /    \__   ",
        r"          ____/           \   \___/   /        \  ",
        r"     ____/     ___         \   |||   /    ___   | ",
        r"    /     ____/   \         \  |||  /   _/   \  | ",
        r"   |    _/         \     ____\_|||_/___/      | | ",
        r"   |   /    /===\   \___/                \    | | ",
        r"    \ |    |     |  /  \                  |   |/  ",
        r"     \|     \===/  / /\ \     /===\       |  /   ",
        r"      \          _/ /  \ \   |     |     _| /    ",
        r"       \________/ _/    \_\   \===/   __/ |/     ",
        r"               | /       \ \_________|  |        ",
        r"               |/    O    \|    ||      /        ",
        r"                \  O   O  /     ||     /         ",
        r"                 \__/ \__/      ||    /          ",
        r"                    | |         ||   /           ",
        r"                    |_|        _||__/            ",
    ],
    "Demon Lord": [
        r"              ___/\\\___/\\\___                   ",
        r"           __/  \\\\\\   //////  \__              ",
        r"         _/   \\\\\\\\ ////////   \_             ",
        r"        /  ___  \\\\\\ //////  ___  \            ",
        r"       | _/   \_ \\\\|//// _/   \_ |            ",
        r"       ||  (X)  |  \\|//  |  (X)  ||            ",
        r"       | \_   _/ ___|||___ \_   _/ |            ",
        r"        \   ---  /   V   \  ---   /             ",
        r"         \      / /|||||\ \      /              ",
        r"          \____/ / ||||| \ \____/               ",
        r"           |    /  |||||  \    |                 ",
        r"           |   /   |||||   \   |                 ",
        r"          /|  / /\ ||||| /\ \  |\               ",
        r"         / | / /  \|||||/  \ \ | \              ",
        r"        /  |/ /    |||||    \ \|  \             ",
        r"       /   || /    |||||    \ ||   \            ",
        r"      /    ||/_____||||||\____\||    \           ",
        r"     /_____|________________________|_____\      ",
    ],
}

# Dramatic subtitles for each boss
BOSS_SUBTITLES = {
    "Goblin King": "Scavenger of the First Seal",
    "Spider Queen": "The Corrupted Guardian",
    "Bone Dragon": "Keeper of the Forgotten Oath",
    "Demon Lord": "Avatar of the Dreaming God",
}

# Floor rumble text before reveal
BOSS_APPROACH_TEXT = {
    "Goblin King": "The stench of stolen gold fills the air...",
    "Spider Queen": "Silk threads brush your face in the darkness...",
    "Bone Dragon": "The ground trembles. Ancient bones begin to stir...",
    "Demon Lord": "Reality tears. The air itself screams...",
}


class BossCutsceneState(GameState):
    """Dramatic cinematic boss introduction.

    Shows a multi-phase cutscene before transitioning to combat.
    """

    PHASE_DARKNESS = "darkness"
    PHASE_ART_REVEAL = "art_reveal"
    PHASE_TITLE = "title"
    PHASE_LORE = "lore"
    PHASE_READY = "ready"

    def __init__(
        self,
        game: Game,
        boss_name: str,
        enemies: list,
        on_complete: Callable | None = None,
    ) -> None:
        super().__init__(game)
        self.boss_name = boss_name
        self.enemies = enemies
        self.on_complete = on_complete

        self.phase = self.PHASE_DARKNESS
        self.phase_timer = 0.0
        self.total_timer = 0.0

        # Art reveal state
        self.art_lines = BOSS_CUTSCENE_ART.get(boss_name, [])
        self.art_chars_revealed = 0
        self.art_reveal_speed = 80  # chars per second

        # Title card state
        self.title_scale = 0.0  # 0 to 1 for slam effect
        self.shake_x = 0.0
        self.shake_y = 0.0

        # Lore text state
        self.lore_text = ""
        self.lore_chars_revealed = 0
        self.lore_speed = 35  # chars per second

        # Particle embers
        self._embers: list[dict] = []

    def on_enter(self) -> None:
        # Get lore text from narrative data
        nm = getattr(self.game, "narrative_manager", None)
        if nm:
            intro = nm.get_boss_intro(self.boss_name)
            if intro:
                # Combine all text pages into one lore block
                texts = [p.get("text", "") for p in intro if p.get("type") == "text"]
                self.lore_text = " ".join(texts)

        if not self.lore_text:
            from data.narrative import BOSS_INTRO_MESSAGES

            lines = BOSS_INTRO_MESSAGES.get(self.boss_name, [])
            self.lore_text = " ".join(lines)

        # Start boss music
        sound = getattr(self.game, "sound", None)
        if sound:
            sound.play_music("boss.wav", loop=True)

    def handle_input(self, key: str) -> None:
        if self.phase == self.PHASE_READY:
            self._start_fight()
        elif self.phase == self.PHASE_LORE:
            # Skip lore text
            self.lore_chars_revealed = len(self.lore_text)
            self.phase = self.PHASE_READY
            self.phase_timer = 0.0
            # Stop narration
            sound = getattr(self.game, "sound", None)
            if sound and hasattr(sound, "stop_speaking"):
                sound.stop_speaking()
        elif self.phase == self.PHASE_ART_REVEAL:
            # Skip art reveal
            total_chars = sum(len(line) for line in self.art_lines)
            self.art_chars_revealed = total_chars
        elif self.phase == self.PHASE_TITLE:
            self.title_scale = 1.0
        elif self.phase == self.PHASE_DARKNESS:
            self.phase_timer = 3.0  # Skip ahead

    def _start_fight(self) -> None:
        from states.combat_state import CombatState

        if self.on_complete:
            self.on_complete()
        else:
            self.game.state_manager.replace(
                CombatState(self.game, self.enemies)
            )

    def update(self, dt: float) -> None:
        self.total_timer += dt
        self.phase_timer += dt

        # Spawn embers
        if random.random() < dt * 10:
            self._embers.append({
                "x": random.uniform(0, 1280),
                "y": 720 + 5,
                "vx": random.uniform(-10, 10),
                "vy": random.uniform(-50, -15),
                "life": random.uniform(2.0, 4.0),
                "max_life": random.uniform(2.0, 4.0),
            })

        # Tick embers
        alive = []
        for e in self._embers:
            e["x"] += e["vx"] * dt
            e["y"] += e["vy"] * dt
            e["life"] -= dt
            if e["life"] > 0:
                alive.append(e)
        self._embers = alive

        # Phase transitions
        if self.phase == self.PHASE_DARKNESS:
            if self.phase_timer > 3.0:
                self.phase = self.PHASE_ART_REVEAL
                self.phase_timer = 0.0
        elif self.phase == self.PHASE_ART_REVEAL:
            self.art_chars_revealed += int(self.art_reveal_speed * dt)
            total_chars = sum(len(line) for line in self.art_lines)
            if self.art_chars_revealed >= total_chars:
                self.art_chars_revealed = total_chars
                if self.phase_timer > 1.0:  # Pause after reveal
                    self.phase = self.PHASE_TITLE
                    self.phase_timer = 0.0
        elif self.phase == self.PHASE_TITLE:
            self.title_scale = min(1.0, self.phase_timer / 0.3)  # Quick slam
            if self.phase_timer < 0.5:
                # Screen shake
                intensity = (0.5 - self.phase_timer) * 10
                self.shake_x = random.uniform(-intensity, intensity)
                self.shake_y = random.uniform(-intensity, intensity)
            else:
                self.shake_x = 0
                self.shake_y = 0
            if self.phase_timer > 2.0:
                self.phase = self.PHASE_LORE
                self.phase_timer = 0.0
                # Start voice narration
                sound = getattr(self.game, "sound", None)
                if sound and hasattr(sound, "speak"):
                    sound.speak(self.lore_text)
        elif self.phase == self.PHASE_LORE:
            self.lore_chars_revealed = int(self.phase_timer * self.lore_speed)
            if self.lore_chars_revealed >= len(self.lore_text):
                self.lore_chars_revealed = len(self.lore_text)
                if self.phase_timer > len(self.lore_text) / self.lore_speed + 1.5:
                    self.phase = self.PHASE_READY
                    self.phase_timer = 0.0

    # -- Rich terminal render (fallback) -----------------------------------

    def render(self) -> RenderableType:
        from rich.align import Align
        from rich.panel import Panel
        from rich.text import Text

        text = Text()
        text.append(f"\n\n  {self.boss_name}\n", style="bold bright_red")
        subtitle = BOSS_SUBTITLES.get(self.boss_name, "")
        if subtitle:
            text.append(f"  {subtitle}\n\n", style="dim bright_yellow")
        if self.phase == self.PHASE_READY:
            text.append("  Press any key to fight...\n", style="blink bold")

        return Align.center(
            Panel(text, border_style="bright_red", title="[bold red]BOSS[/bold red]"),
            vertical="middle",
        )

    # -- Pygame render -----------------------------------------------------

    def render_pygame(self, screen, font, renderer) -> None:
        import pygame
        from pygame_ui.colors import get_rgb

        w, h = screen.get_size()
        cx = w // 2
        t = self.total_timer

        # Apply screen shake
        shake_offset = (int(self.shake_x), int(self.shake_y))

        # Dark red-tinted background
        screen.fill((8, 2, 2))

        # Animated gradient
        for y_band in range(0, h, 2):
            progress = y_band / h
            noise = math.sin(t * 0.5 + progress * 3.0) * 0.2
            r = int(max(0, min(30, 12 + 15 * progress + 10 * noise)))
            g = int(max(0, min(8, 2 + 3 * progress)))
            b = int(max(0, min(8, 2 + 3 * progress)))
            pygame.draw.line(screen, (r, g, b), (0, y_band), (w, y_band))

        # Draw embers
        for e in self._embers:
            alpha = max(0.0, min(1.0, e["life"] / e["max_life"]))
            r = max(0, min(255, int(255 * alpha)))
            g = max(0, min(255, int(80 * alpha)))
            b = max(0, min(255, int(20 * alpha)))
            px = max(0, min(w - 1, int(e["x"])))
            py = max(0, min(h - 1, int(e["y"])))
            pygame.draw.circle(screen, (r, g, b), (px, py), 2)

        if self.phase == self.PHASE_DARKNESS:
            # Rumbling approach text
            approach = BOSS_APPROACH_TEXT.get(self.boss_name, "Something stirs...")
            alpha = min(1.0, self.phase_timer / 2.0)
            if self.phase_timer > 2.5:
                alpha = max(0.0, 1.0 - (self.phase_timer - 2.5) / 0.5)
            r = int(150 * alpha)
            g = int(80 * alpha)
            b = int(60 * alpha)
            surf = font.render_text(approach, (r, g, b))
            screen.blit(surf, (cx - surf.get_width() // 2 + shake_offset[0],
                                h // 2 - font.char_height // 2 + shake_offset[1]))

        elif self.phase == self.PHASE_ART_REVEAL:
            # Draw art character by character with red glow
            art_y = h // 2 - len(self.art_lines) * font.char_height // 2
            chars_drawn = 0
            for line_idx, line in enumerate(self.art_lines):
                line_x = cx - len(line) * font.char_width // 2
                for ci, ch in enumerate(line):
                    if chars_drawn >= self.art_chars_revealed:
                        break
                    chars_drawn += 1
                    if ch == " ":
                        continue
                    # Color: recently revealed chars glow brighter
                    age = self.art_chars_revealed - chars_drawn
                    if age < 5:
                        glow = 1.0
                    elif age < 20:
                        glow = 0.7
                    else:
                        glow = 0.4 + 0.1 * math.sin(t * 2.0 + ci * 0.1)
                    r = int(min(255, 200 * glow + 55))
                    g = int(60 * glow)
                    b = int(30 * glow)
                    screen.blit(
                        font.render_glyph(ch, (r, g, b)),
                        (line_x + ci * font.char_width + shake_offset[0],
                         art_y + line_idx * font.char_height + shake_offset[1]),
                    )
                if chars_drawn >= self.art_chars_revealed:
                    break

        elif self.phase == self.PHASE_TITLE:
            # Boss art (fully revealed, dimmed)
            art_y = 40
            for line_idx, line in enumerate(self.art_lines):
                line_x = cx - len(line) * font.char_width // 2
                for ci, ch in enumerate(line):
                    if ch != " ":
                        screen.blit(
                            font.render_glyph(ch, (100, 30, 20)),
                            (line_x + ci * font.char_width + shake_offset[0],
                             art_y + line_idx * font.char_height + shake_offset[1]),
                        )

            # Title card — name slams in
            if self.title_scale > 0:
                # Boss name
                name_text = self.boss_name.upper()
                # Scale effect: expand from center
                name_surf = font.render_text(name_text, (255, 50, 30))
                name_y = h // 2 + 40
                screen.blit(name_surf,
                            (cx - name_surf.get_width() // 2 + shake_offset[0],
                             name_y + shake_offset[1]))

                # Subtitle
                if self.title_scale > 0.5:
                    subtitle = BOSS_SUBTITLES.get(self.boss_name, "")
                    sub_alpha = min(1.0, (self.title_scale - 0.5) * 2)
                    r = int(180 * sub_alpha)
                    g = int(140 * sub_alpha)
                    b = int(50 * sub_alpha)
                    sub_surf = font.render_text(subtitle, (r, g, b))
                    screen.blit(sub_surf,
                                (cx - sub_surf.get_width() // 2,
                                 name_y + font.char_height * 2))

                # Decorative line
                line_w = int(400 * self.title_scale)
                pygame.draw.line(
                    screen, (150, 40, 20),
                    (cx - line_w // 2, name_y - 8 + shake_offset[1]),
                    (cx + line_w // 2, name_y - 8 + shake_offset[1]), 2,
                )
                pygame.draw.line(
                    screen, (150, 40, 20),
                    (cx - line_w // 2, name_y + font.char_height + 4 + shake_offset[1]),
                    (cx + line_w // 2, name_y + font.char_height + 4 + shake_offset[1]), 2,
                )

        elif self.phase in (self.PHASE_LORE, self.PHASE_READY):
            # Boss art at top, dimmed
            art_y = 20
            for line_idx, line in enumerate(self.art_lines):
                line_x = cx - len(line) * font.char_width // 2
                for ci, ch in enumerate(line):
                    if ch != " ":
                        glow = 0.3 + 0.1 * math.sin(t * 1.5 + ci * 0.2)
                        screen.blit(
                            font.render_glyph(ch, (int(120 * glow), int(30 * glow), int(15 * glow))),
                            (line_x + ci * font.char_width, art_y + line_idx * font.char_height),
                        )

            # Boss name + subtitle
            name_surf = font.render_text(self.boss_name.upper(), (180, 40, 25))
            name_y = art_y + len(self.art_lines) * font.char_height + 10
            screen.blit(name_surf, (cx - name_surf.get_width() // 2, name_y))

            subtitle = BOSS_SUBTITLES.get(self.boss_name, "")
            sub_surf = font.render_text(subtitle, (120, 100, 40))
            screen.blit(sub_surf, (cx - sub_surf.get_width() // 2, name_y + font.char_height + 2))

            # Lore text (word-wrapped, typewriter)
            lore_y = name_y + font.char_height * 3 + 10
            margin = 100
            max_chars = (w - margin * 2) // font.char_width

            visible_text = self.lore_text[:self.lore_chars_revealed]
            words = visible_text.split()
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
                line_surf = font.render_text(line, (170, 150, 130))
                screen.blit(line_surf, (margin, lore_y))
                lore_y += font.char_height

            if self.phase == self.PHASE_READY:
                # "PREPARE FOR BATTLE" pulsing
                pulse = 0.5 + 0.5 * math.sin(t * 4.0)
                r = int(255 * pulse)
                g = int(80 * pulse)
                b = int(30 * pulse)
                ready_surf = font.render_text("P R E P A R E   F O R   B A T T L E", (r, g, b))
                screen.blit(ready_surf, (cx - ready_surf.get_width() // 2, h - 80))

                hint = font.render_text("Press any key...", (60, 50, 40))
                screen.blit(hint, (cx - hint.get_width() // 2, h - 40))

        # Vignette overlay (darkened edges)
        vignette = pygame.Surface((w, h), pygame.SRCALPHA)
        for edge_y in range(40):
            alpha = int(180 * (1 - edge_y / 40))
            pygame.draw.line(vignette, (0, 0, 0, alpha), (0, edge_y), (w, edge_y))
            pygame.draw.line(vignette, (0, 0, 0, alpha), (0, h - 1 - edge_y), (w, h - 1 - edge_y))
        screen.blit(vignette, (0, 0))
