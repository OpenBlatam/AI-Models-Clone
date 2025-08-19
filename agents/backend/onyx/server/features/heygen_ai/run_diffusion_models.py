from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

import torch
import logging
from typing import List, Optional
from PIL import Image
import os
from diffusion_models_implementation import (
from diffusers import DDPMScheduler
    import time
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Diffusion Models Runner
Demonstrates and runs diffusion models for various generative tasks.
"""


# Import our diffusion models implementation
    DiffusionModelManager, DDPMTrainer, CustomUNet
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_text_to_image_generation():
    """Run text-to-image generation using Stable Diffusion."""
    print("\n=== Text-to-Image Generation ===")
    
    manager = DiffusionModelManager()
    
    prompts = [
        "A serene mountain landscape at sunset, digital art",
        "A futuristic city with flying cars, sci-fi style",
        "A cute cat playing with yarn, cartoon style",
        "An ancient castle on a hill, fantasy art"
    ]
    
    for i, prompt in enumerate(prompts):
        print(f"\nGenerating image {i+1}/{len(prompts)}: {prompt}")
        try:
            image = manager.generate_image(
                prompt=prompt,
                num_inference_steps=30,
                guidance_scale=7.5
            )
            print(f"✓ Image generated successfully!")
            # Save image
            output_path = f"generated_image_{i+1}.png"
            image.save(output_path)
            print(f"✓ Image saved to {output_path}")
        except Exception as e:
            print(f"✗ Error generating image: {e}")

def run_batch_generation():
    """Run batch image generation."""
    print("\n=== Batch Image Generation ===")
    
    manager = DiffusionModelManager()
    
    prompts = [
        "A beautiful flower garden",
        "A stormy ocean scene",
        "A cozy coffee shop interior"
    ]
    
    try:
        images = manager.generate_batch(
            prompts=prompts,
            num_inference_steps=25,
            guidance_scale=7.0
        )
        
        for i, (prompt, image) in enumerate(zip(prompts, images)):
            output_path = f"batch_image_{i+1}.png"
            image.save(output_path)
            print(f"✓ Generated: {prompt} -> {output_path}")
            
    except Exception as e:
        print(f"✗ Error in batch generation: {e}")

def run_custom_ddpm_training():
    """Run custom DDPM training demonstration."""
    print("\n=== Custom DDPM Training ===")
    
    # Initialize custom UNet and scheduler
    custom_unet = CustomUNet(in_channels=3, out_channels=3, time_dim=256)
    scheduler = DDPMScheduler(num_train_timesteps=1000)
    
    # Initialize trainer
    trainer = DDPMTrainer(custom_unet, scheduler)
    trainer.setup_training(learning_rate=1e-4, num_training_steps=100)
    
    print("Training setup completed!")
    
    # Simulate training loop
    print("Running training simulation...")
    total_loss = 0
    num_steps = 10
    
    for step in range(num_steps):
        # Create dummy batch (in real training, this would be actual images)
        batch = torch.randn(4, 3, 64, 64)  # 4 images, 3 channels, 64x64
        
        # Training step
        loss_info = trainer.train_step(batch)
        loss = loss_info["loss"]
        total_loss += loss
        
        if (step + 1) % 2 == 0:
            print(f"Step {step+1}/{num_steps}, Loss: {loss:.4f}")
    
    avg_loss = total_loss / num_steps
    print(f"Training completed! Average loss: {avg_loss:.4f}")
    
    # Save model
    trainer.save_model("custom_ddpm_model.pth")
    print("✓ Model saved to custom_ddpm_model.pth")

def run_model_loading_demo():
    """Demonstrate loading and using saved models."""
    print("\n=== Model Loading Demo ===")
    
    # Create new trainer instance
    custom_unet = CustomUNet()
    scheduler = DDPMScheduler(num_train_timesteps=1000)
    trainer = DDPMTrainer(custom_unet, scheduler)
    
    # Check if saved model exists
    if os.path.exists("custom_ddpm_model.pth"):
        print("Loading saved model...")
        trainer.load_model("custom_ddpm_model.pth")
        print("✓ Model loaded successfully!")
    else:
        print("No saved model found. Run training first.")

def run_performance_benchmark():
    """Run performance benchmark for diffusion models."""
    print("\n=== Performance Benchmark ===")
    
    
    manager = DiffusionModelManager()
    
    # Benchmark text-to-image generation
    prompt = "A simple test image for benchmarking"
    
    print("Benchmarking image generation...")
    start_time = time.time()
    
    try:
        image = manager.generate_image(
            prompt=prompt,
            num_inference_steps=20,
            guidance_scale=7.5
        )
        end_time = time.time()
        
        generation_time = end_time - start_time
        print(f"✓ Image generated in {generation_time:.2f} seconds")
        print(f"✓ Average time per step: {generation_time/20:.3f} seconds")
        
    except Exception as e:
        print(f"✗ Benchmark failed: {e}")

def main():
    """Main function to run all diffusion model demonstrations."""
    print("🚀 Starting Diffusion Models Demonstration")
    print("=" * 50)
    
    # Check CUDA availability
    if torch.cuda.is_available():
        print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠ CUDA not available, using CPU")
    
    try:
        # Run demonstrations
        run_text_to_image_generation()
        run_batch_generation()
        run_custom_ddpm_training()
        run_model_loading_demo()
        run_performance_benchmark()
        
        print("\n" + "=" * 50)
        print("✅ All diffusion model demonstrations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        logger.exception("Detailed error information:")

match __name__:
    case "__main__":
    main() 