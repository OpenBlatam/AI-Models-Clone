#!/usr/bin/env python3
"""
🚀 Unified Memory Manager - Consolidated Memory Management System
================================================================

Consolidates all memory management functionality into a single, 
optimized system that eliminates memory leaks and provides 
consistent performance monitoring.
"""

import asyncio
import gc
import sys
import weakref
import mmap
import os
import threading
import time
import tracemalloc
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum, auto
from contextlib import contextmanager
import structlog
import psutil
import numpy as np
from collections import defaultdict, deque
import pickle
import zlib
import lz4
import brotli

# Optional advanced libraries
try:
    import pympler
    from pympler import tracker, muppy, summary
    HAS_PYMPLER = True
except ImportError:
    HAS_PYMPLER = False

try:
    import objgraph
    HAS_OBJGRAPH = True
except ImportError:
    HAS_OBJGRAPH = False

logger = structlog.get_logger()

# =============================================================================
# Memory Management Types
# =============================================================================

class MemoryThreshold(Enum):
    """Memory usage thresholds."""
    LOW = "low"           # < 50%
    MEDIUM = "medium"     # 50-75%
    HIGH = "high"         # 75-90%
    CRITICAL = "critical" # > 90%

class MemoryStrategy(Enum):
    """Memory optimization strategies."""
    LIGHT = "light"           # Basic cleanup
    MEDIUM = "medium"         # Moderate optimization
    AGGRESSIVE = "aggressive" # Heavy optimization
    EMERGENCY = "emergency"   # Emergency cleanup

class CompressionAlgorithm(Enum):
    """Compression algorithms for memory optimization."""
    ZLIB = "zlib"
    LZ4 = "lz4"
    BROTLI = "brotli"
    SNAPPY = "snappy"
    ZSTD = "zstd"

@dataclass
class MemoryMetrics:
    """Memory usage metrics."""
    total_memory: int
    used_memory: int
    available_memory: int
    memory_percentage: float
    gc_objects: int
    gc_collections: int
    memory_leaks: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MemoryLeak:
    """Memory leak information."""
    object_type: str
    previous_count: int
    latest_count: int
    growth: int
    growth_rate: float
    severity: str
    timestamp: datetime = field(default_factory=datetime.now)

# =============================================================================
# Memory Leak Detector
# =============================================================================

class MemoryLeakDetector:
    """Advanced memory leak detection system."""
    
    def __init__(self, max_snapshots: int = 100):
        self.max_snapshots = max_snapshots
        self.memory_snapshots = deque(maxlen=max_snapshots)
        self.leak_candidates = []
        self.tracemalloc_active = False
        
        # Enable tracemalloc for detailed tracking
        if not tracemalloc.is_tracing():
            tracemalloc.start(25)  # Keep last 25 frames
            self.tracemalloc_active = True
    
    def take_snapshot(self) -> Dict[str, Any]:
        """Take a memory snapshot."""
        snapshot = {
            "timestamp": datetime.now(),
            "memory": psutil.virtual_memory()._asdict(),
            "gc_stats": gc.get_stats(),
            "tracemalloc": None
        }
        
        if self.tracemalloc_active:
            snapshot["tracemalloc"] = tracemalloc.take_snapshot()
        
        if HAS_PYMPLER:
            snapshot["summary"] = summary.get_most_common_types()
        
        self.memory_snapshots.append(snapshot)
        return snapshot
    
    def detect_leaks(self) -> List[MemoryLeak]:
        """Detect potential memory leaks."""
        if len(self.memory_snapshots) < 2:
            return []
        
        leaks = []
        latest = self.memory_snapshots[-1]
        previous = self.memory_snapshots[-2]
        
        # Compare object counts
        if HAS_PYMPLER and "summary" in latest and "summary" in previous:
            latest_summary = {item[0].__name__: item[1] for item in latest["summary"]}
            previous_summary = {item[0].__name__: item[1] for item in previous["summary"]}
            
            for obj_name, latest_count in latest_summary.items():
                previous_count = previous_summary.get(obj_name, 0)
                growth = latest_count - previous_count
                
                if growth > 100 and growth > previous_count * 0.5:  # Significant growth
                    leak = MemoryLeak(
                        object_type=obj_name,
                        previous_count=previous_count,
                        latest_count=latest_count,
                        growth=growth,
                        growth_rate=growth / max(previous_count, 1),
                        severity="high" if growth > 1000 else "medium"
                    )
                    leaks.append(leak)
        
        # Check tracemalloc for memory growth
        if (self.tracemalloc_active and 
            "tracemalloc" in latest and "tracemalloc" in previous):
            current_stats = latest["tracemalloc"].statistics("lineno")
            previous_stats = previous["tracemalloc"].statistics("lineno")
            
            for stat in current_stats:
                if stat.size_diff > 1024 * 1024:  # 1MB growth
                    leak = MemoryLeak(
                        object_type=f"tracemalloc:{stat.traceback.format()[:100]}",
                        previous_count=0,
                        latest_count=stat.count,
                        growth=stat.size_diff,
                        growth_rate=1.0,
                        severity="high" if stat.size_diff > 10 * 1024 * 1024 else "medium"
                    )
                    leaks.append(leak)
        
        self.leak_candidates.extend(leaks)
        return leaks
    
    def get_leak_report(self) -> Dict[str, Any]:
        """Get comprehensive leak report."""
        return {
            "total_leaks": len(self.leak_candidates),
            "recent_leaks": self.leak_candidates[-10:] if self.leak_candidates else [],
            "memory_snapshots": len(self.memory_snapshots),
            "tracemalloc_active": self.tracemalloc_active
        }

