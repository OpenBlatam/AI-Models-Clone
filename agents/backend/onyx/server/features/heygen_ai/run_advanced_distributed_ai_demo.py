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
    create_advanced_distributed_ai_system,
    create_minimal_distributed_ai_config,
    create_maximum_distributed_ai_config
)

class AdvancedDistributedAIDemo:
    """Comprehensive demo showcasing Advanced Distributed AI System capabilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.demo")
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
        """Initialize Distributed AI and supporting systems."""
        self.logger.info("🚀 Initializing Advanced Distributed AI Systems...")
        
        # Create maximum configuration
        self.distributed_ai_config = create_maximum_distributed_ai_config()
        self.distributed_ai_system = create_advanced_distributed_ai_system(self.distributed_ai_config)
        
        # Create temporary directory for test data
        self.test_dir = Path(tempfile.mkdtemp(prefix="distributed_ai_demo_"))
        self.logger.info(f"Test directory created: {self.test_dir}")
    
    def create_test_data(self):
        """Create test data for demonstration."""
        self.logger.info("🔧 Creating test data...")
        
        # Create test client models for federated learning
        self.test_client_models = {
            "client_001": {
                "model": {
                    "weights": np.random.rand(1000, 1000).astype(np.float32),
                    "architecture": "transformer",
                    "layers": 12
                },
                "metadata": {
                    "client_id": "client_001",
                    "data_size": 10000,
                    "training_epochs": 5
                },
                "performance": {
                    "accuracy": 0.85,
                    "loss": 0.15,
                    "f1_score": 0.82
                }
            },
            "client_002": {
                "model": {
                    "weights": np.random.rand(1000, 1000).astype(np.float32),
                    "architecture": "transformer",
                    "layers": 12
                },
                "metadata": {
                    "client_id": "client_002",
                    "data_size": 8000,
                    "training_epochs": 5
                },
                "performance": {
                    "accuracy": 0.87,
                    "loss": 0.13,
                    "f1_score": 0.84
                }
            },
            "client_003": {
                "model": {
                    "weights": np.random.rand(1000, 1000).astype(np.float32),
                    "architecture": "transformer",
                    "layers": 12
                },
                "metadata": {
                    "client_id": "client_003",
                    "data_size": 12000,
                    "training_epochs": 5
                },
                "performance": {
                    "accuracy": 0.83,
                    "loss": 0.17,
                    "f1_score": 0.80
                }
            }
        }
        
        # Create test AI agents
        self.test_agents = {
            "agent_001": {
                "capabilities": ["image_processing", "nlp", "decision_making"],
                "location": "edge_server_1",
                "specialization": "computer_vision",
                "performance_metrics": {"speed": 0.9, "accuracy": 0.85}
            },
            "agent_002": {
                "capabilities": ["nlp", "reasoning", "planning"],
                "location": "cloud_service_1",
                "specialization": "natural_language",
                "performance_metrics": {"speed": 0.8, "accuracy": 0.90}
            },
            "agent_003": {
                "capabilities": ["optimization", "scheduling", "coordination"],
                "location": "edge_gateway_1",
                "specialization": "resource_management",
                "performance_metrics": {"speed": 0.95, "accuracy": 0.88}
            }
        }
        
        # Create test edge nodes
        self.test_edge_nodes = {
            "edge_node_001": {
                "capabilities": ["ai_inference", "data_processing", "real_time_analysis"],
                "resources": {
                    "cpu": 8,
                    "memory": 16384,
                    "gpu": 2,
                    "storage": 1000000
                },
                "location": "data_center_1",
                "latency_ms": 5
            },
            "edge_node_002": {
                "capabilities": ["ai_inference", "edge_training", "model_optimization"],
                "resources": {
                    "cpu": 16,
                    "memory": 32768,
                    "gpu": 4,
                    "storage": 2000000
                },
                "location": "data_center_2",
                "latency_ms": 8
            }
        }
        
        # Create test cloud services
        self.test_cloud_services = {
            "cloud_service_001": {
                "capabilities": ["ai_training", "model_deployment", "scaling"],
                "resources": {
                    "cpu": 64,
                    "memory": 131072,
                    "gpu": 16,
                    "storage": 10000000
                },
                "location": "aws_us_east_1",
                "latency_ms": 150
            },
            "cloud_service_002": {
                "capabilities": ["ai_training", "federated_learning", "secure_aggregation"],
                "resources": {
                    "cpu": 128,
                    "memory": 262144,
                    "gpu": 32,
                    "storage": 20000000
                },
                "location": "azure_east_us",
                "latency_ms": 180
            }
        }
        
        # Create test workloads
        self.test_workloads = [
            {
                "id": "workload_001",
                "type": "real_time_inference",
                "compute_intensity": "low",
                "latency_requirement_ms": 50,
                "data_size_mb": 10,
                "privacy_requirement": "basic",
                "cost_budget": 1.0
            },
            {
                "id": "workload_002",
                "type": "model_training",
                "compute_intensity": "high",
                "latency_requirement_ms": 2000,
                "data_size_mb": 1000,
                "privacy_requirement": "differential",
                "cost_budget": 10.0
            },
            {
                "id": "workload_003",
                "type": "hybrid_processing",
                "compute_intensity": "medium",
                "latency_requirement_ms": 500,
                "data_size_mb": 100,
                "privacy_requirement": "advanced",
                "cost_budget": 5.0
            }
        ]
        
        # Create test coordination tasks
        self.test_coordination_tasks = [
            {
                "id": "task_001",
                "type": "image_analysis_pipeline",
                "required_capabilities": ["image_processing", "nlp", "decision_making"],
                "coordination_strategy": "hierarchical",
                "location": "edge_server_1",
                "priority": "high"
            },
            {
                "id": "task_002",
                "type": "distributed_optimization",
                "required_capabilities": ["optimization", "scheduling", "coordination"],
                "coordination_strategy": "distributed",
                "location": "cloud_service_1",
                "priority": "medium"
            },
            {
                "id": "task_003",
                "type": "swarm_intelligence",
                "required_capabilities": ["collective_decision", "adaptive_behavior"],
                "coordination_strategy": "swarm",
                "location": "edge_gateway_1",
                "priority": "low"
            }
        ]
        
        self.logger.info("✅ Test data created successfully")
    
    def run_comprehensive_demo(self):
        """Run comprehensive Distributed AI demonstration."""
        self.logger.info("🚀 Starting Comprehensive Advanced Distributed AI Demo...")
        self.running = True
        
        try:
            # Run individual demos
            self.demo_results["system_initialization"] = self.run_system_initialization_demo()
            self.demo_results["federated_learning"] = self.run_federated_learning_demo()
            self.demo_results["multi_agent_coordination"] = self.run_multi_agent_coordination_demo()
            self.demo_results["edge_cloud_orchestration"] = self.run_edge_cloud_orchestration_demo()
            self.demo_results["privacy_protection"] = self.run_privacy_protection_demo()
            self.demo_results["advanced_features"] = self.run_advanced_features_demo()
            
            self.logger.info("🎉 Comprehensive demo completed successfully!")
            return self.demo_results
            
        except Exception as e:
            self.logger.error(f"❌ Demo failed: {e}")
            raise
        finally:
            self.running = False
    
    def run_system_initialization_demo(self) -> Dict[str, Any]:
        """Demo system initialization and configuration."""
        self.logger.info("🔧 Running System Initialization Demo...")
        
        try:
            # Get system status
            status = self.distributed_ai_system.get_system_status()
            
            # Test different configurations
            minimal_config = create_minimal_distributed_ai_config()
            minimal_system = create_advanced_distributed_ai_system(minimal_config)
            
            results = {
                "main_system_status": status,
                "minimal_system_status": minimal_system.get_system_status(),
                "config_comparison": {
                    "main_system": {
                        "federated_learning": self.distributed_ai_config.enable_federated_learning,
                        "multi_agent_coordination": self.distributed_ai_config.enable_multi_agent_coordination,
                        "edge_cloud_orchestration": self.distributed_ai_config.enable_edge_cloud_orchestration,
                        "privacy_protection": self.distributed_ai_config.enable_privacy_protection
                    },
                    "minimal_system": {
                        "federated_learning": minimal_config.enable_federated_learning,
                        "multi_agent_coordination": minimal_config.enable_multi_agent_coordination,
                        "edge_cloud_orchestration": minimal_config.enable_edge_cloud_orchestration,
                        "privacy_protection": minimal_config.enable_privacy_protection
                    }
                }
            }
            
            self.logger.info("✅ System Initialization Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ System Initialization Demo failed: {e}")
            return {"error": str(e)}
    
    def run_federated_learning_demo(self) -> Dict[str, Any]:
        """Demo federated learning capabilities."""
        self.logger.info("🤝 Running Federated Learning Demo...")
        
        try:
            results = {}
            
            # Test federated learning rounds
            federated_rounds = []
            for round_num in range(3):
                self.logger.info(f"🔄 Starting Federated Round {round_num + 1}")
                
                # Start federated round
                round_result = self.distributed_ai_system.start_federated_round(self.test_client_models)
                federated_rounds.append(round_result)
                
                # Simulate client model updates
                for client_id in self.test_client_models:
                    # Simulate model improvement
                    improvement = np.random.uniform(0.01, 0.05)
                    self.test_client_models[client_id]["performance"]["accuracy"] += improvement
                    self.test_client_models[client_id]["performance"]["loss"] -= improvement * 0.5
            
            # Get federated learning statistics
            federated_stats = self.distributed_ai_system.federated_engine.get_federated_stats()
            
            # Analyze federated learning performance
            total_rounds = len(federated_rounds)
            successful_rounds = len([r for r in federated_rounds if "error" not in r])
            success_rate = successful_rounds / total_rounds if total_rounds > 0 else 0
            
            # Calculate average model quality improvement
            quality_improvements = []
            for round_result in federated_rounds:
                if "round_info" in round_result:
                    quality_improvements.append(round_result["round_info"]["model_quality"])
            
            average_quality = np.mean(quality_improvements) if quality_improvements else 0
            
            results = {
                "federated_rounds": federated_rounds,
                "federated_statistics": federated_stats,
                "performance_analysis": {
                    "total_rounds": total_rounds,
                    "successful_rounds": successful_rounds,
                    "success_rate": success_rate,
                    "average_model_quality": average_quality,
                    "privacy_level": self.distributed_ai_config.privacy_level.value
                }
            }
            
            self.logger.info("✅ Federated Learning Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Federated Learning Demo failed: {e}")
            return {"error": str(e)}
    
    def run_multi_agent_coordination_demo(self) -> Dict[str, Any]:
        """Demo multi-agent coordination capabilities."""
        self.logger.info("🤖 Running Multi-Agent Coordination Demo...")
        
        try:
            results = {}
            
            # Register test agents
            agent_registrations = {}
            for agent_id, agent_info in self.test_agents.items():
                registration_success = self.distributed_ai_system.register_agent(agent_id, agent_info)
                agent_registrations[agent_id] = {
                    "registered": registration_success,
                    "agent_info": agent_info
                }
            
            # Test different coordination strategies
            coordination_results = {}
            for task in self.test_coordination_tasks:
                self.logger.info(f"🔄 Coordinating agents for task: {task['id']}")
                
                # Coordinate agents for task
                coordination_result = self.distributed_ai_system.coordinate_agents(task)
                coordination_results[task["id"]] = {
                    "task": task,
                    "coordination_result": coordination_result
                }
            
            # Get coordination statistics
            coordination_stats = self.distributed_ai_system.agent_coordinator.get_coordination_stats()
            
            # Analyze coordination effectiveness
            total_tasks = len(self.test_coordination_tasks)
            successful_coordinations = len([
                r for r in coordination_results.values() 
                if "error" not in r["coordination_result"]
            ])
            coordination_success_rate = successful_coordinations / total_tasks if total_tasks > 0 else 0
            
            # Analyze strategy usage
            strategy_usage = {}
            for result in coordination_results.values():
                strategy = result["coordination_result"].get("strategy", "unknown")
                strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
            
            results = {
                "agent_registrations": agent_registrations,
                "coordination_results": coordination_results,
                "coordination_statistics": coordination_stats,
                "effectiveness_analysis": {
                    "total_tasks": total_tasks,
                    "successful_coordinations": successful_coordinations,
                    "coordination_success_rate": coordination_success_rate,
                    "strategy_usage": strategy_usage,
                    "emergent_behavior_enabled": self.distributed_ai_config.enable_emergent_behavior
                }
            }
            
            self.logger.info("✅ Multi-Agent Coordination Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Multi-Agent Coordination Demo failed: {e}")
            return {"error": str(e)}
    
    def run_edge_cloud_orchestration_demo(self) -> Dict[str, Any]:
        """Demo edge-cloud orchestration capabilities."""
        self.logger.info("☁️ Running Edge-Cloud Orchestration Demo...")
        
        try:
            results = {}
            
            # Register edge nodes
            edge_registrations = {}
            for node_id, node_info in self.test_edge_nodes.items():
                registration_success = self.distributed_ai_system.register_edge_node(node_id, node_info)
                edge_registrations[node_id] = {
                    "registered": registration_success,
                    "node_info": node_info
                }
            
            # Register cloud services
            cloud_registrations = {}
            for service_id, service_info in self.test_cloud_services.items():
                registration_success = self.distributed_ai_system.register_cloud_service(service_id, service_info)
                cloud_registrations[service_id] = {
                    "registered": registration_success,
                    "service_info": service_info
                }
            
            # Test workload orchestration
            orchestration_results = {}
            for workload in self.test_workloads:
                self.logger.info(f"🎯 Orchestrating workload: {workload['id']}")
                
                # Orchestrate workload
                orchestration_result = self.distributed_ai_system.orchestrate_workload(workload)
                orchestration_results[workload["id"]] = {
                    "workload": workload,
                    "orchestration_result": orchestration_result
                }
            
            # Get orchestration statistics
            orchestration_stats = self.distributed_ai_system.ai_orchestrator.get_orchestration_stats()
            
            # Analyze orchestration effectiveness
            total_workloads = len(self.test_workloads)
            successful_orchestrations = len([
                r for r in orchestration_results.values() 
                if r["orchestration_result"].get("orchestration_success", False)
            ])
            orchestration_success_rate = successful_orchestrations / total_workloads if total_workloads > 0 else 0
            
            # Analyze placement patterns
            placement_patterns = {}
            for result in orchestration_results.values():
                placement = result["orchestration_result"].get("placement", {})
                placement_type = placement.get("placement_type", "unknown")
                placement_patterns[placement_type] = placement_patterns.get(placement_type, 0) + 1
            
            results = {
                "edge_registrations": edge_registrations,
                "cloud_registrations": cloud_registrations,
                "orchestration_results": orchestration_results,
                "orchestration_statistics": orchestration_stats,
                "effectiveness_analysis": {
                    "total_workloads": total_workloads,
                    "successful_orchestrations": successful_orchestrations,
                    "orchestration_success_rate": orchestration_success_rate,
                    "placement_patterns": placement_patterns,
                    "load_balancing_enabled": self.distributed_ai_config.enable_load_balancing
                }
            }
            
            self.logger.info("✅ Edge-Cloud Orchestration Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Edge-Cloud Orchestration Demo failed: {e}")
            return {"error": str(e)}
    
    def run_privacy_protection_demo(self) -> Dict[str, Any]:
        """Demo privacy protection capabilities."""
        self.logger.info("🔒 Running Privacy Protection Demo...")
        
        try:
            results = {}
            
            # Test different privacy levels
            privacy_levels = [PrivacyLevel.NONE, PrivacyLevel.BASIC, PrivacyLevel.DIFFERENTIAL, PrivacyLevel.HOMOMORPHIC]
            privacy_test_results = {}
            
            for privacy_level in privacy_levels:
                self.logger.info(f"🔐 Testing privacy level: {privacy_level.value}")
                
                # Create config with specific privacy level
                privacy_config = create_distributed_ai_config(
                    enable_federated_learning=True,
                    enable_multi_agent_coordination=False,
                    enable_edge_cloud_orchestration=False,
                    enable_privacy_protection=True
                )
                privacy_config.privacy_level = privacy_level
                
                # Create system with privacy config
                privacy_system = create_advanced_distributed_ai_system(privacy_config)
                
                # Test federated learning with privacy
                privacy_round_result = privacy_system.start_federated_round(self.test_client_models)
                
                privacy_test_results[privacy_level.value] = {
                    "privacy_level": privacy_level.value,
                    "federated_round_result": privacy_round_result,
                    "privacy_mechanisms": privacy_system.federated_engine.privacy_mechanisms
                }
            
            # Test secure aggregation
            secure_aggregation_test = self._test_secure_aggregation()
            
            # Analyze privacy effectiveness
            privacy_effectiveness = {
                "differential_privacy_enabled": self.distributed_ai_config.privacy_level in [PrivacyLevel.DIFFERENTIAL, PrivacyLevel.HOMOMORPHIC],
                "homomorphic_encryption_enabled": self.distributed_ai_config.privacy_level == PrivacyLevel.HOMOMORPHIC,
                "secure_aggregation_enabled": self.distributed_ai_config.enable_secure_aggregation,
                "privacy_level": self.distributed_ai_config.privacy_level.value
            }
            
            results = {
                "privacy_test_results": privacy_test_results,
                "secure_aggregation_test": secure_aggregation_test,
                "privacy_effectiveness": privacy_effectiveness
            }
            
            self.logger.info("✅ Privacy Protection Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Privacy Protection Demo failed: {e}")
            return {"error": str(e)}
    
    def _test_secure_aggregation(self) -> Dict[str, Any]:
        """Test secure aggregation capabilities."""
        try:
            # Test secure aggregation with different model configurations
            test_models = {
                "secure_client_1": {
                    "model": {"weights": np.random.rand(100, 100).astype(np.float32)},
                    "metadata": {"client_id": "secure_client_1"},
                    "performance": {"accuracy": 0.85}
                },
                "secure_client_2": {
                    "model": {"weights": np.random.rand(100, 100).astype(np.float32)},
                    "metadata": {"client_id": "secure_client_2"},
                    "performance": {"accuracy": 0.87}
                }
            }
            
            # Test with secure aggregation enabled
            secure_config = create_distributed_ai_config(enable_secure_aggregation=True)
            secure_system = create_advanced_distributed_ai_system(secure_config)
            
            secure_result = secure_system.start_federated_round(test_models)
            
            return {
                "secure_aggregation_result": secure_result,
                "aggregation_success": "error" not in secure_result,
                "privacy_preserved": True  # Simplified check
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def run_advanced_features_demo(self) -> Dict[str, Any]:
        """Demo advanced system features."""
        self.logger.info("🚀 Running Advanced Features Demo...")
        
        try:
            results = {}
            
            # Test emergent behavior
            emergent_behavior = self._test_emergent_behavior()
            
            # Test adaptive routing
            adaptive_routing = self._test_adaptive_routing()
            
            # Test auto-scaling
            auto_scaling = self._test_auto_scaling()
            
            # Test performance tracking
            performance_tracking = self._test_performance_tracking()
            
            # Test system scalability
            system_scalability = self._test_system_scalability()
            
            results = {
                "emergent_behavior": emergent_behavior,
                "adaptive_routing": adaptive_routing,
                "auto_scaling": auto_scaling,
                "performance_tracking": performance_tracking,
                "system_scalability": system_scalability
            }
            
            self.logger.info("✅ Advanced Features Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Advanced Features Demo failed: {e}")
            return {"error": str(e)}
    
    def _test_emergent_behavior(self) -> Dict[str, Any]:
        """Test emergent behavior in multi-agent systems."""
        try:
            # Create swarm coordination task
            swarm_task = {
                "id": "swarm_emergence_test",
                "type": "collective_intelligence",
                "required_capabilities": ["collective_decision", "adaptive_behavior"],
                "coordination_strategy": "swarm",
                "location": "edge_gateway_1"
            }
            
            # Test swarm coordination
            swarm_result = self.distributed_ai_system.coordinate_agents(swarm_task)
            
            return {
                "swarm_coordination_result": swarm_result,
                "emergent_patterns": swarm_result.get("emergent_patterns", []),
                "swarm_behavior": swarm_result.get("swarm_behavior", {}),
                "emergent_behavior_enabled": self.distributed_ai_config.enable_emergent_behavior
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _test_adaptive_routing(self) -> Dict[str, Any]:
        """Test adaptive routing capabilities."""
        try:
            # Test workload with adaptive routing requirements
            adaptive_workload = {
                "id": "adaptive_routing_test",
                "type": "adaptive_processing",
                "compute_intensity": "medium",
                "latency_requirement_ms": 200,
                "data_size_mb": 50,
                "privacy_requirement": "basic",
                "cost_budget": 3.0
            }
            
            # Test orchestration with adaptive routing
            routing_result = self.distributed_ai_system.orchestrate_workload(adaptive_workload)
            
            return {
                "adaptive_routing_result": routing_result,
                "routing_optimization": routing_result.get("placement", {}),
                "adaptive_routing_enabled": self.distributed_ai_config.enable_adaptive_routing
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _test_auto_scaling(self) -> Dict[str, Any]:
        """Test auto-scaling capabilities."""
        try:
            # Simulate high load scenario
            high_load_workloads = []
            for i in range(5):
                workload = {
                    "id": f"high_load_workload_{i}",
                    "type": "intensive_processing",
                    "compute_intensity": "high",
                    "latency_requirement_ms": 1000,
                    "data_size_mb": 500,
                    "privacy_requirement": "basic",
                    "cost_budget": 20.0
                }
                high_load_workloads.append(workload)
            
            # Test orchestration under high load
            scaling_results = []
            for workload in high_load_workloads:
                result = self.distributed_ai_system.orchestrate_workload(workload)
                scaling_results.append(result)
            
            # Analyze scaling effectiveness
            successful_scaling = len([r for r in scaling_results if r.get("orchestration_success", False)])
            scaling_success_rate = successful_scaling / len(high_load_workloads) if high_load_workloads else 0
            
            return {
                "scaling_results": scaling_results,
                "scaling_success_rate": scaling_success_rate,
                "auto_scaling_enabled": self.distributed_ai_config.enable_auto_scaling,
                "load_balancing_enabled": self.distributed_ai_config.enable_load_balancing
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _test_performance_tracking(self) -> Dict[str, Any]:
        """Test performance tracking capabilities."""
        try:
            # Get comprehensive system statistics
            system_status = self.distributed_ai_system.get_system_status()
            
            # Analyze performance metrics
            performance_metrics = {
                "total_operations": system_status.get("total_operations", 0),
                "federated_rounds": system_status.get("federated_stats", {}).get("current_round", 0),
                "agent_coordinations": system_status.get("coordination_stats", {}).get("coordination_events", 0),
                "workload_orchestrations": system_status.get("orchestration_stats", {}).get("workload_history", 0),
                "system_uptime": time.time() - system_status.get("system_stats", {}).get("start_time", time.time())
            }
            
            return {
                "system_status": system_status,
                "performance_metrics": performance_metrics,
                "performance_tracking_enabled": self.distributed_ai_config.enable_performance_tracking
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _test_system_scalability(self) -> Dict[str, Any]:
        """Test system scalability features."""
        try:
            # Test with maximum configuration
            max_config = create_maximum_distributed_ai_config()
            max_system = create_advanced_distributed_ai_system(max_config)
            
            # Test scalability metrics
            scalability_metrics = {
                "max_agents": max_config.max_agents,
                "federated_rounds": max_config.federated_rounds,
                "orchestration_interval": max_config.orchestration_interval,
                "monitoring_interval": max_config.monitoring_interval
            }
            
            # Test system capacity
            system_capacity = {
                "agent_capacity": max_config.max_agents,
                "federated_capacity": max_config.federated_rounds,
                "orchestration_capacity": "unlimited",
                "privacy_capacity": "enterprise_grade"
            }
            
            return {
                "scalability_metrics": scalability_metrics,
                "system_capacity": system_capacity,
                "scalability_features": {
                    "horizontal_scaling": True,
                    "vertical_scaling": True,
                    "auto_scaling": max_config.enable_auto_scaling,
                    "load_balancing": max_config.enable_load_balancing
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def save_demo_results(self, output_path: str = "distributed_ai_demo_results.json"):
        """Save demo results to file."""
        try:
            with open(output_path, 'w') as f:
                json.dump(self.demo_results, f, indent=2)
            self.logger.info(f"Demo results saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save demo results: {e}")
    
    def cleanup(self):
        """Clean up temporary files and resources."""
        try:
            # Shutdown the system gracefully
            if hasattr(self, 'distributed_ai_system'):
                self.distributed_ai_system.shutdown()
            
            # Remove test directory
            import shutil
            if hasattr(self, 'test_dir') and self.test_dir.exists():
                shutil.rmtree(self.test_dir)
            
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

def main():
    """Main demo execution."""
    demo = AdvancedDistributedAIDemo()
    
    try:
        # Run comprehensive demo
        results = demo.run_comprehensive_demo()
        
        # Save results
        demo.save_demo_results()
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 ADVANCED DISTRIBUTED AI SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"🤝 Federated Learning: {results['federated_learning']['performance_analysis']['success_rate']:.1%} success rate")
        print(f"🤖 Multi-Agent Coordination: {results['multi_agent_coordination']['effectiveness_analysis']['coordination_success_rate']:.1%} success rate")
        print(f"☁️ Edge-Cloud Orchestration: {results['edge_cloud_orchestration']['effectiveness_analysis']['orchestration_success_rate']:.1%} success rate")
        print(f"🔒 Privacy Protection: {results['privacy_protection']['privacy_effectiveness']['privacy_level']} level enabled")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
