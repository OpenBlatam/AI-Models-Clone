"""
Key Messages models for Onyx.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    """Types of messages that can be generated."""
    MARKETING = "marketing"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    INFORMATIONAL = "informational"
    CALL_TO_ACTION = "call_to_action"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    WEBSITE = "website"

class MessageTone(str, Enum):
    """Tones for message generation."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    ENTHUSIASTIC = "enthusiastic"
    URGENT = "urgent"
    CALM = "calm"

class KeyMessageRequest(BaseModel):
    """Request model for key message generation."""
    message: str = Field(..., min_length=1, max_length=10000, description="The original message to process")
    message_type: MessageType = Field(MessageType.INFORMATIONAL, description="Type of message to generate")
    tone: MessageTone = Field(MessageTone.PROFESSIONAL, description="Tone for the generated message")
    target_audience: Optional[str] = Field(None, description="Target audience description")
    context: Optional[str] = Field(None, description="Additional context for message generation")
    keywords: List[str] = Field(default_factory=list, description="Keywords to include in the message")
    max_length: Optional[int] = Field(None, description="Maximum length for the generated message")
    brand_voice: Optional[Dict[str, Any]] = Field(None, description="Brand voice settings")
    industry: Optional[str] = Field(None, description="Industry context")
    call_to_action: Optional[str] = Field(None, description="Specific call to action")

class GeneratedResponse(BaseModel):
    """Response model for generated content."""
    id: str = Field(..., description="Unique identifier for the response")
    original_message: str = Field(..., description="Original input message")
    response: str = Field(..., description="Generated response")
    message_type: MessageType = Field(..., description="Type of generated message")
    tone: MessageTone = Field(..., description="Tone used in generation")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    word_count: int = Field(..., description="Number of words in response")
    character_count: int = Field(..., description="Number of characters in response")
    keywords_used: List[str] = Field(default_factory=list, description="Keywords successfully used")
    sentiment_score: Optional[float] = Field(None, description="Sentiment analysis score")
    readability_score: Optional[float] = Field(None, description="Readability score")
    processing_time: float = Field(..., description="Time taken to generate response")
    suggestions: List[str] = Field(default_factory=list, description="Additional suggestions")

class KeyMessageResponse(BaseModel):
    """Main response model for key message operations."""
    success: bool = Field(..., description="Operation success status")
    data: Optional[GeneratedResponse] = Field(None, description="Generated response data")
    error: Optional[str] = Field(None, description="Error message if any")
    processing_time: float = Field(..., description="Total processing time")
    suggestions: List[str] = Field(default_factory=list, description="Additional suggestions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class MessageAnalysis(BaseModel):
    """Analysis results for a message."""
    sentiment: str = Field(..., description="Sentiment analysis result")
    tone_consistency: float = Field(..., description="Tone consistency score")
    clarity_score: float = Field(..., description="Message clarity score")
    engagement_potential: float = Field(..., description="Engagement potential score")
    keyword_optimization: float = Field(..., description="Keyword optimization score")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")

class BatchKeyMessageRequest(BaseModel):
    """Request model for batch key message generation."""
    messages: List[KeyMessageRequest] = Field(..., description="List of messages to process")
    batch_size: Optional[int] = Field(10, description="Maximum batch size for processing")

class BatchKeyMessageResponse(BaseModel):
    """Response model for batch operations."""
    success: bool = Field(..., description="Overall operation success")
    results: List[KeyMessageResponse] = Field(..., description="Individual results")
    total_processed: int = Field(..., description="Total messages processed")
    failed_count: int = Field(..., description="Number of failed operations")
    processing_time: float = Field(..., description="Total processing time") 