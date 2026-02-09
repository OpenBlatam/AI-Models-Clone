#!/usr/bin/env python3
"""
Mixed Precision Training Demo with torch.cuda.amp

This script demonstrates the implementation of mixed precision training using
torch.cuda.amp (Automatic Mixed Precision) in the diffusion performance optimizer.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import time
import logging
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_diffusion_model():
    """Create a mock diffusion model for demonstration."""
    class MockDiffusionModel(nn.Module):
        def __init__(self, input_dim=512, hidden_dim=1024, output_dim=512):
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU()
            )
            self.noise_predictor = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            )
            self.decoder = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            )
            
        def forward(self, x):
            encoded = self.encoder(x)
            noise_pred = self.noise_predictor(encoded)
            decoded = self.decoder(encoded)
            return decoded, noise_pred
    
    return MockDiffusionModel()

def create_mock_dataset(num_samples=1000, input_dim=512):
    """Create a mock dataset for demonstration."""
    class MockDataset:
        def __init__(self, num_samples, input_dim):
            self.num_samples = num_samples
            self.input_dim = input_dim
            
        def __len__(self):
            return self.num_samples
            
        def __getitem__(self, idx):
            data = torch.randn(self.input_dim)
            target = torch.randn(self.input_dim)
            return data, target
    
    dataset = MockDataset(num_samples, input_dim)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
    return dataset, dataloader

def demonstrate_basic_mixed_precision():
    """Demonstrate basic mixed precision training setup."""
    logger.info("🔬 Demonstrating Basic Mixed Precision Training Setup")
    
    try:
        from core.diffusion_performance_optimizer import (
            DiffusionPerformanceOptimizer, 
            PerformanceConfig, 
            TrainingAcceleration
        )
        
        # Create configuration with mixed precision enabled
        config = PerformanceConfig(
            optimization_level="advanced",
            training_accelerations=[TrainingAcceleration.MIXED_PRECISION],
            enable_mixed_precision=True
        )
        
        # Create optimizer
        optimizer = DiffusionPerformanceOptimizer(config)
        
        # Check mixed precision status
        mp_info = optimizer.get_mixed_precision_info()
        logger.info(f"  Mixed Precision Status: {mp_info}")
        
        if mp_info["enabled"]:
            logger.info("✅ Mixed precision training is properly configured")
            logger.info(f"  - GradScaler scale: {mp_info['scaler_state']}")
            logger.info(f"  - Autocast enabled: {mp_info['autocast_enabled']}")
            logger.info(f"  - Expected memory savings: {mp_info['memory_savings']}")
            logger.info(f"  - Expected speedup: {mp_info['training_speedup']}")
        else:
            logger.warning("⚠️ Mixed precision not available")
        
        return optimizer
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import performance optimizer: {e}")
        logger.info("  This is expected if the core modules are not available")
        return None

def demonstrate_mixed_precision_training(optimizer):
    """Demonstrate mixed precision training workflow."""
    if optimizer is None:
        logger.warning("⚠️ Skipping training demo - no optimizer available")
        return
    
    logger.info("🚀 Demonstrating Mixed Precision Training Workflow")
    
    # Create model and dataset
    model = create_mock_diffusion_model()
    dataset, dataloader = create_mock_dataset()
    
    # Setup training
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    # Create optimizer and criterion
    train_optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()
    
    # Training loop with mixed precision
    model.train()
    total_loss = 0
    start_time = time.time()
    
    logger.info("  Starting mixed precision training...")
    
    for batch_idx, (data, targets) in enumerate(dataloader):
        data, targets = data.to(device), targets.to(device)
        
        # Zero gradients
        train_optimizer.zero_grad()
        
        # Forward pass with autocast
        with optimizer.create_autocast_context():
            decoded, noise_pred = model(data)
            loss = criterion(decoded, targets) + 0.1 * criterion(noise_pred, targets)
        
        # Scale loss for mixed precision
        scaled_loss = optimizer.scale_loss(loss)
        
        # Backward pass
        scaled_loss.backward()
        
        # Unscale gradients
        optimizer.unscale_optimizer(train_optimizer)
        
        # Step optimizer
        optimizer.step_optimizer(train_optimizer)
        
        # Update scaler
        optimizer.update_scaler()
        
        total_loss += loss.item()
        
        if batch_idx % 10 == 0:
            logger.info(f"    Batch {batch_idx}: Loss = {loss.item():.6f}")
        
        if batch_idx >= 20:  # Limit for demo
            break
    
    end_time = time.time()
    avg_loss = total_loss / (batch_idx + 1)
    training_time = end_time - start_time
    
    logger.info(f"✅ Mixed precision training completed in {training_time:.2f}s")
    logger.info(f"  Average loss: {avg_loss:.6f}")
    logger.info(f"  Throughput: {20/training_time:.2f} batches/second")
    
    # Show mixed precision info after training
    mp_info = optimizer.get_mixed_precision_info()
    if mp_info["enabled"]:
        logger.info(f"  Final scaler scale: {mp_info['scaler_state']}")

def demonstrate_mixed_precision_context_manager(optimizer):
    """Demonstrate the mixed precision context manager."""
    if optimizer is None:
        logger.warning("⚠️ Skipping context manager demo - no optimizer available")
        return
    
    logger.info("🔄 Demonstrating Mixed Precision Context Manager")
    
    try:
        from core.diffusion_performance_optimizer import mixed_precision_context
        
        # Create model
        model = create_mock_diffusion_model()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        
        # Test context manager
        with mixed_precision_context(optimizer) as mp_optimizer:
            logger.info("  Inside mixed precision context")
            
            # Create dummy data
            dummy_input = torch.randn(1, 512, device=device)
            
            # Forward pass should use mixed precision
            with mp_optimizer.create_autocast_context():
                output = model(dummy_input)
            
            logger.info(f"  Output shape: {output[0].shape}")
            logger.info(f"  Output dtype: {output[0].dtype}")
        
        logger.info("✅ Context manager demo completed")
        
    except ImportError:
        logger.warning("⚠️ Context manager not available")

def demonstrate_mixed_precision_benefits():
    """Demonstrate the benefits of mixed precision training."""
    logger.info("📊 Demonstrating Mixed Precision Training Benefits")
    
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available, cannot demonstrate GPU benefits")
        return
    
    # Create a larger model to show memory benefits
    large_model = create_mock_diffusion_model()
    large_model.encoder = nn.Sequential(
        *[nn.Linear(512, 1024) for _ in range(10)],
        nn.ReLU()
    )
    
    device = torch.device("cuda")
    large_model = large_model.to(device)
    
    # Measure memory usage
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    
    # FP32 training
    start_memory = torch.cuda.memory_allocated(device)
    
    # Simulate FP32 forward pass
    dummy_input = torch.randn(32, 512, device=device, dtype=torch.float32)
    with torch.no_grad():
        _ = large_model(dummy_input)
    
    fp32_memory = torch.cuda.memory_allocated(device) - start_memory
    
    # FP16 training (mixed precision)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    
    start_memory = torch.cuda.memory_allocated(device)
    
    # Simulate FP16 forward pass
    dummy_input = torch.randn(32, 512, device=device, dtype=torch.float16)
    with torch.no_grad():
        _ = large_model(dummy_input)
    
    fp16_memory = torch.cuda.memory_allocated(device) - start_memory
    
    # Calculate savings
    memory_savings = ((fp32_memory - fp16_memory) / fp32_memory) * 100
    
    logger.info(f"  Memory Usage Comparison:")
    logger.info(f"    FP32: {fp32_memory / (1024**2):.2f} MB")
    logger.info(f"    FP16: {fp16_memory / (1024**2):.2f} MB")
    logger.info(f"    Savings: {memory_savings:.1f}%")
    
    # Performance comparison
    num_iterations = 100
    dummy_input_fp32 = torch.randn(32, 512, device=device, dtype=torch.float32)
    dummy_input_fp16 = torch.randn(32, 512, device=device, dtype=torch.float16)
    
    # FP32 timing
    torch.cuda.synchronize()
    start_time = time.time()
    
    with torch.no_grad():
        for _ in range(num_iterations):
            _ = large_model(dummy_input_fp32)
    
    torch.cuda.synchronize()
    fp32_time = time.time() - start_time
    
    # FP16 timing
    torch.cuda.synchronize()
    start_time = time.time()
    
    with torch.no_grad():
        for _ in range(num_iterations):
            _ = large_model(dummy_input_fp16)
    
    torch.cuda.synchronize()
    fp16_time = time.time() - start_time
    
    # Calculate speedup
    speedup = fp32_time / fp16_time
    
    logger.info(f"  Performance Comparison:")
    logger.info(f"    FP32: {fp32_time:.4f}s for {num_iterations} iterations")
    logger.info(f"    FP16: {fp16_time:.4f}s for {num_iterations} iterations")
    logger.info(f"    Speedup: {speedup:.2f}x")

def demonstrate_mixed_precision_integration():
    """Demonstrate integration with existing training systems."""
    logger.info("🔗 Demonstrating Mixed Precision Integration")
    
    try:
        from core.diffusion_training_evaluation_system import DiffusionTrainer, TrainingConfig
        
        # Create training config with mixed precision
        config = TrainingConfig(
            batch_size=32,
            learning_rate=1e-4,
            num_epochs=2,
            mixed_precision=True,  # Enable mixed precision
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        
        logger.info("✅ Successfully created training config with mixed precision")
        logger.info(f"  - Mixed precision enabled: {config.mixed_precision}")
        logger.info(f"  - Device: {config.device}")
        
        # Note: In a real scenario, you would create the trainer and run training
        # For demo purposes, we just show the configuration
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import training system: {e}")
        logger.info("  This is expected if the core modules are not available")

def main():
    """Run all mixed precision demonstrations."""
    logger.info("🎯 Mixed Precision Training Demo with torch.cuda.amp")
    logger.info("=" * 60)
    
    # Check CUDA availability
    if torch.cuda.is_available():
        logger.info(f"🚀 CUDA available: {torch.cuda.get_device_name(0)}")
        logger.info(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
    else:
        logger.warning("⚠️ CUDA not available - some features will be limited")
    
    logger.info("")
    
    # Run demonstrations
    optimizer = demonstrate_basic_mixed_precision()
    
    if optimizer:
        demonstrate_mixed_precision_training(optimizer)
        demonstrate_mixed_precision_context_manager(optimizer)
    
    demonstrate_mixed_precision_benefits()
    demonstrate_mixed_precision_integration()
    
    logger.info("")
    logger.info("🎉 Mixed Precision Training Demo Completed!")
    logger.info("")
    logger.info("📚 Key Takeaways:")
    logger.info("  • Mixed precision reduces memory usage by ~50%")
    logger.info("  • Training speedup of 1.3x-2x on modern GPUs")
    logger.info("  • Automatic gradient scaling with GradScaler")
    logger.info("  • Seamless integration with existing training loops")
    logger.info("  • Context managers for easy adoption")

if __name__ == "__main__":
    main()
