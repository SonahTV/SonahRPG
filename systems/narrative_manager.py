"""Narrative progression manager for SonahRPG story system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from engine.game import Game


class NarrativeManager:
    """Tracks story progression, lore discovery, and ending conditions.

    Integrates with the save system via to_dict/from_dict for persistence.
    """

    def __init__(self, game: Game) -> None:
        self.game = game

        # Progression tracking
        self.floors_visited: set[int] = set()  # floors where narrative was shown
        self.lore_found: list[str] = []  # IDs of discovered lore entries
        self.bosses_defeated: list[str] = []  # boss names defeated
        self.bosses_spared: list[str] = []  # bosses shown mercy (for Liberator ending)
        self.story_flags: dict[str, bool] = {}  # arbitrary branching flags from CYOA choices
        self.exploration_events_triggered: set[int] = set()  # indices of triggered events
        self.intro_shown: bool = False
        self.ending_shown: bool = False

    # -- Event handlers ------------------------------------------------

    def on_floor_entered(self, floor: int) -> list[dict] | None:
        """Called when player enters a new floor.

        Returns narrative pages (list of dicts with 'type', 'text', 'choices' etc.)
        if this floor has a narrative trigger and hasn't been seen before.
        Returns None if no narrative to show.
        """
        if floor in self.floors_visited:
            return None
        self.floors_visited.add(floor)

        from data.narrative import FLOOR_NARRATIVES
        narrative = FLOOR_NARRATIVES.get(floor)
        if narrative:
            return narrative.get("pages")
        return None

    def on_boss_defeated(self, boss_name: str) -> list[dict] | None:
        """Called when a boss is killed.

        Records the defeat and returns epilogue pages if available.
        """
        if boss_name not in self.bosses_defeated:
            self.bosses_defeated.append(boss_name)

        from data.narrative import BOSS_ENCOUNTER_TEXT
        boss_data = BOSS_ENCOUNTER_TEXT.get(boss_name)
        if boss_data:
            return boss_data.get("epilogue_pages")
        return None

    def on_boss_spared(self, boss_name: str) -> None:
        """Called when player shows mercy to a boss."""
        if boss_name not in self.bosses_spared:
            self.bosses_spared.append(boss_name)

    def get_boss_intro(self, boss_name: str) -> list[dict] | None:
        """Get intro cinematic pages for a boss encounter."""
        from data.narrative import BOSS_ENCOUNTER_TEXT
        boss_data = BOSS_ENCOUNTER_TEXT.get(boss_name)
        if boss_data:
            return boss_data.get("intro_pages")
        return None

    def get_boss_mid_fight_dialogue(self, boss_name: str) -> list[str] | None:
        """Get dialogue lines for when boss hits 50% HP."""
        from data.narrative import BOSS_ENCOUNTER_TEXT
        boss_data = BOSS_ENCOUNTER_TEXT.get(boss_name)
        if boss_data:
            return boss_data.get("mid_fight_dialogue")
        return None

    def on_lore_found(self, lore_id: str) -> dict | None:
        """Record lore discovery and return the lore entry data for display."""
        if lore_id in self.lore_found:
            return None  # Already found
        self.lore_found.append(lore_id)

        from data.lore import LORE_COLLECTIBLES
        for entry in LORE_COLLECTIBLES:
            if entry["id"] == lore_id:
                return entry
        return None

    def set_flag(self, flag_name: str, value: bool = True) -> None:
        """Set a story flag from a CYOA choice."""
        self.story_flags[flag_name] = value

    def has_flag(self, flag_name: str) -> bool:
        """Check if a story flag is set."""
        return self.story_flags.get(flag_name, False)

    def check_exploration_event(self, floor: int) -> list[dict] | None:
        """Check if a random exploration event should trigger.

        Called on player movement. Returns event pages or None.
        Uses random chance and checks floor range.
        """
        import random
        from data.narrative import EXPLORATION_EVENTS

        eligible = []
        for i, event in enumerate(EXPLORATION_EVENTS):
            if i in self.exploration_events_triggered:
                continue
            low, high = event["trigger_floors"]
            if low <= floor <= high:
                eligible.append((i, event))

        if not eligible:
            return None

        # Roll for each eligible event
        for idx, event in eligible:
            if random.random() < event.get("chance", 0.05):
                self.exploration_events_triggered.add(idx)
                return event.get("pages")

        return None

    def apply_choice_effect(self, effect: dict | None) -> str:
        """Apply the effect of a CYOA choice and return a log message.

        Effects: heal, damage, gold, xp, item, lore, status_effect
        """
        if not effect:
            return ""

        player = self.game.player
        effect_type = effect.get("type", "")
        value = effect.get("value", 0)

        if effect_type == "heal":
            actual = player.heal(value)
            return f"[green]Restored {actual} HP.[/green]"
        elif effect_type == "damage":
            actual = player.take_damage(value)
            return f"[red]Took {actual} damage![/red]"
        elif effect_type == "gold":
            player.gold += value
            return f"[yellow]Gained {value} gold.[/yellow]"
        elif effect_type == "xp":
            player.xp += value
            return f"[green]Gained {value} XP.[/green]"
        elif effect_type == "lore":
            lore_id = effect.get("lore_id", "")
            self.on_lore_found(lore_id)
            return "[cyan]New lore discovered.[/cyan]"

        return ""

    # -- Ending calculation -------------------------------------------

    def determine_ending(self) -> str:
        """Calculate which ending the player gets based on story state.

        Priority order:
        1. liberator - spared all 3 pre-final bosses
        2. truth_seeker - found 80%+ lore entries
        3. hollow_victory - beat game under level 10
        4. binding_restored - default ending
        """
        player = self.game.player

        # Check Liberator ending
        required_mercy = {"Goblin King", "Spider Queen", "Bone Dragon"}
        if required_mercy.issubset(set(self.bosses_spared)):
            return "liberator"

        # Check Truth Seeker ending
        from data.lore import LORE_COLLECTIBLES
        total_lore = len(LORE_COLLECTIBLES)
        if total_lore > 0 and len(self.lore_found) >= total_lore * 0.8:
            return "truth_seeker"

        # Check Hollow Victory
        if player and player.level < 10:
            return "hollow_victory"

        # Default ending
        return "binding_restored"

    def get_lore_progress(self) -> tuple[int, int]:
        """Return (found, total) lore count."""
        from data.lore import LORE_COLLECTIBLES
        return len(self.lore_found), len(LORE_COLLECTIBLES)

    def get_intro_pages(self) -> list[dict]:
        """Get the intro cinematic pages including class backstory."""
        from data.narrative import INTRO_CINEMATIC
        from data.backstories import CLASS_BACKSTORIES

        pages = list(INTRO_CINEMATIC)  # Copy

        # Add class backstory pages
        player = self.game.player
        if player:
            backstory = CLASS_BACKSTORIES.get(player.player_class)
            if backstory:
                # Insert backstory pages before the final intro page
                for para in backstory["paragraphs"]:
                    pages.insert(-1, {"type": "text", "text": para})

        return pages

    # -- Serialization ------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize narrative state for saving."""
        return {
            "floors_visited": list(self.floors_visited),
            "lore_found": self.lore_found,
            "bosses_defeated": self.bosses_defeated,
            "bosses_spared": self.bosses_spared,
            "story_flags": self.story_flags,
            "exploration_events_triggered": list(self.exploration_events_triggered),
            "intro_shown": self.intro_shown,
            "ending_shown": self.ending_shown,
        }

    @classmethod
    def from_dict(cls, data: dict, game: Game) -> NarrativeManager:
        """Deserialize narrative state from save data."""
        nm = cls(game)
        nm.floors_visited = set(data.get("floors_visited", []))
        nm.lore_found = data.get("lore_found", [])
        nm.bosses_defeated = data.get("bosses_defeated", [])
        nm.bosses_spared = data.get("bosses_spared", [])
        nm.story_flags = data.get("story_flags", {})
        nm.exploration_events_triggered = set(data.get("exploration_events_triggered", []))
        nm.intro_shown = data.get("intro_shown", False)
        nm.ending_shown = data.get("ending_shown", False)
        return nm
