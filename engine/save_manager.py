"""JSON-based save/load system for SonahRPG."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from engine.config import SAVE_DIR

if TYPE_CHECKING:
    from engine.game import Game


def _saves_dir() -> Path:
    """Return (and create if needed) the saves directory."""
    p = Path(SAVE_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _slot_path(slot: int) -> Path:
    return _saves_dir() / f"save_{slot}.json"


class SaveManager:
    """Handles serialising game state to and from JSON files."""

    @staticmethod
    def save(game: Game, slot: int = 0) -> None:
        """Write the current game state to *saves/save_{slot}.json*.

        For Phase 1 we persist the essentials: player identity and
        timestamp.  Full serialisation (inventory, map, quests) will
        be added in Phase 8.
        """
        player = game.player
        data: dict[str, Any] = {
            "slot": slot,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "player": {},
        }

        if player is not None:
            # Full player serialization: stats, inventory, equipment, skills, quests
            data["player"] = player.to_dict()

        # Persist narrative state
        narrative_mgr = getattr(game, "narrative_manager", None)
        if narrative_mgr is not None:
            data["narrative"] = narrative_mgr.to_dict()

        path = _slot_path(slot)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    @staticmethod
    def load(slot: int = 0) -> dict | None:
        """Deserialise save data from disk.  Returns ``None`` if the
        save file does not exist or is corrupt.
        """
        path = _slot_path(slot)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return None

    @staticmethod
    def list_saves() -> list[dict]:
        """Return metadata for every save file found on disk.

        Each entry contains ``slot``, ``name``, ``level``, and ``date``.
        """
        saves: list[dict] = []
        saves_dir = _saves_dir()

        for path in sorted(saves_dir.glob("save_*.json")):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                player = data.get("player", {})
                saves.append({
                    "slot": data.get("slot", 0),
                    "name": player.get("name", "Unknown"),
                    "level": player.get("level", 1),
                    "date": data.get("timestamp", ""),
                })
            except (json.JSONDecodeError, OSError):
                continue

        return saves

    @staticmethod
    def delete_save(slot: int = 0) -> None:
        """Remove the save file for *slot* if it exists."""
        path = _slot_path(slot)
        if path.exists():
            os.remove(path)
