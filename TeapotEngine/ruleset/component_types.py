

"""
Specific component types for the component-based trigger system
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .componentDefinition import ComponentDefinition, ComponentType

class GameComponentDefinition(ComponentDefinition):
    """Game-level component that defines the base game rules and structure"""
    
    component_type: ComponentType = ComponentType.GAME
    
    # Game-specific properties
    phases: List[Dict[str, Any]] = Field(default_factory=list)
    global_zones: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Game rules
    max_players: int = 2
    win_conditions: List[Dict[str, Any]] = Field(default_factory=list)
    
    def __init__(self, **data):
        super().__init__(**data)
        self.component_type = ComponentType.GAME
    
    def get_phase(self, phase_id: int) -> Optional[Dict[str, Any]]:
        """Get a phase definition by ID"""
        for phase in self.phases:
            if phase.get("id") == phase_id:
                return phase
        return None
    
    def get_global_zone(self, zone_id: int) -> Optional[Dict[str, Any]]:
        """Get a global zone definition by ID"""
        for zone in self.global_zones:
            if zone.get("id") == zone_id:
                return zone
        return None
    
    def get_component_specific_data(self) -> Dict[str, Any]:
        """Get game-specific data"""
        return {
            "phases": self.phases,
            "global_zones": self.global_zones,
            "max_players": self.max_players,
            "win_conditions": self.win_conditions,
        }
    
    def validate_component(self) -> bool:
        """Validate game component rules"""
        # Check that max_players is positive
        if self.max_players <= 0:
            return False
        
        # Check that we have at least one phase
        if not self.phases:
            return False
        
        # Check that win conditions are valid
        for condition in self.win_conditions:
            if not isinstance(condition, dict) or "type" not in condition:
                return False
        
        return True


class PlayerComponentDefinition(ComponentDefinition):
    """Player component template that defines player-specific behavior"""
    
    component_type: ComponentType = ComponentType.PLAYER
    
    # Player-specific properties
    starting_hand_size: int = 7
    max_hand_size: int = 7
    starting_life: int = 20
    
    # Player zones
    player_zones: List[Dict[str, Any]] = Field(default_factory=list)
    
    def __init__(self, **data):
        super().__init__(**data)
        self.component_type = ComponentType.PLAYER
    
    def get_player_zone(self, zone_id: int) -> Optional[Dict[str, Any]]:
        """Get a player zone definition by ID"""
        for zone in self.player_zones:
            if zone.get("id") == zone_id:
                return zone
        return None
    
    def get_component_specific_data(self) -> Dict[str, Any]:
        """Get player-specific data"""
        return {
            "starting_hand_size": self.starting_hand_size,
            "max_hand_size": self.max_hand_size,
            "starting_life": self.starting_life,
            "player_zones": self.player_zones
        }
    
    def validate_component(self) -> bool:
        """Validate player component rules"""
        # Check that hand sizes are positive
        if self.starting_hand_size < 0 or self.max_hand_size < 0:
            return False
        
        # Check that starting life is positive
        if self.starting_life <= 0:
            return False
        
        # Check that max hand size is at least as large as starting hand size
        if self.max_hand_size < self.starting_hand_size:
            return False
        
        return True


class CardComponentDefinition(ComponentDefinition):
    """Card component template that defines base card behavior"""
    
    component_type: ComponentType = ComponentType.CARD
    
    # Card-specific properties
    cost: int = 0
    stats: Dict[str, Any] = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)
    text: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        self.component_type = ComponentType.CARD
    
    def has_keyword(self, keyword: str) -> bool:
        """Check if card has a specific keyword"""
        return keyword in self.keywords
    
    def add_keyword(self, keyword: str) -> None:
        """Add a keyword to the card"""
        if keyword not in self.keywords:
            self.keywords.append(keyword)
    
    def remove_keyword(self, keyword: str) -> bool:
        """Remove a keyword from the card"""
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            return True
        return False
    
    def get_component_specific_data(self) -> Dict[str, Any]:
        """Get card-specific data"""
        return {
            "cost": self.cost,
            "stats": self.stats,
            "keywords": self.keywords,
            "text": self.text
        }
    
    def validate_component(self) -> bool:
        """Validate card component rules"""
        # Check that cost is non-negative
        if self.cost < 0:
            return False
        
        # Check that stats are valid (if any)
        for stat_name, stat_value in self.stats.items():
            if not isinstance(stat_value, (int, float)):
                return False
        
        return True


class ZoneComponentDefinition(ComponentDefinition):
    """Zone component that defines zone-specific behavior"""
    
    component_type: ComponentType = ComponentType.ZONE
    
    # Zone-specific properties
    visibility: str = "private"  # "private", "public", "shared"
    ordering: str = "stack"  # "stack", "queue", "unordered"
    max_size: Optional[int] = None
    zone_type: str = "default"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.component_type = ComponentType.ZONE
    
    def is_private(self) -> bool:
        """Check if zone is private"""
        return self.visibility == "private"
    
    def is_public(self) -> bool:
        """Check if zone is public"""
        return self.visibility == "public"
    
    def is_shared(self) -> bool:
        """Check if zone is shared"""
        return self.visibility == "shared"
    
    def get_component_specific_data(self) -> Dict[str, Any]:
        """Get zone-specific data"""
        return {
            "visibility": self.visibility,
            "ordering": self.ordering,
            "max_size": self.max_size,
            "zone_type": self.zone_type
        }
    
    def validate_component(self) -> bool:
        """Validate zone component rules"""
        # Check that visibility is valid
        valid_visibility = ["private", "public", "shared"]
        if self.visibility not in valid_visibility:
            return False
        
        # Check that ordering is valid
        valid_ordering = ["stack", "queue", "unordered"]
        if self.ordering not in valid_ordering:
            return False
        
        # Check that max_size is positive if set
        if self.max_size is not None and self.max_size <= 0:
            return False
        
        return True


class CustomComponentDefinition(ComponentDefinition):
    """Custom component for game-specific components"""
    
    component_type: ComponentType = ComponentType.CUSTOM
    
    # Custom component can have any additional properties
    custom_properties: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        self.component_type = ComponentType.CUSTOM
    
    def set_custom_property(self, key: str, value: Any) -> None:
        """Set a custom property"""
        self.custom_properties[key] = value
    
    def get_custom_property(self, key: str, default: Any = None) -> Any:
        """Get a custom property"""
        return self.custom_properties.get(key, default)
    
    def get_component_specific_data(self) -> Dict[str, Any]:
        """Get custom component data"""
        return {
            "custom_properties": self.custom_properties
        }
    
    def validate_component(self) -> bool:
        """Validate custom component rules"""
        # Custom components are always valid by default
        # Subclasses can override this for specific validation
        return True
