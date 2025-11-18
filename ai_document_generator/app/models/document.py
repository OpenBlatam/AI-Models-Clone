"""
Document model and related schemas
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Integer, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class DocumentStatus(str, enum.Enum):
    """Document status enumeration."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DocumentType(str, enum.Enum):
    """Document type enumeration."""
    TEXT = "text"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    FORM = "form"
    REPORT = "report"
    PROPOSAL = "proposal"
    CONTRACT = "contract"
    MANUAL = "manual"
    OTHER = "other"


class Document(Base):
    """Document model for storing document information."""
    
    __tablename__ = "documents"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("document_templates.id"))
    
    # Document metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    document_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), default=DocumentType.TEXT, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False)
    
    # Document content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[Optional[str]] = mapped_column(Text)
    content_json: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Document settings
    settings: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    
    # Collaboration settings
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_comments: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_editing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_sharing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    edit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    share_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="documents")
    owner: Mapped["User"] = relationship("User", back_populates="documents")
    template: Mapped[Optional["DocumentTemplate"]] = relationship("DocumentTemplate", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion", back_populates="document", cascade="all, delete-orphan"
    )
    collaborations: Mapped[List["Collaboration"]] = relationship(
        "Collaboration", back_populates="document", cascade="all, delete-orphan"
    )
    comments: Mapped[List["DocumentComment"]] = relationship(
        "DocumentComment", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentVersion(Base):
    """Document version model for version control."""
    
    __tablename__ = "document_versions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Version content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[Optional[str]] = mapped_column(Text)
    content_json: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Version metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    changes: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    # Version info
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="versions")
    creator: Mapped["User"] = relationship("User")


class DocumentComment(Base):
    """Document comment model for collaboration."""
    
    __tablename__ = "document_comments"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("document_comments.id"))
    
    # Comment content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[Optional[dict]] = mapped_column(JSON)  # For positioning comments in document
    
    # Comment status
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="comments")
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id])
    resolver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[resolved_by])
    parent: Mapped[Optional["DocumentComment"]] = relationship("DocumentComment", remote_side=[id])
    replies: Mapped[List["DocumentComment"]] = relationship("DocumentComment", back_populates="parent")


class DocumentShare(Base):
    """Document sharing model for access control."""
    
    __tablename__ = "document_shares"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    shared_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shared_with: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    shared_with_email: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Share settings
    permission: Mapped[str] = mapped_column(String(50), nullable=False)  # view, comment, edit
    token: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    document: Mapped["Document"] = relationship("Document")
    sharer: Mapped["User"] = relationship("User", foreign_keys=[shared_by])
    recipient: Mapped[Optional["User"]] = relationship("User", foreign_keys=[shared_with])




