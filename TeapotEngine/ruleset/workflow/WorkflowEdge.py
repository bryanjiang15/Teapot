"""
Workflow edge types for state machine transitions
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Literal, Optional, Annotated, Union
from TeapotEngine.ruleset.ExpressionModel import Predicate


class BaseWorkflowEdge(BaseModel):
    """Base class for all workflow edges"""
    from_node_id: str  # Source node ID
    to_node_id: str  # Target node ID
    priority: int = 0  # Priority for ordering multiple valid edges
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SimpleEdge(BaseWorkflowEdge):
    """Edge that is always taken (auto-advance)
    
    Use this for unconditional transitions between workflow nodes.
    """
    edge_type: Literal["simple"] = "simple"


class ConditionEdge(BaseWorkflowEdge):
    """Edge taken when condition evaluates to true
    
    The condition is a Predicate that is evaluated against the current game state.
    If the condition evaluates to true, this edge is valid for transition.
    """
    edge_type: Literal["condition"] = "condition"
    condition: Predicate  # Required


class InputEdge(BaseWorkflowEdge):
    """Edge taken when a specific input is activated by a player
    
    This edge is NOT auto-evaluated. Instead, when a player activates
    the specified input, this edge becomes the transition path.
    """
    edge_type: Literal["input"] = "input"
    trigger_input_id: int  # Required - the input definition ID that triggers this edge
    condition: Optional[Predicate] = None  # Optional additional condition


# Discriminated Union - Pydantic uses edge_type to pick the correct class
WorkflowEdge = Annotated[
    Union[SimpleEdge, ConditionEdge, InputEdge],
    Field(discriminator="edge_type")
]
