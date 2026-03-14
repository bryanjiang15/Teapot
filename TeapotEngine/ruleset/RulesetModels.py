"""
RulesetModels — shared enums used across the engine.

Only VisibilityType remains from the old engine; everything else
was TCG-specific and is now expressed as plain properties.
"""
from enum import Enum


class VisibilityType(str, Enum):
    """Visibility of a CONTAINER's contents to players.

    Store as a property on CONTAINER component definitions:
        properties={"visibility": VisibilityType.OWNER_ONLY}
    The engine itself does not enforce visibility — that is the
    responsibility of the game scripts and the client layer.
    """
    PUBLIC     = "public"      # all players can see contents
    PRIVATE    = "private"     # no player can see contents (face-down pile)
    OWNER_ONLY = "owner_only"  # only the owning player can see contents
