import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import statistics
from contextlib import asynccontextmanager
import threading
from collections import deque

logger = logging.getLogger("mobile_web_vitals")

# Mobile Web Vitals System
# Comprehensive monitoring and optimization for Load Time, Jank, and Responsiveness

@dataclass
class WebVitalMetrics:
    """Mobile Web Vitals metrics data structure."""
    timestamp: datetime
    load_time: float  # Time to load in seconds
    first_contentful_paint: float  # FCP in seconds
    largest_contentful_paint: float  # LCP in seconds
    first_input_delay: float  # FID in seconds
    cumulative_layout_shift: float  # CLS score
    jank_score: float  # Jank percentage
    responsiveness_score: float  # Responsiveness score (0-100)
    total_blocking_time: float  # TBT in seconds
    time_to_interactive: float  # TTI in seconds

@dataclass
class PerformanceThresholds:
    """Performance thresholds for Mobile Web Vitals."""
    load_time_good: float = 2.0  # seconds
    load_time_poor: float = 4.0  # seconds
    fcp_good: float = 1.8  # seconds
    fcp_poor: float = 3.0  # seconds
    lcp_good: float = 2.5  # seconds
    lcp_poor: float = 4.0  # seconds
    fid_good: float = 100.0  # milliseconds
    fid_poor: float = 300.0  # milliseconds
    cls_good: float = 0.1  # score
    cls_poor: float = 0.25  # score
    jank_good: float = 5.0  # percentage
    jank_poor: float = 15.0  # percentage
    responsiveness_good: float = 80.0  # score
    responsiveness_poor: float = 60.0  # score

