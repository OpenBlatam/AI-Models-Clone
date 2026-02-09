#!/usr/bin/env python3
"""
Comprehensive Gradio Interface for Diffusion Models

This module provides a production-ready Gradio interface for diffusion models
following official documentation best practices from PyTorch, Transformers, 
Diffusers, and Gradio.

Features:
- Modern Gradio 4.x interface with Blocks
- Comprehensive error handling and validation
- Real-time model loading and caching
- Advanced UI components and themes
- Performance monitoring and optimization
- Proper PyTorch integration with device management
- Diffusers pipeline integration
- Responsive design with proper layouts
"""

import gradio as gr
import torch
import numpy as np
from PIL import Image
import logging
import time
import traceback
from typing import Optional, Tuple, Dict, Any, List, Union
from pathlib import Path
import json
import asyncio
from functools import wraps
import warnings

# Try to import diffusers components
try:
    from diffusers import (
        StableDiffusionPipeline, StableDiffusionXLPipeline,
        DDIMScheduler, DDPMScheduler, EulerDiscreteScheduler,
        DPMSolverMultistepScheduler, DPMSolverSinglestepScheduler
    )
    from diffusers.utils import randn_tensor
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    warnings.warn("Diffusers library not available. Some features will be limited.")

# Try to import transformers
try:
    from transformers import CLIPTextModel, CLIPTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    warnings.warn("Transformers library not available. Some features will be limited.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DiffusionModelManager:
    """Manages diffusion model loading, caching, and inference."""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self.current_model = None
        self.model_configs = {
            "stable_diffusion_1.5": {
                "model_id": "runwayml/stable-diffusion-v1-5",
                "pipeline_class": StableDiffusionPipeline if DIFFUSERS_AVAILABLE else None,
                "description": "Standard Stable Diffusion (512x512)",
                "max_resolution": 512
            },
            "stable_diffusion_xl": {
                "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
                "pipeline_class": StableDiffusionXLPipeline if DIFFUSERS_AVAILABLE else None,
                "description": "High-quality XL model (1024x1024)",
                "max_resolution": 1024
            }
        }
        
        logger.info(f"DiffusionModelManager initialized on device: {self.device}")
    
    def load_model(self, model_name: str) -> bool:
        """Load a diffusion model."""
        if not DIFFUSERS_AVAILABLE:
            logger.error("Diffusers library not available")
            return False
        
        if model_name in self.models:
            self.current_model = self.models[model_name]
            logger.info(f"Model {model_name} already loaded")
            return True
        
        try:
            config = self.model_configs.get(model_name)
            if not config:
                logger.error(f"Unknown model: {model_name}")
                return False
            
            logger.info(f"Loading model: {model_name}")
            start_time = time.time()
            
            # Load pipeline with optimizations
            pipeline = config["pipeline_class"].from_pretrained(
                config["model_id"],
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                safety_checker=None,
                requires_safety_checking=False
            )
            
            # Apply optimizations
            if self.device.type == "cuda":
                pipeline.enable_attention_slicing()
                pipeline.enable_vae_slicing()
                pipeline.enable_model_cpu_offload()
                if hasattr(pipeline, 'enable_xformers_memory_efficient_attention'):
                    pipeline.enable_xformers_memory_efficient_attention()
            
            pipeline.to(self.device)
            
            loading_time = time.time() - start_time
            logger.info(f"Model {model_name} loaded in {loading_time:.2f}s")
            
            self.models[model_name] = pipeline
            self.current_model = pipeline
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
        def get_current_model_name(self) -> str:
        """Get the name of the currently loaded model."""
        for name, model in self.models.items():
            if model is self.current_model:
                return name
        return "unknown"
    
    def generate_image(self, prompt: str, negative_prompt: str = "", 
                       num_inference_steps: int = 50, guidance_scale: float = 7.5,
                       height: int = 512, width: int = 512, seed: Optional[int] = None) -> Tuple[Image.Image, Dict[str, Any]]:
        """Generate image using current model."""
        if not self.current_model:
            raise RuntimeError("No model loaded")
        
        try:
            start_time = time.time()
            
            # Set seed if provided
            if seed is not None:
                torch.manual_seed(seed)
                if self.device.type == "cuda":
                    torch.cuda.manual_s


class GradioDiffusionInterface:
    """Main Gradio interface for diffusion models."""
    
    def __init__(self):
        self.model_manager = DiffusionModelManager()
        self.performance_metrics = {
            'total_generations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_generation_time': 0.0
        }
        
        # Load default model
        self.model_manager.load_model("stable_diffusion_1.5")
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        
        # Custom CSS for modern styling
        custom_css = """
        .gradio-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .main-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .model-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        .generation-controls {
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .output-section {
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        """
        
        with gr.Blocks(
            title="🎨 Diffusion Models Interface",
            theme=gr.themes.Soft(),
            css=custom_css
        ) as interface:
            
            # Header
            with gr.Row():
                gr.HTML("""
                    <div class="main-header">
                        <h1>🎨 Diffusion Models Interface</h1>
                        <p>Generate stunning images with state-of-the-art diffusion models</p>
                    </div>
                """)
            
            # Model Selection and Info
            with gr.Row():
                with gr.Column(scale=1):
                    model_dropdown = gr.Dropdown(
                        choices=list(self.model_manager.model_configs.keys()),
                        value="stable_diffusion_1.5",
                        label="Model",
                        info="Select the diffusion model to use"
                    )
                    
                    model_info = gr.HTML("""
                        <div class="model-info">
                            <h4>Model Information</h4>
                            <p><strong>Current:</strong> Stable Diffusion 1.5</p>
                            <p><strong>Resolution:</strong> Up to 512x512</p>
                            <p><strong>Description:</strong> Standard Stable Diffusion for high-quality image generation</p>
                        </div>
                    """)
                
                with gr.Column(scale=2):
                    device_info = gr.HTML(f"""
                        <div class="model-info">
                            <h4>Device Information</h4>
                            <p><strong>Device:</strong> {self.model_manager.device}</p>
                            <p><strong>CUDA Available:</strong> {torch.cuda.is_available()}</p>
                            <p><strong>Memory:</strong> {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB</p>
                        </div>
                    """)
            
            # Generation Controls
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Group(elem_classes="generation-controls"):
                        gr.Markdown("### 🎯 Generation Parameters")
                        
                        prompt_input = gr.Textbox(
                            label="Prompt",
                            placeholder="A beautiful landscape with mountains and lake, photorealistic, 8k",
                            lines=3,
                            max_lines=5
                        )
                        
                        negative_prompt_input = gr.Textbox(
                            label="Negative Prompt",
                            placeholder="blurry, low quality, distorted, ugly, bad anatomy",
                            lines=2,
                            max_lines=3
                        )
                        
                        with gr.Row():
                            with gr.Column():
                                num_steps = gr.Slider(
                                    minimum=10, maximum=100, value=50, step=1,
                                    label="Inference Steps",
                                    info="Higher = better quality, slower generation"
                                )
                                guidance_scale = gr.Slider(
                                    minimum=1.0, maximum=20.0, value=7.5, step=0.1,
                                    label="Guidance Scale",
                                    info="Higher = more prompt adherence"
                                )
                            
                            with gr.Column():
                                height = gr.Slider(
                                    minimum=256, maximum=1024, value=512, step=64,
                                    label="Height",
                                    info="Image height in pixels"
                                )
                                width = gr.Slider(
                                    minimum=256, maximum=1024, value=512, step=64,
                                    label="Width",
                                    info="Image width in pixels"
                                )
                        
                        seed_input = gr.Number(
                            label="Seed",
                            value=-1,
                            info="Set to -1 for random seed, or specific number for reproducible results"
                        )
                        
                        generate_btn = gr.Button(
                            "🚀 Generate Image",
                            variant="primary",
                            size="lg"
                        )
                
                with gr.Column(scale=1):
                    with gr.Group(elem_classes="generation-controls"):
                        gr.Markdown("### ⚙️ Advanced Settings")
                        
                        batch_size = gr.Slider(
                            minimum=1, maximum=4, value=1, step=1,
                            label="Batch Size",
                            info="Number of images to generate"
                        )
                        
                        enable_safety = gr.Checkbox(
                            label="Enable Safety Checker",
                            value=False,
                            info="Filter inappropriate content"
                        )
                        
                        enable_attention_slicing = gr.Checkbox(
                            label="Attention Slicing",
                            value=True,
                            info="Reduce memory usage"
                        )
                        
                        enable_vae_slicing = gr.Checkbox(
                            label="VAE Slicing",
                            value=True,
                            info="Handle high resolutions"
                        )
            
            # Output Section
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Group(elem_classes="output-section"):
                        gr.Markdown("### 🖼️ Generated Image")
                        output_image = gr.Image(
                            label="Generated Image",
                            type="pil",
                            height=512
                        )
                        
                        with gr.Row():
                            download_btn = gr.Button("💾 Download", variant="secondary")
                            regenerate_btn = gr.Button("🔄 Regenerate", variant="secondary")
                
                with gr.Column(scale=1):
                    with gr.Group(elem_classes="output-section"):
                        gr.Markdown("### 📊 Generation Info")
                        generation_info = gr.JSON(
                            label="Generation Details",
                            value={}
                        )
                        
                        performance_metrics = gr.JSON(
                            label="Performance Metrics",
                            value=self.performance_metrics
                        )
            
            # Event Handlers
            def on_model_change(model_name):
                """Handle model selection change."""
                try:
                    success = self.model_manager.load_model(model_name)
                    if success:
                        config = self.model_manager.model_configs[model_name]
                        info_html = f"""
                            <div class="model-info">
                                <h4>Model Information</h4>
                                <p><strong>Current:</strong> {model_name.replace('_', ' ').title()}</p>
                                <p><strong>Resolution:</strong> Up to {config['max_resolution']}x{config['max_resolution']}</p>
                                <p><strong>Description:</strong> {config['description']}</p>
                            </div>
                        """
                        return info_html
                    else:
                        return f"<div class='model-info'><p>❌ Failed to load model: {model_name}</p></div>"
                except Exception as e:
                    logger.error(f"Model change error: {e}")
                    return f"<div class='model-info'><p>❌ Error: {str(e)}</p></div>"
            
            def on_generate(prompt, negative_prompt, num_steps, guidance_scale, 
                           height, width, seed, batch_size, enable_safety, 
                           enable_attention_slicing, enable_vae_slicing):
                """Handle image generation."""
                try:
                    start_time = time.time()
                    
                    # Validate inputs
                    if not prompt or prompt.strip() == "":
                        raise ValueError("Prompt cannot be empty")
                    
                    if height > 1024 or width > 1024:
                        raise ValueError("Maximum resolution is 1024x1024")
                    
                    # Set random seed if -1
                    if seed == -1:
                        seed = torch.randint(0, 2**32 - 1, (1,)).item()
                    
                    # Generate image
                    image, metadata = self.model_manager.generate_image(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        num_inference_steps=num_steps,
                        guidance_scale=guidance_scale,
                        height=height,
                        width=width,
                        seed=seed
                    )
                    
                    # Update performance metrics
                    self.performance_metrics['total_generations'] += 1
                    self.performance_metrics['successful_generations'] += 1
                    self.performance_metrics['average_generation_time'] = (
                        (self.performance_metrics['average_generation_time'] * 
                         (self.performance_metrics['successful_generations'] - 1) + 
                         metadata['generation_time']) / 
                        self.performance_metrics['successful_generations']
                    )
                    
                    return (
                        image,
                        metadata,
                        self.performance_metrics
                    )
                    
                except Exception as e:
                    logger.error(f"Generation error: {e}")
                    self.performance_metrics['total_generations'] += 1
                    self.performance_metrics['failed_generations'] += 1
                    
                    error_metadata = {
                        "error": str(e),
                        "prompt": prompt,
                        "timestamp": time.time()
                    }
                    
                    return (
                        None,
                        error_metadata,
                        self.performance_metrics
                    )
            
            def on_regenerate():
                """Handle regenerate button click."""
                return None, {}, self.performance_metrics
            
            # Connect events
            model_dropdown.change(
                fn=on_model_change,
                inputs=[model_dropdown],
                outputs=[model_info]
            )
            
            generate_btn.click(
                fn=on_generate,
                inputs=[
                    prompt_input, negative_prompt_input, num_steps, guidance_scale,
                    height, width, seed_input, batch_size, enable_safety,
                    enable_attention_slicing, enable_vae_slicing
                ],
                outputs=[
                    output_image, generation_info, performance_metrics
                ]
            )
            
            regenerate_btn.click(
                fn=on_regenerate,
                outputs=[output_image, generation_info, performance_metrics]
            )
            
            # Download functionality
            download_btn.click(
                fn=lambda img: img,
                inputs=[output_image],
                outputs=[gr.File(label="Download Image")]
            )
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface."""
        interface = self.create_interface()
        
        # Default launch parameters
        default_kwargs = {
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,
            "debug": False,
            "show_error": True,
            "enable_queue": True,
            "max_threads": 4
        }
        
        # Update with provided kwargs
        default_kwargs.update(kwargs)
        
        logger.info(f"Launching Gradio interface on port {default_kwargs['server_port']}")
        return interface.launch(**default_kwargs)


def create_demo() -> gr.Blocks:
    """Create and return the diffusion demo interface."""
    demo = GradioDiffusionInterface()
    return demo.create_interface()


if __name__ == "__main__":
    # Create and launch the interface
    demo = GradioDiffusionInterface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )
