#!/usr/bin/env python3
"""
Enhanced Diffusion Models System using Diffusers Library

Comprehensive system for implementing and working with diffusion models
using the Hugging Face Diffusers library, with enhanced pipeline-specific
implementations and integration to the tokenization and sequence handling system.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from diffusers import (
    StableDiffusionPipeline, StableDiffusionXLPipeline, StableDiffusionImg2ImgPipeline,
    StableDiffusionInpaintPipeline, StableDiffusionControlNetPipeline,
    DDIMScheduler, DDPMScheduler, PNDMScheduler, LMSDiscreteScheduler,
    EulerDiscreteScheduler, EulerAncestralDiscreteScheduler, HeunDiscreteScheduler,
    DPMSolverMultistepScheduler, DPMSolverSinglestepScheduler, UniPCMultistepScheduler,
    AutoencoderKL, UNet2DConditionModel, ControlNetModel,
    DiffusionPipeline, TextToImagePipeline, ImageToImagePipeline
)
from diffusers.utils import randn_tensor, logging
from transformers import CLIPTextModel, T5EncoderModel, CLIPVisionModel
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import time
import hashlib
from functools import lru_cache, wraps
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
from collections import defaultdict, Counter
import re
import unicodedata
from enum import Enum
from PIL import Image
import requests
from io import BytesIO

# Import our tokenization system
from .tokenization_sequence_system import (
    TokenizationSequenceSystem, TokenizerConfig, SequenceConfig, TextProcessingConfig,
    TokenizerType, SequenceStrategy
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiffusionModelType(Enum):
    """Supported diffusion model types."""
    STABLE_DIFFUSION = "stable_diffusion"
    STABLE_DIFFUSION_XL = "stable_diffusion_xl"
    STABLE_DIFFUSION_IMG2IMG = "stable_diffusion_img2img"
    STABLE_DIFFUSION_INPAINT = "stable_diffusion_inpaint"
    STABLE_DIFFUSION_CONTROLNET = "stable_diffusion_controlnet"
    CUSTOM = "custom"

class PipelineType(Enum):
    """Specific pipeline types for detailed understanding."""
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    INPAINTING = "inpainting"
    CONTROLNET = "controlnet"
    REFINER = "refiner"
    CASCADE = "cascade"

class SchedulerType(Enum):
    """Supported scheduler types."""
    DDIM = "ddim"
    DDPM = "ddpm"
    PNDM = "pndm"
    LMS = "lms"
    EULER = "euler"
    EULER_ANCESTRAL = "euler_ancestral"
    HEUN = "heun"
    DPM_SOLVER_MULTISTEP = "dpm_solver_multistep"
    DPM_SOLVER_SINGLESTEP = "dpm_solver_singlestep"
    UNIPC_MULTISTEP = "unipc_multistep"

@dataclass
class DiffusionModelConfig:
    """Enhanced configuration for diffusion models."""
    model_name: str
    model_type: DiffusionModelType = DiffusionModelType.STABLE_DIFFUSION
    pipeline_type: PipelineType = PipelineType.TEXT_TO_IMAGE
    scheduler_type: SchedulerType = SchedulerType.DDIM
    torch_dtype: str = "float16"
    use_safetensors: bool = True
    variant: Optional[str] = None
    revision: Optional[str] = None
    cache_dir: Optional[str] = None
    local_files_only: bool = False
    trust_remote_code: bool = False
    device_map: Optional[str] = None
    low_cpu_mem_usage: bool = True
    
    # Memory optimization flags
    enable_attention_slicing: bool = True
    enable_vae_slicing: bool = True
    enable_vae_tiling: bool = False
    enable_model_cpu_offload: bool = False
    enable_sequential_cpu_offload: bool = False
    enable_xformers_memory_efficient_attention: bool = True
    enable_memory_efficient_attention: bool = False
    enable_slicing: bool = True
    enable_sequential_offload: bool = False
    
    # Pipeline-specific configurations
    controlnet_conditioning_scale: float = 1.0
    refiner_strength: float = 0.8
    cascade_guidance_scale: float = 3.0

@dataclass
class GenerationConfig:
    """Enhanced configuration for image generation."""
    prompt: str
    negative_prompt: str = ""
    height: int = 512
    width: int = 512
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    num_images_per_prompt: int = 1
    eta: float = 0.0
    generator: Optional[torch.Generator] = None
    latents: Optional[torch.FloatTensor] = None
    output_type: str = "pil"
    return_dict: bool = True
    callback: Optional[Callable] = None
    callback_steps: int = 1
    cross_attention_kwargs: Optional[Dict[str, Any]] = None
    clip_skip: Optional[int] = None
    
    # SDXL specific parameters
    prompt_2: Optional[str] = None
    negative_prompt_2: Optional[str] = None
    pooled_prompt_embeds: Optional[torch.FloatTensor] = None
    negative_pooled_prompt_embeds: Optional[torch.FloatTensor] = None
    add_text_embeds: Optional[torch.FloatTensor] = None
    negative_add_text_embeds: Optional[torch.FloatTensor] = None
    add_time_ids: Optional[torch.FloatTensor] = None
    negative_add_time_ids: Optional[torch.FloatTensor] = None
    
    # Image-to-image specific parameters
    image: Optional[Union[Image.Image, torch.FloatTensor]] = None
    strength: float = 0.8
    
    # Inpainting specific parameters
    mask_image: Optional[Union[Image.Image, torch.FloatTensor]] = None
    
    # ControlNet specific parameters
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0

@dataclass
class TrainingConfig:
    """Configuration for model training."""
    learning_rate: float = 1e-5
    num_train_epochs: int = 100
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 4
    max_grad_norm: float = 1.0
    warmup_steps: int = 500
    lr_scheduler_type: str = "constant"
    lr_warmup_steps: int = 500
    dataloader_num_workers: int = 4
    save_steps: int = 1000
    save_total_limit: Optional[int] = None
    logging_steps: int = 10
    evaluation_strategy: str = "no"
    eval_steps: Optional[int] = None
    load_best_model_at_end: bool = False
    metric_for_best_model: Optional[str] = None
    greater_is_better: bool = False
    push_to_hub: bool = False
    hub_model_id: Optional[str] = None
    hub_token: Optional[str] = None
    gradient_checkpointing: bool = True
    ddp_find_unused_parameters: bool = False
    dataloader_pin_memory: bool = False
    remove_unused_columns: bool = True
    label_names: Optional[List[str]] = None

class PipelineManager:
    """Manager for different pipeline types with specific implementations."""
    
    def __init__(self):
        self.pipeline_handlers: Dict[PipelineType, Callable] = {
            PipelineType.TEXT_TO_IMAGE: self._handle_text_to_image,
            PipelineType.IMAGE_TO_IMAGE: self._handle_image_to_image,
            PipelineType.INPAINTING: self._handle_inpainting,
            PipelineType.CONTROLNET: self._handle_controlnet,
            PipelineType.REFINER: self._handle_refiner,
            PipelineType.CASCADE: self._handle_cascade
        }
    
    def _handle_text_to_image(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle text-to-image generation."""
        generation_kwargs = {
            "prompt": config.prompt,
            "negative_prompt": config.negative_prompt,
            "height": config.height,
            "width": config.width,
            "num_inference_steps": config.num_inference_steps,
            "guidance_scale": config.guidance_scale,
            "num_images_per_prompt": config.num_images_per_prompt,
            "eta": config.eta,
            "generator": config.generator,
            "latents": config.latents,
            "output_type": config.output_type,
            "return_dict": config.return_dict,
            "callback": config.callback,
            "callback_steps": config.callback_steps,
            "cross_attention_kwargs": config.cross_attention_kwargs
        }
        
        # Add SDXL specific parameters
        if hasattr(pipeline, 'prompt_2') and config.prompt_2:
            generation_kwargs.update({
                "prompt_2": config.prompt_2,
                "negative_prompt_2": config.negative_prompt_2,
                "pooled_prompt_embeds": config.pooled_prompt_embeds,
                "negative_pooled_prompt_embeds": config.negative_pooled_prompt_embeds,
                "add_text_embeds": config.add_text_embeds,
                "negative_add_text_embeds": config.negative_add_text_embeds,
                "add_time_ids": config.add_time_ids,
                "negative_add_time_ids": config.negative_add_time_ids
            })
        
        with torch.no_grad():
            result = pipeline(**generation_kwargs)
        
        if isinstance(result, dict):
            return result.images
        return result
    
    def _handle_image_to_image(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle image-to-image generation."""
        if config.image is None:
            raise ValueError("Image is required for image-to-image generation")
        
        generation_kwargs = {
            "prompt": config.prompt,
            "negative_prompt": config.negative_prompt,
            "image": config.image,
            "strength": config.strength,
            "num_inference_steps": config.num_inference_steps,
            "guidance_scale": config.guidance_scale,
            "num_images_per_prompt": config.num_images_per_prompt,
            "eta": config.eta,
            "generator": config.generator,
            "output_type": config.output_type,
            "return_dict": config.return_dict,
            "callback": config.callback,
            "callback_steps": config.callback_steps
        }
        
        with torch.no_grad():
            result = pipeline(**generation_kwargs)
        
        if isinstance(result, dict):
            return result.images
        return result
    
    def _handle_inpainting(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle inpainting generation."""
        if config.image is None or config.mask_image is None:
            raise ValueError("Both image and mask_image are required for inpainting")
        
        generation_kwargs = {
            "prompt": config.prompt,
            "negative_prompt": config.negative_prompt,
            "image": config.image,
            "mask_image": config.mask_image,
            "num_inference_steps": config.num_inference_steps,
            "guidance_scale": config.guidance_scale,
            "num_images_per_prompt": config.num_images_per_prompt,
            "eta": config.eta,
            "generator": config.generator,
            "output_type": config.output_type,
            "return_dict": config.return_dict,
            "callback": config.callback,
            "callback_steps": config.callback_steps
        }
        
        with torch.no_grad():
            result = pipeline(**generation_kwargs)
        
        if isinstance(result, dict):
            return result.images
        return result
    
    def _handle_controlnet(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle ControlNet generation."""
        generation_kwargs = {
            "prompt": config.prompt,
            "negative_prompt": config.negative_prompt,
            "height": config.height,
            "width": config.width,
            "num_inference_steps": config.num_inference_steps,
            "guidance_scale": config.guidance_scale,
            "num_images_per_prompt": config.num_images_per_prompt,
            "eta": config.eta,
            "generator": config.generator,
            "latents": config.latents,
            "output_type": config.output_type,
            "return_dict": config.return_dict,
            "callback": config.callback,
            "callback_steps": config.callback_steps,
            "cross_attention_kwargs": config.cross_attention_kwargs,
            "controlnet_conditioning_scale": config.controlnet_conditioning_scale,
            "control_guidance_start": config.control_guidance_start,
            "control_guidance_end": config.control_guidance_end
        }
        
        with torch.no_grad():
            result = pipeline(**generation_kwargs)
        
        if isinstance(result, dict):
            return result.images
        return result
    
    def _handle_refiner(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle refiner pipeline generation."""
        # Refiner pipelines typically work with latents from base models
        generation_kwargs = {
            "prompt": config.prompt,
            "negative_prompt": config.negative_prompt,
            "height": config.height,
            "width": config.width,
            "num_inference_steps": config.num_inference_steps,
            "guidance_scale": config.guidance_scale,
            "num_images_per_prompt": config.num_images_per_prompt,
            "eta": config.eta,
            "generator": config.generator,
            "latents": config.latents,
            "output_type": config.output_type,
            "return_dict": config.return_dict,
            "callback": config.callback,
            "callback_steps": config.callback_steps
        }
        
        with torch.no_grad():
            result = pipeline(**generation_kwargs)
        
        if isinstance(result, dict):
            return result.images
        return result
    
    def _handle_cascade(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle cascade pipeline generation."""
        # Cascade pipelines use multiple stages
        generation_kwargs = {
            "prompt": config.prompt,
            "negative_prompt": config.negative_prompt,
            "height": config.height,
            "width": config.width,
            "num_inference_steps": config.num_inference_steps,
            "guidance_scale": config.guidance_scale,
            "num_images_per_prompt": config.num_images_per_prompt,
            "eta": config.eta,
            "generator": config.generator,
            "latents": config.latents,
            "output_type": config.output_type,
            "return_dict": config.return_dict,
            "callback": config.callback,
            "callback_steps": config.callback_steps
        }
        
        with torch.no_grad():
            result = pipeline(**generation_kwargs)
        
        if isinstance(result, dict):
            return result.images
        return result
    
    def generate(self, pipeline: Any, pipeline_type: PipelineType, config: GenerationConfig) -> List[Image.Image]:
        """Generate images using the appropriate pipeline handler."""
        handler = self.pipeline_handlers.get(pipeline_type)
        if handler is None:
            raise ValueError(f"Unsupported pipeline type: {pipeline_type}")
        
        return handler(pipeline, config)

class DiffusionModelManager:
    """Enhanced manager for diffusion models using Diffusers library."""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.tokenization_system = TokenizationSequenceSystem()
        self.pipeline_manager = PipelineManager()
        self._lock = threading.Lock()
        self._setup_default_models()
    
    def _setup_default_models(self):
        """Setup default model configurations with enhanced pipeline types."""
        self.default_configs = {
            "stable-diffusion-v1-5": DiffusionModelConfig(
                model_name="runwayml/stable-diffusion-v1-5",
                model_type=DiffusionModelType.STABLE_DIFFUSION,
                pipeline_type=PipelineType.TEXT_TO_IMAGE,
                scheduler_type=SchedulerType.DDIM
            ),
            "stable-diffusion-v2-1": DiffusionModelConfig(
                model_name="stabilityai/stable-diffusion-2-1",
                model_type=DiffusionModelType.STABLE_DIFFUSION,
                pipeline_type=PipelineType.TEXT_TO_IMAGE,
                scheduler_type=SchedulerType.DDIM
            ),
            "stable-diffusion-xl-base": DiffusionModelConfig(
                model_name="stabilityai/stable-diffusion-xl-base-1.0",
                model_type=DiffusionModelType.STABLE_DIFFUSION_XL,
                pipeline_type=PipelineType.TEXT_TO_IMAGE,
                scheduler_type=SchedulerType.EULER
            ),
            "stable-diffusion-xl-refiner": DiffusionModelConfig(
                model_name="stabilityai/stable-diffusion-xl-refiner-1.0",
                model_type=DiffusionModelType.STABLE_DIFFUSION_XL,
                pipeline_type=PipelineType.REFINER,
                scheduler_type=SchedulerType.EULER
            ),
            "stable-diffusion-img2img": DiffusionModelConfig(
                model_name="runwayml/stable-diffusion-v1-5",
                model_type=DiffusionModelType.STABLE_DIFFUSION_IMG2IMG,
                pipeline_type=PipelineType.IMAGE_TO_IMAGE,
                scheduler_type=SchedulerType.DDIM
            ),
            "stable-diffusion-inpaint": DiffusionModelConfig(
                model_name="runwayml/stable-diffusion-inpainting",
                model_type=DiffusionModelType.STABLE_DIFFUSION_INPAINT,
                pipeline_type=PipelineType.INPAINTING,
                scheduler_type=SchedulerType.DDIM
            )
        }
    
    def _get_scheduler_class(self, scheduler_type: SchedulerType):
        """Get scheduler class based on type."""
        scheduler_map = {
            SchedulerType.DDIM: DDIMScheduler,
            SchedulerType.DDPM: DDPMScheduler,
            SchedulerType.PNDM: PNDMScheduler,
            SchedulerType.LMS: LMSDiscreteScheduler,
            SchedulerType.EULER: EulerDiscreteScheduler,
            SchedulerType.EULER_ANCESTRAL: EulerAncestralDiscreteScheduler,
            SchedulerType.HEUN: HeunDiscreteScheduler,
            SchedulerType.DPM_SOLVER_MULTISTEP: DPMSolverMultistepScheduler,
            SchedulerType.DPM_SOLVER_SINGLESTEP: DPMSolverSinglestepScheduler,
            SchedulerType.UNIPC_MULTISTEP: UniPCMultistepScheduler
        }
        return scheduler_map.get(scheduler_type, DDIMScheduler)
    
    def _get_pipeline_class(self, model_type: DiffusionModelType):
        """Get pipeline class based on model type."""
        pipeline_map = {
            DiffusionModelType.STABLE_DIFFUSION: StableDiffusionPipeline,
            DiffusionModelType.STABLE_DIFFUSION_XL: StableDiffusionXLPipeline,
            DiffusionModelType.STABLE_DIFFUSION_IMG2IMG: StableDiffusionImg2ImgPipeline,
            DiffusionModelType.STABLE_DIFFUSION_INPAINT: StableDiffusionInpaintPipeline,
            DiffusionModelType.STABLE_DIFFUSION_CONTROLNET: StableDiffusionControlNetPipeline
        }
        return pipeline_map.get(model_type, StableDiffusionPipeline)
    
    def load_model(self, name: str, config: Optional[DiffusionModelConfig] = None) -> Any:
        """Load a diffusion model with enhanced pipeline support."""
        try:
            with self._lock:
                if name in self.models:
                    logger.warning(f"Model {name} already loaded")
                    return self.models[name]
                
                if config is None:
                    config = self.default_configs.get(name)
                    if config is None:
                        raise ValueError(f"No default config for model {name}")
                
                logger.info(f"Loading diffusion model: {config.model_name} (Type: {config.pipeline_type.value})")
                
                # Get pipeline class
                pipeline_class = self._get_pipeline_class(config.model_type)
                
                # Load pipeline
                pipeline = pipeline_class.from_pretrained(
                    config.model_name,
                    torch_dtype=getattr(torch, config.torch_dtype),
                    use_safetensors=config.use_safetensors,
                    variant=config.variant,
                    revision=config.revision,
                    cache_dir=config.cache_dir,
                    local_files_only=config.local_files_only,
                    trust_remote_code=config.trust_remote_code,
                    device_map=config.device_map,
                    low_cpu_mem_usage=config.low_cpu_mem_usage
                )
                
                # Set scheduler
                scheduler_class = self._get_scheduler_class(config.scheduler_type)
                pipeline.scheduler = scheduler_class.from_config(pipeline.scheduler.config)
                
                # Move to device
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                pipeline = pipeline.to(device)
                
                # Enable optimizations
                if config.enable_attention_slicing:
                    pipeline.enable_attention_slicing()
                
                if config.enable_vae_slicing:
                    pipeline.enable_vae_slicing()
                
                if config.enable_vae_tiling:
                    pipeline.enable_vae_tiling()
                
                if config.enable_model_cpu_offload:
                    pipeline.enable_model_cpu_offload()
                
                if config.enable_sequential_cpu_offload:
                    pipeline.enable_sequential_cpu_offload()
                
                if config.enable_xformers_memory_efficient_attention:
                    try:
                        pipeline.enable_xformers_memory_efficient_attention()
                    except Exception as e:
                        logger.warning(f"Failed to enable xformers: {e}")
                
                if config.enable_memory_efficient_attention:
                    pipeline.enable_memory_efficient_attention()
                
                # Store model with config
                self.models[name] = {
                    "pipeline": pipeline,
                    "config": config
                }
                
                logger.info(f"✅ Model {name} loaded successfully on {device}")
                return pipeline
                
        except Exception as e:
            logger.error(f"❌ Failed to load model {name}: {e}")
            raise
    
    def get_model(self, name: str) -> Optional[Any]:
        """Get loaded model by name."""
        model_data = self.models.get(name)
        if model_data:
            return model_data["pipeline"]
        return None
    
    def get_model_config(self, name: str) -> Optional[DiffusionModelConfig]:
        """Get model configuration by name."""
        model_data = self.models.get(name)
        if model_data:
            return model_data["config"]
        return None
    
    def unload_model(self, name: str):
        """Unload a model."""
        with self._lock:
            if name in self.models:
                # Clear GPU memory
                pipeline = self.models[name]["pipeline"]
                if hasattr(pipeline, 'to'):
                    pipeline.to('cpu')
                del self.models[name]
                torch.cuda.empty_cache()
                logger.info(f"✅ Model {name} unloaded")
    
    def list_models(self) -> List[str]:
        """List all loaded models."""
        return list(self.models.keys())
    
    def generate_image(self, 
                      model_name: str, 
                      config: GenerationConfig) -> List[Image.Image]:
        """Generate images using a diffusion model with pipeline-specific handling."""
        try:
            model_data = self.models.get(model_name)
            if model_data is None:
                raise ValueError(f"Model {model_name} not loaded")
            
            pipeline = model_data["pipeline"]
            pipeline_config = model_data["config"]
            
            logger.info(f"Generating image with {pipeline_config.pipeline_type.value} pipeline")
            logger.info(f"Prompt: {config.prompt[:50]}...")
            
            # Use pipeline manager for generation
            images = self.pipeline_manager.generate(
                pipeline, pipeline_config.pipeline_type, config
            )
            
            logger.info(f"✅ Generated {len(images)} images")
            return images
            
        except Exception as e:
            logger.error(f"❌ Failed to generate image: {e}")
            raise
    
    def generate_image_batch(self, 
                           model_name: str, 
                           configs: List[GenerationConfig]) -> List[List[Image.Image]]:
        """Generate multiple images in batch."""
        try:
            model = self.get_model(model_name)
            if model is None:
                raise ValueError(f"Model {model_name} not loaded")
            
            logger.info(f"Generating batch of {len(configs)} images")
            
            results = []
            for i, config in enumerate(configs):
                logger.info(f"Generating image {i+1}/{len(configs)}")
                images = self.generate_image(model_name, config)
                results.append(images)
            
            logger.info(f"✅ Generated batch of {len(results)} image sets")
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to generate image batch: {e}")
            raise
    
    def setup_tokenization(self, model_name: str, tokenizer_name: str):
        """Setup tokenization for a model."""
        try:
            # Get model config
            model_data = self.models.get(model_name)
            if model_data is None:
                raise ValueError(f"Model {model_name} not loaded")
            
            pipeline_config = model_data["config"]
            
            # Determine tokenizer type based on model
            if "xl" in model_name.lower():
                tokenizer_type = TokenizerType.T5
                tokenizer_model = "t5-base"
            else:
                tokenizer_type = TokenizerType.CLIP
                tokenizer_model = "openai/clip-vit-base-patch32"
            
            # Add tokenizer to system
            tokenizer_config = TokenizerConfig(
                model_name=tokenizer_model,
                tokenizer_type=tokenizer_type,
                max_length=77
            )
            
            sequence_config = SequenceConfig(
                strategy=SequenceStrategy.TRUNCATE,
                max_length=77
            )
            
            text_config = TextProcessingConfig(
                remove_extra_whitespace=True,
                normalize_unicode=True,
                custom_filters=["artistic_style", "diffusion_optimized"]
            )
            
            processor = self.tokenization_system.add_processor(
                tokenizer_name, tokenizer_config, sequence_config, text_config
            )
            
            logger.info(f"✅ Tokenization setup for {model_name} -> {tokenizer_name}")
            return processor
            
        except Exception as e:
            logger.error(f"❌ Failed to setup tokenization: {e}")
            raise
    
    def process_prompt_with_tokenization(self, 
                                       tokenizer_name: str, 
                                       prompt: str) -> Dict[str, Any]:
        """Process prompt using the tokenization system."""
        try:
            return self.tokenization_system.process_with_processor(tokenizer_name, prompt)
        except Exception as e:
            logger.error(f"❌ Failed to process prompt: {e}")
            raise
    
    def encode_prompt_with_tokenization(self, 
                                      tokenizer_name: str, 
                                      prompt: str) -> torch.Tensor:
        """Encode prompt using the tokenization system."""
        try:
            return self.tokenization_system.encode_with_processor(tokenizer_name, prompt)
        except Exception as e:
            logger.error(f"❌ Failed to encode prompt: {e}")
            raise
    
    def analyze_pipeline(self, model_name: str) -> Dict[str, Any]:
        """Analyze pipeline-specific characteristics."""
        try:
            model_data = self.models.get(model_name)
            if model_data is None:
                raise ValueError(f"Model {model_name} not loaded")
            
            pipeline = model_data["pipeline"]
            config = model_data["config"]
            
            analysis = {
                "model_name": model_name,
                "pipeline_type": config.pipeline_type.value,
                "model_type": config.model_type.value,
                "scheduler_type": config.scheduler_type.value,
                "pipeline_class": type(pipeline).__name__,
                "components": list(pipeline.components.keys()) if hasattr(pipeline, 'components') else [],
                "device": next(pipeline.parameters()).device if hasattr(pipeline, 'parameters') else "unknown",
                "dtype": next(pipeline.parameters()).dtype if hasattr(pipeline, 'parameters') else "unknown",
                "supports_img2img": hasattr(pipeline, 'image_processor'),
                "supports_inpainting": hasattr(pipeline, 'mask_processor'),
                "supports_controlnet": hasattr(pipeline, 'controlnet'),
                "text_encoder_type": type(pipeline.text_encoder).__name__ if hasattr(pipeline, 'text_encoder') else "unknown",
                "vae_type": type(pipeline.vae).__name__ if hasattr(pipeline, 'vae') else "unknown",
                "unet_type": type(pipeline.unet).__name__ if hasattr(pipeline, 'unet') else "unknown"
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze pipeline: {e}")
            raise

class DiffusionModelTrainer:
    """Trainer for diffusion models."""
    
    def __init__(self, model_manager: DiffusionModelManager):
        self.model_manager = model_manager
        self.training_configs: Dict[str, TrainingConfig] = {}
    
    def setup_training(self, 
                      model_name: str, 
                      config: TrainingConfig) -> TrainingConfig:
        """Setup training configuration for a model."""
        try:
            self.training_configs[model_name] = config
            logger.info(f"✅ Training setup for {model_name}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to setup training: {e}")
            raise
    
    def train_model(self, 
                   model_name: str, 
                   dataset_path: str, 
                   output_dir: str):
        """Train a diffusion model."""
        try:
            model = self.model_manager.get_model(model_name)
            if model is None:
                raise ValueError(f"Model {model_name} not loaded")
            
            config = self.training_configs.get(model_name)
            if config is None:
                raise ValueError(f"No training config for {model_name}")
            
            logger.info(f"Starting training for {model_name}")
            
            # This would implement the actual training loop
            # For now, we'll just log the setup
            logger.info(f"Training config: {config}")
            logger.info(f"Dataset path: {dataset_path}")
            logger.info(f"Output directory: {output_dir}")
            
            # TODO: Implement actual training loop
            logger.info("Training loop not yet implemented")
            
        except Exception as e:
            logger.error(f"❌ Failed to train model: {e}")
            raise

class DiffusionModelAnalyzer:
    """Enhanced analyzer for diffusion models."""
    
    def __init__(self, model_manager: DiffusionModelManager):
        self.model_manager = model_manager
    
    def analyze_model(self, model_name: str) -> Dict[str, Any]:
        """Analyze a diffusion model."""
        try:
            model_data = self.model_manager.models.get(model_name)
            if model_data is None:
                raise ValueError(f"Model {model_name} not loaded")
            
            pipeline = model_data["pipeline"]
            config = model_data["config"]
            
            analysis = {
                "model_name": model_name,
                "pipeline_type": config.pipeline_type.value,
                "model_type": config.model_type.value,
                "scheduler_type": config.scheduler_type.value,
                "pipeline_class": type(pipeline).__name__,
                "device": next(pipeline.parameters()).device if hasattr(pipeline, 'parameters') else "unknown",
                "dtype": next(pipeline.parameters()).dtype if hasattr(pipeline, 'parameters') else "unknown",
                "num_parameters": sum(p.numel() for p in pipeline.parameters()) if hasattr(pipeline, 'parameters') else 0,
                "trainable_parameters": sum(p.numel() for p in pipeline.parameters() if p.requires_grad) if hasattr(pipeline, 'parameters') else 0,
                "components": list(pipeline.components.keys()) if hasattr(pipeline, 'components') else []
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze model: {e}")
            raise
    
    def benchmark_model(self, 
                       model_name: str, 
                       prompt: str, 
                       num_runs: int = 5) -> Dict[str, Any]:
        """Benchmark a diffusion model."""
        try:
            model = self.model_manager.get_model(model_name)
            if model is None:
                raise ValueError(f"Model {model_name} not loaded")
            
            logger.info(f"Benchmarking {model_name} with {num_runs} runs")
            
            config = GenerationConfig(
                prompt=prompt,
                num_inference_steps=20,  # Reduced for benchmarking
                num_images_per_prompt=1
            )
            
            times = []
            memory_usage = []
            
            for i in range(num_runs):
                logger.info(f"Benchmark run {i+1}/{num_runs}")
                
                # Measure time
                start_time = time.time()
                start_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
                
                images = self.model_manager.generate_image(model_name, config)
                
                end_time = time.time()
                end_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
                
                times.append(end_time - start_time)
                memory_usage.append(end_memory - start_memory)
            
            benchmark_results = {
                "model_name": model_name,
                "num_runs": num_runs,
                "avg_time": np.mean(times),
                "std_time": np.std(times),
                "min_time": np.min(times),
                "max_time": np.max(times),
                "avg_memory": np.mean(memory_usage) if memory_usage[0] > 0 else 0,
                "std_memory": np.std(memory_usage) if memory_usage[0] > 0 else 0,
                "times": times,
                "memory_usage": memory_usage
            }
            
            logger.info(f"✅ Benchmark completed for {model_name}")
            return benchmark_results
            
        except Exception as e:
            logger.error(f"❌ Failed to benchmark model: {e}")
            raise

# Production usage example
def main():
    """Production usage example with enhanced pipeline support."""
    try:
        # Initialize diffusion model manager
        manager = DiffusionModelManager()
        
        # Load different pipeline types
        sd_model = manager.load_model("stable-diffusion-v1-5")
        sdxl_model = manager.load_model("stable-diffusion-xl-base")
        img2img_model = manager.load_model("stable-diffusion-img2img")
        
        # Setup tokenization
        manager.setup_tokenization("stable-diffusion-v1-5", "sd_clip")
        manager.setup_tokenization("stable-diffusion-xl-base", "sdxl_t5")
        
        # Analyze pipelines
        analyzer = DiffusionModelAnalyzer(manager)
        
        # Analyze text-to-image pipeline
        sd_analysis = analyzer.analyze_model("stable-diffusion-v1-5")
        print(f"SD Pipeline Analysis: {sd_analysis}")
        
        # Analyze SDXL pipeline
        sdxl_analysis = analyzer.analyze_model("stable-diffusion-xl-base")
        print(f"SDXL Pipeline Analysis: {sdxl_analysis}")
        
        # Generate images with different pipelines
        config = GenerationConfig(
            prompt="A beautiful sunset over the mountains, digital art style",
            num_inference_steps=30,
            guidance_scale=7.5
        )
        
        # Text-to-image generation
        images = manager.generate_image("stable-diffusion-v1-5", config)
        print(f"Generated {len(images)} images with SD pipeline")
        
        # Pipeline-specific analysis
        pipeline_analysis = manager.analyze_pipeline("stable-diffusion-v1-5")
        print(f"Pipeline Analysis: {pipeline_analysis}")
        
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")

if __name__ == "__main__":
    main() 