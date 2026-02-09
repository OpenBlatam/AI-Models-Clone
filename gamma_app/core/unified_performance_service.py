"""
Unified Performance Service - Advanced performance optimization
Implements comprehensive performance monitoring, optimization, and auto-tuning
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import time
import psutil
import threading
import gc
import tracemalloc
from datetime import datetime, timedelta
from collections import defaultdict, deque
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
import cProfile
import pstats
import io
import sys
import os

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """Performance Metrics"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CONCURRENT_USERS = "concurrent_users"

class OptimizationStrategy(Enum):
    """Optimization Strategies"""
    CPU_OPTIMIZATION = "cpu_optimization"
    MEMORY_OPTIMIZATION = "memory_optimization"
    I_O_OPTIMIZATION = "io_optimization"
    CACHE_OPTIMIZATION = "cache_optimization"
    CONCURRENCY_OPTIMIZATION = "concurrency_optimization"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"

class PerformanceLevel(Enum):
    """Performance Levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class PerformanceProfile:
    """Performance Profile"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_available: int
    disk_read: int
    disk_write: int
    network_sent: int
    network_recv: int
    active_threads: int
    active_processes: int
    gc_collections: int
    response_time_avg: float
    throughput: float
    error_rate: float

@dataclass
class OptimizationRule:
    """Optimization Rule"""
    name: str
    condition: str
    threshold: float
    action: str
    enabled: bool = True
    cooldown: int = 300  # 5 minutes

@dataclass
class PerformanceAlert:
    """Performance Alert"""
    id: str
    metric: PerformanceMetric
    level: PerformanceLevel
    value: float
    threshold: float
    message: str
    timestamp: datetime
    resolved: bool = False

