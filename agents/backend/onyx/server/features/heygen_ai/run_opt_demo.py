#!/usr/bin/env python3
"""
Optimization Engine Demo for Advanced Distributed AI
Simple demonstration of quantum, neuromorphic, and hybrid optimization capabilities
"""

import logging
import time
import json
import random
from typing import Dict, Any, List

# Import the optimization engine
from core.optimization_engine import (
    OptimizationEngine,
    OptimizationConfig,
    QuantumConfig,
    NeuromorphicConfig,
    create_optimization_engine
)

# ===== PROBLEM GENERATOR =====

class ProblemGenerator:
    """Generates optimization problems for demonstration."""
    
    def __init__(self):
        self.counter = 0
    
    def generate_quantum_problem(self) -> Dict[str, Any]:
        """Generate a quantum optimization problem."""
        self.counter += 1
        return {
            "id": f"quantum_{self.counter:03d}",
            "type": "quantum_optimization",
            "complexity": random.uniform(0.7, 1.0),
            "qubits": random.randint(10, 30),
            "description": "Quantum optimization problem"
        }
    
    def generate_neuromorphic_problem(self) -> Dict[str, Any]:
        """Generate a neuromorphic optimization problem."""
        self.counter += 1
        return {
            "id": f"neuromorphic_{self.counter:03d}",
            "type": "neuromorphic_learning",
            "complexity": random.uniform(0.5, 0.9),
            "neurons": random.randint(500, 5000),
            "description": "Neuromorphic learning problem"
        }
    
    def generate_hybrid_problem(self) -> Dict[str, Any]:
        """Generate a hybrid optimization problem."""
        self.counter += 1
        return {
            "id": f"hybrid_{self.counter:03d}",
            "type": "hybrid_optimization",
            "complexity": random.uniform(0.8, 1.0),
            "description": "Hybrid optimization problem"
        }

# ===== DEMO FUNCTIONS =====

def run_quantum_demo(engine: OptimizationEngine, problem_gen: ProblemGenerator) -> Dict[str, Any]:
    """Run quantum optimization demo."""
    print("🔮 Running Quantum Optimization Demo...")
    
    results = []
    for i in range(5):
        problem = problem_gen.generate_quantum_problem()
        result = engine.optimize(problem, "quantum")
        results.append({"problem": problem, "result": result})
        time.sleep(1)
    
    # Analyze results
    successful = [r for r in results if "error" not in r["result"]]
    if successful:
        scores = [r["result"].get("optimization_score", 0) for r in successful]
        advantages = [r["result"].get("quantum_advantage", 1.0) for r in successful]
        
        analysis = {
            "total_problems": len(results),
            "successful_optimizations": len(successful),
            "success_rate": len(successful) / len(results),
            "average_score": sum(scores) / len(scores),
            "average_quantum_advantage": sum(advantages) / len(advantages),
            "best_quantum_advantage": max(advantages)
        }
    else:
        analysis = {"error": "No successful optimizations"}
    
    print(f"✅ Quantum Demo Complete: {len(successful)}/{len(results)} successful")
    return {"results": results, "analysis": analysis}

def run_neuromorphic_demo(engine: OptimizationEngine, problem_gen: ProblemGenerator) -> Dict[str, Any]:
    """Run neuromorphic optimization demo."""
    print("🧠 Running Neuromorphic Optimization Demo...")
    
    results = []
    for i in range(5):
        problem = problem_gen.generate_neuromorphic_problem()
        result = engine.optimize(problem, "neuromorphic")
        results.append({"problem": problem, "result": result})
        time.sleep(1)
    
    # Analyze results
    successful = [r for r in results if "error" not in r["result"]]
    if successful:
        scores = [r["result"].get("optimization_score", 0) for r in successful]
        learning_progress = [r["result"].get("learning_progress", 0) for r in successful]
        
        analysis = {
            "total_problems": len(results),
            "successful_optimizations": len(successful),
            "success_rate": len(successful) / len(results),
            "average_score": sum(scores) / len(scores),
            "average_learning_progress": sum(learning_progress) / len(learning_progress)
        }
    else:
        analysis = {"error": "No successful optimizations"}
    
    print(f"✅ Neuromorphic Demo Complete: {len(successful)}/{len(results)} successful")
    return {"results": results, "analysis": analysis}

