"""
Tests for StateWatcherEngine and state-based action functionality
"""

import pytest
from TeapotEngine.core.StateWatcherEngine import StateWatcherEngine
from TeapotEngine.core.GameState import GameState
from TeapotEngine.core.Component import Component, ComponentManager
from TeapotEngine.ruleset.rule_definitions.RuleDefinition import TriggerDefinition
from TeapotEngine.ruleset.rule_definitions.EffectDefinition import EffectDefinition
from TeapotEngine.ruleset.state_watcher import TriggerType
from TeapotEngine.ruleset.ComponentDefinition import ComponentType
from TeapotEngine.ruleset.ExpressionModel import Predicate


class TestTriggerType:
    """Tests for TriggerType enum"""
    
    def test_event_trigger_type(self):
        """Test EVENT trigger type value"""
        assert TriggerType.EVENT.value == "event"
    
    def test_state_based_trigger_type(self):
        """Test STATE_BASED trigger type value"""
        assert TriggerType.STATE_BASED.value == "state"
    
    def test_default_trigger_type(self):
        """Test that default trigger type is EVENT"""
        trigger = TriggerDefinition(id=1, when={"eventType": "Test"})
        assert trigger.trigger_type == TriggerType.EVENT


class TestStateWatcherEngine:
    """Tests for StateWatcherEngine class"""
    
    def test_create_engine(self):
        """Test creating a state watcher engine"""
        engine = StateWatcherEngine()
        assert engine.get_watcher_count() == 0
        assert engine.is_dirty() is False
    
    def test_register_watcher(self):
        """Test registering a state watcher"""
        engine = StateWatcherEngine()
        trigger = TriggerDefinition(
            id=1,
            trigger_type=TriggerType.STATE_BASED,
            condition=None,
            effects=[]
        )
        
        watcher_id = engine.register_watcher(trigger, source_component_id=10)
        assert watcher_id == 1
        assert engine.get_watcher_count() == 1
    
    def test_register_multiple_watchers(self):
        """Test registering multiple state watchers"""
        engine = StateWatcherEngine()
        trigger1 = TriggerDefinition(id=1, trigger_type=TriggerType.STATE_BASED)
        trigger2 = TriggerDefinition(id=2, trigger_type=TriggerType.STATE_BASED)
        
        id1 = engine.register_watcher(trigger1, source_component_id=10)
        id2 = engine.register_watcher(trigger2, source_component_id=20)
        
        assert id1 == 1
        assert id2 == 2
        assert engine.get_watcher_count() == 2
    
    def test_unregister_watchers_from_source(self):
        """Test unregistering all watchers from a source component"""
        engine = StateWatcherEngine()
        trigger1 = TriggerDefinition(id=1, trigger_type=TriggerType.STATE_BASED)
        trigger2 = TriggerDefinition(id=2, trigger_type=TriggerType.STATE_BASED)
        trigger3 = TriggerDefinition(id=3, trigger_type=TriggerType.STATE_BASED)
        
        engine.register_watcher(trigger1, source_component_id=10)
        engine.register_watcher(trigger2, source_component_id=10)
        engine.register_watcher(trigger3, source_component_id=20)
        
        assert engine.get_watcher_count() == 3
        
        removed = engine.unregister_watchers_from_source(10)
        assert len(removed) == 2
        assert engine.get_watcher_count() == 1
    
    def test_unregister_nonexistent_source(self):
        """Test unregistering from a nonexistent source"""
        engine = StateWatcherEngine()
        removed = engine.unregister_watchers_from_source(999)
        assert len(removed) == 0
    
    def test_mark_dirty(self):
        """Test marking state as dirty"""
        engine = StateWatcherEngine()
        assert engine.is_dirty() is False
        
        engine.mark_dirty()
        assert engine.is_dirty() is True
    
    def test_check_watchers_not_dirty(self):
        """Test check_watchers when not dirty returns empty list"""
        engine = StateWatcherEngine()
        trigger = TriggerDefinition(id=1, trigger_type=TriggerType.STATE_BASED)
        engine.register_watcher(trigger, source_component_id=10)
        
        # Create a minimal mock game state
        class MockGameState:
            current_phase = 1
            turn_number = 1
        
        triggered = engine.check_watchers(MockGameState())
        assert len(triggered) == 0
    
    def test_check_watchers_clears_dirty(self):
        """Test that check_watchers clears the dirty flag"""
        engine = StateWatcherEngine()
        engine.mark_dirty()
        assert engine.is_dirty() is True
        
        class MockGameState:
            current_phase = 1
            turn_number = 1
        
        engine.check_watchers(MockGameState())
        assert engine.is_dirty() is False
    
    def test_check_watchers_with_no_condition(self):
        """Test check_watchers with a watcher that has no condition (should not trigger)"""
        engine = StateWatcherEngine()
        trigger = TriggerDefinition(
            id=1,
            trigger_type=TriggerType.STATE_BASED,
            condition=None,  # No condition
            effects=[]
        )
        engine.register_watcher(trigger, source_component_id=10)
        engine.mark_dirty()
        
        class MockGameState:
            current_phase = 1
            turn_number = 1
        
        triggered = engine.check_watchers(MockGameState())
        assert len(triggered) == 0  # No condition means no trigger
    
    def test_get_watchers_for_component(self):
        """Test getting all watchers for a specific component"""
        engine = StateWatcherEngine()
        trigger1 = TriggerDefinition(id=1, trigger_type=TriggerType.STATE_BASED)
        trigger2 = TriggerDefinition(id=2, trigger_type=TriggerType.STATE_BASED)
        
        engine.register_watcher(trigger1, source_component_id=10)
        engine.register_watcher(trigger2, source_component_id=10)
        
        watchers = engine.get_watchers_for_component(10)
        assert len(watchers) == 2
    
    def test_get_watchers_for_nonexistent_component(self):
        """Test getting watchers for a component that has none"""
        engine = StateWatcherEngine()
        watchers = engine.get_watchers_for_component(999)
        assert len(watchers) == 0
    
    def test_clear(self):
        """Test clearing all watchers"""
        engine = StateWatcherEngine()
        trigger = TriggerDefinition(id=1, trigger_type=TriggerType.STATE_BASED)
        engine.register_watcher(trigger, source_component_id=10)
        engine.mark_dirty()
        
        assert engine.get_watcher_count() == 1
        assert engine.is_dirty() is True
        
        engine.clear()
        
        assert engine.get_watcher_count() == 0
        assert engine.is_dirty() is False


class TestTriggerDefinitionStateFields:
    """Tests for TriggerDefinition state-related fields"""
    
    def test_create_event_trigger(self):
        """Test creating an event trigger with default trigger_type"""
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "PhaseEntered"},
            effects=[]
        )
        assert trigger.trigger_type == TriggerType.EVENT
        assert trigger.condition is None
    
    def test_create_state_based_trigger(self):
        """Test creating a state-based trigger"""
        trigger = TriggerDefinition(
            id=1,
            trigger_type=TriggerType.STATE_BASED,
            condition=None,
            effects=[]
        )
        assert trigger.trigger_type == TriggerType.STATE_BASED
    
    def test_serialize_trigger_type(self):
        """Test that trigger_type serializes correctly"""
        trigger = TriggerDefinition(
            id=1,
            trigger_type=TriggerType.STATE_BASED,
            effects=[]
        )
        data = trigger.model_dump()
        assert data["trigger_type"] == "state"
    
    def test_deserialize_trigger_type(self):
        """Test that trigger_type deserializes correctly"""
        data = {
            "id": 1,
            "trigger_type": "state",
            "effects": []
        }
        trigger = TriggerDefinition(**data)
        assert trigger.trigger_type == TriggerType.STATE_BASED

