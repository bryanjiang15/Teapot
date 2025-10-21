"""
Ruleset IR (Intermediate Representation) models
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from ruleset.rulesetModels import ZoneVisibilityType
from ruleset.models import ResourceDefinition
from .trigger_definition import TriggerDefinition
from .components import ComponentDefinition, ComponentType
from .component_types import GameComponentDefinition, PlayerComponentDefinition, CardComponentDefinition, ZoneComponentDefinition, CustomComponentDefinition


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
    initial_phase_id: Optional[int] = None


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


# TriggerDefinition moved to trigger_definition.py to avoid circular imports


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
    
    # Component-based structure - all components unified in component_definitions
    component_definitions: List[ComponentDefinition] = Field(default_factory=list)
    
    # Legacy fields for backward compatibility
    turn_structure: TurnStructure
    rules: List[RuleDefinition] = Field(default_factory=list)
    actions: List[ActionDefinition] = Field(default_factory=list)
    keywords: List[KeywordDefinition] = Field(default_factory=list)
    constants: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }
        # Enable enum serialization
        use_enum_values = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper enum serialization"""
        # Get the base dictionary
        data = self.dict()
        
        # Handle component_definitions specially to preserve specific fields
        if 'component_definitions' in data and self.component_definitions:
            serialized_components = []
            for comp in self.component_definitions:  # Use the actual objects, not the serialized data
                if hasattr(comp, 'to_dict'):
                    serialized_components.append(comp.to_dict())
                else:
                    # Fallback for already serialized components
                    serialized_components.append(comp)
            data['component_definitions'] = serialized_components
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RulesetIR":
        """Create from dictionary with polymorphic component deserialization"""
        # Handle component_definitions polymorphically
        if 'component_definitions' in data:
            component_definitions = []
            for comp_data in data['component_definitions']:
                # Deserialize based on component_type
                component = cls._deserialize_component(comp_data)
                component_definitions.append(component)
            data['component_definitions'] = component_definitions
        
        return cls(**data)
    
    @classmethod
    def _deserialize_component(cls, comp_data: Dict[str, Any]) -> ComponentDefinition:
        """Deserialize a component based on its type"""
        from .component_types import (
            GameComponentDefinition,
            PlayerComponentDefinition, 
            CardComponentDefinition,
            ZoneComponentDefinition,
            CustomComponentDefinition
        )
        
        component_type = comp_data.get('component_type', ComponentType.CUSTOM)
        
        # Map component types to their classes
        component_classes = {
            ComponentType.GAME: GameComponentDefinition,
            ComponentType.PLAYER: PlayerComponentDefinition,
            ComponentType.CARD: CardComponentDefinition,
            ComponentType.ZONE: ZoneComponentDefinition,
            ComponentType.CUSTOM: CustomComponentDefinition
        }
        
        # Handle both enum and string values
        if isinstance(component_type, str):
            try:
                component_type = ComponentType(component_type)
            except ValueError:
                component_type = ComponentType.CUSTOM
        
        component_class = component_classes.get(component_type, CustomComponentDefinition)
        
        # Create the appropriate component type
        return component_class(**comp_data)
    
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
    
    def get_all_triggers(self) -> List[TriggerDefinition]:
        """Get all triggers from all components"""
        all_triggers = []
        
        # Create a component registry for resolving references
        from .components import ComponentRegistry
        registry = ComponentRegistry()
        for component in self.component_definitions:
            registry.register(component)
        
        # Get triggers from all component definitions
        for component in self.component_definitions:
            all_triggers.extend(component.get_all_triggers(registry))
        
        return all_triggers
    
    def get_all_zones(self) -> List[ZoneDefinition]:
        """Get all zones from all components"""
        all_zones = []
        
        # Get zones from all component definitions
        for component in self.component_definitions:
            if hasattr(component, 'global_zones'):
                all_zones.extend(component.global_zones)
            elif hasattr(component, 'player_zones'):
                all_zones.extend(component.player_zones)
            elif hasattr(component, 'zones'):
                all_zones.extend(component.zones)
        
        return all_zones
    
    def get_all_resources(self) -> List[ResourceDefinition]:
        """Get all resources from all components"""
        all_resources = []
        
        # Create a component registry for resolving references
        from .components import ComponentRegistry
        registry = ComponentRegistry()
        for component in self.component_definitions:
            registry.register(component)
        
        # Get resources from all component definitions
        for component in self.component_definitions:
            if hasattr(component, 'global_resources'):
                all_resources.extend(component.global_resources)
            elif hasattr(component, 'player_resources'):
                all_resources.extend(component.player_resources)
            else:
                all_resources.extend(component.get_all_resources(registry))
        
        return all_resources
    
    def get_component_by_id(self, component_id: int) -> Optional[ComponentDefinition]:
        """Get a component by ID from any component definition"""
        # Check all component definitions
        for component in self.component_definitions:
            if component.id == component_id:
                return component
        
        return None
    
    def get_components_by_type(self, component_type: ComponentType) -> List[ComponentDefinition]:
        """Get all components of a specific type"""
        return [
            component for component in self.component_definitions
            if getattr(component, 'component_type', ComponentType.CUSTOM) == component_type
        ]
