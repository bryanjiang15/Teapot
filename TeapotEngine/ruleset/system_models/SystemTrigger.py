from TeapotEngine.ruleset.rule_definitions.RuleDefinition import TriggerDefinition
from TeapotEngine.ruleset.system_models.SystemEvent import *

SYSTEM_TRIGGERS = [
    TriggerDefinition(
        id=0,
        when={"eventType": PHASE_STARTED},
        execute_rules=[1]
    )
]