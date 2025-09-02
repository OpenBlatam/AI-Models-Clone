#!/usr/bin/env python3
"""
Enhanced Performance Monitoring System Demo
Comprehensive demonstration of the enhanced performance monitoring capabilities
"""

import logging
import time
import json
import random
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

# Import the enhanced performance monitoring system
from core.enhanced_performance_monitoring_system import (
    EnhancedPerformanceMonitoringSystem,
    PerformanceConfig,
    AlertConfig,
    AnomalyDetectionConfig,
    MonitoringMode,
    AlertSeverity,
    create_enhanced_performance_monitoring_system,
    create_minimal_performance_config,
    create_maximum_performance_config
)

# ===== DEMO CONFIGURATION =====

class DemoConfiguration:
    """Configuration for the performance monitoring demo."""
    
    def __init__(self):
        self.demo_duration = 30  # seconds
        self.metrics_interval = 1.0  # seconds
        self.simulation_intensity = "medium"  # low, medium, high
        self.enable_alerts = True
        self.enable_quantum_simulation = True
        self.enable_neuromorphic_simulation = True
        self.export_results = True
        self.results_file = "enhanced_performance_monitoring_demo_results.json"

# ===== SIMULATION COMPONENTS =====

class SystemLoadSimulator:
    """Simulate varying system load for demonstration."""
    
    def __init__(self, intensity: str = "medium"):
        self.intensity = intensity
        self.base_load = self._get_base_load()
        self.fluctuation_factor = self._get_fluctuation_factor()
        self.anomaly_probability = self._get_anomaly_probability()
        
        # Load patterns
        self.load_patterns = {
            "normal": self._generate_normal_pattern(),
            "spike": self._generate_spike_pattern(),
            "gradual": self._generate_gradual_pattern(),
            "oscillating": self._generate_oscillating_pattern()
        }
    
    def _get_base_load(self) -> float:
        """Get base load based on intensity."""
        return {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8
        }.get(self.intensity, 0.5)
    
    def _get_fluctuation_factor(self) -> float:
        """Get fluctuation factor based on intensity."""
        return {
            "low": 0.1,
            "medium": 0.2,
            "high": 0.4
        }.get(self.intensity, 0.2)
    
    def _get_anomaly_probability(self) -> float:
        """Get anomaly probability based on intensity."""
        return {
            "low": 0.05,
            "medium": 0.1,
            "high": 0.2
        }.get(self.intensity, 0.1)
    
    def _generate_normal_pattern(self) -> List[float]:
        """Generate normal load pattern."""
        return [random.gauss(self.base_load, self.fluctuation_factor) for _ in range(100)]
    
    def _generate_spike_pattern(self) -> List[float]:
        """Generate spike load pattern."""
        pattern = [self.base_load] * 100
        # Add random spikes
        for _ in range(5):
            idx = random.randint(0, 99)
            pattern[idx] = min(1.0, self.base_load + random.uniform(0.3, 0.6))
        return pattern
    
    def _generate_gradual_pattern(self) -> List[float]:
        """Generate gradual load pattern."""
        pattern = []
        current_load = self.base_load
        for _ in range(100):
            change = random.uniform(-0.1, 0.1)
            current_load = max(0.0, min(1.0, current_load + change))
            pattern.append(current_load)
        return pattern
    
    def _generate_oscillating_pattern(self) -> List[float]:
        """Generate oscillating load pattern."""
        pattern = []
        for i in range(100):
            oscillation = 0.3 * np.sin(i * 0.2) + 0.1 * np.sin(i * 0.7)
            load = self.base_load + oscillation
            pattern.append(max(0.0, min(1.0, load)))
        return pattern
    
    def get_current_load(self, pattern_type: str = "normal", time_step: int = 0) -> float:
        """Get current load for a specific pattern and time step."""
        pattern = self.load_patterns.get(pattern_type, self.load_patterns["normal"])
        idx = time_step % len(pattern)
        load = pattern[idx]
        
        # Add random noise
        noise = random.gauss(0, self.fluctuation_factor * 0.1)
        load = max(0.0, min(1.0, load + noise))
        
        # Add anomalies
        if random.random() < self.anomaly_probability:
            anomaly = random.uniform(0.2, 0.5)
            load = min(1.0, load + anomaly)
        
        return load

