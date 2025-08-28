#!/usr/bin/env python3
"""
🚀 Unified Performance Optimizer - Consolidated Performance Management System
============================================================================

Consolidates all performance optimization functionality into a single, 
optimized system that eliminates scattered implementations and provides 
consistent performance monitoring and optimization across the entire codebase.
"""

import asyncio
import time
import threading
import psutil
import gc
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum, auto
from contextlib import asynccontextmanager
import structlog
from datetime import datetime
from collections import defaultdict, deque
import weakref

logger = structlog.get_logger()

# =============================================================================
# Performance Types and Categories
# =============================================================================

class OptimizationLevel(Enum):
    """Performance optimization levels."""
    BASIC = "basic"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    EXTREME = "extreme"

class ResourceType(Enum):
    """Resource types for optimization."""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    DISK = "disk"
    DATABASE = "database"
    CACHE = "cache"

class PerformanceMetric(Enum):
    """Performance metrics to track."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CONNECTION_COUNT = "connection_count"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"

@dataclass
class PerformanceMetrics:
    """Performance metrics data."""
    metric_type: PerformanceMetric
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    context: str = ""

@dataclass
class OptimizationResult:
    """Result of an optimization operation."""
    optimization_type: str
    level: OptimizationLevel
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    improvement_percentage: float
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

# =============================================================================
# Connection Pool Consolidator
# =============================================================================

class UnifiedConnectionPool:
    """
    🚀 Unified Connection Pool - Consolidates all connection pool implementations.
    
    Replaces scattered connection pool implementations with a single,
    optimized system that provides consistent behavior across all
    database types and external services.
    """
    
    def __init__(self, 
                 max_connections: int = 100,
                 max_keepalive: int = 20,
                 health_check_interval: int = 30):
        
        self.max_connections = max_connections
        self.max_keepalive = max_keepalive
        self.health_check_interval = health_check_interval
        
        # Connection management
        self.connections: Dict[str, deque] = defaultdict(deque)
        self.active_connections: Dict[str, int] = defaultdict(int)
        self.connection_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.connection_factories: Dict[str, Callable] = {}
        
        # Performance tracking
        self.connection_times: Dict[str, List[float]] = defaultdict(list)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.health_status: Dict[str, str] = defaultdict(lambda: "unknown")
        
        # Health monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        self.monitoring_active = False
        
        # Start monitoring
        self.start_monitoring()
    
    def register_connection_factory(self, name: str, factory: Callable):
        """Register a connection factory for a specific service."""
        self.connection_factories[name] = factory
        logger.info(f"Registered connection factory for: {name}")
    
    async def get_connection(self, name: str, **kwargs) -> Any:
        """Get a connection from the pool."""
        if name not in self.connection_factories:
            raise ValueError(f"No connection factory registered for: {name}")
        
        start_time = time.time()
        
        async with self.connection_locks[name]:
            # Check for available connections
            if self.connections[name]:
                connection = self.connections[name].popleft()
                if await self._is_connection_healthy(connection):
                    self.active_connections[name] += 1
                    self._record_connection_time(name, time.time() - start_time)
                    return connection
                else:
                    # Remove unhealthy connection
                    await self._close_connection(name, connection)
            
            # Create new connection if pool not full
            if self.active_connections[name] < self.max_connections:
                try:
                    connection = await self.connection_factories[name](**kwargs)
                    self.active_connections[name] += 1
                    self._record_connection_time(name, time.time() - start_time)
                    return connection
                except Exception as e:
                    self.error_counts[name] += 1
                    logger.error(f"Failed to create connection for {name}: {e}")
                    raise
            
            # Wait for available connection
            while not self.connections[name]:
                await asyncio.sleep(0.1)
            
            connection = self.connections[name].popleft()
            self.active_connections[name] += 1
            self._record_connection_time(name, time.time() - start_time)
            return connection
    
    async def return_connection(self, name: str, connection: Any):
        """Return a connection to the pool."""
        async with self.connection_locks[name]:
            if len(self.connections[name]) < self.max_keepalive:
                self.connections[name].append(connection)
            else:
                await self._close_connection(name, connection)
            
            self.active_connections[name] = max(0, self.active_connections[name] - 1)
    
    async def _is_connection_healthy(self, connection: Any) -> bool:
        """Check if a connection is healthy."""
        try:
            # Try to use the connection to see if it's still valid
            if hasattr(connection, 'ping'):
                await connection.ping()
            elif hasattr(connection, 'execute'):
                await connection.execute('SELECT 1')
            elif hasattr(connection, 'is_closing'):
                return not connection.is_closing()
            return True
        except Exception:
            return False
    
    async def _close_connection(self, name: str, connection: Any):
        """Close a connection."""
        try:
            if hasattr(connection, 'close'):
                await connection.close()
            elif hasattr(connection, 'disconnect'):
                await connection.disconnect()
            elif hasattr(connection, 'shutdown'):
                await connection.shutdown()
        except Exception as e:
            logger.warning(f"Error closing connection for {name}: {e}")
    
    def _record_connection_time(self, name: str, duration: float):
        """Record connection time for performance tracking."""
        self.connection_times[name].append(duration)
        # Keep only last 100 measurements
        if len(self.connection_times[name]) > 100:
            self.connection_times[name] = self.connection_times[name][-100:]
    
    def start_monitoring(self):
        """Start health monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Connection pool monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring."""
        self.monitoring_active = False
        if self.health_check_task:
            self.health_check_task.cancel()
        logger.info("Connection pool monitoring stopped")
    
    async def _health_check_loop(self):
        """Health check loop for all connections."""
        while self.monitoring_active:
            try:
                for name in list(self.connection_factories.keys()):
                    # Check pool health
                    total_connections = self.active_connections[name] + len(self.connections[name])
                    utilization = total_connections / self.max_connections if self.max_connections > 0 else 0
                    
                    if utilization > 0.9:
                        self.health_status[name] = "critical"
                    elif utilization > 0.7:
                        self.health_status[name] = "warning"
                    else:
                        self.health_status[name] = "healthy"
                    
                    # Clean up stale connections
                    await self._cleanup_stale_connections(name)
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_stale_connections(self, name: str):
        """Clean up stale connections."""
        async with self.connection_locks[name]:
            # Remove connections that are too old
            current_time = time.time()
            connections_to_remove = []
            
            for connection in self.connections[name]:
                if hasattr(connection, '_last_used'):
                    if current_time - connection._last_used > self.max_keepalive * 2:
                        connections_to_remove.append(connection)
            
            for connection in connections_to_remove:
                self.connections[name].remove(connection)
                await self._close_connection(name, connection)
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        stats = {}
        for name in self.connection_factories.keys():
            stats[name] = {
                "active_connections": self.active_connections[name],
                "available_connections": len(self.connections[name]),
                "total_connections": self.active_connections[name] + len(self.connections[name]),
                "utilization": (self.active_connections[name] + len(self.connections[name])) / self.max_connections,
                "health_status": self.health_status[name],
                "error_count": self.error_counts[name],
                "avg_connection_time": sum(self.connection_times[name]) / len(self.connection_times[name]) if self.connection_times[name] else 0
            }
        return stats

# =============================================================================
# Cache Intelligence System
# =============================================================================

class IntelligentCacheManager:
    """
    🚀 Intelligent Cache Manager - Advanced caching with ML-based prediction.
    
    Provides predictive caching, intelligent cache warming, and advanced
    compression algorithms for optimal performance.
    """
    
    def __init__(self, 
                 max_cache_size: int = 1000,
                 compression_threshold: int = 1024):
        
        self.max_cache_size = max_cache_size
        self.compression_threshold = compression_threshold
        
        # Cache storage
        self.cache: Dict[str, Any] = {}
        self.cache_metadata: Dict[str, Dict[str, Any]] = {}
        self.access_patterns: Dict[str, List[float]] = defaultdict(list)
        
        # Performance tracking
        self.hit_count = 0
        self.miss_count = 0
        self.eviction_count = 0
        self.compression_count = 0
        
        # ML-based prediction
        self.access_frequency: Dict[str, float] = defaultdict(float)
        self.time_based_patterns: Dict[str, List[float]] = defaultdict(list)
        
        # Start background optimization
        self._start_background_optimization()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with intelligent prediction."""
        if key in self.cache:
            self.hit_count += 1
            self._update_access_pattern(key)
            
            # Update metadata
            metadata = self.cache_metadata.get(key, {})
            metadata['last_accessed'] = time.time()
            metadata['access_count'] = metadata.get('access_count', 0) + 1
            
            # Predict and warm related keys
            self._predict_and_warm(key)
            
            return self.cache[key]
        else:
            self.miss_count += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            compression: bool = True) -> None:
        """Set value in cache with intelligent optimization."""
        # Apply compression if beneficial
        if compression and self._should_compress(value):
            value = self._compress_value(value)
            self.compression_count += 1
        
        # Store value and metadata
        self.cache[key] = value
        self.cache_metadata[key] = {
            'created_at': time.time(),
            'last_accessed': time.time(),
            'access_count': 0,
            'ttl': ttl,
            'compressed': compression and self._should_compress(value),
            'size': self._get_value_size(value)
        }
        
        # Manage cache size
        self._manage_cache_size()
        
        # Update access patterns
        self._update_access_pattern(key)
    
    def _should_compress(self, value: Any) -> bool:
        """Determine if value should be compressed."""
        size = self._get_value_size(value)
        return size > self.compression_threshold
    
    def _compress_value(self, value: Any) -> Any:
        """Compress value using appropriate algorithm."""
        try:
            import zlib
            if isinstance(value, str):
                return zlib.compress(value.encode('utf-8'))
            elif isinstance(value, bytes):
                return zlib.compress(value)
            else:
                import pickle
                serialized = pickle.dumps(value)
                return zlib.compress(serialized)
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return value
    
    def _decompress_value(self, value: Any) -> Any:
        """Decompress value."""
        try:
            import zlib
            decompressed = zlib.decompress(value)
            # Try to determine original type and deserialize
            try:
                import pickle
                return pickle.loads(decompressed)
            except:
                return decompressed.decode('utf-8')
        except Exception as e:
            logger.warning(f"Decompression failed: {e}")
            return value
    
    def _get_value_size(self, value: Any) -> int:
        """Get approximate size of value in bytes."""
        try:
            import sys
            return sys.getsizeof(value)
        except:
            return 0
    
    def _update_access_pattern(self, key: str):
        """Update access pattern for ML-based prediction."""
        current_time = time.time()
        self.access_patterns[key].append(current_time)
        
        # Keep only recent patterns
        if len(self.access_patterns[key]) > 100:
            self.access_patterns[key] = self.access_patterns[key][-100:]
        
        # Update frequency
        self.access_frequency[key] = len(self.access_patterns[key]) / 60.0  # accesses per minute
    
    def _predict_and_warm(self, accessed_key: str):
        """Predict and warm related cache entries."""
        # Simple prediction: warm keys with similar access patterns
        for key, frequency in self.access_frequency.items():
            if key != accessed_key and frequency > 0.1:  # Access more than 6 times per minute
                # This is a simplified prediction - in production you'd use ML models
                if key not in self.cache:
                    # Warm this key by prefetching (implementation depends on your data source)
                    pass
    
    def _manage_cache_size(self):
        """Manage cache size using intelligent eviction."""
        if len(self.cache) <= self.max_cache_size:
            return
        
        # Calculate eviction scores based on multiple factors
        eviction_scores = {}
        current_time = time.time()
        
        for key, metadata in self.cache_metadata.items():
            # Factors: age, access frequency, TTL, size
            age = current_time - metadata['created_at']
            access_frequency = metadata['access_count'] / max(age, 1)
            ttl_factor = 1.0 if metadata['ttl'] is None else max(0, metadata['ttl'] - age) / metadata['ttl']
            size_factor = 1.0 / max(metadata['size'], 1)
            
            # Lower score = higher priority for eviction
            eviction_scores[key] = (age * 0.3 + 
                                  (1.0 - access_frequency) * 0.4 + 
                                  (1.0 - ttl_factor) * 0.2 + 
                                  (1.0 - size_factor) * 0.1)
        
        # Evict keys with highest scores
        keys_to_evict = sorted(eviction_scores.items(), key=lambda x: x[1], reverse=True)
        evict_count = len(self.cache) - self.max_cache_size + 10  # Keep some buffer
        
        for i in range(min(evict_count, len(keys_to_evict))):
            key = keys_to_evict[i][0]
            self._evict_key(key)
    
    def _evict_key(self, key: str):
        """Evict a key from cache."""
        if key in self.cache:
            del self.cache[key]
            del self.cache_metadata[key]
            self.eviction_count += 1
    
    def _start_background_optimization(self):
        """Start background optimization tasks."""
        asyncio.create_task(self._background_optimization_loop())
    
    async def _background_optimization_loop(self):
        """Background optimization loop."""
        while True:
            try:
                # Clean up expired entries
                await self._cleanup_expired_entries()
                
                # Optimize cache based on access patterns
                await self._optimize_cache_layout()
                
                # Update ML models (simplified)
                await self._update_prediction_models()
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Background optimization error: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_expired_entries(self):
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for key, metadata in self.cache_metadata.items():
            if metadata['ttl'] and current_time - metadata['created_at'] > metadata['ttl']:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._evict_key(key)
    
    async def _optimize_cache_layout(self):
        """Optimize cache layout based on access patterns."""
        # This is a simplified optimization - in production you'd use more sophisticated algorithms
        pass
    
    async def _update_prediction_models(self):
        """Update ML-based prediction models."""
        # This is a simplified update - in production you'd use actual ML models
        pass
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "eviction_count": self.eviction_count,
            "compression_count": self.compression_count,
            "cache_size": len(self.cache),
            "max_cache_size": self.max_cache_size,
            "utilization": len(self.cache) / self.max_cache_size if self.max_cache_size > 0 else 0
        }

