#!/usr/bin/env python3
"""
Gradio Integration for notebooklm_ai Project
============================================

Comprehensive Gradio interfaces for diffusion models, transformers, and AI workflows.
Features production-ready UI components, async processing, real-time monitoring,
and advanced parameter controls.

Key Features:
- Multiple pipeline types (Stable Diffusion, SDXL, Img2Img, Inpaint, ControlNet)
- Real-time image generation and editing
- Advanced parameter controls and batch processing
- Training monitoring and visualization
- Model performance analysis
- Interactive text generation and analysis
- Comprehensive error handling and logging
"""

import gradio as gr
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.cuda.amp import autocast
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
import warnings
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue
import psutil
import GPUtil

# Import our core components
try:
    from diffusion_pipelines import (
        DiffusionPipelineManager, PipelineConfig, GenerationRequest
    )
    from diffusion_training_evaluation import (
        DiffusionTrainer, TrainingConfig, DiffusionEvaluator, EvaluationConfig
    )
    from gradient_optimization import (
        TrainingStabilityManager, GradientConfig
    )
    from advanced_data_loading import (
        AdvancedDataLoader, DataConfig
    )
    from transformers_integration import (
        TransformerPipeline, TransformerConfig
    )
    from llm_models import (
        LLMPipeline, LLMConfig
    )
except ImportError:
    # Mock classes for demo purposes
    class MockPipeline:
        def __init__(self, *args, **kwargs):
            pass
        async def generate(self, *args, **kwargs):
            return {"images": [np.random.rand(512, 512, 3)]}
        async def train(self, *args, **kwargs):
            return {"loss": 0.1, "accuracy": 0.95}
    
    DiffusionPipelineManager = MockPipeline
    TransformerPipeline = MockPipeline
    LLMPipeline = MockPipeline

# Suppress warnings for cleaner UI
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


@dataclass
class GradioConfig:
    """Configuration for Gradio interface."""
    # Server settings
    server_name: str = "0.0.0.0"
    server_port: int = 7860
    share: bool = False
    debug: bool = False
    
    # UI settings
    theme: str = "soft"
    title: str = "Advanced AI Models Demo"
    description: str = "Interactive demo for diffusion models, transformers, and LLMs"
    
    # Performance settings
    max_batch_size: int = 4
    enable_async: bool = True
    enable_caching: bool = True
    cache_timeout: int = 3600
    
    # Model settings
    default_diffusion_model: str = "runwayml/stable-diffusion-v1-5"
    default_transformer_model: str = "gpt2"
    default_llm_model: str = "microsoft/DialoGPT-medium"
    
    # Generation settings
    default_steps: int = 30
    default_guidance_scale: float = 7.5
    default_height: int = 512
    default_width: int = 512
    
    # Monitoring settings
    enable_monitoring: bool = True
    update_interval: float = 1.0