def run_hybrid_demo(engine: OptimizationEngine, problem_gen: ProblemGenerator) -> Dict[str, Any]:
    """Run hybrid optimization demo."""
    print("🚀 Running Hybrid Optimization Demo...")
    
    results = []
    for i in range(5):
        problem = problem_gen.generate_hybrid_problem()
        result = engine.optimize(problem, "hybrid")
        results.append({"problem": problem, "result": result})
        time.sleep(1.5)
    
    # Analyze results
    successful = [r for r in results if "error" not in r["result"]]
    if successful:
        fused_scores = [r["result"].get("fused_score", 0) for r in successful]
        
        analysis = {
            "total_problems": len(results),
            "successful_optimizations": len(successful),
            "success_rate": len(successful) / len(results),
            "average_fused_score": sum(fused_scores) / len(fused_scores),
            "best_fused_score": max(fused_scores)
        }
    else:
        analysis = {"error": "No successful optimizations"}
    
    print(f"✅ Hybrid Demo Complete: {len(successful)}/{len(results)} successful")
    return {"results": results, "analysis": analysis}

def run_comparative_demo(engine: OptimizationEngine, problem_gen: ProblemGenerator) -> Dict[str, Any]:
    """Run comparative analysis demo."""
    print("📊 Running Comparative Analysis Demo...")
    
    results = []
    for i in range(3):
        problem = problem_gen.generate_hybrid_problem()
        
        # Test all optimizers on the same problem
        quantum_result = engine.optimize(problem, "quantum")
        neuromorphic_result = engine.optimize(problem, "neuromorphic")
        hybrid_result = engine.optimize(problem, "hybrid")
        
        results.append({
            "problem": problem,
            "quantum": quantum_result,
            "neuromorphic": neuromorphic_result,
            "hybrid": hybrid_result
        })
        
        time.sleep(2)
    
    # Analyze comparative performance
    analysis = {"comparisons": len(results), "recommendations": []}
    
    for i, result in enumerate(results):
        quantum_score = result["quantum"].get("optimization_score", 0) if "error" not in result["quantum"] else 0
        neuromorphic_score = result["neuromorphic"].get("optimization_score", 0) if "error" not in result["neuromorphic"] else 0
        hybrid_score = result["hybrid"].get("fused_score", 0) if "error" not in result["hybrid"] else 0
        
        scores = {"quantum": quantum_score, "neuromorphic": neuromorphic_score, "hybrid": hybrid_score}
        best_optimizer = max(scores, key=scores.get)
        
        analysis["recommendations"].append({
            "problem_id": result["problem"]["id"],
            "best_optimizer": best_optimizer,
            "best_score": scores[best_optimizer],
            "all_scores": scores
        })
    
    print(f"✅ Comparative Demo Complete: {len(results)} problems analyzed")
    return {"results": results, "analysis": analysis}

# ===== MAIN DEMO CLASS =====

