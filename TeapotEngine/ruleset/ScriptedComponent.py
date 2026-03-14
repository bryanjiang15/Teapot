"""
ScriptedComponent — the universal game entity model.

There are exactly four component kinds. All domain concepts
(Card, Zone, Phase, Power, Health, Mana) are expressed through
these four kinds plus a properties dict and a lifecycle script.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ComponentKind(str, Enum):
    """The four universal game entity types."""
    GAME      = "game"       # root; always exactly one per match
    PLAYER    = "player"     # a participant
    OBJECT    = "object"     # any game entity: card, piece, token, tile, die…
    CONTAINER = "container"  # holds/orders OBJECTs; has a visibility rule


class ScriptedComponent(BaseModel):
    """A game entity definition with an optional AI-generated lifecycle script.

    Each definition maps to one or more runtime instances:
      - GAME      → exactly one, created at begin_game()
      - PLAYER    → one per player_id in the match
      - OBJECT    → zero or more, created via game.instantiate()
      - CONTAINER → zero or more, created via game.instantiate()

    Fields
    ------
    id : str
        UUID string matching the API component id.
    kind : ComponentKind
        What kind of game entity this is.
    name : str
        Human-readable name ("Fireball", "Hand Zone", "Draw Phase"…).
    description : str | None
        Optional human description (for AI context; not used at runtime).
    script : str | None
        Pre-compiled Python lifecycle script with on_init / on_event /
        on_update hooks. None for static-only components (e.g. a plain
        container with no behavioral logic).
    properties : dict
        Initial property values loaded into every instance of this
        definition before on_init runs. Anything domain-specific
        (cost, health, max_size, visibility) lives here.
    event_subscriptions : list[str]
        Event type strings this component listens for. Populated by the
        compiler from the graph's event nodes. The engine registers each
        instance with the EventBus on these types.
    """
    id: str
    kind: ComponentKind
    name: str
    description: Optional[str] = None
    script: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)
    event_subscriptions: list[str] = Field(default_factory=list)
