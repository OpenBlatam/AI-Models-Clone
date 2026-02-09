"""
Performance models for SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class PerformanceMetric(Base):
    """Performance metric model for storing performance data."""
    __tablename__ = "performance_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_name = Column(String(200), nullable=False, index=True)
    duration_ms = Column(Float, nullable=False)
    memory_usage_mb = Column(Float, nullable=True)
    cpu_usage_percent = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    profiles = relationship("PerformanceProfile", back_populates="metric")


class PerformanceAlert(Base):
    """Performance alert model for storing performance alerts."""
    __tablename__ = "performance_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_name = Column(String(200), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # slow_operation, high_memory, high_cpu, error_rate
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    threshold_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    resolver = relationship("User", foreign_keys=[resolved_by])


class PerformanceProfile(Base):
    """Performance profile model for storing performance profiles."""
    __tablename__ = "performance_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_name = Column(String(200), nullable=False, unique=True)
    metric_id = Column(UUID(as_uuid=True), ForeignKey("performance_metrics.id"), nullable=False)
    profile_data = Column(JSON, nullable=False)  # Profiling data (call stack, timing, etc.)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    metric = relationship("PerformanceMetric", back_populates="profiles")




