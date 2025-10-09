"""
TeapotEngine - Shared Game Logic Library

A flexible, ruleset-driven game engine for TCG games.
Supports event sourcing, reaction systems, and dynamic rulesets.
"""

from .core.engine import GameEngine
from .core.match_actor import MatchActor
from .core.events import Event, Reaction, StackItem, PendingInput
from .core.state import GameState
from .core.interpreter import RulesetInterpreter
from .ruleset.ir import RulesetIR, ActionDefinition, PhaseDefinition
from .ruleset.validator import RulesetValidator

__version__ = "0.1.0"
__author__ = "Teapot Team"

__all__ = [
    "GameEngine",
    "MatchActor", 
    "Event",
    "Reaction",
    "StackItem",
    "PendingInput",
    "GameState",
    "RulesetIR",
    "ActionDefinition",
    "PhaseDefinition",
    "RulesetValidator",
    "RulesetInterpreter"
]
