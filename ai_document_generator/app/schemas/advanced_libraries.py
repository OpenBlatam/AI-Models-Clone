"""
Advanced libraries schemas for Pydantic validation
"""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class AdvancedLibraryResponse(BaseModel):
    """Schema for advanced library response."""
    id: uuid.UUID
    library_name: str
    library_version: str
    library_category: str
    capabilities: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    is_initialized: bool = False
    initialization_time_ms: float = Field(0, ge=0)
    memory_usage_mb: float = Field(0, ge=0)
    cpu_usage_percent: float = Field(0, ge=0, le=100)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(..., regex="^(active|inactive|error|unknown)$")
    last_used: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class LibraryPerformanceResponse(BaseModel):
    """Schema for library performance response."""
    library_name: str
    avg_execution_time_ms: float = Field(0, ge=0)
    total_calls: int = Field(0, ge=0)
    error_rate: float = Field(0, ge=0, le=100)
    memory_usage_mb: float = Field(0, ge=0)
    cpu_usage_percent: float = Field(0, ge=0, le=100)
    cache_hit_rate: float = Field(0, ge=0, le=100)
    optimization_level: str = Field(..., regex="^(basic|advanced|ultra_fast)$")


class LibraryUsageResponse(BaseModel):
    """Schema for library usage response."""
    library_name: str
    operation_name: str
    total_calls: int = Field(0, ge=0)
    successful_calls: int = Field(0, ge=0)
    failed_calls: int = Field(0, ge=0)
    avg_execution_time_ms: float = Field(0, ge=0)
    min_execution_time_ms: float = Field(0, ge=0)
    max_execution_time_ms: float = Field(0, ge=0)
    p95_execution_time_ms: float = Field(0, ge=0)
    p99_execution_time_ms: float = Field(0, ge=0)
    avg_memory_usage_mb: float = Field(0, ge=0)
    avg_cpu_usage_percent: float = Field(0, ge=0, le=100)
    cache_hit_rate: float = Field(0, ge=0, le=100)
    last_used: Optional[datetime] = None


class LibraryAnalysisResponse(BaseModel):
    """Schema for library analysis response."""
    total_libraries: int = Field(0, ge=0)
    initialized_libraries: int = Field(0, ge=0)
    initialization_rate: float = Field(0, ge=0, le=100)
    avg_execution_time_ms: float = Field(0, ge=0)
    avg_error_rate: float = Field(0, ge=0, le=100)
    library_categories: Dict[str, int] = Field(default_factory=dict)
    performance_data: Dict[str, LibraryPerformanceResponse] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    analyzed_at: datetime


class LibraryOptimizationResponse(BaseModel):
    """Schema for library optimization response."""
    optimizations: List[Dict[str, Any]] = Field(default_factory=list)
    total_optimizations: int = Field(0, ge=0)
    optimized_at: datetime


class LibraryBenchmarkRequest(BaseModel):
    """Schema for library benchmark request."""
    library_name: str = Field(..., min_length=1, max_length=200)
    benchmark_type: str = Field(..., regex="^(speed|memory|accuracy|throughput|all)$")
    test_data_size: int = Field(1000, ge=1, le=1000000)
    iterations: int = Field(100, ge=1, le=10000)
    optimization_level: str = Field("advanced", regex="^(basic|advanced|ultra_fast)$")
    benchmark_config: Dict[str, Any] = Field(default_factory=dict)


class LibraryBenchmarkResponse(BaseModel):
    """Schema for library benchmark response."""
    benchmark_id: uuid.UUID
    library_name: str
    benchmark_type: str
    test_data_size: int
    iterations: int
    total_time_ms: float = Field(..., ge=0)
    avg_time_ms: float = Field(..., ge=0)
    min_time_ms: float = Field(..., ge=0)
    max_time_ms: float = Field(..., ge=0)
    p95_time_ms: float = Field(..., ge=0)
    p99_time_ms: float = Field(..., ge=0)
    throughput_ops_per_sec: float = Field(..., ge=0)
    memory_usage_mb: float = Field(..., ge=0)
    cpu_usage_percent: float = Field(..., ge=0)
    accuracy_score: float = Field(0, ge=0, le=1)
    precision_score: float = Field(0, ge=0, le=1)
    recall_score: float = Field(0, ge=0, le=1)
    f1_score: float = Field(0, ge=0, le=1)
    optimization_level: str
    benchmark_results: Dict[str, Any] = Field(default_factory=dict)
    benchmarked_at: datetime


