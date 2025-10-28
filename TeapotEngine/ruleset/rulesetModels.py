from enum import Enum


class ZoneVisibilityType(Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    SHARED = "shared"

class PhaseExitType(Enum):
    EXIT_ON_NO_ACTIONS = "exit_on_no_actions"
    USER_EXIT = "user_exit"
    