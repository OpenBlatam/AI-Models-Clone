#!/usr/bin/env python3
"""
Advanced AI Model Management System Demo
Comprehensive demonstration of enterprise-grade model lifecycle management
"""

import logging
import time
import json
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import os

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from advanced_ai_model_management_system import (
    AdvancedAIModelManagementSystem,
    ModelConfig, ModelType, ModelStatus, DeploymentStrategy, PerformanceMetric,
    ModelRegistryConfig, AutoMLConfig, DeploymentConfig,
    ModelMetadata, ModelPerformance, ModelVersion, ExperimentResult
)

# ===== DEMO CONFIGURATION =====

class DemoConfig:
    """Configuration for the demo."""
    def __init__(self):
        self.demo_duration = 300  # 5 minutes
        self.model_training_interval = 30  # seconds
        self.performance_monitoring_interval = 10  # seconds
        self.deployment_demonstration = True
        self.automl_demonstration = True
        self.performance_analytics = True
        self.model_comparison = True
        self.auto_retrain_demonstration = True

# ===== DEMO DATA GENERATORS =====

class DemoDataGenerator:
    """Generate demo data for model training and testing."""
    
    @staticmethod
    def generate_classification_data(n_samples: int = 1000, n_features: int = 10) -> pd.DataFrame:
        """Generate classification dataset."""
        try:
            # Generate features
            X = np.random.randn(n_samples, n_features)
            
            # Generate target with some pattern
            y = (X[:, 0] + X[:, 1] * 2 + np.random.randn(n_samples) * 0.1 > 0).astype(int)
            
            # Create DataFrame
            feature_names = [f'feature_{i}' for i in range(n_features)]
            data = pd.DataFrame(X, columns=feature_names)
            data['target'] = y
            
            return data
            
        except Exception as e:
            logging.error(f"Failed to generate classification data: {e}")
            raise
    
    @staticmethod
    def generate_regression_data(n_samples: int = 1000, n_features: int = 10) -> pd.DataFrame:
        """Generate regression dataset."""
        try:
            # Generate features
            X = np.random.randn(n_samples, n_features)
            
            # Generate target with linear relationship
            y = X[:, 0] * 2 + X[:, 1] * 1.5 + np.random.randn(n_samples) * 0.1
            
            # Create DataFrame
            feature_names = [f'feature_{i}' for i in range(n_features)]
            data = pd.DataFrame(X, columns=feature_names)
            data['target'] = y
            
            return data
            
        except Exception as e:
            logging.error(f"Failed to generate regression data: {e}")
            raise
    
    @staticmethod
    def generate_time_series_data(n_samples: int = 1000) -> pd.DataFrame:
        """Generate time series dataset."""
        try:
            # Generate time series with trend and seasonality
            t = np.arange(n_samples)
            trend = 0.01 * t
            seasonality = 0.5 * np.sin(2 * np.pi * t / 100)
            noise = np.random.randn(n_samples) * 0.1
            
            y = trend + seasonality + noise
            
            # Create features
            data = pd.DataFrame({
                'timestamp': pd.date_range('2024-01-01', periods=n_samples, freq='H'),
                'value': y,
                'trend': trend,
                'seasonality': seasonality,
                'noise': noise
            })
            
            return data
            
        except Exception as e:
            logging.error(f"Failed to generate time series data: {e}")
            raise

# ===== DEMO SCENARIOS =====

