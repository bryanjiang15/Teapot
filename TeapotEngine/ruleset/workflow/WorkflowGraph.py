"""
Workflow graph data structures for state machine-based component workflows
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from TeapotEngine.ruleset.ExpressionModel import Predicate


class NodeType(str, Enum):
    """Type of workflow node"""
    START = "start"  # Start point of the workflow
    END = "end"  # End point of the workflow
    INTERMEDIATE = "intermediate"  # Regular intermediate node
    PARALLEL_START = "parallel_start"  # Start of parallel branch
    PARALLEL_END = "parallel_end"  # End of parallel branch (joins branches)


@dataclass
class WorkflowNode:
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
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type.value,
            "metadata": self.metadata
        }
        if self.component_definition_id is not None:
            result["component_definition_id"] = self.component_definition_id
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowNode":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            node_type=NodeType(data.get("node_type", "intermediate")),
            component_definition_id=data.get("component_definition_id"),
            metadata=data.get("metadata", {})
        )


class WorkflowEdge(BaseModel):
    """Represents a transition edge in the workflow graph"""
    from_node_id: str  # Source node ID
    to_node_id: str  # Target node ID
    condition: Optional[Predicate] = None  # Optional condition that must be satisfied
    priority: int = 0  # Priority for ordering multiple valid edges
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "priority": self.priority,
            "metadata": self.metadata
        }
        if self.condition:
            # Serialize predicate if present
            result["condition"] = self.condition.model_dump() if hasattr(self.condition, "model_dump") else self.condition
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowEdge":
        """Create from dictionary"""
        condition = None
        if "condition" in data and data["condition"]:
            # Deserialize predicate if present
            from TeapotEngine.ruleset.ExpressionModel import Predicate
            condition = Predicate(**data["condition"]) if isinstance(data["condition"], dict) else data["condition"]
        
        return cls(
            from_node_id=data["from_node_id"],
            to_node_id=data["to_node_id"],
            condition=condition,
            priority=data.get("priority", 0),
            metadata=data.get("metadata", {})
        )


class WorkflowGraph(BaseModel):
    """Container for workflow graph nodes and edges"""
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
    entry_node_id: Optional[str] = None  # ID of the entry node
    exit_node_ids: List[str] = Field(default_factory=list)  # IDs of exit nodes
    
    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """Get a node by ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_entry_node(self) -> Optional[WorkflowNode]:
        """Get the entry node"""
        if self.entry_node_id:
            return self.get_node(self.entry_node_id)
        # Fallback: find first entry-type node
        for node in self.nodes:
            if node.node_type == NodeType.START:
                return node
        return None
    
    def get_exit_nodes(self) -> List[WorkflowNode]:
        """Get all exit nodes"""
        exit_nodes = []
        for node_id in self.exit_node_ids:
            node = self.get_node(node_id)
            if node:
                exit_nodes.append(node)
        # Also check for exit-type nodes
        for node in self.nodes:
            if node.node_type == NodeType.END and node not in exit_nodes:
                exit_nodes.append(node)
        return exit_nodes
    
    def get_outgoing_edges(self, node_id: str) -> List[WorkflowEdge]:
        """Get all outgoing edges from a node"""
        return [edge for edge in self.edges if edge.from_node_id == node_id]
    
    def get_incoming_edges(self, node_id: str) -> List[WorkflowEdge]:
        """Get all incoming edges to a node"""
        return [edge for edge in self.edges if edge.to_node_id == node_id]
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate the workflow graph structure"""
        if not self.nodes:
            return False, "Workflow graph must have at least one node"
        
        # Check that entry node exists
        entry_node = self.get_entry_node()
        if not entry_node:
            return False, "Workflow graph must have an entry node"
        
        # Check that all edges reference valid nodes
        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.from_node_id not in node_ids:
                return False, f"Edge references invalid source node: {edge.from_node_id}"
            if edge.to_node_id not in node_ids:
                return False, f"Edge references invalid target node: {edge.to_node_id}"
        
        # Check that exit nodes exist
        for exit_id in self.exit_node_ids:
            if exit_id not in node_ids:
                return False, f"Exit node ID not found: {exit_id}"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "entry_node_id": self.entry_node_id,
            "exit_node_ids": self.exit_node_ids
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowGraph":
        """Create from dictionary"""
        nodes = [WorkflowNode.from_dict(n) for n in data.get("nodes", [])]
        edges = [WorkflowEdge.from_dict(e) for e in data.get("edges", [])]
        return cls(
            nodes=nodes,
            edges=edges,
            entry_node_id=data.get("entry_node_id"),
            exit_node_ids=data.get("exit_node_ids", [])
        )


@dataclass
class WorkflowState:
    """Tracks the current state of a workflow instance"""
    current_node_id: Optional[str] = None  # Current node in the workflow
    history: List[str] = field(default_factory=list)  # History of visited nodes
    metadata: Dict[str, Any] = field(default_factory=dict)  # Instance-specific metadata
    
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
        """Reset workflow state"""
        self.current_node_id = None
        self.history.clear()
        self.metadata.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "current_node_id": self.current_node_id,
            "history": self.history,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create from dictionary"""
        return cls(
            current_node_id=data.get("current_node_id"),
            history=data.get("history", []),
            metadata=data.get("metadata", {})
        )

