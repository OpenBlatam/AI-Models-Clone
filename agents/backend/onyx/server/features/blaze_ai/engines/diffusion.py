"""
Refactored Diffusion Engine for the Blaze AI module.

This module provides a high-performance, production-ready diffusion engine with
improved architecture, better error handling, and enhanced performance optimizations.
"""

from __future__ import annotations

import asyncio
import gc
import time
from typing import Any, Dict, List, Optional, Union, Tuple, Protocol
from dataclasses import dataclass, field
from pathlib import Path
from contextlib import asynccontextmanager
import weakref
import io
import base64

import torch
import torch.nn.functional as F
from diffusers import (
    StableDiffusionPipeline, StableDiffusionImg2ImgPipeline,
    StableDiffusionInpaintPipeline, StableDiffusionUpscalePipeline,
    DPMSolverMultistepScheduler, EulerDiscreteScheduler, DDIMScheduler,
    LMSDiscreteScheduler, PNDMScheduler, HeunDiscreteScheduler, UniPCMultistepScheduler
)
from PIL import Image
import numpy as np

from . import Engine, EngineStatus
from ..core.interfaces import CoreConfig
from ..utils.logging import get_logger

# =============================================================================
# Protocols and Interfaces
# =============================================================================

class PipelineProvider(Protocol):
    """Protocol for pipeline providers."""
    async def get_pipeline(self, pipeline_type: str) -> Any: ...
    async def unload_pipeline(self, pipeline_type: str) -> None: ...
    def is_pipeline_loaded(self, pipeline_type: str) -> bool: ...

class ImageProcessor(Protocol):
    """Protocol for image processing operations."""
    async def process_image(self, image: Image.Image, operation: str, params: Dict[str, Any]) -> Image.Image: ...
    async def validate_image(self, image: Image.Image) -> bool: ...

# =============================================================================
# Enhanced Data Classes
# =============================================================================

@dataclass
class DiffusionConfig:
    """Enhanced diffusion engine configuration."""
    model_id: str = "runwayml/stable-diffusion-v1-5"
    model_path: Optional[str] = None
    device: str = "auto"
    precision: str = "float16"
    enable_amp: bool = True
    cache_capacity: int = 100
    max_batch_size: int = 4
    enable_xformers: bool = True
    enable_attention_slicing: bool = True
    enable_vae_slicing: bool = True
    enable_model_cpu_offload: bool = True
    enable_sequential_cpu_offload: bool = False
    enable_memory_efficient_attention: bool = True
    enable_gradient_checkpointing: bool = False
    enable_model_compilation: bool = True
    enable_quantization: bool = False
    quantization_bits: int = 8
    enable_safety_checker: bool = True
    enable_watermark: bool = False
    enable_progress_bar: bool = False
    scheduler_type: str = "dpm"  # dpm, euler, ddim, lms, pndm, heun, unipc
    guidance_scale: float = 7.5
    num_inference_steps: int = 50
    enable_negative_prompt: bool = True
    max_concurrent_requests: int = 5
    request_timeout: float = 60.0
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.model_id and not self.model_path:
            errors.append("Either model_id or model_path must be specified")
        
        if self.max_batch_size <= 0:
            errors.append("max_batch_size must be positive")
        
        if self.guidance_scale <= 0.0:
            errors.append("guidance_scale must be positive")
        
        if self.num_inference_steps <= 0:
            errors.append("num_inference_steps must be positive")
        
        if self.request_timeout <= 0.0:
            errors.append("request_timeout must be positive")
        
        if self.quantization_bits not in [4, 8]:
            errors.append("quantization_bits must be 4 or 8")
        
        return errors

@dataclass
class GenerationRequest:
    """Enhanced generation request structure."""
    prompt: str
    negative_prompt: Optional[str] = None
    guidance_scale: Optional[float] = None
    num_inference_steps: Optional[int] = None
    seed: Optional[int] = None
    width: int = 512
    height: int = 512
    batch_size: int = 1
    stream: bool = False
    batch_id: Optional[str] = None
    priority: int = 1
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive")
        
        if self.batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        if self.priority < 1 or self.priority > 10:
            raise ValueError("Priority must be between 1 and 10")

