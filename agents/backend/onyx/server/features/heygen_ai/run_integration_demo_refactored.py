#!/usr/bin/env python3
"""
Refactored Integration Demo for Advanced Distributed AI
Improved architecture with better separation of concerns and cleaner code structure
"""

import logging
import time
import json
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import numpy as np

# Import the systems
from core.enhanced_performance_monitoring_system import (
    EnhancedPerformanceMonitoringSystem,
    PerformanceConfig,
    AlertConfig,
    AnomalyDetectionConfig,
    create_enhanced_performance_monitoring_system
)

from core.optimization_engine import (
    OptimizationEngine,
    OptimizationConfig,
    QuantumConfig,
    NeuromorphicConfig,
    create_optimization_engine
)

# ===== ENHANCED CONFIGURATION =====

@dataclass
class IntegrationDemoConfig:
    """Configuration for the integration demo."""
    demo_duration: int = 60  # seconds
    monitoring_interval: float = 3.0  # seconds
    optimization_trigger_threshold: float = 0.6  # Performance threshold
    optimization_cooldown: int = 30  # seconds between optimizations
    enable_auto_optimization: bool = True
    enable_performance_tracking: bool = True
    export_results: bool = True
    results_file: str = "integration_demo_results_refactored.json"
    log_level: str = "INFO"

@dataclass
class PerformanceMetrics:
    """Structured performance metrics."""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    quantum_advantage: float
    learning_efficiency: float
    overall_score: float

@dataclass
class OptimizationResult:
    """Structured optimization result."""
    timestamp: float
    trigger_metrics: PerformanceMetrics
    problem: Dict[str, Any]
    result: Dict[str, Any]
    success: bool
    score: float

# ===== ABSTRACT BASE CLASSES =====

class BaseComponent(ABC):
    """Abstract base class for system components."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the component."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get component status."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up component resources."""
        pass

