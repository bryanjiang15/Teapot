"""
Game state management with event sourcing
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from .events import Event


@dataclass
class GameState:
    """Current state of the game derived from events"""
    match_id: str
    active_player: str
    current_phase: str = "start"
    current_step: str = "untap"
    turn_number: int = 1
    
    # Player states
    players: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Zones and cards
    zones: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Resources and counters
    resources: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Game flags and status
    flags: Dict[str, Any] = field(default_factory=dict)
    
    # Event log for replay
    event_log: List[Event] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default zones and player states"""
        if not self.players:
            # Initialize with default player structure
            for player_id in ["player1", "player2"]:  # Default for now
                self.players[player_id] = {
                    "life_total": 20,
                    "hand_size": 7,
                    "deck_size": 60,
                    "graveyard_size": 0
                }
        
        if not self.zones:
            # Initialize default zones
            self.zones = {
                "hand": {"player1": [], "player2": []},
                "battlefield": [],
                "graveyard": {"player1": [], "player2": []},
                "exile": [],
                "deck": {"player1": [], "player2": []}
            }
    
    def apply_event(self, event: Event) -> None:
        """Apply an event to the game state"""
        self.event_log.append(event)
        
        # Apply event effects based on type
        if event.type == "PhaseChanged":
            self.current_phase = event.payload.get("phase", self.current_phase)
            self.current_step = event.payload.get("step", self.current_step)
        
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
    
    def _change_resource(self, player_id: str, resource: str, amount: int) -> None:
        """Change a player's resource amount"""
        if player_id not in self.resources:
            self.resources[player_id] = {}
        
        current = self.resources[player_id].get(resource, 0)
        self.resources[player_id][resource] = current + amount
    
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
            "players": self.players,
            "zones": self.zones,
            "resources": self.resources,
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
