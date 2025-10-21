"""
Base component definition classes for the component-based trigger system
"""

from typing import Dict, Any, List, Optional, Union, Type
from enum import Enum
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, create_model
from .trigger_definition import TriggerDefinition
from .models import ResourceDefinition


class ComponentType(Enum):
    """Enumeration of component types"""
    GAME = "game"
    PLAYER = "player"
    CARD = "card"
    ZONE = "zone"
    CUSTOM = "custom"


class ComponentDefinition(BaseModel, ABC):
    """Abstract base component definition that can contain triggers, sub-components, and resources"""
    
    id: int
    name: str
    description: Optional[str] = None
    
    # Component capabilities
    triggers: List[TriggerDefinition] = Field(default_factory=list)
    sub_component_ids: List[int] = Field(default_factory=list)  # References to other components
    resources: List[ResourceDefinition] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Component metadata
    component_type: ComponentType = ComponentType.CUSTOM
    parent_id: Optional[int] = None
    
    @abstractmethod
    def get_component_specific_data(self) -> Dict[str, Any]:
        """Get component-specific data that subclasses must implement"""
        pass
    
    @abstractmethod
    def validate_component(self) -> bool:
        """Validate component-specific rules that subclasses must implement"""
        pass
    
    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }
        # Enable polymorphic serialization
        use_enum_values = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper enum serialization"""
        data = self.dict()
        # Convert enum to string for JSON serialization
        if 'component_type' in data:
            if hasattr(data['component_type'], 'value'):
                data['component_type'] = data['component_type'].value
            elif isinstance(data['component_type'], ComponentType):
                data['component_type'] = data['component_type'].value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentDefinition':
        """Create from dictionary"""
        return cls(**data)
    
    def get_trigger(self, trigger_id: int) -> Optional[TriggerDefinition]:
        """Get a trigger definition by ID"""
        for trigger in self.triggers:
            if trigger.id == trigger_id:
                return trigger
        return None
    
    def get_resource(self, resource_id: int) -> Optional[ResourceDefinition]:
        """Get a resource definition by ID"""
        for resource in self.resources:
            if resource.id == resource_id:
                return resource
        return None
    
    def add_sub_component_reference(self, component_id: int) -> None:
        """Add a reference to a sub-component"""
        if component_id not in self.sub_component_ids:
            self.sub_component_ids.append(component_id)
    
    def remove_sub_component_reference(self, component_id: int) -> bool:
        """Remove a reference to a sub-component"""
        if component_id in self.sub_component_ids:
            self.sub_component_ids.remove(component_id)
            return True
        return False
    
    def get_all_triggers(self, component_registry: Optional['ComponentRegistry'] = None) -> List[TriggerDefinition]:
        """Get all triggers from this component and its sub-components recursively"""
        all_triggers = list(self.triggers)
        
        # If we have a registry, resolve sub-component references
        if component_registry:
            for sub_component_id in self.sub_component_ids:
                sub_component = component_registry.get(sub_component_id)
                if sub_component:
                    all_triggers.extend(sub_component.get_all_triggers(component_registry))
        
        return all_triggers
    
    def get_all_resources(self, component_registry: Optional['ComponentRegistry'] = None) -> List[ResourceDefinition]:
        """Get all resources from this component and its sub-components recursively"""
        all_resources = list(self.resources)
        
        # If we have a registry, resolve sub-component references
        if component_registry:
            for sub_component_id in self.sub_component_ids:
                sub_component = component_registry.get(sub_component_id)
                if sub_component:
                    all_resources.extend(sub_component.get_all_resources(component_registry))
        
        return all_resources


class ComponentRegistry:
    """Registry for managing component definitions"""
    
    def __init__(self):
        self._components: Dict[int, ComponentDefinition] = {}
        self._type_index: Dict[str, List[int]] = {}
    
    def register(self, component: ComponentDefinition) -> None:
        """Register a component definition"""
        self._components[component.id] = component
        
        # Index by type
        component_type_key = component.component_type.value
        if component_type_key not in self._type_index:
            self._type_index[component_type_key] = []
        self._type_index[component_type_key].append(component.id)
    
    def get(self, component_id: int) -> Optional[ComponentDefinition]:
        """Get a component by ID"""
        return self._components.get(component_id)
    
    def get_by_type(self, component_type: str) -> List[ComponentDefinition]:
        """Get all components of a specific type"""
        component_ids = self._type_index.get(component_type, [])
        return [self._components[cid] for cid in component_ids if cid in self._components]
    
    def unregister(self, component_id: int) -> bool:
        """Unregister a component"""
        if component_id in self._components:
            component = self._components[component_id]
            
            # Remove from type index
            component_type_key = component.component_type.value
            if component_type_key in self._type_index:
                if component_id in self._type_index[component_type_key]:
                    self._type_index[component_type_key].remove(component_id)
            
            del self._components[component_id]
            return True
        return False
    
    def list_all(self) -> List[ComponentDefinition]:
        """Get all registered components"""
        return list(self._components.values())
    
    def clear(self) -> None:
        """Clear all components"""
        self._components.clear()
        self._type_index.clear()
