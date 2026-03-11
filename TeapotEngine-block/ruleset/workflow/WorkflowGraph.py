"""
Workflow graph data structures for state machine-based component workflows
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from TeapotEngine.ruleset.workflow.WorkflowEdge import WorkflowEdge


class NodeType(str, Enum):
    """Type of workflow node"""
    START = "start"  # Start point of the workflow
    END = "end"  # End point of the workflow
    INTERMEDIATE = "intermediate"  # Regular intermediate node
    PARALLEL_START = "parallel_start"  # Start of parallel branch
    PARALLEL_END = "parallel_end"  # End of parallel branch (joins branches)


class WorkflowNode(BaseModel):
    """Represents a node in the workflow graph.
    
    The component_definition_id links this node to a child component definition.
    The type of component is inferred from the parent:
    - TurnComponent nodes → PhaseComponentDefinition
    - PhaseComponent nodes → StepComponentDefinition (or step metadata)
    - GameComponent nodes → TurnComponentDefinition
    """
    id: str  # Unique identifier for the node
    name: str  # Human-readable name
    node_type: NodeType = NodeType.INTERMEDIATE
    component_definition_id: Optional[int] = None  # Links to child component definition
    component_id: Optional[int] = None  # Links to the component instance
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Available inputs at this workflow node
    available_input_ids: List[int] = Field(default_factory=list)


class WorkflowGraph(BaseModel):
    """Container for workflow graph nodes and edges.
    
    The graph always contains implicit start and end nodes with reserved IDs.
    The 'nodes' list only contains intermediate nodes (the "middle" of the workflow).
    Edges can reference the start node (START_NODE_ID) as source and 
    the end node (END_NODE_ID) as target.
    """
    # Reserved node IDs for implicit start and end nodes
    START_NODE_ID: str = "__start__"
    END_NODE_ID: str = "__end__"
    
    nodes: List[WorkflowNode] = Field(default_factory=list)  # Only intermediate nodes
    edges: List[WorkflowEdge] = Field(default_factory=list)
    
    model_config = {"arbitrary_types_allowed": True}
    
    @property
    def start_node(self) -> WorkflowNode:
        """Get the implicit start node (always exists)"""
        return WorkflowNode(
            id=self.START_NODE_ID,
            name="Start",
            node_type=NodeType.START
        )
    
    @property
    def end_node(self) -> WorkflowNode:
        """Get the implicit end node (always exists)"""
        return WorkflowNode(
            id=self.END_NODE_ID,
            name="End",
            node_type=NodeType.END
        )
    
    @property
    def all_nodes(self) -> List[WorkflowNode]:
        """Get all nodes including implicit start and end nodes"""
        return [self.start_node] + list(self.nodes) + [self.end_node]
    
    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """Get a node by ID (includes implicit start/end nodes)"""
        if node_id == self.START_NODE_ID:
            return self.start_node
        if node_id == self.END_NODE_ID:
            return self.end_node
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_entry_node(self) -> WorkflowNode:
        """Get the entry node (always the implicit start node)"""
        return self.start_node
    
    def get_exit_node(self) -> WorkflowNode:
        """Get the exit node (always the implicit end node)"""
        return self.end_node
    
    def get_first_nodes(self) -> List[WorkflowNode]:
        """Get the first intermediate nodes (nodes connected from start)"""
        first_node_ids = {edge.to_node_id for edge in self.edges if edge.from_node_id == self.START_NODE_ID}
        return [node for node in self.nodes if node.id in first_node_ids]
    
    def get_last_nodes(self) -> List[WorkflowNode]:
        """Get the last intermediate nodes (nodes connected to end)"""
        last_node_ids = {edge.from_node_id for edge in self.edges if edge.to_node_id == self.END_NODE_ID}
        return [node for node in self.nodes if node.id in last_node_ids]
    
    def get_outgoing_edges(self, node_id: str) -> List[WorkflowEdge]:
        """Get all outgoing edges from a node"""
        return [edge for edge in self.edges if edge.from_node_id == node_id]
    
    def get_incoming_edges(self, node_id: str) -> List[WorkflowEdge]:
        """Get all incoming edges to a node"""
        return [edge for edge in self.edges if edge.to_node_id == node_id]
    
    def validate_graph(self) -> Tuple[bool, Optional[str]]:
        """Validate the workflow graph structure
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Build set of all valid node IDs (including implicit start/end)
        node_ids = {node.id for node in self.nodes}
        node_ids.add(self.START_NODE_ID)
        node_ids.add(self.END_NODE_ID)
        
        # Check that all edges reference valid nodes
        for edge in self.edges:
            if edge.from_node_id not in node_ids:
                return False, f"Edge references invalid source node: {edge.from_node_id}"
            if edge.to_node_id not in node_ids:
                return False, f"Edge references invalid target node: {edge.to_node_id}"
        
        # Check that start node has at least one outgoing edge (if there are intermediate nodes)
        if self.nodes:
            start_edges = self.get_outgoing_edges(self.START_NODE_ID)
            if not start_edges:
                return False, "Start node must have at least one outgoing edge when intermediate nodes exist"
            
            # Check that end node has at least one incoming edge
            end_edges = self.get_incoming_edges(self.END_NODE_ID)
            if not end_edges:
                return False, "End node must have at least one incoming edge when intermediate nodes exist"
        
        # Check that no edges go INTO start or OUT OF end
        for edge in self.edges:
            if edge.to_node_id == self.START_NODE_ID:
                return False, "No edges can target the start node"
            if edge.from_node_id == self.END_NODE_ID:
                return False, "No edges can originate from the end node"
        
        return True, None


class WorkflowState(BaseModel):
    """Tracks the current state of a workflow instance.
    
    Encapsulates both the workflow graph structure and the current position
    within that graph. This provides a self-contained workflow instance.
    """
    graph: WorkflowGraph  # The workflow structure
    current_node_id: Optional[str] = None  # Current node in the workflow
    history: List[str] = Field(default_factory=list)  # History of visited nodes
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Instance-specific metadata
    
    model_config = {"arbitrary_types_allowed": True}
    
    def get_current_node(self) -> Optional[WorkflowNode]:
        """Get the current workflow node.
        
        Returns:
            Current WorkflowNode if position is set, None otherwise
        """
        if not self.current_node_id:
            return None
        return self.graph.get_node(self.current_node_id)
    
    def get_outgoing_edges(self) -> List[WorkflowEdge]:
        """Get all outgoing edges from the current node.
        
        Returns:
            List of WorkflowEdge objects from current node, empty if no current node
        """
        if not self.current_node_id:
            return []
        return self.graph.get_outgoing_edges(self.current_node_id)
    
    def enter_node(self, node_id: str) -> None:
        """Enter a new node"""
        if self.current_node_id:
            self.history.append(self.current_node_id)
        self.current_node_id = node_id
    
    def exit_node(self) -> Optional[str]:
        """Exit the current node and return to previous node if available"""
        if self.current_node_id:
            self.history.append(self.current_node_id)
        previous = self.current_node_id
        self.current_node_id = None
        return previous
    
    def reset(self) -> None:
        """Reset workflow state (position and history, keeps graph)"""
        self.current_node_id = None
        self.history.clear()
        self.metadata.clear()
    
    @classmethod
    def from_graph(cls, graph: WorkflowGraph) -> "WorkflowState":
        """Create a new workflow state from a graph, starting at the start node.
        
        Args:
            graph: WorkflowGraph to create state for
            
        Returns:
            New WorkflowState positioned at the start node
        """
        state = cls(graph=graph)
        state.enter_node(graph.START_NODE_ID)
        return state
