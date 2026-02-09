"""
File models for SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class File(Base):
    """File model for storing file information."""
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    secure_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)  # image, document, etc.
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    metadata = Column(JSON, default=dict)
    is_public = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="files")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    deleter = relationship("User", foreign_keys=[deleted_by])
    versions = relationship("FileVersion", back_populates="file", cascade="all, delete-orphan")
    shares = relationship("FileShare", back_populates="file", cascade="all, delete-orphan")


class FileVersion(Base):
    """File version model for tracking file changes."""
    __tablename__ = "file_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    version_note = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    file = relationship("File", back_populates="versions")
    creator = relationship("User")


class FileShare(Base):
    """File sharing model for controlling file access."""
    __tablename__ = "file_shares"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False)
    shared_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shared_with = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    permission = Column(String(20), nullable=False)  # read, write, admin
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    file = relationship("File", back_populates="shares")
    sharer = relationship("User", foreign_keys=[shared_by])
    recipient = relationship("User", foreign_keys=[shared_with])




