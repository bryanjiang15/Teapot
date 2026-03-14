"""
RulesetIR — the compiled intermediate representation consumed by the engine.

Produced by TeapotAPI's compilation pipeline (POST /projects/{id}/compile)
and loaded by loader/RulesetLoader from GET /projects/{id}/ruleset.
Contains no graph data or AI prompts — only resolved ScriptedComponent
definitions and metadata.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from .ScriptedComponent import ScriptedComponent, ComponentKind


class RulesetIR(BaseModel):
    """Top-level compiled game definition ready for engine execution."""

    version: str = "2.0"
    metadata: dict[str, Any] = Field(default_factory=dict)
    component_definitions: list[ScriptedComponent] = Field(default_factory=list)
    constants: dict[str, Any] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience lookups
    # ------------------------------------------------------------------

    def get_component(self, component_id: str) -> Optional[ScriptedComponent]:
        """Look up a definition by its UUID string."""
        for c in self.component_definitions:
            if c.id == component_id:
                return c
        return None

    def get_component_by_name(self, name: str) -> Optional[ScriptedComponent]:
        """Look up the first definition whose name matches (case-sensitive)."""
        for c in self.component_definitions:
            if c.name == name:
                return c
        return None

    def get_components_by_kind(self, kind: ComponentKind) -> list[ScriptedComponent]:
        return [c for c in self.component_definitions if c.kind == kind]

    def get_game_component(self) -> Optional[ScriptedComponent]:
        comps = self.get_components_by_kind(ComponentKind.GAME)
        return comps[0] if comps else None

    def get_player_components(self) -> list[ScriptedComponent]:
        return self.get_components_by_kind(ComponentKind.PLAYER)

    def get_object_components(self) -> list[ScriptedComponent]:
        return self.get_components_by_kind(ComponentKind.OBJECT)

    def get_container_components(self) -> list[ScriptedComponent]:
        return self.get_components_by_kind(ComponentKind.CONTAINER)

    def get_subscribing_components(self) -> list[ScriptedComponent]:
        """All definitions that subscribe to at least one event."""
        return [c for c in self.component_definitions if c.event_subscriptions]

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RulesetIR":
        return cls.model_validate(data)