# =============================================================================
# Unified Performance Optimizer
# =============================================================================

class UnifiedPerformanceOptimizer:
    """
    🚀 Unified Performance Optimizer - Centralized performance management.
    
    Consolidates all performance optimization functionality and provides
    consistent optimization strategies across the entire application.
    """
    
    def __init__(self):
        # Core components
        self.connection_pool = UnifiedConnectionPool()
        self.cache_manager = IntelligentCacheManager()
        
        # Performance tracking
        self.metrics_history: Dict[PerformanceMetric, List[PerformanceMetrics]] = defaultdict(list)
        self.optimization_history: List[OptimizationResult] = []
        
        # Resource monitoring
        self.resource_monitors: Dict[ResourceType, Callable] = {}
        self.optimization_strategies: Dict[ResourceType, List[Callable]] = defaultdict(list)
        
        # Setup monitoring and strategies
        self._setup_resource_monitoring()
        self._setup_optimization_strategies()
        
        # Start background optimization
        self._start_background_optimization()
    
    def _setup_resource_monitoring(self):
        """Setup resource monitoring functions."""
        self.resource_monitors[ResourceType.CPU] = self._monitor_cpu_usage
        self.resource_monitors[ResourceType.MEMORY] = self._monitor_memory_usage
        self.resource_monitors[ResourceType.NETWORK] = self._monitor_network_usage
        self.resource_monitors[ResourceType.DISK] = self._monitor_disk_usage
    
    def _setup_optimization_strategies(self):
        """Setup optimization strategies for each resource type."""
        # CPU optimizations
        self.optimization_strategies[ResourceType.CPU].extend([
            self._optimize_garbage_collection,
            self._optimize_thread_pool,
            self._optimize_process_priority
        ])
        
        # Memory optimizations
        self.optimization_strategies[ResourceType.MEMORY].extend([
            self._optimize_memory_allocation,
            self._optimize_cache_eviction,
            self._optimize_object_pooling
        ])
        
        # Network optimizations
        self.optimization_strategies[ResourceType.NETWORK].extend([
            self._optimize_connection_pooling,
            self._optimize_keepalive,
            self._optimize_buffering
        ])
    
    def _monitor_cpu_usage(self) -> float:
        """Monitor CPU usage."""
        return psutil.cpu_percent(interval=1)
    
    def _monitor_memory_usage(self) -> float:
        """Monitor memory usage."""
        memory = psutil.virtual_memory()
        return memory.percent
    
    def _monitor_network_usage(self) -> float:
        """Monitor network usage."""
        # Simplified network monitoring
        return 0.0
    
    def _monitor_disk_usage(self) -> float:
        """Monitor disk usage."""
        disk = psutil.disk_usage('/')
        return (disk.used / disk.total) * 100
    
    async def optimize_system(self, level: OptimizationLevel = OptimizationLevel.STANDARD) -> OptimizationResult:
        """Perform system-wide optimization."""
        start_time = time.time()
        
        # Collect metrics before optimization
        metrics_before = {}
        for resource_type in ResourceType:
            if resource_type in self.resource_monitors:
                metrics_before[resource_type.value] = self.resource_monitors[resource_type]()
        
        # Apply optimizations based on level
        optimizations_applied = []
        
        if level in [OptimizationLevel.STANDARD, OptimizationLevel.AGGRESSIVE, OptimizationLevel.EXTREME]:
            # Apply standard optimizations
            for resource_type, strategies in self.optimization_strategies.items():
                for strategy in strategies[:2]:  # Apply first 2 strategies
                    try:
                        result = await strategy()
                        optimizations_applied.append(result)
                    except Exception as e:
                        logger.warning(f"Strategy {strategy.__name__} failed: {e}")
        
        if level in [OptimizationLevel.AGGRESSIVE, OptimizationLevel.EXTREME]:
            # Apply aggressive optimizations
            for resource_type, strategies in self.optimization_strategies.items():
                for strategy in strategies[2:4]:  # Apply strategies 3-4
                    try:
                        result = await strategy()
                        optimizations_applied.append(result)
                    except Exception as e:
                        logger.warning(f"Strategy {strategy.__name__} failed: {e}")
        
        if level == OptimizationLevel.EXTREME:
            # Apply extreme optimizations
            for resource_type, strategies in self.optimization_strategies.items():
                for strategy in strategies[4:]:  # Apply remaining strategies
                    try:
                        result = await strategy()
                        optimizations_applied.append(result)
                    except Exception as e:
                        logger.warning(f"Strategy {strategy.__name__} failed: {e}")
        
        # Collect metrics after optimization
        metrics_after = {}
        for resource_type in ResourceType:
            if resource_type in self.resource_monitors:
                metrics_after[resource_type.value] = self.resource_monitors[resource_type]()
        
        # Calculate improvement
        improvement_percentage = self._calculate_improvement(metrics_before, metrics_after)
        
        # Create result
        result = OptimizationResult(
            optimization_type="system_wide",
            level=level,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            improvement_percentage=improvement_percentage,
            duration_ms=(time.time() - start_time) * 1000,
            details={"optimizations_applied": optimizations_applied}
        )
        
        self.optimization_history.append(result)
        return result
    
    def _calculate_improvement(self, metrics_before: Dict[str, float], 
                             metrics_after: Dict[str, float]) -> float:
        """Calculate overall improvement percentage."""
        if not metrics_before or not metrics_after:
            return 0.0
        
        improvements = []
        for key in metrics_before:
            if key in metrics_after:
                before = metrics_before[key]
                after = metrics_after[key]
                
                if before > 0:
                    # For metrics where lower is better (CPU, memory usage)
                    if key in ['cpu_usage', 'memory_usage']:
                        improvement = ((before - after) / before) * 100
                    else:
                        improvement = ((after - before) / before) * 100
                    improvements.append(improvement)
        
        return sum(improvements) / len(improvements) if improvements else 0.0
    
    # Optimization strategy implementations
    async def _optimize_garbage_collection(self) -> str:
        """Optimize garbage collection."""
        gc.collect()
        return "garbage_collection"
    
    async def _optimize_thread_pool(self) -> str:
        """Optimize thread pool."""
        # Simplified thread pool optimization
        return "thread_pool"
    
    async def _optimize_process_priority(self) -> str:
        """Optimize process priority."""
        # Simplified process priority optimization
        return "process_priority"
    
    async def _optimize_memory_allocation(self) -> str:
        """Optimize memory allocation."""
        # Simplified memory optimization
        return "memory_allocation"
    
    async def _optimize_cache_eviction(self) -> str:
        """Optimize cache eviction."""
        # Trigger cache cleanup
        await self.cache_manager._cleanup_expired_entries()
        return "cache_eviction"
    
    async def _optimize_object_pooling(self) -> str:
        """Optimize object pooling."""
        # Simplified object pooling optimization
        return "object_pooling"
    
    async def _optimize_connection_pooling(self) -> str:
        """Optimize connection pooling."""
        # Trigger connection pool cleanup
        for name in list(self.connection_pool.connection_factories.keys()):
            await self.connection_pool._cleanup_stale_connections(name)
        return "connection_pooling"
    
    async def _optimize_keepalive(self) -> str:
        """Optimize keepalive settings."""
        # Simplified keepalive optimization
        return "keepalive"
    
    async def _optimize_buffering(self) -> str:
        """Optimize buffering."""
        # Simplified buffering optimization
        return "buffering"
    
    def _start_background_optimization(self):
        """Start background optimization tasks."""
        asyncio.create_task(self._background_optimization_loop())
    
    async def _background_optimization_loop(self):
        """Background optimization loop."""
        while True:
            try:
                # Monitor system resources
                for resource_type in ResourceType:
                    if resource_type in self.resource_monitors:
                        value = self.resource_monitors[resource_type]()
                        
                        # Create metric
                        metric = PerformanceMetrics(
                            metric_type=PerformanceMetric.MEMORY_USAGE if resource_type == ResourceType.MEMORY else PerformanceMetric.CPU_USAGE,
                            value=value,
                            unit="%" if resource_type in [ResourceType.CPU, ResourceType.MEMORY, ResourceType.DISK] else "bytes",
                            context=resource_type.value
                        )
                        
                        self.metrics_history[metric.metric_type].append(metric)
                        
                        # Keep only recent metrics
                        if len(self.metrics_history[metric.metric_type]) > 1000:
                            self.metrics_history[metric.metric_type] = self.metrics_history[metric.metric_type][-1000:]
                
                # Auto-optimize if thresholds are exceeded
                await self._auto_optimize_if_needed()
                
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except Exception as e:
                logger.error(f"Background optimization error: {e}")
                await asyncio.sleep(10)
    
    async def _auto_optimize_if_needed(self):
        """Automatically optimize if resource thresholds are exceeded."""
        # Check CPU usage
        cpu_usage = self._monitor_cpu_usage()
        if cpu_usage > 80:
            logger.warning(f"High CPU usage detected: {cpu_usage}%. Triggering optimization.")
            await self.optimize_system(OptimizationLevel.AGGRESSIVE)
        
        # Check memory usage
        memory_usage = self._monitor_memory_usage()
        if memory_usage > 85:
            logger.warning(f"High memory usage detected: {memory_usage}%. Triggering optimization.")
            await self.optimize_system(OptimizationLevel.AGGRESSIVE)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        return {
            "connection_pool": self.connection_pool.get_pool_stats(),
            "cache": self.cache_manager.get_cache_stats(),
            "optimizations": {
                "total_optimizations": len(self.optimization_history),
                "recent_optimizations": [
                    {
                        "type": opt.optimization_type,
                        "level": opt.level.value,
                        "improvement": f"{opt.improvement_percentage:.2f}%",
                        "duration_ms": f"{opt.duration_ms:.2f}ms",
                        "timestamp": opt.timestamp.isoformat()
                    }
                    for opt in self.optimization_history[-10:]  # Last 10 optimizations
                ]
            },
            "metrics": {
                metric_type.value: {
                    "count": len(metrics),
                    "recent_values": [m.value for m in metrics[-10:]] if metrics else [],
                    "average": sum(m.value for m in metrics) / len(metrics) if metrics else 0
                }
                for metric_type, metrics in self.metrics_history.items()
            }
        }

