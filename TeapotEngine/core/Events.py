"""
Core event system for the game engine.

Events are the single communication mechanism between the engine
and component scripts. Scripts never mutate GameState directly —
they emit events via GameAPI, which the engine applies to state.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class EventStatus(Enum):
    PENDING   = "pending"
    APPLIED   = "applied"
    PREVENTED = "prevented"
    FAILED    = "failed"


class StackItemType(Enum):
    EVENT = "event"


class Event(BaseModel):
    """A discrete occurrence in the game."""
    id: int = 0                # assigned by EventRegistry
    type: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    caused_by: Optional[str] = None   # instance_id of the source component
    status: EventStatus = EventStatus.PENDING
    timestamp: datetime = Field(default_factory=datetime.now)
    order: int = Field(default=0)


class StackItem(BaseModel):
    """A unit scheduled for resolution on the stack."""
    kind: StackItemType
    ref_id: int              # event id
    created_at_order: int
    flags: dict[str, Any] = Field(default_factory=dict)


class PendingInput(BaseModel):
    """A request for player choice that pauses the game loop."""
    input_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    for_player_id: str = ""
    prompt: str = ""
    options: list[Any] = Field(default_factory=list)
    expires_at: Optional[datetime] = None
