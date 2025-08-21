#!/usr/bin/env python3
"""
Optimized Diffusion Models Implementation
========================================

Production-ready diffusion models with:
- Stable Diffusion pipeline optimizations
- Custom noise schedulers
- Memory-efficient inference
- Comprehensive error handling
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Union, List, Dict, Any, Tuple
import logging
from pathlib import Path

from diffusers import (
    StableDiffusionPipeline, StableDiffusionXLPipeline,
    DDIMScheduler, DDPMScheduler, EulerDiscreteScheduler,
    AutoencoderKL, UNet2DConditionModel, DiffusionPipeline
)
from diffusers.schedulers.scheduling_utils import SchedulerMixin
from transformers import CLIPTextModel, CLIPTokenizer

# =============================================================================
# Optimized Diffusion Pipeline
# =============================================================================

class OptimizedDiffusionPipeline:
    """Optimized diffusion pipeline with performance enhancements."""
    
    def __init__(
        self,
        model_name: str = "runwayml/stable-diffusion-v1-5",
        device: str = "cuda",
        torch_dtype: torch.dtype = torch.float16,
        use_memory_efficient_attention: bool = True,
        enable_attention_slicing: bool = True,
        enable_vae_slicing: bool = True,
        enable_xformers_memory_efficient_attention: bool = True
    ):
        self.device = device
        self.torch_dtype = torch_dtype
        self.model_name = model_name
        
        # Load pipeline
        self.pipeline = self._load_pipeline(
            model_name=model_name,
            device=device,
            torch_dtype=torch_dtype,
            use_memory_efficient_attention=use_memory_efficient_attention,
            enable_attention_slicing=enable_attention_slicing,
            enable_vae_slicing=enable_vae_slicing,
            enable_xformers_memory_efficient_attention=enable_xformers_memory_efficient_attention
        )
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _load_pipeline(
        self,
        model_name: str,
        device: str,
        torch_dtype: torch.dtype,
        use_memory_efficient_attention: bool,
        enable_attention_slicing: bool,
        enable_vae_slicing: bool,
        enable_xformers_memory_efficient_attention: bool
    ) -> DiffusionPipeline:
        """Load and optimize diffusion pipeline."""
        try:
            # Load pipeline
            pipeline = StableDiffusionPipeline.from_pretrained(
                model_name,
                torch_dtype=torch_dtype,
                safety_checker=None,  # Disable for performance
                requires_safety_checker=False
            )
            
            # Move to device
            pipeline = pipeline.to(device)
            
            # Enable optimizations
            if enable_attention_slicing:
                pipeline.enable_attention_slicing()
            
            if enable_vae_slicing:
                pipeline.enable_vae_slicing()
            
            if enable_xformers_memory_efficient_attention:
                try:
                    pipeline.enable_xformers_memory_efficient_attention()
                except Exception as e:
                    self.logger.warning(f"XFormers optimization failed: {e}")
            
            # Set memory efficient attention
            if use_memory_efficient_attention:
                pipeline.unet.set_use_memory_efficient_attention_xformers(True)
            
            return pipeline
            
        except Exception as e:
            self.logger.error(f"Failed to load pipeline: {e}")
            raise
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
        width: int = 512,
        height: int = 512,
        seed: Optional[int] = None,
        num_images: int = 1
    ) -> List[torch.Tensor]:
        """Generate images with optimizations."""
        try:
            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(seed)
            
            # Generate images
            with torch.autocast(device_type=self.device, dtype=self.torch_dtype):
                result = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    width=width,
                    height=height,
                    num_images_per_prompt=num_images,
                    return_dict=True
                )
            
            return result.images
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise
    
    def generate_image_batch(
        self,
        prompts: List[str],
        negative_prompts: Optional[List[str]] = None,
        **kwargs
    ) -> List[torch.Tensor]:
        """Generate multiple images from a batch of prompts."""
        all_images = []
        
        for i, prompt in enumerate(prompts):
            negative_prompt = negative_prompts[i] if negative_prompts else None
            images = self.generate_image(prompt, negative_prompt, **kwargs)
            all_images.extend(images)
        
        return all_images

# =============================================================================
# Custom Noise Schedulers
# =============================================================================

class OptimizedDDIMScheduler(DDIMScheduler):
    """Optimized DDIM scheduler with enhanced functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
    
    def step(
        self,
        model_output: torch.FloatTensor,
        timestep: int,
        sample: torch.FloatTensor,
        eta: float = 0.0,
        use_clipped_model_output: bool = False,
        generator=None,
        return_dict: bool = True,
    ):
        """Optimized DDIM step with error handling."""
        try:
            return super().step(
                model_output=model_output,
                timestep=timestep,
                sample=sample,
                eta=eta,
                use_clipped_model_output=use_clipped_model_output,
                generator=generator,
                return_dict=return_dict
            )
        except Exception as e:
            self.logger.error(f"DDIM step failed: {e}")
            raise

