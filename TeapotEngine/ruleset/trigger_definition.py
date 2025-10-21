"""
Trigger definition models
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class TriggerDefinition(BaseModel):
    """Definition of an event trigger"""
    id: int
    when: Dict[str, Any]
    conditions: List[Dict[str, Any]] = Field(default_factory=list)
    execute_rules: List[int] = Field(default_factory=list)  # Rule IDs to execute
    timing: str = "post"  # "pre", "post"
    caused_by: Optional[str] = None  # Represents the component that caused the trigger
    scope: str = "self"  # "self", "all", "opponent"
