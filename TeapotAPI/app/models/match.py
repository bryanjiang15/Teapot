"""
Match model for game sessions
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Match(Base):
    """Match model"""
    __tablename__ = "matches"
    
    MatchId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    RulesetId = Column(UUID(as_uuid=True), ForeignKey("rulesets.RulesetId"), nullable=False)
    Status = Column(String(50), default="lobby", nullable=False)
    DateCreated = Column(DateTime(timezone=True), server_default=func.now())
    DateStarted = Column(DateTime(timezone=True), nullable=True)
    EndedAt = Column(DateTime(timezone=True), nullable=True)
    
    # JSON fields for game state
    Players = Column(JSONB, nullable=False)
    GameState = Column(JSONB, nullable=True)
    
    def __repr__(self):
        return f"<Match(MatchId={self.MatchId}, Status={self.Status})>"


class MatchEvent(Base):
    """Match event for event sourcing"""
    __tablename__ = "match_events"
    
    MatchEventId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    MatchId = Column(UUID(as_uuid=True), ForeignKey("matches.MatchId"), nullable=False)
    Version = Column(Integer, nullable=False)
    Step = Column(Integer, nullable=False)
    EventType = Column(String(100), nullable=False)
    EventData = Column(JSONB, nullable=False)
    DateCreated = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<MatchEvent(MatchEventId={self.MatchEventId}, MatchId={self.MatchId}, Type={self.EventType})>"