class OptimizedEulerScheduler(EulerDiscreteScheduler):
    """Optimized Euler scheduler with enhanced functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
    
    def step(
        self,
        model_output: torch.FloatTensor,
        timestep: Union[float, torch.FloatTensor],
        sample: torch.FloatTensor,
        generator=None,
        return_dict: bool = True,
    ):
        """Optimized Euler step with error handling."""
        try:
            return super().step(
                model_output=model_output,
                timestep=timestep,
                sample=sample,
                generator=generator,
                return_dict=return_dict
            )
        except Exception as e:
            self.logger.error(f"Euler step failed: {e}")
            raise

# =============================================================================
# Optimized UNet Model
# =============================================================================

class OptimizedUNet2DConditionModel(UNet2DConditionModel):
    """Optimized UNet model with performance enhancements."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self._setup_optimizations()
    
    def _setup_optimizations(self):
        """Setup model optimizations."""
        # Enable gradient checkpointing for memory efficiency
        self.enable_gradient_checkpointing()
        
        # Set memory efficient attention if available
        try:
            self.set_use_memory_efficient_attention_xformers(True)
        except Exception as e:
            self.logger.warning(f"XFormers optimization failed: {e}")
    
    def forward(
        self,
        sample: torch.FloatTensor,
        timestep: Union[torch.Tensor, float, int],
        encoder_hidden_states: torch.Tensor,
        class_labels: Optional[torch.LongTensor] = None,
        timestep_cond: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        cross_attention_kwargs: Optional[Dict[str, Any]] = None,
        added_cond_kwargs: Optional[Dict[str, torch.Tensor]] = None,
        down_block_additional_residuals: Optional[Tuple[torch.Tensor]] = None,
        mid_block_additional_residual: Optional[torch.Tensor] = None,
        encoder_attention_mask: Optional[torch.Tensor] = None,
        return_dict: bool = True,
    ):
        """Optimized forward pass with error handling."""
        try:
            return super().forward(
                sample=sample,
                timestep=timestep,
                encoder_hidden_states=encoder_hidden_states,
                class_labels=class_labels,
                timestep_cond=timestep_cond,
                attention_mask=attention_mask,
                cross_attention_kwargs=cross_attention_kwargs,
                added_cond_kwargs=added_cond_kwargs,
                down_block_additional_residuals=down_block_additional_residuals,
                mid_block_additional_residual=mid_block_additional_residual,
                encoder_attention_mask=encoder_attention_mask,
                return_dict=return_dict
            )
        except Exception as e:
            self.logger.error(f"UNet forward pass failed: {e}")
            raise

# =============================================================================
# Optimized VAE Model
# =============================================================================

