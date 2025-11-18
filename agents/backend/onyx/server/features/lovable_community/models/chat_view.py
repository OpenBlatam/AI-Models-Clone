"""
ChatView model

Model for chat views/visualizations.
"""

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship

from .base import Base


class ChatView(Base):
    """Model for chat views"""
    __tablename__ = "chat_views"
    
    id = Column(String, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("published_chats.id"), nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    chat = relationship("PublishedChat", back_populates="views")
    
    __table_args__ = (
        Index("idx_chat_created", "chat_id", "created_at"),
    )








