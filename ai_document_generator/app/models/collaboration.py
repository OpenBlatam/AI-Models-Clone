"""
Collaboration model and related schemas
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class CollaborationStatus(str, enum.Enum):
    """Collaboration status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    COMPLETED = "completed"


class CollaborationRole(str, enum.Enum):
    """Collaboration role enumeration."""
    OWNER = "owner"
    EDITOR = "editor"
    COMMENTOR = "commentor"
    VIEWER = "viewer"


class Collaboration(Base):
    """Collaboration model for real-time document collaboration."""
    
    __tablename__ = "collaborations"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Collaboration settings
    role: Mapped[CollaborationRole] = mapped_column(Enum(CollaborationRole), nullable=False)
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    status: Mapped[CollaborationStatus] = mapped_column(Enum(CollaborationStatus), default=CollaborationStatus.ACTIVE, nullable=False)
    
    # Session information
    session_id: Mapped[Optional[str]] = mapped_column(String(255))
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cursor_position: Mapped[Optional[dict]] = mapped_column(JSON)
    selected_text: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="collaborations")
    user: Mapped["User"] = relationship("User", back_populates="collaborations")


class CollaborationEvent(Base):
    """Collaboration event model for tracking real-time changes."""
    
    __tablename__ = "collaboration_events"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # insert, delete, format, cursor_move, etc.
    event_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    position: Mapped[Optional[dict]] = mapped_column(JSON)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document")
    user: Mapped["User"] = relationship("User")


class UserPresence(Base):
    """User presence model for showing active users."""
    
    __tablename__ = "user_presence"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Presence information
    status: Mapped[str] = mapped_column(String(50), default="online", nullable=False)  # online, away, busy, offline
    cursor_position: Mapped[Optional[dict]] = mapped_column(JSON)
    selected_text: Mapped[Optional[str]] = mapped_column(Text)
    current_section: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Timestamps
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    document: Mapped["Document"] = relationship("Document")


class ChatMessage(Base):
    """Chat message model for document collaboration chat."""
    
    __tablename__ = "chat_messages"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_messages.id"))
    
    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), default="text", nullable=False)  # text, image, file, system
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    # Message status
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document")
    author: Mapped["User"] = relationship("User")
    parent: Mapped[Optional["ChatMessage"]] = relationship("ChatMessage", remote_side=[id])
    replies: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="parent")
    reactions: Mapped[List["MessageReaction"]] = relationship(
        "MessageReaction", back_populates="message", cascade="all, delete-orphan"
    )


class MessageReaction(Base):
    """Message reaction model for chat messages."""
    
    __tablename__ = "message_reactions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_messages.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Reaction details
    emoji: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message: Mapped["ChatMessage"] = relationship("ChatMessage", back_populates="reactions")
    user: Mapped["User"] = relationship("User")




