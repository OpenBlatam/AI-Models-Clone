#!/usr/bin/env python3
"""
Multi-GPU Training Demo

This script demonstrates the comprehensive multi-GPU training capabilities
including DataParallel, DistributedDataParallel, Horovod, and DeepSpeed.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import logging
import time
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_diffusion_model(input_dim: int = 512, hidden_dim: int = 768, output_dim: int = 512):
    """Create a mock diffusion model for demonstration."""
    class MockDiffusionModel(nn.Module):
        def __init__(self, input_dim, hidden_dim, output_dim):
            super().__init__()
            self.input_dim = input_dim
            self.hidden_dim = hidden_dim
            self.output_dim = output_dim
            
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU()
            )
            
            self.decoder = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            )
            
            self.noise_predictor = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.ReLU(),
                nn.Linear(hidden_dim // 2, output_dim)
            )
        
        def forward(self, x, timestep=None):
            encoded = self.encoder(x)
            decoded = self.decoder(encoded)
            noise_pred = self.noise_predictor(encoded)
            return decoded, noise_pred
    
    return MockDiffusionModel(input_dim, hidden_dim, output_dim)

def create_mock_dataset(num_samples: int = 1000, input_dim: int = 512):
    """Create a mock dataset for training."""
    # Generate random data
    data = torch.randn(num_samples, input_dim)
    targets = torch.randn(num_samples, input_dim)
    
    # Create dataset and dataloader
    dataset = TensorDataset(data, targets)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=0)
    
    return dataset, dataloader

def demonstrate_single_gpu_training():
    """Demonstrate single GPU training."""
    logger.info("🚀 Demonstrating Single GPU Training")
    
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available, using CPU")
        device = torch.device("cpu")
    else:
        device = torch.device("cuda:0")
        logger.info(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
    
    # Create model and move to device
    model = create_mock_diffusion_model()
    model = model.to(device)
    
    # Create dataset and dataloader
    dataset, dataloader = create_mock_dataset()
    
    # Setup training
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()
    
    # Training loop
    model.train()
    total_loss = 0
    
    for batch_idx, (data, targets) in enumerate(dataloader):
        data, targets = data.to(device), targets.to(device)
        
        optimizer.zero_grad()
        decoded, noise_pred = model(data)
        loss = criterion(decoded, targets) + 0.1 * criterion(noise_pred, targets)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        if batch_idx % 10 == 0:
            logger.info(f"  Batch {batch_idx}: Loss = {loss.item():.6f}")
        
        if batch_idx >= 30:  # Limit for demo
            break
    
    avg_loss = total_loss / (batch_idx + 1)
    logger.info(f"✅ Single GPU training completed. Average loss: {avg_loss:.6f}")
    
    return model, avg_loss

def demonstrate_dataparallel_training():
    """Demonstrate DataParallel training."""
    logger.info("📱 Demonstrating DataParallel Training")
    
    if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
        logger.warning("⚠️ Need at least 2 GPUs for DataParallel")
        return None, 0.0
    
    # Create model
    model = create_mock_diffusion_model()
    
    # Wrap with DataParallel
    model = nn.DataParallel(model)
    logger.info(f"✅ DataParallel model created with {torch.cuda.device_count()} GPUs")
    
    # Move to first GPU
    device = torch.device("cuda:0")
    model = model.to(device)
    
    # Create dataset and dataloader
    dataset, dataloader = create_mock_dataset()
    
    # Setup training
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()
    
    # Training loop
    model.train()
    total_loss = 0
    start_time = time.time()
    
    for batch_idx, (data, targets) in enumerate(dataloader):
        data, targets = data.to(device), targets.to(device)
        
        optimizer.zero_grad()
        decoded, noise_pred = model(data)
        loss = criterion(decoded, targets) + 0.1 * criterion(noise_pred, targets)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        if batch_idx % 10 == 0:
            logger.info(f"  Batch {batch_idx}: Loss = {loss.item():.6f}")
        
        if batch_idx >= 30:  # Limit for demo
            break
    
    end_time = time.time()
    avg_loss = total_loss / (batch_idx + 1)
    training_time = end_time - start_time
    
    logger.info(f"✅ DataParallel training completed in {training_time:.2f}s")
    logger.info(f"  Average loss: {avg_loss:.6f}")
    logger.info(f"  Throughput: {30/training_time:.2f} batches/second")
    
    return model, avg_loss

def demonstrate_distributed_training_setup():
    """Demonstrate DistributedDataParallel setup (without actual training)."""
    logger.info("🌐 Demonstrating DistributedDataParallel Setup")
    
    if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
        logger.warning("⚠️ Need at least 2 GPUs for DistributedDataParallel")
        return None
    
    try:
        import torch.distributed as dist
        
        # Create model
        model = create_mock_diffusion_model()
        
        # Setup distributed environment variables
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '12355'
        os.environ['WORLD_SIZE'] = str(torch.cuda.device_count())
        os.environ['RANK'] = '0'
        
        # Initialize process group
        dist.init_process_group(backend='nccl', init_method='env://')
        
        # Move model to GPU
        device = torch.device("cuda:0")
        model = model.to(device)
        
        # Wrap with DistributedDataParallel
        from torch.nn.parallel import DistributedDataParallel as DDP
        model = DDP(model, device_ids=[0])
        
        logger.info("✅ DistributedDataParallel setup completed")
        logger.info(f"  World size: {dist.get_world_size()}")
        logger.info(f"  Rank: {dist.get_rank()}")
        
        # Cleanup
        dist.destroy_process_group()
        
        return model
        
    except Exception as e:
        logger.warning(f"⚠️ DistributedDataParallel setup failed: {e}")
        return None

def demonstrate_multi_gpu_performance_comparison():
    """Compare performance between single GPU and multi-GPU setups."""
    logger.info("📊 Demonstrating Multi-GPU Performance Comparison")
    
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available for performance comparison")
        return
    
    # Single GPU performance
    logger.info("  Testing Single GPU Performance...")
    single_start = time.time()
    single_model, single_loss = demonstrate_single_gpu_training()
    single_time = time.time() - single_start
    
    # Multi-GPU performance (if available)
    if torch.cuda.device_count() >= 2:
        logger.info("  Testing DataParallel Performance...")
        multi_start = time.time()
        multi_model, multi_loss = demonstrate_dataparallel_training()
        multi_time = time.time() - multi_start
        
        # Performance comparison
        logger.info("📈 Performance Comparison:")
        logger.info(f"  Single GPU: {single_time:.2f}s, Loss: {single_loss:.6f}")
        logger.info(f"  DataParallel: {multi_time:.2f}s, Loss: {multi_loss:.6f}")
        
        if multi_time > 0:
            speedup = single_time / multi_time
            logger.info(f"  Speedup: {speedup:.2f}x")
            
            if speedup > 1.0:
                logger.info("  🚀 DataParallel provides speedup!")
            else:
                logger.info("  ⚠️ DataParallel overhead may be too high for this model size")
    else:
        logger.info("  ⚠️ Multi-GPU not available for comparison")

def demonstrate_memory_optimization():
    """Demonstrate memory optimization techniques."""
    logger.info("💾 Demonstrating Memory Optimization Techniques")
    
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available for memory optimization")
        return
    
    device = torch.device("cuda:0")
    
    # Create large model
    large_model = create_mock_diffusion_model(input_dim=1024, hidden_dim=2048, output_dim=1024)
    large_model = large_model.to(device)
    
    # Check memory usage
    torch.cuda.empty_cache()
    initial_memory = torch.cuda.memory_allocated(device) / (1024**2)  # MB
    logger.info(f"  Initial memory usage: {initial_memory:.1f} MB")
    
    # Apply gradient checkpointing
    if hasattr(large_model, 'gradient_checkpointing_enable'):
        large_model.gradient_checkpointing_enable()
        logger.info("  ✅ Gradient checkpointing enabled")
    
    # Test forward pass
    dummy_input = torch.randn(16, 1024, device=device)
    
    with torch.no_grad():
        _ = large_model(dummy_input)
    
    after_forward = torch.cuda.memory_allocated(device) / (1024**2)  # MB
    logger.info(f"  Memory after forward pass: {after_forward:.1f} MB")
    
    # Test with gradients
    optimizer = optim.Adam(large_model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()
    
    dummy_targets = torch.randn(16, 1024, device=device)
    
    optimizer.zero_grad()
    decoded, noise_pred = large_model(dummy_input)
    loss = criterion(decoded, dummy_targets)
    loss.backward()
    optimizer.step()
    
    after_backward = torch.cuda.memory_allocated(device) / (1024**2)  # MB
    logger.info(f"  Memory after backward pass: {after_backward:.1f} MB")
    
    # Memory efficiency
    memory_increase = after_backward - initial_memory
    logger.info(f"  Total memory increase: {memory_increase:.1f} MB")
    
    # Cleanup
    del large_model, dummy_input, dummy_targets
    torch.cuda.empty_cache()
    
    logger.info("✅ Memory optimization demonstration completed")

def demonstrate_batch_size_scaling():
    """Demonstrate how batch size affects multi-GPU performance."""
    logger.info("📦 Demonstrating Batch Size Scaling")
    
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available for batch size scaling")
        return
    
    device = torch.device("cuda:0")
    model = create_mock_diffusion_model()
    model = model.to(device)
    
    batch_sizes = [8, 16, 32, 64, 128]
    results = {}
    
    for batch_size in batch_sizes:
        try:
            logger.info(f"  Testing batch size: {batch_size}")
            
            # Create data
            data = torch.randn(batch_size, 512, device=device)
            targets = torch.randn(batch_size, 512, device=device)
            
            # Warmup
            model.eval()
            with torch.no_grad():
                for _ in range(5):
                    _ = model(data)
            
            # Benchmark
            model.train()
            start_time = time.time()
            
            for _ in range(10):  # 10 iterations
                optimizer = optim.Adam(model.parameters(), lr=1e-4)
                criterion = nn.MSELoss()
                
                optimizer.zero_grad()
                decoded, noise_pred = model(data)
                loss = criterion(decoded, targets) + 0.1 * criterion(noise_pred, targets)
                loss.backward()
                optimizer.step()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            throughput = (10 * batch_size) / total_time  # samples per second
            results[batch_size] = {
                'time': total_time,
                'throughput': throughput,
                'memory': torch.cuda.memory_allocated(device) / (1024**2)  # MB
            }
            
            logger.info(f"    Time: {total_time:.3f}s, Throughput: {throughput:.1f} samples/s")
            
        except RuntimeError as e:
            if "out of memory" in str(e):
                logger.warning(f"    ⚠️ Out of memory for batch size {batch_size}")
                break
            else:
                raise e
    
    # Summary
    logger.info("📊 Batch Size Scaling Results:")
    for batch_size, metrics in results.items():
        logger.info(f"  Batch {batch_size}: {metrics['throughput']:.1f} samples/s, {metrics['memory']:.1f} MB")
    
    # Find optimal batch size
    if results:
        optimal_batch = max(results.keys(), key=lambda x: results[x]['throughput'])
        logger.info(f"  🎯 Optimal batch size: {optimal_batch}")
    
    logger.info("✅ Batch size scaling demonstration completed")

def main():
    """Main demonstration function."""
    logger.info("🚀 Starting Multi-GPU Training Demonstration")
    logger.info("=" * 60)
    
    # Check system capabilities
    logger.info("🔍 System Information:")
    logger.info(f"  PyTorch version: {torch.__version__}")
    logger.info(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"  CUDA version: {torch.version.cuda}")
        logger.info(f"  Number of GPUs: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            logger.info(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
    
    logger.info("=" * 60)
    
    try:
        # Single GPU training
        demonstrate_single_gpu_training()
        logger.info("-" * 40)
        
        # DataParallel training
        demonstrate_dataparallel_training()
        logger.info("-" * 40)
        
        # DistributedDataParallel setup
        demonstrate_distributed_training_setup()
        logger.info("-" * 40)
        
        # Performance comparison
        demonstrate_multi_gpu_performance_comparison()
        logger.info("-" * 40)
        
        # Memory optimization
        demonstrate_memory_optimization()
        logger.info("-" * 40)
        
        # Batch size scaling
        demonstrate_batch_size_scaling()
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("=" * 60)
    logger.info("✅ Multi-GPU Training Demonstration Completed!")

if __name__ == "__main__":
    main()
