import time
import math
import random
from dataclasses import dataclass, field
from rich.text import Text


@dataclass
class Animation:
    """Base animation that ticks each frame."""
    duration: float  # seconds
    elapsed: float = 0.0
    finished: bool = False

    def tick(self, dt: float) -> None:
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.finished = True

    def get_progress(self) -> float:
        """Returns 0.0 to 1.0"""
        return min(1.0, self.elapsed / self.duration) if self.duration > 0 else 1.0


@dataclass
class FlashAnimation(Animation):
    """Flash a color on text (damage/heal indicator)."""
    color: str = "bright_red"
    original_style: str = ""

    def get_style(self) -> str:
        """Returns style to apply. Alternates between flash color and original."""
        progress = self.get_progress()
        # Flash 3 times during the animation
        phase = int(progress * 6) % 2
        if phase == 0 and not self.finished:
            return f"bold {self.color}"
        return self.original_style


@dataclass
class ShakeAnimation(Animation):
    """Screen shake effect - returns x,y offset."""
    intensity: int = 2

    def get_offset(self) -> tuple[int, int]:
        if self.finished:
            return (0, 0)
        progress = self.get_progress()
        # Decay intensity over time
        current_intensity = int(self.intensity * (1.0 - progress))
        if current_intensity <= 0:
            return (0, 0)
        return (random.randint(-current_intensity, current_intensity),
                random.randint(-current_intensity, current_intensity))


@dataclass
class TypewriterAnimation(Animation):
    """Reveals text character by character."""
    full_text: str = ""
    chars_per_second: float = 30.0

    def get_visible_text(self) -> str:
        chars = int(self.elapsed * self.chars_per_second)
        return self.full_text[:chars]

    def is_complete(self) -> bool:
        return len(self.get_visible_text()) >= len(self.full_text)

    def skip(self) -> None:
        """Skip to end of typewriter effect"""
        self.elapsed = self.duration


@dataclass
class FadeAnimation(Animation):
    """Color fade transition."""
    from_color: str = "bright_white"
    to_color: str = "dim grey30"

    def get_style(self) -> str:
        progress = self.get_progress()
        if progress < 0.5:
            return self.from_color
        return self.to_color


@dataclass
class PulseAnimation(Animation):
    """Pulsing glow effect for selections/highlights."""
    color_a: str = "bright_white"
    color_b: str = "bright_yellow"
    pulse_speed: float = 2.0  # pulses per second

    def get_style(self) -> str:
        phase = math.sin(self.elapsed * self.pulse_speed * math.pi)
        if phase > 0:
            return f"bold {self.color_a}"
        return f"bold {self.color_b}"


@dataclass
class FloatingTextAnimation(Animation):
    """Text that floats upward (damage numbers, heal amounts)."""
    text: str = ""
    color: str = "bright_red"
    start_x: int = 0
    start_y: int = 0

    def get_position(self) -> tuple[int, int]:
        """Returns current (x, y) position - floats upward"""
        progress = self.get_progress()
        y_offset = int(progress * 3)  # float up 3 rows
        return (self.start_x, self.start_y - y_offset)

    def get_styled_text(self) -> Text:
        progress = self.get_progress()
        style = f"bold {self.color}" if progress < 0.7 else f"dim {self.color}"
        return Text(self.text, style=style)


class AnimationManager:
    """Manages all active animations."""
    def __init__(self):
        self.animations: list[Animation] = []
        self.floating_texts: list[FloatingTextAnimation] = []

    def add(self, animation: Animation) -> None:
        if isinstance(animation, FloatingTextAnimation):
            self.floating_texts.append(animation)
        else:
            self.animations.append(animation)

    def tick(self, dt: float) -> None:
        """Update all animations, remove finished ones."""
        for anim in self.animations:
            anim.tick(dt)
        for ft in self.floating_texts:
            ft.tick(dt)

        self.animations = [a for a in self.animations if not a.finished]
        self.floating_texts = [ft for ft in self.floating_texts if not ft.finished]

    def has_active(self) -> bool:
        return bool(self.animations) or bool(self.floating_texts)

    def get_active_flash(self) -> FlashAnimation | None:
        for a in self.animations:
            if isinstance(a, FlashAnimation):
                return a
        return None

    def get_active_shake(self) -> ShakeAnimation | None:
        for a in self.animations:
            if isinstance(a, ShakeAnimation):
                return a
        return None

    def get_active_typewriter(self) -> TypewriterAnimation | None:
        for a in self.animations:
            if isinstance(a, TypewriterAnimation):
                return a
        return None

    def clear(self) -> None:
        self.animations.clear()
        self.floating_texts.clear()
