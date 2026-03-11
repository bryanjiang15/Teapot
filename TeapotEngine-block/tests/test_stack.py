"""
Tests for EventStack class
"""

import pytest
from TeapotEngine.core.Stack import EventStack
from TeapotEngine.core.Events import StackItem, StackItemType


class TestEventStack:
    """Tests for EventStack class"""
    
    def test_create_stack(self):
        """Test creating an empty stack"""
        stack = EventStack()
        assert stack.is_empty()
        assert stack.size() == 0
    
    def test_push_item(self):
        """Test pushing an item onto the stack"""
        stack = EventStack()
        item = StackItem(
            kind=StackItemType.EVENT,
            ref_id=1,
            created_at_order=1
        )
        stack.push(item)
        assert not stack.is_empty()
        assert stack.size() == 1
    
    def test_pop_item(self):
        """Test popping an item from the stack"""
        stack = EventStack()
        item = StackItem(
            kind=StackItemType.EVENT,
            ref_id=1,
            created_at_order=1
        )
        stack.push(item)
        
        popped = stack.pop()
        assert popped is not None
        assert popped.ref_id == 1
        assert stack.is_empty()
        assert stack.size() == 0
    
    def test_pop_from_empty_stack(self):
        """Test popping from an empty stack"""
        stack = EventStack()
        popped = stack.pop()
        assert popped is None
    
    def test_peek_item(self):
        """Test peeking at the top item without removing it"""
        stack = EventStack()
        item = StackItem(
            kind=StackItemType.EVENT,
            ref_id=2,
            created_at_order=2
        )
        stack.push(item)
        
        peeked = stack.peek()
        assert peeked is not None
        assert peeked.ref_id == 2
        assert stack.size() == 1  # Item still on stack
    
    def test_peek_empty_stack(self):
        """Test peeking at an empty stack"""
        stack = EventStack()
        peeked = stack.peek()
        assert peeked is None
    
    def test_lifo_ordering(self):
        """Test that stack follows LIFO ordering"""
        stack = EventStack()
        item1 = StackItem(kind=StackItemType.EVENT, ref_id=1, created_at_order=1)
        item2 = StackItem(kind=StackItemType.EVENT, ref_id=2, created_at_order=2)
        item3 = StackItem(kind=StackItemType.EVENT, ref_id=3, created_at_order=3)
        
        stack.push(item1)
        stack.push(item2)
        stack.push(item3)
        
        # Should pop in reverse order
        assert stack.pop().ref_id == 3
        assert stack.pop().ref_id == 2
        assert stack.pop().ref_id == 1
        assert stack.is_empty()
    
    def test_push_multiple(self):
        """Test pushing multiple items at once"""
        stack = EventStack()
        items = [
            StackItem(kind=StackItemType.EVENT, ref_id=1, created_at_order=1),
            StackItem(kind=StackItemType.EVENT, ref_id=2, created_at_order=2),
            StackItem(kind=StackItemType.EVENT, ref_id=3, created_at_order=3)
        ]
        stack.push_multiple(items)
        
        assert stack.size() == 3
        # Should be in order (last pushed is on top)
        assert stack.pop().ref_id == 3
        assert stack.pop().ref_id == 2
        assert stack.pop().ref_id == 1
    
    def test_get_next_order(self):
        """Test getting next order number"""
        stack = EventStack()
        order1 = stack.get_next_order()
        order2 = stack.get_next_order()
        order3 = stack.get_next_order()
        
        assert order1 == 1
        assert order2 == 2
        assert order3 == 3
    
    def test_clear_stack(self):
        """Test clearing the stack"""
        stack = EventStack()
        stack.push(StackItem(kind=StackItemType.EVENT, ref_id=1, created_at_order=1))
        stack.push(StackItem(kind=StackItemType.EVENT, ref_id=2, created_at_order=2))
        
        assert stack.size() == 2
        stack.clear()
        assert stack.is_empty()
        assert stack.size() == 0
    
    def test_mixed_item_types(self):
        """Test stack with both event and reaction items"""
        stack = EventStack()
        event_item = StackItem(kind=StackItemType.EVENT, ref_id=1, created_at_order=1)
        reaction_item = StackItem(kind=StackItemType.REACTION, ref_id=2, created_at_order=2)
        
        stack.push(event_item)
        stack.push(reaction_item)
        
        popped = stack.pop()
        assert popped.kind == StackItemType.REACTION
        assert popped.ref_id == 2
        
        popped = stack.pop()
        assert popped.kind == StackItemType.EVENT
        assert popped.ref_id == 1
    
    def test_to_dict(self):
        """Test serializing stack to dictionary"""
        stack = EventStack()
        stack.push(StackItem(kind=StackItemType.EVENT, ref_id=1, created_at_order=1))
        stack.push(StackItem(kind=StackItemType.REACTION, ref_id=2, created_at_order=2, flags={"test": True}))
        
        data = stack.to_dict()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["kind"] == "event"
        assert data[0]["ref_id"] == 1
        assert data[1]["kind"] == "reaction"
        assert data[1]["ref_id"] == 2
        assert data[1]["flags"] == {"test": True}
    
    def test_from_dict(self):
        """Test deserializing stack from dictionary"""
        data = [
            {"kind": "event", "ref_id": 1, "created_at_order": 1, "flags": {}},
            {"kind": "reaction", "ref_id": 2, "created_at_order": 2, "flags": {"test": True}}
        ]
        stack = EventStack.from_dict(data)
        
        assert stack.size() == 2
        item = stack.pop()
        assert item.kind == StackItemType.REACTION
        assert item.ref_id == 2
        assert item.flags == {"test": True}
        
        item = stack.pop()
        assert item.kind == StackItemType.EVENT
        assert item.ref_id == 1

