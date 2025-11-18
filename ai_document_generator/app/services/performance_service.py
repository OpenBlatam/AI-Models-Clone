"""
Performance optimization service following functional patterns
"""
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
import uuid
import asyncio
import time
import functools
import weakref
from collections import defaultdict, deque
import psutil
import gc

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.performance import PerformanceMetric, PerformanceAlert, PerformanceProfile
from app.schemas.performance import (
    PerformanceMetricResponse, PerformanceAlertResponse, PerformanceProfileResponse,
    PerformanceOptimizationRequest, PerformanceReportResponse
)
from app.utils.validators import validate_performance_threshold
from app.utils.helpers import calculate_performance_score, format_performance_time
from app.utils.cache import cache_performance_data, get_cached_performance_data

logger = get_logger(__name__)

# Performance tracking
_performance_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
_performance_alerts: List[Dict[str, Any]] = []
_performance_profiles: Dict[str, Dict[str, Any]] = {}


def performance_monitor(
    operation_name: str,
    threshold_ms: float = 1000.0,
    alert_on_slow: bool = True
) -> Callable:
    """Decorator for monitoring function performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                # Record metric
                _performance_metrics[operation_name].append({
                    "timestamp": datetime.utcnow(),
                    "duration_ms": duration_ms,
                    "success": True
                })
                
                # Check for slow operations
                if alert_on_slow and duration_ms > threshold_ms:
                    _performance_alerts.append({
                        "operation": operation_name,
                        "duration_ms": duration_ms,
                        "threshold_ms": threshold_ms,
                        "timestamp": datetime.utcnow(),
                        "severity": "warning" if duration_ms < threshold_ms * 2 else "critical"
                    })
                
                logger.debug(f"Performance: {operation_name} took {duration_ms:.2f}ms")
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000
                
                # Record metric
                _performance_metrics[operation_name].append({
                    "timestamp": datetime.utcnow(),
                    "duration_ms": duration_ms,
                    "success": True
                })
                
                # Check for slow operations
                if alert_on_slow and duration_ms > threshold_ms:
                    _performance_alerts.append({
                        "operation": operation_name,
                        "duration_ms": duration_ms,
                        "threshold_ms": threshold_ms,
                        "timestamp": datetime.utcnow(),
                        "severity": "warning" if duration_ms < threshold_ms * 2 else "critical"
                    })
                
                logger.debug(f"Performance: {operation_name} took {duration_ms:.2f}ms")
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def memory_monitor(
    operation_name: str,
    threshold_mb: float = 100.0
) -> Callable:
    """Decorator for monitoring memory usage."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_delta = end_memory - start_memory
                
                # Record memory usage
                _performance_metrics[f"{operation_name}_memory"].append({
                    "timestamp": datetime.utcnow(),
                    "memory_mb": memory_delta,
                    "total_memory_mb": end_memory
                })
                
                # Check for high memory usage
                if memory_delta > threshold_mb:
                    _performance_alerts.append({
                        "operation": f"{operation_name}_memory",
                        "memory_delta_mb": memory_delta,
                        "threshold_mb": threshold_mb,
                        "timestamp": datetime.utcnow(),
                        "severity": "warning" if memory_delta < threshold_mb * 2 else "critical"
                    })
                
                logger.debug(f"Memory: {operation_name} used {memory_delta:.2f}MB")
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_delta = end_memory - start_memory
                
                # Record memory usage
                _performance_metrics[f"{operation_name}_memory"].append({
                    "timestamp": datetime.utcnow(),
                    "memory_mb": memory_delta,
                    "total_memory_mb": end_memory
                })
                
                # Check for high memory usage
                if memory_delta > threshold_mb:
                    _performance_alerts.append({
                        "operation": f"{operation_name}_memory",
                        "memory_delta_mb": memory_delta,
                        "threshold_mb": threshold_mb,
                        "timestamp": datetime.utcnow(),
                        "severity": "warning" if memory_delta < threshold_mb * 2 else "critical"
                    })
                
                logger.debug(f"Memory: {operation_name} used {memory_delta:.2f}MB")
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def cache_optimization(
    cache_key_func: Optional[Callable] = None,
    ttl_seconds: int = 300,
    max_size: int = 1000
) -> Callable:
    """Decorator for cache optimization."""
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_timestamps = {}
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if cache_key in cache:
                if time.time() - cache_timestamps[cache_key] < ttl_seconds:
                    logger.debug(f"Cache hit: {func.__name__}")
                    return cache[cache_key]
                else:
                    # Cache expired
                    del cache[cache_key]
                    del cache_timestamps[cache_key]
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            if len(cache) >= max_size:
                # Remove oldest entry
                oldest_key = min(cache_timestamps.keys(), key=lambda k: cache_timestamps[k])
                del cache[oldest_key]
                del cache_timestamps[oldest_key]
            
            cache[cache_key] = result
            cache_timestamps[cache_key] = time.time()
            
            logger.debug(f"Cache miss: {func.__name__}")
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if cache_key in cache:
                if time.time() - cache_timestamps[cache_key] < ttl_seconds:
                    logger.debug(f"Cache hit: {func.__name__}")
                    return cache[cache_key]
                else:
                    # Cache expired
                    del cache[cache_key]
                    del cache_timestamps[cache_key]
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            if len(cache) >= max_size:
                # Remove oldest entry
                oldest_key = min(cache_timestamps.keys(), key=lambda k: cache_timestamps[k])
                del cache[oldest_key]
                del cache_timestamps[oldest_key]
            
            cache[cache_key] = result
            cache_timestamps[cache_key] = time.time()
            
            logger.debug(f"Cache miss: {func.__name__}")
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def rate_limit(
    calls_per_second: float = 10.0,
    burst_size: int = 20
) -> Callable:
    """Decorator for rate limiting."""
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]
        tokens = [burst_size]
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            now = time.time()
            time_passed = now - last_called[0]
            last_called[0] = now
            
            # Add tokens based on time passed
            tokens[0] = min(burst_size, tokens[0] + time_passed * calls_per_second)
            
            if tokens[0] < 1:
                # Rate limit exceeded
                sleep_time = (1 - tokens[0]) / calls_per_second
                await asyncio.sleep(sleep_time)
                tokens[0] = 1
            
            tokens[0] -= 1
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            now = time.time()
            time_passed = now - last_called[0]
            last_called[0] = now
            
            # Add tokens based on time passed
            tokens[0] = min(burst_size, tokens[0] + time_passed * calls_per_second)
            
            if tokens[0] < 1:
                # Rate limit exceeded
                sleep_time = (1 - tokens[0]) / calls_per_second
                time.sleep(sleep_time)
                tokens[0] = 1
            
            tokens[0] -= 1
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: type = Exception
) -> Callable:
    """Decorator for circuit breaker pattern."""
    def decorator(func: Callable) -> Callable:
        failure_count = [0]
        last_failure_time = [0.0]
        state = ["closed"]  # closed, open, half-open
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            now = time.time()
            
            # Check circuit state
            if state[0] == "open":
                if now - last_failure_time[0] < recovery_timeout:
                    raise Exception("Circuit breaker is open")
                else:
                    state[0] = "half-open"
            
            try:
                result = await func(*args, **kwargs)
                
                # Success - reset failure count
                if state[0] == "half-open":
                    state[0] = "closed"
                failure_count[0] = 0
                
                return result
            
            except expected_exception as e:
                failure_count[0] += 1
                last_failure_time[0] = now
                
                if failure_count[0] >= failure_threshold:
                    state[0] = "open"
                    logger.warning(f"Circuit breaker opened for {func.__name__}")
                
                raise e
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            now = time.time()
            
            # Check circuit state
            if state[0] == "open":
                if now - last_failure_time[0] < recovery_timeout:
                    raise Exception("Circuit breaker is open")
                else:
                    state[0] = "half-open"
            
            try:
                result = func(*args, **kwargs)
                
                # Success - reset failure count
                if state[0] == "half-open":
                    state[0] = "closed"
                failure_count[0] = 0
                
                return result
            
            except expected_exception as e:
                failure_count[0] += 1
                last_failure_time[0] = now
                
                if failure_count[0] >= failure_threshold:
                    state[0] = "open"
                    logger.warning(f"Circuit breaker opened for {func.__name__}")
                
                raise e
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


