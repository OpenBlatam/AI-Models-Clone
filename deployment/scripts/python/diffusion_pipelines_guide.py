#!/usr/bin/env python3
"""
Diffusion Pipelines Guide for Blaze AI
Comprehensive guide to using different Hugging Face Diffusers pipelines
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass
import logging
from tqdm import tqdm
import warnings
import os
from PIL import Image
import requests
from io import BytesIO

# Diffusers imports
try:
    from diffusers import (
        # Core pipelines
        StableDiffusionPipeline, StableDiffusionXLPipeline,
        StableDiffusionImg2ImgPipeline, StableDiffusionInpaintPipeline,
        StableDiffusionUpscalePipeline, StableDiffusionControlNetPipeline,
        
        # ControlNet
        ControlNetModel,
        
        # Schedulers
        DDIMScheduler, DDPMScheduler, EulerDiscreteScheduler,
        DPMSolverMultistepScheduler, UniPCMultistepScheduler,
        
        # Models
        AutoencoderKL, UNet2DConditionModel,
        
        # Utilities
        make_image_grid, randn_tensor
    )
    from diffusers.utils import logging as diffusers_logging
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    warnings.warn("Diffusers library not available. Install with: pip install diffusers")

# Transformers imports
try:
    from transformers import (
        CLIPTextModel, CLIPTokenizer, CLIPTextModelWithProjection,
        AutoTokenizer, AutoModel
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    warnings.warn("Transformers library not available. Install with: pip install transformers")

warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure diffusers logging
if DIFFUSERS_AVAILABLE:
    diffusers_logging.set_verbosity_info()


@dataclass
class PipelineConfig:
    """Configuration for diffusion pipelines"""
    # Model settings
    model_id: str = "runwayml/stable-diffusion-v1-5"
    model_type: str = "stable-diffusion"  # stable-diffusion, stable-diffusion-xl, controlnet
    
    # Device settings
    device: str = "auto"  # auto, cuda, cpu, mps
    torch_dtype: str = "auto"  # auto, fp16, bf16, fp32
    
    # Generation settings
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    height: int = 512
    width: int = 512
    batch_size: int = 1
    
    # Safety and optimization
    safety_checker: bool = True
    requires_safety_checking: bool = True
    enable_attention_slicing: bool = True
    enable_xformers_memory_efficient_attention: bool = True
    
    # ControlNet settings
    controlnet_model_id: str = "lllyasviel/sd-controlnet-canny"
    
    # LoRA settings
    use_lora: bool = False
    lora_path: str = ""
    
    # Textual inversion
    use_textual_inversion: bool = False
    textual_inversion_path: str = ""


class DiffusionPipelineManager:
    """Manager for different diffusion pipelines"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        
        # Auto-detect device
        if config.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = config.device
        
        # Auto-detect torch dtype
        if config.torch_dtype == "auto":
            if self.device == "cuda":
                self.torch_dtype = torch.float16
            else:
                self.torch_dtype = torch.float32
        else:
            dtype_map = {
                "fp16": torch.float16,
                "bf16": torch.bfloat16,
                "fp32": torch.float32
            }
            self.torch_dtype = dtype_map.get(config.torch_dtype, torch.float32)
        
        self.pipelines = {}
        self.current_pipeline = None
        
        logger.info(f"Using device: {self.device}")
        logger.info(f"Using torch dtype: {self.torch_dtype}")
    
    def load_stable_diffusion_pipeline(self) -> StableDiffusionPipeline:
        """Load Stable Diffusion pipeline"""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers library not available")
        
        logger.info(f"Loading Stable Diffusion pipeline: {self.config.model_id}")
        
        # Load pipeline
        pipeline = StableDiffusionPipeline.from_pretrained(
            self.config.model_id,
            torch_dtype=self.torch_dtype,
            safety_checker=None if not self.config.safety_checker else None,
            requires_safety_checking=self.config.requires_safety_checking
        )
        
        # Move to device
        pipeline = pipeline.to(self.device)
        
        # Apply optimizations
        self._apply_pipeline_optimizations(pipeline)
        
        # Store pipeline
        self.pipelines["stable_diffusion"] = pipeline
        self.current_pipeline = pipeline
        
        logger.info("Stable Diffusion pipeline loaded successfully")
        return pipeline
    
    def load_stable_diffusion_xl_pipeline(self) -> StableDiffusionXLPipeline:
        """Load Stable Diffusion XL pipeline"""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers library not available")
        
        logger.info(f"Loading Stable Diffusion XL pipeline: {self.config.model_id}")
        
        # Load pipeline
        pipeline = StableDiffusionXLPipeline.from_pretrained(
            self.config.model_id,
            torch_dtype=self.torch_dtype,
            safety_checker=None if not self.config.safety_checker else None,
            requires_safety_checking=self.config.requires_safety_checking
        )
        
        # Move to device
        pipeline = pipeline.to(self.device)
        
        # Apply optimizations
        self._apply_pipeline_optimizations(pipeline)
        
        # Store pipeline
        self.pipelines["stable_diffusion_xl"] = pipeline
        self.current_pipeline = pipeline
        
        logger.info("Stable Diffusion XL pipeline loaded successfully")
        return pipeline
    
    def load_img2img_pipeline(self) -> StableDiffusionImg2ImgPipeline:
        """Load image-to-image pipeline"""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers library not available")
        
        logger.info(f"Loading image-to-image pipeline: {self.config.model_id}")
        
        # Load pipeline
        pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            self.config.model_id,
            torch_dtype=self.torch_dtype,
            safety_checker=None if not self.config.safety_checker else None
        )
        
        # Move to device
        pipeline = pipeline.to(self.device)
        
        # Apply optimizations
        self._apply_pipeline_optimizations(pipeline)
        
        # Store pipeline
        self.pipelines["img2img"] = pipeline
        self.current_pipeline = pipeline
        
        logger.info("Image-to-image pipeline loaded successfully")
        return pipeline
    
    def load_inpaint_pipeline(self) -> StableDiffusionInpaintPipeline:
        """Load inpainting pipeline"""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers library not available")
        
        logger.info(f"Loading inpainting pipeline: {self.config.model_id}")
        
        # Load pipeline
        pipeline = StableDiffusionInpaintPipeline.from_pretrained(
            self.config.model_id,
            torch_dtype=self.torch_dtype,
            safety_checker=None if not self.config.safety_checker else None
        )
        
        # Move to device
        pipeline = pipeline.to(self.device)
        
        # Apply optimizations
        self._apply_pipeline_optimizations(pipeline)
        
        # Store pipeline
        self.pipelines["inpaint"] = pipeline
        self.current_pipeline = pipeline
        
        logger.info("Inpainting pipeline loaded successfully")
        return pipeline
    
    def load_controlnet_pipeline(self) -> StableDiffusionControlNetPipeline:
        """Load ControlNet pipeline"""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers library not available")
        
        logger.info(f"Loading ControlNet pipeline: {self.config.model_id}")
        
        # Load ControlNet model
        controlnet = ControlNetModel.from_pretrained(
            self.config.controlnet_model_id,
            torch_dtype=self.torch_dtype
        )
        
        # Load Stable Diffusion pipeline with ControlNet
        pipeline = StableDiffusionControlNetPipeline.from_pretrained(
            self.config.model_id,
            controlnet=controlnet,
            torch_dtype=self.torch_dtype,
            safety_checker=None if not self.config.safety_checker else None
        )
        
        # Move to device
        pipeline = pipeline.to(self.device)
        
        # Apply optimizations
        self._apply_pipeline_optimizations(pipeline)
        
        # Store pipeline
        self.pipelines["controlnet"] = pipeline
        self.current_pipeline = pipeline
        
        logger.info("ControlNet pipeline loaded successfully")
        return pipeline
    
    def load_upscale_pipeline(self) -> StableDiffusionUpscalePipeline:
        """Load upscaling pipeline"""
        if not DIFFUSERS_AVAILABLE:
            raise ImportError("Diffusers library not available")
        
        logger.info(f"Loading upscaling pipeline: {self.config.model_id}")
        
        # Load pipeline
        pipeline = StableDiffusionUpscalePipeline.from_pretrained(
            self.config.model_id,
            torch_dtype=self.torch_dtype
        )
        
        # Move to device
        pipeline = pipeline.to(self.device)
        
        # Apply optimizations
        self._apply_pipeline_optimizations(pipeline)
        
        # Store pipeline
        self.pipelines["upscale"] = pipeline
        self.current_pipeline = pipeline
        
        logger.info("Upscaling pipeline loaded successfully")
        return pipeline
    
    def _apply_pipeline_optimizations(self, pipeline):
        """Apply memory and performance optimizations to pipeline"""
        try:
            # Enable attention slicing for memory efficiency
            if self.config.enable_attention_slicing:
                pipeline.enable_attention_slicing()
                logger.info("✓ Attention slicing enabled")
        except Exception as e:
            logger.warning(f"Could not enable attention slicing: {e}")
        
        try:
            # Enable xformers memory efficient attention
            if self.config.enable_xformers_memory_efficient_attention:
                pipeline.enable_xformers_memory_efficient_attention()
                logger.info("✓ XFormers memory efficient attention enabled")
        except Exception as e:
            logger.warning(f"Could not enable xformers: {e}")
        
        try:
            # Enable model CPU offload for memory efficiency
            pipeline.enable_model_cpu_offload()
            logger.info("✓ Model CPU offload enabled")
        except Exception as e:
            logger.warning(f"Could not enable CPU offload: {e}")
    
    def get_pipeline(self, pipeline_type: str):
        """Get a specific pipeline by type"""
        if pipeline_type not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_type} not loaded. Available: {list(self.pipelines.keys())}")
        return self.pipelines[pipeline_type]
    
    def list_loaded_pipelines(self) -> List[str]:
        """List all loaded pipelines"""
        return list(self.pipelines.keys())
    
    def unload_pipeline(self, pipeline_type: str):
        """Unload a specific pipeline to free memory"""
        if pipeline_type in self.pipelines:
            del self.pipelines[pipeline_type]
            if self.current_pipeline == self.pipelines.get(pipeline_type):
                self.current_pipeline = None
            logger.info(f"Pipeline {pipeline_type} unloaded")
    
    def clear_all_pipelines(self):
        """Clear all pipelines to free memory"""
        self.pipelines.clear()
        self.current_pipeline = None
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        logger.info("All pipelines cleared")


