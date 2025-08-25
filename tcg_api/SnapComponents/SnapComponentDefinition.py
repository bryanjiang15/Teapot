from pydantic import BaseModel
from SnapComponents.SnapComponent import SnapComponentType
from abilityDefinitions import *

class SnapComponentDefinition(BaseModel):
    componentType: SnapComponentType

class SnapActionDefinition(SnapComponentDefinition):
    effect: EffectType
    amount: AmountData
    targetDefinition: TargetData

    def __str__(self) -> str:
        return f"Effect: {self.effect} on {self.targetDefinition}"

class SnapConditionDefinition(SnapComponentDefinition):
    requirement: AbilityRequirement
    requirementTarget: TargetData

    def __str__(self) -> str:
        return f"Condition: {self.requirement}"

class SnapTriggerDefinition(SnapComponentDefinition):
    trigger: AbilityTrigger

    def __str__(self) -> str:
        return f"Trigger: {self.trigger}"
