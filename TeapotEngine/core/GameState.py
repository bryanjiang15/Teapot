"""
GameState — the canonical mutable state of a running match.

All state changes go through GameAPI methods which directly update
this object and queue events. GameState has no domain-specific
fields — turns, health, mana etc. all live in the properties dict.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from .Component import ComponentInstance, ComponentManager
from .Events import Event, PendingInput


class GameState(BaseModel):
    """Full mutable state of one running match.

    Fields
    ------
    match_id : str
    game_instance_id : str
        The runtime instance id of the GAME component.
    player_instance_ids : list[str]
        Runtime instance ids for each PLAYER component, in join order.
    active_player_id : str | None
        Runtime instance id of the currently active PLAYER.
        None until a script calls game.set_active_player().
    manager : ComponentManager
        Registry of all live ComponentInstance objects.
    properties : dict[str, dict[str, Any]]
        Per-instance key→value property store.
        instance_id → {property_key: value}
    containers : dict[str, list[str]]
        Ordered child lists for CONTAINER instances.
        container_instance_id → [child_instance_id, …]
    event_log : list[Event]
        Append-only log of every applied event (used by game.events).
    pending_input : PendingInput | None
        Set when a script calls game.wait_for_input(). Cleared when
        the player submits an answer via MatchActor.submit_input().
    game_ended : bool
        Set to True when end_game() is called.
    winner_id : str | None
        Runtime instance id of the winning PLAYER, if any.
    """
    match_id: str
    game_instance_id: str = ""
    player_instance_ids: list[str] = Field(default_factory=list)
    active_player_id: Optional[str] = None

    manager: ComponentManager = Field(default_factory=ComponentManager)
    properties: dict[str, dict[str, Any]] = Field(default_factory=dict)
    containers: dict[str, list[str]] = Field(default_factory=dict)

    event_log: list[Event] = Field(default_factory=list)
    pending_input: Optional[PendingInput] = None
    game_ended: bool = False
    winner_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Instance convenience helpers
    # ------------------------------------------------------------------

    def get_instance(self, instance_id: str) -> Optional[ComponentInstance]:
        return self.manager.get(instance_id)

    def get_game_instance(self) -> Optional[ComponentInstance]:
        return self.manager.get(self.game_instance_id)

    def get_player_instances(self) -> list[ComponentInstance]:
        return [
            inst for pid in self.player_instance_ids
            if (inst := self.manager.get(pid)) is not None
        ]

    def get_active_player(self) -> Optional[ComponentInstance]:
        if self.active_player_id:
            return self.manager.get(self.active_player_id)
        return None

    # ------------------------------------------------------------------
    # Property helpers
    # ------------------------------------------------------------------

    def get_property(self, instance_id: str, key: str, default: Any = None) -> Any:
        return self.properties.get(instance_id, {}).get(key, default)

    def set_property(self, instance_id: str, key: str, value: Any) -> None:
        if instance_id not in self.properties:
            self.properties[instance_id] = {}
        self.properties[instance_id][key] = value

    def init_properties(self, instance_id: str, initial: dict[str, Any]) -> None:
        """Seed initial properties from definition; does not overwrite existing."""
        if instance_id not in self.properties:
            self.properties[instance_id] = {}
        for k, v in initial.items():
            if k not in self.properties[instance_id]:
                self.properties[instance_id][k] = v

    # ------------------------------------------------------------------
    # Container helpers (ordered children)
    # ------------------------------------------------------------------

    def get_children(self, container_id: str) -> list[str]:
        """Return ordered child instance ids for a container."""
        return list(self.containers.get(container_id, []))

    def add_to_container(self, instance_id: str, container_id: str) -> None:
        """Append instance to a container's ordered list."""
        self.containers.setdefault(container_id, [])
        if instance_id not in self.containers[container_id]:
            self.containers[container_id].append(instance_id)

    def remove_from_container(self, instance_id: str, container_id: str) -> None:
        if container_id in self.containers:
            self.containers[container_id] = [
                i for i in self.containers[container_id] if i != instance_id
            ]

    # ------------------------------------------------------------------
    # Event log
    # ------------------------------------------------------------------

    def record_event(self, event: Event) -> None:
        self.event_log.append(event)

    def to_dict(self) -> dict[str, Any]:
        return {
            "match_id": self.match_id,
            "game_instance_id": self.game_instance_id,
            "player_instance_ids": self.player_instance_ids,
            "active_player_id": self.active_player_id,
            "instance_count": self.manager.count(),
            "event_count": len(self.event_log),
            "game_ended": self.game_ended,
            "winner_id": self.winner_id,
        }
