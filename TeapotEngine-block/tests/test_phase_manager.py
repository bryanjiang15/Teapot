"""
Tests for TurnType enum (PhaseManager was removed - turn/phase state is now in GameState)
"""

import pytest
from TeapotEngine.core.PhaseManager import TurnType


class TestTurnType:
    """Tests for TurnType enum"""
    
    def test_turn_type_values(self):
        """Test TurnType enum values"""
        assert TurnType.SINGLE_PLAYER.value == "single_player"
        assert TurnType.SYNCHRONOUS.value == "synchronous"
    
    def test_turn_type_from_string(self):
        """Test creating TurnType from string"""
        assert TurnType("single_player") == TurnType.SINGLE_PLAYER
        assert TurnType("synchronous") == TurnType.SYNCHRONOUS
    
    def test_turn_type_iteration(self):
        """Test that all TurnType values are accessible"""
        turn_types = list(TurnType)
        assert len(turn_types) == 2
        assert TurnType.SINGLE_PLAYER in turn_types
        assert TurnType.SYNCHRONOUS in turn_types
