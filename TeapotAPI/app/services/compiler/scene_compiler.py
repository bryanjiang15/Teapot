"""
SceneCompiler — derives initial properties and container structure
from a component's SceneRoot JSON.

The SceneRoot is the spatial / hierarchical layout saved by the
frontend scene editor. SceneCompiler extracts:
  - visibility rules for CONTAINER components
  - child relationships (which objects start inside which containers)
  - any static positional / layout properties
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SceneProperties:
    """Properties and child definitions extracted from a SceneRoot.

    Attributes
    ----------
    properties : dict
        Key/value properties to seed on the component instance.
    child_definition_names : list[str]
        Names of component definitions that start as children of
        this component's container instance.
    """
    properties: dict[str, Any] = field(default_factory=dict)
    child_definition_names: list[str] = field(default_factory=list)


class SceneCompiler:
    """Extracts static properties and child relationships from a SceneRoot."""

    def compile(
        self,
        scene_root: Optional[dict[str, Any]],
        kind: str,
    ) -> SceneProperties:
        """Process a component's SceneRoot JSON.

        Parameters
        ----------
        scene_root : dict | None
            The SceneRoot value stored in the Component DB row.
        kind : str
            ComponentKind.value for this component.

        Returns
        -------
        SceneProperties
        """
        if not scene_root:
            return SceneProperties()

        properties: dict[str, Any] = {}
        child_names: list[str] = []

        # Extract common scene properties
        if "visibility" in scene_root:
            properties["visibility"] = scene_root["visibility"]

        if "maxSize" in scene_root:
            properties["max_size"] = scene_root["maxSize"]

        if "position" in scene_root:
            pos = scene_root["position"]
            if isinstance(pos, dict):
                properties["position_x"] = pos.get("x", 0)
                properties["position_y"] = pos.get("y", 0)

        if "size" in scene_root:
            size = scene_root["size"]
            if isinstance(size, dict):
                properties["width"] = size.get("width")
                properties["height"] = size.get("height")

        # Extract static properties blob if present
        for prop_key, prop_val in (scene_root.get("properties") or {}).items():
            properties[prop_key] = prop_val

        # CONTAINER: extract initial children
        if kind == "container":
            for child in scene_root.get("children") or []:
                child_name = (
                    child.get("componentName")
                    or child.get("name")
                    or child.get("type")
                )
                if child_name:
                    child_names.append(child_name)

        return SceneProperties(
            properties=properties,
            child_definition_names=child_names,
        )
