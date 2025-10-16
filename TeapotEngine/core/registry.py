"""
Registry classes for managing event and reaction lifecycle
"""

from typing import Dict, Optional
from .events import Event, Reaction


class EventRegistry:
    """Manages event lifecycle and ID assignment"""
    
    def __init__(self):
        self._counter: int = 0
        self._registry: Dict[int, Event] = {}
    
    def register(self, event: Event) -> int:
        """Assign ID to event, store it, return the ID"""
        self._counter += 1
        event.id = self._counter
        self._registry[event.id] = event
        return event.id
    
    def get(self, event_id: int) -> Optional[Event]:
        """Retrieve event by ID"""
        return self._registry.get(event_id)
    
    def unregister(self, event_id: int) -> None:
        """Remove event from registry after resolution"""
        self._registry.pop(event_id, None)
    
    def clear(self) -> None:
        """Clear all events (for cleanup)"""
        self._registry.clear()
    
    def size(self) -> int:
        """Get number of registered events"""
        return len(self._registry)


class ReactionRegistry:
    """Manages reaction lifecycle and ID assignment"""
    
    def __init__(self):
        self._counter: int = 0
        self._registry: Dict[int, Reaction] = {}
    
    def register(self, reaction: Reaction) -> int:
        """Assign ID to reaction, store it, return the ID"""
        self._counter += 1
        reaction.id = self._counter
        self._registry[reaction.id] = reaction
        return reaction.id
    
    def get(self, reaction_id: int) -> Optional[Reaction]:
        """Retrieve reaction by ID"""
        return self._registry.get(reaction_id)
    
    def unregister(self, reaction_id: int) -> None:
        """Remove reaction from registry after resolution"""
        self._registry.pop(reaction_id, None)
    
    def clear(self) -> None:
        """Clear all reactions (for cleanup)"""
        self._registry.clear()
    
    def size(self) -> int:
        """Get number of registered reactions"""
        return len(self._registry)
