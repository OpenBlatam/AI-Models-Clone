"""
User-Friendly Interfaces for Diffusion Models with Error Handling
===============================================================

This module provides intuitive and visually appealing interfaces that showcase
model capabilities in an easy-to-understand way, with comprehensive error handling.
"""

import gradio as gr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import json
from typing import List, Dict, Any, Optional, Tuple

# Import error handling system
from .gradio_error_handling import (
    InputValidator, ErrorHandler, ErrorSeverity, ValidationError, ProcessingError,
    error_handler_decorator, validation_decorator, GradioErrorHandler
)

class UserFriendlyInterfaces:
    """User-friendly interfaces for diffusion models with error handling."""
    
    def __init__(self):
        self.themes = {
            "modern": {
                "primary_color": "#667eea",
                "secondary_color": "#764ba2",
                "accent_color": "#f093fb",
                "text_color": "#2d3748",
                "background_color": "#f7fafc"
            },
            "dark": {
                "primary_color": "#1a202c",
                "secondary_color": "#2d3748",
                "accent_color": "#667eea",
                "text_color": "#e2e8f0",
                "background_color": "#0f1419"
            },
            "nature": {
                "primary_color": "#38a169",
                "secondary_color": "#68d391",
                "accent_color": "#f6ad55",
                "text_color": "#2f855a",
                "background_color": "#f0fff4"
            }
        }
        self.error_handler = ErrorHandler()
    
    def create_showcase_interface(self, theme: str = "modern") -> gr.Blocks:
        """Create a showcase interface that highlights model capabilities."""
        
        colors = self.themes.get(theme, self.themes["modern"])
        
        with gr.Blocks(
            title="🎨 Diffusion Models Showcase",
            theme=gr.themes.Soft(),
            css=f"""
            .gradio-container {{
                max-width: 1400px !important;
            }}
            .showcase-header {{
                text-align: center;
                padding: 30px;
                background: linear-gradient(135deg, {colors['primary_color']} 0%, {colors['secondary_color']} 100%);
                color: white;
                border-radius: 20px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .capability-card {{
                border: 2px solid {colors['accent_color']};
                border-radius: 20px;
                padding: 25px;
                margin: 20px 0;
                background: white;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }}
            .capability-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }}
            .feature-highlight {{
                background: linear-gradient(45deg, {colors['accent_color']}, {colors['secondary_color']});
                color: white;
                padding: 15px;
                border-radius: 15px;
                margin: 10px 0;
                text-align: center;
                font-weight: bold;
            }}
            .error-notification {{
                background: #ffebee;
                border: 2px solid #f44336;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                color: #d32f2f;
            }}
            .success-notification {{
                background: #e8f5e8;
                border: 2px solid #4caf50;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                color: #2e7d32;
            }}
            """
        ) as demo:
            
            # Header
            gr.HTML(f"""
            <div class="showcase-header">
                <h1>🎨 Diffusion Models Showcase</h1>
                <p>Discover the incredible capabilities of state-of-the-art AI image generation</p>
                <div style="margin-top: 20px;">
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; margin: 0 10px;">
                        ✨ Text-to-Image
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; margin: 0 10px;">
                        🔄 Image-to-Image
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; margin: 0 10px;">
                        🎭 Inpainting
                    </span>
                </div>
            </div>
            """)
            
            with gr.Tabs():
                
                # Capabilities Showcase Tab
                with gr.Tab("🚀 Capabilities Showcase", id="showcase"):
                    self._create_capabilities_showcase_tab(colors)
                
                # Interactive Learning Tab
                with gr.Tab("📚 Interactive Learning", id="learning"):
                    self._create_interactive_learning_tab(colors)
                
                # Creative Playground Tab
                with gr.Tab("🎮 Creative Playground", id="playground"):
                    self._create_creative_playground_tab(colors)
                
                # Model Comparison Tab
                with gr.Tab("⚖️ Model Comparison", id="comparison"):
                    self._create_model_comparison_tab(colors)
                
                # Error Monitor Tab
                GradioErrorHandler.create_error_tab()
            
            # Footer
            gr.HTML(f"""
            <div style="text-align: center; padding: 30px; color: {colors['text_color']}; background: {colors['background_color']}; border-radius: 20px; margin-top: 30px;">
                <h3>🎯 Ready to Create?</h3>
                <p>Choose your preferred interface and start exploring the world of AI-generated art!</p>
            </div>
            """)
        
        return demo
    
    def _create_capabilities_showcase_tab(self, colors: Dict[str, str]):
        """Create capabilities showcase tab."""
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 🌟 What Can Diffusion Models Do?")
                
                # Capability cards
                with gr.Box(elem_classes="capability-card"):
                    gr.Markdown("#### ✨ Text-to-Image Generation")
                    gr.Markdown("Transform your ideas into stunning visuals with just words")
                    
                    with gr.Row():
                        gr.Markdown("**Example Prompts:**")
                        gr.Markdown("• 'A serene mountain landscape at sunset'")
                        gr.Markdown("• 'A futuristic city with flying cars'")
                        gr.Markdown("• 'A magical forest with glowing mushrooms'")
                
                with gr.Box(elem_classes="capability-card"):
                    gr.Markdown("#### 🔄 Image-to-Image Transformation")
                    gr.Markdown("Take existing images and transform them into something new")
                    
                    with gr.Row():
                        gr.Markdown("**Transformations:**")
                        gr.Markdown("• Style changes (realistic → artistic)")
                        gr.Markdown("• Season changes (summer → winter)")
                        gr.Markdown("• Time of day (day → night)")
                
                with gr.Box(elem_classes="capability-card"):
                    gr.Markdown("#### 🎭 Inpainting & Editing")
                    gr.Markdown("Selectively edit and enhance specific parts of images")
                    
                    with gr.Row():
                        gr.Markdown("**Applications:**")
                        gr.Markdown("• Remove unwanted objects")
                        gr.Markdown("• Add new elements")
                        gr.Markdown("• Fix imperfections")
            
            with gr.Column(scale=1):
                gr.Markdown("### 🎯 Try It Now!")
                
                # Quick demo
                demo_prompt = gr.Textbox(
                    label="Quick Demo Prompt",
                    placeholder="A beautiful butterfly in a garden...",
                    lines=3
                )
                
                demo_button = gr.Button("🎨 Generate Demo", variant="primary", size="lg")
                
                # Status and error notifications
                status_output = gr.HTML(label="Status", elem_classes="success-notification")
                
                demo_output = gr.Image(label="Demo Result", height=300)
                
                # Feature highlights
                gr.HTML(f"""
                <div class="feature-highlight">
                    🚀 Lightning Fast Generation
                </div>
                <div class="feature-highlight">
                    🎨 High Quality Output
                </div>
                <div class="feature-highlight">
                    🔧 Easy Parameter Control
                </div>
                """)
        
        # Event handler with error handling
        demo_button.click(
            fn=self._generate_demo_image_safe,
            inputs=[demo_prompt],
            outputs=[demo_output, status_output]
        )
    
    def _create_interactive_learning_tab(self, colors: Dict[str, str]):
        """Create interactive learning tab."""
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📚 Learn the Basics")
                
                # Learning modules
                with gr.Accordion("🎯 Understanding Prompts", open=True):
                    gr.Markdown("""
                    **Good Prompts Include:**
                    - Subject: What you want to see
                    - Style: How you want it to look
                    - Mood: The feeling you want to convey
                    - Details: Specific characteristics
                    
                    **Example:** "A majestic dragon flying over a medieval castle at sunset, cinematic lighting, epic fantasy style"
                    """)
                
                with gr.Accordion("⚙️ Key Parameters", open=False):
                    gr.Markdown("""
                    **Guidance Scale (1-20):**
                    - Lower values = More creative, less controlled
                    - Higher values = More precise, less creative
                    
                    **Inference Steps (10-100):**
                    - More steps = Better quality, slower generation
                    - Fewer steps = Faster generation, lower quality
                    """)
                
                with gr.Accordion("🎨 Style Modifiers", open=False):
                    gr.Markdown("""
                    **Artistic Styles:**
                    - photorealistic, artistic, cartoon, sketch
                    - oil painting, watercolor, digital art
                    
                    **Photography Styles:**
                    - cinematic, portrait, landscape, macro
                    - vintage, black and white, high contrast
                    """)
            
            with gr.Column(scale=2):
                gr.Markdown("### 🧪 Interactive Learning Lab")
                
                # Learning experiment
                experiment_prompt = gr.Textbox(
                    label="Your Learning Prompt",
                    placeholder="Try different prompts to see how they affect the output...",
                    lines=3
                )
                
                with gr.Row():
                    guidance_slider = gr.Slider(1, 20, 7.5, label="Guidance Scale", step=0.5)
                    steps_slider = gr.Slider(10, 100, 50, label="Inference Steps", step=5)
                
                with gr.Row():
                    style_modifier = gr.Dropdown(
                        choices=["realistic", "artistic", "cartoon", "sketch", "cinematic"],
                        label="Style Modifier",
                        value="realistic"
                    )
                    mood_modifier = gr.Dropdown(
                        choices=["peaceful", "dramatic", "mysterious", "joyful", "melancholic"],
                        label="Mood",
                        value="peaceful"
                    )
                
                experiment_button = gr.Button("🧪 Run Experiment", variant="primary")
                
                # Status and results
                experiment_status = gr.HTML(label="Experiment Status", elem_classes="success-notification")
                experiment_output = gr.Image(label="Experiment Result", height=400)
                analysis_output = gr.JSON(label="Parameter Analysis")
        
        # Event handler with error handling
        experiment_button.click(
            fn=self._run_learning_experiment_safe,
            inputs=[experiment_prompt, guidance_slider, steps_slider, style_modifier, mood_modifier],
            outputs=[experiment_output, analysis_output, experiment_status]
        )
    
    def _create_creative_playground_tab(self, colors: Dict[str, str]):
        """Create creative playground tab."""
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎮 Creative Tools")
                
                # Creative prompts
                creative_prompt = gr.Textbox(
                    label="Your Creative Vision",
                    placeholder="Describe your wildest imagination...",
                    lines=4
                )
                
                # Style combinations
                gr.Markdown("#### 🎨 Style Combinations")
                style_combinations = gr.CheckboxGroup(
                    choices=[
                        "cinematic + dramatic lighting",
                        "artistic + vibrant colors",
                        "fantasy + magical atmosphere",
                        "sci-fi + futuristic design",
                        "vintage + nostalgic feeling"
                    ],
                    label="Choose Style Combinations",
                    value=["cinematic + dramatic lighting"]
                )
                
                # Creative parameters
                with gr.Row():
                    creativity_level = gr.Slider(1, 10, 7, label="Creativity Level", step=1)
                    detail_level = gr.Slider(1, 10, 8, label="Detail Level", step=1)
                
                create_button = gr.Button("🎨 Create Magic!", variant="primary", size="lg")
                
                # Progress and status
                progress_bar = gr.Slider(0, 100, 0, label="Creation Progress", interactive=False)
                creation_status = gr.HTML(label="Creation Status", elem_classes="success-notification")
            
            with gr.Column(scale=2):
                gr.Markdown("### 🎭 Creative Results")
                
                # Results gallery
                results_gallery = gr.Gallery(
                    label="Your Creative Creations",
                    show_label=True,
                    elem_id="creative_gallery",
                    height=400
                )
                
                # Creative info
                creative_info = gr.JSON(label="Creation Details")
                
                # Action buttons
                with gr.Row():
                    save_all_button = gr.Button("💾 Save All")
                    refine_button = gr.Button("🔧 Refine Selected")
                    share_button = gr.Button("📤 Share")
            
            # Event handler with error handling
            create_button.click(
                fn=self._create_creative_artwork_safe,
                inputs=[creative_prompt, style_combinations, creativity_level, detail_level],
                outputs=[results_gallery, creative_info, progress_bar, creation_status]
            )
    
    def _create_model_comparison_tab(self, colors: Dict[str, str]):
        """Create model comparison tab."""
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚖️ Compare Models")
                
                # Test prompt
                test_prompt = gr.Textbox(
                    label="Test Prompt",
                    placeholder="Use the same prompt to compare different models...",
                    lines=3
                )
                
                # Model selection
                gr.Markdown("#### 🏗️ Select Models to Compare")
                model1 = gr.Dropdown(
                    choices=[
                        "Stable Diffusion 2.1",
                        "Stable Diffusion XL",
                        "Midjourney Style",
                        "Custom Model A"
                    ],
                    label="Model 1",
                    value="Stable Diffusion 2.1"
                )
                
                model2 = gr.Dropdown(
                    choices=[
                        "Stable Diffusion 2.1",
                        "Stable Diffusion XL",
                        "Midjourney Style",
                        "Custom Model B"
                    ],
                    label="Model 2",
                    value="Stable Diffusion XL"
                )
                
                # Comparison parameters
                with gr.Row():
                    comp_guidance = gr.Slider(1.0, 20.0, 7.5, label="Guidance Scale", step=0.5)
                    comp_steps = gr.Slider(10, 100, 50, label="Inference Steps", step=5)
                
                compare_button = gr.Button("⚖️ Compare Models", variant="primary")
                
                # Progress and status
                compare_progress = gr.Slider(0, 100, 0, label="Comparison Progress", interactive=False)
                comparison_status = gr.HTML(label="Comparison Status", elem_classes="success-notification")
            
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
                comparison_metrics = gr.JSON(label="Performance Metrics")
                
                # Winner selection
                winner_selection = gr.Radio(
                    choices=["Model 1", "Model 2", "Tie", "Different Strengths"],
                    label="Which model performed better?",
                    value="Tie"
                )
                
                # Detailed analysis
                analysis_plot = gr.Plot(label="Detailed Analysis")
        
        # Event handler with error handling
        compare_button.click(
            fn=self._compare_models_detailed_safe,
            inputs=[test_prompt, model1, model2, comp_guidance, comp_steps],
            outputs=[comparison_gallery, comparison_metrics, compare_progress, analysis_plot, comparison_status]
        )
    
    # Safe implementation methods with error handling
    @error_handler_decorator("demo_image_generation")
    @validation_decorator({
        "prompt": InputValidator.validate_prompt
    })
    def _generate_demo_image_safe(self, prompt: str) -> Tuple[Image.Image, str]:
        """Generate a demo image with error handling."""
        try:
            demo_image = self._generate_demo_image(prompt)
            status_html = f"""
            <div class="success-notification">
                <h4>✅ Success!</h4>
                <p>Demo image generated successfully from prompt: "{prompt[:50]}{'...' if len(prompt) > 50 else ''}"</p>
            </div>
            """
            return demo_image, status_html
        except Exception as e:
            error_info = self.error_handler.handle_error(e, "demo_image_generation")
            status_html = f"""
            <div class="error-notification">
                <h4>❌ Error: {error_info.error_type}</h4>
                <p>{error_info.message}</p>
                <small>Severity: {error_info.severity.value}</small>
            </div>
            """
            # Return error image
            error_img = self._create_error_image(error_info.message)
            return error_img, status_html
    
    @error_handler_decorator("learning_experiment")
    @validation_decorator({
        "prompt": InputValidator.validate_prompt,
        "guidance": InputValidator.validate_guidance_scale,
        "steps": InputValidator.validate_inference_steps
    })
    def _run_learning_experiment_safe(self, prompt: str, guidance: float, steps: int, 
                                     style: str, mood: str) -> Tuple[Image.Image, Dict[str, Any], str]:
        """Run a learning experiment with error handling."""
        try:
            # Create enhanced prompt
            enhanced_prompt = f"{prompt}, {style} style, {mood} mood"
            
            # Generate demo image
            demo_image = self._generate_demo_image(enhanced_prompt)
            
            # Analysis results
            analysis = {
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "guidance_scale": guidance,
                "inference_steps": steps,
                "style_modifier": style,
                "mood_modifier": mood,
                "expected_quality": "high" if steps > 50 else "medium",
                "expected_creativity": "high" if guidance < 10 else "medium",
                "recommendations": [
                    "Try increasing steps for better quality",
                    "Lower guidance for more creativity",
                    "Combine multiple style modifiers"
                ]
            }
            
            status_html = f"""
            <div class="success-notification">
                <h4>✅ Experiment Completed!</h4>
                <p>Successfully generated image with {style} style and {mood} mood</p>
            </div>
            """
            
            return demo_image, analysis, status_html
            
        except Exception as e:
            error_info = self.error_handler.handle_error(e, "learning_experiment")
            status_html = f"""
            <div class="error-notification">
                <h4>❌ Experiment Failed</h4>
                <p>{error_info.message}</p>
                <small>Severity: {error_info.severity.value}</small>
            </div>
            """
            
            error_img = self._create_error_image(error_info.message)
            return error_img, {"error": str(e)}, status_html
    
    @error_handler_decorator("creative_artwork")
    @validation_decorator({
        "prompt": InputValidator.validate_prompt
    })
    def _create_creative_artwork_safe(self, prompt: str, styles: List[str], 
                                     creativity: int, detail: int) -> Tuple[List[Image.Image], Dict[str, Any], int, str]:
        """Create creative artwork with error handling."""
        try:
            results = []
            
            # Generate variations based on creativity and detail
            num_variations = min(creativity, 6)  # Max 6 variations
            
            for i in range(num_variations):
                # Create enhanced prompt
                style_text = ", ".join(styles) if styles else "artistic"
                enhanced_prompt = f"{prompt}, {style_text}, creativity level {creativity}, detail level {detail}"
                
                # Generate demo image
                demo_image = self._generate_demo_image(enhanced_prompt)
                results.append(demo_image)
            
            # Creative info
            creative_info = {
                "original_prompt": prompt,
                "style_combinations": styles,
                "creativity_level": creativity,
                "detail_level": detail,
                "variations_created": len(results),
                "creation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            status_html = f"""
            <div class="success-notification">
                <h4>✅ Creative Artwork Created!</h4>
                <p>Successfully generated {len(results)} creative variations</p>
            </div>
            """
            
            return results, creative_info, 100, status_html
            
        except Exception as e:
            error_info = self.error_handler.handle_error(e, "creative_artwork")
            status_html = f"""
            <div class="error-notification">
                <h4>❌ Creation Failed</h4>
                <p>{error_info.message}</p>
                <small>Severity: {error_info.severity.value}</small>
            </div>
            """
            
            return [], {"error": str(e)}, 0, status_html
    
    @error_handler_decorator("model_comparison")
    @validation_decorator({
        "prompt": InputValidator.validate_prompt,
        "guidance": InputValidator.validate_guidance_scale,
        "steps": InputValidator.validate_inference_steps
    })
    def _compare_models_detailed_safe(self, prompt: str, model1: str, model2: str, 
                                     guidance: float, steps: int) -> Tuple[List[Image.Image], Dict[str, Any], int, Any, str]:
        """Compare models with detailed analysis and error handling."""
        try:
            # Simulate model comparison
            time.sleep(2)
            
            # Create comparison images
            model1_image = self._generate_demo_image(f"{prompt} ({model1})")
            model2_image = self._generate_demo_image(f"{prompt} ({model2})")
            
            comparison_images = [model1_image, model2_image]
            
            # Comparison metrics
            metrics = {
                "model1": {
                    "name": model1,
                    "quality_score": 0.85,
                    "generation_time": 2.3,
                    "creativity_score": 0.78,
                    "detail_score": 0.82
                },
                "model2": {
                    "name": model2,
                    "quality_score": 0.78,
                    "generation_time": 1.8,
                    "creativity_score": 0.85,
                    "detail_score": 0.75
                },
                "comparison": {
                    "quality_winner": model1,
                    "speed_winner": model2,
                    "creativity_winner": model2,
                    "detail_winner": model1
                }
            }
            
            # Create analysis plot
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 6))
            
            categories = ['Quality', 'Speed', 'Creativity', 'Detail']
            model1_scores = [0.85, 0.57, 0.78, 0.82]  # Speed inverted (lower is better)
            model2_scores = [0.78, 0.72, 0.85, 0.75]
            
            x = np.arange(len(categories))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, model1_scores, width, label=model1, alpha=0.8)
            bars2 = ax.bar(x + width/2, model2_scores, width, label=model2, alpha=0.8)
            
            ax.set_xlabel('Metrics')
            ax.set_ylabel('Score')
            ax.set_title('Model Comparison Analysis')
            ax.set_xticks(x)
            ax.set_xticklabels(categories)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            status_html = f"""
            <div class="success-notification">
                <h4>✅ Comparison Completed!</h4>
                <p>Successfully compared {model1} vs {model2}</p>
            </div>
            """
            
            return comparison_images, metrics, 100, fig, status_html
            
        except Exception as e:
            error_info = self.error_handler.handle_error(e, "model_comparison")
            status_html = f"""
            <div class="error-notification">
                <h4>❌ Comparison Failed</h4>
                <p>{error_info.message}</p>
                <small>Severity: {error_info.severity.value}</small>
            </div>
            """
            
            error_img = self._create_error_image(error_info.message)
            return [error_img], {"error": str(e)}, 0, None, status_html
    
    # Helper methods
    def _generate_demo_image(self, prompt: str) -> Image.Image:
        """Generate a demo image for showcase."""
        try:
            # Create demo image
            width, height = 512, 512
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
            text = prompt[:40] + "..." if len(prompt) > 40 else prompt
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
            
        except Exception as e:
            # Return error image
            error_img = Image.new('RGB', (512, 512), color='red')
            draw = ImageDraw.Draw(error_img)
            draw.text((10, 10), f"Demo Error: {str(e)}", fill='white')
            return error_img
    
    def _create_error_image(self, message: str) -> Image.Image:
        """Create an error image for display."""
        width, height = 512, 512
        
        # Create error image
        img = Image.new('RGB', (width, height), color='#ffebee')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Add error icon
        draw.ellipse([width//2 - 50, height//2 - 80, width//2 + 50, height//2 + 20], 
                     fill='#f44336', outline='#d32f2f', width=3)
        draw.text((width//2 - 10, height//2 - 60), "!", fill='white', font=font)
        
        # Add error message
        lines = self._wrap_text(message, font, width - 40)
        y_offset = height//2 + 40
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, fill='#d32f2f', font=font)
            y_offset += 30
        
        return img
    
    def _wrap_text(self, text: str, font, max_width: int) -> List[str]:
        """Wrap text to fit within max_width."""
        if not font:
            return [text]
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines[:5]  # Limit to 5 lines

def create_user_friendly_interface(theme: str = "modern") -> gr.Blocks:
    """Create a user-friendly interface with error handling."""
    
    interfaces = UserFriendlyInterfaces()
    return interfaces.create_showcase_interface(theme)

if __name__ == "__main__":
    # Launch the user-friendly interface
    demo = create_user_friendly_interface("modern")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