class QuantumMetricsSimulator:
    """Simulate quantum computing metrics for demonstration."""
    
    def __init__(self):
        self.base_qubits = 20
        self.base_error_rate = 0.05
        self.optimization_level = 2
        self.circuit_depth = 15
        
        # Performance history
        self.execution_times = []
        self.success_rates = []
        self.quantum_advantages = []
    
    def simulate_quantum_metrics(self) -> Dict[str, Any]:
        """Simulate quantum performance metrics."""
        # Simulate varying performance
        error_rate = self.base_error_rate + random.uniform(-0.02, 0.02)
        error_rate = max(0.0, min(0.2, error_rate))
        
        # Simulate quantum advantage
        base_advantage = 1.5
        advantage_variation = random.uniform(-0.3, 0.3)
        quantum_advantage = max(1.0, base_advantage + advantage_variation)
        
        # Simulate circuit execution
        execution_time = random.uniform(0.1, 2.0)
        success_rate = max(0.7, 1.0 - error_rate * 2)
        
        # Store history
        self.execution_times.append(execution_time)
        self.success_rates.append(success_rate)
        self.quantum_advantages.append(quantum_advantage)
        
        # Keep only recent history
        if len(self.execution_times) > 50:
            self.execution_times.pop(0)
            self.success_rates.pop(0)
            self.quantum_advantages.pop(0)
        
        return {
            "active_qubits": self.base_qubits,
            "circuit_depth": self.circuit_depth,
            "error_rates": error_rate,
            "quantum_advantage": quantum_advantage,
            "optimization_level": self.optimization_level,
            "execution_time": execution_time,
            "success_rate": success_rate
        }

class NeuromorphicMetricsSimulator:
    """Simulate neuromorphic computing metrics for demonstration."""
    
    def __init__(self):
        self.base_neurons = 5000
        self.base_connectivity = 0.6
        self.base_plasticity = 0.3
        self.base_spiking_frequency = 100.0
        
        # Performance history
        self.response_times = []
        self.adaptation_rates = []
        self.emergent_scores = []
    
    def simulate_neuromorphic_metrics(self) -> Dict[str, Any]:
        """Simulate neuromorphic performance metrics."""
        # Simulate varying performance
        connectivity = self.base_connectivity + random.uniform(-0.1, 0.1)
        connectivity = max(0.3, min(1.0, connectivity))
        
        plasticity = self.base_plasticity + random.uniform(-0.05, 0.05)
        plasticity = max(0.1, min(0.8, plasticity))
        
        spiking_frequency = self.base_spiking_frequency + random.uniform(-20, 20)
        spiking_frequency = max(50, spiking_frequency)
        
        # Simulate learning efficiency
        learning_efficiency = (connectivity + plasticity) / 2.0 + random.uniform(-0.1, 0.1)
        learning_efficiency = max(0.0, min(1.0, learning_efficiency))
        
        # Simulate response time
        response_time = random.uniform(0.01, 0.5)
        adaptation_rate = random.uniform(0.1, 0.9)
        
        # Calculate emergent behavior score
        emergent_score = (connectivity + plasticity + learning_efficiency) / 3.0
        
        # Store history
        self.response_times.append(response_time)
        self.adaptation_rates.append(adaptation_rate)
        self.emergent_scores.append(emergent_score)
        
        # Keep only recent history
        if len(self.response_times) > 50:
            self.response_times.pop(0)
            self.adaptation_rates.pop(0)
            self.emergent_scores.pop(0)
        
        return {
            "active_neurons": self.base_neurons,
            "network_connectivity": connectivity,
            "plasticity_rate": plasticity,
            "spiking_frequency": spiking_frequency,
            "learning_efficiency": learning_efficiency,
            "response_time": response_time,
            "adaptation_rate": adaptation_rate,
            "emergent_behavior_score": emergent_score
        }

