"""
Component model — belongs to a Project; stores node graph and scene as JSONB
so frontend schema changes require no DB migrations.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Component(Base):
    """Component model"""
    __tablename__ = "components"

    ComponentId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ProjectId = Column(UUID(as_uuid=True), ForeignKey("projects.ProjectId"), nullable=False, index=True)
    Name = Column(String(255), nullable=False)
    Description = Column(String(1000), nullable=True)
    SortOrder = Column(Integer, nullable=False, default=0)
    # Stored as-is from the frontend; opaque JSONB so schema can evolve freely.
    Nodes = Column(JSONB, nullable=False, default=list)
    Edges = Column(JSONB, nullable=False, default=list)
    SceneRoot = Column(JSONB, nullable=True)
    DateCreated = Column(DateTime(timezone=True), server_default=func.now())
    DateUpdated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="components")

    def __repr__(self):
        return f"<Component(ComponentId={self.ComponentId}, Name={self.Name}, ProjectId={self.ProjectId})>"
