"""
PublishedChat model

Model for chats published in the community.
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship

from .base import Base


class PublishedChat(Base):
    """Model for chats published in the community"""
    __tablename__ = "published_chats"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    chat_content = Column(Text, nullable=False)
    tags = Column(String(500), nullable=True)
    
    vote_count = Column(Integer, default=0, nullable=False)
    remix_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    
    score = Column(Float, default=0.0, nullable=False, index=True)
    
    is_public = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    original_chat_id = Column(String, ForeignKey("published_chats.id"), nullable=True)
    
    remixes = relationship("ChatRemix", foreign_keys="ChatRemix.original_chat_id", back_populates="original_chat")
    votes = relationship("ChatVote", back_populates="chat")
    views = relationship("ChatView", back_populates="chat")
    
    __table_args__ = (
        Index("idx_score_created", "score", "created_at"),
        Index("idx_user_created", "user_id", "created_at"),
        Index("idx_public_featured", "is_public", "is_featured"),
        Index("idx_tags", "tags"),
        Index("idx_original_chat", "original_chat_id"),
        Index("idx_public_score", "is_public", "score", "created_at"),
        Index("idx_user_public", "user_id", "is_public", "score"),
    )
    
    def get_tags_list(self) -> list[str]:
        """
        Get tags as a list (cached for performance).
        
        The cache is automatically invalidated when tags are updated.
        
        Returns:
            List of tags or empty list
        """
        cache_key = '_tags_list_cache'
        cache_tag_value = '_tags_cache_value'
        
        if not hasattr(self, cache_key) or getattr(self, cache_tag_value, None) != self.tags:
            if self.tags:
                tags_list = [
                    tag.strip() for tag in self.tags.split(",") if tag.strip()
                ]
            else:
                tags_list = []
            setattr(self, cache_key, tags_list)
            setattr(self, cache_tag_value, self.tags)
        return getattr(self, cache_key)



