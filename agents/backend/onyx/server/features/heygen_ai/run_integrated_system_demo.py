#!/usr/bin/env python3
"""
Integrated System Demo for Advanced Distributed AI
Demonstrates the integration between optimization engine and performance monitoring
"""

import logging
import time
import json
import random
from typing import Dict, Any, List, Optional
import numpy as np

# Import the integrated systems
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

# ===== INTEGRATION CONFIGURATION =====

class IntegrationConfig:
    """Configuration for the integrated system demo."""
    
    def __init__(self):
        self.demo_duration = 120  # seconds
        self.monitoring_interval = 2.0  # seconds
        self.optimization_trigger_threshold = 0.7  # Performance threshold to trigger optimization
        self.enable_auto_optimization = True
        self.enable_performance_tracking = True
        self.export_results = True
        self.results_file = "integrated_system_demo_results.json"

# ===== INTEGRATED SYSTEM CLASS =====

class IntegratedSystem:
    """Integrated system combining performance monitoring and optimization."""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.IntegratedSystem")
        
        # Initialize components
        self.performance_monitor = self._initialize_performance_monitor()
        self.optimization_engine = self._initialize_optimization_engine()
        
        # Integration state
        self.performance_history = []
        self.optimization_history = []
        self.auto_optimization_enabled = config.enable_auto_optimization
        self.last_optimization_time = 0
        self.optimization_cooldown = 30  # seconds between auto-optimizations
        
        # Performance tracking
        self.performance_metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "quantum_performance": [],
            "neuromorphic_performance": [],
            "overall_score": []
        }
        
        self.logger.info("Integrated System initialized successfully")
    
    def _initialize_performance_monitor(self) -> EnhancedPerformanceMonitoringSystem:
        """Initialize the performance monitoring system."""
        performance_config = PerformanceConfig(
            enabled=True,
            sampling_interval=1.0,
            retention_period=3600,
            max_metrics=10000,
            enable_alerts=True,
            enable_anomaly_detection=True,
            enable_auto_optimization=True
        )
        
        alert_config = AlertConfig(
            enabled=True,
            alert_threshold=0.8,
            alert_cooldown=60,
            enable_email_alerts=False,
            enable_webhook_alerts=False
        )
        
        anomaly_config = AnomalyDetectionConfig(
            enabled=True,
            detection_method="isolation_forest",
            sensitivity=0.7,
            min_samples=10
        )
        
        return create_enhanced_performance_monitoring_system(
            performance_config, alert_config, anomaly_config
        )
    
    def _initialize_optimization_engine(self) -> OptimizationEngine:
        """Initialize the optimization engine."""
        optimization_config = OptimizationConfig(
            enabled=True,
            max_iterations=1000,
            convergence_threshold=1e-6,
            timeout_seconds=300,
            enable_parallel=True,
            enable_adaptive=True
        )
        
        quantum_config = QuantumConfig(
            enabled=True,
            qubits=20,
            layers=3,
            shots=1000
        )
        
        neuromorphic_config = NeuromorphicConfig(
            enabled=True,
            neurons=1000,
            learning_rate=0.01
        )
        
        return create_optimization_engine(optimization_config, quantum_config, neuromorphic_config)
    
    def start_monitoring(self):
        """Start the integrated monitoring and optimization system."""
        self.logger.info("🚀 Starting Integrated System Monitoring...")
        
        try:
            # Start performance monitoring
            self.performance_monitor.start_monitoring()
            
            # Start the main monitoring loop
            self._monitoring_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            raise
    
    def _monitoring_loop(self):
        """Main monitoring loop with integrated optimization."""
        start_time = time.time()
        
        while time.time() - start_time < self.config.demo_duration:
            try:
                # Get current performance metrics
                current_metrics = self._get_current_performance()
                
                # Store metrics
                self.performance_history.append({
                    "timestamp": time.time(),
                    "metrics": current_metrics
                })
                
                # Update performance tracking
                self._update_performance_tracking(current_metrics)
                
                # Check if optimization is needed
                if self._should_trigger_optimization(current_metrics):
                    self._trigger_optimization(current_metrics)
                
                # Log current status
                self._log_status(current_metrics)
                
                # Wait for next monitoring cycle
                time.sleep(self.config.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.config.monitoring_interval)
        
        self.logger.info("✅ Monitoring loop completed")
    
    def _get_current_performance(self) -> Dict[str, Any]:
        """Get current performance metrics from the monitoring system."""
        try:
            # Get system performance
            system_metrics = self.performance_monitor.get_system_performance()
            
            # Get quantum performance
            quantum_metrics = self.performance_monitor.get_quantum_performance()
            
            # Get neuromorphic performance
            neuromorphic_metrics = self.performance_monitor.get_neuromorphic_performance()
            
            # Calculate overall performance score
            overall_score = self._calculate_overall_score(system_metrics, quantum_metrics, neuromorphic_metrics)
            
            return {
                "system": system_metrics,
                "quantum": quantum_metrics,
                "neuromorphic": neuromorphic_metrics,
                "overall_score": overall_score,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return {
                "system": {},
                "quantum": {},
                "neuromorphic": {},
                "overall_score": 0.0,
                "timestamp": time.time()
            }
    
    def _calculate_overall_score(self, system_metrics: Dict[str, Any], 
                                quantum_metrics: Dict[str, Any], 
                                neuromorphic_metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score."""
        try:
            # System performance (40% weight)
            system_score = 0.0
            if system_metrics:
                cpu_usage = system_metrics.get("cpu_usage", 0.5)
                memory_usage = system_metrics.get("memory_usage", 0.5)
                system_score = (1.0 - cpu_usage) * 0.6 + (1.0 - memory_usage) * 0.4
            
            # Quantum performance (30% weight)
            quantum_score = 0.0
            if quantum_metrics:
                quantum_advantage = quantum_metrics.get("quantum_advantage", 1.0)
                quantum_score = min(1.0, quantum_advantage / 2.0)  # Normalize to 0-1
            
            # Neuromorphic performance (30% weight)
            neuromorphic_score = 0.0
            if neuromorphic_metrics:
                learning_efficiency = neuromorphic_metrics.get("learning_efficiency", 0.5)
                neuromorphic_score = learning_efficiency
            
            # Calculate weighted average
            overall_score = (system_score * 0.4 + quantum_score * 0.3 + neuromorphic_score * 0.3)
            
            return max(0.0, min(1.0, overall_score))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate overall score: {e}")
            return 0.5
    
    def _update_performance_tracking(self, metrics: Dict[str, Any]):
        """Update performance tracking metrics."""
        try:
            # Update CPU usage
            if "system" in metrics and "cpu_usage" in metrics["system"]:
                self.performance_metrics["cpu_usage"].append(metrics["system"]["cpu_usage"])
                if len(self.performance_metrics["cpu_usage"]) > 100:
                    self.performance_metrics["cpu_usage"] = self.performance_metrics["cpu_usage"][-100:]
            
            # Update memory usage
            if "system" in metrics and "memory_usage" in metrics["system"]:
                self.performance_metrics["memory_usage"].append(metrics["system"]["memory_usage"])
                if len(self.performance_metrics["memory_usage"]) > 100:
                    self.performance_metrics["memory_usage"] = self.performance_metrics["memory_usage"][-100:]
            
            # Update quantum performance
            if "quantum" in metrics and "quantum_advantage" in metrics["quantum"]:
                self.performance_metrics["quantum_performance"].append(metrics["quantum"]["quantum_advantage"])
                if len(self.performance_metrics["quantum_performance"]) > 100:
                    self.performance_metrics["quantum_performance"] = self.performance_metrics["quantum_performance"][-100:]
            
            # Update neuromorphic performance
            if "neuromorphic" in metrics and "learning_efficiency" in metrics["neuromorphic"]:
                self.performance_metrics["neuromorphic_performance"].append(metrics["neuromorphic"]["learning_efficiency"])
                if len(self.performance_metrics["neuromorphic_performance"]) > 100:
                    self.performance_metrics["neuromorphic_performance"] = self.performance_metrics["neuromorphic_performance"][-100:]
            
            # Update overall score
            if "overall_score" in metrics:
                self.performance_metrics["overall_score"].append(metrics["overall_score"])
                if len(self.performance_metrics["overall_score"]) > 100:
                    self.performance_metrics["overall_score"] = self.performance_metrics["overall_score"][-100:]
                    
        except Exception as e:
            self.logger.error(f"Failed to update performance tracking: {e}")
    
    def _should_trigger_optimization(self, metrics: Dict[str, Any]) -> bool:
        """Check if optimization should be triggered."""
        if not self.auto_optimization_enabled:
            return False
        
        # Check cooldown period
        if time.time() - self.last_optimization_time < self.optimization_cooldown:
            return False
        
        # Check performance threshold
        overall_score = metrics.get("overall_score", 1.0)
        if overall_score < self.config.optimization_trigger_threshold:
            return True
        
        # Check for performance degradation
        if len(self.performance_metrics["overall_score"]) >= 5:
            recent_scores = self.performance_metrics["overall_score"][-5:]
            if len(recent_scores) >= 5:
                trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
                if trend < -0.05:  # 5% degradation
                    return True
        
        return False
    
    def _trigger_optimization(self, current_metrics: Dict[str, Any]):
        """Trigger automated optimization based on performance metrics."""
        try:
            self.logger.info("🚀 Triggering automated optimization...")
            
            # Create optimization problem based on current performance
            optimization_problem = self._create_optimization_problem(current_metrics)
            
            # Execute optimization
            optimization_result = self.optimization_engine.optimize(optimization_problem, "hybrid")
            
            # Store optimization result
            self.optimization_history.append({
                "timestamp": time.time(),
                "trigger_metrics": current_metrics,
                "problem": optimization_problem,
                "result": optimization_result
            })
            
            # Update last optimization time
            self.last_optimization_time = time.time()
            
            # Log optimization result
            if "error" not in optimization_result:
                self.logger.info(f"✅ Optimization completed successfully: {optimization_result.get('fused_score', 0):.3f}")
            else:
                self.logger.warning(f"⚠️ Optimization completed with errors: {optimization_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Failed to trigger optimization: {e}")
    
    def _create_optimization_problem(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create optimization problem based on current performance metrics."""
        problem_type = "performance_optimization"
        
        # Determine problem characteristics based on metrics
        if metrics.get("overall_score", 1.0) < 0.5:
            problem_type = "critical_performance_optimization"
            complexity = "very_high"
        elif metrics.get("overall_score", 1.0) < 0.7:
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
                "cpu_usage": metrics.get("system", {}).get("cpu_usage", 0.5),
                "memory_usage": metrics.get("system", {}).get("memory_usage", 0.5),
                "quantum_advantage": metrics.get("quantum", {}).get("quantum_advantage", 1.0),
                "learning_efficiency": metrics.get("neuromorphic", {}).get("learning_efficiency", 0.5)
            },
            "optimization_target": "improve_overall_performance",
            "constraints": {
                "max_iterations": 500,
                "convergence_threshold": 1e-4,
                "timeout_seconds": 120
            }
        }
    
    def _log_status(self, metrics: Dict[str, Any]):
        """Log current system status."""
        try:
            overall_score = metrics.get("overall_score", 0.0)
            cpu_usage = metrics.get("system", {}).get("cpu_usage", 0.0)
            memory_usage = metrics.get("system", {}).get("memory_usage", 0.0)
            quantum_advantage = metrics.get("quantum", {}).get("quantum_advantage", 1.0)
            
            status_msg = (
                f"📊 Status - Overall: {overall_score:.3f}, "
                f"CPU: {cpu_usage:.1%}, "
                f"Memory: {memory_usage:.1%}, "
                f"Quantum: {quantum_advantage:.2f}x"
            )
            
            if overall_score < 0.5:
                self.logger.warning(f"⚠️ {status_msg}")
            elif overall_score < 0.7:
                self.logger.info(f"📈 {status_msg}")
            else:
                self.logger.info(f"✅ {status_msg}")
                
        except Exception as e:
            self.logger.error(f"Failed to log status: {e}")
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive system summary."""
        try:
            # Performance summary
            performance_summary = {
                "total_measurements": len(self.performance_history),
                "average_overall_score": np.mean(self.performance_metrics["overall_score"]) if self.performance_metrics["overall_score"] else 0.0,
                "best_overall_score": max(self.performance_metrics["overall_score"]) if self.performance_metrics["overall_score"] else 0.0,
                "worst_overall_score": min(self.performance_metrics["overall_score"]) if self.performance_metrics["overall_score"] else 0.0,
                "performance_trend": self._calculate_performance_trend()
            }
            
            # Optimization summary
            optimization_summary = {
                "total_optimizations": len(self.optimization_history),
                "successful_optimizations": len([opt for opt in self.optimization_history if "error" not in opt["result"]]),
                "average_optimization_score": 0.0,
                "optimization_effectiveness": 0.0
            }
            
            if optimization_summary["total_optimizations"] > 0:
                successful_optimizations = [opt for opt in self.optimization_history if "error" not in opt["result"]]
                if successful_optimizations:
                    scores = [opt["result"].get("fused_score", 0) for opt in successful_optimizations]
                    optimization_summary["average_optimization_score"] = np.mean(scores)
                    
                    # Calculate optimization effectiveness (performance improvement)
                    if len(self.performance_metrics["overall_score"]) >= 10:
                        before_optimization = np.mean(self.performance_metrics["overall_score"][:5])
                        after_optimization = np.mean(self.performance_metrics["overall_score"][-5:])
                        optimization_summary["optimization_effectiveness"] = (after_optimization - before_optimization) / before_optimization
            
            # System health
            system_health = {
                "monitoring_active": self.performance_monitor.is_monitoring_active(),
                "auto_optimization_enabled": self.auto_optimization_enabled,
                "last_optimization": time.time() - self.last_optimization_time if self.last_optimization_time > 0 else None,
                "performance_stability": self._calculate_performance_stability()
            }
            
            return {
                "performance_summary": performance_summary,
                "optimization_summary": optimization_summary,
                "system_health": system_health,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system summary: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_trend(self) -> str:
        """Calculate performance trend."""
        try:
            if len(self.performance_metrics["overall_score"]) < 10:
                return "insufficient_data"
            
            recent_scores = self.performance_metrics["overall_score"][-10:]
            trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
            
            if trend > 0.01:
                return "improving"
            elif trend < -0.01:
                return "degrading"
            else:
                return "stable"
                
        except Exception as e:
            self.logger.error(f"Failed to calculate performance trend: {e}")
            return "unknown"
    
    def _calculate_performance_stability(self) -> float:
        """Calculate performance stability (lower is more stable)."""
        try:
            if len(self.performance_metrics["overall_score"]) < 5:
                return 0.0
            
            scores = self.performance_metrics["overall_score"][-20:]
            return np.std(scores)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate performance stability: {e}")
            return 0.0
    
    def stop_monitoring(self):
        """Stop the integrated monitoring system."""
        try:
            self.logger.info("🛑 Stopping Integrated System Monitoring...")
            
            # Stop performance monitoring
            if hasattr(self.performance_monitor, 'stop_monitoring'):
                self.performance_monitor.stop_monitoring()
            
            self.logger.info("✅ Integrated System Monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
    
    def export_results(self, filename: Optional[str] = None) -> bool:
        """Export demo results to file."""
        if filename is None:
            filename = self.config.results_file
        
        try:
            export_data = {
                "system_summary": self.get_system_summary(),
                "performance_history": self.performance_history,
                "optimization_history": self.optimization_history,
                "performance_metrics": self.performance_metrics,
                "configuration": {
                    "demo_duration": self.config.demo_duration,
                    "monitoring_interval": self.config.monitoring_interval,
                    "optimization_trigger_threshold": self.config.optimization_trigger_threshold,
                    "auto_optimization_enabled": self.config.enable_auto_optimization
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            self.logger.info(f"Results exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            return False

# ===== MAIN DEMO EXECUTION =====

def main():
    """Main integrated system demo execution."""
    print("🚀 Starting Integrated System Demo...")
    print("="*60)
    
    # Create configuration
    config = IntegrationConfig()
    
    # Create integrated system
    integrated_system = IntegratedSystem(config)
    
    try:
        # Start monitoring
        integrated_system.start_monitoring()
        
        # Get final summary
        summary = integrated_system.get_system_summary()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 INTEGRATED SYSTEM DEMO SUMMARY")
        print("="*60)
        
        if "error" not in summary:
            # Performance summary
            perf_summary = summary.get("performance_summary", {})
            print(f"📈 Performance Summary:")
            print(f"   Total Measurements: {perf_summary.get('total_measurements', 0)}")
            print(f"   Average Score: {perf_summary.get('average_overall_score', 0):.3f}")
            print(f"   Best Score: {perf_summary.get('best_overall_score', 0):.3f}")
            print(f"   Performance Trend: {perf_summary.get('performance_trend', 'N/A')}")
            
            # Optimization summary
            opt_summary = summary.get("optimization_summary", {})
            print(f"\n🔧 Optimization Summary:")
            print(f"   Total Optimizations: {opt_summary.get('total_optimizations', 0)}")
            print(f"   Successful: {opt_summary.get('successful_optimizations', 0)}")
            print(f"   Average Score: {opt_summary.get('average_optimization_score', 0):.3f}")
            print(f"   Effectiveness: {opt_summary.get('optimization_effectiveness', 0):.1%}")
            
            # System health
            health = summary.get("system_health", {})
            print(f"\n💚 System Health:")
            print(f"   Monitoring Active: {health.get('monitoring_active', False)}")
            print(f"   Auto-Optimization: {health.get('auto_optimization_enabled', False)}")
            print(f"   Performance Stability: {health.get('performance_stability', 0):.3f}")
            
        else:
            print(f"❌ Failed to get summary: {summary.get('error', 'Unknown error')}")
        
        print("="*60)
        
        # Export results
        if config.export_results:
            integrated_system.export_results()
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        # Stop monitoring
        integrated_system.stop_monitoring()
        print("✅ Demo completed")

if __name__ == "__main__":
    main()
