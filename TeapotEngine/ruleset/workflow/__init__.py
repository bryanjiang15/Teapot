"""
Workflow graph system for component-based state machines
"""

from .WorkflowGraph import (
    WorkflowNode,
    WorkflowGraph,
    WorkflowState,
    NodeType
)
from .WorkflowEdge import (
    WorkflowEdge,
    BaseWorkflowEdge,
    SimpleEdge,
    ConditionEdge,
    InputEdge
)

__all__ = [
    # Graph components
    "WorkflowNode",
    "WorkflowGraph",
    "WorkflowState",
    "NodeType",
    # Edge types
    "WorkflowEdge",
    "BaseWorkflowEdge",
    "SimpleEdge",
    "ConditionEdge",
    "InputEdge",
]
