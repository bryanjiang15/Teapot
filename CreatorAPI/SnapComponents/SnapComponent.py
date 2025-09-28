from dataclasses import dataclass
from enum import Enum

class SnapComponentType(Enum):
    Action = "Action"
    TRIGGER = "Trigger"
    IF = "If"
    WHILE = "While"
    ELSE = "Else"
    CHOICE = "Choice"
    ENDCONDITION = "EndCondition"

class SnapConditionType(Enum):
    IF = "If"
    WHILE = "While"
    UNTIL = "Until"

@dataclass
class SnapComponent:
    componentType: SnapComponentType
    componentDescription: str