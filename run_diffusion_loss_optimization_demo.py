#!/usr/bin/env python3
"""
Diffusion Loss Functions and Optimization Demo

This script demonstrates the comprehensive system for implementing appropriate
loss functions and optimization algorithms for diffusion models.
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
import torch.nn.functional as F

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our diffusion loss and optimization system
from core.diffusion_loss_optimization_system import (
    DiffusionLossFunctions, DiffusionOptimizers, DiffusionSchedulers, DiffusionTrainingManager,
    LossConfig, OptimizerConfig, SchedulerConfig,
    LossType, OptimizerType, SchedulerType,
    create_diffusion_training_config, create_advanced_training_config
)

class MockDiffusionModel(nn.Module):
    """Mock diffusion model for demonstration purposes."""
    
    def __init__(self, input_dim: int = 64, hidden_dim: int = 128, output_dim: int = 64):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Time embedding
        self.time_embedding = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Main network
        self.network = nn.Sequential(
            nn.Linear(input_dim + hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
    
    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        # Time embedding
        t_emb = self.time_embedding(t.unsqueeze(-1).float())
        
        # Concatenate input and time embedding
        x_combined = torch.cat([x, t_emb], dim=-1)
        
        # Forward through network
        return self.network(x_combined)

def create_sample_batch(batch_size: int = 32, input_dim: int = 64, device: str = "cpu") -> Tuple[torch.Tensor, ...]:
    """Create sample batch for training."""
    x_t = torch.randn(batch_size, input_dim, device=device)
    noise = torch.randn(batch_size, input_dim, device=device)
    t = torch.randint(0, 1000, (batch_size,), device=device)
    
    return x_t, noise, t

def demo_loss_functions():
    """Demonstrate different loss functions."""
    logger.info("🎯 Demo 1: Loss Functions")
    
    # Create sample data
    batch_size = 32
    input_dim = 64
    
    prediction = torch.randn(batch_size, input_dim)
    target = torch.randn(batch_size, input_dim)
    
    # Test different loss types
    loss_types = [
        LossType.MSE,
        LossType.MAE,
        LossType.HUBER,
        LossType.SMOOTH_L1,
        LossType.KL_DIVERGENCE
    ]
    
    loss_results = {}
    
    for loss_type in loss_types:
        try:
            config = LossConfig(loss_type=loss_type)
            loss_fn = DiffusionLossFunctions(config)
            
            loss_value = loss_fn.compute_loss(prediction, target)
            loss_results[loss_type.value] = loss_value.item()
            
            logger.info(f"  {loss_type.value.upper()}: {loss_value.item():.6f}")
            
        except Exception as e:
            logger.error(f"  ❌ {loss_type.value.upper()}: {e}")
            loss_results[loss_type.value] = None
    
    # Test combined loss
    try:
        combined_config = LossConfig(
            loss_type=LossType.COMBINED,
            combined_weights={"mse": 1.0, "perceptual": 0.1}
        )
        combined_loss_fn = DiffusionLossFunctions(combined_config)
        combined_loss = combined_loss_fn.compute_loss(prediction, target)
        loss_results["combined"] = combined_loss.item()
        logger.info(f"  COMBINED: {combined_loss.item():.6f}")
        
    except Exception as e:
        logger.error(f"  ❌ COMBINED: {e}")
        loss_results["combined"] = None
    
    return loss_results

def demo_optimizers():
    """Demonstrate different optimizers."""
    logger.info("\n⚡ Demo 2: Optimizers")
    
    # Create a simple model
    model = MockDiffusionModel()
    
    # Test different optimizer types
    optimizer_types = [
        OptimizerType.ADAM,
        OptimizerType.ADAMW,
        OptimizerType.SGD,
        OptimizerType.RMSprop,
        OptimizerType.ADAGRAD,
        OptimizerType.ADADELTA
    ]
    
    optimizer_results = {}
    
    for opt_type in optimizer_types:
        try:
            config = OptimizerConfig(
                optimizer_type=opt_type,
                learning_rate=1e-4,
                weight_decay=1e-2
            )
            
            optimizer = DiffusionOptimizers(config)
            opt_instance = optimizer.create_optimizer(model)
            
            # Test optimizer step
            x_t, noise, t = create_sample_batch()
            predicted_noise = model(x_t, t)
            loss = F.mse_loss(predicted_noise, noise)
            
            loss.backward()
            opt_instance.step()
            
            optimizer_results[opt_type.value] = "✅ Success"
            logger.info(f"  {opt_type.value.upper()}: ✅ Success")
            
        except Exception as e:
            logger.error(f"  ❌ {opt_type.value.upper()}: {e}")
            optimizer_results[opt_type.value] = f"❌ {e}"
    
    return optimizer_results

def demo_schedulers():
    """Demonstrate different learning rate schedulers."""
    logger.info("\n📈 Demo 3: Learning Rate Schedulers")
    
    # Create a simple model and optimizer
    model = MockDiffusionModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    # Test different scheduler types
    scheduler_types = [
        SchedulerType.STEP,
        SchedulerType.MULTI_STEP,
        SchedulerType.EXPONENTIAL,
        SchedulerType.COSINE,
        SchedulerType.COSINE_WARM_RESTART,
        SchedulerType.LINEAR,
        SchedulerType.POLYNOMIAL
    ]
    
    scheduler_results = {}
    
    for sched_type in scheduler_types:
        try:
            config = SchedulerConfig(
                scheduler_type=sched_type,
                warmup_steps=100,
                warmup_start_lr=1e-6
            )
            
            scheduler = DiffusionSchedulers(config)
            sched_instance = scheduler.create_scheduler(optimizer, total_steps=1000)
            
            # Test scheduler step
            initial_lr = optimizer.param_groups[0]['lr']
            sched_instance.step()
            new_lr = optimizer.param_groups[0]['lr']
            
            scheduler_results[sched_type.value] = {
                "initial_lr": initial_lr,
                "new_lr": new_lr,
                "status": "✅ Success"
            }
            
            logger.info(f"  {sched_type.value.upper()}: ✅ Success (LR: {initial_lr:.6f} → {new_lr:.6f})")
            
        except Exception as e:
            logger.error(f"  ❌ {sched_type.value.upper()}: {e}")
            scheduler_results[sched_type.value] = {"status": f"❌ {e}"}
    
    return scheduler_results

def demo_training_manager():
    """Demonstrate the complete training manager."""
    logger.info("\n🚀 Demo 4: Training Manager")
    
    # Create model
    model = MockDiffusionModel()
    
    # Create training configurations
    configs = [
        ("Basic MSE + AdamW + Cosine", create_diffusion_training_config()),
        ("Advanced Combined + AdamW + OneCycle", create_advanced_training_config(
            use_perceptual_loss=True, use_style_loss=True
        ))
    ]
    
    training_results = {}
    
    for config_name, (loss_config, optimizer_config, scheduler_config) in configs:
        try:
            logger.info(f"\n  Testing: {config_name}")
            
            # Create training manager
            training_manager = DiffusionTrainingManager(
                loss_config, optimizer_config, scheduler_config
            )
            
            # Setup training
            training_manager.setup_training(
                model, 
                total_steps=100, 
                epochs=10, 
                steps_per_epoch=10
            )
            
            # Run a few training steps
            step_metrics = []
            for step in range(10):
                batch = create_sample_batch()
                metrics = training_manager.training_step(model, batch, step)
                step_metrics.append(metrics)
                
                if step % 5 == 0:
                    logger.info(f"    Step {step}: Loss = {metrics['loss']:.6f}, LR = {metrics['learning_rate']:.6f}")
            
            # Get training summary
            summary = training_manager.get_training_summary()
            
            training_results[config_name] = {
                "status": "✅ Success",
                "final_loss": summary.get("final_loss", 0),
                "avg_loss": summary.get("avg_loss", 0),
                "total_steps": summary.get("total_steps", 0)
            }
            
            logger.info(f"    ✅ Training completed successfully")
            logger.info(f"    Final Loss: {summary.get('final_loss', 0):.6f}")
            logger.info(f"    Average Loss: {summary.get('avg_loss', 0):.6f}")
            
        except Exception as e:
            logger.error(f"    ❌ Failed: {e}")
            training_results[config_name] = {"status": f"❌ {e}"}
    
    return training_results

def demo_performance_comparison():
    """Demonstrate performance comparison between different configurations."""
    logger.info("\n⚖️ Demo 5: Performance Comparison")
    
    # Create model
    model = MockDiffusionModel()
    
    # Test configurations
    test_configs = [
        ("MSE + AdamW + Cosine", LossType.MSE, OptimizerType.ADAMW, SchedulerType.COSINE),
        ("MSE + SGD + Step", LossType.MSE, OptimizerType.SGD, SchedulerType.STEP),
        ("Huber + Adam + Exponential", LossType.HUBER, OptimizerType.ADAM, SchedulerType.EXPONENTIAL),
        ("Smooth L1 + RMSprop + MultiStep", LossType.SMOOTH_L1, OptimizerType.RMSprop, SchedulerType.MULTI_STEP)
    ]
    
    performance_results = {}
    
    for config_name, loss_type, opt_type, sched_type in test_configs:
        try:
            logger.info(f"\n  Testing: {config_name}")
            
            # Create configurations
            loss_config = LossConfig(loss_type=loss_type)
            optimizer_config = OptimizerConfig(
                optimizer_type=opt_type,
                learning_rate=1e-4,
                weight_decay=1e-2
            )
            scheduler_config = SchedulerConfig(
                scheduler_type=sched_type,
                warmup_steps=50
            )
            
            # Create training manager
            training_manager = DiffusionTrainingManager(
                loss_config, optimizer_config, scheduler_config
            )
            
            # Setup training
            training_manager.setup_training(model, total_steps=50, epochs=5, steps_per_epoch=10)
            
            # Measure training time
            start_time = time.time()
            
            # Run training steps
            total_loss = 0
            for step in range(50):
                batch = create_sample_batch()
                metrics = training_manager.training_step(model, batch, step)
                total_loss += metrics['loss']
            
            end_time = time.time()
            training_time = end_time - start_time
            
            # Calculate metrics
            avg_loss = total_loss / 50
            steps_per_second = 50 / training_time
            
            performance_results[config_name] = {
                "status": "✅ Success",
                "training_time": training_time,
                "avg_loss": avg_loss,
                "steps_per_second": steps_per_second
            }
            
            logger.info(f"    ✅ Training completed")
            logger.info(f"    Training Time: {training_time:.2f}s")
            logger.info(f"    Average Loss: {avg_loss:.6f}")
            logger.info(f"    Steps/Second: {steps_per_second:.2f}")
            
        except Exception as e:
            logger.error(f"    ❌ Failed: {e}")
            performance_results[config_name] = {"status": f"❌ {e}"}
    
    return performance_results

def create_visualization(results: Dict[str, Any], title: str, save_path: str):
    """Create visualization of results."""
    try:
        # Filter successful results
        successful_results = {k: v for k, v in results.items() if isinstance(v, dict) and v.get("status") == "✅ Success"}
        
        if not successful_results:
            logger.warning(f"No successful results to visualize for {title}")
            return
        
        # Create figure
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Plot 1: Training time comparison
        if any("training_time" in v for v in successful_results.values()):
            names = list(successful_results.keys())
            times = [v.get("training_time", 0) for v in successful_results.values()]
            
            axes[0].bar(names, times, color='skyblue', alpha=0.7)
            axes[0].set_title("Training Time Comparison")
            axes[0].set_ylabel("Time (seconds)")
            axes[0].tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for i, v in enumerate(times):
                axes[0].text(i, v + max(times) * 0.01, f'{v:.2f}s', ha='center', va='bottom')
        
        # Plot 2: Loss comparison
        if any("avg_loss" in v for v in successful_results.values()):
            names = list(successful_results.keys())
            losses = [v.get("avg_loss", 0) for v in successful_results.values()]
            
            axes[1].bar(names, losses, color='lightcoral', alpha=0.7)
            axes[1].set_title("Average Loss Comparison")
            axes[1].set_ylabel("Loss")
            axes[1].tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for i, v in enumerate(losses):
                axes[1].text(i, v + max(losses) * 0.01, f'{v:.6f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"📊 Visualization saved to {save_path}")
        
    except Exception as e:
        logger.error(f"❌ Failed to create visualization: {e}")

def main():
    """Main demonstration function."""
    logger.info("🚀 Starting Diffusion Loss Functions and Optimization Demo")
    logger.info("=" * 80)
    
    # Create output directory
    output_dir = Path("diffusion_loss_optimization_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Demo 1: Loss Functions
    loss_results = demo_loss_functions()
    
    # Demo 2: Optimizers
    optimizer_results = demo_optimizers()
    
    # Demo 3: Schedulers
    scheduler_results = demo_schedulers()
    
    # Demo 4: Training Manager
    training_results = demo_training_manager()
    
    # Demo 5: Performance Comparison
    performance_results = demo_performance_comparison()
    
    # Create visualizations
    logger.info("\n📊 Creating Visualizations...")
    
    create_visualization(
        performance_results, 
        "Performance Comparison", 
        output_dir / "performance_comparison.png"
    )
    
    # Create summary report
    logger.info("\n📋 Creating Summary Report...")
    
    summary_report = f"""
