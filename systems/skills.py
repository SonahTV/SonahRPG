"""Skill system for SonahRPG."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from data.classes import CLASSES
from systems.status_effects import create_status_effect

if TYPE_CHECKING:
    from engine.game import Game
    from entities.player import Player


class SkillSystem:
    def __init__(self, game: Game) -> None:
        self.game = game

    def get_available_skills(self, player: Player) -> list[dict]:
        """Get all skills the player currently knows, with full data."""
        cls_def = CLASSES.get(player.player_class)
        if not cls_def:
            return []
        result: list[dict] = []
        for skill in cls_def.skills:
            if skill["name"] in player.known_skills:
                enriched = dict(skill)
                # Add cooldown status
                cd_remaining = player.skill_cooldowns.get(skill["name"], 0)
                enriched["cooldown_remaining"] = cd_remaining
                enriched["can_use"] = (
                    cd_remaining <= 0 and player.current_mp >= skill.get("mp_cost", 0)
                )
                result.append(enriched)
        return result

    def get_learnable_skills(self, player: Player) -> list[dict]:
        """Get skills the player can learn right now.

        Must meet level requirement, have skill points, and not already know it.
        """
        cls_def = CLASSES.get(player.player_class)
        if not cls_def:
            return []
        result: list[dict] = []
        for skill in cls_def.skills:
            if skill["name"] in player.known_skills:
                continue
            if skill["level_required"] > player.level:
                continue
            # Player must have skill points
            if player.skill_points <= 0:
                continue
            result.append(dict(skill))
        return result

    def learn_skill(self, player: Player, skill_name: str) -> tuple[bool, str]:
        """Learn a new skill. Returns (success, message)."""
        if skill_name in player.known_skills:
            return False, f"You already know {skill_name}."

        if player.skill_points <= 0:
            return False, "No skill points available."

        cls_def = CLASSES.get(player.player_class)
        if not cls_def:
            return False, "Class data not found."

        skill_data = None
        for s in cls_def.skills:
            if s["name"] == skill_name:
                skill_data = s
                break

        if skill_data is None:
            return False, f"Skill '{skill_name}' does not exist for {player.player_class}."

        if skill_data["level_required"] > player.level:
            return (
                False,
                f"{skill_name} requires level {skill_data['level_required']} (you are level {player.level}).",
            )

        player.known_skills.append(skill_name)
        player.skill_points -= 1
        return True, f"Learned {skill_name}! ({player.skill_points} skill points remaining)"

    def use_skill(
        self,
        player: Player,
        skill_name: str,
        target: object | None = None,
        all_enemies: list | None = None,
    ) -> dict:
        """Execute a skill. Returns a result dict.

        This is a standalone execution path (outside the CombatSystem flow).
        The CombatSystem has its own player_use_skill that handles targeting
        by index; this method works with direct entity references.
        """
        can_use, reason = player.can_use_skill(skill_name)
        if not can_use:
            return {"success": False, "message": reason, "damage": 0, "heal": 0}

        cls_def = CLASSES.get(player.player_class)
        skill_data = self.get_skill_info(player.player_class, skill_name)
        if skill_data is None:
            return {"success": False, "message": "Skill not found.", "damage": 0, "heal": 0}

        # Deduct MP
        mp_cost = skill_data.get("mp_cost", 0)
        player.current_mp = max(0, player.current_mp - mp_cost)

        # Set cooldown
        cooldown = skill_data.get("cooldown", 0)
        if cooldown > 0:
            player.skill_cooldowns[skill_name] = cooldown

        target_type = skill_data.get("target", "single")
        multiplier = skill_data.get("damage_multiplier", 1.0)
        effect_name = skill_data.get("effect")

        primary_stat = cls_def.primary_stat if cls_def else "STR"
        stat_value = getattr(player.stats, primary_stat, 10)
        base_damage = max(0, int((player.attack + stat_value) * multiplier) + random.randint(-2, 2))

        total_damage = 0
        total_heal = 0
        messages: list[str] = []
        targets_hit: list[str] = []

        # ---- Self-target ----
        if target_type == "self":
            if effect_name == "heal":
                heal_amount = int((player.stats.WIS + player.stats.INT) * 0.8) + player.level * 3
                actual = player.heal(heal_amount)
                total_heal = actual
                messages.append(f"You heal for {actual} HP.")
            elif effect_name == "heal_over_time":
                se = create_status_effect("regen", 3)
                se.value = int(player.stats.WIS * 0.5) + player.level * 2
                player.status_effects.append(se)
                messages.append(f"You gain regeneration ({se.value}/turn for 3 turns).")
            elif effect_name == "shield":
                shield_val = 15 + player.level * 3 + player.stats.CON
                se = create_status_effect("shield", 3)
                se.value = shield_val
                player.status_effects.append(se)
                messages.append(f"You gain a {shield_val}-point shield.")
            elif effect_name == "cleanse":
                neg_names = {"poison", "bleed", "burn", "stun", "freeze", "slow", "weaken"}
                removed = 0
                remaining = []
                for eff in player.status_effects:
                    n = eff.name if hasattr(eff, "name") else eff.get("name", "")
                    if n in neg_names:
                        removed += 1
                    else:
                        remaining.append(eff)
                player.status_effects = remaining
                messages.append(f"Cleansed {removed} negative effect(s).")
            elif effect_name and effect_name.startswith("buff_"):
                mapped = effect_name
                if mapped == "buff_def":
                    mapped = "buff_defense"
                se = create_status_effect(mapped, 3)
                player.status_effects.append(se)
                messages.append(f"You gain {mapped} for 3 turns.")
            elif effect_name == "buff_all":
                for buff in ("buff_str", "buff_dex", "buff_int", "buff_defense"):
                    se = create_status_effect(buff, 3)
                    player.status_effects.append(se)
                messages.append("All stats boosted for 3 turns!")
            elif effect_name == "undying":
                from systems.status_effects import StatusEffect
                se = StatusEffect(name="undying", duration=3, effect_type="buff", value=1, icon="!", color="bright_red")
                player.status_effects.append(se)
                messages.append("You refuse to die for 3 turns!")
            elif effect_name == "revive":
                se = create_status_effect("shield", 5)
                se.value = player.max_hp // 2
                player.status_effects.append(se)
                messages.append(f"Resurrection shield: {se.value} HP.")
            elif effect_name == "stealth":
                from systems.status_effects import StatusEffect
                se = StatusEffect(name="stealth", duration=2, effect_type="buff", value=0, icon="~", color="dim")
                player.status_effects.append(se)
                messages.append("You vanish into the shadows.")
            elif effect_name == "magic_immune":
                from systems.status_effects import StatusEffect
                se = StatusEffect(name="magic_immune", duration=2, effect_type="buff", value=0, icon="*", color="bright_magenta")
                player.status_effects.append(se)
                messages.append("Magic immunity for 2 turns.")
            elif effect_name == "damage_reduction":
                se = create_status_effect("buff_defense", 3)
                se.value = 10
                player.status_effects.append(se)
                messages.append("+10 Defense for 3 turns.")
            elif effect_name == "taunt":
                from systems.status_effects import StatusEffect
                se = StatusEffect(name="taunt", duration=2, effect_type="buff", value=0, icon="!", color="red")
                player.status_effects.append(se)
                messages.append("You taunt all enemies!")
            else:
                messages.append(f"You use {skill_name}.")
            targets_hit.append(player.name)

        # ---- Single target ----
        elif target_type == "single" and target is not None:
            damage = max(1, base_damage - getattr(target, "defense", 0) // 2)
            crit = random.randint(1, 100) <= player.crit_chance
            if effect_name == "crit_guaranteed":
                crit = True
            if crit:
                damage *= 2
            actual = target.take_damage(damage)
            total_damage = actual
            targets_hit.append(target.name)
            crit_txt = " (CRITICAL!)" if crit else ""
            messages.append(f"{skill_name} hits {target.name} for {actual}{crit_txt}.")
            if effect_name == "life_steal":
                stolen = actual // 3
                healed = player.heal(stolen)
                total_heal = healed
                messages.append(f"You drain {healed} HP.")
            if effect_name and effect_name not in ("crit_guaranteed", "life_steal"):
                self._try_apply_effect(target, effect_name, messages)
            if not target.is_alive():
                messages.append(f"{target.name} is slain!")

        # ---- All enemies ----
        elif target_type == "all_enemies" and all_enemies:
            alive = [e for e in all_enemies if e.is_alive()]
            for t in alive:
                damage = max(1, base_damage - t.defense // 2 + random.randint(-1, 1))
                crit = random.randint(1, 100) <= player.crit_chance
                if crit:
                    damage *= 2
                actual = t.take_damage(damage)
                total_damage += actual
                targets_hit.append(t.name)
                crit_txt = " (CRIT!)" if crit else ""
                messages.append(f"  {t.name}: {actual} damage{crit_txt}.")
                if effect_name and effect_name not in ("crit_guaranteed",):
                    self._try_apply_effect(t, effect_name, messages)
                if not t.is_alive():
                    messages.append(f"  {t.name} is slain!")
            messages.insert(0, f"{skill_name} hits {len(alive)} targets!")

        else:
            messages.append(f"You use {skill_name} but there is no valid target.")

        return {
            "success": True,
            "damage": total_damage,
            "heal": total_heal,
            "effect": effect_name,
            "message": "\n".join(messages),
            "targets_hit": targets_hit,
        }

    def get_skill_info(self, player_class: str, skill_name: str) -> dict | None:
        """Look up full skill definition from class data."""
        cls_def = CLASSES.get(player_class)
        if not cls_def:
            return None
        for s in cls_def.skills:
            if s["name"] == skill_name:
                return dict(s)
        return None

    def get_skill_tree(self, player_class: str) -> dict[str, list[dict]]:
        """Get organized skill tree grouped by branch.

        Returns: {branch_name: [skill_dicts sorted by level_required]}
        """
        cls_def = CLASSES.get(player_class)
        if not cls_def:
            return {}
        tree: dict[str, list[dict]] = {}
        for skill in cls_def.skills:
            branch = skill.get("branch", "General")
            if branch not in tree:
                tree[branch] = []
            tree[branch].append(dict(skill))
        # Sort each branch by level requirement
        for branch in tree:
            tree[branch].sort(key=lambda s: s["level_required"])
        return tree

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _try_apply_effect(
        self, target: object, effect_name: str, messages: list[str]
    ) -> None:
        """Attempt to apply a status effect to a target."""
        effect_map = {
            "poison": "poison",
            "bleed": "bleed",
            "burn": "burn",
            "stun": "stun",
            "freeze": "freeze",
            "slow": "slow",
            "weaken": "weaken",
            "silence": "stun",
            "blind": "weaken",
            "holy_damage": None,
            "marked": "weaken",
            "plague": "poison",
        }
        mapped = effect_map.get(effect_name, effect_name)
        if mapped is None:
            return

        chance = 0.5 if mapped in ("stun", "freeze") else 0.7
        if random.random() < chance:
            duration = 2 if mapped in ("stun", "freeze") else 3
            se = create_status_effect(mapped, duration)
            # Ensure target has status_effects list
            if not hasattr(target, "status_effects"):
                target.status_effects = []
            target.status_effects.append(se)
            messages.append(f"  {target.name} is afflicted with {mapped}!")
