"""
Trigger definition models
"""

from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field
from TeapotEngine.ruleset.RulesetModels import PhaseExitType, ZoneVisibilityType, SelectableObjectType
from TeapotEngine.ruleset.ExpressionModel import Predicate, Selector
from enum import Enum

class TargetDefinition(BaseModel):
    """Definition of a target, can be groups/specific of cards, zones, phases, players, etc."""
    description: str
    type: SelectableObjectType
    selector: Optional[Selector] = None
    


class StepDefinition(BaseModel):
    """Definition of a game step"""
    id: int
    name: str
    mandatory: bool = False
    description: Optional[str] = None


class PhaseDefinition(BaseModel):
    """Definition of a game phase"""
    id: int
    name: str
    steps: List[StepDefinition]
    description: Optional[str] = None
    exit_type: PhaseExitType = PhaseExitType.EXIT_ON_NO_ACTIONS


class TurnStructure(BaseModel):
    """Turn structure definition"""
    phases: List[PhaseDefinition]
    priority_windows: List[Dict[str, Any]] = Field(default_factory=list)
    initial_phase_id: Optional[int] = None
    max_turns_per_player: Optional[int] = None # Maximum number of turns for each player. If both player go in same turn, it will equal the number of turns.

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
    actions: List["ActionDefinition"] = Field(default_factory=list)

    # For "if"
    condition: Optional[Predicate] = None
    then_actions: List["ActionDefinition"] = Field(default_factory=list)
    else_actions: List["ActionDefinition"] = Field(default_factory=list)

    # For "for_each"
    target_filter: Optional[Predicate] = None
    body_actions: List["ActionDefinition"] = Field(default_factory=list)

    # For "modify_state"
    state_op: Optional[str] = None  # e.g. "set_phase", "add_resource"
    state_args: Dict[str, Any] = Field(default_factory=dict)

class ActionTarget(BaseModel):
    """Definition of a target for an action"""
    id: str
    name: Optional[str] = None
    target_type: str = "card"  # "card", "zone", "player", etc.
    count: int = 1
    selector: Selector

class ActionDefinition(BaseModel):
    """Definition of a player action - This should define what a player can do in the game at a specific time"""
    id: int
    name: str
    description: Optional[str] = None
    timing: str = "stack"  # "stack", "instant"
    phase_ids: List[int] = Field(default_factory=list)  # Phases where this action can be executed
    zone_ids: List[int] = Field(default_factory=list)  # Zones where this action can be executed
    preconditions: List[Predicate] = Field(default_factory=list)
    costs: List[Dict[str, Any]] = Field(default_factory=list)
    targets: List[ActionTarget] = Field(default_factory=list)
    
    # What rules to execute when this action is taken
    execute_rules: List[int] = Field(default_factory=list)
    
    # UI/interaction fields
    ui: Optional[Dict[str, Any]] = None
    primary_target_type: Optional[SelectableObjectType] = None  # Type of the main target
    primary_target_selector: Optional[Selector] = None  # How to identify primary target
    interaction_mode: str = "click"  # "click", "drag", "multi_select", "button"
    
    # DEPRECATED: Keep for backward compatibility
    effects: List[Dict[str, Any]] = Field(default_factory=list)


class RuleDefinition(BaseModel):
    """A rule defines what mechanically happens when executed"""
    id: int
    name: str  # e.g., "DrawCard", "DealDamage", "MoveCard"
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    effects: List[Dict[str, Any]] = Field(default_factory=list)

class TriggerDefinition(BaseModel):
    """Definition of an event trigger"""
    id: int
    when: Dict[str, Any]
    conditions: List[Predicate] = Field(default_factory=list)
    execute_rules: List[int] = Field(default_factory=list)  # Rule IDs to execute
    parameters: List[Dict[str, Any]] = Field(default_factory=list) # Parameters for the rules to execute
    timing: str = "post"  # "pre", "post"
    caused_by: Optional[str] = None  # Represents the component that caused the trigger
    
    # NEW: Activation context - when should this trigger be listening?
    active_while: Optional[Predicate] = None
    # If None: Always listening (game/zone/player triggers)
    # If specified: Only register trigger when context matches

class ZoneDefinition(BaseModel):
    """Definition of a game zone"""
    id: int
    name: str
    zone_type: ZoneVisibilityType = ZoneVisibilityType.PRIVATE
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class KeywordDefinition(BaseModel):
    """Definition of a keyword ability"""
    id: int
    name: str
    description: str
    effects: List[Dict[str, Any]] = Field(default_factory=list)
    grants: List[Dict[str, Any]] = Field(default_factory=list)