"""
ChatVote model

Model for chat votes.
"""

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship

from .base import Base


class ChatVote(Base):
    """Model for chat votes"""
    __tablename__ = "chat_votes"
    
    id = Column(String, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("published_chats.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    vote_type = Column(String(10), default="upvote", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    chat = relationship("PublishedChat", back_populates="votes")
    
    __table_args__ = (
        Index("idx_chat_user_vote", "chat_id", "user_id", unique=True),
    )








