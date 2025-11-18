"""
Performance routes following functional patterns
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.user import User
from app.schemas.performance import (
    PerformanceOptimizationRequest, PerformanceOptimizationResponse,
    PerformanceReportResponse, PerformanceSearchRequest, PerformanceStatsResponse,
    PerformanceComparisonRequest, PerformanceComparisonResponse,
    PerformanceThresholdRequest, PerformanceThresholdResponse,
    PerformanceBenchmarkRequest, PerformanceBenchmarkResponse,
    PerformanceLoadTestRequest, PerformanceLoadTestResponse,
    PerformanceMonitoringRequest, PerformanceMonitoringResponse,
    PerformanceDashboardResponse, PerformanceExportRequest,
    PerformanceExportResponse, PerformanceCleanupRequest,
    PerformanceCleanupResponse
)
from app.services.performance_service import (
    get_performance_metrics, get_performance_alerts, optimize_performance,
    get_performance_report, clear_performance_data, performance_monitor,
    memory_monitor, cache_optimization, rate_limit, circuit_breaker
)

router = APIRouter()


@router.get("/metrics/", response_model=Dict[str, Any])
async def get_performance_metrics_endpoint(
    operation_name: Optional[str] = Query(None, description="Filter by operation name"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get performance metrics."""
    try:
        return await get_performance_metrics(operation_name, start_time, end_time, db)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get performance metrics: {str(e)}")


