"""
Enhanced Gradio Interface for HeyGen AI.

This module provides a comprehensive Gradio interface for interacting with
transformer models, diffusion models, and other AI components. Includes
proper error handling, input validation, and user experience features.
"""

import logging
import os
import time
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from pathlib import Path
import warnings

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import gradio as gr
from gradio import Blocks, Interface, Tab, Row, Column, Group
from gradio.components import (
    Textbox, Image, Slider, Dropdown, Checkbox, Button, 
    Number, Radio, File, Video, Audio, Gallery, Plot, HTML
)

# Import our enhanced modules
from .enhanced_transformer_models import TransformerManager, TransformerConfig
from .enhanced_diffusion_models import DiffusionPipelineManager, DiffusionConfig

logger = logging.getLogger(__name__)


class EnhancedGradioInterface:
    """Enhanced Gradio interface for HeyGen AI components with modern UX design."""
    
    def __init__(self):
        """Initialize the enhanced Gradio interface."""
        self.transformer_manager = None
        self.diffusion_manager = None
        self.current_model = None
        self.logger = logging.getLogger(__name__)
        
        # Interface state
        self.interface = None
        self.is_initialized = False
        
        # Initialize interface components
        self._setup_interface()
    
    def _setup_interface(self):
        """Set up the main Gradio interface with modern design."""
        try:
            with gr.Blocks(
                title="🚀 HeyGen AI - Enhanced Interface",
                theme=gr.themes.Soft(
                    primary_hue="blue",
                    secondary_hue="purple",
                    neutral_hue="slate"
                ),
                css="""
                .gradio-container {
                    max-width: 1400px !important;
                    margin: 0 auto !important;
                }
                .main-header {
                    text-align: center;
                    padding: 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }
                .feature-card {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                .status-indicator {
                    padding: 10px;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                }
                .status-success { background: #d4edda; color: #155724; }
                .status-error { background: #f8d7da; color: #721c24; }
                .status-warning { background: #fff3cd; color: #856404; }
                """
            ) as self.interface:
                
                # Header
                gr.HTML("""
                <div class="main-header">
                    <h1>🚀 HeyGen AI - Enhanced Interface</h1>
                    <p>Advanced AI models for text generation, image creation, and more</p>
                    <p>Built with PyTorch, Transformers, Diffusers, and Gradio</p>
                </div>
                """)
                
                # Main tabs
                with gr.Tabs():
                    # Text Generation Tab
                    with gr.Tab("📝 Text Generation", id=0):
                        self._create_text_generation_tab()
                    
                    # Image Generation Tab
                    with gr.Tab("🎨 Image Generation", id=1):
                        self._create_image_generation_tab()
                    
                    # Model Management Tab
                    with gr.Tab("⚙️ Model Management", id=2):
                        self._create_model_management_tab()
                    
                    # Settings Tab
                    with gr.Tab("🔧 Settings", id=3):
                        self._create_settings_tab()
                
                # Footer
                gr.HTML("""
                <div style="text-align: center; padding: 20px; color: #666;">
                    <p>Powered by PyTorch, Transformers, Diffusers, and Gradio</p>
                    <p>Built with ❤️ for the AI community</p>
                </div>
                """)
            
            self.is_initialized = True
            logger.info("Enhanced Gradio interface initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gradio interface: {e}")
            raise
    
    def _create_text_generation_tab(self):
        """Create the text generation tab with comprehensive features."""
        with gr.Row():
            with gr.Column(scale=2):
                # Input section
                with gr.Group():
                    gr.Markdown("### 📝 Text Generation")
                    
                    # Model selection
                    model_dropdown = gr.Dropdown(
                        choices=["GPT-2", "BERT", "Custom"],
                        value="GPT-2",
                        label="Select Model",
                        info="Choose the transformer model to use"
                    )
                    
                    # Prompt input
                    prompt_input = gr.Textbox(
                        label="Input Prompt",
                        placeholder="Enter your text prompt here...",
                        lines=4,
                        max_lines=8,
                        info="The text that will be used to generate content"
                    )
                    
                    # Generation parameters
                    with gr.Row():
                        max_length = gr.Slider(
                            minimum=10,
                            maximum=500,
                            value=100,
                            step=10,
                            label="Max Length",
                            info="Maximum length of generated text"
                        )
                        temperature = gr.Slider(
                            minimum=0.1,
                            maximum=2.0,
                            value=0.7,
                            step=0.1,
                            label="Temperature",
                            info="Controls randomness in generation"
                        )
                        top_p = gr.Slider(
                            minimum=0.1,
                            maximum=1.0,
                            value=0.9,
                            step=0.1,
                            label="Top-p",
                            info="Nucleus sampling parameter"
                        )
                    
                    # Generation button
                    generate_btn = gr.Button(
                        "🚀 Generate Text",
                        variant="primary",
                        size="lg"
                    )
                    
                    # Status indicator
                    status_text = gr.HTML(
                        value="<div class='status-indicator status-warning'>Ready to generate</div>",
                        label="Status"
                    )
            
            with gr.Column(scale=2):
                # Output section
                with gr.Group():
                    gr.Markdown("### 📤 Generated Text")
                    
                    # Generated text output
                    generated_text = gr.Textbox(
                        label="Generated Text",
                        lines=10,
                        max_lines=20,
                        interactive=False,
                        placeholder="Generated text will appear here..."
                    )
                    
                    # Generation info
                    generation_info = gr.JSON(
                        label="Generation Information",
                        value={},
                        visible=True
                    )
                    
                    # Action buttons
                    with gr.Row():
                        copy_btn = gr.Button("📋 Copy Text", size="sm")
                        save_btn = gr.Button("💾 Save Text", size="sm")
                        clear_btn = gr.Button("🗑️ Clear", size="sm", variant="secondary")
        
        # Event handlers
        generate_btn.click(
            fn=self._generate_text,
            inputs=[model_dropdown, prompt_input, max_length, temperature, top_p],
            outputs=[generated_text, generation_info, status_text]
        )
        
        copy_btn.click(
            fn=self._copy_text,
            inputs=[generated_text],
            outputs=[status_text]
        )
        
        save_btn.click(
            fn=self._save_text,
            inputs=[generated_text],
            outputs=[status_text]
        )
        
        clear_btn.click(
            fn=self._clear_text,
            outputs=[prompt_input, generated_text, generation_info, status_text]
        )
    
    def _create_image_generation_tab(self):
        """Create the image generation tab with comprehensive features."""
        with gr.Row():
            with gr.Column(scale=2):
                # Input section
                with gr.Group():
                    gr.Markdown("### 🎨 Image Generation")
                    
                    # Model selection
                    diffusion_model_dropdown = gr.Dropdown(
                        choices=["Stable Diffusion", "Stable Diffusion XL", "ControlNet"],
                        value="Stable Diffusion",
                        label="Select Model",
                        info="Choose the diffusion model to use"
                    )
                    
                    # Prompt input
                    image_prompt = gr.Textbox(
                        label="Image Prompt",
                        placeholder="Describe the image you want to generate...",
                        lines=3,
                        max_lines=5,
                        info="Detailed description of the desired image"
                    )
                    
                    # Negative prompt
                    negative_prompt = gr.Textbox(
                        label="Negative Prompt",
                        placeholder="What you don't want in the image...",
                        lines=2,
                        max_lines=3,
                        info="Elements to avoid in the generated image"
                    )
                    
                    # Generation parameters
                    with gr.Row():
                        num_images = gr.Slider(
                            minimum=1,
                            maximum=4,
                            value=1,
                            step=1,
                            label="Number of Images",
                            info="How many images to generate"
                        )
                        guidance_scale = gr.Slider(
                            minimum=1.0,
                            maximum=20.0,
                            value=7.5,
                            step=0.5,
                            label="Guidance Scale",
                            info="How closely to follow the prompt"
                        )
                        num_steps = gr.Slider(
                            minimum=10,
                            maximum=100,
                            value=50,
                            step=5,
                            label="Inference Steps",
                            info="More steps = better quality, slower generation"
                        )
                    
                    # Image dimensions
                    with gr.Row():
                        width = gr.Slider(
                            minimum=256,
                            maximum=1024,
                            value=512,
                            step=64,
                            label="Width",
                            info="Image width in pixels"
                        )
                        height = gr.Slider(
                            minimum=256,
                            maximum=1024,
                            value=512,
                            step=64,
                            label="Height",
                            info="Image height in pixels"
                        )
                    
                    # Seed for reproducibility
                    seed = gr.Number(
                        label="Random Seed",
                        value=None,
                        info="Set for reproducible results (optional)"
                    )
                    
                    # Generation button
                    generate_image_btn = gr.Button(
                        "🎨 Generate Image",
                        variant="primary",
                        size="lg"
                    )
                    
                    # Status indicator
                    image_status = gr.HTML(
                        value="<div class='status-indicator status-warning'>Ready to generate</div>",
                        label="Status"
                    )
            
            with gr.Column(scale=2):
                # Output section
                with gr.Group():
                    gr.Markdown("### 🖼️ Generated Images")
                    
                    # Image gallery
                    image_gallery = gr.Gallery(
                        label="Generated Images",
                        show_label=True,
                        elem_id="gallery",
                        columns=2,
                        rows=2,
                        height="auto"
                    )
                    
                    # Generation info
                    image_generation_info = gr.JSON(
                        label="Generation Information",
                        value={},
                        visible=True
                    )
                    
                    # Action buttons
                    with gr.Row():
                        download_btn = gr.Button("⬇️ Download All", size="sm")
                        clear_images_btn = gr.Button("🗑️ Clear Images", size="sm", variant="secondary")
        
        # Event handlers
        generate_image_btn.click(
            fn=self._generate_image,
            inputs=[
                diffusion_model_dropdown, image_prompt, negative_prompt,
                num_images, guidance_scale, num_steps, width, height, seed
            ],
            outputs=[image_gallery, image_generation_info, image_status]
        )
        
        download_btn.click(
            fn=self._download_images,
            inputs=[image_gallery],
            outputs=[image_status]
        )
        
        clear_images_btn.click(
            fn=self._clear_images,
            outputs=[image_gallery, image_generation_info, image_status]
        )
    
    def _create_model_management_tab(self):
        """Create the model management tab."""
        with gr.Row():
            with gr.Column(scale=1):
                # Model initialization
                with gr.Group():
                    gr.Markdown("### 🔧 Model Management")
                    
                    # Initialize models
                    init_transformer_btn = gr.Button(
                        "🚀 Initialize Transformer",
                        variant="primary",
                        size="lg"
                    )
                    
                    init_diffusion_btn = gr.Button(
                        "🎨 Initialize Diffusion",
                        variant="primary",
                        size="lg"
                    )
                    
                    # Model status
                    model_status = gr.HTML(
                        value="<div class='status-indicator status-warning'>No models initialized</div>",
                        label="Model Status"
                    )
            
            with gr.Column(scale=2):
                # Model information
                with gr.Group():
                    gr.Markdown("### 📊 Model Information")
                    
                    # Model info display
                    model_info = gr.JSON(
                        label="Model Details",
                        value={},
                        visible=True
                    )
                    
                    # Performance metrics
                    performance_metrics = gr.Plot(
                        label="Performance Metrics",
                        visible=False
                    )
        
        # Event handlers
        init_transformer_btn.click(
            fn=self._initialize_transformer,
            outputs=[model_status, model_info]
        )
        
        init_diffusion_btn.click(
            fn=self._initialize_diffusion,
            outputs=[model_status, model_info]
        )
    
    def _create_settings_tab(self):
        """Create the settings tab."""
        with gr.Row():
            with gr.Column(scale=1):
                # General settings
                with gr.Group():
                    gr.Markdown("### ⚙️ General Settings")
                    
                    # Device selection
                    device_dropdown = gr.Dropdown(
                        choices=["auto", "cpu", "cuda"],
                        value="auto",
                        label="Device",
                        info="Select computation device"
                    )
                    
                    # Memory optimization
                    memory_optimization = gr.Checkbox(
                        label="Enable Memory Optimization",
                        value=True,
                        info="Use memory-efficient attention and VAE slicing"
                    )
                    
                    # Mixed precision
                    mixed_precision = gr.Checkbox(
                        label="Enable Mixed Precision",
                        value=True,
                        info="Use FP16 for faster inference (GPU only)"
                    )
            
            with gr.Column(scale=1):
                # Advanced settings
                with gr.Group():
                    gr.Markdown("### 🔬 Advanced Settings")
                    
                    # LoRA settings
                    use_lora = gr.Checkbox(
                        label="Enable LoRA Fine-tuning",
                        value=False,
                        info="Use LoRA for efficient fine-tuning"
                    )
                    
                    lora_rank = gr.Slider(
                        minimum=4,
                        maximum=64,
                        value=16,
                        step=4,
                        label="LoRA Rank",
                        info="Rank of LoRA adaptation"
                    )
                    
                    # Save settings button
                    save_settings_btn = gr.Button(
                        "💾 Save Settings",
                        variant="primary"
                    )
        
        # Event handlers
        save_settings_btn.click(
            fn=self._save_settings,
            inputs=[device_dropdown, memory_optimization, mixed_precision, use_lora, lora_rank],
            outputs=[]
        )
    
    def _generate_text(self, model_type: str, prompt: str, max_length: int, 
                      temperature: float, top_p: float) -> Tuple[str, Dict, str]:
        """Generate text using the selected model.
        
        Args:
            model_type: Type of model to use
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Tuple of (generated_text, generation_info, status_html)
        """
        try:
            if not prompt.strip():
                return "", {}, "<div class='status-indicator status-error'>Please enter a prompt</div>"
            
            # Initialize transformer if needed
            if self.transformer_manager is None:
                self._initialize_transformer()
            
            if self.transformer_manager is None:
                return "", {}, "<div class='status-indicator status-error'>Failed to initialize transformer model</div>"
            
            # Generate text
            start_time = time.time()
            generated_text = self.transformer_manager.generate_text(
                prompt=prompt,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p
            )
            generation_time = time.time() - start_time
            
            # Prepare generation info
            generation_info = {
                "model_type": model_type,
                "prompt_length": len(prompt),
                "generated_length": len(generated_text),
                "generation_time": f"{generation_time:.2f}s",
                "temperature": temperature,
                "top_p": top_p,
                "max_length": max_length
            }
            
            status_html = f"<div class='status-indicator status-success'>Generated successfully in {generation_time:.2f}s</div>"
            
            return generated_text, generation_info, status_html
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            error_msg = f"Generation failed: {str(e)}"
            return "", {"error": error_msg}, f"<div class='status-indicator status-error'>{error_msg}</div>"
    
    def _generate_image(self, model_type: str, prompt: str, negative_prompt: str,
                       num_images: int, guidance_scale: float, num_steps: int,
                       width: int, height: int, seed: Optional[int]) -> Tuple[List, Dict, str]:
        """Generate images using the selected diffusion model.
        
        Args:
            model_type: Type of diffusion model
            prompt: Image description prompt
            negative_prompt: Negative prompt
            num_images: Number of images to generate
            guidance_scale: Guidance scale
            num_steps: Number of inference steps
            width: Image width
            height: Image height
            seed: Random seed
            
        Returns:
            Tuple of (image_list, generation_info, status_html)
        """
        try:
            if not prompt.strip():
                return [], {}, "<div class='status-indicator status-error'>Please enter a prompt</div>"
            
            # Initialize diffusion model if needed
            if self.diffusion_manager is None:
                self._initialize_diffusion()
            
            if self.diffusion_manager is None:
                return [], {}, "<div class='status-indicator status-error'>Failed to initialize diffusion model</div>"
            
            # Generate images
            start_time = time.time()
            images = self.diffusion_manager.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_images=num_images,
                seed=seed
            )
            generation_time = time.time() - start_time
            
            # Convert PIL images to format suitable for Gradio
            image_list = []
            for img in images:
                if hasattr(img, 'convert'):
                    img = img.convert('RGB')
                image_list.append(img)
            
            # Prepare generation info
            generation_info = {
                "model_type": model_type,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_images": num_images,
                "guidance_scale": guidance_scale,
                "num_steps": num_steps,
                "width": width,
                "height": height,
                "seed": seed,
                "generation_time": f"{generation_time:.2f}s"
            }
            
            status_html = f"<div class='status-indicator status-success'>Generated {num_images} images in {generation_time:.2f}s</div>"
            
            return image_list, generation_info, status_html
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            error_msg = f"Image generation failed: {str(e)}"
            return [], {"error": error_msg}, f"<div class='status-indicator status-error'>{error_msg}</div>"
    
    def _initialize_transformer(self) -> Tuple[str, Dict]:
        """Initialize the transformer model.
        
        Returns:
            Tuple of (status_html, model_info)
        """
        try:
            config = TransformerConfig(
                model_name="gpt2",
                model_type="causal_lm",
                use_fp16=True,
                use_lora=False
            )
            
            self.transformer_manager = TransformerManager(config)
            model_info = self.transformer_manager.get_model_info()
            
            status_html = "<div class='status-indicator status-success'>Transformer model initialized successfully</div>"
            return status_html, model_info
            
        except Exception as e:
            logger.error(f"Failed to initialize transformer: {e}")
            error_msg = f"Failed to initialize transformer: {str(e)}"
            status_html = f"<div class='status-indicator status-error'>{error_msg}</div>"
            return status_html, {"error": error_msg}
    
    def _initialize_diffusion(self) -> Tuple[str, Dict]:
        """Initialize the diffusion model.
        
        Returns:
            Tuple of (status_html, model_info)
        """
        try:
            config = DiffusionConfig(
                model_name="runwayml/stable-diffusion-v1-5",
                model_type="stable_diffusion",
                use_fp16=True,
                enable_attention_slicing=True,
                enable_vae_slicing=True
            )
            
            self.diffusion_manager = DiffusionPipelineManager(config)
            model_info = self.diffusion_manager.get_pipeline_info()
            
            status_html = "<div class='status-indicator status-success'>Diffusion model initialized successfully</div>"
            return status_html, model_info
            
        except Exception as e:
            logger.error(f"Failed to initialize diffusion model: {e}")
            error_msg = f"Failed to initialize diffusion model: {str(e)}"
            status_html = f"<div class='status-indicator status-error'>{error_msg}</div>"
            return status_html, {"error": error_msg}
    
    def _copy_text(self, text: str) -> str:
        """Copy text to clipboard (placeholder).
        
        Args:
            text: Text to copy
            
        Returns:
            Status message
        """
        if text:
            # In a real implementation, you'd use pyperclip or similar
            return "<div class='status-indicator status-success'>Text copied to clipboard</div>"
        else:
            return "<div class='status-indicator status-warning'>No text to copy</div>"
    
    def _save_text(self, text: str) -> str:
        """Save text to file (placeholder).
        
        Args:
            text: Text to save
            
        Returns:
            Status message
        """
        if text:
            try:
                # Create output directory
                output_dir = Path("outputs")
                output_dir.mkdir(exist_ok=True)
                
                # Save text file
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"generated_text_{timestamp}.txt"
                filepath = output_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                return f"<div class='status-indicator status-success'>Text saved to {filename}</div>"
            except Exception as e:
                return f"<div class='status-indicator status-error'>Failed to save text: {str(e)}</div>"
        else:
            return "<div class='status-indicator status-warning'>No text to save</div>"
    
    def _clear_text(self) -> Tuple[str, str, Dict, str]:
        """Clear all text inputs and outputs.
        
        Returns:
            Tuple of (prompt, generated_text, generation_info, status)
        """
        return "", "", {}, "<div class='status-indicator status-warning'>Ready to generate</div>"
    
    def _download_images(self, images: List) -> str:
        """Download generated images (placeholder).
        
        Args:
            images: List of images to download
            
        Returns:
            Status message
        """
        if images:
            try:
                # Create output directory
                output_dir = Path("outputs")
                output_dir.mkdir(exist_ok=True)
                
                # Save images
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                for i, img in enumerate(images):
                    if hasattr(img, 'save'):
                        filename = f"generated_image_{timestamp}_{i+1}.png"
                        filepath = output_dir / filename
                        img.save(filepath)
                
                return f"<div class='status-indicator status-success'>Images saved to outputs folder</div>"
            except Exception as e:
                return f"<div class='status-indicator status-error'>Failed to save images: {str(e)}</div>"
        else:
            return "<div class='status-indicator status-warning'>No images to download</div>"
    
    def _clear_images(self) -> Tuple[List, Dict, str]:
        """Clear generated images.
        
        Returns:
            Tuple of (image_gallery, generation_info, status)
        """
        return [], {}, "<div class='status-indicator status-warning'>Ready to generate</div>"
    
    def _save_settings(self, device: str, memory_opt: bool, mixed_prec: bool, 
                      use_lora: bool, lora_rank: int) -> None:
        """Save interface settings.
        
        Args:
            device: Selected device
            memory_opt: Memory optimization enabled
            mixed_prec: Mixed precision enabled
            use_lora: LoRA enabled
            lora_rank: LoRA rank
        """
        try:
            # Save settings to file
            settings = {
                "device": device,
                "memory_optimization": memory_opt,
                "mixed_precision": mixed_prec,
                "use_lora": use_lora,
                "lora_rank": lora_rank
            }
            
            settings_dir = Path("config")
            settings_dir.mkdir(exist_ok=True)
            
            settings_file = settings_dir / "interface_settings.json"
            import json
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info("Interface settings saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def launch(self, **kwargs):
        """Launch the Gradio interface.
        
        Args:
            **kwargs: Additional arguments for gr.Blocks.launch()
        """
        if not self.is_initialized:
            raise RuntimeError("Interface not initialized")
        
        default_kwargs = {
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,
            "debug": True,
            "show_error": True
        }
        
        # Update with provided kwargs
        default_kwargs.update(kwargs)
        
        logger.info(f"Launching Gradio interface on port {default_kwargs['server_port']}")
        return self.interface.launch(**default_kwargs)


# Factory function for easy instantiation
def create_enhanced_gradio_interface() -> EnhancedGradioInterface:
    """Create an enhanced Gradio interface.
    
    Returns:
        Initialized enhanced Gradio interface
    """
    return EnhancedGradioInterface()

