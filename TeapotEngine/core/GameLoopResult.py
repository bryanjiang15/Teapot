from enum import Enum


class GameLoopResult(Enum):
    """Why the game loop stopped running."""
    WAITING_FOR_INPUT = "waiting_for_input"   # a script called wait_for_input()
    GAME_ENDED        = "game_ended"          # a script called end_game()
