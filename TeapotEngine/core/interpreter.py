"""
Ruleset IR interpreter for game logic
"""

from typing import Dict, Any, List, Optional
from ruleset.ir import RulesetIR, ActionDefinition, PhaseDefinition
from .state import GameState
from .events import Event, Reaction


class RulesetInterpreter:
    """Interprets ruleset IR to drive game logic"""
    
    def __init__(self, ruleset_ir: RulesetIR):
        self.ruleset = ruleset_ir
        self._action_cache: Dict[int, ActionDefinition] = {}
        self._phase_cache: Dict[int, PhaseDefinition] = {}
        
        # Build caches for fast lookup
        self._build_caches()
    
    def _build_caches(self) -> None:
        """Build lookup caches for performance"""
        for action in self.ruleset.actions:
            self._action_cache[action.id] = action
        
        for phase in self.ruleset.turn_structure.phases:
            self._phase_cache[phase.id] = phase
    
    def get_available_actions(self, game_state: GameState, player_id: str) -> List[Dict[str, Any]]:
        """Get available actions for a player given current game state"""
        available_actions = []
        
        for action in self.ruleset.actions:
            if self._can_take_action(action, game_state, player_id):
                available_actions.append({
                    "id": action.id,
                    "name": action.name,
                    "description": action.description,
                    "timing": action.timing,
                    "cost": self._evaluate_costs(action.costs, game_state, player_id),
                    "targets": self._get_target_options(action.targets, game_state, player_id),
                    "ui": action.ui
                })
        
        return available_actions
    
    def _can_take_action(self, action: ActionDefinition, game_state: GameState, player_id: str) -> bool:
        """Check if a player can take a specific action"""
        # Check preconditions
        for precondition in action.preconditions:
            if not self._evaluate_condition(precondition, game_state, player_id):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: Dict[str, Any], game_state: GameState, player_id: str) -> bool:
        """Evaluate a single condition"""
        op = condition.get("op")
        
        if op == "has_resource":
            resource = condition.get("resource")
            amount = condition.get("atLeast", 0)
            player = game_state.get_player(player_id)
            if not player:
                return False
            
            # Get resource manager to find resource by name
            if game_state.resource_manager:
                for resource_def in game_state.resource_manager.resource_definitions.values():
                    if resource_def.name == resource:
                        player_resource = player.get_resource(resource_def.id)
                        if player_resource and player_resource.current_amount >= amount:
                            return True
            return False
        
        elif op == "in_zone":
            zone = condition.get("zone")
            # Check if player has cards in the specified zone
            return len(game_state.get_player_zone(player_id, zone)) > 0
        
        elif op == "phase_allows":
            required_phase = condition.get("phase")
            return game_state.current_phase == required_phase
        
        elif op == "can_attack":
            # Check if player has untapped creatures that can attack
            battlefield = game_state.get_player_zone(player_id, "battlefield")
            return len(battlefield) > 0  # Simplified check
        
        elif op == "not_tapped":
            # Check if the target is not tapped
            return True  # Simplified check
        
        # Add more condition types as needed
        return True
    
    def _evaluate_costs(self, costs: List[Dict[str, Any]], game_state: GameState, player_id: str) -> Dict[str, Any]:
        """Evaluate the costs of an action"""
        total_costs = {}
        
        for cost in costs:
            op = cost.get("op")
            
            if op == "pay_resource":
                resource = cost.get("resource")
                amount = cost.get("amount", 0)
                total_costs[resource] = total_costs.get(resource, 0) + amount
            
            elif op == "tap":
                total_costs["tap"] = total_costs.get("tap", 0) + 1
        
        return total_costs
    
    def _get_target_options(self, targets: List[Dict[str, Any]], game_state: GameState, player_id: str) -> Dict[str, Any]:
        """Get available target options for an action"""
        target_options = {}
        
        for target in targets:
            target_id = target.get("id")
            selector = target.get("selector", {})
            
            # Evaluate selector to get valid targets
            valid_targets = self._evaluate_selector(selector, game_state, player_id)
            
            target_options[target_id] = {
                "selector": selector,
                "count": target.get("count", 1),
                "valid_targets": valid_targets
            }
        
        return target_options
    
    def _evaluate_selector(self, selector: Dict[str, Any], game_state: GameState, player_id: str) -> List[str]:
        """Evaluate a selector to get valid targets"""
        zone = selector.get("zone")
        controller = selector.get("controller", "self")
        count = selector.get("count", 1)
        
        if controller == "self":
            target_player = player_id
        elif controller == "opponent":
            # Get opponent player ID (simplified)
            target_player = "player2" if player_id == "player1" else "player1"
        else:
            target_player = controller
        
        if zone:
            return game_state.get_player_zone(target_player, zone)[:count]
        
        return []
    
    def discover_reactions(self, event: Event, game_state: GameState) -> List[Reaction]:
        """Discover reactions that match an event"""
        reactions = []
        
        for trigger in self.ruleset.triggers:
            if self._trigger_matches(trigger, event, game_state):
                reaction = Reaction(
                    id=f"reaction_{trigger.id}_{event.id}",
                    when=trigger.when,
                    conditions=trigger.conditions,
                    effects=trigger.effects,
                    timing=trigger.timing,
                    source_id=trigger.source_id
                )
                reactions.append(reaction)
        
        return reactions
    
    def _trigger_matches(self, trigger, event: Event, game_state: GameState) -> bool:
        """Check if a trigger matches an event"""
        when = trigger.when
        event_type = when.get("eventType")
        
        if event_type and event.type != event_type:
            return False
        
        # Check additional filters
        filters = when.get("filters", {})
        for key, value in filters.items():
            if event.payload.get(key) != value:
                return False
        
        return True
    
    def get_next_phase(self, current_phase: int) -> Optional[int]:
        """Get the next phase in the turn structure"""
        phases = self.ruleset.turn_structure.phases
        current_index = -1
        
        for i, phase in enumerate(phases):
            if phase.id == current_phase:
                current_index = i
                break
        
        if current_index == -1:
            return None
        
        next_index = current_index + 1
        if next_index < len(phases):
            return phases[next_index].id
        
        return None
    
    def get_phase_steps(self, phase_id: int) -> List[Dict[str, Any]]:
        """Get the steps for a phase"""
        phase = self._phase_cache.get(phase_id)
        if not phase:
            return []
        
        return [step.dict() for step in phase.steps]
    
    def validate_action(self, action_data: Dict[str, Any], game_state: GameState, player_id: str) -> bool:
        """Validate an action against the ruleset"""
        action_id = action_data.get("type")
        action_def = self._action_cache.get(action_id)
        
        if not action_def:
            return False
        
        return self._can_take_action(action_def, game_state, player_id)
