"""
Diffusion Engine following Diffusers library best practices.
Using official documentation recommendations for model loading and training.
"""

import torch
import torch.nn as nn
import torch.distributed as dist
from torch.nn.parallel import DataParallel, DistributedDataParallel
from torch.cuda.amp import GradScaler, autocast
from diffusers import (
    StableDiffusionPipeline, 
    StableDiffusionXLPipeline,
    DDIMScheduler,
    DPMSolverMultistepScheduler,
    EulerDiscreteScheduler
)
from typing import Dict, Any, List, Optional, Union
import os
import time
from datetime import datetime
from dataclasses import dataclass, field
from PIL import Image
import numpy as np
import json
from contextlib import contextmanager

from ..core.interfaces import CoreConfig
from ..utils.logging import get_logger
from ..utils.performance_optimization import create_performance_optimizer, create_diffusion_optimizer
from ..utils.advanced_training import create_trainer, TrainingConfig, TrainingMode
from .base import Engine

@dataclass
class DiffusionTrainingConfig:
    """Configuration for diffusion training following best practices."""
    enable_multi_gpu: bool = True
    gpu_ids: List[int] = field(default_factory=lambda: [0])
    distributed_training: bool = False
    backend: str = "nccl"
    gradient_accumulation_steps: int = 1
    mixed_precision: bool = True
    gradient_checkpointing: bool = True
    enable_xformers: bool = True
    enable_attention_slicing: bool = True
    enable_vae_slicing: bool = True
    enable_cpu_offload: bool = False

class GradientAccumulator:
    """Accumulate gradients over multiple steps for large effective batch sizes."""
    
    def __init__(self, accumulation_steps: int = 1):
        self.accumulation_steps = accumulation_steps
        self.current_step = 0
        self.logger = get_logger(__name__)
        
        if accumulation_steps > 1:
            self.logger.info(f"Gradient accumulation enabled with {accumulation_steps} steps")
    
    def backward_step(self, loss: torch.Tensor, scaler: Optional[GradScaler] = None):
        """Perform backward step with optional gradient scaling."""
        if scaler:
            scaler.scale(loss / self.accumulation_steps).backward()
        else:
            (loss / self.accumulation_steps).backward()
        
        self.current_step += 1
        
        if self.current_step % self.accumulation_steps == 0:
            if scaler:
                scaler.step(self.optimizer)
                scaler.update()
            else:
                self.optimizer.step()
            
            self.optimizer.zero_grad()
            self.current_step = 0

