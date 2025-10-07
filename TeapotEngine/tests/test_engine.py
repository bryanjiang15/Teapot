"""
Tests for the main game engine
"""

import pytest
import sys
import os

from TeapotEngine import GameEngine, RulesetIR


@pytest.fixture
def basic_ruleset():
    """Basic ruleset for testing"""
    return RulesetIR(
        version="1.0.0",
        metadata={"name": "Test Ruleset", "author": "Test"},
        turn_structure={
            "phases": [
                {
                    "id": 1,
                    "name": "Main Phase",
                    "steps": [
                        {"id": 1, "name": "Main Phase 1", "mandatory": False}
                    ]
                }
            ]
        },
        actions=[
            {
                "id": 1,
                "name": "Play Card",
                "timing": "stack",
                "phase_ids": [1],
                "zone_ids": [1, 2],
                "preconditions": [
                    {"op": "has_resource", "resource": "mana", "atLeast": 1}
                ],
                "costs": [
                    {"op": "pay_resource", "resource": "mana", "amount": 1}
                ],
                "effects": [
                    {"op": "move_zone", "target": "card", "to": "battlefield"}
                ]
            }
        ]
    )


@pytest.fixture
def engine():
    """Game engine for testing"""
    return GameEngine()


def test_create_match(engine, basic_ruleset):
    """Test creating a match"""
    match_id = "test_match"
    match = engine.create_match(match_id, basic_ruleset.model_dump())
    
    assert match is not None
    assert match.match_id == match_id
    assert engine.get_match(match_id) == match


def test_get_nonexistent_match(engine):
    """Test getting a nonexistent match"""
    assert engine.get_match("nonexistent") is None


def test_remove_match(engine, basic_ruleset):
    """Test removing a match"""
    match_id = "test_match"
    engine.create_match(match_id, basic_ruleset.model_dump())
    
    assert engine.get_match(match_id) is not None
    assert engine.remove_match(match_id) is True
    assert engine.get_match(match_id) is None


def test_list_matches(engine, basic_ruleset):
    """Test listing matches"""
    assert engine.list_matches() == []
    
    match1 = engine.create_match("match1", basic_ruleset.model_dump())
    match2 = engine.create_match("match2", basic_ruleset.model_dump())
    
    matches = engine.list_matches()
    assert len(matches) == 2
    assert "match1" in matches
    assert "match2" in matches


@pytest.mark.asyncio
async def test_process_action(engine, basic_ruleset):
    """Test processing an action"""
    match_id = "test_match"
    engine.create_match(match_id, basic_ruleset.model_dump())
    
    action = {
        "type": 1,  # play_card
        "card_id": "card_123",
        "player_id": "player1"
    }
    
    result = await engine.process_action(match_id, action)
    assert result["success"] is True


@pytest.mark.asyncio
async def test_process_action_nonexistent_match(engine):
    """Test processing action for nonexistent match"""
    action = {"type": 1, "card_id": "card_123", "player_id": "player1"}  # play_card
    result = await engine.process_action("nonexistent", action)
    assert "error" in result
