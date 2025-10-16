"""
Match Actor - Single-threaded game state manager
"""

from typing import Dict, Any, List, Optional, Callable
from core.state import GameState
from core.events import Event, Reaction, StackItem, PendingInput, EventStatus, StackItemType, PHASE_ENTERED, PHASE_EXITED, ACTION_EXECUTED, RULE_EXECUTED
from core.stack import EventStack
from core.rng import DeterministicRNG
from .interpreter import RulesetInterpreter
from .registry import EventRegistry, ReactionRegistry
from ruleset.ir import SelectableObjectType


class MatchActor:
    """Single-threaded actor that manages a match's game state"""
    
    def __init__(self, match_id: str, ruleset_ir: Dict[str, Any], seed: int = None, verbose: bool = False):
        self.match_id = match_id
        self.ruleset_ir = ruleset_ir
        self.verbose = verbose
        
        # Convert dict to RulesetIR object
        from ruleset.ir import RulesetIR
        ruleset_obj = RulesetIR.from_dict(ruleset_ir)
        self.interpreter = RulesetInterpreter(ruleset_obj)
        
        # Initialize game state
        self.state = GameState(match_id=match_id, active_player="player1")
        
        # Initialize resource manager
        from ruleset.models import GameResourceManager
        resource_manager = GameResourceManager(ruleset_obj.resources)
        resource_manager.initialize_global_resources()
        self.state.set_resource_manager(resource_manager)
        
        # Initialize stack and RNG
        self.stack = EventStack()
        self.rng = DeterministicRNG(seed or hash(match_id))
        
        # Initialize registries
        self.event_registry = EventRegistry()
        self.reaction_registry = ReactionRegistry()
        
        # Pending inputs
        self.pending_inputs: List[PendingInput] = []
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Initialize match
        self._initialize_match()
    
    def _initialize_match(self) -> None:
        """Initialize the match with starting state"""
        # Emit initial events
        initial_events = [
            Event(
                type="MatchStarted",
                payload={"match_id": self.match_id},
                order=self.stack.get_next_order()
            ),
            Event(
                type="PhaseChanged",
                payload={"phase": 1, "step": 1},
                order=self.stack.get_next_order()
            )
        ]
        
        for event in initial_events:
            self.state.apply_event(event)
    
    async def begin_game(self) -> None:
        """Begin the game"""
        # Create and register initial event
        start_match_event = Event(
            type="MatchStarted",
            payload={"match_id": self.match_id},
            order=self.stack.get_next_order()
        )
        event_id = self.event_registry.register(start_match_event)
        
        # Push event ID to stack
        self.stack.push(StackItem(
            kind=StackItemType.EVENT,
            ref_id=event_id,
            created_at_order=self.stack.get_next_order()
        ))

        await self._resolve_stack()
        
        
    
    async def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process a player action"""
        try:
            # 1. Validate action
            if not self._validate_action(action):
                return {"error": "Invalid action", "action": action}
            
            # 2. Pay costs (if any)
            await self._pay_action_costs(action)
            
            # 3. Create and register ActionExecuted event
            action_event = Event(
                type=ACTION_EXECUTED,
                payload={"action_id": action["type"], "player_id": action["player_id"]},
                order=self.stack.get_next_order(),
                caused_by=action["player_id"]
            )
            event_id = self.event_registry.register(action_event)
            
            # 4. Push to stack and resolve
            self.stack.push(StackItem(
                kind=StackItemType.EVENT,
                ref_id=event_id,
                created_at_order=self.stack.get_next_order()
            ))
            await self._resolve_stack()
            
            return {"success": True, "events": [action_event.to_dict()]}
            
        except Exception as e:
            return {"error": str(e), "action": action}
    
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """Validate an action against the ruleset"""
        # This would use the ruleset interpreter to validate
        return self.interpreter.validate_action(action, self.state, action["player_id"])
    
    async def advance_phase(self, next_phase_id: int) -> None:
        """Advance to next phase"""
        current_phase = self.state.current_phase
        
        # 1. Create and register PhaseExited event
        exit_event = Event(
            type=PHASE_EXITED,
            payload={"phase_id": current_phase},
            order=self.stack.get_next_order()
        )
        exit_event_id = self.event_registry.register(exit_event)
        
        # 2. Create and register PhaseEntered event
        enter_event = Event(
            type=PHASE_ENTERED,
            payload={"phase_id": next_phase_id},
            order=self.stack.get_next_order()
        )
        enter_event_id = self.event_registry.register(enter_event)
        
        # 3. Push to stack and resolve
        self.stack.push(StackItem(
            kind=StackItemType.EVENT,
            ref_id=exit_event_id,
            created_at_order=self.stack.get_next_order()
        ))
        self.stack.push(StackItem(
            kind=StackItemType.EVENT,
            ref_id=enter_event_id,
            created_at_order=self.stack.get_next_order()
        ))
        await self._resolve_stack()
    
    async def _pay_action_costs(self, action: Dict[str, Any]) -> None:
        """Pay costs for an action"""
        # This would be implemented to handle resource costs
        pass
    
    async def _resolve_stack(self) -> None:
        """Resolve event stack"""
        while not self.stack.is_empty():
            item = self.stack.pop()
            
            if item.kind == StackItemType.EVENT:
                await self._resolve_event(item)
            elif item.kind == StackItemType.REACTION:
                await self._resolve_reaction(item)
    
    async def _resolve_event(self, item: StackItem) -> None:
        """Resolve an event"""
        # Get event from registry
        event = self.event_registry.get(item.ref_id)

        if self.verbose:
            print(f"🔍 Resolving event: {event.type} {event.payload}")

        if not event:
            return  # Event already cleaned up or missing
        
        # 1. Discover triggers that match this event
        reactions = self.interpreter.discover_reactions(event, self.state)
        
        # 2. Execute rules from triggers
        for reaction in reactions:
            # Register reaction and push to stack
            reaction_id = self.reaction_registry.register(reaction)
            self.stack.push(StackItem(
                kind=StackItemType.REACTION,
                ref_id=reaction_id,
                created_at_order=self.stack.get_next_order()
            ))
        
        # 3. Execute rules from actions (if ActionExecuted event)
        if event.type == ACTION_EXECUTED:
            action_def = self.interpreter._action_cache.get(event.payload.get("action_id"))
            if action_def and action_def.execute_rules:
                for rule_id in action_def.execute_rules:
                    new_events = self.interpreter.rule_executor.execute_rule(
                        rule_id, event.caused_by, self.state
                    )
                    # Register and push new events to stack
                    for evt in new_events:
                        event_id = self.event_registry.register(evt)
                        self.stack.push(StackItem(
                            kind=StackItemType.EVENT,
                            ref_id=event_id,
                            created_at_order=self.stack.get_next_order()
                        ))
        
        # 4. Apply event to state
        self.state.apply_event(event)
        
        # 5. Clean up event from registry after successful resolution
        self.event_registry.unregister(item.ref_id)
    
    async def _resolve_reaction(self, item: StackItem) -> None:
        """Resolve a reaction"""
        # Get reaction from registry
        reaction = self.reaction_registry.get(item.ref_id)
        if not reaction:
            return  # Reaction already cleaned up or missing
        
        if self.verbose:
            print(f"‼️ Resolving reaction: {reaction.when} {reaction.effects} {reaction.caused_by}")

        # Execute reaction effects
        for rule_id in reaction.effects:
            new_events = self.interpreter.rule_executor.execute_rule(
                rule_id, reaction.caused_by, self.state
            )
            # Register and push new events to stack
            for evt in new_events:
                event_id = self.event_registry.register(evt)
                self.stack.push(StackItem(
                    kind=StackItemType.EVENT,
                    ref_id=event_id,
                    created_at_order=self.stack.get_next_order()
                ))
        
        # Clean up reaction from registry after successful resolution
        self.reaction_registry.unregister(item.ref_id)
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return self.state.to_dict()
    
    def get_available_actions(self, player_id: str) -> List[Dict[str, Any]]:
        """Get available actions for a player"""
        return self.interpreter.get_available_actions(self.state, player_id)
    
    def get_actions_for_object(
        self, 
        player_id: str, 
        object_type: SelectableObjectType,
        object_id: str
    ) -> List[Dict[str, Any]]:
        """Get available actions for a player with selected object"""
        return self.interpreter.get_actions_for_object(
            self.state, player_id, object_type, object_id
        )
    
    def submit_input(self, input_id: str, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Submit answers to a pending input"""
        # Find the pending input
        pending_input = None
        for pi in self.pending_inputs:
            if pi.input_id == input_id:
                pending_input = pi
                break
        
        if not pending_input:
            return {"error": "Input not found"}
        
        # Validate answers against constraints
        if not self._validate_input_answers(pending_input, answers):
            return {"error": "Invalid answers"}
        
        # Remove from pending inputs
        self.pending_inputs.remove(pending_input)
        
        # Continue resolution
        # This would resume the paused resolution
        
        return {"success": True}
    
    def _validate_input_answers(self, pending_input: PendingInput, answers: Dict[str, Any]) -> bool:
        """Validate input answers against constraints"""
        # Basic validation for now
        return True
    
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event: Event) -> None:
        """Emit an event and notify handlers"""
        self.state.apply_event(event)
        
        # Notify handlers
        if event.type in self.event_handlers:
            for handler in self.event_handlers[event.type]:
                handler(event)
