"""
Optimization Data Models.

Pydantic models for optimization with comprehensive validation and performance tracking.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field, validator
from .config import OptimizationLevel


class PerformanceMetrics(BaseModel):
    """Performance metrics for tracking optimization effectiveness."""
    
    # Timing metrics
    total_operations: int = Field(default=0, ge=0)
    successful_operations: int = Field(default=0, ge=0)
    failed_operations: int = Field(default=0, ge=0)
    
    # Response time metrics
    avg_response_time_ms: float = Field(default=0.0, ge=0.0)
    p95_response_time_ms: float = Field(default=0.0, ge=0.0)
    p99_response_time_ms: float = Field(default=0.0, ge=0.0)
    min_response_time_ms: float = Field(default=0.0, ge=0.0)
    max_response_time_ms: float = Field(default=0.0, ge=0.0)
    
    # Throughput metrics
    operations_per_second: float = Field(default=0.0, ge=0.0)
    requests_per_minute: float = Field(default=0.0, ge=0.0)
    
    # Cache metrics
    cache_hits: int = Field(default=0, ge=0)
    cache_misses: int = Field(default=0, ge=0)
    cache_hit_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Resource usage
    cpu_usage_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    memory_usage_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    memory_usage_mb: float = Field(default=0.0, ge=0.0)
    
    # Error tracking
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    timeout_count: int = Field(default=0, ge=0)
    
    # Timestamps
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def calculate_success_rate(self) -> float:
        """Calculate operation success rate."""
        if self.total_operations == 0:
            return 0.0
        return self.successful_operations / self.total_operations
    
    def calculate_cache_efficiency(self) -> float:
        """Calculate cache efficiency score."""
        total_cache_operations = self.cache_hits + self.cache_misses
        if total_cache_operations == 0:
            return 0.0
        return self.cache_hits / total_cache_operations
    
    def update_response_time(self, new_time_ms: float):
        """Update response time metrics with new measurement."""
        if self.total_operations == 0:
            self.avg_response_time_ms = new_time_ms
            self.min_response_time_ms = new_time_ms
            self.max_response_time_ms = new_time_ms
        else:
            # Update average
            total_time = self.avg_response_time_ms * self.total_operations
            self.avg_response_time_ms = (total_time + new_time_ms) / (self.total_operations + 1)
            
            # Update min/max
            self.min_response_time_ms = min(self.min_response_time_ms, new_time_ms)
            self.max_response_time_ms = max(self.max_response_time_ms, new_time_ms)
        
        self.last_updated = datetime.now(timezone.utc)


class OptimizationConfig(BaseModel):
    """Configuration for optimization request."""
    level: OptimizationLevel = OptimizationLevel.ADVANCED
    enable_caching: bool = True
    enable_compression: bool = True
    enable_monitoring: bool = True
    cache_ttl: int = Field(default=3600, ge=0)
    timeout_ms: int = Field(default=30000, ge=100)
    
    class Config:
        use_enum_values = True


class SystemStatus(BaseModel):
    """Current system status and health."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # System health
    overall_health: str = Field(default="unknown")  # healthy, degraded, unhealthy
    uptime_seconds: float = Field(default=0.0, ge=0.0)
    
    # Service status
    services_healthy: int = Field(default=0, ge=0)
    services_total: int = Field(default=0, ge=0)
    
    # Performance indicators
    cpu_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    memory_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    disk_usage: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Network status
    active_connections: int = Field(default=0, ge=0)
    network_latency_ms: float = Field(default=0.0, ge=0.0)
    
    # Database status
    database_connections_active: int = Field(default=0, ge=0)
    database_connections_idle: int = Field(default=0, ge=0)
    database_response_time_ms: float = Field(default=0.0, ge=0.0)
    
    # Cache status
    cache_status: str = Field(default="unknown")  # available, unavailable, degraded
    cache_memory_usage: float = Field(default=0.0, ge=0.0)
    
    # Alerts and warnings
    active_alerts: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    def calculate_health_score(self) -> float:
        """Calculate overall health score (0-1)."""
        scores = []
        
        # Service health
        if self.services_total > 0:
            service_score = self.services_healthy / self.services_total
            scores.append(service_score)
        
        # Resource health (inverted - lower usage is better)
        cpu_score = max(0, (100 - self.cpu_usage) / 100)
        memory_score = max(0, (100 - self.memory_usage) / 100)
        scores.extend([cpu_score, memory_score])
        
        # Database health (based on response time)
        if self.database_response_time_ms > 0:
            db_score = max(0, min(1, (1000 - self.database_response_time_ms) / 1000))
            scores.append(db_score)
        
        # Alert penalty
        alert_penalty = min(0.5, len(self.active_alerts) * 0.1)
        
        if scores:
            base_score = sum(scores) / len(scores)
            return max(0, base_score - alert_penalty)
        
        return 0.5  # Default neutral score


