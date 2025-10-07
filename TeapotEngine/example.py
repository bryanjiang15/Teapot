#!/usr/bin/env python3
"""
Example usage of TeapotEngine
"""

import sys
import os

from core.engine import GameEngine
from ruleset.ir import RulesetIR

def main():
    """Example usage"""
    print("🎮 TeapotEngine Example")
    print("=" * 50)
    
    # Create a basic ruleset
    ruleset_data = {
        "version": "1.0.0",
        "metadata": {"name": "Basic TCG", "author": "Teapot Team"},
        "turn_structure": {
            "phases": [
                {
                    "id": 1,
                    "name": "Main Phase",
                    "steps": [
                        {"id": 1, "name": "Main Phase 1", "mandatory": True},
                        {"id": 2, "name": "Main Phase 2", "mandatory": False}
                    ]
                }
            ]
        },
        "actions": [
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
    }
    
    # Create ruleset
    ruleset = RulesetIR.from_dict(ruleset_data)
    print(f"✅ Created ruleset: {ruleset.metadata['name']}")
    
    # Create game engine
    engine = GameEngine()
    print("✅ Created game engine")
    
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
    
    print("\n🎉 Example completed successfully!")

if __name__ == "__main__":
    main()
