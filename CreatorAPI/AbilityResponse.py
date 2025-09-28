
from pydantic import BaseModel
from SnapComponents.SnapComponentDefinition import *
from abilityDefinitions import *

class AbilityRequest(BaseModel):
    abilityDescription: str
    cardDescription: str

class AbilityDefinition(BaseModel):
    triggerDefinition: SnapTriggerDefinition
    snapComponentDefinitions: list[SnapComponentUnion]

class AbilityResponse(BaseModel):
    AbilityDefinition: AbilityDefinition
    CardArtUrl: str