class GradioAIModelsApp:
    """Main Gradio application for AI models."""
    
    def __init__(self, config: GradioConfig):
        self.config = config
        self.pipeline_manager = None
        self.transformer_pipeline = None
        self.llm_pipeline = None
        
        # State management
        self.generation_history = []
        self.training_stats = {}
        self.system_metrics = {}
        
        # Threading and async
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.metrics_queue = Queue()
        self.stop_monitoring = threading.Event()
        
        # Initialize pipelines
        self._initialize_pipelines()
        
        # Start monitoring
        if self.config.enable_monitoring:
            self._start_monitoring()
    
    def _initialize_pipelines(self):
        """Initialize all AI pipelines."""
        try:
            # Initialize diffusion pipeline
            pipeline_config = PipelineConfig(
                device="cuda" if torch.cuda.is_available() else "cpu",
                enable_attention_slicing=True,
                enable_vae_slicing=True,
                enable_xformers_memory_efficient_attention=True
            )
            self.pipeline_manager = DiffusionPipelineManager(pipeline_config)
            
            # Initialize transformer pipeline
            transformer_config = TransformerConfig(
                model_name=self.config.default_transformer_model,
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            self.transformer_pipeline = TransformerPipeline(transformer_config)
            
            # Initialize LLM pipeline
            llm_config = LLMConfig(
                model_name=self.config.default_llm_model,
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            self.llm_pipeline = LLMPipeline(llm_config)
            
            logger.info("✅ All pipelines initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize pipelines: {e}")
    
    def _start_monitoring(self):
        """Start system monitoring in background thread."""
        def monitor_system():
            while not self.stop_monitoring.is_set():
                try:
                    # CPU and memory metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    # GPU metrics
                    gpu_metrics = {}
                    if torch.cuda.is_available():
                        for i in range(torch.cuda.device_count()):
                            gpu = GPUtil.getGPUs()[i]
                            gpu_metrics[f"gpu_{i}"] = {
                                "memory_used": gpu.memoryUsed,
                                "memory_total": gpu.memoryTotal,
                                "gpu_load": gpu.load * 100,
                                "temperature": gpu.temperature
                            }
                    
                    self.system_metrics = {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used_gb": memory.used / (1024**3),
                        "memory_total_gb": memory.total / (1024**3),
                        "gpu_metrics": gpu_metrics,
                        "timestamp": time.time()
                    }
                    
                    time.sleep(self.config.update_interval)
                    
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor_system, daemon=True)
        monitor_thread.start()
    
    async def generate_image(self, 
                           prompt: str,
                           negative_prompt: str,
                           num_steps: int,
                           guidance_scale: float,
                           height: int,
                           width: int,
                           seed: int = -1) -> Dict[str, Any]:
        """Generate image using diffusion model."""
        try:
            if seed == -1:
                seed = torch.randint(0, 2**32 - 1, (1,)).item()
            
            request = GenerationRequest(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_steps,
                guidance_scale=guidance_scale,
                height=height,
                width=width,
                seed=seed
            )
            
            result = await self.pipeline_manager.generate(request)
            
            # Add to history
            self.generation_history.append({
                "prompt": prompt,
                "parameters": {
                    "steps": num_steps,
                    "guidance_scale": guidance_scale,
                    "height": height,
                    "width": width,
                    "seed": seed
                },
                "result": result,
                "timestamp": time.time()
            })
            
            return {
                "images": result.get("images", []),
                "metadata": {
                    "prompt": prompt,
                    "seed": seed,
                    "generation_time": result.get("generation_time", 0),
                    "memory_used": result.get("memory_used", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return {"error": str(e)}
    
    async def generate_text(self, 
                          prompt: str,
                          max_length: int,
                          temperature: float,
                          top_p: float,
                          model_type: str = "transformer") -> Dict[str, Any]:
        """Generate text using transformer or LLM."""
        try:
            if model_type == "transformer":
                result = await self.transformer_pipeline.generate(
                    prompt=prompt,
                    max_length=max_length,
                    temperature=temperature,
                    top_p=top_p
                )
            else:
                result = await self.llm_pipeline.generate(
                    prompt=prompt,
                    max_length=max_length,
                    temperature=temperature,
                    top_p=top_p
                )
            
            return {
                "generated_text": result.get("generated_text", ""),
                "metadata": {
                    "model_type": model_type,
                    "prompt": prompt,
                    "generation_time": result.get("generation_time", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            return {"error": str(e)}
    
    async def batch_generate_images(self, 
                                  prompts: List[str],
                                  **kwargs) -> List[Dict[str, Any]]:
        """Generate multiple images in batch."""
        try:
            tasks = []
            for prompt in prompts:
                task = self.generate_image(prompt=prompt, **kwargs)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out errors
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch generation error for prompt {i}: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Batch generation error: {e}")
            return [{"error": str(e)}]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return self.system_metrics.copy()
    
    def get_generation_history(self) -> List[Dict[str, Any]]:
        """Get generation history."""
        return self.generation_history.copy()
    
    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface."""
        
        with gr.Blocks(
            title=self.config.title,
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
                margin: 0 auto !important;
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
            }
            """
        ) as interface:
            
            # Header
            gr.Markdown(f"# {self.config.title}")
            gr.Markdown(self.config.description)
            
            # System Metrics
            if self.config.enable_monitoring:
                with gr.Row():
                    with gr.Column(scale=1):
                        cpu_metric = gr.Number(label="CPU %", precision=1)
                        memory_metric = gr.Number(label="Memory %", precision=1)
                    with gr.Column(scale=1):
                        gpu_memory_metric = gr.Number(label="GPU Memory %", precision=1)
                        gpu_temp_metric = gr.Number(label="GPU Temp °C", precision=1)
                
                # Update metrics
                def update_metrics():
                    metrics = self.get_system_metrics()
                    cpu = metrics.get("cpu_percent", 0)
                    memory = metrics.get("memory_percent", 0)
                    
                    gpu_memory = 0
                    gpu_temp = 0
                    if metrics.get("gpu_metrics"):
                        for gpu_data in metrics["gpu_metrics"].values():
                            gpu_memory = max(gpu_memory, 
                                           (gpu_data["memory_used"] / gpu_data["memory_total"]) * 100)
                            gpu_temp = max(gpu_temp, gpu_data["temperature"])
                    
                    return cpu, memory, gpu_memory, gpu_temp
                
                gr.on(triggers=[gr.update()], fn=update_metrics, 
                     outputs=[cpu_metric, memory_metric, gpu_memory_metric, gpu_temp_metric],
                     every=2.0)
            
            # Main Tabs
            with gr.Tabs():
                
                # Tab 1: Image Generation
                with gr.TabItem("🖼️ Image Generation"):
                    self._create_image_generation_tab()
                
                # Tab 2: Text Generation
                with gr.TabItem("📝 Text Generation"):
                    self._create_text_generation_tab()
                
                # Tab 3: Batch Processing
                with gr.TabItem("⚡ Batch Processing"):
                    self._create_batch_processing_tab()
                
                # Tab 4: Training & Evaluation
                with gr.TabItem("🎯 Training & Evaluation"):
                    self._create_training_tab()
                
                # Tab 5: Model Analysis
                with gr.TabItem("📊 Model Analysis"):
                    self._create_analysis_tab()
        
        return interface
    
    def _create_image_generation_tab(self):
        """Create image generation tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Generation Parameters")
                
                prompt = gr.Textbox(
                    value="A beautiful landscape with mountains and lake, digital art",
                    label="Prompt",
                    lines=3
                )
                negative_prompt = gr.Textbox(
                    value="blurry, low quality, distorted",
                    label="Negative Prompt",
                    lines=2
                )
                
                with gr.Row():
                    num_steps = gr.Slider(1, 100, self.config.default_steps, 
                                        label="Steps", step=1)
                    guidance_scale = gr.Slider(1.0, 20.0, self.config.default_guidance_scale, 
                                             label="Guidance Scale", step=0.1)
                
                with gr.Row():
                    height = gr.Slider(256, 1024, self.config.default_height, 
                                     label="Height", step=64)
                    width = gr.Slider(256, 1024, self.config.default_width, 
                                    label="Width", step=64)
                
                seed = gr.Number(value=-1, label="Seed (-1 for random)")
                
                generate_btn = gr.Button("Generate Image", variant="primary")
                clear_btn = gr.Button("Clear", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### Generated Image")
                output_image = gr.Image(label="Generated Image")
                output_metadata = gr.JSON(label="Generation Metadata")
        
        # Event handlers
        def generate_image_sync(*args):
            return asyncio.run(self.generate_image(*args))
        
        generate_btn.click(
            fn=generate_image_sync,
            inputs=[prompt, negative_prompt, num_steps, guidance_scale, height, width, seed],
            outputs=[output_image, output_metadata]
        )
        
        clear_btn.click(
            fn=lambda: (None, None),
            outputs=[output_image, output_metadata]
        )
    
    def _create_text_generation_tab(self):
        """Create text generation tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Text Generation Parameters")
                
                text_prompt = gr.Textbox(
                    value="The future of artificial intelligence",
                    label="Prompt",
                    lines=3
                )
                
                model_type = gr.Dropdown(
                    choices=["transformer", "llm"],
                    value="transformer",
                    label="Model Type"
                )
                
                with gr.Row():
                    max_length = gr.Slider(10, 500, 100, label="Max Length", step=1)
                    temperature = gr.Slider(0.1, 2.0, 0.7, label="Temperature", step=0.1)
                
                top_p = gr.Slider(0.1, 1.0, 0.9, label="Top-p", step=0.1)
                
                generate_text_btn = gr.Button("Generate Text", variant="primary")
                clear_text_btn = gr.Button("Clear", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### Generated Text")
                output_text = gr.Textbox(label="Generated Text", lines=10)
                text_metadata = gr.JSON(label="Generation Metadata")
        
        # Event handlers
        def generate_text_sync(*args):
            return asyncio.run(self.generate_text(*args))
        
        generate_text_btn.click(
            fn=generate_text_sync,
            inputs=[text_prompt, max_length, temperature, top_p, model_type],
            outputs=[output_text, text_metadata]
        )
        
        clear_text_btn.click(
            fn=lambda: ("", None),
            outputs=[output_text, text_metadata]
        )
    
    def _create_batch_processing_tab(self):
        """Create batch processing tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Batch Generation")
                
                batch_prompts = gr.Textbox(
                    value="A beautiful sunset\nA futuristic city\nA peaceful forest",
                    label="Prompts (one per line)",
                    lines=5
                )
                
                batch_steps = gr.Slider(1, 100, 30, label="Steps", step=1)
                batch_guidance = gr.Slider(1.0, 20.0, 7.5, label="Guidance Scale", step=0.1)
                
                batch_btn = gr.Button("Generate Batch", variant="primary")
                clear_batch_btn = gr.Button("Clear", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### Batch Results")
                batch_gallery = gr.Gallery(label="Generated Images")
                batch_metadata = gr.JSON(label="Batch Metadata")
        
        # Event handlers
        def process_batch(prompts, steps, guidance):
            prompt_list = [p.strip() for p in prompts.split('\n') if p.strip()]
            results = asyncio.run(self.batch_generate_images(
                prompts=prompt_list,
                num_steps=steps,
                guidance_scale=guidance,
                negative_prompt="blurry, low quality",
                height=512,
                width=512
            ))
            
            images = []
            metadata = []
            for result in results:
                if "images" in result:
                    images.extend(result["images"])
                    metadata.append(result.get("metadata", {}))
            
            return images, metadata
        
        batch_btn.click(
            fn=process_batch,
            inputs=[batch_prompts, batch_steps, batch_guidance],
            outputs=[batch_gallery, batch_metadata]
        )
        
        clear_batch_btn.click(
            fn=lambda: ([], []),
            outputs=[batch_gallery, batch_metadata]
        )
    
    def _create_training_tab(self):
        """Create training and evaluation tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Training Configuration")
                
                training_data = gr.File(label="Training Data")
                epochs = gr.Slider(1, 100, 10, label="Epochs", step=1)
                learning_rate = gr.Slider(1e-6, 1e-2, 1e-4, label="Learning Rate", step=1e-6)
                
                start_training_btn = gr.Button("Start Training", variant="primary")
                stop_training_btn = gr.Button("Stop Training", variant="secondary")
            
            with gr.Column(scale=1):
                gr.Markdown("### Training Progress")
                training_progress = gr.Plot(label="Training Loss")
                training_metrics = gr.JSON(label="Current Metrics")
        
        # Placeholder for training functionality
        def start_training(*args):
            return "Training started (placeholder)"
        
        start_training_btn.click(
            fn=start_training,
            inputs=[training_data, epochs, learning_rate],
            outputs=[training_metrics]
        )
    
    def _create_analysis_tab(self):
        """Create model analysis tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Model Analysis")
                
                analysis_type = gr.Dropdown(
                    choices=["performance", "memory", "accuracy", "latency"],
                    value="performance",
                    label="Analysis Type"
                )
                
                run_analysis_btn = gr.Button("Run Analysis", variant="primary")
            
            with gr.Column(scale=1):
                gr.Markdown("### Analysis Results")
                analysis_plot = gr.Plot(label="Analysis Results")
                analysis_data = gr.JSON(label="Analysis Data")
        
        # Placeholder for analysis functionality
        def run_analysis(analysis_type):
            return "Analysis completed (placeholder)"
        
        run_analysis_btn.click(
            fn=run_analysis,
            inputs=[analysis_type],
            outputs=[analysis_data]
        )


def create_gradio_app(config: Optional[GradioConfig] = None) -> GradioAIModelsApp:
    """Create and configure Gradio app."""
    if config is None:
        config = GradioConfig()
    
    app = GradioAIModelsApp(config)
    return app


def launch_gradio_app(config: Optional[GradioConfig] = None, **kwargs):
    """Launch the Gradio app."""
    app = create_gradio_app(config)
    interface = app.create_interface()
    
    # Launch with custom parameters
    launch_params = {
        "server_name": app.config.server_name,
        "server_port": app.config.server_port,
        "share": app.config.share,
        "debug": app.config.debug,
        **kwargs
    }
    
    interface.launch(**launch_params)


if __name__ == "__main__":
    # Example usage
    config = GradioConfig(
        server_port=7860,
        share=True,
        debug=True
    )
    
    launch_gradio_app(config) 