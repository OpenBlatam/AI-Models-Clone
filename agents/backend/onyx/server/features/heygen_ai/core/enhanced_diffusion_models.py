"""
Enhanced Diffusion Models for HeyGen AI

This module provides enhanced diffusion models with advanced features:
- Multiple diffusion model types (Stable Diffusion, SDXL, ControlNet, etc.)
- LoRA support for efficient fine-tuning
- Ultra performance optimizations
- Comprehensive pipeline management
"""

import logging
import warnings
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import gc

import torch
import torch.nn as nn
from torch.cuda.amp import autocast
import numpy as np
from PIL import Image
import requests
from io import BytesIO

from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionXLPipeline,
    ControlNetPipeline,
    TextToVideoPipeline,
    Img2ImgPipeline,
    InpaintPipeline,
    DPMSolverMultistepScheduler,
    EulerDiscreteScheduler,
    DDIMScheduler,
    PNDMScheduler,
    LMSDiscreteScheduler,
    HeunDiscreteScheduler,
    EulerAncestralDiscreteScheduler,
    DPMSolverSinglestepScheduler,
    KDPM2DiscreteScheduler,
    DPMSolverSDEScheduler,
    UniPCMultistepScheduler,
    DPMSolverMultistepInverseScheduler
)

# Import ultra performance optimizer
from .ultra_performance_optimizer import (
    UltraPerformanceOptimizer,
    UltraPerformanceConfig
)

logger = logging.getLogger(__name__)


@dataclass
class DiffusionConfig:
    """Configuration for diffusion models."""
    
    # Model Settings
    model_type: str = "stable_diffusion"  # stable_diffusion, sdxl, controlnet, text2video, img2img, inpaint
    model_name: str = "runwayml/stable-diffusion-v1-5"
    model_revision: str = "main"
    torch_dtype: str = "fp16"  # fp16, bf16, fp32
    
    # Generation Settings
    prompt: str = "A beautiful landscape painting"
    negative_prompt: str = "blurry, low quality, distorted"
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    num_images_per_prompt: int = 1
    height: int = 512
    width: int = 512
    seed: Optional[int] = None
    
    # LoRA Configuration
    enable_lora: bool = False
    lora_path: Optional[str] = None
    lora_scale: float = 1.0
    
    # Performance Settings
    enable_ultra_performance: bool = True
    performance_mode: str = "balanced"  # maximum, balanced, memory-efficient
    enable_torch_compile: bool = True
    enable_flash_attention: bool = True
    enable_memory_optimization: bool = True
    enable_attention_slicing: bool = False
    enable_vae_slicing: bool = False
    enable_model_cpu_offload: bool = False
    enable_xformers: bool = True
    
    # Scheduler Settings
    scheduler_type: str = "dpm"  # dpm, euler, ddim, pndm, lms, heun, euler_ancestral, dpm_single, kdpm2, dpm_sde, unipc, dpm_inverse
    
    # ControlNet Settings (if applicable)
    controlnet_model: Optional[str] = None
    control_image: Optional[str] = None
    
    # Video Settings (if applicable)
    num_frames: int = 16
    fps: int = 8


