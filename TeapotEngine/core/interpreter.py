"""
Ruleset IR interpreter for game logic
"""

from typing import Dict, Any, List, Optional
from ruleset.ir import RulesetIR, ActionDefinition, PhaseDefinition, SelectableObjectType, RuleDefinition
from ruleset.trigger_definition import TriggerDefinition
from .state import GameState
from .events import Event, Reaction, PHASE_ENTERED, PHASE_EXITED, ACTION_EXECUTED, RULE_EXECUTED, CARD_MOVED, RESOURCE_CHANGED, DAMAGE_DEALT


class RuleExecutor:
    """Executes rules and translates effects into events"""
    
    def __init__(self, ruleset: RulesetIR):
        self.ruleset = ruleset
    
    def execute_rule(
        self,
        rule_id: int,
        caused_by: Dict[str, str],
        game_state: GameState
    ) -> List[Event]:
        """Execute a rule and return generated events"""
        rule = self.ruleset.get_rule(rule_id)
        if not rule:
            return []
        
        events = []
        
        for effect in rule.effects:
            op = effect.get("op")
            
            if op == "execute_rule":
                # Recursively execute another rule
                nested_events = self.execute_rule(
                    effect["rule_id"], caused_by, game_state
                )
                events.extend(nested_events)
            
            elif op == "move_card":
                events.append(Event(
                    type=CARD_MOVED,
                    payload={
                        "card_id": effect.get("card_id", "top_card"),
                        "from_zone": effect.get("from_zone", "deck"),
                        "to_zone": effect.get("to_zone", "hand"),
                        # If the effect refers to "self", resolve based on caused_by
                        "player_id": (
                            game_state.get_player(effect.get("player_id", "self"), caused_by).id
                        )
                    }
                ))
            
            elif op == "gain_resource":
                events.append(Event(
                    type=RESOURCE_CHANGED,
                    payload={
                        "player_id": caused_by,
                        "resource": effect.get("resource", "mana"),
                        "amount": effect.get("amount", 1)
                    }
                ))
            
            elif op == "deal_damage":
                events.append(Event(
                    type=DAMAGE_DEALT,
                    payload={
                        "target": effect.get("target"),
                        "amount": effect.get("amount", 1),
                        "source": effect.get("source")
                    }
                ))
            
            # Add more effect types as needed
        
        # Emit RuleExecuted event for potential triggers
        events.append(Event(
            type=RULE_EXECUTED,
            payload={"rule_id": rule_id, "caused_by": caused_by}
        ))
        
        return events


