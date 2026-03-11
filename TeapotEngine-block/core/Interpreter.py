"""
Ruleset IR interpreter for game logic
"""

from typing import Dict, Any, List, Optional
from TeapotEngine.ruleset.IR import RulesetIR
from TeapotEngine.ruleset.rule_definitions.RuleDefinition import ActionDefinition, PhaseDefinition, SelectableObjectType, RuleDefinition
from TeapotEngine.ruleset.ExpressionModel import EvalContext, Predicate, Selector
from TeapotEngine.ruleset.system_models.SystemEvent import *
from .GameState import GameState
from .Events import Event, Reaction
from .Component import Component
from .EffectInterpreter import EffectInterpreter


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
                        "player_id": game_state.get_player(effect.get("player_id", "self"), caused_by).id,
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
        
        # Build caches for fast lookup
        self._build_caches()
        
        # Initialize rule executor
        self.rule_executor = RuleExecutor(ruleset_ir)
        
        # Initialize effect interpreter
        self.effect_interpreter = EffectInterpreter(ruleset_ir)
    
    def _build_caches(self) -> None:
        """Build lookup caches for performance"""
        for action in self.ruleset.actions:
            self._action_cache[action.id] = action
        
        for phase in self.ruleset.turn_structure.phases:
            self._phase_cache[phase.id] = phase
        
        for rule in self.ruleset.rules:
            self._rule_cache[rule.id] = rule
    
    
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
        player_id: int, 
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
        player_id: int
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
        selector: Selector, 
        object_id: str, 
        game_state: GameState, 
        player_id: str
    ) -> bool:
        """Evaluate if the object matches the primary target selector"""
        # Get the player component for context
        player_component = game_state.get_player(player_id)
        if not player_component:
            return False
        
        # Get the object component
        try:
            object_component = game_state.get_component(int(object_id))
        except (ValueError, TypeError):
            return False
        
        if not object_component:
            return False
        
        # Create evaluation context with the object as source
        ctx = EvalContext(
            source=object_component,
            event=None,
            targets=(),
            game=game_state,
            phase=str(game_state.current_phase),
            turn=game_state.turn_number
        )
        
        # Evaluate selector and check if object_id is in the results
        matching_components = selector.evaluate(ctx)
        return any(str(c.id) == object_id for c in matching_components)
    
    def _get_additional_targets(self, action: ActionDefinition, game_state: GameState, player_id: str) -> List[Dict[str, Any]]:
        """Get additional targets needed beyond the primary target"""
        additional_targets = []
        
        player_component = game_state.get_player(player_id)
        if not player_component:
            return additional_targets
        
        ctx = EvalContext(
            source=player_component,
            event=None,
            targets=(),
            game=game_state,
            phase=str(game_state.current_phase),
            turn=game_state.turn_number
        )
        
        for target in action.targets:
            # Evaluate selector to get valid components
            components = target.selector.evaluate(ctx)
            # Convert components to component IDs (strings)
            valid_targets = [str(c.id) for c in components][:target.count]
            
            additional_targets.append({
                "id": target.id,
                "name": target.name or f"Target {target.id}",
                "target_type": target.target_type,
                "count": target.count,
                "selector": target.selector,
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
            if target.target_type == "zone":
                # For zone selectors, we'd need to extract zone name from the selector
                # This is a simplified check - you may need to enhance this based on
                # how zone selectors are structured in your expression system
                # TODO: fix with better implementation
                if hasattr(target.selector, 'name') and target.selector.kind == "sel.zone":
                    drag_targets.append(target.selector.name)
        
        return drag_targets
    
    def _can_take_action(self, action: ActionDefinition, game_state: GameState, player_id: str) -> bool:
        """Check if a player can take a specific action"""
        #Check Zone and Phase Conditions
        current_phase = game_state.current_phase
        if action.phase_ids and current_phase not in action.phase_ids:
            return False

        # Check preconditions using expression evaluation
        player_component = game_state.get_player(player_id)
        if not player_component:
            return False
        
        ctx = EvalContext(
            source=player_component,
            event=None,
            targets=(),
            game=game_state,
            phase=str(game_state.current_phase),
            turn=game_state.turn_number
        )
        
        for precondition in action.preconditions:
            if not precondition.evaluate(ctx):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: Predicate, ctx: EvalContext) -> bool:
        """Evaluate a predicate condition using expression evaluation"""
        return condition.evaluate(ctx)
    
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
    
    def _get_target_options(self, targets: List, game_state: GameState, player_id: str) -> Dict[str, Any]:
        """Get available target options for an action"""
        target_options = {}
        
        player_component = game_state.get_player(player_id)
        if not player_component:
            return target_options
        
        ctx = EvalContext(
            source=player_component,
            event=None,
            targets=(),
            game=game_state,
            phase=str(game_state.current_phase),
            turn=game_state.turn_number
        )
        
        for target in targets:
            # Evaluate selector to get valid components
            components = target.selector.evaluate(ctx)
            # Convert components to component IDs (strings)
            valid_targets = [str(c.id) for c in components][:target.count]
            
            target_options[target.id] = {
                "selector": target.selector,
                "count": target.count,
                "valid_targets": valid_targets
            }
        
        return target_options
    
    def _evaluate_selector(self, selector: Selector, ctx: EvalContext) -> List[Component]:
        """Evaluate a selector expression to get valid components"""
        return list(selector.evaluate(ctx))
    
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
    
    def _trigger_matches(self, trigger, event: Event, game_state: GameState) -> bool:
        """Check if trigger matches event (filters and conditions only)"""
        # Event type already matched by index lookup
        
        # Match filters
        filters = trigger.when.get("filters", {})
        for key, value in filters.items():
            if event.payload.get(key) != value:
                return False
        
        # Get source component for evaluation context
        # Try to get component from event.caused_by, otherwise use game component
        source_component = game_state.get_game_component_instance()
        if event.caused_by:
            try:
                # Try to get component from caused_by if it's a component ID
                component_id = int(event.caused_by) if isinstance(event.caused_by, str) else None
                if component_id:
                    comp = game_state.get_component(component_id)
                    if comp:
                        source_component = comp
            except (ValueError, TypeError):
                pass
        
        if not source_component:
            # Fallback: create a minimal component context
            # This shouldn't happen in normal operation
            return trigger.condition is None
        
        # Create evaluation context
        ctx = EvalContext(
            source=source_component,
            event=event.to_dict() if hasattr(event, 'to_dict') else {
                "type": event.type,
                "payload": event.payload,
                "caused_by": event.caused_by
            },
            targets=(),
            game=game_state,
            phase=str(game_state.current_phase),
            turn=game_state.turn_number
        )
        
        # Check condition using expression evaluation
        if trigger.condition is not None:
            if not trigger.condition.evaluate(ctx):
                return False
        
        return True
    
    def _trigger_conditions_met_for_source(self, trigger, event: Event, game_state: GameState, source_obj: Dict[str, str]) -> bool:
        """Check if trigger conditions are met for a specific source object"""
        # Get the source component
        source_component = None
        if source_obj and "object_id" in source_obj:
            try:
                component_id = int(source_obj["object_id"])
                source_component = game_state.get_component(component_id)
            except (ValueError, TypeError):
                pass
        
        # Fallback to game component if source not found
        if not source_component:
            source_component = game_state.get_game_component_instance()
        
        if not source_component:
            return trigger.condition is None
        
        # Create evaluation context with source component
        ctx = EvalContext(
            source=source_component,
            event=event.to_dict() if hasattr(event, 'to_dict') else {
                "type": event.type,
                "payload": event.payload,
                "caused_by": event.caused_by
            },
            targets=(),
            game=game_state,
            phase=str(game_state.current_phase),
            turn=game_state.turn_number
        )
        
        # Evaluate condition in context of the source object
        if trigger.condition is not None:
            if not trigger.condition.evaluate(ctx):
                return False
        
        return True
    
    
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