class MobileWebVitalsMonitor:
    """Monitor and track Mobile Web Vitals metrics."""
    
    def __init__(self, thresholds: Optional[PerformanceThresholds] = None):
        self.thresholds = thresholds or PerformanceThresholds()
        self.metrics_history: deque = deque(maxlen=1000)
        self.observers: List[Callable[[WebVitalMetrics], None]] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self) -> bool:
        """Start monitoring Mobile Web Vitals."""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return False
            
        try:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Mobile Web Vitals monitoring started")
            return True
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            self.is_monitoring = False
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop monitoring Mobile Web Vitals."""
        if not self.is_monitoring:
            logger.warning("Monitoring not started")
            return False
            
        try:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5.0)
            logger.info("Mobile Web Vitals monitoring stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def add_observer(self, observer: Callable[[WebVitalMetrics], None]) -> None:
        """Add observer for metrics updates."""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: Callable[[WebVitalMetrics], None]) -> None:
        """Remove observer for metrics updates."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def record_metrics(self, metrics: WebVitalMetrics) -> None:
        """Record new metrics."""
        if not self._validate_metrics(metrics):
            logger.warning("Invalid metrics received, skipping")
            return
            
        self.metrics_history.append(metrics)
        self._notify_observers(metrics)
        self._check_thresholds(metrics)
    
    def get_current_metrics(self) -> Optional[WebVitalMetrics]:
        """Get the most recent metrics."""
        if not self.metrics_history:
            return None
        return self.metrics_history[-1]
    
    def get_metrics_summary(self, window_minutes: int = 5) -> Dict[str, Any]:
        """Get metrics summary for the specified time window."""
        if not self.metrics_history:
            return {}
            
        cutoff_time = datetime.now().timestamp() - (window_minutes * 60)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp.timestamp() > cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        return {
            "load_time": {
                "avg": statistics.mean(m.load_time for m in recent_metrics),
                "min": min(m.load_time for m in recent_metrics),
                "max": max(m.load_time for m in recent_metrics),
                "p95": self._percentile([m.load_time for m in recent_metrics], 95)
            },
            "jank_score": {
                "avg": statistics.mean(m.jank_score for m in recent_metrics),
                "min": min(m.jank_score for m in recent_metrics),
                "max": max(m.jank_score for m in recent_metrics),
                "p95": self._percentile([m.jank_score for m in recent_metrics], 95)
            },
            "responsiveness_score": {
                "avg": statistics.mean(m.responsiveness_score for m in recent_metrics),
                "min": min(m.responsiveness_score for m in recent_metrics),
                "max": max(m.responsiveness_score for m in recent_metrics),
                "p95": self._percentile([m.responsiveness_score for m in recent_metrics], 95)
            },
            "sample_count": len(recent_metrics)
        }
    
    def _validate_metrics(self, metrics: WebVitalMetrics) -> bool:
        """Validate metrics data."""
        if not isinstance(metrics, WebVitalMetrics):
            return False
        if metrics.load_time < 0 or metrics.load_time > 60:
            return False
        if metrics.jank_score < 0 or metrics.jank_score > 100:
            return False
        if metrics.responsiveness_score < 0 or metrics.responsiveness_score > 100:
            return False
        return True
    
    def _notify_observers(self, metrics: WebVitalMetrics) -> None:
        """Notify all observers of new metrics."""
        for observer in self.observers:
            try:
                observer(metrics)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")
    
    def _check_thresholds(self, metrics: WebVitalMetrics) -> None:
        """Check metrics against performance thresholds."""
        alerts = []
        
        if metrics.load_time > self.thresholds.load_time_poor:
            alerts.append(f"Load time poor: {metrics.load_time:.2f}s")
        elif metrics.load_time > self.thresholds.load_time_good:
            alerts.append(f"Load time needs improvement: {metrics.load_time:.2f}s")
        
        if metrics.jank_score > self.thresholds.jank_poor:
            alerts.append(f"Jank poor: {metrics.jank_score:.1f}%")
        elif metrics.jank_score > self.thresholds.jank_good:
            alerts.append(f"Jank needs improvement: {metrics.jank_score:.1f}%")
        
        if metrics.responsiveness_score < self.thresholds.responsiveness_poor:
            alerts.append(f"Responsiveness poor: {metrics.responsiveness_score:.1f}")
        elif metrics.responsiveness_score < self.thresholds.responsiveness_good:
            alerts.append(f"Responsiveness needs improvement: {metrics.responsiveness_score:.1f}")
        
        if alerts:
            logger.warning(f"Performance alerts: {', '.join(alerts)}")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                metrics = self._collect_current_metrics()
                if metrics:
                    self.record_metrics(metrics)
                time.sleep(1.0)  # Collect metrics every second
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _collect_current_metrics(self) -> Optional[WebVitalMetrics]:
        """Collect current performance metrics."""
        try:
            # Simulate metrics collection (replace with actual implementation)
            import random
            
            return WebVitalMetrics(
                timestamp=datetime.now(),
                load_time=random.uniform(1.0, 5.0),
                first_contentful_paint=random.uniform(0.8, 3.0),
                largest_contentful_paint=random.uniform(1.5, 4.5),
                first_input_delay=random.uniform(50, 300),
                cumulative_layout_shift=random.uniform(0.05, 0.3),
                jank_score=random.uniform(2.0, 20.0),
                responsiveness_score=random.uniform(50.0, 95.0),
                total_blocking_time=random.uniform(100, 500),
                time_to_interactive=random.uniform(2.0, 8.0)
            )
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return None
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

