"""
Tests for PhaseManager class
"""

import pytest
from TeapotEngine.core.PhaseManager import PhaseManager, TurnType
from TeapotEngine.ruleset.rule_definitions.RuleDefinition import TurnStructure, PhaseDefinition, StepDefinition
from TeapotEngine.ruleset.IR import RulesetIR
from TeapotEngine.tests.helpers.ruleset_helper import RulesetHelper


class TestPhaseManager:
    """Tests for PhaseManager class"""
    
    def test_create_phase_manager(self):
        """Test creating a phase manager"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1", "player2"]
        )
        assert manager.turn_number == 1
        assert manager.current_phase_id == 1
        assert manager.active_player == "player1"
    
    def test_advance_phase(self):
        """Test advancing to the next phase"""
        ruleset_dict = RulesetHelper.create_ruleset_with_phases([
            {
                "id": 1,
                "name": "Phase 1",
                "steps": [{"id": 1, "name": "Step 1", "mandatory": True}],
                "exit_type": "exit_on_no_actions"
            },
            {
                "id": 2,
                "name": "Phase 2",
                "steps": [{"id": 2, "name": "Step 2", "mandatory": True}],
                "exit_type": "exit_on_no_actions"
            },
            {
                "id": 3,
                "name": "Phase 3",
                "steps": [{"id": 3, "name": "Step 3", "mandatory": True}],
                "exit_type": "exit_on_no_actions"
            }
        ])
        ruleset = RulesetIR.from_dict(ruleset_dict)
        
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1", "player2"]
        )
        
        # Start at phase 1
        assert manager.current_phase_id == 1
        
        # Advance to phase 2
        next_phase = manager.advance_phase()
        assert next_phase == 2
        assert manager.current_phase_id == 2
        
        # Advance to phase 3
        next_phase = manager.advance_phase()
        assert next_phase == 3
        assert manager.current_phase_id == 3
        
        # Advance past last phase (end of turn)
        next_phase = manager.advance_phase()
        assert next_phase is None
    
    def test_advance_turn(self):
        """Test advancing to the next turn"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1", "player2"]
        )
        
        initial_turn = manager.turn_number
        initial_phase = manager.current_phase_id
        initial_player = manager.active_player
        
        new_turn = manager.advance_turn()
        assert new_turn == initial_turn + 1
        assert manager.turn_number == initial_turn + 1
        assert manager.current_phase_id == initial_phase  # Reset to initial phase
        assert manager.active_player != initial_player  # Rotated
    
    def test_advance_turn_synchronous(self):
        """Test advancing turn in synchronous mode (no player rotation)"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SYNCHRONOUS,
            player_ids=["player1", "player2"]
        )
        
        initial_player = manager.active_player
        manager.advance_turn()
        # In synchronous mode, active player should stay the same
        assert manager.active_player == initial_player
    
    def test_get_next_phase(self):
        """Test getting next phase without advancing"""
        ruleset_dict = RulesetHelper.create_ruleset_with_phases([
            {
                "id": 1,
                "name": "Phase 1",
                "steps": [{"id": 1, "name": "Step 1", "mandatory": True}],
                "exit_type": "exit_on_no_actions"
            },
            {
                "id": 2,
                "name": "Phase 2",
                "steps": [{"id": 2, "name": "Step 2", "mandatory": True}],
                "exit_type": "exit_on_no_actions"
            }
        ])
        ruleset = RulesetIR.from_dict(ruleset_dict)
        
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1"]
        )
        
        next_phase = manager.get_next_phase()
        assert next_phase == 2
        assert manager.current_phase_id == 1  # Should not have advanced
    
    def test_get_next_phase_at_end(self):
        """Test getting next phase at end of turn"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1"]
        )
        
        # Advance past last phase
        manager.advance_phase()
        next_phase = manager.get_next_phase()
        assert next_phase is None
    
    def test_get_current_phase_info(self):
        """Test getting current phase definition"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1"]
        )
        
        phase_info = manager.get_current_phase_info()
        assert phase_info is not None
        assert phase_info.id == manager.current_phase_id
        assert phase_info.name == "Main Phase"
    
    def test_get_phase_by_id(self):
        """Test getting phase by ID"""
        ruleset_dict = RulesetHelper.create_ruleset_with_phases([
            {
                "id": 10,
                "name": "Custom Phase",
                "steps": [{"id": 1, "name": "Step", "mandatory": True}],
                "exit_type": "exit_on_no_actions"
            }
        ])
        ruleset = RulesetIR.from_dict(ruleset_dict)
        
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1"]
        )
        
        phase = manager.get_phase_by_id(10)
        assert phase is not None
        assert phase.id == 10
        assert phase.name == "Custom Phase"
    
    def test_get_nonexistent_phase(self):
        """Test getting a nonexistent phase"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1"]
        )
        
        phase = manager.get_phase_by_id(999)
        assert phase is None
    
    def test_can_exit_phase_exit_on_no_actions(self):
        """Test can_exit_phase for exit_on_no_actions type"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1"]
        )
        
        # Mock game state
        class MockGameState:
            pass
        
        game_state = MockGameState()
        can_exit = manager.can_exit_phase(game_state)
        assert can_exit is True
    
    def test_can_exit_phase_user_exit(self):
        """Test can_exit_phase for user_exit type"""
        ruleset_dict = RulesetHelper.create_ruleset_with_phases([
            {
                "id": 1,
                "name": "User Exit Phase",
                "steps": [{"id": 1, "name": "Step", "mandatory": True}],
                "exit_type": "user_exit"
            }
        ])
        ruleset = RulesetIR.from_dict(ruleset_dict)
        
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1"]
        )
        
        class MockGameState:
            pass
        
        game_state = MockGameState()
        can_exit = manager.can_exit_phase(game_state)
        assert can_exit is False
    
    def test_get_phase_steps(self):
        """Test getting steps for a phase"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1"]
        )
        
        steps = manager.get_phase_steps()
        assert len(steps) > 0
        assert steps[0]["id"] == 1
    
    def test_get_phase_steps_by_id(self):
        """Test getting steps for a specific phase"""
        ruleset_dict = RulesetHelper.create_ruleset_with_phases([
            {
                "id": 1,
                "name": "Phase 1",
                "steps": [
                    {"id": 1, "name": "Step 1", "mandatory": True},
                    {"id": 2, "name": "Step 2", "mandatory": False}
                ],
                "exit_type": "exit_on_no_actions"
            }
        ])
        ruleset = RulesetIR.from_dict(ruleset_dict)
        
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1"]
        )
        
        steps = manager.get_phase_steps(phase_id=1)
        assert len(steps) == 2
        assert steps[0]["id"] == 1
        assert steps[1]["id"] == 2
    
    def test_rotate_active_player(self):
        """Test rotating active player"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1", "player2", "player3"]
        )
        
        assert manager.active_player == "player1"
        manager.advance_turn()
        assert manager.active_player == "player2"
        manager.advance_turn()
        assert manager.active_player == "player3"
        manager.advance_turn()
        assert manager.active_player == "player1"  # Wraps around
    
    def test_to_dict(self):
        """Test serializing phase manager to dictionary"""
        ruleset = RulesetHelper.create_ruleset_ir()
        manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=TurnType.SINGLE_PLAYER,
            player_ids=["player1", "player2"]
        )
        
        data = manager.to_dict()
        assert data["current_phase_id"] == 1
        assert data["turn_number"] == 1
        assert data["active_player"] == "player1"
        assert data["turn_type"] == "single_player"
        assert "phase_order" in data
        assert "initial_phase_id" in data

