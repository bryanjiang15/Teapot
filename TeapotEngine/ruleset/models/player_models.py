"""
Player-related models for TeapotEngine
"""

from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field

from .resource_models import Resource, ResourceDefinition


class Player(BaseModel):
    """Represents a game player"""
    id: str
    name: str
    resources: Dict[int, Resource] = Field(default_factory=dict)
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize resources if not provided
        if not self.resources:
            self.resources = {}
    
    def add_resource(self, resource_def: ResourceDefinition) -> None:
        """Add a resource to this player"""
        if resource_def.id not in self.resources:
            self.resources[resource_def.id] = Resource(
                resource_id=resource_def.id,
                current_amount=resource_def.starting_amount
            )
    
    def get_resource(self, resource_id: int) -> Optional[Resource]:
        """Get a player's resource by ID"""
        return self.resources.get(resource_id)
    
    def has_resource(self, resource_id: int, amount: Union[int, float] = 1) -> bool:
        """Check if player has enough of a resource"""
        resource = self.get_resource(resource_id)
        if not resource:
            return False
        return resource.current_amount >= amount
    
    def spend_resource(self, resource_id: int, amount: Union[int, float], resource_def: ResourceDefinition) -> bool:
        """Spend a resource amount"""
        resource = self.get_resource(resource_id)
        if not resource:
            return False
        return resource.spend(amount, resource_def)
    
    def gain_resource(self, resource_id: int, amount: Union[int, float], resource_def: ResourceDefinition) -> None:
        """Gain a resource amount"""
        resource = self.get_resource(resource_id)
        if not resource:
            # Create resource if it doesn't exist
            self.add_resource(resource_def)
            resource = self.get_resource(resource_id)
        
        if resource:
            resource.gain(amount, resource_def)
    
    def reset_turn_resources(self) -> None:
        """Reset per-turn resource tracking"""
        for resource in self.resources.values():
            resource.reset_turn_tracking()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "resources": {
                str(rid): {
                    "current_amount": res.current_amount,
                    "spent_this_turn": res.spent_this_turn,
                    "gained_this_turn": res.gained_this_turn
                }
                for rid, res in self.resources.items()
            },
            "properties": self.properties
        }
