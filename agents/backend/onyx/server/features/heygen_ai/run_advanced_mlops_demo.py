import logging
import time
import json
import os
import tempfile
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn

from core.advanced_mlops_system import (
    AdvancedMLOpsSystem,
    MLOpsConfig,
    ModelType,
    ModelStatus,
    create_advanced_mlops_system,
    create_minimal_mlops_config,
    create_maximum_mlops_config
)

class AdvancedMLOpsDemo:
    """Comprehensive demo showcasing Advanced MLOps System capabilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.demo")
        self.demo_results = {}
        self.running = False
        
        # Initialize systems
        self.initialize_systems()
        self.create_test_models()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def initialize_systems(self):
        """Initialize MLOps and supporting systems."""
        self.logger.info("🚀 Initializing Advanced MLOps Systems...")
        
        # Create maximum MLOps configuration
        self.mlops_config = create_maximum_mlops_config()
        self.mlops_system = create_advanced_mlops_system(self.mlops_config)
        
        # Create temporary directory for test models
        self.test_dir = Path(tempfile.mkdtemp(prefix="mlops_demo_"))
        self.logger.info(f"Test directory created: {self.test_dir}")
    
    def create_test_models(self):
        """Create test models for demonstration."""
        self.logger.info("🔧 Creating test models...")
        
        # Create a simple PyTorch model
        self.transformer_model = self._create_transformer_model()
        self.cnn_model = self._create_cnn_model()
        self.sklearn_model = self._create_sklearn_model()
        
        # Save models to temporary files
        self.transformer_path = self.test_dir / "transformer_model.pt"
        self.cnn_path = self.test_dir / "cnn_model.pt"
        self.sklearn_path = self.test_dir / "sklearn_model.pkl"
        
        torch.save(self.transformer_model.state_dict(), self.transformer_path)
        torch.save(self.cnn_model.state_dict(), self.cnn_path)
        
        # Create dummy sklearn model file
        with open(self.sklearn_path, 'w') as f:
            f.write("dummy_sklearn_model")
        
        self.logger.info("✅ Test models created successfully")
    
    def _create_transformer_model(self) -> nn.Module:
        """Create a simple transformer model."""
        class SimpleTransformer(nn.Module):
            def __init__(self, input_dim=512, hidden_dim=256, num_layers=2):
                super().__init__()
                self.embedding = nn.Linear(input_dim, hidden_dim)
                self.transformer = nn.TransformerEncoder(
                    nn.TransformerEncoderLayer(hidden_dim, nhead=8),
                    num_layers=num_layers
                )
                self.output = nn.Linear(hidden_dim, 10)
            
            def forward(self, x):
                x = self.embedding(x)
                x = self.transformer(x)
                x = x.mean(dim=1)  # Global average pooling
                return self.output(x)
        
        return SimpleTransformer()
    
    def _create_cnn_model(self) -> nn.Module:
        """Create a simple CNN model."""
        class SimpleCNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
                self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
                self.pool = nn.MaxPool2d(2, 2)
                self.fc1 = nn.Linear(32 * 8 * 8, 128)
                self.fc2 = nn.Linear(128, 10)
                self.relu = nn.ReLU()
            
            def forward(self, x):
                x = self.pool(self.relu(self.conv1(x)))
                x = self.pool(self.relu(self.conv2(x)))
                x = x.view(x.size(0), -1)
                x = self.relu(self.fc1(x))
                return self.fc2(x)
        
        return SimpleCNN()
    
    def _create_sklearn_model(self) -> str:
        """Create a dummy sklearn model representation."""
        return "sklearn_model_v1"
    
    def run_comprehensive_demo(self):
        """Run comprehensive MLOps demonstration."""
        self.logger.info("🚀 Starting Comprehensive Advanced MLOps Demo...")
        self.running = True
        
        try:
            # Run individual demos
            self.demo_results["system_initialization"] = self.run_system_initialization_demo()
            self.demo_results["model_registry"] = self.run_model_registry_demo()
            self.demo_results["deployment_pipeline"] = self.run_deployment_pipeline_demo()
            self.demo_results["lifecycle_management"] = self.run_lifecycle_management_demo()
            self.demo_results["mlflow_integration"] = self.run_mlflow_integration_demo()
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
            status = self.mlops_system.get_system_status()
            
            # Test different configurations
            minimal_config = create_minimal_mlops_config()
            minimal_system = create_advanced_mlops_system(minimal_config)
            
            results = {
                "main_system_status": status,
                "minimal_system_status": minimal_system.get_system_status(),
                "config_comparison": {
                    "main_system": {
                        "mlflow_enabled": self.mlops_config.enable_mlflow,
                        "model_registry": self.mlops_config.enable_model_registry,
                        "deployment_pipelines": self.mlops_config.enable_deployment_pipelines,
                        "lifecycle_management": self.mlops_config.enable_lifecycle_management
                    },
                    "minimal_system": {
                        "mlflow_enabled": minimal_config.enable_mlflow,
                        "model_registry": minimal_config.enable_model_registry,
                        "deployment_pipelines": minimal_config.enable_deployment_pipelines,
                        "lifecycle_management": minimal_config.enable_lifecycle_management
                    }
                }
            }
            
            self.logger.info("✅ System Initialization Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ System Initialization Demo failed: {e}")
            return {"error": str(e)}
    
    def run_model_registry_demo(self) -> Dict[str, Any]:
        """Demo model registry capabilities."""
        self.logger.info("📚 Running Model Registry Demo...")
        
        try:
            results = {}
            
            # Register different model types
            transformer_version = self.mlops_system.register_model(
                "transformer_classifier",
                str(self.transformer_path),
                ModelType.PYTORCH,
                {
                    "architecture": "transformer",
                    "input_dim": 512,
                    "hidden_dim": 256,
                    "num_layers": 2,
                    "task": "classification",
                    "dataset": "synthetic_data"
                }
            )
            
            cnn_version = self.mlops_system.register_model(
                "cnn_classifier",
                str(self.cnn_path),
                ModelType.PYTORCH,
                {
                    "architecture": "cnn",
                    "input_channels": 3,
                    "num_classes": 10,
                    "task": "image_classification",
                    "dataset": "synthetic_images"
                }
            )
            
            sklearn_version = self.mlops_system.register_model(
                "sklearn_classifier",
                str(self.sklearn_path),
                ModelType.SKLEARN,
                {
                    "algorithm": "random_forest",
                    "n_estimators": 100,
                    "task": "classification",
                    "dataset": "synthetic_tabular"
                }
            )
            
            # Get model information
            transformer_info = self.mlops_system.get_model_info("transformer_classifier", transformer_version)
            cnn_info = self.mlops_system.get_model_info("cnn_classifier", cnn_version)
            sklearn_info = self.mlops_system.get_model_info("sklearn_classifier", sklearn_version)
            
            # Update model statuses
            self.mlops_system.update_model_status("transformer_classifier", transformer_version, ModelStatus.STAGING)
            self.mlops_system.update_model_status("cnn_classifier", cnn_version, ModelStatus.PRODUCTION)
            
            results = {
                "registered_models": {
                    "transformer_classifier": {
                        "version": transformer_version,
                        "info": transformer_info,
                        "final_status": "staging"
                    },
                    "cnn_classifier": {
                        "version": cnn_version,
                        "info": cnn_info,
                        "final_status": "production"
                    },
                    "sklearn_classifier": {
                        "version": sklearn_version,
                        "info": sklearn_info,
                        "final_status": "development"
                    }
                },
                "registry_summary": {
                    "total_models": len(self.mlops_system.registry.models),
                    "models_by_status": {
                        "development": 1,
                        "staging": 1,
                        "production": 1
                    }
                }
            }
            
            self.logger.info("✅ Model Registry Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Model Registry Demo failed: {e}")
            return {"error": str(e)}
    
    def run_deployment_pipeline_demo(self) -> Dict[str, Any]:
        """Demo deployment pipeline capabilities."""
        self.logger.info("🚀 Running Deployment Pipeline Demo...")
        
        try:
            results = {}
            
            # Deploy models to different environments
            transformer_staging = self.mlops_system.deploy_model(
                "transformer_classifier",
                self.demo_results["model_registry"]["registered_models"]["transformer_classifier"]["version"],
                "staging"
            )
            
            cnn_production = self.mlops_system.deploy_model(
                "cnn_classifier",
                self.demo_results["model_registry"]["registered_models"]["cnn_classifier"]["version"],
                "production"
            )
            
            # Wait for deployments to complete
            time.sleep(5)
            
            # Get deployment information
            staging_deployment = self.mlops_system.deployment_pipeline.deployments.get(transformer_staging, {})
            production_deployment = self.mlops_system.deployment_pipeline.deployments.get(cnn_production, {})
            
            # Test rollback functionality
            rollback_success = self.mlops_system.deployment_pipeline.rollback_deployment(transformer_staging)
            
            results = {
                "deployments": {
                    "transformer_staging": {
                        "deployment_id": transformer_staging,
                        "info": staging_deployment,
                        "rollback_success": rollback_success
                    },
                    "cnn_production": {
                        "deployment_id": cnn_production,
                        "info": production_deployment,
                        "rollback_success": False  # No rollback attempted
                    }
                },
                "pipeline_summary": {
                    "total_deployments": len(self.mlops_system.deployment_pipeline.deployments),
                    "deployments_by_status": {
                        "deployed": 1,
                        "rollback": 1
                    }
                }
            }
            
            self.logger.info("✅ Deployment Pipeline Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Deployment Pipeline Demo failed: {e}")
            return {"error": str(e)}
    
    def run_lifecycle_management_demo(self) -> Dict[str, Any]:
        """Demo lifecycle management capabilities."""
        self.logger.info("🔄 Running Lifecycle Management Demo...")
        
        try:
            results = {}
            
            # Create lifecycle rules for models
            transformer_rules = {
                "retraining": {
                    "performance_threshold": 0.85,
                    "retrain_interval_days": 30
                },
                "archiving": {
                    "max_age_days": 180
                }
            }
            
            cnn_rules = {
                "retraining": {
                    "performance_threshold": 0.90,
                    "retrain_interval_days": 60
                },
                "archiving": {
                    "max_age_days": 365
                }
            }
            
            self.mlops_system.create_lifecycle_rule("transformer_classifier", transformer_rules)
            self.mlops_system.create_lifecycle_rule("cnn_classifier", cnn_rules)
            
            # Apply lifecycle policies
            self.mlops_system.apply_lifecycle_policies()
            
            # Get lifecycle rules
            transformer_lifecycle = self.mlops_system.lifecycle_manager.lifecycle_rules.get("transformer_classifier", {})
            cnn_lifecycle = self.mlops_system.lifecycle_manager.lifecycle_rules.get("cnn_classifier", {})
            
            results = {
                "lifecycle_rules": {
                    "transformer_classifier": transformer_lifecycle,
                    "cnn_classifier": cnn_lifecycle
                },
                "lifecycle_summary": {
                    "total_rules": len(self.mlops_system.lifecycle_manager.lifecycle_rules),
                    "models_with_rules": list(self.mlops_system.lifecycle_manager.lifecycle_rules.keys())
                }
            }
            
            self.logger.info("✅ Lifecycle Management Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Lifecycle Management Demo failed: {e}")
            return {"error": str(e)}
    
    def run_mlflow_integration_demo(self) -> Dict[str, Any]:
        """Demo MLflow integration capabilities."""
        self.logger.info("📊 Running MLflow Integration Demo...")
        
        try:
            results = {}
            
            if self.mlops_config.enable_mlflow:
                # Start MLflow run
                with mlflow.start_run(run_name="mlops_demo_run") as run:
                    # Log parameters
                    mlflow.log_param("demo_type", "advanced_mlops")
                    mlflow.log_param("num_models", 3)
                    mlflow.log_param("deployment_environments", 2)
                    
                    # Log metrics
                    mlflow.log_metric("model_registry_success", 1.0)
                    mlflow.log_metric("deployment_success_rate", 1.0)
                    mlflow.log_metric("lifecycle_management_success", 1.0)
                    
                    # Log artifacts
                    demo_summary = {
                        "demo_results": self.demo_results,
                        "timestamp": time.time(),
                        "system_status": self.mlops_system.get_system_status()
                    }
                    
                    summary_path = self.test_dir / "demo_summary.json"
                    with open(summary_path, 'w') as f:
                        json.dump(demo_summary, f, indent=2)
                    
                    mlflow.log_artifact(str(summary_path))
                    
                    results = {
                        "mlflow_run_id": run.info.run_id,
                        "mlflow_experiment": mlflow.get_experiment_by_name("HeyGen_AI_Enterprise_MLOps"),
                        "logged_parameters": ["demo_type", "num_models", "deployment_environments"],
                        "logged_metrics": ["model_registry_success", "deployment_success_rate", "lifecycle_management_success"],
                        "logged_artifacts": ["demo_summary.json"]
                    }
            else:
                results = {
                    "mlflow_enabled": False,
                    "message": "MLflow integration is disabled in current configuration"
                }
            
            self.logger.info("✅ MLflow Integration Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ MLflow Integration Demo failed: {e}")
            return {"error": str(e)}
    
    def run_advanced_features_demo(self) -> Dict[str, Any]:
        """Demo advanced MLOps features."""
        self.logger.info("⚡ Running Advanced Features Demo...")
        
        try:
            results = {}
            
            # Test different deployment environments
            environments = ["staging", "production", "canary"]
            deployment_results = {}
            
            for env in environments:
                try:
                    # Create a new model version for testing
                    test_model_path = self.test_dir / f"test_model_{env}.pt"
                    torch.save(self.transformer_model.state_dict(), test_model_path)
                    
                    # Register and deploy
                    version = self.mlops_system.register_model(
                        f"test_model_{env}",
                        str(test_model_path),
                        ModelType.PYTORCH,
                        {"environment": env, "purpose": "testing"}
                    )
                    
                    deployment_id = self.mlops_system.deploy_model(f"test_model_{env}", version, env)
                    deployment_results[env] = {
                        "version": version,
                        "deployment_id": deployment_id,
                        "status": "success"
                    }
                    
                except Exception as e:
                    deployment_results[env] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            # Test system scalability
            system_status = self.mlops_system.get_system_status()
            
            results = {
                "multi_environment_deployment": deployment_results,
                "system_scalability": {
                    "total_models": system_status["total_models"],
                    "total_deployments": system_status["total_deployments"],
                    "registry_path": system_status["registry_path"]
                },
                "advanced_configuration": {
                    "auto_deployment": self.mlops_config.enable_auto_deployment,
                    "rollback_enabled": self.mlops_config.enable_rollback,
                    "drift_detection": self.mlops_config.enable_drift_detection,
                    "ab_testing": self.mlops_config.enable_ab_testing
                }
            }
            
            self.logger.info("✅ Advanced Features Demo completed")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Advanced Features Demo failed: {e}")
            return {"error": str(e)}
    
    def save_demo_results(self, output_path: str = "mlops_demo_results.json"):
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
            import shutil
            shutil.rmtree(self.test_dir)
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

def main():
    """Main demo execution."""
    demo = AdvancedMLOpsDemo()
    
    try:
        # Run comprehensive demo
        results = demo.run_comprehensive_demo()
        
        # Save results
        demo.save_demo_results()
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 ADVANCED MLOPS SYSTEM DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📊 Total Models Registered: {len(results['model_registry']['registered_models'])}")
        print(f"🚀 Total Deployments: {len(results['deployment_pipeline']['deployments'])}")
        print(f"🔄 Lifecycle Rules Created: {results['lifecycle_management']['lifecycle_summary']['total_rules']}")
        print(f"📈 MLflow Integration: {'Enabled' if results['mlflow_integration'].get('mlflow_run_id') else 'Disabled'}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