@dataclass
class GenerationResponse:
    """Enhanced generation response structure."""
    images: List[Image.Image]
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    model_name: Optional[str] = None
    batch_id: Optional[str] = None
    seed: Optional[int] = None
    usage: Optional[Dict[str, Any]] = None

@dataclass
class Img2ImgRequest:
    """Image-to-image generation request."""
    prompt: str
    image: Image.Image
    strength: float = 0.8
    guidance_scale: Optional[float] = None
    num_inference_steps: Optional[int] = None
    seed: Optional[int] = None
    batch_size: int = 1
    batch_id: Optional[str] = None
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if not (0.0 <= self.strength <= 1.0):
            raise ValueError("Strength must be between 0.0 and 1.0")

@dataclass
class InpaintRequest:
    """Inpainting request."""
    prompt: str
    image: Image.Image
    mask: Image.Image
    guidance_scale: Optional[float] = None
    num_inference_steps: Optional[int] = None
    seed: Optional[int] = None
    batch_id: Optional[str] = None
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.prompt.strip():
            raise ValueError("Prompt cannot be empty")

# =============================================================================
# Enhanced Scheduler Factory
# =============================================================================

class EnhancedSchedulerFactory:
    """Enhanced scheduler factory with better error handling and configuration."""
    
    SCHEDULER_MAP = {
        "dpm": DPMSolverMultistepScheduler,
        "euler": EulerDiscreteScheduler,
        "ddim": DDIMScheduler,
        "lms": LMSDiscreteScheduler,
        "pndm": PNDMScheduler,
        "heun": HeunDiscreteScheduler,
        "unipc": UniPCMultistepScheduler
    }
    
    @classmethod
    def create_scheduler(cls, scheduler_type: str, **kwargs) -> Any:
        """Create a scheduler with enhanced error handling."""
        if scheduler_type not in cls.SCHEDULER_MAP:
            raise ValueError(f"Unknown scheduler type: {scheduler_type}. Available: {list(cls.SCHEDULER_MAP.keys())}")
        
        try:
            scheduler_class = cls.SCHEDULER_MAP[scheduler_type]
            return scheduler_class(**kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to create scheduler {scheduler_type}: {e}")
    
    @classmethod
    def get_available_schedulers(cls) -> List[str]:
        """Get list of available scheduler types."""
        return list(cls.SCHEDULER_MAP.keys())
    
    @classmethod
    def get_scheduler_info(cls, scheduler_type: str) -> Dict[str, Any]:
        """Get information about a specific scheduler."""
        if scheduler_type not in cls.SCHEDULER_MAP:
            return {"error": f"Unknown scheduler type: {scheduler_type}"}
        
        scheduler_class = cls.SCHEDULER_MAP[scheduler_type]
        return {
            "name": scheduler_type,
            "class": scheduler_class.__name__,
            "module": scheduler_class.__module__,
            "description": scheduler_class.__doc__ or "No description available"
        }

# =============================================================================
# Enhanced Diffusion Model Cache
# =============================================================================

class EnhancedDiffusionModelCache:
    """Intelligent diffusion model caching with advanced features."""
    
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache: Dict[str, Any] = {}
        self.access_order: List[str] = []
        self.memory_usage: Dict[str, int] = {}
        self.access_count: Dict[str, int] = {}
        self.last_access: Dict[str, float] = {}
        self.model_types: Dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(600)  # Cleanup every 10 minutes
                await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue
                continue
    
    async def _perform_cleanup(self):
        """Perform cache cleanup."""
        async with self._lock:
            current_time = time.time()
            
            # Remove items that haven't been accessed in 2 hours
            expired_keys = [
                key for key, last_access in self.last_access.items()
                if current_time - last_access > 7200
            ]
            
            for key in expired_keys:
                await self._remove_item(key)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from cache with enhanced tracking."""
        async with self._lock:
            if key in self.cache:
                # Update access tracking
                self.access_count[key] = self.access_count.get(key, 0) + 1
                self.last_access[key] = time.time()
                
                # Move to end (most recently used)
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                return self.cache[key]
            return None
    
    async def put(self, key: str, value: Any, memory_size: int = 0, model_type: str = "unknown"):
        """Put item in cache with enhanced management."""
        async with self._lock:
            if key in self.cache:
                # Update existing
                if key in self.access_order:
                    self.access_order.remove(key)
            elif len(self.cache) >= self.capacity:
                # Evict least valuable item
                await self._evict_least_valuable()
            
            self.cache[key] = value
            self.access_order.append(key)
            self.memory_usage[key] = memory_size
            self.access_count[key] = 1
            self.last_access[key] = time.time()
            self.model_types[key] = model_type
    
    async def _evict_least_valuable(self):
        """Evict least valuable item based on access pattern and memory usage."""
        if not self.access_order:
            return
        
        # Calculate value score for each item
        item_scores = {}
        current_time = time.time()
        
        for key in self.cache:
            access_score = self.access_count.get(key, 0) / max(current_time - self.last_access.get(key, 0), 1)
            memory_score = 1.0 / (self.memory_usage.get(key, 1) + 1)
            item_scores[key] = access_score * memory_score
        
        # Remove least valuable item
        if item_scores:
            least_valuable = min(item_scores.keys(), key=lambda k: item_scores[k])
            await self._remove_item(least_valuable)
    
    async def _remove_item(self, key: str):
        """Remove item from cache."""
        if key in self.cache:
            # Clear model from memory
            model = self.cache[key]
            if hasattr(model, 'to'):
                model.to('cpu')
            del self.cache[key]
            
            del self.memory_usage[key]
            del self.access_count[key]
            del self.last_access[key]
            del self.model_types[key]
            
            if key in self.access_order:
                self.access_order.remove(key)
    
    async def invalidate(self, key: str) -> bool:
        """Invalidate a specific cache entry."""
        async with self._lock:
            if key in self.cache:
                await self._remove_item(key)
                return True
            return False
    
    async def clear(self):
        """Clear all cached items."""
        async with self._lock:
            for key in list(self.cache.keys()):
                await self._remove_item(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        total_memory = sum(self.memory_usage.values())
        total_accesses = sum(self.access_count.values())
        
        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "total_memory_bytes": total_memory,
            "total_accesses": total_accesses,
            "average_accesses_per_item": total_accesses / len(self.cache) if self.cache else 0.0,
            "memory_efficiency": len(self.cache) / self.capacity if self.capacity > 0 else 0.0,
            "model_types": dict(self.model_types)
        }
    
    async def shutdown(self):
        """Shutdown the cache."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

# =============================================================================
# Enhanced Image Processing Utilities
# =============================================================================

class EnhancedImageProcessor:
    """Enhanced image processing utilities."""
    
    @staticmethod
    async def validate_image(image: Image.Image) -> bool:
        """Validate image for processing."""
        try:
            # Check if image is valid
            image.verify()
            return True
        except Exception:
            return False
    
    @staticmethod
    async def resize_image(image: Image.Image, width: int, height: int, 
                          resample: Image.Resampling = Image.Resampling.LANCZOS) -> Image.Image:
        """Resize image with validation."""
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        
        return image.resize((width, height), resample)
    
    @staticmethod
    async def convert_to_rgb(image: Image.Image) -> Image.Image:
        """Convert image to RGB format."""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    
    @staticmethod
    async def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
        """Convert PIL image to base64 string."""
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    @staticmethod
    async def base64_to_image(base64_str: str) -> Image.Image:
        """Convert base64 string to PIL image."""
        img_data = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_data))
        return img

