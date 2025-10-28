"""
Core event system for the game engine
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid
from datetime import datetime

# Core event type constants

# Phase events
PHASE_ENTERED = "PhaseEntered"
PHASE_EXITED = "PhaseExited"
TURN_ENDED = "TurnEnded"

# Action/Rule events
ACTION_EXECUTED = "ActionExecuted"
RULE_EXECUTED = "RuleExecuted"

# State change events (emitted by rule effects)
CARD_MOVED = "CardMoved"
RESOURCE_CHANGED = "ResourceChanged"
DAMAGE_DEALT = "DamageDealt"


class EventStatus(Enum):
    PENDING = "pending"
    APPLIED = "applied"
    PREVENTED = "prevented"
    FAILED = "failed"


class StackItemType(Enum):
    EVENT = "event"
    REACTION = "reaction"


@dataclass
class Event:
    """A domain occurrence in the game"""
    id: int = 0  # Will be assigned by MatchActor
    type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    caused_by: Optional[str] = None
    status: EventStatus = EventStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.utcnow)
    order: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "caused_by": self.caused_by,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "order": self.order
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        return cls(
            id=data["id"],
            type=data["type"],
            payload=data["payload"],
            caused_by=data.get("caused_by"),
            status=EventStatus(data["status"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            order=data["order"]
        )


@dataclass
class Reaction:
    """A rule-driven response to an event"""
    id: int = field(default_factory=lambda: int(uuid.uuid4().int % 1000000))
    when: Dict[str, Any] = field(default_factory=dict)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    effects: List[Dict[str, Any]] = field(default_factory=list)
    timing: str = "post"  # "pre" or "post"
    caused_by: Optional[Dict[str, str]] = None  # {"object_type": str, "object_id": str}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "when": self.when,
            "conditions": self.conditions,
            "effects": self.effects,
            "timing": self.timing,
            "caused_by": self.caused_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Reaction":
        return cls(
            id=data["id"],
            when=data["when"],
            conditions=data["conditions"],
            effects=data["effects"],
            timing=data["timing"],
            caused_by=data.get("caused_by")
        )


@dataclass
class StackItem:
    """A unit scheduled for resolution on the stack"""
    kind: StackItemType
    ref_id: int  # event_id or reaction_id
    created_at_order: int
    flags: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind.value,
            "ref_id": self.ref_id,
            "created_at_order": self.created_at_order,
            "flags": self.flags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StackItem":
        return cls(
            kind=StackItemType(data["kind"]),
            ref_id=data["ref_id"],
            created_at_order=data["created_at_order"],
            flags=data.get("flags", {})
        )


@dataclass
class PendingInput:
    """A request for player choice needed to continue resolution"""
    input_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    for_player_ids: List[str] = field(default_factory=list)
    kind: str = ""  # "target_select", "order_select", "mode_pick", "pay_cost", "confirm"
    constraints: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_id": self.input_id,
            "for_player_ids": self.for_player_ids,
            "kind": self.kind,
            "constraints": self.constraints,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PendingInput":
        return cls(
            input_id=data["input_id"],
            for_player_ids=data["for_player_ids"],
            kind=data["kind"],
            constraints=data["constraints"],
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
        )
