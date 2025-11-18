"""
Ultra-fast schemas for Pydantic validation
"""
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class UltraFastResponse(BaseModel):
    """Schema for ultra-fast response."""
    response_time_ms: float = Field(..., ge=0)
    optimization_level: str = Field(..., regex="^(basic|advanced|ultra_fast)$")
    cache_hit: bool = False
    parallel_operations: int = Field(0, ge=0)
    jit_compiled: bool = False
    memory_optimized: bool = False
    result: Any = None


class UltraFastStatsResponse(BaseModel):
    """Schema for ultra-fast statistics response."""
    function_name: str
    hits: int = Field(0, ge=0)
    misses: int = Field(0, ge=0)
    hit_rate: float = Field(0, ge=0, le=100)
    avg_response_time_ms: float = Field(0, ge=0)
    total_requests: int = Field(0, ge=0)
    speed_improvement: float = Field(0, ge=0)


class UltraFastOptimizationResponse(BaseModel):
    """Schema for ultra-fast optimization response."""
    optimizations: List[Dict[str, Any]] = Field(default_factory=list)
    total_optimizations: int = Field(0, ge=0)
    speed_improvement_percent: float = Field(0, ge=0)
    optimized_at: datetime


class UltraFastAnalysisResponse(BaseModel):
    """Schema for ultra-fast analysis response."""
    total_functions: int = Field(0, ge=0)
    avg_response_time_ms: float = Field(0, ge=0)
    avg_hit_rate: float = Field(0, ge=0, le=100)
    total_optimizations: int = Field(0, ge=0)
    performance_score: float = Field(0, ge=0, le=100)
    speed_improvements: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    analyzed_at: datetime


class UltraFastPerformanceResponse(BaseModel):
    """Schema for ultra-fast performance response."""
    performance_score: float = Field(..., ge=0, le=100)
    total_functions: int = Field(0, ge=0)
    avg_response_time_ms: float = Field(0, ge=0)
    avg_hit_rate: float = Field(0, ge=0, le=100)
    ultra_fast_stats: Dict[str, UltraFastStatsResponse] = Field(default_factory=dict)
    optimization_recommendations: UltraFastOptimizationResponse
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime


class UltraFastBenchmarkRequest(BaseModel):
    """Schema for ultra-fast benchmark request."""
    benchmark_name: str = Field(..., min_length=1, max_length=200)
    benchmark_type: str = Field(..., regex="^(speed|memory|cpu|cache|parallel|jit)$")
    iterations: int = Field(1000, ge=1, le=100000)
    optimization_level: str = Field("ultra_fast", regex="^(none|basic|advanced|ultra_fast)$")
    test_data_size: int = Field(1000, ge=1, le=1000000)
    parallel_workers: int = Field(4, ge=1, le=32)


class UltraFastBenchmarkResponse(BaseModel):
    """Schema for ultra-fast benchmark response."""
    benchmark_id: uuid.UUID
    benchmark_name: str
    benchmark_type: str
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
    optimization_level: str
    speed_improvement_percent: float = Field(0, ge=0)
    completed_at: datetime


class UltraFastCacheRequest(BaseModel):
    """Schema for ultra-fast cache request."""
    cache_key: str = Field(..., min_length=1, max_length=500)
    cache_value: Any = None
    ttl_seconds: float = Field(1.0, ge=0.001, le=3600)
    cache_type: str = Field("memory", regex="^(memory|redis|memcached)$")
    optimization_level: str = Field("ultra_fast", regex="^(basic|advanced|ultra_fast)$")


class UltraFastCacheResponse(BaseModel):
    """Schema for ultra-fast cache response."""
    cache_key: str
    cache_value: Any = None
    cache_hit: bool = False
    access_time_ms: float = Field(..., ge=0)
    ttl_seconds: float = Field(..., ge=0)
    cache_type: str
    optimization_level: str
    cached_at: datetime


class UltraFastParallelRequest(BaseModel):
    """Schema for ultra-fast parallel processing request."""
    operation_type: str = Field(..., regex="^(document_generation|search|analytics|processing)$")
    data_items: List[Any] = Field(..., min_items=1, max_items=1000)
    parallel_workers: int = Field(4, ge=1, le=32)
    optimization_level: str = Field("ultra_fast", regex="^(basic|advanced|ultra_fast)$")
    use_jit: bool = True
    use_cache: bool = True


class UltraFastParallelResponse(BaseModel):
    """Schema for ultra-fast parallel processing response."""
    operation_type: str
    total_items: int = Field(..., ge=0)
    processed_items: int = Field(..., ge=0)
    parallel_workers: int = Field(..., ge=0)
    total_time_ms: float = Field(..., ge=0)
    avg_time_per_item_ms: float = Field(..., ge=0)
    throughput_items_per_sec: float = Field(..., ge=0)
    speed_improvement_percent: float = Field(0, ge=0)
    optimization_level: str
    results: List[Any] = Field(default_factory=list)
    completed_at: datetime


