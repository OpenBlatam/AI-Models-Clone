#!/usr/bin/env python3
"""
Advanced Gradient Accumulation Demo

This demo showcases the enhanced gradient accumulation system with:
- Adaptive accumulation strategies
- Advanced memory monitoring
- Performance optimization
- Real-time visualization
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import gradio as gr
import logging
import time
from typing import Dict, List, Tuple
import json

from advanced_gradient_accumulation import (
    AdvancedGradientConfig, 
    AdvancedTrainer, 
    create_advanced_config,
    create_experimental_config,
    gradient_accumulation_context
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedDemoModel(nn.Module):
    """Advanced model for demonstration."""
    
    def __init__(self, input_size: int = 100, hidden_size: int = 256, num_classes: int = 10):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, num_classes)
        )
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
    
    def forward(self, x):
        return self.layers(x)

class AdvancedGradientDemo:
    """Advanced gradient accumulation demonstration."""
    
    def __init__(self):
        self.results = {}
        self.training_history = {}
        
    def create_synthetic_dataset(self, num_samples: int = 1000, input_size: int = 100) -> Tuple[torch.Tensor, torch.Tensor]:
        """Create synthetic dataset for demonstration."""
        X = torch.randn(num_samples, input_size)
        y = torch.randint(0, 10, (num_samples,))
        return X, y
    
    def train_with_advanced_config(self, config: AdvancedGradientConfig, num_steps: int = 100) -> Dict:
        """Train with advanced gradient accumulation configuration."""
        print(f"🚀 Training with advanced configuration:")
        print(f"   - Batch size: {config.batch_size}")
        print(f"   - Effective batch size: {config.effective_batch_size}")
        print(f"   - Adaptive accumulation: {config.adaptive_accumulation}")
        print(f"   - Mixed precision: {config.use_mixed_precision}")
        print(f"   - Memory efficient: {config.memory_efficient}")
        
        # Create model and dataset
        model = AdvancedDemoModel()
        X, y = self.create_synthetic_dataset()
        
        # Training loop
        training_metrics = []
        start_time = time.time()
        
        with gradient_accumulation_context(model, config) as trainer:
            for step in range(num_steps):
                # Create batch
                batch_indices = torch.randint(0, len(X), (config.batch_size,))
                batch_X = X[batch_indices]
                batch_y = y[batch_indices]
                
                # Training step
                metrics = trainer.train_step(batch_X, batch_y)
                training_metrics.append(metrics)
                
                # Progress update
                if step % 20 == 0:
                    print(f"Step {step}: Loss = {metrics['loss']:.4f}, "
                          f"Memory = {metrics['memory_utilization']:.2%}, "
                          f"Accumulation Steps = {metrics['accumulation_steps']}")
        
        training_time = time.time() - start_time
        
        # Get performance summary
        summary = trainer.get_performance_summary()
        summary['training_time'] = training_time
        summary['total_steps'] = num_steps
        
        return {
            'config': config,
            'training_metrics': training_metrics,
            'performance_summary': summary,
            'model': model
        }
    
    def compare_advanced_configs(self, num_steps: int = 100) -> Dict:
        """Compare different advanced configurations."""
        print("🔬 Comparing advanced gradient accumulation configurations...")
        
        configs = {
            'baseline': create_advanced_config(
                batch_size=8, effective_batch_size=32, adaptive=False, mixed_precision=False, advanced_features=False
            ),
            'mixed_precision': create_advanced_config(
                batch_size=8, effective_batch_size=32, adaptive=False, mixed_precision=True, advanced_features=False
            ),
            'adaptive': create_advanced_config(
                batch_size=8, effective_batch_size=32, adaptive=True, mixed_precision=True, advanced_features=True
            ),
            'memory_efficient': create_advanced_config(
                batch_size=4, effective_batch_size=32, adaptive=True, mixed_precision=True, memory_efficient=True, advanced_features=True
            ),
            'large_batch': create_advanced_config(
                batch_size=16, effective_batch_size=128, adaptive=True, mixed_precision=True, advanced_features=True
            ),
            'experimental': create_experimental_config(
                batch_size=8, effective_batch_size=64, noise_scale=1e-5
            )
        }
        
        results = {}
        for name, config in configs.items():
            print(f"\n📊 Testing {name} configuration...")
            result = self.train_with_advanced_config(config, num_steps)
            results[name] = result
        
        self.results = results
        return results
    
    def generate_advanced_plots(self) -> Tuple[plt.Figure, plt.Figure, plt.Figure]:
        """Generate advanced visualization plots."""
        if not self.results:
            return None, None, None
        
        # Create subplots
        fig1, axes1 = plt.subplots(2, 2, figsize=(15, 12))
        fig2, axes2 = plt.subplots(2, 2, figsize=(15, 12))
        fig3, axes3 = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Loss curves
        for name, result in self.results.items():
            losses = [m['loss'] for m in result['training_metrics']]
            axes1[0, 0].plot(losses, label=name, alpha=0.8)
        axes1[0, 0].set_title('Training Loss')
        axes1[0, 0].set_xlabel('Step')
        axes1[0, 0].set_ylabel('Loss')
        axes1[0, 0].legend()
        axes1[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Memory utilization
        for name, result in self.results.items():
            memory_util = [m['memory_utilization'] for m in result['training_metrics']]
            axes1[0, 1].plot(memory_util, label=name, alpha=0.8)
        axes1[0, 1].set_title('Memory Utilization')
        axes1[0, 1].set_xlabel('Step')
        axes1[0, 1].set_ylabel('Memory Utilization')
        axes1[0, 1].legend()
        axes1[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Gradient norms
        for name, result in self.results.items():
            grad_norms = [m['grad_norm'] for m in result['training_metrics']]
            axes1[1, 0].plot(grad_norms, label=name, alpha=0.8)
        axes1[1, 0].set_title('Gradient Norms')
        axes1[1, 0].set_xlabel('Step')
        axes1[1, 0].set_ylabel('Gradient Norm')
        axes1[1, 0].legend()
        axes1[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Step times
        for name, result in self.results.items():
            step_times = [m['step_time'] for m in result['training_metrics']]
            axes1[1, 1].plot(step_times, label=name, alpha=0.8)
        axes1[1, 1].set_title('Step Times')
        axes1[1, 1].set_xlabel('Step')
        axes1[1, 1].set_ylabel('Time (s)')
        axes1[1, 1].legend()
        axes1[1, 1].grid(True, alpha=0.3)
        
        # Plot 5: Performance comparison
        config_names = list(self.results.keys())
        avg_losses = [np.mean([m['loss'] for m in result['training_metrics']]) for result in self.results.values()]
        avg_memory = [np.mean([m['memory_utilization'] for m in result['training_metrics']]) for result in self.results.values()]
        training_times = [result['performance_summary']['training_time'] for result in self.results.values()]
        avg_step_times = [result['performance_summary']['avg_step_time'] for result in self.results.values()]
        
        # Performance metrics
        axes2[0, 0].bar(config_names, avg_losses, alpha=0.8)
        axes2[0, 0].set_title('Average Loss')
        axes2[0, 0].set_ylabel('Loss')
        axes2[0, 0].tick_params(axis='x', rotation=45)
        
        axes2[0, 1].bar(config_names, avg_memory, alpha=0.8)
        axes2[0, 1].set_title('Average Memory Utilization')
        axes2[0, 1].set_ylabel('Memory Utilization')
        axes2[0, 1].tick_params(axis='x', rotation=45)
        
        axes2[1, 0].bar(config_names, training_times, alpha=0.8)
        axes2[1, 0].set_title('Total Training Time')
        axes2[1, 0].set_ylabel('Time (s)')
        axes2[1, 0].tick_params(axis='x', rotation=45)
        
        axes2[1, 1].bar(config_names, avg_step_times, alpha=0.8)
        axes2[1, 1].set_title('Average Step Time')
        axes2[1, 1].set_ylabel('Time (s)')
        axes2[1, 1].tick_params(axis='x', rotation=45)
        
        # Plot 6: Memory efficiency analysis
        memory_efficiency = []
        for name, result in self.results.items():
            config = result['config']
            efficiency = config.effective_batch_size / config.batch_size
            memory_efficiency.append(efficiency)
        
        axes3[0].bar(config_names, memory_efficiency, alpha=0.8)
        axes3[0].set_title('Memory Efficiency (Effective Batch / Actual Batch)')
        axes3[0].set_ylabel('Efficiency Ratio')
        axes3[0].tick_params(axis='x', rotation=45)
        
        # Plot 7: Adaptive accumulation analysis
        adaptive_steps = []
        for name, result in self.results.items():
            if result['config'].adaptive_accumulation:
                steps_history = [m['accumulation_steps'] for m in result['training_metrics']]
                adaptive_steps.append(np.mean(steps_history))
            else:
                adaptive_steps.append(result['config'].gradient_accumulation_steps)
        
        axes3[1].bar(config_names, adaptive_steps, alpha=0.8)
        axes3[1].set_title('Average Accumulation Steps')
        axes3[1].set_ylabel('Steps')
        axes3[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig1, fig2, fig3
    
    def get_advanced_analysis(self) -> str:
        """Generate advanced analysis report."""
        if not self.results:
            return "No results available. Please run the comparison first."
        
        analysis = "🔬 Advanced Gradient Accumulation Analysis\n"
        analysis += "=" * 50 + "\n\n"
        
        # Performance comparison
        analysis += "📊 Performance Comparison:\n"
        analysis += "-" * 30 + "\n"
        
        best_loss = float('inf')
        best_memory = float('inf')
        best_time = float('inf')
        best_config = None
        
        for name, result in self.results.items():
            summary = result['performance_summary']
            avg_loss = summary.get('avg_loss', 0.0)
            avg_memory = summary.get('memory_utilization', 0.0)
            training_time = summary.get('training_time', 0.0)
            
            analysis += f"\n{name.upper()}:\n"
            analysis += f"  - Average Loss: {avg_loss:.4f}\n"
            analysis += f"  - Memory Utilization: {avg_memory:.2%}\n"
            analysis += f"  - Training Time: {training_time:.2f}s\n"
            analysis += f"  - Effective Batch Size: {result['config'].effective_batch_size}\n"
            analysis += f"  - Adaptive: {result['config'].adaptive_accumulation}\n"
            analysis += f"  - Mixed Precision: {result['config'].use_mixed_precision}\n"
            
            # Track best performance
            if avg_loss < best_loss:
                best_loss = avg_loss
                best_config = name
        
        analysis += f"\n🏆 Best Configuration: {best_config.upper()}\n"
        analysis += f"   - Lowest Loss: {best_loss:.4f}\n"
        
        # Memory efficiency analysis
        analysis += "\n💾 Memory Efficiency Analysis:\n"
        analysis += "-" * 35 + "\n"
        
        for name, result in self.results.items():
            config = result['config']
            efficiency = config.effective_batch_size / config.batch_size
            analysis += f"{name}: {efficiency:.1f}x memory efficiency\n"
        
        # Recommendations
        analysis += "\n💡 Recommendations:\n"
        analysis += "-" * 20 + "\n"
        
        for name, result in self.results.items():
            if 'recommendations' in result['performance_summary']:
                recs = result['performance_summary']['recommendations']
                if recs:
                    analysis += f"\n{name}:\n"
                    for rec in recs:
                        analysis += f"  - {rec}\n"
        
        return analysis
    
    def create_advanced_gradio_interface(self):
        """Create advanced Gradio interface."""
        with gr.Blocks(title="Advanced Gradient Accumulation Demo") as demo:
            gr.Markdown("# 🚀 Advanced Gradient Accumulation Demo")
            gr.Markdown("""
            This demo showcases advanced gradient accumulation features:
            - **Adaptive Accumulation**: Automatically adjusts accumulation steps based on memory pressure
            - **Advanced Memory Monitoring**: Real-time memory usage tracking and optimization
            - **Performance Optimization**: Mixed precision, model compilation, and efficient optimizers
            - **Comprehensive Analysis**: Detailed performance metrics and recommendations
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Configuration")
                    num_steps = gr.Slider(
                        minimum=50, maximum=500, value=100, step=50,
                        label="Number of Training Steps"
                    )
                    run_comparison_btn = gr.Button("🔬 Run Advanced Comparison", variant="primary")
                    run_single_btn = gr.Button("🎯 Run Single Configuration", variant="secondary")
                    
                    # Single configuration options
                    with gr.Accordion("Single Configuration Options", open=False):
                        batch_size = gr.Slider(2, 32, 8, step=2, label="Batch Size")
                        effective_batch_size = gr.Slider(8, 256, 32, step=8, label="Effective Batch Size")
                        adaptive = gr.Checkbox(True, label="Adaptive Accumulation")
                        mixed_precision = gr.Checkbox(True, label="Mixed Precision")
                        memory_efficient = gr.Checkbox(True, label="Memory Efficient")
                
                with gr.Column():
                    gr.Markdown("## Results")
                    output_text = gr.Textbox(
                        label="Analysis Results",
                        lines=15,
                        max_lines=30
                    )
            
            with gr.Row():
                gr.Markdown("## Performance Visualization")
            
            with gr.Row():
                plot1 = gr.Image(label="Training Metrics")
                plot2 = gr.Image(label="Performance Comparison")
            
            with gr.Row():
                plot3 = gr.Image(label="Memory & Efficiency Analysis")
            
            # Event handlers
            def run_comparison(steps):
                results = self.compare_advanced_configs(steps)
                analysis = self.get_advanced_analysis()
                fig1, fig2, fig3 = self.generate_advanced_plots()
                
                return (
                    analysis,
                    fig1,
                    fig2,
                    fig3
                )
            
            def run_single_config(steps, batch, effective, adaptive, mixed, memory):
                config = create_advanced_config(
                    batch_size=batch,
                    effective_batch_size=effective,
                    adaptive=adaptive,
                    mixed_precision=mixed,
                    memory_efficient=memory
                )
                
                result = self.train_with_advanced_config(config, steps)
                self.results = {'single': result}
                
                analysis = self.get_advanced_analysis()
                fig1, fig2, fig3 = self.generate_advanced_plots()
                
                return (
                    analysis,
                    fig1,
                    fig2,
                    fig3
                )
            
            run_comparison_btn.click(
                fn=run_comparison,
                inputs=[num_steps],
                outputs=[output_text, plot1, plot2, plot3]
            )
            
            run_single_btn.click(
                fn=run_single_config,
                inputs=[num_steps, batch_size, effective_batch_size, adaptive, mixed_precision, memory_efficient],
                outputs=[output_text, plot1, plot2, plot3]
            )
        
        return demo

def main():
    """Main function to run the advanced demo."""
    print("🚀 Advanced Gradient Accumulation Demo")
    print("=" * 50)
    
    demo = AdvancedGradientDemo()
    
    # Run comparison
    print("Running advanced configuration comparison...")
    results = demo.compare_advanced_configs(num_steps=100)
    
    # Generate analysis
    analysis = demo.get_advanced_analysis()
    print("\n" + analysis)
    
    # Generate plots
    fig1, fig2, fig3 = demo.generate_advanced_plots()
    
    # Save plots
    if fig1:
        fig1.savefig('advanced_training_metrics.png', dpi=300, bbox_inches='tight')
        print("✅ Saved training metrics plot")
    
    if fig2:
        fig2.savefig('advanced_performance_comparison.png', dpi=300, bbox_inches='tight')
        print("✅ Saved performance comparison plot")
    
    if fig3:
        fig3.savefig('advanced_memory_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Saved memory analysis plot")
    
    # Launch Gradio interface
    print("\n🎯 Launching Gradio interface...")
    interface = demo.create_advanced_gradio_interface()
    interface.launch(share=True)

if __name__ == "__main__":
    main()