class ModelTrainingDemo:
    """Demonstrate model training capabilities."""
    
    def __init__(self, model_system: AdvancedAIModelManagementSystem):
        self.model_system = model_system
        self.logger = logging.getLogger(f"{__name__}.ModelTrainingDemo")
        self.trained_models = []
    
    def run_classification_training_demo(self) -> str:
        """Run classification model training demo."""
        try:
            self.logger.info("🚀 Starting Classification Model Training Demo")
            
            # Generate data
            data = DemoDataGenerator.generate_classification_data(1000, 10)
            
            # Create model configuration
            model_config = ModelConfig(
                name="Classification_Demo_Model",
                model_type=ModelType.CLASSIFICATION,
                algorithm="random_forest",
                hyperparameters={
                    'n_estimators': 100,
                    'max_depth': 10,
                    'random_state': 42
                },
                target_column="target",
                evaluation_metrics=[PerformanceMetric.ACCURACY, PerformanceMetric.F1_SCORE],
                auto_retrain=True,
                retrain_threshold=0.05
            )
            
            # Train model
            model_id = self.model_system.train_model(model_config, data)
            self.trained_models.append(model_id)
            
            self.logger.info(f"✅ Classification model trained successfully: {model_id}")
            return model_id
            
        except Exception as e:
            self.logger.error(f"Failed to run classification training demo: {e}")
            raise
    
    def run_regression_training_demo(self) -> str:
        """Run regression model training demo."""
        try:
            self.logger.info("🚀 Starting Regression Model Training Demo")
            
            # Generate data
            data = DemoDataGenerator.generate_regression_data(1000, 10)
            
            # Create model configuration
            model_config = ModelConfig(
                name="Regression_Demo_Model",
                model_type=ModelType.REGRESSION,
                algorithm="xgboost",
                hyperparameters={
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'random_state': 42
                },
                target_column="target",
                evaluation_metrics=[PerformanceMetric.R2_SCORE, PerformanceMetric.MAE],
                auto_retrain=True,
                retrain_threshold=0.05
            )
            
            # Train model
            model_id = self.model_system.train_model(model_config, data)
            self.trained_models.append(model_id)
            
            self.logger.info(f"✅ Regression model trained successfully: {model_id}")
            return model_id
            
        except Exception as e:
            self.logger.error(f"Failed to run regression training demo: {e}")
            raise
    
    def run_automl_demo(self) -> str:
        """Run AutoML demonstration."""
        try:
            self.logger.info("🚀 Starting AutoML Demonstration")
            
            # Generate data
            data = DemoDataGenerator.generate_classification_data(1500, 15)
            
            # Create AutoML model configuration
            model_config = ModelConfig(
                name="AutoML_Demo_Model",
                model_type=ModelType.CLASSIFICATION,
                algorithm="random_forest",  # Will be optimized by AutoML
                hyperparameters={},  # Will be optimized
                target_column="target",
                evaluation_metrics=[PerformanceMetric.ACCURACY, PerformanceMetric.ROC_AUC],
                auto_retrain=True,
                retrain_threshold=0.03
            )
            
            # Train with AutoML
            model_id = self.model_system.train_model(model_config, data)
            self.trained_models.append(model_id)
            
            self.logger.info(f"✅ AutoML model trained successfully: {model_id}")
            return model_id
            
        except Exception as e:
            self.logger.error(f"Failed to run AutoML demo: {e}")
            raise

class ModelDeploymentDemo:
    """Demonstrate model deployment capabilities."""
    
    def __init__(self, model_system: AdvancedAIModelManagementSystem):
        self.model_system = model_system
        self.logger = logging.getLogger(f"{__name__}.ModelDeploymentDemo")
        self.deployed_models = []
    
    def run_deployment_demo(self, model_id: str) -> str:
        """Run model deployment demonstration."""
        try:
            self.logger.info(f"🚀 Starting Deployment Demo for Model: {model_id}")
            
            # Deploy with blue-green strategy
            deployment_id = self.model_system.deploy_model(
                model_id, 
                DeploymentStrategy.BLUE_GREEN
            )
            self.deployed_models.append(deployment_id)
            
            self.logger.info(f"✅ Model deployed successfully: {deployment_id}")
            return deployment_id
            
        except Exception as e:
            self.logger.error(f"Failed to run deployment demo: {e}")
            raise
    
    def run_canary_deployment_demo(self, model_id: str) -> str:
        """Run canary deployment demonstration."""
        try:
            self.logger.info(f"🚀 Starting Canary Deployment Demo for Model: {model_id}")
            
            # Deploy with canary strategy
            deployment_id = self.model_system.deploy_model(
                model_id, 
                DeploymentStrategy.CANARY
            )
            self.deployed_models.append(deployment_id)
            
            self.logger.info(f"✅ Canary deployment successful: {deployment_id}")
            return deployment_id
            
        except Exception as e:
            self.logger.error(f"Failed to run canary deployment demo: {e}")
            raise
    
    def run_ab_testing_demo(self, model_id: str) -> str:
        """Run A/B testing deployment demonstration."""
        try:
            self.logger.info(f"🚀 Starting A/B Testing Demo for Model: {model_id}")
            
            # Deploy with A/B testing strategy
            deployment_id = self.model_system.deploy_model(
                model_id, 
                DeploymentStrategy.A_B_TESTING
            )
            self.deployed_models.append(deployment_id)
            
            self.logger.info(f"✅ A/B testing deployment successful: {deployment_id}")
            return deployment_id
            
        except Exception as e:
            self.logger.error(f"Failed to run A/B testing demo: {e}")
            raise

