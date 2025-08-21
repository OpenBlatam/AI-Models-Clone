#!/usr/bin/env python3
"""
Optimized Gradio Interface Implementation
=======================================

Production-ready Gradio interface with:
- Comprehensive error handling
- Input validation
- Performance optimizations
- Multiple model support
- Real-time feedback
"""

import gradio as gr
import torch
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import time
from pathlib import Path
import json

# Import our optimized modules
from deep_learning_optimized import OptimizedTransformerModel, OptimizedDiffusionModel
from attention_mechanisms_optimized import OptimizedTransformerModel as AttentionModel
from diffusion_models_optimized import OptimizedDiffusionPipeline

# =============================================================================
# Optimized Interface Configuration
# =============================================================================

class InterfaceConfig:
    """Configuration for optimized Gradio interface."""
    
    # Model settings
    DEFAULT_MODEL_NAME = "gpt2"
    DEFAULT_DIFFUSION_MODEL = "runwayml/stable-diffusion-v1-5"
    
    # Generation settings
    MAX_LENGTH = 512
    DEFAULT_TEMPERATURE = 0.8
    DEFAULT_TOP_K = 50
    DEFAULT_TOP_P = 0.9
    
    # Image generation settings
    DEFAULT_IMAGE_SIZE = 512
    DEFAULT_INFERENCE_STEPS = 30
    DEFAULT_GUIDANCE_SCALE = 7.5
    
    # Interface settings
    THEME = "default"
    ALLOW_FLAG = True
    SHARE = False
    DEBUG = False

# =============================================================================
# Optimized Model Manager
# =============================================================================

class OptimizedModelManager:
    """Manages multiple models with caching and optimization."""
    
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.models = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize and cache models."""
        try:
            # Text generation model
            self.models["text_generator"] = OptimizedTransformerModel(
                model_name=InterfaceConfig.DEFAULT_MODEL_NAME
            )
            
            # Diffusion model
            self.models["image_generator"] = OptimizedDiffusionPipeline(
                model_name=InterfaceConfig.DEFAULT_DIFFUSION_MODEL,
                device=self.device
            )
            
            # Attention model
            self.models["attention_model"] = AttentionModel(
                vocab_size=50000,
                embed_dim=512,
                num_layers=6,
                num_heads=8,
                ff_dim=2048
            )
            
            self.logger.info("All models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {e}")
            raise
    
    def get_model(self, model_name: str):
        """Get model by name with error handling."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        return self.models[model_name]
    
    def list_models(self) -> List[str]:
        """List available models."""
        return list(self.models.keys())

# =============================================================================
# Optimized Interface Functions
# =============================================================================

