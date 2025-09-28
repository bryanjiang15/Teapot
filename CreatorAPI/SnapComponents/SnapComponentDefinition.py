from pydantic import BaseModel, Field
from typing import Union, Literal, List
from SnapComponents.SnapComponent import SnapComponentType
from abilityDefinitions import *

class SnapComponentDefinition(BaseModel):
    componentType: SnapComponentType
    
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "allow"
    }

class SnapActionDefinition(SnapComponentDefinition):
    componentType: Literal[SnapComponentType.Action] = SnapComponentType.Action
    effect: EffectType
    amount: AmountData
    targetDefinition: List[TargetData]

    def __str__(self) -> str:
        return f"Effect: {self.effect} on {self.targetDefinition}"

class SnapConditionDefinition(SnapComponentDefinition):
    componentType: Literal[SnapComponentType.IF, SnapComponentType.WHILE]
    requirement: AbilityRequirement
    requirementTarget: TargetData

    def __str__(self) -> str:
        return f"Condition: {self.requirement}"

class SnapTriggerDefinition(SnapComponentDefinition):
    componentType: Literal[SnapComponentType.TRIGGER] = SnapComponentType.TRIGGER
    trigger: AbilityTrigger

    def __str__(self) -> str:
        return f"Trigger: {self.trigger}"

# Simple union type - no discriminator needed
SnapComponentUnion = Union[SnapActionDefinition, SnapConditionDefinition, SnapTriggerDefinition, SnapComponentDefinition]
