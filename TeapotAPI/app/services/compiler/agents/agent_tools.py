"""
Agent tools for the game compilation pipeline.

Each @function_tool is a deterministic Python function that agents can call
to validate data, look up schemas, or check syntax — following the same
pattern as CreatorAPI's trigger_schema_tool, effect_schema_tool, etc.
"""
from __future__ import annotations

import ast
from typing import Any

from agents import function_tool

from app.services.compiler.script_generator import ScriptGenerator


# ---------------------------------------------------------------------------
# Kind recommendation
# ---------------------------------------------------------------------------

_KIND_KEYWORDS: dict[str, list[str]] = {
    "game": ["game", "match", "ruleset", "manager", "orchestrat", "turn", "phase", "win"],
    "player": ["player", "user", "participant", "hand", "score", "resource"],
    "container": ["deck", "pile", "zone", "stack", "board", "slot", "area", "collection"],
    "object": ["card", "piece", "token", "tile", "unit", "creature", "item"],
}


@function_tool
def get_component_kind_schema(
    name: str,
    description: str,
    node_types: list[str],
) -> str:
    """Recommend a ComponentKind based on name, description, and node types.

    Returns one of: "game", "player", "object", "container".
    """
    text = f"{name} {description}".lower()
    scores: dict[str, int] = {kind: 0 for kind in _KIND_KEYWORDS}

    for kind, keywords in _KIND_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[kind] += 1

    # Node type signals
    event_nodes = {"on_update", "passive_effect", "win_condition", "state_check"}
    if any(nt.lower() in event_nodes for nt in node_types):
        scores["game"] += 1

    best = max(scores, key=lambda k: scores[k])
    # Default to "object" when nothing matches
    return best if scores[best] > 0 else "object"


# ---------------------------------------------------------------------------
# GameContext schema builder
# ---------------------------------------------------------------------------

@function_tool(strict_mode=False)
def build_game_context_schema(
    game_type: str,
    game_description: str,
    event_vocabulary: list[str],
    component_kinds: dict[str, str],
    raw_summaries: dict[str, str],
) -> dict[str, Any]:
    """Validate and structure the fields for a GameContext.

    Returns a dict with the canonical GameContext field layout.
    """
    # Normalise event names to snake_case
    normalised_vocab = [e.lower().replace(" ", "_").replace("-", "_") for e in event_vocabulary]

    # Ensure kinds are valid
    valid_kinds = {"game", "player", "object", "container"}
    sanitised_kinds = {
        cid: (kind if kind in valid_kinds else "object")
        for cid, kind in component_kinds.items()
    }

    return {
        "game_type": game_type.strip(),
        "game_description": game_description.strip(),
        "event_vocabulary": sorted(set(normalised_vocab)),
        "component_kinds": sanitised_kinds,
        "raw_summaries": raw_summaries,
    }


# ---------------------------------------------------------------------------
# GameAPI reference
# ---------------------------------------------------------------------------

@function_tool
def get_gameapi_reference() -> str:
    """Return the full GameAPI reference string for injection into script prompts."""
    return ScriptGenerator.GAMEAPI_CONTEXT


# ---------------------------------------------------------------------------
# Event name validation
# ---------------------------------------------------------------------------

@function_tool
def validate_event_name(event_name: str, vocabulary: list[str]) -> bool:
    """Return True if event_name is in the established vocabulary.

    Case-insensitive, normalises spaces/hyphens to underscores before
    comparing.
    """
    def normalise(s: str) -> str:
        return s.lower().replace(" ", "_").replace("-", "_")

    norm_name = normalise(event_name)
    norm_vocab = {normalise(v) for v in vocabulary}
    return norm_name in norm_vocab


# ---------------------------------------------------------------------------
# Event subscription map builder
# ---------------------------------------------------------------------------

@function_tool(strict_mode=False)
def build_event_subscription_map(
    emitters: list[dict[str, Any]],
    subscribers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Cross-reference emitters and subscribers; return resolved event pairs.

    Parameters
    ----------
    emitters : list of {"component_id": str, "event_type": str}
    subscribers : list of {"component_id": str, "event_type": str}

    Returns a list of resolved pairs:
      {"event_type": str, "emitter_ids": [str], "subscriber_ids": [str],
       "has_emitter": bool, "has_subscriber": bool}
    """
    def norm(s: str) -> str:
        return s.lower().replace(" ", "_").replace("-", "_")

    # Build maps
    emit_map: dict[str, list[str]] = {}
    for e in emitters:
        et = norm(e.get("event_type", ""))
        emit_map.setdefault(et, []).append(e.get("component_id", ""))

    sub_map: dict[str, list[str]] = {}
    for s in subscribers:
        et = norm(s.get("event_type", ""))
        sub_map.setdefault(et, []).append(s.get("component_id", ""))

    all_events = set(emit_map) | set(sub_map)
    result = []
    for event_type in sorted(all_events):
        emitter_ids = emit_map.get(event_type, [])
        subscriber_ids = sub_map.get(event_type, [])
        result.append({
            "event_type": event_type,
            "emitter_ids": emitter_ids,
            "subscriber_ids": subscriber_ids,
            "has_emitter": bool(emitter_ids),
            "has_subscriber": bool(subscriber_ids),
        })

    return result


# ---------------------------------------------------------------------------
# Script syntax checker
# ---------------------------------------------------------------------------

@function_tool(strict_mode=False)
def check_script_syntax(script: str) -> dict[str, Any]:
    """Check Python script syntax using ast.parse().

    Returns {"valid": bool, "error": str | None}.
    """
    try:
        # Try TeapotEngine's validator first for richer checks
        try:
            from TeapotEngine.core.ScriptRunner import ScriptRunner
            runner = ScriptRunner()
            runner.validate(script)
        except ImportError:
            ast.parse(script)
        return {"valid": True, "error": None}
    except SyntaxError as exc:
        return {"valid": False, "error": f"SyntaxError at line {exc.lineno}: {exc.msg}"}
    except Exception as exc:
        return {"valid": False, "error": str(exc)}