class OptimizedInterfaceFunctions:
    """Optimized functions for Gradio interface."""
    
    def __init__(self, model_manager: OptimizedModelManager):
        self.model_manager = model_manager
        self.logger = logging.getLogger(__name__)
    
    def generate_text(
        self,
        prompt: str,
        max_length: int = InterfaceConfig.MAX_LENGTH,
        temperature: float = InterfaceConfig.DEFAULT_TEMPERATURE,
        top_k: int = InterfaceConfig.DEFAULT_TOP_K,
        top_p: float = InterfaceConfig.DEFAULT_TOP_P,
        do_sample: bool = True
    ) -> Dict[str, Any]:
        """Generate text with comprehensive error handling."""
        try:
            # Input validation
            if not prompt or not prompt.strip():
                return {"error": "Prompt cannot be empty"}
            
            if max_length <= 0 or max_length > 2048:
                return {"error": "Max length must be between 1 and 2048"}
            
            if temperature <= 0 or temperature > 2.0:
                return {"error": "Temperature must be between 0 and 2"}
            
            # Get model
            model = self.model_manager.get_model("text_generator")
            
            # Tokenize input
            tokenizer = model.tokenizer
            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=max_length
            )
            
            # Generate text
            start_time = time.time()
            
            with torch.no_grad():
                generated_ids = model.generate(
                    input_ids=inputs["input_ids"],
                    max_length=max_length,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    do_sample=do_sample,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
            
            generation_time = time.time() - start_time
            
            return {
                "generated_text": generated_text,
                "original_prompt": prompt,
                "generation_time": f"{generation_time:.2f}s",
                "parameters": {
                    "max_length": max_length,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                    "do_sample": do_sample
                }
            }
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            return {"error": f"Text generation failed: {str(e)}"}
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = InterfaceConfig.DEFAULT_IMAGE_SIZE,
        height: int = InterfaceConfig.DEFAULT_IMAGE_SIZE,
        num_inference_steps: int = InterfaceConfig.DEFAULT_INFERENCE_STEPS,
        guidance_scale: float = InterfaceConfig.DEFAULT_GUIDANCE_SCALE,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate image with comprehensive error handling."""
        try:
            # Input validation
            if not prompt or not prompt.strip():
                return {"error": "Prompt cannot be empty"}
            
            if width < 64 or width > 1024 or height < 64 or height > 1024:
                return {"error": "Image dimensions must be between 64 and 1024"}
            
            if num_inference_steps < 1 or num_inference_steps > 100:
                return {"error": "Inference steps must be between 1 and 100"}
            
            if guidance_scale < 1.0 or guidance_scale > 20.0:
                return {"error": "Guidance scale must be between 1.0 and 20.0"}
            
            # Get model
            model = self.model_manager.get_model("image_generator")
            
            # Generate image
            start_time = time.time()
            
            images = model.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt if negative_prompt else None,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                seed=seed
            )
            
            generation_time = time.time() - start_time
            
            return {
                "image": images[0] if images else None,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "generation_time": f"{generation_time:.2f}s",
                "parameters": {
                    "width": width,
                    "height": height,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "seed": seed
                }
            }
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            return {"error": f"Image generation failed: {str(e)}"}
    
    def analyze_attention(
        self,
        text: str,
        max_length: int = 256
    ) -> Dict[str, Any]:
        """Analyze attention patterns with comprehensive error handling."""
        try:
            # Input validation
            if not text or not text.strip():
                return {"error": "Text cannot be empty"}
            
            if max_length <= 0 or max_length > 512:
                return {"error": "Max length must be between 1 and 512"}
            
            # Get model
            model = self.model_manager.get_model("attention_model")
            
            # Tokenize input
            tokenizer = model.tokenizer
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
                padding=True
            )
            
            # Get attention weights
            with torch.no_grad():
                outputs = model(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    output_attentions=True
                )
            
            # Process attention weights
            attention_weights = outputs.attentions[-1][0]  # Last layer, first batch
            tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
            
            # Calculate attention statistics
            avg_attention = attention_weights.mean(dim=0)  # Average across heads
            max_attention = attention_weights.max(dim=0)[0]  # Max across heads
            
            return {
                "tokens": tokens,
                "attention_weights": avg_attention.cpu().numpy(),
                "max_attention": max_attention.cpu().numpy(),
                "text": text,
                "num_tokens": len(tokens),
                "num_heads": attention_weights.shape[0]
            }
            
        except Exception as e:
            self.logger.error(f"Attention analysis failed: {e}")
            return {"error": f"Attention analysis failed: {str(e)}"}

# =============================================================================
# Optimized Gradio Interface
# =============================================================================

class OptimizedGradioInterface:
    """Production-ready Gradio interface with comprehensive features."""
    
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.device = device
        self.model_manager = OptimizedModelManager(device)
        self.interface_functions = OptimizedInterfaceFunctions(self.model_manager)
        self.logger = logging.getLogger(__name__)
    
    def create_interface(self) -> gr.Blocks:
        """Create optimized Gradio interface."""
        
        # Custom CSS for better styling
        css = """
        .gradio-container {
            max-width: 1200px !important;
        }
        .output-text {
            font-family: 'Courier New', monospace;
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
        }
        .error-message {
            color: #d32f2f;
            background-color: #ffebee;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #d32f2f;
        }
        .success-message {
            color: #2e7d32;
            background-color: #e8f5e8;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #2e7d32;
        }
        """
        
        with gr.Blocks(css=css, theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🤖 Optimized AI Model Interface")
            gr.Markdown("Production-ready interface for text generation, image generation, and attention analysis.")
            
            with gr.Tabs():
                # Text Generation Tab
                with gr.TabItem("📝 Text Generation"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            text_prompt = gr.Textbox(
                                label="Prompt",
                                placeholder="Enter your text prompt here...",
                                lines=3,
                                max_lines=10
                            )
                            
                            with gr.Row():
                                max_length = gr.Slider(
                                    minimum=10,
                                    maximum=2048,
                                    value=InterfaceConfig.MAX_LENGTH,
                                    step=10,
                                    label="Max Length"
                                )
                                temperature = gr.Slider(
                                    minimum=0.1,
                                    maximum=2.0,
                                    value=InterfaceConfig.DEFAULT_TEMPERATURE,
                                    step=0.1,
                                    label="Temperature"
                                )
                            
                            with gr.Row():
                                top_k = gr.Slider(
                                    minimum=1,
                                    maximum=100,
                                    value=InterfaceConfig.DEFAULT_TOP_K,
                                    step=1,
                                    label="Top-K"
                                )
                                top_p = gr.Slider(
                                    minimum=0.1,
                                    maximum=1.0,
                                    value=InterfaceConfig.DEFAULT_TOP_P,
                                    step=0.1,
                                    label="Top-P"
                                )
                            
                            do_sample = gr.Checkbox(
                                label="Use Sampling",
                                value=True
                            )
                            
                            generate_text_btn = gr.Button(
                                "Generate Text",
                                variant="primary",
                                size="lg"
                            )
                        
                        with gr.Column(scale=1):
                            text_output = gr.JSON(
                                label="Generated Text",
                                show_label=True
                            )
                            
                            text_metrics = gr.Markdown(
                                label="Generation Metrics",
                                show_label=True
                            )
                
                # Image Generation Tab
                with gr.TabItem("🎨 Image Generation"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            image_prompt = gr.Textbox(
                                label="Image Prompt",
                                placeholder="Describe the image you want to generate...",
                                lines=3
                            )
                            
                            negative_prompt = gr.Textbox(
                                label="Negative Prompt",
                                placeholder="What you don't want in the image...",
                                lines=2
                            )
                            
                            with gr.Row():
                                width = gr.Slider(
                                    minimum=64,
                                    maximum=1024,
                                    value=InterfaceConfig.DEFAULT_IMAGE_SIZE,
                                    step=64,
                                    label="Width"
                                )
                                height = gr.Slider(
                                    minimum=64,
                                    maximum=1024,
                                    value=InterfaceConfig.DEFAULT_IMAGE_SIZE,
                                    step=64,
                                    label="Height"
                                )
                            
                            with gr.Row():
                                num_steps = gr.Slider(
                                    minimum=1,
                                    maximum=100,
                                    value=InterfaceConfig.DEFAULT_INFERENCE_STEPS,
                                    step=1,
                                    label="Inference Steps"
                                )
                                guidance_scale = gr.Slider(
                                    minimum=1.0,
                                    maximum=20.0,
                                    value=InterfaceConfig.DEFAULT_GUIDANCE_SCALE,
                                    step=0.5,
                                    label="Guidance Scale"
                                )
                            
                            seed = gr.Number(
                                label="Seed (optional)",
                                placeholder="Leave empty for random"
                            )
                            
                            generate_image_btn = gr.Button(
                                "Generate Image",
                                variant="primary",
                                size="lg"
                            )
                        
                        with gr.Column(scale=1):
                            image_output = gr.Image(
                                label="Generated Image",
                                show_label=True
                            )
                            
                            image_metrics = gr.Markdown(
                                label="Generation Metrics",
                                show_label=True
                            )
                
                # Attention Analysis Tab
                with gr.TabItem("🔍 Attention Analysis"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            attention_text = gr.Textbox(
                                label="Text for Analysis",
                                placeholder="Enter text to analyze attention patterns...",
                                lines=4
                            )
                            
                            attention_max_length = gr.Slider(
                                minimum=10,
                                maximum=512,
                                value=256,
                                step=10,
                                label="Max Length"
                            )
                            
                            analyze_attention_btn = gr.Button(
                                "Analyze Attention",
                                variant="primary",
                                size="lg"
                            )
                        
                        with gr.Column(scale=1):
                            attention_output = gr.JSON(
                                label="Attention Analysis",
                                show_label=True
                            )
                            
                            attention_heatmap = gr.Plot(
                                label="Attention Heatmap",
                                show_label=True
                            )
            
            # Event handlers
            generate_text_btn.click(
                fn=self._handle_text_generation,
                inputs=[
                    text_prompt, max_length, temperature,
                    top_k, top_p, do_sample
                ],
                outputs=[text_output, text_metrics]
            )
            
            generate_image_btn.click(
                fn=self._handle_image_generation,
                inputs=[
                    image_prompt, negative_prompt, width, height,
                    num_steps, guidance_scale, seed
                ],
                outputs=[image_output, image_metrics]
            )
            
            analyze_attention_btn.click(
                fn=self._handle_attention_analysis,
                inputs=[attention_text, attention_max_length],
                outputs=[attention_output, attention_heatmap]
            )
        
        return interface
    
    def _handle_text_generation(
        self,
        prompt: str,
        max_length: int,
        temperature: float,
        top_k: int,
        top_p: float,
        do_sample: bool
    ) -> Tuple[Dict[str, Any], str]:
        """Handle text generation with error handling."""
        result = self.interface_functions.generate_text(
            prompt=prompt,
            max_length=max_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            do_sample=do_sample
        )
        
        if "error" in result:
            metrics = f"❌ **Error**: {result['error']}"
        else:
            metrics = f"""
            ✅ **Generation Successful**
            - **Generation Time**: {result['generation_time']}
            - **Parameters**: {json.dumps(result['parameters'], indent=2)}
            """
        
        return result, metrics
    
    def _handle_image_generation(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        num_steps: int,
        guidance_scale: float,
        seed: Optional[int]
    ) -> Tuple[Optional[np.ndarray], str]:
        """Handle image generation with error handling."""
        result = self.interface_functions.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_steps,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        if "error" in result:
            metrics = f"❌ **Error**: {result['error']}"
            return None, metrics
        else:
            metrics = f"""
            ✅ **Generation Successful**
            - **Generation Time**: {result['generation_time']}
            - **Parameters**: {json.dumps(result['parameters'], indent=2)}
            """
            return result["image"], metrics
    
    def _handle_attention_analysis(
        self,
        text: str,
        max_length: int
    ) -> Tuple[Dict[str, Any], Optional[Any]]:
        """Handle attention analysis with error handling."""
        result = self.interface_functions.analyze_attention(
            text=text,
            max_length=max_length
        )
        
        if "error" in result:
            return result, None
        else:
            # Create simple heatmap (you can enhance this)
            heatmap = self._create_attention_heatmap(result)
            return result, heatmap
    
    def _create_attention_heatmap(self, result: Dict[str, Any]) -> Any:
        """Create attention heatmap visualization."""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            attention_weights = result["attention_weights"]
            tokens = result["tokens"]
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                attention_weights,
                xticklabels=tokens,
                yticklabels=tokens,
                cmap="Blues",
                cbar_kws={"label": "Attention Weight"}
            )
            plt.title("Attention Heatmap")
            plt.xlabel("Key Tokens")
            plt.ylabel("Query Tokens")
            plt.xticks(rotation=45)
            plt.yticks(rotation=0)
            plt.tight_layout()
            
            return plt.gcf()
            
        except Exception as e:
            self.logger.warning(f"Failed to create heatmap: {e}")
            return None
    
    def launch(
        self,
        server_name: str = "0.0.0.0",
        server_port: int = 7860,
        share: bool = InterfaceConfig.SHARE,
        debug: bool = InterfaceConfig.DEBUG
    ):
        """Launch the optimized interface."""
        interface = self.create_interface()
        
        return interface.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            debug=debug,
            show_error=True,
            quiet=False
        )

# =============================================================================
# Usage Example
# =============================================================================

def main():
    """Example usage of optimized Gradio interface."""
    
    # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create and launch interface
        interface = OptimizedGradioInterface()
        
        print("🚀 Launching Optimized AI Interface...")
        print("📝 Text Generation: Generate text with various parameters")
        print("🎨 Image Generation: Create images from text prompts")
        print("🔍 Attention Analysis: Analyze attention patterns in text")
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False
        )
        
    except Exception as e:
        logging.error(f"Failed to launch interface: {e}")
        raise

if __name__ == "__main__":
    main()