class PipelineUsageExamples:
    """Examples of using different pipelines"""
    
    def __init__(self, pipeline_manager: DiffusionPipelineManager):
        self.pipeline_manager = pipeline_manager
    
    def text_to_image_example(self, prompt: str, negative_prompt: str = "") -> Image.Image:
        """Generate image from text using Stable Diffusion"""
        logger.info(f"Generating image from prompt: {prompt}")
        
        # Get pipeline
        pipeline = self.pipeline_manager.get_pipeline("stable_diffusion")
        
        # Generate image
        with torch.autocast(self.pipeline_manager.device):
            result = pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=self.pipeline_manager.config.num_inference_steps,
                guidance_scale=self.pipeline_manager.config.guidance_scale,
                height=self.pipeline_manager.config.height,
                width=self.pipeline_manager.config.width
            )
        
        image = result.images[0]
        logger.info("Image generation completed")
        return image
    
    def text_to_image_xl_example(self, prompt: str, negative_prompt: str = "") -> Image.Image:
        """Generate image from text using Stable Diffusion XL"""
        logger.info(f"Generating XL image from prompt: {prompt}")
        
        # Get pipeline
        pipeline = self.pipeline_manager.get_pipeline("stable_diffusion_xl")
        
        # Generate image
        with torch.autocast(self.pipeline_manager.device):
            result = pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=self.pipeline_manager.config.num_inference_steps,
                guidance_scale=self.pipeline_manager.config.guidance_scale,
                height=self.pipeline_manager.config.height,
                width=self.pipeline_manager.config.width
            )
        
        image = result.images[0]
        logger.info("XL image generation completed")
        return image
    
    def img2img_example(self, init_image: Image.Image, prompt: str, 
                        strength: float = 0.75) -> Image.Image:
        """Transform image using image-to-image pipeline"""
        logger.info(f"Transforming image with prompt: {prompt}")
        
        # Get pipeline
        pipeline = self.pipeline_manager.get_pipeline("img2img")
        
        # Generate image
        with torch.autocast(self.pipeline_manager.device):
            result = pipeline(
                prompt=prompt,
                image=init_image,
                strength=strength,
                num_inference_steps=self.pipeline_manager.config.num_inference_steps,
                guidance_scale=self.pipeline_manager.config.guidance_scale
            )
        
        image = result.images[0]
        logger.info("Image-to-image transformation completed")
        return image
    
    def inpaint_example(self, init_image: Image.Image, mask_image: Image.Image, 
                       prompt: str) -> Image.Image:
        """Inpaint image using inpainting pipeline"""
        logger.info(f"Inpainting image with prompt: {prompt}")
        
        # Get pipeline
        pipeline = self.pipeline_manager.get_pipeline("inpaint")
        
        # Generate image
        with torch.autocast(self.pipeline_manager.device):
            result = pipeline(
                prompt=prompt,
                image=init_image,
                mask_image=mask_image,
                num_inference_steps=self.pipeline_manager.config.num_inference_steps,
                guidance_scale=self.pipeline_manager.config.guidance_scale
            )
        
        image = result.images[0]
        logger.info("Inpainting completed")
        return image
    
    def controlnet_example(self, control_image: Image.Image, prompt: str) -> Image.Image:
        """Generate image using ControlNet pipeline"""
        logger.info(f"Generating image with ControlNet and prompt: {prompt}")
        
        # Get pipeline
        pipeline = self.pipeline_manager.get_pipeline("controlnet")
        
        # Generate image
        with torch.autocast(self.pipeline_manager.device):
            result = pipeline(
                prompt=prompt,
                image=control_image,
                num_inference_steps=self.pipeline_manager.config.num_inference_steps,
                guidance_scale=self.pipeline_manager.config.guidance_scale,
                height=self.pipeline_manager.config.height,
                width=self.pipeline_manager.config.width
            )
        
        image = result.images[0]
        logger.info("ControlNet generation completed")
        return image
    
    def upscale_example(self, init_image: Image.Image, prompt: str) -> Image.Image:
        """Upscale image using upscaling pipeline"""
        logger.info(f"Upscaling image with prompt: {prompt}")
        
        # Get pipeline
        pipeline = self.pipeline_manager.get_pipeline("upscale")
        
        # Generate image
        with torch.autocast(self.pipeline_manager.device):
            result = pipeline(
                prompt=prompt,
                image=init_image,
                num_inference_steps=self.pipeline_manager.config.num_inference_steps,
                guidance_scale=self.pipeline_manager.config.guidance_scale
            )
        
        image = result.images[0]
        logger.info("Image upscaling completed")
        return image


