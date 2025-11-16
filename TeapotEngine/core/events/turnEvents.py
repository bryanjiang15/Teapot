from ..events import Event, TURN_STARTED, TURN_ENDED

class TurnStarted(Event):
    """Event emitted when a turn starts"""
    
    def __post_init__(self):
        self.type = TURN_STARTED

class TurnEnded(Event):
    """Event emitted when a turn ends"""

    def __post_init__(self):
        self.type = TURN_ENDED
    
    