#!/usr/bin/env python3
"""
Refactored Advanced Gradient Accumulation Demo

This demo showcases the refactored system with:
- Clean architecture and separation of concerns
- Strategy pattern for memory management
- Improved performance monitoring
- Better error handling and logging
- Production-ready optimizations
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import gradio as gr
import logging
import time
from typing import Dict, List, Tuple, Any
import json
from pathlib import Path

from advanced_gradient_accumulation_refactored import (
    AdvancedGradientConfig, 
    RefactoredTrainer, 
    create_refactored_config,
    create_experimental_refactored_config,
    refactored_gradient_accumulation_context,
    MemoryConfig,
    PerformanceConfig
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RefactoredDemoModel(nn.Module):
    """Refactored model for demonstration with improved architecture."""
    
    def __init__(self, input_size: int = 100, hidden_size: int = 256, num_classes: int = 10):
        super().__init__()
        
        # Improved layer architecture
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.BatchNorm1d(hidden_size)
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.BatchNorm1d(hidden_size // 2),
            nn.Linear(hidden_size // 2, num_classes)
        )
        
        # Initialize weights with improved method
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Improved weight initialization."""
        if isinstance(module, nn.Linear):
            nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)
        elif isinstance(module, nn.BatchNorm1d):
            nn.init.constant_(module.weight, 1)
            nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        features = self.feature_extractor(x)
        return self.classifier(features)

