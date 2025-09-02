#!/usr/bin/env python3
"""
Optimization Engine Demo for Advanced Distributed AI
Comprehensive demonstration of quantum, neuromorphic, and hybrid optimization capabilities
"""

import logging
import time
import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

# Import the optimization engine
from core.optimization_engine import (
    OptimizationEngine,
    OptimizationConfig,
    QuantumConfig,
    NeuromorphicConfig,
    OptimizationType,
    OptimizationStatus,
    create_optimization_engine
)

# ===== DEMO CONFIGURATION =====

class DemoConfiguration:
    """Configuration for the optimization engine demo."""
    
    def __init__(self):
        self.demo_duration = 60  # seconds
        self.optimization_interval = 5.0  # seconds
        self.simulation_intensity = "high"  # low, medium, high
        self.enable_quantum = True
        self.enable_neuromorphic = True
        self.enable_hybrid = True
        self.export_results = True
        self.results_file = "optimization_engine_demo_results.json"

# ===== PROBLEM GENERATOR =====

class OptimizationProblemGenerator:
    """Generates various optimization problems for demonstration."""
    
    def __init__(self, intensity: str = "medium"):
        self.intensity = intensity
        self.problem_counter = 0
        
        # Problem types and their characteristics
        self.problem_types = {
            "quantum_optimization": {
                "complexity": "high",
                "quantum_suitable": True,
                "neuromorphic_suitable": False,
                "description": "Quantum optimization problems"
            },
            "neuromorphic_learning": {
                "complexity": "medium",
                "quantum_suitable": False,
                "neuromorphic_suitable": True,
                "description": "Neuromorphic learning problems"
            },
            "hybrid_optimization": {
                "complexity": "very_high",
                "quantum_suitable": True,
                "neuromorphic_suitable": True,
                "description": "Hybrid optimization problems"
            },
            "system_optimization": {
                "complexity": "low",
                "quantum_suitable": False,
                "neuromorphic_suitable": False,
                "description": "System optimization problems"
            }
        }
    
    def generate_quantum_problem(self) -> Dict[str, Any]:
        """Generate a quantum optimization problem."""
        self.problem_counter += 1
        
        problem_types = [
            "max_cut",
            "traveling_salesman",
            "graph_coloring",
            "portfolio_optimization",
            "quantum_chemistry"
        ]
        
        return {
            "problem_id": f"quantum_problem_{self.problem_counter:03d}",
            "problem_type": "quantum_optimization",
            "specific_type": random.choice(problem_types),
            "complexity": random.uniform(0.7, 1.0),
            "qubits_required": random.randint(10, 30),
            "layers_required": random.randint(2, 8),
            "optimization_target": "minimize_energy",
            "constraints": {
                "max_iterations": random.randint(100, 1000),
                "convergence_threshold": random.uniform(1e-6, 1e-4),
                "timeout_seconds": random.randint(60, 300)
            },
            "metadata": {
                "quantum_suitable": True,
                "neuromorphic_suitable": False,
                "hybrid_suitable": True,
                "description": "Quantum optimization problem suitable for QAOA, VQE, or quantum neural networks"
            }
        }
    
    def generate_neuromorphic_problem(self) -> Dict[str, Any]:
        """Generate a neuromorphic optimization problem."""
        self.problem_counter += 1
        
        problem_types = [
            "pattern_recognition",
            "sequence_learning",
            "adaptive_control",
            "reinforcement_learning",
            "emergent_behavior"
        ]
        
        return {
            "problem_id": f"neuromorphic_problem_{self.problem_counter:03d}",
            "problem_type": "neuromorphic_learning",
            "specific_type": random.choice(problem_types),
            "complexity": random.uniform(0.5, 0.9),
            "neurons_required": random.randint(500, 5000),
            "learning_rate": random.uniform(0.001, 0.1),
            "optimization_target": "maximize_learning_efficiency",
            "constraints": {
                "max_epochs": random.randint(50, 500),
                "convergence_threshold": random.uniform(1e-4, 1e-2),
                "timeout_seconds": random.randint(30, 180)
            },
            "metadata": {
                "quantum_suitable": False,
                "neuromorphic_suitable": True,
                "hybrid_suitable": True,
                "description": "Neuromorphic learning problem suitable for STDP, Hebbian learning, or competitive learning"
            }
        }
    
    def generate_hybrid_problem(self) -> Dict[str, Any]:
        """Generate a hybrid optimization problem."""
        self.problem_counter += 1
        
        problem_types = [
            "quantum_neuromorphic_fusion",
            "multi_objective_optimization",
            "adaptive_quantum_learning",
            "emergent_quantum_behavior",
            "collective_intelligence"
        ]
        
        return {
            "problem_id": f"hybrid_problem_{self.problem_counter:03d}",
            "problem_type": "hybrid_optimization",
            "specific_type": random.choice(problem_types),
            "complexity": random.uniform(0.8, 1.0),
            "qubits_required": random.randint(15, 25),
            "neurons_required": random.randint(1000, 3000),
            "optimization_target": "maximize_hybrid_advantage",
            "constraints": {
                "max_iterations": random.randint(200, 800),
                "convergence_threshold": random.uniform(1e-5, 1e-3),
                "timeout_seconds": random.randint(120, 400)
            },
            "metadata": {
                "quantum_suitable": True,
                "neuromorphic_suitable": True,
                "hybrid_suitable": True,
                "description": "Hybrid optimization problem requiring both quantum and neuromorphic capabilities"
            }
        }
    
    def generate_system_problem(self) -> Dict[str, Any]:
        """Generate a system optimization problem."""
        self.problem_counter += 1
        
        problem_types = [
            "resource_allocation",
            "load_balancing",
            "performance_tuning",
            "cost_optimization",
            "scalability_optimization"
        ]
        
        return {
            "problem_id": f"system_problem_{self.problem_counter:03d}",
            "problem_type": "system_optimization",
            "specific_type": random.choice(problem_types),
            "complexity": random.uniform(0.3, 0.7),
            "optimization_target": "minimize_cost_maximize_performance",
            "constraints": {
                "max_iterations": random.randint(50, 200),
                "convergence_threshold": random.uniform(1e-3, 1e-1),
                "timeout_seconds": random.randint(20, 100)
            },
            "metadata": {
                "quantum_suitable": False,
                "neuromorphic_suitable": False,
                "hybrid_suitable": False,
                "description": "System optimization problem suitable for classical optimization methods"
            }
        }
    
    def generate_random_problem(self) -> Dict[str, Any]:
        """Generate a random optimization problem."""
        problem_type = random.choice(list(self.problem_types.keys()))
        
        if problem_type == "quantum_optimization":
            return self.generate_quantum_problem()
        elif problem_type == "neuromorphic_learning":
            return self.generate_neuromorphic_problem()
        elif problem_type == "hybrid_optimization":
            return self.generate_hybrid_problem()
        else:
            return self.generate_system_problem()

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

