"""
Audit models for SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class AuditLog(Base):
    """Audit log model for tracking user actions and system events."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)  # user_action, system_event, security_event
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # document, user, organization, etc.
    resource_id = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    details = Column(JSON, default=dict)  # Additional details about the action
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class AuditEvent(Base):
    """Audit event model for tracking system events."""
    __tablename__ = "audit_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)  # system_startup, backup_completed, etc.
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Can be system
    event_data = Column(JSON, default=dict)  # Event-specific data
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class AuditTrail(Base):
    """Audit trail model for tracking resource changes over time."""
    __tablename__ = "audit_trails"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    old_values = Column(JSON, default=dict)  # Previous values
    new_values = Column(JSON, default=dict)  # New values
    changed_fields = Column(JSON, default=list)  # List of changed fields
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])




