from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import logging
import os
from typing import List, Tuple
from diffusion_processes_implementation import (
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Diffusion Processes Runner
Comprehensive demonstration of forward and reverse diffusion processes.
"""


# Import our diffusion processes implementation
    DiffusionProcesses, SimpleNoisePredictor, DiffusionProcessTrainer
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_forward_diffusion_demo():
    """Demonstrate forward diffusion process step by step."""
    print("\n=== Forward Diffusion Process Demo ===")
    
    # Initialize diffusion processes
    diffusion = DiffusionProcesses(num_timesteps=1000, beta_start=0.0001, beta_end=0.02)
    
    # Create a simple test image (in real usage, this would be an actual image)
    test_image = torch.randn(1, 3, 64, 64)
    print(f"Original image shape: {test_image.shape}")
    print(f"Original image stats - Mean: {test_image.mean():.4f}, Std: {test_image.std():.4f}")
    
    # Demonstrate forward diffusion with different timesteps
    timesteps_to_show = [0, 100, 250, 500, 750, 999]
    
    print("\nForward diffusion progression:")
    print("Timestep | Noise Level | Image Mean | Image Std")
    print("-" * 50)
    
    for t in timesteps_to_show:
        t_batch = torch.full((test_image.shape[0],), t, dtype=torch.long)
        x_t, noise = diffusion.forward_diffusion_step(test_image, t_batch)
        
        noise_level = diffusion.sqrt_one_minus_alphas_cumprod[t].item()
        print(f"{t:8d} | {noise_level:10.4f} | {x_t.mean():10.4f} | {x_t.std():8.4f}")
    
    # Visualize forward diffusion
    print("\nGenerating forward diffusion visualization...")
    forward_images = diffusion.forward_diffusion_visualization(test_image, num_steps=10)
    
    # Save visualization
    save_diffusion_visualization(forward_images, "forward_diffusion.png", "Forward Diffusion Process")
    print("✓ Forward diffusion visualization saved to 'forward_diffusion.png'")
    
    return forward_images

def run_reverse_diffusion_demo():
    """Demonstrate reverse diffusion process step by step."""
    print("\n=== Reverse Diffusion Process Demo ===")
    
    # Initialize diffusion processes
    diffusion = DiffusionProcesses(num_timesteps=1000, beta_start=0.0001, beta_end=0.02)
    
    # Create a simple noise predictor and train it
    print("Training noise predictor...")
    noise_predictor = SimpleNoisePredictor(in_channels=3, time_dim=256)
    trainer = DiffusionProcessTrainer(diffusion, noise_predictor)
    
    # Create training data
    training_image = torch.randn(1, 3, 64, 64)
    
    # Train for a few steps
    print("Training progress:")
    for step in range(20):
        loss_info = trainer.train_step(training_image)
        if (step + 1) % 5 == 0:
            print(f"  Step {step+1}/20, Loss: {loss_info['loss']:.4f}")
    
    # Start with pure noise
    print("\nStarting reverse diffusion from pure noise...")
    pure_noise = torch.randn(1, 3, 64, 64)
    print(f"Pure noise stats - Mean: {pure_noise.mean():.4f}, Std: {pure_noise.std():.4f}")
    
    # Perform reverse diffusion
    def noise_predictor_fn(x_t, t) -> Any:
        with torch.no_grad():
            return noise_predictor(x_t, t)
    
    reverse_images = diffusion.reverse_diffusion_visualization(
        pure_noise, noise_predictor_fn, num_steps=10
    )
    
    # Save visualization
    save_diffusion_visualization(reverse_images, "reverse_diffusion.png", "Reverse Diffusion Process")
    print("✓ Reverse diffusion visualization saved to 'reverse_diffusion.png'")
    
    return reverse_images

def run_full_diffusion_cycle():
    """Run a complete forward and reverse diffusion cycle."""
    print("\n=== Full Diffusion Cycle Demo ===")
    
    # Initialize diffusion processes
    diffusion = DiffusionProcesses(num_timesteps=1000, beta_start=0.0001, beta_end=0.02)
    
    # Create original image
    original_image = torch.randn(1, 3, 64, 64)
    print(f"Original image - Mean: {original_image.mean():.4f}, Std: {original_image.std():.4f}")
    
    # Forward diffusion: add noise
    print("\n1. Forward Diffusion (Adding Noise)")
    t_batch = torch.full((original_image.shape[0],), 999, dtype=torch.long)
    noisy_image, added_noise = diffusion.forward_diffusion_step(original_image, t_batch)
    print(f"Noisy image - Mean: {noisy_image.mean():.4f}, Std: {noisy_image.std():.4f}")
    
    # Train noise predictor
    print("\n2. Training Noise Predictor")
    noise_predictor = SimpleNoisePredictor(in_channels=3, time_dim=256)
    trainer = DiffusionProcessTrainer(diffusion, noise_predictor)
    
    for step in range(15):
        loss_info = trainer.train_step(original_image)
        if (step + 1) % 5 == 0:
            print(f"  Step {step+1}/15, Loss: {loss_info['loss']:.4f}")
    
    # Reverse diffusion: remove noise
    print("\n3. Reverse Diffusion (Removing Noise)")
    def noise_predictor_fn(x_t, t) -> Any:
        with torch.no_grad():
            return noise_predictor(x_t, t)
    
    # Perform reverse diffusion
    denoised_image = noisy_image.clone()
    for t in range(999, 0, -100):  # Reverse from t=999 to t=0
        t_batch = torch.full((denoised_image.shape[0],), t, dtype=torch.long)
        predicted_noise = noise_predictor_fn(denoised_image, t_batch)
        denoised_image = diffusion.reverse_diffusion_step(denoised_image, t_batch, predicted_noise)
        
        if t % 300 == 0:
            print(f"  Timestep {t}: Mean={denoised_image.mean():.4f}, Std={denoised_image.std():.4f}")
    
    print(f"Final denoised image - Mean: {denoised_image.mean():.4f}, Std: {denoised_image.std():.4f}")
    
    # Compare original and denoised
    mse_loss = torch.nn.functional.mse_loss(original_image, denoised_image)
    print(f"\nReconstruction MSE: {mse_loss:.6f}")
    
    return original_image, noisy_image, denoised_image

def run_noise_schedule_analysis():
    """Analyze and visualize the noise schedule."""
    print("\n=== Noise Schedule Analysis ===")
    
    # Initialize diffusion processes
    diffusion = DiffusionProcesses(num_timesteps=1000, beta_start=0.0001, beta_end=0.02)
    
    # Get schedule information
    schedule_info = diffusion.get_noise_schedule_info()
    
    # Analyze key timesteps
    key_timesteps = [0, 100, 250, 500, 750, 999]
    
    print("\nNoise Schedule Analysis:")
    print("Timestep | β_t      | α_t      | ᾱ_t      | √ᾱ_t     | √(1-ᾱ_t)")
    print("-" * 70)
    
    for t in key_timesteps:
        beta_t = diffusion.betas[t].item()
        alpha_t = diffusion.alphas[t].item()
        alpha_cumprod_t = diffusion.alphas_cumprod[t].item()
        sqrt_alpha_cumprod_t = diffusion.sqrt_alphas_cumprod[t].item()
        sqrt_one_minus_alpha_cumprod_t = diffusion.sqrt_one_minus_alphas_cumprod[t].item()
        
        print(f"{t:8d} | {beta_t:8.6f} | {alpha_t:8.6f} | {alpha_cumprod_t:8.6f} | {sqrt_alpha_cumprod_t:8.6f} | {sqrt_one_minus_alpha_cumprod_t:8.6f}")
    
    # Create detailed visualization
    create_detailed_schedule_visualization(schedule_info)
    print("\n✓ Detailed noise schedule visualization saved to 'detailed_diffusion_schedule.png'")

def run_mathematical_verification():
    """Verify the mathematical properties of diffusion processes."""
    print("\n=== Mathematical Verification ===")
    
    # Initialize diffusion processes
    diffusion = DiffusionProcesses(num_timesteps=1000, beta_start=0.0001, beta_end=0.02)
    
    # Test image
    test_image = torch.randn(1, 3, 32, 32)
    
    print("1. Testing Forward Process Properties:")
    
    # Test at different timesteps
    for t in [100, 500, 999]:
        t_batch = torch.full((test_image.shape[0],), t, dtype=torch.long)
        x_t, noise = diffusion.forward_diffusion_step(test_image, t_batch)
        
        # Verify the forward equation: x_t = √(ᾱ_t) * x_0 + √(1 - ᾱ_t) * ε
        sqrt_alpha_cumprod_t = diffusion.sqrt_alphas_cumprod[t]
        sqrt_one_minus_alpha_cumprod_t = diffusion.sqrt_one_minus_alphas_cumprod[t]
        
        expected_x_t = sqrt_alpha_cumprod_t * test_image + sqrt_one_minus_alpha_cumprod_t * noise
        error = torch.abs(x_t - expected_x_t).max().item()
        
        print(f"  Timestep {t}: Max error = {error:.8f}")
    
    print("\n2. Testing Noise Schedule Properties:")
    
    # Verify that ᾱ_t decreases monotonically
    alphas_cumprod = diffusion.alphas_cumprod
    is_monotonic = torch.all(alphas_cumprod[1:] <= alphas_cumprod[:-1])
    print(f"  ᾱ_t is monotonically decreasing: {is_monotonic}")
    
    # Verify that ᾱ_0 = 1 and ᾱ_T ≈ 0
    print(f"  ᾱ_0 = {alphas_cumprod[0]:.6f} (should be 1.0)")
    print(f"  ᾱ_T = {alphas_cumprod[-1]:.6f} (should be close to 0)")
    
    print("\n3. Testing Variance Properties:")
    
    # Test that noise variance increases over time
    noise_variances = 1.0 - diffusion.alphas_cumprod
    is_increasing = torch.all(noise_variances[1:] >= noise_variances[:-1])
    print(f"  Noise variance is monotonically increasing: {is_increasing}")
    
    print("\nMathematical verification completed!")

def save_diffusion_visualization(images: List[torch.Tensor], filename: str, title: str):
    """Save diffusion visualization as a grid of images."""
    # Convert tensors to numpy arrays and normalize
    images_np = []
    for img in images:
        img_np = img.squeeze(0).permute(1, 2, 0).numpy()
        # Normalize to [0, 1] range
        img_np = (img_np - img_np.min()) / (img_np.max() - img_np.min())
        images_np.append(img_np)
    
    # Create grid
    n_images = len(images_np)
    n_cols = min(5, n_images)
    n_rows = (n_images + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 3 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    for i, img in enumerate(images_np):
        row = i // n_cols
        col = i % n_cols
        axes[row, col].imshow(img)
        axes[row, col].set_title(f'Step {i}')
        axes[row, col].axis('off')
    
    # Hide empty subplots
    for i in range(n_images, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        axes[row, col].axis('off')
    
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def create_detailed_schedule_visualization(schedule_info: dict):
    """Create detailed noise schedule visualization."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Plot 1: Betas
    axes[0, 0].plot(schedule_info['betas'].numpy())
    axes[0, 0].set_title('Noise Schedule (β_t)')
    axes[0, 0].set_xlabel('Timestep t')
    axes[0, 0].set_ylabel('β_t')
    axes[0, 0].grid(True)
    
    # Plot 2: Alphas
    axes[0, 1].plot(schedule_info['alphas'].numpy())
    axes[0, 1].set_title('α_t = 1 - β_t')
    axes[0, 1].set_xlabel('Timestep t')
    axes[0, 1].set_ylabel('α_t')
    axes[0, 1].grid(True)
    
    # Plot 3: Cumulative alphas
    axes[0, 2].plot(schedule_info['alphas_cumprod'].numpy())
    axes[0, 2].set_title('Cumulative α (ᾱ_t)')
    axes[0, 2].set_xlabel('Timestep t')
    axes[0, 2].set_ylabel('ᾱ_t')
    axes[0, 2].grid(True)
    
    # Plot 4: Square root of cumulative alphas
    axes[1, 0].plot(schedule_info['sqrt_alphas_cumprod'].numpy())
    axes[1, 0].set_title('√ᾱ_t')
    axes[1, 0].set_xlabel('Timestep t')
    axes[1, 0].set_ylabel('√ᾱ_t')
    axes[1, 0].grid(True)
    
    # Plot 5: Square root of one minus cumulative alphas
    axes[1, 1].plot(schedule_info['sqrt_one_minus_alphas_cumprod'].numpy())
    axes[1, 1].set_title('√(1 - ᾱ_t)')
    axes[1, 1].set_xlabel('Timestep t')
    axes[1, 1].set_ylabel('√(1 - ᾱ_t)')
    axes[1, 1].grid(True)
    
    # Plot 6: Noise level progression
    noise_levels = schedule_info['sqrt_one_minus_alphas_cumprod'].numpy()
    axes[1, 2].plot(noise_levels, label='Noise Level')
    axes[1, 2].set_title('Noise Level Progression')
    axes[1, 2].set_xlabel('Timestep t')
    axes[1, 2].set_ylabel('Noise Level')
    axes[1, 2].grid(True)
    axes[1, 2].legend()
    
    plt.tight_layout()
    plt.savefig('detailed_diffusion_schedule.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main function to run all diffusion processes demonstrations."""
    print("🚀 Starting Diffusion Processes Demonstration")
    print("=" * 60)
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠ CUDA not available, using CPU")
    
    try:
        # Run all demonstrations
        run_forward_diffusion_demo()
        run_reverse_diffusion_demo()
        run_full_diffusion_cycle()
        run_noise_schedule_analysis()
        run_mathematical_verification()
        
        print("\n" + "=" * 60)
        print("✅ All diffusion processes demonstrations completed successfully!")
        print("\nGenerated files:")
        for file in os.listdir("."):
            if file.endswith(".png"):
                print(f"  - {file}")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        logger.exception("Detailed error information:")

match __name__:
    case "__main__":
    main() 