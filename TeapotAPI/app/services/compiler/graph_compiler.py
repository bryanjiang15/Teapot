"""
GraphCompiler — transforms a component's React Flow node graph + description
into a ComponentBlueprint that the ScriptGenerator can use.

The blueprint is a normalised, AI-friendly summary of:
  - what kind of game entity this is
  - what it does (in natural language)
  - which lifecycle hooks it needs (on_init / on_event / on_update)
  - which events it subscribes to
  - which initial properties it should have
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ComponentBlueprint:
    """Intermediate representation of a component ready for the AI Scripter.

    Attributes
    ----------
    component_id : str
        UUID of the API Component row.
    component_name : str
        Human-readable name of the component.
    description : str
        Natural-language description written by the user or the Architect agent.
    kind : str
        "game" | "player" | "object" | "container"
    needs_on_init : bool
        Whether the script should include an on_init hook.
    needs_on_event : bool
        Whether the script should include an on_event hook.
    needs_on_update : bool
        Whether the script should include an on_update hook.
    event_subscriptions : list[str]
        Event types the component listens for.
    initial_properties : dict[str, Any]
        Static key/value properties derived from the graph.
    node_summary : list[dict]
        Simplified summary of the relevant nodes (for AI context).
    """
    component_id: str
    component_name: str
    description: str
    kind: str
    needs_on_init: bool = True
    needs_on_event: bool = False
    needs_on_update: bool = False
    event_subscriptions: list[str] = field(default_factory=list)
    initial_properties: dict[str, Any] = field(default_factory=dict)
    node_summary: list[dict] = field(default_factory=list)


class GraphCompiler:
    """Converts a component's node graph + metadata into a ComponentBlueprint."""

    # Node type categories used to decide which lifecycle hooks are needed
    _EVENT_NODE_TYPES: frozenset[str] = frozenset({
        "event_trigger", "on_event", "event_listener", "trigger",
    })
    _UPDATE_NODE_TYPES: frozenset[str] = frozenset({
        "on_update", "passive_effect", "state_check", "win_condition",
    })
    _PROPERTY_NODE_TYPES: frozenset[str] = frozenset({
        "property", "stat", "attribute", "variable",
    })

    def compile(
        self,
        component_id: str,
        name: str,
        description: Optional[str],
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        kind: str = "object",
    ) -> ComponentBlueprint:
        """Build a ComponentBlueprint from the raw React Flow graph.

        Parameters
        ----------
        component_id : str
        name : str
        description : str | None
        nodes : list of React Flow node dicts
        edges : list of React Flow edge dicts
        kind : str  (ComponentKind.value)
        """
        description = description or f"A {kind} named {name}."

        needs_on_event = False
        needs_on_update = False
        event_subscriptions: list[str] = []
        initial_properties: dict[str, Any] = {}
        node_summary: list[dict] = []

        for node in nodes:
            node_type: str = (node.get("type") or "").lower()
            node_data: dict = node.get("data") or {}
            label: str = node_data.get("label") or node_data.get("name") or node_type

            # Detect lifecycle hook requirements
            if node_type in self._EVENT_NODE_TYPES:
                needs_on_event = True
                event_type = node_data.get("eventType") or node_data.get("event_type") or ""
                if event_type and event_type not in event_subscriptions:
                    event_subscriptions.append(event_type)

            if node_type in self._UPDATE_NODE_TYPES:
                needs_on_update = True

            # Collect initial properties
            if node_type in self._PROPERTY_NODE_TYPES:
                prop_name = node_data.get("key") or label
                prop_value = node_data.get("value") or node_data.get("default")
                if prop_name and prop_value is not None:
                    initial_properties[prop_name] = prop_value

            # Simplified summary for AI context
            if node_type:
                node_summary.append({
                    "type": node_type,
                    "label": label,
                    "data": {
                        k: v for k, v in node_data.items()
                        if k not in ("id", "position") and v is not None
                    },
                })

        return ComponentBlueprint(
            component_id=component_id,
            component_name=name,
            description=description,
            kind=kind,
            needs_on_init=True,  # always include on_init for property setup
            needs_on_event=needs_on_event,
            needs_on_update=needs_on_update,
            event_subscriptions=event_subscriptions,
            initial_properties=initial_properties,
            node_summary=node_summary,
        )
