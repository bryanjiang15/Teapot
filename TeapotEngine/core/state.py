"""
Game state management with event sourcing
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set

from ruleset.models.player_models import Player
from ruleset.models.resource_models import GameResourceManager
from ruleset.components import ComponentDefinition
from ruleset.component_types import GameComponentDefinition, PlayerComponentDefinition, CardComponentDefinition, ZoneComponentDefinition
from .events import Event, PHASE_ENTERED, PHASE_EXITED


@dataclass
class GameState:
    """Current state of the game derived from events"""
    match_id: str
    active_player: str
    current_phase: int = 0
    current_step: int = 0
    turn_number: int = 1
    
    # Player states - now using Player objects
    players: Dict[str, 'Player'] = field(default_factory=dict)
    
    # Resource manager for this match
    resource_manager: Optional['GameResourceManager'] = None
    
    # Zones and cards
    zones: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Game flags and status
    flags: Dict[str, Any] = field(default_factory=dict)
    
    # Event log for replay
    event_log: List[Event] = field(default_factory=list)
    
    # Component definitions
    game_component: Optional[GameComponentDefinition] = None
    player_components: Dict[int, PlayerComponentDefinition] = field(default_factory=dict)
    card_components: Dict[int, CardComponentDefinition] = field(default_factory=dict)
    zone_components: Dict[int, ZoneComponentDefinition] = field(default_factory=dict)
    custom_components: Dict[int, ComponentDefinition] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default zones and player states"""
        if not self.zones:
            # Initialize default zones
            self.zones = {
                "hand": {"player1": [], "player2": []},
                "battlefield": [],
                "graveyard": {"player1": [], "player2": []},
                "exile": [],
                "deck": {"player1": [], "player2": []}
            }
    
    def add_player(self, player: 'Player') -> None:
        """Add a player to the game state"""
        self.players[player.id] = player
    
    def get_player(self, player_id: str, caused_by: Dict[str, str]) -> Optional['Player']:
        """Get a player by ID"""
        if player_id == "self":
            return self.players.get(caused_by.get("object_id"))
        return self.players.get(player_id)
    
    def set_resource_manager(self, resource_manager: 'GameResourceManager') -> None:
        """Set the resource manager for this match"""
        self.resource_manager = resource_manager
    
    def set_game_component(self, game_component: GameComponentDefinition) -> None:
        """Set the game component definition"""
        self.game_component = game_component
    
    def add_player_component(self, player_id: int, player_component: PlayerComponentDefinition) -> None:
        """Add a player component definition"""
        self.player_components[player_id] = player_component
    
    def get_player_component(self, player_id: int) -> Optional[PlayerComponentDefinition]:
        """Get a player component definition"""
        return self.player_components.get(player_id)
    
    def add_card_component(self, card_id: int, card_component: CardComponentDefinition) -> None:
        """Add a card component definition"""
        self.card_components[card_id] = card_component
    
    def get_card_component(self, card_id: int) -> Optional[CardComponentDefinition]:
        """Get a card component definition"""
        return self.card_components.get(card_id)
    
    def add_zone_component(self, zone_id: int, zone_component: ZoneComponentDefinition) -> None:
        """Add a zone component definition"""
        self.zone_components[zone_id] = zone_component
    
    def get_zone_component(self, zone_id: int) -> Optional[ZoneComponentDefinition]:
        """Get a zone component definition"""
        return self.zone_components.get(zone_id)
    
    def add_custom_component(self, component_id: int, component: ComponentDefinition) -> None:
        """Add a custom component definition"""
        self.custom_components[component_id] = component
    
    def get_custom_component(self, component_id: int) -> Optional[ComponentDefinition]:
        """Get a custom component definition"""
        return self.custom_components.get(component_id)
    
    def get_all_component_definitions(self) -> List[ComponentDefinition]:
        """Get all component definitions"""
        all_components = []
        
        if self.game_component:
            all_components.append(self.game_component)
        
        all_components.extend(self.player_components.values())
        all_components.extend(self.card_components.values())
        all_components.extend(self.zone_components.values())
        all_components.extend(self.custom_components.values())
        
        return all_components
        
    
    def apply_event(self, event: Event) -> None:
        """Apply an event to the game state"""
        self.event_log.append(event)
        
        # Apply event effects based on type
        if event.type == "PhaseChanged":
            self.current_phase = event.payload.get("phase", self.current_phase)
            self.current_step = event.payload.get("step", self.current_step)
        
        elif event.type == PHASE_ENTERED:
            self.current_phase = event.payload.get("phase_id", self.current_phase)
        
        elif event.type == PHASE_EXITED:
            # Phase exit doesn't change current phase, but could trigger cleanup
            pass
        
        elif event.type == "TurnChanged":
            self.turn_number = event.payload.get("turn_number", self.turn_number)
            self.active_player = event.payload.get("active_player", self.active_player)
        
        elif event.type == "CardMoved":
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
        """Change a player's resource amount using the new resource system"""
        player = self.get_player(player_id)
        if not player or not self.resource_manager:
            return
        
        resource_def = self.resource_manager.get_resource_definition(resource_id)
        if not resource_def:
            return
        
        if amount > 0:
            player.gain_resource(resource_id, amount, resource_def)
        else:
            player.spend_resource(resource_id, abs(amount), resource_def)
    
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
            "current_phase": self.current_phase,
            "current_step": self.current_step,
            "turn_number": self.turn_number,
            "players": {pid: player.to_dict() for pid, player in self.players.items()},
            "zones": self.zones,
            "flags": self.flags,
            "event_count": len(self.event_log)
        }
    
    @classmethod
    def from_events(cls, match_id: str, events: List[Event]) -> "GameState":
        """Reconstruct state from event log"""
        state = cls(match_id=match_id, active_player="player1")
        
        for event in events:
            state.apply_event(event)
        
        return state
