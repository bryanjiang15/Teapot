"""
Ruleset IR (Intermediate Representation) models
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from ruleset.rulesetModels import ZoneVisibilityType


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
    """Definition of a player action"""
    id: int
    name: str
    description: Optional[str] = None
    timing: str = "stack"  # "stack", "instant"
    phase_ids: List[int] = Field(default_factory=list)  # Phases where this action can be executed
    zone_ids: List[int] = Field(default_factory=list)  # Zones where this action can be executed
    preconditions: List[Dict[str, Any]] = Field(default_factory=list)
    costs: List[Dict[str, Any]] = Field(default_factory=list)
    targets: List[Dict[str, Any]] = Field(default_factory=list)
    effects: List[Dict[str, Any]] = Field(default_factory=list)
    ui: Optional[Dict[str, Any]] = None


class TriggerDefinition(BaseModel):
    """Definition of an event trigger"""
    id: int
    when: Dict[str, Any]
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    effects: List[Dict[str, Any]] = Field(default_factory=list)
    timing: str = "post"  # "pre", "post"
    source_id: Optional[int] = None


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
    actions: List[ActionDefinition] = Field(default_factory=list)
    triggers: List[TriggerDefinition] = Field(default_factory=list)
    zones: List[ZoneDefinition] = Field(default_factory=list)
    keywords: List[KeywordDefinition] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)
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
