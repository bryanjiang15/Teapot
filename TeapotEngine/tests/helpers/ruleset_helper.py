"""
Helper class to generate minimal rulesets for testing
"""

from typing import Dict, Any, List, Optional
from TeapotEngine.ruleset.ir import RulesetIR

class RulesetHelper:
    """Helper class to generate minimal rulesets for testing"""
    
    @staticmethod
    def create_minimal_ruleset() -> Dict[str, Any]:
        """Create a basic ruleset with minimal required fields"""
        return {
            "version": "1.0.0",
            "metadata": {
                "name": "Minimal Test Ruleset",
                "author": "Test"
            },
            "turn_structure": {
                "phases": [
                    {
                        "id": 1,
                        "name": "Main Phase",
                        "steps": [
                            {"id": 1, "name": "Main Step", "mandatory": True}
                        ],
                        "exit_type": "exit_on_no_actions"
                    }
                ],
                "initial_phase_id": 1
            },
            "actions": [],
            "rules": [],
            "component_definitions": []
        }
    
    @staticmethod
    def create_ruleset_with_phases(phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a ruleset with specific phases"""
        ruleset = RulesetHelper.create_minimal_ruleset()
        ruleset["turn_structure"]["phases"] = phases
        if phases:
            ruleset["turn_structure"]["initial_phase_id"] = phases[0]["id"]
        return ruleset
    
    @staticmethod
    def create_ruleset_with_actions(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a ruleset with specific actions"""
        ruleset = RulesetHelper.create_minimal_ruleset()
        ruleset["actions"] = actions
        return ruleset
    
    @staticmethod
    def create_ruleset_with_components(components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a ruleset with component definitions"""
        ruleset = RulesetHelper.create_minimal_ruleset()
        ruleset["component_definitions"] = components
        return ruleset
    
    @staticmethod
    def create_ruleset_with_resources(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a ruleset with resource definitions"""
        ruleset = RulesetHelper.create_minimal_ruleset()
        # Resources are typically part of component definitions
        # Create a player component with the resources
        player_component = {
            "id": 1,
            "name": "Test Player",
            "component_type": "player",
            "resources": resources,
            "starting_hand_size": 7,
            "max_hand_size": 7,
            "starting_life": 20,
            "player_zones": [],
            "triggers": []
        }
        ruleset["component_definitions"] = [player_component]
        return ruleset
    
    @staticmethod
    def create_ruleset_with_player_component() -> Dict[str, Any]:
        """Create a ruleset with a basic player component"""
        return {
            "version": "1.0.0",
            "metadata": {"name": "Test Ruleset", "author": "Test"},
            "turn_structure": {
                "phases": [
                    {
                        "id": 1,
                        "name": "Main Phase",
                        "steps": [{"id": 1, "name": "Main Step", "mandatory": True}],
                        "exit_type": "exit_on_no_actions"
                    }
                ],
                "initial_phase_id": 1,
                "max_turns_per_player": 2
            },
            "actions": [],
            "rules": [],
            "component_definitions": [
                {
                    "id": 1,
                    "name": "Base Player",
                    "component_type": "player",
                    "resources": [
                        {
                            "id": 1,
                            "name": "mana",
                            "description": "Mana resource",
                            "scope": "player",
                            "resource_type": "consumable",
                            "starting_amount": 0,
                            "max_per_turn": 10,
                            "regeneration_per_turn": 1
                        }
                    ],
                    "starting_hand_size": 7,
                    "max_hand_size": 7,
                    "starting_life": 20,
                    "player_zones": [],
                    "triggers": []
                }
            ]
        }
    
    @staticmethod
    def create_ruleset_with_game_component() -> Dict[str, Any]:
        """Create a ruleset with a game component"""
        return {
            "version": "1.0.0",
            "metadata": {"name": "Test Ruleset", "author": "Test"},
            "game_component": {
                "id": 1,
                "name": "Base Game",
                "component_type": "game",
                "phases": [
                    {
                        "id": 1,
                        "name": "Main Phase",
                        "steps": [{"id": 1, "name": "Main Step", "mandatory": True}]
                    }
                ],
                "global_zones": [],
                "max_players": 2,
                "win_conditions": [],
                "triggers": [],
                "resources": []
            },
            "turn_structure": {
                "phases": [
                    {
                        "id": 1,
                        "name": "Main Phase",
                        "steps": [{"id": 1, "name": "Main Step", "mandatory": True}],
                        "exit_type": "exit_on_no_actions"
                    }
                ],
                "initial_phase_id": 1
            },
            "actions": [],
            "rules": [],
            "component_definitions": []
        }
    
    @staticmethod
    def create_ruleset_with_triggers(triggers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a ruleset with triggers on a player component"""
        ruleset = RulesetHelper.create_ruleset_with_player_component()
        ruleset["component_definitions"][0]["triggers"] = triggers
        return ruleset
    
    @staticmethod
    def create_ruleset_ir() -> RulesetIR:
        """Create a RulesetIR object for testing"""
        ruleset_dict = RulesetHelper.create_ruleset_with_player_component()
        return RulesetIR.from_dict(ruleset_dict)

