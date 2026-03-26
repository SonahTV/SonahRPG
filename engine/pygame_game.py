"""Pygame-based game loop for SonahRPG windowed mode."""

from __future__ import annotations

import time
from typing import Any

import pygame

from engine.base_game import BaseGame
from engine.config import FPS, GAME_TITLE
from engine.pygame_input import PygameInputHandler
from engine.sound import SoundManager
from pygame_ui.font_manager import FontManager
from pygame_ui.pg_renderer import PygameRenderer

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


class PygameGame(BaseGame):
    """Pygame-based game — renders to a window instead of terminal.

    Inherits all game logic from BaseGame. Provides a Pygame main loop
    with event processing, rendering, and frame pacing.
    """

    def __init__(self) -> None:
        super().__init__()
        self.input_handler = PygameInputHandler()
        self.font_manager = FontManager()
        self.renderer = PygameRenderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.sound = SoundManager()
        self.screen: pygame.Surface | None = None

    def run(self) -> None:
        """Main Pygame game loop.

        1. Initialize Pygame, create window
        2. Each frame: process events -> drain input -> update state -> render
        3. Clean up on exit
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)

        # Initialize subsystems
        self.font_manager.init()
        self.sound.init()

        self.running = True
        clock = pygame.time.Clock()
        last_time = time.perf_counter()
        _last_state_name = ""

        try:
            while self.running:
                now = time.perf_counter()
                dt = now - last_time
                last_time = now

                # 1. Process Pygame events
                if not self.input_handler.process_events():
                    self.running = False
                    break

                # 1b. Poll held keys for smooth movement
                self.input_handler.poll_held_keys(dt)

                state = self.state_manager.current
                if state is None:
                    self.running = False
                    break

                # 2. Drain input queue
                while True:
                    key = self.input_handler.get_key()
                    if key is None:
                        break
                    state.handle_input(key)

                # 2b. Auto-switch music when state changes
                state_name = type(state).__name__
                if state_name != _last_state_name:
                    _last_state_name = state_name
                    self.sound.play_music_for_state(state_name)

                # 3. Update
                state.update(dt)

                # 4. Render
                # Try Pygame render method first, fall back to blank screen
                if hasattr(state, "render_pygame"):
                    state.render_pygame(self.screen, self.font_manager, self.renderer)
                else:
                    # Fallback: render a message that this state hasn't been ported
                    self.screen.fill((0, 0, 0))
                    fallback_text = self.font_manager.render_text(
                        f"[{type(state).__name__} - no Pygame renderer]",
                        (200, 200, 200),
                    )
                    self.screen.blit(fallback_text, (20, 20))

                pygame.display.flip()

                # 5. Frame pacing
                clock.tick(FPS)

        except KeyboardInterrupt:
            pass
        except Exception as exc:
            print(f"Error: {exc}")
            import traceback

            traceback.print_exc()
        finally:
            self.sound.cleanup()
            pygame.quit()
            self.state_manager.clear()