class BaseMonitor(BaseComponent):
    """Abstract base class for monitoring components."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
    
    def add_metric(self, metric: PerformanceMetrics) -> None:
        """Add a performance metric to history."""
        self.metrics_history.append(metric)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def get_latest_metrics(self, count: int = 10) -> List[PerformanceMetrics]:
        """Get the latest performance metrics."""
        return self.metrics_history[-count:] if self.metrics_history else []
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        scores = [m.overall_score for m in self.metrics_history]
        cpu_usage = [m.cpu_usage for m in self.metrics_history]
        memory_usage = [m.memory_usage for m in self.metrics_history]
        quantum_advantage = [m.quantum_advantage for m in self.metrics_history]
        learning_efficiency = [m.learning_efficiency for m in self.metrics_history]
        
        return {
            "total_measurements": len(self.metrics_history),
            "overall_score": {
                "average": np.mean(scores),
                "best": max(scores),
                "worst": min(scores),
                "current": scores[-1] if scores else 0.0,
                "trend": self._calculate_trend(scores)
            },
            "system_performance": {
                "cpu_usage": {
                    "average": np.mean(cpu_usage),
                    "current": cpu_usage[-1] if cpu_usage else 0.0
                },
                "memory_usage": {
                    "average": np.mean(memory_usage),
                    "current": memory_usage[-1] if memory_usage else 0.0
                }
            },
            "ai_performance": {
                "quantum_advantage": {
                    "average": np.mean(quantum_advantage),
                    "current": quantum_advantage[-1] if quantum_advantage else 1.0
                },
                "learning_efficiency": {
                    "average": np.mean(learning_efficiency),
                    "current": learning_efficiency[-1] if learning_efficiency else 0.0
                }
            }
        }
    
    def _calculate_trend(self, values: List[float], window: int = 5) -> str:
        """Calculate trend of values."""
        if len(values) < window:
            return "insufficient_data"
        
        recent_values = values[-window:]
        if len(recent_values) < 2:
            return "insufficient_data"
        
        trend = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
        
        if trend > 0.01:
            return "improving"
        elif trend < -0.01:
            return "degrading"
        else:
            return "stable"

class BaseOptimizer(BaseComponent):
    """Abstract base class for optimization components."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.optimization_history: List[OptimizationResult] = []
        self.max_history_size = 1000
    
    def add_optimization_result(self, result: OptimizationResult) -> None:
        """Add an optimization result to history."""
        self.optimization_history.append(result)
        if len(self.optimization_history) > self.max_history_size:
            self.optimization_history = self.optimization_history[-self.max_history_size:]
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization results."""
        if not self.optimization_history:
            return {"total_optimizations": 0}
        
        successful = [opt for opt in self.optimization_history if opt.success]
        scores = [opt.score for opt in successful] if successful else []
        
        return {
            "total_optimizations": len(self.optimization_history),
            "successful_optimizations": len(successful),
            "success_rate": len(successful) / len(self.optimization_history),
            "average_score": np.mean(scores) if scores else 0.0,
            "best_score": max(scores) if scores else 0.0,
            "recent_performance": self._get_recent_performance()
        }
    
    def _get_recent_performance(self, count: int = 5) -> Dict[str, Any]:
        """Get recent optimization performance."""
        recent = self.optimization_history[-count:] if self.optimization_history else []
        if not recent:
            return {"recent_count": 0}
        
        recent_successful = [opt for opt in recent if opt.success]
        recent_scores = [opt.score for opt in recent_successful] if recent_successful else []
        
        return {
            "recent_count": len(recent),
            "recent_success_rate": len(recent_successful) / len(recent),
            "recent_average_score": np.mean(recent_scores) if recent_scores else 0.0
        }

# ===== CONCRETE COMPONENT IMPLEMENTATIONS =====

class PerformanceMonitor(BaseMonitor):
    """Performance monitoring component."""
    
    def __init__(self, config: IntegrationDemoConfig):
        super().__init__("PerformanceMonitor")
        self.config = config
        self.monitor_system = None
    
    def initialize(self) -> bool:
        """Initialize the performance monitor."""
        try:
            # Create performance monitoring system
            perf_config = PerformanceConfig(
                enabled=True,
                sampling_interval=1.0,
                retention_period=3600,
                max_metrics=1000,
                enable_alerts=True,
                enable_anomaly_detection=True,
                enable_auto_optimization=True
            )
            
            alert_config = AlertConfig(
                enabled=True,
                alert_threshold=0.8,
                alert_cooldown=30,
                enable_email_alerts=False,
                enable_webhook_alerts=False
            )
            
            anomaly_config = AnomalyDetectionConfig(
                enabled=True,
                detection_method="isolation_forest",
                sensitivity=0.7,
                min_samples=5
            )
            
            self.monitor_system = create_enhanced_performance_monitoring_system(
                perf_config, alert_config, anomaly_config
            )
            
            self.initialized = True
            self.logger.info("Performance monitor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance monitor: {e}")
            return False
    
    def get_current_performance(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        try:
            # Simulate performance data (in real implementation, get from monitor_system)
            cpu_usage = random.uniform(0.3, 0.9)
            memory_usage = random.uniform(0.4, 0.8)
            quantum_advantage = random.uniform(1.0, 2.5)
            learning_efficiency = random.uniform(0.4, 0.9)
            
            # Calculate overall score
            overall_score = (
                (1.0 - cpu_usage) * 0.4 +
                (1.0 - memory_usage) * 0.3 +
                min(1.0, quantum_advantage / 2.0) * 0.2 +
                learning_efficiency * 0.1
            )
            
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                quantum_advantage=quantum_advantage,
                learning_efficiency=learning_efficiency,
                overall_score=overall_score
            )
            
            # Add to history
            self.add_metric(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get current performance: {e}")
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_usage=0.5,
                memory_usage=0.5,
                quantum_advantage=1.0,
                learning_efficiency=0.5,
                overall_score=0.5
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitor status."""
        return {
            "initialized": self.initialized,
            "metrics_collected": len(self.metrics_history),
            "monitoring_active": self.initialized
        }
    
    def cleanup(self) -> None:
        """Clean up monitor resources."""
        try:
            if self.monitor_system and hasattr(self.monitor_system, 'stop_monitoring'):
                self.monitor_system.stop_monitoring()
            self.logger.info("Performance monitor cleanup completed")
        except Exception as e:
            self.logger.error(f"Performance monitor cleanup failed: {e}")