class LibraryConfigurationRequest(BaseModel):
    """Schema for library configuration request."""
    library_name: str = Field(..., min_length=1, max_length=200)
    config_name: str = Field(..., min_length=1, max_length=200)
    config_type: str = Field(..., regex="^(performance|memory|caching|parallelization|all)$")
    config_values: Dict[str, Any] = Field(..., min_items=1)
    is_active: bool = True
    is_default: bool = False


class LibraryConfigurationResponse(BaseModel):
    """Schema for library configuration response."""
    config_id: uuid.UUID
    library_name: str
    config_name: str
    config_type: str
    config_values: Dict[str, Any]
    is_active: bool
    is_default: bool
    performance_impact: Dict[str, Any] = Field(default_factory=dict)
    memory_impact: Dict[str, Any] = Field(default_factory=dict)
    cpu_impact: Dict[str, Any] = Field(default_factory=dict)
    configured_at: datetime


class LibraryDependencyRequest(BaseModel):
    """Schema for library dependency request."""
    library_name: str = Field(..., min_length=1, max_length=200)
    dependency_name: str = Field(..., min_length=1, max_length=200)
    dependency_version: str = Field(..., min_length=1, max_length=50)
    dependency_type: str = Field(..., regex="^(required|optional|dev|peer)$")
    auto_install: bool = False


class LibraryDependencyResponse(BaseModel):
    """Schema for library dependency response."""
    dependency_id: uuid.UUID
    library_name: str
    dependency_name: str
    dependency_version: str
    dependency_type: str
    is_installed: bool
    is_compatible: bool
    compatibility_issues: List[str] = Field(default_factory=list)
    installation_time_ms: float = Field(0, ge=0)
    memory_impact_mb: float = Field(0, ge=0)
    cpu_impact_percent: float = Field(0, ge=0, le=100)
    installed_at: datetime


class LibraryInitializationRequest(BaseModel):
    """Schema for library initialization request."""
    library_names: List[str] = Field(..., min_items=1)
    initialization_config: Dict[str, Any] = Field(default_factory=dict)
    force_reinitialize: bool = False
    parallel_initialization: bool = True


class LibraryInitializationResponse(BaseModel):
    """Schema for library initialization response."""
    initialization_results: Dict[str, bool] = Field(default_factory=dict)
    total_libraries: int = Field(0, ge=0)
    successful_initializations: int = Field(0, ge=0)
    failed_initializations: int = Field(0, ge=0)
    initialization_time_ms: float = Field(..., ge=0)
    initialization_errors: Dict[str, str] = Field(default_factory=dict)
    initialized_at: datetime


class LibraryHealthRequest(BaseModel):
    """Schema for library health check request."""
    library_names: Optional[List[str]] = None
    check_type: str = Field("full", regex="^(quick|full|deep)$")
    include_dependencies: bool = True
    include_performance: bool = True
    include_benchmarks: bool = False


class LibraryHealthResponse(BaseModel):
    """Schema for library health check response."""
    library_health: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    overall_health_score: float = Field(..., ge=0, le=100)
    total_libraries: int = Field(0, ge=0)
    healthy_libraries: int = Field(0, ge=0)
    unhealthy_libraries: int = Field(0, ge=0)
    health_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    checked_at: datetime


class LibraryReportRequest(BaseModel):
    """Schema for library report request."""
    report_type: str = Field(..., regex="^(performance|usage|optimization|benchmark|all)$")
    library_names: Optional[List[str]] = None
    time_range_hours: int = Field(24, ge=1, le=168)
    include_recommendations: bool = True
    include_benchmarks: bool = True
    include_optimizations: bool = True


