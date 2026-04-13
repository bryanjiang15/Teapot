"""
Game compilation agents for the multi-agent pipeline.

Six agents, each with a single responsibility, following the same
Agent(name, instructions, tools, output_type, handoffs?) pattern
used in CreatorAPI/Agents/CardAgents.py.

Stages:
  1. GameSystemAnalyzer   — holistic game understanding → GameContext
  2. ComponentGraphAnalyzer — per-component blueprint enrichment (parallel)
     2a. EventNodeAnalyzer — sub-agent for event-heavy node clusters
  3. ComponentScriptGenerator — per-component Python script (parallel)
  4. EventSubscriptionResolver — cross-component subscription patching
  5. RulesetValidatorAgent — final coherence check
"""
from __future__ import annotations

from typing import Any, Optional

from agents import Agent, AgentOutputSchema
from pydantic import BaseModel

from .agent_registry import agent_registry
from .agent_tools import (
    build_event_subscription_map,
    build_game_context_schema,
    check_script_syntax,
    get_component_kind_schema,
    get_gameapi_reference,
    validate_event_name,
)


# ---------------------------------------------------------------------------
# Pydantic output types
# (AgentOutputSchema wraps these so the SDK can parse LLM JSON output)
# ---------------------------------------------------------------------------

class ComponentRelationshipOutput(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str  # "emits_event" | "subscribes_to" | "owns" | "contains"
    detail: str


class GameContextOutput(BaseModel):
    game_type: str
    game_description: str
    component_kinds: dict[str, str]       # component_id → kind
    event_vocabulary: list[str]
    relationships: list[ComponentRelationshipOutput]
    raw_summaries: dict[str, str]         # component_id → one-sentence role


class EventNodeAnalysisItem(BaseModel):
    event_type: str
    is_emitter: bool                      # True = emits, False = subscribes
    payload_fields: list[str]


class EventNodeAnalysisOutput(BaseModel):
    event_nodes: list[EventNodeAnalysisItem]


class EnrichedBlueprintOutput(BaseModel):
    component_id: str
    inferred_kind: str
    needs_on_init: bool
    needs_on_event: bool
    needs_on_update: bool
    event_subscriptions: list[str]
    emitted_events: list[str]
    initial_properties: dict[str, Any]
    referenced_component_names: list[str]
    game_context_snippet: str


class ScriptOutput(BaseModel):
    script: str
    syntax_valid: bool
    error: Optional[str] = None


class SubscriptionPatch(BaseModel):
    component_id: str
    patched_subscriptions: list[str]


class ResolverReportOutput(BaseModel):
    patches: list[SubscriptionPatch]
    warnings: list[str]
    errors: list[str]


class ValidationReportOutput(BaseModel):
    is_valid: bool
    errors: list[str]
    warnings: list[str]


# ---------------------------------------------------------------------------
# 2a. EventNodeAnalyzer  (sub-agent — defined first so it can be referenced
#     in ComponentGraphAnalyzer's handoffs list)
# ---------------------------------------------------------------------------

event_node_analyzer = Agent(
    name="Event Node Analyzer",
    instructions="""
    You are a specialist in analyzing event-driven node graphs for game components.

    You receive:
      - A JSON list of event/trigger nodes from a component's node_summary
      - The game's event_vocabulary (canonical event type strings)

    For each node, determine:
    1. The canonical event_type string — match to vocabulary if possible
       (use validate_event_name), else propose a new snake_case name.
    2. Whether the node is an emitter (game.emit) or subscriber (on_event handler).
    3. Any payload fields the event carries (infer from node labels/parameters).

    Return a list of EventNodeAnalysisItem objects.
    """,
    tools=[validate_event_name],
    output_type=AgentOutputSchema(EventNodeAnalysisOutput),
)


# ---------------------------------------------------------------------------
# 1. GameSystemAnalyzer
# ---------------------------------------------------------------------------

game_system_analyzer = Agent(
    name="Game System Analyzer",
    instructions="""
    You are a game architect analyzing a complete set of game component summaries.

    You will receive a JSON array. Each element has:
      - id: component UUID
      - name: component name
      - description: user-written description
      - kind: existing kind value (may be null or stale)
      - node_summary: list of {type, label, data} objects from the node graph

    Your tasks:
    1. Determine the high-level game_type (e.g. "turn-based card game",
       "deck-building game", "board game").
    2. Write a concise one-paragraph game_description.
    3. Infer the correct ComponentKind for each component:
       - "game"      → root orchestrator: manages turns, phases, win conditions
       - "player"    → a participant: has a hand, score, resources
       - "object"    → a card, piece, token, tile — the active gameplay entity
       - "container" → holds/orders objects: deck, hand, discard pile, board zone
       Use get_component_kind_schema as a heuristic aid.
    4. Build the canonical event_vocabulary: all event types that flow between
       components (e.g. "turn_start", "card_played", "damage_dealt").
    5. Identify cross-component relationships:
       - emits_event / subscribes_to (event-driven coupling)
       - owns (player owns containers/objects)
       - contains (container holds objects)
    6. Write a one-sentence raw_summary per component.

    Use build_game_context_schema to structure and validate your output.
    """,
    tools=[build_game_context_schema, get_component_kind_schema],
    output_type=AgentOutputSchema(GameContextOutput, strict_json_schema=False),
)


# ---------------------------------------------------------------------------
# 2. ComponentGraphAnalyzer
# ---------------------------------------------------------------------------

component_graph_analyzer = Agent(
    name="Component Graph Analyzer",
    instructions="""
    You are a component analyst enriching a single component's blueprint with
    cross-component context.

    You receive a JSON object with:
      - component: {id, name, description, kind, nodes (raw), node_summary}
      - game_context: {game_type, event_vocabulary, component_kinds,
                       relationships, raw_summaries}

    Your tasks:
    1. Confirm or correct the component's inferred_kind using the GameContext.
    2. Identify ALL event_subscriptions — event types this component listens for.
    3. Identify ALL emitted_events — event types this component emits.
    4. List referenced_component_names — other component names this script will
       interact with (via game.find() or game.instantiate()).
    5. Write a one-sentence game_context_snippet describing this component's
       role in the full game (inject into script generation prompt).
    6. Decide which lifecycle hooks are needed:
       - needs_on_init: True (always, for property setup)
       - needs_on_event: True if component reacts to any events
       - needs_on_update: True if component has passive/continuous logic
    7. Extract initial_properties from variable/property nodes in node_summary.

    If the component has more than 3 event-related nodes in its node_summary,
    hand off to event_node_analyzer for deeper event analysis, then merge the
    results into your output.

    Use get_component_kind_schema and validate_event_name as needed.
    """,
    tools=[get_component_kind_schema, validate_event_name, get_gameapi_reference],
    output_type=AgentOutputSchema(EnrichedBlueprintOutput, strict_json_schema=False),
    handoffs=[event_node_analyzer],
)


# ---------------------------------------------------------------------------
# 3. ComponentScriptGenerator
# ---------------------------------------------------------------------------

component_script_generator = Agent(
    name="Component Script Generator",
    instructions="""
    You are a game scripting expert. You write Python lifecycle scripts for
    individual game components using only the GameAPI interface.

    You receive a JSON object with:
      - blueprint: {component_id, component_name, kind, description,
                    inferred_kind, needs_on_init, needs_on_event,
                    needs_on_update, event_subscriptions, emitted_events,
                    initial_properties, node_summary, game_context_snippet,
                    referenced_component_names}

    Step 1: call get_gameapi_reference() to get the full GameAPI reference.
    Step 2: write the script following these rules:
      - Include ONLY the required hooks:
          on_init(game)        always
          on_event(event, game) if needs_on_event
          on_update(game)      if needs_on_update
      - on_event MUST dispatch on event.type using if/elif matching each
        event_subscription exactly
      - Use game.emit(event_type, payload={}) for each emitted_event
      - Only use the `game` object — no imports, no global/nonlocal
      - Allowed builtins: len, range, min, max, sum, abs, any, all, sorted,
        list, dict, set, filter, map, enumerate, zip, reversed, int, float,
        str, bool, round, isinstance
      - Keep logic concise and correct
      - Return ONLY the Python code, no markdown fences

    Step 3: call check_script_syntax(script) to validate.
    Step 4: if invalid, fix the error and re-validate (up to 3 attempts).

    Return a ScriptOutput with the final script, syntax_valid flag, and any
    remaining error message.
    """,
    tools=[get_gameapi_reference, check_script_syntax],
    output_type=AgentOutputSchema(ScriptOutput),
)


# ---------------------------------------------------------------------------
# 4. EventSubscriptionResolver
# ---------------------------------------------------------------------------

event_subscription_resolver = Agent(
    name="Event Subscription Resolver",
    instructions="""
    You are a cross-component event consistency checker.

    You receive a JSON array where each element has:
      - component_id: str
      - event_subscriptions: list[str]  (what the component listens for)
      - emitted_events: list[str]       (what the component emits)
      - script: str                     (generated Python lifecycle script)

    Your tasks:
    1. Use build_event_subscription_map to cross-reference all emitters and
       subscribers across components.
    2. For each component, inspect its script for `if event.type == "..."` branches.
    3. Detect and patch inconsistencies:
       a. A subscription listed but no matching handler in the script → remove it
       b. A handler in the script (`event.type == "X"`) but X not in subscriptions
          → add X to subscriptions
       c. An emitted event with no subscriber anywhere → add a warning
       d. A subscription with no emitter anywhere → add a warning
    4. Use validate_event_name on each resolved event name.

    Return a ResolverReportOutput with:
      - patches: [{component_id, patched_subscriptions}] for every component
        (include all components, even those with no changes)
      - warnings: list of human-readable warning strings
      - errors: list of human-readable error strings (blocking issues)
    """,
    tools=[build_event_subscription_map, validate_event_name],
    output_type=AgentOutputSchema(ResolverReportOutput),
)


# ---------------------------------------------------------------------------
# 5. RulesetValidatorAgent
# ---------------------------------------------------------------------------

ruleset_validator_agent = Agent(
    name="Ruleset Validator",
    instructions="""
    You are a final-pass game ruleset validator.

    You receive a JSON object representing a complete RulesetIR:
      {
        "version": "2.0",
        "metadata": {...},
        "component_definitions": [
          {
            "id": str,
            "kind": str,
            "name": str,
            "description": str,
            "script": str | null,
            "properties": dict,
            "event_subscriptions": list[str]
          },
          ...
        ]
      }

    Check for:
    1. Exactly one "game" component — error if 0 or >1.
    2. At least one "player" component — warning if 0.
    3. Every component with event_subscriptions has a non-null script — warning
       for each that doesn't.
    4. Every non-null script passes check_script_syntax — error for each failure.
    5. The "game" component's on_init should call game.emit() to bootstrap
       the game loop — warning if no `game.emit` found in the script.

    Set is_valid = True only if there are no errors (warnings are allowed).

    Return a ValidationReportOutput.
    """,
    tools=[check_script_syntax],
    output_type=AgentOutputSchema(ValidationReportOutput),
)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_AGENTS_TO_REGISTER: dict[str, Agent] = {
    "game_system_analyzer": game_system_analyzer,
    "component_graph_analyzer": component_graph_analyzer,
    "event_node_analyzer": event_node_analyzer,
    "component_script_generator": component_script_generator,
    "event_subscription_resolver": event_subscription_resolver,
    "ruleset_validator_agent": ruleset_validator_agent,
}


def register_game_agents() -> None:
    """Register all game compilation agents into the singleton registry.

    Safe to call at application startup (main.py startup_event).
    Skips already-registered agents so repeated calls are idempotent.
    """
    to_register = {
        name: agent
        for name, agent in _AGENTS_TO_REGISTER.items()
        if not agent_registry.has_agent(name)
    }
    if to_register:
        agent_registry.register_multiple_agents(to_register)