# Diffusion Loss Functions and Optimization Demo Results

## Demo Summary

### 1. Loss Functions Tested
{chr(10).join([f"- {loss_type}: {'✅ Success' if result is not None else '❌ Failed'}" for loss_type, result in loss_results.items()])}

### 2. Optimizers Tested
{chr(10).join([f"- {opt_type}: {result}" for opt_type, result in optimizer_results.items()])}

### 3. Schedulers Tested
{chr(10).join([f"- {sched_type}: {result.get('status', 'Unknown')}" for sched_type, result in scheduler_results.items()])}

### 4. Training Configurations Tested
{chr(10).join([f"- {config_name}: {result.get('status', 'Unknown')}" for config_name, result in training_results.items()])}

### 5. Performance Comparison
{chr(10).join([f"- {config_name}: {result.get('status', 'Unknown')}" for config_name, result in performance_results.items()])}

## Key Features Demonstrated

✅ **Loss Functions**: MSE, MAE, Huber, Smooth L1, KL Divergence, Combined Losses
✅ **Optimizers**: Adam, AdamW, SGD, RMSprop, AdaGrad, AdaDelta
✅ **Schedulers**: Step, Multi-step, Exponential, Cosine, One Cycle, Linear, Polynomial
✅ **Training Manager**: Complete training pipeline with loss computation, optimization, and scheduling
✅ **Performance Analysis**: Training time and loss comparison between different configurations

