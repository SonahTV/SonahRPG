"""Status effect definitions and processing logic for SonahRPG."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StatusEffect:
    name: str
    duration: int  # turns remaining
    effect_type: str  # "dot", "buff", "debuff", "cc", "hot", "absorb"
    value: int  # damage per tick, stat bonus, etc.
    stat: str | None = None  # which stat to modify for buffs
    icon: str = ""  # single char for display
    color: str = "white"


STATUS_EFFECTS: dict[str, dict] = {
    "poison": {
        "effect_type": "dot",
        "value": 5,
        "icon": "\u2620",
        "color": "green",
        "description": "Takes poison damage each turn",
    },
    "bleed": {
        "effect_type": "dot",
        "value": 3,
        "icon": "\U0001fa78",
        "color": "red",
        "description": "Bleeding, takes damage each turn",
    },
    "burn": {
        "effect_type": "dot",
        "value": 7,
        "icon": "\U0001f525",
        "color": "bright_red",
        "description": "Burning, takes fire damage each turn",
    },
    "stun": {
        "effect_type": "cc",
        "value": 0,
        "icon": "\u26a1",
        "color": "yellow",
        "description": "Stunned, cannot act",
    },
    "freeze": {
        "effect_type": "cc",
        "value": 0,
        "icon": "\u2744",
        "color": "cyan",
        "description": "Frozen, cannot act",
    },
    "regen": {
        "effect_type": "hot",
        "value": 8,
        "icon": "\U0001f49a",
        "color": "green",
        "description": "Regenerating health each turn",
    },
    "shield": {
        "effect_type": "absorb",
        "value": 20,
        "icon": "\U0001f6e1",
        "color": "blue",
        "description": "Absorbs incoming damage",
    },
    "buff_str": {
        "effect_type": "buff",
        "value": 5,
        "stat": "STR",
        "icon": "\u2b06",
        "color": "red",
        "description": "+5 STR",
    },
    "buff_dex": {
        "effect_type": "buff",
        "value": 5,
        "stat": "DEX",
        "icon": "\u2b06",
        "color": "green",
        "description": "+5 DEX",
    },
    "buff_int": {
        "effect_type": "buff",
        "value": 5,
        "stat": "INT",
        "icon": "\u2b06",
        "color": "blue",
        "description": "+5 INT",
    },
    "buff_defense": {
        "effect_type": "buff",
        "value": 5,
        "stat": "defense",
        "icon": "\u2b06",
        "color": "grey70",
        "description": "+5 Defense",
    },
    "buff_dodge": {
        "effect_type": "buff",
        "value": 10,
        "stat": "dodge_chance",
        "icon": "\u2b06",
        "color": "green",
        "description": "+10 Dodge",
    },
    "weaken": {
        "effect_type": "debuff",
        "value": -5,
        "stat": "attack",
        "icon": "\u2b07",
        "color": "dim red",
        "description": "-5 Attack",
    },
    "slow": {
        "effect_type": "debuff",
        "value": -5,
        "stat": "initiative",
        "icon": "\u2b07",
        "color": "dim blue",
        "description": "-5 Initiative",
    },
}


def create_status_effect(name: str, duration: int) -> StatusEffect:
    """Create a StatusEffect instance from the template."""
    if name not in STATUS_EFFECTS:
        return StatusEffect(name=name, duration=duration, effect_type="buff", value=0)
    template = STATUS_EFFECTS[name]
    filtered = {k: v for k, v in template.items() if k != "description"}
    return StatusEffect(name=name, duration=duration, **filtered)


def apply_effect_tick(entity: object, effect: StatusEffect) -> tuple[int, str]:
    """Apply one tick of a status effect. Returns (damage_or_heal, message).

    Positive return means damage dealt; negative means healing done.
    """
    if effect.effect_type == "dot":
        dmg = entity.take_damage(effect.value)
        return dmg, f"{entity.name} takes {dmg} {effect.name} damage"
    elif effect.effect_type == "hot":
        heal = entity.heal(effect.value)
        return -heal, f"{entity.name} regenerates {heal} HP"
    elif effect.effect_type == "cc":
        return 0, f"{entity.name} is {effect.name}ned!"
    elif effect.effect_type == "absorb":
        # Shield doesn't tick damage — it absorbs on hit. Nothing to do here.
        return 0, f"{entity.name} is shielded ({effect.value} remaining)"
    elif effect.effect_type in ("buff", "debuff"):
        # Stat modifiers are applied once when the effect starts and removed
        # when it expires.  The tick just serves as a reminder message.
        direction = "boosted" if effect.effect_type == "buff" else "reduced"
        stat_label = effect.stat or "stats"
        return 0, f"{entity.name}'s {stat_label} is {direction} ({effect.name})"
    return 0, ""


def is_crowd_controlled(entity: object) -> bool:
    """Check if entity has any CC status effects (stun, freeze)."""
    for se in getattr(entity, "status_effects", []):
        if isinstance(se, dict):
            if se.get("name") in ("stun", "freeze"):
                return True
        elif isinstance(se, StatusEffect):
            if se.effect_type == "cc":
                return True
    return False


def get_shield_amount(entity: object) -> int:
    """Return total shield absorption remaining on an entity."""
    total = 0
    for se in getattr(entity, "status_effects", []):
        if isinstance(se, StatusEffect) and se.effect_type == "absorb":
            total += se.value
        elif isinstance(se, dict) and se.get("name") == "shield":
            total += se.get("value", 0)
    return total


def absorb_damage(entity: object, damage: int) -> int:
    """Run damage through shield effects first, return remaining damage."""
    remaining = damage
    effects = getattr(entity, "status_effects", [])
    to_remove = []
    for i, se in enumerate(effects):
        if remaining <= 0:
            break
        is_shield = False
        shield_val = 0
        if isinstance(se, StatusEffect) and se.effect_type == "absorb":
            is_shield = True
            shield_val = se.value
        elif isinstance(se, dict) and se.get("name") == "shield":
            is_shield = True
            shield_val = se.get("value", 0)

        if is_shield:
            absorbed = min(remaining, shield_val)
            remaining -= absorbed
            new_val = shield_val - absorbed
            if new_val <= 0:
                to_remove.append(i)
            else:
                if isinstance(se, StatusEffect):
                    se.value = new_val
                else:
                    se["value"] = new_val

    # Remove fully consumed shields in reverse order to preserve indices
    for idx in reversed(to_remove):
        effects.pop(idx)
    return remaining


def apply_buff(entity: object, effect: StatusEffect) -> None:
    """Apply a buff/debuff stat modifier to an entity."""
    if effect.stat and effect.effect_type in ("buff", "debuff"):
        stat_name = effect.stat
        # Handle base stats (STR, DEX, etc.) via the stats dataclass
        if hasattr(entity, "stats") and hasattr(entity.stats, stat_name):
            current = getattr(entity.stats, stat_name)
            setattr(entity.stats, stat_name, current + effect.value)
            entity.compute_derived_stats()
        elif hasattr(entity, stat_name):
            current = getattr(entity, stat_name)
            setattr(entity, stat_name, current + effect.value)


def remove_buff(entity: object, effect: StatusEffect) -> None:
    """Remove a buff/debuff stat modifier from an entity."""
    if effect.stat and effect.effect_type in ("buff", "debuff"):
        stat_name = effect.stat
        if hasattr(entity, "stats") and hasattr(entity.stats, stat_name):
            current = getattr(entity.stats, stat_name)
            setattr(entity.stats, stat_name, current - effect.value)
            entity.compute_derived_stats()
        elif hasattr(entity, stat_name):
            current = getattr(entity, stat_name)
            setattr(entity, stat_name, current - effect.value)
