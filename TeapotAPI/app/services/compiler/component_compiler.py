"""
ComponentCompilerService — orchestrates the full compilation pipeline
for a single Component DB row.

Pipeline
--------
1. GraphCompiler:  Nodes + Edges + description → ComponentBlueprint
2. SceneCompiler:  SceneRoot → SceneProperties (merges into blueprint.initial_properties)
3. ScriptGenerator: ComponentBlueprint → validated lifecycle Python script
4. Persist:        Kind, Script, Properties, EventSubscriptions saved back to DB row
"""
from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .graph_compiler import GraphCompiler, ComponentBlueprint
from .scene_compiler import SceneCompiler
from .script_generator import ScriptGenerator, ScriptGenerationError

if TYPE_CHECKING:
    from app.models.component import Component


class CompilationResult:
    """Result of compiling one component."""

    def __init__(
        self,
        component_id: str,
        success: bool,
        kind: Optional[str] = None,
        script: Optional[str] = None,
        properties: Optional[dict[str, Any]] = None,
        event_subscriptions: Optional[list[str]] = None,
        error: Optional[str] = None,
    ):
        self.component_id = component_id
        self.success = success
        self.kind = kind
        self.script = script
        self.properties = properties or {}
        self.event_subscriptions = event_subscriptions or []
        self.error = error

    def __repr__(self) -> str:
        status = "OK" if self.success else f"ERROR: {self.error}"
        return f"<CompilationResult {self.component_id} {status}>"


class ComponentCompilerService:
    """Compiles one Component DB row through the full pipeline.

    Parameters
    ----------
    script_generator : ScriptGenerator | None
        If None, a default ScriptGenerator (template mode) is used.
    """

    def __init__(self, script_generator: Optional[ScriptGenerator] = None):
        self._graph_compiler = GraphCompiler()
        self._scene_compiler = SceneCompiler()
        self._script_generator = script_generator or ScriptGenerator()

    def compile_component(self, component: "Component") -> CompilationResult:
        """Run the full compilation pipeline for a single component.

        Parameters
        ----------
        component : Component
            The SQLAlchemy Component ORM row.

        Returns
        -------
        CompilationResult
            Always returns a result — check .success and .error.
        """
        comp_id = str(component.ComponentId)

        # Determine kind — use existing Kind if already set, otherwise "object"
        kind: str = (component.Kind or "object").lower()
        if kind not in ("game", "player", "object", "container"):
            kind = "object"

        try:
            # Step 1: graph → blueprint
            blueprint: ComponentBlueprint = self._graph_compiler.compile(
                component_id=comp_id,
                name=component.Name,
                description=component.Description,
                nodes=list(component.Nodes or []),
                edges=list(component.Edges or []),
                kind=kind,
            )

            # Step 2: scene → extra properties
            scene_props = self._scene_compiler.compile(
                scene_root=component.SceneRoot,
                kind=kind,
            )
            # Merge scene properties into blueprint (scene wins over graph for shared keys)
            blueprint.initial_properties.update(scene_props.properties)

            # Step 3: generate script
            script: Optional[str] = None
            if blueprint.needs_on_init or blueprint.needs_on_event or blueprint.needs_on_update:
                script = self._script_generator.generate(blueprint)

            return CompilationResult(
                component_id=comp_id,
                success=True,
                kind=kind,
                script=script,
                properties=blueprint.initial_properties,
                event_subscriptions=blueprint.event_subscriptions,
            )

        except ScriptGenerationError as exc:
            return CompilationResult(
                component_id=comp_id,
                success=False,
                error=f"Script generation failed: {exc}",
            )
        except Exception as exc:
            return CompilationResult(
                component_id=comp_id,
                success=False,
                error=f"Unexpected error: {exc}",
            )
