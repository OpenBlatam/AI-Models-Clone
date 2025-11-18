"""
Workflow models for SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Workflow(Base):
    """Workflow model for storing workflow definitions."""
    __tablename__ = "workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    workflow_type = Column(String(50), nullable=False)  # document, email, automation, etc.
    trigger_type = Column(String(50), nullable=False)  # manual, scheduled, webhook, event
    trigger_config = Column(JSON, default=dict)
    steps = Column(JSON, nullable=False)  # Workflow steps configuration
    variables = Column(JSON, default=dict)  # Workflow variables
    metadata = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    execution_count = Column(Integer, default=0)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    deleter = relationship("User", foreign_keys=[deleted_by])
    steps_rel = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    triggers = relationship("WorkflowTrigger", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowStep(Base):
    """Workflow step model for storing individual workflow steps."""
    __tablename__ = "workflow_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    step_name = Column(String(100), nullable=False)
    step_type = Column(String(50), nullable=False)  # ai_generation, document_creation, notification, etc.
    step_config = Column(JSON, nullable=False)  # Step-specific configuration
    step_order = Column(Integer, nullable=False)
    conditions = Column(JSON, default=list)  # Step execution conditions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps_rel")


class WorkflowExecution(Base):
    """Workflow execution model for tracking workflow runs."""
    __tablename__ = "workflow_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    executed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    input_data = Column(JSON, default=dict)  # Input data for the workflow
    output_data = Column(JSON, default=dict)  # Output data from the workflow
    status = Column(String(20), nullable=False)  # running, completed, failed, cancelled
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    executor = relationship("User", foreign_keys=[executed_by])


class WorkflowTrigger(Base):
    """Workflow trigger model for managing workflow triggers."""
    __tablename__ = "workflow_triggers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False)
    trigger_type = Column(String(50), nullable=False)  # scheduled, webhook, event, manual
    trigger_config = Column(JSON, nullable=False)  # Trigger-specific configuration
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="triggers")




