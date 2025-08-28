# DIFFUSION MODELS SYSTEM
# ============================================================================
# COMPREHENSIVE DIFFUSION MODELS IMPLEMENTATION USING DIFFUSERS LIBRARY
# ============================================================================

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import pickle
import os
from tqdm import tqdm
import warnings

# Try to import diffusers components
try:
    from diffusers import (
        DiffusionPipeline, StableDiffusionPipeline, StableDiffusionXLPipeline,
        DDIMScheduler, DDPMScheduler, EulerDiscreteScheduler, 
        EulerAncestralDiscreteScheduler, HeunDiscreteScheduler,
        DPMSolverMultistepScheduler, DPMSolverSinglestepScheduler,
        UNet2DConditionModel, AutoencoderKL, Transformer2DModel,
        ControlNetModel, MultiControlNetModel
    )
    from diffusers.utils import randn_tensor, logging
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    warnings.warn("Diffusers library not available. Some features will be limited.")

# Try to import transformers
try:
    from transformers import CLIPTextModel, CLIPTokenizer, CLIPTextConfig
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    warnings.warn("Transformers library not available. Some features will be limited.")

# ============================================================================
# DIFFUSION CONFIGURATION AND UTILITIES
# ============================================================================

@dataclass
class DiffusionConfig:
    """Configuration for diffusion models."""
    
    # Model parameters
    image_size: int = 64
    in_channels: int = 3
    out_channels: int = 3
    model_channels: int = 128
    num_res_blocks: int = 2
    attention_resolutions: Tuple[int, ...] = (8, 16)
    dropout: float = 0.1
    channel_mult: Tuple[int, ...] = (1, 2, 4, 8)
    conv_resample: bool = True
    num_heads: int = 4
    use_spatial_transformer: bool = True
    transformer_depth: int = 1
    context_dim: Optional[int] = None
    num_classes: Optional[int] = None
    
    # Diffusion parameters
    beta_start: float = 0.0001
    beta_end: float = 0.02
    num_diffusion_timesteps: int = 1000
    beta_schedule: str = "linear"  # linear, cosine, sigmoid
    loss_type: str = "l2"  # l2, l1, huber
    
    # Training parameters
    learning_rate: float = 1e-4
    batch_size: int = 16
    num_epochs: int = 100
    gradient_clip_val: float = 1.0
    use_amp: bool = True
    
    # Sampling parameters
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    eta: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {k: v for k, v in self.__dict__.items()}
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DiffusionConfig':
        """Create config from dictionary."""
        return cls(**config_dict)
    
    def save(self, path: str):
        """Save config to file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'DiffusionConfig':
        """Load config from file."""
        with open(path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

class BetaSchedule:
    """Beta schedule implementations for diffusion models."""
    
    @staticmethod
    def linear(beta_start: float, beta_end: float, num_timesteps: int) -> torch.Tensor:
        """Linear beta schedule."""
        return torch.linspace(beta_start, beta_end, num_timesteps)
    
    @staticmethod
    def cosine(beta_start: float, beta_end: float, num_timesteps: int) -> torch.Tensor:
        """Cosine beta schedule."""
        steps = num_timesteps + 1
        x = torch.linspace(0, num_timesteps, steps)
        alphas_cumprod = torch.cos(((x / num_timesteps) + 0.008) / 1.008 * torch.pi * 0.5) ** 2
        alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
        betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
        return torch.clip(betas, 0.0001, 0.9999)
    
    @staticmethod
    def sigmoid(beta_start: float, beta_end: float, num_timesteps: int) -> torch.Tensor:
        """Sigmoid beta schedule."""
        betas = torch.linspace(-6, 6, num_timesteps)
        betas = torch.sigmoid(betas) * (beta_end - beta_start) + beta_start
        return betas

# ============================================================================
# CUSTOM DIFFUSION SCHEDULER
# ============================================================================

class CustomDiffusionScheduler:
    """Custom diffusion scheduler with forward and reverse processes."""
    
    def __init__(self, config: DiffusionConfig):
        self.config = config
        self.num_timesteps = config.num_diffusion_timesteps
        self.beta_start = config.beta_start
        self.beta_end = config.beta_end
        self.beta_schedule = config.beta_schedule
        
        # Initialize beta schedule
        if self.beta_schedule == "linear":
            self.betas = BetaSchedule.linear(self.beta_start, self.beta_end, self.num_timesteps)
        elif self.beta_schedule == "cosine":
            self.betas = BetaSchedule.cosine(self.beta_start, self.beta_end, self.num_timesteps)
        elif self.beta_schedule == "sigmoid":
            self.betas = BetaSchedule.sigmoid(self.beta_start, self.beta_end, self.num_timesteps)
        else:
            raise ValueError(f"Unknown beta schedule: {self.beta_schedule}")
        
        # Pre-compute values
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.alphas_cumprod_prev = F.pad(self.alphas_cumprod[:-1], (1, 0), value=1.0)
        
        # Calculations for diffusion q(x_t | x_{t-1}) and others
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - self.alphas_cumprod)
        self.log_one_minus_alphas_cumprod = torch.log(1.0 - self.alphas_cumprod)
        self.sqrt_recip_alphas_cumprod = torch.sqrt(1.0 / self.alphas_cumprod)
        self.sqrt_recipm1_alphas_cumprod = torch.sqrt(1.0 / self.alphas_cumprod - 1)
        
        # Calculations for posterior q(x_{t-1} | x_t, x_0)
        self.posterior_variance = (
            self.betas * (1.0 - self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)
        )
        self.posterior_log_variance_clipped = torch.log(
            torch.cat([self.posterior_variance[1:2], self.posterior_variance[1:]])
        )
        self.posterior_mean_coef1 = (
            self.betas * torch.sqrt(self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)
        )
        self.posterior_mean_coef2 = (
            (1.0 - self.alphas_cumprod_prev) * torch.sqrt(self.alphas) / (1.0 - self.alphas_cumprod)
        )
    
    def add_noise(self, original_samples: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        """Add noise to samples according to timesteps (forward process)."""
        sqrt_alpha = self.sqrt_alphas_cumprod[timesteps].reshape(-1, 1, 1, 1)
        sqrt_one_minus_alpha = self.sqrt_one_minus_alphas_cumprod[timesteps].reshape(-1, 1, 1, 1)
        
        noise = torch.randn_like(original_samples)
        noisy_samples = sqrt_alpha * original_samples + sqrt_one_minus_alpha * noise
        
        return noisy_samples, noise
    
    def step(self, model_output: torch.Tensor, timestep: int, sample: torch.Tensor,
             eta: float = 0.0, use_clipped_model_output: bool = False) -> torch.Tensor:
        """Reverse diffusion step."""
        if timestep == 0:
            return sample
        
        # Get current timestep
        t = timestep
        prev_t = t - 1
        
        # Get model output
        if use_clipped_model_output:
            model_output = torch.clamp(model_output, -1, 1)
        
        # Predict x_0
        pred_original_sample = (
            sample - self.sqrt_one_minus_alphas_cumprod[t] * model_output
        ) / self.sqrt_alphas_cumprod[t]
        
        # Clip prediction
        pred_original_sample = torch.clamp(pred_original_sample, -1, 1)
        
        # Calculate q(x_{t-1} | x_t, x_0)
        pred_sample_direction = (
            (1 - self.alphas_cumprod_prev[prev_t]) / (1 - self.alphas_cumprod[t])
        ) ** 0.5 * model_output
        
        # Add noise if eta > 0
        if eta > 0:
            noise = torch.randn_like(sample)
            pred_sample_direction += eta * self.sqrt_one_minus_alphas_cumprod[prev_t] * noise
        
        # Calculate x_{t-1}
        pred_prev_sample = (
            self.sqrt_alphas_cumprod_prev[prev_t] * pred_original_sample +
            pred_sample_direction
        )
        
        return pred_prev_sample
    
    def set_timesteps(self, num_inference_steps: int):
        """Set the number of inference steps."""
        self.num_inference_steps = num_inference_steps
        step_ratio = self.num_timesteps // num_inference_steps
        timesteps = (torch.arange(0, num_inference_steps) * step_ratio).flip(0)
        self.timesteps = timesteps

# ============================================================================
# CUSTOM UNET ARCHITECTURE
# ============================================================================

class ResBlock(nn.Module):
    """Residual block for UNet."""
    
    def __init__(self, channels: int, dropout: float = 0.1):
        super().__init__()
        self.channels = channels
        self.dropout = dropout
        
        self.norm1 = nn.GroupNorm(32, channels)
        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
        self.norm2 = nn.GroupNorm(32, channels)
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)
        self.dropout_layer = nn.Dropout(dropout)
        
        # No shortcut needed for same channel dimensions
        self.shortcut = nn.Identity()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = x
        h = self.norm1(h)
        h = F.silu(h)
        h = self.conv1(h)
        h = self.norm2(h)
        h = F.silu(h)
        h = self.dropout_layer(h)
        h = self.conv2(h)
        return self.shortcut(x) + h

class CrossAttention(nn.Module):
    """Cross attention module."""
    
    def __init__(self, query_dim: int, context_dim: Optional[int] = None, heads: int = 8, dim_head: int = 64):
        super().__init__()
        inner_dim = dim_head * heads
        context_dim = context_dim if context_dim is not None else query_dim
        
        self.scale = dim_head ** -0.5
        self.heads = heads
        
        self.to_q = nn.Linear(query_dim, inner_dim, bias=False)
        self.to_k = nn.Linear(context_dim, inner_dim, bias=False)
        self.to_v = nn.Linear(context_dim, inner_dim, bias=False)
        self.to_out = nn.Linear(inner_dim, query_dim)
    
    def forward(self, x: torch.Tensor, context: Optional[torch.Tensor] = None) -> torch.Tensor:
        h = self.heads
        
        q = self.to_q(x)
        context = context if context is not None else x
        k = self.to_k(context)
        v = self.to_v(context)
        
        q, k, v = map(lambda t: t.reshape(*t.shape[:2], h, -1).transpose(1, 2), (q, k, v))
        
        sim = torch.einsum('b h i d, b h j d -> b h i j', q, k) * self.scale
        attn = sim.softmax(dim=-1)
        
        out = torch.einsum('b h i j, b h j d -> b h i d', attn, v)
        out = out.transpose(1, 2).reshape(*out.shape[:2], -1)
        return self.to_out(out)

class SpatialTransformer(nn.Module):
    """Spatial transformer for UNet."""
    
    def __init__(self, in_channels: int, n_heads: int, d_head: int, depth: int = 1, context_dim: Optional[int] = None):
        super().__init__()
        self.in_channels = in_channels
        inner_dim = n_heads * d_head
        self.norm = nn.GroupNorm(32, in_channels)
        
        self.proj_in = nn.Conv2d(in_channels, inner_dim, kernel_size=1, stride=1, padding=0)
        
        self.transformer_blocks = nn.ModuleList([
            CrossAttention(inner_dim, context_dim, n_heads, d_head)
            for _ in range(depth)
        ])
        
        self.proj_out = nn.Conv2d(inner_dim, in_channels, kernel_size=1, stride=1, padding=0)
    
    def forward(self, x: torch.Tensor, context: Optional[torch.Tensor] = None) -> torch.Tensor:
        b, c, h, w = x.shape
        x_in = x
        
        x = self.norm(x)
        x = self.proj_in(x)
        x = x.reshape(b, c, h * w).transpose(1, 2)  # (b, h*w, c)
        
        for block in self.transformer_blocks:
            x = block(x, context)
        
        x = x.transpose(1, 2).reshape(b, c, h, w)
        x = self.proj_out(x)
        return x + x_in

class UNetBlock(nn.Module):
    """UNet block with residual connections."""
    
    def __init__(self, in_channels: int, out_channels: int, dropout: float = 0.1,
                 use_attention: bool = True, attention_heads: int = 8, context_dim: Optional[int] = None):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        # Downsampling
        self.down = nn.Conv2d(in_channels, out_channels, 4, 2, 1)
        
        # Residual blocks
        self.res1 = ResBlock(out_channels, dropout)
        self.res2 = ResBlock(out_channels, dropout)
        
        # Attention
        if use_attention:
            self.attn = SpatialTransformer(out_channels, attention_heads, out_channels // attention_heads, 
                                         context_dim=context_dim)
        else:
            self.attn = None
    
    def forward(self, x: torch.Tensor, context: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = self.down(x)
        x = self.res1(x)
        x = self.res2(x)
        if self.attn is not None:
            x = self.attn(x, context)
        return x

class UNetUpBlock(nn.Module):
    """UNet upsampling block."""
    
    def __init__(self, in_channels: int, out_channels: int, dropout: float = 0.1,
                 use_attention: bool = True, attention_heads: int = 8, context_dim: Optional[int] = None):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        # Upsampling
        self.up = nn.ConvTranspose2d(in_channels, out_channels, 4, 2, 1)
        
        # Residual blocks
        self.res1 = ResBlock(out_channels, dropout)
        self.res2 = ResBlock(out_channels, dropout)
        
        # Attention
        if use_attention:
            self.attn = SpatialTransformer(out_channels, attention_heads, out_channels // attention_heads,
                                         context_dim=context_dim)
        else:
            self.attn = None
    
    def forward(self, x: torch.Tensor, context: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = self.up(x)
        x = self.res1(x)
        x = self.res2(x)
        if self.attn is not None:
            x = self.attn(x, context)
        return x

class CustomUNet(nn.Module):
    """Custom UNet architecture for diffusion models."""
    
    def __init__(self, config: DiffusionConfig):
        super().__init__()
        self.config = config
        
        # Initial convolution
        self.conv_in = nn.Conv2d(config.in_channels, config.model_channels, 3, padding=1)
        
        # Time embedding
        time_embed_dim = config.model_channels * 4
        self.time_embed = nn.Sequential(
            nn.Linear(config.model_channels, time_embed_dim),
            nn.SiLU(),
            nn.Linear(time_embed_dim, time_embed_dim),
        )
        
        # Downsampling blocks
        self.down_blocks = nn.ModuleList()
        ch = config.model_channels
        input_block_chans = [ch]
        
        for level, mult in enumerate(config.channel_mult):
            for _ in range(config.num_res_blocks):
                layers = [
                    ResBlock(ch, config.dropout),
                    ResBlock(ch, config.dropout),
                ]
                if config.use_spatial_transformer and ch in config.attention_resolutions:
                    layers.append(
                        SpatialTransformer(ch, config.num_heads, ch // config.num_heads,
                                        config.transformer_depth, config.context_dim)
                    )
                self.down_blocks.append(nn.ModuleList(layers))
                input_block_chans.append(ch)
            
            if level != len(config.channel_mult) - 1:
                ch = mult * config.model_channels
                self.down_blocks.append(
                    UNetBlock(input_block_chans[-1], ch, config.dropout, 
                             ch in config.attention_resolutions, config.num_heads, config.context_dim)
                )
                input_block_chans.append(ch)
            else:
                ch = mult * config.model_channels
        
        # Middle block
        self.middle_block = nn.ModuleList([
            ResBlock(ch, config.dropout),
            SpatialTransformer(ch, config.num_heads, ch // config.num_heads,
                            config.transformer_depth, config.context_dim) if config.use_spatial_transformer else nn.Identity(),
            ResBlock(ch, config.dropout),
        ])
        
        # Upsampling blocks
        self.up_blocks = nn.ModuleList()
        for level, mult in list(enumerate(config.channel_mult))[::-1]:
            for i in range(config.num_res_blocks + 1):
                # Get input channels for skip connections
                skip_ch = input_block_chans.pop() if input_block_chans else ch
                layers = [
                    ResBlock(skip_ch + ch, config.dropout),
                    ResBlock(skip_ch + ch, config.dropout),
                ]
                if config.use_spatial_transformer and ch in config.attention_resolutions:
                    layers.append(
                        SpatialTransformer(ch, config.num_heads, ch // config.num_heads,
                                        config.transformer_depth, config.context_dim)
                    )
                if level and i == config.num_res_blocks:
                    layers.append(
                        UNetUpBlock(ch, ch, config.dropout,
                                  ch in config.attention_resolutions, config.num_heads, config.context_dim)
                    )
                self.up_blocks.append(nn.ModuleList(layers))
            
            # Update channel count for next level
            if level > 0:
                ch = config.channel_mult[level - 1] * config.model_channels
        
        # Final layers
        self.norm_out = nn.GroupNorm(32, ch)
        self.conv_out = nn.Conv2d(ch, config.out_channels, 3, padding=1)
    
    def forward(self, x: torch.Tensor, timesteps: torch.Tensor, 
                context: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Time embedding
        t_emb = timesteps.float()
        t_emb = t_emb.unsqueeze(-1).expand(-1, self.config.model_channels)
        t_emb = self.time_embed(t_emb)
        t_emb = t_emb.unsqueeze(-1).unsqueeze(-1)
        
        # Initial convolution
        h = self.conv_in(x)
        # Add time embedding to spatial dimensions (only first model_channels)
        t_emb_spatial = t_emb[:, :self.config.model_channels, :, :].expand(-1, -1, h.shape[2], h.shape[3])
        h = h + t_emb_spatial
        
        # Downsampling
        hs = []
        for block in self.down_blocks:
            if isinstance(block, UNetBlock):
                h = block(h, context)
            else:
                for layer in block:
                    if isinstance(layer, SpatialTransformer):
                        h = layer(h, context)
                    else:
                        h = layer(h)
            hs.append(h)
        
        # Middle block
        for layer in self.middle_block:
            if isinstance(layer, SpatialTransformer):
                h = layer(h, context)
            else:
                h = layer(h)
        
        # Upsampling
        for block in self.up_blocks:
            h = torch.cat([h, hs.pop()], dim=1)
            for layer in block:
                if isinstance(layer, SpatialTransformer):
                    h = layer(h, context)
                elif isinstance(layer, UNetUpBlock):
                    h = layer(h, context)
                else:
                    h = layer(h)
        
        # Final layers
        h = self.norm_out(h)
        h = F.silu(h)
        h = self.conv_out(h)
        
        return h

# ============================================================================
# ADVANCED DIFFUSION MODEL
# ============================================================================

class AdvancedDiffusionModel:
    """Advanced diffusion model combining custom UNet and scheduler."""
    
    def __init__(self, config: DiffusionConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize components
        self.unet = CustomUNet(config).to(self.device)
        self.scheduler = CustomDiffusionScheduler(config)
        
        # Text conditioning (if available)
        if TRANSFORMERS_AVAILABLE and config.context_dim is not None:
            self.text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-base-patch32")
            self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
            self.text_encoder.to(self.device)
        else:
            self.text_encoder = None
            self.tokenizer = None
        
        # Training components
        self.optimizer = optim.AdamW(self.unet.parameters(), lr=config.learning_rate)
        self.scaler = torch.cuda.amp.GradScaler() if config.use_amp else None
    
    def encode_text(self, text: str) -> torch.Tensor:
        """Encode text to embeddings."""
        if self.text_encoder is None or self.tokenizer is None:
            return None
        
        tokens = self.tokenizer(text, padding=True, return_tensors="pt").to(self.device)
        with torch.no_grad():
            text_embeddings = self.text_encoder(**tokens).last_hidden_state
        return text_embeddings
    
    def train_step(self, batch: torch.Tensor, text: Optional[str] = None) -> Dict[str, float]:
        """Single training step."""
        batch = batch.to(self.device)
        batch_size = batch.shape[0]
        
        # Sample random timesteps
        timesteps = torch.randint(0, self.config.num_diffusion_timesteps, (batch_size,), device=self.device)
        
        # Add noise
        noisy_batch, noise = self.scheduler.add_noise(batch, timesteps)
        
        # Encode text if provided
        context = None
        if text is not None and self.text_encoder is not None:
            context = self.encode_text(text)
        
        # Predict noise
        with torch.cuda.amp.autocast() if self.config.use_amp else torch.no_grad():
            noise_pred = self.unet(noisy_batch, timesteps, context)
        
        # Calculate loss
        if self.config.loss_type == "l2":
            loss = F.mse_loss(noise_pred, noise)
        elif self.config.loss_type == "l1":
            loss = F.l1_loss(noise_pred, noise)
        elif self.config.loss_type == "huber":
            loss = F.smooth_l1_loss(noise_pred, noise)
        else:
            raise ValueError(f"Unknown loss type: {self.config.loss_type}")
        
        # Backward pass
        self.optimizer.zero_grad()
        if self.config.use_amp:
            self.scaler.scale(loss).backward()
            self.scaler.unscale_(self.optimizer)
            torch.nn.utils.clip_grad_norm_(self.unet.parameters(), self.config.gradient_clip_val)
            self.scaler.step(self.optimizer)
            self.scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.unet.parameters(), self.config.gradient_clip_val)
            self.optimizer.step()
        
        return {"loss": loss.item()}
    
    def sample(self, batch_size: int = 1, text: Optional[str] = None, 
               num_inference_steps: int = None, guidance_scale: float = None) -> torch.Tensor:
        """Generate samples using the diffusion model."""
        if num_inference_steps is None:
            num_inference_steps = self.config.num_inference_steps
        if guidance_scale is None:
            guidance_scale = self.config.guidance_scale
        
        # Set timesteps
        self.scheduler.set_timesteps(num_inference_steps)
        
        # Start from random noise
        x = torch.randn(batch_size, self.config.in_channels, self.config.image_size, 
                       self.config.image_size, device=self.device)
        
        # Encode text if provided
        context = None
        if text is not None and self.text_encoder is not None:
            context = self.encode_text(text)
        
        # Sampling loop
        for i, t in enumerate(self.scheduler.timesteps):
            # Prepare timestep
            timestep = t.unsqueeze(0).expand(batch_size)
            
            # Classifier-free guidance
            if guidance_scale > 1.0 and context is not None:
                # Unconditional prediction
                with torch.no_grad():
                    uncond_pred = self.unet(x, timestep, None)
                
                # Conditional prediction
                with torch.no_grad():
                    cond_pred = self.unet(x, timestep, context)
                
                # Apply guidance
                noise_pred = uncond_pred + guidance_scale * (cond_pred - uncond_pred)
            else:
                with torch.no_grad():
                    noise_pred = self.unet(x, timestep, context)
            
            # Denoising step
            x = self.scheduler.step(noise_pred, t.item(), x)
        
        return x
    
    def save(self, path: str):
        """Save model and config."""
        # Save config
        config_path = path.replace('.pth', '_config.json')
        self.config.save(config_path)
        
        # Save model
        torch.save({
            'unet_state_dict': self.unet.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, path)
    
    def load(self, path: str):
        """Load model and config."""
        # Load config
        config_path = path.replace('.pth', '_config.json')
        if os.path.exists(config_path):
            self.config = DiffusionConfig.load(config_path)
        
        # Load model
        checkpoint = torch.load(path, map_location=self.device)
        self.unet.load_state_dict(checkpoint['unet_state_dict'])
        if 'optimizer_state_dict' in checkpoint:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

# ============================================================================
# DIFFUSERS PIPELINE FACTORIES
# ============================================================================

class DiffusersSchedulerFactory:
    """Factory for creating diffusers schedulers."""
    
    @staticmethod
    def create_scheduler(scheduler_type: str, **kwargs) -> Any:
        """Create a diffusers scheduler."""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers library not available")
        
        schedulers = {
            'ddpm': DDPMScheduler,
            'ddim': DDIMScheduler,
            'euler': EulerDiscreteScheduler,
            'euler_ancestral': EulerAncestralDiscreteScheduler,
            'heun': HeunDiscreteScheduler,
            'dpm_solver_multistep': DPMSolverMultistepScheduler,
            'dpm_solver_singlestep': DPMSolverSinglestepScheduler,
        }
        
        if scheduler_type not in schedulers:
            raise ValueError(f"Unknown scheduler type: {scheduler_type}")
        
        return schedulers[scheduler_type](**kwargs)

class DiffusersPipelineFactory:
    """Factory for creating diffusers pipelines."""
    
    @staticmethod
    def create_pipeline(pipeline_type: str, **kwargs) -> Any:
        """Create a diffusers pipeline."""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers library not available")
        
        pipelines = {
            'stable_diffusion': StableDiffusionPipeline,
            'stable_diffusion_xl': StableDiffusionXLPipeline,
            'diffusion': DiffusionPipeline,
        }
        
        if pipeline_type not in pipelines:
            raise ValueError(f"Unknown pipeline type: {pipeline_type}")
        
        return pipelines[pipeline_type](**kwargs)

# ============================================================================
# ULTRA-OPTIMIZED DIFFUSION MODEL
# ============================================================================

class UltraOptimizedDiffusionModel:
    """Ultra-optimized diffusion model wrapper for diffusers pipelines and custom models."""
    
    def __init__(self, model_type: str = "custom", **kwargs):
        self.model_type = model_type
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if model_type == "custom":
            config = kwargs.get('config', DiffusionConfig())
            self.model = AdvancedDiffusionModel(config)
        elif model_type == "stable_diffusion":
            if not DIFFUSERS_AVAILABLE:
                raise ImportError("Diffusers library not available for Stable Diffusion")
            self.model = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5", **kwargs
            ).to(self.device)
        elif model_type == "stable_diffusion_xl":
            if not DIFFUSERS_AVAILABLE:
                raise ImportError("Diffusers library not available for Stable Diffusion XL")
            self.model = StableDiffusionXLPipeline.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0", **kwargs
            ).to(self.device)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Performance optimizations
        if hasattr(self.model, 'enable_attention_slicing'):
            self.model.enable_attention_slicing()
        if hasattr(self.model, 'enable_vae_slicing'):
            self.model.enable_vae_slicing()
        if hasattr(self.model, 'enable_model_cpu_offload'):
            self.model.enable_model_cpu_offload()
    
    def generate(self, prompt: str = None, batch_size: int = 1, 
                num_inference_steps: int = 50, guidance_scale: float = 7.5,
                **kwargs) -> torch.Tensor:
        """Generate images using the model."""
        if self.model_type == "custom":
            return self.model.sample(
                batch_size=batch_size,
                text=prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
        else:
            # Use diffusers pipeline
            result = self.model(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                num_images_per_prompt=batch_size,
                **kwargs
            )
            return result.images
    
    def train(self, dataset: Dataset, num_epochs: int = None, **kwargs):
        """Train the model."""
        if self.model_type == "custom":
            if num_epochs is None:
                num_epochs = self.model.config.num_epochs
            
            dataloader = DataLoader(dataset, batch_size=self.model.config.batch_size, shuffle=True)
            
            for epoch in range(num_epochs):
                epoch_loss = 0
                for batch in tqdm(dataloader, desc=f"Epoch {epoch+1}/{num_epochs}"):
                    loss_dict = self.model.train_step(batch)
                    epoch_loss += loss_dict["loss"]
                
                print(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss/len(dataloader):.6f}")
        else:
            raise NotImplementedError("Training not implemented for diffusers pipelines")
    
    def save(self, path: str):
        """Save the model."""
        if self.model_type == "custom":
            self.model.save(path)
        else:
            self.model.save_pretrained(path)
    
    def load(self, path: str):
        """Load the model."""
        if self.model_type == "custom":
            self.model.load(path)
        else:
            self.model = self.model.__class__.from_pretrained(path)
            self.model.to(self.device)

# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def demonstrate_diffusion_models():
    """Demonstrate the diffusion models system."""
    print("Diffusion Models System Demonstration")
    print("=" * 60)
    
    # Check library availability
    print(f"Diffusers available: {DIFFUSERS_AVAILABLE}")
    print(f"Transformers available: {TRANSFORMERS_AVAILABLE}")
    
    # Create configuration
    print("\n1. Creating Diffusion Configuration:")
    config = DiffusionConfig(
        image_size=64,
        model_channels=64,
        num_diffusion_timesteps=100,
        beta_schedule="cosine",
        learning_rate=1e-4
    )
    print(f"   Configuration created: {config.image_size}x{config.image_size} images")
    print(f"   Model channels: {config.model_channels}")
    print(f"   Timesteps: {config.num_diffusion_timesteps}")
    
    # Test beta schedules
    print("\n2. Testing Beta Schedules:")
    for schedule_type in ["linear", "cosine", "sigmoid"]:
        if schedule_type == "linear":
            betas = BetaSchedule.linear(0.0001, 0.02, 100)
        elif schedule_type == "cosine":
            betas = BetaSchedule.cosine(0.0001, 0.02, 100)
        elif schedule_type == "sigmoid":
            betas = BetaSchedule.sigmoid(0.0001, 0.02, 100)
        
        print(f"   {schedule_type.capitalize()}: min={betas.min():.6f}, max={betas.max():.6f}")
    
    # Test scheduler
    print("\n3. Testing Custom Diffusion Scheduler:")
    try:
        scheduler = CustomDiffusionScheduler(config)
        print(f"   Scheduler created successfully")
        print(f"   Beta schedule: {scheduler.beta_schedule}")
        print(f"   Number of timesteps: {scheduler.num_timesteps}")
        
        # Test noise addition
        test_image = torch.randn(1, 3, 64, 64)
        timesteps = torch.tensor([50])
        noisy_image, noise = scheduler.add_noise(test_image, timesteps)
        print(f"   Noise addition test: {noisy_image.shape}")
        
    except Exception as e:
        print(f"   Scheduler test failed: {e}")
    
    # Test UNet
    print("\n4. Testing Custom UNet:")
    try:
        unet = CustomUNet(config)
        print(f"   UNet created successfully")
        print(f"   Parameters: {sum(p.numel() for p in unet.parameters()):,}")
        
        # Test forward pass
        test_input = torch.randn(1, 3, 64, 64)
        test_timesteps = torch.tensor([50])
        test_context = torch.randn(1, 10, 512) if config.context_dim else None
        
        with torch.no_grad():
            output = unet(test_input, test_timesteps, test_context)
        print(f"   Forward pass test: {output.shape}")
        
    except Exception as e:
        print(f"   UNet test failed: {e}")
    
    # Test advanced model
    print("\n5. Testing Advanced Diffusion Model:")
    try:
        model = AdvancedDiffusionModel(config)
        print(f"   Advanced model created successfully")
        
        # Test training step
        test_batch = torch.randn(2, 3, 64, 64)
        loss_dict = model.train_step(test_batch)
        print(f"   Training step test: loss = {loss_dict['loss']:.6f}")
        
    except Exception as e:
        print(f"   Advanced model test failed: {e}")
    
    # Test diffusers integration
    if DIFFUSERS_AVAILABLE:
        print("\n6. Testing Diffusers Integration:")
        try:
            # Test scheduler factory
            ddpm_scheduler = DiffusersSchedulerFactory.create_scheduler('ddpm')
            print(f"   DDPM scheduler created: {type(ddpm_scheduler).__name__}")
            
            # Test pipeline factory
            print(f"   Pipeline factory available")
            
        except Exception as e:
            print(f"   Diffusers integration test failed: {e}")
    
    # Test ultra-optimized model
    print("\n7. Testing Ultra-Optimized Model:")
    try:
        ultra_model = UltraOptimizedDiffusionModel("custom", config=config)
        print(f"   Ultra-optimized model created successfully")
        
        # Test generation
        with torch.no_grad():
            samples = ultra_model.generate(
                prompt="a beautiful landscape",
                batch_size=1,
                num_inference_steps=10
            )
        print(f"   Generation test: {samples.shape}")
        
    except Exception as e:
        print(f"   Ultra-optimized model test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Diffusion models demonstration completed!")

if __name__ == "__main__":
    demonstrate_diffusion_models()
