#!/usr/bin/env python3
"""
Diffusion Models System

Comprehensive implementation of diffusion models including:
- DDPM (Denoising Diffusion Probabilistic Models)
- DDIM (Denoising Diffusion Implicit Models)
- Advanced sampling techniques
- Custom noise schedulers
- Efficient training and inference
- Proper autograd integration with PyTorch
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
from dataclasses import dataclass
import math
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt


@dataclass
class DiffusionConfig:
    """Configuration for diffusion models.
    
    Attributes:
        num_timesteps: Number of diffusion timesteps
        beta_start: Starting noise schedule value
        beta_end: Ending noise schedule value
        image_size: Size of input images
        in_channels: Number of input channels
        model_channels: Number of model channels
        num_res_blocks: Number of residual blocks
        attention_resolutions: Attention resolution levels
        dropout: Dropout probability
        learning_rate: Learning rate
        batch_size: Training batch size
        num_epochs: Number of training epochs
        use_ema: Whether to use exponential moving average
        ema_decay: EMA decay rate
    """
    
    num_timesteps: int = 1000
    beta_start: float = 1e-4
    beta_end: float = 0.02
    image_size: int = 32
    in_channels: int = 3
    model_channels: int = 128
    num_res_blocks: int = 2
    attention_resolutions: Tuple[int, ...] = (16,)
    dropout: float = 0.1
    learning_rate: float = 1e-4
    batch_size: int = 32
    num_epochs: int = 100
    use_ema: bool = True
    ema_decay: float = 0.9999


class NoiseScheduler(ABC):
    """Abstract base class for noise schedulers.
    
    This class defines the interface for different noise scheduling
    strategies in diffusion models.
    """
    
    @abstractmethod
    def get_noise_schedule(self, num_timesteps: int) -> torch.Tensor:
        """Get noise schedule for given number of timesteps.
        
        Args:
            num_timesteps: Number of diffusion timesteps
            
        Returns:
            Noise schedule tensor
        """
        pass
    
    @abstractmethod
    def get_alpha_bars(self, num_timesteps: int) -> torch.Tensor:
        """Get cumulative alpha values.
        
        Args:
            num_timesteps: Number of diffusion timesteps
            
        Returns:
            Cumulative alpha values
        """
        pass


class LinearNoiseScheduler(NoiseScheduler):
    """Linear noise scheduler for DDPM.
    
    This scheduler implements the linear noise schedule used
    in the original DDPM paper.
    """
    
    def __init__(self, beta_start: float = 1e-4, beta_end: float = 0.02):
        """Initialize linear noise scheduler.
        
        Args:
            beta_start: Starting noise value
            beta_end: Ending noise value
        """
        self.beta_start = beta_start
        self.beta_end = beta_end
    
    def get_noise_schedule(self, num_timesteps: int) -> torch.Tensor:
        """Get linear noise schedule.
        
        Args:
            num_timesteps: Number of diffusion timesteps
            
        Returns:
            Linear noise schedule
        """
        return torch.linspace(self.beta_start, self.beta_end, num_timesteps)
    
    def get_alpha_bars(self, num_timesteps: int) -> torch.Tensor:
        """Get cumulative alpha values for linear schedule.
        
        Args:
            num_timesteps: Number of diffusion timesteps
            
        Returns:
            Cumulative alpha values
        """
        betas = self.get_noise_schedule(num_timesteps)
        alphas = 1.0 - betas
        alpha_bars = torch.cumprod(alphas, dim=0)
        return alpha_bars


class CosineNoiseScheduler(NoiseScheduler):
    """Cosine noise scheduler for improved diffusion.
    
    This scheduler implements the cosine noise schedule that
    provides better results than linear scheduling.
    """
    
    def __init__(self, s: float = 0.008):
        """Initialize cosine noise scheduler.
        
        Args:
            s: Small constant for numerical stability
        """
        self.s = s
    
    def get_noise_schedule(self, num_timesteps: int) -> torch.Tensor:
        """Get cosine noise schedule.
        
        Args:
            num_timesteps: Number of diffusion timesteps
            
        Returns:
            Cosine noise schedule
        """
        t = torch.arange(num_timesteps + 1) / num_timesteps
        alpha_bars = torch.cos((t + self.s) / (1 + self.s) * math.pi * 0.5) ** 2
        alpha_bars = alpha_bars / alpha_bars[0]
        betas = 1 - alpha_bars[1:] / alpha_bars[:-1]
        return torch.clamp(betas, 0.0001, 0.9999)
    
    def get_alpha_bars(self, num_timesteps: int) -> torch.Tensor:
        """Get cumulative alpha values for cosine schedule.
        
        Args:
            num_timesteps: Number of diffusion timesteps
            
        Returns:
            Cumulative alpha values
        """
        t = torch.arange(num_timesteps + 1) / num_timesteps
        alpha_bars = torch.cos((t + self.s) / (1 + self.s) * math.pi * 0.5) ** 2
        alpha_bars = alpha_bars / alpha_bars[0]
        return alpha_bars


class ResidualBlock(nn.Module):
    """Residual block for U-Net architecture.
    
    This module implements a residual block with proper
    normalization and activation functions.
    """
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        dropout: float = 0.1,
        use_attention: bool = False
    ):
        """Initialize residual block.
        
        Args:
            in_channels: Number of input channels
            out_channels: Number of output channels
            dropout: Dropout probability
            use_attention: Whether to use self-attention
        """
        super().__init__()
        
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        # Main path
        self.norm1 = nn.GroupNorm(32, in_channels)
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.norm2 = nn.GroupNorm(32, out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1)
        self.dropout = nn.Dropout(dropout)
        
        # Shortcut connection
        if in_channels != out_channels:
            self.shortcut = nn.Conv2d(in_channels, out_channels, 1)
        else:
            self.shortcut = nn.Identity()
        
        # Self-attention
        self.use_attention = use_attention
        if use_attention:
            self.attention = SelfAttention(out_channels)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with residual connection.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor
        """
        residual = self.shortcut(x)
        
        # Main path
        x = F.silu(self.norm1(x))
        x = self.conv1(x)
        x = F.silu(self.norm2(x))
        x = self.dropout(x)
        x = self.conv2(x)
        
        # Add residual
        x = x + residual
        
        # Self-attention
        if self.use_attention:
            x = self.attention(x)
        
        return x


