"""
Ruleset IR (Intermediate Representation) models
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from ruleset.rulesetModels import ZoneVisibilityType
from ruleset.models import ResourceDefinition


class SelectableObjectType(Enum):
    CARD = "card"
    ZONE = "zone"
    PLAYER = "player"
    STACK_ABILITY = "stack_ability"

class TargetDefinition(BaseModel):
    """Definition of a target, can be groups/specific of cards, zones, phases, players, etc."""
    description: str
    type: SelectableObjectType
    selector: Optional[Dict[str, Any]] = None
    


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


class TurnStructure(BaseModel):
    """Turn structure definition"""
    phases: List[PhaseDefinition]
    priority_windows: List[Dict[str, Any]] = Field(default_factory=list)


class ActionDefinition(BaseModel):
    """Definition of a player action - This should define what a player can do in the game at a specific time"""
    id: int
    name: str
    description: Optional[str] = None
    timing: str = "stack"  # "stack", "instant"
    phase_ids: List[int] = Field(default_factory=list)  # Phases where this action can be executed
    zone_ids: List[int] = Field(default_factory=list)  # Zones where this action can be executed
    preconditions: List[Dict[str, Any]] = Field(default_factory=list)
    costs: List[Dict[str, Any]] = Field(default_factory=list)
    targets: List[Dict[str, Any]] = Field(default_factory=list)
    
    # What rules to execute when this action is taken
    execute_rules: List[int] = Field(default_factory=list)
    
    # UI/interaction fields
    ui: Optional[Dict[str, Any]] = None
    primary_target_type: Optional[SelectableObjectType] = None  # Type of the main target
    primary_target_selector: Optional[Dict[str, Any]] = None  # How to identify primary target
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
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    execute_rules: List[int] = Field(default_factory=list)  # Rule IDs to execute
    timing: str = "post"  # "pre", "post"
    triggerSource: Optional[TargetDefinition] = None
    caused_by: Optional[str] = None


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


class RulesetIR(BaseModel):
    """Complete ruleset intermediate representation"""
    version: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    turn_structure: TurnStructure
    rules: List[RuleDefinition] = Field(default_factory=list)
    actions: List[ActionDefinition] = Field(default_factory=list)
    triggers: List[TriggerDefinition] = Field(default_factory=list)
    zones: List[ZoneDefinition] = Field(default_factory=list)
    keywords: List[KeywordDefinition] = Field(default_factory=list)
    resources: List[ResourceDefinition] = Field(default_factory=list)
    constants: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RulesetIR":
        """Create from dictionary"""
        return cls(**data)
    
    def get_action(self, action_id: int) -> Optional[ActionDefinition]:
        """Get an action definition by ID"""
        for action in self.actions:
            if action.id == action_id:
                return action
        return None
    
    def get_phase(self, phase_id: int) -> Optional[PhaseDefinition]:
        """Get a phase definition by ID"""
        for phase in self.turn_structure.phases:
            if phase.id == phase_id:
                return phase
        return None
    
    def get_zone(self, zone_id: int) -> Optional[ZoneDefinition]:
        """Get a zone definition by ID"""
        for zone in self.zones:
            if zone.id == zone_id:
                return zone
        return None
    
    def get_keyword(self, keyword_id: int) -> Optional[KeywordDefinition]:
        """Get a keyword definition by ID"""
        for keyword in self.keywords:
            if keyword.id == keyword_id:
                return keyword
        return None
    
    def get_resource(self, resource_id: int) -> Optional[ResourceDefinition]:
        """Get a resource definition by ID"""
        for resource in self.resources:
            if resource.id == resource_id:
                return resource
        return None
    
    def get_rule(self, rule_id: int) -> Optional[RuleDefinition]:
        """Get a rule definition by ID"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
