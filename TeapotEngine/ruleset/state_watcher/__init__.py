"""
State watcher types and utilities for state-based action checking
"""

from enum import Enum


class TriggerType(str, Enum):
    """Type of trigger - event-driven or state-based"""
    EVENT = "event"           # Normal event-driven trigger
    STATE_BASED = "state"     # Checked after stack empties


# TODO: Future implementation - add StateWatcherPriority enum for ordering
# watchers by priority (e.g., GAME_LOSS=100, GAME_WIN=90, COMPONENT_DEATH=50, PHASE_TRANSITION=10)

# TODO: Future implementation - analyze predicates to determine relevant categories for optimization

