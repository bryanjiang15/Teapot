"""
TeapotEngine — Primitive-First Game Runtime

A domain-agnostic game engine. The only concrete primitives are GAME,
PLAYER, OBJECT, and CONTAINER. All game-specific concepts (turns, health,
cards, damage) are expressed as properties and events inside AI-generated
lifecycle scripts.

Quick start
-----------
    from TeapotEngine import MatchActor, RulesetLoader

    loader = RulesetLoader()
    ruleset = loader.from_api_response(api_json)

    actor = MatchActor(match_id="game-1", ruleset=ruleset, player_ids=["alice", "bob"])
    result = actor.begin_game()

    # When result == GameLoopResult.WAITING_FOR_INPUT:
    pending = actor.get_pending_input()   # {"prompt": ..., "options": [...]}
    result = actor.submit_input(answer=pending["options"][0])
"""

from .core.MatchActor import MatchActor
from .core.GameLoopResult import GameLoopResult
from .core.GameAPI import GameAPI, ObjectView
from .core.ScriptRunner import ScriptRunner, ScriptValidationError
from .core.GameState import GameState
from .core.Component import ComponentInstance

from .ruleset.IR import RulesetIR
from .ruleset.ScriptedComponent import ScriptedComponent, ComponentKind
from .ruleset.RulesetModels import VisibilityType
from .ruleset.Validator import RulesetValidator
from .ruleset.system_models.SystemEvent import SYSTEM_EVENTS

from .loader.RulesetLoader import RulesetLoader, RulesetLoadError

__version__ = "2.0.0"
__author__ = "Teapot Team"

__all__ = [
    # Engine
    "MatchActor",
    "GameLoopResult",
    "GameAPI",
    "ObjectView",
    "ScriptRunner",
    "ScriptValidationError",
    "GameState",
    "ComponentInstance",
    # Ruleset
    "RulesetIR",
    "ScriptedComponent",
    "ComponentKind",
    "VisibilityType",
    "RulesetValidator",
    "SYSTEM_EVENTS",
    # Loader
    "RulesetLoader",
    "RulesetLoadError",
]
