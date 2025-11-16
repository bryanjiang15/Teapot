"""
Tests for EventRegistry and ReactionRegistry classes
"""

import pytest
from TeapotEngine.core.registry import EventRegistry, ReactionRegistry
from TeapotEngine.core.events import Event, Reaction, EventStatus


class TestEventRegistry:
    """Tests for EventRegistry class"""
    
    def test_create_registry(self):
        """Test creating an event registry"""
        registry = EventRegistry()
        assert registry.size() == 0
    
    def test_register_event(self):
        """Test registering an event"""
        registry = EventRegistry()
        event = Event(type="TestEvent", payload={})
        
        event_id = registry.register(event)
        assert event_id == 1
        assert event.id == 1
        assert registry.size() == 1
    
    def test_register_multiple_events(self):
        """Test registering multiple events"""
        registry = EventRegistry()
        event1 = Event(type="Event1", payload={})
        event2 = Event(type="Event2", payload={})
        
        id1 = registry.register(event1)
        id2 = registry.register(event2)
        
        assert id1 == 1
        assert id2 == 2
        assert registry.size() == 2
    
    def test_get_event(self):
        """Test retrieving an event by ID"""
        registry = EventRegistry()
        event = Event(type="TestEvent", payload={"test": "value"})
        event_id = registry.register(event)
        
        retrieved = registry.get(event_id)
        assert retrieved is not None
        assert retrieved.id == event_id
        assert retrieved.type == "TestEvent"
        assert retrieved.payload == {"test": "value"}
    
    def test_get_nonexistent_event(self):
        """Test retrieving a nonexistent event"""
        registry = EventRegistry()
        retrieved = registry.get(999)
        assert retrieved is None
    
    def test_unregister_event(self):
        """Test unregistering an event"""
        registry = EventRegistry()
        event = Event(type="TestEvent", payload={})
        event_id = registry.register(event)
        
        assert registry.size() == 1
        registry.unregister(event_id)
        assert registry.size() == 0
        assert registry.get(event_id) is None
    
    def test_unregister_nonexistent_event(self):
        """Test unregistering a nonexistent event"""
        registry = EventRegistry()
        # Should not raise an error
        registry.unregister(999)
        assert registry.size() == 0
    
    def test_clear_registry(self):
        """Test clearing all events"""
        registry = EventRegistry()
        registry.register(Event(type="Event1", payload={}))
        registry.register(Event(type="Event2", payload={}))
        
        assert registry.size() == 2
        registry.clear()
        assert registry.size() == 0


class TestReactionRegistry:
    """Tests for ReactionRegistry class"""
    
    def test_create_registry(self):
        """Test creating a reaction registry"""
        registry = ReactionRegistry()
        assert registry.size() == 0
    
    def test_register_reaction(self):
        """Test registering a reaction"""
        registry = ReactionRegistry()
        reaction = Reaction(when={"eventType": "TestEvent"}, effects=[1])
        
        reaction_id = registry.register(reaction)
        assert reaction_id == 1
        assert reaction.id == 1
        assert registry.size() == 1
    
    def test_register_multiple_reactions(self):
        """Test registering multiple reactions"""
        registry = ReactionRegistry()
        reaction1 = Reaction(when={"eventType": "Event1"}, effects=[1])
        reaction2 = Reaction(when={"eventType": "Event2"}, effects=[2])
        
        id1 = registry.register(reaction1)
        id2 = registry.register(reaction2)
        
        assert id1 == 1
        assert id2 == 2
        assert registry.size() == 2
    
    def test_get_reaction(self):
        """Test retrieving a reaction by ID"""
        registry = ReactionRegistry()
        reaction = Reaction(
            when={"eventType": "TestEvent"},
            effects=[1, 2],
            timing="post"
        )
        reaction_id = registry.register(reaction)
        
        retrieved = registry.get(reaction_id)
        assert retrieved is not None
        assert retrieved.id == reaction_id
        assert retrieved.when == {"eventType": "TestEvent"}
        assert retrieved.effects == [1, 2]
        assert retrieved.timing == "post"
    
    def test_get_nonexistent_reaction(self):
        """Test retrieving a nonexistent reaction"""
        registry = ReactionRegistry()
        retrieved = registry.get(999)
        assert retrieved is None
    
    def test_unregister_reaction(self):
        """Test unregistering a reaction"""
        registry = ReactionRegistry()
        reaction = Reaction(when={"eventType": "TestEvent"}, effects=[1])
        reaction_id = registry.register(reaction)
        
        assert registry.size() == 1
        registry.unregister(reaction_id)
        assert registry.size() == 0
        assert registry.get(reaction_id) is None
    
    def test_unregister_nonexistent_reaction(self):
        """Test unregistering a nonexistent reaction"""
        registry = ReactionRegistry()
        # Should not raise an error
        registry.unregister(999)
        assert registry.size() == 0
    
    def test_clear_registry(self):
        """Test clearing all reactions"""
        registry = ReactionRegistry()
        registry.register(Reaction(when={"eventType": "Event1"}, effects=[1]))
        registry.register(Reaction(when={"eventType": "Event2"}, effects=[2]))
        
        assert registry.size() == 2
        registry.clear()
        assert registry.size() == 0

