"""
Component — runtime instances of ScriptedComponent definitions.

Unlike the old engine, Component instances carry no workflow, no
resource definitions, and no trigger objects. All logic lives in
the script attached to the definition.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from TeapotEngine.ruleset.ScriptedComponent import ComponentKind


class ComponentStatus(Enum):
    ACTIVE    = "active"
    INACTIVE  = "inactive"
    DESTROYED = "destroyed"


class ComponentInstance(BaseModel):
    """A live runtime instance of a ScriptedComponent definition.

    Fields
    ------
    id : str
        Unique runtime UUID for this instance (not the definition id).
    definition_id : str
        The ScriptedComponent.id this instance was created from.
    kind : ComponentKind
        Copied from the definition for fast lookup.
    name : str
        Copied from the definition (may be overridden at instantiation).
    owner_id : str | None
        The instance id of the PLAYER or GAME component that "owns" this
        object.  None for the GAME component itself.
    container_id : str | None
        The instance id of the CONTAINER currently holding this object.
        None if the object is not in any container.
    status : ComponentStatus
        ACTIVE / INACTIVE / DESTROYED.
    """
    id: str
    definition_id: str
    kind: ComponentKind
    name: str
    owner_id: Optional[str] = None
    container_id: Optional[str] = None
    status: ComponentStatus = ComponentStatus.ACTIVE

    def is_active(self) -> bool:
        return self.status == ComponentStatus.ACTIVE


class ComponentManager(BaseModel):
    """In-memory registry of all live ComponentInstance objects.

    Keeps secondary indices for O(1) lookup by kind and by container.
    """
    instances: dict[str, ComponentInstance] = Field(default_factory=dict)
    by_kind: dict[str, list[str]] = Field(default_factory=dict)   # kind.value → [instance_ids]
    by_container: dict[str, list[str]] = Field(default_factory=dict)  # container_id → [instance_ids]
    by_owner: dict[str, list[str]] = Field(default_factory=dict)  # owner_id → [instance_ids]

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add(self, instance: ComponentInstance) -> None:
        """Register a new instance and update all indices."""
        self.instances[instance.id] = instance
        self._index(instance)

    def get(self, instance_id: str) -> Optional[ComponentInstance]:
        return self.instances.get(instance_id)

    def remove(self, instance_id: str) -> Optional[ComponentInstance]:
        """Remove an instance and clean up all indices. Returns the removed instance."""
        instance = self.instances.pop(instance_id, None)
        if instance:
            self._unindex(instance)
        return instance

    def all(self) -> list[ComponentInstance]:
        return list(self.instances.values())

    def count(self) -> int:
        return len(self.instances)

    # ------------------------------------------------------------------
    # Indexed queries
    # ------------------------------------------------------------------

    def by_kind_query(self, kind: ComponentKind) -> list[ComponentInstance]:
        ids = self.by_kind.get(kind.value, [])
        return [self.instances[i] for i in ids if i in self.instances]

    def by_container_query(self, container_id: str) -> list[ComponentInstance]:
        ids = self.by_container.get(container_id, [])
        return [self.instances[i] for i in ids if i in self.instances]

    def by_owner_query(self, owner_id: str) -> list[ComponentInstance]:
        ids = self.by_owner.get(owner_id, [])
        return [self.instances[i] for i in ids if i in self.instances]

    # ------------------------------------------------------------------
    # Container / owner movement
    # ------------------------------------------------------------------

    def move_to_container(
        self,
        instance_id: str,
        new_container_id: Optional[str],
    ) -> bool:
        instance = self.get(instance_id)
        if not instance:
            return False

        old = instance.container_id
        if old and old in self.by_container:
            self.by_container[old] = [i for i in self.by_container[old] if i != instance_id]

        instance.container_id = new_container_id
        if new_container_id is not None:
            self.by_container.setdefault(new_container_id, [])
            if instance_id not in self.by_container[new_container_id]:
                self.by_container[new_container_id].append(instance_id)
        return True

    def set_owner(self, instance_id: str, new_owner_id: Optional[str]) -> bool:
        instance = self.get(instance_id)
        if not instance:
            return False

        old = instance.owner_id
        if old and old in self.by_owner:
            self.by_owner[old] = [i for i in self.by_owner[old] if i != instance_id]

        instance.owner_id = new_owner_id
        if new_owner_id is not None:
            self.by_owner.setdefault(new_owner_id, [])
            if instance_id not in self.by_owner[new_owner_id]:
                self.by_owner[new_owner_id].append(instance_id)
        return True

    # ------------------------------------------------------------------
    # Index helpers
    # ------------------------------------------------------------------

    def _index(self, instance: ComponentInstance) -> None:
        kind_key = instance.kind.value
        self.by_kind.setdefault(kind_key, [])
        if instance.id not in self.by_kind[kind_key]:
            self.by_kind[kind_key].append(instance.id)

        if instance.container_id:
            self.by_container.setdefault(instance.container_id, [])
            if instance.id not in self.by_container[instance.container_id]:
                self.by_container[instance.container_id].append(instance.id)

        if instance.owner_id:
            self.by_owner.setdefault(instance.owner_id, [])
            if instance.id not in self.by_owner[instance.owner_id]:
                self.by_owner[instance.owner_id].append(instance.id)

    def _unindex(self, instance: ComponentInstance) -> None:
        kind_key = instance.kind.value
        if kind_key in self.by_kind:
            self.by_kind[kind_key] = [i for i in self.by_kind[kind_key] if i != instance.id]

        if instance.container_id and instance.container_id in self.by_container:
            self.by_container[instance.container_id] = [
                i for i in self.by_container[instance.container_id] if i != instance.id
            ]

        if instance.owner_id and instance.owner_id in self.by_owner:
            self.by_owner[instance.owner_id] = [
                i for i in self.by_owner[instance.owner_id] if i != instance.id
            ]