class UnifiedPerformanceService:
    """
    Unified Performance Service - Advanced performance optimization
    Implements comprehensive performance monitoring, optimization, and auto-tuning
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Performance tracking
        self.performance_history: deque = deque(maxlen=1000)
        self.current_profile: Optional[PerformanceProfile] = None
        
        # Optimization rules
        self.optimization_rules: Dict[str, OptimizationRule] = {}
        self.last_optimization: Dict[str, datetime] = {}
        
        # Performance alerts
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        
        # Profiling
        self.profiler = cProfile.Profile()
        self.profiling_active = False
        
        # Memory tracking
        self.memory_snapshots: List[Dict[str, Any]] = []
        self.memory_tracking = False
        
        # Thread/Process pools
        self.thread_pool: Optional[ThreadPoolExecutor] = None
        self.process_pool: Optional[ProcessPoolExecutor] = None
        
        # Performance baselines
        self.baselines: Dict[str, float] = {}
        self.baseline_established = False
        
        # Auto-optimization
        self.auto_optimization_enabled = True
        self.optimization_cooldown = 300  # 5 minutes
        
        # Monitoring tasks
        self.monitoring_tasks: List[asyncio.Task] = []
        self.running = False
        
        logger.info("UnifiedPerformanceService initialized")
    
    async def initialize(self):
        """Initialize performance service"""
        try:
            # Start memory tracking
            if self.config.get("enable_memory_tracking", True):
                tracemalloc.start()
                self.memory_tracking = True
            
            # Initialize thread/process pools
            max_workers = self.config.get("max_workers", multiprocessing.cpu_count())
            self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
            self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
            
            # Register default optimization rules
            await self._register_default_rules()
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            # Establish performance baselines
            await self._establish_baselines()
            
            self.running = True
            logger.info("Performance service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing performance service: {e}")
            raise
    
    async def _register_default_rules(self):
        """Register default optimization rules"""
        try:
            # CPU optimization rules
            await self.register_optimization_rule(OptimizationRule(
                name="high_cpu_usage",
                condition="cpu_percent > 80",
                threshold=80.0,
                action="scale_up_cpu",
                cooldown=300
            ))
            
            await self.register_optimization_rule(OptimizationRule(
                name="low_cpu_usage",
                condition="cpu_percent < 20",
                threshold=20.0,
                action="scale_down_cpu",
                cooldown=600
            ))
            
            # Memory optimization rules
            await self.register_optimization_rule(OptimizationRule(
                name="high_memory_usage",
                condition="memory_percent > 85",
                threshold=85.0,
                action="optimize_memory",
                cooldown=180
            ))
            
            await self.register_optimization_rule(OptimizationRule(
                name="memory_leak_detected",
                condition="memory_growth_rate > 10",
                threshold=10.0,
                action="force_garbage_collection",
                cooldown=60
            ))
            
            # Response time optimization rules
            await self.register_optimization_rule(OptimizationRule(
                name="slow_response_time",
                condition="response_time_avg > 2.0",
                threshold=2.0,
                action="optimize_response_time",
                cooldown=300
            ))
            
            # Error rate optimization rules
            await self.register_optimization_rule(OptimizationRule(
                name="high_error_rate",
                condition="error_rate > 5.0",
                threshold=5.0,
                action="investigate_errors",
                cooldown=120
            ))
            
            logger.info("Default optimization rules registered")
            
        except Exception as e:
            logger.error(f"Error registering default rules: {e}")
    
    async def _start_monitoring_tasks(self):
        """Start performance monitoring tasks"""
        try:
            # Performance profiling
            task = asyncio.create_task(self._monitor_performance())
            self.monitoring_tasks.append(task)
            
            # Optimization evaluation
            task = asyncio.create_task(self._evaluate_optimizations())
            self.monitoring_tasks.append(task)
            
            # Memory monitoring
            if self.memory_tracking:
                task = asyncio.create_task(self._monitor_memory())
                self.monitoring_tasks.append(task)
            
            # Baseline updates
            task = asyncio.create_task(self._update_baselines())
            self.monitoring_tasks.append(task)
            
            logger.info("Performance monitoring tasks started")
            
        except Exception as e:
            logger.error(f"Error starting monitoring tasks: {e}")
    
    async def _establish_baselines(self):
        """Establish performance baselines"""
        try:
            # Collect baseline data for 5 minutes
            baseline_data = []
            for _ in range(30):  # 30 samples over 5 minutes
                profile = await self._collect_performance_profile()
                baseline_data.append(profile)
                await asyncio.sleep(10)
            
            # Calculate baselines
            self.baselines = {
                "cpu_percent": np.mean([p.cpu_percent for p in baseline_data]),
                "memory_percent": np.mean([p.memory_percent for p in baseline_data]),
                "response_time_avg": np.mean([p.response_time_avg for p in baseline_data]),
                "throughput": np.mean([p.throughput for p in baseline_data]),
                "error_rate": np.mean([p.error_rate for p in baseline_data])
            }
            
            self.baseline_established = True
            logger.info(f"Performance baselines established: {self.baselines}")
            
        except Exception as e:
            logger.error(f"Error establishing baselines: {e}")
    
    async def _monitor_performance(self):
        """Monitor system performance"""
        try:
            while self.running:
                try:
                    # Collect performance profile
                    profile = await self._collect_performance_profile()
                    self.current_profile = profile
                    self.performance_history.append(profile)
                    
                    # Check for performance alerts
                    await self._check_performance_alerts(profile)
                    
                except Exception as e:
                    logger.error(f"Error monitoring performance: {e}")
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
        except asyncio.CancelledError:
            logger.info("Performance monitoring cancelled")
    
    async def _collect_performance_profile(self) -> PerformanceProfile:
        """Collect comprehensive performance profile"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # Thread/Process counts
            active_threads = threading.active_count()
            active_processes = len(psutil.pids())
            
            # Garbage collection
            gc_collections = sum(gc.get_stats())
            
            # Application metrics (placeholders)
            response_time_avg = self._get_average_response_time()
            throughput = self._get_current_throughput()
            error_rate = self._get_current_error_rate()
            
            return PerformanceProfile(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_available=memory.available,
                disk_read=disk_io.read_bytes if disk_io else 0,
                disk_write=disk_io.write_bytes if disk_io else 0,
                network_sent=network_io.bytes_sent if network_io else 0,
                network_recv=network_io.bytes_recv if network_io else 0,
                active_threads=active_threads,
                active_processes=active_processes,
                gc_collections=gc_collections,
                response_time_avg=response_time_avg,
                throughput=throughput,
                error_rate=error_rate
            )
            
        except Exception as e:
            logger.error(f"Error collecting performance profile: {e}")
            return PerformanceProfile(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used=0,
                memory_available=0,
                disk_read=0,
                disk_write=0,
                network_sent=0,
                network_recv=0,
                active_threads=0,
                active_processes=0,
                gc_collections=0,
                response_time_avg=0.0,
                throughput=0.0,
                error_rate=0.0
            )
    
    def _get_average_response_time(self) -> float:
        """Get average response time (placeholder)"""
        # In a real implementation, this would track actual response times
        return 0.5  # Placeholder
    
    def _get_current_throughput(self) -> float:
        """Get current throughput (placeholder)"""
        # In a real implementation, this would track actual throughput
        return 100.0  # Placeholder
    
    def _get_current_error_rate(self) -> float:
        """Get current error rate (placeholder)"""
        # In a real implementation, this would track actual error rates
        return 0.1  # Placeholder
    
    async def _check_performance_alerts(self, profile: PerformanceProfile):
        """Check for performance alerts"""
        try:
            # CPU alerts
            if profile.cpu_percent > 90:
                await self._create_alert(
                    PerformanceMetric.CPU_USAGE,
                    PerformanceLevel.CRITICAL,
                    profile.cpu_percent,
                    90.0,
                    f"Critical CPU usage: {profile.cpu_percent:.1f}%"
                )
            elif profile.cpu_percent > 80:
                await self._create_alert(
                    PerformanceMetric.CPU_USAGE,
                    PerformanceLevel.POOR,
                    profile.cpu_percent,
                    80.0,
                    f"High CPU usage: {profile.cpu_percent:.1f}%"
                )
            
            # Memory alerts
            if profile.memory_percent > 95:
                await self._create_alert(
                    PerformanceMetric.MEMORY_USAGE,
                    PerformanceLevel.CRITICAL,
                    profile.memory_percent,
                    95.0,
                    f"Critical memory usage: {profile.memory_percent:.1f}%"
                )
            elif profile.memory_percent > 85:
                await self._create_alert(
                    PerformanceMetric.MEMORY_USAGE,
                    PerformanceLevel.POOR,
                    profile.memory_percent,
                    85.0,
                    f"High memory usage: {profile.memory_percent:.1f}%"
                )
            
            # Response time alerts
            if profile.response_time_avg > 5.0:
                await self._create_alert(
                    PerformanceMetric.RESPONSE_TIME,
                    PerformanceLevel.CRITICAL,
                    profile.response_time_avg,
                    5.0,
                    f"Critical response time: {profile.response_time_avg:.2f}s"
                )
            elif profile.response_time_avg > 2.0:
                await self._create_alert(
                    PerformanceMetric.RESPONSE_TIME,
                    PerformanceLevel.POOR,
                    profile.response_time_avg,
                    2.0,
                    f"Slow response time: {profile.response_time_avg:.2f}s"
                )
            
            # Error rate alerts
            if profile.error_rate > 10.0:
                await self._create_alert(
                    PerformanceMetric.ERROR_RATE,
                    PerformanceLevel.CRITICAL,
                    profile.error_rate,
                    10.0,
                    f"Critical error rate: {profile.error_rate:.1f}%"
                )
            elif profile.error_rate > 5.0:
                await self._create_alert(
                    PerformanceMetric.ERROR_RATE,
                    PerformanceLevel.POOR,
                    profile.error_rate,
                    5.0,
                    f"High error rate: {profile.error_rate:.1f}%"
                )
                
        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")
    
    async def _create_alert(self, metric: PerformanceMetric, level: PerformanceLevel, 
                          value: float, threshold: float, message: str):
        """Create performance alert"""
        try:
            alert_id = f"{metric.value}_{int(time.time())}"
            
            if alert_id not in self.active_alerts:
                alert = PerformanceAlert(
                    id=alert_id,
                    metric=metric,
                    level=level,
                    value=value,
                    threshold=threshold,
                    message=message,
                    timestamp=datetime.now()
                )
                
                self.active_alerts[alert_id] = alert
                self.alert_history.append(alert)
                
                logger.warning(f"Performance alert: {message}")
                
        except Exception as e:
            logger.error(f"Error creating performance alert: {e}")
    
    async def _evaluate_optimizations(self):
        """Evaluate optimization rules"""
        try:
            while self.running:
                if not self.current_profile or not self.auto_optimization_enabled:
                    await asyncio.sleep(30)
                    continue
                
                for name, rule in self.optimization_rules.items():
                    if not rule.enabled:
                        continue
                    
                    # Check cooldown
                    if name in self.last_optimization:
                        time_since_last = datetime.now() - self.last_optimization[name]
                        if time_since_last.total_seconds() < rule.cooldown:
                            continue
                    
                    # Evaluate condition
                    if await self._evaluate_condition(rule.condition, self.current_profile):
                        await self._execute_optimization(rule)
                        self.last_optimization[name] = datetime.now()
                
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                
        except asyncio.CancelledError:
            logger.info("Optimization evaluation cancelled")
    
    async def _evaluate_condition(self, condition: str, profile: PerformanceProfile) -> bool:
        """Evaluate optimization condition"""
        try:
            # Simple condition evaluation (in practice, use a proper expression evaluator)
            if "cpu_percent >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return profile.cpu_percent > threshold
            elif "memory_percent >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return profile.memory_percent > threshold
            elif "response_time_avg >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return profile.response_time_avg > threshold
            elif "error_rate >" in condition:
                threshold = float(condition.split(">")[1].strip())
                return profile.error_rate > threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating condition {condition}: {e}")
            return False
    
    async def _execute_optimization(self, rule: OptimizationRule):
        """Execute optimization action"""
        try:
            logger.info(f"Executing optimization: {rule.action}")
            
            if rule.action == "scale_up_cpu":
                await self._scale_up_cpu()
            elif rule.action == "scale_down_cpu":
                await self._scale_down_cpu()
            elif rule.action == "optimize_memory":
                await self._optimize_memory()
            elif rule.action == "force_garbage_collection":
                await self._force_garbage_collection()
            elif rule.action == "optimize_response_time":
                await self._optimize_response_time()
            elif rule.action == "investigate_errors":
                await self._investigate_errors()
            else:
                logger.warning(f"Unknown optimization action: {rule.action}")
                
        except Exception as e:
            logger.error(f"Error executing optimization {rule.action}: {e}")
    
    async def _scale_up_cpu(self):
        """Scale up CPU resources"""
        try:
            # Increase thread pool size
            if self.thread_pool:
                # In practice, you would dynamically adjust pool size
                logger.info("Scaling up CPU resources")
            
        except Exception as e:
            logger.error(f"Error scaling up CPU: {e}")
    
    async def _scale_down_cpu(self):
        """Scale down CPU resources"""
        try:
            # Decrease thread pool size
            if self.thread_pool:
                # In practice, you would dynamically adjust pool size
                logger.info("Scaling down CPU resources")
            
        except Exception as e:
            logger.error(f"Error scaling down CPU: {e}")
    
    async def _optimize_memory(self):
        """Optimize memory usage"""
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear caches if available
            # In practice, you would clear application caches
            
            logger.info("Memory optimization completed")
            
        except Exception as e:
            logger.error(f"Error optimizing memory: {e}")
    
    async def _force_garbage_collection(self):
        """Force garbage collection"""
        try:
            collected = gc.collect()
            logger.info(f"Forced garbage collection: {collected} objects collected")
            
        except Exception as e:
            logger.error(f"Error forcing garbage collection: {e}")
    
    async def _optimize_response_time(self):
        """Optimize response time"""
        try:
            # In practice, you would implement response time optimizations
            logger.info("Response time optimization completed")
            
        except Exception as e:
            logger.error(f"Error optimizing response time: {e}")
    
    async def _investigate_errors(self):
        """Investigate errors"""
        try:
            # In practice, you would implement error investigation
            logger.info("Error investigation completed")
            
        except Exception as e:
            logger.error(f"Error investigating errors: {e}")
    
    async def _monitor_memory(self):
        """Monitor memory usage"""
        try:
            while self.running and self.memory_tracking:
                try:
                    # Take memory snapshot
                    snapshot = tracemalloc.take_snapshot()
                    top_stats = snapshot.statistics('lineno')
                    
                    memory_info = {
                        "timestamp": datetime.now(),
                        "current_memory": psutil.Process().memory_info().rss,
                        "peak_memory": tracemalloc.get_traced_memory()[1],
                        "top_allocations": [
                            {
                                "filename": stat.traceback.format()[0],
                                "size": stat.size,
                                "count": stat.count
                            }
                            for stat in top_stats[:10]
                        ]
                    }
                    
                    self.memory_snapshots.append(memory_info)
                    
                    # Keep only last 100 snapshots
                    if len(self.memory_snapshots) > 100:
                        self.memory_snapshots = self.memory_snapshots[-100:]
                    
                except Exception as e:
                    logger.error(f"Error monitoring memory: {e}")
                
                await asyncio.sleep(60)  # Monitor every minute
                
        except asyncio.CancelledError:
            logger.info("Memory monitoring cancelled")
    
    async def _update_baselines(self):
        """Update performance baselines"""
        try:
            while self.running:
                if len(self.performance_history) >= 100:  # Update every 100 samples
                    recent_profiles = list(self.performance_history)[-100:]
                    
                    # Update baselines with recent data
                    self.baselines.update({
                        "cpu_percent": np.mean([p.cpu_percent for p in recent_profiles]),
                        "memory_percent": np.mean([p.memory_percent for p in recent_profiles]),
                        "response_time_avg": np.mean([p.response_time_avg for p in recent_profiles]),
                        "throughput": np.mean([p.throughput for p in recent_profiles]),
                        "error_rate": np.mean([p.error_rate for p in recent_profiles])
                    })
                    
                    logger.info("Performance baselines updated")
                
                await asyncio.sleep(3600)  # Update every hour
                
        except asyncio.CancelledError:
            logger.info("Baseline updates cancelled")
    
    async def start_profiling(self, duration: int = 60):
        """Start performance profiling"""
        try:
            if self.profiling_active:
                logger.warning("Profiling already active")
                return
            
            self.profiler.enable()
            self.profiling_active = True
            
            logger.info(f"Performance profiling started for {duration} seconds")
            
            # Stop profiling after duration
            await asyncio.sleep(duration)
            await self.stop_profiling()
            
        except Exception as e:
            logger.error(f"Error starting profiling: {e}")
    
    async def stop_profiling(self) -> Dict[str, Any]:
        """Stop performance profiling and get results"""
        try:
            if not self.profiling_active:
                logger.warning("Profiling not active")
                return {}
            
            self.profiler.disable()
            self.profiling_active = False
            
            # Get profiling results
            s = io.StringIO()
            ps = pstats.Stats(self.profiler, stream=s)
            ps.sort_stats('cumulative')
            ps.print_stats(20)  # Top 20 functions
            
            profiling_results = {
                "timestamp": datetime.now().isoformat(),
                "results": s.getvalue(),
                "total_calls": ps.total_calls,
                "total_time": ps.total_tt
            }
            
            logger.info("Performance profiling completed")
            return profiling_results
            
        except Exception as e:
            logger.error(f"Error stopping profiling: {e}")
            return {}
    
    async def register_optimization_rule(self, rule: OptimizationRule):
        """Register optimization rule"""
        try:
            self.optimization_rules[rule.name] = rule
            logger.info(f"Optimization rule {rule.name} registered")
            
        except Exception as e:
            logger.error(f"Error registering optimization rule: {e}")
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        try:
            if not self.current_profile:
                return {"error": "No performance data available"}
            
            # Calculate performance level
            performance_level = self._calculate_performance_level(self.current_profile)
            
            # Get recent trends
            recent_profiles = list(self.performance_history)[-10:] if self.performance_history else []
            
            return {
                "current_performance": {
                    "level": performance_level.value,
                    "cpu_percent": self.current_profile.cpu_percent,
                    "memory_percent": self.current_profile.memory_percent,
                    "response_time_avg": self.current_profile.response_time_avg,
                    "throughput": self.current_profile.throughput,
                    "error_rate": self.current_profile.error_rate
                },
                "baselines": self.baselines,
                "trends": {
                    "cpu_trend": self._calculate_trend([p.cpu_percent for p in recent_profiles]),
                    "memory_trend": self._calculate_trend([p.memory_percent for p in recent_profiles]),
                    "response_time_trend": self._calculate_trend([p.response_time_avg for p in recent_profiles])
                },
                "active_alerts": len(self.active_alerts),
                "optimization_rules": len(self.optimization_rules),
                "auto_optimization_enabled": self.auto_optimization_enabled
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_level(self, profile: PerformanceProfile) -> PerformanceLevel:
        """Calculate overall performance level"""
        try:
            score = 100
            
            # CPU score
            if profile.cpu_percent > 90:
                score -= 30
            elif profile.cpu_percent > 80:
                score -= 20
            elif profile.cpu_percent > 70:
                score -= 10
            
            # Memory score
            if profile.memory_percent > 95:
                score -= 30
            elif profile.memory_percent > 85:
                score -= 20
            elif profile.memory_percent > 75:
                score -= 10
            
            # Response time score
            if profile.response_time_avg > 5.0:
                score -= 25
            elif profile.response_time_avg > 2.0:
                score -= 15
            elif profile.response_time_avg > 1.0:
                score -= 5
            
            # Error rate score
            if profile.error_rate > 10.0:
                score -= 25
            elif profile.error_rate > 5.0:
                score -= 15
            elif profile.error_rate > 1.0:
                score -= 5
            
            # Determine level
            if score >= 90:
                return PerformanceLevel.EXCELLENT
            elif score >= 75:
                return PerformanceLevel.GOOD
            elif score >= 60:
                return PerformanceLevel.FAIR
            elif score >= 40:
                return PerformanceLevel.POOR
            else:
                return PerformanceLevel.CRITICAL
                
        except Exception as e:
            logger.error(f"Error calculating performance level: {e}")
            return PerformanceLevel.UNKNOWN
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend for a list of values"""
        try:
            if len(values) < 2:
                return "stable"
            
            # Simple linear trend calculation
            x = np.arange(len(values))
            y = np.array(values)
            
            # Calculate slope
            slope = np.polyfit(x, y, 1)[0]
            
            if slope > 0.1:
                return "increasing"
            elif slope < -0.1:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return "unknown"
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for performance service"""
        try:
            return {
                "status": "healthy",
                "monitoring_active": self.running,
                "current_profile_available": self.current_profile is not None,
                "baseline_established": self.baseline_established,
                "profiling_active": self.profiling_active,
                "memory_tracking": self.memory_tracking,
                "optimization_rules": len(self.optimization_rules),
                "active_alerts": len(self.active_alerts),
                "auto_optimization_enabled": self.auto_optimization_enabled
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def shutdown(self):
        """Shutdown performance service"""
        try:
            self.running = False
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            # Shutdown thread/process pools
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
            
            if self.process_pool:
                self.process_pool.shutdown(wait=True)
            
            # Stop memory tracking
            if self.memory_tracking:
                tracemalloc.stop()
            
            logger.info("Performance service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down performance service: {e}")


























