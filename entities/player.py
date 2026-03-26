from __future__ import annotations

from dataclasses import dataclass, field

from entities.entity import Entity, Stats


@dataclass
class Equipment:
    weapon: dict | None = None
    armor: dict | None = None
    helmet: dict | None = None
    boots: dict | None = None
    ring: dict | None = None
    amulet: dict | None = None

    _SLOTS = ("weapon", "armor", "helmet", "boots", "ring", "amulet")

    def get_total_bonus(self, stat: str) -> int:
        """Sum up all equipment bonuses for a stat."""
        total = 0
        for slot_name in self._SLOTS:
            item = getattr(self, slot_name)
            if item and "bonuses" in item:
                total += item["bonuses"].get(stat, 0)
        return total

    def get_slot(self, slot_name: str) -> dict | None:
        """Get item in a slot by name."""
        if slot_name in self._SLOTS:
            return getattr(self, slot_name)
        return None

    def equip(self, item: dict) -> dict | None:
        """Equip item to its slot, return previously equipped item or None.

        The item dict must have a 'slot' key indicating which slot it goes in.
        """
        slot_name = item.get("slot", "weapon")
        if slot_name not in self._SLOTS:
            return None
        previous = getattr(self, slot_name)
        setattr(self, slot_name, item)
        return previous

    def unequip(self, slot_name: str) -> dict | None:
        """Unequip and return item from slot."""
        if slot_name not in self._SLOTS:
            return None
        item = getattr(self, slot_name)
        setattr(self, slot_name, None)
        return item

    def to_dict(self) -> dict:
        return {slot: getattr(self, slot) for slot in self._SLOTS}

    @classmethod
    def from_dict(cls, data: dict) -> Equipment:
        eq = cls()
        for slot in cls._SLOTS:
            setattr(eq, slot, data.get(slot))
        return eq