class OptimizedAutoencoderKL(AutoencoderKL):
    """Optimized VAE model with performance enhancements."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self._setup_optimizations()
    
    def _setup_optimizations(self):
        """Setup VAE optimizations."""
        # Enable gradient checkpointing
        self.enable_gradient_checkpointing()
    
    def encode(
        self,
        x: torch.FloatTensor,
        return_dict: bool = True,
    ):
        """Optimized VAE encoding with error handling."""
        try:
            return super().encode(x, return_dict=return_dict)
        except Exception as e:
            self.logger.error(f"VAE encoding failed: {e}")
            raise
    
    def decode(
        self,
        z: torch.FloatTensor,
        return_dict: bool = True,
    ):
        """Optimized VAE decoding with error handling."""
        try:
            return super().decode(z, return_dict=return_dict)
        except Exception as e:
            self.logger.error(f"VAE decoding failed: {e}")
            raise

# =============================================================================
# Diffusion Training Utilities
# =============================================================================

class DiffusionTrainingUtils:
    """Utilities for diffusion model training."""
    
    def __init__(self, device: str = "cuda"):
        self.device = device
        self.logger = logging.getLogger(__name__)
    
    def add_noise(
        self,
        original_samples: torch.FloatTensor,
        noise: torch.FloatTensor,
        timesteps: torch.IntTensor,
        scheduler: SchedulerMixin
    ) -> torch.FloatTensor:
        """Add noise to samples according to timesteps."""
        try:
            # Scale the image values to [0, 1] range
            original_samples = original_samples / 2 + 0.5
            
            # Add noise
            noisy_samples = scheduler.add_noise(original_samples, noise, timesteps)
            
            # Scale back to [-1, 1] range
            noisy_samples = noisy_samples * 2 - 1
            
            return noisy_samples
            
        except Exception as e:
            self.logger.error(f"Adding noise failed: {e}")
            raise
    
    def compute_loss(
        self,
        model_pred: torch.FloatTensor,
        target: torch.FloatTensor,
        loss_type: str = "l2"
    ) -> torch.FloatTensor:
        """Compute loss between model prediction and target."""
        try:
            if loss_type == "l2":
                loss = F.mse_loss(model_pred, target, reduction="mean")
            elif loss_type == "l1":
                loss = F.l1_loss(model_pred, target, reduction="mean")
            elif loss_type == "huber":
                loss = F.huber_loss(model_pred, target, reduction="mean")
            else:
                raise ValueError(f"Unsupported loss type: {loss_type}")
            
            return loss
            
        except Exception as e:
            self.logger.error(f"Loss computation failed: {e}")
            raise
    
    def sample_timesteps(
        self,
        batch_size: int,
        num_train_timesteps: int,
        device: str = "cuda"
    ) -> torch.LongTensor:
        """Sample random timesteps for training."""
        try:
            timesteps = torch.randint(
                0, num_train_timesteps, (batch_size,), device=device
            ).long()
            return timesteps
            
        except Exception as e:
            self.logger.error(f"Timestep sampling failed: {e}")
            raise

# =============================================================================
# Optimized Diffusion Trainer
# =============================================================================

class OptimizedDiffusionTrainer:
    """Optimized trainer for diffusion models."""
    
    def __init__(
        self,
        unet: OptimizedUNet2DConditionModel,
        vae: OptimizedAutoencoderKL,
        text_encoder: CLIPTextModel,
        tokenizer: CLIPTokenizer,
        scheduler: SchedulerMixin,
        device: str = "cuda",
        learning_rate: float = 1e-4,
        weight_decay: float = 0.01
    ):
        self.unet = unet
        self.vae = vae
        self.text_encoder = text_encoder
        self.tokenizer = tokenizer
        self.scheduler = scheduler
        self.device = device
        
        # Move models to device
        self.unet = self.unet.to(device)
        self.vae = self.vae.to(device)
        self.text_encoder = self.text_encoder.to(device)
        
        # Freeze VAE and text encoder
        self.vae.requires_grad_(False)
        self.text_encoder.requires_grad_(False)
        
        # Setup optimizer
        self.optimizer = torch.optim.AdamW(
            self.unet.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        # Training utilities
        self.training_utils = DiffusionTrainingUtils(device)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def train_step(
        self,
        images: torch.FloatTensor,
        prompts: List[str],
        loss_type: str = "l2"
    ) -> Dict[str, float]:
        """Single training step."""
        try:
            # Tokenize prompts
            tokenized = self.tokenizer(
                prompts,
                padding="max_length",
                max_length=self.tokenizer.model_max_length,
                truncation=True,
                return_tensors="pt"
            )
            
            # Move to device
            tokenized = {k: v.to(self.device) for k, v in tokenized.items()}
            images = images.to(self.device)
            
            # Get text embeddings
            with torch.no_grad():
                text_embeddings = self.text_encoder(**tokenized).last_hidden_state
            
            # Get VAE latents
            with torch.no_grad():
                latents = self.vae.encode(images).latent_dist.sample()
                latents = latents * 0.18215
            
            # Sample timesteps
            timesteps = self.training_utils.sample_timesteps(
                batch_size=images.shape[0],
                num_train_timesteps=self.scheduler.num_train_timesteps,
                device=self.device
            )
            
            # Add noise
            noise = torch.randn_like(latents)
            noisy_latents = self.scheduler.add_noise(latents, noise, timesteps)
            
            # Predict noise
            noise_pred = self.unet(
                noisy_latents,
                timesteps,
                encoder_hidden_states=text_embeddings
            ).sample
            
            # Compute loss
            loss = self.training_utils.compute_loss(noise_pred, noise, loss_type)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()
            
            return {"loss": loss.item()}
            
        except Exception as e:
            self.logger.error(f"Training step failed: {e}")
            raise
    
    def save_checkpoint(self, path: str, epoch: int, metrics: Dict[str, float]):
        """Save training checkpoint."""
        try:
            checkpoint = {
                "epoch": epoch,
                "unet_state_dict": self.unet.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "scheduler_state_dict": self.scheduler.state_dict(),
                "metrics": metrics
            }
            
            torch.save(checkpoint, path)
            self.logger.info(f"Checkpoint saved to {path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
            raise

# =============================================================================
# Usage Example
# =============================================================================

def main():
    """Example usage of optimized diffusion models."""
    
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create optimized pipeline
        pipeline = OptimizedDiffusionPipeline(
            model_name="runwayml/stable-diffusion-v1-5",
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        
        # Generate image
        prompt = "A beautiful sunset over mountains, high quality, detailed"
        negative_prompt = "blurry, low quality, distorted"
        
        images = pipeline.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            seed=42
        )
        
        print(f"Generated {len(images)} images")
        
        # Save first image
        if images:
            images[0].save("generated_image.png")
            print("Image saved as generated_image.png")
        
    except Exception as e:
        logging.error(f"Example failed: {e}")
        raise

if __name__ == "__main__":
    main()

