"""
api_models — Pydantic mirror of TeapotAPI's RulesetIR response schemas.

Used by loader/RulesetLoader to deserialise the JSON payload from
GET /projects/{id}/ruleset into typed objects before converting them
to engine-internal RulesetIR and ScriptedComponent instances.

These models should stay in sync with TeapotAPI/app/schemas/ruleset.py.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ScriptedComponentResponse(BaseModel):
    """API representation of one compiled component definition."""
    id: str
    kind: str                                    # ComponentKind.value
    name: str
    description: Optional[str] = None
    script: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)
    event_subscriptions: list[str] = Field(default_factory=list)


class RulesetIRResponse(BaseModel):
    """Top-level response from GET /projects/{id}/ruleset."""
    version: str = "2.0"
    metadata: dict[str, Any] = Field(default_factory=dict)
    component_definitions: list[ScriptedComponentResponse] = Field(default_factory=list)
    constants: dict[str, Any] = Field(default_factory=dict)
