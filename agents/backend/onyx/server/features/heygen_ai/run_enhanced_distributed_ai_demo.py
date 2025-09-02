import logging
import time
import json
import os
import tempfile
from pathlib import Path
import numpy as np
import asyncio

from core.advanced_distributed_ai_system import (
    AdvancedDistributedAISystem,
    DistributedAIConfig,
    AITaskType,
    NodeType,
    PrivacyLevel,
    CoordinationStrategy,
    QuantumBackend,
    create_enhanced_distributed_ai_config,
    create_quantum_enhanced_distributed_ai_system,
    create_neuromorphic_enhanced_distributed_ai_system,
    create_hybrid_quantum_neuromorphic_system,
    create_minimal_distributed_ai_config,
    create_maximum_distributed_ai_config
)

class EnhancedDistributedAIDemo:
    """Enhanced comprehensive demo showcasing Advanced Distributed AI System capabilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.enhanced_demo")
        self.demo_results = {}
        self.running = False
        
        # Initialize systems
        self.initialize_systems()
        self.create_test_data()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def initialize_systems(self):
        """Initialize Enhanced Distributed AI and supporting systems."""
        self.logger.info("🚀 Initializing Enhanced Advanced Distributed AI Systems...")
        
        # Create different system configurations
        self.standard_system = create_maximum_distributed_ai_config()
        self.quantum_system = create_quantum_enhanced_distributed_ai_system()
        self.neuromorphic_system = create_neuromorphic_enhanced_distributed_ai_system()
        self.hybrid_system = create_hybrid_quantum_neuromorphic_system()
        
        # Create temporary directory for test data
        self.test_dir = Path(tempfile.mkdtemp(prefix="enhanced_distributed_ai_demo_"))
        self.logger.info(f"Test directory created: {self.test_dir}")
    
    def create_test_data(self):
        """Create enhanced test data for demonstration."""
        self.logger.info("🔧 Creating enhanced test data...")
        
        # Enhanced test client models for federated learning
        self.test_client_models = {
            "quantum_client_001": {
                "model": {
                    "weights": np.random.rand(1000, 1000).astype(np.float32),
                    "architecture": "quantum_enhanced_transformer",
                    "layers": 12,
                    "quantum_features": ["quantum_attention", "quantum_embedding"]
                },
                "metadata": {
                    "client_id": "quantum_client_001",
                    "data_size": 15000,
                    "training_epochs": 8,
                    "quantum_qubits": 10
                },
                "performance": {
                    "accuracy": 0.92,
                    "loss": 0.08,
                    "f1_score": 0.90,
                    "quantum_advantage": 1.8
                }
            },
            "neuromorphic_client_001": {
                "model": {
                    "weights": np.random.rand(1000, 1000).astype(np.float32),
                    "architecture": "spiking_neural_network",
                    "layers": 8,
                    "neuromorphic_features": ["spiking_neurons", "plasticity", "adaptive_thresholds"]
                },
                "metadata": {
                    "client_id": "neuromorphic_client_001",
                    "data_size": 12000,
                    "training_epochs": 6,
                    "spiking_neurons": 5000
                },
                "performance": {
                    "accuracy": 0.89,
                    "loss": 0.11,
                    "f1_score": 0.87,
                    "plasticity_score": 0.85
                }
            },
            "hybrid_client_001": {
                "model": {
                    "weights": np.random.rand(1000, 1000).astype(np.float32),
                    "architecture": "quantum_neuromorphic_hybrid",
                    "layers": 15,
                    "hybrid_features": ["quantum_swarm", "neuromorphic_coordination", "emergent_intelligence"]
                },
                "metadata": {
                    "client_id": "hybrid_client_001",
                    "data_size": 20000,
                    "training_epochs": 10,
                    "quantum_qubits": 15,
                    "spiking_neurons": 8000
                },
                "performance": {
                    "accuracy": 0.95,
                    "loss": 0.05,
                    "f1_score": 0.93,
                    "hybrid_advantage": 2.5
                }
            }
        }
        
        # Enhanced test AI agents
        self.test_agents = {
            "quantum_agent_001": {
                "capabilities": ["quantum_optimization", "quantum_swarm", "quantum_encryption"],
                "location": "quantum_edge_server_1",
                "specialization": "quantum_ai",
                "quantum_qubits": 10,
                "performance_metrics": {"quantum_speed": 0.95, "quantum_accuracy": 0.92}
            },
            "neuromorphic_agent_001": {
                "capabilities": ["spiking_computation", "plasticity_learning", "adaptive_thresholds"],
                "location": "neuromorphic_edge_server_1",
                "specialization": "neuromorphic_ai",
                "spiking_neurons": 5000,
                "performance_metrics": {"neuromorphic_speed": 0.90, "neuromorphic_accuracy": 0.88}
            },
            "hybrid_agent_001": {
                "capabilities": ["quantum_neuromorphic_hybrid", "emergent_intelligence", "collective_consciousness"],
                "location": "hybrid_edge_server_1",
                "specialization": "hybrid_ai",
                "quantum_qubits": 15,
                "spiking_neurons": 8000,
                "performance_metrics": {"hybrid_speed": 0.98, "hybrid_accuracy": 0.95}
            }
        }
        
        # Enhanced test workloads
        self.test_workloads = [
            {
                "id": "quantum_optimization_workload",
                "type": "quantum_ai_optimization",
                "compute_intensity": "ultra_high",
                "latency_requirement_ms": 100,
                "data_size_mb": 500,
                "privacy_requirement": "quantum_encryption",
                "cost_budget": 50.0,
                "quantum_qubits_required": 15
            },
            {
                "id": "neuromorphic_learning_workload",
                "type": "neuromorphic_learning",
                "compute_intensity": "high",
                "latency_requirement_ms": 200,
                "data_size_mb": 300,
                "privacy_requirement": "post_quantum",
                "cost_budget": 30.0,
                "spiking_neurons_required": 10000
            },
            {
                "id": "hybrid_consciousness_workload",
                "type": "hybrid_consciousness_simulation",
                "compute_intensity": "extreme",
                "latency_requirement_ms": 500,
                "data_size_mb": 1000,
                "privacy_requirement": "quantum_encryption",
                "cost_budget": 100.0,
                "quantum_qubits_required": 20,
                "spiking_neurons_required": 15000
            }
        ]
        
        # Enhanced test coordination tasks
        self.test_coordination_tasks = [
            {
                "id": "quantum_swarm_coordination",
                "type": "quantum_swarm_intelligence",
                "required_capabilities": ["quantum_swarm", "quantum_optimization", "emergent_behavior"],
                "coordination_strategy": "quantum_swarm",
                "location": "quantum_edge_server_1",
                "priority": "critical",
                "quantum_qubits_required": 20
            },
            {
                "id": "neuromorphic_swarm_coordination",
                "type": "neuromorphic_swarm_intelligence",
                "required_capabilities": ["neuromorphic_swarm", "plasticity_learning", "adaptive_coordination"],
                "coordination_strategy": "neuromorphic_swarm",
                "location": "neuromorphic_edge_server_1",
                "priority": "high",
                "spiking_neurons_required": 12000
            },
            {
                "id": "hybrid_consciousness_coordination",
                "type": "hybrid_consciousness_simulation",
                "required_capabilities": ["hybrid_consciousness", "emergent_intelligence", "collective_consciousness"],
                "coordination_strategy": "emergent_intelligence",
                "location": "hybrid_edge_server_1",
                "priority": "critical",
                "quantum_qubits_required": 25,
                "spiking_neurons_required": 20000
            }
        ]
        
        self.logger.info("✅ Enhanced test data created successfully")
    
    def run_comprehensive_enhanced_demo(self):
        """Run comprehensive enhanced demonstration."""
        self.logger.info("🚀 Starting Comprehensive Enhanced Advanced Distributed AI Demo...")
        self.running = True
        
        try:
            # Run enhanced demos
            self.demo_results["system_comparison"] = self.run_system_comparison_demo()
            self.demo_results["quantum_ai_demo"] = self.run_quantum_ai_demo()
            self.demo_results["neuromorphic_computing_demo"] = self.run_neuromorphic_computing_demo()
            self.demo_results["hybrid_system_demo"] = self.run_hybrid_system_demo()
            self.demo_results["enhanced_privacy_demo"] = self.run_enhanced_privacy_demo()
            self.demo_results["advanced_swarm_intelligence_demo"] = self.run_advanced_swarm_intelligence_demo()
            self.demo_results["performance_benchmarks"] = self.run_performance_benchmarks()
            
            self.logger.info("🎉 Comprehensive enhanced demo completed successfully!")
            return self.demo_results
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced demo failed: {e}")
            raise
        finally:
            self.running = False
    
    def run_system_comparison_demo(self) -> Dict[str, Any]:
        """Demo comparing different system configurations."""
        self.logger.info("🔍 Running System Comparison Demo...")
        
        try:
            results = {}
            
            # Compare system capabilities
            systems = {
                "standard": self.standard_system,
                "quantum": self.quantum_system,
                "neuromorphic": self.neuromorphic_system,
                "hybrid": self.hybrid_system
            }
            
            for system_name, system in systems.items():
                system_status = system.get_system_status()
                results[system_name] = {
                    "system_name": system_name,
                    "status": system_status.get("system_status", "unknown"),
                    "capabilities": self._extract_system_capabilities(system_status),
                    "performance_metrics": self._extract_performance_metrics(system_status)
                }
            
            # Analyze system differences
            capability_comparison = self._compare_system_capabilities(results)
            performance_comparison = self._compare_system_performance(results)
            
            return {
                "system_results": results,
                "capability_comparison": capability_comparison,
                "performance_comparison": performance_comparison
            }
            
        except Exception as e:
            self.logger.error(f"❌ System Comparison Demo failed: {e}")
            return {"error": str(e)}
    
    def run_quantum_ai_demo(self) -> Dict[str, Any]:
        """Demo quantum AI capabilities."""
        self.logger.info("🔮 Running Quantum AI Demo...")
        
        try:
            results = {}
            
            # Test quantum circuit creation
            quantum_circuit = self.quantum_system.create_quantum_circuit("demo_circuit", 10)
            results["quantum_circuit_creation"] = quantum_circuit
            
            # Test quantum optimization
            optimization_problems = [
                {
                    "type": "quantum_machine_learning",
                    "complexity": 5,
                    "quantum_advantage": True
                },
                {
                    "type": "quantum_optimization",
                    "complexity": 8,
                    "quantum_advantage": True
                }
            ]
            
            optimization_results = []
            for problem in optimization_problems:
                result = self.quantum_system.execute_quantum_optimization(problem)
                optimization_results.append(result)
            
            results["quantum_optimization"] = optimization_results
            
            # Test quantum-enhanced federated learning
            quantum_federated_result = self.quantum_system.start_federated_round(
                self.test_client_models, PrivacyLevel.QUANTUM_ENCRYPTION
            )
            results["quantum_federated_learning"] = quantum_federated_result
            
            # Get quantum statistics
            quantum_stats = self.quantum_system.get_system_status().get("quantum_stats", {})
            results["quantum_statistics"] = quantum_stats
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Quantum AI Demo failed: {e}")
            return {"error": str(e)}
    
    def run_neuromorphic_computing_demo(self) -> Dict[str, Any]:
        """Demo neuromorphic computing capabilities."""
        self.logger.info("🧠 Running Neuromorphic Computing Demo...")
        
        try:
            results = {}
            
            # Test spiking network creation
            spiking_network = self.neuromorphic_system.create_spiking_network("demo_network", 1000)
            results["spiking_network_creation"] = spiking_network
            
            # Test spiking computation
            input_spikes = [
                {"target_neuron": 0, "strength": 0.8},
                {"target_neuron": 1, "strength": 0.6},
                {"target_neuron": 2, "strength": 0.9}
            ]
            
            spiking_result = self.neuromorphic_system.execute_spiking_computation("demo_network", input_spikes)
            results["spiking_computation"] = spiking_result
            
            # Test neuromorphic-enhanced coordination
            neuromorphic_coordination = self.neuromorphic_system.coordinate_agents(
                self.test_coordination_tasks[1], CoordinationStrategy.NEUROMORPHIC_SWARM
            )
            results["neuromorphic_coordination"] = neuromorphic_coordination
            
            # Get neuromorphic statistics
            neuromorphic_stats = self.neuromorphic_system.get_system_status().get("neuromorphic_stats", {})
            results["neuromorphic_statistics"] = neuromorphic_stats
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Neuromorphic Computing Demo failed: {e}")
            return {"error": str(e)}
    
    def run_hybrid_system_demo(self) -> Dict[str, Any]:
        """Demo hybrid quantum-neuromorphic system capabilities."""
        self.logger.info("🌟 Running Hybrid System Demo...")
        
        try:
            results = {}
            
            # Test hybrid system capabilities
            hybrid_status = self.hybrid_system.get_system_status()
            results["hybrid_system_status"] = hybrid_status
            
            # Test hybrid coordination
            hybrid_coordination = self.hybrid_system.coordinate_agents(
                self.test_coordination_tasks[2], CoordinationStrategy.EMERGENT_INTELLIGENCE
            )
            results["hybrid_coordination"] = hybrid_coordination
            
            # Test hybrid workload orchestration
            hybrid_workload = self.hybrid_system.orchestrate_workload(self.test_workloads[2])
            results["hybrid_workload_orchestration"] = hybrid_workload
            
            # Test hybrid privacy protection
            hybrid_privacy = self.hybrid_system.apply_enhanced_privacy(
                {"sensitive_data": "hybrid_test_data"}, PrivacyLevel.QUANTUM_ENCRYPTION, "hybrid_client"
            )
            results["hybrid_privacy_protection"] = hybrid_privacy
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Hybrid System Demo failed: {e}")
            return {"error": str(e)}
    
    def run_enhanced_privacy_demo(self) -> Dict[str, Any]:
        """Demo enhanced privacy protection capabilities."""
        self.logger.info("🔒 Running Enhanced Privacy Protection Demo...")
        
        try:
            results = {}
            
            # Test different privacy levels
            privacy_levels = [
                PrivacyLevel.DIFFERENTIAL,
                PrivacyLevel.HOMOMORPHIC,
                PrivacyLevel.QUANTUM_ENCRYPTION,
                PrivacyLevel.POST_QUANTUM
            ]
            
            test_data = {"sensitive_info": "test_sensitive_data", "metadata": "test_metadata"}
            
            privacy_results = {}
            for privacy_level in privacy_levels:
                privacy_result = self.hybrid_system.apply_enhanced_privacy(
                    test_data, privacy_level, f"privacy_test_client_{privacy_level.value}"
                )
                privacy_results[privacy_level.value] = privacy_result
            
            results["privacy_level_testing"] = privacy_results
            
            # Test privacy budget management
            privacy_stats = self.hybrid_system.get_system_status().get("privacy_stats", {})
            results["privacy_statistics"] = privacy_stats
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced Privacy Demo failed: {e}")
            return {"error": str(e)}
    
    def run_advanced_swarm_intelligence_demo(self) -> Dict[str, Any]:
        """Demo advanced swarm intelligence capabilities."""
        self.logger.info("🐝 Running Advanced Swarm Intelligence Demo...")
        
        try:
            results = {}
            
            # Test different swarm types
            swarm_types = ["standard", "quantum_swarm", "neuromorphic_swarm"]
            
            swarm_results = {}
            for swarm_type in swarm_types:
                # Create test collective
                collective_id = f"demo_collective_{swarm_type}"
                agent_ids = [f"agent_{i}" for i in range(5)]
                
                if swarm_type == "quantum_swarm":
                    system = self.quantum_system
                elif swarm_type == "neuromorphic_swarm":
                    system = self.neuromorphic_system
                else:
                    system = self.hybrid_system
                
                # Test swarm coordination
                swarm_task = {
                    "id": f"swarm_task_{swarm_type}",
                    "type": "collective_intelligence",
                    "complexity": "high"
                }
                
                swarm_result = system.coordinate_agents(swarm_task)
                swarm_results[swarm_type] = swarm_result
            
            results["swarm_intelligence_testing"] = swarm_results
            
            # Get swarm statistics
            swarm_stats = self.hybrid_system.get_system_status().get("swarm_stats", {})
            results["swarm_statistics"] = swarm_stats
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Advanced Swarm Intelligence Demo failed: {e}")
            return {"error": str(e)}
    
    def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmarks."""
        self.logger.info("📊 Running Performance Benchmarks...")
        
        try:
            results = {}
            
            # Benchmark different systems
            systems = {
                "standard": self.standard_system,
                "quantum": self.quantum_system,
                "neuromorphic": self.neuromorphic_system,
                "hybrid": self.hybrid_system
            }
            
            benchmark_results = {}
            for system_name, system in systems.items():
                start_time = time.time()
                
                # Benchmark federated learning
                federated_start = time.time()
                federated_result = system.start_federated_round(self.test_client_models)
                federated_time = time.time() - federated_start
                
                # Benchmark coordination
                coordination_start = time.time()
                coordination_result = system.coordinate_agents(self.test_coordination_tasks[0])
                coordination_time = time.time() - coordination_start
                
                # Benchmark workload orchestration
                orchestration_start = time.time()
                orchestration_result = system.orchestrate_workload(self.test_workloads[0])
                orchestration_time = time.time() - orchestration_start
                
                total_time = time.time() - start_time
                
                benchmark_results[system_name] = {
                    "federated_learning_time": federated_time,
                    "coordination_time": coordination_time,
                    "orchestration_time": orchestration_time,
                    "total_benchmark_time": total_time,
                    "performance_score": self._calculate_performance_score(
                        federated_time, coordination_time, orchestration_time
                    )
                }
            
            results["system_benchmarks"] = benchmark_results
            
            # Performance analysis
            performance_analysis = self._analyze_performance_benchmarks(benchmark_results)
            results["performance_analysis"] = performance_analysis
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Performance Benchmarks failed: {e}")
            return {"error": str(e)}
    
    def _extract_system_capabilities(self, system_status: Dict[str, Any]) -> Dict[str, Any]:
        """Extract system capabilities from status."""
        capabilities = {}
        
        # Check quantum capabilities
        if "quantum_stats" in system_status:
            capabilities["quantum_ai"] = True
            capabilities["quantum_qubits"] = system_status["quantum_stats"].get("quantum_qubits", 0)
        else:
            capabilities["quantum_ai"] = False
        
        # Check neuromorphic capabilities
        if "neuromorphic_stats" in system_status:
            capabilities["neuromorphic_computing"] = True
            capabilities["spiking_neurons"] = system_status["neuromorphic_stats"].get("total_neurons", 0)
        else:
            capabilities["neuromorphic_computing"] = False
        
        # Check privacy capabilities
        if "privacy_stats" in system_status:
            capabilities["enhanced_privacy"] = True
            capabilities["privacy_mechanisms"] = system_status["privacy_stats"].get("active_privacy_mechanisms", {})
        else:
            capabilities["enhanced_privacy"] = False
        
        return capabilities
    
    def _extract_performance_metrics(self, system_status: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics from status."""
        metrics = {}
        
        # Extract key metrics
        metrics["total_operations"] = system_status.get("system_stats", {}).get("total_operations", 0)
        metrics["federated_rounds"] = system_status.get("federated_stats", {}).get("current_round", 0)
        metrics["registered_agents"] = system_status.get("coordination_stats", {}).get("registered_agents", 0)
        metrics["edge_nodes"] = system_status.get("orchestration_stats", {}).get("edge_nodes", 0)
        
        return metrics
    
    def _compare_system_capabilities(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare capabilities across different systems."""
        comparison = {}
        
        # Compare quantum capabilities
        quantum_systems = [name for name, result in results.items() 
                          if result["capabilities"].get("quantum_ai", False)]
        comparison["quantum_capable_systems"] = quantum_systems
        
        # Compare neuromorphic capabilities
        neuromorphic_systems = [name for name, result in results.items() 
                               if result["capabilities"].get("neuromorphic_computing", False)]
        comparison["neuromorphic_capable_systems"] = neuromorphic_systems
        
        # Compare privacy capabilities
        privacy_systems = [name for name, result in results.items() 
                          if result["capabilities"].get("enhanced_privacy", False)]
        comparison["enhanced_privacy_systems"] = privacy_systems
        
        return comparison
    
    def _compare_system_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare performance across different systems."""
        comparison = {}
        
        # Find best performing system in each category
        best_federated = min(results.items(), key=lambda x: x[1]["performance_metrics"].get("federated_rounds", 0))
        best_coordination = max(results.items(), key=lambda x: x[1]["performance_metrics"].get("registered_agents", 0))
        best_orchestration = max(results.items(), key=lambda x: x[1]["performance_metrics"].get("edge_nodes", 0))
        
        comparison["best_federated_learning"] = best_federated[0]
        comparison["best_coordination"] = best_coordination[0]
        comparison["best_orchestration"] = best_orchestration[0]
        
        return comparison
    
    def _calculate_performance_score(self, federated_time: float, coordination_time: float, 
                                   orchestration_time: float) -> float:
        """Calculate overall performance score."""
        # Normalize times (lower is better)
        max_time = max(federated_time, coordination_time, orchestration_time)
        if max_time == 0:
            return 100.0
        
        normalized_federated = (1 - federated_time / max_time) * 100
        normalized_coordination = (1 - coordination_time / max_time) * 100
        normalized_orchestration = (1 - orchestration_time / max_time) * 100
        
        # Weighted average
        return (normalized_federated * 0.4 + normalized_coordination * 0.3 + normalized_orchestration * 0.3)
    
    def _analyze_performance_benchmarks(self, benchmark_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance benchmark results."""
        analysis = {}
        
        # Find fastest system
        fastest_system = min(benchmark_results.items(), 
                           key=lambda x: x[1]["total_benchmark_time"])
        analysis["fastest_system"] = fastest_system[0]
        analysis["fastest_time"] = fastest_system[1]["total_benchmark_time"]
        
        # Find highest performing system
        highest_performing = max(benchmark_results.items(), 
                               key=lambda x: x[1]["performance_score"])
        analysis["highest_performing_system"] = highest_performing[0]
        analysis["highest_score"] = highest_performing[1]["performance_score"]
        
        # Calculate average performance
        total_score = sum(result["performance_score"] for result in benchmark_results.values())
        analysis["average_performance_score"] = total_score / len(benchmark_results)
        
        return analysis
    
    def save_demo_results(self, output_path: str = "enhanced_distributed_ai_demo_results.json"):
        """Save enhanced demo results to file."""
        try:
            with open(output_path, 'w') as f:
                json.dump(self.demo_results, f, indent=2)
            self.logger.info(f"Enhanced demo results saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save enhanced demo results: {e}")
    
    def cleanup(self):
        """Clean up temporary files and resources."""
        try:
            # Shutdown all systems gracefully
            systems = [self.standard_system, self.quantum_system, 
                      self.neuromorphic_system, self.hybrid_system]
            
            for system in systems:
                if hasattr(system, 'shutdown'):
                    system.shutdown()
            
            # Remove test directory
            import shutil
            if hasattr(self, 'test_dir') and self.test_dir.exists():
                shutil.rmtree(self.test_dir)
            
            self.logger.info("Enhanced demo cleanup completed")
        except Exception as e:
            self.logger.error(f"Enhanced demo cleanup failed: {e}")

def main():
    """Main enhanced demo execution."""
    demo = EnhancedDistributedAIDemo()
    
    try:
        # Run comprehensive enhanced demo
        results = demo.run_comprehensive_enhanced_demo()
        
        # Save results
        demo.save_demo_results()
        
        # Print enhanced summary
        print("\n" + "="*80)
        print("🎉 ENHANCED ADVANCED DISTRIBUTED AI SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        # System comparison summary
        if "system_comparison" in results:
            comparison = results["system_comparison"]
            print(f"🔍 System Comparison: {len(comparison.get('system_results', {}))} systems analyzed")
            
            if "capability_comparison" in comparison:
                caps = comparison["capability_comparison"]
                print(f"🔮 Quantum AI Systems: {len(caps.get('quantum_capable_systems', []))}")
                print(f"🧠 Neuromorphic Systems: {len(caps.get('neuromorphic_capable_systems', []))}")
                print(f"🔒 Enhanced Privacy Systems: {len(caps.get('enhanced_privacy_systems', []))}")
        
        # Performance summary
        if "performance_benchmarks" in results:
            perf = results["performance_benchmarks"]
            if "performance_analysis" in perf:
                analysis = perf["performance_analysis"]
                print(f"⚡ Fastest System: {analysis.get('fastest_system', 'N/A')}")
                print(f"🏆 Highest Performing: {analysis.get('highest_performing_system', 'N/A')}")
                print(f"📊 Average Performance: {analysis.get('average_performance_score', 0):.1f}")
        
        print("="*80)
        
    except Exception as e:
        print(f"❌ Enhanced demo failed: {e}")
        raise
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
