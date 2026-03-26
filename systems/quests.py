"""Quest system for SonahRPG."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game import Game
    from entities.player import Player


@dataclass
class Quest:
    quest_id: str
    name: str
    description: str
    quest_type: str  # "kill", "fetch", "explore", "boss"
    objective: dict  # {target: str, count: int, current: int}
    rewards: dict  # {xp: int, gold: int, item: dict | None}
    floor: int  # which floor this quest is for
    completed: bool = False
    turned_in: bool = False

    def to_dict(self) -> dict:
        return {
            "quest_id": self.quest_id,
            "name": self.name,
            "description": self.description,
            "quest_type": self.quest_type,
            "objective": self.objective,
            "rewards": self.rewards,
            "floor": self.floor,
            "completed": self.completed,
            "turned_in": self.turned_in,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Quest:
        return cls(
            quest_id=data["quest_id"],
            name=data["name"],
            description=data["description"],
            quest_type=data["quest_type"],
            objective=data["objective"],
            rewards=data["rewards"],
            floor=data["floor"],
            completed=data.get("completed", False),
            turned_in=data.get("turned_in", False),
        )


# ======================================================================
# Quest templates for procedural generation
# ======================================================================

KILL_TARGETS_BY_FLOOR: dict[int, list[str]] = {
    1: ["Rat", "Goblin", "Skeleton", "Slime"],
    2: ["Goblin", "Skeleton", "Slime", "Rat"],
    3: ["Orc", "Spider", "Zombie", "Bat Swarm", "Goblin King"],
    4: ["Orc", "Spider", "Zombie", "Bat Swarm"],
    5: ["Orc", "Spider", "Zombie", "Bat Swarm"],
    6: ["Dark Knight", "Wraith", "Troll", "Basilisk", "Spider Queen"],
    7: ["Dark Knight", "Wraith", "Troll", "Basilisk"],
    8: ["Dark Knight", "Wraith", "Troll", "Basilisk"],
    9: ["Dark Knight", "Wraith", "Troll", "Basilisk"],
    10: ["Demon", "Dragon Whelp", "Lich Apprentice", "Bone Dragon"],
}

FETCH_ITEMS: list[str] = [
    "Ancient Scroll",
    "Dragon Scale",
    "Enchanted Gem",
    "Lost Relic",
    "Sacred Amulet",
    "Shadow Crystal",
    "Phoenix Feather",
    "Blood Ruby",
    "Void Shard",
    "Soul Fragment",
]

LOCATION_NAMES: list[str] = [
    "Forgotten Chamber",
    "Hidden Passage",
    "Ancient Vault",
    "Cursed Hall",
    "Shadow Alcove",
    "Bone Crypt",
    "Crystal Cavern",
    "Sealed Tomb",
    "Abyssal Rift",
    "Dragon's Lair",
]

BOSS_NAMES_BY_FLOOR: dict[int, list[str]] = {
    3: ["Goblin King"],
    6: ["Spider Queen"],
    10: ["Bone Dragon"],
    15: ["Demon Lord"],
}


def _get_floor_targets(floor: int) -> list[str]:
    """Get kill targets for a floor, falling back to nearest defined tier."""
    if floor in KILL_TARGETS_BY_FLOOR:
        return KILL_TARGETS_BY_FLOOR[floor]
    # Find the nearest lower defined floor
    defined = sorted(KILL_TARGETS_BY_FLOOR.keys())
    best = defined[0]
    for f in defined:
        if f <= floor:
            best = f
    return KILL_TARGETS_BY_FLOOR[best]


class QuestSystem:
    def __init__(self, game: Game) -> None:
        self.game = game
        self._quest_counter: int = 0

    def _next_id(self) -> str:
        self._quest_counter += 1
        return f"quest_{self._quest_counter:04d}"

    def generate_quest(self, floor: int) -> Quest:
        """Generate a random quest appropriate for the floor level."""
        # Check if this is a boss floor
        boss_floors = BOSS_NAMES_BY_FLOOR
        if floor in boss_floors:
            # 50% chance of a boss quest on boss floors
            if random.random() < 0.5:
                return self._generate_boss_quest(floor)

        # Weight quest types
        roll = random.random()
        if roll < 0.45:
            return self._generate_kill_quest(floor)
        elif roll < 0.75:
            return self._generate_fetch_quest(floor)
        else:
            return self._generate_explore_quest(floor)

    def update_quest_progress(
        self, player: Player, event_type: str, **data
    ) -> list[str]:
        """Check all active quests for progress updates.

        Called when enemies are killed, items picked up, rooms explored, etc.
        Returns list of notification messages.

        event_type values: "kill", "pickup", "explore", "boss_kill"
        data keys: target (str), item (str), location (str), count (int)
        """
        messages: list[str] = []
        quests = self._get_quest_objects(player)

        for quest in quests:
            if quest.completed or quest.turned_in:
                continue

            if quest.quest_type == "kill" and event_type in ("kill", "boss_kill"):
                target_name = data.get("target", "")
                if target_name == quest.objective.get("target"):
                    quest.objective["current"] = quest.objective.get("current", 0) + data.get("count", 1)
                    remaining = quest.objective["count"] - quest.objective["current"]
                    if remaining <= 0:
                        quest.completed = True
                        messages.append(
                            f"[bright_green]Quest Complete:[/bright_green] {quest.name}!"
                        )
                    else:
                        messages.append(
                            f"Quest progress: {quest.name} — "
                            f"{quest.objective['current']}/{quest.objective['count']}"
                        )

            elif quest.quest_type == "fetch" and event_type == "pickup":
                item_name = data.get("item", "")
                if item_name == quest.objective.get("target"):
                    quest.objective["current"] = quest.objective.get("current", 0) + data.get("count", 1)
                    if quest.objective["current"] >= quest.objective["count"]:
                        quest.completed = True
                        messages.append(
                            f"[bright_green]Quest Complete:[/bright_green] {quest.name}!"
                        )
                    else:
                        messages.append(
                            f"Quest progress: {quest.name} — "
                            f"{quest.objective['current']}/{quest.objective['count']}"
                        )

            elif quest.quest_type == "explore" and event_type == "explore":
                location_name = data.get("location", "")
                # Explore quests just need visiting rooms — any room counts
                quest.objective["current"] = quest.objective.get("current", 0) + 1
                if quest.objective["current"] >= quest.objective["count"]:
                    quest.completed = True
                    messages.append(
                        f"[bright_green]Quest Complete:[/bright_green] {quest.name}!"
                    )
                else:
                    messages.append(
                        f"Quest progress: {quest.name} — "
                        f"{quest.objective['current']}/{quest.objective['count']} rooms explored"
                    )

            elif quest.quest_type == "boss" and event_type == "boss_kill":
                target_name = data.get("target", "")
                if target_name == quest.objective.get("target"):
                    quest.objective["current"] = 1
                    quest.completed = True
                    messages.append(
                        f"[bright_green]Quest Complete:[/bright_green] {quest.name}!"
                    )

            # Sync back to player's active_quests list
            self._sync_quest_to_player(player, quest)

        return messages

    def complete_quest(self, player: Player, quest_id: str) -> dict:
        """Mark quest complete, award rewards, and mark as turned in.

        Returns: {xp: int, gold: int, item: dict | None, message: str}
        """
        quests = self._get_quest_objects(player)
        target_quest = None
        for q in quests:
            if q.quest_id == quest_id:
                target_quest = q
                break

        if target_quest is None:
            return {"xp": 0, "gold": 0, "item": None, "message": "Quest not found."}

        if not target_quest.completed:
            return {
                "xp": 0,
                "gold": 0,
                "item": None,
                "message": "Quest is not yet complete.",
            }

        if target_quest.turned_in:
            return {
                "xp": 0,
                "gold": 0,
                "item": None,
                "message": "Quest already turned in.",
            }

        # Award rewards
        xp = target_quest.rewards.get("xp", 0)
        gold = target_quest.rewards.get("gold", 0)
        item = target_quest.rewards.get("item")

        player.xp += xp
        player.gold += gold
        if item:
            player.add_item(item)

        target_quest.turned_in = True

        # Move to completed_quests
        player.completed_quests.append(target_quest.quest_id)

        # Remove from active_quests
        player.active_quests = [
            q for q in player.active_quests
            if (q.get("quest_id") if isinstance(q, dict) else getattr(q, "quest_id", "")) != quest_id
        ]

        # Sync back
        self._sync_quest_to_player(player, target_quest)

        parts = [f"Quest turned in: {target_quest.name}"]
        if xp:
            parts.append(f"+{xp} XP")
        if gold:
            parts.append(f"+{gold} Gold")
        if item:
            parts.append(f"Received: {item.get('name', 'item')}")

        return {
            "xp": xp,
            "gold": gold,
            "item": item,
            "message": " | ".join(parts),
        }

    def get_active_quests(self, player: Player) -> list[Quest]:
        """Get all active (not completed/not turned in) quests."""
        return [
            q for q in self._get_quest_objects(player)
            if not q.turned_in
        ]

    def get_completed_quests(self, player: Player) -> list[Quest]:
        """Get quests that are completed but not yet turned in."""
        return [
            q for q in self._get_quest_objects(player)
            if q.completed and not q.turned_in
        ]

    # ------------------------------------------------------------------
    # Quest generation helpers
    # ------------------------------------------------------------------

    def _generate_kill_quest(self, floor: int) -> Quest:
        targets = _get_floor_targets(floor)
        target = random.choice(targets)
        count = random.randint(3, 6 + floor)
        xp_reward = 20 * count + floor * 15
        gold_reward = 10 * count + floor * 10

        quest_id = self._next_id()
        return Quest(
            quest_id=quest_id,
            name=f"Exterminate the {target}s",
            description=f"Defeat {count} {target}(s) on floor {floor}.",
            quest_type="kill",
            objective={"target": target, "count": count, "current": 0},
            rewards={"xp": xp_reward, "gold": gold_reward, "item": None},
            floor=floor,
        )

    def _generate_fetch_quest(self, floor: int) -> Quest:
        item_name = random.choice(FETCH_ITEMS)
        count = random.randint(1, 3)
        xp_reward = 30 * count + floor * 20
        gold_reward = 15 * count + floor * 12

        quest_id = self._next_id()
        return Quest(
            quest_id=quest_id,
            name=f"Retrieve the {item_name}",
            description=f"Find {count} {item_name}(s) on floor {floor}.",
            quest_type="fetch",
            objective={"target": item_name, "count": count, "current": 0},
            rewards={"xp": xp_reward, "gold": gold_reward, "item": None},
            floor=floor,
        )

    def _generate_explore_quest(self, floor: int) -> Quest:
        location = random.choice(LOCATION_NAMES)
        count = random.randint(5, 10 + floor)
        xp_reward = 10 * count + floor * 10
        gold_reward = 5 * count + floor * 8

        quest_id = self._next_id()
        return Quest(
            quest_id=quest_id,
            name=f"Map the {location}",
            description=f"Explore {count} rooms on floor {floor}.",
            quest_type="explore",
            objective={"target": location, "count": count, "current": 0},
            rewards={"xp": xp_reward, "gold": gold_reward, "item": None},
            floor=floor,
        )

    def _generate_boss_quest(self, floor: int) -> Quest:
        bosses = BOSS_NAMES_BY_FLOOR.get(floor, [])
        if not bosses:
            # Fallback to kill quest if no boss defined
            return self._generate_kill_quest(floor)
        boss = random.choice(bosses)
        xp_reward = 100 + floor * 50
        gold_reward = 50 + floor * 30

        # Boss quests sometimes give an item reward
        item_reward = None
        if random.random() < 0.5:
            item_reward = {
                "name": f"{boss}'s Trophy",
                "type": "junk",
                "rarity": "rare",
                "description": f"A trophy from defeating the {boss}.",
                "gold_value": gold_reward,
            }

        quest_id = self._next_id()
        return Quest(
            quest_id=quest_id,
            name=f"Defeat {boss}",
            description=f"Find and defeat the {boss} on floor {floor}.",
            quest_type="boss",
            objective={"target": boss, "count": 1, "current": 0},
            rewards={"xp": xp_reward, "gold": gold_reward, "item": item_reward},
            floor=floor,
        )

    # ------------------------------------------------------------------
    # Player quest data synchronization
    # ------------------------------------------------------------------

    def _get_quest_objects(self, player: Player) -> list[Quest]:
        """Convert player's active_quests (list of dicts) to Quest objects."""
        result: list[Quest] = []
        for entry in player.active_quests:
            if isinstance(entry, Quest):
                result.append(entry)
            elif isinstance(entry, dict):
                try:
                    result.append(Quest.from_dict(entry))
                except (KeyError, TypeError):
                    continue
        return result

    def _sync_quest_to_player(self, player: Player, quest: Quest) -> None:
        """Update a quest in the player's active_quests list."""
        quest_data = quest.to_dict()
        for i, entry in enumerate(player.active_quests):
            entry_id = ""
            if isinstance(entry, dict):
                entry_id = entry.get("quest_id", "")
            elif isinstance(entry, Quest):
                entry_id = entry.quest_id
            if entry_id == quest.quest_id:
                player.active_quests[i] = quest_data
                return
        # If not found and not turned in, add it
        if not quest.turned_in:
            player.active_quests.append(quest_data)