class PipelineComparison:
    """Compare different pipelines"""
    
    def __init__(self, pipeline_manager: DiffusionPipelineManager):
        self.pipeline_manager = pipeline_manager
    
    def compare_generation_speed(self, prompt: str, num_runs: int = 3) -> Dict[str, float]:
        """Compare generation speed of different pipelines"""
        logger.info(f"Comparing generation speed with {num_runs} runs")
        
        results = {}
        test_prompt = prompt
        
        # Test Stable Diffusion
        if "stable_diffusion" in self.pipeline_manager.pipelines:
            pipeline = self.pipeline_manager.get_pipeline("stable_diffusion")
            times = []
            
            for i in range(num_runs):
                start_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
                end_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
                
                if start_time and end_time:
                    start_time.record()
                else:
                    start_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
                
                with torch.autocast(self.pipeline_manager.device):
                    _ = pipeline(
                        prompt=test_prompt,
                        num_inference_steps=20,  # Use fewer steps for speed test
                        height=512,
                        width=512
                    )
                
                if end_time:
                    end_time.record()
                    torch.cuda.synchronize()
                    elapsed_time = start_time.elapsed_time(end_time) / 1000.0  # Convert to seconds
                    times.append(elapsed_time)
                else:
                    times.append(0.0)
            
            results["stable_diffusion"] = {
                "mean_time": np.mean(times),
                "std_time": np.std(times),
                "times": times
            }
        
        # Test Stable Diffusion XL
        if "stable_diffusion_xl" in self.pipeline_manager.pipelines:
            pipeline = self.pipeline_manager.get_pipeline("stable_diffusion_xl")
            times = []
            
            for i in range(num_runs):
                start_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
                end_time = torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
                
                if start_time and end_time:
                    start_time.record()
                
                with torch.autocast(self.pipeline_manager.device):
                    _ = pipeline(
                        prompt=test_prompt,
                        num_inference_steps=20,
                        height=512,
                        width=512
                    )
                
                if end_time:
                    end_time.record()
                    torch.cuda.synchronize()
                    elapsed_time = start_time.elapsed_time(end_time) / 1000.0
                    times.append(elapsed_time)
                else:
                    times.append(0.0)
            
            results["stable_diffusion_xl"] = {
                "mean_time": np.mean(times),
                "std_time": np.std(times),
                "times": times
            }
        
        return results
    
    def compare_memory_usage(self) -> Dict[str, Dict[str, float]]:
        """Compare memory usage of different pipelines"""
        logger.info("Comparing memory usage of different pipelines")
        
        results = {}
        
        for pipeline_name, pipeline in self.pipeline_manager.pipelines.items():
            # Clear cache before measurement
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()
                
                # Measure memory before
                memory_before = torch.cuda.memory_allocated() / 1024**3  # GB
                
                # Run a simple forward pass
                with torch.autocast(self.pipeline_manager.device):
                    _ = pipeline(
                        prompt="test",
                        num_inference_steps=1,
                        height=64,
                        width=64
                    )
                
                # Measure memory after
                memory_after = torch.cuda.memory_allocated() / 1024**3  # GB
                peak_memory = torch.cuda.max_memory_allocated() / 1024**3  # GB
                
                results[pipeline_name] = {
                    "memory_before_gb": memory_before,
                    "memory_after_gb": memory_after,
                    "peak_memory_gb": peak_memory,
                    "memory_increase_gb": memory_after - memory_before
                }
        
        return results
    
    def print_comparison_results(self, speed_results: Dict, memory_results: Dict):
        """Print formatted comparison results"""
        logger.info("📊 PIPELINE COMPARISON RESULTS")
        logger.info("=" * 50)
        
        # Speed comparison
        logger.info("\n⚡ SPEED COMPARISON:")
        for pipeline_name, data in speed_results.items():
            logger.info(f"  {pipeline_name}:")
            logger.info(f"    Mean time: {data['mean_time']:.2f}s ± {data['std_time']:.2f}s")
            logger.info(f"    Times: {[f'{t:.2f}s' for t in data['times']]}")
        
        # Memory comparison
        logger.info("\n💾 MEMORY COMPARISON:")
        for pipeline_name, data in memory_results.items():
            logger.info(f"  {pipeline_name}:")
            logger.info(f"    Peak memory: {data['peak_memory_gb']:.2f} GB")
            logger.info(f"    Memory increase: {data['memory_increase_gb']:.2f} GB")


