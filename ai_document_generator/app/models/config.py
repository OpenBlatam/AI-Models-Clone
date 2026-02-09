"""
Configuration models for SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Config(Base):
    """Configuration model for storing application settings."""
    __tablename__ = "configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(200), nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(50), nullable=False)  # string, integer, float, boolean, json, yaml
    environment = Column(String(50), nullable=False, default="default", index=True)
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    versions = relationship("ConfigVersion", back_populates="config", cascade="all, delete-orphan")
    
    # Unique constraint
    __table_args__ = (
        {"extend_existing": True}
    )


class ConfigVersion(Base):
    """Configuration version model for tracking changes."""
    __tablename__ = "config_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(UUID(as_uuid=True), ForeignKey("configs.id"), nullable=False)
    value = Column(Text, nullable=False)
    value_type = Column(String(50), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    config = relationship("Config", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])


class ConfigEnvironment(Base):
    """Configuration environment model for managing environments."""
    __tablename__ = "config_environments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])




