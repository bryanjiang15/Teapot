"""
State Watcher Engine - Manages state-based action checking with dirty flag optimization
"""

from typing import Dict, List, Optional, TYPE_CHECKING
from TeapotEngine.ruleset.rule_definitions.RuleDefinition import TriggerDefinition
from TeapotEngine.ruleset.ExpressionModel import EvalContext, Predicate

if TYPE_CHECKING:
    from .GameState import GameState


class StateWatcherEngine:
    """Manages state-based action checking with dirty flag optimization.
    
    State watchers are checked after the event stack empties. When any state
    changes, the engine is marked dirty and all registered watchers are
    evaluated on the next check.
    """
    
    def __init__(self):
        self._watchers: Dict[int, TriggerDefinition] = {}
        self._watchers_by_source: Dict[int, List[int]] = {}
        self._is_dirty: bool = False
        self._next_id: int = 1
    
    def register_watcher(self, watcher: TriggerDefinition, source_component_id: int) -> int:
        """Register a state-based watcher.
        
        Args:
            watcher: The TriggerDefinition with trigger_type=STATE_BASED
            source_component_id: The component that owns this watcher
            
        Returns:
            The assigned watcher ID
        """
        watcher_id = self._next_id
        self._next_id += 1
        self._watchers[watcher_id] = watcher
        
        # Index by source for cleanup when component is removed
        if source_component_id not in self._watchers_by_source:
            self._watchers_by_source[source_component_id] = []
        self._watchers_by_source[source_component_id].append(watcher_id)
        
        return watcher_id
    
    def unregister_watchers_from_source(self, source_component_id: int) -> List[int]:
        """Remove all watchers from a source component.
        
        Args:
            source_component_id: The component whose watchers should be removed
            
        Returns:
            List of removed watcher IDs
        """
        removed = []
        for watcher_id in self._watchers_by_source.get(source_component_id, []):
            if watcher_id in self._watchers:
                del self._watchers[watcher_id]
                removed.append(watcher_id)
        if source_component_id in self._watchers_by_source:
            del self._watchers_by_source[source_component_id]
        return removed
    
    def mark_dirty(self) -> None:
        """Mark state as changed, requiring watcher re-evaluation."""
        self._is_dirty = True
    
    def is_dirty(self) -> bool:
        """Check if state has been marked dirty."""
        return self._is_dirty
    
    def check_watchers(self, game_state: "GameState") -> List[TriggerDefinition]:
        """Check all watchers if state is dirty.
        
        Args:
            game_state: The current game state to evaluate conditions against
            
        Returns:
            List of triggered watchers (watchers whose conditions evaluated to True)
        """
        if not self._is_dirty:
            return []
        
        triggered = []
        for watcher_id, watcher in self._watchers.items():
            if self._evaluate_condition(watcher.condition, game_state):
                triggered.append(watcher)
        
        self._is_dirty = False
        # TODO: Sort by priority when check_priority is implemented
        return triggered
    
    def _evaluate_condition(self, condition: Optional[Predicate], game_state: "GameState") -> bool:
        """Evaluate a state condition predicate.
        
        Args:
            condition: The predicate to evaluate
            game_state: The current game state
            
        Returns:
            True if condition is satisfied, False otherwise
        """
        if condition is None:
            return False
        
        ctx = EvalContext(
            source=None,
            event=None,
            targets=[],
            game=game_state,
            phase=str(game_state.current_phase),
            turn=game_state.turn_number
        )
        
        try:
            return condition.evaluate(ctx)
        except Exception:
            # If evaluation fails, assume condition is not satisfied
            return False
    
    def clear(self) -> None:
        """Clear all watchers and reset dirty flag."""
        self._watchers.clear()
        self._watchers_by_source.clear()
        self._is_dirty = False
    
    def get_watcher_count(self) -> int:
        """Get the number of registered watchers."""
        return len(self._watchers)
    
    def get_watchers_for_component(self, component_id: int) -> List[TriggerDefinition]:
        """Get all watchers registered by a component.
        
        Args:
            component_id: The component to get watchers for
            
        Returns:
            List of TriggerDefinitions registered by the component
        """
        watcher_ids = self._watchers_by_source.get(component_id, [])
        return [self._watchers[wid] for wid in watcher_ids if wid in self._watchers]

