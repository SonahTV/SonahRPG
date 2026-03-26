from __future__ import annotations

import random
from dataclasses import dataclass, field

from entities.entity import Entity, Stats


@dataclass
class Enemy(Entity):
    template_name: str = ""
    modifier: str | None = None
    xp_reward: int = 0
    gold_reward: int = 0
    loot_table: list[dict] = field(default_factory=list)
    abilities: list[str] = field(default_factory=list)
    ascii_art: str = ""
    flavor_text: str = ""
    is_boss: bool = False

    @classmethod
    def from_template(
        cls,
        template_name: str,
        level: int | None = None,
        modifier: str | None = None,
    ) -> Enemy:
        """Create enemy from template with optional level override and modifier."""
        from data.enemies import ENEMY_TEMPLATES, ENEMY_MODIFIERS

        template = ENEMY_TEMPLATES[template_name]

        # Determine level within range
        if level is None:
            level = random.randint(*template.level_range)

        enemy = cls(
            name=template.name,
            template_name=template_name,
            level=level,
            xp_reward=template.xp_reward + level * 5,
            gold_reward=random.randint(*template.gold_range),
            loot_table=list(template.loot_table),
            abilities=list(template.abilities),
            ascii_art=template.ascii_art,
            flavor_text=template.flavor_text,
            is_boss=getattr(template, "is_boss", False),
        )

        # Scale stats by level
        enemy.max_hp = template.base_hp + level * 8
        enemy.current_hp = enemy.max_hp
        enemy.attack = template.base_attack + level * 3
        enemy.defense = template.base_defense + level * 2

        # Apply modifier if any
        if modifier:
            mod = ENEMY_MODIFIERS.get(modifier)
            if mod:
                enemy.modifier = modifier
                enemy.name = f"{mod['prefix']} {enemy.name}"
                if "attack_mult" in mod:
                    enemy.attack = int(enemy.attack * mod["attack_mult"])
                if "defense_mult" in mod:
                    enemy.defense = int(enemy.defense * mod["defense_mult"])
                if "hp_mult" in mod:
                    enemy.max_hp = int(enemy.max_hp * mod["hp_mult"])
                    enemy.current_hp = enemy.max_hp
                if "xp_mult" in mod:
                    enemy.xp_reward = int(enemy.xp_reward * mod["xp_mult"])
                if "gold_mult" in mod:
                    enemy.gold_reward = int(enemy.gold_reward * mod["gold_mult"])

        return enemy

    def choose_action(self, player_hp_pct: float) -> dict:
        """AI: choose attack or ability based on situation.

        Returns {"type": "attack"} or {"type": "skill", "name": skill_name}.

        Heuristics:
        - If has healing ability and HP < 30%, try to heal.
        - Random chance to use special ability vs basic attack.
        - Weighted toward basic attacks so combat isn't all abilities.
        """
        hp_pct = self.current_hp / max(self.max_hp, 1)

        # Check for healing ability when low HP
        if hp_pct < 0.3:
            heal_abilities = [a for a in self.abilities if "heal" in a.lower()]
            if heal_abilities:
                return {"type": "skill", "name": random.choice(heal_abilities)}

        # No abilities? Basic attack.
        if not self.abilities:
            return {"type": "attack"}

        # 40% chance to use a special ability
        if random.random() < 0.4:
            chosen = random.choice(self.abilities)
            return {"type": "skill", "name": chosen}

        # Default to basic attack
        return {"type": "attack"}

    def to_dict(self) -> dict:
        """Serialize enemy to dict."""
        data = super().to_dict()
        data.update({
            "template_name": self.template_name,
            "modifier": self.modifier,
            "xp_reward": self.xp_reward,
            "gold_reward": self.gold_reward,
            "loot_table": self.loot_table,
            "abilities": self.abilities,
            "ascii_art": self.ascii_art,
            "flavor_text": self.flavor_text,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Enemy:
        """Deserialize enemy from dict."""
        enemy = cls(
            name=data["name"],
            x=data.get("x", 0),
            y=data.get("y", 0),
            stats=Stats.from_dict(data.get("stats", {})),
            level=data.get("level", 1),
            template_name=data.get("template_name", ""),
            modifier=data.get("modifier"),
            xp_reward=data.get("xp_reward", 0),
            gold_reward=data.get("gold_reward", 0),
            loot_table=data.get("loot_table", []),
            abilities=data.get("abilities", []),
            ascii_art=data.get("ascii_art", ""),
            flavor_text=data.get("flavor_text", ""),
        )
        enemy.max_hp = data.get("max_hp", 0)
        enemy.current_hp = data.get("current_hp", 0)
        enemy.max_mp = data.get("max_mp", 0)
        enemy.current_mp = data.get("current_mp", 0)
        enemy.attack = data.get("attack", 0)
        enemy.defense = data.get("defense", 0)
        enemy.crit_chance = data.get("crit_chance", 5)
        enemy.dodge_chance = data.get("dodge_chance", 5)
        enemy.initiative = data.get("initiative", 0)
        enemy.alive = data.get("alive", True)
        # If derived stats are zero and no template overrides, recompute
        if enemy.max_hp == 0:
            enemy.compute_derived_stats()
            enemy.current_hp = enemy.max_hp
            enemy.current_mp = enemy.max_mp
        return enemy