class RefactoredGradientDemo:
    """Refactored gradient accumulation demonstration with improved architecture."""
    
    def __init__(self):
        self.results = {}
        self.training_history = {}
        self.performance_analysis = {}
        
    def create_synthetic_dataset(self, num_samples: int = 1000, input_size: int = 100) -> Tuple[torch.Tensor, torch.Tensor]:
        """Create synthetic dataset with improved data generation."""
        # Generate more realistic synthetic data
        X = torch.randn(num_samples, input_size)
        # Add some structure to the data
        X[:, :input_size//4] *= 2.0  # Scale first quarter
        X[:, input_size//4:input_size//2] += 1.0  # Add bias to second quarter
        
        # Generate correlated labels
        y = torch.randint(0, 10, (num_samples,))
        # Make some labels correlated with input features
        y = (y + (X[:, 0] > 0).long()) % 10
        
        return X, y
    
    def train_with_refactored_config(self, config: AdvancedGradientConfig, num_steps: int = 100) -> Dict:
        """Train with refactored gradient accumulation configuration."""
        print(f"🚀 Training with refactored configuration:")
        print(f"   - Batch size: {config.batch_size}")
        print(f"   - Effective batch size: {config.effective_batch_size}")
        print(f"   - Adaptive accumulation: {config.performance.enable_adaptive_accumulation}")
        print(f"   - Mixed precision: {config.performance.enable_mixed_precision}")
        print(f"   - Memory efficient: {config.memory.enable_auto_cleanup}")
        print(f"   - Advanced profiling: {config.memory.enable_advanced_profiling}")
        
        # Create model and dataset
        model = RefactoredDemoModel()
        X, y = self.create_synthetic_dataset()
        
        # Training loop with improved monitoring
        training_metrics = []
        memory_snapshots = []
        start_time = time.time()
        
        with refactored_gradient_accumulation_context(model, config) as trainer:
            for step in range(num_steps):
                # Create batch
                batch_indices = torch.randint(0, len(X), (config.batch_size,))
                batch_X = X[batch_indices]
                batch_y = y[batch_indices]
                
                # Training step
                metrics = trainer.train_step(batch_X, batch_y)
                training_metrics.append(metrics)
                
                # Memory snapshot
                if step % config.profile_interval == 0:
                    snapshot = trainer.gradient_accumulator.memory_manager.take_snapshot(
                        step, f"Training step {step}"
                    )
                    memory_snapshots.append(snapshot)
                
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
        summary['memory_snapshots'] = memory_snapshots
        
        return {
            'config': config,
            'training_metrics': training_metrics,
            'performance_summary': summary,
            'model': model,
            'memory_analysis': self._analyze_memory_usage(memory_snapshots)
        }
    
    def _analyze_memory_usage(self, snapshots: List[Dict]) -> Dict[str, Any]:
        """Analyze memory usage patterns from snapshots."""
        if not snapshots:
            return {}
        
        analysis = {
            'total_snapshots': len(snapshots),
            'optimization_count': snapshots[-1].get('optimization_counter', 0),
            'memory_trends': {},
            'peak_usage': {},
            'efficiency_score': 0.0
        }
        
        # Analyze GPU memory trends
        gpu_memory_values = []
        for snapshot in snapshots:
            if 'memory_status' in snapshot and 'gpu' in snapshot['memory_status']:
                gpu_status = snapshot['memory_status']['gpu']
                if gpu_status and 'utilization' in gpu_status:
                    gpu_memory_values.append(gpu_status['utilization'])
        
        if gpu_memory_values:
            analysis['memory_trends']['gpu'] = {
                'mean': np.mean(gpu_memory_values),
                'std': np.std(gpu_memory_values),
                'peak': np.max(gpu_memory_values),
                'trend': 'increasing' if gpu_memory_values[-1] > gpu_memory_values[0] else 'decreasing'
            }
            analysis['peak_usage']['gpu'] = np.max(gpu_memory_values)
        
        # Calculate efficiency score
        if analysis['memory_trends'].get('gpu'):
            gpu_trend = analysis['memory_trends']['gpu']
            # Lower std and stable usage = higher efficiency
            stability_score = 1.0 / (1.0 + gpu_trend['std'])
            utilization_score = 1.0 - gpu_trend['peak']  # Lower peak = higher efficiency
            analysis['efficiency_score'] = (stability_score + utilization_score) / 2
        
        return analysis
    
    def compare_refactored_configs(self, num_steps: int = 100) -> Dict:
        """Compare different refactored configurations."""
        print("🔬 Comparing refactored gradient accumulation configurations...")
        
        configs = {
            'baseline': create_refactored_config(
                batch_size=8, effective_batch_size=32, adaptive=False, mixed_precision=False, advanced_features=False
            ),
            'mixed_precision': create_refactored_config(
                batch_size=8, effective_batch_size=32, adaptive=False, mixed_precision=True, advanced_features=False
            ),
            'adaptive': create_refactored_config(
                batch_size=8, effective_batch_size=32, adaptive=True, mixed_precision=True, advanced_features=True
            ),
            'memory_efficient': create_refactored_config(
                batch_size=4, effective_batch_size=32, adaptive=True, mixed_precision=True, memory_efficient=True, advanced_features=True
            ),
            'large_batch': create_refactored_config(
                batch_size=16, effective_batch_size=128, adaptive=True, mixed_precision=True, advanced_features=True
            ),
            'experimental': create_experimental_refactored_config(
                batch_size=8, effective_batch_size=64, noise_scale=1e-5
            )
        }
        
        results = {}
        for name, config in configs.items():
            print(f"\n📊 Testing {name} configuration...")
            result = self.train_with_refactored_config(config, num_steps)
            results[name] = result
        
        self.results = results
        return results
    
    def generate_refactored_plots(self) -> Tuple[plt.Figure, plt.Figure, plt.Figure]:
        """Generate refactored visualization plots with improved analysis."""
        if not self.results:
            return None, None, None
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        # Create subplots
        fig1, axes1 = plt.subplots(2, 2, figsize=(16, 12))
        fig2, axes2 = plt.subplots(2, 2, figsize=(16, 12))
        fig3, axes3 = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot 1: Training metrics
        for name, result in self.results.items():
            losses = [m['loss'] for m in result['training_metrics']]
            axes1[0, 0].plot(losses, label=name, alpha=0.8, linewidth=2)
        axes1[0, 0].set_title('Training Loss (Refactored)', fontsize=14, fontweight='bold')
        axes1[0, 0].set_xlabel('Step')
        axes1[0, 0].set_ylabel('Loss')
        axes1[0, 0].legend()
        axes1[0, 0].grid(True, alpha=0.3)
        
        # Memory utilization
        for name, result in self.results.items():
            memory_util = [m['memory_utilization'] for m in result['training_metrics']]
            axes1[0, 1].plot(memory_util, label=name, alpha=0.8, linewidth=2)
        axes1[0, 1].set_title('Memory Utilization (Refactored)', fontsize=14, fontweight='bold')
        axes1[0, 1].set_xlabel('Step')
        axes1[0, 1].set_ylabel('Memory Utilization')
        axes1[0, 1].legend()
        axes1[0, 1].grid(True, alpha=0.3)
        
        # Gradient norms
        for name, result in self.results.items():
            grad_norms = [m['grad_norm'] for m in result['training_metrics']]
            axes1[1, 0].plot(grad_norms, label=name, alpha=0.8, linewidth=2)
        axes1[1, 0].set_title('Gradient Norms (Refactored)', fontsize=14, fontweight='bold')
        axes1[1, 0].set_xlabel('Step')
        axes1[1, 0].set_ylabel('Gradient Norm')
        axes1[1, 0].legend()
        axes1[1, 0].grid(True, alpha=0.3)
        
        # Step times
        for name, result in self.results.items():
            step_times = [m['step_time'] for m in result['training_metrics']]
            axes1[1, 1].plot(step_times, label=name, alpha=0.8, linewidth=2)
        axes1[1, 1].set_title('Step Times (Refactored)', fontsize=14, fontweight='bold')
        axes1[1, 1].set_xlabel('Step')
        axes1[1, 1].set_ylabel('Time (s)')
        axes1[1, 1].legend()
        axes1[1, 1].grid(True, alpha=0.3)
        
        # Plot 2: Performance comparison
        config_names = list(self.results.keys())
        avg_losses = [np.mean([m['loss'] for m in result['training_metrics']]) for result in self.results.values()]
        avg_memory = [np.mean([m['memory_utilization'] for m in result['training_metrics']]) for result in self.results.values()]
        training_times = [result['performance_summary']['training_time'] for result in self.results.values()]
        avg_step_times = [result['performance_summary']['avg_step_time'] for result in self.results.values()]
        
        # Performance metrics
        axes2[0, 0].bar(config_names, avg_losses, alpha=0.8, color='skyblue')
        axes2[0, 0].set_title('Average Loss (Refactored)', fontsize=14, fontweight='bold')
        axes2[0, 0].set_ylabel('Loss')
        axes2[0, 0].tick_params(axis='x', rotation=45)
        
        axes2[0, 1].bar(config_names, avg_memory, alpha=0.8, color='lightcoral')
        axes2[0, 1].set_title('Average Memory Utilization (Refactored)', fontsize=14, fontweight='bold')
        axes2[0, 1].set_ylabel('Memory Utilization')
        axes2[0, 1].tick_params(axis='x', rotation=45)
        
        axes2[1, 0].bar(config_names, training_times, alpha=0.8, color='lightgreen')
        axes2[1, 0].set_title('Total Training Time (Refactored)', fontsize=14, fontweight='bold')
        axes2[1, 0].set_ylabel('Time (s)')
        axes2[1, 0].tick_params(axis='x', rotation=45)
        
        axes2[1, 1].bar(config_names, avg_step_times, alpha=0.8, color='gold')
        axes2[1, 1].set_title('Average Step Time (Refactored)', fontsize=14, fontweight='bold')
        axes2[1, 1].set_ylabel('Time (s)')
        axes2[1, 1].tick_params(axis='x', rotation=45)
        
        # Plot 3: Advanced analysis
        # Memory efficiency analysis
        memory_efficiency = []
        for name, result in self.results.items():
            config = result['config']
            efficiency = config.effective_batch_size / config.batch_size
            memory_efficiency.append(efficiency)
        
        axes3[0].bar(config_names, memory_efficiency, alpha=0.8, color='plum')
        axes3[0].set_title('Memory Efficiency (Refactored)', fontsize=14, fontweight='bold')
        axes3[0].set_ylabel('Efficiency Ratio')
        axes3[0].tick_params(axis='x', rotation=45)
        
        # Memory optimization analysis
        optimization_counts = []
        for name, result in self.results.items():
            if 'memory_analysis' in result and 'optimization_count' in result['memory_analysis']:
                optimization_counts.append(result['memory_analysis']['optimization_count'])
            else:
                optimization_counts.append(0)
        
        axes3[1].bar(config_names, optimization_counts, alpha=0.8, color='orange')
        axes3[1].set_title('Memory Optimizations (Refactored)', fontsize=14, fontweight='bold')
        axes3[1].set_ylabel('Optimization Count')
        axes3[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig1, fig2, fig3
    
    def get_refactored_analysis(self) -> str:
        """Generate refactored analysis report with improved insights."""
        if not self.results:
            return "No results available. Please run the comparison first."
        
        analysis = "🔬 Refactored Advanced Gradient Accumulation Analysis\n"
        analysis += "=" * 60 + "\n\n"
        
        # Performance comparison
        analysis += "📊 Performance Comparison (Refactored):\n"
        analysis += "-" * 40 + "\n"
        
        best_loss = float('inf')
        best_memory = float('inf')
        best_time = float('inf')
        best_config = None
        best_efficiency = 0.0
        
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
            analysis += f"  - Adaptive: {result['config'].performance.enable_adaptive_accumulation}\n"
            analysis += f"  - Mixed Precision: {result['config'].performance.enable_mixed_precision}\n"
            
            # Memory analysis
            if 'memory_analysis' in result:
                mem_analysis = result['memory_analysis']
                analysis += f"  - Memory Optimizations: {mem_analysis.get('optimization_count', 0)}\n"
                analysis += f"  - Efficiency Score: {mem_analysis.get('efficiency_score', 0.0):.3f}\n"
                
                if mem_analysis.get('efficiency_score', 0.0) > best_efficiency:
                    best_efficiency = mem_analysis.get('efficiency_score', 0.0)
            
            # Track best performance
            if avg_loss < best_loss:
                best_loss = avg_loss
                best_config = name
        
        analysis += f"\n🏆 Best Configuration: {best_config.upper()}\n"
        analysis += f"   - Lowest Loss: {best_loss:.4f}\n"
        analysis += f"   - Best Efficiency Score: {best_efficiency:.3f}\n"
        
        # Architecture benefits
        analysis += "\n🏗️ Architecture Benefits (Refactored):\n"
        analysis += "-" * 40 + "\n"
        analysis += "✅ Clean separation of concerns\n"
        analysis += "✅ Strategy pattern for memory management\n"
        analysis += "✅ Improved error handling and logging\n"
        analysis += "✅ Better performance monitoring\n"
        analysis += "✅ Production-ready optimizations\n"
        analysis += "✅ Enhanced memory analysis\n"
        
        # Recommendations
        analysis += "\n💡 Recommendations (Refactored):\n"
        analysis += "-" * 30 + "\n"
        
        for name, result in self.results.items():
            if 'recommendations' in result['performance_summary']:
                recs = result['performance_summary']['recommendations']
                if recs:
                    analysis += f"\n{name}:\n"
                    for rec in recs:
                        analysis += f"  - {rec}\n"
        
        return analysis
    
    def create_refactored_gradio_interface(self):
        """Create refactored Gradio interface with improved UX."""
        with gr.Blocks(title="Refactored Advanced Gradient Accumulation Demo") as demo:
            gr.Markdown("# 🚀 Refactored Advanced Gradient Accumulation Demo")
            gr.Markdown("""
            This demo showcases the **refactored** gradient accumulation system with:
            - **🏗️ Clean Architecture**: Better separation of concerns and maintainability
            - **🎯 Strategy Pattern**: Flexible memory management strategies
            - **📊 Enhanced Monitoring**: Improved performance tracking and analysis
            - **⚡ Production Optimizations**: Better error handling and logging
            - **🧠 Intelligent Analysis**: Advanced memory usage insights
            """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Configuration")
                    num_steps = gr.Slider(
                        minimum=50, maximum=500, value=100, step=50,
                        label="Number of Training Steps"
                    )
                    run_comparison_btn = gr.Button("🔬 Run Refactored Comparison", variant="primary")
                    run_single_btn = gr.Button("🎯 Run Single Configuration", variant="secondary")
                    
                    # Single configuration options
                    with gr.Accordion("Single Configuration Options", open=False):
                        batch_size = gr.Slider(2, 32, 8, step=2, label="Batch Size")
                        effective_batch_size = gr.Slider(8, 256, 32, step=8, label="Effective Batch Size")
                        adaptive = gr.Checkbox(True, label="Adaptive Accumulation")
                        mixed_precision = gr.Checkbox(True, label="Mixed Precision")
                        memory_efficient = gr.Checkbox(True, label="Memory Efficient")
                        advanced_features = gr.Checkbox(True, label="Advanced Features")
                
                with gr.Column():
                    gr.Markdown("## Results")
                    output_text = gr.Textbox(
                        label="Refactored Analysis Results",
                        lines=20,
                        max_lines=40
                    )
            
            with gr.Row():
                gr.Markdown("## Performance Visualization (Refactored)")
            
            with gr.Row():
                plot1 = gr.Image(label="Training Metrics (Refactored)")
                plot2 = gr.Image(label="Performance Comparison (Refactored)")
            
            with gr.Row():
                plot3 = gr.Image(label="Advanced Analysis (Refactored)")
            
            # Event handlers
            def run_comparison(steps):
                results = self.compare_refactored_configs(steps)
                analysis = self.get_refactored_analysis()
                fig1, fig2, fig3 = self.generate_refactored_plots()
                
                return (
                    analysis,
                    fig1,
                    fig2,
                    fig3
                )
            
            def run_single_config(steps, batch, effective, adaptive, mixed, memory, advanced):
                config = create_refactored_config(
                    batch_size=batch,
                    effective_batch_size=effective,
                    adaptive=adaptive,
                    mixed_precision=mixed,
                    memory_efficient=memory,
                    advanced_features=advanced
                )
                
                result = self.train_with_refactored_config(config, steps)
                self.results = {'single': result}
                
                analysis = self.get_refactored_analysis()
                fig1, fig2, fig3 = self.generate_refactored_plots()
                
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
                inputs=[num_steps, batch_size, effective_batch_size, adaptive, mixed_precision, memory_efficient, advanced_features],
                outputs=[output_text, plot1, plot2, plot3]
            )
        
        return demo

def main():
    """Main function to run the refactored demo."""
    print("🚀 Refactored Advanced Gradient Accumulation Demo")
    print("=" * 60)
    
    demo = RefactoredGradientDemo()
    
    # Run comparison
    print("Running refactored configuration comparison...")
    results = demo.compare_refactored_configs(num_steps=100)
    
    # Generate analysis
    analysis = demo.get_refactored_analysis()
    print("\n" + analysis)
    
    # Generate plots
    fig1, fig2, fig3 = demo.generate_refactored_plots()
    
    # Save plots
    if fig1:
        fig1.savefig('refactored_training_metrics.png', dpi=300, bbox_inches='tight')
        print("✅ Saved refactored training metrics plot")
    
    if fig2:
        fig2.savefig('refactored_performance_comparison.png', dpi=300, bbox_inches='tight')
        print("✅ Saved refactored performance comparison plot")
    
    if fig3:
        fig3.savefig('refactored_advanced_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Saved refactored advanced analysis plot")
    
    # Launch Gradio interface
    print("\n🎯 Launching refactored Gradio interface...")
    interface = demo.create_refactored_gradio_interface()
    interface.launch(share=True)

if __name__ == "__main__":
    main()
