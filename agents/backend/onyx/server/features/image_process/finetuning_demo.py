#!/usr/bin/env python3
"""
Efficient Fine-tuning Techniques Demo

This demo showcases various parameter-efficient fine-tuning methods:
- LoRA (Low-Rank Adaptation)
- P-tuning (Prompt Tuning)
- Parameter efficiency analysis
- Performance comparison
"""

import gradio as gr
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any, List, Tuple
import logging
import time
import json

# Import fine-tuning modules
try:
    from lora_finetuning import LoRAFineTuner
    from ptuning_module import PTuningFineTuner
    FINETUNING_AVAILABLE = True
except ImportError:
    FINETUNING_AVAILABLE = False
    print("Warning: Fine-tuning modules not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockTransformerModel(nn.Module):
    """Mock transformer model for demonstration purposes."""
    
    def __init__(self, vocab_size: int = 1000, hidden_size: int = 768, 
                 num_layers: int = 6, num_heads: int = 12):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, hidden_size)
        
        # Transformer layers (simplified)
        self.transformer_layers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_size, hidden_size * 4),
                nn.GELU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_size * 4, hidden_size),
                nn.Dropout(0.1)
            ) for _ in range(num_layers)
        ])
        
        # Layer normalization
        self.layer_norms = nn.ModuleList([
            nn.LayerNorm(hidden_size) for _ in range(num_layers)
        ])
        
        # Output projection
        self.output_projection = nn.Linear(hidden_size, vocab_size)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize model weights."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                nn.init.normal_(module.weight, std=0.02)
    
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the model.
        
        Args:
            input_ids: Input token IDs
            
        Returns:
            Logits for next token prediction
        """
        # Get embeddings
        x = self.token_embedding(input_ids)
        
        # Pass through transformer layers
        for i, (layer, norm) in enumerate(zip(self.transformer_layers, self.layer_norms)):
            # Residual connection
            residual = x
            x = norm(layer(x))
            x = x + residual
        
        # Output projection
        logits = self.output_projection(x)
        
        return logits


class FineTuningDemo:
    """Main demo class for fine-tuning techniques."""
    
    def __init__(self):
        """Initialize the fine-tuning demo."""
        self.models = {}
        self.fine_tuners = {}
        self.training_stats = {}
        
        if FINETUNING_AVAILABLE:
            self._initialize_models()
    
    def _initialize_models(self):
        """Initialize different model configurations."""
        # Base model configurations
        model_configs = {
            'small': {'hidden_size': 256, 'num_layers': 4, 'num_heads': 8},
            'medium': {'hidden_size': 512, 'num_layers': 6, 'num_heads': 8},
            'large': {'hidden_size': 768, 'num_layers': 12, 'num_heads': 12}
        }
        
        for size, config in model_configs.items():
            # Create base model
            model = MockTransformerModel(
                hidden_size=config['hidden_size'],
                num_layers=config['num_layers'],
                num_heads=config['num_heads']
            )
            
            self.models[size] = model
            
            # Initialize LoRA fine-tuner
            lora_targets = ['token_embedding', 'output_projection']
            lora_fine_tuner = LoRAFineTuner(
                model=model,
                target_modules=lora_targets,
                r=16,
                alpha=32.0,
                dropout=0.1
            )
            
            # Initialize P-tuning fine-tuner
            p_tuning_config = {
                'num_virtual_tokens': 20,
                'token_dim': config['hidden_size'],
                'encoder_hidden_size': 64,
                'encoder_num_layers': 2,
                'encoder_dropout': 0.1
            }
            p_tuning_fine_tuner = PTuningFineTuner(model, p_tuning_config)
            
            # Store fine-tuners
            self.fine_tuners[f"{size}_lora"] = lora_fine_tuner
            self.fine_tuners[f"{size}_p_tuning"] = p_tuning_fine_tuner
        
        logger.info(f"Initialized {len(self.models)} models with fine-tuning capabilities")
    
    def analyze_model_efficiency(self, model_size: str, fine_tuning_method: str) -> str:
        """
        Analyze parameter efficiency of a model with fine-tuning method.
        
        Args:
            model_size: Size of the model (small, medium, large)
            fine_tuning_method: Fine-tuning method (lora, p_tuning)
            
        Returns:
            Analysis report as string
        """
        if not FINETUNING_AVAILABLE:
            return "❌ Fine-tuning modules not available"
        
        fine_tuner_key = f"{model_size}_{fine_tuning_method}"
        if fine_tuner_key not in self.fine_tuners:
            return f"❌ Fine-tuner not found: {fine_tuner_key}"
        
        fine_tuner = self.fine_tuners[fine_tuner_key]
        
        # Get parameter statistics
        if fine_tuning_method == "lora":
            stats = fine_tuner.get_parameter_stats()
        else:  # p_tuning
            stats = fine_tuner.get_parameter_stats()
        
        # Generate report
        report = f"## 📊 Parameter Efficiency Analysis\n\n"
        report += f"**Model:** {model_size.title()}\n"
        report += f"**Fine-tuning Method:** {fine_tuning_method.upper()}\n\n"
        
        report += "**Parameter Statistics:**\n"
        report += f"- Total Parameters: {stats['total_parameters']:,}\n"
        report += f"- Trainable Parameters: {stats['trainable_parameters']:,}\n"
        report += f"- Frozen Parameters: {stats['frozen_parameters']:,}\n"
        report += f"- Efficiency Ratio: {stats['efficiency_ratio']:.2%}\n"
        
        if 'compression_ratio' in stats:
            report += f"- Compression Ratio: {stats['compression_ratio']:.1f}x\n"
        
        if 'virtual_tokens' in stats:
            report += f"- Virtual Tokens: {stats['virtual_tokens']}\n"
            report += f"- Token Dimension: {stats['token_dimension']}\n"
        
        # Calculate memory savings
        memory_savings_mb = (stats['frozen_parameters'] * 4) / (1024 * 1024)
        report += f"- Memory Savings: {memory_savings_mb:.1f} MB\n"
        
        # Efficiency rating
        efficiency = stats['efficiency_ratio']
        if efficiency < 0.01:
            rating = "🟢 Excellent"
        elif efficiency < 0.05:
            rating = "🟡 Good"
        elif efficiency < 0.1:
            rating = "🟠 Fair"
        else:
            rating = "🔴 Poor"
        
        report += f"\n**Efficiency Rating:** {rating}\n"
        
        return report
    
    def compare_finetuning_methods(self, model_size: str) -> str:
        """
        Compare different fine-tuning methods for a given model size.
        
        Args:
            model_size: Size of the model to compare
            
        Returns:
            Comparison report as string
        """
        if not FINETUNING_AVAILABLE:
            return "❌ Fine-tuning modules not available"
        
        if model_size not in self.models:
            return f"❌ Model size not found: {model_size}"
        
        # Get statistics for both methods
        lora_key = f"{model_size}_lora"
        p_tuning_key = f"{model_size}_p_tuning"
        
        if lora_key not in self.fine_tuners or p_tuning_key not in self.fine_tuners:
            return f"❌ Fine-tuners not found for {model_size}"
        
        lora_stats = self.fine_tuners[lora_key].get_parameter_stats()
        p_tuning_stats = self.fine_tuners[p_tuning_key].get_parameter_stats()
        
        # Generate comparison report
        report = f"## 🔍 Fine-tuning Methods Comparison\n\n"
        report += f"**Model Size:** {model_size.title()}\n\n"
        
        report += "**LoRA (Low-Rank Adaptation):**\n"
        report += f"- Trainable Parameters: {lora_stats['trainable_parameters']:,}\n"
        report += f"- Efficiency Ratio: {lora_stats['efficiency_ratio']:.2%}\n"
        report += f"- Memory Savings: {(lora_stats['frozen_parameters'] * 4) / (1024 * 1024):.1f} MB\n\n"
        
        report += "**P-tuning (Prompt Tuning):**\n"
        report += f"- Trainable Parameters: {p_tuning_stats['trainable_parameters']:,}\n"
        report += f"- Efficiency Ratio: {p_tuning_stats['efficiency_ratio']:.2%}\n"
        report += f"- Memory Savings: {(p_tuning_stats['frozen_parameters'] * 4) / (1024 * 1024):.1f} MB\n"
        report += f"- Virtual Tokens: {p_tuning_stats['virtual_tokens']}\n\n"
        
        # Determine winner
        if lora_stats['efficiency_ratio'] < p_tuning_stats['efficiency_ratio']:
            winner = "LoRA"
            advantage = f"LoRA is {(p_tuning_stats['efficiency_ratio'] / lora_stats['efficiency_ratio']):.1f}x more efficient"
        else:
            winner = "P-tuning"
            advantage = f"P-tuning is {(lora_stats['efficiency_ratio'] / p_tuning_stats['efficiency_ratio']):.1f}x more efficient"
        
        report += f"**Winner:** 🏆 {winner}\n"
        report += f"**Advantage:** {advantage}\n"
        
        return report
    
    def demonstrate_lora_training(self, model_size: str, r_value: int, alpha_value: float) -> str:
        """
        Demonstrate LoRA training process.
        
        Args:
            model_size: Size of the model
            r_value: LoRA rank
            alpha_value: LoRA scaling factor
            
        Returns:
            Demonstration results
        """
        if not FINETUNING_AVAILABLE:
            return "❌ Fine-tuning modules not available"
        
        lora_key = f"{model_size}_lora"
        if lora_key not in self.fine_tuners:
            return f"❌ LoRA fine-tuner not found: {lora_key}"
        
        fine_tuner = self.fine_tuners[lora_key]
        
        # Update LoRA configuration
        fine_tuner.r = r_value
        fine_tuner.alpha = alpha_value
        
        # Get updated statistics
        stats = fine_tuner.get_parameter_stats()
        
        # Simulate training process
        start_time = time.time()
        
        # Mock training data
        batch_size = 8
        seq_len = 32
        vocab_size = 1000
        
        # Create mock input
        input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
        
        # Forward pass
        with torch.no_grad():
            model = fine_tuner.model
            outputs = model(input_ids)
        
        training_time = time.time() - start_time
        
        # Generate demonstration report
        report = f"## 🚀 LoRA Training Demonstration\n\n"
        report += f"**Configuration:**\n"
        report += f"- Model Size: {model_size.title()}\n"
        report += f"- LoRA Rank (r): {r_value}\n"
        report += f"- LoRA Alpha: {alpha_value}\n"
        report += f"- Scaling Factor: {alpha_value / r_value:.2f}\n\n"
        
        report += f"**Training Statistics:**\n"
        report += f"- Total Parameters: {stats['total_parameters']:,}\n"
        report += f"- Trainable Parameters: {stats['trainable_parameters']:,}\n"
        report += f"- Efficiency Ratio: {stats['efficiency_ratio']:.2%}\n"
        report += f"- Training Time: {training_time:.4f}s\n\n"
        
        report += f"**Input/Output:**\n"
        report += f"- Input Shape: {input_ids.shape}\n"
        report += f"- Output Shape: {outputs.shape}\n"
        report += f"- Batch Size: {batch_size}\n"
        report += f"- Sequence Length: {seq_len}\n"
        
        return report
    
    def demonstrate_p_tuning(self, model_size: str, num_tokens: int, encoder_layers: int) -> str:
        """
        Demonstrate P-tuning process.
        
        Args:
            model_size: Size of the model
            num_tokens: Number of virtual tokens
            encoder_layers: Number of encoder layers
            
        Returns:
            Demonstration results
        """
        if not FINETUNING_AVAILABLE:
            return "❌ Fine-tuning modules not available"
        
        p_tuning_key = f"{model_size}_p_tuning"
        if p_tuning_key not in self.fine_tuners:
            return f"❌ P-tuning fine-tuner not found: {p_tuning_key}"
        
        fine_tuner = self.fine_tuners[p_tuning_key]
        
        # Update P-tuning configuration
        fine_tuner.p_tuning_module.num_virtual_tokens = num_tokens
        fine_tuner.p_tuning_module.prompt_encoder.num_layers = encoder_layers
        
        # Get updated statistics
        stats = fine_tuner.get_parameter_stats()
        
        # Simulate P-tuning process
        start_time = time.time()
        
        # Mock input embeddings
        batch_size = 4
        seq_len = 20
        token_dim = fine_tuner.p_tuning_module.token_dim
        
        input_embeddings = torch.randn(batch_size, seq_len, token_dim)
        
        # Add prompts
        combined_embeddings = fine_tuner.add_prompts_to_input(input_embeddings)
        
        # Mock model forward pass
        with torch.no_grad():
            # Simulate model processing
            model_outputs = combined_embeddings + torch.randn_like(combined_embeddings) * 0.1
        
        # Extract prompt and content outputs
        prompt_outputs, content_outputs = fine_tuner.extract_prompt_outputs(model_outputs)
        
        processing_time = time.time() - start_time
        
        # Generate demonstration report
        report = f"## 🎯 P-tuning Demonstration\n\n"
        report += f"**Configuration:**\n"
        report += f"- Model Size: {model_size.title()}\n"
        report += f"- Virtual Tokens: {num_tokens}\n"
        report += f"- Encoder Layers: {encoder_layers}\n"
        report += f"- Token Dimension: {token_dim}\n\n"
        
        report += f"**Parameter Statistics:**\n"
        report += f"- Total Parameters: {stats['total_parameters']:,}\n"
        report += f"- Trainable Parameters: {stats['trainable_parameters']:,}\n"
        report += f"- Efficiency Ratio: {stats['efficiency_ratio']:.2%}\n"
        report += f"- Processing Time: {processing_time:.4f}s\n\n"
        
        report += f"**Input/Output Shapes:**\n"
        report += f"- Input Embeddings: {input_embeddings.shape}\n"
        report += f"- Combined Embeddings: {combined_embeddings.shape}\n"
        report += f"- Prompt Outputs: {prompt_outputs.shape}\n"
        report += f"- Content Outputs: {content_outputs.shape}\n"
        
        return report
    
    def get_available_models(self) -> str:
        """Get information about available models."""
        if not FINETUNING_AVAILABLE:
            return "❌ Fine-tuning modules not available"
        
        info = "## 🤖 Available Models and Fine-tuning Methods\n\n"
        
        for size, model in self.models.items():
            info += f"**{size.title()} Model:**\n"
            info += f"- Hidden Size: {model.hidden_size}\n"
            info += f"- Layers: {model.num_layers}\n"
            info += f"- Heads: {model.num_heads}\n"
            info += f"- Total Parameters: {sum(p.numel() for p in model.parameters()):,}\n\n"
            
            info += f"  **Fine-tuning Methods:**\n"
            
            # LoRA
            lora_key = f"{size}_lora"
            if lora_key in self.fine_tuners:
                lora_stats = self.fine_tuners[lora_key].get_parameter_stats()
                info += f"  - LoRA: {lora_stats['trainable_parameters']:,} trainable params\n"
            
            # P-tuning
            p_tuning_key = f"{size}_p_tuning"
            if p_tuning_key in self.fine_tuners:
                p_tuning_stats = self.fine_tuners[p_tuning_key].get_parameter_stats()
                info += f"  - P-tuning: {p_tuning_stats['trainable_parameters']:,} trainable params\n"
            
            info += "\n"
        
        return info


def create_finetuning_demo_interface():
    """Create the Gradio interface for the fine-tuning demo."""
    
    demo = FineTuningDemo()
    
    with gr.Blocks(title="Efficient Fine-tuning Techniques Demo", 
                   theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("# 🚀 Efficient Fine-tuning Techniques Demo")
        gr.Markdown("Explore parameter-efficient fine-tuning methods: LoRA, P-tuning, and more")
        
        with gr.Tabs():
            with gr.Tab("Parameter Efficiency Analysis"):
                with gr.Row():
                    with gr.Column(scale=1):
                        model_size_dropdown = gr.Dropdown(
                            choices=["small", "medium", "large"],
                            value="medium",
                            label="Model Size"
                        )
                        method_dropdown = gr.Dropdown(
                            choices=["lora", "p_tuning"],
                            value="lora",
                            label="Fine-tuning Method"
                        )
                        analyze_button = gr.Button("Analyze Efficiency", variant="primary")
                    
                    with gr.Column(scale=1):
                        efficiency_report = gr.Markdown(label="Efficiency Analysis")
                
                analyze_button.click(
                    fn=demo.analyze_model_efficiency,
                    inputs=[model_size_dropdown, method_dropdown],
                    outputs=efficiency_report
                )
            
            with gr.Tab("Method Comparison"):
                with gr.Row():
                    with gr.Column(scale=1):
                        comp_model_size = gr.Dropdown(
                            choices=["small", "medium", "large"],
                            value="medium",
                            label="Model Size to Compare"
                        )
                        compare_button = gr.Button("Compare Methods", variant="primary")
                    
                    with gr.Column(scale=1):
                        comparison_report = gr.Markdown(label="Method Comparison")
                
                compare_button.click(
                    fn=demo.compare_finetuning_methods,
                    inputs=[comp_model_size],
                    outputs=comparison_report
                )
            
            with gr.Tab("LoRA Demonstration"):
                with gr.Row():
                    with gr.Column(scale=1):
                        lora_model_size = gr.Dropdown(
                            choices=["small", "medium", "large"],
                            value="medium",
                            label="Model Size"
                        )
                        r_slider = gr.Slider(
                            minimum=4, maximum=64, value=16, step=4,
                            label="LoRA Rank (r)"
                        )
                        alpha_slider = gr.Slider(
                            minimum=8, maximum=128, value=32, step=8,
                            label="LoRA Alpha"
                        )
                        lora_demo_button = gr.Button("Demonstrate LoRA", variant="primary")
                    
                    with gr.Column(scale=1):
                        lora_demo_report = gr.Markdown(label="LoRA Demonstration")
                
                lora_demo_button.click(
                    fn=demo.demonstrate_lora_training,
                    inputs=[lora_model_size, r_slider, alpha_slider],
                    outputs=lora_demo_report
                )
            
            with gr.Tab("P-tuning Demonstration"):
                with gr.Row():
                    with gr.Column(scale=1):
                        pt_model_size = gr.Dropdown(
                            choices=["small", "medium", "large"],
                            value="medium",
                            label="Model Size"
                        )
                        num_tokens_slider = gr.Slider(
                            minimum=5, maximum=50, value=20, step=5,
                            label="Number of Virtual Tokens"
                        )
                        encoder_layers_slider = gr.Slider(
                            minimum=1, maximum=4, value=2, step=1,
                            label="Encoder Layers"
                        )
                        pt_demo_button = gr.Button("Demonstrate P-tuning", variant="primary")
                    
                    with gr.Column(scale=1):
                        pt_demo_report = gr.Markdown(label="P-tuning Demonstration")
                
                pt_demo_button.click(
                    fn=demo.demonstrate_p_tuning,
                    inputs=[pt_model_size, num_tokens_slider, encoder_layers_slider],
                    outputs=pt_demo_report
                )
            
            with gr.Tab("Model Information"):
                with gr.Row():
                    with gr.Column():
                        info_button = gr.Button("Show Model Info", variant="secondary")
                        model_info = gr.Markdown(label="Model Information")
                
                info_button.click(
                    fn=demo.get_available_models,
                    outputs=model_info
                )
        
        gr.Markdown("---")
        gr.Markdown("*Efficient Fine-tuning Techniques: LoRA, P-tuning, and Parameter Efficiency*")
    
    return interface


def main():
    """Main function to launch the fine-tuning demo."""
    try:
        interface = create_finetuning_demo_interface()
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7862,  # Different port to avoid conflicts
            share=False,
            debug=False,
            show_error=True,
            quiet=False
        )
        
    except Exception as error:
        logger.error(f"Failed to launch fine-tuning demo: {error}")
        raise


if __name__ == "__main__":
    main()