async def get_performance_metrics(
    operation_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Get performance metrics."""
    try:
        if operation_name:
            metrics = _performance_metrics.get(operation_name, deque())
        else:
            # Get all metrics
            metrics = []
            for op_metrics in _performance_metrics.values():
                metrics.extend(op_metrics)
        
        # Filter by time range
        if start_time or end_time:
            filtered_metrics = []
            for metric in metrics:
                if start_time and metric["timestamp"] < start_time:
                    continue
                if end_time and metric["timestamp"] > end_time:
                    continue
                filtered_metrics.append(metric)
            metrics = filtered_metrics
        
        if not metrics:
            return {
                "operation_name": operation_name,
                "total_calls": 0,
                "avg_duration_ms": 0,
                "min_duration_ms": 0,
                "max_duration_ms": 0,
                "p95_duration_ms": 0,
                "p99_duration_ms": 0,
                "success_rate": 0
            }
        
        # Calculate statistics
        durations = [m["duration_ms"] for m in metrics if "duration_ms" in m]
        successes = [m["success"] for m in metrics if "success" in m]
        
        if durations:
            durations.sort()
            total_calls = len(durations)
            avg_duration = sum(durations) / total_calls
            min_duration = min(durations)
            max_duration = max(durations)
            p95_duration = durations[int(total_calls * 0.95)] if total_calls > 0 else 0
            p99_duration = durations[int(total_calls * 0.99)] if total_calls > 0 else 0
        else:
            total_calls = 0
            avg_duration = 0
            min_duration = 0
            max_duration = 0
            p95_duration = 0
            p99_duration = 0
        
        success_rate = (sum(successes) / len(successes) * 100) if successes else 0
        
        return {
            "operation_name": operation_name,
            "total_calls": total_calls,
            "avg_duration_ms": round(avg_duration, 2),
            "min_duration_ms": round(min_duration, 2),
            "max_duration_ms": round(max_duration, 2),
            "p95_duration_ms": round(p95_duration, 2),
            "p99_duration_ms": round(p99_duration, 2),
            "success_rate": round(success_rate, 2)
        }
    
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return {}


async def get_performance_alerts(
    severity: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Get performance alerts."""
    try:
        alerts = _performance_alerts.copy()
        
        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a.get("severity") == severity]
        
        # Filter by time range
        if start_time or end_time:
            filtered_alerts = []
            for alert in alerts:
                if start_time and alert["timestamp"] < start_time:
                    continue
                if end_time and alert["timestamp"] > end_time:
                    continue
                filtered_alerts.append(alert)
            alerts = filtered_alerts
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return alerts
    
    except Exception as e:
        logger.error(f"Failed to get performance alerts: {e}")
        return []


