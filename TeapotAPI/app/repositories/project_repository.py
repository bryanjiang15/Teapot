"""
Project repository for data access
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.project import Project


class ProjectRepository:
    """Data access operations for Project."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, owner_id: str, name: str, description: Optional[str], status: str) -> Project:
        project = Project(OwnerId=owner_id, Name=name, Description=description, Status=status)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        result = await self.db.execute(
            select(Project).where(Project.ProjectId == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_components(self, project_id: str) -> Optional[Project]:
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.components))
            .where(Project.ProjectId == project_id)
        )
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id: str) -> list[Project]:
        result = await self.db.execute(
            select(Project).where(Project.OwnerId == owner_id).order_by(Project.DateCreated.desc())
        )
        return list(result.scalars().all())

    async def update(self, project: Project, **fields) -> Project:
        for key, value in fields.items():
            if value is not None:
                setattr(project, key, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.db.delete(project)
        await self.db.commit()
