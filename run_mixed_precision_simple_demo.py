#!/usr/bin/env python3
"""
Simple Mixed Precision Training Demo with torch.cuda.amp

This script demonstrates the core mixed precision functionality
without complex training loops that might cause gradient issues.
"""

import torch
import torch.nn as nn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demonstrate_basic_mixed_precision():
    """Demonstrate basic mixed precision setup and usage."""
    logger.info("🔬 Demonstrating Basic Mixed Precision Training")
    
    # Check CUDA availability
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available - using CPU for demonstration")
        device = torch.device("cpu")
        # For CPU, we'll simulate mixed precision concepts
        logger.info("  Note: Mixed precision benefits are most apparent on GPU")
    else:
        device = torch.device("cuda")
        logger.info(f"🚀 CUDA available: {torch.cuda.get_device_name(0)}")
    
    # Create a simple model
    model = nn.Sequential(
        nn.Linear(100, 200),
        nn.ReLU(),
        nn.Linear(200, 100)
    ).to(device)
    
    # Ensure parameters require gradients
    for param in model.parameters():
        param.requires_grad = True
    
    # Create optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()
    
    # Create dummy data
    data = torch.randn(32, 100, device=device)
    target = torch.randn(32, 100, device=device)
    
    logger.info("✅ Model and data created successfully")
    logger.info(f"  - Device: {device}")
    logger.info(f"  - Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    logger.info(f"  - Data shape: {data.shape}")
    
    # Demonstrate mixed precision if CUDA is available
    if torch.cuda.is_available():
        demonstrate_cuda_mixed_precision(model, optimizer, criterion, data, target)
    else:
        demonstrate_cpu_training(model, optimizer, criterion, data, target)

def demonstrate_cuda_mixed_precision(model, optimizer, criterion, data, target):
    """Demonstrate CUDA mixed precision training."""
    logger.info("🚀 Demonstrating CUDA Mixed Precision Training")
    
    # Initialize GradScaler
    scaler = torch.cuda.amp.GradScaler()
    logger.info("✅ GradScaler initialized")
    
    # Training loop with mixed precision
    model.train()
    
    for step in range(5):  # Just a few steps for demo
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass with autocast
        with torch.cuda.amp.autocast():
            output = model(data)
            loss = criterion(output, target)
        
        logger.info(f"  Step {step + 1}: Loss = {loss.item():.6f}")
        logger.info(f"    Output dtype: {output.dtype}")
        logger.info(f"    Loss dtype: {loss.dtype}")
        
        # Scale loss for mixed precision
        scaled_loss = scaler.scale(loss)
        
        # Backward pass
        scaled_loss.backward()
        
        # Unscale gradients
        scaler.unscale_(optimizer)
        
        # Step optimizer
        scaler.step(optimizer)
        
        # Update scaler
        scaler.update()
        
        # Show scaler state
        logger.info(f"    Scaler scale: {scaler.get_scale():.2f}")
    
    logger.info("✅ CUDA mixed precision training completed")
    logger.info(f"  Final scaler scale: {scaler.get_scale():.2f}")

def demonstrate_cpu_training(model, optimizer, criterion, data, target):
    """Demonstrate CPU training (without mixed precision)."""
    logger.info("🖥️ Demonstrating CPU Training (No Mixed Precision)")
    
    # Regular training loop
    model.train()
    
    for step in range(5):  # Just a few steps for demo
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        output = model(data)
        loss = criterion(output, target)
        
        logger.info(f"  Step {step + 1}: Loss = {loss.item():.6f}")
        logger.info(f"    Output dtype: {output.dtype}")
        logger.info(f"    Loss dtype: {loss.dtype}")
        
        # Backward pass
        loss.backward()
        
        # Step optimizer
        optimizer.step()
    
    logger.info("✅ CPU training completed")

def demonstrate_mixed_precision_benefits():
    """Demonstrate the benefits of mixed precision training."""
    logger.info("📊 Demonstrating Mixed Precision Training Benefits")
    
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available - cannot demonstrate GPU benefits")
        logger.info("  Mixed precision benefits:")
        logger.info("    • Memory reduction: ~50% on GPU")
        logger.info("    • Training speedup: 1.3x-2x on modern GPUs")
        logger.info("    • Automatic gradient scaling")
        return
    
    # Create a larger model to show memory benefits
    large_model = nn.Sequential(
        *[nn.Linear(512, 1024) for _ in range(20)],
        nn.ReLU(),
        nn.Linear(1024, 512)
    ).to('cuda')
    
    # Measure memory usage
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    
    # FP32 forward pass
    start_memory = torch.cuda.memory_allocated()
    dummy_input = torch.randn(64, 512, device='cuda', dtype=torch.float32)
    
    with torch.no_grad():
        _ = large_model(dummy_input)
    
    fp32_memory = torch.cuda.memory_allocated() - start_memory
    
    # FP16 forward pass (simulating mixed precision)
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    
    start_memory = torch.cuda.memory_allocated()
    dummy_input = torch.randn(64, 512, device='cuda', dtype=torch.float16)
    
    with torch.no_grad():
        _ = large_model(dummy_input)
    
    fp16_memory = torch.cuda.memory_allocated() - start_memory
    
    # Calculate savings
    memory_savings = ((fp32_memory - fp16_memory) / fp32_memory) * 100
    
    logger.info(f"  Memory Usage Comparison:")
    logger.info(f"    FP32: {fp32_memory / (1024**2):.2f} MB")
    logger.info(f"    FP16: {fp16_memory / (1024**2):.2f} MB")
    logger.info(f"    Savings: {memory_savings:.1f}%")

def demonstrate_autocast_context():
    """Demonstrate autocast context manager."""
    logger.info("🔄 Demonstrating Autocast Context Manager")
    
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available - autocast not available")
        return
    
    # Create simple model and data
    model = nn.Linear(100, 100).cuda()
    data = torch.randn(32, 100, device='cuda')
    
    # Without autocast (FP32)
    with torch.no_grad():
        output_fp32 = model(data)
    
    # With autocast (mixed precision)
    with torch.cuda.amp.autocast():
        output_fp16 = model(data)
    
    logger.info(f"  Output without autocast: {output_fp32.dtype}")
    logger.info(f"  Output with autocast: {output_fp16.dtype}")
    logger.info("✅ Autocast context manager demonstrated")

def demonstrate_grad_scaler():
    """Demonstrate GradScaler functionality."""
    logger.info("⚖️ Demonstrating GradScaler Functionality")
    
    if not torch.cuda.is_available():
        logger.warning("⚠️ CUDA not available - GradScaler not available")
        return
    
    # Create scaler
    scaler = torch.cuda.amp.GradScaler()
    
    # Show initial state
    logger.info(f"  Initial scale: {scaler.get_scale()}")
    
    # Simulate some training steps
    for step in range(3):
        # Create dummy loss
        loss = torch.tensor(1.0, device='cuda', requires_grad=True)
        
        # Scale loss
        scaled_loss = scaler.scale(loss)
        
        # Simulate backward pass
        scaled_loss.backward()
        
        # Update scaler
        scaler.update()
        
        logger.info(f"  Step {step + 1}: Scale = {scaler.get_scale():.2f}")
    
    logger.info("✅ GradScaler functionality demonstrated")

def main():
    """Run all mixed precision demonstrations."""
    logger.info("🎯 Simple Mixed Precision Training Demo with torch.cuda.amp")
    logger.info("=" * 60)
    
    # Check PyTorch version
    logger.info(f"📦 PyTorch version: {torch.__version__}")
    
    # Check CUDA availability
    if torch.cuda.is_available():
        logger.info(f"🚀 CUDA available: {torch.cuda.get_device_name(0)}")
        logger.info(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
        logger.info(f"  CUDA version: {torch.version.cuda}")
    else:
        logger.warning("⚠️ CUDA not available - some features will be limited")
    
    logger.info("")
    
    # Run demonstrations
    demonstrate_basic_mixed_precision()
    demonstrate_mixed_precision_benefits()
    demonstrate_autocast_context()
    demonstrate_grad_scaler()
    
    logger.info("")
    logger.info("🎉 Simple Mixed Precision Training Demo Completed!")
    logger.info("")
    logger.info("📚 Key Takeaways:")
    logger.info("  • Mixed precision reduces memory usage by ~50%")
    logger.info("  • Training speedup of 1.3x-2x on modern GPUs")
    logger.info("  • Automatic gradient scaling with GradScaler")
    logger.info("  • Autocast context handles precision conversion")
    logger.info("  • Easy integration with existing training loops")

if __name__ == "__main__":
    main()
