#!/usr/bin/env python3
"""
Example usage of TeapotEngine
"""

import sys
import os

from core.engine import GameEngine
from ruleset.ir import RulesetIR
from example_ruleset import get_example_ruleset

def main():
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
    match = engine.create_match(match_id, ruleset.model_dump())
    print(f"✅ Created match: {match_id}")
    
    # Get match state
    state = engine.get_match_state(match_id)
    print(f"✅ Match state: {state['current_phase']} phase, turn {state['turn_number']}")
    
    # Get available actions
    actions = engine.get_available_actions(match_id, "player1")
    print(f"✅ Available actions: {len(actions)}")
    for action in actions:
        print(f"   - {action['name']} ({action['id']})")
    
    # Display turn structure
    print("\n🔄 Turn Structure:")
    for phase in ruleset.turn_structure.phases:
        print(f"   Phase {phase.id}: {phase.name}")
        for step in phase.steps:
            mandatory = " (mandatory)" if step.mandatory else ""
            print(f"     - Step {step.id}: {step.name}{mandatory}")
    
    print("\n🎉 Example completed successfully!")

if __name__ == "__main__":
    main()
