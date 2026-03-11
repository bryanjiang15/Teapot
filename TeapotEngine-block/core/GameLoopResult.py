from enum import Enum


class GameLoopResult(Enum):
    """Why the game loop stopped"""
    WAITING_FOR_INPUT = "waiting_for_input"
    GAME_ENDED = "game_ended"
    PHASE_WAITING_FOR_ACTION = "phase_waiting_for_action"