class OptimizationEngine(BaseOptimizer):
    """Optimization engine component."""
    
    def __init__(self, config: IntegrationDemoConfig):
        super().__init__("OptimizationEngine")
        self.config = config
        self.engine = None
    
    def initialize(self) -> bool:
        """Initialize the optimization engine."""
        try:
            # Create optimization engine
            opt_config = OptimizationConfig(
                enabled=True,
                max_iterations=500,
                convergence_threshold=1e-4,
                timeout_seconds=120,
                enable_parallel=True,
                enable_adaptive=True
            )
            
            quantum_config = QuantumConfig(
                enabled=True,
                qubits=15,
                layers=2,
                shots=500
            )
            
            neuromorphic_config = NeuromorphicConfig(
                enabled=True,
                neurons=500,
                learning_rate=0.01
            )
            
            self.engine = create_optimization_engine(opt_config, quantum_config, neuromorphic_config)
            
            self.initialized = True
            self.logger.info("Optimization engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize optimization engine: {e}")
            return False
    
    def optimize(self, trigger_metrics: PerformanceMetrics) -> OptimizationResult:
        """Run optimization based on performance metrics."""
        try:
            # Create optimization problem
            problem = self._create_optimization_problem(trigger_metrics)
            
            # Execute optimization
            result = self.engine.optimize(problem, "hybrid")
            
            # Create optimization result
            optimization_result = OptimizationResult(
                timestamp=time.time(),
                trigger_metrics=trigger_metrics,
                problem=problem,
                result=result,
                success="error" not in result,
                score=result.get("fused_score", 0.0) if "error" not in result else 0.0
            )
            
            # Add to history
            self.add_optimization_result(optimization_result)
            
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Failed to run optimization: {e}")
            return OptimizationResult(
                timestamp=time.time(),
                trigger_metrics=trigger_metrics,
                problem={},
                result={"error": str(e)},
                success=False,
                score=0.0
            )
    
    def _create_optimization_problem(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Create optimization problem based on performance metrics."""
        # Determine problem characteristics
        if metrics.overall_score < 0.5:
            problem_type = "critical_performance_optimization"
            complexity = "very_high"
        elif metrics.overall_score < 0.7:
            problem_type = "performance_optimization"
            complexity = "high"
        else:
            problem_type = "maintenance_optimization"
            complexity = "medium"
        
        return {
            "id": f"auto_opt_{int(time.time())}",
            "type": problem_type,
            "complexity": complexity,
            "target_metrics": {
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "quantum_advantage": metrics.quantum_advantage,
                "learning_efficiency": metrics.learning_efficiency
            },
            "optimization_target": "improve_overall_performance",
            "constraints": {
                "max_iterations": 500,
                "convergence_threshold": 1e-4,
                "timeout_seconds": 120
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status."""
        return {
            "initialized": self.initialized,
            "optimizations_performed": len(self.optimization_history),
            "engine_active": self.initialized
        }
    
    def cleanup(self) -> None:
        """Clean up engine resources."""
        try:
            self.logger.info("Optimization engine cleanup completed")
        except Exception as e:
            self.logger.error(f"Optimization engine cleanup failed: {e}")

# ===== INTEGRATION COORDINATOR =====

class IntegrationCoordinator:
    """Coordinates the integration between monitoring and optimization."""
    
    def __init__(self, config: IntegrationDemoConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.IntegrationCoordinator")
        
        # Initialize components
        self.performance_monitor = PerformanceMonitor(config)
        self.optimization_engine = OptimizationEngine(config)
        
        # Integration state
        self.last_optimization_time = 0
        self.demo_start_time = 0
        self.demo_running = False
        
        self.logger.info("Integration coordinator initialized")
    
    def initialize(self) -> bool:
        """Initialize all components."""
        try:
            self.logger.info("Initializing integration components...")
            
            # Initialize performance monitor
            if not self.performance_monitor.initialize():
                self.logger.error("Failed to initialize performance monitor")
                return False
            
            # Initialize optimization engine
            if not self.optimization_engine.initialize():
                self.logger.error("Failed to initialize optimization engine")
                return False
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False
    
    def start_demo(self) -> None:
        """Start the integration demo."""
        if not self.performance_monitor.initialized or not self.optimization_engine.initialized:
            self.logger.error("Components not initialized")
            return
        
        self.logger.info(f"🚀 Starting Integration Demo ({self.config.demo_duration} seconds)...")
        self.demo_start_time = time.time()
        self.demo_running = True
        
        try:
            self._run_demo_loop()
        except KeyboardInterrupt:
            self.logger.info("Demo interrupted by user")
        except Exception as e:
            self.logger.error(f"Demo failed: {e}")
            raise
        finally:
            self.demo_running = False
            self.logger.info("Demo completed")
    
    def _run_demo_loop(self) -> None:
        """Main demo loop."""
        cycle = 0
        
        while time.time() - self.demo_start_time < self.config.demo_duration:
            cycle += 1
            self.logger.info(f"📊 Cycle {cycle}")
            
            # Get current performance
            metrics = self.performance_monitor.get_current_performance()
            
            # Check if optimization is needed
            if self._should_trigger_optimization(metrics):
                self._trigger_optimization(metrics)
            
            # Log current status
            self._log_status(metrics)
            
            # Wait for next cycle
            time.sleep(self.config.monitoring_interval)
    
    def _should_trigger_optimization(self, metrics: PerformanceMetrics) -> bool:
        """Check if optimization should be triggered."""
        if not self.config.enable_auto_optimization:
            return False
        
        # Check cooldown period
        if time.time() - self.last_optimization_time < self.config.optimization_cooldown:
            return False
        
        # Check performance threshold
        if metrics.overall_score < self.config.optimization_trigger_threshold:
            return True
        
        # Check for degradation trend
        recent_metrics = self.performance_monitor.get_latest_metrics(3)
        if len(recent_metrics) >= 3:
            scores = [m.overall_score for m in recent_metrics]
            if len(scores) >= 3:
                trend = (scores[-1] - scores[0]) / len(scores)
                if trend < -0.05:  # 5% degradation
                    return True
        
        return False
    
    def _trigger_optimization(self, metrics: PerformanceMetrics) -> None:
        """Trigger optimization based on performance metrics."""
        self.logger.info("🚀 Triggering optimization...")
        
        # Run optimization
        result = self.optimization_engine.optimize(metrics)
        
        # Update last optimization time
        self.last_optimization_time = time.time()
        
        # Log result
        if result.success:
            self.logger.info(f"✅ Optimization completed: Score {result.score:.3f}")
        else:
            self.logger.warning(f"⚠️ Optimization failed")
    
    def _log_status(self, metrics: PerformanceMetrics) -> None:
        """Log current system status."""
        status = (
            f"Score: {metrics.overall_score:.3f}, "
            f"CPU: {metrics.cpu_usage:.1%}, "
            f"Memory: {metrics.memory_usage:.1%}, "
            f"Quantum: {metrics.quantum_advantage:.2f}x"
        )
        
        if metrics.overall_score < 0.5:
            self.logger.warning(f"⚠️ {status}")
        elif metrics.overall_score < 0.7:
            self.logger.info(f"📈 {status}")
        else:
            self.logger.info(f"✅ {status}")
    
    def get_demo_summary(self) -> Dict[str, Any]:
        """Get comprehensive demo summary."""
        try:
            # Performance summary
            performance_summary = self.performance_monitor.get_metrics_summary()
            
            # Optimization summary
            optimization_summary = self.optimization_engine.get_optimization_summary()
            
            # Integration summary
            integration_summary = {
                "demo_duration": time.time() - self.demo_start_time if self.demo_start_time > 0 else 0,
                "total_cycles": len(self.performance_monitor.metrics_history),
                "optimizations_triggered": len(self.optimization_engine.optimization_history),
                "auto_optimization_enabled": self.config.enable_auto_optimization,
                "last_optimization": time.time() - self.last_optimization_time if self.last_optimization_time > 0 else None
            }
            
            return {
                "performance_summary": performance_summary,
                "optimization_summary": optimization_summary,
                "integration_summary": integration_summary,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get demo summary: {e}")
            return {"error": str(e)}
    
    def cleanup(self) -> None:
        """Clean up all components."""
        try:
            self.logger.info("Cleaning up integration components...")
            
            # Clean up components
            self.performance_monitor.cleanup()
            self.optimization_engine.cleanup()
            
            self.logger.info("Integration cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Integration cleanup failed: {e}")

# ===== RESULTS EXPORTER =====

class ResultsExporter:
    """Handles export of demo results."""
    
    def __init__(self, config: IntegrationDemoConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ResultsExporter")
    
    def export_results(self, coordinator: IntegrationCoordinator, 
                      filename: Optional[str] = None) -> bool:
        """Export demo results to file."""
        if filename is None:
            filename = self.config.results_file
        
        try:
            # Get demo summary
            summary = coordinator.get_demo_summary()
            
            # Prepare export data
            export_data = {
                "summary": summary,
                "performance_history": [
                    {
                        "timestamp": m.timestamp,
                        "cpu_usage": m.cpu_usage,
                        "memory_usage": m.memory_usage,
                        "quantum_advantage": m.quantum_advantage,
                        "learning_efficiency": m.learning_efficiency,
                        "overall_score": m.overall_score
                    }
                    for m in coordinator.performance_monitor.metrics_history
                ],
                "optimization_history": [
                    {
                        "timestamp": opt.timestamp,
                        "trigger_metrics": {
                            "overall_score": opt.trigger_metrics.overall_score,
                            "cpu_usage": opt.trigger_metrics.cpu_usage,
                            "memory_usage": opt.trigger_metrics.memory_usage
                        },
                        "problem": opt.problem,
                        "result": opt.result,
                        "success": opt.success,
                        "score": opt.score
                    }
                    for opt in coordinator.optimization_engine.optimization_history
                ],
                "configuration": {
                    "demo_duration": self.config.demo_duration,
                    "monitoring_interval": self.config.monitoring_interval,
                    "optimization_trigger_threshold": self.config.optimization_trigger_threshold,
                    "optimization_cooldown": self.config.optimization_cooldown,
                    "auto_optimization_enabled": self.config.enable_auto_optimization
                }
            }
            
            # Write to file
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Results exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            return False

# ===== MAIN DEMO EXECUTION =====

def main():
    """Main demo execution."""
    print("🚀 Refactored Integration System Demo")
    print("="*60)
    
    # Create configuration
    config = IntegrationDemoConfig()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create coordinator
    coordinator = IntegrationCoordinator(config)
    
    try:
        # Initialize components
        if not coordinator.initialize():
            print("❌ Failed to initialize components")
            return
        
        # Start demo
        coordinator.start_demo()
        
        # Get and print summary
        summary = coordinator.get_demo_summary()
        print_summary(summary)
        
        # Export results
        if config.export_results:
            exporter = ResultsExporter(config)
            exporter.export_results(coordinator)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        # Cleanup
        coordinator.cleanup()

def print_summary(summary: Dict[str, Any]):
    """Print demo summary."""
    print("\n" + "="*60)
    print("📊 INTEGRATED SYSTEM DEMO SUMMARY")
    print("="*60)
    
    if "error" not in summary:
        # Performance summary
        perf = summary.get("performance_summary", {})
        if "error" not in perf:
            overall = perf.get("overall_score", {})
            print(f"📈 Performance Summary:")
            print(f"   Total Measurements: {perf.get('total_measurements', 0)}")
            print(f"   Average Score: {overall.get('average', 0):.3f}")
            print(f"   Best Score: {overall.get('best', 0):.3f}")
            print(f"   Current Score: {overall.get('current', 0):.3f}")
            print(f"   Trend: {overall.get('trend', 'N/A')}")
        
        # Optimization summary
        opt = summary.get("optimization_summary", {})
        print(f"\n🔧 Optimization Summary:")
        print(f"   Total Optimizations: {opt.get('total_optimizations', 0)}")
        print(f"   Successful: {opt.get('successful_optimizations', 0)}")
        print(f"   Success Rate: {opt.get('success_rate', 0):.1%}")
        print(f"   Average Score: {opt.get('average_score', 0):.3f}")
        print(f"   Best Score: {opt.get('best_score', 0):.3f}")
        
        # Integration summary
        integration = summary.get("integration_summary", {})
        print(f"\n🔗 Integration Summary:")
        print(f"   Demo Duration: {integration.get('demo_duration', 0):.1f} seconds")
        print(f"   Total Cycles: {integration.get('total_cycles', 0)}")
        print(f"   Optimizations Triggered: {integration.get('optimizations_triggered', 0)}")
        print(f"   Auto-Optimization: {integration.get('auto_optimization_enabled', False)}")
        
    else:
        print(f"❌ Failed to get summary: {summary.get('error', 'Unknown error')}")
    
    print("="*60)

if __name__ == "__main__":
    main()
