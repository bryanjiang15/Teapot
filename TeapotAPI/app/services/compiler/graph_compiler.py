"""
GraphCompiler — transforms a component's React Flow node graph + description
into a ComponentBlueprint that the ScriptGenerator can use.

The blueprint is a normalised, AI-friendly summary of:
  - what kind of game entity this is
  - what it does (in natural language)
  - which lifecycle hooks it needs (on_init / on_event / on_update)
  - which events it subscribes to
  - which initial properties it should have

Classification prefers **data.templateId**, **data.category**, and **data.eventType**
because React Flow `node.type` is usually the string ``custom``.
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

    _UPDATE_TEMPLATE_IDS: frozenset[str] = frozenset({
        "flow-multibranch",
    })
    _UPDATE_CATEGORIES: frozenset[str] = frozenset({
        "flow",
    })
    # Heuristic fallbacks when templateId / category missing (legacy graphs)
    _RF_PROPERTY_TYPES: frozenset[str] = frozenset({
        "property", "stat", "attribute", "variable",
    })

    @staticmethod
    def _param_dict(node_data: dict) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for p in node_data.get("parameters") or []:
            if isinstance(p, dict) and p.get("id") is not None:
                out[str(p["id"])] = p.get("value")
        return out

    @staticmethod
    def _append_subscription(subs: list[str], event_type: str) -> None:
        et = str(event_type).strip()
        if et and et not in subs:
            subs.append(et)

    def _ingest_node(
        self,
        node: dict[str, Any],
        needs_on_event: bool,
        needs_on_update: bool,
        event_subscriptions: list[str],
        initial_properties: dict[str, Any],
        node_summary: list[dict],
    ) -> tuple[bool, bool]:
        node_data: dict = node.get("data") or {}
        label: str = node_data.get("label") or node_data.get("name") or ""
        template_id: str = str(node_data.get("templateId") or "").strip().lower()
        category: str = str(node_data.get("category") or "").strip().lower()
        rf_type: str = str(node.get("type") or "").strip().lower()
        params = self._param_dict(node_data)
        subkind = str(node_data.get("subkind") or "").strip().lower()

        summary_type = template_id or category or rf_type
        if summary_type:
            node_summary.append({
                "type": summary_type,
                "label": label,
                "data": {
                    k: v for k, v in node_data.items()
                    if k not in ("id", "position") and v is not None
                },
            })

        is_emit = (
            template_id == "trigger-emit-event"
            or subkind == "emit_event"
        )
        is_trigger_subscribe = (
            category == "trigger"
            and not is_emit
        )
        # Legacy: workspace used category "event"
        if category == "event":
            is_trigger_subscribe = True
            is_emit = False

        ne = needs_on_event
        nu = needs_on_update

        if is_trigger_subscribe:
            ne = True
            et = (
                node_data.get("eventType")
                or node_data.get("event_type")
                or params.get("listenEventType")
                or ""
            )
            self._append_subscription(event_subscriptions, str(et))

        if (
            template_id in self._UPDATE_TEMPLATE_IDS
            or category in self._UPDATE_CATEGORIES
            or rf_type in self._UPDATE_TEMPLATE_IDS
        ):
            nu = True

        # Named variable → component property key (init placeholder)
        # variable_reference nodes wire graphs only; they never declare properties.
        if subkind != "variable_reference" and (
            template_id in ("state-variable", "state-get-property")
            or (category == "state" and subkind in ("variable", "get_property"))
        ):
            name = str(
                params.get("name") or params.get("propertyKey") or ""
            ).strip()
            if name:
                initial_properties.setdefault(name, None)

        # initial_properties from constant / legacy variable node
        if template_id == "input-constant" or (
            category == "input" and subkind == "constant"
        ):
            key = str(params.get("asPropertyKey") or "").strip()
            if key:
                kind = str(params.get("constantKind") or "integer")
                if kind == "integer":
                    initial_properties[key] = params.get("intValue", 0)
                elif kind == "string":
                    initial_properties[key] = params.get("stringValue", "")
                else:
                    initial_properties[key] = params.get("enumValue", "")

        # Legacy graphs: category variable + constant-style parameters
        if category == "variable" and node_data.get("label") == "Constant":
            prop_name = label or "value"
            prop_value = params.get("value") if "value" in params else node_data.get("value")
            if prop_value is not None and prop_name:
                initial_properties.setdefault(prop_name, prop_value)

        # Fallback: RF type used as semantic discriminator (older tooling)
        if rf_type in self._RF_PROPERTY_TYPES:
            prop_name = node_data.get("key") or label
            prop_value = node_data.get("value") or node_data.get("default")
            if prop_name and prop_value is not None:
                initial_properties[str(prop_name)] = prop_value

        if rf_type in ("on_update", "passive_effect", "state_check", "win_condition"):
            nu = True
        if rf_type in ("event_trigger", "on_event", "event_listener", "trigger"):
            ne = True
            et = node_data.get("eventType") or node_data.get("event_type") or ""
            self._append_subscription(event_subscriptions, str(et))

        return ne, nu

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

        Notes
        -----
        ``edges`` are accepted for API compatibility; hook analysis may use them later.
        """
        _ = edges  # reserved
        description = description or f"A {kind} named {name}."

        needs_on_event = False
        needs_on_update = False
        event_subscriptions: list[str] = []
        initial_properties: dict[str, Any] = {}
        node_summary: list[dict] = []

        for node in nodes:
            needs_on_event, needs_on_update = self._ingest_node(
                node,
                needs_on_event,
                needs_on_update,
                event_subscriptions,
                initial_properties,
                node_summary,
            )

        return ComponentBlueprint(
            component_id=component_id,
            component_name=name,
            description=description,
            kind=kind,
            needs_on_init=True,
            needs_on_event=needs_on_event,
            needs_on_update=needs_on_update,
            event_subscriptions=event_subscriptions,
            initial_properties=initial_properties,
            node_summary=node_summary,
        )
