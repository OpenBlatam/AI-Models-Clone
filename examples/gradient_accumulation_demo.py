from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

# Constants
BUFFER_SIZE = 1024

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import warnings
from gradient_accumulation_system import GradientAccumulationConfig, GradientAccumulationTrainer
    import json
    from pathlib import Path
from typing import Any, List, Dict, Optional
import asyncio
"""
🔄 Gradient Accumulation Demo
============================
Demonstration of gradient accumulation for handling large batch sizes
in Facebook Posts AI training.
"""

warnings.filterwarnings('ignore')

# Import our modules

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

class GradientAccumulationDemo:
    """Demo class for gradient accumulation."""
    
    def __init__(self) -> Any:
        self.configs = {}
        self.trainers = {}
        self.results = {}
    
    def create_configs(self) -> Any:
        """Create different gradient accumulation configurations."""
        logger.info("Creating gradient accumulation configurations")
        
        # Configuration 1: Small effective batch size
        self.configs['small_batch'] = GradientAccumulationConfig(
            batch_size=4,
            effective_batch_size=32,
            learning_rate=1e-4,
            num_epochs=5,
            model_type="transformer",
            dataset_size=1000,
            save_dir="models/small_batch_demo"
        )
        
        # Configuration 2: Medium effective batch size
        self.configs['medium_batch'] = GradientAccumulationConfig(
            batch_size=8,
            effective_batch_size=128,
            learning_rate=1e-4,
            num_epochs=5,
            model_type="transformer",
            dataset_size=1000,
            save_dir="models/medium_batch_demo"
        )
        
        # Configuration 3: Large effective batch size
        self.configs['large_batch'] = GradientAccumulationConfig(
            batch_size=16,
            effective_batch_size=512,
            learning_rate=1e-4,
            num_epochs=5,
            model_type="transformer",
            dataset_size=1000,
            save_dir="models/large_batch_demo"
        )
        
        # Configuration 4: Very large effective batch size
        self.configs['xlarge_batch'] = GradientAccumulationConfig(
            batch_size=32,
            effective_batch_size=1024,
            learning_rate=1e-4,
            num_epochs=5,
            model_type="transformer",
            dataset_size=1000,
            save_dir="models/xlarge_batch_demo"
        )
        
        logger.info(f"Created {len(self.configs)} configurations")
    
    def demo_memory_comparison(self) -> Any:
        """Demo memory usage comparison between different batch sizes."""
        logger.info("🔄 Demo: Memory Usage Comparison")
        logger.info("=" * 50)
        
        if not torch.cuda.is_available():
            logger.warning("CUDA not available. Skipping memory comparison demo.")
            return None
        
        results = []
        
        for config_name, config in self.configs.items():
            logger.info(f"\nTesting {config_name} configuration")
            logger.info(f"  Batch size per step: {config.batch_size}")
            logger.info(f"  Effective batch size: {config.effective_batch_size}")
            logger.info(f"  Accumulation steps: {config.accumulation_steps}")
            
            # Clear memory before test
            torch.cuda.empty_cache()
            
            # Monitor memory before training
            initial_memory = torch.cuda.memory_allocated() / 1024**3
            
            try:
                # Create trainer
                trainer = GradientAccumulationTrainer(config)
                
                # Monitor memory after model creation
                model_memory = torch.cuda.memory_allocated() / 1024**3
                
                # Run a few training steps
                trainer.model.train()
                trainer.reset_accumulation_state()
                
                # Get a batch of data
                data_iter = iter(trainer.train_loader)
                data, target = next(data_iter)
                
                # Run accumulation steps
                max_steps = min(config.accumulation_steps, 5)  # Limit for demo
                for step in range(max_steps):
                    result = trainer.accumulate_gradients(data, target)
                    if result['should_update']:
                        break
                
                # Monitor memory after training
                training_memory = torch.cuda.memory_allocated() / 1024**3
                
                result = {
                    'config_name': config_name,
                    'batch_size': config.batch_size,
                    'effective_batch_size': config.effective_batch_size,
                    'accumulation_steps': config.accumulation_steps,
                    'initial_memory_gb': initial_memory,
                    'model_memory_gb': model_memory,
                    'training_memory_gb': training_memory,
                    'memory_increase_gb': training_memory - initial_memory
                }
                
                results.append(result)
                
                logger.info(f"  Initial Memory: {initial_memory:.2f}GB")
                logger.info(f"  Model Memory: {model_memory:.2f}GB")
                logger.info(f"  Training Memory: {training_memory:.2f}GB")
                logger.info(f"  Memory Increase: {training_memory - initial_memory:.2f}GB")
                
            except Exception as e:
                logger.error(f"{config_name} failed: {e}")
                results.append({
                    'config_name': config_name,
                    'error': str(e)
                })
        
        # Analyze results
        if results:
            logger.info("\n📊 Memory Usage Analysis:")
            logger.info("-" * 40)
            
            for result in results:
                if 'error' not in result:
                    logger.info(f"{result['config_name']}:")
                    logger.info(f"  Batch Size: {result['batch_size']}")
                    logger.info(f"  Effective Batch Size: {result['effective_batch_size']}")
                    logger.info(f"  Memory Increase: {result['memory_increase_gb']:.2f}GB")
                    logger.info(f"  Memory per Sample: {result['memory_increase_gb'] / result['batch_size']:.3f}GB")
        
        return results
    
    def demo_training_comparison(self) -> Any:
        """Demo training comparison between different batch sizes."""
        logger.info("🔄 Demo: Training Comparison")
        logger.info("=" * 50)
        
        results = []
        
        for config_name, config in self.configs.items():
            logger.info(f"\nTraining with {config_name} configuration")
            
            try:
                # Create trainer
                trainer = GradientAccumulationTrainer(config)
                
                # Train
                start_time = time.time()
                history = trainer.train()
                training_time = time.time() - start_time
                
                # Evaluate
                test_metrics = trainer.evaluate()
                
                # Calculate metrics
                final_train_loss = history[-1]['train_loss'] if history else 0
                final_train_acc = history[-1]['train_accuracy'] if history else 0
                final_val_loss = history[-1]['val_loss'] if history else 0
                final_val_acc = history[-1]['val_accuracy'] if history else 0
                
                result = {
                    'config_name': config_name,
                    'batch_size': config.batch_size,
                    'effective_batch_size': config.effective_batch_size,
                    'accumulation_steps': config.accumulation_steps,
                    'training_time': training_time,
                    'final_train_loss': final_train_loss,
                    'final_train_acc': final_train_acc,
                    'final_val_loss': final_val_loss,
                    'final_val_acc': final_val_acc,
                    'test_loss': test_metrics['loss'],
                    'test_accuracy': test_metrics['accuracy']
                }
                
                results.append(result)
                
                logger.info(f"  Training Time: {training_time:.2f}s")
                logger.info(f"  Final Train Loss: {final_train_loss:.4f}")
                logger.info(f"  Final Train Acc: {final_train_acc:.2f}%")
                logger.info(f"  Final Val Loss: {final_val_loss:.4f}")
                logger.info(f"  Final Val Acc: {final_val_acc:.2f}%")
                logger.info(f"  Test Loss: {test_metrics['loss']:.4f}")
                logger.info(f"  Test Acc: {test_metrics['accuracy']:.2f}%")
                
            except Exception as e:
                logger.error(f"{config_name} training failed: {e}")
                results.append({
                    'config_name': config_name,
                    'error': str(e)
                })
        
        # Analyze results
        if results:
            logger.info("\n📊 Training Comparison Analysis:")
            logger.info("-" * 40)
            
            for result in results:
                if 'error' not in result:
                    logger.info(f"{result['config_name']}:")
                    logger.info(f"  Effective Batch Size: {result['effective_batch_size']}")
                    logger.info(f"  Training Time: {result['training_time']:.2f}s")
                    logger.info(f"  Test Accuracy: {result['test_accuracy']:.2f}%")
                    logger.info(f"  Test Loss: {result['test_loss']:.4f}")
        
        return results
    
    def demo_accumulation_visualization(self) -> Any:
        """Demo visualization of gradient accumulation process."""
        logger.info("🔄 Demo: Gradient Accumulation Visualization")
        logger.info("=" * 50)
        
        # Use medium batch configuration for visualization
        config = self.configs['medium_batch']
        
        try:
            # Create trainer
            trainer = GradientAccumulationTrainer(config)
            
            logger.info(f"Visualizing gradient accumulation process:")
            logger.info(f"  Batch size per step: {config.batch_size}")
            logger.info(f"  Effective batch size: {config.effective_batch_size}")
            logger.info(f"  Accumulation steps: {config.accumulation_steps}")
            
            # Reset accumulation state
            trainer.reset_accumulation_state()
            
            # Get data iterator
            data_iter = iter(trainer.train_loader)
            
            # Simulate accumulation process
            for step in range(config.accumulation_steps + 2):  # Extra steps for visualization
                try:
                    data, target = next(data_iter)
                except StopIteration:
                    # Restart iterator if needed
                    data_iter = iter(trainer.train_loader)
                    data, target = next(data_iter)
                
                # Accumulate gradients
                result = trainer.accumulate_gradients(data, target)
                
                logger.info(
                    f"Step {step + 1}: "
                    f"Loss: {result['loss']:.4f}, "
                    f"Correct: {result['correct']}/{result['samples']}, "
                    f"Accumulation: {trainer.accumulation_step}/{config.accumulation_steps}, "
                    f"Update: {'Yes' if result['should_update'] else 'No'}"
                )
                
                if result['should_update']:
                    logger.info("  → Parameter update performed!")
                    break
            
            logger.info("Gradient accumulation visualization completed")
            
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
    
    def demo_batch_size_scaling(self) -> Any:
        """Demo batch size scaling with gradient accumulation."""
        logger.info("🔄 Demo: Batch Size Scaling with Gradient Accumulation")
        logger.info("=" * 50)
        
        # Test different effective batch sizes
        effective_batch_sizes = [32, 64, 128, 256, 512]
        batch_size_per_step = 8  # Keep constant
        results = []
        
        for effective_batch_size in effective_batch_sizes:
            logger.info(f"\nTesting effective batch size: {effective_batch_size}")
            
            config = GradientAccumulationConfig(
                batch_size=batch_size_per_step,
                effective_batch_size=effective_batch_size,
                learning_rate=1e-4,
                num_epochs=3,
                model_type="transformer",
                dataset_size=1000,
                save_dir=f"models/scaling_demo_{effective_batch_size}"
            )
            
            try:
                # Create trainer
                trainer = GradientAccumulationTrainer(config)
                
                # Train
                start_time = time.time()
                history = trainer.train()
                training_time = time.time() - start_time
                
                # Evaluate
                test_metrics = trainer.evaluate()
                
                # Calculate throughput
                total_samples = len(trainer.train_loader.dataset)
                throughput = total_samples / training_time
                
                result = {
                    'effective_batch_size': effective_batch_size,
                    'batch_size_per_step': batch_size_per_step,
                    'accumulation_steps': config.accumulation_steps,
                    'training_time': training_time,
                    'test_accuracy': test_metrics['accuracy'],
                    'test_loss': test_metrics['loss'],
                    'throughput': throughput
                }
                
                results.append(result)
                
                logger.info(f"  Accumulation Steps: {config.accumulation_steps}")
                logger.info(f"  Training Time: {training_time:.2f}s")
                logger.info(f"  Test Accuracy: {test_metrics['accuracy']:.2f}%")
                logger.info(f"  Throughput: {throughput:.1f} samples/s")
                
            except Exception as e:
                logger.error(f"Effective batch size {effective_batch_size} failed: {e}")
        
        # Analyze results
        if results:
            logger.info("\n📊 Batch Size Scaling Analysis:")
            logger.info("-" * 40)
            
            for result in results:
                logger.info(f"Effective Batch Size {result['effective_batch_size']}:")
                logger.info(f"  Accumulation Steps: {result['accumulation_steps']}")
                logger.info(f"  Training Time: {result['training_time']:.2f}s")
                logger.info(f"  Test Accuracy: {result['test_accuracy']:.2f}%")
                logger.info(f"  Throughput: {result['throughput']:.1f} samples/s")
        
        return results
    
    def demo_learning_rate_scaling(self) -> Any:
        """Demo learning rate scaling with batch size."""
        logger.info("🔄 Demo: Learning Rate Scaling with Batch Size")
        logger.info("=" * 50)
        
        # Test different learning rates for large batch sizes
        effective_batch_sizes = [64, 128, 256]
        base_lr = 1e-4
        results = []
        
        for effective_batch_size in effective_batch_sizes:
            logger.info(f"\nTesting effective batch size: {effective_batch_size}")
            
            # Scale learning rate with batch size (linear scaling rule)
            scaled_lr = base_lr * (effective_batch_size / 64)
            
            config = GradientAccumulationConfig(
                batch_size=8,
                effective_batch_size=effective_batch_size,
                learning_rate=scaled_lr,
                num_epochs=3,
                model_type="transformer",
                dataset_size=1000,
                save_dir=f"models/lr_scaling_demo_{effective_batch_size}"
            )
            
            try:
                # Create trainer
                trainer = GradientAccumulationTrainer(config)
                
                # Train
                start_time = time.time()
                history = trainer.train()
                training_time = time.time() - start_time
                
                # Evaluate
                test_metrics = trainer.evaluate()
                
                # Calculate convergence metrics
                initial_loss = history[0]['train_loss'] if history else 0
                final_loss = history[-1]['train_loss'] if history else 0
                loss_reduction = (initial_loss - final_loss) / initial_loss if initial_loss > 0 else 0
                
                result = {
                    'effective_batch_size': effective_batch_size,
                    'learning_rate': scaled_lr,
                    'scaling_factor': effective_batch_size / 64,
                    'training_time': training_time,
                    'test_accuracy': test_metrics['accuracy'],
                    'test_loss': test_metrics['loss'],
                    'loss_reduction': loss_reduction
                }
                
                results.append(result)
                
                logger.info(f"  Learning Rate: {scaled_lr:.2e}")
                logger.info(f"  Scaling Factor: {effective_batch_size / 64:.1f}x")
                logger.info(f"  Training Time: {training_time:.2f}s")
                logger.info(f"  Test Accuracy: {test_metrics['accuracy']:.2f}%")
                logger.info(f"  Loss Reduction: {loss_reduction:.2%}")
                
            except Exception as e:
                logger.error(f"Effective batch size {effective_batch_size} failed: {e}")
        
        # Analyze results
        if results:
            logger.info("\n📊 Learning Rate Scaling Analysis:")
            logger.info("-" * 40)
            
            for result in results:
                logger.info(f"Effective Batch Size {result['effective_batch_size']}:")
                logger.info(f"  Learning Rate: {result['learning_rate']:.2e}")
                logger.info(f"  Scaling Factor: {result['scaling_factor']:.1f}x")
                logger.info(f"  Test Accuracy: {result['test_accuracy']:.2f}%")
                logger.info(f"  Loss Reduction: {result['loss_reduction']:.2%}")
        
        return results
    
    def run_all_demos(self) -> Any:
        """Run all demos."""
        logger.info("🔄 Starting Gradient Accumulation Demos")
        logger.info("=" * 60)
        
        # Create configurations
        self.create_configs()
        
        # Run demos
        demos = [
            ("Memory Comparison", self.demo_memory_comparison),
            ("Training Comparison", self.demo_training_comparison),
            ("Accumulation Visualization", self.demo_accumulation_visualization),
            ("Batch Size Scaling", self.demo_batch_size_scaling),
            ("Learning Rate Scaling", self.demo_learning_rate_scaling)
        ]
        
        for demo_name, demo_func in demos:
            try:
                logger.info(f"\n{'='*20} {demo_name} {'='*20}")
                result = demo_func()
                self.results[demo_name] = result
                logger.info(f"✅ {demo_name} completed successfully")
            except Exception as e:
                logger.error(f"❌ {demo_name} failed: {e}")
                self.results[demo_name] = None
        
        # Summary
        logger.info("\n🎉 All demos completed!")
        logger.info("=" * 60)
        
        successful_demos = sum(1 for result in self.results.values() if result is not None)
        total_demos = len(self.results)
        
        logger.info(f"Successful demos: {successful_demos}/{total_demos}")
        
        return self.results

def main():
    """Main function to run the demo."""
    demo = GradientAccumulationDemo()
    results = demo.run_all_demos()
    
    # Save results
    
    results_path = Path("gradient_accumulation_demo_results.json")
    
    # Convert results to serializable format
    serializable_results = {}
    for demo_name, result in results.items():
        if result is not None:
            if isinstance(result, list):
                serializable_results[demo_name] = [
                    {k: v for k, v in r.items() if not k.startswith('_')}
                    for r in result
                ]
            else:
                serializable_results[demo_name] = {
                    k: v for k, v in result.items() if not k.startswith('_')
                }
        else:
            serializable_results[demo_name] = None
    
    with open(results_path, 'w') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        json.dump(serializable_results, f, indent=2)
    
    logger.info(f"Results saved to {results_path}")

match __name__:
    case "__main__":
    main() 