#!/usr/bin/env python3
"""
Advanced Memory Manager
Comprehensive memory optimization and leak prevention system
"""

import gc
import psutil
import asyncio
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import weakref
import tracemalloc
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class MemoryThreshold(Enum):
    """Memory threshold levels for different optimization strategies."""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    CRITICAL = 0.9

@dataclass
class MemoryMetrics:
    """Memory usage metrics."""
    total_memory: float
    used_memory: float
    available_memory: float
    memory_percentage: float
    gc_objects: int
    gc_collections: int
    memory_leaks: List[str]

class AdvancedMemoryManager:
    """
    Advanced memory management system with leak detection and optimization.
    """
    
    def __init__(self):
        self.memory_pool = {}
        self.object_tracker = weakref.WeakSet()
        self.cleanup_callbacks = []
        self.memory_thresholds = {
            MemoryThreshold.LOW: 0.3,
            MemoryThreshold.MEDIUM: 0.6,
            MemoryThreshold.HIGH: 0.8,
            MemoryThreshold.CRITICAL: 0.9
        }
        self.optimization_strategies = {
            MemoryThreshold.LOW: self._light_optimization,
            MemoryThreshold.MEDIUM: self._medium_optimization,
            MemoryThreshold.HIGH: self._aggressive_optimization,
            MemoryThreshold.CRITICAL: self._emergency_optimization
        }
        self.monitoring_active = False
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        self.memory_history = []
        self.leak_detector = MemoryLeakDetector()
        
        # Start monitoring
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start memory monitoring in background."""
        self.monitoring_active = True
        threading.Thread(target=self._monitor_memory, daemon=True).start()
        logger.info("Advanced memory monitoring started")
    
    def _monitor_memory(self):
        """Background memory monitoring."""
        while self.monitoring_active:
            try:
                metrics = self.get_memory_metrics()
                self.memory_history.append(metrics)
                
                # Keep only last 1000 measurements
                if len(self.memory_history) > 1000:
                    self.memory_history = self.memory_history[-1000:]
                
                # Check for memory threshold
                threshold = self._get_memory_threshold(metrics.memory_percentage)
                if threshold != MemoryThreshold.LOW:
                    self._apply_optimization_strategy(threshold, metrics)
                
                # Periodic cleanup
                if time.time() - self.last_cleanup > self.cleanup_interval:
                    self._perform_periodic_cleanup()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                time.sleep(30)  # Wait longer on error
    
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
    
    def _get_memory_threshold(self, memory_percentage: float) -> MemoryThreshold:
        """Determine memory threshold level."""
        if memory_percentage >= self.memory_thresholds[MemoryThreshold.CRITICAL]:
            return MemoryThreshold.CRITICAL
        elif memory_percentage >= self.memory_thresholds[MemoryThreshold.HIGH]:
            return MemoryThreshold.HIGH
        elif memory_percentage >= self.memory_thresholds[MemoryThreshold.MEDIUM]:
            return MemoryThreshold.MEDIUM
        else:
            return MemoryThreshold.LOW
    
    def _apply_optimization_strategy(self, threshold: MemoryThreshold, metrics: MemoryMetrics):
        """Apply optimization strategy based on memory threshold."""
        strategy = self.optimization_strategies[threshold]
        logger.warning(f"Memory threshold {threshold.name} reached ({metrics.memory_percentage:.1%})")
        strategy(metrics)
    
    def _light_optimization(self, metrics: MemoryMetrics):
        """Light memory optimization."""
        logger.info("Applying light memory optimization")
        gc.collect()
        self._cleanup_memory_pool()
    
    def _medium_optimization(self, metrics: MemoryMetrics):
        """Medium memory optimization."""
        logger.info("Applying medium memory optimization")
        gc.collect()
        self._cleanup_memory_pool()
        self._clear_caches()
        self._optimize_torch_memory()
    
    def _aggressive_optimization(self, metrics: MemoryMetrics):
        """Aggressive memory optimization."""
        logger.warning("Applying aggressive memory optimization")
        gc.collect()
        self._cleanup_memory_pool()
        self._clear_caches()
        self._optimize_torch_memory()
        self._force_garbage_collection()
        self._cleanup_weak_references()
    
    def _emergency_optimization(self, metrics: MemoryMetrics):
        """Emergency memory optimization."""
        logger.critical("Applying emergency memory optimization")
        gc.collect()
        self._cleanup_memory_pool()
        self._clear_caches()
        self._optimize_torch_memory()
        self._force_garbage_collection()
        self._cleanup_weak_references()
        self._clear_memory_history()
        self._emergency_cleanup()
    
    def _cleanup_memory_pool(self):
        """Clean up memory pool."""
        for key, obj in list(self.memory_pool.items()):
            if hasattr(obj, '__del__'):
                try:
                    del obj
                except:
                    pass
        self.memory_pool.clear()
    
    def _clear_caches(self):
        """Clear various caches."""
        # Clear function caches
        for func in list(self.object_tracker):
            if hasattr(func, 'cache_clear'):
                try:
                    func.cache_clear()
                except:
                    pass
        
        # Clear module caches
        import sys
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('__'):
                continue
            module = sys.modules.get(module_name)
            if module and hasattr(module, 'cache_clear'):
                try:
                    module.cache_clear()
                except:
                    pass
    
    def _optimize_torch_memory(self):
        """Optimize PyTorch memory usage."""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except ImportError:
            pass
    
    def _force_garbage_collection(self):
        """Force aggressive garbage collection."""
        gc.collect()
        gc.collect()
        gc.collect()
    
    def _cleanup_weak_references(self):
        """Clean up weak references."""
        self.object_tracker.clear()
    
    def _clear_memory_history(self):
        """Clear memory history to free memory."""
        self.memory_history.clear()
    
    def _emergency_cleanup(self):
        """Emergency cleanup procedures."""
        # Force cleanup of all callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except:
                pass
        self.cleanup_callbacks.clear()
    
    def _perform_periodic_cleanup(self):
        """Perform periodic cleanup tasks."""
        logger.info("Performing periodic memory cleanup")
        self._light_optimization(self.get_memory_metrics())
        self.last_cleanup = time.time()
    
    @contextmanager
    def memory_context(self, context_name: str):
        """Context manager for memory tracking."""
        start_metrics = self.get_memory_metrics()
        try:
            yield
        finally:
            end_metrics = self.get_memory_metrics()
            memory_diff = end_metrics.used_memory - start_metrics.used_memory
            if memory_diff > 1024 * 1024:  # 1MB threshold
                logger.warning(f"Memory increase in {context_name}: {memory_diff / 1024 / 1024:.2f}MB")
    
    def register_cleanup_callback(self, callback: Callable):
        """Register a cleanup callback."""
        self.cleanup_callbacks.append(callback)
    
    def get_memory_report(self) -> Dict[str, Any]:
        """Get comprehensive memory report."""
        metrics = self.get_memory_metrics()
        return {
            "current_usage_mb": metrics.used_memory / 1024 / 1024,
            "total_memory_mb": metrics.total_memory / 1024 / 1024,
            "memory_percentage": metrics.memory_percentage * 100,
            "gc_objects": metrics.gc_objects,
            "memory_leaks": metrics.memory_leaks,
            "pool_size": len(self.memory_pool),
            "tracked_objects": len(self.object_tracker),
            "cleanup_callbacks": len(self.cleanup_callbacks)
        }
    
    def shutdown(self):
        """Shutdown memory manager."""
        self.monitoring_active = False
        self._emergency_cleanup()
        logger.info("Advanced memory manager shutdown complete")

class MemoryLeakDetector:
    """Detect memory leaks in the system."""
    
    def __init__(self):
        self.snapshots = []
        self.max_snapshots = 10
    
    def detect_leaks(self) -> List[str]:
        """Detect potential memory leaks."""
        leaks = []
        
        # Take snapshot
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append(snapshot)
        
        # Keep only recent snapshots
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-self.max_snapshots:]
        
        # Compare with previous snapshot
        if len(self.snapshots) >= 2:
            current = self.snapshots[-1]
            previous = self.snapshots[-2]
            
            # Find top differences
            stats = current.compare_to(previous, 'lineno')
            for stat in stats[:5]:  # Top 5 differences
                if stat.size_diff > 1024 * 1024:  # 1MB threshold
                    leaks.append(f"{stat.traceback.format()}: +{stat.size_diff / 1024 / 1024:.2f}MB")
        
        return leaks

# Global memory manager instance
memory_manager = AdvancedMemoryManager()

def get_memory_manager() -> AdvancedMemoryManager:
    """Get the global memory manager instance."""
    return memory_manager

# Decorator for memory tracking
def track_memory(func):
    """Decorator to track memory usage of a function."""
    def wrapper(*args, **kwargs):
        with memory_manager.memory_context(func.__name__):
            return func(*args, **kwargs)
    return wrapper

# Async decorator for memory tracking
def track_memory_async(func):
    """Async decorator to track memory usage of a function."""
    async def wrapper(*args, **kwargs):
        with memory_manager.memory_context(func.__name__):
            return await func(*args, **kwargs)
    return wrapper 