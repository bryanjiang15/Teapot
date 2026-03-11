from typing import Literal, Optional, Dict, Any, List
from pydantic import BaseModel, Field
from TeapotEngine.ruleset.ExpressionModel import Predicate

class EffectDefinition(BaseModel):
    """A single step in a trigger's effect pipeline."""
    kind: Literal[
        "execute_rule",   # existing behavior
        "emit_event",     # push system/custom events onto stack
        "sequence",       # sequence of sub-actions
        "if",             # conditional
        "for_each",       # loop over filtered targets
        "modify_state",   # direct state changes, if you allow this
    ]

    # For "execute_rule"
    rule_id: Optional[int] = None
    rule_params: Dict[str, Any] = Field(default_factory=dict)

    # For "emit_event"
    event_type: Optional[str] = None
    event_payload: Dict[str, Any] = Field(default_factory=dict)

    # For "sequence"
    actions: List["EffectDefinition"] = Field(default_factory=list)

    # For "if"
    condition: Optional[Predicate] = None
    then_actions: List["EffectDefinition"] = Field(default_factory=list)
    else_actions: List["EffectDefinition"] = Field(default_factory=list)

    # For "for_each"
    target_filter: Optional[Predicate] = None
    body_actions: List["EffectDefinition"] = Field(default_factory=list)

    # For "modify_state"
    state_op: Optional[str] = None  # e.g. "set_phase", "add_resource"
    state_args: Dict[str, Any] = Field(default_factory=dict)