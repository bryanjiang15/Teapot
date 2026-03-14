"""
GameAPI — the sandboxed read/write interface exposed to component scripts.

Scripts never access GameState directly. All reads return ObjectView
(an immutable snapshot), all writes are routed through GameAPI methods
which update state and queue events for the MatchActor to process.

Design rules
------------
- Mutations update state immediately (direct write) AND queue a system
  event so other components can react.
- Events queued during a script call are collected in _pending_events
  and pushed to the MatchActor's stack after the script returns.
- wait_for_input() raises WaitForInputSignal to pause execution cleanly.
- All RNG goes through the match's DeterministicRNG.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Callable, Optional, TYPE_CHECKING

from .Events import Event, PendingInput
from .rng import DeterministicRNG
from TeapotEngine.ruleset.system_models.SystemEvent import (
    OBJECT_MOVED,
    PROPERTY_CHANGED,
    OBJECT_INSTANTIATED,
    OBJECT_DESTROYED,
    GAME_ENDED,
)

if TYPE_CHECKING:
    from .GameState import GameState
    from .EventBus import EventBus
    from .ScriptRunner import ScriptRunner
    from TeapotEngine.ruleset.IR import RulesetIR


# ---------------------------------------------------------------------------
# Signal exception — raised inside scripts to pause execution
# ---------------------------------------------------------------------------

class WaitForInputSignal(Exception):
    """Raised by GameAPI.wait_for_input() to cleanly pause script execution."""
    def __init__(self, player_id: str, prompt: str, options: list):
        self.player_id = player_id
        self.prompt = prompt
        self.options = options


# ---------------------------------------------------------------------------
# Immutable view objects returned to scripts
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ObjectView:
    """Immutable snapshot of a ComponentInstance exposed to scripts."""
    id: str
    name: str
    kind: str          # ComponentKind.value string
    owner_id: Optional[str]
    container_id: Optional[str]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ObjectView):
            return self.id == other.id
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"<{self.kind}:{self.name}>"


class EventHistoryAPI:
    """Read-only query interface for the event log, accessible via game.events."""

    def __init__(self, event_log: list[Event]):
        self._log = event_log

    def count(self, event_type: str) -> int:
        """Total occurrences of event_type in the log."""
        return sum(1 for e in self._log if e.type == event_type)

    def count_since(self, event_type: str, since_event_type: str) -> int:
        """Count event_type occurrences since the last occurrence of since_event_type."""
        last_reset = -1
        for i, e in enumerate(self._log):
            if e.type == since_event_type:
                last_reset = i
        return sum(1 for e in self._log[last_reset + 1:] if e.type == event_type)

    def last(self, event_type: str) -> Optional[dict[str, Any]]:
        """Payload dict of the most recent event of event_type, or None."""
        for e in reversed(self._log):
            if e.type == event_type:
                return dict(e.payload)
        return None

    def history(self) -> list[dict[str, Any]]:
        """Full event log as a list of {type, payload} dicts."""
        return [{"type": e.type, "payload": dict(e.payload)} for e in self._log]


# ---------------------------------------------------------------------------
# GameAPI
# ---------------------------------------------------------------------------

class GameAPI:
    """Sandboxed interface for component scripts.

    One GameAPI instance is created per script call, scoped to the
    component currently executing. Collected events are flushed back
    to the engine after the script returns.

    Parameters
    ----------
    state       : GameState
    current_id  : str
        Instance id of the component whose script is running.
    ruleset     : RulesetIR
        Used by instantiate() to look up definition names.
    event_bus   : EventBus
        Used by instantiate() to register new instances.
    runner      : ScriptRunner
        Used by instantiate() to call on_init on the new instance.
    rng         : DeterministicRNG
    """

    def __init__(
        self,
        state: "GameState",
        current_id: str,
        ruleset: "RulesetIR",
        event_bus: "EventBus",
        runner: "ScriptRunner",
        rng: DeterministicRNG,
    ):
        self._state = state
        self._current_id = current_id
        self._ruleset = ruleset
        self._event_bus = event_bus
        self._runner = runner
        self._rng = rng
        self._pending_events: list[Event] = []

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def self(self) -> ObjectView:
        """The component currently running this script."""
        return self._view(self._current_id)

    # ------------------------------------------------------------------
    # Reads (return ObjectView, not mutable state)
    # ------------------------------------------------------------------

    @property
    def game(self) -> ObjectView:
        return self._view(self._state.game_instance_id)

    @property
    def players(self) -> list[ObjectView]:
        return [self._view(pid) for pid in self._state.player_instance_ids]

    @property
    def active_player(self) -> Optional[ObjectView]:
        if self._state.active_player_id:
            return self._view(self._state.active_player_id)
        return None

    @property
    def events(self) -> EventHistoryAPI:
        return EventHistoryAPI(self._state.event_log)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def find(
        self,
        kind: Optional[str] = None,
        container: Optional[ObjectView] = None,
        owner: Optional[ObjectView] = None,
        filter_fn: Optional[Callable[[ObjectView], bool]] = None,
    ) -> list[ObjectView]:
        """Return ObjectViews matching all supplied filters.

        Parameters
        ----------
        kind      : "game" | "player" | "object" | "container" (ComponentKind value)
        container : ObjectView of a CONTAINER — restrict to its direct children
        owner     : ObjectView of a PLAYER or GAME — restrict to owned instances
        filter_fn : arbitrary predicate (ObjectView) → bool
        """
        from TeapotEngine.ruleset.ScriptedComponent import ComponentKind

        if container is not None:
            child_ids = self._state.get_children(container.id)
            candidates = [
                self._state.manager.get(cid)
                for cid in child_ids
                if self._state.manager.get(cid)
            ]
        elif kind is not None:
            try:
                ck = ComponentKind(kind)
            except ValueError:
                return []
            candidates = self._state.manager.by_kind_query(ck)
        elif owner is not None:
            candidates = self._state.manager.by_owner_query(owner.id)
        else:
            candidates = self._state.manager.all()

        views = [self._view(inst.id) for inst in candidates if inst.is_active()]

        if kind is not None and container is not None:
            views = [v for v in views if v.kind == kind]
        if owner is not None:
            views = [v for v in views if v.owner_id == owner.id]
        if filter_fn is not None:
            views = [v for v in views if filter_fn(v)]
        return views

    def get_property(self, obj: ObjectView, key: str, default: Any = None) -> Any:
        return self._state.get_property(obj.id, key, default)

    # ------------------------------------------------------------------
    # Mutations (update state directly + queue a system event)
    # ------------------------------------------------------------------

    def set_property(self, obj: ObjectView, key: str, value: Any) -> None:
        old_value = self._state.get_property(obj.id, key)
        self._state.set_property(obj.id, key, value)
        self._queue(Event(
            type=PROPERTY_CHANGED,
            payload={"instance_id": obj.id, "key": key, "value": value, "old_value": old_value},
            caused_by=self._current_id,
        ))

    def move(self, obj: ObjectView, to_container: ObjectView) -> None:
        """Move obj into to_container.

        Updates the ComponentInstance, the container ordered lists in
        GameState, and queues an OBJECT_MOVED event.
        """
        instance = self._state.manager.get(obj.id)
        if not instance:
            return

        old_container_id = instance.container_id

        if old_container_id:
            self._state.remove_from_container(obj.id, old_container_id)

        self._state.add_to_container(obj.id, to_container.id)
        self._state.manager.move_to_container(obj.id, to_container.id)

        self._queue(Event(
            type=OBJECT_MOVED,
            payload={
                "instance_id": obj.id,
                "from_container_id": old_container_id,
                "to_container_id": to_container.id,
            },
            caused_by=self._current_id,
        ))

    def instantiate(
        self,
        definition_name: str,
        owner: ObjectView,
        properties: Optional[dict[str, Any]] = None,
    ) -> Optional[ObjectView]:
        """Create a new runtime instance of a named ScriptedComponent definition.

        Merges the definition's default properties with any overrides
        supplied in `properties`, then calls the new instance's on_init.
        Returns an ObjectView for the new instance, or None if the
        definition_name is not found.
        """
        from .Component import ComponentInstance

        definition = self._ruleset.get_component_by_name(definition_name)
        if not definition:
            return None

        new_id = str(uuid.uuid4())
        instance = ComponentInstance(
            id=new_id,
            definition_id=definition.id,
            kind=definition.kind,
            name=definition.name,
            owner_id=owner.id,
        )
        self._state.manager.add(instance)

        # Initialise properties: definition defaults merged with overrides
        merged = dict(definition.properties)
        if properties:
            merged.update(properties)
        self._state.init_properties(new_id, merged)

        # Register event subscriptions for the new instance
        if definition.event_subscriptions:
            self._event_bus.subscribe(new_id, definition.event_subscriptions)

        # Call on_init immediately (the new instance's GameAPI buffers its events)
        if definition.script:
            child_api = GameAPI(
                state=self._state,
                current_id=new_id,
                ruleset=self._ruleset,
                event_bus=self._event_bus,
                runner=self._runner,
                rng=self._rng,
            )
            try:
                self._runner.call_on_init(definition.script, child_api)
            except WaitForInputSignal:
                pass  # on_init should not wait for input; ignore if it does

            # Merge child's pending events into ours
            self._pending_events.extend(child_api._collect_events())

        self._queue(Event(
            type=OBJECT_INSTANTIATED,
            payload={"instance_id": new_id, "definition_name": definition_name, "owner_id": owner.id},
            caused_by=self._current_id,
        ))

        return self._view(new_id)

    def destroy(self, obj: ObjectView) -> None:
        """Remove an instance from the game.

        Unsubscribes from EventBus, removes from its container, and
        removes from the ComponentManager.
        """
        instance = self._state.manager.get(obj.id)
        if not instance:
            return

        self._event_bus.unsubscribe_all(obj.id)

        if instance.container_id:
            self._state.remove_from_container(obj.id, instance.container_id)

        self._state.manager.remove(obj.id)

        self._queue(Event(
            type=OBJECT_DESTROYED,
            payload={"instance_id": obj.id, "name": obj.name},
            caused_by=self._current_id,
        ))

    def set_active_player(self, player: ObjectView) -> None:
        self._state.active_player_id = player.id

    # ------------------------------------------------------------------
    # Flow control
    # ------------------------------------------------------------------

    def emit(self, event_type: str, payload: Optional[dict[str, Any]] = None) -> None:
        """Broadcast a custom game event."""
        self._queue(Event(
            type=event_type,
            payload=payload or {},
            caused_by=self._current_id,
        ))

    def wait_for_input(self, player: ObjectView, prompt: str, options: list[Any]) -> None:
        """Pause the game loop until the player submits a choice.

        Stores a PendingInput on GameState, then raises WaitForInputSignal
        which MatchActor catches to return WAITING_FOR_INPUT.
        The loop resumes via MatchActor.submit_input() which emits
        INPUT_RECEIVED with the player's answer.
        """
        self._state.pending_input = PendingInput(
            for_player_id=player.id,
            prompt=prompt,
            options=list(options),
        )
        raise WaitForInputSignal(player.id, prompt, options)

    def end_game(self, winner: Optional[ObjectView] = None) -> None:
        """Declare the game over."""
        self._state.game_ended = True
        self._state.winner_id = winner.id if winner else None
        self._queue(Event(
            type=GAME_ENDED,
            payload={"winner_id": self._state.winner_id},
            caused_by=self._current_id,
        ))

    # ------------------------------------------------------------------
    # RNG
    # ------------------------------------------------------------------

    def shuffle(self, container: ObjectView) -> None:
        """Randomly reorder the children of a CONTAINER instance."""
        children = self._state.containers.get(container.id)
        if children:
            self._rng.shuffle(children)

    def random_pick(self, container: ObjectView, count: int = 1) -> list[ObjectView]:
        """Pick `count` random children from a CONTAINER without removing them."""
        children = self._state.containers.get(container.id, [])
        k = min(count, len(children))
        if k == 0:
            return []
        picked = self._rng.sample(children, k)
        return [self._view(cid) for cid in picked if self._state.manager.get(cid)]

    def random_int(self, min_val: int, max_val: int) -> int:
        return self._rng.randint(min_val, max_val)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _view(self, instance_id: str) -> ObjectView:
        inst = self._state.manager.get(instance_id)
        if inst is None:
            # Return a tombstone view so scripts don't crash on destroyed objects
            return ObjectView(id=instance_id, name="<destroyed>", kind="object",
                              owner_id=None, container_id=None)
        return ObjectView(
            id=inst.id,
            name=inst.name,
            kind=inst.kind.value,
            owner_id=inst.owner_id,
            container_id=inst.container_id,
        )

    def _queue(self, event: Event) -> None:
        self._pending_events.append(event)

    def _collect_events(self) -> list[Event]:
        """Called by MatchActor after a script returns to get queued events."""
        events = list(self._pending_events)
        self._pending_events.clear()
        return events