class DiffusionEngine(Engine):
    """Diffusion Engine following Diffusers best practices."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        
        # Initialize performance optimizers
        self.performance_optimizer = create_performance_optimizer(config)
        self.diffusion_optimizer = create_diffusion_optimizer(config)
        
        # Pipeline and components
        self.pipeline = None
        self.unet = None
        self.vae = None
        self.text_encoder = None
        self.tokenizer = None
        self.scheduler = None
        
        # Training configuration
        self.training_config = DiffusionTrainingConfig(**config.get('diffusion_training', {}))
        
        # Mixed precision configuration
        self.mixed_precision = config.get('mixed_precision', True)
        self.scaler = None
        
        # Performance profiling
        self.performance_profiler = None
        
        # Initialize components
        self._initialize_pipeline()
        self._setup_multi_gpu()
    
    def _get_device(self) -> torch.device:
        """Get the appropriate device for the model."""
        if torch.cuda.is_available():
            return torch.device(f"cuda:{self.training_config.gpu_ids[0]}")
        else:
            return torch.device("cpu")
    
    def _initialize_pipeline(self):
        """Initialize the diffusion pipeline following Diffusers best practices."""
        try:
            # Load pipeline based on configuration
            if self.config.get('use_xl', False):
                self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                    self.config.get('model_name', 'stabilityai/stable-diffusion-xl-base-1.0'),
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    use_safetensors=True,
                    variant="fp16" if torch.cuda.is_available() else None
                )
            else:
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    self.config.get('model_name', 'runwayml/stable-diffusion-v1-5'),
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    use_safetensors=True,
                    variant="fp16" if torch.cuda.is_available() else None
                )
            
            # Apply performance optimizations
            self.pipeline = self.diffusion_optimizer.optimize_pipeline(self.pipeline)
            
            # Extract components for training
            self.unet = self.pipeline.unet
            self.vae = self.pipeline.vae
            self.text_encoder = self.pipeline.text_encoder
            self.tokenizer = self.pipeline.tokenizer
            self.scheduler = self.pipeline.scheduler
            
            # Apply performance optimizations to components
            if torch.cuda.is_available():
                self.unet = self.performance_optimizer.optimize_model(self.unet)
                self.vae = self.performance_optimizer.optimize_model(self.vae)
                if self.text_encoder:
                    self.text_encoder = self.performance_optimizer.optimize_model(self.text_encoder)
            
            # Initialize mixed precision scaler
            if self.mixed_precision and torch.cuda.is_available():
                self.scaler = GradScaler()
            
            self.logger.info(f"Diffusion pipeline initialized: {self.config.get('model_name')}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize diffusion pipeline: {e}")
            raise
    
    def _apply_performance_optimizations(self):
        """Apply additional performance optimizations following best practices."""
        try:
            # Enable memory efficient attention
            if hasattr(torch.backends.cuda, 'enable_flash_sdp'):
                torch.backends.cuda.enable_flash_sdp(True)
                torch.backends.cuda.enable_mem_efficient_sdp(True)
                torch.backends.cuda.enable_math_sdp(True)
            
            # Enable gradient checkpointing
            if self.training_config.gradient_checkpointing:
                if hasattr(self.unet, 'enable_gradient_checkpointing'):
                    self.unet.enable_gradient_checkpointing()
                if hasattr(self.vae, 'enable_gradient_checkpointing'):
                    self.vae.enable_gradient_checkpointing()
            
        except Exception as e:
            self.logger.warning(f"Some performance optimizations failed: {e}")
    
    def _setup_multi_gpu(self):
        """Setup multi-GPU training following best practices."""
        if not torch.cuda.is_available():
            return
        
        if len(self.training_config.gpu_ids) > 1:
            if self.training_config.distributed_training:
                # Distributed training setup
                if not dist.is_initialized():
                    dist.init_process_group(
                        backend=self.training_config.backend,
                        init_method='env://'
                    )
                
                self.unet = DistributedDataParallel(
                    self.unet,
                    device_ids=[self.device],
                    find_unused_parameters=False,
                    gradient_as_bucket_view=True
                )
                
                self.vae = DistributedDataParallel(
                    self.vae,
                    device_ids=[self.device],
                    find_unused_parameters=False,
                    gradient_as_bucket_view=True
                )
            else:
                # DataParallel setup
                self.unet = DataParallel(
                    self.unet, 
                    device_ids=self.training_config.gpu_ids
                )
                
                self.vae = DataParallel(
                    self.vae, 
                    device_ids=self.training_config.gpu_ids
                )
            
            # Initialize gradient accumulator
            self.gradient_accumulator = GradientAccumulator(
                self.training_config.gradient_accumulation_steps
            )
    
    def _execute_operation(self, operation: str, **kwargs) -> Any:
        """Execute diffusion operations following best practices."""
        try:
            if operation == "generate_image":
                return self.generate_image(**kwargs)
            elif operation == "train_model":
                return self.train_model(**kwargs)
            elif operation == "fine_tune_model":
                return self.fine_tune_model(**kwargs)
            elif operation == "evaluate_model":
                return self.evaluate_model(**kwargs)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        except Exception as e:
            self.logger.error(f"Operation {operation} failed: {e}")
            raise
    
    def generate_image(self, prompt: str, negative_prompt: str = "", num_steps: int = 50,
                      guidance_scale: float = 7.5, width: int = 512, height: int = 512,
                      seed: Optional[int] = None, num_images: int = 1) -> List[Image.Image]:
        """Generate images using the diffusion pipeline following best practices."""
        try:
            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(seed)
            
            # Generate images with optimized inference
            with torch.no_grad():
                with autocast() if self.mixed_precision and torch.cuda.is_available() else self._noop_context():
                    outputs = self.pipeline(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        num_inference_steps=num_steps,
                        guidance_scale=guidance_scale,
                        width=width,
                        height=height,
                        num_images_per_prompt=num_images,
                        generator=torch.Generator(device=self.device).manual_seed(seed) if seed else None
                    )
            
            # Extract images
            images = outputs.images
            
            # Save images if requested
            if self.config.get('save_generated_images', True):
                self._save_generated_images(images, prompt, seed)
            
            return images
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise
    
    def _save_generated_images(self, images: List[Image.Image], prompt: str, seed: Optional[int]):
        """Save generated images following best practices."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_dir = f"./generated_images/{timestamp}"
            os.makedirs(save_dir, exist_ok=True)
            
            for i, image in enumerate(images):
                filename = f"image_{i}_{seed or 'random'}_{timestamp}.png"
                filepath = os.path.join(save_dir, filename)
                image.save(filepath)
                
                # Save metadata
                metadata = {
                    'prompt': prompt,
                    'seed': seed,
                    'timestamp': timestamp,
                    'filename': filename
                }
                metadata_path = os.path.join(save_dir, f"metadata_{i}.json")
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Generated images saved to {save_dir}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save generated images: {e}")
    
    def train_model(self, training_data: List[Dict[str, Any]], epochs: int = 100,
                   batch_size: int = 1, learning_rate: float = 1e-5) -> Dict[str, Any]:
        """Train the diffusion model using advanced training system."""
        try:
            # Create training configuration
            training_config = TrainingConfig(
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate,
                mixed_precision=self.mixed_precision,
                gradient_accumulation_steps=self.training_config.gradient_accumulation_steps,
                training_mode=TrainingMode.DATA_PARALLEL if len(self.training_config.gpu_ids) > 1 else TrainingMode.SINGLE_GPU,
                gpu_ids=self.training_config.gpu_ids
            )
            
            # Create trainer
            trainer = create_trainer(self.unet, training_config, "diffusion")
            
            # Prepare training data
            dataset = self._prepare_training_data(training_data)
            
            # Create dataloader with optimizations
            dataloader = torch.utils.data.DataLoader(
                dataset,
                batch_size=batch_size,
                shuffle=True,
                num_workers=self.config.get('num_workers', 4),
                pin_memory=True,
                prefetch_factor=2
            )
            
            # Optimize dataloader
            dataloader = self.performance_optimizer.optimize_data_loading(dataloader)
            
            # Training loop
            for epoch in range(epochs):
                # Train epoch
                train_metrics = trainer.train_epoch(dataloader)
                
                # Log metrics
                self.logger.info(f"Epoch {epoch+1}/{epochs}: {train_metrics}")
                
                # Save checkpoint
                if (epoch + 1) % 10 == 0:
                    checkpoint_path = f"./checkpoints/diffusion_checkpoint_epoch_{epoch+1}.pt"
                    trainer.save_checkpoint(checkpoint_path)
            
            # Save final model
            trainer.save_checkpoint("./checkpoints/diffusion_final_model.pt", is_best=True)
            
            return {
                "status": "success",
                "message": "Diffusion model training completed successfully",
                "checkpoint_path": "./checkpoints/diffusion_final_model.pt"
            }
            
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            raise
    
    def _prepare_training_data(self, training_data: List[Dict[str, Any]]):
        """Prepare training data following best practices."""
        # This is a placeholder - implement based on your data format
        class DiffusionDataset(torch.utils.data.Dataset):
            def __init__(self, data, tokenizer, vae, max_length=77):
                self.data = data
                self.tokenizer = tokenizer
                self.vae = vae
                self.max_length = max_length
            
            def __len__(self):
                return len(self.data)
            
            def __getitem__(self, idx):
                item = self.data[idx]
                prompt = item.get('prompt', '')
                image_path = item.get('image_path', '')
                
                # Tokenize prompt
                encoding = self.tokenizer(
                    prompt,
                    truncation=True,
                    padding='max_length',
                    max_length=self.max_length,
                    return_tensors='pt'
                )
                
                # Load and encode image
                if image_path and os.path.exists(image_path):
                    image = Image.open(image_path).convert('RGB')
                    # Resize to VAE input size
                    image = image.resize((512, 512))
                    image_tensor = torch.from_numpy(np.array(image)).float() / 255.0
                    image_tensor = image_tensor.permute(2, 0, 1).unsqueeze(0)
                    
                    # Encode with VAE
                    with torch.no_grad():
                        latents = self.vae.encode(image_tensor).latent_dist.sample()
                else:
                    # Create dummy latents
                    latents = torch.randn(1, 4, 64, 64)
                
                return {
                    'input_ids': encoding['input_ids'].squeeze(),
                    'attention_mask': encoding['attention_mask'].squeeze(),
                    'latents': latents.squeeze()
                }
        
        return DiffusionDataset(training_data, self.tokenizer, self.vae)
    
    def fine_tune_model(self, training_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Fine-tune the diffusion model following best practices."""
        # Placeholder for fine-tuning implementation
        return {"status": "not_implemented", "message": "Fine-tuning not yet implemented"}
    
    def evaluate_model(self, test_data: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Evaluate the diffusion model following best practices."""
        # Placeholder for evaluation implementation
        return {"status": "not_implemented", "message": "Evaluation not yet implemented"}
    
    def _save_checkpoint(self, path: str, model: nn.Module, optimizer, scheduler, epoch: int, loss: float):
        """Save training checkpoint following best practices."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'loss': loss,
                'config': self.config
            }
            
            if self.scaler:
                checkpoint['scaler_state_dict'] = self.scaler.state_dict()
            
            torch.save(checkpoint, path)
            self.logger.info(f"Checkpoint saved to {path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get engine health status following best practices."""
        try:
            # Basic health info
            health = {
                'status': 'healthy',
                'pipeline_loaded': self.pipeline is not None,
                'unet_loaded': self.unet is not None,
                'vae_loaded': self.vae is not None,
                'device': str(self.device),
                'mixed_precision': self.mixed_precision
            }
            
            # Performance stats
            if hasattr(self, 'performance_optimizer'):
                health.update(self.performance_optimizer.get_performance_stats())
            
            # Training info
            if hasattr(self, 'training_config'):
                health.update({
                    'multi_gpu_enabled': self.training_config.enable_multi_gpu,
                    'gpu_count': len(self.training_config.gpu_ids),
                    'distributed_training': self.training_config.distributed_training
                })
            
            return health
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def shutdown(self):
        """Shutdown the engine following best practices."""
        try:
            # Clean up distributed training
            if hasattr(self, 'dist') and dist.is_initialized():
                dist.destroy_process_group()
            
            # Clean up memory
            if hasattr(self, 'performance_optimizer'):
                self.performance_optimizer.memory_cleanup()
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.logger.info("Diffusion Engine shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
    
    @contextmanager
    def _noop_context(self):
        """No-op context manager for when autocast is disabled."""
        yield


