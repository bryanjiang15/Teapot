"""
Example ruleset data for TeapotEngine
"""

def get_example_ruleset():
    """
    Returns a comprehensive example ruleset for testing the Teapot Engine
    """
    return {
        "version": "1.0.0",
        "metadata": {
            "name": "Teapot TCG",
            "author": "Teapot Team",
            "description": "A comprehensive trading card game ruleset"
        },
        "turn_structure": {
            "phases": [
                {
                    "id": 1,
                    "name": "Draw Phase",
                    "steps": [
                        {"id": 1, "name": "Draw Step", "mandatory": True}
                    ]
                },
                {
                    "id": 2,
                    "name": "Main Phase",
                    "steps": [
                        {"id": 2, "name": "Main Phase 1", "mandatory": True},
                        {"id": 3, "name": "Main Phase 2", "mandatory": False}
                    ]
                },
                {
                    "id": 3,
                    "name": "Combat Phase",
                    "steps": [
                        {"id": 4, "name": "Declare Attackers", "mandatory": False},
                        {"id": 5, "name": "Declare Blockers", "mandatory": False},
                        {"id": 6, "name": "Damage Step", "mandatory": False}
                    ]
                },
                {
                    "id": 4,
                    "name": "End Phase",
                    "steps": [
                        {"id": 7, "name": "End Step", "mandatory": True}
                    ]
                }
            ]
        },
        "zones": [
            {
                "id": 1,
                "name": "Hand",
                "zone_type": "private",
                "description": "Player's hand of cards"
            },
            {
                "id": 2,
                "name": "Battlefield",
                "zone_type": "public",
                "description": "Cards in play"
            },
            {
                "id": 3,
                "name": "Graveyard",
                "zone_type": "public",
                "description": "Destroyed cards"
            },
            {
                "id": 4,
                "name": "Library",
                "zone_type": "private",
                "description": "Player's deck"
            }
        ],
        "resources": [
            {
                "id": 1,
                "name": "mana",
                "description": "Primary resource for playing cards",
                "scope": "player",
                "resource_type": "consumable",
                "starting_amount": 0,
                "max_per_turn": 10,
                "regeneration_per_turn": 1
            },
            {
                "id": 2,
                "name": "life",
                "description": "Player's life total",
                "scope": "player",
                "resource_type": "tracked",
                "starting_amount": 20,
                "max_amount": None,
                "min_amount": 0
            },
            {
                "id": 3,
                "name": "energy",
                "description": "Secondary resource for special abilities",
                "scope": "player",
                "resource_type": "consumable",
                "starting_amount": 0,
                "max_per_turn": 5,
                "regeneration_per_turn": 0
            },
            {
                "id": 4,
                "name": "global_turn_counter",
                "description": "Global turn counter for the game",
                "scope": "global",
                "resource_type": "accumulating",
                "starting_amount": 0,
                "max_amount": None
            },
            {
                "id": 5,
                "name": "card_charges",
                "description": "Charges on individual cards",
                "scope": "object",
                "resource_type": "consumable",
                "starting_amount": 0,
                "max_amount": 3
            }
        ],
        "actions": [
            {
                "id": 1,
                "name": "Play Card",
                "description": "Play a card from hand to battlefield",
                "timing": "stack",
                "phase_ids": [2, 3],
                "zone_ids": [1],
                "preconditions": [
                    {"op": "has_resource", "resource": "mana", "atLeast": 1},
                    {"op": "zone_contains", "zone": "hand", "min": 1}
                ],
                "costs": [
                    {"op": "pay_resource", "resource": "mana", "amount": 1}
                ],
                "effects": [
                    {"op": "move_zone", "target": "card", "from": "hand", "to": "battlefield"}
                ]
            },
            {
                "id": 2,
                "name": "Attack",
                "description": "Attack with a creature",
                "timing": "instant",
                "phase_ids": [3],
                "zone_ids": [2],
                "preconditions": [
                    {"op": "zone_contains", "zone": "battlefield", "min": 1},
                    {"op": "card_has_property", "property": "can_attack", "value": True}
                ],
                "effects": [
                    {"op": "declare_attack", "target": "opponent"}
                ]
            },
            {
                "id": 3,
                "name": "Draw Card",
                "description": "Draw a card from library",
                "timing": "instant",
                "phase_ids": [1, 2, 3, 4],
                "zone_ids": [4],
                "preconditions": [
                    {"op": "zone_contains", "zone": "library", "min": 1}
                ],
                "effects": [
                    {"op": "move_zone", "target": "card", "from": "library", "to": "hand"}
                ]
            },
            {
                "id": 4,
                "name": "Use Special Ability",
                "description": "Use a special ability that costs energy",
                "timing": "stack",
                "phase_ids": [2, 3],
                "zone_ids": [2],
                "preconditions": [
                    {"op": "has_resource", "resource": "energy", "atLeast": 2},
                    {"op": "zone_contains", "zone": "battlefield", "min": 1}
                ],
                "costs": [
                    {"op": "pay_resource", "resource": "energy", "amount": 2}
                ],
                "effects": [
                    {"op": "deal_damage", "target": "opponent", "amount": 1}
                ]
            }
        ],
        "triggers": [
            {
                "id": 1,
                "when": {"event": "card_played", "card_type": "creature"},
                "conditions": [],
                "effects": [
                    {"op": "gain_resource", "resource": "energy", "amount": 1}
                ],
                "timing": "post"
            },
            {
                "id": 2,
                "when": {"event": "turn_start"},
                "conditions": [],
                "effects": [
                    {"op": "gain_resource", "resource": "mana", "amount": 1}
                ],
                "timing": "post"
            }
        ],
        "keywords": [
            {
                "id": 1,
                "name": "Flying",
                "description": "Can only be blocked by creatures with Flying",
                "effects": [
                    {"op": "set_property", "property": "flying", "value": True}
                ],
                "grants": [
                    {"op": "blocking_restriction", "type": "flying_only"}
                ]
            },
            {
                "id": 2,
                "name": "First Strike",
                "description": "Deals damage before creatures without First Strike",
                "effects": [
                    {"op": "set_property", "property": "first_strike", "value": True}
                ],
                "grants": [
                    {"op": "damage_timing", "priority": "first"}
                ]
            }
        ],
        "constants": {
            "max_hand_size": 7,
            "starting_life": 20,
            "starting_mana": 0,
            "deck_size": 60
        }
    }
