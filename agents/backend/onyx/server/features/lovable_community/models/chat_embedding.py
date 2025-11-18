"""
ChatEmbedding model

Model for storing chat embeddings for semantic search.
"""

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Index, JSON
from sqlalchemy.orm import relationship

from .base import Base


class ChatEmbedding(Base):
    """Model for storing chat embeddings for semantic search"""
    __tablename__ = "chat_embeddings"
    
    id = Column(String, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("published_chats.id"), nullable=False, unique=True, index=True)
    embedding = Column(JSON, nullable=False)  # Stores embedding vector as JSON
    embedding_model = Column(String(200), nullable=False)  # Model used to generate embedding
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    chat = relationship("PublishedChat", backref="embedding")
    
    __table_args__ = (
        Index("idx_chat_embedding", "chat_id"),
    )








