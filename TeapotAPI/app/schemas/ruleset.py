"""
Ruleset schemas — response types for the compiled RulesetIR.

These are served by GET /projects/{id}/ruleset and consumed by
TeapotEngine's RulesetLoader. The schemas must stay in sync with
TeapotEngine/models/api_models.py.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ScriptedComponentResponse(BaseModel):
    """Compiled representation of one component definition."""
    id: str
    kind: str                                    # ComponentKind value
    name: str
    description: Optional[str] = None
    script: Optional[str] = None                 # AI-generated lifecycle script
    properties: dict[str, Any] = Field(default_factory=dict)
    event_subscriptions: list[str] = Field(default_factory=list)


class RulesetIRResponse(BaseModel):
    """Full compiled ruleset returned by GET /projects/{id}/ruleset."""
    version: str = "2.0"
    metadata: dict[str, Any] = Field(default_factory=dict)
    component_definitions: list[ScriptedComponentResponse] = Field(default_factory=list)
    constants: dict[str, Any] = Field(default_factory=dict)
