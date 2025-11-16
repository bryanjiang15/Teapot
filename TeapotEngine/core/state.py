"""
Game state management with event sourcing
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

from TeapotEngine.ruleset.models.resource_models import ResourceScope, ResourceDefinition
from TeapotEngine.ruleset.componentDefinition import ComponentDefinition, ComponentType
from TeapotEngine.ruleset.ir import RulesetIR
from TeapotEngine.ruleset.system_data.system_events import *
from .component import Component
from .events import Event
from .component import ComponentManager
from .phase_manager import PhaseManager, TurnType


@dataclass
class GameState:
    """Current state of the game derived from events"""
    match_id: str
    active_player: str
    phase_manager: Optional[PhaseManager] = None
    # Resource definition registry (by definition id)
    resource_definitions: Dict[int, ResourceDefinition] = field(default_factory=dict)
    
    # Player states - now using Player objects
    players: Dict[int, 'Component'] = field(default_factory=dict)
    
    # Zones and cards
    zones: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Game flags and status
    flags: Dict[str, Any] = field(default_factory=dict)
    
    # Event log for replay
    event_log: List[Event] = field(default_factory=list)
    
    # Component manager for component instances
    component_manager: ComponentManager = field(default_factory=ComponentManager)
    
    # Trigger metadata for future priority calculations
    trigger_metadata: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Global allocator for resource instance IDs
    _next_resource_instance_id: int = 1
    # Example: {"card_123": {"entered_play_turn": 5, "controller": "player1"}}
    
    def __post_init__(self):
        """Initialize default zones and player states"""
        if not self.zones:
            # Initialize default zones
            self.zones = {
                "hand": {2: [], 3: []},
                "battlefield": [],
                "graveyard": {2: [], 3: []},
                "exile": [],
                "deck": {2: [], 3: []}
            }

    def allocate_resource_instance_id(self) -> int:
        """Allocate a unique, incrementing resource instance id."""
        rid = self._next_resource_instance_id
        self._next_resource_instance_id += 1
        return rid
    
    @classmethod
    def from_ruleset(cls, match_id: str, ruleset: RulesetIR, player_ids: List[str] = None) -> 'GameState':
        """Create a GameState initialized with a ruleset
        
        Args:
            match_id: Unique identifier for the match
            ruleset: RulesetIR object containing game rules and structure
            player_ids: List of player IDs, defaults to ["player1", "player2"]
            
        Returns:
            Initialized GameState with phase manager and resource manager
        """
        if player_ids is None:
            player_ids = ["player1", "player2"]
        
        # Create GameState instance
        state = cls(match_id=match_id, active_player=player_ids[0])
        
        # Load resource definitions into state registry
        state.resource_definitions = {rd.id: rd for rd in ruleset.get_all_resources()}
        
        # Initialize phase manager
        turn_type_str = getattr(ruleset.turn_structure, 'turn_type', 'single_player')
        turn_type = TurnType.SINGLE_PLAYER if turn_type_str == "single_player" else TurnType.SYNCHRONOUS
        
        phase_manager = PhaseManager(
            turn_structure=ruleset.turn_structure,
            turn_type=turn_type,
            player_ids=player_ids
        )
        state.phase_manager = phase_manager
        
        # Sync active_player with phase manager
        if phase_manager.active_player:
            state.active_player = phase_manager.active_player
        
        return state
    
    def get_player(self, player_id: str, caused_by: Optional[Dict[str, str]] = None) -> Optional[Component]:
        """Get a player by ID"""
        if player_id == "self" and caused_by:
            return self.component_manager.get_component_by_type_and_id(ComponentType.PLAYER, int(caused_by.get("object_id"))) 
        return self.component_manager.get_component_by_type_and_id(ComponentType.PLAYER, player_id)
    
    
    def create_component(self, definition: ComponentDefinition, zone_component_id: Optional[int] = None, 
                        controller_component_id: Optional[int] = None,
                        properties: Optional[Dict[str, Any]] = None):
        """Create a new component instance from a definition and initialize its resources."""
        component = self.component_manager.create_component(definition, zone_component_id, controller_component_id, properties)
        # Initialize resources defined on this component definition
        for res_def in getattr(definition, 'resources', []) or []:
            # Attach GLOBAL resources to the Game component instance; others attach to this component
            if getattr(res_def, 'scope', None) == ResourceScope.GLOBAL:
                target_component = component if component.component_type == ComponentType.GAME else self.get_game_component_instance()
                if target_component:
                    instance_id = self.allocate_resource_instance_id()
                    target_component.add_resource_instance(instance_id, res_def)
            else:
                instance_id = self.allocate_resource_instance_id()
                component.add_resource_instance(instance_id, res_def)
        return component
    
    def get_component(self, component_id: int):
        """Get a component instance by ID"""
        return self.component_manager.get_component(component_id)
    
    def remove_component(self, component_id: int) -> bool:
        """Remove a component instance"""
        return self.component_manager.remove_component(component_id)
    
    def get_components_by_type(self, component_type):
        """Get all component instances of a specific type"""
        return self.component_manager.get_components_by_type(component_type)

    def get_game_component_instance(self) -> Optional[Component]:
        """Get the single Game component instance, if any."""
        comps = self.component_manager.get_components_by_type(ComponentType.GAME)
        return comps[0] if comps else None
    
    def get_components_by_zone(self, zone_component_id: int):
        """Get all component instances in a specific zone component"""
        return self.component_manager.get_components_by_zone(zone_component_id)
    
    def find_zone_component_by_name(self, zone_name: str) -> Optional[List[Component]]:
        """Find a zone component by its name"""
        zone_components = self.component_manager.get_components_by_type(ComponentType.ZONE)
        return [zone_component for zone_component in zone_components if zone_component.name == zone_name]
    
    def get_components_by_controller(self, controller_component_id: int):
        """Get all component instances controlled by a specific controller component"""
        return self.component_manager.get_components_by_controller(controller_component_id)
    
    def move_component(self, component_id: int, new_zone_component_id: Optional[int] = None, new_controller_component_id: Optional[int] = None) -> bool:
        """Move a component to a new zone and/or controller"""
        return self.component_manager.move_component(component_id, new_zone_component_id, new_controller_component_id)
    
    def get_all_components(self):
        """Get all component instances"""
        return self.component_manager.get_all_components()
    
    @property
    def current_phase(self) -> int:
        """Get current phase ID from phase manager"""
        return self.phase_manager.current_phase_id if self.phase_manager else 0
    
    @property
    def turn_number(self) -> int:
        """Get current turn number from phase manager"""
        return self.phase_manager.turn_number if self.phase_manager else 1
    
    @property
    def current_step(self) -> int:
        """Get current step ID from phase manager"""
        return self.phase_manager.current_step_id if self.phase_manager else 0
        
    
    def apply_event(self, event: Event) -> None:
        """Apply an event to the game state"""
        self.event_log.append(event)
        
        # Delegate phase/turn events to phase manager
        if self.phase_manager:
            if event.type == PHASE_STARTED:
                phase_id = event.payload.get("phase_id")
                if phase_id:
                    self.phase_manager.current_phase_id = phase_id
                    self.phase_manager.current_step_id = 0  # Reset to first step
            
            elif event.type == PHASE_ENDED:
                # Phase exit doesn't change current phase, but could trigger cleanup
                pass
            
            elif event.type == TURN_ENDED:
                # Turn ended - phase manager should already be updated
                # Sync active_player with phase manager
                if self.phase_manager.active_player:
                    self.active_player = self.phase_manager.active_player
        
        # Handle other event types
        if event.type == "CardMoved":
            self._move_card(
                event.payload["card_id"],
                event.payload["from_zone"],
                event.payload["to_zone"],
                event.payload.get("player_id")
            )
        
        elif event.type == "ResourceChanged":
            player_id = event.payload["player_id"]
            resource = event.payload["resource"]
            amount = event.payload["amount"]
            self._change_resource(player_id, resource, amount)
        
        elif event.type == "DamageDealt":
            self._deal_damage(
                event.payload["target"],
                event.payload["amount"],
                event.payload.get("source")
            )
    
    def _move_card(self, card_id: str, from_zone: str, to_zone: str, player_id: Optional[str] = None) -> None:
        """Move a card between zones"""
        # Remove from source zone
        if from_zone in self.zones:
            if player_id and from_zone in ["hand", "graveyard", "deck"]:
                if card_id in self.zones[from_zone][player_id]:
                    self.zones[from_zone][player_id].remove(card_id)
            else:
                if card_id in self.zones[from_zone]:
                    self.zones[from_zone].remove(card_id)
        
        # Add to destination zone
        if to_zone in self.zones:
            if player_id and to_zone in ["hand", "graveyard", "deck"]:
                self.zones[to_zone][player_id].append(card_id)
            else:
                self.zones[to_zone].append(card_id)
    
    def _change_resource(self, player_id: str, resource_id: int, amount: int) -> None:
        """Backward-compatible resource change routed to component-local resource storage.
        Resolves the first matching resource instance on the target component by resource definition id.
        """
        target_component: Optional[Component] = None
        # In legacy events, player_id may be an id or the string "self" handled by get_player
        try:
            target_component = self.get_player(player_id, caused_by={})  # type: ignore
        except TypeError:
            # Fallback to older signature
            target_component = self.get_player(player_id)  # type: ignore
        if not target_component:
            return

        # Resolve the resource definition from global registry
        resource_def = self.resource_definitions.get(resource_id)
        if not resource_def:
            return

        instance_ids = target_component.get_resource_instances(resource_def.id)
        if not instance_ids:
            return
        instance_id = instance_ids[0]

        if amount > 0:
            target_component.gain_resource(instance_id, amount, resource_def)
        else:
            target_component.spend_resource(instance_id, abs(amount), resource_def)

    def find_resource_instance(self, component_id: int, resource_def_id: int) -> Optional[int]:
        """Find a resource instance id on a component by resource definition id."""
        comp = self.get_component(component_id)
        if not comp:
            return None
        instances = comp.get_resource_instances(resource_def_id)
        return instances[0] if instances else None

    def gain_resource_instance(self, instance_id: int, amount: int) -> None:
        """Gain resource by instance id after resolving owner component and definition."""
        # Resolve owner component and definition; operate directly
        owner = None
        resource_id = None
        for comp in self.get_all_components():
            res = comp.get_resource_by_instance(instance_id)
            if res:
                owner = comp
                resource_id = res.resource_id
                break
        if not owner or resource_id is None:
            return
        res_def = self.resource_definitions.get(resource_id)
        if not res_def:
            return
        owner.gain_resource(instance_id, amount, res_def)

    def spend_resource_instance(self, instance_id: int, amount: int) -> bool:
        """Spend resource by instance id after resolving owner component and definition."""
        # Resolve owner component and definition; operate directly
        owner = None
        resource_id = None
        for comp in self.get_all_components():
            res = comp.get_resource_by_instance(instance_id)
            if res:
                owner = comp
                resource_id = res.resource_id
                break
        if not owner or resource_id is None:
            return False
        res_def = self.resource_definitions.get(resource_id)
        if not res_def:
            return False
        return owner.spend_resource(instance_id, amount, res_def)
    
    def _deal_damage(self, target: str, amount: int, source: Optional[str] = None) -> None:
        """Deal damage to a target"""
        # This would need to be implemented based on specific game rules
        # For now, just track it in flags
        if "damage_dealt" not in self.flags:
            self.flags["damage_dealt"] = []
        
        self.flags["damage_dealt"].append({
            "target": target,
            "amount": amount,
            "source": source
        })
    
    def get_card_location(self, card_id: str) -> Optional[tuple]:
        """Get the current location of a card (zone, player_id)"""
        for zone_name, zone_data in self.zones.items():
            if isinstance(zone_data, dict):
                # Player-specific zones
                for player_id, cards in zone_data.items():
                    if card_id in cards:
                        return (zone_name, player_id)
            else:
                # Shared zones
                if card_id in zone_data:
                    return (zone_name, None)
        return None
    
    def get_player_zone(self, player_id: str, zone_name: str) -> List[str]:
        """Get cards in a player's zone"""
        if zone_name in self.zones and isinstance(self.zones[zone_name], dict):
            return self.zones[zone_name].get(player_id, [])
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "match_id": self.match_id,
            "active_player": self.active_player,
            "current_phase": self.phase_manager.get_current_phase_info().name,
            "current_step": self.current_step,
            "turn_number": self.turn_number,
            "players": {pid: player.model_dump() for pid, player in self.players.items()},
            "zones": self.zones,
            "flags": self.flags,
            "event_count": len(self.event_log)
        }
    
    @classmethod
    def from_events(cls, match_id: str, ruleset: RulesetIR, events: List[Event], player_ids: List[str] = None) -> "GameState":
        """Reconstruct state from event log"""
        state = cls.from_ruleset(match_id, ruleset, player_ids)
        
        for event in events:
            state.apply_event(event)
        
        return state
