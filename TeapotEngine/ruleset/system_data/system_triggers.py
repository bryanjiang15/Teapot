from TeapotEngine.ruleset.ruleDefinitions.rule_definitions import TriggerDefinition
from TeapotEngine.ruleset.system_data.system_events import *

SYSTEM_TRIGGERS = [
    TriggerDefinition(
        id=0,
        when={"eventType": PHASE_STARTED},
        execute_rules=[1]
    )
]