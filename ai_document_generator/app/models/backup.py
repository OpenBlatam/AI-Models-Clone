"""
Backup models for SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Backup(Base):
    """Backup model for storing backup information."""
    __tablename__ = "backups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    backup_type = Column(String(50), nullable=False)  # full, incremental, differential
    backup_path = Column(String(500), nullable=False)
    size = Column(BigInteger, default=0)  # Size in bytes
    checksum = Column(String(64), nullable=True)  # SHA-256 checksum
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    deleter = relationship("User", foreign_keys=[deleted_by])
    jobs = relationship("BackupJob", back_populates="backup", cascade="all, delete-orphan")


class BackupJob(Base):
    """Backup job model for tracking backup operations."""
    __tablename__ = "backup_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    backup_id = Column(UUID(as_uuid=True), ForeignKey("backups.id"), nullable=False)
    job_type = Column(String(20), nullable=False)  # backup, restore, cleanup
    status = Column(String(20), nullable=False)  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # Progress percentage (0-100)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    backup = relationship("Backup", back_populates="jobs")


class BackupSchedule(Base):
    """Backup schedule model for automated backups."""
    __tablename__ = "backup_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    backup_type = Column(String(50), nullable=False)  # full, incremental, differential
    schedule_cron = Column(String(100), nullable=False)  # Cron expression
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    metadata = Column(JSON, default=dict)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])