## Usage Examples

The system provides:
- Flexible loss function configuration
- Multiple optimizer choices with automatic parameter setup
- Comprehensive learning rate scheduling with warmup support
- Complete training management with checkpointing
- Performance monitoring and comparison tools

## Output Files

- Performance comparison visualization: `performance_comparison.png`
- This summary report: `summary_report.md`

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Save summary report
    summary_path = output_dir / "summary_report.md"
    with open(summary_path, 'w') as f:
        f.write(summary_report)
    
    logger.info(f"📄 Summary report saved to {summary_path}")
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("🎉 Diffusion Loss Functions and Optimization Demo Completed!")
    logger.info(f"📁 All outputs saved to: {output_dir}")
    
    # Print key statistics
    successful_configs = sum(1 for result in performance_results.values() 
                           if isinstance(result, dict) and result.get("status") == "✅ Success")
    total_configs = len(performance_results)
    
    logger.info(f"📊 Success Rate: {successful_configs}/{total_configs} configurations tested successfully")
    
    if successful_configs > 0:
        best_config = min(
            [(name, result) for name, result in performance_results.items() 
             if isinstance(result, dict) and result.get("status") == "✅ Success"],
            key=lambda x: x[1].get("avg_loss", float('inf'))
        )
        logger.info(f"🏆 Best Performing Configuration: {best_config[0]} (Loss: {best_config[1].get('avg_loss', 0):.6f})")

if __name__ == "__main__":
    main()
