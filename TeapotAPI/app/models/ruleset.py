"""
Ruleset model for game rules
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Ruleset(Base):
    """Ruleset model"""
    __tablename__ = "rulesets"
    
    RulesetId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    OwnerId = Column(UUID(as_uuid=True), ForeignKey("users.UserId"), nullable=False)
    Name = Column(String(255), nullable=False)
    Version = Column(String(50), nullable=False)
    Schema = Column(JSONB, nullable=False)
    Status = Column(String(50), default="draft", nullable=False)
    DateCreated = Column(DateTime(timezone=True), server_default=func.now())
    DateUpdated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Ruleset(RulesetId={self.RulesetId}, Name={self.Name}, Version={self.Version})>"
