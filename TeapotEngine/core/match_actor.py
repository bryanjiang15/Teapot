"""
Match Actor - Single-threaded game state manager
"""

from typing import Dict, Any, List, Optional, Callable
from core.state import GameState
from core.events import Event, Reaction, StackItem, PendingInput, EventStatus, StackItemType
from core.stack import EventStack
from core.rng import DeterministicRNG
from .interpreter import RulesetInterpreter


class MatchActor:
    """Single-threaded actor that manages a match's game state"""
    
    def __init__(self, match_id: str, ruleset_ir: Dict[str, Any], seed: int = None):
        self.match_id = match_id
        self.ruleset_ir = ruleset_ir
        
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
                payload={"phase": "start", "step": "untap"},
                order=self.stack.get_next_order()
            )
        ]
        
        for event in initial_events:
            self.state.apply_event(event)
    
    async def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process a player action"""
        try:
            # Validate action against ruleset
            if not self._validate_action(action):
                return {"error": "Invalid action", "action": action}
            
            # Convert action to events
            events = self._action_to_events(action)
            
            # Push events to stack
            for event in events:
                self.stack.push(StackItem(
                    kind=StackItemType.EVENT,
                    ref_id=event.id,
                    created_at_order=self.stack.get_next_order()
                ))
            
            # Resolve stack
            await self._resolve_stack()
            
            return {"success": True, "events": [e.to_dict() for e in events]}
            
        except Exception as e:
            return {"error": str(e), "action": action}
    
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """Validate an action against the ruleset"""
        # This would use the ruleset interpreter to validate
        return self.interpreter.validate_action(action, self.state, action["player_id"])
    
    def _action_to_events(self, action: Dict[str, Any]) -> List[Event]:
        """Convert an action to events"""
        events = []
        
        if action["type"] == 1:  # play_card
            events.append(Event(
                type="CardPlayed",
                payload={
                    "card_id": action["card_id"],
                    "player_id": action["player_id"]
                },
                order=self.stack.get_next_order()
            ))
        
        elif action["type"] == 2:  # attack
            events.append(Event(
                type="AttackDeclared",
                payload={
                    "attacker_id": action["attacker_id"],
                    "defender_id": action["defender_id"],
                    "player_id": action["player_id"]
                },
                order=self.stack.get_next_order()
            ))
        
        return events
    
    async def _resolve_stack(self) -> None:
        """Resolve the event stack until empty or paused"""
        while not self.stack.is_empty():
            item = self.stack.pop()
            
            if item.kind == StackItemType.EVENT:
                await self._resolve_event(item)
            elif item.kind == StackItemType.REACTION:
                await self._resolve_reaction(item)
    
    async def _resolve_event(self, item: StackItem) -> None:
        """Resolve an event"""
        # Find the event by ID (in a real implementation, you'd store events)
        # For now, just apply the event to state
        pass
    
    async def _resolve_reaction(self, item: StackItem) -> None:
        """Resolve a reaction"""
        # Find the reaction by ID and execute its effects
        pass
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return self.state.to_dict()
    
    def get_available_actions(self, player_id: str) -> List[Dict[str, Any]]:
        """Get available actions for a player"""
        return self.interpreter.get_available_actions(self.state, player_id)
    
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