class PerformanceAnalyticsDemo:
    """Demonstrate performance analytics capabilities."""
    
    def __init__(self, model_system: AdvancedAIModelManagementSystem):
        self.model_system = model_system
        self.logger = logging.getLogger(f"{__name__}.PerformanceAnalyticsDemo")
        self.analytics_active = False
        self.analytics_thread = None
    
    def start_performance_analytics(self) -> None:
        """Start performance analytics demonstration."""
        try:
            self.analytics_active = True
            self.analytics_thread = threading.Thread(
                target=self._analytics_loop, 
                daemon=True
            )
            self.analytics_thread.start()
            
            self.logger.info("📊 Performance analytics started")
            
        except Exception as e:
            self.logger.error(f"Failed to start performance analytics: {e}")
    
    def _analytics_loop(self) -> None:
        """Performance analytics loop."""
        while self.analytics_active:
            try:
                # Analyze all deployed models
                for model_id in self.model_system.deployed_models:
                    self._analyze_model_performance(model_id)
                
                time.sleep(10)  # Analyze every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in analytics loop: {e}")
                time.sleep(10)
    
    def _analyze_model_performance(self, model_id: str) -> None:
        """Analyze individual model performance."""
        try:
            # Get performance summary
            summary = self.model_system.get_model_performance_summary(model_id)
            
            # Log key metrics
            if 'current_performance' in summary:
                current_perf = summary['current_performance']
                self.logger.info(f"📈 Model {model_id} Performance: {current_perf}")
            
            # Check for trends
            if 'performance_trend' in summary:
                trend = summary['performance_trend']
                if trend == 'degrading':
                    self.logger.warning(f"⚠️ Performance degradation detected for model: {model_id}")
                elif trend == 'improving':
                    self.logger.info(f"📈 Performance improvement detected for model: {model_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to analyze model performance: {e}")
    
    def stop_performance_analytics(self) -> None:
        """Stop performance analytics."""
        self.analytics_active = False
        if self.analytics_thread and self.analytics_thread.is_alive():
            self.analytics_thread.join(timeout=5)

