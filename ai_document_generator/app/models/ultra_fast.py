"""
Ultra-fast models for SQLAlchemy
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON, Float, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class UltraFastCache(Base):
    """Ultra-fast cache model for storing cache performance data."""
    __tablename__ = "ultra_fast_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(500), nullable=False, index=True)
    cache_value = Column(Text, nullable=False)
    cache_type = Column(String(50), nullable=False)  # memory, redis, memcached
    ttl_seconds = Column(Float, nullable=False)
    hit_count = Column(Integer, default=0)
    miss_count = Column(Integer, default=0)
    avg_access_time_ms = Column(Float, default=0)
    last_accessed = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)


class UltraFastStats(Base):
    """Ultra-fast statistics model for tracking performance metrics."""
    __tablename__ = "ultra_fast_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    function_name = Column(String(200), nullable=False, index=True)
    operation_type = Column(String(50), nullable=False)  # document_generation, search, analytics
    total_requests = Column(BigInteger, default=0)
    total_hits = Column(BigInteger, default=0)
    total_misses = Column(BigInteger, default=0)
    avg_response_time_ms = Column(Float, default=0)
    min_response_time_ms = Column(Float, default=0)
    max_response_time_ms = Column(Float, default=0)
    p95_response_time_ms = Column(Float, default=0)
    p99_response_time_ms = Column(Float, default=0)
    speed_improvement_percent = Column(Float, default=0)
    memory_usage_mb = Column(Float, default=0)
    cpu_usage_percent = Column(Float, default=0)
    parallel_operations = Column(Integer, default=0)
    jit_compilations = Column(Integer, default=0)
    cache_hit_rate = Column(Float, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UltraFastOptimization(Base):
    """Ultra-fast optimization model for tracking optimization results."""
    __tablename__ = "ultra_fast_optimizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    optimization_type = Column(String(50), nullable=False)  # cache, parallel, memory, jit
    optimization_name = Column(String(200), nullable=False)
    function_name = Column(String(200), nullable=True)
    before_value = Column(String(500), nullable=True)
    after_value = Column(String(500), nullable=True)
    improvement_percent = Column(Float, default=0)
    speed_improvement_ms = Column(Float, default=0)
    memory_improvement_mb = Column(Float, default=0)
    cpu_improvement_percent = Column(Float, default=0)
    optimization_status = Column(String(20), default="pending")  # pending, applied, failed
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())


class UltraFastPerformance(Base):
    """Ultra-fast performance model for tracking overall system performance."""
    __tablename__ = "ultra_fast_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    performance_score = Column(Float, nullable=False)
    total_functions = Column(Integer, default=0)
    avg_response_time_ms = Column(Float, default=0)
    avg_hit_rate = Column(Float, default=0)
    total_optimizations = Column(Integer, default=0)
    speed_improvement_percent = Column(Float, default=0)
    memory_usage_mb = Column(Float, default=0)
    cpu_usage_percent = Column(Float, default=0)
    cache_size = Column(Integer, default=0)
    parallel_threads = Column(Integer, default=0)
    jit_functions = Column(Integer, default=0)
    performance_issues = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    measured_at = Column(DateTime, default=func.now())


class UltraFastBenchmark(Base):
    """Ultra-fast benchmark model for tracking benchmark results."""
    __tablename__ = "ultra_fast_benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    benchmark_name = Column(String(200), nullable=False)
    benchmark_type = Column(String(50), nullable=False)  # speed, memory, cpu, cache
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
    optimization_level = Column(String(20), default="none")  # none, basic, advanced, ultra_fast
    benchmark_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())


class UltraFastAlert(Base):
    """Ultra-fast alert model for tracking performance alerts."""
    __tablename__ = "ultra_fast_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(String(50), nullable=False)  # slow_response, high_memory, low_hit_rate
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    function_name = Column(String(200), nullable=True)
    threshold_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    resolver = relationship("User", foreign_keys=[resolved_by])




