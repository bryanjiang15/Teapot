"""
GameContext and EnrichedComponentBlueprint — shared data models for the
multi-agent game compilation pipeline.

GameContext is produced by Stage 1 (GameSystemAnalyzer) and injected into
every per-component agent in Stages 2 and 3 so each agent understands the
full game system, not just its own component in isolation.

EnrichedComponentBlueprint extends ComponentBlueprint with cross-component
context fields produced by ComponentGraphAnalyzer (Stage 2).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .graph_compiler import ComponentBlueprint


@dataclass
class ComponentRelationship:
    """Describes a directed dependency between two components.

    Attributes
    ----------
    source_id : str
        Component ID of the emitter / owner.
    target_id : str
        Component ID of the subscriber / child.
    relationship_type : str
        One of: "emits_event", "subscribes_to", "owns", "contains".
    detail : str
        Event name, container name, or other relationship detail.
    """
    source_id: str
    target_id: str
    relationship_type: str
    detail: str


@dataclass
class GameContext:
    """Shared game-level context produced by GameSystemAnalyzer.

    Passed read-only to every downstream agent so they understand the
    full system before generating per-component blueprints and scripts.

    Attributes
    ----------
    game_type : str
        High-level genre inferred by the analyzer (e.g. "turn-based card game").
    game_description : str
        One-paragraph natural language synthesis of the full game.
    component_names : list[str]
        All component names in the project.
    component_kinds : dict[str, str]
        component_id → kind ("game" | "player" | "object" | "container").
    event_vocabulary : list[str]
        Canonical event type strings used across the game
        (e.g. "turn_start", "card_played", "game_over").
    relationships : list[ComponentRelationship]
        Cross-component dependencies detected by the analyzer.
    raw_summaries : dict[str, str]
        component_id → one-sentence role description.
    """
    game_type: str = ""
    game_description: str = ""
    component_names: list[str] = field(default_factory=list)
    component_kinds: dict[str, str] = field(default_factory=dict)
    event_vocabulary: list[str] = field(default_factory=list)
    relationships: list[ComponentRelationship] = field(default_factory=list)
    raw_summaries: dict[str, str] = field(default_factory=dict)

    def to_prompt_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dict suitable for injection into LLM prompts."""
        return {
            "game_type": self.game_type,
            "game_description": self.game_description,
            "component_names": self.component_names,
            "component_kinds": self.component_kinds,
            "event_vocabulary": self.event_vocabulary,
            "relationships": [
                {
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "type": r.relationship_type,
                    "detail": r.detail,
                }
                for r in self.relationships
            ],
            "raw_summaries": self.raw_summaries,
        }


@dataclass
class EnrichedComponentBlueprint(ComponentBlueprint):
    """ComponentBlueprint extended with cross-component context.

    Produced by ComponentGraphAnalyzer (Stage 2) after combining the
    structural blueprint from GraphCompiler with GameContext knowledge.

    Additional attributes beyond ComponentBlueprint
    -----------------------------------------------
    inferred_kind : str
        Kind confirmed or overridden by the AI agent (may differ from the
        DB value if the DB value was stale or None).
    emitted_events : list[str]
        Event types this component emits (used by EventSubscriptionResolver).
    referenced_component_names : list[str]
        Names of other components this script will interact with via
        game.find() or game.instantiate().
    game_context_snippet : str
        Compact prose summary of this component's role in the full game,
        injected into the ComponentScriptGenerator prompt.
    """
    inferred_kind: str = ""
    emitted_events: list[str] = field(default_factory=list)
    referenced_component_names: list[str] = field(default_factory=list)
    game_context_snippet: str = ""
