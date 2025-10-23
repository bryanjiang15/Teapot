"""
Ruleset IR validation
"""

from typing import List, Dict, Any, Optional
from .ir import RulesetIR
from .rule_definitions import TriggerDefinition, ActionDefinition, PhaseDefinition


class ValidationError(Exception):
    """Raised when ruleset validation fails"""
    pass


class RulesetValidator:
    """Validates ruleset IR for correctness and safety"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, ruleset: RulesetIR) -> bool:
        """Validate a complete ruleset"""
        self.errors.clear()
        self.warnings.clear()
        
        # Validate structure
        self._validate_metadata(ruleset)
        self._validate_turn_structure(ruleset)
        self._validate_actions(ruleset)
        self._validate_triggers(ruleset)
        self._validate_zones(ruleset)
        self._validate_keywords(ruleset)
        
        # Validate component-based structure
        self._validate_components(ruleset)
        
        # Validate references
        self._validate_action_references(ruleset)
        self._validate_trigger_references(ruleset)
        
        return len(self.errors) == 0
    
    def _validate_metadata(self, ruleset: RulesetIR) -> None:
        """Validate ruleset metadata"""
        if not ruleset.metadata.get("name"):
            self.errors.append("Ruleset must have a name")
        
        if not ruleset.metadata.get("author"):
            self.warnings.append("Ruleset should have an author")
    
    def _validate_turn_structure(self, ruleset: RulesetIR) -> None:
        """Validate turn structure"""
        if not ruleset.turn_structure.phases:
            self.errors.append("Ruleset must have at least one phase")
            return
        
        # Check for duplicate phase IDs
        phase_ids = [phase.id for phase in ruleset.turn_structure.phases]
        if len(phase_ids) != len(set(phase_ids)):
            self.errors.append("Duplicate phase IDs found")
        
        # Validate each phase
        for phase in ruleset.turn_structure.phases:
            self._validate_phase(phase)
    
    def _validate_phase(self, phase: PhaseDefinition) -> None:
        """Validate a single phase"""
        if not phase.steps:
            self.errors.append(f"Phase '{phase.id}' must have at least one step")
            return
        
        # Check for duplicate step IDs
        step_ids = [step.id for step in phase.steps]
        if len(step_ids) != len(set(step_ids)):
            self.errors.append(f"Duplicate step IDs in phase '{phase.id}'")
    
    def _validate_actions(self, ruleset: RulesetIR) -> None:
        """Validate actions"""
        if not ruleset.actions:
            self.warnings.append("Ruleset has no actions defined")
            return
        
        # Check for duplicate action IDs
        action_ids = [action.id for action in ruleset.actions]
        if len(action_ids) != len(set(action_ids)):
            self.errors.append("Duplicate action IDs found")
        
        # Validate each action
        for action in ruleset.actions:
            self._validate_action(action)
    
    def _validate_action(self, action: ActionDefinition) -> None:
        """Validate a single action"""
        if not action.effects:
            self.warnings.append(f"Action '{action.id}' has no effects")
        
        # Validate timing
        if action.timing not in ["stack", "instant", "sorcery"]:
            self.errors.append(f"Action '{action.id}' has invalid timing: {action.timing}")
    
    def _validate_triggers(self, ruleset: RulesetIR) -> None:
        """Validate triggers"""
        # Check for duplicate trigger IDs
        trigger_ids = [trigger.id for trigger in ruleset.triggers]
        if len(trigger_ids) != len(set(trigger_ids)):
            self.errors.append("Duplicate trigger IDs found")
        
        # Validate each trigger
        for trigger in ruleset.triggers:
            self._validate_trigger(trigger)
    
    def _validate_trigger(self, trigger) -> None:
        """Validate a single trigger"""
        if not trigger.when:
            self.errors.append(f"Trigger '{trigger.id}' must have 'when' condition")
        
        if not trigger.execute_rules:
            self.warnings.append(f"Trigger '{trigger.id}' has no execute_rules")
        
        # Validate timing
        if trigger.timing not in ["pre", "post"]:
            self.errors.append(f"Trigger '{trigger.id}' has invalid timing: {trigger.timing}")
    
    def _validate_zones(self, ruleset: RulesetIR) -> None:
        """Validate zones"""
        # Check for duplicate zone IDs
        zone_ids = [zone.id for zone in ruleset.zones]
        if len(zone_ids) != len(set(zone_ids)):
            self.errors.append("Duplicate zone IDs found")
        
        # Validate each zone
        for zone in ruleset.zones:
            self._validate_zone(zone)
    
    def _validate_zone(self, zone) -> None:
        """Validate a single zone"""
        # Handle both string and enum values
        zone_type = zone.zone_type
        if hasattr(zone_type, 'value'):
            zone_type = zone_type.value
        
        if zone_type not in ["private", "public", "shared"]:
            self.errors.append(f"Zone '{zone.id}' has invalid type: {zone_type}")
    
    def _validate_keywords(self, ruleset: RulesetIR) -> None:
        """Validate keywords"""
        # Check for duplicate keyword IDs
        keyword_ids = [keyword.id for keyword in ruleset.keywords]
        if len(keyword_ids) != len(set(keyword_ids)):
            self.errors.append("Duplicate keyword IDs found")
    
    def _validate_action_references(self, ruleset: RulesetIR) -> None:
        """Validate references between actions and other components"""
        # This would check for references to zones, keywords, etc.
        pass
    
    def _validate_trigger_references(self, ruleset: RulesetIR) -> None:
        """Validate references between triggers and other components"""
        # This would check for references to actions, zones, etc.
        pass
    
    def _validate_components(self, ruleset: RulesetIR) -> None:
        """Validate component-based structure"""
        # Validate all component definitions
        for component in ruleset.component_definitions:
            component.validate_component()

    def get_errors(self) -> List[str]:
        """Get validation errors"""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """Get validation warnings"""
        return self.warnings.copy()
    
    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return len(self.warnings) > 0
