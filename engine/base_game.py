"""Base game class with shared logic for both terminal and Pygame backends."""

from __future__ import annotations
from typing import Any
from engine.config import MAX_LOG_LINES
from engine.events import EventBus
from engine.state import StateManager


class BaseGame:
    """Shared game logic for all rendering backends.

    Subclasses must implement:
    - run() — the main loop
    - Any backend-specific initialization
    """

    def __init__(self) -> None:
        self.event_bus = EventBus()
        self.state_manager = StateManager()
        self.player: Any = None
        self.current_map: Any = None
        self.combat_log: list[str] = []
        self.running = False
        self.narrative_manager = None  # Initialized in new_game()

    def add_log(self, message: str, style: str = "") -> None:
        """Append a message to the combat log, trimming old entries."""
        if style:
            self.combat_log.append(f"[{style}]{message}[/{style}]")
        else:
            self.combat_log.append(message)
        if len(self.combat_log) > MAX_LOG_LINES:
            self.combat_log = self.combat_log[-MAX_LOG_LINES:]

    def new_game(self, player: Any) -> None:
        """Initialize a fresh game with the given player entity."""
        self.player = player
        self.combat_log.clear()
        # Initialize narrative manager
        from systems.narrative_manager import NarrativeManager
        self.narrative_manager = NarrativeManager(self)

    def start_combat(self, enemies: list) -> None:
        from engine.events import COMBAT_START
        self.event_bus.emit(COMBAT_START, enemies=enemies)
        self.add_log("Combat begins!", "bold red")

    def end_combat(self) -> None:
        from engine.events import COMBAT_END
        self.event_bus.emit(COMBAT_END)
        self.state_manager.pop()
        self.add_log("Combat has ended.", "bold green")

    def quit(self) -> None:
        self.running = False
