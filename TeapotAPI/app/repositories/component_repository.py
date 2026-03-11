"""
Component repository for data access
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import uuid

from app.models.component import Component
from app.schemas.project import ComponentSave


class ComponentRepository:
    """Data access operations for Component."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_project(self, project_id: str) -> list[Component]:
        result = await self.db.execute(
            select(Component)
            .where(Component.ProjectId == project_id)
            .order_by(Component.SortOrder)
        )
        return list(result.scalars().all())

    async def get_by_id(self, component_id: str) -> Optional[Component]:
        result = await self.db.execute(
            select(Component).where(Component.ComponentId == component_id)
        )
        return result.scalar_one_or_none()

    async def bulk_save_for_project(self, project_id: str, components: list[ComponentSave]) -> list[Component]:
        """Replace the full component list for a project.

        - Components with a matching id are updated in place.
        - Components without an id (or whose id isn't found) are created.
        - Any existing components not present in the incoming list are deleted.
        """
        incoming_ids: set[str] = {c.id for c in components if c.id}

        # Fetch existing components for diffing
        existing_rows = await self.list_by_project(project_id)
        existing_map: dict[str, Component] = {str(c.ComponentId): c for c in existing_rows}

        # Delete components that are no longer in the list
        ids_to_delete = set(existing_map.keys()) - incoming_ids
        if ids_to_delete:
            await self.db.execute(
                delete(Component).where(Component.ComponentId.in_(list(ids_to_delete)))
            )

        saved: list[Component] = []
        for idx, comp_data in enumerate(components):
            comp_id = comp_data.id
            if comp_id and comp_id in existing_map:
                # Update existing
                row = existing_map[comp_id]
                row.Name = comp_data.name
                row.Description = comp_data.description
                row.SortOrder = idx
                row.Nodes = comp_data.nodes
                row.Edges = comp_data.edges
                row.SceneRoot = comp_data.scene_root
                saved.append(row)
            else:
                # Insert new
                # If the frontend sends a non-UUID temporary id (e.g. "card", "comp-123"),
                # fall back to generating a fresh UUID instead of raising.
                if comp_id:
                    try:
                        new_id = uuid.UUID(comp_id)
                    except ValueError:
                        new_id = uuid.uuid4()
                else:
                    new_id = uuid.uuid4()

                row = Component(
                    ComponentId=new_id,
                    ProjectId=project_id,
                    Name=comp_data.name,
                    Description=comp_data.description,
                    SortOrder=idx,
                    Nodes=comp_data.nodes,
                    Edges=comp_data.edges,
                    SceneRoot=comp_data.scene_root,
                )
                self.db.add(row)
                saved.append(row)

        await self.db.commit()
        for row in saved:
            await self.db.refresh(row)
        return saved