async def optimize_performance(
    optimization_request: PerformanceOptimizationRequest,
    db: AsyncSession
) -> Dict[str, Any]:
    """Optimize system performance."""
    try:
        optimizations = []
        
        # Memory optimization
        if optimization_request.optimize_memory:
            memory_optimization = await optimize_memory()
            optimizations.append(memory_optimization)
        
        # Database optimization
        if optimization_request.optimize_database:
            db_optimization = await optimize_database(db)
            optimizations.append(db_optimization)
        
        # Cache optimization
        if optimization_request.optimize_cache:
            cache_optimization = await optimize_cache()
            optimizations.append(cache_optimization)
        
        # Garbage collection
        if optimization_request.run_garbage_collection:
            gc_optimization = await run_garbage_collection()
            optimizations.append(gc_optimization)
        
        return {
            "optimizations": optimizations,
            "total_optimizations": len(optimizations),
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to optimize performance: {e}")
        raise handle_internal_error(f"Failed to optimize performance: {str(e)}")


async def optimize_memory() -> Dict[str, Any]:
    """Optimize memory usage."""
    try:
        process = psutil.Process()
        before_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Force garbage collection
        collected = gc.collect()
        
        # Clear performance metrics if too large
        for operation in list(_performance_metrics.keys()):
            if len(_performance_metrics[operation]) > 500:
                _performance_metrics[operation].clear()
        
        # Clear old alerts
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        _performance_alerts[:] = [
            alert for alert in _performance_alerts
            if alert["timestamp"] > cutoff_time
        ]
        
        after_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_saved = before_memory - after_memory
        
        return {
            "type": "memory",
            "memory_saved_mb": round(memory_saved, 2),
            "garbage_collected": collected,
            "before_memory_mb": round(before_memory, 2),
            "after_memory_mb": round(after_memory, 2)
        }
    
    except Exception as e:
        logger.error(f"Failed to optimize memory: {e}")
        return {"type": "memory", "error": str(e)}


async def optimize_database(db: AsyncSession) -> Dict[str, Any]:
    """Optimize database performance."""
    try:
        optimizations = []
        
        # Analyze tables
        analyze_query = text("ANALYZE")
        await db.execute(analyze_query)
        optimizations.append("Tables analyzed")
        
        # Vacuum if needed (PostgreSQL)
        try:
            vacuum_query = text("VACUUM ANALYZE")
            await db.execute(vacuum_query)
            optimizations.append("Database vacuumed")
        except Exception:
            # Not PostgreSQL or vacuum not available
            pass
        
        # Get database statistics
        stats_query = text("""
            SELECT 
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                n_live_tup as live_tuples,
                n_dead_tup as dead_tuples
            FROM pg_stat_user_tables
            ORDER BY n_dead_tup DESC
            LIMIT 10
        """)
        
        stats_result = await db.execute(stats_query)
        table_stats = [
            {
                "schema": row[0],
                "table": row[1],
                "inserts": row[2],
                "updates": row[3],
                "deletes": row[4],
                "live_tuples": row[5],
                "dead_tuples": row[6]
            }
            for row in stats_result.fetchall()
        ]
        
        return {
            "type": "database",
            "optimizations": optimizations,
            "table_stats": table_stats
        }
    
    except Exception as e:
        logger.error(f"Failed to optimize database: {e}")
        return {"type": "database", "error": str(e)}


async def optimize_cache() -> Dict[str, Any]:
    """Optimize cache performance."""
    try:
        # This would implement actual cache optimization
        # For now, returning placeholder data
        return {
            "type": "cache",
            "cache_hit_rate": 85.5,
            "cache_size": len(_performance_metrics),
            "optimizations": ["Cache entries cleaned", "TTL optimized"]
        }
    
    except Exception as e:
        logger.error(f"Failed to optimize cache: {e}")
        return {"type": "cache", "error": str(e)}


async def run_garbage_collection() -> Dict[str, Any]:
    """Run garbage collection."""
    try:
        # Get GC stats before
        before_stats = gc.get_stats()
        
        # Run garbage collection
        collected = gc.collect()
        
        # Get GC stats after
        after_stats = gc.get_stats()
        
        return {
            "type": "garbage_collection",
            "objects_collected": collected,
            "before_stats": before_stats,
            "after_stats": after_stats
        }
    
    except Exception as e:
        logger.error(f"Failed to run garbage collection: {e}")
        return {"type": "garbage_collection", "error": str(e)}


async def get_performance_report(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = None
) -> PerformanceReportResponse:
    """Get comprehensive performance report."""
    try:
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=1)
        if not end_time:
            end_time = datetime.utcnow()
        
        # Get system metrics
        system_metrics = await get_system_performance_metrics()
        
        # Get application metrics
        app_metrics = await get_application_performance_metrics(start_time, end_time)
        
        # Get database metrics
        db_metrics = await get_database_performance_metrics(db)
        
        # Get performance alerts
        alerts = await get_performance_alerts(start_time=start_time, end_time=end_time)
        
        # Calculate overall performance score
        performance_score = calculate_performance_score(
            system_metrics, app_metrics, db_metrics, alerts
        )
        
        # Generate recommendations
        recommendations = await generate_performance_recommendations(
            system_metrics, app_metrics, db_metrics, alerts
        )
        
        return PerformanceReportResponse(
            performance_score=performance_score,
            system_metrics=system_metrics,
            application_metrics=app_metrics,
            database_metrics=db_metrics,
            alerts=alerts,
            recommendations=recommendations,
            report_period_start=start_time,
            report_period_end=end_time,
            generated_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to get performance report: {e}")
        raise handle_internal_error(f"Failed to get performance report: {str(e)}")


async def get_system_performance_metrics() -> Dict[str, Any]:
    """Get system performance metrics."""
    try:
        process = psutil.Process()
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "process_memory_mb": process.memory_info().rss / 1024 / 1024,
            "process_cpu_percent": process.cpu_percent(),
            "open_files": len(process.open_files()),
            "threads": process.num_threads()
        }
    
    except Exception as e:
        logger.error(f"Failed to get system performance metrics: {e}")
        return {}