class DiffusionPipelineManager:
    """Enhanced diffusion pipeline manager with ultra performance optimizations."""
    
    def __init__(self, config: DiffusionConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pipeline = None
        
        # Ultra performance optimizer
        self.ultra_performance_optimizer = None
        if self.config.enable_ultra_performance:
            self._setup_ultra_performance()
        
        # Initialize pipeline
        self._setup_pipeline()
        
        # Apply optimizations
        self._apply_optimizations()
    
    def _setup_ultra_performance(self):
        """Setup ultra performance optimizations."""
        try:
            performance_config = UltraPerformanceConfig(
                enable_torch_compile=self.config.enable_torch_compile,
                enable_flash_attention=self.config.enable_flash_attention,
                enable_memory_efficient_forward=self.config.enable_memory_optimization,
                enable_attention_slicing=self.config.enable_attention_slicing,
                enable_vae_slicing=self.config.enable_vae_slicing,
                enable_model_cpu_offload=self.config.enable_model_cpu_offload,
                enable_xformers=self.config.enable_xformers
            )
            
            self.ultra_performance_optimizer = UltraPerformanceOptimizer(
                config=performance_config,
                device=self.device
            )
            
            logger.info("Ultra performance optimizations enabled for DiffusionPipelineManager")
            
        except Exception as e:
            logger.warning(f"Failed to setup ultra performance optimizations: {e}")
            self.ultra_performance_optimizer = None
    
    def _setup_pipeline(self):
        """Setup the diffusion pipeline based on configuration."""
        try:
            # Get torch dtype
            torch_dtype = self._get_torch_dtype()
            
            # Create pipeline based on model type
            if self.config.model_type == "stable_diffusion":
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    self.config.model_name,
                    revision=self.config.model_revision,
                    torch_dtype=torch_dtype,
                    safety_checker=None,
                    requires_safety_checker=False
                )
            elif self.config.model_type == "sdxl":
                self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                    self.config.model_name,
                    revision=self.config.model_revision,
                    torch_dtype=torch_dtype,
                    safety_checker=None,
                    requires_safety_checker=False
                )
            elif self.config.model_type == "controlnet":
                if not self.config.controlnet_model:
                    raise ValueError("ControlNet model path must be specified for ControlNet pipeline")
                
                self.pipeline = ControlNetPipeline.from_pretrained(
                    self.config.model_name,
                    controlnet=self.config.controlnet_model,
                    revision=self.config.model_revision,
                    torch_dtype=torch_dtype,
                    safety_checker=None,
                    requires_safety_checker=False
                )
            elif self.config.model_type == "text2video":
                self.pipeline = TextToVideoPipeline.from_pretrained(
                    self.config.model_name,
                    revision=self.config.model_revision,
                    torch_dtype=torch_dtype
                )
            elif self.config.model_type == "img2img":
                self.pipeline = Img2ImgPipeline.from_pretrained(
                    self.config.model_name,
                    revision=self.config.model_revision,
                    torch_dtype=torch_dtype,
                    safety_checker=None,
                    requires_safety_checker=False
                )
            elif self.config.model_type == "inpaint":
                self.pipeline = InpaintPipeline.from_pretrained(
                    self.config.model_name,
                    revision=self.config.model_revision,
                    torch_dtype=torch_dtype,
                    safety_checker=None,
                    requires_safety_checker=False
                )
            else:
                raise ValueError(f"Unsupported model type: {self.config.model_type}")
            
            # Move pipeline to device
            self.pipeline = self.pipeline.to(self.device)
            
            # Setup scheduler
            self._setup_scheduler()
            
            logger.info(f"Pipeline {self.config.model_type} loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to setup pipeline: {e}")
            raise
    
    def _get_torch_dtype(self) -> torch.dtype:
        """Get torch dtype from config."""
        if self.config.torch_dtype == "fp16":
            return torch.float16
        elif self.config.torch_dtype == "bf16":
            return torch.bfloat16
        else:
            return torch.float32
    
    def _setup_scheduler(self):
        """Setup the scheduler for the pipeline."""
        try:
            scheduler_map = {
                "dpm": DPMSolverMultistepScheduler,
                "euler": EulerDiscreteScheduler,
                "ddim": DDIMScheduler,
                "pndm": PNDMScheduler,
                "lms": LMSDiscreteScheduler,
                "heun": HeunDiscreteScheduler,
                "euler_ancestral": EulerAncestralDiscreteScheduler,
                "dpm_single": DPMSolverSinglestepScheduler,
                "kdpm2": KDPM2DiscreteScheduler,
                "dpm_sde": DPMSolverSDEScheduler,
                "unipc": UniPCMultistepScheduler,
                "dpm_inverse": DPMSolverMultistepInverseScheduler
            }
            
            scheduler_class = scheduler_map.get(self.config.scheduler_type, DPMSolverMultistepScheduler)
            
            if scheduler_class == DPMSolverMultistepScheduler:
                scheduler = scheduler_class.from_config(self.pipeline.scheduler.config)
            else:
                scheduler = scheduler_class.from_config(self.pipeline.scheduler.config)
            
            self.pipeline.scheduler = scheduler
            logger.info(f"Scheduler {self.config.scheduler_type} applied successfully")
            
        except Exception as e:
            logger.warning(f"Failed to setup scheduler: {e}")
    
    def _apply_optimizations(self):
        """Apply performance optimizations to the pipeline."""
        try:
            # Apply ultra performance optimizations if available
            if self.ultra_performance_optimizer:
                self.pipeline = self.ultra_performance_optimizer.optimize_diffusion_pipeline(self.pipeline)
                logger.info("Ultra performance optimizations applied to pipeline")
            
            # Apply LoRA if enabled
            if self.config.enable_lora and self.config.lora_path:
                self._apply_lora()
            
            # Apply attention slicing
            if self.config.enable_attention_slicing:
                self.pipeline.enable_attention_slicing()
                logger.info("Attention slicing enabled")
            
            # Apply VAE slicing
            if self.config.enable_vae_slicing:
                self.pipeline.enable_vae_slicing()
                logger.info("VAE slicing enabled")
            
            # Apply model CPU offload
            if self.config.enable_model_cpu_offload:
                self.pipeline.enable_model_cpu_offload()
                logger.info("Model CPU offload enabled")
            
            # Apply xFormers memory efficient attention
            if self.config.enable_xformers:
                try:
                    self.pipeline.enable_xformers_memory_efficient_attention()
                    logger.info("xFormers memory efficient attention enabled")
                except Exception as e:
                    logger.warning(f"Failed to enable xFormers: {e}")
            
            logger.info("Pipeline optimizations applied successfully")
            
        except Exception as e:
            logger.warning(f"Failed to apply some optimizations: {e}")
    
    def _apply_lora(self):
        """Apply LoRA to the pipeline."""
        try:
            if self.config.lora_path and Path(self.config.lora_path).exists():
                self.pipeline.load_lora_weights(
                    self.config.lora_path,
                    weight_name="pytorch_lora_weights.safetensors"
                )
                logger.info(f"LoRA weights loaded from {self.config.lora_path}")
            else:
                logger.warning(f"LoRA path not found: {self.config.lora_path}")
                
        except Exception as e:
            logger.error(f"Failed to apply LoRA: {e}")
    
    def generate_image(
        self,
        prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> List[Image.Image]:
        """Generate images using the diffusion pipeline."""
        try:
            # Use config values if not provided
            prompt = prompt or self.config.prompt
            negative_prompt = negative_prompt or self.config.negative_prompt
            num_inference_steps = num_inference_steps or self.config.num_inference_steps
            guidance_scale = guidance_scale or self.config.guidance_scale
            height = height or self.config.height
            width = width or self.config.width
            seed = seed or self.config.seed
            
            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(seed)
                    torch.cuda.manual_seed_all(seed)
            
            # Prepare generation arguments
            generation_kwargs = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "height": height,
                "width": width,
                "num_images_per_prompt": self.config.num_images_per_prompt,
                **kwargs
            }
            
            # Generate images
            with autocast(enabled=self.config.torch_dtype != "fp32"):
                if self.config.model_type == "controlnet":
                    # Load control image if provided
                    if self.config.control_image:
                        control_image = self._load_control_image(self.config.control_image)
                        generation_kwargs["image"] = control_image
                    
                    outputs = self.pipeline(**generation_kwargs)
                else:
                    outputs = self.pipeline(**generation_kwargs)
            
            # Extract images
            if hasattr(outputs, 'images'):
                images = outputs.images
            elif isinstance(outputs, list):
                images = outputs
            else:
                images = [outputs]
            
            logger.info(f"Generated {len(images)} images successfully")
            return images
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise
    
    def _load_control_image(self, image_path: str) -> Image.Image:
        """Load control image for ControlNet."""
        try:
            if image_path.startswith(('http://', 'https://')):
                response = requests.get(image_path)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_path)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to load control image: {e}")
            raise
    
    def generate_video(
        self,
        prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        num_frames: Optional[int] = None,
        fps: Optional[int] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> List[torch.Tensor]:
        """Generate video using the text-to-video pipeline."""
        if self.config.model_type != "text2video":
            raise ValueError("Video generation only supported for text2video pipeline")
        
        try:
            # Use config values if not provided
            prompt = prompt or self.config.prompt
            negative_prompt = negative_prompt or self.config.negative_prompt
            num_inference_steps = num_inference_steps or self.config.num_inference_steps
            guidance_scale = guidance_scale or self.config.guidance_scale
            num_frames = num_frames or self.config.num_frames
            fps = fps or self.config.fps
            height = height or self.config.height
            width = width or self.config.width
            seed = seed or self.config.seed
            
            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(seed)
                    torch.cuda.manual_seed_all(seed)
            
            # Prepare generation arguments
            generation_kwargs = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "num_frames": num_frames,
                "height": height,
                "width": width,
                **kwargs
            }
            
            # Generate video
            with autocast(enabled=self.config.torch_dtype != "fp32"):
                outputs = self.pipeline(**generation_kwargs)
            
            # Extract video frames
            if hasattr(outputs, 'frames'):
                frames = outputs.frames
            elif isinstance(outputs, list):
                frames = outputs
            else:
                frames = [outputs]
            
            logger.info(f"Generated video with {len(frames)} frames successfully")
            return frames
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise
    
    def img2img(
        self,
        image: Union[str, Image.Image],
        prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        strength: float = 0.8,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> List[Image.Image]:
        """Generate image-to-image using the pipeline."""
        if self.config.model_type != "img2img":
            raise ValueError("Image-to-image only supported for img2img pipeline")
        
        try:
            # Load image if path provided
            if isinstance(image, str):
                if image.startswith(('http://', 'https://')):
                    response = requests.get(image)
                    input_image = Image.open(BytesIO(response.content))
                else:
                    input_image = Image.open(image)
            else:
                input_image = image
            
            # Use config values if not provided
            prompt = prompt or self.config.prompt
            negative_prompt = negative_prompt or self.config.negative_prompt
            num_inference_steps = num_inference_steps or self.config.num_inference_steps
            guidance_scale = guidance_scale or self.config.guidance_scale
            seed = seed or self.config.seed
            
            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(seed)
                    torch.cuda.manual_seed_all(seed)
            
            # Prepare generation arguments
            generation_kwargs = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "image": input_image,
                "strength": strength,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "num_images_per_prompt": self.config.num_images_per_prompt,
                **kwargs
            }
            
            # Generate images
            with autocast(enabled=self.config.torch_dtype != "fp32"):
                outputs = self.pipeline(**generation_kwargs)
            
            # Extract images
            if hasattr(outputs, 'images'):
                images = outputs.images
            elif isinstance(outputs, list):
                images = outputs
            else:
                images = [outputs]
            
            logger.info(f"Generated {len(images)} images from input image successfully")
            return images
            
        except Exception as e:
            logger.error(f"Image-to-image generation failed: {e}")
            raise
    
    def inpaint(
        self,
        image: Union[str, Image.Image],
        mask: Union[str, Image.Image],
        prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> List[Image.Image]:
        """Generate inpainting using the pipeline."""
        if self.config.model_type != "inpaint":
            raise ValueError("Inpainting only supported for inpaint pipeline")
        
        try:
            # Load image and mask if paths provided
            if isinstance(image, str):
                if image.startswith(('http://', 'https://')):
                    response = requests.get(image)
                    input_image = Image.open(BytesIO(response.content))
                else:
                    input_image = Image.open(image)
            else:
                input_image = image
            
            if isinstance(mask, str):
                if mask.startswith(('http://', 'https://')):
                    response = requests.get(mask)
                    input_mask = Image.open(BytesIO(response.content))
                else:
                    input_mask = Image.open(mask)
            else:
                input_mask = mask
            
            # Use config values if not provided
            prompt = prompt or self.config.prompt
            negative_prompt = negative_prompt or self.config.negative_prompt
            num_inference_steps = num_inference_steps or self.config.num_inference_steps
            guidance_scale = guidance_scale or self.config.guidance_scale
            seed = seed or self.config.seed
            
            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(seed)
                    torch.cuda.manual_seed_all(seed)
            
            # Prepare generation arguments
            generation_kwargs = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "image": input_image,
                "mask_image": input_mask,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "num_images_per_prompt": self.config.num_images_per_prompt,
                **kwargs
            }
            
            # Generate images
            with autocast(enabled=self.config.torch_dtype != "fp32"):
                outputs = self.pipeline(**generation_kwargs)
            
            # Extract images
            if hasattr(outputs, 'images'):
                images = outputs.images
            elif isinstance(outputs, list):
                images = outputs
            else:
                images = [outputs]
            
            logger.info(f"Generated {len(images)} inpainted images successfully")
            return images
            
        except Exception as e:
            logger.error(f"Inpainting generation failed: {e}")
            raise
    
    def setup_training(self, config: Dict[str, Any]):
        """Setup training configuration."""
        # Apply ultra performance optimizations
        if self.ultra_performance_optimizer:
            try:
                self.ultra_performance_optimizer.pre_training_optimization(self.pipeline)
                logger.info("Pre-training optimizations applied to pipeline")
            except Exception as e:
                logger.warning(f"Failed to apply pre-training optimizations: {e}")
    
    def save_pipeline(self, output_dir: str):
        """Save the pipeline to disk."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.pipeline.save_pretrained(output_path)
            logger.info(f"Pipeline saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save pipeline: {e}")
    
    def load_pipeline(self, pipeline_path: str):
        """Load a pipeline from disk."""
        try:
            if self.config.model_type == "stable_diffusion":
                self.pipeline = StableDiffusionPipeline.from_pretrained(pipeline_path)
            elif self.config.model_type == "sdxl":
                self.pipeline = StableDiffusionXLPipeline.from_pretrained(pipeline_path)
            elif self.config.model_type == "controlnet":
                self.pipeline = ControlNetPipeline.from_pretrained(pipeline_path)
            elif self.config.model_type == "text2video":
                self.pipeline = TextToVideoPipeline.from_pretrained(pipeline_path)
            elif self.config.model_type == "img2img":
                self.pipeline = Img2ImgPipeline.from_pretrained(pipeline_path)
            elif self.config.model_type == "inpaint":
                self.pipeline = InpaintPipeline.from_pretrained(pipeline_path)
            
            self.pipeline = self.pipeline.to(self.device)
            self._apply_optimizations()
            
            logger.info(f"Pipeline loaded from {pipeline_path}")
            
        except Exception as e:
            logger.error(f"Failed to load pipeline: {e}")
            raise
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the current pipeline."""
        if self.pipeline is None:
            return {"error": "No pipeline loaded"}
        
        return {
            "model_type": self.config.model_type,
            "model_name": self.config.model_name,
            "device": str(self.device),
            "torch_dtype": self.config.torch_dtype,
            "scheduler": self.config.scheduler_type,
            "enable_lora": self.config.enable_lora,
            "enable_ultra_performance": self.config.enable_ultra_performance,
            "enable_attention_slicing": self.config.enable_attention_slicing,
            "enable_vae_slicing": self.config.enable_vae_slicing,
            "enable_model_cpu_offload": self.config.enable_model_cpu_offload,
            "enable_xformers": self.config.enable_xformers
        }
    
    def cleanup(self):
        """Cleanup resources."""
        if self.ultra_performance_optimizer:
            self.ultra_performance_optimizer.cleanup()
        
        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
        
        logger.info("DiffusionPipelineManager cleanup completed")


