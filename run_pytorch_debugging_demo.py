#!/usr/bin/env python3
"""
PyTorch Debugging Tools Demo

This script demonstrates the integration of PyTorch's built-in debugging tools,
specifically autograd.detect_anomaly(), into the diffusion training system.
"""

import torch
import torch.nn as nn
import numpy as np
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_model():
    """Create a mock model for demonstration purposes."""
    class MockDiffusionModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
            self.conv2 = nn.Conv2d(64, 64, 3, padding=1)
            self.conv3 = nn.Conv2d(64, 3, 3, padding=1)
            self.relu = nn.ReLU()
            
        def forward(self, x, timesteps, text_tokens=None):
            # Simulate diffusion model forward pass
            x = self.relu(self.conv1(x))
            x = self.relu(self.conv2(x))
            x = self.conv3(x)
            return x
    
    return MockDiffusionModel()

def create_mock_dataset(batch_size=2, image_size=64):
    """Create mock dataset for demonstration."""
    # Create mock images and text
    images = torch.randn(batch_size, 3, image_size, image_size)
    text_tokens = torch.randint(0, 1000, (batch_size, 77))  # Mock CLIP tokens
    
    return {
        'image': images,
        'text_tokens': text_tokens
    }

def demonstrate_autograd_anomaly_detection():
    """Demonstrate autograd.detect_anomaly() functionality."""
    logger.info("🔍 Demonstrating autograd.detect_anomaly() functionality...")
    
    # Create a simple model and data
    model = create_mock_model()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    # Create mock data
    batch = create_mock_dataset()
    images = batch['image']
    text_tokens = batch['text_tokens']
    
    logger.info("📊 Model parameters before training:")
    for name, param in model.named_parameters():
        logger.info(f"  {name}: {param.shape}, requires_grad={param.requires_grad}")
    
    # Demonstrate normal training without anomaly detection
    logger.info("\n🚀 Normal training (no anomaly detection):")
    try:
        for step in range(3):
            optimizer.zero_grad()
            
            # Forward pass
            output = model(images, torch.randint(0, 1000, (images.shape[0],)), text_tokens)
            loss = nn.functional.mse_loss(output, images)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            logger.info(f"  Step {step + 1}: Loss = {loss.item():.6f}")
            
    except Exception as e:
        logger.error(f"❌ Error during normal training: {e}")
    
    # Demonstrate training with anomaly detection
    logger.info("\n🔍 Training with autograd.detect_anomaly():")
    try:
        with torch.autograd.detect_anomaly():
            for step in range(3):
                optimizer.zero_grad()
                
                # Forward pass
                output = model(images, torch.randint(0, 1000, (images.shape[0],)), text_tokens)
                loss = nn.functional.mse_loss(output, images)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                logger.info(f"  Step {step + 1}: Loss = {loss.item():.6f}")
                
    except Exception as e:
        logger.error(f"❌ Error during anomaly detection training: {e}")
        logger.info("💡 autograd.detect_anomaly() caught the error and provided detailed information!")

def demonstrate_gradient_debugging():
    """Demonstrate gradient debugging functionality."""
    logger.info("\n🔍 Demonstrating gradient debugging...")
    
    model = create_mock_model()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    batch = create_mock_dataset()
    images = batch['image']
    text_tokens = batch['text_tokens']
    
    # Train for a few steps and monitor gradients
    for step in range(3):
        optimizer.zero_grad()
        
        # Forward pass
        output = model(images, torch.randint(0, 1000, (images.shape[0],)), text_tokens)
        loss = nn.functional.mse_loss(output, images)
        
        # Backward pass
        loss.backward()
        
        # Analyze gradients
        logger.info(f"\n📊 Gradient analysis for step {step + 1}:")
        total_grad_norm = 0
        param_count = 0
        
        for name, param in model.named_parameters():
            if param.grad is not None:
                grad_norm = param.grad.norm().item()
                grad_mean = param.grad.mean().item()
                grad_std = param.grad.std().item()
                has_nan = torch.isnan(param.grad).any().item()
                has_inf = torch.isinf(param.grad).any().item()
                
                total_grad_norm += grad_norm
                param_count += 1
                
                logger.info(f"  {name}:")
                logger.info(f"    - Grad norm: {grad_norm:.6f}")
                logger.info(f"    - Grad mean: {grad_mean:.6f}")
                logger.info(f"    - Grad std: {grad_std:.6f}")
                logger.info(f"    - Has NaN: {has_nan}")
                logger.info(f"    - Has Inf: {has_inf}")
                
                if has_nan or has_inf:
                    logger.warning(f"⚠️  WARNING: {name} has {'NaN' if has_nan else 'Inf'} values!")
        
        if param_count > 0:
            avg_grad_norm = total_grad_norm / param_count
            logger.info(f"  Average gradient norm: {avg_grad_norm:.6f}")
        
        optimizer.step()

