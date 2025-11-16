from enum import Enum


class ZoneVisibilityType(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    SHARED = "shared"

class PhaseExitType(str, Enum):
    EXIT_ON_NO_ACTIONS = "exit_on_no_actions"
    USER_EXIT = "user_exit"

class SelectableObjectType(str, Enum):
    CARD = "card"
    ZONE = "zone"
    PLAYER = "player"
    STACK_ABILITY = "stack_ability"