"""
Card model for TCG cards
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Card(Base):
    """Card model"""
    __tablename__ = "cards"
    
    CardId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    RulesetId = Column(UUID(as_uuid=True), ForeignKey("rulesets.RulesetId"), nullable=False)
    Name = Column(String(255), nullable=False)
    Cost = Column(Integer, nullable=False)
    Stats = Column(JSONB, nullable=False)  # {"attack": 3, "health": 2}
    Keywords = Column(JSONB, nullable=True)  # ["demon", "flying"]
    Text = Column(String(1000), nullable=True)
    Abilities = Column(JSONB, nullable=True)  # [{"id": "a1", "trigger": "ON_PLAY", "python": "..."}]
    Art = Column(JSONB, nullable=True)  # {"imageUrl": "...", "artist": "..."}
    Version = Column(Integer, default=1)
    DateCreated = Column(DateTime(timezone=True), server_default=func.now())
    DateUpdated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Card(CardId={self.CardId}, Name={self.Name}, Cost={self.Cost})>"
