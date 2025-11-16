"""
Tests for the main game engine
"""

import pytest
from TeapotEngine.core.Engine import GameEngine
from TeapotEngine.tests.helpers.ruleset_helper import RulesetHelper


@pytest.fixture
def basic_ruleset():
    """Basic ruleset for testing"""
    return RulesetHelper.create_ruleset_ir()


@pytest.fixture
def engine():
    """Game engine for testing"""
    return GameEngine()


def test_create_match(engine, basic_ruleset):
    """Test creating a match"""
    match_id = "test_match"
    match = engine.create_match(match_id, basic_ruleset.to_dict())
    
    assert match is not None
    assert match.match_id == match_id
    assert engine.get_match(match_id) == match


def test_get_nonexistent_match(engine):
    """Test getting a nonexistent match"""
    assert engine.get_match("nonexistent") is None


def test_remove_match(engine, basic_ruleset):
    """Test removing a match"""
    match_id = "test_match"
    engine.create_match(match_id, basic_ruleset.to_dict())
    
    assert engine.get_match(match_id) is not None
    assert engine.remove_match(match_id) is True
    assert engine.get_match(match_id) is None


def test_list_matches(engine, basic_ruleset):
    """Test listing matches"""
    assert engine.list_matches() == []
    
    match1 = engine.create_match("match1", basic_ruleset.to_dict())
    match2 = engine.create_match("match2", basic_ruleset.to_dict())
    
    matches = engine.list_matches()
    assert len(matches) == 2
    assert "match1" in matches
    assert "match2" in matches


@pytest.mark.asyncio
async def test_process_action(engine, basic_ruleset):
    """Test processing an action"""
    match_id = "test_match"
    engine.create_match(match_id, basic_ruleset.to_dict())
    
    action = {
        "type": 1,
        "card_id": "card_123",
        "player_id": "player1"
    }
    
    result = await engine.process_action(match_id, action)
    assert "success" in result or "error" in result


@pytest.mark.asyncio
async def test_process_action_nonexistent_match(engine):
    """Test processing action for nonexistent match"""
    action = {"type": 1, "card_id": "card_123", "player_id": "player1"}
    result = await engine.process_action("nonexistent", action)
    assert "error" in result


def test_get_match_state(engine, basic_ruleset):
    """Test getting match state"""
    match_id = "test_match"
    engine.create_match(match_id, basic_ruleset.to_dict())
    
    state = engine.get_match_state(match_id)
    assert state is not None
    assert isinstance(state, dict)


def test_get_match_state_nonexistent(engine):
    """Test getting state for nonexistent match"""
    state = engine.get_match_state("nonexistent")
    assert state is None


def test_get_available_actions(engine, basic_ruleset):
    """Test getting available actions for a player"""
    match_id = "test_match"
    engine.create_match(match_id, basic_ruleset.to_dict())
    
    actions = engine.get_available_actions(match_id, "player1")
    assert isinstance(actions, list)


def test_get_available_actions_nonexistent_match(engine):
    """Test getting actions for nonexistent match"""
    actions = engine.get_available_actions("nonexistent", "player1")
    assert actions is None


def test_get_actions_for_object(engine, basic_ruleset):
    """Test getting actions for a selected object"""
    match_id = "test_match"
    engine.create_match(match_id, basic_ruleset.to_dict())
    
    actions = engine.get_actions_for_object(match_id, 1, "card", "1")
    assert isinstance(actions, list) or actions is None


def test_create_duplicate_match(engine, basic_ruleset):
    """Test creating a duplicate match should raise error"""
    match_id = "test_match"
    engine.create_match(match_id, basic_ruleset.to_dict())
    
    with pytest.raises(ValueError):
        engine.create_match(match_id, basic_ruleset.to_dict())
