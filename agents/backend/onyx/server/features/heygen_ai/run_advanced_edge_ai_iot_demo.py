import logging
import time
import json
import os
import tempfile
from pathlib import Path
import numpy as np
import asyncio

from core.advanced_edge_ai_iot_system import (
    AdvancedEdgeAIIoTSystem,
    EdgeAIConfig,
    DeviceType,
    EdgeTier,
    InferenceMode,
    IoTDevice,
    create_advanced_edge_ai_iot_system,
    create_minimal_edge_ai_config,
    create_maximum_edge_ai_config
)

class AdvancedEdgeAIIoTDemo:
    """Comprehensive demo showcasing Advanced Edge AI & IoT System capabilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.demo")
        self.demo_results = {}
        self.running = False
        
        # Initialize systems
        self.initialize_systems()
        self.create_test_devices()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def initialize_systems(self):
        """Initialize Edge AI & IoT and supporting systems."""
        self.logger.info("🚀 Initializing Advanced Edge AI & IoT Systems...")
        
        # Create maximum Edge AI configuration
        self.edge_ai_config = create_maximum_edge_ai_config()
        self.edge_ai_system = create_advanced_edge_ai_iot_system(self.edge_ai_config)
        
        # Create temporary directory for test data
        self.test_dir = Path(tempfile.mkdtemp(prefix="edge_ai_demo_"))
        self.logger.info(f"Test directory created: {self.test_dir}")
    
    def create_test_devices(self):
        """Create test IoT devices for demonstration."""
        self.logger.info("🔧 Creating test IoT devices...")
        
        # Create camera device
        self.camera_device = IoTDevice(
            device_id="camera_001",
            device_type=DeviceType.CAMERA,
            capabilities={
                "gpu": True,
                "memory": 8192,  # 8GB
                "storage": 256,   # 256GB
                "network": 1000,  # 1Gbps
                "resolution": "4K",
                "fps": 30
            },
            location={"lat": 40.7128, "lon": -74.0060, "alt": 10}
        )
        
        # Create sensor device
        self.sensor_device = IoTDevice(
            device_id="sensor_001",
            device_type=DeviceType.SENSOR,
            capabilities={
                "gpu": False,
                "memory": 1024,   # 1GB
                "storage": 32,     # 32GB
                "network": 100,    # 100Mbps
                "sensor_types": ["temperature", "humidity", "pressure"],
                "sampling_rate": 1000  # 1kHz
            },
            location={"lat": 40.7128, "lon": -74.0060, "alt": 5}
        )
        
        # Create edge gateway
        self.gateway_device = IoTDevice(
            device_id="gateway_001",
            device_type=DeviceType.GATEWAY,
            capabilities={
                "gpu": True,
                "memory": 16384,  # 16GB
                "storage": 512,    # 512GB
                "network": 10000,  # 10Gbps
                "protocols": ["MQTT", "HTTP", "CoAP", "WebSocket"],
                "max_connections": 1000
            },
            location={"lat": 40.7128, "lon": -74.0060, "alt": 15}
        )
        
        # Create mobile device
        self.mobile_device = IoTDevice(
            device_id="mobile_001",
            device_type=DeviceType.MOBILE_DEVICE,
            capabilities={
                "gpu": True,
                "memory": 4096,   # 4GB
                "storage": 128,    # 128GB
                "network": 5000,   # 5G
                "os": "Android",
                "battery": 4000    # 4000mAh
            },
            location={"lat": 40.7128, "lon": -74.0060, "alt": 2}
        )
        
        self.logger.info("✅ Test IoT devices created successfully")
    
    def run_comprehensive_demo(self):
        """Run comprehensive Edge AI & IoT demonstration."""
        self.logger.info("🚀 Starting Comprehensive Advanced Edge AI & IoT Demo...")
        self.running = True
        
        try:
            # Run individual demos
            self.demo_results["system_initialization"] = self.run_system_initialization_demo()
            self.demo_results["iot_device_management"] = self.run_iot_device_management_demo()
            self.demo_results["edge_computing_optimization"] = self.run_edge_computing_optimization_demo()
            self.demo_results["real_time_inference"] = self.run_real_time_inference_demo()
            self.demo_results["edge_cloud_orchestration"] = self.run_edge_cloud_orchestration_demo()
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
            status = self.edge_ai_system.get_system_status()
            
            # Test different configurations
            minimal_config = create_minimal_edge_ai_config()
            minimal_system = create_advanced_edge_ai_iot_system(minimal_config)
            
            results = {
                "main_system_status": status,
                "minimal_system_status": minimal_system.get_system_status(),
                "config_comparison": {
                    "main_system": {
                        "edge_computing": self.edge_ai_config.enable_edge_computing,
                        "iot_management": self.edge_ai_config.enable_iot_management,
                        "real_time_inference": self.edge_ai_config.enable_real_time_inference,
                        "edge_cloud_orchestration": self.edge_ai_config.enable_edge_cloud_orchestration
                    },
                    "minimal_system": {
                        "edge_computing": minimal_config.enable_edge_computing,
                        "iot_management": minimal_config.enable_iot_management,
                        "real_time_inference": minimal_config.enable_real_time_inference,
                        "edge_cloud_orchestration": minimal_config.enable_edge_cloud_orchestration
                    }
                }
            }
            
            self.logger.info("✅ System Initialization Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ System Initialization Demo failed: {e}")
            return {"error": str(e)}
    
    def run_iot_device_management_demo(self) -> Dict[str, Any]:
        """Demo IoT device management capabilities."""
        self.logger.info("📱 Running IoT Device Management Demo...")
        
        try:
            results = {}
            
            # Register different device types
            camera_registered = self.edge_ai_system.register_device(self.camera_device)
            sensor_registered = self.edge_ai_system.register_device(self.sensor_device)
            gateway_registered = self.edge_ai_system.register_device(self.gateway_device)
            mobile_registered = self.edge_ai_system.register_device(self.mobile_device)
            
            # Update device resources
            self.camera_device.update_resources(cpu=0.3, memory=0.4, storage=0.2, network=0.6)
            self.sensor_device.update_resources(cpu=0.1, memory=0.2, storage=0.1, network=0.3)
            self.gateway_device.update_resources(cpu=0.5, memory=0.6, storage=0.3, network=0.8)
            self.mobile_device.update_resources(cpu=0.2, memory=0.3, storage=0.4, network=0.7)
            
            # Get device information
            camera_info = self.camera_device.get_device_info()
            sensor_info = self.sensor_device.get_device_info()
            gateway_info = self.gateway_device.get_device_info()
            mobile_info = self.mobile_device.get_device_info()
            
            # Test device discovery and monitoring
            all_devices = self.edge_ai_system.device_manager.get_all_devices()
            online_devices = self.edge_ai_system.device_manager.get_devices_by_status(DeviceStatus.ONLINE)
            camera_devices = self.edge_ai_system.device_manager.get_devices_by_type(DeviceType.CAMERA)
            
            results = {
                "device_registration": {
                    "camera": camera_registered,
                    "sensor": sensor_registered,
                    "gateway": gateway_registered,
                    "mobile": mobile_registered
                },
                "device_information": {
                    "camera": camera_info,
                    "sensor": sensor_info,
                    "gateway": gateway_info,
                    "mobile": mobile_info
                },
                "device_management": {
                    "total_devices": len(all_devices),
                    "online_devices": len(online_devices),
                    "camera_devices": len(camera_devices),
                    "device_types": [device.device_type.value for device in all_devices]
                }
            }
            
            self.logger.info("✅ IoT Device Management Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ IoT Device Management Demo failed: {e}")
            return {"error": str(e)}
    
    def run_edge_computing_optimization_demo(self) -> Dict[str, Any]:
        """Demo edge computing optimization capabilities."""
        self.logger.info("⚡ Running Edge Computing Optimization Demo...")
        
        try:
            results = {}
            
            # Create test models for optimization
            test_models = [
                {
                    "id": "image_classification_v1",
                    "name": "Image Classification Model",
                    "type": "cnn",
                    "requires_gpu": True,
                    "memory_required": 2048,
                    "latency_target_ms": 50
                },
                {
                    "id": "sensor_analysis_v1",
                    "name": "Sensor Data Analysis",
                    "type": "regression",
                    "requires_gpu": False,
                    "memory_required": 512,
                    "latency_target_ms": 100
                },
                {
                    "id": "object_detection_v1",
                    "name": "Object Detection Model",
                    "type": "yolo",
                    "requires_gpu": True,
                    "memory_required": 4096,
                    "latency_target_ms": 75
                },
                {
                    "id": "anomaly_detection_v1",
                    "name": "Anomaly Detection",
                    "type": "autoencoder",
                    "requires_gpu": False,
                    "memory_required": 1024,
                    "latency_target_ms": 150
                }
            ]
            
            # Run edge computing optimization
            optimization_result = self.edge_ai_system.optimize_edge_deployment(test_models)
            
            # Analyze optimization results
            deployment_plan = optimization_result["deployment_plan"]
            device_loads = optimization_result["device_loads"]
            optimization_score = optimization_result["optimization_score"]
            
            # Calculate optimization metrics
            total_models = len(test_models)
            deployed_models = len(deployment_plan)
            deployment_rate = deployed_models / total_models if total_models > 0 else 0
            
            # Analyze load distribution
            load_values = list(device_loads.values())
            load_variance = np.var(load_values) if len(load_values) > 1 else 0
            load_balance_score = max(0, 100 - load_variance * 10)
            
            results = {
                "optimization_result": optimization_result,
                "deployment_analysis": {
                    "total_models": total_models,
                    "deployed_models": deployed_models,
                    "deployment_rate": deployment_rate,
                    "deployment_plan": deployment_plan
                },
                "load_analysis": {
                    "device_loads": device_loads,
                    "load_variance": load_variance,
                    "load_balance_score": load_balance_score
                },
                "optimization_metrics": {
                    "optimization_score": optimization_score,
                    "overall_score": (optimization_score + load_balance_score) / 2
                }
            }
            
            self.logger.info("✅ Edge Computing Optimization Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Edge Computing Optimization Demo failed: {e}")
            return {"error": str(e)}
    
    def run_real_time_inference_demo(self) -> Dict[str, Any]:
        """Demo real-time inference capabilities."""
        self.logger.info("⚡ Running Real-Time Inference Demo...")
        
        try:
            results = {}
            
            # Test different inference modes
            inference_modes = [
                InferenceMode.REAL_TIME,
                InferenceMode.BATCH,
                InferenceMode.STREAMING,
                InferenceMode.HYBRID
            ]
            
            inference_results = {}
            
            for mode in inference_modes:
                # Execute inference on camera device
                camera_inference = self.edge_ai_system.execute_inference(
                    "camera_001",
                    "image_classification",
                    {"image_data": "sample_image_001.jpg"},
                    mode
                )
                
                # Execute inference on sensor device
                sensor_inference = self.edge_ai_system.execute_inference(
                    "sensor_001",
                    "sensor_analysis",
                    {"sensor_data": [23.5, 65.2, 1013.25]},
                    mode
                )
                
                inference_results[mode.value] = {
                    "camera": camera_inference,
                    "sensor": sensor_inference
                }
            
            # Get inference statistics
            inference_stats = self.edge_ai_system.inference_engine.get_inference_stats()
            
            # Calculate performance metrics
            total_requests = inference_stats["total_requests"]
            success_rate = inference_stats["successful_requests"] / total_requests if total_requests > 0 else 0
            average_latency = inference_stats["average_latency_ms"]
            
            # Check latency targets
            latency_target = self.edge_ai_config.inference_latency_target_ms
            latency_compliance = average_latency <= latency_target if average_latency > 0 else False
            
            results = {
                "inference_results": inference_results,
                "inference_statistics": inference_stats,
                "performance_metrics": {
                    "total_requests": total_requests,
                    "success_rate": success_rate,
                    "average_latency_ms": average_latency,
                    "latency_target_ms": latency_target,
                    "latency_compliance": latency_compliance
                },
                "device_performance": {
                    "camera_device": {
                        "device_id": "camera_001",
                        "inference_count": len([r for r in inference_results.values() if r["camera"]["success"]]),
                        "average_latency": np.mean([r["camera"]["latency_ms"] for r in inference_results.values() if r["camera"]["success"]])
                    },
                    "sensor_device": {
                        "device_id": "sensor_001",
                        "inference_count": len([r for r in inference_results.values() if r["sensor"]["success"]]),
                        "average_latency": np.mean([r["sensor"]["latency_ms"] for r in inference_results.values() if r["sensor"]["success"]])
                    }
                }
            }
            
            self.logger.info("✅ Real-Time Inference Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Real-Time Inference Demo failed: {e}")
            return {"error": str(e)}
    
    def run_edge_cloud_orchestration_demo(self) -> Dict[str, Any]:
        """Demo edge-cloud orchestration capabilities."""
        self.logger.info("☁️ Running Edge-Cloud Orchestration Demo...")
        
        try:
            results = {}
            
            # Test different workload types
            test_workloads = [
                {
                    "id": "ultra_low_latency_workload",
                    "type": "real_time_processing",
                    "latency_requirement_ms": 50,
                    "data_size_mb": 10,
                    "priority": "high"
                },
                {
                    "id": "low_latency_workload",
                    "type": "interactive_processing",
                    "latency_requirement_ms": 200,
                    "data_size_mb": 50,
                    "priority": "medium"
                },
                {
                    "id": "standard_workload",
                    "type": "batch_processing",
                    "latency_requirement_ms": 1000,
                    "data_size_mb": 200,
                    "priority": "low"
                },
                {
                    "id": "large_data_workload",
                    "type": "data_analytics",
                    "latency_requirement_ms": 5000,
                    "data_size_mb": 1000,
                    "priority": "low"
                }
            ]
            
            orchestration_results = {}
            
            for workload in test_workloads:
                # Orchestrate workload
                orchestration_result = self.edge_ai_system.orchestrate_workload(workload)
                orchestration_results[workload["id"]] = orchestration_result
            
            # Analyze orchestration results
            total_workloads = len(test_workloads)
            edge_workloads = len([r for r in orchestration_results.values() if r["placement"]["target_tier"] == "edge"])
            cloud_workloads = len([r for r in orchestration_results.values() if r["placement"]["target_tier"] == "cloud"])
            hybrid_workloads = len([r for r in orchestration_results.values() if r["placement"]["target_tier"] not in ["edge", "cloud"]])
            
            # Calculate average estimated latency
            estimated_latencies = [r["placement"]["estimated_latency_ms"] for r in orchestration_results.values()]
            average_estimated_latency = np.mean(estimated_latencies) if estimated_latencies else 0
            
            # Test data synchronization
            sync_data = {
                "id": "demo_sync_data",
                "type": "inference_results",
                "data": {"results": "sample_inference_results"},
                "timestamp": time.time()
            }
            
            sync_success = self.edge_ai_system.orchestrator.sync_edge_cloud_data(sync_data)
            
            results = {
                "orchestration_results": orchestration_results,
                "workload_analysis": {
                    "total_workloads": total_workloads,
                    "edge_workloads": edge_workloads,
                    "cloud_workloads": cloud_workloads,
                    "hybrid_workloads": hybrid_workloads,
                    "edge_percentage": edge_workloads / total_workloads if total_workloads > 0 else 0,
                    "cloud_percentage": cloud_workloads / total_workloads if total_workloads > 0 else 0
                },
                "latency_analysis": {
                    "estimated_latencies": estimated_latencies,
                    "average_estimated_latency_ms": average_estimated_latency,
                    "min_latency_ms": min(estimated_latencies) if estimated_latencies else 0,
                    "max_latency_ms": max(estimated_latencies) if estimated_latencies else 0
                },
                "data_sync": {
                    "sync_success": sync_success,
                    "sync_data": sync_data
                }
            }
            
            self.logger.info("✅ Edge-Cloud Orchestration Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Edge-Cloud Orchestration Demo failed: {e}")
            return {"error": str(e)}
    
    def run_advanced_features_demo(self) -> Dict[str, Any]:
        """Demo advanced Edge AI & IoT features."""
        self.logger.info("🚀 Running Advanced Features Demo...")
        
        try:
            results = {}
            
            # Test device auto-provisioning
            auto_provisioning_results = {}
            for device in [self.camera_device, self.sensor_device, self.gateway_device, self.mobile_device]:
                device_info = device.get_device_info()
                auto_provisioning_results[device.device_id] = {
                    "device_type": device_info["device_type"],
                    "models_installed": len(device.models),
                    "auto_provisioned": len(device.models) > 0
                }
            
            # Test resource monitoring
            resource_monitoring = {}
            for device in [self.camera_device, self.sensor_device, self.gateway_device, self.mobile_device]:
                resource_monitoring[device.device_id] = {
                    "cpu_usage": device.resources["cpu"],
                    "memory_usage": device.resources["memory"],
                    "storage_usage": device.resources["storage"],
                    "network_usage": device.resources["network"]
                }
            
            # Test edge optimization features
            edge_optimization_features = {
                "model_compression": self.edge_ai_config.enable_model_compression,
                "quantization": self.edge_ai_config.enable_quantization,
                "pruning": self.edge_ai_config.enable_pruning,
                "edge_caching": self.edge_ai_config.enable_edge_caching,
                "load_balancing": self.edge_ai_config.enable_load_balancing,
                "failover": self.edge_ai_config.enable_failover
            }
            
            # Test security features
            security_features = {
                "edge_security": self.edge_ai_config.enable_edge_security,
                "device_authentication": self.edge_ai_config.enable_device_authentication,
                "data_encryption": self.edge_ai_config.enable_data_encryption
            }
            
            # Test system scalability
            system_status = self.edge_ai_system.get_system_status()
            
            results = {
                "auto_provisioning": auto_provisioning_results,
                "resource_monitoring": resource_monitoring,
                "edge_optimization_features": edge_optimization_features,
                "security_features": security_features,
                "system_scalability": {
                    "total_devices": system_status["total_devices"],
                    "online_devices": system_status["online_devices"],
                    "edge_nodes": system_status["edge_nodes"],
                    "cloud_services": system_status["cloud_services"],
                    "inference_stats": system_status["inference_stats"]
                }
            }
            
            self.logger.info("✅ Advanced Features Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Advanced Features Demo failed: {e}")
            return {"error": str(e)}
    
    def save_demo_results(self, output_path: str = "edge_ai_iot_demo_results.json"):
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
            if hasattr(self, 'edge_ai_system'):
                self.edge_ai_system.shutdown()
            
            # Remove test directory
            import shutil
            if hasattr(self, 'test_dir') and self.test_dir.exists():
                shutil.rmtree(self.test_dir)
            
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

def main():
    """Main demo execution."""
    demo = AdvancedEdgeAIIoTDemo()
    
    try:
        # Run comprehensive demo
        results = demo.run_comprehensive_demo()
        
        # Save results
        demo.save_demo_results()
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 ADVANCED EDGE AI & IOT SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📱 Total IoT Devices: {len(results['iot_device_management']['device_management']['total_devices'])}")
        print(f"⚡ Edge Optimization Score: {results['edge_computing_optimization']['optimization_metrics']['optimization_score']:.1f}")
        print(f"🚀 Real-Time Inference Success Rate: {results['real_time_inference']['performance_metrics']['success_rate']:.1%}")
        print(f"☁️ Edge-Cloud Orchestration: {results['edge_cloud_orchestration']['workload_analysis']['edge_percentage']:.1%} edge workloads")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
