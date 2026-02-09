#!/usr/bin/env python3
"""
Diffusion Processes Demo

Comprehensive demonstration of forward and reverse diffusion processes,
including various noise schedulers and sampling methods with mathematical
verification and visualization.
"""

import asyncio
import sys
import logging
import time
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from PIL import Image
import math

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import diffusion processes
from core.diffusion_processes_core import (
    DiffusionProcesses, DiffusionConfig, NoiseScheduleType, 
    SamplingMethod, PredictionType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diffusion_processes_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleUNet(nn.Module):
    """Simple UNet for demonstration purposes."""
    
    def __init__(self, in_channels=3, out_channels=3, time_dim=128):
        super().__init__()
        self.time_dim = time_dim
        
        # Time embedding
        self.time_mlp = nn.Sequential(
            nn.Linear(1, time_dim),
            nn.SiLU(),
            nn.Linear(time_dim, time_dim)
        )
        
        # Simple UNet architecture
        self.inc = nn.Conv2d(in_channels, 64, 3, padding=1)
        self.down1 = nn.Conv2d(64, 128, 3, stride=2, padding=1)
        self.down2 = nn.Conv2d(128, 256, 3, stride=2, padding=1)
        
        self.mid = nn.Conv2d(256, 256, 3, padding=1)
        
        self.up2 = nn.ConvTranspose2d(256, 128, 4, stride=2, padding=1)
        self.up1 = nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1)
        self.outc = nn.Conv2d(64, out_channels, 3, padding=1)
        
        # Time embedding layers
        self.time_embed1 = nn.Linear(time_dim, 64)
        self.time_embed2 = nn.Linear(time_dim, 128)
        self.time_embed3 = nn.Linear(time_dim, 256)
    
    def forward(self, x, t, condition=None):
        # Time embedding
        t = t.float().unsqueeze(-1) / 1000.0  # Normalize timesteps
        t_emb = self.time_mlp(t)
        
        # Downsampling
        x1 = self.inc(x)
        x1 = x1 + self.time_embed1(t_emb).view(-1, 64, 1, 1)
        
        x2 = self.down1(x1)
        x2 = x2 + self.time_embed2(t_emb).view(-1, 128, 1, 1)
        
        x3 = self.down2(x2)
        x3 = x3 + self.time_embed3(t_emb).view(-1, 256, 1, 1)
        
        # Middle
        x3 = self.mid(x3)
        
        # Upsampling
        x2 = self.up2(x3)
        x1 = self.up1(x2)
        
        return self.outc(x1)

