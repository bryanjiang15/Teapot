"""
TeapotEngine - Shared Game Logic Library

A flexible, ruleset-driven game engine for TCG games.
Supports event sourcing, reaction systems, and dynamic rulesets.
"""

from .ruleset.IR import RulesetIR, ActionDefinition, PhaseDefinition
from .ruleset.Validator import RulesetValidator
from .core import GameEngine, MatchActor, Event, Reaction, StackItem, PendingInput, GameState, RulesetInterpreter

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
