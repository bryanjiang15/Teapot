# Phase events
PHASE_STARTED = "PhaseStarted" #notification
PHASE_END_REQUESTED = "PhaseEndRequested"
PHASE_ENDED = "PhaseEnded" #notification
NEXT_PHASE = "NextPhase"
TURN_STARTED = "TurnStarted" #notification
TURN_END_REQUESTED = "TurnEndRequested"
TURN_ENDED = "TurnEnded" #notification
NEXT_TURN = "NextTurn"
END_GAME = "EndGame"
GAME_ENDED = "GameEnded" #notification

# Action/Rule events
EXECUTE_ACTION = "ExecuteAction"
ACTION_EXECUTED = "ActionExecuted"
RULE_EXECUTED = "RuleExecuted"

# State change events (emitted by rule effects)
CARD_MOVED = "CardMoved"
RESOURCE_CHANGED = "ResourceChanged"
DAMAGE_DEALT = "DamageDealt"