class LoadTimeOptimizer:
    """Optimize page load times."""
    
    def __init__(self):
        self.optimization_strategies = {
            "resource_minification": self._minify_resources,
            "image_optimization": self._optimize_images,
            "caching_strategy": self._implement_caching,
            "code_splitting": self._implement_code_splitting,
            "lazy_loading": self._implement_lazy_loading
        }
    
    async def optimize_load_time(self, current_load_time: float) -> Dict[str, Any]:
        """Optimize load time using various strategies."""
        optimizations = {}
        
        for strategy_name, strategy_func in self.optimization_strategies.items():
            try:
                result = await strategy_func(current_load_time)
                optimizations[strategy_name] = result
            except Exception as e:
                logger.error(f"Optimization {strategy_name} failed: {e}")
                optimizations[strategy_name] = {"error": str(e)}
        
        return optimizations
    
    async def _minify_resources(self, current_load_time: float) -> Dict[str, Any]:
        """Minify CSS, JavaScript, and HTML resources."""
        try:
            # Simulate minification process
            await asyncio.sleep(0.1)
            
            estimated_savings = min(current_load_time * 0.15, 1.0)  # Up to 15% improvement
            
            return {
                "estimated_savings": estimated_savings,
                "recommendations": [
                    "Minify CSS files",
                    "Minify JavaScript files",
                    "Remove unnecessary whitespace",
                    "Use CSS and JS minifiers"
                ]
            }
        except Exception as e:
            logger.error(f"Resource minification failed: {e}")
            return {"error": str(e)}
    
    async def _optimize_images(self, current_load_time: float) -> Dict[str, Any]:
        """Optimize image loading and formats."""
        try:
            # Simulate image optimization
            await asyncio.sleep(0.1)
            
            estimated_savings = min(current_load_time * 0.25, 1.5)  # Up to 25% improvement
            
            return {
                "estimated_savings": estimated_savings,
                "recommendations": [
                    "Use WebP format for images",
                    "Implement responsive images",
                    "Use image compression",
                    "Implement lazy loading for images",
                    "Use appropriate image sizes"
                ]
            }
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return {"error": str(e)}
    
    async def _implement_caching(self, current_load_time: float) -> Dict[str, Any]:
        """Implement effective caching strategies."""
        try:
            # Simulate caching implementation
            await asyncio.sleep(0.1)
            
            estimated_savings = min(current_load_time * 0.20, 1.2)  # Up to 20% improvement
            
            return {
                "estimated_savings": estimated_savings,
                "recommendations": [
                    "Set appropriate cache headers",
                    "Use browser caching",
                    "Implement CDN caching",
                    "Use service worker caching",
                    "Cache API responses"
                ]
            }
        except Exception as e:
            logger.error(f"Caching implementation failed: {e}")
            return {"error": str(e)}
    
    async def _implement_code_splitting(self, current_load_time: float) -> Dict[str, Any]:
        """Implement code splitting for better load times."""
        try:
            # Simulate code splitting
            await asyncio.sleep(0.1)
            
            estimated_savings = min(current_load_time * 0.30, 2.0)  # Up to 30% improvement
            
            return {
                "estimated_savings": estimated_savings,
                "recommendations": [
                    "Split JavaScript bundles",
                    "Use dynamic imports",
                    "Implement route-based splitting",
                    "Lazy load components",
                    "Use tree shaking"
                ]
            }
        except Exception as e:
            logger.error(f"Code splitting failed: {e}")
            return {"error": str(e)}
    
    async def _implement_lazy_loading(self, current_load_time: float) -> Dict[str, Any]:
        """Implement lazy loading for resources."""
        try:
            # Simulate lazy loading implementation
            await asyncio.sleep(0.1)
            
            estimated_savings = min(current_load_time * 0.10, 0.8)  # Up to 10% improvement
            
            return {
                "estimated_savings": estimated_savings,
                "recommendations": [
                    "Lazy load images",
                    "Lazy load components",
                    "Implement intersection observer",
                    "Use skeleton screens",
                    "Progressive loading"
                ]
            }
        except Exception as e:
            logger.error(f"Lazy loading failed: {e}")
            return {"error": str(e)}

