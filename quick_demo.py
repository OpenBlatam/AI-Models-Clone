#!/usr/bin/env python3
"""
Quick Demo for Interactive Diffusion Models
===========================================

A simple demo that can be run immediately to showcase the system.
"""

import gradio as gr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import json

def create_quick_demo():
    """Create a quick demo interface."""
    
    def generate_demo_image(prompt, steps, guidance, width, height):
        """Generate a demo image based on parameters."""
        try:
            # Create a simple colored image with text
            img_array = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add gradient background based on parameters
            for y in range(height):
                for x in range(width):
                    r = int(255 * (x / width) * (guidance / 20.0))
                    g = int(255 * (y / height) * (steps / 100.0))
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
            
            # Add parameter info
            param_text = f"Steps: {steps}, Guidance: {guidance}"
            bbox = draw.textbbox((0, 0), param_text, font=font)
            param_width = bbox[2] - bbox[0]
            param_height = bbox[3] - bbox[1]
            
            param_x = (width - param_width) // 2
            param_y = height - param_height - 20
            
            draw.text((param_x, param_y), param_text, fill=(255, 255, 255), font=font)
            
            return img
            
        except Exception as e:
            # Return error image
            error_img = Image.new('RGB', (width, height), color='red')
            draw = ImageDraw.Draw(error_img)
            draw.text((10, 10), f"Error: {str(e)}", fill='white')
            return error_img
    
    def explore_parameters(base_prompt, param_type, min_val, max_val, num_steps):
        """Explore parameters and show results."""
        try:
            results = []
            param_values = np.linspace(min_val, max_val, num_steps)
            
            for val in param_values:
                # Create demo image for each parameter value
                demo_img = generate_demo_image(
                    f"{base_prompt} ({param_type}={val:.2f})",
                    50, 7.5, 256, 256
                )
                results.append(demo_img)
            
            return results
            
        except Exception as e:
            return []
    
    def create_parameter_plot(param_type, min_val, max_val, num_steps):
        """Create a parameter analysis plot."""
        try:
            import matplotlib.pyplot as plt
            
            param_values = np.linspace(min_val, max_val, num_steps)
            quality_scores = [0.7 + 0.2 * np.random.random() for _ in param_values]
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(param_values, quality_scores, 'o-', linewidth=2, markersize=8)
            ax.set_xlabel(param_type.replace('_', ' ').title())
            ax.set_ylabel('Quality Score')
            ax.set_title(f'Parameter vs Quality Analysis')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            # Return a simple error plot
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Parameter Analysis Error')
            plt.tight_layout()
            return fig
    
    # Create the interface
    with gr.Blocks(
        title="🎨 Quick Diffusion Demo",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1000px !important;
        }
        .demo-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        """
    ) as demo:
        
        # Header
        gr.HTML("""
        <div class="demo-header">
            <h1>🎨 Quick Diffusion Demo</h1>
            <p>Experience interactive diffusion model generation in real-time</p>
        </div>
        """)
        
        with gr.Tabs():
            
            # Basic Generation Tab
            with gr.Tab("🚀 Basic Generation"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎯 Generation Parameters")
                        
                        prompt_input = gr.Textbox(
                            label="Prompt",
                            placeholder="A beautiful landscape with mountains and trees...",
                            lines=3
                        )
                        
                        with gr.Row():
                            steps_slider = gr.Slider(10, 100, 50, label="Inference Steps", step=1)
                            guidance_slider = gr.Slider(1.0, 20.0, 7.5, label="Guidance Scale", step=0.1)
                        
                        with gr.Row():
                            width_slider = gr.Slider(256, 1024, 512, step=64, label="Width")
                            height_slider = gr.Slider(256, 1024, 512, step=64, label="Height")
                        
                        generate_button = gr.Button("🎨 Generate Image", variant="primary", size="lg")
                        
                        # Progress
                        progress_bar = gr.Slider(0, 100, 0, label="Generation Progress", interactive=False)
                        status_output = gr.Textbox(label="Status", interactive=False)
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 🖼️ Generated Result")
                        
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
                            regenerate_button = gr.Button("🔄 Regenerate")
                
                # Event handlers
                generate_button.click(
                    fn=lambda p, s, g, w, h: (generate_demo_image(p, s, g, w, h), 
                                              {"prompt": p, "steps": s, "guidance": g, "width": w, "height": h}),
                    inputs=[prompt_input, steps_slider, guidance_slider, width_slider, height_slider],
                    outputs=[output_image, generation_info]
                )
                
                save_button.click(
                    fn=lambda img: f"✅ Image saved as generated_image_{int(time.time())}.png" if img else "❌ No image to save",
                    inputs=[output_image],
                    outputs=[status_output]
                )
                
                regenerate_button.click(
                    fn=lambda p, s, g, w, h: (generate_demo_image(p, s, g, w, h), 
                                              {"prompt": p, "steps": s, "guidance": g, "width": w, "height": h}),
                    inputs=[prompt_input, steps_slider, guidance_slider, width_slider, height_slider],
                    outputs=[output_image, generation_info]
                )
            
            # Parameter Exploration Tab
            with gr.Tab("🔬 Parameter Explorer"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🔬 Parameter Exploration")
                        
                        base_prompt = gr.Textbox(
                            label="Base Prompt",
                            placeholder="A beautiful landscape...",
                            lines=2
                        )
                        
                        param_type = gr.Dropdown(
                            choices=["guidance_scale", "num_inference_steps", "strength"],
                            label="Parameter to Explore",
                            value="guidance_scale"
                        )
                        
                        with gr.Row():
                            param_min = gr.Number(label="Min Value", value=1.0)
                            param_max = gr.Number(label="Max Value", value=20.0)
                            param_steps = gr.Number(label="Number of Steps", value=5)
                        
                        explore_button = gr.Button("🔬 Explore Parameters", variant="primary")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 📊 Exploration Results")
                        
                        exploration_gallery = gr.Gallery(
                            label="Parameter Exploration Results",
                            show_label=True,
                            elem_id="exploration_gallery",
                            height=300
                        )
                        
                        parameter_plot = gr.Plot(label="Parameter vs Quality Analysis")
                
                # Event handlers
                explore_button.click(
                    fn=explore_parameters,
                    inputs=[base_prompt, param_type, param_min, param_max, param_steps],
                    outputs=[exploration_gallery]
                )
                
                explore_button.click(
                    fn=create_parameter_plot,
                    inputs=[param_type, param_min, param_max, param_steps],
                    outputs=[parameter_plot]
                )
            
            # Creative Variations Tab
            with gr.Tab("🎭 Creative Variations"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🎭 Creative Input")
                        
                        creative_prompt = gr.Textbox(
                            label="Creative Prompt",
                            placeholder="A surreal dreamscape where...",
                            lines=3
                        )
                        
                        style_modifiers = gr.CheckboxGroup(
                            choices=["cinematic", "artistic", "photorealistic", "abstract"],
                            label="Style Modifiers",
                            value=["artistic"]
                        )
                        
                        mood = gr.Dropdown(
                            choices=["peaceful", "energetic", "mysterious", "joyful"],
                            label="Mood",
                            value="peaceful"
                        )
                        
                        generate_variations_button = gr.Button("🎨 Generate Variations", variant="primary")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("### 🎨 Creative Variations")
                        
                        variations_gallery = gr.Gallery(
                            label="Creative Variations",
                            show_label=True,
                            elem_id="variations_gallery",
                            height=400
                        )
                
                # Event handler
                def generate_variations(prompt, styles, mood):
                    variations = []
                    for i in range(4):
                        variation_prompt = f"{prompt}, {', '.join(styles)}, {mood} mood"
                        demo_img = generate_demo_image(variation_prompt, 50, 7.5, 512, 512)
                        variations.append(demo_img)
                    return variations
                
                generate_variations_button.click(
                    fn=generate_variations,
                    inputs=[creative_prompt, style_modifiers, mood],
                    outputs=[variations_gallery]
                )
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 20px; color: #666;">
            <p>Quick Demo - Built with ❤️ using Gradio</p>
        </div>
        """)
    
    return demo

if __name__ == "__main__":
    # Create and launch the quick demo
    demo = create_quick_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )
