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
from app.schemas.ruleset import RulesetIRResponse, ScriptedComponentResponse
from app.services.compiler.component_compiler import ComponentCompilerService
from app.services.compiler.game_compilation_pipeline import GameCompilationPipeline

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


@router.post("/{project_id}/compile", status_code=status.HTTP_200_OK)
async def compile_project(
    project_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Compile all components in the project.

    Runs the full compilation pipeline (graph → blueprint → AI script) for
    every component in the project and persists the results to the DB.

    Returns a summary of which components compiled successfully and which failed.
    """
    _validate_project_id_or_404(project_id)
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _assert_owner(project, current_user_id)

    comp_repo = ComponentRepository(db)
    components = await comp_repo.list_by_project(project_id)

    pipeline = GameCompilationPipeline()
    pipeline_result = await pipeline.run(components, project_id)

    for component in components:
        cid = str(component.ComponentId)
        comp_result = pipeline_result.compiled_map.get(cid)
        if comp_result:
            component.Kind = comp_result.kind
            component.Script = comp_result.script
            component.Properties = comp_result.properties
            component.EventSubscriptions = comp_result.event_subscriptions

    await db.commit()
    return {
        "project_id": project_id,
        "compiled_count": len(pipeline_result.compiled),
        "failed_count": len(pipeline_result.failed),
        "compiled": pipeline_result.compiled,
        "failed": pipeline_result.failed,
    }


@router.get("/{project_id}/ruleset", response_model=RulesetIRResponse)
async def get_project_ruleset(
    project_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Return the compiled RulesetIR for the project.

    Serves pre-compiled component definitions to TeapotEngine's RulesetLoader.
    Components that have not yet been compiled (Script is None and Kind is None)
    are omitted from the response.
    """
    _validate_project_id_or_404(project_id)
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    _assert_owner(project, current_user_id)

    comp_repo = ComponentRepository(db)
    components = await comp_repo.list_by_project(project_id)

    component_defs: list[ScriptedComponentResponse] = []
    for comp in components:
        if not comp.Kind:
            continue  # not yet compiled
        component_defs.append(ScriptedComponentResponse(
            id=str(comp.ComponentId),
            kind=comp.Kind,
            name=comp.Name,
            description=comp.Description,
            script=comp.Script,
            properties=comp.Properties or {},
            event_subscriptions=comp.EventSubscriptions or [],
        ))

    return RulesetIRResponse(
        version="2.0",
        metadata={"project_id": project_id, "project_name": project.Name},
        component_definitions=component_defs,
        constants={},
    )


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
