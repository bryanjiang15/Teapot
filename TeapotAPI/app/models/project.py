"""
Project model
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Project(Base):
    """Project model"""
    __tablename__ = "projects"

    ProjectId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    OwnerId = Column(UUID(as_uuid=True), ForeignKey("users.UserId"), nullable=False, index=True)
    Name = Column(String(255), nullable=False)
    Description = Column(String(1000), nullable=True)
    Status = Column(String(50), nullable=False, default="draft")  # 'draft', 'development', 'published'
    DateCreated = Column(DateTime(timezone=True), server_default=func.now())
    DateUpdated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    components = relationship("Component", back_populates="project", cascade="all, delete-orphan", order_by="Component.SortOrder")

    def __repr__(self):
        return f"<Project(ProjectId={self.ProjectId}, Name={self.Name})>"
