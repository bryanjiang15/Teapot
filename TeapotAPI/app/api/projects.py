"""
Project API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.api.auth import get_current_user_id
from app.repositories.project_repository import ProjectRepository
from app.repositories.component_repository import ComponentRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithComponentsResponse,
    ComponentResponse,
    SaveProjectComponentsRequest,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def _assert_owner(project, current_user_id: str):
    """Raise 403 if the project does not belong to the current user."""
    if str(project.OwnerId) != str(current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def _validate_project_id_or_404(project_id: str) -> None:
    """Ensure project_id is a valid UUID string; otherwise return 404.

    This avoids leaking low-level asyncpg UUID errors when the frontend
    still uses temporary numeric ids (e.g. \"1\") for mock projects.
    """
    try:
        uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all projects owned by the current user."""
    repo = ProjectRepository(db)
    projects = await repo.list_by_owner(current_user_id)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project."""
    repo = ProjectRepository(db)
    project = await repo.create(
        owner_id=current_user_id,
        name=body.name,
        description=body.description,
        status=body.status,
    )
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a single project by ID."""
    _validate_project_id_or_404(project_id)
    repo = ProjectRepository(db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _assert_owner(project, current_user_id)
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    body: ProjectUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update project metadata (name, description, status)."""
    _validate_project_id_or_404(project_id)
    repo = ProjectRepository(db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _assert_owner(project, current_user_id)
    project = await repo.update(
        project,
        Name=body.name,
        Description=body.description,
        Status=body.status,
    )
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a project and all its components."""
    _validate_project_id_or_404(project_id)
    repo = ProjectRepository(db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _assert_owner(project, current_user_id)
    await repo.delete(project)


# ---------------------------------------------------------------------------
# Component load / save
# ---------------------------------------------------------------------------

@router.get("/{project_id}/components", response_model=ProjectWithComponentsResponse)
async def get_project_with_components(
    project_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Return a project together with all its components (nodes, edges, scene)."""
    _validate_project_id_or_404(project_id)
    repo = ProjectRepository(db)
    project = await repo.get_by_id_with_components(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _assert_owner(project, current_user_id)
    return ProjectWithComponentsResponse.model_validate(project)


@router.put("/{project_id}/components", response_model=ProjectWithComponentsResponse)
async def save_project_components(
    project_id: str,
    body: SaveProjectComponentsRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Bulk-save (upsert + delete) all components for a project.

    The full component list from the frontend replaces what is in the database:
    - Components with a matching id are updated.
    - Components without an id are created.
    - Components previously in the DB but absent from the request are deleted.
    """
    _validate_project_id_or_404(project_id)
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _assert_owner(project, current_user_id)

    comp_repo = ComponentRepository(db)
    saved_components = await comp_repo.bulk_save_for_project(project_id, body.components)

    # Re-fetch the project with freshly saved components for the response
    project = await project_repo.get_by_id_with_components(project_id)
    return ProjectWithComponentsResponse.model_validate(project)