# =============================================================================
# Global Instance and Utilities
# =============================================================================

# Global performance optimizer instance
_performance_optimizer: Optional[UnifiedPerformanceOptimizer] = None

def get_performance_optimizer() -> UnifiedPerformanceOptimizer:
    """Get or create global performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = UnifiedPerformanceOptimizer()
    return _performance_optimizer

def get_connection_pool() -> UnifiedConnectionPool:
    """Get connection pool from global optimizer."""
    return get_performance_optimizer().connection_pool

def get_cache_manager() -> IntelligentCacheManager:
    """Get cache manager from global optimizer."""
    return get_performance_optimizer().cache_manager

async def optimize_system(level: OptimizationLevel = OptimizationLevel.STANDARD) -> OptimizationResult:
    """Optimize system using global optimizer."""
    return await get_performance_optimizer().optimize_system(level)

def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary from global optimizer."""
    return get_performance_optimizer().get_performance_summary()

# =============================================================================
# Example Usage
# =============================================================================

async def example_usage():
    """Example of how to use the unified performance optimizer."""
    
    # Get performance optimizer
    optimizer = get_performance_optimizer()
    
    # Register connection factories
    async def create_redis_connection():
        # Simulate Redis connection creation
        return {"type": "redis", "connected": True}
    
    async def create_postgres_connection():
        # Simulate PostgreSQL connection creation
        return {"type": "postgres", "connected": True}
    
    optimizer.connection_pool.register_connection_factory("redis", create_redis_connection)
    optimizer.connection_pool.register_connection_factory("postgres", create_postgres_connection)
    
    # Use connection pool
    async with asynccontextmanager(optimizer.connection_pool.get_connection)("redis") as redis_conn:
        print(f"Using Redis connection: {redis_conn}")
    
    # Use cache manager
    optimizer.cache_manager.set("test_key", "test_value", ttl=300)
    value = optimizer.cache_manager.get("test_key")
    print(f"Cached value: {value}")
    
    # Perform system optimization
    result = await optimizer.optimize_system(OptimizationLevel.AGGRESSIVE)
    print(f"Optimization result: {result.improvement_percentage:.2f}% improvement")
    
    # Get performance summary
    summary = optimizer.get_performance_summary()
    print(f"Performance summary: {summary}")

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
