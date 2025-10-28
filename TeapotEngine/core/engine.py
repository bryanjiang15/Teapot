"""
Main game engine that coordinates match actors
"""

from typing import Dict, Any, List, Optional
from core.match_actor import MatchActor
from core.state import GameState
from core.events import Event


class GameEngine:
    """Main game engine that manages match actors"""
    
    def __init__(self):
        self.match_actors: Dict[str, MatchActor] = {}
    
    def create_match(self, match_id: str, ruleset_ir: Dict[str, Any], seed: Optional[int] = None, verbose: bool = False) -> MatchActor:
        """Create a new match actor"""
        if match_id in self.match_actors:
            raise ValueError(f"Match {match_id} already exists")
        
        actor = MatchActor(match_id, ruleset_ir, seed, verbose)
        self.match_actors[match_id] = actor
        return actor
    
    def get_match(self, match_id: str) -> Optional[MatchActor]:
        """Get a match actor by ID"""
        return self.match_actors.get(match_id)
    
    def remove_match(self, match_id: str) -> bool:
        """Remove a match actor"""
        if match_id in self.match_actors:
            del self.match_actors[match_id]
            return True
        return False
    
    def list_matches(self) -> List[str]:
        """List all active match IDs"""
        return list(self.match_actors.keys())
    
    async def process_action(self, match_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Process an action for a specific match"""
        actor = self.get_match(match_id)
        if not actor:
            return {"error": f"Match {match_id} not found"}
        
        return await actor.process_action(action)
    
    def get_match_state(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a match"""
        actor = self.get_match(match_id)
        if not actor:
            return None
        
        return actor.get_current_state()
    
    def get_available_actions(self, match_id: str, player_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get available actions for a player in a match"""
        actor = self.get_match(match_id)
        if not actor:
            return None
        
        return actor.get_available_actions(player_id)
    
    def get_actions_for_object(
        self, 
        match_id: str, 
        player_id: int, 
        object_type: str,
        object_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get available actions for a selected object"""
        actor = self.get_match(match_id)
        if not actor:
            return None
        
        # Convert string to enum
        from ruleset.rule_definitions import SelectableObjectType
        try:
            object_type_enum = SelectableObjectType(object_type)
        except ValueError:
            return None
        
        return actor.get_actions_for_object(player_id, object_type_enum, object_id)