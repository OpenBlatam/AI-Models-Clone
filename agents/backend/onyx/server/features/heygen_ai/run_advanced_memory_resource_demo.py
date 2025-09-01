import logging
import time
import json
import os
import tempfile
from pathlib import Path
import numpy as np
import asyncio

from core.advanced_memory_resource_system import (
    AdvancedMemoryResourceSystem,
    MemoryResourceConfig,
    MemoryTier,
    ResourceType,
    CacheStrategy,
    create_advanced_memory_resource_system,
    create_minimal_memory_resource_config,
    create_maximum_memory_resource_config
)

class AdvancedMemoryResourceDemo:
    """Comprehensive demo showcasing Advanced Memory & Resource Management System capabilities."""
    
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
        """Initialize Memory & Resource Management and supporting systems."""
        self.logger.info("🚀 Initializing Advanced Memory & Resource Management Systems...")
        
        # Create maximum configuration
        self.memory_config = create_maximum_memory_resource_config()
        self.memory_system = create_advanced_memory_resource_system(self.memory_config)
        
        # Create temporary directory for test data
        self.test_dir = Path(tempfile.mkdtemp(prefix="memory_resource_demo_"))
        self.logger.info(f"Test directory created: {self.test_dir}")
    
    def create_test_data(self):
        """Create test data for demonstration."""
        self.logger.info("🔧 Creating test data...")
        
        # Create test models (simulated)
        self.test_models = {
            "small_model": {"size_mb": 50, "type": "classification", "complexity": "low"},
            "medium_model": {"size_mb": 200, "type": "detection", "complexity": "medium"},
            "large_model": {"size_mb": 800, "type": "generation", "complexity": "high"},
            "huge_model": {"size_mb": 2000, "type": "multimodal", "complexity": "very_high"}
        }
        
        # Create test data samples
        self.test_data = {
            "image_data": np.random.rand(224, 224, 3).astype(np.float32),
            "text_data": "Sample text data for testing purposes",
            "numerical_data": np.random.rand(1000).astype(np.float32),
            "model_weights": np.random.rand(1000000).astype(np.float32)
        }
        
        # Create resource requirements
        self.resource_requests = [
            {
                "id": "low_latency_request",
                "required_resources": {"cpu": 2, "memory": 4096, "gpu": 1},
                "latency_requirement_ms": 100,
                "cost_budget": 1.0
            },
            {
                "id": "high_performance_request",
                "required_resources": {"cpu": 8, "memory": 16384, "gpu": 4},
                "latency_requirement_ms": 500,
                "cost_budget": 5.0
            },
            {
                "id": "batch_processing_request",
                "required_resources": {"cpu": 16, "memory": 32768, "gpu": 0},
                "latency_requirement_ms": 2000,
                "cost_budget": 10.0
            }
        ]
        
        self.logger.info("✅ Test data created successfully")
    
    def run_comprehensive_demo(self):
        """Run comprehensive Memory & Resource Management demonstration."""
        self.logger.info("🚀 Starting Comprehensive Advanced Memory & Resource Management Demo...")
        self.running = True
        
        try:
            # Run individual demos
            self.demo_results["system_initialization"] = self.run_system_initialization_demo()
            self.demo_results["intelligent_caching"] = self.run_intelligent_caching_demo()
            self.demo_results["model_optimization"] = self.run_model_optimization_demo()
            self.demo_results["resource_coordination"] = self.run_resource_coordination_demo()
            self.demo_results["performance_analysis"] = self.run_performance_analysis_demo()
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
            status = self.memory_system.get_system_status()
            
            # Test different configurations
            minimal_config = create_minimal_memory_resource_config()
            minimal_system = create_advanced_memory_resource_system(minimal_config)
            
            results = {
                "main_system_status": status,
                "minimal_system_status": minimal_system.get_system_status(),
                "config_comparison": {
                    "main_system": {
                        "intelligent_caching": self.memory_config.enable_intelligent_caching,
                        "model_compression": self.memory_config.enable_model_compression,
                        "resource_optimization": self.memory_config.enable_resource_optimization,
                        "distributed_coordination": self.memory_config.enable_distributed_coordination
                    },
                    "minimal_system": {
                        "intelligent_caching": minimal_config.enable_intelligent_caching,
                        "model_compression": minimal_config.enable_model_compression,
                        "resource_optimization": minimal_config.enable_resource_optimization,
                        "distributed_coordination": minimal_config.enable_distributed_coordination
                    }
                }
            }
            
            self.logger.info("✅ System Initialization Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ System Initialization Demo failed: {e}")
            return {"error": str(e)}
    
    def run_intelligent_caching_demo(self) -> Dict[str, Any]:
        """Demo intelligent caching capabilities."""
        self.logger.info("💾 Running Intelligent Caching Demo...")
        
        try:
            results = {}
            
            # Test different data types and sizes
            test_items = [
                ("small_image", self.test_data["image_data"], 1024 * 1024, 9),  # 1MB, high priority
                ("medium_text", self.test_data["text_data"], 512, 7),            # 512B, medium priority
                ("large_weights", self.test_data["model_weights"], 4 * 1024 * 1024, 5),  # 4MB, low priority
                ("cached_result", {"result": "cached_inference"}, 1024, 8),     # 1KB, high priority
                ("model_metadata", {"layers": 50, "parameters": 1000000}, 256, 6)  # 256B, medium priority
            ]
            
            # Cache items
            cache_results = {}
            for key, value, size, priority in test_items:
                success = self.memory_system.cache_item(key, value, size, priority)
                cache_results[key] = {
                    "cached": success,
                    "size_bytes": size,
                    "priority": priority
                }
            
            # Test cache retrieval
            retrieval_results = {}
            for key, _, _, _ in test_items:
                item = self.memory_system.get_cached_item(key)
                retrieval_results[key] = {
                    "retrieved": item is not None,
                    "item_type": type(item).__name__ if item is not None else None
                }
            
            # Get cache statistics
            cache_stats = self.memory_system.intelligent_cache.get_cache_stats()
            
            # Test cache performance
            performance_test = self._test_cache_performance()
            
            results = {
                "cache_operations": cache_results,
                "retrieval_results": retrieval_results,
                "cache_statistics": cache_stats,
                "performance_test": performance_test
            }
            
            self.logger.info("✅ Intelligent Caching Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Intelligent Caching Demo failed: {e}")
            return {"error": str(e)}
    
    def _test_cache_performance(self) -> Dict[str, Any]:
        """Test cache performance with multiple operations."""
        performance_results = {
            "cache_speed": {},
            "hit_rate_evolution": [],
            "memory_efficiency": {}
        }
        
        # Test cache speed
        test_key = "performance_test_key"
        test_value = np.random.rand(1000, 1000)
        test_size = test_value.nbytes
        
        # Measure cache write time
        start_time = time.time()
        self.memory_system.cache_item(test_key, test_value, test_size, 9)
        write_time = time.time() - start_time
        
        # Measure cache read time
        start_time = time.time()
        retrieved_value = self.memory_system.get_cached_item(test_key)
        read_time = time.time() - start_time
        
        performance_results["cache_speed"] = {
            "write_time_ms": write_time * 1000,
            "read_time_ms": read_time * 1000,
            "speedup_factor": write_time / read_time if read_time > 0 else 0
        }
        
        # Test hit rate evolution
        for i in range(10):
            # Access the same key multiple times
            for _ in range(5):
                self.memory_system.get_cached_item(test_key)
            
            # Get current hit rate
            stats = self.memory_system.intelligent_cache.get_cache_stats()
            performance_results["hit_rate_evolution"].append({
                "iteration": i,
                "hit_rate": stats["hit_rate"]
            })
        
        # Test memory efficiency
        cache_stats = self.memory_system.intelligent_cache.get_cache_stats()
        total_usage = sum(cache_stats["current_usage"].values())
        total_limit = sum(cache_stats["cache_limits"].values())
        
        performance_results["memory_efficiency"] = {
            "total_usage_bytes": total_usage,
            "total_limit_bytes": total_limit,
            "usage_percentage": (total_usage / total_limit) * 100 if total_limit > 0 else 0,
            "active_items": cache_stats["metadata_count"]
        }
        
        return performance_results
    
    def run_model_optimization_demo(self) -> Dict[str, Any]:
        """Demo model optimization capabilities."""
        self.logger.info("⚡ Running Model Optimization Demo...")
        
        try:
            results = {}
            
            # Test optimization for different model types
            optimization_results = {}
            
            for model_name, model_info in self.test_models.items():
                # Simulate model optimization
                optimization_result = self.memory_system.optimize_model(
                    model_info, f"edge_device_{model_name}"
                )
                
                optimization_results[model_name] = {
                    "model_info": model_info,
                    "optimization_result": optimization_result
                }
            
            # Analyze optimization effectiveness
            total_original_size = sum(
                result["model_info"]["size_mb"] for result in optimization_results.values()
            )
            total_optimized_size = sum(
                result["optimization_result"].get("optimized_size_mb", 0) 
                for result in optimization_results.values()
            )
            
            overall_compression_ratio = total_optimized_size / total_original_size if total_original_size > 0 else 1.0
            total_size_reduction = (1 - overall_compression_ratio) * 100
            
            # Test different optimization strategies
            strategy_test = self._test_optimization_strategies()
            
            results = {
                "optimization_results": optimization_results,
                "overall_analysis": {
                    "total_original_size_mb": total_original_size,
                    "total_optimized_size_mb": total_optimized_size,
                    "overall_compression_ratio": overall_compression_ratio,
                    "total_size_reduction_percent": total_size_reduction
                },
                "strategy_test": strategy_test
            }
            
            self.logger.info("✅ Model Optimization Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Model Optimization Demo failed: {e}")
            return {"error": str(e)}
    
    def _test_optimization_strategies(self) -> Dict[str, Any]:
        """Test different optimization strategies."""
        strategy_results = {}
        
        # Test with different configurations
        test_configs = [
            ("minimal", create_minimal_memory_resource_config()),
            ("maximum", create_maximum_memory_resource_config()),
            ("custom", create_memory_resource_config(
                enable_quantization=True,
                enable_pruning=False,
                enable_model_fusion=True
            ))
        ]
        
        for config_name, config in test_configs:
            # Create temporary system for testing
            temp_system = create_advanced_memory_resource_system(config)
            
            # Test optimization
            test_model = {"size_mb": 500, "type": "test", "complexity": "medium"}
            result = temp_system.optimize_model(test_model, "test_device")
            
            strategy_results[config_name] = {
                "config_features": {
                    "quantization": config.enable_quantization,
                    "pruning": config.enable_pruning,
                    "model_fusion": config.enable_model_fusion
                },
                "optimization_result": result
            }
        
        return strategy_results
    
    def run_resource_coordination_demo(self) -> Dict[str, Any]:
        """Demo resource coordination capabilities."""
        self.logger.info("🔄 Running Resource Coordination Demo...")
        
        try:
            results = {}
            
            # Register test resources
            self._register_test_resources()
            
            # Test resource allocation
            allocation_results = {}
            for request in self.resource_requests:
                allocation_result = self.memory_system.allocate_resources(request)
                allocation_results[request["id"]] = {
                    "request": request,
                    "allocation_result": allocation_result
                }
            
            # Analyze allocation patterns
            edge_allocations = len([
                r for r in allocation_results.values() 
                if r["allocation_result"].get("target_location") == "edge"
            ])
            cloud_allocations = len([
                r for r in allocation_results.values() 
                if r["allocation_result"].get("target_location") == "cloud"
            ])
            
            # Test resource monitoring
            coordination_stats = self.memory_system.resource_coordinator.get_coordination_stats()
            
            # Test resource efficiency
            efficiency_test = self._test_resource_efficiency()
            
            results = {
                "allocation_results": allocation_results,
                "allocation_analysis": {
                    "total_requests": len(self.resource_requests),
                    "edge_allocations": edge_allocations,
                    "cloud_allocations": cloud_allocations,
                    "edge_percentage": edge_allocations / len(self.resource_requests) if self.resource_requests else 0,
                    "cloud_percentage": cloud_allocations / len(self.resource_requests) if self.resource_requests else 0
                },
                "coordination_stats": coordination_stats,
                "efficiency_test": efficiency_test
            }
            
            self.logger.info("✅ Resource Coordination Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Resource Coordination Demo failed: {e}")
            return {"error": str(e)}
    
    def _register_test_resources(self):
        """Register test edge and cloud resources."""
        # Register edge resources
        edge_resources = {
            "edge_device_1": {
                "cpu": 4, "memory": 8192, "gpu": 1, "storage": 100000
            },
            "edge_device_2": {
                "cpu": 8, "memory": 16384, "gpu": 2, "storage": 200000
            },
            "edge_gateway": {
                "cpu": 16, "memory": 32768, "gpu": 4, "storage": 500000
            }
        }
        
        for device_id, resources in edge_resources.items():
            self.memory_system.resource_coordinator.register_edge_resource(device_id, resources)
        
        # Register cloud resources
        cloud_resources = {
            "cloud_service_1": {
                "cpu": 32, "memory": 65536, "gpu": 8, "storage": 1000000
            },
            "cloud_service_2": {
                "cpu": 64, "memory": 131072, "gpu": 16, "storage": 2000000
            }
        }
        
        for service_id, resources in cloud_resources.items():
            self.memory_system.resource_coordinator.register_cloud_resource(service_id, resources)
    
    def _test_resource_efficiency(self) -> Dict[str, Any]:
        """Test resource allocation efficiency."""
        efficiency_results = {
            "allocation_speed": {},
            "resource_utilization": {},
            "cost_analysis": {}
        }
        
        # Test allocation speed
        test_request = {
            "required_resources": {"cpu": 2, "memory": 4096},
            "latency_requirement_ms": 100,
            "cost_budget": 1.0
        }
        
        start_time = time.time()
        allocation_result = self.memory_system.allocate_resources(test_request)
        allocation_time = time.time() - start_time
        
        efficiency_results["allocation_speed"] = {
            "allocation_time_ms": allocation_time * 1000,
            "allocation_success": "error" not in allocation_result
        }
        
        # Analyze resource utilization
        coordination_stats = self.memory_system.resource_coordinator.get_coordination_stats()
        total_resources = coordination_stats["edge_resources"] + coordination_stats["cloud_resources"]
        active_allocations = coordination_stats["active_allocations"]
        
        efficiency_results["resource_utilization"] = {
            "total_resources": total_resources,
            "active_allocations": active_allocations,
            "utilization_rate": active_allocations / total_resources if total_resources > 0 else 0
        }
        
        # Cost analysis
        total_cost = sum(
            r["allocation_result"].get("estimated_cost", 0) 
            for r in self.demo_results.get("resource_coordination", {}).get("allocation_results", {}).values()
        )
        
        efficiency_results["cost_analysis"] = {
            "total_cost": total_cost,
            "average_cost_per_request": total_cost / len(self.resource_requests) if self.resource_requests else 0,
            "cost_efficiency": "high" if total_cost < 5.0 else "medium" if total_cost < 10.0 else "low"
        }
        
        return efficiency_results
    
    def run_performance_analysis_demo(self) -> Dict[str, Any]:
        """Demo performance analysis capabilities."""
        self.logger.info("📊 Running Performance Analysis Demo...")
        
        try:
            results = {}
            
            # Get comprehensive system statistics
            system_status = self.memory_system.get_system_status()
            
            # Analyze cache performance
            cache_performance = self._analyze_cache_performance()
            
            # Analyze resource coordination performance
            coordination_performance = self._analyze_coordination_performance()
            
            # Analyze overall system performance
            system_performance = self._analyze_system_performance()
            
            results = {
                "system_status": system_status,
                "cache_performance": cache_performance,
                "coordination_performance": coordination_performance,
                "system_performance": system_performance
            }
            
            self.logger.info("✅ Performance Analysis Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Performance Analysis Demo failed: {e}")
            return {"error": str(e)}
    
    def _analyze_cache_performance(self) -> Dict[str, Any]:
        """Analyze cache performance metrics."""
        cache_stats = self.memory_system.intelligent_cache.get_cache_stats()
        
        # Calculate performance metrics
        total_operations = sum(cache_stats["cache_stats"]["hits"].values()) + sum(cache_stats["cache_stats"]["misses"].values())
        hit_rate = cache_stats["hit_rate"]
        
        # Analyze cache efficiency
        cache_efficiency = {
            "excellent": hit_rate >= 0.9,
            "good": 0.8 <= hit_rate < 0.9,
            "fair": 0.7 <= hit_rate < 0.8,
            "poor": hit_rate < 0.7
        }
        
        # Calculate cache utilization
        total_usage = sum(cache_stats["current_usage"].values())
        total_limit = sum(cache_stats["cache_limits"].values())
        utilization_rate = total_usage / total_limit if total_limit > 0 else 0
        
        return {
            "hit_rate": hit_rate,
            "total_operations": total_operations,
            "cache_efficiency": cache_efficiency,
            "utilization_rate": utilization_rate,
            "cache_stats": cache_stats
        }
    
    def _analyze_coordination_performance(self) -> Dict[str, Any]:
        """Analyze resource coordination performance."""
        coordination_stats = self.memory_system.resource_coordinator.get_coordination_stats()
        
        # Calculate coordination metrics
        total_resources = coordination_stats["edge_resources"] + coordination_stats["cloud_resources"]
        resource_efficiency = coordination_stats["active_allocations"] / total_resources if total_resources > 0 else 0
        
        # Analyze coordination effectiveness
        coordination_effectiveness = {
            "excellent": resource_efficiency >= 0.8,
            "good": 0.6 <= resource_efficiency < 0.8,
            "fair": 0.4 <= resource_efficiency < 0.6,
            "poor": resource_efficiency < 0.4
        }
        
        return {
            "resource_efficiency": resource_efficiency,
            "coordination_effectiveness": coordination_effectiveness,
            "coordination_stats": coordination_stats
        }
    
    def _analyze_system_performance(self) -> Dict[str, Any]:
        """Analyze overall system performance."""
        system_stats = self.memory_system.system_stats
        
        # Calculate performance metrics
        uptime_seconds = time.time() - system_stats["start_time"]
        operations_per_second = system_stats["total_operations"] / uptime_seconds if uptime_seconds > 0 else 0
        
        # Analyze system health
        system_health = {
            "excellent": operations_per_second >= 10,
            "good": 5 <= operations_per_second < 10,
            "fair": 2 <= operations_per_second < 5,
            "poor": operations_per_second < 2
        }
        
        return {
            "uptime_seconds": uptime_seconds,
            "operations_per_second": operations_per_second,
            "system_health": system_health,
            "system_stats": system_stats
        }
    
    def run_advanced_features_demo(self) -> Dict[str, Any]:
        """Demo advanced system features."""
        self.logger.info("🚀 Running Advanced Features Demo...")
        
        try:
            results = {}
            
            # Test adaptive caching strategies
            adaptive_caching = self._test_adaptive_caching()
            
            # Test predictive resource scaling
            predictive_scaling = self._test_predictive_scaling()
            
            # Test memory optimization features
            memory_optimization = self._test_memory_optimization()
            
            # Test system scalability
            system_scalability = self._test_system_scalability()
            
            results = {
                "adaptive_caching": adaptive_caching,
                "predictive_scaling": predictive_scaling,
                "memory_optimization": memory_optimization,
                "system_scalability": system_scalability
            }
            
            self.logger.info("✅ Advanced Features Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Advanced Features Demo failed: {e}")
            return {"error": str(e)}
    
    def _test_adaptive_caching(self) -> Dict[str, Any]:
        """Test adaptive caching strategies."""
        # Test different cache strategies
        strategies = [CacheStrategy.LRU, CacheStrategy.LFU, CacheStrategy.FIFO]
        strategy_results = {}
        
        for strategy in strategies:
            # Create temporary system with specific strategy
            temp_config = create_memory_resource_config()
            temp_config.cache_strategy = strategy
            temp_system = create_advanced_memory_resource_system(temp_config)
            
            # Test caching performance
            test_items = [
                ("strategy_test_1", "data1", 1024, 8),
                ("strategy_test_2", "data2", 1024, 7),
                ("strategy_test_3", "data3", 1024, 6)
            ]
            
            for key, value, size, priority in test_items:
                temp_system.cache_item(key, value, size, priority)
            
            # Get cache stats
            cache_stats = temp_system.intelligent_cache.get_cache_stats()
            strategy_results[strategy.value] = {
                "hit_rate": cache_stats["hit_rate"],
                "evictions": sum(cache_stats["cache_stats"]["evictions"].values())
            }
        
        return strategy_results
    
    def _test_predictive_scaling(self) -> Dict[str, Any]:
        """Test predictive resource scaling."""
        # Simulate resource usage patterns
        usage_patterns = []
        for i in range(10):
            # Simulate varying resource usage
            usage = {
                "timestamp": time.time() + i * 60,
                "cpu_usage": 0.3 + (i % 3) * 0.2,
                "memory_usage": 0.4 + (i % 2) * 0.3,
                "predicted_demand": "high" if i % 2 == 0 else "low"
            }
            usage_patterns.append(usage)
        
        # Analyze patterns
        high_demand_periods = len([u for u in usage_patterns if u["predicted_demand"] == "high"])
        scaling_recommendations = {
            "scale_up": high_demand_periods > len(usage_patterns) * 0.6,
            "scale_down": high_demand_periods < len(usage_patterns) * 0.3,
            "maintain": len(usage_patterns) * 0.3 <= high_demand_periods <= len(usage_patterns) * 0.6
        }
        
        return {
            "usage_patterns": usage_patterns,
            "scaling_recommendations": scaling_recommendations,
            "prediction_accuracy": "high" if len(usage_patterns) > 5 else "medium"
        }
    
    def _test_memory_optimization(self) -> Dict[str, Any]:
        """Test memory optimization features."""
        # Test memory pooling
        memory_pooling = {
            "enabled": self.memory_config.enable_memory_pooling,
            "pool_size_mb": self.memory_config.memory_pool_size_mb,
            "efficiency": "high" if self.memory_config.memory_pool_size_mb >= 1024 else "medium"
        }
        
        # Test auto-cleanup
        auto_cleanup = {
            "enabled": self.memory_config.enable_auto_cleanup,
            "cleanup_threshold": self.memory_config.memory_cleanup_threshold,
            "effectiveness": "high" if self.memory_config.memory_cleanup_threshold <= 0.8 else "medium"
        }
        
        # Test model compression
        model_compression = {
            "quantization": self.memory_config.enable_quantization,
            "pruning": self.memory_config.enable_pruning,
            "model_fusion": self.memory_config.enable_model_fusion,
            "compression_ratio": self.memory_config.pruning_ratio
        }
        
        return {
            "memory_pooling": memory_pooling,
            "auto_cleanup": auto_cleanup,
            "model_compression": model_compression
        }
    
    def _test_system_scalability(self) -> Dict[str, Any]:
        """Test system scalability features."""
        # Test horizontal scaling
        horizontal_scaling = {
            "cache_levels": 3,  # L1, L2, L3
            "cache_capacity_mb": sum([
                self.memory_config.l1_cache_size_mb,
                self.memory_config.l2_cache_size_mb,
                self.memory_config.l3_cache_size_mb
            ]),
            "scalability": "high" if self.memory_config.l3_cache_size_mb >= 1024 else "medium"
        }
        
        # Test resource coordination
        resource_coordination = {
            "edge_resources": len(self.memory_system.resource_coordinator.edge_resources),
            "cloud_resources": len(self.memory_system.resource_coordinator.cloud_resources),
            "coordination_capacity": "high" if len(self.memory_system.resource_coordinator.edge_resources) >= 3 else "medium"
        }
        
        # Test monitoring capabilities
        monitoring_capabilities = {
            "monitoring_interval": self.memory_config.monitoring_interval,
            "predictive_scaling": self.memory_config.enable_predictive_scaling,
            "auto_cleanup": self.memory_config.enable_auto_cleanup,
            "effectiveness": "high" if self.memory_config.monitoring_interval <= 10 else "medium"
        }
        
        return {
            "horizontal_scaling": horizontal_scaling,
            "resource_coordination": resource_coordination,
            "monitoring_capabilities": monitoring_capabilities
        }
    
    def save_demo_results(self, output_path: str = "memory_resource_demo_results.json"):
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
            if hasattr(self, 'memory_system'):
                self.memory_system.shutdown()
            
            # Remove test directory
            import shutil
            if hasattr(self, 'test_dir') and self.test_dir.exists():
                shutil.rmtree(self.test_dir)
            
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

def main():
    """Main demo execution."""
    demo = AdvancedMemoryResourceDemo()
    
    try:
        # Run comprehensive demo
        results = demo.run_comprehensive_demo()
        
        # Save results
        demo.save_demo_results()
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 ADVANCED MEMORY & RESOURCE MANAGEMENT SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"💾 Cache Hit Rate: {results['intelligent_caching']['cache_statistics']['hit_rate']:.1%}")
        print(f"⚡ Model Compression: {results['model_optimization']['overall_analysis']['total_size_reduction_percent']:.1f}% size reduction")
        print(f"🔄 Resource Allocation: {results['resource_coordination']['allocation_analysis']['edge_percentage']:.1%} edge allocations")
        print(f"📊 System Performance: {results['performance_analysis']['system_performance']['operations_per_second']:.1f} ops/sec")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
