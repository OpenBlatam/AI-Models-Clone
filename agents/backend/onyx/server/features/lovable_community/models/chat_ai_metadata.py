"""
ChatAIMetadata model

Model for storing AI analysis metadata (sentiment, moderation, etc.).
"""

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Index, JSON, Float, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class ChatAIMetadata(Base):
    """Model for storing AI analysis metadata"""
    __tablename__ = "chat_ai_metadata"
    
    id = Column(String, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("published_chats.id"), nullable=False, unique=True, index=True)
    
    # Sentiment Analysis
    sentiment_label = Column(String(50), nullable=True)  # positive, negative, neutral
    sentiment_score = Column(Float, nullable=True)  # Confidence score
    
    # Content Moderation
    toxicity_score = Column(Float, nullable=True)
    is_toxic = Column(Boolean, default=False, nullable=False)
    moderation_flags = Column(JSON, nullable=True)  # List of moderation flags
    
    # Text Quality
    readability_score = Column(Float, nullable=True)
    text_quality_score = Column(Float, nullable=True)
    
    # Metadata
    ai_analysis_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    chat = relationship("PublishedChat", backref="ai_metadata")
    
    __table_args__ = (
        Index("idx_chat_ai", "chat_id"),
        Index("idx_toxicity", "is_toxic", "toxicity_score"),
        Index("idx_sentiment", "sentiment_label", "sentiment_score"),
    )

