from dataclasses import dataclass
from rich.text import Text
from rich.panel import Panel
from rich.align import Align


@dataclass
class Transition:
    duration: float
    elapsed: float = 0.0
    finished: bool = False

    def tick(self, dt: float) -> None:
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.finished = True

    def get_progress(self) -> float:
        return min(1.0, self.elapsed / self.duration) if self.duration > 0 else 1.0


class FadeTransition(Transition):
    """Fade to black and back."""
    def __init__(self, duration: float = 0.5):
        super().__init__(duration=duration)

    def render(self, width: int, height: int) -> Text:
        progress = self.get_progress()
        text = Text()
        # First half: darken, second half: lighten
        if progress < 0.5:
            # Getting darker
            intensity = int((progress * 2) * 5)
            chars = ["\u2591", "\u2592", "\u2593", "\u2588", "\u2588"]
            char = chars[min(intensity, len(chars) - 1)]
            style = "dim grey30"
        else:
            # Getting lighter
            intensity = int(((1.0 - progress) * 2) * 5)
            chars = ["\u2591", "\u2592", "\u2593", "\u2588", "\u2588"]
            char = chars[min(intensity, len(chars) - 1)]
            style = "dim grey50"

        for _ in range(height):
            text.append(char * width + "\n", style=style)
        return text


class WipeTransition(Transition):
    """Horizontal wipe transition."""
    def __init__(self, duration: float = 0.3, direction: str = "left"):
        super().__init__(duration=duration)
        self.direction = direction

    def render(self, width: int, height: int) -> Text:
        progress = self.get_progress()
        text = Text()
        wipe_col = int(progress * width)

        for _ in range(height):
            if self.direction == "left":
                text.append("\u2588" * wipe_col, style="black on black")
                text.append(" " * (width - wipe_col))
            else:
                text.append(" " * (width - wipe_col))
                text.append("\u2588" * wipe_col, style="black on black")
            text.append("\n")
        return text


class FlashTransition(Transition):
    """Quick white flash (for big hits, level ups)."""
    def __init__(self, duration: float = 0.15, color: str = "bright_white"):
        super().__init__(duration=duration)
        self.color = color

    def render(self, width: int, height: int) -> Text:
        progress = self.get_progress()
        text = Text()
        if progress < 0.5:
            style = f"bold {self.color} on {self.color}"
            for _ in range(height):
                text.append("\u2588" * width + "\n", style=style)
        return text


class TransitionManager:
    """Manages screen transitions."""
    def __init__(self):
        self.current: Transition | None = None

    def start(self, transition: Transition) -> None:
        self.current = transition

    def tick(self, dt: float) -> None:
        if self.current:
            self.current.tick(dt)
            if self.current.finished:
                self.current = None

    def is_active(self) -> bool:
        return self.current is not None

    def render(self, width: int, height: int) -> Text | None:
        if self.current:
            return self.current.render(width, height)
        return None