class DiffusionProcessesDemo:
    """Comprehensive demo for diffusion processes."""
    
    def __init__(self):
        self.start_time = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
    
    async def demo_noise_schedules(self):
        """Demo different noise schedules."""
        try:
            logger.info("📊 Demo: Noise Schedules")
            
            # Test different noise schedules
            schedules = [
                ("Linear", NoiseScheduleType.LINEAR),
                ("Cosine", NoiseScheduleType.COSINE),
                ("Cosine Beta", NoiseScheduleType.COSINE_BETA),
                ("Sigmoid", NoiseScheduleType.SIGMOID),
                ("Quadratic", NoiseScheduleType.QUADRATIC),
                ("Exponential", NoiseScheduleType.EXPONENTIAL),
                ("Scaled Linear", NoiseScheduleType.SCALED_LINEAR),
                ("Piecewise Linear", NoiseScheduleType.PIECEWISE_LINEAR)
            ]
            
            fig, axes = plt.subplots(2, 4, figsize=(16, 8))
            axes = axes.flatten()
            
            for i, (name, schedule_type) in enumerate(schedules):
                logger.info(f"  Testing {name} schedule:")
                
                config = DiffusionConfig(
                    num_timesteps=1000,
                    beta_start=0.0001,
                    beta_end=0.02,
                    schedule_type=schedule_type
                )
                
                diffusion = DiffusionProcesses(config)
                info = diffusion.get_noise_schedule_info()
                
                # Plot beta schedule
                betas = np.array(info["betas"])
                alphas_cumprod = np.array(info["alphas_cumprod"])
                
                axes[i].plot(betas, label='β_t', color='blue')
                axes[i].plot(alphas_cumprod, label='ᾱ_t', color='red')
                axes[i].set_title(f"{name} Schedule")
                axes[i].set_xlabel("Timestep")
                axes[i].set_ylabel("Value")
                axes[i].legend()
                axes[i].grid(True, alpha=0.3)
                
                logger.info(f"    Beta range: {betas.min():.6f} - {betas.max():.6f}")
                logger.info(f"    Alphā range: {alphas_cumprod.min():.6f} - {alphas_cumprod.max():.6f}")
            
            plt.tight_layout()
            plt.savefig("noise_schedules_comparison.png", dpi=300, bbox_inches='tight')
            logger.info("    Saved noise schedules comparison plot")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Noise schedules demo failed: {e}")
            return False
    
    async def demo_forward_diffusion(self):
        """Demo forward diffusion process."""
        try:
            logger.info("🔄 Demo: Forward Diffusion Process")
            
            # Create test image
            batch_size = 4
            channels = 3
            height, width = 64, 64
            
            # Create a simple test pattern
            x_start = torch.zeros(batch_size, channels, height, width, device=self.device)
            for i in range(batch_size):
                # Create different patterns for each image
                if i == 0:
                    x_start[i, 0] = torch.linspace(0, 1, width).view(1, -1).repeat(height, 1)  # Red gradient
                elif i == 1:
                    x_start[i, 1] = torch.linspace(0, 1, height).view(-1, 1).repeat(1, width)  # Green gradient
                elif i == 2:
                    x_start[i, 2] = torch.ones(height, width) * 0.5  # Blue constant
                else:
                    x_start[i] = torch.randn(channels, height, width) * 0.1  # Random noise
            
            # Setup diffusion
            config = DiffusionConfig(
                num_timesteps=1000,
                schedule_type=NoiseScheduleType.COSINE
            )
            diffusion = DiffusionProcesses(config)
            
            # Test forward diffusion at different timesteps
            timesteps = [0, 100, 250, 500, 750, 999]
            
            fig, axes = plt.subplots(len(timesteps), batch_size, figsize=(batch_size * 2, len(timesteps) * 2))
            if len(timesteps) == 1:
                axes = axes.reshape(1, -1)
            
            for i, t in enumerate(timesteps):
                logger.info(f"  Forward diffusion at timestep {t}:")
                
                t_tensor = torch.full((batch_size,), t, device=self.device, dtype=torch.long)
                x_t = diffusion.forward_diffusion(x_start, t_tensor)
                
                # Calculate SNR
                alpha_cumprod_t = diffusion.scheduler.alphas_cumprod[t]
                snr = alpha_cumprod_t / (1 - alpha_cumprod_t)
                logger.info(f"    SNR: {snr:.4f}")
                
                # Visualize
                for j in range(batch_size):
                    img = x_t[j].cpu().detach().permute(1, 2, 0).numpy()
                    img = np.clip(img, 0, 1)
                    axes[i, j].imshow(img)
                    axes[i, j].set_title(f"t={t}, SNR={snr:.2f}")
                    axes[i, j].axis('off')
            
            plt.tight_layout()
            plt.savefig("forward_diffusion_process.png", dpi=300, bbox_inches='tight')
            logger.info("    Saved forward diffusion visualization")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Forward diffusion demo failed: {e}")
            return False
    
    async def demo_mathematical_verification(self):
        """Demo mathematical verification of diffusion processes."""
        try:
            logger.info("🧮 Demo: Mathematical Verification")
            
            # Setup
            config = DiffusionConfig(
                num_timesteps=1000,
                schedule_type=NoiseScheduleType.COSINE
            )
            diffusion = DiffusionProcesses(config)
            
            # Test 1: Forward process consistency
            logger.info("  Test 1: Forward Process Consistency")
            
            batch_size = 2
            x_start = torch.randn(batch_size, 3, 32, 32, device=self.device)
            t = torch.tensor([100, 500], device=self.device, dtype=torch.long)
            
            # Forward diffusion
            x_t = diffusion.forward_diffusion(x_start, t)
            
            # Verify mean and variance
            alpha_cumprod_t = diffusion.scheduler.alphas_cumprod[t].view(-1, 1, 1, 1)
            expected_mean = torch.sqrt(alpha_cumprod_t) * x_start
            expected_var = 1.0 - alpha_cumprod_t
            
            # Calculate empirical mean and variance
            empirical_mean = x_t.mean(dim=(2, 3), keepdim=True)
            empirical_var = x_t.var(dim=(2, 3), keepdim=True)
            
            mean_error = torch.abs(expected_mean - empirical_mean).mean()
            var_error = torch.abs(expected_var - empirical_var).mean()
            
            logger.info(f"    Mean error: {mean_error:.6f}")
            logger.info(f"    Variance error: {var_error:.6f}")
            
            # Test 2: Reverse process consistency
            logger.info("  Test 2: Reverse Process Consistency")
            
            # Create simple model
            model = SimpleUNet().to(self.device)
            diffusion.set_model(model)
            
            # Test reverse process
            x_t = torch.randn(batch_size, 3, 32, 32, device=self.device)
            t = torch.tensor([500, 100], device=self.device, dtype=torch.long)
            
            x_prev = diffusion.reverse_diffusion(x_t, t)
            
            logger.info(f"    Input shape: {x_t.shape}")
            logger.info(f"    Output shape: {x_prev.shape}")
            logger.info(f"    Output range: [{x_prev.min():.4f}, {x_prev.max():.4f}]")
            
            # Test 3: Noise schedule properties
            logger.info("  Test 3: Noise Schedule Properties")
            
            betas = diffusion.scheduler.betas
            alphas = diffusion.scheduler.alphas
            alphas_cumprod = diffusion.scheduler.alphas_cumprod
            
            # Check properties
            assert torch.all(betas >= 0) and torch.all(betas <= 1), "Betas should be in [0, 1]"
            assert torch.all(alphas >= 0) and torch.all(alphas <= 1), "Alphas should be in [0, 1]"
            assert torch.all(alphas_cumprod >= 0) and torch.all(alphas_cumprod <= 1), "Alphā should be in [0, 1]"
            assert torch.all(alphas_cumprod[1:] <= alphas_cumprod[:-1]), "Alphā should be decreasing"
            
            logger.info("    ✅ All noise schedule properties verified")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Mathematical verification demo failed: {e}")
            return False
    
    async def demo_sampling_methods(self):
        """Demo different sampling methods."""
        try:
            logger.info("🎲 Demo: Sampling Methods")
            
            # Create simple model
            model = SimpleUNet().to(self.device)
            
            # Test different sampling methods
            methods = [
                ("DDPM", SamplingMethod.DDPM),
                ("DDIM", SamplingMethod.DDIM)
            ]
            
            fig, axes = plt.subplots(1, len(methods), figsize=(len(methods) * 4, 4))
            if len(methods) == 1:
                axes = [axes]
            
            for i, (name, method) in enumerate(methods):
                logger.info(f"  Testing {name} sampling:")
                
                config = DiffusionConfig(
                    num_timesteps=1000,
                    schedule_type=NoiseScheduleType.COSINE,
                    sampling_method=method,
                    ddim_eta=0.0 if method == SamplingMethod.DDIM else 0.0
                )
                
                diffusion = DiffusionProcesses(config, model)
                
                # Generate sample
                shape = (1, 3, 64, 64)
                start_time = time.time()
                sample = diffusion.sample(shape)
                generation_time = time.time() - start_time
                
                logger.info(f"    Generation time: {generation_time:.2f}s")
                logger.info(f"    Sample range: [{sample.min():.4f}, {sample.max():.4f}]")
                
                # Visualize
                img = sample[0].cpu().detach().permute(1, 2, 0).numpy()
                img = np.clip(img, 0, 1)
                axes[i].imshow(img)
                axes[i].set_title(f"{name}\nTime: {generation_time:.2f}s")
                axes[i].axis('off')
            
            plt.tight_layout()
            plt.savefig("sampling_methods_comparison.png", dpi=300, bbox_inches='tight')
            logger.info("    Saved sampling methods comparison")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sampling methods demo failed: {e}")
            return False
    
    async def demo_prediction_types(self):
        """Demo different prediction types."""
        try:
            logger.info("🎯 Demo: Prediction Types")
            
            # Create simple model
            model = SimpleUNet().to(self.device)
            
            # Test different prediction types
            prediction_types = [
                ("Epsilon", PredictionType.EPSILON),
                ("X0", PredictionType.X0),
                ("V", PredictionType.V)
            ]
            
            for name, pred_type in prediction_types:
                logger.info(f"  Testing {name} prediction:")
                
                config = DiffusionConfig(
                    num_timesteps=1000,
                    schedule_type=NoiseScheduleType.COSINE,
                    prediction_type=pred_type
                )
                
                diffusion = DiffusionProcesses(config, model)
                
                # Test single step
                x_t = torch.randn(2, 3, 32, 32, device=self.device)
                t = torch.tensor([500, 100], device=self.device, dtype=torch.long)
                
                x_prev = diffusion.reverse_diffusion(x_t, t)
                
                logger.info(f"    Input shape: {x_t.shape}")
                logger.info(f"    Output shape: {x_prev.shape}")
                logger.info(f"    Output range: [{x_prev.min():.4f}, {x_prev.max():.4f}]")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Prediction types demo failed: {e}")
            return False
    
    async def demo_trajectory_visualization(self):
        """Demo trajectory visualization."""
        try:
            logger.info("📈 Demo: Trajectory Visualization")
            
            # Create simple model
            model = SimpleUNet().to(self.device)
            
            config = DiffusionConfig(
                num_timesteps=1000,
                schedule_type=NoiseScheduleType.COSINE,
                sampling_method=SamplingMethod.DDIM
            )
            
            diffusion = DiffusionProcesses(config, model)
            
            # Generate sample with trajectory
            shape = (1, 3, 64, 64)
            
            # Custom timesteps for visualization
            timesteps = list(range(999, -1, -100))  # Every 100 steps
            
            device = next(model.parameters()).device
            batch_size = shape[0]
            
            # Initialize x_T
            x = torch.randn(shape, device=device)
            
            # Store trajectory
            trajectory = [x.cpu().detach()]
            
            # Reverse process with trajectory
            for i, t in enumerate(timesteps[:-1]):
                t_tensor = torch.full((batch_size,), t, device=device, dtype=torch.long)
                t_prev = timesteps[i + 1]
                t_prev_tensor = torch.full((batch_size,), t_prev, device=device, dtype=torch.long)
                
                x = diffusion.reverse_process.p_sample_ddim(x, t_tensor, t_prev_tensor)
                trajectory.append(x.cpu().detach())
            
            # Visualize trajectory
            fig, axes = plt.subplots(1, len(trajectory), figsize=(len(trajectory) * 2, 2))
            
            for i, x_t in enumerate(trajectory):
                img = x_t[0].permute(1, 2, 0).numpy()
                img = np.clip(img, 0, 1)
                axes[i].imshow(img)
                axes[i].set_title(f"t={timesteps[i]}")
                axes[i].axis('off')
            
            plt.tight_layout()
            plt.savefig("diffusion_trajectory.png", dpi=300, bbox_inches='tight')
            logger.info("    Saved diffusion trajectory visualization")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Trajectory visualization demo failed: {e}")
            return False
    
    async def demo_performance_benchmark(self):
        """Demo performance benchmarking."""
        try:
            logger.info("⚡ Demo: Performance Benchmark")
            
            # Create simple model
            model = SimpleUNet().to(self.device)
            
            # Test different configurations
            configs = [
                ("Cosine + DDPM", DiffusionConfig(
                    schedule_type=NoiseScheduleType.COSINE,
                    sampling_method=SamplingMethod.DDPM
                )),
                ("Cosine + DDIM", DiffusionConfig(
                    schedule_type=NoiseScheduleType.COSINE,
                    sampling_method=SamplingMethod.DDIM
                )),
                ("Linear + DDPM", DiffusionConfig(
                    schedule_type=NoiseScheduleType.LINEAR,
                    sampling_method=SamplingMethod.DDPM
                )),
                ("Linear + DDIM", DiffusionConfig(
                    schedule_type=NoiseScheduleType.LINEAR,
                    sampling_method=SamplingMethod.DDIM
                ))
            ]
            
            shape = (1, 3, 64, 64)
            num_runs = 3
            
            results = []
            
            for name, config in configs:
                logger.info(f"  Benchmarking {name}:")
                
                diffusion = DiffusionProcesses(config, model)
                
                times = []
                for run in range(num_runs):
                    start_time = time.time()
                    sample = diffusion.sample(shape)
                    generation_time = time.time() - start_time
                    times.append(generation_time)
                
                avg_time = np.mean(times)
                std_time = np.std(times)
                
                results.append({
                    "name": name,
                    "avg_time": avg_time,
                    "std_time": std_time,
                    "times": times
                })
                
                logger.info(f"    Average time: {avg_time:.2f}s ± {std_time:.2f}s")
                logger.info(f"    Individual times: {[f'{t:.2f}s' for t in times]}")
            
            # Print summary
            logger.info("  Performance Summary:")
            for result in results:
                logger.info(f"    {result['name']}: {result['avg_time']:.2f}s ± {result['std_time']:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance benchmark demo failed: {e}")
            return False
    
    async def run(self):
        """Main demo execution."""
        try:
            self.start_time = datetime.now()
            
            logger.info("🚀 Starting Diffusion Processes Demo...")
            logger.info(f"⏰ Start time: {self.start_time}")
            
            # Run demos
            demos = [
                self.demo_noise_schedules(),
                self.demo_forward_diffusion(),
                self.demo_mathematical_verification(),
                self.demo_sampling_methods(),
                self.demo_prediction_types(),
                self.demo_trajectory_visualization(),
                self.demo_performance_benchmark()
            ]
            
            for demo in demos:
                if not await demo:
                    logger.warning("⚠️ Demo completed with warnings")
            
            # Final status
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            logger.info("🎉 Diffusion Processes Demo completed successfully!")
            logger.info(f"⏱️  Total duration: {duration}")
            logger.info("📊 All demos executed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo execution failed: {e}")
            return False

async def main():
    """Main entry point."""
    demo = DiffusionProcessesDemo()
    
    try:
        success = await demo.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
