"""
User model for authentication and user management
"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    UserId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Email = Column(String(255), unique=True, nullable=False, index=True)
    PasswordHash = Column(String(255), nullable=False)
    IsActive = Column(Boolean, default=True)
    DateCreated = Column(DateTime(timezone=True), server_default=func.now())
    DateUpdated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(UserId={self.UserId}, Email={self.Email})>"