def demonstrate_pipelines():
    """Demonstrate different diffusion pipelines"""
    logger.info("🚀 Starting Diffusion Pipelines Demonstration")
    logger.info("=" * 60)
    
    # 1. Setup pipeline manager
    logger.info("\n⚙️  STEP 1: Setting up Pipeline Manager")
    config = PipelineConfig(
        model_id="runwayml/stable-diffusion-v1-5",
        model_type="stable-diffusion",
        num_inference_steps=20,  # Use fewer steps for demonstration
        height=512,
        width=512
    )
    
    pipeline_manager = DiffusionPipelineManager(config)
    
    # 2. Load different pipelines
    logger.info("\n📦 STEP 2: Loading Different Pipelines")
    
    try:
        # Load Stable Diffusion
        pipeline_manager.load_stable_diffusion_pipeline()
        
        # Load Stable Diffusion XL (if available)
        try:
            xl_config = PipelineConfig(
                model_id="stabilityai/stable-diffusion-xl-base-1.0",
                model_type="stable-diffusion-xl"
            )
            xl_manager = DiffusionPipelineManager(xl_config)
            xl_manager.load_stable_diffusion_xl_pipeline()
            logger.info("✓ Stable Diffusion XL loaded")
        except Exception as e:
            logger.warning(f"Could not load SDXL: {e}")
        
        # Load other pipelines
        pipeline_manager.load_img2img_pipeline()
        pipeline_manager.load_inpaint_pipeline()
        
        # Try to load ControlNet
        try:
            pipeline_manager.load_controlnet_pipeline()
        except Exception as e:
            logger.warning(f"Could not load ControlNet: {e}")
        
        logger.info(f"✓ Loaded pipelines: {pipeline_manager.list_loaded_pipelines()}")
        
    except Exception as e:
        logger.error(f"Failed to load pipelines: {e}")
        return
    
    # 3. Demonstrate pipeline usage
    logger.info("\n🎯 STEP 3: Pipeline Usage Examples")
    
    examples = PipelineUsageExamples(pipeline_manager)
    
    # Text-to-image generation
    test_prompt = "A beautiful landscape with mountains and a lake, digital art"
    
    try:
        logger.info("Generating image with Stable Diffusion...")
        image = examples.text_to_image_example(test_prompt)
        
        # Save the generated image
        image_path = "./generated_image.png"
        image.save(image_path)
        logger.info(f"✓ Image saved to {image_path}")
        
    except Exception as e:
        logger.warning(f"Image generation failed: {e}")
    
    # 4. Compare pipelines
    logger.info("\n🔍 STEP 4: Pipeline Comparison")
    
    comparison = PipelineComparison(pipeline_manager)
    
    try:
        # Compare generation speed
        speed_results = comparison.compare_generation_speed(test_prompt, num_runs=2)
        
        # Compare memory usage
        memory_results = comparison.compare_memory_usage()
        
        # Print results
        comparison.print_comparison_results(speed_results, memory_results)
        
    except Exception as e:
        logger.warning(f"Pipeline comparison failed: {e}")
    
    # 5. Summary
    logger.info("\n📋 SUMMARY: Key Insights About Diffusion Pipelines")
    logger.info("=" * 60)
    
    logger.info("🔍 PIPELINE TYPES:")
    logger.info("   • StableDiffusionPipeline: Standard text-to-image generation")
    logger.info("   • StableDiffusionXLPipeline: Higher resolution, better quality")
    logger.info("   • StableDiffusionImg2ImgPipeline: Transform existing images")
    logger.info("   • StableDiffusionInpaintPipeline: Fill in masked areas")
    logger.info("   • StableDiffusionControlNetPipeline: Control generation with conditions")
    logger.info("   • StableDiffusionUpscalePipeline: Increase image resolution")
    
    logger.info("\n🔍 CHOOSING A PIPELINE:")
    logger.info("   • Text-to-image: StableDiffusionPipeline or StableDiffusionXLPipeline")
    logger.info("   • Image editing: Img2ImgPipeline or InpaintPipeline")
    logger.info("   • Controlled generation: ControlNetPipeline")
    logger.info("   • High quality: StableDiffusionXLPipeline")
    logger.info("   • Fast generation: StableDiffusionPipeline with fewer steps")
    
    logger.info("\n🔍 OPTIMIZATION TIPS:")
    logger.info("   • Enable attention slicing for memory efficiency")
    logger.info("   • Use xformers for faster attention computation")
    logger.info("   • Enable model CPU offload for large models")
    logger.info("   • Use mixed precision (fp16) on supported devices")
    logger.info("   • Adjust inference steps based on quality vs. speed needs")
    
    logger.info("\n✅ Demonstration completed successfully!")
    logger.info("Check the generated image file: generated_image.png")


def main():
    """Main execution function"""
    logger.info("Starting Diffusion Pipelines Guide...")
    
    # Demonstrate pipelines
    demonstrate_pipelines()
    
    logger.info("All demonstrations completed!")


if __name__ == "__main__":
    main()
