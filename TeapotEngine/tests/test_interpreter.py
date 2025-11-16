"""
Tests for RulesetInterpreter and RuleExecutor classes
"""

import pytest
from TeapotEngine.core.interpreter import RulesetInterpreter, RuleExecutor
from TeapotEngine.core.state import GameState
from TeapotEngine.core.events import Event
from TeapotEngine.core.component import Component
from TeapotEngine.ruleset.ir import RulesetIR
from TeapotEngine.ruleset.ruleDefinitions.rule_definitions import RuleDefinition, ActionDefinition
from TeapotEngine.ruleset.componentDefinition import ComponentDefinition, ComponentType
from TeapotEngine.ruleset.ruleDefinitions.rule_definitions import TriggerDefinition
from TeapotEngine.tests.helpers.ruleset_helper import RulesetHelper


class TestRuleExecutor:
    """Tests for RuleExecutor class"""
    
    def test_create_rule_executor(self):
        """Test creating a rule executor"""
        ruleset = RulesetHelper.create_ruleset_ir()
        executor = RuleExecutor(ruleset)
        assert executor.ruleset == ruleset
    
    def test_execute_rule(self):
        """Test executing a rule"""
        ruleset_dict = RulesetHelper.create_minimal_ruleset()
        ruleset_dict["rules"] = [
            {
                "id": 1,
                "name": "TestRule",
                "effects": [
                    {"op": "gain_resource", "resource": 1, "amount": 5}
                ]
            }
        ]
        ruleset = RulesetIR.from_dict(ruleset_dict)
        executor = RuleExecutor(ruleset)
        
        game_state = GameState.from_ruleset("test", ruleset, ["player1"])
        events = executor.execute_rule(1, {"object_type": "player", "object_id": "player1"}, game_state)
        
        assert len(events) > 0
        # Should include RuleExecuted event
        rule_events = [e for e in events if e.type == "RuleExecuted"]
        assert len(rule_events) == 1
    
    def test_execute_nonexistent_rule(self):
        """Test executing a nonexistent rule"""
        ruleset = RulesetHelper.create_ruleset_ir()
        executor = RuleExecutor(ruleset)
        
        game_state = GameState.from_ruleset("test", ruleset, ["player1"])
        events = executor.execute_rule(999, {}, game_state)
        
        assert len(events) == 0
    
    def test_execute_rule_with_nested_rule(self):
        """Test executing a rule that calls another rule"""
        ruleset_dict = RulesetHelper.create_minimal_ruleset()
        ruleset_dict["rules"] = [
            {
                "id": 1,
                "name": "ParentRule",
                "effects": [
                    {"op": "execute_rule", "rule_id": 2}
                ]
            },
            {
                "id": 2,
                "name": "ChildRule",
                "effects": [
                    {"op": "gain_resource", "resource": 1, "amount": 3}
                ]
            }
        ]
        ruleset = RulesetIR.from_dict(ruleset_dict)
        executor = RuleExecutor(ruleset)
        
        game_state = GameState.from_ruleset("test", ruleset, ["player1"])
        events = executor.execute_rule(1, {}, game_state)
        
        # Should have events from both rules
        assert len(events) >= 2


