"""Simple pub/sub event bus for decoupled game systems."""

from collections.abc import Callable

# Event type constants
DAMAGE_DEALT = "damage_dealt"
DAMAGE_TAKEN = "damage_taken"
ENEMY_KILLED = "enemy_killed"
ITEM_PICKED = "item_picked"
ITEM_EQUIPPED = "item_equipped"
LEVEL_UP = "level_up"
QUEST_COMPLETE = "quest_complete"
GOLD_CHANGED = "gold_changed"
PLAYER_DIED = "player_died"
COMBAT_START = "combat_start"
COMBAT_END = "combat_end"
SKILL_USED = "skill_used"
STATUS_APPLIED = "status_applied"
STATUS_REMOVED = "status_removed"


class EventBus:
    """Lightweight publish/subscribe event system.

    Any game system can subscribe to named events and get notified
    when another system emits that event with arbitrary keyword data.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Register *handler* to be called when *event_type* is emitted."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Remove *handler* from *event_type* listeners.

        Silently does nothing if the handler was never registered.
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
            except ValueError:
                pass

    def emit(self, event_type: str, **data) -> None:
        """Fire *event_type*, calling every registered handler with *data*.

        Handlers receive a single ``dict`` containing whatever keyword
        arguments were passed to ``emit``.  If a handler raises, the
        exception is printed but does not prevent other handlers from
        running.
        """
        for handler in self._handlers.get(event_type, []):
            try:
                handler(data)
            except Exception as exc:  # noqa: BLE001
                print(f"[EventBus] handler {handler.__name__} raised: {exc}")