@dataclass
class Player(Entity):
    player_class: str = "Warrior"
    xp: int = 0
    xp_to_next: int = 100
    gold: int = 0
    floor: int = 1

    # Inventory
    inventory: list[dict] = field(default_factory=list)  # list of item dicts
    max_inventory: int = 20
    equipment: Equipment = field(default_factory=Equipment)

    # Skills
    known_skills: list[str] = field(default_factory=list)  # skill names
    skill_cooldowns: dict[str, int] = field(default_factory=dict)  # skill_name -> turns remaining
    skill_points: int = 0

    # Quest tracking
    active_quests: list[dict] = field(default_factory=list)
    completed_quests: list[str] = field(default_factory=list)

    # Status effects
    status_effects: list[dict] = field(default_factory=list)  # [{name, duration, effect}]

    def compute_derived_stats(self) -> None:
        """Override: include equipment bonuses."""
        super().compute_derived_stats()
        # Add equipment bonuses
        for stat in ["attack", "defense", "hp_bonus", "mp_bonus", "crit_chance", "dodge_chance"]:
            bonus = self.equipment.get_total_bonus(stat)
            if stat == "hp_bonus":
                self.max_hp += bonus
            elif stat == "mp_bonus":
                self.max_mp += bonus
            else:
                setattr(self, stat, getattr(self, stat) + bonus)

    def gain_xp(self, amount: int) -> bool:
        """Add XP, return True if leveled up."""
        self.xp += amount
        if self.xp >= self.xp_to_next:
            return True
        return False

    def level_up(self) -> dict:
        """Process level up: increase level, carry over excess xp."""
        self.xp = max(0, self.xp - self.xp_to_next)
        self.level += 1
        self.xp_to_next = int(self.xp_to_next * 1.5)
        self.skill_points += 1
        from data.classes import CLASSES
        cls_def = CLASSES.get(self.player_class)
        hp_gain = cls_def.hp_per_level if cls_def else 8
        mp_gain = cls_def.mp_per_level if cls_def else 4
        self.compute_derived_stats()
        self.current_hp = self.max_hp  # full heal on level up
        self.current_mp = self.max_mp
        return {"hp_gain": hp_gain, "mp_gain": mp_gain, "level": self.level}

    def add_item(self, item: dict) -> bool:
        """Add item to inventory, return False if full."""
        if len(self.inventory) >= self.max_inventory:
            return False
        self.inventory.append(item)
        return True

    def remove_item(self, index: int) -> dict | None:
        """Remove and return item at index."""
        if 0 <= index < len(self.inventory):
            return self.inventory.pop(index)
        return None

    def use_item(self, index: int) -> dict | None:
        """Use consumable item. Returns effect info dict or None.

        Supported item effects:
        - heal: restores HP by item's 'value'
        - restore_mp: restores MP by item's 'value'
        - buff_str / buff_def / buff_int: adds a temporary status effect
        - cure: removes all negative status effects
        """
        if index < 0 or index >= len(self.inventory):
            return None
        item = self.inventory[index]
        if item.get("type") != "consumable":
            return None

        effect = item.get("effect", "")
        value = item.get("value", 0)
        result: dict = {"item_name": item.get("name", "Unknown"), "effect": effect}

        if effect == "heal":
            actual = self.heal(value)
            result["actual"] = actual
        elif effect == "restore_mp":
            actual = self.restore_mp(value)
            result["actual"] = actual
        elif effect in ("buff_str", "buff_def", "buff_int"):
            duration = item.get("duration", 3)
            self.status_effects.append({
                "name": effect,
                "duration": duration,
                "effect": effect,
                "value": value,
            })
            result["duration"] = duration
            result["value"] = value
        elif effect == "cure":
            removed = [e for e in self.status_effects if e.get("negative", False)]
            self.status_effects = [e for e in self.status_effects if not e.get("negative", False)]
            result["removed"] = len(removed)
        else:
            result["actual"] = value

        # Consume the item
        self.inventory.pop(index)
        return result

    def learn_skill(self, skill_name: str) -> bool:
        """Learn a skill if not known and has skill points."""
        if skill_name in self.known_skills:
            return False
        if self.skill_points <= 0:
            return False
        self.known_skills.append(skill_name)
        self.skill_points -= 1
        return True

    def can_use_skill(self, skill_name: str) -> tuple[bool, str]:
        """Check if can use skill. Returns (can_use, reason)."""
        if skill_name not in self.known_skills:
            return False, "Skill not learned"

        # Look up skill data from class definition
        from data.classes import CLASSES
        cls_def = CLASSES.get(self.player_class)
        skill_data = None
        if cls_def:
            for s in cls_def.skills:
                if s["name"] == skill_name:
                    skill_data = s
                    break

        if skill_data is None:
            return False, "Skill data not found"

        # Check cooldown
        remaining = self.skill_cooldowns.get(skill_name, 0)
        if remaining > 0:
            return False, f"On cooldown ({remaining} turns)"

        # Check MP
        mp_cost = skill_data.get("mp_cost", 0)
        if self.current_mp < mp_cost:
            return False, f"Not enough MP ({self.current_mp}/{mp_cost})"

        return True, "OK"

    def tick_cooldowns(self) -> None:
        """Reduce all cooldowns by 1, remove expired ones."""
        expired = []
        for skill_name in self.skill_cooldowns:
            self.skill_cooldowns[skill_name] -= 1
            if self.skill_cooldowns[skill_name] <= 0:
                expired.append(skill_name)
        for skill_name in expired:
            del self.skill_cooldowns[skill_name]

    def tick_status_effects(self) -> list[dict]:
        """Tick status effects, return list of expired effects."""
        expired = []
        remaining = []
        for effect in self.status_effects:
            effect["duration"] -= 1
            if effect["duration"] <= 0:
                expired.append(effect)
            else:
                remaining.append(effect)
        self.status_effects = remaining
        return expired

    @classmethod
    def create(cls, name: str, player_class: str) -> Player:
        """Factory: create a new player with class-appropriate stats."""
        from data.classes import CLASSES
        class_def = CLASSES[player_class]
        player = cls(name=name, player_class=player_class)
        player.stats = Stats(**class_def.base_stats)
        # Give starting skills (level 1 skills from class)
        for skill in class_def.skills:
            if skill["level_required"] <= 1:
                player.known_skills.append(skill["name"])
        player.compute_derived_stats()
        player.current_hp = player.max_hp
        player.current_mp = player.max_mp
        player.gold = 50  # starting gold
        return player

    def to_dict(self) -> dict:
        """Full serialization including inventory, equipment, skills, quests."""
        data = super().to_dict()
        data.update({
            "player_class": self.player_class,
            "xp": self.xp,
            "xp_to_next": self.xp_to_next,
            "gold": self.gold,
            "floor": self.floor,
            "inventory": self.inventory,
            "max_inventory": self.max_inventory,
            "equipment": self.equipment.to_dict(),
            "known_skills": self.known_skills,
            "skill_cooldowns": self.skill_cooldowns,
            "skill_points": self.skill_points,
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests,
            "status_effects": self.status_effects,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Player:
        """Full deserialization."""
        player = cls(
            name=data["name"],
            x=data.get("x", 0),
            y=data.get("y", 0),
            stats=Stats.from_dict(data.get("stats", {})),
            level=data.get("level", 1),
            player_class=data.get("player_class", "Warrior"),
        )
        player.max_hp = data.get("max_hp", 0)
        player.current_hp = data.get("current_hp", 0)
        player.max_mp = data.get("max_mp", 0)
        player.current_mp = data.get("current_mp", 0)
        player.attack = data.get("attack", 0)
        player.defense = data.get("defense", 0)
        player.crit_chance = data.get("crit_chance", 5)
        player.dodge_chance = data.get("dodge_chance", 5)
        player.initiative = data.get("initiative", 0)
        player.alive = data.get("alive", True)
        player.xp = data.get("xp", 0)
        player.xp_to_next = data.get("xp_to_next", 100)
        player.gold = data.get("gold", 0)
        player.floor = data.get("floor", 1)
        player.inventory = data.get("inventory", [])
        player.max_inventory = data.get("max_inventory", 20)
        player.equipment = Equipment.from_dict(data.get("equipment", {}))
        player.known_skills = data.get("known_skills", [])
        player.skill_cooldowns = data.get("skill_cooldowns", {})
        player.skill_points = data.get("skill_points", 0)
        player.active_quests = data.get("active_quests", [])
        player.completed_quests = data.get("completed_quests", [])
        player.status_effects = data.get("status_effects", [])
        # If derived stats are zero, recompute
        if player.max_hp == 0:
            player.compute_derived_stats()
            player.current_hp = player.max_hp
            player.current_mp = player.max_mp
        return player
