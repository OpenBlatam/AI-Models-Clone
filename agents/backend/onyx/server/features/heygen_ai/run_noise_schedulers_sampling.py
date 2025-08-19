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
import numpy as np
import matplotlib.pyplot as plt
import time
import logging
import os
from typing import Dict, List, Tuple
from noise_schedulers_sampling_implementation import (
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Noise Schedulers and Sampling Methods Runner
Comprehensive demonstration of various noise schedulers and sampling methods.
"""


# Import our noise schedulers and sampling implementation
    NoiseSchedulerManager, SamplingMethodManager, DiffusionSampler,
    LinearNoiseScheduler, CosineNoiseScheduler, SigmoidNoiseScheduler,
    QuadraticNoiseScheduler, ExponentialNoiseScheduler,
    DDPMSampling, DDIMSampling, PNDMSampling, EulerSampling,
    HeunSampling, DPMSolverSampling
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_noise_scheduler_comparison():
    """Compare different noise schedulers."""
    print("\n=== Noise Scheduler Comparison ===")
    
    # Create scheduler manager
    scheduler_manager = NoiseSchedulerManager()
    
    # Get all schedulers
    schedulers = scheduler_manager.get_all_schedulers(num_timesteps=1000)
    
    # Compare key properties
    print("\nNoise Schedule Properties:")
    print("Schedule Type | β_start | β_end | ᾱ_0 | ᾱ_T | Noise Range")
    print("-" * 65)
    
    for name, scheduler in schedulers.items():
        beta_start = scheduler.betas[0].item()
        beta_end = scheduler.betas[-1].item()
        alpha_cumprod_0 = scheduler.alphas_cumprod[0].item()
        alpha_cumprod_T = scheduler.alphas_cumprod[-1].item()
        noise_range = scheduler.sqrt_one_minus_alphas_cumprod[-1].item()
        
        print(f"{name:12s} | {beta_start:7.5f} | {beta_end:5.5f} | {alpha_cumprod_0:4.6f} | {alpha_cumprod_T:4.6f} | {noise_range:10.6f}")
    
    # Analyze convergence properties
    print("\nConvergence Analysis:")
    print("Schedule Type | Convergence Rate | Stability")
    print("-" * 40)
    
    for name, scheduler in schedulers.items():
        # Calculate convergence rate (how quickly noise increases)
        noise_curve = scheduler.sqrt_one_minus_alphas_cumprod.numpy()
        convergence_rate = np.mean(np.diff(noise_curve))
        
        # Calculate stability (variance of beta changes)
        beta_changes = np.diff(scheduler.betas.numpy())
        stability = 1.0 / (1.0 + np.std(beta_changes))
        
        print(f"{name:12s} | {convergence_rate:14.6f} | {stability:9.4f}")
    
    return schedulers

def run_sampling_method_comparison():
    """Compare different sampling methods."""
    print("\n=== Sampling Method Comparison ===")
    
    # Create a simple but realistic noise predictor
    class RealisticNoisePredictor(nn.Module):
        def __init__(self, in_channels: int = 3, time_dim: int = 128):
            
    """__init__ function."""
super().__init__()
            self.time_dim = time_dim
            
            # Time embedding
            self.time_mlp = nn.Sequential(
                nn.Linear(1, time_dim),
                nn.SiLU(),
                nn.Linear(time_dim, time_dim)
            )
            
            # Simple U-Net like structure
            self.conv1 = nn.Conv2d(in_channels + time_dim, 64, 3, padding=1)
            self.conv2 = nn.Conv2d(64, 64, 3, padding=1)
            self.conv3 = nn.Conv2d(64, in_channels, 3, padding=1)
            
        def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
            # Time embedding
            t = t.unsqueeze(-1).float()
            t = self.time_mlp(t)
            t = t.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, x.shape[2], x.shape[3])
            
            # Concatenate input and time embedding
            x = torch.cat([x, t], dim=1)
            
            # Forward pass
            x = torch.nn.functional.silu(self.conv1(x))
            x = torch.nn.functional.silu(self.conv2(x))
            x = self.conv3(x)
            
            return x
    
    # Use linear scheduler for comparison
    scheduler = LinearNoiseScheduler(num_timesteps=1000, beta_start=0.0001, beta_end=0.02)
    scheduler.setup()
    
    # Create sampling method manager
    sampling_manager = SamplingMethodManager()
    sampling_methods = sampling_manager.get_all_sampling_methods(scheduler)
    
    # Test parameters
    x_T = torch.randn(1, 3, 64, 64)  # Initial noise
    num_steps = 50
    
    print(f"\nSampling from noise with {num_steps} steps:")
    print("Method      | Time (s) | Memory (MB) | Quality | Consistency")
    print("-" * 60)
    
    results = {}
    
    for name, method in sampling_methods.items():
        # Create noise predictor
        noise_predictor = RealisticNoisePredictor()
        
        # Create sampler
        sampler = DiffusionSampler(scheduler, method)
        
        # Measure time and memory
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        start_time = time.time()
        start_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        
        images = sampler.sample(noise_predictor, x_T, num_steps=num_steps)
        
        end_time = time.time()
        end_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        
        sampling_time = end_time - start_time
        memory_used = (end_memory - start_memory) / 1024 / 1024  # Convert to MB
        
        # Calculate quality metrics
        final_image = images[-1]
        quality = 1.0 / (1.0 + final_image.std().item())  # Higher std = lower quality
        
        # Calculate consistency (how much the image changes in final steps)
        if len(images) >= 5:
            final_changes = torch.stack(images[-5:])
            consistency = 1.0 / (1.0 + torch.std(final_changes).item())
        else:
            consistency = 0.0
        
        print(f"{name:10s} | {sampling_time:8.3f} | {memory_used:10.1f} | {quality:7.4f} | {consistency:11.4f}")
        
        results[name] = {
            'time': sampling_time,
            'memory': memory_used,
            'quality': quality,
            'consistency': consistency,
            'images': images
        }
    
    return results

def run_scheduler_method_combinations():
    """Test different combinations of schedulers and sampling methods."""
    print("\n=== Scheduler-Method Combinations ===")
    
    # Create schedulers
    scheduler_manager = NoiseSchedulerManager()
    schedulers = scheduler_manager.get_all_schedulers(num_timesteps=1000)
    
    # Create sampling methods
    sampling_manager = SamplingMethodManager()
    
    # Simple noise predictor
    class SimpleNoisePredictor(nn.Module):
        def __init__(self) -> Any:
            super().__init__()
            self.conv = nn.Conv2d(3, 3, 3, padding=1)
            
        def forward(self, x, t) -> Any:
            return self.conv(x)
    
    noise_predictor = SimpleNoisePredictor()
    
    # Test combinations
    print("\nTesting Scheduler-Method Combinations:")
    print("Scheduler   | Method   | Quality | Time (s)")
    print("-" * 40)
    
    combinations_results = {}
    
    for scheduler_name, scheduler in schedulers.items():
        sampling_methods = sampling_manager.get_all_sampling_methods(scheduler)
        
        for method_name, method in sampling_methods.items():
            sampler = DiffusionSampler(scheduler, method)
            
            x_T = torch.randn(1, 3, 32, 32)
            
            start_time = time.time()
            images = sampler.sample(noise_predictor, x_T, num_steps=20)
            end_time = time.time()
            
            final_image = images[-1]
            quality = 1.0 / (1.0 + final_image.std().item())
            sampling_time = end_time - start_time
            
            print(f"{scheduler_name:10s} | {method_name:8s} | {quality:7.4f} | {sampling_time:8.3f}")
            
            combinations_results[f"{scheduler_name}_{method_name}"] = {
                'scheduler': scheduler_name,
                'method': method_name,
                'quality': quality,
                'time': sampling_time,
                'images': images
            }
    
    return combinations_results

def run_adaptive_sampling_demo():
    """Demonstrate adaptive sampling with different step counts."""
    print("\n=== Adaptive Sampling Demonstration ===")
    
    # Create scheduler and method
    scheduler = LinearNoiseScheduler(num_timesteps=1000)
    scheduler.setup()
    
    sampling_manager = SamplingMethodManager()
    ddpm_method = sampling_manager.create_sampling_method(
        SamplingMethod.DDPM, scheduler
    )
    
    # Simple noise predictor
    class AdaptiveNoisePredictor(nn.Module):
        def __init__(self) -> Any:
            super().__init__()
            self.conv = nn.Conv2d(3, 3, 3, padding=1)
            
        def forward(self, x, t) -> Any:
            return self.conv(x)
    
    noise_predictor = AdaptiveNoisePredictor()
    
    # Test different step counts
    step_counts = [10, 20, 50, 100, 200]
    x_T = torch.randn(1, 3, 64, 64)
    
    print("\nAdaptive Sampling Results:")
    print("Steps | Time (s) | Quality | Efficiency")
    print("-" * 35)
    
    adaptive_results = {}
    
    for steps in step_counts:
        sampler = DiffusionSampler(scheduler, ddpm_method)
        
        start_time = time.time()
        images = sampler.sample(noise_predictor, x_T, num_steps=steps)
        end_time = time.time()
        
        sampling_time = end_time - start_time
        final_image = images[-1]
        quality = 1.0 / (1.0 + final_image.std().item())
        efficiency = quality / sampling_time  # Quality per second
        
        print(f"{steps:5d} | {sampling_time:8.3f} | {quality:7.4f} | {efficiency:10.4f}")
        
        adaptive_results[steps] = {
            'time': sampling_time,
            'quality': quality,
            'efficiency': efficiency,
            'images': images
        }
    
    return adaptive_results

def run_noise_schedule_analysis():
    """Detailed analysis of noise schedules."""
    print("\n=== Noise Schedule Analysis ===")
    
    # Create schedulers
    scheduler_manager = NoiseSchedulerManager()
    schedulers = scheduler_manager.get_all_schedulers(num_timesteps=1000)
    
    # Analyze each schedule
    analysis_results = {}
    
    for name, scheduler in schedulers.items():
        print(f"\n{name.upper()} Schedule Analysis:")
        
        # Basic properties
        betas = scheduler.betas.numpy()
        alphas_cumprod = scheduler.alphas_cumprod.numpy()
        noise_levels = scheduler.sqrt_one_minus_alphas_cumprod.numpy()
        
        # Calculate metrics
        beta_mean = np.mean(betas)
        beta_std = np.std(betas)
        noise_growth_rate = np.mean(np.diff(noise_levels))
        convergence_point = np.argmax(noise_levels > 0.5 * noise_levels[-1])
        
        print(f"  β mean: {beta_mean:.6f}")
        print(f"  β std: {beta_std:.6f}")
        print(f"  Noise growth rate: {noise_growth_rate:.6f}")
        print(f"  Convergence point: {convergence_point}/{len(noise_levels)}")
        
        analysis_results[name] = {
            'beta_mean': beta_mean,
            'beta_std': beta_std,
            'noise_growth_rate': noise_growth_rate,
            'convergence_point': convergence_point,
            'betas': betas,
            'alphas_cumprod': alphas_cumprod,
            'noise_levels': noise_levels
        }
    
    return analysis_results

def create_comprehensive_visualizations(schedulers, sampling_results, combinations_results, adaptive_results, analysis_results) -> Any:
    """Create comprehensive visualizations."""
    print("\n=== Creating Visualizations ===")
    
    # 1. Noise Schedule Comparison
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    for i, (name, scheduler) in enumerate(schedulers.items()):
        row = i // 3
        col = i % 3
        
        axes[row, col].plot(scheduler.betas.numpy(), label='β_t', linewidth=2)
        axes[row, col].plot(scheduler.alphas_cumprod.numpy(), label='ᾱ_t', linewidth=2)
        axes[row, col].set_title(f'{name.capitalize()} Schedule', fontsize=14, fontweight='bold')
        axes[row, col].set_xlabel('Timestep t')
        axes[row, col].set_ylabel('Value')
        axes[row, col].legend()
        axes[row, col].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('noise_schedules_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Noise schedules comparison saved")
    
    # 2. Sampling Methods Performance
    if sampling_results:
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        methods = list(sampling_results.keys())
        times = [sampling_results[m]['time'] for m in methods]
        qualities = [sampling_results[m]['quality'] for m in methods]
        memories = [sampling_results[m]['memory'] for m in methods]
        consistencies = [sampling_results[m]['consistency'] for m in methods]
        
        # Time vs Quality
        axes[0, 0].scatter(times, qualities, s=100, alpha=0.7)
        for i, method in enumerate(methods):
            axes[0, 0].annotate(method, (times[i], qualities[i]), xytext=(5, 5), textcoords='offset points')
        axes[0, 0].set_xlabel('Sampling Time (s)')
        axes[0, 0].set_ylabel('Quality')
        axes[0, 0].set_title('Time vs Quality')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Memory vs Quality
        axes[0, 1].scatter(memories, qualities, s=100, alpha=0.7)
        for i, method in enumerate(methods):
            axes[0, 1].annotate(method, (memories[i], qualities[i]), xytext=(5, 5), textcoords='offset points')
        axes[0, 1].set_xlabel('Memory Usage (MB)')
        axes[0, 1].set_ylabel('Quality')
        axes[0, 1].set_title('Memory vs Quality')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Consistency vs Quality
        axes[1, 0].scatter(consistencies, qualities, s=100, alpha=0.7)
        for i, method in enumerate(methods):
            axes[1, 0].annotate(method, (consistencies[i], qualities[i]), xytext=(5, 5), textcoords='offset points')
        axes[1, 0].set_xlabel('Consistency')
        axes[1, 0].set_ylabel('Quality')
        axes[1, 0].set_title('Consistency vs Quality')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Bar chart of qualities
        axes[1, 1].bar(methods, qualities, alpha=0.7)
        axes[1, 1].set_xlabel('Sampling Method')
        axes[1, 1].set_ylabel('Quality')
        axes[1, 1].set_title('Quality Comparison')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('sampling_methods_performance.png', dpi=300, bbox_inches='tight')
        print("✓ Sampling methods performance saved")
    
    # 3. Adaptive Sampling Results
    if adaptive_results:
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        steps = list(adaptive_results.keys())
        times = [adaptive_results[s]['time'] for s in steps]
        qualities = [adaptive_results[s]['quality'] for s in steps]
        efficiencies = [adaptive_results[s]['efficiency'] for s in steps]
        
        # Time vs Steps
        axes[0].plot(steps, times, 'o-', linewidth=2, markersize=8)
        axes[0].set_xlabel('Number of Steps')
        axes[0].set_ylabel('Time (s)')
        axes[0].set_title('Sampling Time vs Steps')
        axes[0].grid(True, alpha=0.3)
        
        # Quality vs Steps
        axes[1].plot(steps, qualities, 'o-', linewidth=2, markersize=8)
        axes[1].set_xlabel('Number of Steps')
        axes[1].set_ylabel('Quality')
        axes[1].set_title('Quality vs Steps')
        axes[1].grid(True, alpha=0.3)
        
        # Efficiency vs Steps
        axes[2].plot(steps, efficiencies, 'o-', linewidth=2, markersize=8)
        axes[2].set_xlabel('Number of Steps')
        axes[2].set_ylabel('Efficiency (Quality/Time)')
        axes[2].set_title('Efficiency vs Steps')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('adaptive_sampling_results.png', dpi=300, bbox_inches='tight')
        print("✓ Adaptive sampling results saved")

def main():
    """Main function to run all noise schedulers and sampling demonstrations."""
    print("🚀 Starting Noise Schedulers and Sampling Methods Demonstration")
    print("=" * 70)
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
        print(f"✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("⚠ CUDA not available, using CPU")
    
    try:
        # Run all demonstrations
        schedulers = run_noise_scheduler_comparison()
        sampling_results = run_sampling_method_comparison()
        combinations_results = run_scheduler_method_combinations()
        adaptive_results = run_adaptive_sampling_demo()
        analysis_results = run_noise_schedule_analysis()
        
        # Create visualizations
        create_comprehensive_visualizations(
            schedulers, sampling_results, combinations_results, 
            adaptive_results, analysis_results
        )
        
        print("\n" + "=" * 70)
        print("✅ All noise schedulers and sampling methods demonstrations completed!")
        print("\nGenerated files:")
        print("  - noise_schedules_comparison.png")
        print("  - sampling_methods_performance.png")
        print("  - adaptive_sampling_results.png")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        logger.exception("Detailed error information:")

match __name__:
    case "__main__":
    main() 