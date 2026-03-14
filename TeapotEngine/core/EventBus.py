"""
EventBus — lightweight pub/sub registry mapping event types to component instance ids.

The engine looks up subscribed instance ids when an event fires, then
calls ScriptRunner.call_on_event() for each one. There are no Reaction
or TriggerDefinition objects — subscriptions are pure (event_type → instance_id) pairs.
"""
from __future__ import annotations


class EventBus:
    """Maps event_type strings to lists of subscribed component instance ids."""

    def __init__(self):
        # event_type → list of instance_ids (in subscription order)
        self._subscriptions: dict[str, list[str]] = {}
        # instance_id → list of event_types (for O(1) unsubscribe-all)
        self._by_instance: dict[str, list[str]] = {}

    # ------------------------------------------------------------------
    # Subscribe / unsubscribe
    # ------------------------------------------------------------------

    def subscribe(self, instance_id: str, event_types: list[str]) -> None:
        """Register instance_id to receive each event type in the list."""
        for event_type in event_types:
            self._subscriptions.setdefault(event_type, [])
            if instance_id not in self._subscriptions[event_type]:
                self._subscriptions[event_type].append(instance_id)

            self._by_instance.setdefault(instance_id, [])
            if event_type not in self._by_instance[instance_id]:
                self._by_instance[instance_id].append(event_type)

    def unsubscribe(self, instance_id: str, event_type: str) -> None:
        """Remove a single (instance_id, event_type) subscription."""
        if event_type in self._subscriptions:
            self._subscriptions[event_type] = [
                i for i in self._subscriptions[event_type] if i != instance_id
            ]
        if instance_id in self._by_instance:
            self._by_instance[instance_id] = [
                t for t in self._by_instance[instance_id] if t != event_type
            ]

    def unsubscribe_all(self, instance_id: str) -> None:
        """Remove all subscriptions for a given instance (called on destroy)."""
        for event_type in self._by_instance.get(instance_id, []):
            if event_type in self._subscriptions:
                self._subscriptions[event_type] = [
                    i for i in self._subscriptions[event_type] if i != instance_id
                ]
        self._by_instance.pop(instance_id, None)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def get_subscribers(self, event_type: str) -> list[str]:
        """Return all instance ids subscribed to event_type (+ wildcard "*")."""
        result: list[str] = list(self._subscriptions.get(event_type, []))
        for iid in self._subscriptions.get("*", []):
            if iid not in result:
                result.append(iid)
        return result

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_subscriptions_for_instance(self, instance_id: str) -> list[str]:
        return list(self._by_instance.get(instance_id, []))

    def subscription_count(self) -> int:
        return sum(len(v) for v in self._subscriptions.values())

    def clear(self) -> None:
        self._subscriptions.clear()
        self._by_instance.clear()
