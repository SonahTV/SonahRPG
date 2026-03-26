"""Main Game class — the central orchestrator for SonahRPG (terminal mode)."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.live import Live
from rich.text import Text

from engine.base_game import BaseGame
from engine.config import FPS, GAME_TITLE
from engine.input_handler import InputHandler

if TYPE_CHECKING:
    from engine.state import GameState


class Game(BaseGame):
    """Top-level game object for terminal (Rich) rendering.

    Inherits shared game logic from BaseGame. Adds the Rich console
    and msvcrt-based input handler. The ``run()`` method drives the
    main loop at ~20 fps using Rich Live for flicker-free rendering.
    """

    def __init__(self) -> None:
        super().__init__()
        self.input_handler = InputHandler()
        self._console = Console()

    # -- main loop -----------------------------------------------------------

    def run(self) -> None:
        """Run the game loop inside a Rich Live context.

        Flow per frame:
        1. Read queued key presses and forward to the active state.
        2. Call ``update(dt)`` on the active state.
        3. Call ``render()`` on the active state and push the result
           to the Live display.
        4. Sleep to maintain the target frame rate.
        """
        self.running = True
        self.input_handler.start()
        frame_time = 1.0 / FPS

        try:
            with Live(
                Text(f"Starting {GAME_TITLE}..."),
                console=self._console,
                auto_refresh=False,
                screen=True,
            ) as live:
                last_time = time.perf_counter()

                while self.running:
                    now = time.perf_counter()
                    dt = now - last_time
                    last_time = now

                    state = self.state_manager.current
                    if state is None:
                        # Nothing on the stack — exit gracefully.
                        self.running = False
                        break

                    # 1. Drain input queue
                    while True:
                        key = self.input_handler.get_key()
                        if key is None:
                            break
                        state.handle_input(key)

                    # 2. Update
                    state.update(dt)

                    # 3. Render
                    renderable = state.render()
                    live.update(renderable, refresh=True)

                    # 4. Frame pacing
                    elapsed = time.perf_counter() - now
                    sleep_for = frame_time - elapsed
                    if sleep_for > 0:
                        time.sleep(sleep_for)

        except KeyboardInterrupt:
            pass  # Ctrl-C is a normal exit path
        except Exception as exc:
            self._console.print_exception()
        finally:
            self.input_handler.stop()
            self.state_manager.clear()
