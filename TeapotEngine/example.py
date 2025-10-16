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
    print(f"   Resources: {len(ruleset.resources)}")
    print(f"   Zones: {len(ruleset.zones)}")
    print(f"   Actions: {len(ruleset.actions)}")
    print(f"   Triggers: {len(ruleset.triggers)}")
    print(f"   Keywords: {len(ruleset.keywords)}")
    
    # Display resources
    print("\n📊 Resources:")
    for resource in ruleset.resources:
        scope_info = f"({resource.scope.value})"
        print(f"   - {resource.name}: {resource.description} {scope_info}")
        print(f"     Type: {resource.resource_type.value}, Starting: {resource.starting_amount}")
        if resource.max_per_turn:
            print(f"     Max per turn: {resource.max_per_turn}")
        if resource.regeneration_per_turn:
            print(f"     Regeneration: {resource.regeneration_per_turn}/turn")
    
    # Display zones
    print("\n🗂️  Zones:")
    for zone in ruleset.zones:
        print(f"   - {zone.name}: {zone.description} ({zone.zone_type.value})")
    
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

    #Add players
    match.state.add_player(Player(id="player1", name="Player 1"))
    match.state.add_player(Player(id="player2", name="Player 2"))


    #Start the game
    await match.begin_game()
    
    # Get match state
    state = engine.get_match_state(match_id)
    print(f"✅ Match state: phase {state['current_phase']}, turn {state['turn_number']}")

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
    card_actions = engine.get_actions_for_object(match_id, "player1", "card", "card_123")
    if card_actions:
        for action in card_actions:
            print(f"   - {action['name']} (Mode: {action['interaction_mode']})")
            if action['costs']:
                print(f"     Costs: {action['costs']}")
            if action['additional_targets']:
                print(f"     Additional targets needed: {len(action['additional_targets'])}")
    else:
        print("🟥 No actions available for this card")
    
    print("\n🎉 Example completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