class ModelComparisonDemo:
    """Demonstrate model comparison capabilities."""
    
    def __init__(self, model_system: AdvancedAIModelManagementSystem):
        self.model_system = model_system
        self.logger = logging.getLogger(f"{__name__}.ModelComparisonDemo")
    
    def run_model_comparison(self, model_ids: List[str]) -> Dict[str, Any]:
        """Run comprehensive model comparison."""
        try:
            self.logger.info("🔍 Starting Model Comparison Demo")
            
            comparison_results = {}
            
            for model_id in model_ids:
                # Get performance summary
                summary = self.model_system.get_model_performance_summary(model_id)
                comparison_results[model_id] = summary
            
            # Find best performing model
            best_model = self._find_best_model(comparison_results)
            
            # Generate comparison report
            report = self._generate_comparison_report(comparison_results, best_model)
            
            self.logger.info(f"✅ Model comparison completed. Best model: {best_model}")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to run model comparison: {e}")
            raise
    
    def _find_best_model(self, comparison_results: Dict[str, Any]) -> str:
        """Find the best performing model."""
        best_model = None
        best_score = -1
        
        for model_id, results in comparison_results.items():
            if 'current_performance' in results:
                current_perf = results['current_performance']
                if 'accuracy' in current_perf:
                    score = current_perf['accuracy']
                    if score > best_score:
                        best_score = score
                        best_model = model_id
        
        return best_model
    
    def _generate_comparison_report(self, comparison_results: Dict[str, Any], best_model: str) -> Dict[str, Any]:
        """Generate comprehensive comparison report."""
        return {
            "comparison_timestamp": datetime.now(),
            "total_models_compared": len(comparison_results),
            "best_model": best_model,
            "model_rankings": self._rank_models(comparison_results),
            "performance_summary": comparison_results,
            "recommendations": self._generate_recommendations(comparison_results, best_model)
        }
    
    def _rank_models(self, comparison_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank models by performance."""
        rankings = []
        
        for model_id, results in comparison_results.items():
            if 'current_performance' in results:
                current_perf = results['current_performance']
                score = current_perf.get('accuracy', 0.0)
                rankings.append({
                    "model_id": model_id,
                    "score": score,
                    "performance": current_perf
                })
        
        # Sort by score (descending)
        rankings.sort(key=lambda x: x['score'], reverse=True)
        
        return rankings
    
    def _generate_recommendations(self, comparison_results: Dict[str, Any], best_model: str) -> List[str]:
        """Generate recommendations based on comparison."""
        recommendations = []
        
        if best_model:
            recommendations.append(f"Deploy model {best_model} as it shows the best performance")
        
        # Check for underperforming models
        for model_id, results in comparison_results.items():
            if 'performance_trend' in results:
                trend = results['performance_trend']
                if trend == 'degrading':
                    recommendations.append(f"Consider retraining model {model_id} due to performance degradation")
        
        return recommendations

class AutoRetrainDemo:
    """Demonstrate auto-retraining capabilities."""
    
    def __init__(self, model_system: AdvancedAIModelManagementSystem):
        self.model_system = model_system
        self.logger = logging.getLogger(f"{__name__}.AutoRetrainDemo")
    
    def simulate_performance_degradation(self, model_id: str) -> None:
        """Simulate performance degradation to trigger auto-retrain."""
        try:
            self.logger.info(f"🎭 Simulating performance degradation for model: {model_id}")
            
            # Simulate degraded performance by adding poor performance data
            degraded_performance = ModelPerformance(
                model_id=model_id,
                timestamp=datetime.now(),
                metrics={
                    'accuracy': 0.5,  # Significantly lower than baseline
                    'precision': 0.5,
                    'recall': 0.5,
                    'f1_score': 0.5
                },
                dataset_split="production",
                execution_time=1.0,
                memory_usage=0.5,
                cpu_usage=0.8
            )
            
            # Add to performance history
            self.model_system.performance_history[model_id].append(degraded_performance)
            
            self.logger.info("✅ Performance degradation simulated")
            
        except Exception as e:
            self.logger.error(f"Failed to simulate performance degradation: {e}")
    
    def monitor_auto_retrain(self, model_id: str) -> None:
        """Monitor auto-retraining process."""
        try:
            self.logger.info(f"👀 Monitoring auto-retrain for model: {model_id}")
            
            # Check if model is being retrained
            if model_id in self.model_system.model_versions:
                versions = self.model_system.model_versions[model_id]
                latest_version = versions[-1]
                
                if latest_version.status == ModelStatus.TRAINING:
                    self.logger.info("🔄 Model is currently being retrained")
                elif latest_version.status == ModelStatus.DEPLOYED:
                    self.logger.info("✅ Model retraining completed and deployed")
                elif latest_version.status == ModelStatus.ERROR:
                    self.logger.error("❌ Model retraining failed")
            
        except Exception as e:
            self.logger.error(f"Failed to monitor auto-retrain: {e}")

# ===== MAIN DEMO ORCHESTRATOR =====

class AdvancedAIModelManagementDemo:
    """Main demo orchestrator for the Advanced AI Model Management System."""
    
    def __init__(self):
        self.config = DemoConfig()
        self.logger = logging.getLogger(f"{__name__}.MainDemo")
        
        # Initialize model management system
        self.model_system = self._initialize_model_system()
        
        # Initialize demo components
        self.training_demo = ModelTrainingDemo(self.model_system)
        self.deployment_demo = ModelDeploymentDemo(self.model_system)
        self.analytics_demo = PerformanceAnalyticsDemo(self.model_system)
        self.comparison_demo = ModelComparisonDemo(self.model_system)
        self.retrain_demo = AutoRetrainDemo(self.model_system)
        
        # Demo state
        self.demo_active = False
        self.trained_models = []
        self.deployed_models = []
    
    def _initialize_model_system(self) -> AdvancedAIModelManagementSystem:
        """Initialize the model management system."""
        try:
            # Create configurations
            model_registry_config = ModelRegistryConfig(
                storage_path="./demo_model_registry",
                versioning_enabled=True,
                metadata_tracking=True,
                model_comparison=True,
                performance_tracking=True,
                experiment_tracking=True,
                mlflow_integration=True
            )
            
            automl_config = AutoMLConfig(
                enabled=True,
                max_trials=50,
                timeout_minutes=30,
                optimization_metric="accuracy",
                cross_validation_folds=5,
                hyperparameter_tuning=True,
                feature_engineering=True,
                ensemble_methods=True
            )
            
            deployment_config = DeploymentConfig(
                auto_deployment=True,
                health_check_interval=30,
                performance_monitoring=True,
                load_balancing=True,
                scaling_enabled=True,
                rollback_enabled=True,
                a_b_testing=True,
                canary_percentage=0.1
            )
            
            # Create system
            model_system = AdvancedAIModelManagementSystem(
                model_registry_config=model_registry_config,
                automl_config=automl_config,
                deployment_config=deployment_config
            )
            
            self.logger.info("✅ Model Management System initialized")
            return model_system
            
        except Exception as e:
            self.logger.error(f"Failed to initialize model system: {e}")
            raise
    
    def run_comprehensive_demo(self) -> None:
        """Run comprehensive demonstration of all capabilities."""
        try:
            self.logger.info("🚀 Starting Comprehensive Advanced AI Model Management Demo")
            self.demo_active = True
            
            # Phase 1: Model Training
            self._run_training_phase()
            
            # Phase 2: Model Deployment
            self._run_deployment_phase()
            
            # Phase 3: Performance Analytics
            self._run_analytics_phase()
            
            # Phase 4: Model Comparison
            self._run_comparison_phase()
            
            # Phase 5: Auto-Retraining
            self._run_retraining_phase()
            
            # Phase 6: System Monitoring
            self._run_monitoring_phase()
            
            self.logger.info("✅ Comprehensive demo completed successfully")
            
        except Exception as e:
            self.logger.error(f"Demo failed: {e}")
            raise
        finally:
            self.demo_active = False
            self._cleanup_demo()
    
    def _run_training_phase(self) -> None:
        """Run model training phase."""
        try:
            self.logger.info("📚 Phase 1: Model Training")
            
            # Train classification model
            classification_model = self.training_demo.run_classification_training_demo()
            self.trained_models.append(classification_model)
            
            time.sleep(2)
            
            # Train regression model
            regression_model = self.training_demo.run_regression_training_demo()
            self.trained_models.append(regression_model)
            
            time.sleep(2)
            
            # Train AutoML model
            automl_model = self.training_demo.run_automl_demo()
            self.trained_models.append(automl_model)
            
            self.logger.info(f"✅ Training phase completed. Models trained: {len(self.trained_models)}")
            
        except Exception as e:
            self.logger.error(f"Training phase failed: {e}")
            raise
    
    def _run_deployment_phase(self) -> None:
        """Run model deployment phase."""
        try:
            self.logger.info("🚀 Phase 2: Model Deployment")
            
            for model_id in self.trained_models:
                # Deploy with different strategies
                if model_id == self.trained_models[0]:
                    deployment_id = self.deployment_demo.run_deployment_demo(model_id)
                elif model_id == self.trained_models[1]:
                    deployment_id = self.deployment_demo.run_canary_deployment_demo(model_id)
                else:
                    deployment_id = self.deployment_demo.run_ab_testing_demo(model_id)
                
                self.deployed_models.append(deployment_id)
                time.sleep(1)
            
            self.logger.info(f"✅ Deployment phase completed. Models deployed: {len(self.deployed_models)}")
            
        except Exception as e:
            self.logger.error(f"Deployment phase failed: {e}")
            raise
    
    def _run_analytics_phase(self) -> None:
        """Run performance analytics phase."""
        try:
            self.logger.info("📊 Phase 3: Performance Analytics")
            
            # Start performance analytics
            self.analytics_demo.start_performance_analytics()
            
            # Let analytics run for a while
            time.sleep(30)
            
            # Stop analytics
            self.analytics_demo.stop_performance_analytics()
            
            self.logger.info("✅ Analytics phase completed")
            
        except Exception as e:
            self.logger.error(f"Analytics phase failed: {e}")
            raise
    
    def _run_comparison_phase(self) -> None:
        """Run model comparison phase."""
        try:
            self.logger.info("🔍 Phase 4: Model Comparison")
            
            # Run comprehensive comparison
            comparison_report = self.comparison_demo.run_model_comparison(self.trained_models)
            
            # Log comparison results
            self.logger.info(f"📋 Comparison Report: {json.dumps(comparison_report, indent=2, default=str)}")
            
            self.logger.info("✅ Comparison phase completed")
            
        except Exception as e:
            self.logger.error(f"Comparison phase failed: {e}")
            raise
    
    def _run_retraining_phase(self) -> None:
        """Run auto-retraining phase."""
        try:
            self.logger.info("🔄 Phase 5: Auto-Retraining")
            
            # Simulate performance degradation for first model
            if self.trained_models:
                self.retrain_demo.simulate_performance_degradation(self.trained_models[0])
                
                # Monitor auto-retrain
                time.sleep(10)
                self.retrain_demo.monitor_auto_retrain(self.trained_models[0])
            
            self.logger.info("✅ Retraining phase completed")
            
        except Exception as e:
            self.logger.error(f"Retraining phase failed: {e}")
            raise
    
    def _run_monitoring_phase(self) -> None:
        """Run system monitoring phase."""
        try:
            self.logger.info("👀 Phase 6: System Monitoring")
            
            # Get system status
            system_status = self.model_system.get_system_status()
            self.logger.info(f"📊 System Status: {json.dumps(system_status, indent=2, default=str)}")
            
            # Monitor for a while
            time.sleep(20)
            
            self.logger.info("✅ Monitoring phase completed")
            
        except Exception as e:
            self.logger.error(f"Monitoring phase failed: {e}")
            raise
    
    def _cleanup_demo(self) -> None:
        """Cleanup demo resources."""
        try:
            self.logger.info("🧹 Cleaning up demo resources")
            
            # Stop model system
            self.model_system.stop()
            
            # Clean up demo files
            demo_path = Path("./demo_model_registry")
            if demo_path.exists():
                import shutil
                shutil.rmtree(demo_path)
            
            self.logger.info("✅ Demo cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Demo cleanup failed: {e}")
    
    def run_quick_demo(self) -> None:
        """Run a quick demonstration of key features."""
        try:
            self.logger.info("⚡ Starting Quick Demo")
            
            # Train one model
            model_id = self.training_demo.run_classification_training_demo()
            
            # Deploy it
            deployment_id = self.deployment_demo.run_deployment_demo(model_id)
            
            # Get performance summary
            summary = self.model_system.get_model_performance_summary(model_id)
            self.logger.info(f"📊 Performance Summary: {json.dumps(summary, indent=2, default=str)}")
            
            # Get system status
            status = self.model_system.get_system_status()
            self.logger.info(f"📈 System Status: {json.dumps(status, indent=2, default=str)}")
            
            self.logger.info("✅ Quick demo completed")
            
        except Exception as e:
            self.logger.error(f"Quick demo failed: {e}")
            raise
        finally:
            self._cleanup_demo()

# ===== MAIN EXECUTION =====

def main():
    """Main execution function."""
    print("🚀 Advanced AI Model Management System Demo")
    print("="*60)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create demo
    demo = AdvancedAIModelManagementDemo()
    
    try:
        # Ask user for demo type
        print("\nSelect demo type:")
        print("1. Comprehensive Demo (5+ minutes)")
        print("2. Quick Demo (2 minutes)")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            demo.run_comprehensive_demo()
        elif choice == "2":
            demo.run_quick_demo()
        else:
            print("Invalid choice. Running quick demo...")
            demo.run_quick_demo()
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise
    finally:
        print("🏁 Demo completed")

if __name__ == "__main__":
    main()