# =============================================================================
# Memory Optimizer
# =============================================================================

class MemoryOptimizer:
    """Advanced memory optimization strategies."""
    
    def __init__(self):
        self.compression_algorithms = {
            CompressionAlgorithm.ZLIB: zlib,
            CompressionAlgorithm.LZ4: lz4,
            CompressionAlgorithm.BROTLI: brotli,
            CompressionAlgorithm.ZSTD: None  # Will be set if available
        }
        
        # Try to import zstd
        try:
            import zstandard as zstd
            self.compression_algorithms[CompressionAlgorithm.ZSTD] = zstd
        except ImportError:
            pass
    
    def optimize_memory(self, strategy: MemoryStrategy) -> Dict[str, Any]:
        """Apply memory optimization strategy."""
        results = {
            "strategy": strategy.value,
            "timestamp": datetime.now(),
            "optimizations_applied": [],
            "memory_freed_mb": 0,
            "gc_collections": 0
        }
        
        if strategy == MemoryStrategy.LIGHT:
            results.update(self._light_optimization())
        elif strategy == MemoryStrategy.MEDIUM:
            results.update(self._medium_optimization())
        elif strategy == MemoryStrategy.AGGRESSIVE:
            results.update(self._aggressive_optimization())
        elif strategy == MemoryStrategy.EMERGENCY:
            results.update(self._emergency_optimization())
        
        return results
    
    def _light_optimization(self) -> Dict[str, Any]:
        """Light memory optimization."""
        before_memory = psutil.virtual_memory().used
        
        # Basic garbage collection
        gc.collect()
        
        after_memory = psutil.virtual_memory().used
        memory_freed = before_memory - after_memory
        
        return {
            "memory_freed_mb": memory_freed / (1024 * 1024),
            "gc_collections": 1,
            "optimizations_applied": ["basic_gc"]
        }
    
    def _medium_optimization(self) -> Dict[str, Any]:
        """Medium memory optimization."""
        before_memory = psutil.virtual_memory().used
        
        # Multiple GC passes
        for _ in range(3):
            gc.collect()
        
        # Clear some caches
        if hasattr(sys, 'intern'):
            sys.intern.clear()
        
        after_memory = psutil.virtual_memory().used
        memory_freed = before_memory - after_memory
        
        return {
            "memory_freed_mb": memory_freed / (1024 * 1024),
            "gc_collections": 3,
            "optimizations_applied": ["multiple_gc", "cache_clear"]
        }
    
    def _aggressive_optimization(self) -> Dict[str, Any]:
        """Aggressive memory optimization."""
        before_memory = psutil.virtual_memory().used
        
        # Multiple GC passes with different generations
        for generation in range(3):
            gc.collect(generation)
        
        # Clear all caches
        if hasattr(sys, 'intern'):
            sys.intern.clear()
        
        # Force memory compaction
        if hasattr(gc, 'compact'):
            gc.compact()
        
        after_memory = psutil.virtual_memory().used
        memory_freed = before_memory - after_memory
        
        return {
            "memory_freed_mb": memory_freed / (1024 * 1024),
            "gc_collections": 3,
            "optimizations_applied": ["generational_gc", "cache_clear", "memory_compaction"]
        }
    
    def _emergency_optimization(self) -> Dict[str, Any]:
        """Emergency memory optimization."""
        before_memory = psutil.virtual_memory().used
        
        # Maximum GC effort
        for _ in range(5):
            gc.collect()
        
        # Clear all possible caches
        if hasattr(sys, 'intern'):
            sys.intern.clear()
        
        # Force memory compaction
        if hasattr(gc, 'compact'):
            gc.compact()
        
        # Clear numpy cache if available
        if hasattr(np, 'get_include'):
            try:
                np.core._internal._clear_typenum_cache()
            except:
                pass
        
        after_memory = psutil.virtual_memory().used
        memory_freed = before_memory - after_memory
        
        return {
            "memory_freed_mb": memory_freed / (1024 * 1024),
            "gc_collections": 5,
            "optimizations_applied": ["maximum_gc", "cache_clear", "memory_compaction", "numpy_cache_clear"]
        }

