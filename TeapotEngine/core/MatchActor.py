"""
Match Actor - Single-threaded game state manager
"""

from collections import deque
from typing import Dict, Any, List, Optional, Callable, Set

from TeapotEngine.core import Component
from TeapotEngine.core.GameLoopResult import GameLoopResult
from TeapotEngine.ruleset.workflow import WorkflowGraph
from .GameState import GameState
from .Events import *
from .Stack import EventStack
from .rng import DeterministicRNG
from .Interpreter import RulesetInterpreter
from .EventBus import EventBus
from .EventRegistry import EventRegistry, ReactionRegistry
from .WorkflowExecutor import WorkflowExecutor, StepResult
from .PhaseManager import TurnType
from .StateWatcherEngine import StateWatcherEngine
from TeapotEngine.ruleset.IR import RulesetIR
from TeapotEngine.ruleset.rule_definitions.RuleDefinition import SelectableObjectType, TriggerDefinition
from TeapotEngine.ruleset.ComponentDefinition import ComponentType
from TeapotEngine.ruleset.state_watcher import TriggerType
from TeapotEngine.ruleset.system_models.SystemEvent import *


class MatchActor:
    """Single-threaded actor that manages a match's game state"""
    MAX_RECURSION_DEPTH = 100
    
    def __init__(self, match_id: str, ruleset_ir: Dict[str, Any], seed: int = None, verbose: bool = False):
        self.match_id = match_id
        self.ruleset_ir = ruleset_ir
        self.verbose = verbose
        
        # Event bus for trigger management (owned by MatchActor)
        self.event_bus = EventBus()
        
        # Convert dict to RulesetIR object
        ruleset_obj = RulesetIR.from_dict(ruleset_ir)
        self.ruleset = ruleset_obj
        self.interpreter = RulesetInterpreter(ruleset_obj)
        
        # Initialize game state with ruleset
        player_ids = ["player1", "player2"]  # TODO: Make this configurable
        self.state = GameState.from_ruleset(match_id, ruleset_obj, player_ids)
        
        # Initialize stack and RNG
        self.stack = EventStack()
        self.rng = DeterministicRNG(seed or hash(match_id))
        
        # Initialize registries
        self.event_registry = EventRegistry()
        self.reaction_registry = ReactionRegistry()
        
        # Pending inputs
        self.pending_inputs: List[PendingInput] = []

        self.recursion_depth = 0

        self.game_ended = False
        
        # Track which events have had pre-reactions discovered
        self._activated_events: Set[int] = set()
        
        # Workflow executor - stateless, owned by MatchActor
        self.workflow_executor = WorkflowExecutor(verbose=verbose)
        
        # State watcher engine for state-based actions
        self.state_watcher_engine = StateWatcherEngine()

        # Initialize component instances
        self._initialize_component_instances(ruleset_obj)
    
    def _initialize_component_instances(self, ruleset_obj: RulesetIR) -> None:
        """Initialize component instances from unified component definitions"""
        
        # Initialize game component first (if it exists)
        if ruleset_obj.game_component:
            game_component = self.state.create_component(ruleset_obj.game_component)
            # Register triggers for game component
            self.register_component_triggers(game_component)
            # Register state-based watchers
            self._register_component_state_watchers(game_component)

            self.state.game_component = game_component
            self.workflow_executor.initialize_workflow(game_component, self.state, self.ruleset)

        
        # Initialize other components
        for component_data in ruleset_obj.component_definitions:
            
            component_type = component_data.component_type
            
            if component_type == ComponentType.PLAYER:
                # Create player component instances for each player
                # TODO: Fix hardcode player IDs
                for player_id in [3, 4]:
                    player_component = self.state.create_component(
                        component_data, 
                        controller_component_id=player_id
                    )
                    # Register triggers for player component
                    self.register_component_triggers(player_component)
                    # Register state-based watchers
                    self._register_component_state_watchers(player_component)
            
            elif component_type == ComponentType.ZONE:
                # Create zone component instance
                zone_component = self.state.create_component(component_data)
                # Register triggers for zone component
                self.register_component_triggers(zone_component)
                # Register state-based watchers
                self._register_component_state_watchers(zone_component)
            
            else:
                # Custom component - create instance
                custom_component = self.state.create_component(component_data)
                # Register triggers for custom component
                self.register_component_triggers(custom_component)
                # Register state-based watchers
                self._register_component_state_watchers(custom_component)

    def _register_component_state_watchers(self, component) -> None:
        """Register state-based triggers from a component with the StateWatcherEngine"""
        for trigger in component.triggers:
            if trigger.trigger_type == TriggerType.STATE_BASED:
                self.state_watcher_engine.register_watcher(trigger, component.id)
    
    def register_component_triggers(self, component) -> List[int]:
        """Register all triggers for a component instance with the EventBus"""
        subscription_ids = []
        
        for trigger in component.triggers:
            # Only register EVENT triggers (STATE_BASED triggers have when=None)
            if trigger.when is not None:
                event_type = trigger.when.get("eventType")
                if event_type:
                    subscription_id = self.event_bus.subscribe(
                        event_type, trigger, component.id, component.metadata
                    )
                    subscription_ids.append(subscription_id)
        
        return subscription_ids
    
    def unregister_component_triggers(self, component_id: int) -> List[int]:
        """Unregister all triggers for a component instance from the EventBus"""
        return self.event_bus.unsubscribe_all_from_component(component_id)
    
    def register_system_triggers(self) -> List[int]:
        """Register system triggers with the EventBus"""
        subscription_ids = []
        for trigger in self.ruleset.system_triggers:
            # Only register EVENT triggers (STATE_BASED triggers have when=None)
            if trigger.when is not None:
                event_type = trigger.when.get("eventType")
                if event_type:
                    subscription_id = self.event_bus.subscribe(
                        event_type, trigger, 0, {}  # System triggers use component_id=0
                    )
                    subscription_ids.append(subscription_id)
        return subscription_ids
    
    def discover_reactions(self, event: Event, game_state: GameState) -> List[Reaction]:
        """Find all triggers that match an event using EventBus"""
        return self.event_bus.dispatch(event, game_state)
    
    def _rotate_active_player(self) -> None:
        """Rotate to the next active player"""
        if not self.state.player_ids:
            return
            
        try:
            current_index = self.state.player_ids.index(self.state.active_player)
            next_index = (current_index + 1) % len(self.state.player_ids)
            self.state.active_player = self.state.player_ids[next_index]
        except ValueError:
            # Current player not found, use first player
            self.state.active_player = self.state.player_ids[0]
    
    def _check_game_over(self) -> bool:
        """Check if the game is over based on max turns"""
        if not self.state.current_turn_component:
            return False
        
        # Get max_turns from turn component definition, not metadata
        turn_def = self.ruleset.get_component_by_id(
            self.state.current_turn_component.definition_id
        )
        if turn_def:
            max_turns = getattr(turn_def, 'max_turns_per_player', None)
            if max_turns:
                return self.state.turn_number > max_turns
        
        return False
    
    async def begin_game(self) -> None:
        """Begin the game"""
        # Create and push initial event
        start_match_event = Event(
            type="MatchStarted",
            payload={"match_id": self.match_id}
        )

        await self._publish_event(start_match_event)

        current_turn = self.state.game_component.get_current_workflow_node()
        if current_turn and current_turn.component_id:
            turn_component_id = current_turn.component_id
            turn_component = self.state.get_component_by_id(turn_component_id)
            if turn_component:
                start_turn_event = Event(
                    type=TURN_STARTED,
                    payload={"turn": turn_component.name},
                    order=self.stack.get_next_order()
                )
                await self._push_action_and_resolve(start_turn_event)

        await self.run_until_blocked()
        
    
    async def run_until_blocked(self) -> GameLoopResult:
        """Run the game loop, stepping through workflows until blocked or ended.
        
        This continuously steps through the game component's workflow,
        recursively entering child workflows (turns, phases) and executing
        procedures, until it reaches a point where player input is needed
        or the game ends.
        
        Returns:
            GameLoopResult.WAITING_FOR_INPUT if blocked waiting for player action
            GameLoopResult.GAME_ENDED if the game has finished
        """
        while not self.game_ended:
            if self.pending_inputs:
                return GameLoopResult.WAITING_FOR_INPUT
            
            # Step through the game component's workflow
            result, component = self.workflow_executor.step_workflow(
                self.state.game_component,
                game_state=self.state
            )
            
            if result == StepResult.BLOCKED:
                return GameLoopResult.WAITING_FOR_INPUT
            elif result == StepResult.ENDED:
                self.game_ended = True
                break
            # result == StepResult.ADVANCED → continue loop
        
        return GameLoopResult.GAME_ENDED
    
    async def _handle_workflow_transition(
        self, 
        component: Component, 
        transition_type: str  # "entering" or "exiting"
    ) -> None:
        """Called by workflow executor at each transition point."""
        if component.component_type not in (ComponentType.TURN, ComponentType.PHASE):
            return
        
        # Create and process event IMMEDIATELY before state advances further
        if transition_type == "exiting":
            if component.component_type == ComponentType.TURN:
                event = Event(type=TURN_ENDED, payload={"turn": component.name}, order=self.stack.get_next_order())
            else:
                event = Event(type=PHASE_ENDED, payload={"phase": component.name}, order=self.stack.get_next_order())
            await self._push_action_and_resolve(event)
        
        elif transition_type == "entering":
            if component.component_type == ComponentType.TURN:
                event = Event(type=TURN_STARTED, payload={"turn": component.name}, order=self.stack.get_next_order())
            else:
                event = Event(type=PHASE_STARTED, payload={"phase": component.name}, order=self.stack.get_next_order())
            await self._push_action_and_resolve(event)
    

    async def process_event(self, event: Event) -> None:
        """Process an event"""
        reactions = self.discover_reactions(event, self.state)
        for reaction in reactions:
            await self._push_event_and_resolve(reaction)

    
    async def process_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process a player action"""
        try:
            # 1. Validate action
            if not self._validate_action(action):
                return {"error": "Invalid action", "action": action}
            
            # 2. Pay costs (if any)
            await self._pay_action_costs(action)
            
            # 3. Create and push ActionExecuted event
            action_event = Event(
                type=EXECUTE_ACTION,
                payload={"action_id": action["type"], "player_id": action["player_id"]},
                order=self.stack.get_next_order(),
                caused_by=action["player_id"]
            )
            await self._push_action_and_resolve(action_event)

            "Check post-resolution events"
            "If there are no more actions that can be taken, advance to the next phase"
            if await self.check_if_phase_can_exit():
                if self.verbose:
                    print(f"🔍 No actions can be taken, advancing to next phase")
                await self.advance_phase()
            
            return {"success": True, "events": [action_event.to_dict()]}
            
        except Exception as e:
            return {"error": str(e), "action": action}
    
    def _validate_action(self, action: Dict[str, Any]) -> bool:
        """Validate an action against the ruleset"""
        # This would use the ruleset interpreter to validate
        return self.interpreter.validate_action(action, self.state, action["player_id"])
    
    async def _advance_phase_component_based(self) -> None:
        """Advance phase using component-based workflow"""
        phase_component = self.state.current_phase_component
        turn_component = self.state.current_turn_component
        
        # Get phase component definition from ruleset
        phase_def = self.ruleset.get_component_by_id(phase_component.definition_id)
        
        if not phase_def or not hasattr(phase_def, 'workflow_graph'):
            # No workflow graph, end turn
            await self.end_turn()
            return
        
        # Get valid transitions (pass game_state to stateless executor)
        valid_edges = self.workflow_executor.get_valid_transitions(phase_component, phase_def, self.state)
        
        if not valid_edges:
            # No valid transitions, end turn
            await self.end_turn()
            return
        
        # Take first valid transition (highest priority)
        target_node_id = valid_edges[0].to_node_id
        
        # Transition to next phase node
        success = self.workflow_executor.transition_to_node(
            phase_component,
            phase_def,
            target_node_id,
            self.state
        )
        
        if success:
            # Check if we've reached an exit node
            current_node = self.workflow_executor.get_current_node(phase_component)
            if current_node and current_node.node_type.value == "end":
                # Phase ended, need to transition to next phase in turn workflow
                await self._transition_to_next_phase_in_turn()
        else:
            # Transition failed, end turn
            await self.end_turn()
    
    async def _transition_to_next_phase_in_turn(self) -> None:
        """Transition to next phase in turn workflow"""
        turn_component = self.state.current_turn_component
        
        if not turn_component:
            await self.end_turn()
            return
        
        # Get turn component definition from ruleset
        turn_def = self.ruleset.get_component_by_id(turn_component.definition_id)
        
        if not turn_def or not hasattr(turn_def, 'workflow_graph'):
            await self.end_turn()
            return
        
        # Get valid transitions from current turn node
        valid_edges = self.workflow_executor.get_valid_transitions(turn_component, turn_def, self.state)
        
        if not valid_edges:
            # No more phases in turn, end turn
            await self.end_turn()
            return
        
        # Transition to next phase node
        target_node_id = valid_edges[0].to_node_id
        target_node = turn_def.workflow_graph.get_node(target_node_id)
        
        # Find phase component definition for target node
        phase_defs = self.ruleset.get_phase_components()
        target_phase_def = None
        
        if target_node and target_node.component_definition_id is not None:
            # Use explicit component_definition_id
            for phase_def in phase_defs:
                if phase_def.id == target_node.component_definition_id:
                    target_phase_def = phase_def
                    break
        
        if target_phase_def:
            # Create new phase component instance
            new_phase_component = self.state.create_component(target_phase_def)
            
            # Enter workflow
            success = self.workflow_executor.enter_workflow(
                new_phase_component,
                target_phase_def
            )
            
            if success:
                # Update state
                self.state.current_phase_component = new_phase_component
                # Use definition ID, not instance ID
                self.state.current_phase_id = target_phase_def.id
        else:
            await self.end_turn()
    
    async def check_if_phase_can_exit(self) -> bool:
        """Check if the current phase can be exited"""
        actions = self.interpreter.get_available_actions(self.state, self.state.active_player)
        if not actions:
            # No actions available, phase can exit
            if self.state.current_phase_component:
                phase_def = self.interpreter.ruleset.get_component_by_id(
                    self.state.current_phase_component.definition_id
                )
                if phase_def and hasattr(phase_def, 'workflow_graph'):
                    return self.workflow_executor.can_exit_workflow(
                        self.state.current_phase_component, 
                        phase_def, 
                        self.state
                    )
            return True
        return False
    
    async def end_turn(self) -> None:
        """End the current turn and advance to the next turn"""
        # Component-based workflow path
        if self.state.current_turn_component:
            await self._end_turn_component_based()
            return
        
        # No turn component, end game
        await self.end_game()
    
    async def _end_turn_component_based(self) -> None:
        """End turn using component-based workflow"""
        turn_component = self.state.current_turn_component
        
        # 1. Emit TurnEnded event
        turn_ended_event = Event(
            type=TURN_ENDED,
            payload={"turn_number": self.state.turn_number},
            order=self.stack.get_next_order()
        )
        await self._push_action_and_resolve(turn_ended_event)
        
        # 2. Advance turn number
        self.state.turn_number += 1
        self.state.current_step_id = 0
        
        # 3. Rotate active player
        if self.state.turn_type == TurnType.SINGLE_PLAYER:
            self._rotate_active_player()
        
        # 4. Check if game is over
        if self._check_game_over():
            await self.end_game()
            return
        
        # 5. Reset turn component workflow or create new turn instance
        # For now, reset workflow state to entry
        if turn_component.workflow:
            turn_component.workflow.reset()
        
        # Get turn component definition from ruleset
        turn_def = self.ruleset.get_component_by_id(turn_component.definition_id)
        
        if turn_def and hasattr(turn_def, 'workflow_graph'):
            # Enter turn workflow at entry node
            success = self.workflow_executor.enter_workflow(
                turn_component,
                turn_def
            )
            
            # Get first phase from turn workflow
            entry_node = turn_def.workflow_graph.get_entry_node()
            if entry_node:
                # Find and create phase component for entry node
                phase_defs = self.ruleset.get_phase_components()
                target_phase_def = None
                
                if entry_node.component_definition_id is not None:
                    # Use explicit component_definition_id
                    for phase_def in phase_defs:
                        if phase_def.id == entry_node.component_definition_id:
                            target_phase_def = phase_def
                            break
                else:
                    # Fallback: match by name for backward compatibility
                    for phase_def in phase_defs:
                        if phase_def.name == entry_node.name:
                            target_phase_def = phase_def
                            break
                
                if target_phase_def:
                    # Create new phase component instance
                    new_phase_component = self.state.create_component(target_phase_def)
                    
                    # Enter phase workflow
                    success = self.workflow_executor.enter_workflow(
                        new_phase_component,
                        target_phase_def
                    )
                    
                    if success:
                        self.state.current_phase_component = new_phase_component
                        # Use definition ID, not instance ID
                        self.state.current_phase_id = target_phase_def.id
        else:
            await self.end_game()
    
    async def end_game(self) -> None:
        """End the game"""
        end_game_event = Event(
            type=GAME_ENDED,
            payload={"game_id": self.match_id},
            order=self.stack.get_next_order()
        )
        await self._push_action_and_resolve(end_game_event)
    
    async def _pay_action_costs(self, action: Dict[str, Any]) -> None:
        """Pay costs for an action"""
        # This would be implemented to handle resource costs
        pass

    async def _publish_event(self, event: Event) -> None:
        """Publish an event to the event bus"""
        reactions = self.discover_reactions(event, self.state)

        for reaction in reactions:
            reaction_id = self.reaction_registry.register(reaction)
            self.stack.push(StackItem(
                kind=StackItemType.REACTION,
                ref_id=reaction_id,
                created_at_order=self.stack.get_next_order()
            ))
        await self._resolve_stack()
    
    async def _push_action_and_resolve(self, event: Event) -> None:
        """Helper function to push an event to the stack and resolve the stack"""
        # Register the event
        event_id = self.event_registry.register(event)
        
        # Push event ID to stack
        self.stack.push(StackItem(
            kind=StackItemType.EVENT,
            ref_id=event_id,
            created_at_order=self.stack.get_next_order()
        ))
        
        # Resolve the stack
        await self._resolve_stack()

    async def _resolve_stack(self) -> None:
        """Resolve event stack"""
        self.recursion_depth += 1
        if self.recursion_depth > self.MAX_RECURSION_DEPTH:
            raise RecursionError("Maximum recursion depth reached")
        
        if self.game_ended:
            return
        
        while not self.stack.is_empty():
            item = self.stack.peek()  # Peek first instead of popping immediately
            
            if item.kind == StackItemType.EVENT:
                # Check if we've already discovered pre-reactions for this event
                if item.ref_id not in self._activated_events:
                    # Discover pre-reactions before popping
                    pre_reactions = await self._discover_pre_reactions(item)
                    if pre_reactions:
                        # Push pre-reactions (reversed for LIFO)
                        for reaction in reversed(pre_reactions):
                            reaction_id = self.reaction_registry.register(reaction)
                            self.stack.push(StackItem(
                                kind=StackItemType.REACTION,
                                ref_id=reaction_id,
                                created_at_order=self.stack.get_next_order()
                            ))
                        # Mark that we've discovered pre-reactions for this event
                        self._activated_events.add(item.ref_id)
                        # Continue loop - pre-reactions will resolve first
                        continue
                
                # No pre-reactions or already discovered - pop and resolve event
                item = self.stack.pop()
                self._activated_events.discard(item.ref_id)  # Clean up
                event = self.event_registry.get(item.ref_id)
                await self._resolve_event(event)
            elif item.kind == StackItemType.REACTION:
                item = self.stack.pop()
                await self._resolve_reaction(item)
        
        # Stack is empty - check state-based actions
        await self._check_state_based_actions()
    
    async def _discover_pre_reactions(self, item: StackItem) -> List[Reaction]:
        """Discover pre-reactions for an event without popping it"""
        event = self.event_registry.get(item.ref_id)
        if not event:
            return []
        
        all_reactions = self.discover_reactions(event, self.state)
        return [r for r in all_reactions if r.timing == "pre"]
    
    async def _resolve_event(self, event: Event) -> None:
        """Resolve an event."""
        if self.verbose:
            print(f"🔍 Resolving event: {event.type} {event.payload}")
        
        # 1. Discover triggers that match this event (before applying)
        all_reactions = self.discover_reactions(event, self.state)
        
        # Separate pre-reactions from post-reactions
        post_reactions = [r for r in all_reactions if r.timing == "post"]

        # 2. Apply event to state
        self.state.apply_event(event)
        
        # Mark state as dirty for state-based action checking
        self.state_watcher_engine.mark_dirty()

        if event.type == NEXT_PHASE:
            # Phase advancement handled by workflow executor
            await self.advance_phase()
        if event.type == NEXT_TURN:
            # Turn advancement handled by workflow executor
            await self.end_turn()
        if event.type == PHASE_END_REQUESTED:
            phase_id = self.state.current_phase_id
            exit_phase_event = Event(
                type=PHASE_ENDED,
                payload={"phase_id": phase_id},
                order=self.stack.get_next_order()
            )
            self.push_event_to_stack(exit_phase_event)
        if event.type == TURN_END_REQUESTED:
            turn_number = self.state.turn_number
            turn_ended_event = Event(
                type=TURN_ENDED,
                payload={"turn_number": turn_number},
                order=self.stack.get_next_order()
            )
            self.push_event_to_stack(turn_ended_event)
        if event.type == END_GAME:
            self.game_ended = True
            self.stack.clear()

        # 3. Execute rules from actions (if EXECUTE_ACTION event)
        if event.type == EXECUTE_ACTION:
            action_def = self.interpreter._action_cache.get(event.payload.get("action_id"))
            if action_def and action_def.execute_rules:
                for rule_id in action_def.execute_rules:
                    new_events = self.interpreter.rule_executor.execute_rule(
                        rule_id, event.caused_by, self.state
                    )
                    # Register and push new events to stack (Push events backwards to the stack)
                    for evt in reversed(new_events):
                        event_id = self.event_registry.register(evt)
                        self.stack.push(StackItem(
                            kind=StackItemType.EVENT,
                            ref_id=event_id,
                            created_at_order=self.stack.get_next_order()
                        ))
                    
        
        # 4. Push post-reactions to stack
        for reaction in post_reactions:
            # Register reaction and push to stack
            reaction_id = self.reaction_registry.register(reaction)
            self.stack.push(StackItem(
                kind=StackItemType.REACTION,
                ref_id=reaction_id,
                created_at_order=self.stack.get_next_order()
            ))
        
        # 5. Clean up event from registry after successful resolution
        self.event_registry.unregister(event.id)
    
    async def _resolve_reaction(self, item: StackItem) -> None:
        """Resolve a reaction"""
        # Get reaction from registry
        reaction = self.reaction_registry.get(item.ref_id)
        if not reaction:
            return  # Reaction already cleaned up or missing
        
        if self.verbose:
            print(f"‼️ Resolving reaction: {reaction.when} {reaction.effects} {reaction.caused_by}")

        # Execute reaction effects
        new_events = self.interpreter.effect_interpreter.process_effects(
            reaction.effects, self.state, reaction.caused_by
        )
        # Register and push new events to stack
        for evt in new_events:
            self.push_event_to_stack(evt)
        
        # Mark state as dirty for state-based action checking
        self.state_watcher_engine.mark_dirty()
        
        # Clean up reaction from registry after successful resolution
        self.reaction_registry.unregister(item.ref_id)
    
    async def _check_state_based_actions(self) -> None:
        """Check and process state-based actions after stack resolution"""
        if self.game_ended:
            return
        
        max_iterations = 100  # Prevent infinite loops
        
        for _ in range(max_iterations):
            triggered = self.state_watcher_engine.check_watchers(self.state)
            if not triggered:
                break
            
            if self.verbose:
                print(f"🔍 State-based actions triggered: {len(triggered)} watchers")
            
            # TODO: Sort by priority when check_priority is implemented
            for watcher in triggered:
                await self._execute_watcher_effects(watcher)
            
            # Re-resolve any new stack items
            while not self.stack.is_empty():
                item = self.stack.pop()
                if item.kind == StackItemType.EVENT:
                    await self._resolve_event(item)
                elif item.kind == StackItemType.REACTION:
                    await self._resolve_reaction(item)
    
    async def _execute_watcher_effects(self, watcher: TriggerDefinition) -> None:
        """Execute effects from a triggered state watcher"""
        if self.verbose:
            print(f"🔍 Executing state watcher effects: {watcher.id}")
        
        new_events = self.interpreter.effect_interpreter.process_effects(
            watcher.effects, self.state, watcher.caused_by
        )
        for evt in new_events:
            self.push_event_to_stack(evt)
    
    def push_event_to_stack(self, event: Event) -> None:
        """Add an event to the stack"""
        event_id = self.event_registry.register(event)
        self.stack.push(StackItem(
            kind=StackItemType.EVENT,
            ref_id=event_id,
            created_at_order=self.stack.get_next_order()
        ))
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current game state"""
        return self.state.to_dict()
    
    def get_available_actions(self, player_id: str) -> List[Dict[str, Any]]:
        """Get available actions for a player"""
        return self.interpreter.get_available_actions(self.state, player_id)
    
    def get_actions_for_object(
        self, 
        player_id: int, 
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