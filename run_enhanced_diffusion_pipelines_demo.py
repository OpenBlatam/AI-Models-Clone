#!/usr/bin/env python3
"""
Enhanced Diffusion Pipelines Demo

This script demonstrates the enhanced diffusion models system with
different pipeline types and their specific implementations.
"""

import torch
import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock classes for demonstration (to avoid diffusers import issues)
class MockPipeline:
    """Mock pipeline for demonstration purposes."""
    
    def __init__(self, pipeline_type: str, components: dict = None):
        self.pipeline_type = pipeline_type
        self.components = components or {}
        self.scheduler = MockScheduler()
        self.text_encoder = MockTextEncoder()
        self.vae = MockVAE()
        self.unet = MockUNet()
        
        # Add pipeline-specific attributes
        if "img2img" in pipeline_type:
            self.image_processor = MockImageProcessor()
        if "inpaint" in pipeline_type:
            self.mask_processor = MockMaskProcessor()
        if "controlnet" in pipeline_type:
            self.controlnet = MockControlNet()
    
    def parameters(self):
        """Mock parameters method."""
        return [torch.randn(10, 10)]
    
    def __call__(self, **kwargs):
        """Mock generation method."""
        # Simulate generation time
        time.sleep(0.1)
        
        # Create mock images
        images = []
        num_images = kwargs.get('num_images_per_prompt', 1)
        
        for _ in range(num_images):
            # Create a simple colored image based on pipeline type
            if "xl" in self.pipeline_type:
                size = (1024, 1024)
            else:
                size = (512, 512)
            
            img = Image.new('RGB', size, color=self._get_pipeline_color())
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), f"{self.pipeline_type}", fill="white")
            draw.text((10, 30), f"Prompt: {kwargs.get('prompt', '')[:20]}...", fill="white")
            
            images.append(img)
        
        return type('MockResult', (), {'images': images})()
    
    def _get_pipeline_color(self):
        """Get color based on pipeline type."""
        colors = {
            'stable_diffusion': '#FF6B6B',
            'stable_diffusion_xl': '#4ECDC4',
            'img2img': '#45B7D1',
            'inpaint': '#96CEB4',
            'controlnet': '#FFEAA7',
            'refiner': '#DDA0DD'
        }
        
        for key, color in colors.items():
            if key in self.pipeline_type:
                return color
        
        return '#FF6B6B'
    
    def to(self, device):
        """Mock device movement."""
        return self
    
    def enable_attention_slicing(self):
        """Mock attention slicing."""
        pass
    
    def enable_vae_slicing(self):
        """Mock VAE slicing."""
        pass

class MockScheduler:
    """Mock scheduler."""
    def __init__(self):
        self.config = type('MockConfig', (), {})()
    
    @classmethod
    def from_config(cls, config):
        """Mock from_config method."""
        return cls()

class MockTextEncoder:
    """Mock text encoder."""
    pass

class MockVAE:
    """Mock VAE."""
    pass

class MockUNet:
    """Mock UNet."""
    pass

class MockImageProcessor:
    """Mock image processor."""
    pass

class MockMaskProcessor:
    """Mock mask processor."""
    pass

class MockControlNet:
    """Mock ControlNet."""
    pass