# =============================================================================
# Unified Memory Manager
# =============================================================================

class UnifiedMemoryManager:
    """
    🚀 Unified Memory Manager - Single source of truth for memory management.
    
    Consolidates all memory management functionality and eliminates
    the scattered implementations that were causing memory leaks.
    """
    
    def __init__(self, 
                 monitoring_interval: int = 30,
                 cleanup_interval: int = 300,
                 memory_thresholds: Dict[str, float] = None):
        
        # Configuration
        self.monitoring_interval = monitoring_interval
        self.cleanup_interval = cleanup_interval
        self.memory_thresholds = memory_thresholds or {
            "low": 0.5,      # 50%
            "medium": 0.75,  # 75%
            "high": 0.9,     # 90%
            "critical": 0.95 # 95%
        }
        
        # Components
        self.leak_detector = MemoryLeakDetector()
        self.optimizer = MemoryOptimizer()
        
        # State
        self.monitoring_active = False
        self.monitoring_thread = None
        self.memory_history = deque(maxlen=1000)
        self.last_cleanup = time.time()
        self.optimization_history = deque(maxlen=100)
        
        # Performance tracking
        self.operation_times = defaultdict(list)
        self.memory_usage_tracking = {}
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background memory monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="MemoryMonitor"
        )
        self.monitoring_thread.start()
        logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop background memory monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Memory monitoring stopped")
    
    def _monitoring_loop(self):
        """Background memory monitoring loop."""
        while self.monitoring_active:
            try:
                # Take memory snapshot
                self.leak_detector.take_snapshot()
                
                # Get current metrics
                metrics = self.get_memory_metrics()
                self.memory_history.append(metrics)
                
                # Check for memory threshold
                threshold = self._get_memory_threshold(metrics.memory_percentage)
                if threshold != MemoryThreshold.LOW:
                    self._apply_optimization_strategy(threshold, metrics)
                
                # Periodic cleanup
                if time.time() - self.last_cleanup > self.cleanup_interval:
                    self._perform_periodic_cleanup()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _get_memory_threshold(self, memory_percentage: float) -> MemoryThreshold:
        """Determine memory usage threshold."""
        if memory_percentage >= self.memory_thresholds["critical"]:
            return MemoryThreshold.CRITICAL
        elif memory_percentage >= self.memory_thresholds["high"]:
            return MemoryThreshold.HIGH
        elif memory_percentage >= self.memory_thresholds["medium"]:
            return MemoryThreshold.MEDIUM
        else:
            return MemoryThreshold.LOW
    
    def _apply_optimization_strategy(self, threshold: MemoryThreshold, metrics: MemoryMetrics):
        """Apply appropriate optimization strategy based on threshold."""
        strategy_map = {
            MemoryThreshold.MEDIUM: MemoryStrategy.LIGHT,
            MemoryThreshold.HIGH: MemoryStrategy.MEDIUM,
            MemoryThreshold.CRITICAL: MemoryStrategy.AGGRESSIVE
        }
        
        strategy = strategy_map.get(threshold, MemoryStrategy.LIGHT)
        logger.warning(f"Memory threshold {threshold.value} reached, applying {strategy.value} optimization")
        
        results = self.optimizer.optimize_memory(strategy)
        self.optimization_history.append(results)
        
        logger.info(f"Memory optimization completed: {results['memory_freed_mb']:.2f}MB freed")
    
    def _perform_periodic_cleanup(self):
        """Perform periodic memory cleanup."""
        self.last_cleanup = time.time()
        
        # Light cleanup every 5 minutes
        results = self.optimizer.optimize_memory(MemoryStrategy.LIGHT)
        self.optimization_history.append(results)
        
        # Clear old history to prevent memory buildup
        if len(self.memory_history) > 500:
            self.memory_history = deque(list(self.memory_history)[-500:], maxlen=1000)
        
        if len(self.optimization_history) > 50:
            self.optimization_history = deque(list(self.optimization_history)[-50:], maxlen=100)
    
    def get_memory_metrics(self) -> MemoryMetrics:
        """Get current memory usage metrics."""
        memory = psutil.virtual_memory()
        gc_stats = gc.get_stats()
        
        return MemoryMetrics(
            total_memory=memory.total,
            used_memory=memory.used,
            available_memory=memory.available,
            memory_percentage=memory.percent / 100,
            gc_objects=sum(stat['collections'] for stat in gc_stats),
            gc_collections=len(gc_stats),
            memory_leaks=self.leak_detector.detect_leaks()
        )
    
    def get_memory_report(self) -> Dict[str, Any]:
        """Get comprehensive memory report."""
        current_metrics = self.get_memory_metrics()
        
        return {
            "current": current_metrics,
            "history": {
                "memory_usage": [m.memory_percentage for m in list(self.memory_history)[-100:]],
                "timestamps": [m.timestamp.isoformat() for m in list(self.memory_history)[-100:]]
            },
            "leaks": self.leak_detector.get_leak_report(),
            "optimizations": list(self.optimization_history)[-10:],
            "performance": {
                "operation_times": dict(self.operation_times),
                "memory_tracking": self.memory_usage_tracking
            }
        }
    
    @contextmanager
    def track_memory(self, operation_name: str):
        """Context manager for tracking memory usage during operations."""
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            
            duration = end_time - start_time
            memory_change = end_memory - start_memory
            
            self.operation_times[operation_name].append(duration)
            self.memory_usage_tracking[operation_name] = {
                "duration": duration,
                "memory_change_mb": memory_change / (1024 * 1024),
                "timestamp": datetime.now()
            }
            
            # Keep only last 100 measurements
            if len(self.operation_times[operation_name]) > 100:
                self.operation_times[operation_name] = self.operation_times[operation_name][-100:]
    
    async def track_memory_async(self, operation_name: str):
        """Decorator for tracking memory usage in async functions."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                with self.track_memory(operation_name):
                    return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def optimize_for_ai_models(self):
        """Special optimization for AI model operations."""
        logger.info("Applying AI model-specific memory optimization")
        
        # Clear PyTorch cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("PyTorch CUDA cache cleared")
        except ImportError:
            pass
        
        # Clear numpy cache
        try:
            np.core._internal._clear_typenum_cache()
        except:
            pass
        
        # Aggressive optimization
        results = self.optimizer.optimize_memory(MemoryStrategy.AGGRESSIVE)
        self.optimization_history.append(results)
        
        return results
    
    def __del__(self):
        """Cleanup on deletion."""
        self.stop_monitoring()
        if self.tracemalloc_active:
            tracemalloc.stop()

# =============================================================================
# Global Instance and Utilities
# =============================================================================

# Global memory manager instance
_memory_manager: Optional[UnifiedMemoryManager] = None

def get_memory_manager() -> UnifiedMemoryManager:
    """Get or create global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = UnifiedMemoryManager()
    return _memory_manager

