"""
Turn Type Enum for game state
"""

from enum import Enum


class TurnType(Enum):
    """Types of turn management"""
    SINGLE_PLAYER = "single_player"  # Rotating active player
    SYNCHRONOUS = "synchronous"      # All players in same turn
