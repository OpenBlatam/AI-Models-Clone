#!/usr/bin/env python3
"""
Simple Diffusion Demo
"""

import gradio as gr
import torch
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any
import io
import base64

try:
    from advanced_diffusion_system import DiffusionModel, DiffusionConfig
    DIFFUSION_AVAILABLE = True
except ImportError:
    DIFFUSION_AVAILABLE = False

class SimpleDiffusionDemo:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        
    def generate_samples(self, model_type: str, num_samples: int) -> Dict[str, Any]:
        if not DIFFUSION_AVAILABLE:
            return {"error": "Diffusion modules not available"}
        
        try:
            # Create config
            config = DiffusionConfig(
                model_type=model_type,
                image_size=32,
                hidden_size=64,
                num_layers=3,
                num_timesteps=50,
                num_inference_steps=20
            )
            
            # Create model
            model = DiffusionModel(config)
            model.to(self.device)
            
            # Generate samples
            model.eval()
            with torch.no_grad():
                samples = model.sample(batch_size=num_samples)
            
            # Convert to images
            samples = (samples + 1) / 2
            samples = torch.clamp(samples, 0, 1)
            
            # Create grid
            fig, axes = plt.subplots(2, 2, figsize=(8, 8))
            for i, ax in enumerate(axes.flat):
                if i < num_samples:
                    img = samples[i].cpu().permute(1, 2, 0).numpy()
                    ax.imshow(img)
                ax.axis('off')
            
            plt.tight_layout()
            
            # Convert to base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode()
            plt.close()
            
            return {
                "samples": f"data:image/png;base64,{img_str}",
                "model_type": model_type,
                "num_samples": num_samples
            }
        
        except Exception as e:
            return {"error": f"Generation error: {str(e)}"}

def create_diffusion_demo():
    demo_system = SimpleDiffusionDemo()
    
    with gr.Blocks(title="Diffusion Demo") as demo:
        gr.Markdown("# 🎨 Diffusion Models Demo")
        
        with gr.Row():
            with gr.Column():
                model_type = gr.Dropdown(
                    choices=["unet", "latent"],
                    value="unet",
                    label="Model Type"
                )
                num_samples = gr.Slider(
                    minimum=1, maximum=4, value=4, step=1,
                    label="Number of Samples"
                )
                generate_btn = gr.Button("Generate", variant="primary")
            
            with gr.Column():
                output = gr.JSON(label="Results")
                image = gr.Image(label="Generated Samples", visible=False)
        
        def handle_generation(model_type, num_samples):
            result = demo_system.generate_samples(model_type, num_samples)
            if "samples" in result:
                return result, result["samples"], True
            else:
                return result, None, False
        
        generate_btn.click(
            handle_generation,
            inputs=[model_type, num_samples],
            outputs=[output, image, image]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_diffusion_demo()
    demo.launch(server_name="0.0.0.0", server_port=7861, share=True)