def track_memory_async(operation_name: str):
    """Decorator for tracking memory usage in async functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            manager = get_memory_manager()
            with manager.track_memory(operation_name):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

def get_memory_report() -> Dict[str, Any]:
    """Get memory report from global manager."""
    return get_memory_manager().get_memory_report()

def optimize_memory(strategy: MemoryStrategy = MemoryStrategy.MEDIUM) -> Dict[str, Any]:
    """Optimize memory using global manager."""
    return get_memory_manager().optimizer.optimize_memory(strategy)

# =============================================================================
# Performance Monitoring
# =============================================================================

class MemoryPerformanceMonitor:
    """Monitor memory performance metrics."""
    
    def __init__(self):
        self.manager = get_memory_manager()
        self.metrics_history = deque(maxlen=1000)
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance metric."""
        metric = {
            "name": metric_name,
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.now()
        }
        self.metrics_history.append(metric)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics_history:
            return {}
        
        metrics_by_name = defaultdict(list)
        for metric in self.metrics_history:
            metrics_by_name[metric["name"]].append(metric["value"])
        
        summary = {}
        for name, values in metrics_by_name.items():
            summary[name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "recent": values[-10:] if len(values) > 10 else values
            }
        
        return summary

# Global performance monitor
performance_monitor = MemoryPerformanceMonitor()

if __name__ == "__main__":
    # Test the memory manager
    manager = UnifiedMemoryManager()
    
    try:
        # Simulate some memory usage
        print("Testing memory manager...")
        
        # Get initial report
        report = manager.get_memory_report()
        print(f"Initial memory usage: {report['current'].memory_percentage:.2%}")
        
        # Test memory tracking
        with manager.track_memory("test_operation"):
            # Simulate work
            time.sleep(1)
            _ = [i for i in range(1000000)]
        
        # Get final report
        final_report = manager.get_memory_report()
        print(f"Final memory usage: {final_report['current'].memory_percentage:.2%}")
        
        # Show performance metrics
        performance = final_report['performance']
        print(f"Operation times: {performance['operation_times']}")
        
    finally:
        manager.stop_monitoring()
        print("Memory manager test completed")
