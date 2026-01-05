"""
Workflow execution engine for component-based state machines
"""

from enum import Enum
from typing import Callable, Dict, Any, List, Optional, Tuple, TYPE_CHECKING
from TeapotEngine.ruleset.IR import RulesetIR
from TeapotEngine.ruleset.workflow import (
    WorkflowNode,
    WorkflowEdge,
    NodeType
)
from TeapotEngine.ruleset.ComponentDefinition import ComponentDefinition, ComponentType
from .Component import Component
from .Events import Event
from TeapotEngine.ruleset.ExpressionModel import EvalContext

if TYPE_CHECKING:
    from .GameState import GameState


class StepResult(Enum):
    """Result of stepping through a workflow"""
    ADVANCED = "advanced"   # Moved to next node
    BLOCKED = "blocked"     # Waiting for user input
    ENDED = "ended"         # Workflow reached end node


class WorkflowExecutor:
    """Stateless executor for workflow graph transitions.
    
    This class does not hold any state - all methods receive game_state as a parameter.
    This avoids circular imports and makes the executor easier to test.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def get_valid_transitions(
        self,
        component: Component,
        definition: ComponentDefinition,
        game_state: "GameState"
    ) -> List[WorkflowEdge]:
        """Get all valid transitions from the current node (legacy method using definition)
        
        Args:
            component: Component instance with workflow
            definition: Component definition (deprecated, uses component.workflow)
            game_state: GameState instance for evaluating conditions
        
        Returns:
            List of valid WorkflowEdge objects that can be taken
        """
        if not component.workflow or not component.workflow.current_node_id:
            return []
        
        # Get all outgoing edges from component's workflow
        outgoing_edges = component.workflow.get_outgoing_edges()
        
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
        """Transition component to a target node (legacy method using definition)
        
        Args:
            component: Component instance to transition
            definition: Component definition (deprecated, uses component.workflow)
            target_node_id: ID of target node
            game_state: GameState instance for evaluating conditions
        
        Returns:
            True if transition was successful, False otherwise
        """
        if not component.workflow:
            return False
        
        # Validate target node exists
        target_node = component.workflow.graph.get_node(target_node_id)
        if not target_node:
            return False
        
        # Check if transition is valid
        valid_edges = self.get_valid_transitions(component, definition, game_state)
        valid_target_ids = {edge.to_node_id for edge in valid_edges}
        
        if target_node_id not in valid_target_ids:
            return False
        
        if self.verbose:
            print(f"Transitioning from node {component.workflow.current_node_id} to node {target_node_id} for component {component.id}")
    
        
        # Exit current node if exists
        if component.workflow.current_node_id:
            component.workflow.exit_node()
        
        # Enter target node
        component.workflow.enter_node(target_node_id)

            
        return True
    
    def initialize_workflow(
        self,
        component: Component,
        game_state: "GameState",
        ruleset: "RulesetIR"
    ) -> bool:
        """Initialize the workflow by creating child component instances for each node"""
        if not component.workflow:
            return False
        
        workflow_graph = component.workflow.graph
        start_node = workflow_graph.start_node
        
        for node in workflow_graph.nodes:
            # Create a new component instance for each node if it has a definition
            if node.component_definition_id:
                definition = ruleset.get_component_by_id(node.component_definition_id)
                if definition:
                    component_instance = game_state.create_component(
                        definition=definition,
                    )
                    node.component_id = component_instance.id
                    self.initialize_workflow(component_instance, game_state, ruleset)
        
        component.workflow.enter_node(start_node.id)
        return True

    def enter_workflow(
        self,
        component: Component,
        definition: ComponentDefinition = None,
    ) -> bool:
        """Enter a workflow at its entry node
        
        Args:
            component: Component instance with workflow
            definition: Deprecated, uses component.workflow
        
        Returns:
            True if workflow was entered successfully, False otherwise
        """
        if not component.workflow:
            return False
        
        start_node = component.workflow.graph.start_node
        
        # Enter start node directly (no transition validation needed for entry)
        component.workflow.enter_node(start_node.id)
        return True
    
    def exit_workflow(
        self,
        component: Component,
        definition: ComponentDefinition = None,
        game_state: "GameState" = None
    ) -> bool:
        """Exit a workflow (transition to exit node)
        
        Args:
            component: Component instance with workflow
            definition: Deprecated, uses component.workflow
            game_state: GameState instance for evaluating conditions
        
        Returns:
            True if workflow was exited successfully, False otherwise
        """
        if not component.workflow or not component.workflow.current_node_id:
            return False
        
        exit_node = component.workflow.graph.get_exit_node()
        
        # Transition to the exit node
        return self.transition_to_node(component, definition, exit_node.id, game_state)
    
    def get_current_node(
        self,
        component: Component,
    ) -> Optional[WorkflowNode]:
        """Get the current workflow node for a component
        
        Args:
            component: Component instance
        
        Returns:
            Current WorkflowNode or None
        """
        return component.get_current_workflow_node()
    
    def can_exit_workflow(
        self,
        component: Component,
        definition: ComponentDefinition = None,
        game_state: "GameState" = None
    ) -> bool:
        """Check if workflow can be exited from current node
        
        Args:
            component: Component instance with workflow
            definition: Deprecated, uses component.workflow
            game_state: GameState instance for evaluating conditions
        
        Returns:
            True if workflow can be exited, False otherwise
        """
        if not component.workflow or not component.workflow.current_node_id:
            return False
        
        exit_node = component.workflow.graph.get_exit_node()
        
        # Check if there's a valid path to the exit node
        valid_edges = self._get_valid_transitions_local(component, game_state)
        valid_target_ids = {edge.to_node_id for edge in valid_edges}
        
        # Check if we can directly transition to the exit node
        if exit_node.id in valid_target_ids:
            return True
        
        # TODO: Could implement pathfinding here to check if exit is reachable
        return False
    
    def advance_workflow(
        self,
        component: Component,
        definition: ComponentDefinition = None,
        game_state: "GameState" = None
    ) -> bool:
        """Advance the workflow to the next node"""
        if not component.workflow or not component.workflow.current_node_id:
            return False
        
        transitions = self._get_valid_transitions_local(component, game_state)
        if not transitions:
            return False
        
        # Take the first valid transition (highest priority)
        target_node_id = transitions[0].to_node_id
        return self.transition_to_node(component, definition, target_node_id, game_state)
    
    def step_workflow(
        self,
        component: Component,
        game_state: "GameState",
        on_transition: Callable[[Component, str], None] = None
    ) -> Tuple[StepResult, Optional[Component]]:
        """Step through workflow, handling both container and procedure nodes.
        
        This method recursively steps through nested workflows:
        - For PROCEDURE components: executes effects and auto-advances
        - For container components (TURN/PHASE): recurses into child workflow
        
        Args:
            component: Component instance with workflow
            game_state: GameState instance for evaluating conditions
        
        Returns:
            Tuple of (StepResult, component_at_current_node or None)
        """
        current_node = component.get_current_workflow_node()
        
        if not current_node:
            return (StepResult.ENDED, None)
        
        
        # End node reached
        if current_node.node_type == NodeType.END:
            return (StepResult.ENDED, None)
        
        # Node has a child component
        if current_node.component_id:
            child = game_state.get_component(current_node.component_id)
            if not child:
                return (StepResult.ENDED, None)
            
            # PROCEDURE: Execute effects and auto-advance
            if child.component_type == ComponentType.PROCEDURE:
                self._execute_procedure(child, game_state)
                return self._advance_to_next(component, game_state)
            
            # CONTAINER (Turn/Phase): Recurse into child workflow
            if child.workflow:
                child_result, child_component = self.step_workflow(child, game_state, on_transition)
                
                if child_result == StepResult.ENDED:
                    # Child finished - advance parent to next node
                    return self._advance_to_next(component, game_state, on_transition)
                else:
                    # Child still running or blocked
                    return (child_result, child_component)
        
        # No child component - check if we can auto-advance
        valid_transitions = self._get_valid_transitions_local(component, game_state)
        if valid_transitions:
            if self.verbose:
                print(f"Auto-advancing from node {current_node.id} to node {valid_transitions[0].to_node_id} for component {component.id}")
            return self._advance_to_next(component, game_state, on_transition)
        
        if self.verbose:
            print(f"No valid transitions found for component {component.id} at node {current_node.id}")
    
        # No valid transitions - blocked waiting for player action
        return (StepResult.BLOCKED, None)
    
    def _get_valid_transitions_local(
        self,
        component: Component,
        game_state: "GameState"
    ) -> List[WorkflowEdge]:
        """Get valid transitions using component's workflow.
        
        Args:
            component: Component instance with workflow
            game_state: GameState instance for evaluating conditions
        
        Returns:
            List of valid WorkflowEdge objects that can be taken
        """
        if not component.workflow or not component.workflow.current_node_id:
            return []
        
        # Get all outgoing edges from workflow
        outgoing_edges = component.workflow.get_outgoing_edges()
        
        # Filter edges based on conditions
        valid_edges = []
        for edge in outgoing_edges:
            if self._evaluate_edge_condition_local(edge, component, game_state):
                valid_edges.append(edge)
        
        # Sort by priority (higher priority first)
        valid_edges.sort(key=lambda e: e.priority, reverse=True)
        
        return valid_edges
    
    def _evaluate_edge_condition_local(
        self,
        edge: WorkflowEdge,
        component: Component,
        game_state: "GameState"
    ) -> bool:
        """Evaluate whether an edge condition is satisfied.
        
        Args:
            edge: WorkflowEdge to evaluate
            component: Component instance
            game_state: GameState instance for evaluating conditions
        
        Returns:
            True if condition is satisfied or no condition exists, False otherwise
        """
        if edge.edge_type == "simple":
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
    
    def _advance_to_next(
        self,
        component: Component,
        game_state: "GameState",
        on_transition: Callable[[Component, str], None] = None
    ) -> Tuple[StepResult, Optional[Component]]:
        """Advance component to the next node in its workflow.
        
        Args:
            component: Component instance to advance
            game_state: GameState instance for evaluating conditions
        
        Returns:
            Tuple of (StepResult, new_node_component or None)
        """
        if not component.workflow:
            return (StepResult.ENDED, None)
        
        valid_transitions = self._get_valid_transitions_local(component, game_state)
        
        if not valid_transitions:
            # No valid transitions - check if we're at an end state
            current_node = component.get_current_workflow_node()
            if current_node and current_node.node_type == NodeType.END:
                return (StepResult.ENDED, None)
            return (StepResult.BLOCKED, None)
        
        # Take the first valid transition (highest priority)
        target_node_id = valid_transitions[0].to_node_id
        
        # Transition to the next node
        exit_node = component.get_current_workflow_node()
        component.workflow.exit_node()
        if on_transition:
            on_transition(exit_node, "exiting")
        component.workflow.enter_node(target_node_id)

        target_node = component.get_current_workflow_node()
        if on_transition:
            on_transition(target_node, "entering")
        
        # Get the new node and its component
        new_node = component.get_current_workflow_node()
        if new_node and new_node.node_type == NodeType.END:
            return (StepResult.ENDED, None)
        
        # Return the new node's component if it exists
        new_component = None
        if new_node and new_node.component_id:
            new_component = game_state.get_component(new_node.component_id)
        
        return (StepResult.ADVANCED, new_component)
    
    def _execute_procedure(self, procedure: Component, game_state: "GameState") -> None:
        """Execute a procedure component's effects.
        
        Args:
            procedure: Procedure component to execute
            game_state: GameState instance
        """
        # Effects are stored in the component's properties or need to be looked up
        # from the definition. For now, we'll check properties first.
        effects = procedure.properties.get('effects', [])
        
        # If no effects in properties, the caller would need to hook into
        # the EffectInterpreter with the definition's effects
        # This is a hook point for the MatchActor to process effects
        pass
