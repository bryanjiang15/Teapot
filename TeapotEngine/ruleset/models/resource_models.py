"""
Resource-related models for TeapotEngine
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class ResourceScope(Enum):
    """Defines the scope of a resource"""
    GLOBAL = "global"  # One resource per game
    PLAYER = "player"  # One resource per player
    OBJECT = "object"  # One resource per object (card, etc.)


class ResourceType(Enum):
    """Defines the type of resource behavior"""
    CONSUMABLE = "consumable"  # Can be spent and regenerated
    TRACKED = "tracked"  # Tracks a value (like life total)
    ACCUMULATING = "accumulating"  # Only increases (like experience)
    BINARY = "binary"  # On/off state


class ResourceDefinition(BaseModel):
    """Definition of a game resource"""
    id: int
    name: str
    description: str
    scope: ResourceScope = ResourceScope.PLAYER
    resource_type: ResourceType = ResourceType.CONSUMABLE
    
    # Starting values
    starting_amount: Union[int, float] = 0
    max_amount: Optional[Union[int, float]] = None
    min_amount: Union[int, float] = 0
    
    # Per-turn limits (for consumable resources)
    max_per_turn: Optional[Union[int, float]] = None
    regeneration_per_turn: Union[int, float] = 0
    
    # Properties
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    def get_effective_max(self, current_turn: int = 1) -> Optional[Union[int, float]]:
        """Get the effective maximum for this turn"""
        if self.max_per_turn is not None:
            return min(self.max_per_turn * current_turn, self.max_amount or float('inf'))
        return self.max_amount


@dataclass
class Resource:
    """Represents a resource instance stored on any component"""
    resource_id: int
    current_amount: Union[int, float] = 0
    spent_this_turn: Union[int, float] = 0
    gained_this_turn: Union[int, float] = 0
    
    def can_spend(self, amount: Union[int, float], resource_def: ResourceDefinition) -> bool:
        """Check if player can spend this amount"""
        if self.current_amount < amount:
            return False
        
        # Check per-turn limits
        if resource_def.max_per_turn is not None:
            if self.spent_this_turn + amount > resource_def.max_per_turn:
                return False
        
        return True
    
    def spend(self, amount: Union[int, float], resource_def: ResourceDefinition) -> bool:
        """Spend resource amount"""
        if not self.can_spend(amount, resource_def):
            return False
        
        self.current_amount -= amount
        self.spent_this_turn += amount
        return True
    
    def gain(self, amount: Union[int, float], resource_def: ResourceDefinition) -> None:
        """Gain resource amount"""
        self.current_amount += amount
        self.gained_this_turn += amount
        
        # Enforce maximum limits
        if resource_def.max_amount is not None:
            self.current_amount = min(self.current_amount, resource_def.max_amount)
        
        # Enforce minimum limits
        self.current_amount = max(self.current_amount, resource_def.min_amount)
    
    def reset_turn_tracking(self) -> None:
        """Reset per-turn tracking"""
        self.spent_this_turn = 0
        self.gained_this_turn = 0


# Deprecated manager removed; resource definitions are owned by GameState