class LibraryReportResponse(BaseModel):
    """Schema for library report response."""
    report_id: uuid.UUID
    report_name: str
    report_type: str
    report_period_start: datetime
    report_period_end: datetime
    total_libraries: int = Field(0, ge=0)
    active_libraries: int = Field(0, ge=0)
    avg_performance_score: float = Field(0, ge=0, le=100)
    avg_memory_usage_mb: float = Field(0, ge=0)
    avg_cpu_usage_percent: float = Field(0, ge=0, le=100)
    total_optimizations: int = Field(0, ge=0)
    total_benchmarks: int = Field(0, ge=0)
    performance_summary: Dict[str, Any] = Field(default_factory=dict)
    usage_summary: Dict[str, Any] = Field(default_factory=dict)
    optimization_summary: Dict[str, Any] = Field(default_factory=dict)
    benchmark_summary: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime


class LibraryAlertRequest(BaseModel):
    """Schema for library alert request."""
    library_name: str = Field(..., min_length=1, max_length=200)
    alert_type: str = Field(..., regex="^(performance|memory|error|dependency)$")
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    threshold_value: Optional[float] = None
    alert_message: str = Field(..., min_length=1)
    is_active: bool = True


class LibraryAlertResponse(BaseModel):
    """Schema for library alert response."""
    alert_id: uuid.UUID
    library_name: str
    alert_type: str
    severity: str
    alert_message: str
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    alert_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class LibraryComparisonRequest(BaseModel):
    """Schema for library comparison request."""
    library_names: List[str] = Field(..., min_items=2, max_items=10)
    comparison_type: str = Field(..., regex="^(performance|memory|accuracy|speed|all)$")
    test_data_size: int = Field(1000, ge=1, le=1000000)
    iterations: int = Field(100, ge=1, le=10000)
    include_benchmarks: bool = True
    include_optimizations: bool = True


class LibraryComparisonResponse(BaseModel):
    """Schema for library comparison response."""
    comparison_id: uuid.UUID
    library_names: List[str]
    comparison_type: str
    test_data_size: int
    iterations: int
    comparison_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    performance_ranking: List[Dict[str, Any]] = Field(default_factory=list)
    memory_ranking: List[Dict[str, Any]] = Field(default_factory=list)
    speed_ranking: List[Dict[str, Any]] = Field(default_factory=list)
    accuracy_ranking: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    compared_at: datetime


class LibraryExportRequest(BaseModel):
    """Schema for library export request."""
    export_type: str = Field(..., regex="^(libraries|performance|usage|benchmarks|all)$")
    library_names: Optional[List[str]] = None
    format: str = Field(..., regex="^(json|csv|excel|parquet)$")
    time_range_hours: int = Field(24, ge=1, le=168)
    include_metadata: bool = True
    compression: bool = True


class LibraryExportResponse(BaseModel):
    """Schema for library export response."""
    export_id: uuid.UUID
    export_type: str
    format: str
    file_size_mb: float = Field(..., ge=0)
    total_records: int = Field(..., ge=0)
    download_url: str
    expires_at: datetime
    exported_at: datetime


class LibraryUpdateRequest(BaseModel):
    """Schema for library update request."""
    library_name: str = Field(..., min_length=1, max_length=200)
    update_type: str = Field(..., regex="^(version|configuration|optimization|all)$")
    new_version: Optional[str] = None
    new_configuration: Optional[Dict[str, Any]] = None
    optimization_settings: Optional[Dict[str, Any]] = None
    force_update: bool = False


class LibraryUpdateResponse(BaseModel):
    """Schema for library update response."""
    update_id: uuid.UUID
    library_name: str
    update_type: str
    update_status: str = Field(..., regex="^(success|failed|partial)$")
    old_version: Optional[str] = None
    new_version: Optional[str] = None
    update_time_ms: float = Field(..., ge=0)
    update_errors: List[str] = Field(default_factory=list)
    update_warnings: List[str] = Field(default_factory=list)
    updated_at: datetime


class LibraryStatusResponse(BaseModel):
    """Schema for library status response."""
    library_name: str
    status: str = Field(..., regex="^(active|inactive|error|unknown)$")
    is_initialized: bool
    version: str
    category: str
    capabilities: List[str] = Field(default_factory=list)
    memory_usage_mb: float = Field(0, ge=0)
    cpu_usage_percent: float = Field(0, ge=0, le=100)
    last_used: Optional[datetime] = None
    health_score: float = Field(0, ge=0, le=100)
    performance_score: float = Field(0, ge=0, le=100)
    optimization_level: str = Field(..., regex="^(basic|advanced|ultra_fast)$")
    status_checked_at: datetime




