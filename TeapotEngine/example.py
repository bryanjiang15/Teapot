#!/usr/bin/env python3
"""
Example usage of TeapotEngine
"""

import sys
import os
import asyncio

from core.state import Player
from core.engine import GameEngine
from ruleset.ir import RulesetIR
from example_ruleset import get_example_ruleset

async def main():
    """Example usage"""
    print("🎮 TeapotEngine Example")
    print("=" * 50)
    
    # Get the example ruleset
    ruleset_data = get_example_ruleset()
    
    # Create ruleset
    ruleset = RulesetIR.from_dict(ruleset_data)
    print(f"✅ Created ruleset: {ruleset.metadata['name']}")
    print(f"   Description: {ruleset.metadata['description']}")
    print(f"   Actions: {len(ruleset.actions)}")
    print(f"   Keywords: {len(ruleset.keywords)}")
    
    # Display actions
    print("\n⚡ Actions:")
    for action in ruleset.actions:
        print(f"   - {action.name}: {action.description}")
        print(f"     Timing: {action.timing}, Phases: {action.phase_ids}")
    
    # Create game engine
    engine = GameEngine()
    print("\n✅ Created game engine")
    
    # Create a match
    match_id = "example_match"
    match = engine.create_match(match_id, ruleset.model_dump(), verbose=True)
    print(f"✅ Created match: {match_id}")


    #Start the game
    await match.begin_game()
    
    # Get match state
    state = engine.get_match_state(match_id)
    print(f"✅ Match state: phase {state['current_phase']}, turn {state['turn_number']}")
    print(f"✅ Player 1 hand: {state['zones']['hand'][2]}")
    print(f"✅ Player 2 hand: {state['zones']['hand'][3]}")
    # Game engine should automatically advance to the draw phase, which triggers the draw action
    
    # Get available actions
    actions = engine.get_available_actions(match_id, "player1")
    print(f"✅ Available actions: {len(actions)}")
    for action in actions:
        print(f"   - {action['name']} ({action['id']})")
    
    # Demonstrate object-based action queries
    print("\n🎯 Object-Based Action Queries:")
    
    # Example: Query actions for a card in hand
    print("\n📋 Actions for card in hand:")
    card_actions = engine.get_actions_for_object(match_id, 2, "card", "card_123")
    if card_actions:
        for action in card_actions:
            print(f"   - {action['name']} (Mode: {action['interaction_mode']})")
            if action['costs']:
                print(f"     Costs: {action['costs']}")
            if action['additional_targets']:
                print(f"     Additional targets needed: {len(action['additional_targets'])}")
    else:
        print("🟥 No actions available for this card")
    
    # Demonstrate manual turn ending
    print(f"\n🔄 Turn Management Demo:")
    print(f"   Before end_turn: Turn {match.state.turn_number}, Phase {match.state.current_phase}")
    await match.end_turn()
    print(f"   After end_turn: Turn {match.state.turn_number}, Phase {match.state.current_phase}")
    print(f"   Active player: {match.state.active_player}")
    
    print("\n🎉 Example completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
