"""
GameCompilationPipeline — 5-stage multi-agent orchestrator.

Compiles an entire project's component set into a coherent RulesetIR by
coordinating specialized AI agents, each with a single responsibility.

Stages
------
1. GameSystemAnalyzer (sequential)
   Reads all component summaries → GameContext
   (game type, component kinds, event vocabulary, cross-component relationships)

2. ComponentGraphAnalyzer × N (parallel via asyncio.gather)
   Per-component: node graph + behaviorDescription + GameContext
   → EnrichedComponentBlueprint
   [Hands off to EventNodeAnalyzer for event-heavy components]

3. ComponentScriptGenerator × N (parallel via asyncio.gather)
   Per-component: EnrichedComponentBlueprint + GameContext → Python script
   [Validates via check_script_syntax, retries up to 3×]

4. EventSubscriptionResolver (sequential)
   Cross-component: patches event_subscriptions for consistency across all scripts

5. RulesetValidatorAgent (sequential)
   Validates the assembled RulesetIR for structural coherence

The compile_project endpoint in projects.py calls pipeline.run() and writes
the results back to the DB using the same field assignments as before.
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from agents import Runner, trace

from .agents.agent_registry import agent_registry
from .game_context import ComponentRelationship, EnrichedComponentBlueprint, GameContext
from .graph_compiler import GraphCompiler
from .scene_compiler import SceneCompiler

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class ComponentCompileResult:
    component_id: str
    kind: str
    script: str
    properties: dict[str, Any]
    event_subscriptions: list[str]


@dataclass
class GameCompilationPipelineResult:
    project_id: str
    compiled: list[str] = field(default_factory=list)          # component_ids that succeeded
    failed: list[dict[str, str]] = field(default_factory=list) # [{id, name, error}]
    compiled_map: dict[str, ComponentCompileResult] = field(default_factory=dict)
    validation_report: dict[str, Any] = field(default_factory=dict)
    game_context: Optional[GameContext] = None


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class GameCompilationPipeline:
    """Multi-agent pipeline that compiles all components in a project.

    Uses the same AgentRegistry singleton populated by register_game_agents()
    at FastAPI startup. GraphCompiler and SceneCompiler are still used to
    produce cheap deterministic node_summary / initial_properties before the
    LLM calls — reducing token usage and improving reliability.
    """

    def __init__(self) -> None:
        self._graph_compiler = GraphCompiler()
        self._scene_compiler = SceneCompiler()

    # -----------------------------------------------------------------------
    # Public entry point
    # -----------------------------------------------------------------------

    async def run(
        self,
        components: list,          # SQLAlchemy Component ORM rows
        project_id: str,
    ) -> GameCompilationPipelineResult:
        """Execute the full 5-stage pipeline and return a result container.

        Falls back to template compilation per-component if any stage raises
        an unrecoverable exception.
        """
        result = GameCompilationPipelineResult(project_id=project_id)

        try:
            with trace("Game Compilation"):
                # ── Stage 1 ──────────────────────────────────────────────
                game_context = await self._stage1_analyze_game_system(components)
                result.game_context = game_context

                # ── Stage 2 ──────────────────────────────────────────────
                blueprints = await self._stage2_analyze_components_parallel(
                    components, game_context
                )

                # ── Stage 3 ──────────────────────────────────────────────
                scripts = await self._stage3_generate_scripts_parallel(
                    blueprints, game_context
                )

                # ── Stage 4 ──────────────────────────────────────────────
                patched_subs = await self._stage4_resolve_event_subscriptions(
                    blueprints, scripts
                )

                # ── Stage 5 ──────────────────────────────────────────────
                validation = await self._stage5_validate_ruleset(
                    blueprints, scripts, patched_subs, project_id
                )
                result.validation_report = validation

                # ── Assemble final per-component results ──────────────────
                for bp in blueprints:
                    cid = bp.component_id
                    script = scripts.get(cid, "")
                    subs = patched_subs.get(cid, bp.event_subscriptions)
                    props = bp.initial_properties

                    result.compiled_map[cid] = ComponentCompileResult(
                        component_id=cid,
                        kind=bp.inferred_kind or bp.kind,
                        script=script,
                        properties=props,
                        event_subscriptions=subs,
                    )
                    result.compiled.append(cid)

        except Exception as exc:
            logger.error(
                "GameCompilationPipeline failed for project %s: %s",
                project_id, exc, exc_info=True,
            )
            # Fall back to template compilation for all components
            result = self._fallback_template_compile(components, project_id, str(exc))

        return result

    # -----------------------------------------------------------------------
    # Stage 1 — Game System Analysis
    # -----------------------------------------------------------------------

    async def _stage1_analyze_game_system(
        self,
        components: list,
    ) -> GameContext:
        """Run GameSystemAnalyzer to produce a shared GameContext."""
        summaries = self._build_component_summaries_for_llm(components)
        agent = agent_registry.get_agent_or_raise("game_system_analyzer")

        response = await Runner.run(agent, json.dumps(summaries))
        output = response.final_output  # GameContextOutput (Pydantic model)

        relationships = [
            ComponentRelationship(
                source_id=r.source_id,
                target_id=r.target_id,
                relationship_type=r.relationship_type,
                detail=r.detail,
            )
            for r in output.relationships
        ]

        return GameContext(
            game_type=output.game_type,
            game_description=output.game_description,
            component_names=[c["name"] for c in summaries],
            component_kinds=output.component_kinds,
            event_vocabulary=output.event_vocabulary,
            relationships=relationships,
            raw_summaries=output.raw_summaries,
        )

    # -----------------------------------------------------------------------
    # Stage 2 — Component Graph Analysis (parallel)
    # -----------------------------------------------------------------------

    async def _stage2_analyze_components_parallel(
        self,
        components: list,
        game_context: GameContext,
    ) -> list[EnrichedComponentBlueprint]:
        """Run ComponentGraphAnalyzer for all components concurrently."""
        tasks = [
            self._analyze_one_component(component, game_context)
            for component in components
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        blueprints: list[EnrichedComponentBlueprint] = []
        for component, result in zip(components, results):
            if isinstance(result, Exception):
                logger.warning(
                    "ComponentGraphAnalyzer failed for %s (%s): %s",
                    component.Name, component.ComponentId, result,
                )
                # Fall back to a basic blueprint from GraphCompiler
                blueprints.append(self._make_basic_enriched_blueprint(component, game_context))
            else:
                blueprints.append(result)

        return blueprints

    async def _analyze_one_component(
        self,
        component,
        game_context: GameContext,
    ) -> EnrichedComponentBlueprint:
        """Analyse a single component via ComponentGraphAnalyzer."""
        # First build a deterministic baseline blueprint (no LLM)
        base_bp = self._graph_compiler.compile(
            component_id=str(component.ComponentId),
            name=component.Name,
            description=component.Description or "",
            nodes=component.Nodes or [],
            edges=component.Edges or [],
            kind=component.Kind or "object",
        )

        # Merge SceneCompiler properties
        scene_props = self._scene_compiler.compile(
            component.SceneRoot,
            base_bp.kind,
        )
        merged_props = {**base_bp.initial_properties, **scene_props.properties}

        agent = agent_registry.get_agent_or_raise("component_graph_analyzer")
        payload = {
            "component": {
                "id": base_bp.component_id,
                "name": base_bp.component_name,
                "description": base_bp.description,
                "kind": base_bp.kind,
                "node_summary": base_bp.node_summary,
            },
            "game_context": game_context.to_prompt_dict(),
        }

        response = await Runner.run(agent, json.dumps(payload))
        output = response.final_output  # EnrichedBlueprintOutput

        return EnrichedComponentBlueprint(
            component_id=base_bp.component_id,
            component_name=base_bp.component_name,
            description=base_bp.description,
            kind=output.inferred_kind or base_bp.kind,
            needs_on_init=output.needs_on_init,
            needs_on_event=output.needs_on_event,
            needs_on_update=output.needs_on_update,
            event_subscriptions=output.event_subscriptions,
            initial_properties={**merged_props, **output.initial_properties},
            node_summary=base_bp.node_summary,
            inferred_kind=output.inferred_kind or base_bp.kind,
            emitted_events=output.emitted_events,
            referenced_component_names=output.referenced_component_names,
            game_context_snippet=output.game_context_snippet,
        )

    # -----------------------------------------------------------------------
    # Stage 3 — Script Generation (parallel)
    # -----------------------------------------------------------------------

    async def _stage3_generate_scripts_parallel(
        self,
        blueprints: list[EnrichedComponentBlueprint],
        game_context: GameContext,
    ) -> dict[str, str]:
        """Generate Python scripts for all components concurrently."""
        tasks = [
            self._generate_script_one(bp, game_context)
            for bp in blueprints
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scripts: dict[str, str] = {}
        for bp, result in zip(blueprints, results):
            if isinstance(result, Exception):
                logger.warning(
                    "ComponentScriptGenerator failed for %s: %s",
                    bp.component_name, result,
                )
                scripts[bp.component_id] = self._fallback_template_script(bp)
            else:
                scripts[bp.component_id] = result

        return scripts

    async def _generate_script_one(
        self,
        blueprint: EnrichedComponentBlueprint,
        game_context: GameContext,
    ) -> str:
        """Generate a Python script for a single component."""
        agent = agent_registry.get_agent_or_raise("component_script_generator")
        payload = {
            "blueprint": {
                "component_id": blueprint.component_id,
                "component_name": blueprint.component_name,
                "kind": blueprint.inferred_kind or blueprint.kind,
                "description": blueprint.description,
                "needs_on_init": blueprint.needs_on_init,
                "needs_on_event": blueprint.needs_on_event,
                "needs_on_update": blueprint.needs_on_update,
                "event_subscriptions": blueprint.event_subscriptions,
                "emitted_events": blueprint.emitted_events,
                "initial_properties": blueprint.initial_properties,
                "node_summary": blueprint.node_summary,
                "game_context_snippet": blueprint.game_context_snippet,
                "referenced_component_names": blueprint.referenced_component_names,
            },
        }

        response = await Runner.run(agent, json.dumps(payload))
        output = response.final_output  # ScriptOutput

        if not output.syntax_valid:
            logger.warning(
                "ScriptGenerator returned invalid script for %s: %s",
                blueprint.component_name, output.error,
            )

        return output.script

    # -----------------------------------------------------------------------
    # Stage 4 — Event Subscription Resolution
    # -----------------------------------------------------------------------

    async def _stage4_resolve_event_subscriptions(
        self,
        blueprints: list[EnrichedComponentBlueprint],
        scripts: dict[str, str],
    ) -> dict[str, list[str]]:
        """Run EventSubscriptionResolver; return patched subscriptions per component."""
        agent = agent_registry.get_agent_or_raise("event_subscription_resolver")

        payload = [
            {
                "component_id": bp.component_id,
                "event_subscriptions": bp.event_subscriptions,
                "emitted_events": bp.emitted_events,
                "script": scripts.get(bp.component_id, ""),
            }
            for bp in blueprints
        ]

        response = await Runner.run(agent, json.dumps(payload))
        output = response.final_output  # ResolverReportOutput

        if output.errors:
            for err in output.errors:
                logger.error("EventSubscriptionResolver error: %s", err)
        if output.warnings:
            for w in output.warnings:
                logger.warning("EventSubscriptionResolver warning: %s", w)

        return {
            patch.component_id: patch.patched_subscriptions
            for patch in output.patches
        }

    # -----------------------------------------------------------------------
    # Stage 5 — Ruleset Validation
    # -----------------------------------------------------------------------

    async def _stage5_validate_ruleset(
        self,
        blueprints: list[EnrichedComponentBlueprint],
        scripts: dict[str, str],
        patched_subs: dict[str, list[str]],
        project_id: str,
    ) -> dict[str, Any]:
        """Assemble RulesetIR dict, run RulesetValidatorAgent, return report."""
        component_defs = [
            {
                "id": bp.component_id,
                "kind": bp.inferred_kind or bp.kind,
                "name": bp.component_name,
                "description": bp.description,
                "script": scripts.get(bp.component_id),
                "properties": bp.initial_properties,
                "event_subscriptions": patched_subs.get(bp.component_id, bp.event_subscriptions),
            }
            for bp in blueprints
        ]

        ruleset_ir = {
            "version": "2.0",
            "metadata": {"project_id": project_id},
            "component_definitions": component_defs,
        }

        agent = agent_registry.get_agent_or_raise("ruleset_validator_agent")
        response = await Runner.run(agent, json.dumps(ruleset_ir))
        output = response.final_output  # ValidationReportOutput

        return {
            "is_valid": output.is_valid,
            "errors": output.errors,
            "warnings": output.warnings,
        }

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _build_component_summaries_for_llm(self, components: list) -> list[dict]:
        """Build lightweight component summaries for Stage 1.

        Runs GraphCompiler cheaply (no LLM) to get node_summary; strips the
        full nodes/edges blobs to keep the Stage 1 prompt manageable.
        """
        summaries = []
        for comp in components:
            bp = self._graph_compiler.compile(
                component_id=str(comp.ComponentId),
                name=comp.Name,
                description=comp.Description or "",
                nodes=comp.Nodes or [],
                edges=comp.Edges or [],
                kind=comp.Kind or "object",
            )
            summaries.append({
                "id": str(comp.ComponentId),
                "name": comp.Name,
                "description": comp.Description or "",
                "kind": comp.Kind,
                "node_summary": bp.node_summary,
            })
        return summaries

    def _make_basic_enriched_blueprint(
        self,
        component,
        game_context: GameContext,
    ) -> EnrichedComponentBlueprint:
        """Fallback: build an EnrichedComponentBlueprint without the LLM."""
        cid = str(component.ComponentId)
        bp = self._graph_compiler.compile(
            component_id=cid,
            name=component.Name,
            description=component.Description or "",
            nodes=component.Nodes or [],
            edges=component.Edges or [],
            kind=component.Kind or "object",
        )
        scene_props = self._scene_compiler.compile(component.SceneRoot, bp.kind)
        inferred_kind = game_context.component_kinds.get(cid, bp.kind)

        return EnrichedComponentBlueprint(
            component_id=bp.component_id,
            component_name=bp.component_name,
            description=bp.description,
            kind=bp.kind,
            needs_on_init=bp.needs_on_init,
            needs_on_event=bp.needs_on_event,
            needs_on_update=bp.needs_on_update,
            event_subscriptions=bp.event_subscriptions,
            initial_properties={**bp.initial_properties, **scene_props.properties},
            node_summary=bp.node_summary,
            inferred_kind=inferred_kind,
            emitted_events=[],
            referenced_component_names=[],
            game_context_snippet=game_context.raw_summaries.get(cid, ""),
        )

    def _fallback_template_script(self, bp: EnrichedComponentBlueprint) -> str:
        """Generate a template script without LLM as a last-resort fallback."""
        from .script_generator import ScriptGenerator
        gen = ScriptGenerator(llm_client=None)
        return gen.generate(bp)

    def _fallback_template_compile(
        self,
        components: list,
        project_id: str,
        error_reason: str,
    ) -> GameCompilationPipelineResult:
        """Full fallback: compile every component with template mode (no LLM)."""
        from .component_compiler import ComponentCompilerService
        compiler = ComponentCompilerService()
        result = GameCompilationPipelineResult(
            project_id=project_id,
            validation_report={
                "is_valid": False,
                "errors": [f"Pipeline failed, used template fallback: {error_reason}"],
                "warnings": [],
            },
        )
        for component in components:
            try:
                comp_result = compiler.compile_component(component)
                if comp_result.success:
                    cid = str(component.ComponentId)
                    result.compiled.append(cid)
                    result.compiled_map[cid] = ComponentCompileResult(
                        component_id=cid,
                        kind=comp_result.kind,
                        script=comp_result.script,
                        properties=comp_result.properties,
                        event_subscriptions=comp_result.event_subscriptions,
                    )
                else:
                    result.failed.append({
                        "id": str(component.ComponentId),
                        "name": component.Name,
                        "error": comp_result.error or "unknown",
                    })
            except Exception as exc:
                result.failed.append({
                    "id": str(component.ComponentId),
                    "name": component.Name,
                    "error": str(exc),
                })
        return result