class JankDetector:
    """Detect and analyze jank (frame drops and stuttering)."""
    
    def __init__(self):
        self.frame_times: deque = deque(maxlen=300)  # Store 5 seconds at 60fps
        self.jank_threshold = 16.67  # 60fps = 16.67ms per frame
        self.is_monitoring = False
    
    def start_jank_monitoring(self) -> bool:
        """Start monitoring for jank."""
        if self.is_monitoring:
            return False
        
        try:
            self.is_monitoring = True
            self._monitor_frames()
            return True
        except Exception as e:
            logger.error(f"Failed to start jank monitoring: {e}")
            return False
    
    def stop_jank_monitoring(self) -> bool:
        """Stop monitoring for jank."""
        self.is_monitoring = False
        return True
    
    def record_frame_time(self, frame_time_ms: float) -> None:
        """Record frame render time."""
        if not self._validate_frame_time(frame_time_ms):
            return
            
        self.frame_times.append(frame_time_ms)
        self._analyze_jank()
    
    def get_jank_score(self) -> float:
        """Calculate current jank score."""
        if len(self.frame_times) < 10:
            return 0.0
        
        janky_frames = sum(1 for ft in self.frame_times if ft > self.jank_threshold)
        return (janky_frames / len(self.frame_times)) * 100
    
    def get_jank_analysis(self) -> Dict[str, Any]:
        """Get detailed jank analysis."""
        if not self.frame_times:
            return {"jank_score": 0.0, "frame_count": 0}
        
        jank_score = self.get_jank_score()
        avg_frame_time = statistics.mean(self.frame_times)
        max_frame_time = max(self.frame_times)
        min_frame_time = min(self.frame_times)
        
        return {
            "jank_score": jank_score,
            "frame_count": len(self.frame_times),
            "avg_frame_time": avg_frame_time,
            "max_frame_time": max_frame_time,
            "min_frame_time": min_frame_time,
            "fps": 1000 / avg_frame_time if avg_frame_time > 0 else 0,
            "jank_severity": self._get_jank_severity(jank_score)
        }
    
    def _validate_frame_time(self, frame_time_ms: float) -> bool:
        """Validate frame time data."""
        return 0 < frame_time_ms < 1000  # Reasonable frame time range
    
    def _analyze_jank(self) -> None:
        """Analyze current jank patterns."""
        if len(self.frame_times) < 60:  # Need at least 1 second of data
            return
        
        jank_score = self.get_jank_score()
        if jank_score > 10:  # More than 10% jank
            logger.warning(f"High jank detected: {jank_score:.1f}%")
    
    def _get_jank_severity(self, jank_score: float) -> str:
        """Get jank severity level."""
        if jank_score < 5:
            return "low"
        elif jank_score < 15:
            return "medium"
        else:
            return "high"
    
    def _monitor_frames(self) -> None:
        """Monitor frame rendering (simulated)."""
        import random
        
        def frame_monitor():
            while self.is_monitoring:
                # Simulate frame time measurement
                frame_time = random.uniform(10, 25)  # 10-25ms frame times
                self.record_frame_time(frame_time)
                time.sleep(0.016)  # ~60fps monitoring
        
        threading.Thread(target=frame_monitor, daemon=True).start()

