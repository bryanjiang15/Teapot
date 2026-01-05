"""
Core event system for the game engine
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid
from datetime import datetime
from TeapotEngine.ruleset.rule_definitions.EffectDefinition import EffectDefinition


class EventStatus(Enum):
    PENDING = "pending"
    APPLIED = "applied"
    PREVENTED = "prevented"
    FAILED = "failed"


class StackItemType(Enum):
    EVENT = "event"
    REACTION = "reaction"


class Event(BaseModel):
    """A domain occurrence in the game"""
    id: int = 0  # Will be assigned by MatchActor
    type: str = ""
    payload: Dict[str, Any] = Field(default_factory=dict)
    caused_by: Optional[str] = None
    status: EventStatus = EventStatus.PENDING
    timestamp: datetime = Field(default_factory=datetime.now)
    order: int = Field(default=0)


class Reaction(BaseModel):
    """A rule-driven response to an event"""
    id: int = Field(default_factory=lambda: int(uuid.uuid4().int % 1000000))
    when: Dict[str, Any] = Field(default_factory=dict)
    condition: Optional[Dict[str, Any]] = None  # Single condition predicate
    effects: List["EffectDefinition"] = Field(default_factory=list)
    timing: str = "post"  # "pre" or "post"
    caused_by: Optional[Dict[str, str]] = None  # {"object_type": str, "object_id": str}


class StackItem(BaseModel):
    """A unit scheduled for resolution on the stack"""
    kind: StackItemType
    ref_id: int  # event_id or reaction_id
    created_at_order: int
    flags: Dict[str, Any] = Field(default_factory=dict)


class PendingInput(BaseModel):
    """A request for player choice needed to continue resolution"""
    input_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    for_player_ids: List[str] = Field(default_factory=list)
    kind: str = ""  # "target_select", "order_select", "mode_pick", "pay_cost", "confirm"
    constraints: Dict[str, Any] = Field(default_factory=dict)
    expires_at: Optional[datetime] = None
    
