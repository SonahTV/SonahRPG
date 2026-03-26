"""Pygame-based input handler — translates pygame.KEYDOWN to key name strings.

Supports both tap-to-move (KEYDOWN events) and hold-to-move (key.get_pressed
polling with repeat delay) for smooth exploration movement.
"""

from __future__ import annotations

import queue

import pygame


# Pygame key → string name mapping (must match msvcrt handler output)
_KEY_MAP: dict[int, str] = {
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
    pygame.K_RETURN: "enter",
    pygame.K_KP_ENTER: "enter",
    pygame.K_ESCAPE: "escape",
    pygame.K_BACKSPACE: "backspace",
    pygame.K_TAB: "tab",
    pygame.K_SPACE: "space",
    pygame.K_PERIOD: ".",
    pygame.K_COMMA: ",",
    pygame.K_GREATER: ">",
    pygame.K_LESS: "<",
    # Letters handled dynamically
}

# Movement keys that support hold-to-repeat
_MOVE_KEYS: dict[int, str] = {
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
    pygame.K_w: "w",
    pygame.K_a: "a",
    pygame.K_s: "s",
    pygame.K_d: "d",
}

# How fast held keys repeat (seconds)
_HOLD_INITIAL_DELAY = 0.18  # delay before repeating starts
_HOLD_REPEAT_RATE = 0.08    # time between repeats once held


class PygameInputHandler:
    """Processes Pygame events and queues key names.

    Supports hold-to-move: when a movement key is held down, it repeats
    at a comfortable rate after a short initial delay.
    """

    def __init__(self) -> None:
        self._queue: queue.Queue[str] = queue.Queue()
        self._held_keys: dict[int, float] = {}  # key → time until next repeat
        self._held_active: dict[int, bool] = {}  # key → past initial delay?

    def process_events(self) -> bool:
        """Process all pending Pygame events.

        Returns False if a QUIT event was received (window closed).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                key_name = self._translate_key(event)
                if key_name:
                    self._queue.put(key_name)

                # Track held movement keys
                if event.key in _MOVE_KEYS:
                    self._held_keys[event.key] = _HOLD_INITIAL_DELAY
                    self._held_active[event.key] = False

            elif event.type == pygame.KEYUP:
                self._held_keys.pop(event.key, None)
                self._held_active.pop(event.key, None)

        return True

    def poll_held_keys(self, dt: float) -> None:
        """Check for held movement keys and emit repeat events.

        Call this once per frame after process_events().
        """
        for key, timer in list(self._held_keys.items()):
            timer -= dt
            if timer <= 0:
                key_name = _MOVE_KEYS.get(key)
                if key_name:
                    self._queue.put(key_name)
                self._held_keys[key] = _HOLD_REPEAT_RATE
                self._held_active[key] = True
            else:
                self._held_keys[key] = timer

    def get_key(self) -> str | None:
        """Return the next queued key name, or None if empty."""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def _translate_key(self, event: pygame.event.Event) -> str | None:
        """Convert a pygame KEYDOWN event to a key name string."""
        # Handle shift+period = ">" for stairs
        if event.key == pygame.K_PERIOD and event.mod & pygame.KMOD_SHIFT:
            return ">"

        # Check direct mapping first
        mapped = _KEY_MAP.get(event.key)
        if mapped:
            return mapped

        # Handle printable characters
        if event.unicode and len(event.unicode) == 1:
            char = event.unicode
            if char.isprintable():
                return char.lower()

        return None

    def start(self) -> None:
        """No-op for API compatibility with terminal InputHandler."""

    def stop(self) -> None:
        """No-op for API compatibility with terminal InputHandler."""