class OptimizationDemo:
    """Main demo class for optimization engine."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results = {}
        
        # Initialize components
        self.problem_generator = ProblemGenerator()
        self.optimization_engine = self._initialize_engine()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    def _initialize_engine(self) -> OptimizationEngine:
        """Initialize the optimization engine."""
        print("🔧 Initializing Optimization Engine...")
        
        # Create configurations
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
        
        # Create and return engine
        engine = create_optimization_engine(optimization_config, quantum_config, neuromorphic_config)
        print("✅ Optimization Engine initialized successfully")
        return engine
    
    def run_demo(self) -> Dict[str, Any]:
        """Run the complete optimization demo."""
        print("\n🚀 Starting Optimization Engine Demo...")
        print("="*60)
        
        try:
            # Run quantum demo
            self.results["quantum"] = run_quantum_demo(self.optimization_engine, self.problem_generator)
            
            # Run neuromorphic demo
            self.results["neuromorphic"] = run_neuromorphic_demo(self.optimization_engine, self.problem_generator)
            
            # Run hybrid demo
            self.results["hybrid"] = run_hybrid_demo(self.optimization_engine, self.problem_generator)
            
            # Run comparative demo
            self.results["comparative"] = run_comparative_demo(self.optimization_engine, self.problem_generator)
            
            # Get system status
            self.results["system_status"] = self.optimization_engine.get_system_status()
            
            # Generate summary
            self.results["summary"] = self._generate_summary()
            
            print("\n🎉 Optimization Engine Demo completed successfully!")
            return self.results
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            raise
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of demo results."""
        summary = {
            "total_optimizations": 0,
            "success_rates": {},
            "best_performers": {},
            "recommendations": []
        }
        
        # Collect data from each demo
        for demo_name, demo_result in self.results.items():
            if demo_name == "system_status" or demo_name == "summary":
                continue
                
            if "analysis" in demo_result:
                analysis = demo_result["analysis"]
                if "error" not in analysis:
                    summary["total_optimizations"] += analysis.get("total_problems", 0)
                    summary["success_rates"][demo_name] = analysis.get("success_rate", 0)
                    
                    # Track best performers
                    if demo_name == "quantum":
                        summary["best_performers"]["quantum_advantage"] = analysis.get("best_quantum_advantage", 1.0)
                    elif demo_name == "hybrid":
                        summary["best_performers"]["fused_score"] = analysis.get("best_fused_score", 0)
        
        # Add recommendations from comparative analysis
        if "comparative" in self.results:
            comparative = self.results["comparative"]
            if "analysis" in comparative and "recommendations" in comparative["analysis"]:
                summary["recommendations"] = comparative["analysis"]["recommendations"]
        
        return summary
    
    def print_summary(self):
        """Print demo summary."""
        if "summary" not in self.results:
            print("❌ No summary available")
            return
        
        summary = self.results["summary"]
        
        print("\n" + "="*60)
        print("📊 OPTIMIZATION ENGINE DEMO SUMMARY")
        print("="*60)
        
        print(f"🔢 Total Optimizations: {summary.get('total_optimizations', 0)}")
        
        print(f"\n📈 Success Rates:")
        for demo, rate in summary.get("success_rates", {}).items():
            print(f"   {demo.capitalize()}: {rate:.1%}")
        
        print(f"\n🏆 Best Performers:")
        for metric, value in summary.get("best_performers", {}).items():
            print(f"   {metric.replace('_', ' ').title()}: {value:.3f}")
        
        print(f"\n💡 Top Recommendations:")
        recommendations = summary.get("recommendations", [])
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. Problem {rec.get('problem_id', 'N/A')}: Use {rec.get('best_optimizer', 'N/A')} optimizer")
        
        print("="*60)
    
    def save_results(self, filename: str = "optimization_demo_results.json"):
        """Save demo results to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"💾 Demo results saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def cleanup(self):
        """Clean up demo resources."""
        try:
            # Get final statistics
            history = self.optimization_engine.get_optimization_history()
            metrics = self.optimization_engine.get_performance_metrics()
            
            print(f"\n🧹 Cleanup: {len(history)} optimizations performed")
            for optimizer, perf_metrics in metrics.items():
                print(f"   {optimizer}: {len(perf_metrics)} performance records")
            
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")

# ===== MAIN EXECUTION =====

def main():
    """Main demo execution."""
    demo = OptimizationDemo()
    
    try:
        # Run the demo
        demo.run_demo()
        
        # Print summary
        demo.print_summary()
        
        # Save results
        demo.save_results()
        
    except Exception as e:
        print(f"❌ Demo execution failed: {e}")
        raise
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