class UltraFastJITRequest(BaseModel):
    """Schema for ultra-fast JIT compilation request."""
    function_name: str = Field(..., min_length=1, max_length=200)
    function_code: str = Field(..., min_length=1)
    compilation_type: str = Field("numba", regex="^(numba|cython|pypy)$")
    optimization_level: str = Field("aggressive", regex="^(conservative|moderate|aggressive)$")
    cache_compilation: bool = True
    parallel_compilation: bool = True


class UltraFastJITResponse(BaseModel):
    """Schema for ultra-fast JIT compilation response."""
    function_name: str
    compilation_type: str
    compilation_time_ms: float = Field(..., ge=0)
    optimization_level: str
    cache_compilation: bool
    parallel_compilation: bool
    compilation_success: bool
    performance_improvement_percent: float = Field(0, ge=0)
    compiled_at: datetime


class UltraFastMemoryRequest(BaseModel):
    """Schema for ultra-fast memory optimization request."""
    optimization_type: str = Field(..., regex="^(numpy|pandas|cache|gc|allocation)$")
    target_memory_mb: float = Field(100, ge=1, le=10000)
    optimization_level: str = Field("aggressive", regex="^(conservative|moderate|aggressive)$")
    use_memory_mapping: bool = True
    use_compression: bool = True


class UltraFastMemoryResponse(BaseModel):
    """Schema for ultra-fast memory optimization response."""
    optimization_type: str
    before_memory_mb: float = Field(..., ge=0)
    after_memory_mb: float = Field(..., ge=0)
    memory_saved_mb: float = Field(..., ge=0)
    memory_improvement_percent: float = Field(..., ge=0)
    optimization_level: str
    use_memory_mapping: bool
    use_compression: bool
    optimization_time_ms: float = Field(..., ge=0)
    optimized_at: datetime


class UltraFastAlertRequest(BaseModel):
    """Schema for ultra-fast alert request."""
    alert_type: str = Field(..., regex="^(slow_response|high_memory|low_hit_rate|high_cpu|cache_miss)$")
    threshold_value: float = Field(..., ge=0)
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    function_name: Optional[str] = None
    is_active: bool = True
    notification_methods: List[str] = Field(default_factory=list)


class UltraFastAlertResponse(BaseModel):
    """Schema for ultra-fast alert response."""
    id: uuid.UUID
    alert_type: str
    threshold_value: float
    severity: str
    function_name: Optional[str] = None
    is_active: bool
    notification_methods: List[str] = Field(default_factory=list)
    created_at: datetime


class UltraFastReportRequest(BaseModel):
    """Schema for ultra-fast report request."""
    report_type: str = Field(..., regex="^(performance|optimization|benchmark|analysis)$")
    time_range_hours: int = Field(24, ge=1, le=168)
    include_recommendations: bool = True
    include_benchmarks: bool = True
    include_alerts: bool = True


class UltraFastReportResponse(BaseModel):
    """Schema for ultra-fast report response."""
    report_id: uuid.UUID
    report_type: str
    time_range_hours: int
    performance_summary: Dict[str, Any] = Field(default_factory=dict)
    optimization_summary: Dict[str, Any] = Field(default_factory=dict)
    benchmark_summary: Dict[str, Any] = Field(default_factory=dict)
    alert_summary: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime


class UltraFastHealthRequest(BaseModel):
    """Schema for ultra-fast health check request."""
    check_type: str = Field("full", regex="^(quick|full|deep)$")
    include_benchmarks: bool = False
    include_optimizations: bool = True
    include_alerts: bool = True


class UltraFastHealthResponse(BaseModel):
    """Schema for ultra-fast health check response."""
    status: str = Field(..., regex="^(healthy|warning|critical|unknown)$")
    performance_score: float = Field(..., ge=0, le=100)
    avg_response_time_ms: float = Field(..., ge=0)
    cache_hit_rate: float = Field(..., ge=0, le=100)
    memory_usage_mb: float = Field(..., ge=0)
    cpu_usage_percent: float = Field(..., ge=0)
    active_optimizations: int = Field(0, ge=0)
    active_alerts: int = Field(0, ge=0)
    health_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    checked_at: datetime


class UltraFastExportRequest(BaseModel):
    """Schema for ultra-fast export request."""
    export_type: str = Field(..., regex="^(stats|benchmarks|optimizations|alerts)$")
    format: str = Field(..., regex="^(json|csv|excel|parquet)$")
    time_range_hours: int = Field(24, ge=1, le=168)
    include_metadata: bool = True
    compression: bool = True


class UltraFastExportResponse(BaseModel):
    """Schema for ultra-fast export response."""
    export_id: uuid.UUID
    export_type: str
    format: str
    file_size_mb: float = Field(..., ge=0)
    total_records: int = Field(..., ge=0)
    download_url: str
    expires_at: datetime
    exported_at: datetime




