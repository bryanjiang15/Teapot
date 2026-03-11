"""
Project and Component schemas for request/response validation.
Node, Edge, and SceneRoot are stored as arbitrary JSON — typed as Any
so the backend stays agnostic to frontend schema changes.
"""
from pydantic import BaseModel, ConfigDict
from typing import Any, Optional
from datetime import datetime
import uuid


# ---------------------------------------------------------------------------
# Component schemas
# ---------------------------------------------------------------------------

class ComponentCreate(BaseModel):
    """Schema for creating a new component."""
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    nodes: list[Any] = []
    edges: list[Any] = []
    scene_root: Optional[Any] = None


class ComponentSave(BaseModel):
    """Schema used when bulk-saving components for a project.
    id is optional — omit to create, supply to update an existing component.
    """
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    nodes: list[Any] = []
    edges: list[Any] = []
    scene_root: Optional[Any] = None


class ComponentResponse(BaseModel):
    """Schema returned for a component."""
    id: str
    project_id: str
    name: str
    description: Optional[str]
    sort_order: int
    nodes: list[Any]
    edges: list[Any]
    scene_root: Optional[Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def model_validate(cls, obj):
        if hasattr(obj, "ComponentId"):
            return cls(
                id=str(obj.ComponentId),
                project_id=str(obj.ProjectId),
                name=obj.Name,
                description=obj.Description,
                sort_order=obj.SortOrder,
                nodes=obj.Nodes or [],
                edges=obj.Edges or [],
                scene_root=obj.SceneRoot,
                created_at=obj.DateCreated,
                updated_at=obj.DateUpdated,
            )
        return super().model_validate(obj)


# ---------------------------------------------------------------------------
# Project schemas
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str
    description: Optional[str] = None
    status: str = "draft"


class ProjectUpdate(BaseModel):
    """Schema for updating project metadata (all fields optional)."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema returned for a project (without components)."""
    id: str
    owner_id: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def model_validate(cls, obj):
        if hasattr(obj, "ProjectId"):
            return cls(
                id=str(obj.ProjectId),
                owner_id=str(obj.OwnerId),
                name=obj.Name,
                description=obj.Description,
                status=obj.Status,
                created_at=obj.DateCreated,
                updated_at=obj.DateUpdated,
            )
        return super().model_validate(obj)


class ProjectWithComponentsResponse(ProjectResponse):
    """Schema returned for a project including its full component list."""
    components: list[ComponentResponse] = []

    @classmethod
    def model_validate(cls, obj):
        if hasattr(obj, "ProjectId"):
            return cls(
                id=str(obj.ProjectId),
                owner_id=str(obj.OwnerId),
                name=obj.Name,
                description=obj.Description,
                status=obj.Status,
                created_at=obj.DateCreated,
                updated_at=obj.DateUpdated,
                components=[ComponentResponse.model_validate(c) for c in (obj.components or [])],
            )
        return super().model_validate(obj)


# ---------------------------------------------------------------------------
# Bulk-save request
# ---------------------------------------------------------------------------

class SaveProjectComponentsRequest(BaseModel):
    """Request body for PUT /projects/{id}/components."""
    components: list[ComponentSave]
