"""
🚀 Multi-GPU Training Example
=============================

This example demonstrates comprehensive multi-GPU training using
DataParallel and DistributedDataParallel in the Gradio app.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import json
import time
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the multi-GPU trainer from the Gradio app
from gradio_app import MultiGPUTrainer, MultiGPUConfig


class SimpleNeuralNetwork(nn.Module):
    """Simple neural network for demonstration."""
    
    def __init__(self, input_size: int = 10, hidden_size: int = 64, num_classes: int = 2):
        super(SimpleNeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
        
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc3(x)
        return x


class DummyDataset:
    """Dummy dataset for demonstration."""
    
    def __init__(self, num_samples: int = 1000, input_size: int = 10, num_classes: int = 2):
        self.num_samples = num_samples
        self.input_size = input_size
        self.num_classes = num_classes
        
        # Generate random data
        self.X = torch.randn(num_samples, input_size)
        self.y = torch.randint(0, num_classes, (num_samples,))
        
    def __len__(self):
        return self.num_samples
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def demonstrate_gpu_info():
    """Demonstrate GPU information retrieval."""
    print("=" * 60)
    print("🔍 GPU INFORMATION DEMONSTRATION")
    print("=" * 60)
    
    trainer = MultiGPUTrainer()
    gpu_info = trainer.get_gpu_info()
    
    print(f"CUDA Available: {gpu_info['cuda_available']}")
    print(f"GPU Count: {gpu_info['gpu_count']}")
    print(f"Multi-GPU Available: {gpu_info['multi_gpu_available']}")
    
    if gpu_info['cuda_available']:
        print(f"Current Device: {gpu_info['current_device']}")
        print("\nDevice Properties:")
        for i, props in enumerate(gpu_info['device_properties']):
            print(f"  GPU {i}: {props['name']}")
            print(f"    Memory: {props['total_memory_gb']:.1f} GB")
            print(f"    Compute Capability: {props['compute_capability']}")
            print(f"    Multi-Processors: {props['multi_processor_count']}")
        
        print(f"\nMemory Usage:")
        print(f"  Allocated: {gpu_info['memory_info']['allocated_gb']:.2f} GB")
        print(f"  Reserved: {gpu_info['memory_info']['reserved_gb']:.2f} GB")
        print(f"  Total: {gpu_info['memory_info']['total_gb']:.1f} GB")
    
    return gpu_info


def demonstrate_data_parallel():
    """Demonstrate DataParallel training."""
    print("\n" + "=" * 60)
    print("📦 DATAPARALLEL TRAINING DEMONSTRATION")
    print("=" * 60)
    
    # Check if multi-GPU is available
    if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
        print("❌ DataParallel requires at least 2 GPUs")
        return
    
    trainer = MultiGPUTrainer()
    
    # Create model and dataset
    model = SimpleNeuralNetwork()
    dataset = DummyDataset(num_samples=1000)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Setup optimizer and loss
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    print("🚀 Starting DataParallel training...")
    start_time = time.time()
    
    # Train with DataParallel
    training_metrics = trainer.train_with_multi_gpu(
        model=model,
        train_loader=train_loader,
        optimizer=optimizer,
        criterion=criterion,
        num_epochs=5,
        strategy='DataParallel',
        use_mixed_precision=True
    )
    
    training_time = time.time() - start_time
    
    print(f"✅ DataParallel training completed in {training_time:.2f}s")
    print(f"Strategy Used: {training_metrics['strategy_used']}")
    print(f"Final Loss: {training_metrics['final_loss']:.4f}")
    print(f"Total Training Time: {training_metrics['total_training_time']:.2f}s")
    
    if 'gpu_utilization' in training_metrics:
        avg_utilization = np.mean(training_metrics['gpu_utilization'])
        print(f"Average GPU Utilization: {avg_utilization:.1f}%")
    
    return training_metrics


def demonstrate_distributed_data_parallel():
    """Demonstrate DistributedDataParallel training."""
    print("\n" + "=" * 60)
    print("🌐 DISTRIBUTEDDATAPARALLEL TRAINING DEMONSTRATION")
    print("=" * 60)
    
    # Check if multi-GPU is available
    if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
        print("❌ DistributedDataParallel requires at least 2 GPUs")
        return
    
    trainer = MultiGPUTrainer()
    
    # Create model and dataset
    model = SimpleNeuralNetwork()
    dataset = DummyDataset(num_samples=1000)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Setup optimizer and loss
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    print("🚀 Starting DistributedDataParallel training...")
    start_time = time.time()
    
    # Train with DistributedDataParallel
    training_metrics = trainer.train_with_multi_gpu(
        model=model,
        train_loader=train_loader,
        optimizer=optimizer,
        criterion=criterion,
        num_epochs=5,
        strategy='DistributedDataParallel',
        use_mixed_precision=True
    )
    
    training_time = time.time() - start_time
    
    print(f"✅ DistributedDataParallel training completed in {training_time:.2f}s")
    print(f"Strategy Used: {training_metrics['strategy_used']}")
    print(f"Final Loss: {training_metrics['final_loss']:.4f}")
    print(f"Total Training Time: {training_metrics['total_training_time']:.2f}s")
    
    if 'gpu_utilization' in training_metrics:
        avg_utilization = np.mean(training_metrics['gpu_utilization'])
        print(f"Average GPU Utilization: {avg_utilization:.1f}%")
    
    return training_metrics


def demonstrate_auto_strategy_selection():
    """Demonstrate automatic strategy selection."""
    print("\n" + "=" * 60)
    print("🤖 AUTOMATIC STRATEGY SELECTION DEMONSTRATION")
    print("=" * 60)
    
    trainer = MultiGPUTrainer()
    
    # Create model and dataset
    model = SimpleNeuralNetwork()
    dataset = DummyDataset(num_samples=1000)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Setup optimizer and loss
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    print("🚀 Starting training with automatic strategy selection...")
    start_time = time.time()
    
    # Train with auto strategy selection
    training_metrics = trainer.train_with_multi_gpu(
        model=model,
        train_loader=train_loader,
        optimizer=optimizer,
        criterion=criterion,
        num_epochs=5,
        strategy='auto',  # Automatic selection
        use_mixed_precision=True
    )
    
    training_time = time.time() - start_time
    
    print(f"✅ Auto-strategy training completed in {training_time:.2f}s")
    print(f"Selected Strategy: {training_metrics['strategy_used']}")
    print(f"Final Loss: {training_metrics['final_loss']:.4f}")
    print(f"Total Training Time: {training_metrics['total_training_time']:.2f}s")
    
    return training_metrics


def demonstrate_batch_size_optimization():
    """Demonstrate batch size optimization for multi-GPU."""
    print("\n" + "=" * 60)
    print("⚡ BATCH SIZE OPTIMIZATION DEMONSTRATION")
    print("=" * 60)
    
    if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
        print("❌ Multi-GPU batch optimization requires at least 2 GPUs")
        return
    
    trainer = MultiGPUTrainer()
    gpu_info = trainer.get_gpu_info()
    
    # Test different batch sizes
    batch_sizes = [16, 32, 64, 128]
    results = {}
    
    for batch_size in batch_sizes:
        print(f"\n🧪 Testing batch size: {batch_size}")
        
        # Create model and dataset
        model = SimpleNeuralNetwork()
        dataset = DummyDataset(num_samples=1000)
        train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Setup optimizer and loss
        optimizer = optim.Adam(model.parameters(), lr=1e-4)
        criterion = nn.CrossEntropyLoss()
        
        try:
            # Train with current batch size
            training_metrics = trainer.train_with_multi_gpu(
                model=model,
                train_loader=train_loader,
                optimizer=optimizer,
                criterion=criterion,
                num_epochs=3,  # Shorter for testing
                strategy='auto',
                use_mixed_precision=True
            )
            
            results[batch_size] = {
                'final_loss': training_metrics['final_loss'],
                'training_time': training_metrics['total_training_time'],
                'success': True
            }
            
            print(f"  ✅ Success - Loss: {training_metrics['final_loss']:.4f}, Time: {training_metrics['total_training_time']:.2f}s")
            
        except Exception as e:
            results[batch_size] = {
                'error': str(e),
                'success': False
            }
            print(f"  ❌ Failed - {e}")
    
    # Find optimal batch size
    successful_results = {k: v for k, v in results.items() if v['success']}
    if successful_results:
        optimal_batch_size = min(successful_results.keys(), 
                               key=lambda x: successful_results[x]['training_time'])
        
        print(f"\n🎯 Optimal batch size: {optimal_batch_size}")
        print(f"   Training time: {successful_results[optimal_batch_size]['training_time']:.2f}s")
        print(f"   Final loss: {successful_results[optimal_batch_size]['final_loss']:.4f}")
    
    return results


def demonstrate_training_metrics():
    """Demonstrate comprehensive training metrics."""
    print("\n" + "=" * 60)
    print("📊 TRAINING METRICS DEMONSTRATION")
    print("=" * 60)
    
    trainer = MultiGPUTrainer()
    
    # Create model and dataset
    model = SimpleNeuralNetwork()
    dataset = DummyDataset(num_samples=1000)
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Setup optimizer and loss
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    print("🚀 Starting training with comprehensive metrics...")
    
    # Train with detailed metrics
    training_metrics = trainer.train_with_multi_gpu(
        model=model,
        train_loader=train_loader,
        optimizer=optimizer,
        criterion=criterion,
        num_epochs=5,
        strategy='auto',
        use_mixed_precision=True
    )
    
    print("\n📈 Training Metrics Summary:")
    print(f"  Strategy Used: {training_metrics['strategy_used']}")
    print(f"  Total Training Time: {training_metrics['total_training_time']:.2f}s")
    print(f"  Final Loss: {training_metrics['final_loss']:.4f}")
    print(f"  Number of Epochs: {len(training_metrics['epochs'])}")
    
    if 'train_losses' in training_metrics:
        losses = training_metrics['train_losses']
        print(f"  Loss Progression: {[f'{loss:.4f}' for loss in losses]}")
        print(f"  Best Loss: {min(losses):.4f}")
        print(f"  Loss Improvement: {losses[0] - losses[-1]:.4f}")
    
    if 'gpu_utilization' in training_metrics:
        utilizations = training_metrics['gpu_utilization']
        print(f"  GPU Utilization: {np.mean(utilizations):.1f}% (avg)")
        print(f"  GPU Utilization Range: {min(utilizations):.1f}% - {max(utilizations):.1f}%")
    
    if 'memory_usage' in training_metrics:
        memory_usage = training_metrics['memory_usage']
        print(f"  Memory Usage: {np.mean(memory_usage):.2f} GB (avg)")
        print(f"  Peak Memory: {max(memory_usage):.2f} GB")
    
    return training_metrics


def demonstrate_multi_gpu_status():
    """Demonstrate multi-GPU status monitoring."""
    print("\n" + "=" * 60)
    print("📊 MULTI-GPU STATUS MONITORING")
    print("=" * 60)
    
    trainer = MultiGPUTrainer()
    
    # Get initial status
    print("🔍 Getting initial multi-GPU status...")
    initial_status = trainer.get_multi_gpu_status()
    
    print(f"Current Strategy: {initial_status['current_strategy']}")
    print(f"Monitoring Active: {initial_status['monitoring_active']}")
    
    if 'gpu_info' in initial_status:
        gpu_info = initial_status['gpu_info']
        print(f"GPU Count: {gpu_info['gpu_count']}")
        print(f"Multi-GPU Available: {gpu_info['multi_gpu_available']}")
    
    if 'current_metrics' in initial_status:
        metrics = initial_status['current_metrics']
        if metrics:
            print(f"Current Memory Usage: {metrics.get('memory_used_gb', 0):.2f} GB")
            print(f"Current GPU Utilization: {metrics.get('utilization', 0):.1f}%")
    
    # Start monitoring
    print("\n📈 Starting GPU monitoring...")
    trainer.start_monitoring()
    
    # Simulate some work
    print("🔄 Simulating GPU work...")
    time.sleep(3)
    
    # Get status during monitoring
    print("📊 Getting status during monitoring...")
    monitoring_status = trainer.get_multi_gpu_status()
    
    print(f"Monitoring Active: {monitoring_status['monitoring_active']}")
    print(f"Monitoring History Length: {len(monitoring_status['monitoring_history'])}")
    
    # Stop monitoring
    print("⏹️ Stopping GPU monitoring...")
    trainer.stop_monitoring()
    
    # Get final status
    print("📊 Getting final status...")
    final_status = trainer.get_multi_gpu_status()
    print(f"Monitoring Active: {final_status['monitoring_active']}")
    
    return {
        'initial': initial_status,
        'monitoring': monitoring_status,
        'final': final_status
    }


def demonstrate_distributed_cleanup():
    """Demonstrate distributed training cleanup."""
    print("\n" + "=" * 60)
    print("🧹 DISTRIBUTED TRAINING CLEANUP")
    print("=" * 60)
    
    trainer = MultiGPUTrainer()
    
    # Simulate some training
    if torch.cuda.is_available() and torch.cuda.device_count() >= 2:
        print("🚀 Running brief training session...")
        
        model = SimpleNeuralNetwork()
        dataset = DummyDataset(num_samples=100)
        train_loader = DataLoader(dataset, batch_size=16, shuffle=True)
        optimizer = optim.Adam(model.parameters(), lr=1e-4)
        criterion = nn.CrossEntropyLoss()
        
        # Quick training
        training_metrics = trainer.train_with_multi_gpu(
            model=model,
            train_loader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            num_epochs=2,
            strategy='auto',
            use_mixed_precision=True
        )
        
        print(f"✅ Training completed: {training_metrics['strategy_used']}")
    
    # Perform cleanup
    print("🧹 Performing cleanup...")
    trainer.cleanup()
    
    print("✅ Cleanup completed successfully")
    
    return True


def main():
    """Run all demonstrations."""
    print("🚀 MULTI-GPU TRAINING DEMONSTRATION SUITE")
    print("=" * 80)
    
    # Check CUDA availability
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU Count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            print(f"  GPU {i}: {props.name}")
    
    print("\n" + "=" * 80)
    
    # Run demonstrations
    demonstrations = [
        ("GPU Information", demonstrate_gpu_info),
        ("DataParallel Training", demonstrate_data_parallel),
        ("DistributedDataParallel Training", demonstrate_distributed_data_parallel),
        ("Auto Strategy Selection", demonstrate_auto_strategy_selection),
        ("Batch Size Optimization", demonstrate_batch_size_optimization),
        ("Training Metrics", demonstrate_training_metrics),
        ("Multi-GPU Status", demonstrate_multi_gpu_status),
        ("Distributed Cleanup", demonstrate_distributed_cleanup),
    ]
    
    results = {}
    
    for name, demo_func in demonstrations:
        try:
            print(f"\n🎯 Running: {name}")
            result = demo_func()
            results[name] = {"success": True, "result": result}
            print(f"✅ {name} completed successfully")
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results[name] = {"success": False, "error": str(e)}
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 DEMONSTRATION SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    print(f"Successful Demonstrations: {successful}/{total}")
    
    for name, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"{status} {name}")
    
    print(f"\n🎉 Multi-GPU training demonstration completed!")
    print(f"   Success Rate: {successful/total*100:.1f}%")
    
    return results


if __name__ == "__main__":
    main() 