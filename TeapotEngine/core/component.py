"""
Component system for game objects
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from TeapotEngine.ruleset.ruleDefinitions.rule_definitions import TriggerDefinition
from TeapotEngine.ruleset.componentDefinition import ComponentDefinition, ComponentType
from TeapotEngine.ruleset.models.resource_models import Resource, ResourceDefinition


class ComponentStatus(Enum):
    """Status of a component instance"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DESTROYED = "destroyed"


@dataclass
class Component:
    """Represents an actual component instance in the game"""
    id: int  # Unique instance ID
    definition_id: int  # ID of the ComponentDefinition this instance is based on
    name: str
    component_type: ComponentType
    
    # Instance-specific properties
    properties: Dict[str, Any] = field(default_factory=dict)
    status: ComponentStatus = ComponentStatus.ACTIVE
    
    # Location information
    zone_component_id: Optional[int] = None
    controller_component_id: Optional[int] = None
    
    # Triggers from the definition (copied at creation)
    triggers: List[TriggerDefinition] = field(default_factory=list)
    
    # Metadata for trigger activation
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Resource storage per component instance
    resources_by_instance_id: Dict[int, Resource] = field(default_factory=dict)
    resource_instance_ids_by_def_id: Dict[int, List[int]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize component after creation"""
        # Copy triggers from definition if not already set
        if not self.triggers:
            self.triggers = []
    
    def add_trigger(self, trigger: TriggerDefinition) -> None:
        """Add a trigger to this component instance"""
        self.triggers.append(trigger)

    # Resource APIs
    def add_resource_instance(self, instance_id: int, resource_def: ResourceDefinition, starting_amount: Optional[Union[int, float]] = None) -> int:
        """Attach a new resource instance to this component and index it by its definition id."""
        if instance_id in self.resources_by_instance_id:
            return instance_id
        resource = Resource(
            resource_id=resource_def.id,
            current_amount=resource_def.starting_amount if starting_amount is None else starting_amount
        )
        self.resources_by_instance_id[instance_id] = resource
        self.resource_instance_ids_by_def_id.setdefault(resource_def.id, []).append(instance_id)
        return instance_id

    def get_resource_instances(self, resource_def_id: int) -> List[int]:
        """Get all resource instance ids for a given resource definition id on this component."""
        return list(self.resource_instance_ids_by_def_id.get(resource_def_id, []))

    def get_resource_by_instance(self, instance_id: int) -> Optional[Resource]:
        """Get a resource instance by its instance id."""
        return self.resources_by_instance_id.get(instance_id)

    def gain_resource(self, instance_id: int, amount: Union[int, float], resource_def: ResourceDefinition) -> None:
        """Increase a resource instance's amount."""
        resource = self.get_resource_by_instance(instance_id)
        if not resource:
            return
        resource.gain(amount, resource_def)

    def spend_resource(self, instance_id: int, amount: Union[int, float], resource_def: ResourceDefinition) -> bool:
        """Attempt to spend from a resource instance."""
        resource = self.get_resource_by_instance(instance_id)
        if not resource:
            return False
        return resource.spend(amount, resource_def)
    
    def is_active(self) -> bool:
        """Check if component is active"""
        return self.status == ComponentStatus.ACTIVE
    
    def set_zone(self, zone_component_id: Optional[int]) -> None:
        """Set the zone component this component is in"""
        self.zone_component_id = zone_component_id
    
    def set_controller(self, controller_component_id: Optional[int]) -> None:
        """Set the controller component of this component"""
        self.controller_component_id = controller_component_id
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update component metadata"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get component metadata"""
        return self.metadata.get(key, default)


class ComponentManager:
    """Manages component instances in the game"""
    
    def __init__(self):
        self._components: Dict[int, Component] = {}
        self._next_component_id: int = 1
        self._components_by_type: Dict[ComponentType, List[int]] = {}
        self._components_by_zone: Dict[int, List[int]] = {}
        self._components_by_controller: Dict[int, List[int]] = {}
    
    def create_component(self, definition: ComponentDefinition, 
                        zone_component_id: Optional[int] = None, 
                        controller_component_id: Optional[int] = None,
                        properties: Optional[Dict[str, Any]] = None) -> Component:
        """Create a new component instance from a definition"""
        component_id = self._next_component_id
        self._next_component_id += 1
        
        # Create component instance
        component = Component(
            id=component_id,
            definition_id=definition.id,
            name=definition.name,
            component_type=definition.component_type,
            properties=properties or {},
            zone_component_id=zone_component_id,
            controller_component_id=controller_component_id,
            triggers=definition.triggers.copy()  # Copy triggers from definition
        )
        
        # Register component
        self._components[component_id] = component
        self._index_component(component)
        
        return component
    
    def get_component(self, component_id: int) -> Optional[Component]:
        """Get a component by ID"""
        return self._components.get(component_id)
    
    def remove_component(self, component_id: int) -> bool:
        """Remove a component instance"""
        if component_id not in self._components:
            return False
        
        component = self._components[component_id]
        
        # Remove from indices
        self._unindex_component(component)
        
        # Remove from main registry
        del self._components[component_id]
        
        return True
    
    def get_components_by_type(self, component_type: ComponentType) -> List[Component]:
        """Get all components of a specific type"""
        component_ids = self._components_by_type.get(component_type, [])
        return [self._components[cid] for cid in component_ids if cid in self._components]
    
    def get_component_by_type_and_id(self, component_type: ComponentType, id: int) -> Optional[Component]:
        """Get a component by type and ID"""
        component_ids = self._components_by_type.get(component_type, [])
        for cid in component_ids:
            if cid == id:
                return self._components[cid]
        return None
    
    def get_components_by_zone(self, zone_component_id: int) -> List[Component]:
        """Get all components in a specific zone component"""
        component_ids = self._components_by_zone.get(zone_component_id, [])
        return [self._components[cid] for cid in component_ids if cid in self._components]
    
    def get_components_by_controller(self, controller_component_id: int) -> List[Component]:
        """Get all components controlled by a specific controller component"""
        component_ids = self._components_by_controller.get(controller_component_id, [])
        return [self._components[cid] for cid in component_ids if cid in self._components]
    
    def move_component(self, component_id: int, new_zone_component_id: Optional[int] = None, new_controller_component_id: Optional[int] = None) -> bool:
        """Move a component to a new zone and/or controller"""
        component = self.get_component(component_id)
        if not component:
            return False
        
        # Update component
        old_zone_component_id = component.zone_component_id
        if new_zone_component_id is not None:
            component.set_zone(new_zone_component_id)
        if new_controller_component_id is not None:
            component.set_controller(new_controller_component_id)
        
        # Update indices
        if old_zone_component_id is not None:
            if old_zone_component_id in self._components_by_zone:
                self._components_by_zone[old_zone_component_id] = [
                    cid for cid in self._components_by_zone[old_zone_component_id] if cid != component_id
                ]
        
        if new_zone_component_id is not None:
            self._components_by_zone.setdefault(new_zone_component_id, []).append(component_id)
        
        # Update controller indices
        old_controller_component_id = component.controller_component_id
        if old_controller_component_id is not None and old_controller_component_id != new_controller_component_id:
            if old_controller_component_id in self._components_by_controller:
                self._components_by_controller[old_controller_component_id] = [
                    cid for cid in self._components_by_controller[old_controller_component_id] if cid != component_id
                ]
        
        if new_controller_component_id is not None:
            self._components_by_controller.setdefault(new_controller_component_id, []).append(component_id)
        
        return True
    
    def _index_component(self, component: Component) -> None:
        """Add component to all relevant indices"""
        # Index by type
        if component.component_type not in self._components_by_type:
            self._components_by_type[component.component_type] = []
        self._components_by_type[component.component_type].append(component.id)
        
        # Index by zone
        if component.zone_component_id is not None:
            if component.zone_component_id not in self._components_by_zone:
                self._components_by_zone[component.zone_component_id] = []
            self._components_by_zone[component.zone_component_id].append(component.id)
        
        # Index by controller
        if component.controller_component_id is not None:
            if component.controller_component_id not in self._components_by_controller:
                self._components_by_controller[component.controller_component_id] = []
            self._components_by_controller[component.controller_component_id].append(component.id)
    
    def _unindex_component(self, component: Component) -> None:
        """Remove component from all indices"""
        # Remove from type index
        if component.component_type in self._components_by_type:
            self._components_by_type[component.component_type] = [
                cid for cid in self._components_by_type[component.component_type] if cid != component.id
            ]
        
        # Remove from zone index
        if component.zone_component_id is not None and component.zone_component_id in self._components_by_zone:
            self._components_by_zone[component.zone_component_id] = [
                cid for cid in self._components_by_zone[component.zone_component_id] if cid != component.id
            ]
        
        # Remove from controller index
        if component.controller_component_id is not None and component.controller_component_id in self._components_by_controller:
            self._components_by_controller[component.controller_component_id] = [
                cid for cid in self._components_by_controller[component.controller_component_id] if cid != component.id
            ]
    
    def get_all_components(self) -> List[Component]:
        """Get all component instances"""
        return list(self._components.values())
    
    def get_component_count(self) -> int:
        """Get total number of component instances"""
        return len(self._components)