# Mock enums and dataclasses
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Union, Callable

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
        logger.info(f"Using TEXT_TO_IMAGE pipeline handler")
        
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
        
        logger.info(f"Text-to-image kwargs: {list(generation_kwargs.keys())}")
        
        result = pipeline(**generation_kwargs)
        
        if hasattr(result, 'images'):
            return result.images
        return result
    
    def _handle_image_to_image(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle image-to-image generation."""
        logger.info(f"Using IMAGE_TO_IMAGE pipeline handler")
        
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
        
        logger.info(f"Image-to-image kwargs: {list(generation_kwargs.keys())}")
        
        result = pipeline(**generation_kwargs)
        
        if hasattr(result, 'images'):
            return result.images
        return result
    
    def _handle_inpainting(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle inpainting generation."""
        logger.info(f"Using INPAINTING pipeline handler")
        
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
        
        logger.info(f"Inpainting kwargs: {list(generation_kwargs.keys())}")
        
        result = pipeline(**generation_kwargs)
        
        if hasattr(result, 'images'):
            return result.images
        return result
    
    def _handle_controlnet(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle ControlNet generation."""
        logger.info(f"Using CONTROLNET pipeline handler")
        
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
        
        logger.info(f"ControlNet kwargs: {list(generation_kwargs.keys())}")
        
        result = pipeline(**generation_kwargs)
        
        if hasattr(result, 'images'):
            return result.images
        return result
    
    def _handle_refiner(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle refiner pipeline generation."""
        logger.info(f"Using REFINER pipeline handler")
        
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
        
        logger.info(f"Refiner kwargs: {list(generation_kwargs.keys())}")
        
        result = pipeline(**generation_kwargs)
        
        if hasattr(result, 'images'):
            return result.images
        return result
    
    def _handle_cascade(self, pipeline: Any, config: GenerationConfig) -> List[Image.Image]:
        """Handle cascade pipeline generation."""
        logger.info(f"Using CASCADE pipeline handler")
        
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
        
        logger.info(f"Cascade kwargs: {list(generation_kwargs.keys())}")
        
        result = pipeline(**generation_kwargs)
        
        if hasattr(result, 'images'):
            return result.images
        return result
    
    def generate(self, pipeline: Any, pipeline_type: PipelineType, config: GenerationConfig) -> List[Image.Image]:
        """Generate images using the appropriate pipeline handler."""
        handler = self.pipeline_handlers.get(pipeline_type)
        if handler is None:
            raise ValueError(f"Unsupported pipeline type: {pipeline_type}")
        
        return handler(pipeline, config)

class MockDiffusionModelManager:
    """Mock manager for diffusion models using Diffusers library."""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
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
            ),
            "stable-diffusion-controlnet": DiffusionModelConfig(
                model_name="lllyasviel/sd-controlnet-canny",
                model_type=DiffusionModelType.STABLE_DIFFUSION_CONTROLNET,
                pipeline_type=PipelineType.CONTROLNET,
                scheduler_type=SchedulerType.DDIM
            )
        }
    
    def load_model(self, name: str, config: Optional[DiffusionModelConfig] = None) -> Any:
        """Load a diffusion model with enhanced pipeline support."""
        try:
            if name in self.models:
                logger.warning(f"Model {name} already loaded")
                return self.models[name]["pipeline"]
            
            if config is None:
                config = self.default_configs.get(name)
                if config is None:
                    raise ValueError(f"No default config for model {name}")
            
            logger.info(f"Loading diffusion model: {config.model_name} (Type: {config.pipeline_type.value})")
            
            # Create mock pipeline
            pipeline_name = f"{config.model_type.value}_{config.pipeline_type.value}"
            pipeline = MockPipeline(pipeline_name)
            
            # Store model with config
            self.models[name] = {
                "pipeline": pipeline,
                "config": config
            }
            
            logger.info(f"✅ Model {name} loaded successfully")
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
                "device": "cpu",  # Mock device
                "dtype": "float32",  # Mock dtype
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