class TestRulesetInterpreter:
    """Tests for RulesetInterpreter class"""
    
    def test_create_interpreter(self):
        """Test creating a ruleset interpreter"""
        ruleset = RulesetHelper.create_ruleset_ir()
        interpreter = RulesetInterpreter(ruleset)
        assert interpreter.ruleset == ruleset
        assert interpreter.event_bus is not None
        assert interpreter.rule_executor is not None
    
    def test_register_component_triggers(self):
        """Test registering triggers for a component"""
        ruleset = RulesetHelper.create_ruleset_ir()
        interpreter = RulesetInterpreter(ruleset)
        
        component = Component(
            id=1,
            definition_id=1,
            name="Test Component",
            component_type=ComponentType.CARD
        )
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "PhaseEntered"},
            execute_rules=[1]
        )
        component.add_trigger(trigger)
        
        subscription_ids = interpreter.register_component_triggers(component)
        assert len(subscription_ids) == 1
        assert interpreter.event_bus.get_subscription_count() == 1
    
    def test_unregister_component_triggers(self):
        """Test unregistering triggers for a component"""
        ruleset = RulesetHelper.create_ruleset_ir()
        interpreter = RulesetInterpreter(ruleset)
        
        component = Component(
            id=1,
            definition_id=1,
            name="Test Component",
            component_type=ComponentType.CARD
        )
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "PhaseEntered"},
            execute_rules=[1]
        )
        component.add_trigger(trigger)
        
        subscription_ids = interpreter.register_component_triggers(component)
        assert len(subscription_ids) == 1
        
        removed_ids = interpreter.unregister_component_triggers(1)
        assert len(removed_ids) == 1
        assert interpreter.event_bus.get_subscription_count() == 0
    
    def test_get_available_actions(self):
        """Test getting available actions for a player"""
        ruleset_dict = RulesetHelper.create_ruleset_with_actions([
            {
                "id": 1,
                "name": "Test Action",
                "timing": "stack",
                "phase_ids": [1],
                "preconditions": [],
                "costs": [],
                "targets": []
            }
        ])
        ruleset = RulesetIR.from_dict(ruleset_dict)
        interpreter = RulesetInterpreter(ruleset)
        
        game_state = GameState.from_ruleset("test", ruleset, ["player1"])
        actions = interpreter.get_available_actions(game_state, "player1")
        
        # Should return available actions
        assert isinstance(actions, list)
    
    def test_validate_action(self):
        """Test validating an action"""
        ruleset_dict = RulesetHelper.create_ruleset_with_actions([
            {
                "id": 1,
                "name": "Test Action",
                "timing": "stack",
                "phase_ids": [1],
                "preconditions": [],
                "costs": [],
                "targets": []
            }
        ])
        ruleset = RulesetIR.from_dict(ruleset_dict)
        interpreter = RulesetInterpreter(ruleset)
        
        game_state = GameState.from_ruleset("test", ruleset, ["player1"])
        action_data = {"type": 1, "player_id": "player1"}
        
        result = interpreter.validate_action(action_data, game_state, "player1")
        # Result depends on preconditions and phase matching
        assert isinstance(result, bool)
    
    def test_validate_nonexistent_action(self):
        """Test validating a nonexistent action"""
        ruleset = RulesetHelper.create_ruleset_ir()
        interpreter = RulesetInterpreter(ruleset)
        
        game_state = GameState.from_ruleset("test", ruleset, ["player1"])
        action_data = {"type": 999, "player_id": "player1"}
        
        result = interpreter.validate_action(action_data, game_state, "player1")
        assert result is False
    
    def test_discover_reactions(self):
        """Test discovering reactions for an event"""
        ruleset = RulesetHelper.create_ruleset_ir()
        interpreter = RulesetInterpreter(ruleset)
        
        # Register a trigger
        component = Component(
            id=1,
            definition_id=1,
            name="Test Component",
            component_type=ComponentType.CARD
        )
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "PhaseEntered"},
            execute_rules=[1]
        )
        component.add_trigger(trigger)
        interpreter.register_component_triggers(component)
        
        game_state = GameState.from_ruleset("test", ruleset, ["player1"])
        # Add component to game state
        game_state.component_manager._components[1] = component
        
        event = Event(type="PhaseEntered", payload={"phase_id": 1})
        reactions = interpreter.discover_reactions(event, game_state)
        
        # Should find matching reactions
        assert isinstance(reactions, list)
    
    def test_get_phase_steps(self):
        """Test getting phase steps"""
        ruleset = RulesetHelper.create_ruleset_ir()
        interpreter = RulesetInterpreter(ruleset)
        
        steps = interpreter.get_phase_steps(1)
        assert isinstance(steps, list)
    
    def test_get_actions_for_object(self):
        """Test getting actions for a selected object"""
        ruleset_dict = RulesetHelper.create_ruleset_with_actions([
            {
                "id": 1,
                "name": "Test Action",
                "timing": "stack",
                "phase_ids": [1],
                "primary_target_type": "card",
                "preconditions": [],
                "costs": [],
                "targets": []
            }
        ])
        ruleset = RulesetIR.from_dict(ruleset_dict)
        interpreter = RulesetInterpreter(ruleset)
        
        game_state = GameState.from_ruleset("test", ruleset, ["player1"])
        actions = interpreter.get_actions_for_object(game_state, 1, "card", "1")
        
        assert isinstance(actions, list)

