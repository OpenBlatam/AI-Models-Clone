"""
Performance Optimization Engine

Provides comprehensive performance optimization capabilities including:
- Memory optimization
- Database query optimization
- Caching strategies
- Request optimization
- Resource management
"""

import asyncio
import time
import gc
import sys
import psutil
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import weakref
from functools import wraps, lru_cache
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import OptimizationConfig
from ..models import (
    OptimizationResult, 
    PerformanceMetrics, 
    OptimizationStrategy,
    CacheStrategy,
    DatabaseOptimization
)
from ..exceptions import OptimizationError, PerformanceError

logger = logging.getLogger(__name__)

@dataclass
class PerformanceContext:
    """Context for performance optimization operations"""
    start_time: float = field(default_factory=time.time)
    memory_before: float = 0.0
    cpu_before: float = 0.0
    operation_name: str = ""
    optimization_level: str = "standard"
    cache_enabled: bool = True
    
    def __post_init__(self):
        self.memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.cpu_before = psutil.cpu_percent()

class PerformanceOptimizer:
    """Advanced performance optimization engine"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.cache = {}
        self.performance_cache = {}
        self.memory_threshold = config.memory_threshold_mb
        self.cpu_threshold = config.cpu_threshold_percent
        self.optimization_history: List[OptimizationResult] = []
        self.active_contexts: Dict[str, PerformanceContext] = {}
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        self._setup_monitoring()
    
    def _setup_monitoring(self):
        """Setup performance monitoring"""
        self._memory_monitor = threading.Thread(
            target=self._monitor_memory, 
            daemon=True
        )
        self._memory_monitor.start()
    
    def _monitor_memory(self):
        """Monitor memory usage continuously"""
        while True:
            try:
                memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
                if memory_usage > self.memory_threshold:
                    self._trigger_memory_cleanup()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(10)
    
    def _trigger_memory_cleanup(self):
        """Trigger memory cleanup when threshold exceeded"""
        logger.warning("Memory threshold exceeded, triggering cleanup")
        self.cleanup_memory()
    
    def cleanup_memory(self) -> PerformanceMetrics:
        """Clean up memory and optimize resources"""
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Clear caches
        cache_items_cleared = len(self.cache) + len(self.performance_cache)
        self.cache.clear()
        self.performance_cache.clear()
        
        # Force garbage collection
        gc.collect()
        
        # Clear old optimization history
        if len(self.optimization_history) > 1000:
            self.optimization_history = self.optimization_history[-500:]
        
        memory_after = psutil.Process().memory_info().rss / 1024 / 1024
        execution_time = time.time() - start_time
        
        metrics = PerformanceMetrics(
            execution_time=execution_time,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_saved=memory_before - memory_after,
            cache_items_cleared=cache_items_cleared,
            optimization_applied="memory_cleanup"
        )
        
        logger.info(f"Memory cleanup completed: {metrics}")
        return metrics
    
    def optimize_function(self, optimization_level: str = "standard") -> Callable:
        """Decorator for optimizing function performance"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                context = PerformanceContext(
                    operation_name=func.__name__,
                    optimization_level=optimization_level
                )
                
                try:
                    # Apply pre-optimization
                    await self._pre_optimize(context)
                    
                    # Execute function
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    # Apply post-optimization
                    metrics = await self._post_optimize(context)
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Optimization error in {func.__name__}: {e}")
                    raise PerformanceError(f"Function optimization failed: {e}")
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                context = PerformanceContext(
                    operation_name=func.__name__,
                    optimization_level=optimization_level
                )
                
                try:
                    # Apply pre-optimization
                    self._pre_optimize_sync(context)
                    
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Apply post-optimization
                    metrics = self._post_optimize_sync(context)
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Optimization error in {func.__name__}: {e}")
                    raise PerformanceError(f"Function optimization failed: {e}")
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    async def _pre_optimize(self, context: PerformanceContext):
        """Apply pre-execution optimizations"""
        self.active_contexts[context.operation_name] = context
        
        # Memory optimization for high-level operations
        if context.optimization_level in ["high", "ultra"]:
            if psutil.Process().memory_info().rss / 1024 / 1024 > self.memory_threshold * 0.8:
                gc.collect()
    
    def _pre_optimize_sync(self, context: PerformanceContext):
        """Apply pre-execution optimizations (sync)"""
        self.active_contexts[context.operation_name] = context
        
        if context.optimization_level in ["high", "ultra"]:
            if psutil.Process().memory_info().rss / 1024 / 1024 > self.memory_threshold * 0.8:
                gc.collect()
    
    async def _post_optimize(self, context: PerformanceContext) -> PerformanceMetrics:
        """Apply post-execution optimizations"""
        end_time = time.time()
        memory_after = psutil.Process().memory_info().rss / 1024 / 1024
        cpu_after = psutil.cpu_percent()
        
        metrics = PerformanceMetrics(
            execution_time=end_time - context.start_time,
            memory_before=context.memory_before,
            memory_after=memory_after,
            memory_used=memory_after - context.memory_before,
            cpu_before=context.cpu_before,
            cpu_after=cpu_after,
            optimization_applied=context.optimization_level
        )
        
        # Store metrics for analysis
        self.optimization_history.append(
            OptimizationResult(
                operation=context.operation_name,
                metrics=metrics,
                timestamp=datetime.utcnow(),
                success=True
            )
        )
        
        # Cleanup context
        if context.operation_name in self.active_contexts:
            del self.active_contexts[context.operation_name]
        
        return metrics
    
    def _post_optimize_sync(self, context: PerformanceContext) -> PerformanceMetrics:
        """Apply post-execution optimizations (sync)"""
        end_time = time.time()
        memory_after = psutil.Process().memory_info().rss / 1024 / 1024
        cpu_after = psutil.cpu_percent()
        
        metrics = PerformanceMetrics(
            execution_time=end_time - context.start_time,
            memory_before=context.memory_before,
            memory_after=memory_after,
            memory_used=memory_after - context.memory_before,
            cpu_before=context.cpu_before,
            cpu_after=cpu_after,
            optimization_applied=context.optimization_level
        )
        
        # Store metrics for analysis
        self.optimization_history.append(
            OptimizationResult(
                operation=context.operation_name,
                metrics=metrics,
                timestamp=datetime.utcnow(),
                success=True
            )
        )
        
        # Cleanup context
        if context.operation_name in self.active_contexts:
            del self.active_contexts[context.operation_name]
        
        return metrics
    
    def optimize_database_query(self, query: str, params: Dict = None) -> DatabaseOptimization:
        """Optimize database query performance"""
        try:
            # Analyze query complexity
            query_lower = query.lower().strip()
            complexity_score = self._analyze_query_complexity(query_lower)
            
            optimizations = []
            
            # Suggest indexes
            if 'where' in query_lower:
                optimizations.append("Consider adding indexes on WHERE clause columns")
            
            if 'join' in query_lower:
                optimizations.append("Ensure JOIN columns are indexed")
            
            if 'order by' in query_lower:
                optimizations.append("Consider adding composite index for ORDER BY")
            
            # Suggest query rewriting
            if 'select *' in query_lower:
                optimizations.append("Avoid SELECT *, specify only needed columns")
            
            if complexity_score > 5:
                optimizations.append("Consider breaking complex query into smaller parts")
            
            return DatabaseOptimization(
                original_query=query,
                complexity_score=complexity_score,
                suggested_optimizations=optimizations,
                estimated_improvement=min(complexity_score * 0.1, 0.8)
            )
            
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
            raise OptimizationError(f"Failed to optimize database query: {e}")
    
    def _analyze_query_complexity(self, query: str) -> int:
        """Analyze query complexity and return score (1-10)"""
        score = 1
        
        # Count complexity factors
        if 'join' in query:
            score += query.count('join') * 2
        if 'subquery' in query or '(' in query:
            score += 2
        if 'group by' in query:
            score += 1
        if 'having' in query:
            score += 1
        if 'order by' in query:
            score += 1
        if 'union' in query:
            score += 3
        
        return min(score, 10)
    
    def create_cache_strategy(self, cache_type: str = "lru") -> CacheStrategy:
        """Create optimized caching strategy"""
        try:
            if cache_type == "lru":
                return CacheStrategy(
                    cache_type="lru",
                    max_size=self.config.cache_size,
                    ttl=self.config.cache_ttl,
                    cleanup_threshold=0.9
                )
            elif cache_type == "time_based":
                return CacheStrategy(
                    cache_type="time_based",
                    max_size=self.config.cache_size,
                    ttl=300,  # 5 minutes
                    cleanup_threshold=0.8
                )
            else:
                return CacheStrategy(
                    cache_type="simple",
                    max_size=1000,
                    ttl=600,
                    cleanup_threshold=0.9
                )
                
        except Exception as e:
            logger.error(f"Cache strategy creation error: {e}")
            raise OptimizationError(f"Failed to create cache strategy: {e}")
    
    async def optimize_batch_operation(self, items: List[Any], 
                                     operation: Callable, 
                                     batch_size: int = None) -> List[Any]:
        """Optimize batch operations with parallel processing"""
        if batch_size is None:
            batch_size = self.config.batch_size
        
        try:
            results = []
            
            # Process in batches
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                # Process batch in parallel
                tasks = []
                for item in batch:
                    if asyncio.iscoroutinefunction(operation):
                        tasks.append(operation(item))
                    else:
                        tasks.append(asyncio.get_event_loop().run_in_executor(
                            self.executor, operation, item
                        ))
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter out exceptions and log them
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Batch operation error: {result}")
                    else:
                        results.append(result)
                
                # Memory cleanup between batches
                if i % (batch_size * 10) == 0:
                    gc.collect()
            
            return results
            
        except Exception as e:
            logger.error(f"Batch optimization error: {e}")
            raise OptimizationError(f"Batch operation optimization failed: {e}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            if not self.optimization_history:
                return {"message": "No optimization data available"}
            
            # Calculate statistics
            total_operations = len(self.optimization_history)
            avg_execution_time = sum(
                result.metrics.execution_time 
                for result in self.optimization_history
            ) / total_operations
            
            memory_stats = [
                result.metrics.memory_used 
                for result in self.optimization_history
                if result.metrics.memory_used is not None
            ]
            
            avg_memory_usage = sum(memory_stats) / len(memory_stats) if memory_stats else 0
            
            # Group by operation type
            operation_stats = {}
            for result in self.optimization_history:
                op_name = result.operation
                if op_name not in operation_stats:
                    operation_stats[op_name] = {
                        'count': 0,
                        'total_time': 0,
                        'avg_time': 0,
                        'success_count': 0
                    }
                
                operation_stats[op_name]['count'] += 1
                operation_stats[op_name]['total_time'] += result.metrics.execution_time
                if result.success:
                    operation_stats[op_name]['success_count'] += 1
            
            # Calculate averages
            for op_name, stats in operation_stats.items():
                stats['avg_time'] = stats['total_time'] / stats['count']
                stats['success_rate'] = stats['success_count'] / stats['count']
            
            return {
                'total_operations': total_operations,
                'average_execution_time': avg_execution_time,
                'average_memory_usage_mb': avg_memory_usage,
                'current_memory_usage_mb': psutil.Process().memory_info().rss / 1024 / 1024,
                'memory_threshold_mb': self.memory_threshold,
                'operation_statistics': operation_stats,
                'active_contexts': len(self.active_contexts),
                'cache_size': len(self.cache),
                'performance_cache_size': len(self.performance_cache)
            }
            
        except Exception as e:
            logger.error(f"Performance report error: {e}")
            return {"error": f"Failed to generate performance report: {e}"}
    
    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Factory function
def create_performance_optimizer(config: OptimizationConfig) -> PerformanceOptimizer:
    """Create and configure performance optimizer"""
    return PerformanceOptimizer(config)

# Convenience decorators
def optimize_performance(level: str = "standard"):
    """Decorator for performance optimization"""
    config = OptimizationConfig()
    optimizer = create_performance_optimizer(config)
    return optimizer.optimize_function(level)

@lru_cache(maxsize=128)
def cached_operation(func: Callable) -> Callable:
    """Simple cached operation decorator"""
    return lru_cache(maxsize=128)(func) 