# Factory functions for different pipeline configurations
def create_stable_diffusion_pipeline(
    model_name: str = "runwayml/stable-diffusion-v1-5",
    enable_ultra_performance: bool = True,
    enable_lora: bool = False,
    **kwargs
) -> DiffusionPipelineManager:
    """Create a Stable Diffusion pipeline."""
    config = DiffusionConfig(
        model_type="stable_diffusion",
        model_name=model_name,
        enable_ultra_performance=enable_ultra_performance,
        enable_lora=enable_lora,
        **kwargs
    )
    
    return DiffusionPipelineManager(config)


def create_sdxl_pipeline(
    model_name: str = "stabilityai/stable-diffusion-xl-base-1.0",
    enable_ultra_performance: bool = True,
    enable_lora: bool = False,
    **kwargs
) -> DiffusionPipelineManager:
    """Create an SDXL pipeline."""
    config = DiffusionConfig(
        model_type="sdxl",
        model_name=model_name,
        enable_ultra_performance=enable_ultra_performance,
        enable_lora=enable_lora,
        **kwargs
    )
    
    return DiffusionPipelineManager(config)


def create_controlnet_pipeline(
    model_name: str = "runwayml/stable-diffusion-v1-5",
    controlnet_model: str = "lllyasviel/sd-controlnet-canny",
    enable_ultra_performance: bool = True,
    enable_lora: bool = False,
    **kwargs
) -> DiffusionPipelineManager:
    """Create a ControlNet pipeline."""
    config = DiffusionConfig(
        model_type="controlnet",
        model_name=model_name,
        controlnet_model=controlnet_model,
        enable_ultra_performance=enable_ultra_performance,
        enable_lora=enable_lora,
        **kwargs
    )
    
    return DiffusionPipelineManager(config)


