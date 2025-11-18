"""
ChatRemix model

Model for chat remixes.
"""

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship

from .base import Base


class ChatRemix(Base):
    """Model for chat remixes"""
    __tablename__ = "chat_remixes"
    
    id = Column(String, primary_key=True, index=True)
    original_chat_id = Column(String, ForeignKey("published_chats.id"), nullable=False, index=True)
    remix_chat_id = Column(String, ForeignKey("published_chats.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    original_chat = relationship("PublishedChat", foreign_keys=[original_chat_id], back_populates="remixes")
    remix_chat = relationship("PublishedChat", foreign_keys=[remix_chat_id])
    
    __table_args__ = (
        Index("idx_original_remix", "original_chat_id", "remix_chat_id"),
        Index("idx_user_remix", "user_id", "created_at"),
    )