class OptimizationResult(BaseModel):
    """Result of an optimization operation."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    operation_name: str
    optimization_level: OptimizationLevel
    
    # Execution details
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_ms: float = Field(default=0.0, ge=0.0)
    
    # Results
    success: bool = Field(default=False)
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    
    # Performance metrics
    metrics: Optional[PerformanceMetrics] = None
    
    # Optimization details
    optimizations_applied: List[str] = Field(default_factory=list)
    cache_used: bool = Field(default=False)
    compression_used: bool = Field(default=False)
    
    # Resource usage
    memory_peak_mb: float = Field(default=0.0, ge=0.0)
    cpu_time_ms: float = Field(default=0.0, ge=0.0)
    
    def mark_completed(self, success: bool = True, error: Optional[str] = None):
        """Mark the operation as completed."""
        self.end_time = datetime.now(timezone.utc)
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.success = success
        self.error_message = error
    
    def add_optimization(self, optimization_name: str):
        """Add an optimization that was applied."""
        if optimization_name not in self.optimizations_applied:
            self.optimizations_applied.append(optimization_name)
    
    class Config:
        use_enum_values = True


class CacheStats(BaseModel):
    """Cache performance statistics."""
    
    # Cache levels
    l1_size: int = Field(default=0, ge=0)
    l1_hits: int = Field(default=0, ge=0)
    l1_misses: int = Field(default=0, ge=0)
    
    l2_size: int = Field(default=0, ge=0)
    l2_hits: int = Field(default=0, ge=0)
    l2_misses: int = Field(default=0, ge=0)
    
    l3_size: int = Field(default=0, ge=0)
    l3_hits: int = Field(default=0, ge=0)
    l3_misses: int = Field(default=0, ge=0)
    
    # Overall stats
    total_hits: int = Field(default=0, ge=0)
    total_misses: int = Field(default=0, ge=0)
    hit_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Memory usage
    memory_usage_mb: float = Field(default=0.0, ge=0.0)
    max_memory_mb: float = Field(default=0.0, ge=0.0)
    
    # Hot key tracking
    hot_keys_count: int = Field(default=0, ge=0)
    evictions: int = Field(default=0, ge=0)
    
    def calculate_hit_ratio(self) -> float:
        """Calculate overall cache hit ratio."""
        total_requests = self.total_hits + self.total_misses
        if total_requests == 0:
            return 0.0
        return self.total_hits / total_requests
    
    def update_totals(self):
        """Update total statistics from individual levels."""
        self.total_hits = self.l1_hits + self.l2_hits + self.l3_hits
        self.total_misses = self.l1_misses + self.l2_misses + self.l3_misses
        self.hit_ratio = self.calculate_hit_ratio()


class DatabaseStats(BaseModel):
    """Database performance statistics."""
    
    # Connection pool stats
    active_connections: int = Field(default=0, ge=0)
    idle_connections: int = Field(default=0, ge=0)
    max_connections: int = Field(default=0, ge=0)
    pool_utilization: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Query stats
    total_queries: int = Field(default=0, ge=0)
    successful_queries: int = Field(default=0, ge=0)
    failed_queries: int = Field(default=0, ge=0)
    cached_queries: int = Field(default=0, ge=0)
    
    # Performance metrics
    avg_query_time_ms: float = Field(default=0.0, ge=0.0)
    slow_queries_count: int = Field(default=0, ge=0)
    
    # Query cache stats
    query_cache_size: int = Field(default=0, ge=0)
    query_cache_hits: int = Field(default=0, ge=0)
    query_cache_misses: int = Field(default=0, ge=0)
    
    def calculate_success_rate(self) -> float:
        """Calculate query success rate."""
        if self.total_queries == 0:
            return 0.0
        return self.successful_queries / self.total_queries
    
    def calculate_cache_efficiency(self) -> float:
        """Calculate query cache efficiency."""
        total_cache_requests = self.query_cache_hits + self.query_cache_misses
        if total_cache_requests == 0:
            return 0.0
        return self.query_cache_hits / total_cache_requests


# Export all models
__all__ = [
    "PerformanceMetrics",
    "OptimizationConfig",
    "SystemStatus",
    "OptimizationResult",
    "CacheStats",
    "DatabaseStats"
] 