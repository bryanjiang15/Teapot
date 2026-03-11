"""
Tests for EventBus and TriggerSubscription classes
"""

import pytest
from TeapotEngine.core.EventBus import EventBus, TriggerSubscription
from TeapotEngine.core.Events import Event, Reaction
from TeapotEngine.core.Component import Component, ComponentStatus
from TeapotEngine.ruleset.rule_definitions.RuleDefinition import TriggerDefinition
from TeapotEngine.ruleset.ComponentDefinition import ComponentType
from TeapotEngine.tests.helpers.ruleset_helper import RulesetHelper


class TestTriggerSubscription:
    """Tests for TriggerSubscription class"""
    
    def test_create_subscription(self):
        """Test creating a trigger subscription"""
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "PhaseEntered"},
            execute_rules=[1]
        )
        subscription = TriggerSubscription(
            id=1,
            event_type="PhaseEntered",
            trigger=trigger,
            component_id=10,
            metadata={"priority": 1}
        )
        assert subscription.id == 1
        assert subscription.event_type == "PhaseEntered"
        assert subscription.trigger.id == 1
        assert subscription.component_id == 10
        assert subscription.metadata == {"priority": 1}


class TestEventBus:
    """Tests for EventBus class"""
    
    def test_create_event_bus(self):
        """Test creating an event bus"""
        bus = EventBus()
        assert bus.get_subscription_count() == 0
    
    def test_subscribe(self):
        """Test subscribing to an event type"""
        bus = EventBus()
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "PhaseEntered"},
            execute_rules=[1]
        )
        
        subscription_id = bus.subscribe("PhaseEntered", trigger, component_id=1)
        assert subscription_id == 1
        assert bus.get_subscription_count() == 1
    
    def test_subscribe_multiple(self):
        """Test subscribing multiple triggers"""
        bus = EventBus()
        trigger1 = TriggerDefinition(id=1, when={"eventType": "PhaseEntered"}, execute_rules=[1])
        trigger2 = TriggerDefinition(id=2, when={"eventType": "PhaseExited"}, execute_rules=[2])
        
        id1 = bus.subscribe("PhaseEntered", trigger1, component_id=1)
        id2 = bus.subscribe("PhaseExited", trigger2, component_id=2)
        
        assert id1 == 1
        assert id2 == 2
        assert bus.get_subscription_count() == 2
    
    def test_unsubscribe(self):
        """Test unsubscribing from an event type"""
        bus = EventBus()
        trigger = TriggerDefinition(id=1, when={"eventType": "PhaseEntered"}, execute_rules=[1])
        subscription_id = bus.subscribe("PhaseEntered", trigger, component_id=1)
        
        result = bus.unsubscribe(subscription_id)
        assert result is True
        assert bus.get_subscription_count() == 0
    
    def test_unsubscribe_nonexistent(self):
        """Test unsubscribing a nonexistent subscription"""
        bus = EventBus()
        result = bus.unsubscribe(999)
        assert result is False
    
    def test_unsubscribe_all_from_component(self):
        """Test unsubscribing all triggers from a component"""
        bus = EventBus()
        trigger1 = TriggerDefinition(id=1, when={"eventType": "PhaseEntered"}, execute_rules=[1])
        trigger2 = TriggerDefinition(id=2, when={"eventType": "PhaseExited"}, execute_rules=[2])
        
        bus.subscribe("PhaseEntered", trigger1, component_id=1)
        bus.subscribe("PhaseExited", trigger2, component_id=1)
        bus.subscribe("PhaseEntered", trigger1, component_id=2)
        
        assert bus.get_subscription_count() == 3
        removed_ids = bus.unsubscribe_all_from_component(1)
        assert len(removed_ids) == 2
        assert bus.get_subscription_count() == 1
    
    def test_get_subscriptions_for_component(self):
        """Test getting all subscriptions for a component"""
        bus = EventBus()
        trigger = TriggerDefinition(id=1, when={"eventType": "PhaseEntered"}, execute_rules=[1])
        
        bus.subscribe("PhaseEntered", trigger, component_id=1)
        bus.subscribe("PhaseEntered", trigger, component_id=1)
        
        subscriptions = bus.get_subscriptions_for_component(1)
        assert len(subscriptions) == 2
        assert all(sub.component_id == 1 for sub in subscriptions)
    
    def test_get_all_subscriptions(self):
        """Test getting all subscriptions"""
        bus = EventBus()
        trigger = TriggerDefinition(id=1, when={"eventType": "PhaseEntered"}, execute_rules=[1])
        
        bus.subscribe("PhaseEntered", trigger, component_id=1)
        bus.subscribe("PhaseExited", trigger, component_id=2)
        
        all_subs = bus.get_all_subscriptions()
        assert "PhaseEntered" in all_subs
        assert "PhaseExited" in all_subs
        assert len(all_subs["PhaseEntered"]) == 1
        assert len(all_subs["PhaseExited"]) == 1
    
    def test_dispatch_matching_event(self):
        """Test dispatching an event that matches a trigger"""
        bus = EventBus()
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "PhaseEntered", "filters": {"phase_id": 1}},
            execute_rules=[1]
        )
        
        # Create a mock game state with component manager
        class MockGameState:
            def __init__(self):
                from core.Component import ComponentManager
                self.component_manager = ComponentManager()
                component = Component(
                    id=1,
                    definition_id=1,
                    name="Test Component",
                    component_type=ComponentType.CARD
                )
                self.component_manager._components[1] = component
        
        game_state = MockGameState()
        bus.subscribe("PhaseEntered", trigger, component_id=1)
        
        event = Event(
            type="PhaseEntered",
            payload={"phase_id": 1}
        )
        
        reactions = bus.dispatch(event, game_state)
        assert len(reactions) == 1
        assert reactions[0].effects == [1]
    
    def test_dispatch_non_matching_event(self):
        """Test dispatching an event that doesn't match any triggers"""
        bus = EventBus()
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "PhaseEntered", "filters": {"phase_id": 1}},
            execute_rules=[1]
        )
        
        class MockGameState:
            def __init__(self):
                from core.Component import ComponentManager
                self.component_manager = ComponentManager()
        
        game_state = MockGameState()
        bus.subscribe("PhaseEntered", trigger, component_id=1)
        
        event = Event(
            type="PhaseEntered",
            payload={"phase_id": 2}  # Different phase_id
        )
        
        reactions = bus.dispatch(event, game_state)
        assert len(reactions) == 0
    
    def test_dispatch_wildcard_subscription(self):
        """Test dispatching to wildcard subscriptions"""
        bus = EventBus()
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "*"},
            execute_rules=[1]
        )
        
        class MockGameState:
            def __init__(self):
                from core.Component import ComponentManager
                self.component_manager = ComponentManager()
                component = Component(
                    id=1,
                    definition_id=1,
                    name="Test Component",
                    component_type=ComponentType.CARD
                )
                self.component_manager._components[1] = component
        
        game_state = MockGameState()
        bus.subscribe("*", trigger, component_id=1)
        
        event = Event(type="AnyEvent", payload={})
        reactions = bus.dispatch(event, game_state)
        assert len(reactions) == 1
    
    def test_get_next_subscription_id(self):
        """Test getting the next subscription ID"""
        bus = EventBus()
        assert bus.get_next_subscription_id() == 1
        
        trigger = TriggerDefinition(id=1, when={"eventType": "Test"}, execute_rules=[1])
        bus.subscribe("Test", trigger, component_id=1)
        
        assert bus.get_next_subscription_id() == 2
    
    def test_subscription_id_auto_increment(self):
        """Test that subscription IDs auto-increment"""
        bus = EventBus()
        trigger = TriggerDefinition(id=1, when={"eventType": "Test"}, execute_rules=[1])
        
        id1 = bus.subscribe("Test", trigger, component_id=1)
        id2 = bus.subscribe("Test", trigger, component_id=2)
        id3 = bus.subscribe("Test", trigger, component_id=3)
        
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

