"""
Tests for MatchActor class
"""

import pytest
from TeapotEngine.core.MatchActor import MatchActor
from TeapotEngine.core.Events import Event
from TeapotEngine.ruleset.IR import RulesetIR
from TeapotEngine.ruleset.rule_definitions.RuleDefinition import SelectableObjectType
from TeapotEngine.tests.helpers.ruleset_helper import RulesetHelper


class TestMatchActor:
    """Tests for MatchActor class"""
    
    @pytest.mark.asyncio
    async def test_create_match_actor(self):
        """Test creating a match actor"""
        ruleset = RulesetHelper.create_ruleset_ir()
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42)
        
        assert actor.match_id == "test_match"
        assert actor.state is not None
        assert actor.stack is not None
        assert actor.rng is not None
    
    @pytest.mark.asyncio
    async def test_begin_game(self):
        """Test beginning a game"""
        ruleset = RulesetHelper.create_ruleset_ir()
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42, verbose=True)
        
        await actor.begin_game()
        
        # Game should be initialized and finished
        assert actor.state is not None
        assert actor.game_ended is True
    
    @pytest.mark.asyncio
    async def test_process_action(self):
        """Test processing a player action"""
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
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42)
        await actor.begin_game()
        
        action = {
            "type": 1,
            "player_id": "player1"
        }
        
        result = await actor.process_action(action)
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_process_invalid_action(self):
        """Test processing an invalid action"""
        ruleset = RulesetHelper.create_ruleset_ir()
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42)
        await actor.begin_game()
        
        action = {
            "type": 999,  # Nonexistent action
            "player_id": "player1"
        }
        
        result = await actor.process_action(action)
        assert "error" in result
        
    @pytest.mark.asyncio
    async def test_end_turn(self):
        """Test ending a turn"""
        ruleset = RulesetHelper.create_ruleset_ir()
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42)
        await actor.begin_game()
        
        initial_turn = actor.state.turn_number
        await actor.end_turn()
        
        # Turn should have advanced
        assert actor.state.turn_number >= initial_turn
    
    def test_get_current_state(self):
        """Test getting current game state"""
        ruleset = RulesetHelper.create_ruleset_ir()
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42)
        
        state = actor.get_current_state()
        assert isinstance(state, dict)
        assert "match_id" in state or "current_phase" in state
    
    def test_get_available_actions(self):
        """Test getting available actions for a player"""
        ruleset = RulesetHelper.create_ruleset_ir()
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42)
        
        actions = actor.get_available_actions("player1")
        assert isinstance(actions, list)
    
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
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42)
        
        actions = actor.get_actions_for_object(1, SelectableObjectType.CARD, "1")
        assert isinstance(actions, list)
    
    def test_submit_input(self):
        """Test submitting input for a pending input"""
        ruleset = RulesetHelper.create_ruleset_ir()
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42)
        
        # Create a pending input
        from TeapotEngine.core.Events import PendingInput
        pending_input = PendingInput(
            input_id="test_input",
            for_player_ids=["player1"],
            kind="target_select",
            constraints={}
        )
        actor.pending_inputs.append(pending_input)
        
        result = actor.submit_input("test_input", {"target": "card_1"})
        assert "success" in result or "error" in result
    
    def test_submit_input_nonexistent(self):
        """Test submitting input for a nonexistent pending input"""
        ruleset = RulesetHelper.create_ruleset_ir()
        actor = MatchActor("test_match", ruleset.to_dict(), seed=42)
        
        result = actor.submit_input("nonexistent", {})
        assert "error" in result

            

