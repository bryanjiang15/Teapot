"""
Ruleset IR (Intermediate Representation) models
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from .models.ResourceModel import ResourceDefinition
from .rule_definitions.RuleDefinition import TriggerDefinition, ActionDefinition, RuleDefinition, PhaseDefinition, ZoneDefinition, KeywordDefinition, TurnStructure
from .ComponentDefinition import ComponentDefinition, ComponentType, ComponentRegistry
from .ComponentType import GameComponentDefinition


class RulesetIR(BaseModel):
    """Complete ruleset intermediate representation"""
    version: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Game component - separate from other components
    game_component: Optional[GameComponentDefinition] = None
    
    # Other components (player, card, zone, custom)
    component_definitions: List[ComponentDefinition] = Field(default_factory=list)
    
    # Legacy fields for backward compatibility
    turn_structure: TurnStructure
    rules: List[RuleDefinition] = Field(default_factory=list)
    actions: List[ActionDefinition] = Field(default_factory=list)
    keywords: List[KeywordDefinition] = Field(default_factory=list)
    constants: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        # Enable enum serialization
        use_enum_values=True
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper enum serialization"""
        # Get the base dictionary
        data = self.model_dump()
        
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
        from .ComponentType import (
            GameComponentDefinition,
            PlayerComponentDefinition, 
            CardComponentDefinition,
            ZoneComponentDefinition,
            TurnComponentDefinition,
            PhaseComponentDefinition,
            CustomComponentDefinition
        )
        
        component_type = comp_data.get('component_type', ComponentType.CUSTOM)
        
        # Map component types to their classes
        component_classes = {
            ComponentType.GAME: GameComponentDefinition,
            ComponentType.PLAYER: PlayerComponentDefinition,
            ComponentType.CARD: CardComponentDefinition,
            ComponentType.ZONE: ZoneComponentDefinition,
            ComponentType.TURN: TurnComponentDefinition,
            ComponentType.PHASE: PhaseComponentDefinition,
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
        #Get the turn structure from the component definitions

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
        registry = ComponentRegistry()
        
        # Register game component if it exists
        if self.game_component:
            registry.register(self.game_component)
        
        # Register other components
        for component in self.component_definitions:
            registry.register(component)
        
        # Get triggers from game component
        if self.game_component:
            all_triggers.extend(self.game_component.get_all_triggers(registry))
        
        # Get triggers from other component definitions
        for component in self.component_definitions:
            all_triggers.extend(component.get_all_triggers(registry))
        
        return all_triggers
    
    def get_all_zones(self) -> List[ZoneDefinition]:
        """Get all zones from all components"""
        all_zones = []
        
        # Get zones from game component
        if self.game_component and hasattr(self.game_component, 'global_zones'):
            all_zones.extend(self.game_component.global_zones)
        
        # Get zones from other component definitions
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
        
        for component in self.component_definitions:
            all_resources.extend(component.resources)
        
        return all_resources
    
    def get_component_by_id(self, component_id: int) -> Optional[ComponentDefinition]:
        """Get a component by ID from any component definition"""
        # Check game component first
        if self.game_component and self.game_component.id == component_id:
            return self.game_component
        
        # Check other component definitions
        for component in self.component_definitions:
            if component.id == component_id:
                return component
        
        return None
    
    def get_components_by_type(self, component_type: ComponentType) -> List[ComponentDefinition]:
        """Get all components of a specific type"""
        components = []
        
        # Check game component
        if self.game_component and getattr(self.game_component, 'component_type', ComponentType.CUSTOM) == component_type:
            components.append(self.game_component)
        
        # Check other component definitions
        components.extend([
            component for component in self.component_definitions
            if getattr(component, 'component_type', ComponentType.CUSTOM) == component_type
        ])
        
        return components
    
    def get_turn_components(self) -> List[ComponentDefinition]:
        """Get all turn component definitions"""
        return self.get_components_by_type(ComponentType.TURN)
    
    def get_phase_components(self) -> List[ComponentDefinition]:
        """Get all phase component definitions"""
        return self.get_components_by_type(ComponentType.PHASE)
