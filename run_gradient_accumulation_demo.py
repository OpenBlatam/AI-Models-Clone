#!/usr/bin/env python3
"""
Gradient Accumulation Demo

This script demonstrates the comprehensive gradient accumulation capabilities
for training with large effective batch sizes while maintaining memory efficiency.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import logging
import time
import matplotlib.pyplot as plt
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
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU()
            )
            
            self.decoder = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            )
            
            self.noise_predictor = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.BatchNorm1d(hidden_dim // 2),
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

def demonstrate_basic_gradient_accumulation():
    """Demonstrate basic gradient accumulation."""
    logger.info("🔄 Demonstrating Basic Gradient Accumulation")
    
    # Import the gradient accumulation system
    try:
        from core.gradient_accumulation_system import (
            GradientAccumulationConfig, 
            AccumulationMode, 
            create_gradient_accumulator
        )
    except ImportError:
        logger.warning("⚠️ Could not import gradient accumulation system, using mock implementation")
        return None
    
    # Create configuration
    config = GradientAccumulationConfig(
        enabled=True,
        mode=AccumulationMode.FIXED,
        accumulation_steps=4,
        effective_batch_size=128,
        gradient_clipping=True,
        clip_norm=1.0
    )
    
    # Create accumulator
    accumulator = create_gradient_accumulator(config)
    
    # Create model and optimizer
    model = create_mock_diffusion_model()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()
    
    # Create dataset
    dataset, dataloader = create_mock_dataset()
    
    # Setup accumulation
    model, dataloader = accumulator.setup_accumulation(model, dataloader)
    
    # Training loop with accumulation
    model.train()
    total_loss = 0
    accumulation_count = 0
    
    logger.info("  Starting training with gradient accumulation...")
    
    for batch_idx, (data, targets) in enumerate(dataloader):
        # Forward pass
        decoded, noise_pred = model(data)
        loss = criterion(decoded, targets) + 0.1 * criterion(noise_pred, targets)
        
        # Accumulate gradients
        optimizer_step_taken = accumulator.accumulate_gradients(
            loss, model, optimizer, batch_idx
        )
        
        total_loss += loss.item()
        
        if optimizer_step_taken:
            accumulation_count += 1
            logger.info(f"    Step {batch_idx}: Loss = {loss.item():.6f}, "
                       f"Accumulation {accumulation_count}")
        
        if batch_idx >= 20:  # Limit for demo
            break
    
    # Get accumulation info
    info = accumulator.get_accumulation_info()
    logger.info(f"  ✅ Basic gradient accumulation completed")
    logger.info(f"    Effective batch size: {info['effective_batch_size']}")
    logger.info(f"    Accumulation steps: {info['target_accumulation_steps']}")
    
    return accumulator, info

def demonstrate_adaptive_gradient_accumulation():
    """Demonstrate adaptive gradient accumulation."""
    logger.info("🎯 Demonstrating Adaptive Gradient Accumulation")
    
    try:
        from core.gradient_accumulation_system import (
            GradientAccumulationConfig, 
            AccumulationMode, 
            create_gradient_accumulator
        )
    except ImportError:
        logger.warning("⚠️ Could not import gradient accumulation system")
        return None
    
    # Create adaptive configuration
    config = GradientAccumulationConfig(
        enabled=True,
        mode=AccumulationMode.ADAPTIVE,
        accumulation_steps=4,
        effective_batch_size=128,
        min_accumulation_steps=2,
        max_accumulation_steps=16,
        memory_threshold=0.7,
        adaptive_memory_check=True
    )
    
    # Create adaptive accumulator
    accumulator = create_gradient_accumulator(config)
    
    # Create model and optimizer
    model = create_mock_diffusion_model()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()
    
    # Create dataset
    dataset, dataloader = create_mock_dataset()
    
    # Setup accumulation
    model, dataloader = accumulator.setup_accumulation(model, dataloader)
    
    # Training loop with adaptive accumulation
    model.train()
    total_loss = 0
    adaptation_history = []
    
    logger.info("  Starting adaptive training...")
    
    for batch_idx, (data, targets) in enumerate(dataloader):
        # Forward pass
        decoded, noise_pred = model(data)
        loss = criterion(decoded, targets) + 0.1 * criterion(noise_pred, targets)
        
        # Simulate performance metrics for adaptation
        if torch.cuda.is_available():
            memory_usage = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
        else:
            memory_usage = 0.5  # Mock value
        
        current_performance = {
            'memory_usage': memory_usage,
            'training_speed': 1.0 + np.random.normal(0, 0.1),
            'loss_stability': np.random.uniform(0.005, 0.05)
        }
        
        # Adapt accumulation steps
        if hasattr(accumulator, 'adapt_accumulation_steps'):
            optimal_steps = accumulator.adapt_accumulation_steps(model, current_performance)
            adaptation_history.append({
                'step': batch_idx,
                'optimal_steps': optimal_steps,
                'memory_usage': memory_usage
            })
        
        # Accumulate gradients
        optimizer_step_taken = accumulator.accumulate_gradients(
            loss, model, optimizer, batch_idx
        )
        
        total_loss += loss.item()
        
        if optimizer_step_taken:
            logger.info(f"    Step {batch_idx}: Loss = {loss.item():.6f}, "
                       f"Memory: {memory_usage:.2%}")
        
        if batch_idx >= 20:  # Limit for demo
            break
    
    # Get metrics summary
    metrics = accumulator.get_metrics_summary()
    logger.info(f"  ✅ Adaptive gradient accumulation completed")
    logger.info(f"    Final accumulation steps: {metrics['accumulation_config']['steps']}")
    
    return accumulator, metrics, adaptation_history

def demonstrate_memory_efficiency_comparison():
    """Compare memory efficiency with and without gradient accumulation."""
    logger.info("💾 Demonstrating Memory Efficiency Comparison")
    
    # Test without accumulation
    logger.info("  Testing without gradient accumulation...")
    model_no_acc = create_mock_diffusion_model()
    optimizer_no_acc = optim.Adam(model_no_acc.parameters(), lr=1e-4)
    criterion = nn.MSELoss()
    
    dataset, dataloader = create_mock_dataset()
    
    # Measure memory without accumulation
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        initial_memory = torch.cuda.memory_allocated() / (1024**2)  # MB
        
        model_no_acc.train()
        for batch_idx, (data, targets) in enumerate(dataloader):
            if batch_idx >= 5:  # Few steps
                break
            
            decoded, noise_pred = model_no_acc(data)
            loss = criterion(decoded, targets)
            loss.backward()
            optimizer_no_acc.step()
            optimizer_no_acc.zero_grad()
        
        final_memory = torch.cuda.memory_allocated() / (1024**2)  # MB
        memory_increase_no_acc = final_memory - initial_memory
        
        logger.info(f"    Memory increase without accumulation: {memory_increase_no_acc:.1f} MB")
    
    # Test with accumulation
    logger.info("  Testing with gradient accumulation...")
    try:
        from core.gradient_accumulation_system import (
            GradientAccumulationConfig, 
            AccumulationMode, 
            create_gradient_accumulator
        )
        
        config = GradientAccumulationConfig(
            enabled=True,
            mode=AccumulationMode.FIXED,
            accumulation_steps=4,
            effective_batch_size=128
        )
        
        accumulator = create_gradient_accumulator(config)
        model_acc = create_mock_diffusion_model()
        optimizer_acc = optim.Adam(model_acc.parameters(), lr=1e-4)
        
        # Setup accumulation
        model_acc, dataloader = accumulator.setup_accumulation(model_acc, dataloader)
        
        # Measure memory with accumulation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            initial_memory = torch.cuda.memory_allocated() / (1024**2)  # MB
            
            model_acc.train()
            for batch_idx, (data, targets) in enumerate(dataloader):
                if batch_idx >= 20:  # More steps due to accumulation
                    break
                
                decoded, noise_pred = model_acc(data)
                loss = criterion(decoded, targets)
                accumulator.accumulate_gradients(loss, model_acc, optimizer_acc, batch_idx)
            
            final_memory = torch.cuda.memory_allocated() / (1024**2)  # MB
            memory_increase_acc = final_memory - initial_memory
            
            logger.info(f"    Memory increase with accumulation: {memory_increase_acc:.1f} MB")
            
            # Calculate efficiency
            if memory_increase_no_acc > 0:
                efficiency = memory_increase_no_acc / memory_increase_acc
                logger.info(f"    Memory efficiency improvement: {efficiency:.2f}x")
        
        return True
        
    except ImportError:
        logger.warning("⚠️ Could not import gradient accumulation system for comparison")
        return False

def demonstrate_batch_size_scaling():
    """Demonstrate how gradient accumulation enables larger effective batch sizes."""
    logger.info("📦 Demonstrating Batch Size Scaling with Gradient Accumulation")
    
    try:
        from core.gradient_accumulation_system import (
            GradientAccumulationConfig, 
            AccumulationMode, 
            create_gradient_accumulator,
            calculate_optimal_accumulation_steps
        )
        
        # Test different target batch sizes
        target_batch_sizes = [64, 128, 256, 512]
        current_batch_size = 32
        
        logger.info(f"  Current batch size: {current_batch_size}")
        logger.info("  Calculating optimal accumulation steps for different target sizes...")
        
        for target_size in target_batch_sizes:
            # Calculate optimal steps
            optimal_steps = calculate_optimal_accumulation_steps(
                target_batch_size=target_size,
                current_batch_size=current_batch_size,
                available_memory=8.0,  # 8GB mock
                model_memory=2.0       # 2GB mock
            )
            
            effective_batch = current_batch_size * optimal_steps
            logger.info(f"    Target: {target_size}, Steps: {optimal_steps}, "
                       f"Effective: {effective_batch}")
        
        # Test with actual accumulation
        config = GradientAccumulationConfig(
            enabled=True,
            mode=AccumulationMode.FIXED,
            accumulation_steps=8,
            effective_batch_size=256
        )
        
        accumulator = create_gradient_accumulator(config)
        model = create_mock_diffusion_model()
        optimizer = optim.Adam(model.parameters(), lr=1e-4)
        criterion = nn.MSELoss()
        
        dataset, dataloader = create_mock_dataset()
        model, dataloader = accumulator.setup_accumulation(model, dataloader)
        
        # Training loop
        model.train()
        total_loss = 0
        
        logger.info("  Training with large effective batch size...")
        
        for batch_idx, (data, targets) in enumerate(dataloader):
            if batch_idx >= 16:  # Limit for demo
                break
            
            decoded, noise_pred = model(data)
            loss = criterion(decoded, targets) + 0.1 * criterion(noise_pred, targets)
            
            optimizer_step_taken = accumulator.accumulate_gradients(
                loss, model, optimizer, batch_idx
            )
            
            total_loss += loss.item()
            
            if optimizer_step_taken:
                logger.info(f"    Step {batch_idx}: Loss = {loss.item():.6f}")
        
        logger.info(f"  ✅ Large batch training completed")
        logger.info(f"    Total loss: {total_loss:.6f}")
        
        return True
        
    except ImportError:
        logger.warning("⚠️ Could not import gradient accumulation system for batch scaling")
        return False

def plot_accumulation_metrics(accumulator, adaptation_history=None):
    """Plot accumulation metrics and performance."""
    try:
        import matplotlib.pyplot as plt
        
        metrics = accumulator.get_metrics_summary()
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot 1: Gradient norms over time
        if metrics['metrics']['gradient_norms']:
            ax1.plot(metrics['metrics']['gradient_norms'])
            ax1.set_title('Gradient Norms Over Time')
            ax1.set_xlabel('Optimizer Steps')
            ax1.set_ylabel('Gradient Norm')
            ax1.grid(True)
        
        # Plot 2: Accumulation times
        if metrics['metrics']['accumulation_times']:
            ax2.plot(metrics['metrics']['accumulation_times'])
            ax2.set_title('Accumulation Time per Step')
            ax2.set_xlabel('Optimizer Steps')
            ax2.set_ylabel('Time (seconds)')
            ax2.grid(True)
        
        # Plot 3: Memory usage
        if metrics['metrics']['memory_usage_gb'] > 0:
            ax3.bar(['Memory Usage'], [metrics['metrics']['memory_usage_gb']])
            ax3.set_title('Memory Usage')
            ax3.set_ylabel('Memory (GB)')
            ax3.grid(True)
        
        # Plot 4: Adaptation history (if available)
        if adaptation_history:
            steps = [h['step'] for h in adaptation_history]
            optimal_steps = [h['optimal_steps'] for h in adaptation_history]
            memory_usage = [h['memory_usage'] for h in adaptation_history]
            
            ax4_twin = ax4.twinx()
            ax4.plot(steps, optimal_steps, 'b-', label='Optimal Steps')
            ax4_twin.plot(steps, memory_usage, 'r--', label='Memory Usage')
            
            ax4.set_title('Adaptive Accumulation')
            ax4.set_xlabel('Training Steps')
            ax4.set_ylabel('Accumulation Steps', color='b')
            ax4_twin.set_ylabel('Memory Usage', color='r')
            ax4.grid(True)
            
            # Add legends
            lines1, labels1 = ax4.get_legend_handles_labels()
            lines2, labels2 = ax4_twin.get_legend_handles_labels()
            ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        plt.tight_layout()
        
        # Save plot
        output_dir = Path("demo_gradient_accumulation_results")
        output_dir.mkdir(exist_ok=True)
        
        plot_path = output_dir / "accumulation_metrics.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"📊 Metrics plot saved to {plot_path}")
        
        plt.show()
        
    except ImportError:
        logger.warning("⚠️ Matplotlib not available for plotting")
    except Exception as e:
        logger.error(f"❌ Plotting failed: {e}")

def main():
    """Main demonstration function."""
    logger.info("🚀 Starting Gradient Accumulation Demonstration")
    logger.info("=" * 60)
    
    try:
        # Basic gradient accumulation
        logger.info("1️⃣ Basic Gradient Accumulation")
        basic_result = demonstrate_basic_gradient_accumulation()
        logger.info("-" * 40)
        
        # Adaptive gradient accumulation
        logger.info("2️⃣ Adaptive Gradient Accumulation")
        adaptive_result = demonstrate_adaptive_gradient_accumulation()
        logger.info("-" * 40)
        
        # Memory efficiency comparison
        logger.info("3️⃣ Memory Efficiency Comparison")
        memory_result = demonstrate_memory_efficiency_comparison()
        logger.info("-" * 40)
        
        # Batch size scaling
        logger.info("4️⃣ Batch Size Scaling")
        scaling_result = demonstrate_batch_size_scaling()
        logger.info("-" * 40)
        
        # Plot results if available
        if basic_result and basic_result[0]:
            logger.info("📊 Generating metrics plots...")
            plot_accumulation_metrics(basic_result[0])
        
        if adaptive_result and adaptive_result[0]:
            logger.info("📊 Generating adaptive metrics plots...")
            plot_accumulation_metrics(adaptive_result[0], adaptive_result[2])
        
        # Summary
        logger.info("📋 Demonstration Summary:")
        if basic_result:
            logger.info("  ✅ Basic gradient accumulation: Working")
        if adaptive_result:
            logger.info("  ✅ Adaptive gradient accumulation: Working")
        if memory_result:
            logger.info("  ✅ Memory efficiency comparison: Working")
        if scaling_result:
            logger.info("  ✅ Batch size scaling: Working")
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("=" * 60)
    logger.info("✅ Gradient Accumulation Demonstration Completed!")

if __name__ == "__main__":
    main()
