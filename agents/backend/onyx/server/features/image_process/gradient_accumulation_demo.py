#!/usr/bin/env python3
"""
Gradient Accumulation Demo for Large Batch Sizes

This demo showcases how to use gradient accumulation to train diffusion models
with large effective batch sizes while maintaining memory efficiency.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import time
from typing import Dict, List, Tuple
import gradio as gr

# Import our diffusion system
from advanced_diffusion_system import (
    DiffusionConfig, DiffusionModel, DiffusionTrainer, 
    NoiseScheduler, UNet, Autoencoder
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GradientAccumulationDemo:
    """Demo class for gradient accumulation in diffusion models."""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self.trainers = {}
        self.configs = {}
        
    def create_training_configs(self) -> Dict[str, DiffusionConfig]:
        """Create different training configurations for comparison."""
        configs = {}
        
        # Small batch size (baseline)
        configs["small_batch"] = DiffusionConfig(
            model_type="unet",
            image_size=32,
            hidden_size=64,
            num_layers=3,
            num_timesteps=100,
            batch_size=8,
            gradient_accumulation_steps=1,
            effective_batch_size=8,
            learning_rate=1e-4
        )
        
        # Medium batch size with gradient accumulation
        configs["medium_batch"] = DiffusionConfig(
            model_type="unet",
            image_size=32,
            hidden_size=64,
            num_layers=3,
            num_timesteps=100,
            batch_size=8,
            gradient_accumulation_steps=4,
            effective_batch_size=32,
            learning_rate=1e-4
        )
        
        # Large batch size with gradient accumulation
        configs["large_batch"] = DiffusionConfig(
            model_type="unet",
            image_size=32,
            hidden_size=64,
            num_layers=3,
            num_timesteps=100,
            batch_size=8,
            gradient_accumulation_steps=16,
            effective_batch_size=128,
            learning_rate=1e-4
        )
        
        # Very large batch size with gradient accumulation
        configs["xlarge_batch"] = DiffusionConfig(
            model_type="unet",
            image_size=32,
            hidden_size=64,
            num_layers=3,
            num_timesteps=100,
            batch_size=8,
            gradient_accumulation_steps=32,
            effective_batch_size=256,
            learning_rate=1e-4
        )
        
        return configs
    
    def create_synthetic_dataset(self, num_samples: int = 1000, image_size: int = 32) -> DataLoader:
        """Create synthetic dataset for training demonstration."""
        # Generate synthetic images (random noise for demo purposes)
        images = torch.randn(num_samples, 3, image_size, image_size)
        images = torch.clamp(images, -1, 1)  # Normalize to [-1, 1]
        
        dataset = TensorDataset(images)
        dataloader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=0)
        
        return dataloader
    
    def train_with_config(self, config_name: str, num_epochs: int = 2) -> Dict[str, List[float]]:
        """Train a model with specific configuration."""
        if config_name not in self.configs:
            raise ValueError(f"Unknown config: {config_name}")
        
        config = self.configs[config_name]
        
        # Create model
        model = DiffusionModel(config)
        model.to(self.device)
        
        # Create trainer
        trainer = DiffusionTrainer(model, config)
        
        # Create dataset
        dataloader = self.create_synthetic_dataset()
        
        # Store references
        self.models[config_name] = model
        self.trainers[config_name] = trainer
        self.configs[config_name] = config
        
        # Training
        logger.info(f"Training with config: {config_name}")
        logger.info(f"Effective batch size: {trainer.get_effective_batch_size()}")
        logger.info(f"Gradient accumulation steps: {trainer.gradient_accumulation_steps}")
        
        start_time = time.time()
        results = trainer.train(dataloader, num_epochs)
        training_time = time.time() - start_time
        
        # Add training time to results
        results["training_time"] = training_time
        results["config_name"] = config_name
        
        return results
    
    def compare_training_configs(self, num_epochs: int = 2) -> Dict[str, Dict]:
        """Compare different training configurations."""
        results = {}
        
        for config_name in self.configs.keys():
            try:
                logger.info(f"Training with {config_name} configuration...")
                result = self.train_with_config(config_name, num_epochs)
                results[config_name] = result
                
                # Memory usage
                trainer = self.trainers[config_name]
                memory_info = trainer.get_memory_usage()
                results[config_name]["memory_info"] = memory_info
                
            except Exception as e:
                logger.error(f"Error training with {config_name}: {e}")
                results[config_name] = {"error": str(e)}
        
        return results
    
    def generate_comparison_plot(self, results: Dict[str, Dict]) -> str:
        """Generate comparison plot for different configurations."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Loss comparison
        for config_name, result in results.items():
            if "losses" in result and "error" not in result:
                ax1.plot(result["losses"], label=f"{config_name} (batch={result.get('effective_batch_size', 'N/A')})")
        
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Loss")
        ax1.set_title("Training Loss Comparison")
        ax1.legend()
        ax1.grid(True)
        
        # Training time comparison
        config_names = []
        training_times = []
        effective_batch_sizes = []
        
        for config_name, result in results.items():
            if "training_time" in result and "error" not in result:
                config_names.append(config_name)
                training_times.append(result["training_time"])
                effective_batch_sizes.append(result.get("effective_batch_size", 0))
        
        if config_names:
            bars = ax2.bar(config_names, training_times)
            ax2.set_xlabel("Configuration")
            ax2.set_ylabel("Training Time (seconds)")
            ax2.set_title("Training Time Comparison")
            
            # Add batch size labels on bars
            for bar, batch_size in zip(bars, effective_batch_sizes):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'batch={batch_size}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save plot
        plot_path = "gradient_accumulation_comparison.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def get_memory_efficiency_analysis(self) -> Dict[str, float]:
        """Analyze memory efficiency of different configurations."""
        analysis = {}
        
        for config_name, trainer in self.trainers.items():
            memory_info = trainer.get_memory_usage()
            
            if "gpu_memory_allocated" in memory_info:
                memory_gb = memory_info["gpu_memory_allocated"]
                effective_batch = trainer.get_effective_batch_size()
                
                # Memory efficiency: samples per GB of memory
                memory_efficiency = effective_batch / memory_gb if memory_gb > 0 else 0
                
                analysis[config_name] = {
                    "memory_gb": memory_gb,
                    "effective_batch_size": effective_batch,
                    "memory_efficiency": memory_efficiency,
                    "gradient_steps": trainer.gradient_accumulation_steps
                }
        
        return analysis
    
    def create_gradio_interface(self):
        """Create Gradio interface for the demo."""
        with gr.Blocks(title="Gradient Accumulation Demo") as demo:
            gr.Markdown("# 🚀 Gradient Accumulation Demo for Large Batch Sizes")
            gr.Markdown("This demo showcases how gradient accumulation enables training with large effective batch sizes while maintaining memory efficiency.")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Configuration")
                    config_selector = gr.Dropdown(
                        choices=list(self.configs.keys()),
                        value="medium_batch",
                        label="Training Configuration"
                    )
                    
                    num_epochs = gr.Slider(
                        minimum=1, maximum=5, value=2, step=1,
                        label="Number of Epochs"
                    )
                    
                    train_btn = gr.Button("🚀 Train Model", variant="primary")
                    
                    with gr.Row():
                        compare_btn = gr.Button("📊 Compare All Configs", variant="secondary")
                        analyze_btn = gr.Button("💾 Memory Analysis", variant="secondary")
                
                with gr.Column():
                    gr.Markdown("## Results")
                    output_text = gr.Textbox(
                        label="Training Output",
                        lines=10,
                        max_lines=20
                    )
                    
                    plot_output = gr.Image(label="Comparison Plot")
            
            # Training button
            train_btn.click(
                fn=self.train_single_config,
                inputs=[config_selector, num_epochs],
                outputs=[output_text]
            )
            
            # Compare button
            compare_btn.click(
                fn=self.run_comparison,
                inputs=[num_epochs],
                outputs=[output_text, plot_output]
            )
            
            # Analyze button
            analyze_btn.click(
                fn=self.run_memory_analysis,
                inputs=[],
                outputs=[output_text]
            )
        
        return demo
    
    def train_single_config(self, config_name: str, num_epochs: int) -> str:
        """Train a single configuration and return results as string."""
        try:
            result = self.train_with_config(config_name, num_epochs)
            
            output = f"✅ Training completed for {config_name}!\n\n"
            output += f"Configuration:\n"
            output += f"- Effective batch size: {result.get('effective_batch_size', 'N/A')}\n"
            output += f"- Gradient accumulation steps: {result.get('gradient_accumulation_steps', 'N/A')}\n"
            output += f"- Training time: {result.get('training_time', 0):.2f} seconds\n"
            output += f"- Final loss: {result.get('losses', [0])[-1]:.4f}\n"
            
            # Memory info
            if config_name in self.trainers:
                memory_info = self.trainers[config_name].get_memory_usage()
                output += f"\nMemory Usage:\n"
                for key, value in memory_info.items():
                    if isinstance(value, float):
                        output += f"- {key}: {value:.2f} GB\n"
                    else:
                        output += f"- {key}: {value}\n"
            
            return output
            
        except Exception as e:
            return f"❌ Error training {config_name}: {str(e)}"
    
    def run_comparison(self, num_epochs: int) -> Tuple[str, str]:
        """Run comparison of all configurations."""
        try:
            results = self.compare_training_configs(num_epochs)
            plot_path = self.generate_comparison_plot(results)
            
            output = "📊 Comparison Results:\n\n"
            
            for config_name, result in results.items():
                if "error" not in result:
                    output += f"🔹 {config_name}:\n"
                    output += f"   - Effective batch size: {result.get('effective_batch_size', 'N/A')}\n"
                    output += f"   - Training time: {result.get('training_time', 0):.2f}s\n"
                    output += f"   - Final loss: {result.get('losses', [0])[-1]:.4f}\n"
                    output += f"   - Memory: {result.get('memory_info', {}).get('gpu_memory_allocated', 'N/A')} GB\n\n"
                else:
                    output += f"❌ {config_name}: {result['error']}\n\n"
            
            return output, plot_path
            
        except Exception as e:
            return f"❌ Error in comparison: {str(e)}", None
    
    def run_memory_analysis(self) -> str:
        """Run memory efficiency analysis."""
        try:
            analysis = self.get_memory_efficiency_analysis()
            
            output = "💾 Memory Efficiency Analysis:\n\n"
            
            for config_name, data in analysis.items():
                output += f"🔹 {config_name}:\n"
                output += f"   - Memory used: {data['memory_gb']:.2f} GB\n"
                output += f"   - Effective batch size: {data['effective_batch_size']}\n"
                output += f"   - Memory efficiency: {data['memory_efficiency']:.1f} samples/GB\n"
                output += f"   - Gradient accumulation steps: {data['gradient_steps']}\n\n"
            
            # Find most efficient configuration
            if analysis:
                most_efficient = max(analysis.items(), key=lambda x: x[1]['memory_efficiency'])
                output += f"🏆 Most memory efficient: {most_efficient[0]} "
                output += f"({most_efficient[1]['memory_efficiency']:.1f} samples/GB)\n"
            
            return output
            
        except Exception as e:
            return f"❌ Error in memory analysis: {str(e)}"


def main():
    """Main function to run the demo."""
    print("🚀 Starting Gradient Accumulation Demo...")
    
    # Create demo instance
    demo = GradientAccumulationDemo()
    
    # Create configurations
    demo.configs = demo.create_training_configs()
    
    print(f"Created {len(demo.configs)} training configurations:")
    for name, config in demo.configs.items():
        print(f"  - {name}: batch_size={config.batch_size}, "
              f"accumulation_steps={config.gradient_accumulation_steps}, "
              f"effective_batch_size={config.effective_batch_size}")
    
    # Create Gradio interface
    interface = demo.create_gradio_interface()
    
    # Launch
    print("🎯 Launching Gradio interface...")
    interface.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=True,
        show_error=True
    )


if __name__ == "__main__":
    main()
