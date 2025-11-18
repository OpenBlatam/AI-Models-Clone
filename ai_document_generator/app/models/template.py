"""
Template models for SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class TemplateCategory(Base):
    """Template category model."""
    __tablename__ = "template_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    templates = relationship("Template", back_populates="category")


class Template(Base):
    """Template model for storing document templates."""
    __tablename__ = "templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    template_type = Column(String(50), nullable=False)  # document, email, report, etc.
    category_id = Column(UUID(as_uuid=True), ForeignKey("template_categories.id"), nullable=True)
    tags = Column(JSON, default=list)
    variables = Column(JSON, default=list)  # Template variables with types and defaults
    metadata = Column(JSON, default=dict)
    is_public = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("TemplateCategory", back_populates="templates")
    creator = relationship("User", foreign_keys=[created_by])
    deleter = relationship("User", foreign_keys=[deleted_by])
    usages = relationship("TemplateUsage", back_populates="template", cascade="all, delete-orphan")


class TemplateUsage(Base):
    """Template usage tracking model."""
    __tablename__ = "template_usages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    used_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    variables_used = Column(JSON, default=dict)  # Variables used when template was applied
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    template = relationship("Template", back_populates="usages")
    user = relationship("User", foreign_keys=[used_by])
    document = relationship("Document")