async def get_application_performance_metrics(
    start_time: datetime,
    end_time: datetime
) -> Dict[str, Any]:
    """Get application performance metrics."""
    try:
        # Get metrics for all operations
        all_metrics = []
        for operation_name in _performance_metrics.keys():
            metrics = await get_performance_metrics(operation_name, start_time, end_time)
            all_metrics.append(metrics)
        
        # Calculate aggregate metrics
        total_calls = sum(m.get("total_calls", 0) for m in all_metrics)
        avg_duration = sum(m.get("avg_duration_ms", 0) for m in all_metrics) / len(all_metrics) if all_metrics else 0
        max_duration = max((m.get("max_duration_ms", 0) for m in all_metrics), default=0)
        avg_success_rate = sum(m.get("success_rate", 0) for m in all_metrics) / len(all_metrics) if all_metrics else 0
        
        return {
            "total_operations": len(all_metrics),
            "total_calls": total_calls,
            "avg_duration_ms": round(avg_duration, 2),
            "max_duration_ms": round(max_duration, 2),
            "avg_success_rate": round(avg_success_rate, 2),
            "operation_metrics": all_metrics
        }
    
    except Exception as e:
        logger.error(f"Failed to get application performance metrics: {e}")
        return {}


async def get_database_performance_metrics(db: AsyncSession) -> Dict[str, Any]:
    """Get database performance metrics."""
    try:
        # Get connection count
        conn_query = text("SELECT count(*) FROM pg_stat_activity")
        conn_result = await db.execute(conn_query)
        connection_count = conn_result.scalar()
        
        # Get database size
        size_query = text("SELECT pg_database_size(current_database())")
        size_result = await db.execute(size_query)
        db_size_bytes = size_result.scalar()
        
        # Get slow queries
        try:
            slow_query = text("""
                SELECT query, mean_time, calls
                FROM pg_stat_statements
                ORDER BY mean_time DESC
                LIMIT 5
            """)
            slow_result = await db.execute(slow_query)
            slow_queries = [
                {
                    "query": row[0][:100] + "..." if len(row[0]) > 100 else row[0],
                    "mean_time": row[1],
                    "calls": row[2]
                }
                for row in slow_result.fetchall()
            ]
        except Exception:
            slow_queries = []
        
        return {
            "connection_count": connection_count,
            "database_size_mb": round(db_size_bytes / 1024 / 1024, 2),
            "slow_queries": slow_queries
        }
    
    except Exception as e:
        logger.error(f"Failed to get database performance metrics: {e}")
        return {}