class ResponsivenessOptimizer:
    """Optimize application responsiveness."""
    
    def __init__(self):
        self.interaction_times: deque = deque(maxlen=100)
        self.responsiveness_threshold = 100  # 100ms for good responsiveness
    
    def record_interaction_time(self, interaction_time_ms: float) -> None:
        """Record user interaction response time."""
        if not self._validate_interaction_time(interaction_time_ms):
            return
            
        self.interaction_times.append(interaction_time_ms)
        self._analyze_responsiveness()
    
    def get_responsiveness_score(self) -> float:
        """Calculate responsiveness score (0-100)."""
        if not self.interaction_times:
            return 100.0
        
        # Calculate score based on interaction times
        avg_time = statistics.mean(self.interaction_times)
        
        if avg_time <= 50:
            return 100.0
        elif avg_time <= 100:
            return 90.0
        elif avg_time <= 200:
            return 75.0
        elif avg_time <= 300:
            return 50.0
        else:
            return max(0, 100 - (avg_time - 300) / 10)
    
    def get_responsiveness_analysis(self) -> Dict[str, Any]:
        """Get detailed responsiveness analysis."""
        if not self.interaction_times:
            return {"responsiveness_score": 100.0, "interaction_count": 0}
        
        responsiveness_score = self.get_responsiveness_score()
        avg_interaction_time = statistics.mean(self.interaction_times)
        max_interaction_time = max(self.interaction_times)
        min_interaction_time = min(self.interaction_times)
        
        return {
            "responsiveness_score": responsiveness_score,
            "interaction_count": len(self.interaction_times),
            "avg_interaction_time": avg_interaction_time,
            "max_interaction_time": max_interaction_time,
            "min_interaction_time": min_interaction_time,
            "responsiveness_level": self._get_responsiveness_level(responsiveness_score)
        }
    
    async def optimize_responsiveness(self) -> Dict[str, Any]:
        """Optimize application responsiveness."""
        optimizations = {}
        
        # Analyze current responsiveness
        analysis = self.get_responsiveness_analysis()
        current_score = analysis["responsiveness_score"]
        
        if current_score < 80:
            optimizations["main_thread_optimization"] = await self._optimize_main_thread()
            optimizations["event_handling"] = await self._optimize_event_handling()
            optimizations["memory_management"] = await self._optimize_memory_management()
        
        return optimizations
    
    async def _optimize_main_thread(self) -> Dict[str, Any]:
        """Optimize main thread performance."""
        try:
            await asyncio.sleep(0.1)
            
            return {
                "recommendations": [
                    "Move heavy computations to Web Workers",
                    "Use requestIdleCallback for non-critical tasks",
                    "Implement virtual scrolling for large lists",
                    "Optimize DOM operations",
                    "Use CSS transforms instead of layout changes"
                ],
                "estimated_improvement": 15.0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _optimize_event_handling(self) -> Dict[str, Any]:
        """Optimize event handling."""
        try:
            await asyncio.sleep(0.1)
            
            return {
                "recommendations": [
                    "Use event delegation",
                    "Implement debouncing for frequent events",
                    "Use passive event listeners",
                    "Optimize event handler functions",
                    "Remove unused event listeners"
                ],
                "estimated_improvement": 10.0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _optimize_memory_management(self) -> Dict[str, Any]:
        """Optimize memory management."""
        try:
            await asyncio.sleep(0.1)
            
            return {
                "recommendations": [
                    "Implement proper cleanup in components",
                    "Use object pooling for frequently created objects",
                    "Avoid memory leaks in event listeners",
                    "Optimize image memory usage",
                    "Use weak references where appropriate"
                ],
                "estimated_improvement": 8.0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _validate_interaction_time(self, interaction_time_ms: float) -> bool:
        """Validate interaction time data."""
        return 0 < interaction_time_ms < 5000  # Reasonable interaction time range
    
    def _analyze_responsiveness(self) -> None:
        """Analyze current responsiveness patterns."""
        if len(self.interaction_times) < 5:
            return
        
        responsiveness_score = self.get_responsiveness_score()
        if responsiveness_score < 70:
            logger.warning(f"Poor responsiveness detected: {responsiveness_score:.1f}")
    
    def _get_responsiveness_level(self, score: float) -> str:
        """Get responsiveness level."""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 60:
            return "needs_improvement"
        else:
            return "poor"

class MobileWebVitalsManager:
    """Main manager for Mobile Web Vitals optimization."""
    
    def __init__(self):
        self.monitor = MobileWebVitalsMonitor()
        self.load_optimizer = LoadTimeOptimizer()
        self.jank_detector = JankDetector()
        self.responsiveness_optimizer = ResponsivenessOptimizer()
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the Mobile Web Vitals system."""
        try:
            # Start monitoring
            if not self.monitor.start_monitoring():
                return False
            
            # Start jank detection
            if not self.jank_detector.start_jank_monitoring():
                return False
            
            # Add observers
            self.monitor.add_observer(self._on_metrics_update)
            
            self.is_initialized = True
            logger.info("Mobile Web Vitals system initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Mobile Web Vitals system: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the Mobile Web Vitals system."""
        try:
            self.monitor.stop_monitoring()
            self.jank_detector.stop_jank_monitoring()
            self.is_initialized = False
            logger.info("Mobile Web Vitals system shutdown")
            return True
        except Exception as e:
            logger.error(f"Failed to shutdown Mobile Web Vitals system: {e}")
            return False
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        if not self.is_initialized:
            return {"error": "System not initialized"}
        
        try:
            current_metrics = self.monitor.get_current_metrics()
            metrics_summary = self.monitor.get_metrics_summary()
            jank_analysis = self.jank_detector.get_jank_analysis()
            responsiveness_analysis = self.responsiveness_optimizer.get_responsiveness_analysis()
            
            return {
                "current_metrics": current_metrics.__dict__ if current_metrics else None,
                "metrics_summary": metrics_summary,
                "jank_analysis": jank_analysis,
                "responsiveness_analysis": responsiveness_analysis,
                "overall_score": self._calculate_overall_score(
                    current_metrics, jank_analysis, responsiveness_analysis
                )
            }
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {"error": str(e)}
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Run comprehensive performance optimization."""
        if not self.is_initialized:
            return {"error": "System not initialized"}
        
        try:
            current_metrics = self.monitor.get_current_metrics()
            if not current_metrics:
                return {"error": "No metrics available"}
            
            optimizations = {}
            
            # Optimize load time
            load_optimizations = await self.load_optimizer.optimize_load_time(
                current_metrics.load_time
            )
            optimizations["load_time"] = load_optimizations
            
            # Optimize responsiveness
            responsiveness_optimizations = await self.responsiveness_optimizer.optimize_responsiveness()
            optimizations["responsiveness"] = responsiveness_optimizations
            
            return optimizations
        except Exception as e:
            logger.error(f"Failed to optimize performance: {e}")
            return {"error": str(e)}
    
    def _on_metrics_update(self, metrics: WebVitalMetrics) -> None:
        """Handle metrics updates."""
        try:
            # Update jank detector with frame time data
            frame_time = 1000 / 60  # Simulate 60fps
            self.jank_detector.record_frame_time(frame_time)
            
            # Update responsiveness optimizer
            interaction_time = metrics.first_input_delay
            self.responsiveness_optimizer.record_interaction_time(interaction_time)
            
        except Exception as e:
            logger.error(f"Error handling metrics update: {e}")
    
    def _calculate_overall_score(self, metrics: WebVitalMetrics, 
                                jank_analysis: Dict[str, Any], 
                                responsiveness_analysis: Dict[str, Any]) -> float:
        """Calculate overall performance score."""
        if not metrics:
            return 0.0
        
        # Weighted average of different metrics
        load_score = max(0, 100 - (metrics.load_time - 2.0) * 20)  # 2s = 100, 7s = 0
        jank_score = max(0, 100 - jank_analysis.get("jank_score", 0))
        responsiveness_score = responsiveness_analysis.get("responsiveness_score", 100)
        
        # Weighted average (load: 40%, jank: 30%, responsiveness: 30%)
        overall_score = (
            load_score * 0.4 +
            jank_score * 0.3 +
            responsiveness_score * 0.3
        )
        
        return max(0, min(100, overall_score))

# Context manager for Mobile Web Vitals monitoring
@asynccontextmanager
async def mobile_web_vitals_context():
    """Context manager for Mobile Web Vitals monitoring."""
    manager = MobileWebVitalsManager()
    try:
        await manager.initialize()
        yield manager
    finally:
        await manager.shutdown()

# Example usage
async def main():
    """Example usage of Mobile Web Vitals system."""
    
    async with mobile_web_vitals_context() as manager:
        # Get performance report
        report = await manager.get_performance_report()
        print("Performance Report:", json.dumps(report, indent=2, default=str))
        
        # Run optimizations
        optimizations = await manager.optimize_performance()
        print("Optimizations:", json.dumps(optimizations, indent=2, default=str))
        
        # Wait for some metrics to be collected
        await asyncio.sleep(5)
        
        # Get updated report
        updated_report = await manager.get_performance_report()
        print("Updated Report:", json.dumps(updated_report, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main()) 