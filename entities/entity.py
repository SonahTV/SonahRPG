from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Stats:
    STR: int = 10
    DEX: int = 10
    INT: int = 10
    WIS: int = 10
    CON: int = 10
    CHA: int = 10

    def to_dict(self) -> dict:
        return {
            "STR": self.STR,
            "DEX": self.DEX,
            "INT": self.INT,
            "WIS": self.WIS,
            "CON": self.CON,
            "CHA": self.CHA,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Stats:
        return cls(
            STR=data.get("STR", 10),
            DEX=data.get("DEX", 10),
            INT=data.get("INT", 10),
            WIS=data.get("WIS", 10),
            CON=data.get("CON", 10),
            CHA=data.get("CHA", 10),
        )


@dataclass
class Entity:
    name: str
    x: int = 0
    y: int = 0
    stats: Stats = field(default_factory=Stats)
    level: int = 1

    # Derived stats (computed from base stats)
    max_hp: int = 0
    current_hp: int = 0
    max_mp: int = 0
    current_mp: int = 0
    attack: int = 0
    defense: int = 0
    crit_chance: int = 5  # percentage
    dodge_chance: int = 5  # percentage
    initiative: int = 0

    alive: bool = True

    def compute_derived_stats(self) -> None:
        """Calculate HP, MP, attack, defense, etc. from base stats."""
        self.max_hp = 50 + self.stats.CON * 5 + self.level * 10
        self.max_mp = 20 + self.stats.INT * 3 + self.stats.WIS * 2 + self.level * 5
        self.attack = self.stats.STR * 2 + self.level * 2
        self.defense = self.stats.CON + self.stats.DEX // 2 + self.level
        self.crit_chance = 5 + self.stats.DEX // 2
        self.dodge_chance = self.stats.DEX // 3
        self.initiative = self.stats.DEX + self.level

    def take_damage(self, amount: int) -> int:
        """Apply damage, return actual damage dealt. Handles death."""
        actual = max(0, amount)
        self.current_hp = max(0, self.current_hp - actual)
        if self.current_hp <= 0:
            self.alive = False
        return actual

    def heal(self, amount: int) -> int:
        """Heal HP, return actual amount healed."""
        actual = min(amount, self.max_hp - self.current_hp)
        self.current_hp += actual
        return actual

    def restore_mp(self, amount: int) -> int:
        """Restore MP, return actual amount restored."""
        actual = min(amount, self.max_mp - self.current_mp)
        self.current_mp += actual
        return actual

    def is_alive(self) -> bool:
        return self.alive and self.current_hp > 0

    def to_dict(self) -> dict:
        """Serialize to dict for save/load."""
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "stats": self.stats.to_dict(),
            "level": self.level,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "max_mp": self.max_mp,
            "current_mp": self.current_mp,
            "attack": self.attack,
            "defense": self.defense,
            "crit_chance": self.crit_chance,
            "dodge_chance": self.dodge_chance,
            "initiative": self.initiative,
            "alive": self.alive,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Entity:
        """Deserialize from dict."""
        entity = cls(
            name=data["name"],
            x=data.get("x", 0),
            y=data.get("y", 0),
            stats=Stats.from_dict(data.get("stats", {})),
            level=data.get("level", 1),
        )
        entity.max_hp = data.get("max_hp", 0)
        entity.current_hp = data.get("current_hp", 0)
        entity.max_mp = data.get("max_mp", 0)
        entity.current_mp = data.get("current_mp", 0)
        entity.attack = data.get("attack", 0)
        entity.defense = data.get("defense", 0)
        entity.crit_chance = data.get("crit_chance", 5)
        entity.dodge_chance = data.get("dodge_chance", 5)
        entity.initiative = data.get("initiative", 0)
        entity.alive = data.get("alive", True)
        # If derived stats are all zero, recompute them
        if entity.max_hp == 0:
            entity.compute_derived_stats()
            entity.current_hp = entity.max_hp
            entity.current_mp = entity.max_mp
        return entity
