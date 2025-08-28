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
from torch.nn.parallel import DataParallel, DistributedDataParallel
from torch.utils.data import DataLoader, DistributedSampler
import numpy as np
import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import warnings
from multi_gpu_training_system import MultiGPUConfig, MultiGPUTrainer
    import json
    from pathlib import Path
from typing import Any, List, Dict, Optional
import asyncio
"""
🚀 Multi-GPU Training Demo
==========================
Demonstration of multi-GPU training using PyTorch's DataParallel
and DistributedDataParallel for Facebook Posts AI models.
"""

warnings.filterwarnings('ignore')

# Import our modules

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_GPUS = torch.cuda.device_count() if torch.cuda.is_available() else 0
logger.info(f"Using device: {DEVICE}")
logger.info(f"Number of GPUs available: {NUM_GPUS}")

class MultiGPUTrainingDemo:
    """Demo class for multi-GPU training."""
    
    def __init__(self) -> Any:
        self.configs = {}
        self.trainers = {}
        self.results = {}
    
    def create_configs(self) -> Any:
        """Create different training configurations."""
        logger.info("Creating training configurations")
        
        # Configuration 1: DataParallel
        self.configs['dataparallel'] = MultiGPUConfig(
            batch_size=32,
            learning_rate=1e-4,
            num_epochs=10,
            model_type="transformer",
            use_data_parallel=True,
            use_distributed=False,
            mixed_precision=True,
            save_dir="models/dataparallel_demo"
        )
        
        # Configuration 2: DistributedDataParallel (if multiple GPUs)
        if NUM_GPUS > 1:
            self.configs['distributed'] = MultiGPUConfig(
                batch_size=32,
                learning_rate=1e-4,
                num_epochs=10,
                model_type="transformer",
                use_data_parallel=False,
                use_distributed=True,
                mixed_precision=True,
                save_dir="models/distributed_demo"
            )
        
        # Configuration 3: Single GPU
        self.configs['single_gpu'] = MultiGPUConfig(
            batch_size=32,
            learning_rate=1e-4,
            num_epochs=10,
            model_type="transformer",
            use_data_parallel=False,
            use_distributed=False,
            mixed_precision=True,
            save_dir="models/single_gpu_demo"
        )
        
        logger.info(f"Created {len(self.configs)} configurations")
    
    def demo_data_parallel_training(self) -> Any:
        """Demo DataParallel training."""
        logger.info("🚀 Demo: DataParallel Training")
        logger.info("=" * 50)
        
        if NUM_GPUS < 2:
            logger.warning("DataParallel requires at least 2 GPUs. Skipping demo.")
            return None
        
        config = self.configs['dataparallel']
        logger.info(f"Configuration: {config}")
        
        try:
            # Create trainer
            trainer = MultiGPUTrainer(config)
            
            # Train
            start_time = time.time()
            history = trainer.train()
            training_time = time.time() - start_time
            
            # Evaluate
            test_metrics = trainer.evaluate()
            
            result = {
                'method': 'DataParallel',
                'training_time': training_time,
                'test_accuracy': test_metrics['accuracy'],
                'test_loss': test_metrics['loss'],
                'history': history
            }
            
            logger.info(f"DataParallel training completed in {training_time:.2f}s")
            logger.info(f"Test Accuracy: {test_metrics['accuracy']:.2f}%")
            logger.info(f"Test Loss: {test_metrics['loss']:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"DataParallel training failed: {e}")
            return None
    
    def demo_single_gpu_training(self) -> Any:
        """Demo single GPU training."""
        logger.info("🚀 Demo: Single GPU Training")
        logger.info("=" * 50)
        
        config = self.configs['single_gpu']
        logger.info(f"Configuration: {config}")
        
        try:
            # Create trainer
            trainer = MultiGPUTrainer(config)
            
            # Train
            start_time = time.time()
            history = trainer.train()
            training_time = time.time() - start_time
            
            # Evaluate
            test_metrics = trainer.evaluate()
            
            result = {
                'method': 'Single GPU',
                'training_time': training_time,
                'test_accuracy': test_metrics['accuracy'],
                'test_loss': test_metrics['loss'],
                'history': history
            }
            
            logger.info(f"Single GPU training completed in {training_time:.2f}s")
            logger.info(f"Test Accuracy: {test_metrics['accuracy']:.2f}%")
            logger.info(f"Test Loss: {test_metrics['loss']:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Single GPU training failed: {e}")
            return None
    
    def demo_performance_comparison(self) -> Any:
        """Demo performance comparison between different methods."""
        logger.info("🚀 Demo: Performance Comparison")
        logger.info("=" * 50)
        
        results = []
        
        # Single GPU training
        single_result = self.demo_single_gpu_training()
        if single_result:
            results.append(single_result)
        
        # DataParallel training
        dp_result = self.demo_data_parallel_training()
        if dp_result:
            results.append(dp_result)
        
        # Compare results
        if len(results) > 1:
            logger.info("\n📊 Performance Comparison:")
            logger.info("-" * 40)
            
            for result in results:
                logger.info(f"{result['method']}:")
                logger.info(f"  Training Time: {result['training_time']:.2f}s")
                logger.info(f"  Test Accuracy: {result['test_accuracy']:.2f}%")
                logger.info(f"  Test Loss: {result['test_loss']:.4f}")
            
            # Calculate speedup
            if len(results) >= 2:
                single_time = results[0]['training_time']
                multi_time = results[1]['training_time']
                speedup = single_time / multi_time
                
                logger.info(f"\n⚡ Speedup: {speedup:.2f}x")
                logger.info(f"   Single GPU: {single_time:.2f}s")
                logger.info(f"   Multi-GPU: {multi_time:.2f}s")
        
        return results
    
    def demo_memory_usage(self) -> Any:
        """Demo memory usage monitoring."""
        logger.info("🚀 Demo: Memory Usage Monitoring")
        logger.info("=" * 50)
        
        if not torch.cuda.is_available():
            logger.warning("CUDA not available. Skipping memory usage demo.")
            return
        
        # Monitor memory before training
        logger.info("Memory usage before training:")
        for i in range(NUM_GPUS):
            allocated = torch.cuda.memory_allocated(i) / 1024**3
            cached = torch.cuda.memory_reserved(i) / 1024**3
            total = torch.cuda.get_device_properties(i).total_memory / 1024**3
            
            logger.info(f"  GPU {i}:")
            logger.info(f"    Allocated: {allocated:.2f}GB")
            logger.info(f"    Cached: {cached:.2f}GB")
            logger.info(f"    Total: {total:.2f}GB")
            logger.info(f"    Usage: {allocated/total*100:.1f}%")
        
        # Run a quick training session
        config = MultiGPUConfig(
            batch_size=16,
            learning_rate=1e-4,
            num_epochs=2,
            model_type="transformer",
            use_data_parallel=True,
            use_distributed=False,
            dataset_size=1000
        )
        
        try:
            trainer = MultiGPUTrainer(config)
            trainer.train()
            
            # Monitor memory after training
            logger.info("\nMemory usage after training:")
            for i in range(NUM_GPUS):
                allocated = torch.cuda.memory_allocated(i) / 1024**3
                cached = torch.cuda.memory_reserved(i) / 1024**3
                total = torch.cuda.get_device_properties(i).total_memory / 1024**3
                
                logger.info(f"  GPU {i}:")
                logger.info(f"    Allocated: {allocated:.2f}GB")
                logger.info(f"    Cached: {cached:.2f}GB")
                logger.info(f"    Total: {total:.2f}GB")
                logger.info(f"    Usage: {allocated/total*100:.1f}%")
            
            # Clear memory
            torch.cuda.empty_cache()
            logger.info("\nMemory cleared")
            
        except Exception as e:
            logger.error(f"Memory usage demo failed: {e}")
    
    def demo_batch_size_scaling(self) -> Any:
        """Demo batch size scaling with multi-GPU."""
        logger.info("🚀 Demo: Batch Size Scaling")
        logger.info("=" * 50)
        
        if NUM_GPUS < 2:
            logger.warning("Multi-GPU required for batch size scaling demo. Skipping.")
            return
        
        batch_sizes = [16, 32, 64, 128]
        results = []
        
        for batch_size in batch_sizes:
            logger.info(f"\nTesting batch size: {batch_size}")
            
            config = MultiGPUConfig(
                batch_size=batch_size,
                learning_rate=1e-4,
                num_epochs=3,
                model_type="transformer",
                use_data_parallel=True,
                use_distributed=False,
                dataset_size=2000
            )
            
            try:
                trainer = MultiGPUTrainer(config)
                
                start_time = time.time()
                history = trainer.train()
                training_time = time.time() - start_time
                
                test_metrics = trainer.evaluate()
                
                result = {
                    'batch_size': batch_size,
                    'training_time': training_time,
                    'test_accuracy': test_metrics['accuracy'],
                    'test_loss': test_metrics['loss'],
                    'effective_batch_size': batch_size * NUM_GPUS
                }
                
                results.append(result)
                
                logger.info(f"  Training Time: {training_time:.2f}s")
                logger.info(f"  Test Accuracy: {test_metrics['accuracy']:.2f}%")
                logger.info(f"  Effective Batch Size: {batch_size * NUM_GPUS}")
                
            except Exception as e:
                logger.error(f"Batch size {batch_size} failed: {e}")
        
        # Analyze results
        if results:
            logger.info("\n📊 Batch Size Scaling Analysis:")
            logger.info("-" * 40)
            
            for result in results:
                throughput = result['effective_batch_size'] / result['training_time']
                logger.info(f"Batch Size {result['batch_size']}:")
                logger.info(f"  Effective Batch Size: {result['effective_batch_size']}")
                logger.info(f"  Training Time: {result['training_time']:.2f}s")
                logger.info(f"  Throughput: {throughput:.1f} samples/s")
                logger.info(f"  Accuracy: {result['test_accuracy']:.2f}%")
    
    def demo_model_scaling(self) -> Any:
        """Demo model scaling with different model sizes."""
        logger.info("🚀 Demo: Model Scaling")
        logger.info("=" * 50)
        
        model_configs = [
            {'name': 'Small', 'hidden_dim': 256, 'num_layers': 4, 'num_heads': 4},
            {'name': 'Medium', 'hidden_dim': 512, 'num_layers': 6, 'num_heads': 8},
            {'name': 'Large', 'hidden_dim': 1024, 'num_layers': 8, 'num_heads': 16}
        ]
        
        results = []
        
        for model_config in model_configs:
            logger.info(f"\nTesting {model_config['name']} model")
            
            config = MultiGPUConfig(
                batch_size=32,
                learning_rate=1e-4,
                num_epochs=3,
                model_type="transformer",
                hidden_dim=model_config['hidden_dim'],
                num_layers=model_config['num_layers'],
                num_heads=model_config['num_heads'],
                use_data_parallel=True,
                use_distributed=False,
                dataset_size=2000
            )
            
            try:
                trainer = MultiGPUTrainer(config)
                
                # Count parameters
                total_params = sum(p.numel() for p in trainer.model.parameters())
                
                start_time = time.time()
                history = trainer.train()
                training_time = time.time() - start_time
                
                test_metrics = trainer.evaluate()
                
                result = {
                    'model_name': model_config['name'],
                    'total_params': total_params,
                    'training_time': training_time,
                    'test_accuracy': test_metrics['accuracy'],
                    'test_loss': test_metrics['loss']
                }
                
                results.append(result)
                
                logger.info(f"  Parameters: {total_params:,}")
                logger.info(f"  Training Time: {training_time:.2f}s")
                logger.info(f"  Test Accuracy: {test_metrics['accuracy']:.2f}%")
                
            except Exception as e:
                logger.error(f"{model_config['name']} model failed: {e}")
        
        # Analyze results
        if results:
            logger.info("\n📊 Model Scaling Analysis:")
            logger.info("-" * 40)
            
            for result in results:
                params_per_second = result['total_params'] / result['training_time']
                logger.info(f"{result['model_name']} Model:")
                logger.info(f"  Parameters: {result['total_params']:,}")
                logger.info(f"  Training Time: {result['training_time']:.2f}s")
                logger.info(f"  Parameters/Second: {params_per_second:,.0f}")
                logger.info(f"  Accuracy: {result['test_accuracy']:.2f}%")
    
    def run_all_demos(self) -> Any:
        """Run all demos."""
        logger.info("🚀 Starting Multi-GPU Training Demos")
        logger.info("=" * 60)
        
        # Create configurations
        self.create_configs()
        
        # Run demos
        demos = [
            ("Performance Comparison", self.demo_performance_comparison),
            ("Memory Usage", self.demo_memory_usage),
            ("Batch Size Scaling", self.demo_batch_size_scaling),
            ("Model Scaling", self.demo_model_scaling)
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
    demo = MultiGPUTrainingDemo()
    results = demo.run_all_demos()
    
    # Save results
    
    results_path = Path("multi_gpu_demo_results.json")
    
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