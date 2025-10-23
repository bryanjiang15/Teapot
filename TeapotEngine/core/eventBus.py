"""
Event bus for managing trigger subscriptions with dynamic registration
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from .events import Event, Reaction
from .component import Component
from ruleset.rule_definitions import TriggerDefinition


@dataclass
class TriggerSubscription:
    """Represents a registered trigger subscription"""
    id: int  # Auto-incrementing integer ID
    event_type: str
    trigger: TriggerDefinition
    component_id: int  # Component instance ID that has this trigger
    metadata: Dict[str, Any]  # For future priority: entered_play_turn, controller_id
    # TODO: Add priority field for future state-dependent ordering


class EventBus:
    """Manages trigger subscriptions and event dispatch"""
    
    def __init__(self):
        # event_type -> List[TriggerSubscription]
        self._subscriptions: Dict[str, List[TriggerSubscription]] = {}
        # source_id -> List[subscription_id] for efficient cleanup
        self._source_subscriptions: Dict[int, List[int]] = {}
        # Auto-incrementing ID counter
        self._next_subscription_id: int = 1
    
    def subscribe(self, event_type: str, trigger: TriggerDefinition, component_id: int, 
                  metadata: Optional[Dict[str, Any]] = None) -> int:
        """Register a trigger subscription"""
        subscription_id = self._next_subscription_id
        self._next_subscription_id += 1
        
        subscription = TriggerSubscription(
            id=subscription_id,
            event_type=event_type,
            trigger=trigger,
            component_id=component_id,
            metadata=metadata or {}
        )
        
        # Add to event type index
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
        self._subscriptions[event_type].append(subscription)
        
        # Add to component index for cleanup
        if component_id not in self._source_subscriptions:
            self._source_subscriptions[component_id] = []
        self._source_subscriptions[component_id].append(subscription_id)
        
        return subscription_id
    
    def unsubscribe(self, subscription_id: int) -> bool:
        """Remove a trigger subscription by ID"""
        # Find the subscription
        for event_type, subscriptions in self._subscriptions.items():
            for i, sub in enumerate(subscriptions):
                if sub.id == subscription_id:
                    # Remove from event type index
                    subscriptions.pop(i)
                    
                    # Remove from component index
                    component_id = sub.component_id
                    if component_id in self._source_subscriptions:
                        if subscription_id in self._source_subscriptions[component_id]:
                            self._source_subscriptions[component_id].remove(subscription_id)
                    
                    return True
        return False
    
    def unsubscribe_all_from_component(self, component_id: int) -> List[int]:
        """Remove all triggers from a specific component"""
        if component_id not in self._source_subscriptions:
            return []
        
        subscription_ids = self._source_subscriptions[component_id].copy()
        for subscription_id in subscription_ids:
            self.unsubscribe(subscription_id)
        
        return subscription_ids
    
    def dispatch(self, event: Event, game_state) -> List[Reaction]:
        """Find matching triggers and return Reactions"""
        # Get triggers subscribed to this event type
        subscriptions = self._subscriptions.get(event.type, []).copy()
        
        # Also check wildcard subscriptions if any
        subscriptions.extend(self._subscriptions.get("*", []))
        
        reactions = []
        for sub in subscriptions:
            # Check if trigger should be active right now
            if not self._is_trigger_active(sub, game_state):
                continue
                
            # Check if trigger matches event (filters, conditions)
            if self._trigger_matches(sub.trigger, event, game_state):
                # Create reaction with proper caused_by
                reaction = self._create_reaction_from_trigger(sub.trigger, sub.component_id, event, game_state)
                reactions.append(reaction)
        
        # TODO: Sort reactions by priority before returning
        # For now, return in registration order (deterministic)
        return reactions
    
    def _is_trigger_active(self, subscription: TriggerSubscription, game_state) -> bool:
        """Check if a trigger should be active based on its active_while condition"""
        trigger = subscription.trigger
        
        # If no active_while condition, always active
        if not trigger.active_while:
            return True
        
        # Get the component instance
        component = self._get_component_instance(subscription.component_id, game_state)
        if not component or not component.is_active():
            return False
        
        # Check zone-based activation
        if "zones" in trigger.active_while:
            required_zones = trigger.active_while["zones"]
            if component.zone not in required_zones:
                return False
        
        # Check phase-based activation
        if "phases" in trigger.active_while:
            required_phases = trigger.active_while["phases"]
            if hasattr(game_state, 'current_phase') and game_state.current_phase not in required_phases:
                return False
        
        # Add more activation conditions as needed
        return True
    
    def _get_component_instance(self, component_id: int, game_state) -> Optional[Component]:
        """Get component instance from game state"""
        # This assumes game_state has a component_manager
        if hasattr(game_state, 'component_manager'):
            return game_state.component_manager.get_component(component_id)
        return None
    
    
    def _trigger_matches(self, trigger: TriggerDefinition, event: Event, game_state) -> bool:
        """Check if trigger matches event (filters and conditions)"""
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
    
    def _evaluate_condition(self, condition: Dict[str, Any], game_state, event: Event) -> bool:
        """Evaluate a single condition (simplified for now)"""
        # This is a placeholder - in a real implementation, this would
        # use the same condition evaluation logic as the interpreter
        return True
    
    def _create_reaction_from_trigger(self, trigger: TriggerDefinition, component_id: int, 
                                    event: Event, game_state) -> Reaction:
        """Create a Reaction from a trigger"""
        # Determine caused_by based on trigger scope and component
        caused_by = {"object_type": "component", "object_id": str(component_id)}
        
        return Reaction(
            when=trigger.when,
            conditions=trigger.conditions,
            effects=trigger.execute_rules,
            timing=trigger.timing,
            caused_by=caused_by
        )
    
    def get_subscriptions_for_component(self, component_id: int) -> List[TriggerSubscription]:
        """Get all subscriptions for a component (for debugging)"""
        if component_id not in self._source_subscriptions:
            return []
        
        subscription_ids = self._source_subscriptions[component_id]
        subscriptions = []
        
        for event_type, subs in self._subscriptions.items():
            for sub in subs:
                if sub.id in subscription_ids:
                    subscriptions.append(sub)
        
        return subscriptions
    
    def get_all_subscriptions(self) -> Dict[str, List[TriggerSubscription]]:
        """Get all subscriptions (for debugging)"""
        return self._subscriptions.copy()
    
    def get_subscription_count(self) -> int:
        """Get total number of active subscriptions"""
        total = 0
        for subscriptions in self._subscriptions.values():
            total += len(subscriptions)
        return total
    
    def get_next_subscription_id(self) -> int:
        """Get the next subscription ID that will be assigned"""
        return self._next_subscription_id
