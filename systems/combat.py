"""Turn-based combat system for SonahRPG."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from systems.status_effects import (
    StatusEffect,
    absorb_damage,
    apply_buff,
    apply_effect_tick,
    create_status_effect,
    is_crowd_controlled,
    remove_buff,
)

if TYPE_CHECKING:
    from engine.game import Game
    from entities.enemy import Enemy
    from entities.player import Player


class CombatSystem:
    def __init__(self, game: Game) -> None:
        self.game = game
        self.turn_order: list = []  # entities sorted by initiative
        self.current_turn: int = 0
        self.round_number: int = 0
        self.combat_active: bool = False
        self.enemies: list[Enemy] = []
        self.player: Player | None = None

    # ------------------------------------------------------------------
    # Combat lifecycle
    # ------------------------------------------------------------------

    def start_combat(self, player: Player, enemies: list[Enemy]) -> None:
        """Initialize combat: set combatants, roll initiative, sort turn order."""
        self.player = player
        self.enemies = list(enemies)
        self.combat_active = True
        self.round_number = 1
        self.current_turn = 0
        self._roll_initiative()

    def _roll_initiative(self) -> None:
        """Roll d20 + initiative modifier for all combatants, sort descending."""
        combatants = [self.player] + self.enemies
        rolls: list[tuple[object, int]] = []
        for c in combatants:
            roll = random.randint(1, 20) + c.initiative
            rolls.append((c, roll))
        # Sort descending by roll; ties broken randomly (unstable sort is fine)
        rolls.sort(key=lambda x: x[1], reverse=True)
        self.turn_order = [c for c, _ in rolls]

    def get_current_entity(self) -> object | None:
        """Return whose turn it is."""
        if not self.turn_order:
            return None
        return self.turn_order[self.current_turn % len(self.turn_order)]

    def is_player_turn(self) -> bool:
        """Check whether it is the player's turn."""
        return self.get_current_entity() is self.player

    def advance_turn(self) -> None:
        """Move to next living combatant, incrementing round if we wrap."""
        # Prune dead entities
        self.turn_order = [e for e in self.turn_order if e.is_alive()]
        if not self.turn_order:
            return
        self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        if self.current_turn == 0:
            self.round_number += 1
            # Tick player cooldowns and status effects at the start of a new round
            if self.player and self.player.is_alive():
                self.player.tick_cooldowns()

    # ------------------------------------------------------------------
    # Player actions
    # ------------------------------------------------------------------

    def player_attack(self, target_index: int) -> dict:
        """Player basic attack against enemy at *target_index*.

        Returns dict with keys: hit, damage, critical, killed, message
        """
        if target_index < 0 or target_index >= len(self.enemies):
            return {
                "hit": False,
                "damage": 0,
                "critical": False,
                "killed": False,
                "message": "Invalid target.",
            }

        target = self.enemies[target_index]
        if not target.is_alive():
            return {
                "hit": False,
                "damage": 0,
                "critical": False,
                "killed": False,
                "message": f"{target.name} is already dead.",
            }

        # Hit check: d20 + player.attack/5 vs target dodge_chance
        hit_roll = random.randint(1, 20) + self.player.attack // 5
        dodge_threshold = target.dodge_chance
        if hit_roll <= dodge_threshold // 2:
            return {
                "hit": False,
                "damage": 0,
                "critical": False,
                "killed": False,
                "message": f"{target.name} dodges your attack!",
            }

        # Damage calculation
        base_damage = self.player.attack - target.defense // 2 + random.randint(-3, 3)
        damage = max(1, base_damage)

        # Critical hit check
        critical = False
        crit_roll = random.randint(1, 100)
        if crit_roll <= self.player.crit_chance:
            damage *= 2
            critical = True

        # Run through shield absorption on target
        damage = absorb_damage(target, damage)
        actual = target.take_damage(damage)
        killed = not target.is_alive()

        if critical:
            msg = f"CRITICAL HIT! You strike {target.name} for {actual} damage!"
        else:
            msg = f"You hit {target.name} for {actual} damage."
        if killed:
            msg += f" {target.name} is slain!"

        return {
            "hit": True,
            "damage": actual,
            "critical": critical,
            "killed": killed,
            "message": msg,
        }

    def player_use_skill(self, skill_name: str, target_index: int | None = None) -> dict:
        """Player uses a skill.

        Returns dict with keys: success, damage, heal, effect, message, targets_hit
        """
        from data.classes import CLASSES

        player = self.player
        can_use, reason = player.can_use_skill(skill_name)
        if not can_use:
            return {
                "success": False,
                "damage": 0,
                "heal": 0,
                "effect": None,
                "message": reason,
                "targets_hit": [],
            }

        # Look up skill data
        cls_def = CLASSES.get(player.player_class)
        skill_data = None
        if cls_def:
            for s in cls_def.skills:
                if s["name"] == skill_name:
                    skill_data = s
                    break
        if skill_data is None:
            return {
                "success": False,
                "damage": 0,
                "heal": 0,
                "effect": None,
                "message": "Skill data not found.",
                "targets_hit": [],
            }

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

        total_damage = 0
        total_heal = 0
        targets_hit: list[str] = []
        messages: list[str] = []

        # Determine base spell/skill damage
        # Use primary stat for damage scaling
        primary_stat = cls_def.primary_stat if cls_def else "STR"
        stat_value = getattr(player.stats, primary_stat, 10)
        base_damage = int((player.attack + stat_value) * multiplier) + random.randint(-2, 2)
        base_damage = max(0, base_damage)

        # ---- Self-targeted skills (heals, buffs, shields) ----
        if target_type == "self":
            if effect_name == "heal":
                # Heal based on WIS + INT
                heal_amount = int((player.stats.WIS + player.stats.INT) * 0.8) + player.level * 3
                actual_heal = player.heal(heal_amount)
                total_heal = actual_heal
                messages.append(f"You heal yourself for {actual_heal} HP.")
                targets_hit.append(player.name)
            elif effect_name == "heal_over_time":
                se = create_status_effect("regen", 3)
                se.value = int(player.stats.WIS * 0.5) + player.level * 2
                self.apply_status_effect(player, se)
                messages.append(f"You gain regeneration ({se.value} HP/turn for 3 turns).")
                targets_hit.append(player.name)
            elif effect_name == "shield":
                shield_val = 15 + player.level * 3 + player.stats.CON
                se = create_status_effect("shield", 3)
                se.value = shield_val
                self.apply_status_effect(player, se)
                messages.append(f"You gain a shield absorbing {shield_val} damage.")
                targets_hit.append(player.name)
            elif effect_name == "cleanse":
                removed_count = self._cleanse_negative_effects(player)
                messages.append(f"You cleanse {removed_count} negative effect(s).")
                targets_hit.append(player.name)
            elif effect_name == "revive":
                # Grants undying for a few turns
                se = create_status_effect("shield", 5)
                se.value = player.max_hp // 2
                self.apply_status_effect(player, se)
                messages.append(f"You prepare a resurrection shield ({se.value} HP).")
                targets_hit.append(player.name)
            elif effect_name == "undying":
                # Undying rage / guardian angel — stored as a special status
                se = StatusEffect(
                    name="undying",
                    duration=3,
                    effect_type="buff",
                    value=1,
                    stat=None,
                    icon="!",
                    color="bright_red",
                )
                self.apply_status_effect(player, se)
                messages.append("You refuse to die! Undying for 3 turns.")
                targets_hit.append(player.name)
            elif effect_name == "stealth":
                se = StatusEffect(
                    name="stealth",
                    duration=2,
                    effect_type="buff",
                    value=0,
                    stat=None,
                    icon="~",
                    color="dim",
                )
                self.apply_status_effect(player, se)
                messages.append("You vanish into the shadows.")
                targets_hit.append(player.name)
            elif effect_name == "extra_turn":
                # Time Warp — we grant the player an extra turn by inserting
                # them into the turn order again immediately after current position
                idx = self.current_turn
                if idx < len(self.turn_order):
                    self.turn_order.insert(idx + 1, player)
                messages.append("Time bends! You gain an extra turn.")
                targets_hit.append(player.name)
            elif effect_name == "magic_immune":
                se = StatusEffect(
                    name="magic_immune",
                    duration=2,
                    effect_type="buff",
                    value=0,
                    stat=None,
                    icon="*",
                    color="bright_magenta",
                )
                self.apply_status_effect(player, se)
                messages.append("You are immune to magic for 2 turns.")
                targets_hit.append(player.name)
            elif effect_name == "damage_reduction":
                se = create_status_effect("buff_defense", 3)
                se.value = 10
                self.apply_status_effect(player, se)
                messages.append("You gain +10 Defense for 3 turns.")
                targets_hit.append(player.name)
            elif effect_name == "buff_all":
                for buff_name in ("buff_str", "buff_dex", "buff_int", "buff_defense"):
                    se = create_status_effect(buff_name, 3)
                    self.apply_status_effect(player, se)
                messages.append("All stats boosted for 3 turns!")
                targets_hit.append(player.name)
            elif effect_name in (
                "buff_str", "buff_def", "buff_int", "buff_dex", "buff_dodge",
            ):
                mapped = effect_name
                if mapped == "buff_def":
                    mapped = "buff_defense"
                se = create_status_effect(mapped, 3)
                self.apply_status_effect(player, se)
                messages.append(f"You gain {mapped.replace('buff_', '').upper()} buff for 3 turns.")
                targets_hit.append(player.name)
            elif effect_name == "taunt":
                # Taunt is self-targeted but conceptually affects all enemies.
                # We just mark a note; enemy AI would check for taunt.
                se = StatusEffect(
                    name="taunt",
                    duration=2,
                    effect_type="buff",
                    value=0,
                    stat=None,
                    icon="!",
                    color="red",
                )
                self.apply_status_effect(player, se)
                messages.append("You taunt all enemies, forcing them to attack you!")
                targets_hit.append(player.name)
            elif effect_name == "frenzy":
                # Frenzy: attack twice but lower defense
                se = create_status_effect("weaken", 2)
                se.stat = "defense"
                se.value = -3
                self.apply_status_effect(player, se)
                # Perform two attacks on the target
                if target_index is not None and 0 <= target_index < len(self.enemies):
                    t = self.enemies[target_index]
                    for _ in range(2):
                        if t.is_alive():
                            dmg = max(1, int(player.attack * multiplier) - t.defense // 2 + random.randint(-2, 2))
                            dmg = absorb_damage(t, dmg)
                            actual = t.take_damage(dmg)
                            total_damage += actual
                            targets_hit.append(t.name)
                    messages.append(f"Frenzy! You strike {t.name} twice for {total_damage} total damage!")
                    if not t.is_alive():
                        messages.append(f"{t.name} is slain!")
                else:
                    messages.append("Frenzy activated! Defense lowered.")
            else:
                # Generic self-buff fallback
                messages.append(f"You use {skill_name}.")
                targets_hit.append(player.name)

        # ---- Single-target offensive skills ----
        elif target_type == "single":
            if target_index is None:
                # Default to first alive enemy
                target_index = self._first_alive_enemy_index()
            if target_index is None or target_index < 0 or target_index >= len(self.enemies):
                return {
                    "success": False,
                    "damage": 0,
                    "heal": 0,
                    "effect": None,
                    "message": "No valid target.",
                    "targets_hit": [],
                }
            target = self.enemies[target_index]
            if not target.is_alive():
                return {
                    "success": False,
                    "damage": 0,
                    "heal": 0,
                    "effect": None,
                    "message": f"{target.name} is already dead.",
                    "targets_hit": [],
                }

            damage = max(1, base_damage - target.defense // 2)

            # Executioner's Blow: bonus damage to wounded foes (< 50% HP)
            if skill_name == "Executioner's Blow" and target.current_hp < target.max_hp * 0.5:
                damage = int(damage * 1.5)

            # Assassinate: bonus damage to wounded foes (< 30% HP)
            if skill_name == "Assassinate" and target.current_hp < target.max_hp * 0.3:
                damage = int(damage * 1.8)

            # Crit guaranteed from Ambush
            critical = False
            if effect_name == "crit_guaranteed":
                damage *= 2
                critical = True
            else:
                crit_roll = random.randint(1, 100)
                if crit_roll <= player.crit_chance:
                    damage *= 2
                    critical = True

            # Apply shield absorption on target
            damage = absorb_damage(target, damage)
            actual = target.take_damage(damage)
            total_damage = actual
            targets_hit.append(target.name)

            crit_text = " (CRITICAL!)" if critical else ""
            messages.append(
                f"{skill_name} hits {target.name} for {actual} damage{crit_text}."
            )

            # Apply status effect to target
            if effect_name and effect_name not in ("crit_guaranteed",):
                self._apply_offensive_effect(target, effect_name, messages)

            # Life steal
            if effect_name == "life_steal":
                stolen = actual // 3
                actual_heal = player.heal(stolen)
                total_heal = actual_heal
                messages.append(f"You drain {actual_heal} HP from {target.name}.")

            if not target.is_alive():
                messages.append(f"{target.name} is slain!")

        # ---- AoE skills ----
        elif target_type == "all_enemies":
            alive_enemies = [e for e in self.enemies if e.is_alive()]
            if not alive_enemies:
                return {
                    "success": False,
                    "damage": 0,
                    "heal": 0,
                    "effect": None,
                    "message": "No enemies alive.",
                    "targets_hit": [],
                }
            for target in alive_enemies:
                damage = max(1, base_damage - target.defense // 2 + random.randint(-1, 1))
                # Crit per target
                crit_roll = random.randint(1, 100)
                critical = crit_roll <= player.crit_chance
                if critical:
                    damage *= 2
                damage = absorb_damage(target, damage)
                actual = target.take_damage(damage)
                total_damage += actual
                targets_hit.append(target.name)
                crit_text = " (CRIT!)" if critical else ""
                messages.append(f"  {target.name} takes {actual} damage{crit_text}.")
                # Apply effect
                if effect_name and effect_name not in ("crit_guaranteed",):
                    self._apply_offensive_effect(target, effect_name, messages)
                if not target.is_alive():
                    messages.append(f"  {target.name} is slain!")

            messages.insert(0, f"{skill_name} hits {len(alive_enemies)} enemies for {total_damage} total damage!")

        return {
            "success": True,
            "damage": total_damage,
            "heal": total_heal,
            "effect": effect_name,
            "message": "\n".join(messages),
            "targets_hit": targets_hit,
        }

    # ------------------------------------------------------------------
    # Enemy actions
    # ------------------------------------------------------------------

    def enemy_turn(self, enemy: Enemy) -> dict:
        """Execute enemy AI turn.

        Returns dict with keys: action, damage, message
        """
        if not enemy.is_alive():
            return {"action": "dead", "damage": 0, "message": f"{enemy.name} is dead."}

        # Process status effects at the start of the enemy's turn
        effect_messages = self.process_status_effects(enemy)

        # Check if stunned/frozen
        if is_crowd_controlled(enemy):
            msg = f"{enemy.name} is incapacitated and cannot act!"
            if effect_messages:
                msg = "\n".join(effect_messages) + "\n" + msg
            return {"action": "stunned", "damage": 0, "message": msg}

        player = self.player
        if not player or not player.is_alive():
            return {"action": "none", "damage": 0, "message": ""}

        player_hp_pct = player.current_hp / max(player.max_hp, 1)
        action = enemy.choose_action(player_hp_pct)

        messages = list(effect_messages)

        if action["type"] == "attack":
            # Basic attack: d20 + enemy.attack/5 vs player dodge_chance
            hit_roll = random.randint(1, 20) + enemy.attack // 5
            if hit_roll <= player.dodge_chance // 2:
                messages.append(f"You dodge {enemy.name}'s attack!")
                return {
                    "action": "attack",
                    "damage": 0,
                    "message": "\n".join(messages),
                }

            base_damage = enemy.attack - player.defense // 2 + random.randint(-3, 3)
            damage = max(1, base_damage)

            # Enemy crit (flat 5% unless modified)
            crit_chance = getattr(enemy, "crit_chance", 5)
            critical = random.randint(1, 100) <= crit_chance
            if critical:
                damage *= 2

            # Check for undying status on player
            damage = absorb_damage(player, damage)
            actual = player.take_damage(damage)

            # If player would die but has undying, keep them at 1 HP
            if not player.is_alive():
                undying_found = False
                for se in list(getattr(player, "status_effects", [])):
                    se_name = se.name if isinstance(se, StatusEffect) else se.get("name", "")
                    if se_name == "undying":
                        player.alive = True
                        player.current_hp = 1
                        # Remove the undying effect
                        player.status_effects.remove(se)
                        undying_found = True
                        messages.append(f"Undying triggers! {player.name} survives with 1 HP!")
                        break

            crit_text = " (CRITICAL!)" if critical else ""
            messages.append(
                f"{enemy.name} attacks you for {actual} damage{crit_text}."
            )
            if not player.is_alive():
                messages.append("You have been defeated!")

            return {
                "action": "attack",
                "damage": actual,
                "message": "\n".join(messages),
            }

        elif action["type"] == "skill":
            skill_name = action.get("name", "Unknown Ability")
            # Enemy skills: use a simplified formula
            damage = max(1, enemy.attack + random.randint(-2, 4))
            damage = absorb_damage(player, damage)
            actual = player.take_damage(damage)

            messages.append(
                f"{enemy.name} uses {skill_name} dealing {actual} damage!"
            )

            # Some enemy abilities apply status effects
            lower = skill_name.lower()
            if "poison" in lower or "venom" in lower or "infect" in lower:
                self._apply_offensive_effect(player, "poison", messages)
            elif "stun" in lower or "bash" in lower or "paralyze" in lower:
                self._apply_offensive_effect(player, "stun", messages)
            elif "fire" in lower or "burn" in lower or "flame" in lower:
                self._apply_offensive_effect(player, "burn", messages)
            elif "slow" in lower or "cripple" in lower or "frost" in lower or "freeze" in lower:
                self._apply_offensive_effect(player, "slow", messages)
            elif "drain" in lower or "life" in lower or "absorb" in lower:
                stolen = actual // 3
                healed = enemy.heal(stolen)
                messages.append(f"{enemy.name} drains {healed} HP from you.")
            elif "heal" in lower or "regenerate" in lower:
                heal_amt = enemy.max_hp // 5
                healed = enemy.heal(heal_amt)
                messages.append(f"{enemy.name} heals for {healed} HP.")
            elif "roar" in lower or "cry" in lower or "wail" in lower:
                self._apply_offensive_effect(player, "weaken", messages)

            if not player.is_alive():
                # Check undying
                undying_found = False
                for se in list(getattr(player, "status_effects", [])):
                    se_name = se.name if isinstance(se, StatusEffect) else se.get("name", "")
                    if se_name == "undying":
                        player.alive = True
                        player.current_hp = 1
                        player.status_effects.remove(se)
                        undying_found = True
                        messages.append(f"Undying triggers! {player.name} survives with 1 HP!")
                        break
                if not undying_found:
                    messages.append("You have been defeated!")

            return {
                "action": "skill",
                "damage": actual,
                "message": "\n".join(messages),
            }

        return {"action": "none", "damage": 0, "message": ""}

    # ------------------------------------------------------------------
    # Combat end checks
    # ------------------------------------------------------------------

    def check_combat_end(self) -> str | None:
        """Check if combat is over.

        Returns 'victory' if all enemies dead, 'defeat' if player dead, None if ongoing.
        """
        if self.player and not self.player.is_alive():
            self.combat_active = False
            return "defeat"
        if all(not e.is_alive() for e in self.enemies):
            self.combat_active = False
            return "victory"
        return None

    def get_combat_rewards(self) -> dict:
        """Calculate total XP, gold, and loot drops from defeated enemies.

        Returns: {xp: int, gold: int, items: list[dict]}
        """
        total_xp = 0
        total_gold = 0
        items: list[dict] = []

        for enemy in self.enemies:
            if not enemy.is_alive():
                total_xp += enemy.xp_reward
                total_gold += enemy.gold_reward

                # Roll loot table
                for loot_entry in enemy.loot_table:
                    chance = loot_entry.get("chance", 0.0)
                    if random.random() < chance:
                        item_type = loot_entry.get("item_type", "potion")
                        rarity = loot_entry.get("rarity", "common")
                        # Generate a simple item dict
                        item = self._generate_simple_loot(
                            item_type, enemy.level, rarity
                        )
                        if item:
                            items.append(item)

        return {"xp": total_xp, "gold": total_gold, "items": items}

    # ------------------------------------------------------------------
    # Status effect management
    # ------------------------------------------------------------------

    def apply_status_effect(self, target: object, effect: StatusEffect | str, duration: int = 3) -> None:
        """Apply a status effect to a target entity.

        Accepts either a StatusEffect instance or a string name.
        """
        if isinstance(effect, str):
            effect = create_status_effect(effect, duration)

        effects_list = getattr(target, "status_effects", None)
        if effects_list is None:
            target.status_effects = []
            effects_list = target.status_effects

        # Replace existing effect of same name with new one (refresh duration)
        for i, existing in enumerate(effects_list):
            existing_name = ""
            if isinstance(existing, StatusEffect):
                existing_name = existing.name
            elif isinstance(existing, dict):
                existing_name = existing.get("name", "")
            if existing_name == effect.name:
                # Remove old buff before applying new one
                if isinstance(existing, StatusEffect):
                    remove_buff(target, existing)
                effects_list[i] = effect
                apply_buff(target, effect)
                return

        effects_list.append(effect)
        apply_buff(target, effect)

    def process_status_effects(self, entity: object) -> list[str]:
        """Process start-of-turn status effects. Returns list of log messages.

        Handles: poison/bleed/burn (DoT), regen (HoT), stun/freeze (CC),
        shield (info only), and ticks down durations.
        """
        messages: list[str] = []
        effects = getattr(entity, "status_effects", [])
        if not effects:
            return messages

        to_remove: list[int] = []
        for i, se in enumerate(effects):
            if isinstance(se, StatusEffect):
                # Apply tick
                _, msg = apply_effect_tick(entity, se)
                if msg:
                    messages.append(msg)
                # Decrement duration
                se.duration -= 1
                if se.duration <= 0:
                    to_remove.append(i)
            elif isinstance(se, dict):
                # Legacy dict-style effects from player.use_item()
                name = se.get("name", "")
                se["duration"] = se.get("duration", 0) - 1
                if name in ("poison", "bleed", "burn"):
                    dmg_val = se.get("value", 3)
                    actual = entity.take_damage(dmg_val)
                    messages.append(f"{entity.name} takes {actual} {name} damage.")
                if se["duration"] <= 0:
                    to_remove.append(i)

        # Remove expired effects in reverse order
        for idx in reversed(to_remove):
            expired = effects[idx]
            if isinstance(expired, StatusEffect):
                remove_buff(entity, expired)
            effects.pop(idx)

        return messages

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _first_alive_enemy_index(self) -> int | None:
        """Return index of first living enemy, or None."""
        for i, e in enumerate(self.enemies):
            if e.is_alive():
                return i
        return None

    def _apply_offensive_effect(
        self, target: object, effect_name: str, messages: list[str]
    ) -> None:
        """Apply an offensive status effect to a target with a chance-based roll."""
        # Map skill effect names to status effect names
        effect_map = {
            "poison": "poison",
            "bleed": "bleed",
            "burn": "burn",
            "stun": "stun",
            "freeze": "freeze",
            "slow": "slow",
            "weaken": "weaken",
            "silence": "stun",  # treat silence as a 1-turn stun for simplicity
            "blind": "weaken",  # treat blind as attack debuff
            "holy_damage": None,  # no extra effect, just flavor
            "marked": "weaken",  # marked = take more damage, approximate as weaken
            "plague": "poison",  # plague = strong poison
        }
        mapped = effect_map.get(effect_name, effect_name)
        if mapped is None:
            return

        # 70% chance to apply the effect (except stun which is 50%)
        apply_chance = 0.5 if mapped in ("stun", "freeze") else 0.7
        if random.random() < apply_chance:
            duration = 2 if mapped in ("stun", "freeze") else 3
            se = create_status_effect(mapped, duration)
            self.apply_status_effect(target, se)
            messages.append(f"  {target.name} is afflicted with {mapped}!")

    def _cleanse_negative_effects(self, entity: object) -> int:
        """Remove all negative status effects from entity. Returns count removed."""
        effects = getattr(entity, "status_effects", [])
        negative_types = {"dot", "cc", "debuff"}
        removed = 0
        remaining = []
        for se in effects:
            is_negative = False
            if isinstance(se, StatusEffect):
                is_negative = se.effect_type in negative_types
            elif isinstance(se, dict):
                is_negative = se.get("negative", False) or se.get("name", "") in (
                    "poison", "bleed", "burn", "stun", "freeze", "slow", "weaken",
                )
            if is_negative:
                if isinstance(se, StatusEffect):
                    remove_buff(entity, se)
                removed += 1
            else:
                remaining.append(se)
        entity.status_effects = remaining
        return removed

    def _generate_simple_loot(
        self, item_type: str, level: int, rarity: str
    ) -> dict | None:
        """Generate a simple loot item dict for combat rewards.

        This is a lightweight version; the full LootSystem provides richer generation.
        """
        rarity_mult = {
            "common": 1.0,
            "uncommon": 1.3,
            "rare": 1.6,
            "epic": 2.0,
            "legendary": 3.0,
        }
        mult = rarity_mult.get(rarity, 1.0)

        if item_type == "potion":
            return {
                "name": f"Health Potion Lv.{level}",
                "type": "consumable",
                "effect": "heal",
                "value": int(20 + level * 8 * mult),
                "rarity": rarity,
                "description": "Restores HP when consumed.",
                "gold_value": int(10 * mult),
            }
        elif item_type == "scroll":
            return {
                "name": f"Scroll of Power Lv.{level}",
                "type": "consumable",
                "effect": "buff_str",
                "value": int(3 + level * mult),
                "duration": 3,
                "rarity": rarity,
                "description": "Temporarily boosts STR.",
                "gold_value": int(15 * mult),
            }
        elif item_type == "junk":
            return {
                "name": "Rat Tail",
                "type": "junk",
                "rarity": "common",
                "description": "A grimy tail. Might be worth a few coins.",
                "gold_value": random.randint(1, 5),
            }
        elif item_type in ("weapon", "armor", "helmet", "boots", "ring", "amulet"):
            # Defer to loot system if available; otherwise simple fallback
            stat_bonus = int((2 + level) * mult)
            slot = item_type if item_type in (
                "weapon", "armor", "helmet", "boots", "ring", "amulet",
            ) else "weapon"
            if slot == "weapon":
                main_stat = "attack"
            elif slot in ("armor", "helmet", "boots"):
                main_stat = "defense"
            elif slot == "ring":
                main_stat = "crit_chance"
            else:
                main_stat = "hp_bonus"

            rarity_names = {
                "common": "",
                "uncommon": "Fine ",
                "rare": "Superior ",
                "epic": "Masterwork ",
                "legendary": "Legendary ",
            }
            base_names = {
                "weapon": "Blade",
                "armor": "Chainmail",
                "helmet": "Helm",
                "boots": "Greaves",
                "ring": "Ring",
                "amulet": "Amulet",
            }
            prefix = rarity_names.get(rarity, "")
            base = base_names.get(slot, "Item")

            return {
                "name": f"{prefix}{base} Lv.{level}",
                "type": "equipment",
                "slot": slot,
                "rarity": rarity,
                "level": level,
                "bonuses": {main_stat: stat_bonus},
                "description": f"A {rarity} {base.lower()} suitable for level {level}.",
                "gold_value": int(stat_bonus * 5 * mult),
            }
        return None