class SelfAttention(nn.Module):
    """Self-attention module for spatial dimensions.
    
    This module implements self-attention over spatial
    dimensions for better feature modeling.
    """
    
    def __init__(self, channels: int):
        """Initialize self-attention.
        
        Args:
            channels: Number of channels
        """
        super().__init__()
        
        self.channels = channels
        self.mha = nn.MultiheadAttention(channels, 4, batch_first=True)
        self.norm = nn.GroupNorm(32, channels)
        self.proj = nn.Conv2d(channels, channels, 1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with self-attention.
        
        Args:
            x: Input tensor (batch, channels, height, width)
            
        Returns:
            Output tensor
        """
        batch, channels, height, width = x.shape
        
        # Reshape for attention
        x_flat = x.view(batch, channels, -1).transpose(1, 2)
        
        # Apply attention
        attn_out, _ = self.mha(x_flat, x_flat, x_flat)
        
        # Reshape back
        attn_out = attn_out.transpose(1, 2).view(batch, channels, height, width)
        
        # Project and add residual
        x = x + self.proj(self.norm(attn_out))
        
        return x


class TimeEmbedding(nn.Module):
    """Time embedding for diffusion models.
    
    This module creates embeddings for timesteps that
    can be used to condition the diffusion process.
    """
    
    def __init__(self, dim: int):
        """Initialize time embedding.
        
        Args:
            dim: Embedding dimension
        """
        super().__init__()
        
        self.dim = dim
        self.projection = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.SiLU(),
            nn.Linear(dim * 4, dim)
        )
    
    def forward(self, t: torch.Tensor) -> torch.Tensor:
        """Forward pass for time embedding.
        
        Args:
            t: Timestep tensor
            
        Returns:
            Time embedding
        """
        half_dim = self.dim // 2
        embeddings = math.log(10000) / (half_dim - 1)
        embeddings = torch.exp(torch.arange(half_dim, device=t.device) * -embeddings)
        embeddings = t[:, None] * embeddings[None, :]
        embeddings = torch.cat((embeddings.sin(), embeddings.cos()), dim=-1)
        embeddings = self.projection(embeddings)
        return embeddings


class UNet(nn.Module):
    """U-Net architecture for diffusion models.
    
    This module implements a U-Net architecture specifically
    designed for diffusion models with time conditioning.
    """
    
    def __init__(self, config: DiffusionConfig):
        """Initialize U-Net.
        
        Args:
            config: Diffusion configuration
        """
        super().__init__()
        
        self.config = config
        self.image_size = config.image_size
        self.in_channels = config.in_channels
        self.model_channels = config.model_channels
        
        # Time embedding
        self.time_embedding = TimeEmbedding(config.model_channels)
        
        # Initial convolution
        self.input_blocks = nn.ModuleList([
            nn.Conv2d(config.in_channels, config.model_channels, 3, padding=1)
        ])
        
        # Downsampling path
        input_block_chans = [config.model_channels]
        ch = config.model_channels
        ds = 1
        
        for level, mult in enumerate([1, 2, 4, 8]):
            for _ in range(config.num_res_blocks):
                layers = [
                    ResidualBlock(
                        ch,
                        mult * config.model_channels,
                        config.dropout,
                        use_attention=ds in config.attention_resolutions
                    )
                ]
                ch = mult * config.model_channels
                if ds in config.attention_resolutions:
                    layers.append(SelfAttention(ch))
                self.input_blocks.append(nn.ModuleList(layers))
                input_block_chans.append(ch)
            
            if level != 3:  # No downsampling at the last level
                self.input_blocks.append(
                    nn.ModuleList([ResidualBlock(ch, ch, config.dropout)])
                )
                input_block_chans.append(ch)
                ds *= 2
        
        # Middle block
        self.middle_block = nn.ModuleList([
            ResidualBlock(ch, ch, config.dropout, use_attention=True),
            ResidualBlock(ch, ch, config.dropout)
        ])
        
        # Upsampling path
        self.output_blocks = nn.ModuleList([])
        for level, mult in enumerate([8, 4, 2, 1]):
            for i in range(config.num_res_blocks + 1):
                ich = input_block_chans.pop()
                layers = [
                    ResidualBlock(
                        ch + ich,
                        mult * config.model_channels,
                        config.dropout,
                        use_attention=ds in config.attention_resolutions
                    )
                ]
                ch = mult * config.model_channels
                if ds in config.attention_resolutions:
                    layers.append(SelfAttention(ch))
                if level and i == config.num_res_blocks:
                    layers.append(nn.Upsample(scale_factor=2, mode="nearest"))
                    ds //= 2
                self.output_blocks.append(nn.ModuleList(layers))
        
        # Output projection
        self.out = nn.Sequential(
            nn.GroupNorm(32, ch),
            nn.SiLU(),
            nn.Conv2d(ch, config.in_channels, 3, padding=1)
        )
    
    def forward(
        self,
        x: torch.Tensor,
        timesteps: torch.Tensor
    ) -> torch.Tensor:
        """Forward pass through U-Net.
        
        Args:
            x: Input tensor (batch, channels, height, width)
            timesteps: Timestep tensor (batch,)
            
        Returns:
            Predicted noise
        """
        # Time embedding
        temb = self.time_embedding(timesteps)
        
        # Initial convolution
        hs = []
        h = self.input_blocks[0](x)
        hs.append(h)
        
        # Downsampling path
        for module in self.input_blocks[1:]:
            if isinstance(module, nn.ModuleList):
                for layer in module:
                    if isinstance(layer, ResidualBlock):
                        h = layer(h)
                    elif isinstance(layer, SelfAttention):
                        h = layer(h)
            else:
                h = module(h)
            hs.append(h)
        
        # Middle block
        for module in self.middle_block:
            if isinstance(module, ResidualBlock):
                h = module(h)
            elif isinstance(module, SelfAttention):
                h = module(h)
        
        # Upsampling path
        for module in self.output_blocks:
            if isinstance(module, nn.ModuleList):
                for layer in module:
                    if isinstance(layer, ResidualBlock):
                        h = torch.cat([h, hs.pop()], dim=1)
                        h = layer(h)
                    elif isinstance(layer, SelfAttention):
                        h = layer(h)
                    elif isinstance(layer, nn.Upsample):
                        h = layer(h)
        
        # Output projection
        return self.out(h)


class DiffusionModel:
    """Complete diffusion model implementation.
    
    This class implements the full diffusion process including
    training, sampling, and various inference techniques.
    """
    
    def __init__(self, config: DiffusionConfig):
        """Initialize diffusion model.
        
        Args:
            config: Diffusion configuration
        """
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize noise scheduler
        self.noise_scheduler = CosineNoiseScheduler()
        self.betas = self.noise_scheduler.get_noise_schedule(config.num_timesteps)
        self.alphas = 1.0 - self.betas
        self.alpha_bars = torch.cumprod(self.alphas, dim=0)
        
        # Move to device
        self.betas = self.betas.to(self.device)
        self.alphas = self.alphas.to(self.device)
        self.alpha_bars = self.alpha_bars.to(self.device)
        
        # Initialize U-Net
        self.model = UNet(config).to(self.device)
        
        # EMA model for inference
        if config.use_ema:
            self.ema_model = UNet(config).to(self.device)
            self.ema_model.load_state_dict(self.model.state_dict())
            self.ema_decay = config.ema_decay
        
        logging.info(f"Diffusion model initialized on device: {self.device}")
    
    def q_sample(
        self,
        x_start: torch.Tensor,
        t: torch.Tensor,
        noise: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward diffusion process (q(x_t | x_0)).
        
        Args:
            x_start: Starting image
            t: Timestep
            noise: Optional noise to use
            
        Returns:
            Tuple of (noisy image, noise)
        """
        if noise is None:
            noise = torch.randn_like(x_start)
        
        # Get alpha_bar for timestep t
        alpha_bar_t = self.alpha_bars[t].view(-1, 1, 1, 1)
        
        # Add noise
        noisy_image = torch.sqrt(alpha_bar_t) * x_start + torch.sqrt(1 - alpha_bar_t) * noise
        
        return noisy_image, noise
    
    def p_losses(
        self,
        x_start: torch.Tensor,
        t: torch.Tensor,
        noise: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Compute loss for training.
        
        Args:
            x_start: Starting image
            t: Timestep
            noise: Optional noise to use
            
        Returns:
            Loss value
        """
        if noise is None:
            noise = torch.randn_like(x_start)
        
        # Forward diffusion
        x_noisy, target = self.q_sample(x_start, t, noise)
        
        # Predict noise
        predicted = self.model(x_noisy, t)
        
        # Compute loss
        loss = F.mse_loss(predicted, target, reduction="mean")
        
        return loss
    
    def p_sample(
        self,
        x: torch.Tensor,
        t: torch.Tensor,
        t_index: int,
        use_ema: bool = True
    ) -> torch.Tensor:
        """Single denoising step (p(x_{t-1} | x_t)).
        
        Args:
            x: Current noisy image
            t: Current timestep
            t_index: Timestep index
            use_ema: Whether to use EMA model
            
        Returns:
            Denoised image
        """
        model = self.ema_model if use_ema and self.config.use_ema else self.model
        
        # Predict noise
        predicted_noise = model(x, t)
        
        # Get alpha values
        alpha_t = self.alphas[t_index]
        alpha_bar_t = self.alpha_bars[t_index]
        beta_t = self.betas[t_index]
        
        if t_index > 0:
            noise = torch.randn_like(x)
        else:
            noise = torch.zeros_like(x)
        
        # Denoising step
        x_prev = (1 / torch.sqrt(alpha_t)) * (
            x - ((1 - alpha_t) / torch.sqrt(1 - alpha_bar_t)) * predicted_noise
        ) + torch.sqrt(beta_t) * noise
        
        return x_prev
    
    def p_sample_loop(
        self,
        shape: Tuple[int, ...],
        use_ema: bool = True
    ) -> torch.Tensor:
        """Complete sampling loop.
        
        Args:
            shape: Shape of image to generate
            use_ema: Whether to use EMA model
            
        Returns:
            Generated image
        """
        batch_size = shape[0]
        x = torch.randn(shape, device=self.device)
        
        for i in reversed(range(0, self.config.num_timesteps)):
            t = torch.full((batch_size,), i, device=self.device, dtype=torch.long)
            x = self.p_sample(x, t, i, use_ema)
        
        return x
    
    def sample(
        self,
        batch_size: int = 1,
        use_ema: bool = True
    ) -> torch.Tensor:
        """Generate samples.
        
        Args:
            batch_size: Number of samples to generate
            use_ema: Whether to use EMA model
            
        Returns:
            Generated samples
        """
        shape = (batch_size, self.config.in_channels, self.config.image_size, self.config.image_size)
        return self.p_sample_loop(shape, use_ema)
    
    def update_ema(self) -> None:
        """Update EMA model."""
        if self.config.use_ema:
            with torch.no_grad():
                for param, ema_param in zip(self.model.parameters(), self.ema_model.parameters()):
                    ema_param.data.mul_(self.ema_decay).add_(param.data, alpha=1 - self.ema_decay)
    
    def train_step(
        self,
        batch: torch.Tensor,
        optimizer: torch.optim.Optimizer
    ) -> float:
        """Single training step.
        
        Args:
            batch: Training batch
            optimizer: Optimizer
            
        Returns:
            Loss value
        """
        batch = batch.to(self.device)
        batch_size = batch.shape[0]
        
        # Sample random timesteps
        t = torch.randint(0, self.config.num_timesteps, (batch_size,), device=self.device)
        
        # Compute loss
        loss = self.p_losses(batch, t)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Update EMA
        self.update_ema()
        
        return loss.item()


def demonstrate_diffusion():
    """Demonstrate diffusion model capabilities."""
    logging.info("Demonstrating Diffusion Models System...")
    
    # Initialize configuration
    config = DiffusionConfig(
        num_timesteps=100,  # Reduced for demonstration
        image_size=32,
        batch_size=4,
        num_epochs=10
    )
    
    # Create diffusion model
    diffusion = DiffusionModel(config)
    
    # Create sample data
    sample_data = torch.randn(config.batch_size, config.in_channels, config.image_size, config.image_size)
    
    # Demonstrate training step
    optimizer = torch.optim.AdamW(diffusion.model.parameters(), lr=config.learning_rate)
    loss = diffusion.train_step(sample_data, optimizer)
    logging.info(f"Training loss: {loss:.4f}")
    
    # Demonstrate sampling
    samples = diffusion.sample(batch_size=2)
    logging.info(f"Generated samples shape: {samples.shape}")
    
    logging.info("Diffusion models demonstration completed!")


if __name__ == "__main__":
    demonstrate_diffusion() 