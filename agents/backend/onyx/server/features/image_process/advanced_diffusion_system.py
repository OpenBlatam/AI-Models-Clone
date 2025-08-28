#!/usr/bin/env python3
"""
Advanced Diffusion Models System

This module implements comprehensive diffusion models including:
- DDPM (Denoising Diffusion Probabilistic Models)
- DDIM (Denoising Diffusion Implicit Models)
- Advanced sampling techniques
- Conditional generation
- Classifier-free guidance
- Latent diffusion models
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
import numpy as np
import math
import logging
from dataclasses import dataclass
from tqdm import tqdm
import matplotlib.pyplot as plt
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class DiffusionConfig:
    """Configuration for diffusion models."""
    # Model architecture
    model_type: str = "unet"  # "unet", "transformer", "latent"
    image_size: int = 64
    in_channels: int = 3
    out_channels: int = 3
    hidden_size: int = 128
    num_layers: int = 4
    num_heads: int = 8
    dropout: float = 0.1
    
    # Diffusion process
    num_timesteps: int = 1000
    beta_start: float = 1e-4
    beta_end: float = 0.02
    schedule_type: str = "linear"  # "linear", "cosine", "sigmoid"
    
    # Sampling
    sampling_method: str = "ddpm"  # "ddpm", "ddim", "plms"
    guidance_scale: float = 7.5
    classifier_free_guidance: bool = True
    num_inference_steps: int = 50
    
    # Training
    batch_size: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    num_epochs: int = 100
    gradient_clip: float = 1.0
    
    # Gradient accumulation
    gradient_accumulation_steps: int = 1
    effective_batch_size: int = 32
    
    # Latent diffusion
    latent_channels: int = 4
    latent_size: int = 16
    autoencoder_scale_factor: float = 8.0


class NoiseScheduler:
    """Noise scheduler for diffusion models."""
    
    def __init__(self, config: DiffusionConfig):
        self.config = config
        self.num_timesteps = config.num_timesteps
        self.beta_start = config.beta_start
        self.beta_end = config.beta_end
        self.schedule_type = config.schedule_type
        
        # Initialize noise schedule
        self.betas = self._get_beta_schedule()
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alphas_cumprod_prev = F.pad(self.alphas_cumprod[:-1], (1, 0), value=1.0)
        
        # Precompute values for sampling
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - self.alphas_cumprod)
        self.log_one_minus_alphas_cumprod = torch.log(1.0 - self.alphas_cumprod)
        self.sqrt_recip_alphas_cumprod = torch.sqrt(1.0 / self.alphas_cumprod)
        self.sqrt_recipm1_alphas_cumprod = torch.sqrt(1.0 / self.alphas_cumprod - 1)
        
        # DDIM specific
        self.ddim_eta = 0.0
        self.ddim_timesteps = self._make_ddim_timesteps()
    
    def _get_beta_schedule(self) -> torch.Tensor:
        """Get beta schedule based on configuration."""
        if self.schedule_type == "linear":
            return torch.linspace(self.beta_start, self.beta_end, self.num_timesteps)
        elif self.schedule_type == "cosine":
            return self._cosine_beta_schedule()
        elif self.schedule_type == "sigmoid":
            return self._sigmoid_beta_schedule()
        else:
            raise ValueError(f"Unknown schedule type: {self.schedule_type}")
    
    def _cosine_beta_schedule(self) -> torch.Tensor:
        """Cosine beta schedule."""
        steps = self.num_timesteps + 1
        x = torch.linspace(0, self.num_timesteps, steps)
        alphas_cumprod = torch.cos(((x / self.num_timesteps) + 0.008) / 1.008 * math.pi * 0.5) ** 2
        alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
        betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
        return torch.clip(betas, 0, 0.999)
    
    def _sigmoid_beta_schedule(self) -> torch.Tensor:
        """Sigmoid beta schedule."""
        betas = torch.linspace(-6, 6, self.num_timesteps)
        return torch.sigmoid(betas) * (self.beta_end - self.beta_start) + self.beta_start
    
    def _make_ddim_timesteps(self) -> List[int]:
        """Make DDIM timesteps."""
        c = self.num_timesteps // self.config.num_inference_steps
        ddim_timesteps = [i * c for i in range(self.config.num_inference_steps)]
        return ddim_timesteps
    
    def add_noise(self, x_start: torch.Tensor, t: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Add noise to images at timestep t."""
        noise = torch.randn_like(x_start)
        sqrt_alphas_cumprod_t = self.sqrt_alphas_cumprod[t].reshape(-1, 1, 1, 1)
        sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t].reshape(-1, 1, 1, 1)
        
        x_noisy = sqrt_alphas_cumprod_t * x_start + sqrt_one_minus_alphas_cumprod_t * noise
        return x_noisy, noise
    
    def remove_noise(self, x_noisy: torch.Tensor, noise_pred: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """Remove predicted noise from noisy image."""
        sqrt_alphas_cumprod_t = self.sqrt_alphas_cumprod[t].reshape(-1, 1, 1, 1)
        sqrt_one_minus_alphas_cumprod_t = self.sqrt_one_minus_alphas_cumprod[t].reshape(-1, 1, 1, 1)
        
        x_denoised = (x_noisy - sqrt_one_minus_alphas_cumprod_t * noise_pred) / sqrt_alphas_cumprod_t
        return x_denoised


class UNetBlock(nn.Module):
    """UNet block with residual connections."""
    
    def __init__(self, in_channels: int, out_channels: int, time_emb_dim: int, dropout: float = 0.1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1)
        self.time_mlp = nn.Sequential(
            nn.SiLU(),
            nn.Linear(time_emb_dim, out_channels)
        )
        self.dropout = nn.Dropout(dropout)
        self.norm1 = nn.GroupNorm(8, out_channels)
        self.norm2 = nn.GroupNorm(8, out_channels)
        
        if in_channels != out_channels:
            self.residual_conv = nn.Conv2d(in_channels, out_channels, 1)
        else:
            self.residual_conv = nn.Identity()
    
    def forward(self, x: torch.Tensor, time_emb: torch.Tensor) -> torch.Tensor:
        residual = self.residual_conv(x)
        
        x = self.conv1(x)
        x = self.norm1(x)
        x = F.silu(x)
        
        # Add time embedding
        time_emb = self.time_mlp(time_emb)
        x = x + time_emb.unsqueeze(-1).unsqueeze(-1)
        
        x = self.conv2(x)
        x = self.norm2(x)
        x = F.silu(x)
        x = self.dropout(x)
        
        return x + residual


class UNet(nn.Module):
    """UNet architecture for diffusion models."""
    
    def __init__(self, config: DiffusionConfig):
        super().__init__()
        self.config = config
        
        # Time embedding
        time_dim = config.hidden_size * 4
        self.time_embedding = nn.Sequential(
            nn.Linear(1, config.hidden_size),
            nn.SiLU(),
            nn.Linear(config.hidden_size, time_dim)
        )
        
        # Initial convolution
        self.init_conv = nn.Conv2d(config.in_channels, config.hidden_size, 3, padding=1)
        
        # Down blocks
        self.down_blocks = nn.ModuleList()
        in_channels = config.hidden_size
        for i in range(config.num_layers):
            out_channels = config.hidden_size * (2 ** i)
            self.down_blocks.append(UNetBlock(in_channels, out_channels, time_dim, config.dropout))
            in_channels = out_channels
        
        # Middle block
        self.middle_block = UNetBlock(in_channels, in_channels, time_dim, config.dropout)
        
        # Up blocks
        self.up_blocks = nn.ModuleList()
        for i in range(config.num_layers - 1, -1, -1):
            out_channels = config.hidden_size * (2 ** i)
            self.up_blocks.append(UNetBlock(in_channels * 2, out_channels, time_dim, config.dropout))
            in_channels = out_channels
        
        # Final convolution
        self.final_conv = nn.Sequential(
            nn.GroupNorm(8, in_channels),
            nn.SiLU(),
            nn.Conv2d(in_channels, config.out_channels, 3, padding=1)
        )
    
    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        # Time embedding
        t = t.float() / self.config.num_timesteps
        time_emb = self.time_embedding(t.unsqueeze(-1))
        
        # Initial convolution
        x = self.init_conv(x)
        
        # Down sampling
        down_features = []
        for block in self.down_blocks:
            x = block(x, time_emb)
            down_features.append(x)
            x = F.avg_pool2d(x, 2)
        
        # Middle block
        x = self.middle_block(x, time_emb)
        
        # Up sampling
        for i, block in enumerate(self.up_blocks):
            x = F.interpolate(x, scale_factor=2, mode='nearest')
            x = torch.cat([x, down_features[-(i + 1)]], dim=1)
            x = block(x, time_emb)
        
        # Final convolution
        x = self.final_conv(x)
        
        return x


class Autoencoder(nn.Module):
    """Autoencoder for latent diffusion models."""
    
    def __init__(self, config: DiffusionConfig):
        super().__init__()
        self.config = config
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(config.in_channels, 64, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 256, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, config.latent_channels, 3, padding=1)
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Conv2d(config.latent_channels, 256, 3, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, config.out_channels, 4, stride=2, padding=1),
            nn.Tanh()
        )
    
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode image to latent."""
        return self.encoder(x)
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent to image."""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass: encode and decode."""
        z = self.encode(x)
        x_recon = self.decode(z)
        return x_recon, z


class DiffusionModel(nn.Module):
    """Main diffusion model class."""
    
    def __init__(self, config: DiffusionConfig):
        super().__init__()
        self.config = config
        
        # Initialize components
        if config.model_type == "unet":
            self.model = UNet(config)
        elif config.model_type == "latent":
            self.autoencoder = Autoencoder(config)
            # Use smaller UNet for latent space
            latent_config = DiffusionConfig(
                model_type="unet",
                image_size=config.latent_size,
                in_channels=config.latent_channels,
                out_channels=config.latent_channels,
                hidden_size=config.hidden_size // 2,
                num_layers=config.num_layers - 1
            )
            self.model = UNet(latent_config)
        else:
            raise ValueError(f"Unknown model type: {config.model_type}")
        
        # Noise scheduler
        self.noise_scheduler = NoiseScheduler(config)
        
        # Classifier-free guidance
        self.classifier_free_guidance = config.classifier_free_guidance
        self.guidance_scale = config.guidance_scale
    
    def forward(self, x: torch.Tensor, t: torch.Tensor, 
                condition: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass."""
        if self.config.model_type == "latent":
            # Encode to latent space
            with torch.no_grad():
                z = self.autoencoder.encode(x)
            # Predict noise in latent space
            noise_pred = self.model(z, t)
            return noise_pred
        else:
            # Direct prediction in pixel space
            return self.model(x, t)
    
    def sample(self, batch_size: int = 1, condition: Optional[torch.Tensor] = None,
               num_steps: Optional[int] = None) -> torch.Tensor:
        """Generate samples using the diffusion model."""
        if num_steps is None:
            num_steps = self.config.num_inference_steps
        
        device = next(self.parameters()).device
        
        if self.config.sampling_method == "ddpm":
            return self._sample_ddpm(batch_size, condition, num_steps)
        elif self.config.sampling_method == "ddim":
            return self._sample_ddim(batch_size, condition, num_steps)
        else:
            raise ValueError(f"Unknown sampling method: {self.config.sampling_method}")
    
    def _sample_ddpm(self, batch_size: int, condition: Optional[torch.Tensor],
                     num_steps: int) -> torch.Tensor:
        """DDPM sampling."""
        device = next(self.parameters()).device
        
        # Start from pure noise
        if self.config.model_type == "latent":
            x = torch.randn(batch_size, self.config.latent_channels, 
                           self.config.latent_size, self.config.latent_size, device=device)
        else:
            x = torch.randn(batch_size, self.config.in_channels, 
                           self.config.image_size, self.config.image_size, device=device)
        
        # Reverse diffusion process
        for i in tqdm(range(num_steps - 1, -1, -1), desc="Sampling"):
            t = torch.full((batch_size,), i, device=device, dtype=torch.long)
            
            # Predict noise
            noise_pred = self.forward(x, t, condition)
            
            # Apply classifier-free guidance if enabled
            if self.classifier_free_guidance and condition is not None:
                uncond_pred = self.forward(x, t, None)
                noise_pred = uncond_pred + self.guidance_scale * (noise_pred - uncond_pred)
            
            # Remove noise
            x = self.noise_scheduler.remove_noise(x, noise_pred, t)
            
            # Add noise for next step (except last step)
            if i > 0:
                noise = torch.randn_like(x)
                x = x + torch.sqrt(self.noise_scheduler.betas[i]) * noise
        
        # Decode if using latent diffusion
        if self.config.model_type == "latent":
            with torch.no_grad():
                x = self.autoencoder.decode(x)
        
        return x
    
    def _sample_ddim(self, batch_size: int, condition: Optional[torch.Tensor],
                     num_steps: int) -> torch.Tensor:
        """DDIM sampling."""
        device = next(self.parameters()).device
        
        # Start from pure noise
        if self.config.model_type == "latent":
            x = torch.randn(batch_size, self.config.latent_channels, 
                           self.config.latent_size, self.config.latent_size, device=device)
        else:
            x = torch.randn(batch_size, self.config.in_channels, 
                           self.config.image_size, self.config.image_size, device=device)
        
        # DDIM timesteps
        timesteps = self.noise_scheduler.ddim_timesteps[:num_steps]
        
        # Reverse diffusion process
        for i, t in enumerate(tqdm(timesteps[::-1], desc="DDIM Sampling")):
            t_tensor = torch.full((batch_size,), t, device=device, dtype=torch.long)
            
            # Predict noise
            noise_pred = self.forward(x, t_tensor, condition)
            
            # Apply classifier-free guidance if enabled
            if self.classifier_free_guidance and condition is not None:
                uncond_pred = self.forward(x, t_tensor, None)
                noise_pred = uncond_pred + self.guidance_scale * (noise_pred - uncond_pred)
            
            # DDIM update
            alpha_cumprod = self.noise_scheduler.alphas_cumprod[t]
            alpha_cumprod_prev = self.noise_scheduler.alphas_cumprod_prev[t]
            
            # Predicted x_0
            pred_x0 = (x - torch.sqrt(1 - alpha_cumprod) * noise_pred) / torch.sqrt(alpha_cumprod)
            
            # Direction pointing to x_t
            dir_xt = torch.sqrt(1 - alpha_cumprod_prev) * noise_pred
            
            # Add noise for stochasticity
            noise = torch.randn_like(x) if self.noise_scheduler.ddim_eta > 0 else 0
            noise_scale = self.noise_scheduler.ddim_eta * torch.sqrt((1 - alpha_cumprod_prev) / (1 - alpha_cumprod)) * torch.sqrt(1 - alpha_cumprod / alpha_cumprod_prev)
            
            x = torch.sqrt(alpha_cumprod_prev) * pred_x0 + dir_xt + noise_scale * noise
        
        # Decode if using latent diffusion
        if self.config.model_type == "latent":
            with torch.no_grad():
                x = self.autoencoder.decode(x)
        
        return x