class RulesetInterpreter:
    """Interprets ruleset IR to drive game logic"""
    
    def __init__(self, ruleset_ir: RulesetIR):
        self.ruleset = ruleset_ir
        self._action_cache: Dict[int, ActionDefinition] = {}
        self._phase_cache: Dict[int, PhaseDefinition] = {}
        self._rule_cache: Dict[int, RuleDefinition] = {}
        
        # NEW: Trigger index by event type for fast lookup
        self._trigger_index: Dict[str, List] = {}
        
        # Build caches for fast lookup
        self._build_caches()
        self._build_trigger_index()
        
        # Initialize rule executor
        self.rule_executor = RuleExecutor(ruleset_ir)
    
    def _build_caches(self) -> None:
        """Build lookup caches for performance"""
        for action in self.ruleset.actions:
            self._action_cache[action.id] = action
        
        for phase in self.ruleset.turn_structure.phases:
            self._phase_cache[phase.id] = phase
        
        for rule in self.ruleset.rules:
            self._rule_cache[rule.id] = rule
    
    def _build_trigger_index(self) -> None:
        """Build index of triggers by event type for efficient discovery"""
        self._trigger_index.clear()

        # Get all triggers from component hierarchy
        all_triggers = self.ruleset.get_all_triggers()
        
        for trigger in all_triggers:
            event_type = trigger.when.get("eventType")
            
            if event_type:
                # Index by specific event type
                self._trigger_index.setdefault(event_type, [])
                self._trigger_index[event_type].append(trigger)
            else:
                # Wildcard trigger (matches any event) - store under special key
                self._trigger_index.setdefault("*", [])
                self._trigger_index["*"].append(trigger)
    
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
    
    def get_actions_for_object(
        self, 
        game_state: GameState, 
        player_id: str, 
        object_type: SelectableObjectType,
        object_id: str
    ) -> List[Dict[str, Any]]:
        """Get available actions where the specified object is the primary target"""
        available_actions = []
        
        for action in self.ruleset.actions:
            # Check if this action can use the selected object as primary target
            if self._object_matches_primary_target(action, object_type, object_id, game_state, player_id):
                if self._can_take_action(action, game_state, player_id):
                    # Build action response with interaction metadata
                    action_response = {
                        "id": action.id,
                        "name": action.name,
                        "description": action.description,
                        "interaction_mode": action.interaction_mode,
                        "costs": self._evaluate_costs(action.costs, game_state, player_id),
                        "additional_targets": self._get_additional_targets(action, game_state, player_id),
                        "ui": action.ui,
                        "activation_requirements": self._get_activation_requirements(action)
                    }
                    available_actions.append(action_response)
        
        return available_actions
    
    def _object_matches_primary_target(
        self, 
        action: ActionDefinition, 
        object_type: SelectableObjectType, 
        object_id: str, 
        game_state: GameState, 
        player_id: str
    ) -> bool:
        """Check if the selected object matches the action's primary target requirements"""
        # If no primary target type specified, this action doesn't use object selection
        if not action.primary_target_type:
            return False
        
        # Check if object type matches
        if action.primary_target_type != object_type:
            return False
        
        # If there's a selector, evaluate it
        if action.primary_target_selector:
            return self._evaluate_primary_target_selector(
                action.primary_target_selector, 
                object_id, 
                game_state, 
                player_id
            )
        
        # If no selector, assume any object of the right type is valid
        return True
    
    def _evaluate_primary_target_selector(
        self, 
        selector: Dict[str, Any], 
        object_id: str, 
        game_state: GameState, 
        player_id: str
    ) -> bool:
        """Evaluate if the object matches the primary target selector"""
        # Check zone requirements
        if "zone" in selector:
            object_location = game_state.get_card_location(object_id)
            if not object_location or object_location[0] != selector["zone"]:
                return False
        
        # Check controller requirements
        if "controller" in selector:
            if selector["controller"] == "self":
                # Check if object is controlled by the player
                object_location = game_state.get_card_location(object_id)
                if not object_location or object_location[1] != player_id:
                    return False
            elif selector["controller"] == "opponent":
                # Check if object is controlled by opponent
                opponent_id = "player2" if player_id == "player1" else "player1"
                object_location = game_state.get_card_location(object_id)
                if not object_location or object_location[1] != opponent_id:
                    return False
        
        # Add more selector conditions as needed
        return True
    
    def _get_additional_targets(self, action: ActionDefinition, game_state: GameState, player_id: str) -> List[Dict[str, Any]]:
        """Get additional targets needed beyond the primary target"""
        additional_targets = []
        
        for target in action.targets:
            target_id = target.get("id")
            selector = target.get("selector", {})
            
            # Evaluate selector to get valid targets
            valid_targets = self._evaluate_selector(selector, game_state, player_id)
            
            additional_targets.append({
                "id": target_id,
                "name": target.get("name", f"Target {target_id}"),
                "target_type": target.get("target_type", "card"),
                "count": target.get("count", 1),
                "selector": selector,
                "valid_targets": valid_targets
            })
        
        return additional_targets
    
    def _get_activation_requirements(self, action: ActionDefinition) -> Dict[str, Any]:
        """Get activation requirements for the action"""
        requirements = {
            "needs_button": action.interaction_mode == "button",
            "needs_drag_target": action.interaction_mode == "drag",
            "needs_additional_selection": action.interaction_mode == "multi_select",
            "selection_count": len(action.targets) if action.interaction_mode == "multi_select" else 0
        }
        
        # Add drag targets if it's a drag interaction
        if action.interaction_mode == "drag":
            requirements["drag_targets"] = self._get_drag_targets(action)
        
        return requirements
    
    def _get_drag_targets(self, action: ActionDefinition) -> List[str]:
        """Get valid drag targets for drag interactions"""
        drag_targets = []
        
        # Look for zone targets that could be drag destinations
        for target in action.targets:
            if target.get("target_type") == "zone":
                zone_name = target.get("selector", {}).get("zone")
                if zone_name:
                    drag_targets.append(zone_name)
        
        return drag_targets
    
    def _can_take_action(self, action: ActionDefinition, game_state: GameState, player_id: str) -> bool:
        """Check if a player can take a specific action"""
        #Check Zone and Phase Conditions
        current_phase = game_state.current_phase
        if action.phase_ids and current_phase not in action.phase_ids:
            return False

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
    
    def _determine_trigger_caused_by(self, trigger, event: Event, game_state: GameState) -> List[Dict[str, str]]:
        """Determine caused_by objects based on trigger scope and component source"""
        caused_by_objects = []
        
        # Get trigger scope
        scope = getattr(trigger, 'scope', 'self')
        
        if scope == "self":
            # Trigger affects only the component that caused the event
            if event.caused_by:
                caused_by_objects.append({"object_type": "player", "object_id": event.caused_by})
            else:
                # Fallback to active player
                caused_by_objects.append({"object_type": "player", "object_id": game_state.active_player})
        
        elif scope == "all":
            # Trigger affects all players
            caused_by_objects.append({"object_type": "player", "object_id": "player1"})
            caused_by_objects.append({"object_type": "player", "object_id": "player2"})
        
        elif scope == "opponent":
            # Trigger affects the opponent of the event causer
            if event.caused_by:
                opponent_id = "player2" if event.caused_by == "player1" else "player1"
                caused_by_objects.append({"object_type": "player", "object_id": opponent_id})
            else:
                # Fallback to opponent of active player
                opponent_id = "player2" if game_state.active_player == "player1" else "player1"
                caused_by_objects.append({"object_type": "player", "object_id": opponent_id})
        
        else:
            # Default to self scope
            if event.caused_by:
                caused_by_objects.append({"object_type": "player", "object_id": event.caused_by})
            else:
                caused_by_objects.append({"object_type": "player", "object_id": game_state.active_player})
        
        return caused_by_objects
    
    def discover_reactions(self, event: Event, game_state: GameState) -> List[Reaction]:
        """Find all triggers that match an event using indexed lookup"""
        reactions = []
        
        # Get triggers indexed by this event type (O(1) lookup)
        candidate_triggers = self._trigger_index.get(event.type, [])
        
        # Also check wildcard triggers
        candidate_triggers.extend(self._trigger_index.get("*", []))
        
        # Filter candidates by conditions and filters
        for trigger in candidate_triggers:
            if self._trigger_matches(trigger, event, game_state):
                # Determine caused_by based on trigger scope and component source
                caused_by_objects = self._determine_trigger_caused_by(trigger, event, game_state)
                
                # Create one reaction per caused_by object
                for caused_by_obj in caused_by_objects:
                    # Check conditions for this specific source object
                    if self._trigger_conditions_met_for_source(trigger, event, game_state, caused_by_obj):
                        reaction = Reaction(
                            id=trigger.id,
                            when=trigger.when,
                            conditions=trigger.conditions,
                            effects=trigger.execute_rules,
                            timing=trigger.timing,
                            caused_by=caused_by_obj
                        )
                        reactions.append(reaction)
        
        return reactions
    
    def _trigger_matches(self, trigger, event: Event, game_state: GameState) -> bool:
        """Check if trigger matches event (filters and conditions only)"""
        # Event type already matched by index lookup
        
        # Match filters
        filters = trigger.when.get("filters", {})
        for key, value in filters.items():
            if event.payload.get(key) != value:
                return False
        
        # Check conditions
        for condition in trigger.conditions:
            if not self._evaluate_condition(condition, game_state, event):
                return False
        
        return True
    
    def _trigger_conditions_met_for_source(self, trigger, event: Event, game_state: GameState, source_obj: Dict[str, str]) -> bool:
        """Check if trigger conditions are met for a specific source object"""
        # For now, use the same condition evaluation as the general trigger
        # In the future, this could be enhanced to evaluate conditions in context of the source object
        for condition in trigger.conditions:
            if not self._evaluate_condition(condition, game_state, event):
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