# ===== DEMO COMPONENTS =====

class DemoComponent:
    """Base class for demo components."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def run(self, **kwargs) -> Dict[str, Any]:
        """Run the demo component."""
        try:
            self.logger.info(f"Running {self.name} demo...")
            result = self._execute(**kwargs)
            self.logger.info(f"{self.name} demo completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"{self.name} demo failed: {e}")
            return {"error": str(e), "component": self.name}

class SystemMonitoringDemo(DemoComponent):
    """Demo system resource monitoring capabilities."""
    
    def __init__(self):
        super().__init__("System Monitoring")
    
    def _execute(self, monitoring_system: EnhancedPerformanceMonitoringSystem, 
                load_simulator: SystemLoadSimulator, duration: int) -> Dict[str, Any]:
        """Execute system monitoring demo."""
        results = {
            "system_metrics": [],
            "performance_analysis": {},
            "anomaly_detection": []
        }
        
        start_time = time.time()
        step = 0
        
        while time.time() - start_time < duration:
            # Simulate varying system load
            cpu_load = load_simulator.get_current_load("oscillating", step)
            memory_load = load_simulator.get_current_load("gradual", step)
            disk_load = load_simulator.get_current_load("normal", step)
            
            # Get current metrics
            current_metrics = monitoring_system.get_current_metrics()
            
            # Store metrics
            results["system_metrics"].append({
                "timestamp": time.time(),
                "step": step,
                "simulated_loads": {
                    "cpu": cpu_load,
                    "memory": memory_load,
                    "disk": disk_load
                },
                "actual_metrics": current_metrics
            })
            
            # Check for anomalies
            if cpu_load > 0.9 or memory_load > 0.9:
                results["anomaly_detection"].append({
                    "timestamp": time.time(),
                    "step": step,
                    "type": "high_load",
                    "cpu_load": cpu_load,
                    "memory_load": memory_load
                })
            
            step += 1
            time.sleep(1.0)
        
        # Analyze performance
        results["performance_analysis"] = self._analyze_performance(results["system_metrics"])
        
        return results
    
    def _analyze_performance(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze system performance metrics."""
        if not metrics:
            return {}
        
        analysis = {
            "total_samples": len(metrics),
            "monitoring_duration": metrics[-1]["timestamp"] - metrics[0]["timestamp"],
            "average_cpu_load": np.mean([m["simulated_loads"]["cpu"] for m in metrics]),
            "average_memory_load": np.mean([m["simulated_loads"]["memory"] for m in metrics]),
            "peak_cpu_load": max([m["simulated_loads"]["cpu"] for m in metrics]),
            "peak_memory_load": max([m["simulated_loads"]["memory"] for m in metrics])
        }
        
        return analysis

