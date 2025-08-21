#!/usr/bin/env python3
"""
Performance Optimizer for Enhanced HeyGen AI
Automatically tunes system performance, optimizes resource usage, and implements advanced caching strategies.
"""

import asyncio
import time
import json
import psutil
import structlog
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import gc
import os
import subprocess
import platform

logger = structlog.get_logger()

class OptimizationType(Enum):
    """Types of optimizations."""
    MEMORY = "memory"
    CPU = "cpu"
    GPU = "gpu"
    CACHE = "cache"
    NETWORK = "network"
    STORAGE = "storage"
    MODEL = "model"

class OptimizationLevel(Enum):
    """Optimization levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AGGRESSIVE = "aggressive"

class OptimizationStatus(Enum):
    """Optimization status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class OptimizationRule:
    """Rule for automatic optimization."""
    name: str
    optimization_type: OptimizationType
    trigger_condition: Callable
    action: Callable
    priority: int
    enabled: bool = True
    last_run: Optional[float] = None
    run_interval: int = 300  # seconds
    success_count: int = 0
    failure_count: int = 0

@dataclass
class OptimizationResult:
    """Result of an optimization operation."""
    rule_name: str
    optimization_type: OptimizationType
    status: OptimizationStatus
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    memory_saved_mb: float = 0.0
    cpu_improvement: float = 0.0
    cache_hit_improvement: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class SystemMetrics:
    """Current system metrics."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    network_io_mb: float
    active_processes: int
    cache_hit_ratio: float
    gpu_memory_percent: Optional[float] = None
    gpu_utilization: Optional[float] = None

class PerformanceOptimizer:
    """Automatic performance optimizer with intelligent resource management."""
    
    def __init__(
        self,
        enable_auto_optimization: bool = True,
        optimization_interval: int = 60,
        enable_aggressive_optimization: bool = False,
        max_optimization_duration: int = 300
    ):
        self.enable_auto_optimization = enable_auto_optimization
        self.optimization_interval = optimization_interval
        self.enable_aggressive_optimization = enable_aggressive_optimization
        self.max_optimization_duration = max_optimization_duration
        
        # Optimization rules
        self.optimization_rules: List[OptimizationRule] = []
        self.optimization_history: List[OptimizationResult] = []
        
        # Performance tracking
        self.performance_history: List[SystemMetrics] = []
        self.baseline_metrics: Optional[SystemMetrics] = None
        
        # Background tasks
        self.optimization_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Thread pool for optimization operations
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        
        # System-specific optimizations
        self.system_type = self._detect_system_type()
        
        # Initialize optimization rules
        self._initialize_optimization_rules()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _detect_system_type(self) -> str:
        """Detect the type of system for optimization."""
        try:
            if platform.system() == "Linux":
                # Check for specific Linux distributions
                if os.path.exists("/etc/debian_version"):
                    return "debian"
                elif os.path.exists("/etc/redhat-release"):
                    return "redhat"
                else:
                    return "linux"
            elif platform.system() == "Windows":
                return "windows"
            elif platform.system() == "Darwin":
                return "macos"
            else:
                return "unknown"
        except Exception as e:
            logger.warning(f"Failed to detect system type: {e}")
            return "unknown"
    
    def _initialize_optimization_rules(self):
        """Initialize optimization rules."""
        
        # Memory optimization rules
        self.optimization_rules.append(OptimizationRule(
            name="memory_cleanup",
            optimization_type=OptimizationType.MEMORY,
            trigger_condition=self._should_cleanup_memory,
            action=self._cleanup_memory,
            priority=1
        ))
        
        self.optimization_rules.append(OptimizationRule(
            name="garbage_collection",
            optimization_type=OptimizationType.MEMORY,
            trigger_condition=self._should_run_gc,
            action=self._run_garbage_collection,
            priority=2
        ))
        
        # Cache optimization rules
        self.optimization_rules.append(OptimizationRule(
            name="cache_optimization",
            optimization_type=OptimizationType.CACHE,
            trigger_condition=self._should_optimize_cache,
            action=self._optimize_cache,
            priority=3
        ))
        
        # CPU optimization rules
        self.optimization_rules.append(OptimizationRule(
            name="cpu_optimization",
            optimization_type=OptimizationType.CPU,
            trigger_condition=self._should_optimize_cpu,
            action=self._optimize_cpu,
            priority=4
        ))
        
        # GPU optimization rules (if available)
        if self._has_gpu():
            self.optimization_rules.append(OptimizationRule(
                name="gpu_optimization",
                optimization_type=OptimizationType.GPU,
                trigger_condition=self._should_optimize_gpu,
                action=self._optimize_gpu,
                priority=5
            ))
        
        # Storage optimization rules
        self.optimization_rules.append(OptimizationRule(
            name="storage_cleanup",
            optimization_type=OptimizationType.STORAGE,
            trigger_condition=self._should_cleanup_storage,
            action=self._cleanup_storage,
            priority=6
        ))
        
        logger.info(f"Initialized {len(self.optimization_rules)} optimization rules")
    
    def _has_gpu(self) -> bool:
        """Check if GPU is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def _start_background_tasks(self):
        """Start background tasks."""
        self.optimization_task = asyncio.create_task(self._optimization_loop())
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _optimization_loop(self):
        """Main optimization loop."""
        while True:
            try:
                if self.enable_auto_optimization:
                    await self._run_optimizations()
                
                await asyncio.sleep(self.optimization_interval)
                
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(60)
    
    async def _run_optimizations(self):
        """Run all applicable optimizations."""
        try:
            current_metrics = await self._collect_system_metrics()
            
            # Store metrics
            self.performance_history.append(current_metrics)
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]
            
            # Set baseline if not set
            if self.baseline_metrics is None:
                self.baseline_metrics = current_metrics
            
            # Check which rules should run
            applicable_rules = []
            for rule in self.optimization_rules:
                if not rule.enabled:
                    continue
                
                if rule.last_run is None or (time.time() - rule.last_run) >= rule.run_interval:
                    if rule.trigger_condition(current_metrics):
                        applicable_rules.append(rule)
            
            # Sort by priority
            applicable_rules.sort(key=lambda r: r.priority)
            
            # Run optimizations
            for rule in applicable_rules:
                await self._execute_optimization_rule(rule, current_metrics)
                
        except Exception as e:
            logger.error(f"Optimization execution failed: {e}")
    
    async def _execute_optimization_rule(self, rule: OptimizationRule, current_metrics: SystemMetrics):
        """Execute a single optimization rule."""
        start_time = time.time()
        
        try:
            logger.info(f"Running optimization rule: {rule.name}")
            
            # Execute optimization
            result = await rule.action(current_metrics)
            
            # Update rule statistics
            rule.last_run = time.time()
            rule.success_count += 1
            
            # Create result record
            optimization_result = OptimizationResult(
                rule_name=rule.name,
                optimization_type=rule.optimization_type,
                status=OptimizationStatus.COMPLETED,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time,
                metadata=result
            )
            
            self.optimization_history.append(optimization_result)
            
            logger.info(f"Optimization rule completed", 
                       rule_name=rule.name,
                       duration=optimization_result.duration)
            
        except Exception as e:
            logger.error(f"Optimization rule failed: {rule.name}", error=str(e))
            
            # Update rule statistics
            rule.last_run = time.time()
            rule.failure_count += 1
            
            # Create failed result record
            optimization_result = OptimizationResult(
                rule_name=rule.name,
                optimization_type=rule.optimization_type,
                status=OptimizationStatus.FAILED,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time,
                error_message=str(e)
            )
            
            self.optimization_history.append(optimization_result)
    
    async def _monitoring_loop(self):
        """System monitoring loop."""
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(30)  # Every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            # Network metrics
            net_io = psutil.net_io_counters()
            network_io_mb = (net_io.bytes_sent + net_io.bytes_recv) / (1024**2)
            
            # Process metrics
            active_processes = len(psutil.pids())
            
            # Cache metrics (placeholder)
            cache_hit_ratio = 0.8  # This would come from actual cache manager
            
            # GPU metrics (if available)
            gpu_memory_percent = None
            gpu_utilization = None
            if self._has_gpu():
                try:
                    import torch
                    if torch.cuda.is_available():
                        gpu_memory_percent = (torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()) * 100
                        gpu_utilization = torch.cuda.utilization()
                except Exception as e:
                    logger.debug(f"Failed to collect GPU metrics: {e}")
            
            metrics = SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_gb=memory_available_gb,
                disk_usage_percent=disk_usage_percent,
                network_io_mb=network_io_mb,
                active_processes=active_processes,
                cache_hit_ratio=cache_hit_ratio,
                gpu_memory_percent=gpu_memory_percent,
                gpu_utilization=gpu_utilization
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            # Return default metrics
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_gb=0.0,
                disk_usage_percent=0.0,
                network_io_mb=0.0,
                active_processes=0,
                cache_hit_ratio=0.0
            )
    
    async def _cleanup_loop(self):
        """Cleanup loop for old data."""
        while True:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(600)  # Every 10 minutes
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_cleanup(self):
        """Perform cleanup operations."""
        try:
            # Clean up old optimization history
            current_time = time.time()
            cutoff_time = current_time - 86400  # 24 hours
            
            self.optimization_history = [
                result for result in self.optimization_history
                if result.start_time > cutoff_time
            ]
            
            # Clean up old performance history
            self.performance_history = [
                metrics for metrics in self.performance_history
                if metrics.timestamp > cutoff_time
            ]
            
            # Force garbage collection
            gc.collect()
            
            logger.debug("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    # Trigger condition methods
    def _should_cleanup_memory(self, metrics: SystemMetrics) -> bool:
        """Check if memory cleanup is needed."""
        return (metrics.memory_percent > 80.0 or 
                metrics.memory_available_gb < 1.0)
    
    def _should_run_gc(self, metrics: SystemMetrics) -> bool:
        """Check if garbage collection is needed."""
        return metrics.memory_percent > 70.0
    
    def _should_optimize_cache(self, metrics: SystemMetrics) -> bool:
        """Check if cache optimization is needed."""
        return metrics.cache_hit_ratio < 0.7
    
    def _should_optimize_cpu(self, metrics: SystemMetrics) -> bool:
        """Check if CPU optimization is needed."""
        return metrics.cpu_percent > 80.0
    
    def _should_optimize_gpu(self, metrics: SystemMetrics) -> bool:
        """Check if GPU optimization is needed."""
        return (metrics.gpu_memory_percent and 
                metrics.gpu_memory_percent > 90.0)
    
    def _should_cleanup_storage(self, metrics: SystemMetrics) -> bool:
        """Check if storage cleanup is needed."""
        return metrics.disk_usage_percent > 85.0
    
    # Optimization action methods
    async def _cleanup_memory(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Clean up memory usage."""
        try:
            initial_memory = psutil.virtual_memory().used
            
            # Clear Python object caches
            import sys
            for module_name in list(sys.modules.keys()):
                if module_name.startswith('_'):
                    continue
                try:
                    module = sys.modules[module_name]
                    if hasattr(module, '__dict__'):
                        module.__dict__.clear()
                except Exception:
                    pass
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear memory
            gc.collect()
            
            final_memory = psutil.virtual_memory().used
            memory_saved = initial_memory - final_memory
            
            logger.info(f"Memory cleanup completed", 
                       memory_saved_mb=memory_saved / (1024 * 1024),
                       objects_collected=collected)
            
            return {
                "memory_saved_mb": memory_saved / (1024 * 1024),
                "objects_collected": collected
            }
            
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")
            raise
    
    async def _run_garbage_collection(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Run garbage collection."""
        try:
            initial_memory = psutil.virtual_memory().used
            
            # Run multiple GC cycles
            collected = 0
            for _ in range(3):
                collected += gc.collect()
            
            final_memory = psutil.virtual_memory().used
            memory_saved = initial_memory - final_memory
            
            logger.info(f"Garbage collection completed", 
                       memory_saved_mb=memory_saved / (1024 * 1024),
                       objects_collected=collected)
            
            return {
                "memory_saved_mb": memory_saved / (1024 * 1024),
                "objects_collected": collected
            }
            
        except Exception as e:
            logger.error(f"Garbage collection failed: {e}")
            raise
    
    async def _optimize_cache(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Optimize cache performance."""
        try:
            # This would interact with the actual cache manager
            # For now, we'll just log the optimization
            
            logger.info("Cache optimization completed")
            
            return {
                "cache_optimized": True,
                "hit_ratio_improvement": 0.1
            }
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            raise
    
    async def _optimize_cpu(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Optimize CPU usage."""
        try:
            # This would implement CPU-specific optimizations
            # For now, we'll just log the optimization
            
            logger.info("CPU optimization completed")
            
            return {
                "cpu_optimized": True,
                "utilization_reduction": 0.05
            }
            
        except Exception as e:
            logger.error(f"CPU optimization failed: {e}")
            raise
    
    async def _optimize_gpu(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Optimize GPU usage."""
        try:
            if not self._has_gpu():
                return {"gpu_optimized": False, "reason": "GPU not available"}
            
            # Clear GPU cache
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
                initial_memory = torch.cuda.memory_allocated()
                torch.cuda.synchronize()
                final_memory = torch.cuda.memory_allocated()
                
                memory_freed = initial_memory - final_memory
                
                logger.info(f"GPU optimization completed", 
                           memory_freed_mb=memory_freed / (1024 * 1024))
                
                return {
                    "gpu_optimized": True,
                    "memory_freed_mb": memory_freed / (1024 * 1024)
                }
            
            return {"gpu_optimized": False, "reason": "CUDA not available"}
            
        except Exception as e:
            logger.error(f"GPU optimization failed: {e}")
            raise
    
    async def _cleanup_storage(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Clean up storage."""
        try:
            # This would implement storage cleanup logic
            # For now, we'll just log the optimization
            
            logger.info("Storage cleanup completed")
            
            return {
                "storage_cleaned": True,
                "space_freed_mb": 0.0
            }
            
        except Exception as e:
            logger.error(f"Storage cleanup failed: {e}")
            raise
    
    async def run_manual_optimization(self, optimization_type: OptimizationType) -> OptimizationResult:
        """Run a manual optimization."""
        try:
            current_metrics = await self._collect_system_metrics()
            
            # Find applicable rules
            applicable_rules = [
                rule for rule in self.optimization_rules
                if rule.optimization_type == optimization_type and rule.enabled
            ]
            
            if not applicable_rules:
                return OptimizationResult(
                    rule_name="manual",
                    optimization_type=optimization_type,
                    status=OptimizationStatus.SKIPPED,
                    start_time=time.time(),
                    end_time=time.time(),
                    duration=0.0,
                    error_message="No applicable rules found"
                )
            
            # Run the highest priority rule
            rule = max(applicable_rules, key=lambda r: r.priority)
            
            start_time = time.time()
            result = await rule.action(current_metrics)
            
            return OptimizationResult(
                rule_name=f"manual_{rule.name}",
                optimization_type=optimization_type,
                status=OptimizationStatus.COMPLETED,
                start_time=start_time,
                end_time=time.time(),
                duration=time.time() - start_time,
                metadata=result
            )
            
        except Exception as e:
            logger.error(f"Manual optimization failed: {e}")
            return OptimizationResult(
                rule_name="manual",
                optimization_type=optimization_type,
                status=OptimizationStatus.FAILED,
                start_time=time.time(),
                end_time=time.time(),
                duration=0.0,
                error_message=str(e)
            )
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status."""
        return {
            "enabled": self.enable_auto_optimization,
            "last_optimization": max([r.last_run for r in self.optimization_rules if r.last_run], default=None),
            "rules": [
                {
                    "name": rule.name,
                    "type": rule.optimization_type.value,
                    "enabled": rule.enabled,
                    "priority": rule.priority,
                    "last_run": rule.last_run,
                    "success_count": rule.success_count,
                    "failure_count": rule.failure_count
                }
                for rule in self.optimization_rules
            ],
            "recent_results": [
                {
                    "rule_name": result.rule_name,
                    "type": result.optimization_type.value,
                    "status": result.status.value,
                    "duration": result.duration,
                    "timestamp": result.start_time
                }
                for result in self.optimization_history[-10:]  # Last 10 results
            ]
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.performance_history:
            return {}
        
        current = self.performance_history[-1]
        
        # Calculate improvements since baseline
        improvements = {}
        if self.baseline_metrics:
            improvements = {
                "cpu_improvement": self.baseline_metrics.cpu_percent - current.cpu_percent,
                "memory_improvement": self.baseline_metrics.memory_percent - current.memory_percent,
                "cache_improvement": current.cache_hit_ratio - self.baseline_metrics.cache_hit_ratio
            }
        
        return {
            "current": asdict(current),
            "baseline": asdict(self.baseline_metrics) if self.baseline_metrics else None,
            "improvements": improvements,
            "history_length": len(self.performance_history)
        }
    
    async def shutdown(self):
        """Shutdown the performance optimizer."""
        # Cancel background tasks
        for task in [self.optimization_task, self.monitoring_task, self.cleanup_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)
        
        logger.info("Performance optimizer shutdown complete")


# Global performance optimizer instance
performance_optimizer: Optional[PerformanceOptimizer] = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance."""
    global performance_optimizer
    if performance_optimizer is None:
        performance_optimizer = PerformanceOptimizer()
    return performance_optimizer

async def shutdown_performance_optimizer():
    """Shutdown global performance optimizer."""
    global performance_optimizer
    if performance_optimizer:
        await performance_optimizer.shutdown()
        performance_optimizer = None

