import random
import math
from dataclasses import dataclass, field
from rich.text import Text


@dataclass
class Particle:
    x: float
    y: float
    vx: float  # velocity
    vy: float
    char: str
    color: str
    life: float  # seconds remaining
    max_life: float = 0.0

    def __post_init__(self):
        if self.max_life == 0:
            self.max_life = self.life

    def tick(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 2.0 * dt  # gravity
        self.life -= dt

    def is_alive(self) -> bool:
        return self.life > 0


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def tick(self, dt: float) -> None:
        for p in self.particles:
            p.tick(dt)
        self.particles = [p for p in self.particles if p.is_alive()]

    def emit_burst(self, x: int, y: int, count: int = 10,
                   chars: str = "*+\u00b7.\u2726\u2727", color: str = "bright_yellow",
                   speed: float = 5.0, lifetime: float = 0.5) -> None:
        """Emit a burst of particles in all directions"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(speed * 0.5, speed)
            char = random.choice(chars)
            self.particles.append(Particle(
                x=float(x), y=float(y),
                vx=math.cos(angle) * spd,
                vy=math.sin(angle) * spd - 2.0,  # bias upward
                char=char, color=color,
                life=random.uniform(lifetime * 0.5, lifetime)
            ))

    def emit_damage(self, x: int, y: int) -> None:
        """Red damage burst"""
        self.emit_burst(x, y, count=8, chars="*\u00d7\u2726!", color="bright_red", speed=4.0)

    def emit_heal(self, x: int, y: int) -> None:
        """Green healing sparkles"""
        self.emit_burst(x, y, count=6, chars="+\u2726\u2665", color="bright_green", speed=3.0, lifetime=0.8)

    def emit_magic(self, x: int, y: int, color: str = "bright_blue") -> None:
        """Magic spell particles"""
        self.emit_burst(x, y, count=12, chars="\u2726\u2727\u25c6\u25c7\u2605\u2606", color=color, speed=6.0, lifetime=0.6)

    def emit_death(self, x: int, y: int) -> None:
        """Death/vanishing effect"""
        self.emit_burst(x, y, count=15, chars="\u2591\u2592\u2593\u00b7", color="dim grey50", speed=3.0, lifetime=1.0)

    def emit_gold(self, x: int, y: int) -> None:
        """Gold pickup sparkles"""
        self.emit_burst(x, y, count=5, chars="$\u00a2\u2726", color="bright_yellow", speed=2.0, lifetime=0.4)

    def emit_level_up(self, x: int, y: int) -> None:
        """Level up celebration"""
        for color in ["bright_yellow", "bright_cyan", "bright_magenta"]:
            self.emit_burst(x, y, count=8, chars="\u2605\u2726\u2727\u25c6\u2666", color=color, speed=7.0, lifetime=1.0)

    def render_to_text(self, width: int, height: int, offset_x: int = 0, offset_y: int = 0) -> dict[tuple[int, int], tuple[str, str]]:
        """Render particles to a dict of (x,y) -> (char, style) for overlaying on other renders"""
        result = {}
        for p in self.particles:
            px = int(p.x) - offset_x
            py = int(p.y) - offset_y
            if 0 <= px < width and 0 <= py < height:
                # Fade out as life decreases
                life_pct = p.life / p.max_life if p.max_life > 0 else 0
                style = f"bold {p.color}" if life_pct > 0.5 else p.color
                result[(px, py)] = (p.char, style)
        return result

    def has_particles(self) -> bool:
        return len(self.particles) > 0
