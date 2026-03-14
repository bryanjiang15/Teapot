"""
EventRegistry — manages event lifecycle and auto-incrementing IDs.
"""
from __future__ import annotations

from typing import Optional

from .Events import Event


class EventRegistry:
    """Manages event lifecycle and ID assignment."""

    def __init__(self):
        self._counter: int = 0
        self._registry: dict[int, Event] = {}

    def register(self, event: Event) -> int:
        """Assign an ID to the event, store it, and return the ID."""
        self._counter += 1
        event.id = self._counter
        self._registry[event.id] = event
        return event.id

    def get(self, event_id: int) -> Optional[Event]:
        return self._registry.get(event_id)

    def unregister(self, event_id: int) -> None:
        """Remove an event after it has been resolved."""
        self._registry.pop(event_id, None)

    def clear(self) -> None:
        self._registry.clear()

    def size(self) -> int:
        return len(self._registry)
