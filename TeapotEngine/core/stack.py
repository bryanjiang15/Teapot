"""
Event stack management for the game engine
"""

from typing import List, Optional, Dict, Any
from .events import StackItem, Event, Reaction, StackItemType
from .state import GameState


class EventStack:
    """LIFO stack for managing event resolution"""
    
    def __init__(self):
        self.items: List[StackItem] = []
        self.order_counter = 0
    
    def push(self, item: StackItem) -> None:
        """Push an item onto the stack"""
        self.items.append(item)
    
    def push_multiple(self, items: List[StackItem]) -> None:
        """Push multiple items onto the stack (in order)"""
        for item in items:
            self.push(item)
    
    def pop(self) -> Optional[StackItem]:
        """Pop the top item from the stack"""
        if self.is_empty():
            return None
        return self.items.pop()
    
    def peek(self) -> Optional[StackItem]:
        """Peek at the top item without removing it"""
        if self.is_empty():
            return None
        return self.items[-1]
    
    def is_empty(self) -> bool:
        """Check if the stack is empty"""
        return len(self.items) == 0
    
    def size(self) -> int:
        """Get the current stack size"""
        return len(self.items)
    
    def clear(self) -> None:
        """Clear all items from the stack"""
        self.items.clear()
    
    def get_next_order(self) -> int:
        """Get the next order number for stack items"""
        self.order_counter += 1
        return self.order_counter
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Convert stack to dictionary for serialization"""
        return [item.to_dict() for item in self.items]
    
    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> "EventStack":
        """Create stack from dictionary"""
        stack = cls()
        for item_data in data:
            stack.push(StackItem.from_dict(item_data))
        return stack