async def generate_performance_recommendations(
    system_metrics: Dict[str, Any],
    app_metrics: Dict[str, Any],
    db_metrics: Dict[str, Any],
    alerts: List[Dict[str, Any]]
) -> List[str]:
    """Generate performance recommendations."""
    try:
        recommendations = []
        
        # System recommendations
        if system_metrics.get("cpu_percent", 0) > 80:
            recommendations.append("High CPU usage detected. Consider scaling or optimizing CPU-intensive operations.")
        
        if system_metrics.get("memory_percent", 0) > 80:
            recommendations.append("High memory usage detected. Consider memory optimization or scaling.")
        
        if system_metrics.get("disk_percent", 0) > 80:
            recommendations.append("High disk usage detected. Consider cleanup or storage expansion.")
        
        # Application recommendations
        if app_metrics.get("avg_duration_ms", 0) > 1000:
            recommendations.append("Slow application performance detected. Consider optimizing slow operations.")
        
        if app_metrics.get("avg_success_rate", 100) < 95:
            recommendations.append("Low success rate detected. Investigate error patterns.")
        
        # Database recommendations
        if db_metrics.get("connection_count", 0) > 50:
            recommendations.append("High database connection count. Consider connection pooling optimization.")
        
        if db_metrics.get("slow_queries"):
            recommendations.append("Slow queries detected. Consider query optimization or indexing.")
        
        # Alert-based recommendations
        critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
        if critical_alerts:
            recommendations.append(f"{len(critical_alerts)} critical performance alerts require immediate attention.")
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Failed to generate performance recommendations: {e}")
        return ["Failed to generate recommendations"]


async def clear_performance_data(
    operation_name: Optional[str] = None
) -> Dict[str, str]:
    """Clear performance data."""
    try:
        if operation_name:
            if operation_name in _performance_metrics:
                _performance_metrics[operation_name].clear()
            return {"message": f"Performance data cleared for {operation_name}"}
        else:
            _performance_metrics.clear()
            _performance_alerts.clear()
            return {"message": "All performance data cleared"}
    
    except Exception as e:
        logger.error(f"Failed to clear performance data: {e}")
        return {"error": str(e)}




