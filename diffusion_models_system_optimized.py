"""
Optimized Diffusion Models System with Enhanced Performance and Features.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from diffusers import (
    StableDiffusionPipeline, DDIMScheduler, DDPM, UNet2DConditionModel,
    AutoencoderKL, DiffusionPipeline, DPMSolverMultistepScheduler,
    EMAModel, AttnProcessor2_0, DiffusionScheduler, EulerAncestralDiscreteScheduler
)
from transformers import CLIPTextModel, CLIPTokenizer
from typing import Dict, Any, Optional, Tuple, List, Union, Callable
from dataclasses import dataclass, field
import numpy as np
import PIL.Image
import logging
import time
from pathlib import Path
import json
import warnings
import gc
from contextlib import contextmanager
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


@dataclass
class OptimizedDiffusionConfig:
    """Optimized configuration for diffusion models."""
    # Model settings
    model_name: str = "runwayml/stable-diffusion-v1-5"
    model_type: str = "stable_diffusion"
    use_pipeline: bool = True
    
    # Performance optimization
    use_compile: bool = True  # torch.compile optimization
    use_channels_last: bool = True  # Memory layout optimization
    use_fp16: bool = True  # Mixed precision
    use_bf16: bool = False  # Brain float 16
    
    # Memory optimization
    enable_attention_slicing: bool = True
    enable_vae_slicing: bool = True
    enable_xformers_memory_efficient_attention: bool = True
    enable_model_cpu_offload: bool = False
    enable_sequential_cpu_offload: bool = False
    enable_vae_tiling: bool = True
    
    # Advanced optimizations
    use_gradient_checkpointing: bool = True
    use_ema: bool = True
    use_8bit_adam: bool = False
    use_amp: bool = True
    use_slicing: bool = True
    
    # Inference settings
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    eta: float = 0.0
    use_classifier_free_guidance: bool = True
    
    # Quality settings
    height: int = 512
    width: int = 512
    num_images_per_prompt: int = 1
    
    # Scheduler optimization
    scheduler_type: str = "ddim"  # ddim, euler_a, dpm_solver++
    beta_start: float = 0.00085
    beta_end: float = 0.012
    beta_schedule: str = "scaled_linear"
    
    # Batch processing
    max_batch_size: int = 4
    enable_batch_processing: bool = True
    
    # Caching
    enable_model_caching: bool = True
    cache_dir: str = ".model_cache"
    
    # Monitoring
    enable_performance_monitoring: bool = True
    enable_memory_tracking: bool = True


@dataclass
class OptimizedTrainingConfig:
    """Optimized training configuration."""
    # Basic training
    learning_rate: float = 1e-5
    num_epochs: int = 100
    batch_size: int = 1
    gradient_accumulation_steps: int = 4
    
    # Advanced optimization
    optimizer: str = "adamw"  # adamw, lion, adafactor, 8bit_adam
    weight_decay: float = 0.01
    warmup_steps: int = 500
    lr_scheduler: str = "cosine_with_restarts"
    
    # Loss and regularization
    loss_type: str = "l2"  # l2, l1, huber, focal, perceptual
    label_smoothing: float = 0.0
    gradient_clip_norm: float = 1.0
    
    # Performance optimization
    use_mixed_precision: bool = True
    use_gradient_accumulation: bool = True
    use_dynamic_batch_sizing: bool = True
    use_adaptive_learning_rate: bool = True
    
    # Checkpointing
    save_steps: int = 500
    save_total_limit: int = 10
    evaluation_steps: int = 100
    save_best_only: bool = True
    
    # Data
    train_data_dir: str = "data/train"
    val_data_dir: str = "data/val"
    image_size: int = 512
    center_crop: bool = True
    random_flip: bool = True
    
    # Advanced features
    use_ema_training: bool = True
    ema_decay: float = 0.9999
    use_curriculum_learning: bool = False
    use_progressive_training: bool = False


class PerformanceMonitor:
    """Advanced performance monitoring and optimization."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.metrics = {}
        self.start_times = {}
        self.memory_tracker = MemoryTracker() if enabled else None
        
    def start_timer(self, name: str):
        """Start timing an operation."""
        if self.enabled:
            self.start_times[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """End timing and return duration."""
        if not self.enabled or name not in self.start_times:
            return 0.0
        
        duration = time.time() - self.start_times[name]
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(duration)
        
        del self.start_times[name]
        return duration
    
    def get_average_time(self, name: str) -> float:
        """Get average time for an operation."""
        if name in self.metrics and self.metrics[name]:
            return np.mean(self.metrics[name])
        return 0.0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics."""
        if self.memory_tracker:
            return self.memory_tracker.get_stats()
        return {}
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        report = {
            'timing': {name: self.get_average_time(name) for name in self.metrics},
            'memory': self.get_memory_stats(),
            'summary': {
                'total_operations': len(self.metrics),
                'total_time': sum(sum(times) for times in self.metrics.values())
            }
        }
        return report


class MemoryTracker:
    """Advanced memory tracking and optimization."""
    
    def __init__(self):
        self.memory_history = []
        self.peak_memory = 0
        
    def track_memory(self):
        """Track current memory usage."""
        if torch.cuda.is_available():
            current_memory = torch.cuda.memory_allocated() / 1024**3  # GB
            self.memory_history.append(current_memory)
            self.peak_memory = max(self.peak_memory, current_memory)
        else:
            # CPU memory tracking
            process = psutil.Process()
            current_memory = process.memory_info().rss / 1024**3  # GB
            self.memory_history.append(current_memory)
            self.peak_memory = max(self.peak_memory, current_memory)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        if not self.memory_history:
            return {}
        
        return {
            'current': self.memory_history[-1] if self.memory_history else 0,
            'peak': self.peak_memory,
            'average': np.mean(self.memory_history),
            'history': self.memory_history[-100:]  # Last 100 measurements
        }
    
    def clear_history(self):
        """Clear memory history."""
        self.memory_history.clear()
        self.peak_memory = 0


class OptimizedDiffusionModelManager:
    """Optimized diffusion model manager with enhanced performance."""
    
    def __init__(self, config: OptimizedDiffusionConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger = self._setup_logging()
        self.performance_monitor = PerformanceMonitor(config.enable_performance_monitoring)
        
        # Initialize components
        self.pipeline = None
        self.unet = None
        self.vae = None
        self.text_encoder = None
        self.tokenizer = None
        self.scheduler = None
        self.ema_model = None
        
        # Model cache
        self.model_cache = {}
        
        self._load_models()
        self._apply_optimizations()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup optimized logging."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_models(self):
        """Load models with optimization and caching."""
        try:
            self.performance_monitor.start_timer("model_loading")
            
            if self.config.use_pipeline:
                self._load_pipeline()
            else:
                self._load_individual_components()
            
            # Load EMA model if enabled
            if self.config.use_ema:
                self._setup_ema_model()
            
            loading_time = self.performance_monitor.end_timer("model_loading")
            self.logger.info(f"✅ Models loaded successfully in {loading_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading models: {e}")
            raise
    
    def _load_pipeline(self):
        """Load pipeline with optimizations."""
        # Check cache first
        cache_key = f"{self.config.model_name}_{self.config.use_fp16}"
        if self.config.enable_model_caching and cache_key in self.model_cache:
            self.pipeline = self.model_cache[cache_key]
            self.logger.info("✅ Loaded pipeline from cache")
        else:
            # Load from Hugging Face
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.config.model_name,
                torch_dtype=torch.float16 if self.config.use_fp16 else torch.float32,
                safety_checker=None,
                requires_safety_checker=False,
                cache_dir=self.config.cache_dir
            )
            
            # Cache the model
            if self.config.enable_model_caching:
                self.model_cache[cache_key] = self.pipeline
                self.logger.info("✅ Cached pipeline")
        
        # Move to device
        self.pipeline = self.pipeline.to(self.device)
        
        # Extract components
        self.unet = self.pipeline.unet
        self.vae = self.pipeline.vae
        self.text_encoder = self.pipeline.text_encoder
        self.tokenizer = self.pipeline.tokenizer
        self.scheduler = self.pipeline.scheduler
        
        # Apply torch.compile if enabled
        if self.config.use_compile and hasattr(torch, 'compile'):
            try:
                self.unet = torch.compile(self.unet, mode="reduce-overhead")
                self.logger.info("✅ Applied torch.compile optimization")
            except Exception as e:
                self.logger.warning(f"⚠️ torch.compile failed: {e}")
    
    def _setup_ema_model(self):
        """Setup Exponential Moving Average model."""
        if self.unet:
            self.ema_model = EMAModel(self.unet.parameters())
            self.logger.info("✅ EMA model initialized")
    
    def _apply_optimizations(self):
        """Apply comprehensive optimizations."""
        if not self.pipeline:
            return
        
        optimizations_applied = []
        
        # Memory optimizations
        if self.config.enable_attention_slicing and hasattr(self.pipeline, 'enable_attention_slicing'):
            self.pipeline.enable_attention_slicing()
            optimizations_applied.append("attention_slicing")
        
        if self.config.enable_vae_slicing and hasattr(self.pipeline, 'enable_vae_slicing'):
            self.pipeline.enable_vae_slicing()
            optimizations_applied.append("vae_slicing")
        
        if self.config.enable_vae_tiling and hasattr(self.pipeline, 'enable_vae_tiling'):
            self.pipeline.enable_vae_tiling()
            optimizations_applied.append("vae_tiling")
        
        if self.config.enable_xformers_memory_efficient_attention:
            try:
                self.pipeline.enable_xformers_memory_efficient_attention()
                optimizations_applied.append("xformers_attention")
            except Exception as e:
                self.logger.warning(f"⚠️ XFormers not available: {e}")
        
        if self.config.enable_model_cpu_offload and hasattr(self.pipeline, 'enable_model_cpu_offload'):
            self.pipeline.enable_model_cpu_offload()
            optimizations_applied.append("cpu_offload")
        
        if self.config.enable_sequential_cpu_offload and hasattr(self.pipeline, 'enable_sequential_cpu_offload'):
            self.pipeline.enable_sequential_cpu_offload()
            optimizations_applied.append("sequential_cpu_offload")
        
        # Performance optimizations
        if self.config.use_channels_last and hasattr(self.pipeline, 'to'):
            self.pipeline = self.pipeline.to(memory_format=torch.channels_last)
            optimizations_applied.append("channels_last")
        
        if self.config.use_gradient_checkpointing:
            self.unet.enable_gradient_checkpointing()
            optimizations_applied.append("gradient_checkpointing")
        
        self.logger.info(f"✅ Applied optimizations: {', '.join(optimizations_applied)}")
    
    @contextmanager
    def memory_optimization_context(self):
        """Context manager for memory optimization."""
        if self.performance_monitor.memory_tracker:
            self.performance_monitor.memory_tracker.track_memory()
        
        try:
            yield
        finally:
            # Force garbage collection
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
    
    def generate_image_optimized(
        self,
        prompt: str,
        negative_prompt: str = "",
        num_images: int = 1,
        **kwargs
    ) -> List[PIL.Image.Image]:
        """Generate images with optimized performance."""
        try:
            self.performance_monitor.start_timer("image_generation")
            
            with self.memory_optimization_context():
                # Override config with kwargs
                generation_kwargs = {
                    'num_inference_steps': self.config.num_inference_steps,
                    'guidance_scale': self.config.guidance_scale,
                    'eta': self.config.eta,
                    'height': self.config.height,
                    'width': self.config.width,
                    'num_images_per_prompt': num_images,
                    **kwargs
                }
                
                # Generate images
                if self.pipeline:
                    images = self.pipeline(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        **generation_kwargs
                    ).images
                else:
                    images = self._generate_with_components(
                        prompt, negative_prompt, **generation_kwargs
                    )
                
                generation_time = self.performance_monitor.end_timer("image_generation")
                self.logger.info(f"✅ Generated {len(images)} images in {generation_time:.2f}s")
                
                return images
                
        except Exception as e:
            self.logger.error(f"❌ Error generating images: {e}")
            raise
    
    def generate_batch_optimized(
        self,
        prompts: List[str],
        negative_prompts: Optional[List[str]] = None,
        **kwargs
    ) -> Tuple[List[PIL.Image.Image], List[float]]:
        """Generate images in batches with optimization."""
        if negative_prompts is None:
            negative_prompts = [""] * len(prompts)
        
        all_images = []
        generation_times = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=min(len(prompts), 4)) as executor:
            future_to_prompt = {
                executor.submit(self.generate_image_optimized, prompt, neg_prompt, 1, **kwargs): i
                for i, (prompt, neg_prompt) in enumerate(zip(prompts, negative_prompts))
            }
            
            for future in as_completed(future_to_prompt):
                try:
                    images = future.result()
                    all_images.extend(images)
                    generation_times.append(self.performance_monitor.get_average_time("image_generation"))
                except Exception as e:
                    self.logger.error(f"❌ Error in batch generation: {e}")
        
        return all_images, generation_times
    
    def get_optimized_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information with performance metrics."""
        info = {
            'config': self.config.__dict__,
            'device': str(self.device),
            'models_loaded': {
                'pipeline': self.pipeline is not None,
                'unet': self.unet is not None,
                'vae': self.vae is not None,
                'text_encoder': self.text_encoder is not None,
                'tokenizer': self.tokenizer is not None,
                'scheduler': self.scheduler is not None,
                'ema_model': self.ema_model is not None
            },
            'performance': self.performance_monitor.generate_report() if self.performance_monitor else {},
            'memory': self.performance_monitor.get_memory_stats() if self.performance_monitor else {}
        }
        
        # Parameter counts
        if self.unet:
            info['unet_params'] = sum(p.numel() for p in self.unet.parameters())
            info['unet_trainable_params'] = sum(p.numel() for p in self.unet.parameters() if p.requires_grad)
        
        if self.vae:
            info['vae_params'] = sum(p.numel() for p in self.vae.parameters())
        
        if self.text_encoder:
            info['text_encoder_params'] = sum(p.numel() for p in self.text_encoder.parameters())
        
        return info


def create_optimized_diffusion_system(
    diffusion_config: OptimizedDiffusionConfig,
    training_config: OptimizedTrainingConfig
) -> OptimizedDiffusionModelManager:
    """Create an optimized diffusion system."""
    return OptimizedDiffusionModelManager(diffusion_config)


# Example usage and optimization functions
def optimize_for_inference(config: OptimizedDiffusionConfig) -> OptimizedDiffusionConfig:
    """Optimize configuration for inference."""
    config.use_compile = True
    config.use_fp16 = True
    config.enable_attention_slicing = True
    config.enable_vae_slicing = True
    config.enable_xformers_memory_efficient_attention = True
    config.use_channels_last = True
    return config


def optimize_for_training(config: OptimizedDiffusionConfig) -> OptimizedDiffusionConfig:
    """Optimize configuration for training."""
    config.use_gradient_checkpointing = True
    config.use_ema = True
    config.use_amp = True
    config.enable_model_cpu_offload = True
    return config


def optimize_for_memory(config: OptimizedDiffusionConfig) -> OptimizedDiffusionConfig:
    """Optimize configuration for memory efficiency."""
    config.enable_attention_slicing = True
    config.enable_vae_slicing = True
    config.enable_vae_tiling = True
    config.enable_sequential_cpu_offload = True
    config.max_batch_size = 1
    return config





