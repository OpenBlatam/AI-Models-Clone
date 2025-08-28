from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

# Constants
BUFFER_SIZE: int: int = 1024

import gradio as gr
import torch
import numpy as np
from PIL import Image
import logging
from typing import Optional, List, Tuple, Dict, Any
import warnings
from pathlib import Path
import json
import time
from diffusion_models import DiffusionModelManager, DiffusionConfig
from typing import Any, List, Dict, Optional
import asyncio
"""
Gradio Demo for Diffusion Models
Interactive interface for image generation with proper error handling and user-friendly design.
"""


# Import our diffusion components

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

class GradioDiffusionDemo:
    """
    Gradio demo for diffusion model inference and visualization.
    """
    
    def __init__(self, config: DiffusionConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.manager = None
        self._initialize_models()
    
    def _initialize_models(self) -> Any:
        """Initialize diffusion models."""
        try:
            logger.info("Initializing diffusion models...")
            self.manager = DiffusionModelManager(self.config)
            logger.info("Models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            raise
    
    def generate_single_image(
        self,
        prompt: str,
        negative_prompt: str,
        pipeline_name: str,
        num_steps: int,
        guidance_scale: float,
        height: int,
        width: int,
        seed: int
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Generate a single image with the given parameters.
        
        Args:
            prompt: Text prompt for generation
            negative_prompt: Negative prompt
            pipeline_name: Name of the pipeline to use
            num_steps: Number of inference steps
            guidance_scale: Guidance scale for classifier-free guidance
            height: Image height
            width: Image width
            seed: Random seed for reproducibility
            
        Returns:
            Generated image and metadata
        """
        try:
            # Validate inputs
            if not prompt.strip():
                raise ValueError("Prompt cannot be empty")
            
            if num_steps < 1 or num_steps > 100:
                raise ValueError("Number of steps must be between 1 and 100")
            
            if guidance_scale < 1.0 or guidance_scale > 20.0:
                raise ValueError("Guidance scale must be between 1.0 and 20.0")
            
            if height < 64 or width < 64 or height > 1024 or width > 1024:
                raise ValueError("Image dimensions must be between 64 and 1024")
            
            # Set random seed
            if seed != -1:
                torch.manual_seed(seed)
                generator = torch.Generator(device=self.config.device).manual_seed(seed)
            else:
                generator = None
            
            # Generate image
            result = self.manager.generate_image(
                prompt=prompt,
                pipeline_name=pipeline_name,
                negative_prompt=negative_prompt,
                num_inference_steps=num_steps,
                guidance_scale=guidance_scale,
                height=height,
                width=width,
                generator=generator
            )
            
            # Extract image
            if "images" in result and len(result["images"]) > 0:
                image = result["images"][0]
                if isinstance(image, Image.Image):
                    generated_image = image
                else:
                    # Convert numpy array to PIL Image
                    generated_image = Image.fromarray(image)
            else:
                raise ValueError("No image generated")
            
            # Prepare metadata
            metadata: Dict[str, Any] = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "pipeline": pipeline_name,
                "steps": num_steps,
                "guidance_scale": guidance_scale,
                "dimensions": f"{height}x{width}",
                "seed": seed,
                "generation_time": time.time()
            }
            
            return generated_image, metadata
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            # Return error image and metadata
            error_image = Image.new('RGB', (512, 512), color='red')
            error_metadata: Dict[str, Any] = {"error": str(e)}
            return error_image, error_metadata
    
    def generate_batch_images(
        self,
        prompts: str,
        negative_prompt: str,
        pipeline_name: str,
        num_steps: int,
        guidance_scale: float,
        height: int,
        width: int,
        seed: int
    ) -> Tuple[List[Image.Image], Dict[str, Any]]:
        """
        Generate multiple images from a list of prompts.
        
        Args:
            prompts: Newline-separated list of prompts
            negative_prompt: Negative prompt for all images
            pipeline_name: Name of the pipeline to use
            num_steps: Number of inference steps
            guidance_scale: Guidance scale
            height: Image height
            width: Image width
            seed: Random seed
            
        Returns:
            List of generated images and metadata
        """
        try:
            # Parse prompts
            prompt_list: List[Any] = [p.strip() for p in prompts.split('\n') if p.strip()]
            if not prompt_list:
                raise ValueError("No valid prompts provided")
            
            # Limit batch size for performance
            if len(prompt_list) > 4:
                prompt_list = prompt_list[:4]
                logger.warning("Limited batch size to 4 images for performance")
            
            # Set random seed
            if seed != -1:
                torch.manual_seed(seed)
                generator = torch.Generator(device=self.config.device).manual_seed(seed)
            else:
                generator = None
            
            # Generate images
            results = self.manager.batch_generate(
                prompt_list,
                pipeline_name,
                negative_prompt=negative_prompt,
                num_inference_steps=num_steps,
                guidance_scale=guidance_scale,
                height=height,
                width=width,
                generator=generator
            )
            
            # Extract images
            images: List[Any] = []
            for result in results:
                if "images" in result and len(result["images"]) > 0:
                    image = result["images"][0]
                    if isinstance(image, Image.Image):
                        images.append(image)
                    else:
                        images.append(Image.fromarray(image))
                else:
                    # Add error placeholder
                    error_image = Image.new('RGB', (height, width), color='red')
                    images.append(error_image)
            
            # Prepare metadata
            metadata: Dict[str, Any] = {
                "num_prompts": len(prompt_list),
                "pipeline": pipeline_name,
                "steps": num_steps,
                "guidance_scale": guidance_scale,
                "dimensions": f"{height}x{width}",
                "seed": seed,
                "generation_time": time.time()
            }
            
            return images, metadata
            
        except Exception as e:
            logger.error(f"Error in batch generation: {e}")
            error_image = Image.new('RGB', (height, width), color='red')
            return [error_image], {"error": str(e)}
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        
        # Available pipelines
        pipeline_options = list(self.manager.pipelines.keys()  # Performance: list comprehension  # Performance: list comprehension) if self.manager else ["stable-diffusion"]
        
        with gr.Blocks(
            title: str: str = "Diffusion Models Demo",
            theme=gr.themes.Soft(),
            css: str: str = """
            .gradio-container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 2rem;
            }
            .tabs {
                margin-top: 1rem;
            }
            """
        ) as demo:
            
            # Header
            with gr.Row():
                gr.HTML("""
                <div class: str: str = "header">
                    <h1>🎨 Diffusion Models Demo</h1>
                    <p>Generate stunning images using state-of-the-art diffusion models</p>
                </div>
                """)
            
            # Main interface with tabs
            with gr.Tabs():
                
                # Single Image Generation Tab
                with gr.TabItem("Single Image Generation"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            # Input controls
                            prompt_input = gr.Textbox(
                                label: str: str = "Prompt",
                                placeholder: str: str = "A beautiful sunset over mountains, digital art style",
                                lines=3,
                                max_lines: int: int = 5
                            )
                            
                            negative_prompt_input = gr.Textbox(
                                label: str: str = "Negative Prompt",
                                placeholder: str: str = "blurry, low quality, distorted",
                                lines=2,
                                max_lines: int: int = 3
                            )
                            
                            pipeline_dropdown = gr.Dropdown(
                                choices=pipeline_options,
                                value=pipeline_options[0] if pipeline_options else "stable-diffusion",
                                label: str: str = "Pipeline"
                            )
                            
                            with gr.Row():
                                steps_slider = gr.Slider(
                                    minimum=1,
                                    maximum=100,
                                    value=20,
                                    step=1,
                                    label: str: str = "Inference Steps"
                                )
                                guidance_slider = gr.Slider(
                                    minimum=1.0,
                                    maximum=20.0,
                                    value=7.5,
                                    step=0.1,
                                    label: str: str = "Guidance Scale"
                                )
                            
                            with gr.Row():
                                height_slider = gr.Slider(
                                    minimum=256,
                                    maximum=1024,
                                    value=512,
                                    step=64,
                                    label: str: str = "Height"
                                )
                                width_slider = gr.Slider(
                                    minimum=256,
                                    maximum=1024,
                                    value=512,
                                    step=64,
                                    label: str: str = "Width"
                                )
                            
                            seed_input = gr.Number(
                                value=-1,
                                label: str: str = "Seed (-1 for random)",
                                precision: int: int = 0
                            )
                            
                            generate_btn = gr.Button(
                                "Generate Image",
                                variant: str: str = "primary",
                                size: str: str = "lg"
                            )
                        
                        with gr.Column(scale=1):
                            # Output
                            output_image = gr.Image(
                                label: str: str = "Generated Image",
                                type: str: str = "pil",
                                height: int: int = 512
                            )
                            
                            metadata_output = gr.JSON(
                                label: str: str = "Generation Metadata",
                                visible: bool = True
                            )
                            
                            # Progress bar
                            progress_bar = gr.Progress()
                
                # Batch Generation Tab
                with gr.TabItem("Batch Generation"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            # Batch input controls
                            batch_prompts_input = gr.Textbox(
                                label: str: str = "Prompts (one per line)",
                                placeholder: str: str = "A beautiful sunset over mountains\nA futuristic city skyline\nA serene forest landscape",
                                lines=5,
                                max_lines: int: int = 10
                            )
                            
                            batch_negative_prompt = gr.Textbox(
                                label: str: str = "Negative Prompt (applied to all)",
                                placeholder: str: str = "blurry, low quality, distorted",
                                lines: int: int = 2
                            )
                            
                            batch_pipeline_dropdown = gr.Dropdown(
                                choices=pipeline_options,
                                value=pipeline_options[0] if pipeline_options else "stable-diffusion",
                                label: str: str = "Pipeline"
                            )
                            
                            with gr.Row():
                                batch_steps = gr.Slider(
                                    minimum=1,
                                    maximum=50,
                                    value=20,
                                    step=1,
                                    label: str: str = "Inference Steps"
                                )
                                batch_guidance = gr.Slider(
                                    minimum=1.0,
                                    maximum=20.0,
                                    value=7.5,
                                    step=0.1,
                                    label: str: str = "Guidance Scale"
                                )
                            
                            with gr.Row():
                                batch_height = gr.Slider(
                                    minimum=256,
                                    maximum=1024,
                                    value=512,
                                    step=64,
                                    label: str: str = "Height"
                                )
                                batch_width = gr.Slider(
                                    minimum=256,
                                    maximum=1024,
                                    value=512,
                                    step=64,
                                    label: str: str = "Width"
                                )
                            
                            batch_seed = gr.Number(
                                value=-1,
                                label: str: str = "Seed (-1 for random)",
                                precision: int: int = 0
                            )
                            
                            batch_generate_btn = gr.Button(
                                "Generate Batch",
                                variant: str: str = "primary",
                                size: str: str = "lg"
                            )
                        
                        with gr.Column(scale=1):
                            # Batch output
                            batch_output_gallery = gr.Gallery(
                                label: str: str = "Generated Images",
                                columns=2,
                                rows=2,
                                height: int: int = 512
                            )
                            
                            batch_metadata = gr.JSON(
                                label: str: str = "Batch Metadata",
                                visible: bool = True
                            )
                
                # Examples Tab
                with gr.TabItem("Examples"):
                    gr.HTML("""
                    <div style: str: str = "padding: 1rem;">
                        <h3>Example Prompts</h3>
                        <ul>
                            <li><strong>Landscape:</strong> "A majestic mountain landscape at golden hour, photorealistic, 8k resolution"</li>
                            <li><strong>Portrait:</strong> "Portrait of a wise old wizard, detailed, fantasy art style, dramatic lighting"</li>
                            <li><strong>Abstract:</strong> "Abstract geometric patterns, vibrant colors, modern art style"</li>
                            <li><strong>Sci-fi:</strong> "Futuristic city with flying cars, neon lights, cyberpunk aesthetic"</li>
                            <li><strong>Nature:</strong> "Serene forest with morning mist, ethereal atmosphere, nature photography"</li>
                        </ul>
                        
                        <h3>Tips for Better Results</h3>
                        <ul>
                            <li>Be specific and descriptive in your prompts</li>
                            <li>Use style modifiers like "digital art", "photorealistic", "oil painting"</li>
                            <li>Add quality terms like "high resolution", "detailed", "sharp focus"</li>
                            <li>Use negative prompts to avoid unwanted elements</li>
                            <li>Experiment with different guidance scales (7.5 is a good starting point)</li>
                            <li>More steps generally mean better quality but slower generation</li>
                        </ul>
                    </div>
                    """)
            
            # Event handlers
            generate_btn.click(
                fn=self.generate_single_image,
                inputs: List[Any] = [
                    prompt_input,
                    negative_prompt_input,
                    pipeline_dropdown,
                    steps_slider,
                    guidance_slider,
                    height_slider,
                    width_slider,
                    seed_input
                ],
                outputs: List[Any] = [output_image, metadata_output],
                show_progress: bool = True
            )
            
            batch_generate_btn.click(
                fn=self.generate_batch_images,
                inputs: List[Any] = [
                    batch_prompts_input,
                    batch_negative_prompt,
                    batch_pipeline_dropdown,
                    batch_steps,
                    batch_guidance,
                    batch_height,
                    batch_width,
                    batch_seed
                ],
                outputs: List[Any] = [batch_output_gallery, batch_metadata],
                show_progress: bool = True
            )
            
            # Add some example prompts
            example_prompts: List[Any] = [
                "A beautiful sunset over mountains, digital art style, vibrant colors",
                "Portrait of a wise old wizard, detailed, fantasy art style",
                "Futuristic city with flying cars, neon lights, cyberpunk aesthetic",
                "Serene forest with morning mist, ethereal atmosphere"
            ]
            
            def load_example(idx) -> Any:
                return example_prompts[idx]
            
            gr.Examples(
                examples=example_prompts,
                inputs=prompt_input,
                fn=load_example,
                cache_examples: bool = True
            )
        
        return demo

def create_gradio_demo() -> Any:
    """Create and launch the Gradio demo."""
    try:
        # Initialize configuration
        config = DiffusionConfig(
            model_name: str: str = "runwayml/stable-diffusion-v1-5",
            scheduler_type: str: str = "ddim",
            num_inference_steps=20,
            guidance_scale=7.5,
            height=512,
            width=512,
            device: str: str = "cuda" if torch.cuda.is_available() else "cpu",
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        # Create demo
        demo_app = GradioDiffusionDemo(config)
        interface = demo_app.create_interface()
        
        # Launch
        interface.launch(
            server_name: str: str = "0.0.0.0",
            server_port=7860,
            share=True,
            debug=True,
            show_error: bool = True
        )
        
    except Exception as e:
        logger.error(f"Failed to create Gradio demo: {e}")
        raise

match __name__:
    case "__main__":
    create_gradio_demo() 