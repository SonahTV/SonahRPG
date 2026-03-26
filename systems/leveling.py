"""Experience and leveling system for SonahRPG."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from data.classes import CLASSES

if TYPE_CHECKING:
    from engine.game import Game
    from entities.player import Player


class LevelingSystem:
    def __init__(self, game: Game) -> None:
        self.game = game

    def award_xp(self, player: Player, amount: int) -> bool:
        """Award XP to the player and check for level up.

        Returns True if the player leveled up. Does NOT call level_up()
        here — the caller is responsible for calling process_level_up().
        """
        if amount <= 0:
            return False

        player.xp += amount
        return player.xp >= player.xp_to_next

    def process_level_up(self, player: Player) -> dict:
        """Process one or more pending level ups and return the gains.

        Handles multi-level-ups (e.g. big XP reward). Keeps calling
        level_up() until xp < xp_to_next.

        Returns dict with: level, hp_gain, mp_gain, skill_points_gained,
        new_skills_available (list of skill names newly unlocked).
        """
        old_level = player.level
        old_skill_points = player.skill_points
        total_hp = 0
        total_mp = 0

        # Process all pending level-ups
        while player.xp >= player.xp_to_next:
            gains = player.level_up()
            total_hp += gains.get("hp_gain", 0)
            total_mp += gains.get("mp_gain", 0)

        # Find skills that became available across all new levels
        cls_def = CLASSES.get(player.player_class)
        new_skills: list[str] = []
        if cls_def:
            for skill in cls_def.skills:
                if (
                    old_level < skill["level_required"] <= player.level
                    and skill["name"] not in player.known_skills
                ):
                    new_skills.append(skill["name"])

        return {
            "level": player.level,
            "hp_gain": total_hp,
            "mp_gain": total_mp,
            "skill_points_gained": player.skill_points - old_skill_points,
            "new_skills_available": new_skills,
        }

    def get_xp_for_level(self, level: int) -> int:
        """Calculate total XP needed to reach a given level.

        Formula: 100 * level^1.5 (rounded to nearest int).
        """
        if level <= 1:
            return 0
        return int(100 * math.pow(level, 1.5))

    def get_xp_progress(self, player: Player) -> float:
        """Get XP progress toward next level as a float 0.0 to 1.0."""
        if player.xp_to_next <= 0:
            return 1.0
        return min(1.0, max(0.0, player.xp / player.xp_to_next))

    def get_xp_bar(self, player: Player, width: int = 20) -> str:
        """Generate a text-based XP progress bar.

        Example: [===========.........] 55%
        """
        progress = self.get_xp_progress(player)
        filled = int(progress * width)
        empty = width - filled
        pct = int(progress * 100)
        return f"[{'=' * filled}{'.' * empty}] {pct}%"

    def calculate_combat_xp(
        self, player_level: int, enemy_levels: list[int]
    ) -> int:
        """Calculate XP for a combat encounter with level scaling.

        Enemies much lower than the player give reduced XP.
        Enemies higher than the player give bonus XP.
        """
        total = 0
        for elevel in enemy_levels:
            diff = elevel - player_level
            if diff >= 3:
                # Much harder: 50% bonus
                multiplier = 1.5
            elif diff >= 1:
                # Slightly harder: 20% bonus
                multiplier = 1.2
            elif diff >= -2:
                # Around same level: normal
                multiplier = 1.0
            elif diff >= -5:
                # Slightly lower: reduced
                multiplier = 0.5
            else:
                # Way below: minimal XP
                multiplier = 0.1

            base = int(100 * math.pow(max(1, elevel), 1.2))
            total += int(base * multiplier)

        return max(1, total)