class DiffusionTrainer:
    """Trainer for diffusion models with gradient accumulation support."""
    
    def __init__(self, model: DiffusionModel, config: DiffusionConfig):
        self.model = model
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Calculate effective batch size
        self.effective_batch_size = config.effective_batch_size
        self.gradient_accumulation_steps = config.gradient_accumulation_steps
        self.actual_batch_size = self.effective_batch_size // self.gradient_accumulation_steps
        
        # Optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay
        )
        
        # Loss function
        self.criterion = nn.MSELoss()
        
        # Training state
        self.global_step = 0
        self.best_loss = float('inf')
        self.accumulation_step = 0
        self.accumulated_loss = 0.0
        
        # Mixed precision training
        self.use_amp = torch.cuda.is_available()
        if self.use_amp:
            self.scaler = torch.cuda.amp.GradScaler()
        
        logger.info(f"Initialized trainer with effective batch size: {self.effective_batch_size}")
        logger.info(f"Gradient accumulation steps: {self.gradient_accumulation_steps}")
        logger.info(f"Actual batch size per step: {self.actual_batch_size}")
        logger.info(f"Mixed precision: {self.use_amp}")
    
    def train_step(self, batch: torch.Tensor) -> Dict[str, float]:
        """Single training step with gradient accumulation."""
        self.model.train()
        
        batch = batch.to(self.device)
        batch_size = batch.shape[0]
        
        # Sample random timesteps
        t = torch.randint(0, self.config.num_timesteps, (batch_size,), device=self.device)
        
        # Add noise
        x_noisy, noise = self.model.noise_scheduler.add_noise(batch, t)
        
        # Predict noise
        if self.use_amp:
            with torch.cuda.amp.autocast():
                noise_pred = self.model(x_noisy, t)
                loss = self.criterion(noise_pred, noise)
        else:
            noise_pred = self.model(x_noisy, t)
            loss = self.criterion(noise_pred, noise)
        
        # Scale loss for gradient accumulation
        loss = loss / self.gradient_accumulation_steps
        
        # Backward pass
        if self.use_amp:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
        
        # Accumulate loss
        self.accumulated_loss += loss.item() * self.gradient_accumulation_steps
        self.accumulation_step += 1
        
        # Update weights if accumulation is complete
        if self.accumulation_step >= self.gradient_accumulation_steps:
            if self.use_amp:
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clip)
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clip)
                self.optimizer.step()
            
            self.optimizer.zero_grad()
            self.accumulation_step = 0
            self.global_step += 1
        
        return {"loss": loss.item() * self.gradient_accumulation_steps}
    
    def train(self, dataloader: DataLoader, num_epochs: int) -> Dict[str, List[float]]:
        """Training loop with gradient accumulation."""
        losses = []
        
        for epoch in range(num_epochs):
            epoch_losses = []
            
            for batch in tqdm(dataloader, desc=f"Epoch {epoch + 1}"):
                if isinstance(batch, (list, tuple)):
                    batch = batch[0]
                
                step_metrics = self.train_step(batch)
                epoch_losses.append(step_metrics["loss"])
                
                # Log progress
                if self.global_step % 100 == 0:
                    avg_loss = np.mean(epoch_losses[-100:])
                    logger.info(f"Step {self.global_step}, Loss: {avg_loss:.4f}")
                    logger.info(f"Effective batch size: {self.effective_batch_size}")
                
                # Generate samples periodically
                if self.global_step % 1000 == 0:
                    self._generate_samples(epoch, self.global_step)
            
            avg_epoch_loss = np.mean(epoch_losses)
            losses.append(avg_epoch_loss)
            logger.info(f"Epoch {epoch + 1} completed. Average loss: {avg_epoch_loss:.4f}")
            
            # Save checkpoint
            if avg_epoch_loss < self.best_loss:
                self.best_loss = avg_epoch_loss
                self.save_checkpoint("best_model.pt")
        
        return {"losses": losses}
    
    def _generate_samples(self, epoch: int, step: int, num_samples: int = 4):
        """Generate and save sample images."""
        self.model.eval()
        
        with torch.no_grad():
            samples = self.model.sample(num_samples)
        
        # Save samples
        samples = (samples + 1) / 2  # Convert from [-1, 1] to [0, 1]
        samples = torch.clamp(samples, 0, 1)
        
        # Create grid
        fig, axes = plt.subplots(2, 2, figsize=(8, 8))
        for i, ax in enumerate(axes.flat):
            if i < num_samples:
                img = samples[i].cpu().permute(1, 2, 0).numpy()
                ax.imshow(img)
                ax.axis('off')
        
        plt.tight_layout()
        plt.savefig(f"samples_epoch_{epoch}_step_{step}.png")
        plt.close()
    
    def save_checkpoint(self, filename: str):
        """Save model checkpoint."""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config,
            'global_step': self.global_step,
            'best_loss': self.best_loss
        }
        torch.save(checkpoint, filename)
        logger.info(f"Checkpoint saved: {filename}")
    
    def load_checkpoint(self, filename: str):
        """Load model checkpoint."""
        checkpoint = torch.load(filename, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.global_step = checkpoint['global_step']
        self.best_loss = checkpoint['best_loss']
        logger.info(f"Checkpoint loaded: {filename}")

    def get_effective_batch_size(self) -> int:
        """Get the effective batch size after gradient accumulation."""
        return self.effective_batch_size
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage information."""
        if torch.cuda.is_available():
            return {
                "gpu_memory_allocated": torch.cuda.memory_allocated() / 1024**3,  # GB
                "gpu_memory_reserved": torch.cuda.memory_reserved() / 1024**3,    # GB
                "gpu_memory_free": (torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()) / 1024**3
            }
        else:
            return {"cpu_memory": "N/A"}
    
    def optimize_batch_size(self, target_memory_gb: float = 8.0) -> int:
        """Dynamically optimize batch size based on available memory."""
        if not torch.cuda.is_available():
            return self.actual_batch_size
        
        current_memory = torch.cuda.memory_allocated() / 1024**3
        available_memory = target_memory_gb - current_memory
        
        if available_memory > 2.0:  # At least 2GB available
            # Increase batch size
            new_batch_size = min(self.actual_batch_size * 2, 128)
            if new_batch_size != self.actual_batch_size:
                self.actual_batch_size = new_batch_size
                self.effective_batch_size = new_batch_size * self.gradient_accumulation_steps
                logger.info(f"Optimized batch size to: {self.actual_batch_size}")
        
        return self.actual_batch_size


# Example usage and testing
if __name__ == "__main__":
    # Test configuration with gradient accumulation for large batch sizes
    config = DiffusionConfig(
        model_type="unet",
        image_size=32,
        hidden_size=64,
        num_layers=3,
        num_timesteps=100,
        num_inference_steps=20,
        batch_size=4,
        # Gradient accumulation settings
        gradient_accumulation_steps=8,  # Accumulate gradients over 8 steps
        effective_batch_size=32,        # Effective batch size = 4 * 8 = 32
        learning_rate=1e-4,
        gradient_clip=1.0
    )
    
    # Create model
    model = DiffusionModel(config)
    
    # Create trainer with gradient accumulation
    trainer = DiffusionTrainer(model, config)
    
    # Test sampling
    samples = model.sample(batch_size=2)
    print(f"Generated samples shape: {samples.shape}")
    
    # Print training configuration
    print(f"Effective batch size: {trainer.get_effective_batch_size()}")
    print(f"Gradient accumulation steps: {trainer.gradient_accumulation_steps}")
    print(f"Actual batch size per step: {trainer.actual_batch_size}")
    
    # Memory usage info
    memory_info = trainer.get_memory_usage()
    print(f"Memory usage: {memory_info}")
    
    print("Advanced diffusion system with gradient accumulation ready!")