def create_sample_image(size=(512, 512), color=(100, 150, 200)):
    """Create a sample image for testing."""
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, size[0]-50, size[1]-50], outline="white", width=3)
    draw.text((size[0]//2-50, size[1]//2), "Sample", fill="white")
    return img

def create_sample_mask(size=(512, 512)):
    """Create a sample mask for testing."""
    mask = Image.new('L', size, color=0)
    draw = ImageDraw.Draw(mask)
    # Create a circular mask
    center = (size[0]//2, size[1]//2)
    radius = min(size)//4
    draw.ellipse([center[0]-radius, center[1]-radius, 
                   center[0]+radius, center[1]+radius], fill=255)
    return mask

def demo_pipeline_types():
    """Demonstrate different pipeline types."""
    logger.info("🚀 Starting Enhanced Diffusion Pipelines Demo")
    
    # Initialize manager
    manager = MockDiffusionModelManager()
    
    # Load different pipeline types
    logger.info("\n📥 Loading different pipeline types...")
    
    pipelines = [
        "stable-diffusion-v1-5",      # Text-to-image
        "stable-diffusion-xl-base",   # Text-to-image (XL)
        "stable-diffusion-img2img",   # Image-to-image
        "stable-diffusion-inpaint",   # Inpainting
        "stable-diffusion-controlnet" # ControlNet
    ]
    
    for pipeline_name in pipelines:
        try:
            pipeline = manager.load_model(pipeline_name)
            config = manager.get_model_config(pipeline_name)
            logger.info(f"✅ Loaded {pipeline_name}: {config.pipeline_type.value}")
        except Exception as e:
            logger.error(f"❌ Failed to load {pipeline_name}: {e}")
    
    # Demo 1: Text-to-Image Pipeline
    logger.info("\n🎨 Demo 1: Text-to-Image Pipeline")
    try:
        config = GenerationConfig(
            prompt="A beautiful sunset over the mountains, digital art style",
            num_inference_steps=20,
            guidance_scale=7.5,
            num_images_per_prompt=2
        )
        
        images = manager.generate_image("stable-diffusion-v1-5", config)
        logger.info(f"Generated {len(images)} images with SD v1.5")
        
        # Save images
        for i, img in enumerate(images):
            img.save(f"demo_text2img_sd_{i}.png")
            logger.info(f"Saved demo_text2img_sd_{i}.png")
            
    except Exception as e:
        logger.error(f"❌ Text-to-image demo failed: {e}")
    
    # Demo 2: SDXL Pipeline
    logger.info("\n🌟 Demo 2: SDXL Pipeline")
    try:
        config = GenerationConfig(
            prompt="A majestic dragon flying over a medieval castle, epic fantasy art",
            prompt_2="Detailed, high quality, masterpiece",
            negative_prompt="blurry, low quality",
            height=1024,
            width=1024,
            num_inference_steps=25,
            guidance_scale=8.0,
            num_images_per_prompt=1
        )
        
        images = manager.generate_image("stable-diffusion-xl-base", config)
        logger.info(f"Generated {len(images)} images with SDXL")
        
        # Save images
        for i, img in enumerate(images):
            img.save(f"demo_text2img_sdxl_{i}.png")
            logger.info(f"Saved demo_text2img_sdxl_{i}.png")
            
    except Exception as e:
        logger.error(f"❌ SDXL demo failed: {e}")
    
    # Demo 3: Image-to-Image Pipeline
    logger.info("\n🔄 Demo 3: Image-to-Image Pipeline")
    try:
        # Create sample input image
        input_image = create_sample_image((512, 512), (150, 100, 200))
        input_image.save("demo_input_image.png")
        logger.info("Created demo_input_image.png")
        
        config = GenerationConfig(
            prompt="Transform this into a futuristic cityscape with neon lights",
            image=input_image,
            strength=0.7,
            num_inference_steps=20,
            guidance_scale=7.5,
            num_images_per_prompt=1
        )
        
        images = manager.generate_image("stable-diffusion-img2img", config)
        logger.info(f"Generated {len(images)} images with img2img pipeline")
        
        # Save images
        for i, img in enumerate(images):
            img.save(f"demo_img2img_{i}.png")
            logger.info(f"Saved demo_img2img_{i}.png")
            
    except Exception as e:
        logger.error(f"❌ Image-to-image demo failed: {e}")
    
    # Demo 4: Inpainting Pipeline
    logger.info("\n🎭 Demo 4: Inpainting Pipeline")
    try:
        # Create sample input image and mask
        input_image = create_sample_image((512, 512), (200, 150, 100))
        mask_image = create_sample_mask((512, 512))
        
        input_image.save("demo_inpaint_input.png")
        mask_image.save("demo_inpaint_mask.png")
        logger.info("Created demo_inpaint_input.png and demo_inpaint_mask.png")
        
        config = GenerationConfig(
            prompt="Fill the masked area with a beautiful flower garden",
            image=input_image,
            mask_image=mask_image,
            num_inference_steps=20,
            guidance_scale=7.5,
            num_images_per_prompt=1
        )
        
        images = manager.generate_image("stable-diffusion-inpaint", config)
        logger.info(f"Generated {len(images)} images with inpainting pipeline")
        
        # Save images
        for i, img in enumerate(images):
            img.save(f"demo_inpaint_{i}.png")
            logger.info(f"Saved demo_inpaint_{i}.png")
            
    except Exception as e:
        logger.error(f"❌ Inpainting demo failed: {e}")
    
    # Demo 5: ControlNet Pipeline
    logger.info("\n🎯 Demo 5: ControlNet Pipeline")
    try:
        config = GenerationConfig(
            prompt="A detailed portrait of a wise old wizard",
            height=512,
            width=512,
            num_inference_steps=20,
            guidance_scale=7.5,
            controlnet_conditioning_scale=1.0,
            control_guidance_start=0.0,
            control_guidance_end=1.0,
            num_images_per_prompt=1
        )
        
        images = manager.generate_image("stable-diffusion-controlnet", config)
        logger.info(f"Generated {len(images)} images with ControlNet pipeline")
        
        # Save images
        for i, img in enumerate(images):
            img.save(f"demo_controlnet_{i}.png")
            logger.info(f"Saved demo_controlnet_{i}.png")
            
    except Exception as e:
        logger.error(f"❌ ControlNet demo failed: {e}")
    
    # Demo 6: Pipeline Analysis
    logger.info("\n🔍 Demo 6: Pipeline Analysis")
    try:
        for pipeline_name in pipelines:
            if pipeline_name in manager.models:
                analysis = manager.analyze_pipeline(pipeline_name)
                logger.info(f"\n📊 Analysis for {pipeline_name}:")
                for key, value in analysis.items():
                    logger.info(f"  {key}: {value}")
                    
    except Exception as e:
        logger.error(f"❌ Pipeline analysis failed: {e}")
    
    # Demo 7: Pipeline Comparison
    logger.info("\n⚖️ Demo 7: Pipeline Comparison")
    try:
        comparison_data = []
        
        for pipeline_name in pipelines:
            if pipeline_name in manager.models:
                config = manager.get_model_config(pipeline_name)
                analysis = manager.analyze_pipeline(pipeline_name)
                
                comparison_data.append({
                    "name": pipeline_name,
                    "pipeline_type": config.pipeline_type.value,
                    "model_type": config.model_type.value,
                    "supports_img2img": analysis["supports_img2img"],
                    "supports_inpainting": analysis["supports_inpainting"],
                    "supports_controlnet": analysis["supports_controlnet"]
                })
        
        logger.info("\n📋 Pipeline Comparison Table:")
        logger.info("Name".ljust(30) + "Type".ljust(20) + "Model".ljust(20) + "Img2Img".ljust(10) + "Inpaint".ljust(10) + "ControlNet".ljust(10))
        logger.info("-" * 100)
        
        for data in comparison_data:
            logger.info(
                f"{data['name'][:29].ljust(30)}"
                f"{data['pipeline_type'][:19].ljust(20)}"
                f"{data['model_type'][:19].ljust(20)}"
                f"{str(data['supports_img2img']).ljust(10)}"
                f"{str(data['supports_inpainting']).ljust(10)}"
                f"{str(data['supports_controlnet']).ljust(10)}"
            )
            
    except Exception as e:
        logger.error(f"❌ Pipeline comparison failed: {e}")
    
    logger.info("\n🎉 Enhanced Diffusion Pipelines Demo Completed!")
    logger.info("📁 Generated demo images have been saved to the current directory")

if __name__ == "__main__":
    import threading
    demo_pipeline_types()
