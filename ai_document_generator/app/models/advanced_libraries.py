"""
Advanced libraries models for SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON, Float, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class AdvancedLibrary(Base):
    """Advanced library model for tracking library information."""
    __tablename__ = "advanced_libraries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_name = Column(String(200), nullable=False, unique=True, index=True)
    library_version = Column(String(50), nullable=False)
    library_category = Column(String(50), nullable=False)  # ml_ai, data_processing, performance, etc.
    capabilities = Column(JSON, default=list)
    dependencies = Column(JSON, default=list)
    is_initialized = Column(Boolean, default=False)
    initialization_time_ms = Column(Float, default=0)
    memory_usage_mb = Column(Float, default=0)
    cpu_usage_percent = Column(Float, default=0)
    configuration = Column(JSON, default=dict)
    status = Column(String(20), default="unknown")  # active, inactive, error, unknown
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class LibraryPerformance(Base):
    """Library performance model for tracking performance metrics."""
    __tablename__ = "library_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id = Column(UUID(as_uuid=True), ForeignKey("advanced_libraries.id"), nullable=False)
    operation_type = Column(String(100), nullable=False)  # initialization, execution, optimization
    execution_time_ms = Column(Float, nullable=False)
    memory_usage_mb = Column(Float, default=0)
    cpu_usage_percent = Column(Float, default=0)
    cache_hit_rate = Column(Float, default=0)
    error_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    throughput_ops_per_sec = Column(Float, default=0)
    optimization_level = Column(String(20), default="basic")  # basic, advanced, ultra_fast
    performance_score = Column(Float, default=0)
    benchmark_results = Column(JSON, default=dict)
    measured_at = Column(DateTime, default=func.now())
    
    # Relationships
    library = relationship("AdvancedLibrary", foreign_keys=[library_id])


class LibraryUsage(Base):
    """Library usage model for tracking usage statistics."""
    __tablename__ = "library_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id = Column(UUID(as_uuid=True), ForeignKey("advanced_libraries.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    operation_name = Column(String(200), nullable=False)
    total_calls = Column(BigInteger, default=0)
    successful_calls = Column(BigInteger, default=0)
    failed_calls = Column(BigInteger, default=0)
    total_execution_time_ms = Column(Float, default=0)
    avg_execution_time_ms = Column(Float, default=0)
    min_execution_time_ms = Column(Float, default=0)
    max_execution_time_ms = Column(Float, default=0)
    p95_execution_time_ms = Column(Float, default=0)
    p99_execution_time_ms = Column(Float, default=0)
    total_memory_usage_mb = Column(Float, default=0)
    avg_memory_usage_mb = Column(Float, default=0)
    total_cpu_usage_percent = Column(Float, default=0)
    avg_cpu_usage_percent = Column(Float, default=0)
    cache_hits = Column(BigInteger, default=0)
    cache_misses = Column(BigInteger, default=0)
    cache_hit_rate = Column(Float, default=0)
    last_used = Column(DateTime, nullable=True)
    usage_date = Column(DateTime, default=func.now())
    
    # Relationships
    library = relationship("AdvancedLibrary", foreign_keys=[library_id])
    user = relationship("User", foreign_keys=[user_id])


class LibraryOptimization(Base):
    """Library optimization model for tracking optimization results."""
    __tablename__ = "library_optimizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id = Column(UUID(as_uuid=True), ForeignKey("advanced_libraries.id"), nullable=False)
    optimization_type = Column(String(50), nullable=False)  # caching, parallelization, jit, memory
    optimization_name = Column(String(200), nullable=False)
    before_metrics = Column(JSON, default=dict)
    after_metrics = Column(JSON, default=dict)
    improvement_percent = Column(Float, default=0)
    speed_improvement_ms = Column(Float, default=0)
    memory_improvement_mb = Column(Float, default=0)
    cpu_improvement_percent = Column(Float, default=0)
    optimization_status = Column(String(20), default="pending")  # pending, applied, failed, reverted
    applied_at = Column(DateTime, nullable=True)
    reverted_at = Column(DateTime, nullable=True)
    optimization_config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    library = relationship("AdvancedLibrary", foreign_keys=[library_id])


class LibraryBenchmark(Base):
    """Library benchmark model for tracking benchmark results."""
    __tablename__ = "library_benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id = Column(UUID(as_uuid=True), ForeignKey("advanced_libraries.id"), nullable=False)
    benchmark_name = Column(String(200), nullable=False)
    benchmark_type = Column(String(50), nullable=False)  # speed, memory, accuracy, throughput
    test_data_size = Column(Integer, nullable=False)
    iterations = Column(Integer, nullable=False)
    total_time_ms = Column(Float, nullable=False)
    avg_time_ms = Column(Float, nullable=False)
    min_time_ms = Column(Float, nullable=False)
    max_time_ms = Column(Float, nullable=False)
    p95_time_ms = Column(Float, nullable=False)
    p99_time_ms = Column(Float, nullable=False)
    throughput_ops_per_sec = Column(Float, default=0)
    memory_usage_mb = Column(Float, default=0)
    cpu_usage_percent = Column(Float, default=0)
    accuracy_score = Column(Float, default=0)
    precision_score = Column(Float, default=0)
    recall_score = Column(Float, default=0)
    f1_score = Column(Float, default=0)
    benchmark_config = Column(JSON, default=dict)
    benchmark_results = Column(JSON, default=dict)
    comparison_with_baseline = Column(JSON, default=dict)
    benchmarked_at = Column(DateTime, default=func.now())
    
    # Relationships
    library = relationship("AdvancedLibrary", foreign_keys=[library_id])


class LibraryDependency(Base):
    """Library dependency model for tracking library dependencies."""
    __tablename__ = "library_dependencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id = Column(UUID(as_uuid=True), ForeignKey("advanced_libraries.id"), nullable=False)
    dependency_name = Column(String(200), nullable=False)
    dependency_version = Column(String(50), nullable=False)
    dependency_type = Column(String(20), nullable=False)  # required, optional, dev, peer
    is_installed = Column(Boolean, default=False)
    is_compatible = Column(Boolean, default=True)
    compatibility_issues = Column(JSON, default=list)
    installation_time_ms = Column(Float, default=0)
    memory_impact_mb = Column(Float, default=0)
    cpu_impact_percent = Column(Float, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    library = relationship("AdvancedLibrary", foreign_keys=[library_id])


class LibraryConfiguration(Base):
    """Library configuration model for storing library configurations."""
    __tablename__ = "library_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id = Column(UUID(as_uuid=True), ForeignKey("advanced_libraries.id"), nullable=False)
    config_name = Column(String(200), nullable=False)
    config_type = Column(String(50), nullable=False)  # performance, memory, caching, parallelization
    config_values = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    performance_impact = Column(JSON, default=dict)
    memory_impact = Column(JSON, default=dict)
    cpu_impact = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    library = relationship("AdvancedLibrary", foreign_keys=[library_id])


class LibraryAlert(Base):
    """Library alert model for tracking library-related alerts."""
    __tablename__ = "library_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    library_id = Column(UUID(as_uuid=True), ForeignKey("advanced_libraries.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # performance, memory, error, dependency
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    alert_message = Column(Text, nullable=False)
    threshold_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    alert_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    library = relationship("AdvancedLibrary", foreign_keys=[library_id])
    resolver = relationship("User", foreign_keys=[resolved_by])


class LibraryReport(Base):
    """Library report model for storing library analysis reports."""
    __tablename__ = "library_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # performance, usage, optimization, benchmark
    report_period_start = Column(DateTime, nullable=False)
    report_period_end = Column(DateTime, nullable=False)
    total_libraries = Column(Integer, default=0)
    active_libraries = Column(Integer, default=0)
    avg_performance_score = Column(Float, default=0)
    avg_memory_usage_mb = Column(Float, default=0)
    avg_cpu_usage_percent = Column(Float, default=0)
    total_optimizations = Column(Integer, default=0)
    total_benchmarks = Column(Integer, default=0)
    performance_summary = Column(JSON, default=dict)
    usage_summary = Column(JSON, default=dict)
    optimization_summary = Column(JSON, default=dict)
    benchmark_summary = Column(JSON, default=dict)
    recommendations = Column(JSON, default=list)
    report_data = Column(JSON, default=dict)
    generated_at = Column(DateTime, default=func.now())
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    generator = relationship("User", foreign_keys=[generated_by])




