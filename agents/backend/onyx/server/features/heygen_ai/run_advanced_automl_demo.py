"""
Advanced AutoML System Demo for HeyGen AI Enterprise
Comprehensive demonstration of Neural Architecture Search, Hyperparameter Optimization,
and Intelligent Model Selection capabilities
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
from core.advanced_automl_system import (
    AdvancedAutoMLSystem, 
    AutoMLConfig, 
    create_advanced_automl_system,
    create_automl_config
)
from core.advanced_performance_optimizer import create_advanced_performance_optimizer
from core.performance_benchmarking_suite import create_performance_benchmarking_suite
from core.advanced_neural_network_optimizer import create_advanced_neural_network_optimizer


class AdvancedAutoMLDemo:
    """Comprehensive demo showcasing Advanced AutoML System capabilities."""
    
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
        """Initialize all required systems."""
        self.logger.info("🔧 Initializing Advanced AutoML System...")
        
        # Create AutoML system with custom configuration
        automl_config = create_automl_config(
            enable_nas=True,
            nas_strategy="evolutionary",
            max_trials=50,  # Reduced for demo
            population_size=10,
            generations=5,
            enable_hpo=True,
            hpo_strategy="optuna",
            max_hpo_trials=20,  # Reduced for demo
            timeout_hours=1,
            enable_model_selection=True,
            selection_metric="balanced",
            ensemble_method="stacking",
            enable_performance_optimization=True,
            enable_mlflow=True,
            enable_ray_dashboard=True
        )
        
        self.automl_system = create_advanced_automl_system(automl_config)
        
        # Initialize supporting systems
        self.performance_optimizer = create_advanced_performance_optimizer()
        self.benchmarking_suite = create_performance_benchmarking_suite()
        self.neural_optimizer = create_advanced_neural_network_optimizer()
        
        self.logger.info("✅ All systems initialized successfully!")
    
    def create_test_data(self):
        """Create synthetic test data for demonstration."""
        self.logger.info("📊 Creating synthetic test data...")
        
        # Create synthetic datasets
        np.random.seed(42)
        
        # Transformer data (sequence classification)
        seq_length = 128
        vocab_size = 1000
        num_samples = 1000
        
        transformer_data = np.random.randint(0, vocab_size, (num_samples, seq_length))
        transformer_labels = np.random.randint(0, 10, num_samples)
        
        # CNN data (image classification)
        img_height, img_width, channels = 32, 32, 3
        cnn_data = np.random.randn(num_samples, channels, img_height, img_width)
        cnn_labels = np.random.randint(0, 10, num_samples)
        
        # RNN data (time series classification)
        time_steps = 64
        features = 16
        rnn_data = np.random.randn(num_samples, time_steps, features)
        rnn_labels = np.random.randint(0, 5, num_samples)
        
        # Create DataLoaders
        batch_size = 32
        
        self.transformer_dataloader = DataLoader(
            TensorDataset(
                torch.LongTensor(transformer_data),
                torch.LongTensor(transformer_labels)
            ),
            batch_size=batch_size,
            shuffle=True
        )
        
        self.cnn_dataloader = DataLoader(
            TensorDataset(
                torch.FloatTensor(cnn_data),
                torch.LongTensor(cnn_labels)
            ),
            batch_size=batch_size,
            shuffle=True
        )
        
        self.rnn_dataloader = DataLoader(
            TensorDataset(
                torch.FloatTensor(rnn_data),
                torch.LongTensor(rnn_labels)
            ),
            batch_size=batch_size,
            shuffle=True
        )
        
        self.logger.info("✅ Test data created successfully!")
    
    def run_comprehensive_demo(self):
        """Run comprehensive AutoML demonstration."""
        self.logger.info("🚀 Starting Comprehensive Advanced AutoML Demo...")
        self.running = True
        
        try:
            # Run individual demos
            self.demo_results["transformer_automl"] = self.run_transformer_automl_demo()
            self.demo_results["cnn_automl"] = self.run_cnn_automl_demo()
            self.demo_results["rnn_automl"] = self.run_rnn_automl_demo()
            self.demo_results["multi_task_automl"] = self.run_multi_task_automl_demo()
            self.demo_results["performance_integration"] = self.run_performance_integration_demo()
            self.demo_results["advanced_features"] = self.run_advanced_features_demo()
            
            self.logger.info("🎉 Comprehensive demo completed successfully!")
            return self.demo_results
            
        except Exception as e:
            self.logger.error(f"❌ Demo failed: {e}")
            raise
        finally:
            self.running = False
    
    def run_transformer_automl_demo(self):
        """Demonstrate AutoML for Transformer models."""
        self.logger.info("🔍 Running Transformer AutoML Demo...")
        
        start_time = time.time()
        
        # Run complete AutoML pipeline for transformer
        results = self.automl_system.run_complete_automl(
            task_type="transformer",
            input_shape=(128, 1000),  # (seq_length, vocab_size)
            num_classes=10,
            train_data=self.transformer_dataloader,
            val_data=self.transformer_dataloader  # Using same data for demo
        )
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "transformer",
            "duration_seconds": duration,
            "best_architecture": results.get("best_architecture", {}),
            "best_hyperparameters": results.get("best_hyperparameters", {}),
            "selected_models": len(results.get("selected_models", [])),
            "ensemble_created": results.get("ensemble", {}).get("type", "none"),
            "performance_metrics": results.get("performance_metrics", [])
        }
        
        self.logger.info(f"✅ Transformer AutoML completed in {duration:.2f}s")
        return demo_result
    
    def run_cnn_automl_demo(self):
        """Demonstrate AutoML for CNN models."""
        self.logger.info("🔍 Running CNN AutoML Demo...")
        
        start_time = time.time()
        
        # Run complete AutoML pipeline for CNN
        results = self.automl_system.run_complete_automl(
            task_type="cnn",
            input_shape=(3, 32, 32),  # (channels, height, width)
            num_classes=10,
            train_data=self.cnn_dataloader,
            val_data=self.cnn_dataloader
        )
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "cnn",
            "duration_seconds": duration,
            "best_architecture": results.get("best_architecture", {}),
            "best_hyperparameters": results.get("best_hyperparameters", {}),
            "selected_models": len(results.get("selected_models", [])),
            "ensemble_created": results.get("ensemble", {}).get("type", "none"),
            "performance_metrics": results.get("performance_metrics", [])
        }
        
        self.logger.info(f"✅ CNN AutoML completed in {duration:.2f}s")
        return demo_result
    
    def run_rnn_automl_demo(self):
        """Demonstrate AutoML for RNN models."""
        self.logger.info("🔍 Running RNN AutoML Demo...")
        
        start_time = time.time()
        
        # Run complete AutoML pipeline for RNN
        results = self.automl_system.run_complete_automl(
            task_type="rnn",
            input_shape=(64, 16),  # (time_steps, features)
            num_classes=5,
            train_data=self.rnn_dataloader,
            val_data=self.rnn_dataloader
        )
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "rnn",
            "duration_seconds": duration,
            "best_architecture": results.get("best_architecture", {}),
            "best_hyperparameters": results.get("best_hyperparameters", {}),
            "selected_models": len(results.get("selected_models", [])),
            "ensemble_created": results.get("ensemble", {}).get("type", "none"),
            "performance_metrics": results.get("performance_metrics", [])
        }
        
        self.logger.info(f"✅ RNN AutoML completed in {duration:.2f}s")
        return demo_result
    
    def run_multi_task_automl_demo(self):
        """Demonstrate multi-task AutoML capabilities."""
        self.logger.info("🔍 Running Multi-Task AutoML Demo...")
        
        start_time = time.time()
        
        # Create multi-task configuration
        multi_task_config = create_automl_config(
            enable_nas=True,
            nas_strategy="bayesian",
            max_trials=30,
            enable_hpo=True,
            hpo_strategy="ray_tune",
            max_hpo_trials=15,
            enable_model_selection=True,
            selection_metric="balanced",
            ensemble_method="blending"
        )
        
        multi_task_automl = create_advanced_automl_system(multi_task_config)
        
        # Run AutoML for multiple tasks
        tasks = [
            ("transformer", self.transformer_dataloader, (128, 1000), 10),
            ("cnn", self.cnn_dataloader, (3, 32, 32), 10),
            ("rnn", self.rnn_dataloader, (64, 16), 5)
        ]
        
        multi_task_results = {}
        for task_type, dataloader, input_shape, num_classes in tasks:
            self.logger.info(f"🔄 Running {task_type} in multi-task pipeline...")
            
            results = multi_task_automl.run_complete_automl(
                task_type=task_type,
                input_shape=input_shape,
                num_classes=num_classes,
                train_data=dataloader,
                val_data=dataloader
            )
            
            multi_task_results[task_type] = results
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "multi_task",
            "duration_seconds": duration,
            "tasks_completed": len(tasks),
            "results_per_task": multi_task_results,
            "total_models_generated": sum(
                len(results.get("selected_models", [])) 
                for results in multi_task_results.values()
            )
        }
        
        self.logger.info(f"✅ Multi-Task AutoML completed in {duration:.2f}s")
        return demo_result
    
    def run_performance_integration_demo(self):
        """Demonstrate integration with performance optimization systems."""
        self.logger.info("🔍 Running Performance Integration Demo...")
        
        start_time = time.time()
        
        # Get AutoML summary
        automl_summary = self.automl_system.get_automl_summary()
        
        # Run performance benchmarking on selected models
        benchmark_results = {}
        if hasattr(self.automl_system, 'selector') and self.automl_system.selector.selected_models:
            self.logger.info("📊 Benchmarking selected models...")
            
            for i, model in enumerate(self.automl_system.selector.selected_models[:3]):
                model_name = f"automl_model_{i}"
                
                # Run performance benchmark
                benchmark_result = self.benchmarking_suite.run_comprehensive_benchmark(
                    model_name=model_name,
                    model_config=model,
                    test_data=self.transformer_dataloader,
                    num_runs=5
                )
                
                benchmark_results[model_name] = benchmark_result
        
        # Run neural network optimization
        optimization_results = {}
        if hasattr(self.automl_system, 'selector') and self.automl_system.selector.selected_models:
            self.logger.info("⚡ Optimizing selected models...")
            
            for i, model in enumerate(self.automl_system.selector.selected_models[:3]):
                model_name = f"automl_model_{i}"
                
                # Run neural network optimization
                optimization_result = self.neural_optimizer.optimize_neural_network(
                    model_name=model_name,
                    model_config=model
                )
                
                optimization_results[model_name] = optimization_result
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "performance_integration",
            "duration_seconds": duration,
            "automl_summary": automl_summary,
            "benchmark_results": benchmark_results,
            "optimization_results": optimization_results,
            "integration_success": True
        }
        
        self.logger.info(f"✅ Performance Integration completed in {duration:.2f}s")
        return demo_result
    
    def run_advanced_features_demo(self):
        """Demonstrate advanced AutoML features."""
        self.logger.info("🔍 Running Advanced Features Demo...")
        
        start_time = time.time()
        
        # Test different NAS strategies
        nas_strategies = ["evolutionary", "bayesian"]
        nas_results = {}
        
        for strategy in nas_strategies:
            self.logger.info(f"🧬 Testing {strategy} NAS strategy...")
            
            strategy_config = create_automl_config(
                nas_strategy=strategy,
                max_trials=20,
                population_size=8,
                generations=3
            )
            
            strategy_automl = create_advanced_automl_system(strategy_config)
            
            # Quick search
            architecture = strategy_automl.nas.search_architecture(
                "transformer", (128, 1000), 10
            )
            
            nas_results[strategy] = architecture
        
        # Test different HPO strategies
        hpo_strategies = ["optuna", "ray_tune"]
        hpo_results = {}
        
        for strategy in hpo_strategies:
            self.logger.info(f"🔧 Testing {strategy} HPO strategy...")
            
            strategy_config = create_automl_config(
                hpo_strategy=strategy,
                max_hpo_trials=10
            )
            
            strategy_automl = create_advanced_automl_system(strategy_config)
            
            # Quick optimization
            search_space = {
                "learning_rate": {"type": "float", "low": 1e-4, "high": 1e-2, "log": True},
                "batch_size": {"type": "categorical", "choices": [16, 32, 64]}
            }
            
            best_params = strategy_automl.hpo.optimize_hyperparameters(
                type("TestModel", (), {}),
                self.transformer_dataloader,
                self.transformer_dataloader,
                search_space
            )
            
            hpo_results[strategy] = best_params
        
        # Test different ensemble methods
        ensemble_methods = ["stacking", "voting", "blending"]
        ensemble_results = {}
        
        for method in ensemble_methods:
            self.logger.info(f"🎭 Testing {method} ensemble method...")
            
            method_config = create_automl_config(ensemble_method=method)
            method_automl = create_advanced_automl_system(method_config)
            
            # Create sample models
            sample_models = [
                {"id": f"model_{i}", "type": "transformer"} 
                for i in range(3)
            ]
            
            ensemble = method_automl.selector.create_ensemble(sample_models)
            ensemble_results[method] = ensemble
        
        duration = time.time() - start_time
        
        demo_result = {
            "task_type": "advanced_features",
            "duration_seconds": duration,
            "nas_strategies_tested": nas_results,
            "hpo_strategies_tested": hpo_results,
            "ensemble_methods_tested": ensemble_results,
            "features_demonstrated": [
                "Multiple NAS strategies",
                "Multiple HPO strategies", 
                "Multiple ensemble methods",
                "Strategy comparison"
            ]
        }
        
        self.logger.info(f"✅ Advanced Features completed in {duration:.2f}s")
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
            "automl_capabilities_demonstrated": [
                "Neural Architecture Search (NAS)",
                "Hyperparameter Optimization (HPO)",
                "Intelligent Model Selection",
                "Ensemble Creation",
                "Performance Integration",
                "Multi-Task Optimization",
                "Strategy Comparison"
            ]
        }
        
        return summary
    
    def save_demo_results(self, output_path: str = "automl_demo_results.json"):
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
    """Main function to run the Advanced AutoML Demo."""
    print("🚀 HeyGen AI Enterprise - Advanced AutoML System Demo")
    print("=" * 60)
    
    # Create and run demo
    demo = AdvancedAutoMLDemo()
    
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
        
        print("\n🎉 Advanced AutoML Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
