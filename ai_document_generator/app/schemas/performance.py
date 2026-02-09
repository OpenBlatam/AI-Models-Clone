"""
Performance schemas for Pydantic validation
"""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class PerformanceMetricResponse(BaseModel):
    """Schema for performance metric response."""
    id: uuid.UUID
    operation_name: str
    duration_ms: float
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PerformanceAlertResponse(BaseModel):
    """Schema for performance alert response."""
    id: uuid.UUID
    operation_name: str
    alert_type: str
    severity: str
    threshold_value: float
    actual_value: float
    message: str
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[uuid.UUID] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        from_attributes = True


class PerformanceProfileResponse(BaseModel):
    """Schema for performance profile response."""
    id: uuid.UUID
    profile_name: str
    metric_id: uuid.UUID
    profile_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        from_attributes = True


class PerformanceOptimizationRequest(BaseModel):
    """Schema for performance optimization request."""
    optimize_memory: bool = True
    optimize_database: bool = True
    optimize_cache: bool = True
    run_garbage_collection: bool = True
    optimization_level: str = Field("standard", regex="^(light|standard|aggressive)$")


class PerformanceOptimizationResponse(BaseModel):
    """Schema for performance optimization response."""
    optimizations: List[Dict[str, Any]] = Field(default_factory=list)
    total_optimizations: int
    timestamp: datetime


class PerformanceReportResponse(BaseModel):
    """Schema for performance report response."""
    performance_score: float = Field(..., ge=0, le=100)
    system_metrics: Dict[str, Any] = Field(default_factory=dict)
    application_metrics: Dict[str, Any] = Field(default_factory=dict)
    database_metrics: Dict[str, Any] = Field(default_factory=dict)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    report_period_start: datetime
    report_period_end: datetime
    generated_at: datetime


class PerformanceSearchRequest(BaseModel):
    """Schema for performance search request."""
    operation_name: Optional[str] = None
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: int = Field(1, ge=1)
    size: int = Field(50, ge=1, le=100)


class PerformanceStatsResponse(BaseModel):
    """Schema for performance statistics response."""
    total_operations: int
    total_calls: int
    avg_duration_ms: float
    max_duration_ms: float
    min_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    success_rate: float
    error_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float


class PerformanceComparisonRequest(BaseModel):
    """Schema for performance comparison request."""
    operation_name: str
    baseline_start: datetime
    baseline_end: datetime
    comparison_start: datetime
    comparison_end: datetime
    metrics: List[str] = Field(default_factory=lambda: ["duration_ms", "success_rate"])


class PerformanceComparisonResponse(BaseModel):
    """Schema for performance comparison response."""
    operation_name: str
    baseline_period: Dict[str, Any] = Field(default_factory=dict)
    comparison_period: Dict[str, Any] = Field(default_factory=dict)
    improvements: Dict[str, Any] = Field(default_factory=dict)
    regressions: Dict[str, Any] = Field(default_factory=dict)
    overall_change: str  # improved, degraded, unchanged


class PerformanceThresholdRequest(BaseModel):
    """Schema for performance threshold request."""
    operation_name: str
    threshold_type: str = Field(..., regex="^(duration|memory|cpu|error_rate)$")
    threshold_value: float
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    is_active: bool = True


class PerformanceThresholdResponse(BaseModel):
    """Schema for performance threshold response."""
    id: uuid.UUID
    operation_name: str
    threshold_type: str
    threshold_value: float
    severity: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PerformanceBenchmarkRequest(BaseModel):
    """Schema for performance benchmark request."""
    operation_name: str
    iterations: int = Field(100, ge=1, le=10000)
    warmup_iterations: int = Field(10, ge=0, le=1000)
    concurrent_requests: int = Field(1, ge=1, le=100)
    timeout_seconds: int = Field(30, ge=1, le=300)


class PerformanceBenchmarkResponse(BaseModel):
    """Schema for performance benchmark response."""
    operation_name: str
    iterations: int
    warmup_iterations: int
    concurrent_requests: int
    results: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime


class PerformanceLoadTestRequest(BaseModel):
    """Schema for performance load test request."""
    test_name: str
    duration_seconds: int = Field(60, ge=1, le=3600)
    concurrent_users: int = Field(10, ge=1, le=1000)
    ramp_up_seconds: int = Field(10, ge=0, le=300)
    operations: List[Dict[str, Any]] = Field(..., min_items=1)


class PerformanceLoadTestResponse(BaseModel):
    """Schema for performance load test response."""
    test_id: uuid.UUID
    test_name: str
    status: str
    results: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime
    completed_at: Optional[datetime] = None


class PerformanceMonitoringRequest(BaseModel):
    """Schema for performance monitoring request."""
    operation_name: str
    monitoring_type: str = Field(..., regex="^(continuous|scheduled|on_demand)$")
    interval_seconds: int = Field(60, ge=1, le=3600)
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)
    is_active: bool = True


class PerformanceMonitoringResponse(BaseModel):
    """Schema for performance monitoring response."""
    id: uuid.UUID
    operation_name: str
    monitoring_type: str
    interval_seconds: int
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PerformanceDashboardResponse(BaseModel):
    """Schema for performance dashboard response."""
    system_health: Dict[str, Any] = Field(default_factory=dict)
    recent_metrics: List[PerformanceMetricResponse] = Field(default_factory=list)
    active_alerts: List[PerformanceAlertResponse] = Field(default_factory=list)
    performance_trends: Dict[str, Any] = Field(default_factory=dict)
    top_operations: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    last_updated: datetime


class PerformanceExportRequest(BaseModel):
    """Schema for performance export request."""
    format: str = Field(..., regex="^(json|csv|excel)$")
    operation_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    include_metadata: bool = True


class PerformanceExportResponse(BaseModel):
    """Schema for performance export response."""
    export_filename: str
    export_path: str
    total_records: int
    format: str
    download_url: str
    expires_at: datetime


class PerformanceCleanupRequest(BaseModel):
    """Schema for performance cleanup request."""
    older_than_days: int = Field(30, ge=1, le=365)
    operation_name: Optional[str] = None
    dry_run: bool = True


class PerformanceCleanupResponse(BaseModel):
    """Schema for performance cleanup response."""
    deleted_metrics: int
    deleted_alerts: int
    deleted_profiles: int
    total_deleted: int
    dry_run: bool
    completed_at: datetime




