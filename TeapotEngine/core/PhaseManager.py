"""
Turn/Phase Manager for game state
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
from TeapotEngine.ruleset.rule_definitions.RuleDefinition import TurnStructure, PhaseDefinition


class TurnType(Enum):
    """Types of turn management"""
    SINGLE_PLAYER = "single_player"  # Rotating active player
    SYNCHRONOUS = "synchronous"      # All players in same turn


@dataclass
class PhaseManager:
    """Manages turn and phase state for a game"""
    
    turn_structure: TurnStructure
    turn_type: TurnType
    player_ids: List[str]
    
    # Current state
    current_phase_id: int = 0
    current_step_id: int = 0
    turn_number: int = 1
    active_player: str = ""
    
    # Extracted phase order for easy navigation
    phase_order: List[int] = None
    initial_phase_id: int = None
    
    def __post_init__(self):
        """Initialize phase order and set initial phase"""
        # Extract phase order from turn structure
        self.phase_order = [phase.id for phase in self.turn_structure.phases]
        self.initial_phase_id = self.turn_structure.initial_phase_id or self.phase_order[0]
        
        # Set initial phase if not set
        if not self.current_phase_id:
            self.current_phase_id = self.initial_phase_id
        
        # Set initial active player
        if not self.active_player and self.player_ids:
            self.active_player = self.player_ids[0]
        
        self.max_turns_per_player = self.turn_structure.max_turns_per_player
    
    def advance_phase(self) -> Optional[int]:
        """Advance to the next phase in the turn structure
        
        Returns:
            Next phase ID if there is one, None if turn should end
        """
        try:
            current_index = self.phase_order.index(self.current_phase_id)
            next_index = current_index + 1
            
            if next_index < len(self.phase_order):
                # Move to next phase
                self.current_phase_id = self.phase_order[next_index]
                self.current_step_id = 0  # Reset to first step of new phase
                return self.current_phase_id
            else:
                # End of turn - no more phases
                return None
                
        except ValueError:
            # Current phase not found in order, reset to first phase
            self.current_phase_id = self.initial_phase_id
            self.current_step_id = 0
            return self.current_phase_id
    
    def advance_turn(self) -> int:
        """Advance to the next turn
        
        Returns:
            The new turn number
        """
        self.turn_number += 1
        self.current_phase_id = self.initial_phase_id
        self.current_step_id = 0
        
        # Rotate active player based on turn type
        if self.turn_type == TurnType.SINGLE_PLAYER:
            self._rotate_active_player()
        # For SYNCHRONOUS, active_player stays the same (all players)
        
        return self.turn_number
    
    def _rotate_active_player(self) -> None:
        """Rotate to the next active player"""
        if not self.player_ids:
            return
            
        try:
            current_index = self.player_ids.index(self.active_player)
            next_index = (current_index + 1) % len(self.player_ids)
            self.active_player = self.player_ids[next_index]
        except ValueError:
            # Current player not found, use first player
            self.active_player = self.player_ids[0]
    
    def game_over(self) -> bool:
        """Check if the game is over"""
        if not self.max_turns_per_player:
            return False

        return self.turn_number > self.max_turns_per_player
    
    def get_next_phase(self) -> Optional[int]:
        """Get the next phase ID without advancing state
        
        Returns:
            Next phase ID if there is one, None if turn would end
        """
        try:
            current_index = self.phase_order.index(self.current_phase_id)
            next_index = current_index + 1
            
            if next_index < len(self.phase_order):
                return self.phase_order[next_index]
            else:
                return None
                
        except ValueError:
            return self.initial_phase_id
    
    def get_current_phase_info(self) -> Optional[PhaseDefinition]:
        """Get the current phase definition
        
        Returns:
            PhaseDefinition for current phase, None if not found
        """
        return self.get_phase_by_id(self.current_phase_id)
    
    def get_phase_by_id(self, phase_id: int) -> Optional[PhaseDefinition]:
        """Get phase definition by ID
        
        Args:
            phase_id: The phase ID to look up
            
        Returns:
            PhaseDefinition if found, None otherwise
        """
        for phase in self.turn_structure.phases:
            if phase.id == phase_id:
                return phase
        return None
    
    def can_exit_phase(self, game_state) -> bool:
        """Check if the current phase can be exited based on exit conditions
        
        Args:
            game_state: GameState instance to check conditions against
            
        Returns:
            True if phase can be exited, False otherwise
        """
        phase = self.get_current_phase_info()
        if not phase:
            return True  # Unknown phase, allow exit
        
        # Check exit type conditions
        if phase.exit_type.value == "exit_on_no_actions":
            # This would need to be implemented based on game rules
            # For now, always allow exit
            return True
        elif phase.exit_type.value == "user_exit":
            # Requires explicit user action to exit
            return False
        
        return True
    
    def get_phase_steps(self, phase_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get steps for a phase
        
        Args:
            phase_id: Phase ID to get steps for, defaults to current phase
            
        Returns:
            List of step definitions
        """
        if phase_id is None:
            phase_id = self.current_phase_id
            
        phase = self.get_phase_by_id(phase_id)
        if not phase:
            return []
        
        return [step.dict() for step in phase.steps]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "current_phase_id": self.current_phase_id,
            "current_step_id": self.current_step_id,
            "turn_number": self.turn_number,
            "active_player": self.active_player,
            "turn_type": self.turn_type.value,
            "phase_order": self.phase_order,
            "initial_phase_id": self.initial_phase_id
        }
