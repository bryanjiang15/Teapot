from TeapotEngine.ruleset.ExpressionModel import Eq, EvalContext, Func, Predicate
from TeapotEngine.ruleset.rule_definitions.EffectDefinition import EffectDefinition
from TeapotEngine.ruleset.rule_definitions.RuleDefinition import TriggerDefinition
from TeapotEngine.ruleset.state_watcher import TriggerType
from TeapotEngine.ruleset.system_models.SystemEvent import *

SYSTEM_TRIGGERS = [
    TriggerDefinition(
        when={"eventType": PHASE_ENDED},
        effects=[
            EffectDefinition(
                kind="emit_event",
                event_type=NEXT_PHASE,
            )
        ]
    ),
    TriggerDefinition(
        when={"eventType": TURN_ENDED},
        effects=[
            EffectDefinition(
                kind="emit_event",
                event_type=NEXT_TURN,
            )
        ]
    )
]

# State-based action watchers - checked after stack empties
# TODO: Add system state watchers when predicate support is expanded
# Example watchers to add:
# - Phase exit when no actions available (requires "no_available_actions" predicate)
# - Player loss at 0 life (requires resource comparison predicate)
# - Component death at 0 health (requires property comparison predicate)

def check_if_phase_can_exit(ctx: EvalContext) -> bool:
    game = ctx.game

SYSTEM_STATE_WATCHERS = [
    # Currently empty - phase exit is handled by check_if_phase_can_exit() in MatchActor
    # State watchers can be added to GameComponent or other components via their triggers list
    TriggerDefinition(
        trigger_type=TriggerType.STATE_BASED,
        condition=Func(
        )
    )
]