# =============================================================================
# Refactored Diffusion Engine Implementation
# =============================================================================

class DiffusionEngine(Engine):
    """Refactored high-performance diffusion engine with enhanced features."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.diffusion_config = DiffusionConfig(**config)
        
        # Validate configuration
        errors = self.diffusion_config.validate()
        if errors:
            raise ValueError(f"Invalid diffusion configuration: {errors}")
        
        # Initialize components
        self.model_cache = EnhancedDiffusionModelCache(self.diffusion_config.cache_capacity)
        self.image_processor = EnhancedImageProcessor()
        
        # Pipeline state
        self.pipelines: Dict[str, Any] = {}
        self.device: Optional[str] = None
        self.is_quantized: bool = False
        self.is_compiled: bool = False
        
        # Request management
        self._request_semaphore = asyncio.Semaphore(self.diffusion_config.max_concurrent_requests)
        self._pipeline_lock = asyncio.Lock()
        
        # Performance tracking
        self._performance_metrics = {
            "total_generations": 0,
            "total_images_generated": 0,
            "average_generation_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "successful_generations": 0,
            "failed_generations": 0
        }
    
    async def _initialize_engine(self) -> None:
        """Initialize the diffusion engine with enhanced error handling."""
        try:
            self.logger.info(f"Initializing diffusion engine: {self.diffusion_config.model_id}")
            
            # Determine device
            self.device = await self._determine_device()
            self.logger.info(f"Using device: {self.device}")
            
            # Load base pipeline
            await self._load_base_pipeline()
            
            # Apply optimizations
            await self._apply_optimizations()
            
            self.logger.info("Diffusion engine initialization complete")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize diffusion engine: {e}")
            raise
    
    async def _determine_device(self) -> str:
        """Determine the best device to use."""
        if self.diffusion_config.device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return self.diffusion_config.device
    
    async def _load_base_pipeline(self) -> None:
        """Load the base diffusion pipeline."""
        try:
            model_path = self.diffusion_config.model_path or self.diffusion_config.model_id
            
            # Load base pipeline
            pipeline = StableDiffusionPipeline.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.diffusion_config.precision == "float16" else torch.float32,
                safety_checker=None if not self.diffusion_config.enable_safety_checker else None,
                requires_safety_checker=self.diffusion_config.enable_safety_checker
            )
            
            # Move to device
            if self.device != "auto" and hasattr(pipeline, 'to'):
                pipeline.to(self.device)
            
            # Store pipeline
            self.pipelines["base"] = pipeline
            
            self.logger.info(f"Base pipeline loaded: {model_path}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load base pipeline: {e}")
    
    async def _apply_optimizations(self) -> None:
        """Apply various optimizations to the pipeline."""
        try:
            base_pipeline = self.pipelines.get("base")
            if not base_pipeline:
                return
            
            # Memory optimizations
            if self.diffusion_config.enable_attention_slicing:
                base_pipeline.enable_attention_slicing()
                self.logger.info("Attention slicing enabled")
            
            if self.diffusion_config.enable_vae_slicing:
                base_pipeline.enable_vae_slicing()
                self.logger.info("VAE slicing enabled")
            
            if self.diffusion_config.enable_model_cpu_offload:
                base_pipeline.enable_model_cpu_offload()
                self.logger.info("Model CPU offload enabled")
            
            if self.diffusion_config.enable_sequential_cpu_offload:
                base_pipeline.enable_sequential_cpu_offload()
                self.logger.info("Sequential CPU offload enabled")
            
            # xFormers optimization
            if self.diffusion_config.enable_xformers and self.device == "cuda":
                try:
                    base_pipeline.enable_xformers_memory_efficient_attention()
                    self.logger.info("xFormers memory efficient attention enabled")
                except Exception as e:
                    self.logger.warning(f"xFormers optimization failed: {e}")
            
            # Memory efficient attention
            if self.diffusion_config.enable_memory_efficient_attention and self.device == "cuda":
                try:
                    base_pipeline.enable_memory_efficient_attention()
                    self.logger.info("Memory efficient attention enabled")
                except Exception as e:
                    self.logger.warning(f"Memory efficient attention failed: {e}")
            
            # Gradient checkpointing
            if self.diffusion_config.enable_gradient_checkpointing:
                base_pipeline.enable_gradient_checkpointing()
                self.logger.info("Gradient checkpointing enabled")
            
            # Quantization
            if self.diffusion_config.enable_quantization:
                await self._quantize_pipeline()
            
            # Model compilation
            if self.diffusion_config.enable_model_compilation and hasattr(torch, "compile") and self.device == "cuda":
                await self._compile_pipeline()
            
            # Set scheduler
            await self._set_scheduler()
            
        except Exception as e:
            self.logger.warning(f"Some optimizations failed: {e}")
    
    async def _quantize_pipeline(self) -> None:
        """Quantize the pipeline for reduced memory usage."""
        try:
            if self.diffusion_config.quantization_bits == 8:
                # 8-bit quantization
                for component in ["unet", "vae", "text_encoder"]:
                    if hasattr(self.pipelines["base"], component):
                        model = getattr(self.pipelines["base"], component)
                        if hasattr(model, "to"):
                            model = torch.quantization.quantize_dynamic(
                                model, {torch.nn.Linear}, dtype=torch.qint8
                            )
                            setattr(self.pipelines["base"], component, model)
            
            elif self.diffusion_config.quantization_bits == 4:
                # 4-bit quantization using bitsandbytes
                try:
                    import bitsandbytes as bnb
                    for component in ["unet", "vae", "text_encoder"]:
                        if hasattr(self.pipelines["base"], component):
                            model = getattr(self.pipelines["base"], component)
                            if hasattr(model, "to"):
                                model = bnb.nn.Linear4bit.from_pretrained(
                                    model,
                                    load_in_4bit=True,
                                    bnb_4bit_compute_dtype=torch.float16
                                )
                                setattr(self.pipelines["base"], component, model)
                except ImportError:
                    self.logger.warning("bitsandbytes not available, skipping 4-bit quantization")
                    return
            
            self.is_quantized = True
            self.logger.info(f"Pipeline quantized to {self.diffusion_config.quantization_bits} bits")
            
        except Exception as e:
            self.logger.warning(f"Quantization failed: {e}")
    
    async def _compile_pipeline(self) -> None:
        """Compile the pipeline with PyTorch 2.0+."""
        try:
            for component in ["unet", "vae", "text_encoder"]:
                if hasattr(self.pipelines["base"], component):
                    model = getattr(self.pipelines["base"], component)
                    if hasattr(model, "to"):
                        compiled_model = torch.compile(model)
                        setattr(self.pipelines["base"], component, compiled_model)
            
            self.is_compiled = True
            self.logger.info("Pipeline compiled with torch.compile")
            
        except Exception as e:
            self.logger.warning(f"Pipeline compilation failed: {e}")
    
    async def _set_scheduler(self) -> None:
        """Set the scheduler for the pipeline."""
        try:
            scheduler = EnhancedSchedulerFactory.create_scheduler(
                self.diffusion_config.scheduler_type
            )
            self.pipelines["base"].scheduler = scheduler
            self.logger.info(f"Scheduler set to: {self.diffusion_config.scheduler_type}")
            
        except Exception as e:
            self.logger.warning(f"Failed to set scheduler: {e}")
    
    async def _execute_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute diffusion operation with enhanced error handling."""
        if operation == "generate":
            return await self._generate_image(params)
        elif operation == "generate_batch":
            return await self._generate_batch(params)
        elif operation == "img2img":
            return await self._generate_img2img(params)
        elif operation == "inpaint":
            return await self._generate_inpaint(params)
        elif operation == "upscale":
            return await self._generate_upscale(params)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    async def _generate_image(self, params: Dict[str, Any]) -> GenerationResponse:
        """Generate image using the diffusion model with enhanced features."""
        if "base" not in self.pipelines:
            raise RuntimeError("Pipeline not initialized")
        
        request = GenerationRequest(**params)
        start_time = time.time()
        
        try:
            async with self._request_semaphore:
                # Check cache first
                cache_key = self._generate_cache_key(request)
                cached_result = await self.model_cache.get(cache_key)
                
                if cached_result:
                    self._performance_metrics["cache_hits"] += 1
                    return cached_result
                
                self._performance_metrics["cache_misses"] += 1
                
                # Generate image
                result = await self._perform_generation(request)
                
                # Create response
                response = GenerationResponse(
                    images=result["images"],
                    metadata=result["metadata"],
                    processing_time=time.time() - start_time,
                    model_name=self.diffusion_config.model_id,
                    batch_id=request.batch_id,
                    seed=result.get("seed"),
                    usage=result.get("usage")
                )
                
                # Cache the result
                await self.model_cache.put(
                    cache_key, 
                    response, 
                    memory_size=len(str(response)),
                    model_type="generation"
                )
                
                # Update metrics
                self._update_generation_metrics(response)
                
                return response
                
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            self._performance_metrics["failed_generations"] += 1
            raise
    
    def _generate_cache_key(self, request: GenerationRequest) -> str:
        """Generate cache key for the request."""
        import hashlib
        import json
        
        # Create deterministic key
        key_data = {
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "guidance_scale": request.guidance_scale or self.diffusion_config.guidance_scale,
            "num_inference_steps": request.num_inference_steps or self.diffusion_config.num_inference_steps,
            "seed": request.seed,
            "width": request.width,
            "height": request.height,
            "batch_size": request.batch_size
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _perform_generation(self, request: GenerationRequest) -> Dict[str, Any]:
        """Perform the actual image generation."""
        async with self._pipeline_lock:
            # Set seed if provided
            if request.seed is not None:
                torch.manual_seed(request.seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(request.seed)
            
            # Generation parameters
            gen_kwargs = {
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "guidance_scale": request.guidance_scale or self.diffusion_config.guidance_scale,
                "num_inference_steps": request.num_inference_steps or self.diffusion_config.num_inference_steps,
                "width": request.width,
                "height": request.height,
                "num_images_per_prompt": request.batch_size
            }
            
            # Generate
            with torch.no_grad():
                if self.diffusion_config.enable_amp and self.device == "cuda":
                    with torch.cuda.amp.autocast():
                        images = self.pipelines["base"](**gen_kwargs).images
                else:
                    images = self.pipelines["base"](**gen_kwargs).images
            
            # Calculate usage
            usage = {
                "prompt_tokens": len(request.prompt.split()),
                "images_generated": len(images),
                "inference_steps": gen_kwargs["num_inference_steps"]
            }
            
            return {
                "images": images,
                "seed": request.seed,
                "usage": usage,
                "metadata": {
                    "model_id": self.diffusion_config.model_id,
                    "device": self.device,
                    "is_quantized": self.is_quantized,
                    "is_compiled": self.is_compiled,
                    "scheduler": self.diffusion_config.scheduler_type
                }
            }
    
    def _update_generation_metrics(self, response: GenerationResponse):
        """Update performance metrics."""
        self._performance_metrics["total_generations"] += 1
        self._performance_metrics["total_images_generated"] += len(response.images)
        self._performance_metrics["successful_generations"] += 1
        
        # Update average generation time
        current_avg = self._performance_metrics["average_generation_time"]
        total_gens = self._performance_metrics["total_generations"]
        new_avg = (current_avg * (total_gens - 1) + response.processing_time) / total_gens
        self._performance_metrics["average_generation_time"] = new_avg
    
    async def _generate_batch(self, params: Dict[str, Any]) -> List[GenerationResponse]:
        """Generate images for multiple prompts in batch."""
        requests = params.get("requests", [])
        if not requests:
            raise ValueError("No requests provided for batch generation")
        
        results = []
        for i, request_data in enumerate(requests):
            try:
                request = GenerationRequest(**request_data)
                request.batch_id = f"batch_{i}"
                result = await self._generate_image({"prompt": request.prompt, **request_data})
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch generation failed for request {i}: {e}")
                # Create error response
                results.append(GenerationResponse(
                    images=[],
                    batch_id=f"batch_{i}",
                    processing_time=0.0,
                    metadata={"error": str(e)}
                ))
        
        return results
    
    async def _generate_img2img(self, params: Dict[str, Any]) -> GenerationResponse:
        """Generate image-to-image transformation."""
        if "base" not in self.pipelines:
            raise RuntimeError("Pipeline not initialized")
        
        request = Img2ImgRequest(**params)
        start_time = time.time()
        
        try:
            # Load img2img pipeline if not loaded
            if "img2img" not in self.pipelines:
                await self._load_img2img_pipeline()
            
            async with self._pipeline_lock:
                # Set seed if provided
                if request.seed is not None:
                    torch.manual_seed(request.seed)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed(request.seed)
                
                # Generation parameters
                gen_kwargs = {
                    "prompt": request.prompt,
                    "image": request.image,
                    "strength": request.strength,
                    "guidance_scale": request.guidance_scale or self.diffusion_config.guidance_scale,
                    "num_inference_steps": request.num_inference_steps or self.diffusion_config.num_inference_steps,
                    "num_images_per_prompt": request.batch_size
                }
                
                # Generate
                with torch.no_grad():
                    if self.diffusion_config.enable_amp and self.device == "cuda":
                        with torch.cuda.amp.autocast():
                            images = self.pipelines["img2img"](**gen_kwargs).images
                    else:
                        images = self.pipelines["img2img"](**gen_kwargs).images
                
                # Create response
                response = GenerationResponse(
                    images=images,
                    metadata={
                        "operation": "img2img",
                        "strength": request.strength,
                        "model_id": self.diffusion_config.model_id
                    },
                    processing_time=time.time() - start_time,
                    model_name=self.diffusion_config.model_id,
                    batch_id=request.batch_id,
                    seed=request.seed
                )
                
                return response
                
        except Exception as e:
            self.logger.error(f"Image-to-image generation failed: {e}")
            raise
    
    async def _load_img2img_pipeline(self) -> None:
        """Load the img2img pipeline."""
        try:
            model_path = self.diffusion_config.model_path or self.diffusion_config.model_id
            
            pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.diffusion_config.precision == "float16" else torch.float32,
                safety_checker=None if not self.diffusion_config.enable_safety_checker else None
            )
            
            if self.device != "auto" and hasattr(pipeline, 'to'):
                pipeline.to(self.device)
            
            self.pipelines["img2img"] = pipeline
            self.logger.info("Img2img pipeline loaded")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load img2img pipeline: {e}")
    
    async def _generate_inpaint(self, params: Dict[str, Any]) -> GenerationResponse:
        """Generate inpainting transformation."""
        # Implementation for inpainting
        raise NotImplementedError("Inpainting not yet implemented")
    
    async def _generate_upscale(self, params: Dict[str, Any]) -> GenerationResponse:
        """Generate image upscaling."""
        # Implementation for upscaling
        raise NotImplementedError("Upscaling not yet implemented")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            **self._performance_metrics,
            "cache_stats": self.model_cache.get_stats(),
            "pipeline_info": {
                "device": self.device,
                "is_quantized": self.is_quantized,
                "is_compiled": self.is_compiled,
                "precision": self.diffusion_config.precision,
                "scheduler": self.diffusion_config.scheduler_type,
                "loaded_pipelines": list(self.pipelines.keys())
            }
        }
    
    async def shutdown(self):
        """Enhanced shutdown with cleanup."""
        self.logger.info("Shutting down diffusion engine...")
        
        # Clear cache
        await self.model_cache.shutdown()
        
        # Clear pipelines from memory
        for name, pipeline in self.pipelines.items():
            if hasattr(pipeline, 'to'):
                pipeline.to('cpu')
            del pipeline
        
        self.pipelines.clear()
        
        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        await super().shutdown()
        self.logger.info("Diffusion engine shutdown complete")


