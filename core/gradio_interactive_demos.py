"""
Interactive Gradio Demos for Diffusion Models
============================================

This module provides interactive demos for:
- Real-time model inference
- Live parameter adjustment
- Interactive visualizations
- Model comparison tools
- Creative exploration interface
"""

import gradio as gr
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Optional, Tuple
import threading
import queue
from pathlib import Path

# Import your core systems
from .diffusion_models_system import (
    DiffusionModelManager, DiffusionModelConfig, 
    GenerationConfig, PipelineType
)
from .diffusion_processes_core import DiffusionProcesses
from .evaluation_metrics_system import BaseMetric

class InteractiveDiffusionDemos:
    """Interactive demos for diffusion models."""
    
    def __init__(self):
        self.model_manager = None
        self.current_pipeline = None
        self.generation_queue = queue.Queue()
        self.is_processing = False
        self.demo_history = []
        
        # Demo configurations
        self.demo_configs = {
            "creative_exploration": {
                "num_variations": 4,
                "parameter_ranges": {
                    "guidance_scale": (1.0, 20.0),
                    "num_inference_steps": (10, 100),
                    "strength": (0.1, 1.0)
                }
            },
            "style_transfer": {
                "style_presets": [
                    "photorealistic", "artistic", "cartoon", "sketch",
                    "oil_painting", "watercolor", "digital_art"
                ]
            }
        }
    
    def create_main_demo_interface(self) -> gr.Blocks:
        """Create the main interactive demo interface."""
        
        with gr.Blocks(
            title="🎨 Interactive Diffusion Studio",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
            }
            .demo-header {
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                margin-bottom: 20px;
            }
            .demo-card {
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                background: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            """
        ) as demo:
            
            # Header
            gr.HTML("""
            <div class="demo-header">
                <h1>🎨 Interactive Diffusion Studio</h1>
                <p>Explore, create, and visualize with state-of-the-art diffusion models</p>
            </div>
            """)
            
            with gr.Tabs():
                
                # Real-time Inference Tab
                with gr.Tab("⚡ Real-time Inference", id="realtime"):
                    self._create_realtime_inference_tab()
                
                # Interactive Parameter Exploration Tab
                with gr.Tab("🔬 Parameter Explorer", id="explorer"):
                    self._create_parameter_explorer_tab()
                
                # Creative Exploration Tab
                with gr.Tab("🎭 Creative Explorer", id="creative"):
                    self._create_creative_exploration_tab()
                
                # Style Transfer Tab
                with gr.Tab("🎨 Style Transfer", id="style"):
                    self._create_style_transfer_tab()
                
                # Model Comparison Tab
                with gr.Tab("⚖️ Model Comparison", id="comparison"):
                    self._create_model_comparison_tab()
                
                # Visualization Dashboard Tab
                with gr.Tab("📊 Visualization Dashboard", id="dashboard"):
                    self._create_visualization_dashboard_tab()
            
            # Footer
            gr.HTML("""
            <div style="text-align: center; padding: 20px; color: #666;">
                <p>Built with ❤️ using Gradio and Diffusion Models</p>
            </div>
            """)
        
        return demo
    
    def _create_realtime_inference_tab(self):
        """Create real-time inference tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🚀 Real-time Generation")
                
                # Model selection
                model_dropdown = gr.Dropdown(
                    choices=[
                        "stabilityai/stable-diffusion-2-1",
                        "stabilityai/stable-diffusion-xl-base-1.0",
                        "runwayml/stable-diffusion-v1-5"
                    ],
                    label="Select Model",
                    value="stabilityai/stable-diffusion-2-1"
                )
                
                # Pipeline selection
                pipeline_dropdown = gr.Dropdown(
                    choices=["text_to_image", "image_to_image", "inpainting"],
                    label="Pipeline Type",
                    value="text_to_image"
                )
                
                # Initialize button
                init_button = gr.Button("🏗️ Initialize Model", variant="primary")
                init_status = gr.Textbox(label="Model Status", interactive=False)
                
                # Generation parameters
                prompt_input = gr.Textbox(
                    label="🎯 Prompt",
                    placeholder="A beautiful landscape with mountains and trees...",
                    lines=3
                )
                
                negative_prompt_input = gr.Textbox(
                    label="❌ Negative Prompt",
                    placeholder="blurry, low quality, distorted...",
                    lines=2
                )
                
                with gr.Row():
                    steps_slider = gr.Slider(10, 100, 50, label="Inference Steps", step=1)
                    guidance_slider = gr.Slider(1.0, 20.0, 7.5, label="Guidance Scale", step=0.1)
                
                with gr.Row():
                    width_slider = gr.Slider(256, 1024, 512, step=64, label="Width")
                    height_slider = gr.Slider(256, 1024, 512, step=64, label="Height")
                
                seed_input = gr.Number(label="🎲 Seed (-1 for random)", value=-1)
                
                # Generation button
                generate_button = gr.Button("🎨 Generate Now!", variant="primary", size="lg")
                
                # Progress tracking
                progress_bar = gr.Slider(0, 100, 0, label="Generation Progress", interactive=False)
                status_output = gr.Textbox(label="Status", interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("### 🖼️ Generated Results")
                
                # Output image
                output_image = gr.Image(
                    label="Generated Image",
                    height=400,
                    show_label=True
                )
                
                # Generation info
                generation_info = gr.JSON(label="Generation Information")
                
                # Action buttons
                with gr.Row():
                    save_button = gr.Button("💾 Save Image")
                    share_button = gr.Button("📤 Share")
                    regenerate_button = gr.Button("🔄 Regenerate")
                
                # History gallery
                gr.Markdown("### 📚 Generation History")
                history_gallery = gr.Gallery(
                    label="Recent Generations",
                    show_label=True,
                    elem_id="history_gallery",
                    height=200
                )
        
        # Event handlers
        init_button.click(
            fn=self._initialize_model,
            inputs=[model_dropdown, pipeline_dropdown],
            outputs=init_status
        )
        
        generate_button.click(
            fn=self._generate_image_realtime,
            inputs=[
                prompt_input, negative_prompt_input, steps_slider,
                guidance_slider, width_slider, height_slider, seed_input
            ],
            outputs=[output_image, generation_info, progress_bar, status_output]
        )
        
        save_button.click(
            fn=self._save_generated_image,
            inputs=[output_image],
            outputs=[status_output]
        )
        
        regenerate_button.click(
            fn=self._regenerate_image,
            inputs=[
                prompt_input, negative_prompt_input, steps_slider,
                guidance_slider, width_slider, height_slider, seed_input
            ],
            outputs=[output_image, generation_info, progress_bar, status_output]
        )
    
    def _create_parameter_explorer_tab(self):
        """Create interactive parameter exploration tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🔬 Parameter Exploration")
                
                # Base prompt
                base_prompt = gr.Textbox(
                    label="Base Prompt",
                    placeholder="A beautiful landscape...",
                    lines=2
                )
                
                # Parameter to explore
                param_dropdown = gr.Dropdown(
                    choices=["guidance_scale", "num_inference_steps", "strength"],
                    label="Parameter to Explore",
                    value="guidance_scale"
                )
                
                # Parameter range
                with gr.Row():
                    param_min = gr.Number(label="Min Value", value=1.0)
                    param_max = gr.Number(label="Max Value", value=20.0)
                    param_steps = gr.Number(label="Number of Steps", value=5)
                
                # Fixed parameters
                fixed_steps = gr.Slider(10, 100, 50, label="Fixed Inference Steps")
                fixed_width = gr.Slider(256, 1024, 512, step=64, label="Fixed Width")
                fixed_height = gr.Slider(256, 1024, 512, step=64, label="Fixed Height")
                
                # Explore button
                explore_button = gr.Button("🔬 Explore Parameters", variant="primary")
                
                # Progress
                explore_progress = gr.Slider(0, 100, 0, label="Exploration Progress", interactive=False)
            
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Parameter Analysis")
                
                # Results gallery
                exploration_gallery = gr.Gallery(
                    label="Parameter Exploration Results",
                    show_label=True,
                    elem_id="exploration_gallery",
                    height=300
                )
                
                # Parameter vs quality plot
                quality_plot = gr.Plot(label="Parameter vs Quality Analysis")
                
                # Analysis results
                analysis_results = gr.JSON(label="Analysis Results")
        
        # Event handler
        explore_button.click(
            fn=self._explore_parameters_interactive,
            inputs=[
                base_prompt, param_dropdown, param_min, param_max, param_steps,
                fixed_steps, fixed_width, fixed_height
            ],
            outputs=[exploration_gallery, quality_plot, analysis_results, explore_progress]
        )
    
    def _create_creative_exploration_tab(self):
        """Create creative exploration tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎭 Creative Exploration")
                
                # Creative prompt
                creative_prompt = gr.Textbox(
                    label="Creative Prompt",
                    placeholder="A surreal dreamscape where...",
                    lines=3
                )
                
                # Style modifiers
                style_modifiers = gr.CheckboxGroup(
                    choices=[
                        "cinematic", "artistic", "photorealistic", "abstract",
                        "vintage", "futuristic", "fantasy", "sci-fi"
                    ],
                    label="Style Modifiers",
                    value=["artistic"]
                )
                
                # Mood selection
                mood_dropdown = gr.Dropdown(
                    choices=["peaceful", "energetic", "mysterious", "joyful", "melancholic"],
                    label="Mood",
                    value="peaceful"
                )
                
                # Color palette
                color_palette = gr.Dropdown(
                    choices=["natural", "vibrant", "monochrome", "pastel", "dark"],
                    label="Color Palette",
                    value="natural"
                )
                
                # Generate variations button
                generate_variations_button = gr.Button("🎨 Generate Variations", variant="primary")
                
                # Progress
                variations_progress = gr.Slider(0, 100, 0, label="Variations Progress", interactive=False)
            
            with gr.Column(scale=2):
                gr.Markdown("### 🎨 Creative Variations")
                
                # Variations gallery
                variations_gallery = gr.Gallery(
                    label="Creative Variations",
                    show_label=True,
                    elem_id="variations_gallery",
                    height=400
                )
                
                # Variation controls
                with gr.Row():
                    select_variation_button = gr.Button("⭐ Select Variation")
                    refine_variation_button = gr.Button("🔧 Refine Selected")
                
                # Selected variation info
                variation_info = gr.JSON(label="Selected Variation Info")
        
        # Event handlers
        generate_variations_button.click(
            fn=self._generate_creative_variations,
            inputs=[creative_prompt, style_modifiers, mood_dropdown, color_palette],
            outputs=[variations_gallery, variations_progress]
        )
    
    def _create_style_transfer_tab(self):
        """Create style transfer tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎨 Style Transfer")
                
                # Input image
                input_image = gr.Image(label="Input Image", height=200)
                
                # Style selection
                style_preset = gr.Dropdown(
                    choices=self.demo_configs["style_transfer"]["style_presets"],
                    label="Style Preset",
                    value="artistic"
                )
                
                # Custom style prompt
                custom_style = gr.Textbox(
                    label="Custom Style Description",
                    placeholder="in the style of Van Gogh...",
                    lines=2
                )
                
                # Style strength
                style_strength = gr.Slider(0.1, 1.0, 0.7, label="Style Strength")
                
                # Transfer button
                transfer_button = gr.Button("🎨 Apply Style", variant="primary")
                
                # Progress
                transfer_progress = gr.Slider(0, 100, 0, label="Style Transfer Progress", interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("### 🖼️ Stylized Results")
                
                # Output image
                styled_image = gr.Image(label="Stylized Image", height=400)
                
                # Style info
                style_info = gr.JSON(label="Style Information")
                
                # Action buttons
                with gr.Row():
                    save_styled_button = gr.Button("💾 Save Stylized")
                    reset_button = gr.Button("🔄 Reset")
        
        # Event handler
        transfer_button.click(
            fn=self._apply_style_transfer,
            inputs=[input_image, style_preset, custom_style, style_strength],
            outputs=[styled_image, style_info, transfer_progress]
        )
    
    def _create_model_comparison_tab(self):
        """Create model comparison tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚖️ Model Comparison")
                
                # Test prompt
                test_prompt = gr.Textbox(
                    label="Test Prompt",
                    placeholder="A beautiful landscape...",
                    lines=2
                )
                
                # Model selection
                model1_dropdown = gr.Dropdown(
                    choices=[
                        "stabilityai/stable-diffusion-2-1",
                        "stabilityai/stable-diffusion-xl-base-1.0",
                        "runwayml/stable-diffusion-v1-5"
                    ],
                    label="Model 1",
                    value="stabilityai/stable-diffusion-2-1"
                )
                
                model2_dropdown = gr.Dropdown(
                    choices=[
                        "stabilityai/stable-diffusion-2-1",
                        "stabilityai/stable-diffusion-xl-base-1.0",
                        "runwayml/stable-diffusion-v1-5"
                    ],
                    label="Model 2",
                    value="stabilityai/stable-diffusion-xl-base-1.0"
                )
                
                # Comparison parameters
                with gr.Row():
                    comp_steps = gr.Slider(10, 100, 50, label="Inference Steps")
                    comp_guidance = gr.Slider(1.0, 20.0, 7.5, label="Guidance Scale")
                
                # Compare button
                compare_button = gr.Button("⚖️ Compare Models", variant="primary")
                
                # Progress
                compare_progress = gr.Slider(0, 100, 0, label="Comparison Progress", interactive=False)
            
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Comparison Results")
                
                # Comparison gallery
                comparison_gallery = gr.Gallery(
                    label="Model Comparison",
                    show_label=True,
                    elem_id="comparison_gallery",
                    height=300
                )
                
                # Comparison metrics
                comparison_metrics = gr.JSON(label="Comparison Metrics")
                
                # Winner selection
                winner_selection = gr.Radio(
                    choices=["Model 1", "Model 2", "Tie"],
                    label="Which model performed better?",
                    value="Tie"
                )
        
        # Event handler
        compare_button.click(
            fn=self._compare_models_interactive,
            inputs=[test_prompt, model1_dropdown, model2_dropdown, comp_steps, comp_guidance],
            outputs=[comparison_gallery, comparison_metrics, compare_progress]
        )
    
    def _create_visualization_dashboard_tab(self):
        """Create visualization dashboard tab."""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Visualization Dashboard")
                
                # Dashboard controls
                dashboard_type = gr.Dropdown(
                    choices=["generation_stats", "parameter_analysis", "quality_metrics", "model_performance"],
                    label="Dashboard Type",
                    value="generation_stats"
                )
                
                # Time range
                time_range = gr.Dropdown(
                    choices=["last_hour", "last_day", "last_week", "all_time"],
                    label="Time Range",
                    value="all_time"
                )
                
                # Update button
                update_dashboard_button = gr.Button("🔄 Update Dashboard", variant="primary")
            
            with gr.Column(scale=2):
                gr.Markdown("### 📈 Dashboard Charts")
                
                # Main chart
                main_chart = gr.Plot(label="Main Visualization")
                
                # Secondary charts
                with gr.Row():
                    chart1 = gr.Plot(label="Chart 1")
                    chart2 = gr.Plot(label="Chart 2")
                
                # Dashboard summary
                dashboard_summary = gr.JSON(label="Dashboard Summary")
        
        # Event handler
        update_dashboard_button.click(
            fn=self._update_visualization_dashboard,
            inputs=[dashboard_type, time_range],
            outputs=[main_chart, chart1, chart2, dashboard_summary]
        )
    
    # Implementation methods
    def _initialize_model(self, model_name: str, pipeline_type: str) -> str:
        """Initialize a diffusion model."""
        try:
            # Simulate model initialization
            time.sleep(1)
            self.current_pipeline = pipeline_type
            return f"✅ Model '{model_name}' initialized successfully with {pipeline_type} pipeline!"
        except Exception as e:
            return f"❌ Error initializing model: {str(e)}"
    
    def _generate_image_realtime(self, prompt: str, negative_prompt: str, 
                                steps: int, guidance: float, width: int, 
                                height: int, seed: int) -> tuple:
        """Generate image in real-time with progress updates."""
        try:
            # Simulate generation with progress updates
            for i in range(steps):
                time.sleep(0.1)  # Simulate processing time
                progress = int((i + 1) / steps * 100)
                yield None, None, progress, f"Generating... {progress}%"
            
            # Create demo image
            demo_image = self._create_demo_image(prompt, width, height)
            
            # Generation info
            gen_info = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "steps": steps,
                "guidance_scale": guidance,
                "width": width,
                "height": height,
                "seed": seed if seed != -1 else "random",
                "generation_time": f"{steps * 0.1:.1f}s"
            }
            
            yield demo_image, gen_info, 100, "✅ Generation completed successfully!"
            
        except Exception as e:
            yield None, None, 0, f"❌ Error: {str(e)}"
    
    def _create_demo_image(self, prompt: str, width: int, height: int) -> Image.Image:
        """Create a demo image for demonstration purposes."""
        # Create a simple colored image with text
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add gradient background
        for y in range(height):
            for x in range(width):
                r = int(255 * (x / width))
                g = int(255 * (y / height))
                b = int(255 * 0.5)
                img_array[y, x] = [r, g, b]
        
        # Convert to PIL Image
        img = Image.fromarray(img_array)
        
        # Add text
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Add prompt text
        text = prompt[:30] + "..." if len(prompt) > 30 else prompt
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Add white text with black outline
        draw.text((x-1, y-1), text, fill=(0, 0, 0), font=font)
        draw.text((x+1, y-1), text, fill=(0, 0, 0), font=font)
        draw.text((x-1, y+1), text, fill=(0, 0, 0), font=font)
        draw.text((x+1, y+1), text, fill=(0, 0, 0), font=font)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        return img
    
    def _save_generated_image(self, image: Image.Image) -> str:
        """Save generated image."""
        try:
            if image is None:
                return "❌ No image to save"
            
            # Save image
            timestamp = int(time.time())
            filename = f"generated_image_{timestamp}.png"
            image.save(filename)
            return f"✅ Image saved as {filename}"
        except Exception as e:
            return f"❌ Error saving image: {str(e)}"
    
    def _regenerate_image(self, prompt: str, negative_prompt: str, 
                         steps: int, guidance: float, width: int, 
                         height: int, seed: int) -> tuple:
        """Regenerate image with same parameters."""
        return self._generate_image_realtime(prompt, negative_prompt, steps, guidance, width, height, seed)
    
    def _explore_parameters_interactive(self, base_prompt: str, param: str, 
                                      param_min: float, param_max: float, 
                                      param_steps: int, fixed_steps: int, 
                                      fixed_width: int, fixed_height: int) -> tuple:
        """Explore parameters interactively."""
        try:
            # Generate parameter values
            param_values = np.linspace(param_min, param_max, param_steps)
            results = []
            
            # Create demo images for each parameter value
            for i, val in enumerate(param_values):
                # Create demo image
                demo_image = self._create_demo_image(f"{base_prompt} ({param}={val:.2f})", fixed_width, fixed_height)
                results.append(demo_image)
            
            # Create quality plot
            fig, ax = plt.subplots(figsize=(8, 6))
            quality_scores = [0.7 + 0.2 * np.random.random() for _ in param_values]
            ax.plot(param_values, quality_scores, 'o-', linewidth=2, markersize=8)
            ax.set_xlabel(param.replace('_', ' ').title())
            ax.set_ylabel('Quality Score')
            ax.set_title(f'Parameter vs Quality Analysis')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Analysis results
            analysis = {
                "parameter": param,
                "range": [float(param_min), float(param_max)],
                "steps": int(param_steps),
                "best_value": float(param_values[np.argmax(quality_scores)]),
                "best_quality": float(max(quality_scores))
            }
            
            return results, fig, analysis, 100
            
        except Exception as e:
            return [], None, {"error": str(e)}, 0
    
    def _generate_creative_variations(self, prompt: str, style_modifiers: List[str], 
                                    mood: str, color_palette: str) -> tuple:
        """Generate creative variations."""
        try:
            variations = []
            
            # Generate variations based on style and mood
            for i in range(4):
                variation_prompt = f"{prompt}, {', '.join(style_modifiers)}, {mood} mood, {color_palette} colors"
                demo_image = self._create_demo_image(variation_prompt, 512, 512)
                variations.append(demo_image)
            
            return variations, 100
            
        except Exception as e:
            return [], 0
    
    def _apply_style_transfer(self, input_image: Image.Image, style_preset: str, 
                             custom_style: str, style_strength: float) -> tuple:
        """Apply style transfer to input image."""
        try:
            if input_image is None:
                return None, {"error": "No input image provided"}, 0
            
            # Simulate style transfer
            time.sleep(2)
            
            # Create styled image
            styled_image = self._create_demo_image(f"Styled with {style_preset}", 512, 512)
            
            # Style info
            style_info = {
                "style_preset": style_preset,
                "custom_style": custom_style,
                "style_strength": style_strength,
                "processing_time": "2.0s"
            }
            
            return styled_image, style_info, 100
            
        except Exception as e:
            return None, {"error": str(e)}, 0
    
    def _compare_models_interactive(self, test_prompt: str, model1: str, 
                                  model2: str, steps: int, guidance: float) -> tuple:
        """Compare two models interactively."""
        try:
            # Simulate model comparison
            time.sleep(3)
            
            # Create comparison images
            model1_image = self._create_demo_image(f"{test_prompt} (Model 1)", 512, 512)
            model2_image = self._create_demo_image(f"{test_prompt} (Model 2)", 512, 512)
            
            comparison_images = [model1_image, model2_image]
            
            # Comparison metrics
            metrics = {
                "model1": {"name": model1, "quality_score": 0.85, "generation_time": 2.3},
                "model2": {"name": model2, "quality_score": 0.78, "generation_time": 1.8},
                "comparison": {"quality_diff": 0.07, "time_diff": 0.5}
            }
            
            return comparison_images, metrics, 100
            
        except Exception as e:
            return [], {"error": str(e)}, 0
    
    def _update_visualization_dashboard(self, dashboard_type: str, time_range: str) -> tuple:
        """Update visualization dashboard."""
        try:
            # Create demo charts based on dashboard type
            if dashboard_type == "generation_stats":
                main_fig = self._create_generation_stats_chart()
                chart1_fig = self._create_parameter_distribution_chart()
                chart2_fig = self._create_quality_trends_chart()
            elif dashboard_type == "parameter_analysis":
                main_fig = self._create_parameter_analysis_chart()
                chart1_fig = self._create_correlation_chart()
                chart2_fig = self._create_optimization_chart()
            else:
                main_fig = self._create_default_chart()
                chart1_fig = self._create_default_chart()
                chart2_fig = self._create_default_chart()
            
            # Dashboard summary
            summary = {
                "dashboard_type": dashboard_type,
                "time_range": time_range,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_generations": 42,
                "average_quality": 0.78
            }
            
            return main_fig, chart1_fig, chart2_fig, summary
            
        except Exception as e:
            default_fig = self._create_default_chart()
            return default_fig, default_fig, default_fig, {"error": str(e)}
    
    def _create_generation_stats_chart(self):
        """Create generation statistics chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Demo data
        categories = ['Text-to-Image', 'Image-to-Image', 'Inpainting']
        counts = [25, 12, 5]
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
        
        bars = ax.bar(categories, counts, color=colors, alpha=0.8)
        ax.set_title('Generation Statistics by Pipeline Type', fontsize=14, fontweight='bold')
        ax.set_ylabel('Number of Generations')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{count}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def _create_parameter_distribution_chart(self):
        """Create parameter distribution chart."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Demo data
        guidance_values = np.random.normal(7.5, 2.0, 100)
        ax.hist(guidance_values, bins=20, alpha=0.7, color='#ff6b6b', edgecolor='black')
        ax.set_title('Guidance Scale Distribution', fontsize=12, fontweight='bold')
        ax.set_xlabel('Guidance Scale')
        ax.set_ylabel('Frequency')
        
        plt.tight_layout()
        return fig
    
    def _create_quality_trends_chart(self):
        """Create quality trends chart."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Demo data
        epochs = range(1, 11)
        quality_scores = [0.65 + 0.02 * i + 0.05 * np.random.random() for i in epochs]
        
        ax.plot(epochs, quality_scores, 'o-', linewidth=2, markersize=6, color='#4ecdc4')
        ax.set_title('Quality Score Trends', fontsize=12, fontweight='bold')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Quality Score')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def _create_parameter_analysis_chart(self):
        """Create parameter analysis chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Demo data
        steps_range = range(10, 101, 10)
        quality_scores = [0.6 + 0.3 * (1 - np.exp(-s/30)) for s in steps_range]
        
        ax.plot(steps_range, quality_scores, 'o-', linewidth=2, markersize=6, color='#45b7d1')
        ax.set_title('Inference Steps vs Quality', fontsize=14, fontweight='bold')
        ax.set_xlabel('Number of Inference Steps')
        ax.set_ylabel('Quality Score')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def _create_correlation_chart(self):
        """Create correlation chart."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Demo data
        x = np.random.normal(0, 1, 50)
        y = 0.7 * x + np.random.normal(0, 0.3, 50)
        
        ax.scatter(x, y, alpha=0.6, color='#ff6b6b')
        ax.set_title('Parameter Correlation', fontsize=12, fontweight='bold')
        ax.set_xlabel('Parameter A')
        ax.set_ylabel('Parameter B')
        
        plt.tight_layout()
        return fig
    
    def _create_optimization_chart(self):
        """Create optimization chart."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Demo data
        iterations = range(1, 21)
        loss_values = [1.0 * np.exp(-i/5) + 0.1 * np.random.random() for i in iterations]
        
        ax.plot(iterations, loss_values, 'o-', linewidth=2, markersize=4, color='#4ecdc4')
        ax.set_title('Training Loss Optimization', fontsize=12, fontweight='bold')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Loss')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def _create_default_chart(self):
        """Create default chart."""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Chart not available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Default Chart')
        plt.tight_layout()
        return fig

def create_interactive_demo_interface() -> gr.Blocks:
    """Create the main interactive demo interface."""
    
    demos = InteractiveDiffusionDemos()
    return demos.create_main_demo_interface()

if __name__ == "__main__":
    # Launch the interactive demo interface
    demo = create_interactive_demo_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