@router.get("/alerts/", response_model=List[Dict[str, Any]])
async def get_performance_alerts_endpoint(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get performance alerts."""
    try:
        return await get_performance_alerts(severity, start_time, end_time)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get performance alerts: {str(e)}")


@router.post("/optimize", response_model=PerformanceOptimizationResponse)
async def optimize_system_performance(
    optimization_request: PerformanceOptimizationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PerformanceOptimizationResponse:
    """Optimize system performance."""
    try:
        result = await optimize_performance(optimization_request, db)
        return PerformanceOptimizationResponse(**result)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to optimize performance: {str(e)}")


@router.get("/report/", response_model=PerformanceReportResponse)
async def get_performance_report_endpoint(
    start_time: Optional[datetime] = Query(None, description="Report start time"),
    end_time: Optional[datetime] = Query(None, description="Report end time"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PerformanceReportResponse:
    """Get comprehensive performance report."""
    try:
        return await get_performance_report(start_time, end_time, db)
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get performance report: {str(e)}")


@router.get("/stats/", response_model=PerformanceStatsResponse)
async def get_performance_stats(
    operation_name: Optional[str] = Query(None, description="Filter by operation name"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PerformanceStatsResponse:
    """Get performance statistics."""
    try:
        metrics = await get_performance_metrics(operation_name, start_time, end_time, db)
        
        return PerformanceStatsResponse(
            total_operations=metrics.get("total_calls", 0),
            total_calls=metrics.get("total_calls", 0),
            avg_duration_ms=metrics.get("avg_duration_ms", 0),
            max_duration_ms=metrics.get("max_duration_ms", 0),
            min_duration_ms=metrics.get("min_duration_ms", 0),
            p95_duration_ms=metrics.get("p95_duration_ms", 0),
            p99_duration_ms=metrics.get("p99_duration_ms", 0),
            success_rate=metrics.get("success_rate", 0),
            error_rate=100 - metrics.get("success_rate", 0),
            memory_usage_mb=0,  # Would be calculated from actual metrics
            cpu_usage_percent=0  # Would be calculated from actual metrics
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get performance stats: {str(e)}")


@router.post("/compare", response_model=PerformanceComparisonResponse)
async def compare_performance(
    comparison_request: PerformanceComparisonRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PerformanceComparisonResponse:
    """Compare performance between two time periods."""
    try:
        # Get baseline metrics
        baseline_metrics = await get_performance_metrics(
            comparison_request.operation_name,
            comparison_request.baseline_start,
            comparison_request.baseline_end,
            db
        )
        
        # Get comparison metrics
        comparison_metrics = await get_performance_metrics(
            comparison_request.operation_name,
            comparison_request.comparison_start,
            comparison_request.comparison_end,
            db
        )
        
        # Calculate improvements and regressions
        improvements = {}
        regressions = {}
        
        for metric in comparison_request.metrics:
            baseline_value = baseline_metrics.get(metric, 0)
            comparison_value = comparison_metrics.get(metric, 0)
            
            if metric in ["duration_ms", "error_rate"]:
                # Lower is better
                if comparison_value < baseline_value:
                    improvements[metric] = {
                        "baseline": baseline_value,
                        "comparison": comparison_value,
                        "improvement": baseline_value - comparison_value,
                        "improvement_percent": ((baseline_value - comparison_value) / baseline_value * 100) if baseline_value > 0 else 0
                    }
                elif comparison_value > baseline_value:
                    regressions[metric] = {
                        "baseline": baseline_value,
                        "comparison": comparison_value,
                        "regression": comparison_value - baseline_value,
                        "regression_percent": ((comparison_value - baseline_value) / baseline_value * 100) if baseline_value > 0 else 0
                    }
            else:
                # Higher is better
                if comparison_value > baseline_value:
                    improvements[metric] = {
                        "baseline": baseline_value,
                        "comparison": comparison_value,
                        "improvement": comparison_value - baseline_value,
                        "improvement_percent": ((comparison_value - baseline_value) / baseline_value * 100) if baseline_value > 0 else 0
                    }
                elif comparison_value < baseline_value:
                    regressions[metric] = {
                        "baseline": baseline_value,
                        "comparison": comparison_value,
                        "regression": baseline_value - comparison_value,
                        "regression_percent": ((baseline_value - comparison_value) / baseline_value * 100) if baseline_value > 0 else 0
                    }
        
        # Determine overall change
        if len(improvements) > len(regressions):
            overall_change = "improved"
        elif len(regressions) > len(improvements):
            overall_change = "degraded"
        else:
            overall_change = "unchanged"
        
        return PerformanceComparisonResponse(
            operation_name=comparison_request.operation_name,
            baseline_period=baseline_metrics,
            comparison_period=comparison_metrics,
            improvements=improvements,
            regressions=regressions,
            overall_change=overall_change
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to compare performance: {str(e)}")


@router.post("/benchmark", response_model=PerformanceBenchmarkResponse)
async def run_performance_benchmark(
    benchmark_request: PerformanceBenchmarkRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PerformanceBenchmarkResponse:
    """Run performance benchmark."""
    try:
        # This would implement actual benchmarking
        # For now, returning placeholder data
        results = {
            "iterations": benchmark_request.iterations,
            "warmup_iterations": benchmark_request.warmup_iterations,
            "concurrent_requests": benchmark_request.concurrent_requests,
            "avg_duration_ms": 150.5,
            "min_duration_ms": 120.0,
            "max_duration_ms": 200.0,
            "p95_duration_ms": 180.0,
            "p99_duration_ms": 195.0,
            "throughput_per_second": 6.7,
            "success_rate": 99.5
        }
        
        summary = {
            "total_time_seconds": benchmark_request.iterations * 0.15,
            "operations_per_second": 6.7,
            "average_latency_ms": 150.5,
            "error_rate": 0.5
        }
        
        return PerformanceBenchmarkResponse(
            operation_name=benchmark_request.operation_name,
            iterations=benchmark_request.iterations,
            warmup_iterations=benchmark_request.warmup_iterations,
            concurrent_requests=benchmark_request.concurrent_requests,
            results=results,
            summary=summary,
            completed_at=datetime.utcnow()
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to run benchmark: {str(e)}")


@router.post("/load-test", response_model=PerformanceLoadTestResponse)
async def run_load_test(
    load_test_request: PerformanceLoadTestRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PerformanceLoadTestResponse:
    """Run load test."""
    try:
        # This would implement actual load testing
        # For now, returning placeholder data
        test_id = uuid.uuid4()
        
        return PerformanceLoadTestResponse(
            test_id=test_id,
            test_name=load_test_request.test_name,
            status="running",
            results={
                "duration_seconds": load_test_request.duration_seconds,
                "concurrent_users": load_test_request.concurrent_users,
                "ramp_up_seconds": load_test_request.ramp_up_seconds,
                "operations": load_test_request.operations
            },
            started_at=datetime.utcnow()
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to run load test: {str(e)}")


@router.get("/dashboard/", response_model=PerformanceDashboardResponse)
async def get_performance_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PerformanceDashboardResponse:
    """Get performance dashboard data."""
    try:
        # Get system health
        system_health = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "status": "healthy"
        }
        
        # Get recent metrics
        recent_metrics = await get_performance_metrics(None, None, None, db)
        
        # Get active alerts
        active_alerts = await get_performance_alerts()
        
        # Get performance trends (placeholder)
        performance_trends = {
            "duration_trend": "stable",
            "throughput_trend": "increasing",
            "error_rate_trend": "decreasing"
        }
        
        # Get top operations (placeholder)
        top_operations = [
            {"operation": "document_generation", "avg_duration_ms": 150.5, "calls": 1000},
            {"operation": "ai_analysis", "avg_duration_ms": 200.0, "calls": 500},
            {"operation": "user_authentication", "avg_duration_ms": 50.0, "calls": 2000}
        ]
        
        # Generate recommendations
        recommendations = []
        if system_health["cpu_percent"] > 80:
            recommendations.append("High CPU usage detected. Consider scaling.")
        if system_health["memory_percent"] > 80:
            recommendations.append("High memory usage detected. Consider optimization.")
        if len(active_alerts) > 5:
            recommendations.append("Multiple performance alerts require attention.")
        
        return PerformanceDashboardResponse(
            system_health=system_health,
            recent_metrics=recent_metrics,
            active_alerts=active_alerts,
            performance_trends=performance_trends,
            top_operations=top_operations,
            recommendations=recommendations,
            last_updated=datetime.utcnow()
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to get performance dashboard: {str(e)}")


@router.post("/export", response_model=PerformanceExportResponse)
async def export_performance_data(
    export_request: PerformanceExportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PerformanceExportResponse:
    """Export performance data."""
    try:
        # Get performance data
        metrics = await get_performance_metrics(
            export_request.operation_name,
            export_request.start_time,
            export_request.end_time,
            db
        )
        
        # Generate export file
        export_filename = f"performance_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{export_request.format}"
        export_path = os.path.join("exports", export_filename)
        
        # Ensure export directory exists
        os.makedirs("exports", exist_ok=True)
        
        # Write export file
        if export_request.format == "json":
            with open(export_path, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
        elif export_request.format == "csv":
            # Convert to CSV format
            csv_data = convert_metrics_to_csv(metrics)
            with open(export_path, 'w', newline='') as f:
                f.write(csv_data)
        
        return PerformanceExportResponse(
            export_filename=export_filename,
            export_path=export_path,
            total_records=1,  # Would be actual count
            format=export_request.format,
            download_url=f"/api/v1/performance/download/{export_filename}",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to export performance data: {str(e)}")


@router.post("/cleanup", response_model=PerformanceCleanupResponse)
async def cleanup_performance_data(
    cleanup_request: PerformanceCleanupRequest,
    user: User = Depends(get_current_user)
) -> PerformanceCleanupResponse:
    """Cleanup old performance data."""
    try:
        if cleanup_request.dry_run:
            # Simulate cleanup
            deleted_metrics = 100
            deleted_alerts = 50
            deleted_profiles = 10
        else:
            # Actual cleanup
            result = await clear_performance_data(cleanup_request.operation_name)
            deleted_metrics = 100  # Would be actual count
            deleted_alerts = 50    # Would be actual count
            deleted_profiles = 10  # Would be actual count
        
        return PerformanceCleanupResponse(
            deleted_metrics=deleted_metrics,
            deleted_alerts=deleted_alerts,
            deleted_profiles=deleted_profiles,
            total_deleted=deleted_metrics + deleted_alerts + deleted_profiles,
            dry_run=cleanup_request.dry_run,
            completed_at=datetime.utcnow()
        )
    
    except Exception as e:
        raise handle_internal_error(f"Failed to cleanup performance data: {str(e)}")


@router.delete("/data/")
async def clear_performance_data_endpoint(
    operation_name: Optional[str] = Query(None, description="Clear data for specific operation"),
    user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Clear performance data."""
    try:
        result = await clear_performance_data(operation_name)
        return result
    
    except Exception as e:
        raise handle_internal_error(f"Failed to clear performance data: {str(e)}")


@router.get("/health/", response_model=Dict[str, Any])
async def performance_health_check(
    user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Performance system health check."""
    try:
        # Check system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        # Determine health status
        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            status = "critical"
        elif cpu_percent > 80 or memory_percent > 80 or disk_percent > 80:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "active_alerts": len(await get_performance_alerts()),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Helper functions
def convert_metrics_to_csv(metrics: Dict[str, Any]) -> str:
    """Convert metrics to CSV format."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Operation Name', 'Total Calls', 'Avg Duration (ms)', 'Min Duration (ms)',
        'Max Duration (ms)', 'P95 Duration (ms)', 'P99 Duration (ms)', 'Success Rate (%)'
    ])
    
    # Write data
    writer.writerow([
        metrics.get("operation_name", ""),
        metrics.get("total_calls", 0),
        metrics.get("avg_duration_ms", 0),
        metrics.get("min_duration_ms", 0),
        metrics.get("max_duration_ms", 0),
        metrics.get("p95_duration_ms", 0),
        metrics.get("p99_duration_ms", 0),
        metrics.get("success_rate", 0)
    ])
    
    return output.getvalue()




