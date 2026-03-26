"""Stack-based game state machine.

States are pushed/popped like a stack.  Only the top state receives
input, update, and render calls.  When a state is pushed on top of
another, the lower state gets ``on_pause``; when the upper state is
popped, the lower state gets ``on_resume``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game


class GameState(ABC):
    """Base class for every game state (menu, exploration, combat, etc.)."""

    def __init__(self, game: Game) -> None:
        self.game = game

    @abstractmethod
    def handle_input(self, key: str) -> None:
        """Process a single key press."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance state logic by *dt* seconds."""

    @abstractmethod
    def render(self) -> RenderableType:
        """Return a Rich renderable representing the current frame."""

    def render_pygame(self, screen: Any, font: Any, renderer: Any) -> None:
        """Render to a Pygame surface. Override for Pygame support.

        Default implementation does nothing — states that haven't been
        ported to Pygame will show a fallback message in the game loop.
        """

    # -- lifecycle hooks (optional overrides) --------------------------------

    def on_enter(self) -> None:
        """Called when this state is first pushed onto the stack."""

    def on_exit(self) -> None:
        """Called when this state is popped off the stack."""

    def on_pause(self) -> None:
        """Called when another state is pushed on top of this one."""

    def on_resume(self) -> None:
        """Called when the state above this one is popped."""


class StateManager:
    """Manages an ordered stack of ``GameState`` instances."""

    def __init__(self) -> None:
        self._stack: list[GameState] = []

    @property
    def current(self) -> GameState | None:
        """The topmost state, or ``None`` if the stack is empty."""
        return self._stack[-1] if self._stack else None

    def push(self, state: GameState) -> None:
        """Pause the current state (if any), push *state*, and enter it."""
        if self._stack:
            self._stack[-1].on_pause()
        self._stack.append(state)
        state.on_enter()

    def pop(self) -> GameState | None:
        """Exit and remove the topmost state.  Resume the one below it.

        Returns the popped state, or ``None`` if the stack was empty.
        """
        if not self._stack:
            return None
        state = self._stack.pop()
        state.on_exit()
        if self._stack:
            self._stack[-1].on_resume()
        return state

    def replace(self, state: GameState) -> None:
        """Pop the current state and push *state* in one operation."""
        if self._stack:
            old = self._stack.pop()
            old.on_exit()
        self._stack.append(state)
        state.on_enter()

    def clear(self) -> None:
        """Pop every state off the stack (calling ``on_exit`` for each)."""
        while self._stack:
            self._stack.pop().on_exit()
