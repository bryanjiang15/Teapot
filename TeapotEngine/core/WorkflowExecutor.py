"""
Workflow execution engine for component-based state machines
"""

from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING
from TeapotEngine.ruleset.workflow.WorkflowGraph import (
    WorkflowGraph,
    WorkflowNode,
    WorkflowEdge,
    WorkflowState
)
from TeapotEngine.ruleset.ComponentDefinition import ComponentDefinition
from .Component import Component
from .Events import Event
from TeapotEngine.ruleset.ExpressionModel import EvalContext

if TYPE_CHECKING:
    from .GameState import GameState


class WorkflowExecutor:
    """Stateless executor for workflow graph transitions.
    
    This class does not hold any state - all methods receive game_state as a parameter.
    This avoids circular imports and makes the executor easier to test.
    """
    
    def get_valid_transitions(
        self,
        component: Component,
        definition: ComponentDefinition,
        game_state: "GameState"
    ) -> List[WorkflowEdge]:
        """Get all valid transitions from the current node
        
        Args:
            component: Component instance with workflow state
            definition: Component definition with workflow graph
            game_state: GameState instance for evaluating conditions
        
        Returns:
            List of valid WorkflowEdge objects that can be taken
        """
        if not component.workflow_state or not component.workflow_state.current_node_id:
            return []
        
        if not hasattr(definition, 'workflow_graph') or not definition.workflow_graph:
            return []
        
        workflow_graph = definition.workflow_graph
        current_node_id = component.workflow_state.current_node_id
        
        # Get all outgoing edges
        outgoing_edges = workflow_graph.get_outgoing_edges(current_node_id)
        
        # Filter edges based on conditions
        valid_edges = []
        for edge in outgoing_edges:
            if self._evaluate_edge_condition(edge, component, definition, game_state):
                valid_edges.append(edge)
        
        # Sort by priority (higher priority first)
        valid_edges.sort(key=lambda e: e.priority, reverse=True)
        
        return valid_edges
    
    def _evaluate_edge_condition(
        self,
        edge: WorkflowEdge,
        component: Component,
        definition: ComponentDefinition,
        game_state: "GameState"
    ) -> bool:
        """Evaluate whether an edge condition is satisfied
        
        Args:
            edge: WorkflowEdge to evaluate
            component: Component instance
            definition: Component definition
            game_state: GameState instance for evaluating conditions
        
        Returns:
            True if condition is satisfied or no condition exists, False otherwise
        """
        if edge.condition is None:
            return True
        
        # Create evaluation context
        try:
            ctx = EvalContext(
                source=component,
                event=None,
                targets=[],
                game=game_state,
                phase=str(game_state.current_phase),
                turn=game_state.turn_number
            )
            
            return edge.condition.evaluate(ctx)
        except Exception:
            # If evaluation fails, assume condition is not satisfied
            return False
    
    def transition_to_node(
        self,
        component: Component,
        definition: ComponentDefinition,
        target_node_id: str,
        game_state: "GameState"
    ) -> bool:
        """Transition component to a target node
        
        Args:
            component: Component instance to transition
            definition: Component definition with workflow graph
            target_node_id: ID of target node
            game_state: GameState instance for evaluating conditions
        
        Returns:
            True if transition was successful, False otherwise
        """
        if not hasattr(definition, 'workflow_graph') or not definition.workflow_graph:
            return False
        
        workflow_graph = definition.workflow_graph
        
        # Validate target node exists
        target_node = workflow_graph.get_node(target_node_id)
        if not target_node:
            return False
        
        # Check if transition is valid
        valid_edges = self.get_valid_transitions(component, definition, game_state)
        valid_target_ids = {edge.to_node_id for edge in valid_edges}
        
        if target_node_id not in valid_target_ids:
            return False
        
        # Exit current node if exists
        if component.workflow_state and component.workflow_state.current_node_id:
            component.workflow_state.exit_node()
        
        # Enter target node
        if not component.workflow_state:
            from TeapotEngine.ruleset.workflow.WorkflowGraph import WorkflowState
            component.workflow_state = WorkflowState()
        
        component.workflow_state.enter_node(target_node_id)
        
        return True
    
    def enter_workflow(
        self,
        component: Component,
        definition: ComponentDefinition,
    ) -> bool:
        """Enter a workflow at its entry node
        
        Args:
            component: Component instance
            definition: Component definition with workflow graph
        
        Returns:
            True if workflow was entered successfully, False otherwise
        """
        if not hasattr(definition, 'workflow_graph') or not definition.workflow_graph:
            return False
        
        workflow_graph = definition.workflow_graph
        entry_node = workflow_graph.get_entry_node()
        
        if not entry_node:
            return False
        
        # Enter target node directly (no transition validation needed for entry)
        if not component.workflow_state:
            from TeapotEngine.ruleset.workflow.WorkflowGraph import WorkflowState
            component.workflow_state = WorkflowState()
        
        component.workflow_state.enter_node(entry_node.id)
        
        return True
    
    def exit_workflow(
        self,
        component: Component,
        definition: ComponentDefinition,
        game_state: "GameState"
    ) -> bool:
        """Exit a workflow (transition to exit node)
        
        Args:
            component: Component instance
            definition: Component definition with workflow graph
            game_state: GameState instance for evaluating conditions
        
        Returns:
            True if workflow was exited successfully, False otherwise
        """
        if not component.workflow_state or not component.workflow_state.current_node_id:
            return False
        
        if not hasattr(definition, 'workflow_graph') or not definition.workflow_graph:
            return False
        
        workflow_graph = definition.workflow_graph
        exit_nodes = workflow_graph.get_exit_nodes()
        
        if not exit_nodes:
            # No exit nodes defined, just reset workflow state
            component.workflow_state.reset()
            return True
        
        # Transition to first exit node
        return self.transition_to_node(component, definition, exit_nodes[0].id, game_state)
    
    def get_current_node(
        self,
        component: Component,
        definition: ComponentDefinition
    ) -> Optional[WorkflowNode]:
        """Get the current workflow node for a component
        
        Args:
            component: Component instance
            definition: Component definition with workflow graph
        
        Returns:
            Current WorkflowNode or None
        """
        return component.get_current_workflow_node(definition)
    
    def can_exit_workflow(
        self,
        component: Component,
        definition: ComponentDefinition,
        game_state: "GameState"
    ) -> bool:
        """Check if workflow can be exited from current node
        
        Args:
            component: Component instance
            definition: Component definition with workflow graph
            game_state: GameState instance for evaluating conditions
        
        Returns:
            True if workflow can be exited, False otherwise
        """
        if not component.workflow_state or not component.workflow_state.current_node_id:
            return False
        
        if not hasattr(definition, 'workflow_graph') or not definition.workflow_graph:
            return False
        
        workflow_graph = definition.workflow_graph
        exit_nodes = workflow_graph.get_exit_nodes()
        
        if not exit_nodes:
            return True  # Can always exit if no exit nodes defined
        
        # Check if there's a valid path to any exit node
        valid_edges = self.get_valid_transitions(component, definition, game_state)
        
        exit_node_ids = {node.id for node in exit_nodes}
        valid_target_ids = {edge.to_node_id for edge in valid_edges}
        
        # Check if we can directly transition to an exit node
        if exit_node_ids.intersection(valid_target_ids):
            return True
        
        # TODO: Could implement pathfinding here to check if exit is reachable
        return False