class QuantumMonitoringDemo(DemoComponent):
    """Demo quantum performance monitoring capabilities."""
    
    def __init__(self):
        super().__init__("Quantum Monitoring")
    
    def _execute(self, monitoring_system: EnhancedPerformanceMonitoringSystem, 
                quantum_simulator: QuantumMetricsSimulator, duration: int) -> Dict[str, Any]:
        """Execute quantum monitoring demo."""
        results = {
            "quantum_metrics": [],
            "performance_trends": {},
            "optimization_insights": []
        }
        
        start_time = time.time()
        step = 0
        
        while time.time() - start_time < duration:
            # Simulate quantum metrics
            quantum_metrics = quantum_simulator.simulate_quantum_metrics()
            
            # Store metrics
            results["quantum_metrics"].append({
                "timestamp": time.time(),
                "step": step,
                "metrics": quantum_metrics
            })
            
            # Check for optimization opportunities
            if quantum_metrics["error_rates"] > 0.1:
                results["optimization_insights"].append({
                    "timestamp": time.time(),
                    "step": step,
                    "type": "error_mitigation",
                    "current_error_rate": quantum_metrics["error_rates"],
                    "recommendation": "Enable error mitigation techniques"
                })
            
            if quantum_metrics["quantum_advantage"] < 1.2:
                results["optimization_insights"].append({
                    "timestamp": time.time(),
                    "step": step,
                    "type": "circuit_optimization",
                    "current_advantage": quantum_metrics["quantum_advantage"],
                    "recommendation": "Optimize circuit design for better quantum advantage"
                })
            
            step += 1
            time.sleep(1.0)
        
        # Analyze trends
        results["performance_trends"] = self._analyze_quantum_trends(results["quantum_metrics"])
        
        return results
    
    def _analyze_quantum_trends(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quantum performance trends."""
        if not metrics:
            return {}
        
        analysis = {
            "total_circuits": len(metrics),
            "average_error_rate": np.mean([m["metrics"]["error_rates"] for m in metrics]),
            "average_quantum_advantage": np.mean([m["metrics"]["quantum_advantage"] for m in metrics]),
            "average_execution_time": np.mean([m["metrics"]["execution_time"] for m in metrics]),
            "success_rate_trend": "improving" if len(metrics) > 1 and 
                                 metrics[-1]["metrics"]["success_rate"] > metrics[0]["metrics"]["success_rate"] else "stable"
        }
        
        return analysis

class NeuromorphicMonitoringDemo(DemoComponent):
    """Demo neuromorphic performance monitoring capabilities."""
    
    def __init__(self):
        super().__init__("Neuromorphic Monitoring")
    
    def _execute(self, monitoring_system: EnhancedPerformanceMonitoringSystem, 
                neuromorphic_simulator: NeuromorphicMetricsSimulator, duration: int) -> Dict[str, Any]:
        """Execute neuromorphic monitoring demo."""
        results = {
            "neuromorphic_metrics": [],
            "learning_analysis": {},
            "emergent_behavior_insights": []
        }
        
        start_time = time.time()
        step = 0
        
        while time.time() - start_time < duration:
            # Simulate neuromorphic metrics
            neuromorphic_metrics = neuromorphic_simulator.simulate_neuromorphic_metrics()
            
            # Store metrics
            results["neuromorphic_metrics"].append({
                "timestamp": time.time(),
                "step": step,
                "metrics": neuromorphic_metrics
            })
            
            # Check for learning insights
            if neuromorphic_metrics["learning_efficiency"] < 0.4:
                results["emergent_behavior_insights"].append({
                    "timestamp": time.time(),
                    "step": step,
                    "type": "learning_optimization",
                    "current_efficiency": neuromorphic_metrics["learning_efficiency"],
                    "recommendation": "Review network architecture and training parameters"
                })
            
            if neuromorphic_metrics["emergent_behavior_score"] > 0.7:
                results["emergent_behavior_insights"].append({
                    "timestamp": time.time(),
                    "step": step,
                    "type": "emergent_behavior",
                    "current_score": neuromorphic_metrics["emergent_behavior_score"],
                    "observation": "Strong emergent behavior patterns detected"
                })
            
            step += 1
            time.sleep(1.0)
        
        # Analyze learning patterns
        results["learning_analysis"] = self._analyze_learning_patterns(results["neuromorphic_metrics"])
        
        return results
    
    def _analyze_learning_patterns(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze neuromorphic learning patterns."""
        if not metrics:
            return {}
        
        analysis = {
            "total_learning_steps": len(metrics),
            "average_learning_efficiency": np.mean([m["metrics"]["learning_efficiency"] for m in metrics]),
            "average_plasticity_rate": np.mean([m["metrics"]["plasticity_rate"] for m in metrics]),
            "average_emergent_score": np.mean([m["metrics"]["emergent_behavior_score"] for m in metrics]),
            "learning_progress": "improving" if len(metrics) > 1 and 
                                metrics[-1]["metrics"]["learning_efficiency"] > metrics[0]["metrics"]["learning_efficiency"] else "stable"
        }
        
        return analysis

class AlertSystemDemo(DemoComponent):
    """Demo alert system capabilities."""
    
    def __init__(self):
        super().__init__("Alert System")
    
    def _execute(self, monitoring_system: EnhancedPerformanceMonitoringSystem, 
                load_simulator: SystemLoadSimulator, duration: int) -> Dict[str, Any]:
        """Execute alert system demo."""
        results = {
            "alerts_triggered": [],
            "alert_analysis": {},
            "threshold_testing": []
        }
        
        start_time = time.time()
        step = 0
        
        while time.time() - start_time < duration:
            # Simulate extreme loads to trigger alerts
            if step % 10 == 0:  # Every 10 seconds
                # Simulate high CPU load
                cpu_load = load_simulator.get_current_load("spike", step)
                if cpu_load > 0.8:
                    results["alerts_triggered"].append({
                        "timestamp": time.time(),
                        "step": step,
                        "type": "high_cpu_alert",
                        "cpu_load": cpu_load,
                        "threshold": 0.8
                    })
                
                # Simulate high memory load
                memory_load = load_simulator.get_current_load("spike", step)
                if memory_load > 0.85:
                    results["alerts_triggered"].append({
                        "timestamp": time.time(),
                        "step": step,
                        "type": "high_memory_alert",
                        "memory_load": memory_load,
                        "threshold": 0.85
                    })
            
            step += 1
            time.sleep(1.0)
        
        # Analyze alert patterns
        results["alert_analysis"] = self._analyze_alerts(results["alerts_triggered"])
        
        return results
    
    def _analyze_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze alert patterns."""
        if not alerts:
            return {}
        
        alert_types = {}
        for alert in alerts:
            alert_type = alert["type"]
            if alert_type not in alert_types:
                alert_types[alert_type] = 0
            alert_types[alert_type] += 1
        
        analysis = {
            "total_alerts": len(alerts),
            "alert_types": alert_types,
            "alert_frequency": len(alerts) / max(1, len(alerts)),
            "most_common_alert": max(alert_types.items(), key=lambda x: x[1])[0] if alert_types else "none"
        }
        
        return analysis

# ===== MAIN DEMO CLASS =====

class EnhancedPerformanceMonitoringDemo:
    """Main demo class for enhanced performance monitoring system."""
    
    def __init__(self, config: DemoConfiguration):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.EnhancedPerformanceMonitoringDemo")
        self.demo_results = {}
        self.running = False
        
        # Initialize components
        self.load_simulator = SystemLoadSimulator(config.simulation_intensity)
        self.quantum_simulator = QuantumMetricsSimulator()
        self.neuromorphic_simulator = NeuromorphicMetricsSimulator()
        
        # Initialize demo components
        self.demo_components = self._initialize_demo_components()
        
        # Initialize monitoring system
        self.monitoring_system = self._initialize_monitoring_system()
        
        # Setup logging
        self._setup_logging()
    
    def _initialize_demo_components(self) -> List[DemoComponent]:
        """Initialize demo components."""
        return [
            SystemMonitoringDemo(),
            QuantumMonitoringDemo(),
            NeuromorphicMonitoringDemo(),
            AlertSystemDemo()
        ]
    
    def _initialize_monitoring_system(self) -> EnhancedPerformanceMonitoringSystem:
        """Initialize the performance monitoring system."""
        # Create performance configuration
        if self.config.enable_alerts:
            performance_config = create_maximum_performance_config()
        else:
            performance_config = create_minimal_performance_config()
        
        # Create alert configuration
        alert_config = AlertConfig(
            enabled=self.config.enable_alerts,
            severity_threshold=AlertSeverity.WARNING,
            notification_channels=["console", "log"],
            alert_cooldown=5,  # Short cooldown for demo
            max_alerts_per_hour=1000
        )
        
        # Create monitoring system
        monitoring_system = create_enhanced_performance_monitoring_system(
            performance_config, alert_config
        )
        
        return monitoring_system
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def run_comprehensive_demo(self) -> Dict[str, Any]:
        """Run comprehensive performance monitoring demonstration."""
        self.logger.info("🚀 Starting Enhanced Performance Monitoring System Demo...")
        self.running = True
        
        try:
            # Start monitoring system
            self.monitoring_system.start_monitoring()
            
            # Run system monitoring demo
            self.demo_results["system_monitoring"] = self.demo_components[0].run(
                monitoring_system=self.monitoring_system,
                load_simulator=self.load_simulator,
                duration=self.config.demo_duration
            )
            
            # Run quantum monitoring demo
            if self.config.enable_quantum_simulation:
                self.demo_results["quantum_monitoring"] = self.demo_components[1].run(
                    monitoring_system=self.monitoring_system,
                    quantum_simulator=self.quantum_simulator,
                    duration=self.config.demo_duration
                )
            
            # Run neuromorphic monitoring demo
            if self.config.enable_neuromorphic_simulation:
                self.demo_results["neuromorphic_monitoring"] = self.demo_components[2].run(
                    monitoring_system=self.monitoring_system,
                    neuromorphic_simulator=self.neuromorphic_simulator,
                    duration=self.config.demo_duration
                )
            
            # Run alert system demo
            if self.config.enable_alerts:
                self.demo_results["alert_system"] = self.demo_components[3].run(
                    monitoring_system=self.monitoring_system,
                    load_simulator=self.load_simulator,
                    duration=self.config.demo_duration
                )
            
            # Get final system status
            self.demo_results["system_status"] = self.monitoring_system.get_system_status()
            self.demo_results["metrics_summary"] = self._generate_metrics_summary()
            
            self.logger.info("🎉 Enhanced Performance Monitoring Demo completed successfully!")
            return self.demo_results
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced Performance Monitoring Demo failed: {e}")
            raise
        finally:
            self.running = False
            self.monitoring_system.stop_monitoring()
    
    def _generate_metrics_summary(self) -> Dict[str, Any]:
        """Generate summary of collected metrics."""
        summary = {
            "total_metrics_collected": 0,
            "monitoring_duration": self.config.demo_duration,
            "system_performance": {},
            "quantum_performance": {},
            "neuromorphic_performance": {},
            "alert_summary": {}
        }
        
        # System performance summary
        if "system_monitoring" in self.demo_results:
            system_demo = self.demo_results["system_monitoring"]
            summary["system_performance"] = {
                "total_samples": system_demo.get("performance_analysis", {}).get("total_samples", 0),
                "average_cpu_load": system_demo.get("performance_analysis", {}).get("average_cpu_load", 0),
                "peak_cpu_load": system_demo.get("performance_analysis", {}).get("peak_cpu_load", 0),
                "anomalies_detected": len(system_demo.get("anomaly_detection", []))
            }
            summary["total_metrics_collected"] += summary["system_performance"]["total_samples"]
        
        # Quantum performance summary
        if "quantum_monitoring" in self.demo_results:
            quantum_demo = self.demo_results["quantum_monitoring"]
            summary["quantum_performance"] = {
                "total_circuits": quantum_demo.get("performance_trends", {}).get("total_circuits", 0),
                "average_error_rate": quantum_demo.get("performance_trends", {}).get("average_error_rate", 0),
                "average_quantum_advantage": quantum_demo.get("performance_trends", {}).get("average_quantum_advantage", 0),
                "optimization_insights": len(quantum_demo.get("optimization_insights", []))
            }
            summary["total_metrics_collected"] += summary["quantum_performance"]["total_circuits"]
        
        # Neuromorphic performance summary
        if "neuromorphic_monitoring" in self.demo_results:
            neuromorphic_demo = self.demo_results["neuromorphic_monitoring"]
            summary["neuromorphic_performance"] = {
                "total_learning_steps": neuromorphic_demo.get("learning_analysis", {}).get("total_learning_steps", 0),
                "average_learning_efficiency": neuromorphic_demo.get("learning_analysis", {}).get("average_learning_efficiency", 0),
                "average_emergent_score": neuromorphic_demo.get("learning_analysis", {}).get("average_emergent_score", 0),
                "emergent_insights": len(neuromorphic_demo.get("emergent_behavior_insights", []))
            }
            summary["total_metrics_collected"] += summary["neuromorphic_performance"]["total_learning_steps"]
        
        # Alert summary
        if "alert_system" in self.demo_results:
            alert_demo = self.demo_results["alert_system"]
            summary["alert_summary"] = {
                "total_alerts": alert_demo.get("alert_analysis", {}).get("total_alerts", 0),
                "alert_types": alert_demo.get("alert_analysis", {}).get("alert_types", {}),
                "most_common_alert": alert_demo.get("alert_analysis", {}).get("most_common_alert", "none")
            }
        
        return summary
    
    def save_results(self, output_path: Optional[str] = None) -> None:
        """Save demo results to file."""
        if output_path is None:
            output_path = self.config.results_file
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.demo_results, f, indent=2, default=str)
            self.logger.info(f"Enhanced Performance Monitoring Demo results saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save demo results: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.monitoring_system:
                self.monitoring_system.stop_monitoring()
            self.logger.info("Enhanced Performance Monitoring Demo cleanup completed")
        except Exception as e:
            self.logger.error(f"Demo cleanup failed: {e}")

# ===== MAIN EXECUTION =====

def main():
    """Main demo execution."""
    # Create demo configuration
    config = DemoConfiguration()
    
    # Create and run demo
    demo = EnhancedPerformanceMonitoringDemo(config)
    
    try:
        # Run comprehensive demo
        results = demo.run_comprehensive_demo()
        
        # Save results if enabled
        if config.export_results:
            demo.save_results()
        
        # Print demo summary
        print("\n" + "="*80)
        print("🎉 ENHANCED PERFORMANCE MONITORING SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        # Print metrics summary
        if "metrics_summary" in results:
            summary = results["metrics_summary"]
            print(f"📊 Metrics Summary:")
            print(f"   Total Metrics Collected: {summary.get('total_metrics_collected', 0)}")
            print(f"   Monitoring Duration: {summary.get('monitoring_duration', 0)} seconds")
            
            # System performance
            system_perf = summary.get("system_performance", {})
            if system_perf:
                print(f"   System Performance:")
                print(f"     Total Samples: {system_perf.get('total_samples', 0)}")
                print(f"     Average CPU Load: {system_perf.get('average_cpu_load', 0):.2f}")
                print(f"     Peak CPU Load: {system_perf.get('peak_cpu_load', 0):.2f}")
                print(f"     Anomalies Detected: {system_perf.get('anomalies_detected', 0)}")
            
            # Quantum performance
            quantum_perf = summary.get("quantum_performance", {})
            if quantum_perf:
                print(f"   Quantum Performance:")
                print(f"     Total Circuits: {quantum_perf.get('total_circuits', 0)}")
                print(f"     Average Error Rate: {quantum_perf.get('average_error_rate', 0):.3f}")
                print(f"     Average Quantum Advantage: {quantum_perf.get('average_quantum_advantage', 0):.2f}")
                print(f"     Optimization Insights: {quantum_perf.get('optimization_insights', 0)}")
            
            # Neuromorphic performance
            neuromorphic_perf = summary.get("neuromorphic_performance", {})
            if neuromorphic_perf:
                print(f"   Neuromorphic Performance:")
                print(f"     Total Learning Steps: {neuromorphic_perf.get('total_learning_steps', 0)}")
                print(f"     Average Learning Efficiency: {neuromorphic_perf.get('average_learning_efficiency', 0):.2f}")
                print(f"     Average Emergent Score: {neuromorphic_perf.get('average_emergent_score', 0):.2f}")
                print(f"     Emergent Insights: {neuromorphic_perf.get('emergent_insights', 0)}")
            
            # Alert summary
            alert_summary = summary.get("alert_summary", {})
            if alert_summary:
                print(f"   Alert Summary:")
                print(f"     Total Alerts: {alert_summary.get('total_alerts', 0)}")
                print(f"     Alert Types: {alert_summary.get('alert_types', {})}")
        
        print("="*80)
        
    except Exception as e:
        print(f"❌ Enhanced Performance Monitoring Demo failed: {e}")
        raise
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
