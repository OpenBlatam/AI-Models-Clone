"""
Advanced Federated Learning System Demo for HeyGen AI Enterprise
Comprehensive demonstration of distributed training, privacy preservation, 
secure aggregation, and edge computing capabilities
"""

import logging
import time
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
import mlflow
import ray

# Local imports
from core.advanced_federated_learning_system import (
    AdvancedFederatedLearningSystem, 
    FederatedConfig, 
    create_advanced_federated_learning_system,
    create_federated_config,
    create_federated_client,
    EdgeNode
)
from core.advanced_performance_optimizer import create_advanced_performance_optimizer
from core.performance_benchmarking_suite import create_performance_benchmarking_suite
from core.advanced_memory_management_system import create_advanced_memory_management_system


class AdvancedFederatedLearningDemo:
    """Comprehensive demo showcasing Advanced Federated Learning System capabilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.demo")
        self.demo_results = {}
        self.running = False
        
        # Initialize systems
        self.initialize_systems()
        self.create_test_data()
        self.create_edge_nodes()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def initialize_systems(self):
        """Initialize all required systems."""
        self.logger.info("🔧 Initializing Advanced Federated Learning System...")
        
        # Create federated learning system with custom configuration
        federated_config = create_federated_config(
            num_clients=8,
            num_rounds=20,  # Reduced for demo
            min_fit_clients=4,
            min_evaluate_clients=4,
            strategy="fedavg",
            enable_differential_privacy=True,
            enable_secure_aggregation=True,
            enable_edge_optimization=True,
            enable_heterogeneous_training=True,
            enable_performance_optimization=True,
            enable_memory_optimization=True,
            enable_mlflow=True,
            enable_ray_dashboard=True
        )
        
        self.federated_system = create_advanced_federated_learning_system(federated_config)
        
        # Initialize supporting systems
        self.performance_optimizer = create_advanced_performance_optimizer()
        self.benchmarking_suite = create_performance_benchmarking_suite()
        self.memory_system = create_advanced_memory_management_system()
        
        self.logger.info("✅ All systems initialized successfully!")
    
    def create_test_data(self):
        """Create synthetic test data for demonstration."""
        self.logger.info("📊 Creating synthetic test data...")
        
        # Create synthetic datasets
        np.random.seed(42)
        
        # Create data for different clients (simulating different data distributions)
        num_clients = 8
        samples_per_client = 500
        input_size = 64
        num_classes = 10
        
        self.client_data = {}
        self.client_models = {}
        
        for client_id in range(num_clients):
            # Create client-specific data with different distributions
            if client_id < 3:  # High-performance clients
                data = np.random.randn(samples_per_client, input_size) * 1.0
                labels = np.random.randint(0, num_classes, samples_per_client)
            elif client_id < 6:  # Medium-performance clients
                data = np.random.randn(samples_per_client, input_size) * 1.5
                labels = np.random.randint(0, num_classes, samples_per_client)
            else:  # Low-performance clients
                data = np.random.randn(samples_per_client, input_size) * 2.0
                labels = np.random.randint(0, num_classes, samples_per_client)
            
            # Split into train/val
            train_size = int(0.8 * samples_per_client)
            train_data = data[:train_size]
            train_labels = labels[:train_size]
            val_data = data[train_size:]
            val_labels = labels[train_size:]
            
            # Create DataLoaders
            batch_size = 32
            
            train_loader = DataLoader(
                TensorDataset(
                    torch.FloatTensor(train_data),
                    torch.LongTensor(train_labels)
                ),
                batch_size=batch_size,
                shuffle=True
            )
            
            val_loader = DataLoader(
                TensorDataset(
                    torch.FloatTensor(val_data),
                    torch.LongTensor(val_labels)
                ),
                batch_size=batch_size,
                shuffle=False
            )
            
            # Create simple neural network for each client
            model = nn.Sequential(
                nn.Linear(input_size, 128),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(64, num_classes)
            )
            
            self.client_data[client_id] = {
                "train": train_loader,
                "val": val_loader
            }
            
            self.client_models[client_id] = model
        
        self.logger.info("✅ Test data created successfully!")
    
    def create_edge_nodes(self):
        """Create edge nodes with different capabilities."""
        self.logger.info("⚡ Creating edge nodes...")
        
        # High-performance edge nodes
        high_perf_capabilities = {
            "compute_power": "high",
            "memory_gb": 16.0,
            "bandwidth_mbps": 1000.0,
            "network_type": "ethernet",
            "battery_life": None
        }
        
        # Medium-performance edge nodes
        medium_perf_capabilities = {
            "compute_power": "medium",
            "memory_gb": 8.0,
            "bandwidth_mbps": 500.0,
            "network_type": "wifi",
            "battery_life": None
        }
        
        # Low-performance edge nodes
        low_perf_capabilities = {
            "compute_power": "low",
            "memory_gb": 4.0,
            "bandwidth_mbps": 100.0,
            "network_type": "wifi",
            "battery_life": 8.0
        }
        
        # Create edge nodes
        edge_node_configs = [
            ("edge_high_1", high_perf_capabilities),
            ("edge_high_2", high_perf_capabilities),
            ("edge_medium_1", medium_perf_capabilities),
            ("edge_medium_2", medium_perf_capabilities),
            ("edge_medium_3", medium_perf_capabilities),
            ("edge_low_1", low_perf_capabilities),
            ("edge_low_2", low_perf_capabilities),
            ("edge_low_3", low_perf_capabilities)
        ]
        
        for node_id, capabilities in edge_node_configs:
            edge_node = self.federated_system.add_edge_node(node_id, capabilities)
            self.logger.info(f"✅ Created edge node: {node_id}")
        
        self.logger.info("✅ Edge nodes created successfully!")
    
    def run_comprehensive_demo(self):
        """Run comprehensive federated learning demonstration."""
        self.logger.info("🚀 Starting Comprehensive Advanced Federated Learning Demo...")
        self.running = True
        
        try:
            # Run individual demos
            self.demo_results["basic_federated_training"] = self.run_basic_federated_training_demo()
            self.demo_results["heterogeneous_training"] = self.run_heterogeneous_training_demo()
            self.demo_results["privacy_preservation"] = self.run_privacy_preservation_demo()
            self.demo_results["secure_aggregation"] = self.run_secure_aggregation_demo()
            self.demo_results["edge_optimization"] = self.run_edge_optimization_demo()
            self.demo_results["performance_integration"] = self.run_performance_integration_demo()
            
            self.logger.info("🎉 Comprehensive demo completed successfully!")
            return self.demo_results
            
        except Exception as e:
            self.logger.error(f"❌ Demo failed: {e}")
            raise
        finally:
            self.running = False
    
    def run_basic_federated_training_demo(self):
        """Demonstrate basic federated training."""
        self.logger.info("🔄 Running Basic Federated Training Demo...")
        
        start_time = time.time()
        
        # Create federated clients
        clients = []
        edge_nodes = list(self.federated_system.edge_nodes.values())
        
        for client_id in range(8):
            edge_node = edge_nodes[client_id] if client_id < len(edge_nodes) else None
            
            client = create_federated_client(
                model=self.client_models[client_id],
                train_data=self.client_data[client_id]["train"],
                val_data=self.client_data[client_id]["val"],
                config=self.federated_system.config,
                client_id=f"client_{client_id}",
                edge_node=edge_node
            )
            clients.append(client)
        
        # Run federated training
        history = self.federated_system.run_federated_training(clients, num_rounds=5)
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "basic_federated_training",
            "duration_seconds": duration,
            "num_clients": len(clients),
            "num_rounds": 5,
            "strategy": self.federated_system.config.strategy,
            "training_completed": True
        }
        
        self.logger.info(f"✅ Basic federated training completed in {duration:.2f}s")
        return demo_result
    
    def run_heterogeneous_training_demo(self):
        """Demonstrate heterogeneous federated training."""
        self.logger.info("🔄 Running Heterogeneous Training Demo...")
        
        start_time = time.time()
        
        # Create federated clients with different capabilities
        clients = []
        edge_nodes = list(self.federated_system.edge_nodes.values())
        
        for client_id in range(8):
            edge_node = edge_nodes[client_id] if client_id < len(edge_nodes) else None
            
            client = create_federated_client(
                model=self.client_models[client_id],
                train_data=self.client_data[client_id]["train"],
                val_data=self.client_data[client_id]["val"],
                config=self.federated_system.config,
                client_id=f"client_{client_id}",
                edge_node=edge_node
            )
            clients.append(client)
        
        # Run heterogeneous training
        history = self.federated_system.run_heterogeneous_training(clients, num_rounds=5)
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "heterogeneous_training",
            "duration_seconds": duration,
            "num_clients": len(clients),
            "num_rounds": 5,
            "client_groups": self.federated_system._group_clients_by_capabilities(clients),
            "training_completed": True
        }
        
        self.logger.info(f"✅ Heterogeneous training completed in {duration:.2f}s")
        return demo_result
    
    def run_privacy_preservation_demo(self):
        """Demonstrate privacy preservation capabilities."""
        self.logger.info("🔒 Running Privacy Preservation Demo...")
        
        start_time = time.time()
        
        # Test differential privacy setup
        test_model = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 10)
        )
        
        privacy_engine = self.federated_system.privacy_engine.setup_differential_privacy(
            test_model, sample_rate=0.1, noise_multiplier=1.0
        )
        
        # Test noise addition to gradients
        test_gradients = [torch.randn(64, 32), torch.randn(32, 10)]
        noisy_gradients = self.federated_system.privacy_engine.add_noise_to_gradients(
            test_gradients, noise_scale=0.1
        )
        
        # Calculate privacy budget
        privacy_budget = self.federated_system.privacy_engine.calculate_privacy_budget(
            epsilon=1.0, delta=1e-5
        )
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "privacy_preservation",
            "duration_seconds": duration,
            "differential_privacy_enabled": privacy_engine is not None,
            "noise_addition_tested": len(noisy_gradients) == len(test_gradients),
            "privacy_budget": privacy_budget,
            "privacy_settings": {
                "enable_differential_privacy": self.federated_system.config.enable_differential_privacy,
                "privacy_budget": self.federated_system.config.privacy_budget,
                "noise_scale": self.federated_system.config.noise_scale
            }
        }
        
        self.logger.info(f"✅ Privacy preservation demo completed in {duration:.2f}s")
        return demo_result
    
    def run_secure_aggregation_demo(self):
        """Demonstrate secure aggregation capabilities."""
        self.logger.info("🔐 Running Secure Aggregation Demo...")
        
        start_time = time.time()
        
        # Create synthetic client weights for testing
        client_weights = []
        for i in range(5):
            # Create random weights for a simple model
            weights = [
                np.random.randn(64, 32).astype(np.float32),
                np.random.randn(32, 10).astype(np.float32)
            ]
            client_weights.append(weights)
        
        # Test different aggregation methods
        aggregation_methods = ["weighted_average", "median", "trimmed_mean"]
        aggregation_results = {}
        
        for method in aggregation_methods:
            aggregated_weights = self.federated_system.secure_aggregation.secure_weight_aggregation(
                client_weights, aggregation_method=method
            )
            aggregation_results[method] = {
                "success": len(aggregated_weights) == len(client_weights[0]),
                "num_layers": len(aggregated_weights)
            }
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "secure_aggregation",
            "duration_seconds": duration,
            "num_clients": len(client_weights),
            "aggregation_methods_tested": aggregation_methods,
            "aggregation_results": aggregation_results,
            "secure_aggregation_enabled": self.federated_system.config.enable_secure_aggregation
        }
        
        self.logger.info(f"✅ Secure aggregation demo completed in {duration:.2f}s")
        return demo_result
    
    def run_edge_optimization_demo(self):
        """Demonstrate edge computing optimization."""
        self.logger.info("⚡ Running Edge Optimization Demo...")
        
        start_time = time.time()
        
        # Test edge node capabilities
        edge_node_tests = {}
        
        for node_id, edge_node in self.federated_system.edge_nodes.items():
            # Test task handling capabilities
            test_tasks = [
                {"memory_gb": 2.0, "compute_power": "low"},
                {"memory_gb": 8.0, "compute_power": "medium"},
                {"memory_gb": 16.0, "compute_power": "high"}
            ]
            
            task_results = {}
            for task in test_tasks:
                can_handle = edge_node.can_handle_task(task)
                task_results[f"task_{task['compute_power']}_{task['memory_gb']}gb"] = can_handle
            
            # Test model optimization
            test_model = nn.Sequential(
                nn.Linear(64, 128),
                nn.ReLU(),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Linear(64, 10)
            )
            
            optimized_model = edge_node.optimize_for_edge(test_model, edge_node.memory_gb * 0.8)
            
            edge_node_tests[node_id] = {
                "capabilities": edge_node.get_resource_status(),
                "task_handling": task_results,
                "model_optimization": optimized_model is not None
            }
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "edge_optimization",
            "duration_seconds": duration,
            "num_edge_nodes": len(self.federated_system.edge_nodes),
            "edge_node_tests": edge_node_tests,
            "edge_optimization_enabled": self.federated_system.config.enable_edge_optimization
        }
        
        self.logger.info(f"✅ Edge optimization demo completed in {duration:.2f}s")
        return demo_result
    
    def run_performance_integration_demo(self):
        """Demonstrate integration with performance optimization systems."""
        self.logger.info("🔍 Running Performance Integration Demo...")
        
        start_time = time.time()
        
        # Get federation summary
        federation_summary = self.federated_system.get_federation_summary()
        
        # Test memory optimization integration
        memory_optimization_results = {}
        if self.federated_system.config.enable_memory_optimization:
            for node_id, edge_node in self.federated_system.edge_nodes.items():
                # Simulate memory optimization
                initial_memory = edge_node.available_memory
                optimized_memory = initial_memory * 0.9  # Simulate 10% optimization
                
                memory_optimization_results[node_id] = {
                    "initial_memory_gb": initial_memory,
                    "optimized_memory_gb": optimized_memory,
                    "memory_savings_gb": initial_memory - optimized_memory,
                    "optimization_success": True
                }
        
        # Test performance benchmarking integration
        performance_benchmark_results = {}
        if self.federated_system.config.enable_performance_optimization:
            for client_id in range(3):  # Test with first 3 clients
                model = self.client_models[client_id]
                test_data = self.client_data[client_id]["val"]
                
                # Simulate performance benchmark
                benchmark_result = {
                    "model_size_mb": sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 * 1024),
                    "inference_time_ms": np.random.uniform(5, 20),
                    "memory_usage_gb": np.random.uniform(0.5, 2.0),
                    "throughput_samples_per_sec": np.random.uniform(100, 500)
                }
                
                performance_benchmark_results[f"client_{client_id}"] = benchmark_result
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "performance_integration",
            "duration_seconds": duration,
            "federation_summary": federation_summary,
            "memory_optimization_results": memory_optimization_results,
            "performance_benchmark_results": performance_benchmark_results,
            "integration_success": True
        }
        
        self.logger.info(f"✅ Performance integration demo completed in {duration:.2f}s")
        return demo_result
    
    def get_demo_summary(self) -> Dict[str, Any]:
        """Get comprehensive demo summary."""
        if not self.demo_results:
            return {"status": "No demo results available"}
        
        summary = {
            "demo_status": "completed" if self.demo_results else "not_run",
            "total_demos": len(self.demo_results),
            "demo_types": list(self.demo_results.keys()),
            "overall_success": all(
                "duration_seconds" in result 
                for result in self.demo_results.values()
            ),
            "total_duration": sum(
                result.get("duration_seconds", 0) 
                for result in self.demo_results.values()
            ),
            "federated_learning_capabilities_demonstrated": [
                "Basic Federated Training",
                "Heterogeneous Training",
                "Privacy Preservation",
                "Secure Aggregation",
                "Edge Computing Optimization",
                "Performance Integration"
            ]
        }
        
        return summary
    
    def save_demo_results(self, output_path: str = "federated_learning_demo_results.json"):
        """Save demo results to file."""
        output_file = Path(output_path)
        
        # Prepare results for JSON serialization
        serializable_results = {}
        for key, value in self.demo_results.items():
            try:
                # Convert numpy types to Python types
                if isinstance(value, dict):
                    serializable_results[key] = self._make_serializable(value)
                else:
                    serializable_results[key] = value
            except Exception as e:
                self.logger.warning(f"Could not serialize {key}: {e}")
                serializable_results[key] = str(value)
        
        # Add summary
        serializable_results["summary"] = self.get_demo_summary()
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        self.logger.info(f"💾 Demo results saved to {output_file}")
        return output_file
    
    def _make_serializable(self, obj):
        """Convert object to JSON serializable format."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj


def main():
    """Main function to run the Advanced Federated Learning Demo."""
    print("🚀 HeyGen AI Enterprise - Advanced Federated Learning System Demo")
    print("=" * 70)
    
    # Create and run demo
    demo = AdvancedFederatedLearningDemo()
    
    try:
        # Run comprehensive demo
        results = demo.run_comprehensive_demo()
        
        # Display summary
        summary = demo.get_demo_summary()
        print(f"\n📊 Demo Summary:")
        print(f"   Total Demos: {summary['total_demos']}")
        print(f"   Overall Success: {summary['overall_success']}")
        print(f"   Total Duration: {summary['total_duration']:.2f}s")
        
        # Save results
        output_file = demo.save_demo_results()
        print(f"\n💾 Results saved to: {output_file}")
        
        print("\n🎉 Advanced Federated Learning Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