def demonstrate_memory_profiling():
    """Demonstrate memory profiling functionality."""
    logger.info("\n💾 Demonstrating memory profiling...")
    
    if not torch.cuda.is_available():
        logger.info("  CUDA not available, skipping memory profiling demo")
        return
    
    model = create_mock_model().cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    # Create data on GPU
    batch = create_mock_dataset()
    images = batch['image'].cuda()
    text_tokens = batch['text_tokens'].cuda()
    
    logger.info("📊 Memory usage before training:")
    logger.info(f"  Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
    logger.info(f"  Reserved: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
    
    # Train and monitor memory
    for step in range(3):
        optimizer.zero_grad()
        
        # Forward pass
        output = model(images, torch.randint(0, 1000, (images.shape[0],)).cuda(), text_tokens)
        loss = nn.functional.mse_loss(output, images)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        logger.info(f"\n  Step {step + 1} memory usage:")
        logger.info(f"    - Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
        logger.info(f"    - Reserved: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
        logger.info(f"    - Loss: {loss.item():.6f}")
    
    # Clear GPU memory
    del model, optimizer, images, text_tokens, output, loss
    torch.cuda.empty_cache()
    
    logger.info(f"\n  Memory after cleanup:")
    logger.info(f"    - Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
    logger.info(f"    - Reserved: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")

def demonstrate_performance_profiling():
    """Demonstrate performance profiling functionality."""
    logger.info("\n⏱️ Demonstrating performance profiling...")
    
    model = create_mock_model()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    batch = create_mock_dataset()
    images = batch['image']
    text_tokens = batch['text_tokens']
    
    # Profile different operations
    operations = [
        ("Forward pass", lambda: model(images, torch.randint(0, 1000, (images.shape[0],)), text_tokens)),
        ("Loss computation", lambda: nn.functional.mse_loss(images, images)),
        ("Backward pass", lambda: nn.functional.mse_loss(images, images).backward()),
        ("Optimizer step", lambda: optimizer.step())
    ]
    
    for op_name, operation in operations:
        # Warm up
        for _ in range(3):
            try:
                operation()
            except:
                pass
        
        # Profile
        times = []
        for _ in range(10):
            start_time = time.time()
            try:
                operation()
                times.append(time.time() - start_time)
            except:
                pass
        
        if times:
            avg_time = np.mean(times)
            std_time = np.std(times)
            logger.info(f"  {op_name}: {avg_time:.6f}s ± {std_time:.6f}s")

def demonstrate_integrated_debugging():
    """Demonstrate the integrated debugging system from the training class."""
    logger.info("\n🔧 Demonstrating integrated debugging system...")
    
    try:
        # Import the training system
        from core.diffusion_training_evaluation_system import DiffusionTrainer, TrainingConfig
        
        # Create a mock model
        model = create_mock_model()
        
        # Create training config with debugging enabled
        config = TrainingConfig(
            batch_size=2,
            learning_rate=1e-3,
            num_epochs=1,
            enable_autograd_anomaly=True,
            enable_gradient_debugging=True,
            enable_memory_profiling=True,
            enable_performance_profiling=True,
            autograd_anomaly_mode="default"
        )
        
        # Create trainer
        trainer = DiffusionTrainer(model, config, train_dataset=None, val_dataset=None)
        
        # Log debugging status
        trainer.log_debugging_info()
        
        # Enable/disable debugging dynamically
        logger.info("\n🔄 Dynamic debugging control:")
        trainer.disable_debugging()
        logger.info(f"  Debugging status: {trainer.get_debugging_status()}")
        
        trainer.enable_debugging(
            enable_autograd_anomaly=True,
            enable_gradient_debugging=True,
            autograd_anomaly_mode="trace"
        )
        logger.info(f"  Debugging status: {trainer.get_debugging_status()}")
        
    except ImportError as e:
        logger.warning(f"⚠️ Could not import training system: {e}")
        logger.info("  This is expected if the core modules are not available")
    except Exception as e:
        logger.error(f"❌ Error demonstrating integrated debugging: {e}")

def main():
    """Main demonstration function."""
    logger.info("🚀 Starting PyTorch Debugging Tools Demo")
    logger.info("=" * 60)
    
    # Check PyTorch version
    logger.info(f"📦 PyTorch version: {torch.__version__}")
    logger.info(f"🔧 CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"🎮 GPU: {torch.cuda.get_device_name()}")
    
    logger.info("=" * 60)
    
    try:
        # Demonstrate individual debugging tools
        demonstrate_autograd_anomaly_detection()
        demonstrate_gradient_debugging()
        demonstrate_memory_profiling()
        demonstrate_performance_profiling()
        
        # Demonstrate integrated system
        demonstrate_integrated_debugging()
        
    except Exception as e:
        logger.error(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ PyTorch Debugging Tools Demo completed!")
    logger.info("\n💡 Key takeaways:")
    logger.info("  - autograd.detect_anomaly() catches gradient computation issues")
    logger.info("  - Gradient debugging helps identify NaN/Inf values")
    logger.info("  - Memory profiling tracks GPU memory usage")
    logger.info("  - Performance profiling identifies bottlenecks")
    logger.info("  - All tools can be enabled/disabled dynamically")

if __name__ == "__main__":
    main()
