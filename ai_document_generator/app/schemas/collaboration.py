"""
Collaboration schemas for API validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import uuid

from app.models.collaboration import CollaborationStatus, CollaborationRole


class CollaborationBase(BaseModel):
    """Base collaboration schema with common fields."""
    role: CollaborationRole
    permissions: Dict[str, Any] = Field(default_factory=dict)


class CollaborationCreate(CollaborationBase):
    """Schema for creating collaboration."""
    pass


class CollaborationUpdate(BaseModel):
    """Schema for updating collaboration."""
    role: Optional[CollaborationRole] = None
    permissions: Optional[Dict[str, Any]] = None
    status: Optional[CollaborationStatus] = None


class Collaboration(CollaborationBase):
    """Schema for collaboration response."""
    id: uuid.UUID
    document_id: uuid.UUID
    user_id: uuid.UUID
    status: CollaborationStatus
    session_id: Optional[str] = None
    last_activity: Optional[datetime] = None
    cursor_position: Optional[Dict[str, Any]] = None
    selected_text: Optional[str] = None
    joined_at: datetime
    left_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CollaborationResponse(Collaboration):
    """Schema for collaboration response with user information."""
    user: Optional["User"] = None


class CollaborationEventBase(BaseModel):
    """Base collaboration event schema."""
    event_type: str = Field(..., min_length=1, max_length=100)
    event_data: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Dict[str, Any]] = None


class CollaborationEventCreate(CollaborationEventBase):
    """Schema for creating collaboration event."""
    session_id: Optional[str] = None


class CollaborationEvent(CollaborationEventBase):
    """Schema for collaboration event response."""
    id: uuid.UUID
    document_id: uuid.UUID
    user_id: uuid.UUID
    session_id: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class CollaborationEventResponse(CollaborationEvent):
    """Schema for collaboration event response with user information."""
    user: Optional["User"] = None


class UserPresenceBase(BaseModel):
    """Base user presence schema."""
    status: str = Field(default="online", regex="^(online|away|busy|offline)$")
    cursor_position: Optional[Dict[str, Any]] = None
    selected_text: Optional[str] = None
    current_section: Optional[str] = None


class UserPresenceUpdate(UserPresenceBase):
    """Schema for updating user presence."""
    pass


class UserPresence(UserPresenceBase):
    """Schema for user presence response."""
    id: uuid.UUID
    user_id: uuid.UUID
    document_id: uuid.UUID
    session_id: str
    last_seen: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPresenceResponse(UserPresence):
    """Schema for user presence response with user information."""
    user: Optional["User"] = None


class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: str = Field(default="text", regex="^(text|image|file|system)$")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating chat message."""
    parent_id: Optional[uuid.UUID] = None


class ChatMessageUpdate(BaseModel):
    """Schema for updating chat message."""
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    is_edited: Optional[bool] = None


class ChatMessage(ChatMessageBase):
    """Schema for chat message response."""
    id: uuid.UUID
    document_id: uuid.UUID
    author_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    is_edited: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    edited_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChatMessageResponse(ChatMessage):
    """Schema for chat message response with author information."""
    author: Optional["User"] = None
    replies: List["ChatMessage"] = []
    reactions: List["MessageReaction"] = []


class MessageReactionBase(BaseModel):
    """Base message reaction schema."""
    emoji: str = Field(..., min_length=1, max_length=10)


class MessageReactionCreate(MessageReactionBase):
    """Schema for creating message reaction."""
    pass


class MessageReaction(MessageReactionBase):
    """Schema for message reaction response."""
    id: uuid.UUID
    message_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageReactionResponse(MessageReaction):
    """Schema for message reaction response with user information."""
    user: Optional["User"] = None


class DocumentEdit(BaseModel):
    """Schema for document edit operation."""
    operation: str = Field(..., regex="^(insert|delete|retain|format)$")
    position: int = Field(..., ge=0)
    length: Optional[int] = Field(None, ge=0)
    content: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentEditResult(BaseModel):
    """Schema for document edit result."""
    id: uuid.UUID
    document_id: uuid.UUID
    user_id: uuid.UUID
    edit: DocumentEdit
    applied: bool
    conflict: Optional[Dict[str, Any]] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class CursorPosition(BaseModel):
    """Schema for cursor position."""
    line: int = Field(..., ge=0)
    column: int = Field(..., ge=0)
    offset: int = Field(..., ge=0)


class TextSelection(BaseModel):
    """Schema for text selection."""
    start: CursorPosition
    end: CursorPosition
    text: Optional[str] = None


class TypingIndicator(BaseModel):
    """Schema for typing indicator."""
    user_id: uuid.UUID
    is_typing: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentConflict(BaseModel):
    """Schema for document conflict."""
    id: uuid.UUID
    document_id: uuid.UUID
    conflict_type: str = Field(..., regex="^(edit|format|structure)$")
    conflicting_edits: List[DocumentEdit]
    users_involved: List[uuid.UUID]
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None
    
    class Config:
        from_attributes = True


class ConflictResolution(BaseModel):
    """Schema for conflict resolution."""
    resolution_type: str = Field(..., regex="^(accept|reject|merge|manual)$")
    selected_edit: Optional[DocumentEdit] = None
    merged_content: Optional[str] = None
    manual_content: Optional[str] = None
    reason: Optional[str] = None


class CollaborationStats(BaseModel):
    """Schema for collaboration statistics."""
    document_id: uuid.UUID
    total_collaborators: int
    active_collaborators: int
    total_edits: int
    total_messages: int
    total_time: float  # in minutes
    average_session_duration: float  # in minutes
    most_active_user: Optional[uuid.UUID] = None
    last_activity: Optional[datetime] = None


class CollaborationHistory(BaseModel):
    """Schema for collaboration history."""
    document_id: uuid.UUID
    events: List[CollaborationEvent]
    messages: List[ChatMessage]
    edits: List[DocumentEditResult]
    conflicts: List[DocumentConflict]
    stats: CollaborationStats
    period_start: datetime
    period_end: datetime


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str = Field(..., min_length=1)
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebSocketResponse(BaseModel):
    """Schema for WebSocket responses."""
    type: str = Field(..., min_length=1)
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Update forward references
CollaborationResponse.model_rebuild()
CollaborationEventResponse.model_rebuild()
UserPresenceResponse.model_rebuild()
ChatMessageResponse.model_rebuild()
MessageReactionResponse.model_rebuild()