class QuantumOptimizationDemo(DemoComponent):
    """Demo quantum optimization capabilities."""
    
    def __init__(self):
        super().__init__("Quantum Optimization")
    
    def _execute(self, optimization_engine: OptimizationEngine, 
                problem_generator: OptimizationProblemGenerator, duration: int) -> Dict[str, Any]:
        """Execute quantum optimization demo."""
        results = {
            "quantum_optimizations": [],
            "performance_analysis": {},
            "quantum_advantage_analysis": []
        }
        
        start_time = time.time()
        optimization_count = 0
        
        while time.time() - start_time < duration:
            # Generate quantum problem
            problem = problem_generator.generate_quantum_problem()
            
            # Execute quantum optimization
            optimization_result = optimization_engine.optimize(problem, "quantum")
            
            # Store results
            results["quantum_optimizations"].append({
                "problem": problem,
                "result": optimization_result,
                "timestamp": time.time(),
                "optimization_number": optimization_count + 1
            })
            
            # Analyze quantum advantage
            if "error" not in optimization_result:
                quantum_advantage = optimization_result.get("quantum_advantage", 1.0)
                results["quantum_advantage_analysis"].append({
                    "optimization_number": optimization_count + 1,
                    "quantum_advantage": quantum_advantage,
                    "advantage_category": "high" if quantum_advantage > 1.5 else "medium" if quantum_advantage > 1.2 else "low"
                })
            
            optimization_count += 1
            time.sleep(2.0)  # Brief pause between optimizations
        
        # Analyze performance
        results["performance_analysis"] = self._analyze_quantum_performance(results["quantum_optimizations"])
        
        return results
    
    def _analyze_quantum_performance(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quantum optimization performance."""
        if not optimizations:
            return {}
        
        successful_optimizations = [opt for opt in optimizations if "error" not in opt["result"]]
        
        if not successful_optimizations:
            return {"total_optimizations": len(optimizations), "success_rate": 0.0}
        
        # Calculate performance metrics
        execution_times = [opt["result"].get("execution_time", 0) for opt in successful_optimizations]
        optimization_scores = [opt["result"].get("optimization_score", 0) for opt in successful_optimizations]
        quantum_advantages = [opt["result"].get("quantum_advantage", 1.0) for opt in successful_optimizations]
        
        analysis = {
            "total_optimizations": len(optimizations),
            "successful_optimizations": len(successful_optimizations),
            "success_rate": len(successful_optimizations) / len(optimizations),
            "average_execution_time": np.mean(execution_times) if execution_times else 0,
            "average_optimization_score": np.mean(optimization_scores) if optimization_scores else 0,
            "average_quantum_advantage": np.mean(quantum_advantages) if quantum_advantages else 1.0,
            "best_quantum_advantage": max(quantum_advantages) if quantum_advantages else 1.0,
            "worst_quantum_advantage": min(quantum_advantages) if quantum_advantages else 1.0
        }
        
        return analysis

class NeuromorphicOptimizationDemo(DemoComponent):
    """Demo neuromorphic optimization capabilities."""
    
    def __init__(self):
        super().__init__("Neuromorphic Optimization")
    
    def _execute(self, optimization_engine: OptimizationEngine, 
                problem_generator: OptimizationProblemGenerator, duration: int) -> Dict[str, Any]:
        """Execute neuromorphic optimization demo."""
        results = {
            "neuromorphic_optimizations": [],
            "learning_analysis": {},
            "plasticity_analysis": []
        }
        
        start_time = time.time()
        optimization_count = 0
        
        while time.time() - start_time < duration:
            # Generate neuromorphic problem
            problem = problem_generator.generate_neuromorphic_problem()
            
            # Execute neuromorphic optimization
            optimization_result = optimization_engine.optimize(problem, "neuromorphic")
            
            # Store results
            results["neuromorphic_optimizations"].append({
                "problem": problem,
                "result": optimization_result,
                "timestamp": time.time(),
                "optimization_number": optimization_count + 1
            })
            
            # Analyze learning progress
            if "error" not in optimization_result:
                learning_progress = optimization_result.get("learning_progress", 0.0)
                results["plasticity_analysis"].append({
                    "optimization_number": optimization_count + 1,
                    "learning_progress": learning_progress,
                    "progress_category": "high" if learning_progress > 0.8 else "medium" if learning_progress > 0.5 else "low"
                })
            
            optimization_count += 1
            time.sleep(2.0)  # Brief pause between optimizations
        
        # Analyze performance
        results["learning_analysis"] = self._analyze_neuromorphic_performance(results["neuromorphic_optimizations"])
        
        return results
    
    def _analyze_neuromorphic_performance(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze neuromorphic optimization performance."""
        if not optimizations:
            return {}
        
        successful_optimizations = [opt for opt in optimizations if "error" not in opt["result"]]
        
        if not successful_optimizations:
            return {"total_optimizations": len(optimizations), "success_rate": 0.0}
        
        # Calculate performance metrics
        execution_times = [opt["result"].get("execution_time", 0) for opt in successful_optimizations]
        optimization_scores = [opt["result"].get("optimization_score", 0) for opt in successful_optimizations]
        learning_progress = [opt["result"].get("learning_progress", 0) for opt in successful_optimizations]
        
        analysis = {
            "total_optimizations": len(optimizations),
            "successful_optimizations": len(successful_optimizations),
            "success_rate": len(successful_optimizations) / len(optimizations),
            "average_execution_time": np.mean(execution_times) if execution_times else 0,
            "average_optimization_score": np.mean(optimization_scores) if optimization_scores else 0,
            "average_learning_progress": np.mean(learning_progress) if learning_progress else 0,
            "best_learning_progress": max(learning_progress) if learning_progress else 0,
            "worst_learning_progress": min(learning_progress) if learning_progress else 0
        }
        
        return analysis

class HybridOptimizationDemo(DemoComponent):
    """Demo hybrid optimization capabilities."""
    
    def __init__(self):
        super().__init__("Hybrid Optimization")
    
    def _execute(self, optimization_engine: OptimizationEngine, 
                problem_generator: OptimizationProblemGenerator, duration: int) -> Dict[str, Any]:
        """Execute hybrid optimization demo."""
        results = {
            "hybrid_optimizations": [],
            "fusion_analysis": {},
            "hybrid_advantage_analysis": []
        }
        
        start_time = time.time()
        optimization_count = 0
        
        while time.time() - start_time < duration:
            # Generate hybrid problem
            problem = problem_generator.generate_hybrid_problem()
            
            # Execute hybrid optimization
            optimization_result = optimization_engine.optimize(problem, "hybrid")
            
            # Store results
            results["hybrid_optimizations"].append({
                "problem": problem,
                "result": optimization_result,
                "timestamp": time.time(),
                "optimization_number": optimization_count + 1
            })
            
            # Analyze hybrid advantage
            if "error" not in optimization_result:
                fused_score = optimization_result.get("fused_score", 0.0)
                results["hybrid_advantage_analysis"].append({
                    "optimization_number": optimization_count + 1,
                    "fused_score": fused_score,
                    "advantage_category": "high" if fused_score > 0.8 else "medium" if fused_score > 0.6 else "low"
                })
            
            optimization_count += 1
            time.sleep(3.0)  # Longer pause for hybrid optimizations
        
        # Analyze performance
        results["fusion_analysis"] = self._analyze_hybrid_performance(results["hybrid_optimizations"])
        
        return results
    
    def _analyze_hybrid_performance(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze hybrid optimization performance."""
        if not optimizations:
            return {}
        
        successful_optimizations = [opt for opt in optimizations if "error" not in opt["result"]]
        
        if not successful_optimizations:
            return {"total_optimizations": len(optimizations), "success_rate": 0.0}
        
        # Calculate performance metrics
        execution_times = [opt["result"].get("total_time", 0) for opt in successful_optimizations]
        fused_scores = [opt["result"].get("fused_score", 0) for opt in successful_optimizations]
        
        # Analyze sub-results
        quantum_scores = []
        neuromorphic_scores = []
        
        for opt in successful_optimizations:
            sub_results = opt["result"].get("sub_results", {})
            if "quantum" in sub_results:
                quantum_scores.append(sub_results["quantum"].get("optimization_score", 0))
            if "neuromorphic" in sub_results:
                neuromorphic_scores.append(sub_results["neuromorphic"].get("optimization_score", 0))
        
        analysis = {
            "total_optimizations": len(optimizations),
            "successful_optimizations": len(successful_optimizations),
            "success_rate": len(successful_optimizations) / len(optimizations),
            "average_execution_time": np.mean(execution_times) if execution_times else 0,
            "average_fused_score": np.mean(fused_scores) if fused_scores else 0,
            "best_fused_score": max(fused_scores) if fused_scores else 0,
            "worst_fused_score": min(fused_scores) if fused_scores else 0,
            "average_quantum_score": np.mean(quantum_scores) if quantum_scores else 0,
            "average_neuromorphic_score": np.mean(neuromorphic_scores) if neuromorphic_scores else 0
        }
        
        return analysis

class ComparativeAnalysisDemo(DemoComponent):
    """Demo comparative analysis of different optimization approaches."""
    
    def __init__(self):
        super().__init__("Comparative Analysis")
    
    def _execute(self, optimization_engine: OptimizationEngine, 
                problem_generator: OptimizationProblemGenerator, duration: int) -> Dict[str, Any]:
        """Execute comparative analysis demo."""
        results = {
            "comparative_optimizations": [],
            "performance_comparison": {},
            "optimizer_recommendations": []
        }
        
        start_time = time.time()
        optimization_count = 0
        
        while time.time() - start_time < duration:
            # Generate a problem that can be solved by multiple approaches
            problem = problem_generator.generate_hybrid_problem()
            
            # Execute optimization with different approaches
            quantum_result = optimization_engine.optimize(problem, "quantum")
            neuromorphic_result = optimization_engine.optimize(problem, "neuromorphic")
            hybrid_result = optimization_engine.optimize(problem, "hybrid")
            
            # Store comparative results
            results["comparative_optimizations"].append({
                "problem": problem,
                "optimization_number": optimization_count + 1,
                "timestamp": time.time(),
                "quantum_result": quantum_result,
                "neuromorphic_result": neuromorphic_result,
                "hybrid_result": hybrid_result
            })
            
            # Generate recommendations
            recommendation = self._generate_optimizer_recommendation(
                problem, quantum_result, neuromorphic_result, hybrid_result
            )
            results["optimizer_recommendations"].append(recommendation)
            
            optimization_count += 1
            time.sleep(4.0)  # Longer pause for comparative analysis
        
        # Analyze comparative performance
        results["performance_comparison"] = self._analyze_comparative_performance(results["comparative_optimizations"])
        
        return results
    
    def _generate_optimizer_recommendation(self, problem: Dict[str, Any], 
                                         quantum_result: Dict[str, Any], 
                                         neuromorphic_result: Dict[str, Any], 
                                         hybrid_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimizer recommendation based on results."""
        # Extract scores
        quantum_score = quantum_result.get("optimization_score", 0) if "error" not in quantum_result else 0
        neuromorphic_score = neuromorphic_result.get("optimization_score", 0) if "error" not in neuromorphic_result else 0
        hybrid_score = hybrid_result.get("fused_score", 0) if "error" not in hybrid_result else 0
        
        # Determine best optimizer
        scores = {
            "quantum": quantum_score,
            "neuromorphic": neuromorphic_score,
            "hybrid": hybrid_score
        }
        
        best_optimizer = max(scores, key=scores.get)
        best_score = scores[best_optimizer]
        
        # Generate recommendation reasoning
        reasoning = []
        if quantum_score > 0.8:
            reasoning.append("Quantum optimizer achieved high performance")
        if neuromorphic_score > 0.8:
            reasoning.append("Neuromorphic optimizer achieved high performance")
        if hybrid_score > 0.8:
            reasoning.append("Hybrid optimizer achieved high performance")
        
        if not reasoning:
            reasoning.append("All optimizers achieved moderate performance")
        
        return {
            "problem_id": problem["problem_id"],
            "recommended_optimizer": best_optimizer,
            "recommended_score": best_score,
            "all_scores": scores,
            "reasoning": reasoning,
            "timestamp": time.time()
        }
    
    def _analyze_comparative_performance(self, optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze comparative optimization performance."""
        if not optimizations:
            return {}
        
        # Collect scores for each optimizer
        quantum_scores = []
        neuromorphic_scores = []
        hybrid_scores = []
        
        for opt in optimizations:
            if "error" not in opt["quantum_result"]:
                quantum_scores.append(opt["quantum_result"].get("optimization_score", 0))
            if "error" not in opt["neuromorphic_result"]:
                neuromorphic_scores.append(opt["neuromorphic_result"].get("optimization_score", 0))
            if "error" not in opt["hybrid_result"]:
                hybrid_scores.append(opt["hybrid_result"].get("fused_score", 0))
        
        analysis = {
            "total_comparisons": len(optimizations),
            "quantum_performance": {
                "average_score": np.mean(quantum_scores) if quantum_scores else 0,
                "best_score": max(quantum_scores) if quantum_scores else 0,
                "total_optimizations": len(quantum_scores)
            },
            "neuromorphic_performance": {
                "average_score": np.mean(neuromorphic_scores) if neuromorphic_scores else 0,
                "best_score": max(neuromorphic_scores) if neuromorphic_scores else 0,
                "total_optimizations": len(neuromorphic_scores)
            },
            "hybrid_performance": {
                "average_score": np.mean(hybrid_scores) if hybrid_scores else 0,
                "best_score": max(hybrid_scores) if hybrid_scores else 0,
                "total_optimizations": len(hybrid_scores)
            }
        }
        
        # Determine overall winner
        avg_scores = {
            "quantum": analysis["quantum_performance"]["average_score"],
            "neuromorphic": analysis["neuromorphic_performance"]["average_score"],
            "hybrid": analysis["hybrid_performance"]["average_score"]
        }
        
        overall_winner = max(avg_scores, key=avg_scores.get)
        analysis["overall_winner"] = overall_winner
        analysis["overall_winner_score"] = avg_scores[overall_winner]
        
        return analysis

# ===== MAIN DEMO CLASS =====

class OptimizationEngineDemo:
    """Main demo class for optimization engine."""
    
    def __init__(self, config: DemoConfiguration):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.OptimizationEngineDemo")
        self.demo_results = {}
        self.running = False
        
        # Initialize components
        self.problem_generator = OptimizationProblemGenerator(config.simulation_intensity)
        self.demo_components = self._initialize_demo_components()
        
        # Initialize optimization engine
        self.optimization_engine = self._initialize_optimization_engine()
        
        # Setup logging
        self._setup_logging()
    
    def _initialize_demo_components(self) -> List[DemoComponent]:
        """Initialize demo components."""
        components = []
        
        if self.config.enable_quantum:
            components.append(QuantumOptimizationDemo())
        if self.config.enable_neuromorphic:
            components.append(NeuromorphicOptimizationDemo())
        if self.config.enable_hybrid:
            components.append(HybridOptimizationDemo())
        
        # Always include comparative analysis
        components.append(ComparativeAnalysisDemo())
        
        return components
    
    def _initialize_optimization_engine(self) -> OptimizationEngine:
        """Initialize the optimization engine."""
        # Create configurations
        optimization_config = OptimizationConfig(
            enabled=True,
            optimization_type=OptimizationType.HYBRID,
            max_iterations=1000,
            convergence_threshold=1e-6,
            timeout_seconds=300,
            enable_parallel=True,
            enable_adaptive=True
        )
        
        quantum_config = QuantumConfig(
            enabled=self.config.enable_quantum,
            qubits=20,
            layers=3,
            shots=1000,
            enable_error_mitigation=True
        )
        
        neuromorphic_config = NeuromorphicConfig(
            enabled=self.config.enable_neuromorphic,
            neurons=1000,
            learning_rate=0.01,
            enable_adaptation=True
        )
        
        # Create optimization engine
        return create_optimization_engine(optimization_config, quantum_config, neuromorphic_config)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def run_comprehensive_demo(self) -> Dict[str, Any]:
        """Run comprehensive optimization engine demonstration."""
        self.logger.info("🚀 Starting Optimization Engine Demo...")
        self.running = True
        
        try:
            # Run quantum optimization demo
            if self.config.enable_quantum:
                self.demo_results["quantum_optimization"] = self.demo_components[0].run(
                    optimization_engine=self.optimization_engine,
                    problem_generator=self.problem_generator,
                    duration=self.config.demo_duration
                )
            
            # Run neuromorphic optimization demo
            if self.config.enable_neuromorphic:
                neuromorphic_index = 1 if self.config.enable_quantum else 0
                self.demo_results["neuromorphic_optimization"] = self.demo_components[neuromorphic_index].run(
                    optimization_engine=self.optimization_engine,
                    problem_generator=self.problem_generator,
                    duration=self.config.demo_duration
                )
            
            # Run hybrid optimization demo
            if self.config.enable_hybrid:
                hybrid_index = 2 if self.config.enable_quantum and self.config.enable_neuromorphic else 1
                self.demo_results["hybrid_optimization"] = self.demo_components[hybrid_index].run(
                    optimization_engine=self.optimization_engine,
                    problem_generator=self.problem_generator,
                    duration=self.config.demo_duration
                )
            
            # Run comparative analysis demo
            comparative_index = len(self.demo_components) - 1
            self.demo_results["comparative_analysis"] = self.demo_components[comparative_index].run(
                optimization_engine=self.optimization_engine,
                problem_generator=self.problem_generator,
                duration=self.config.demo_duration
            )
            
            # Get final system status
            self.demo_results["system_status"] = self.optimization_engine.get_system_status()
            self.demo_results["demo_summary"] = self._generate_demo_summary()
            
            self.logger.info("🎉 Optimization Engine Demo completed successfully!")
            return self.demo_results
            
        except Exception as e:
            self.logger.error(f"❌ Optimization Engine Demo failed: {e}")
            raise
        finally:
            self.running = False
    
    def _generate_demo_summary(self) -> Dict[str, Any]:
        """Generate summary of demo results."""
        summary = {
            "total_optimizations": 0,
            "success_rate": 0.0,
            "best_performing_optimizer": "unknown",
            "performance_breakdown": {},
            "recommendations": []
        }
        
        # Collect performance data
        optimizer_performances = {}
        
        if "quantum_optimization" in self.demo_results:
            quantum_demo = self.demo_results["quantum_optimization"]
            if "performance_analysis" in quantum_demo:
                perf = quantum_demo["performance_analysis"]
                optimizer_performances["quantum"] = {
                    "success_rate": perf.get("success_rate", 0.0),
                    "average_score": perf.get("average_optimization_score", 0.0),
                    "total_optimizations": perf.get("total_optimizations", 0)
                }
                summary["total_optimizations"] += perf.get("total_optimizations", 0)
        
        if "neuromorphic_optimization" in self.demo_results:
            neuromorphic_demo = self.demo_results["neuromorphic_optimization"]
            if "learning_analysis" in neuromorphic_demo:
                perf = neuromorphic_demo["learning_analysis"]
                optimizer_performances["neuromorphic"] = {
                    "success_rate": perf.get("success_rate", 0.0),
                    "average_score": perf.get("average_optimization_score", 0.0),
                    "total_optimizations": perf.get("total_optimizations", 0)
                }
                summary["total_optimizations"] += perf.get("total_optimizations", 0)
        
        if "hybrid_optimization" in self.demo_results:
            hybrid_demo = self.demo_results["hybrid_optimization"]
            if "fusion_analysis" in hybrid_demo:
                perf = hybrid_demo["fusion_analysis"]
                optimizer_performances["hybrid"] = {
                    "success_rate": perf.get("success_rate", 0.0),
                    "average_score": perf.get("average_fused_score", 0.0),
                    "total_optimizations": perf.get("total_optimizations", 0)
                }
                summary["total_optimizations"] += perf.get("total_optimizations", 0)
        
        # Calculate overall success rate
        total_successful = sum(perf["success_rate"] * perf["total_optimizations"] for perf in optimizer_performances.values())
        summary["success_rate"] = total_successful / summary["total_optimizations"] if summary["total_optimizations"] > 0 else 0.0
        
        # Determine best performing optimizer
        if optimizer_performances:
            best_optimizer = max(optimizer_performances.items(), key=lambda x: x[1]["average_score"])
            summary["best_performing_optimizer"] = best_optimizer[0]
            summary["best_performing_score"] = best_optimizer[1]["average_score"]
        
        summary["performance_breakdown"] = optimizer_performances
        
        # Add recommendations from comparative analysis
        if "comparative_analysis" in self.demo_results:
            comparative_demo = self.demo_results["comparative_analysis"]
            if "optimizer_recommendations" in comparative_demo:
                summary["recommendations"] = comparative_demo["optimizer_recommendations"]
        
        return summary
    
    def save_results(self, output_path: Optional[str] = None) -> None:
        """Save demo results to file."""
        if output_path is None:
            output_path = self.config.results_file
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.demo_results, f, indent=2, default=str)
            self.logger.info(f"Optimization Engine Demo results saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save demo results: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Get final optimization history
            final_history = self.optimization_engine.get_optimization_history()
            self.logger.info(f"Total optimizations performed: {len(final_history)}")
            
            # Get performance metrics
            performance_metrics = self.optimization_engine.get_performance_metrics()
            for optimizer_type, metrics in performance_metrics.items():
                self.logger.info(f"{optimizer_type} optimizer: {len(metrics)} performance records")
            
            self.logger.info("Optimization Engine Demo cleanup completed")
        except Exception as e:
            self.logger.error(f"Demo cleanup failed: {e}")

# ===== MAIN EXECUTION =====

def main():
    """Main demo execution."""
    # Create demo configuration
    config = DemoConfiguration()
    
    # Create and run demo
    demo = OptimizationEngineDemo(config)
    
    try:
        # Run comprehensive demo
        results = demo.run_comprehensive_demo()
        
        # Save results if enabled
        if config.export_results:
            demo.save_results()
        
        # Print demo summary
        print("\n" + "="*80)
        print("🎉 OPTIMIZATION ENGINE DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        # Print demo summary
        if "demo_summary" in results:
            summary = results["demo_summary"]
            print(f"📊 Demo Summary:")
            print(f"   Total Optimizations: {summary.get('total_optimizations', 0)}")
            print(f"   Overall Success Rate: {summary.get('success_rate', 0):.2%}")
            print(f"   Best Performing Optimizer: {summary.get('best_performing_optimizer', 'N/A')}")
            print(f"   Best Performance Score: {summary.get('best_performing_score', 0):.3f}")
            
            # Performance breakdown
            performance_breakdown = summary.get("performance_breakdown", {})
            if performance_breakdown:
                print(f"\n🔍 Performance Breakdown:")
                for optimizer, perf in performance_breakdown.items():
                    print(f"   {optimizer.capitalize()}:")
                    print(f"     Success Rate: {perf.get('success_rate', 0):.2%}")
                    print(f"     Average Score: {perf.get('average_score', 0):.3f}")
                    print(f"     Total Optimizations: {perf.get('total_optimizations', 0)}")
            
            # Recommendations
            recommendations = summary.get("recommendations", [])
            if recommendations:
                print(f"\n💡 Top Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. Problem {rec.get('problem_id', 'N/A')}: Use {rec.get('recommended_optimizer', 'N/A')} optimizer")
        
        print("="*80)
        
    except Exception as e:
        print(f"❌ Optimization Engine Demo failed: {e}")
        raise
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