def create_text2video_pipeline(
    model_name: str = "damo-vilab/text-to-video-ms-1.7b",
    enable_ultra_performance: bool = True,
    **kwargs
) -> DiffusionPipelineManager:
    """Create a text-to-video pipeline."""
    config = DiffusionConfig(
        model_type="text2video",
        model_name=model_name,
        enable_ultra_performance=enable_ultra_performance,
        **kwargs
    )
    
    return DiffusionPipelineManager(config)


def create_img2img_pipeline(
    model_name: str = "runwayml/stable-diffusion-v1-5",
    enable_ultra_performance: bool = True,
    enable_lora: bool = False,
    **kwargs
) -> DiffusionPipelineManager:
    """Create an image-to-image pipeline."""
    config = DiffusionConfig(
        model_type="img2img",
        model_name=model_name,
        enable_ultra_performance=enable_ultra_performance,
        enable_lora=enable_lora,
        **kwargs
    )
    
    return DiffusionPipelineManager(config)


def create_inpaint_pipeline(
    model_name: str = "runwayml/stable-diffusion-inpainting",
    enable_ultra_performance: bool = True,
    enable_lora: bool = False,
    **kwargs
) -> DiffusionPipelineManager:
    """Create an inpainting pipeline."""
    config = DiffusionConfig(
        model_type="inpaint",
        model_name=model_name,
        enable_ultra_performance=enable_ultra_performance,
        enable_lora=enable_lora,
        **kwargs
    )
    
    return DiffusionPipelineManager(config)


# Example usage
if __name__ == "__main__":
    # Create a Stable Diffusion pipeline
    pipeline = create_stable_diffusion_pipeline(enable_ultra_performance=True)
    
    # Print pipeline info
    info = pipeline.get_pipeline_info()
    print(f"Pipeline created successfully!")
    print(f"Pipeline info: {info}")
    
    # Generate an image
    try:
        images = pipeline.generate_image(
            prompt="A beautiful sunset over mountains",
            num_inference_steps=20
        )
        print(f"Generated {len(images)} images")
        
        # Save the first image
        if images:
            images[0].save("generated_image.png")
            print("Image saved as generated_image.png")
    
    except Exception as e:
        print(f"Image generation failed: {e}")
    
    # Cleanup
    pipeline.cleanup()

