"""
🎨 Interactive Gradio Demos for Model Inference & Visualization
==============================================================

A comprehensive collection of interactive demos showcasing:
- Real-time model inference
- Interactive visualizations
- Dynamic parameter adjustment
- Performance monitoring
- Multi-model comparison
"""

import gradio as gr
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import time
import threading
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import logging
from datetime import datetime
import asyncio
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

@dataclass
class DemoConfig:
    """Configuration for interactive demos."""
    
    # Model settings
    model_type: str = "transformer"
    batch_size: int = 32
    max_length: int = 512
    
    # Visualization settings
    theme: str = "plotly_white"
    colors: List[str] = None
    
    # Performance settings
    enable_cache: bool = True
    enable_profiling: bool = True
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

class InteractiveGradioDemos:
    """Main class for interactive Gradio demos."""
    
    def __init__(self, config: Optional[DemoConfig] = None):
        self.config = config or DemoConfig()
        self.models = {}
        self.demo_data = {}
        self.performance_metrics = {}
        self.initialize_demo_environment()
    
    def initialize_demo_environment(self):
        """Initialize the demo environment with sample models and data."""
        try:
            # Create sample neural network models for demo
            self.models = {
                "simple_classifier": self._create_simple_classifier(),
                "regression_model": self._create_regression_model(),
                "autoencoder": self._create_autoencoder(),
                "gan_generator": self._create_gan_generator()
            }
            
            # Generate sample data
            self.demo_data = self._generate_sample_data()
            
            # Initialize performance tracking
            self.performance_metrics = {
                "inference_times": [],
                "accuracy_scores": [],
                "loss_values": [],
                "memory_usage": []
            }
            
            logger.info("Demo environment initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize demo environment: {e}")
    
    def _create_simple_classifier(self) -> nn.Module:
        """Create a simple classification model for demo."""
        model = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 5),  # 5 classes
            nn.Softmax(dim=1)
        )
        return model
    
    def _create_regression_model(self) -> nn.Module:
        """Create a regression model for demo."""
        model = nn.Sequential(
            nn.Linear(8, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1)
        )
        return model
    
    def _create_autoencoder(self) -> nn.Module:
        """Create an autoencoder model for demo."""
        class Autoencoder(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(20, 64),
                    nn.ReLU(),
                    nn.Linear(64, 32),
                    nn.ReLU(),
                    nn.Linear(32, 8)
                )
                self.decoder = nn.Sequential(
                    nn.Linear(8, 32),
                    nn.ReLU(),
                    nn.Linear(32, 64),
                    nn.ReLU(),
                    nn.Linear(64, 20)
                )
            
            def forward(self, x):
                encoded = self.encoder(x)
                decoded = self.decoder(encoded)
                return decoded
        
        return Autoencoder()
    
    def _create_gan_generator(self) -> nn.Module:
        """Create a GAN generator model for demo."""
        model = nn.Sequential(
            nn.Linear(100, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 1024),
            nn.LeakyReLU(0.2),
            nn.Linear(1024, 784),  # 28x28 image
            nn.Tanh()
        )
        return model
    
    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample data for demos."""
        np.random.seed(42)
        
        # Classification data
        X_class = np.random.randn(1000, 10)
        y_class = np.random.randint(0, 5, 1000)
        
        # Regression data
        X_reg = np.random.randn(800, 8)
        y_reg = np.sum(X_reg * np.random.randn(8), axis=1) + np.random.randn(800) * 0.1
        
        # Autoencoder data
        X_ae = np.random.randn(500, 20)
        
        # Time series data
        time_steps = np.linspace(0, 10, 200)
        time_series = np.sin(time_steps) + np.random.randn(200) * 0.1
        
        return {
            "classification": {"X": X_class, "y": y_class},
            "regression": {"X": X_reg, "y": y_reg},
            "autoencoder": {"X": X_ae},
            "time_series": {"time": time_steps, "values": time_series}
        }
    
    def create_model_inference_demo(self) -> gr.Blocks:
        """Create interactive model inference demo."""
        
        with gr.Blocks(title="Model Inference Demo", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🤖 Interactive Model Inference Demo")
            gr.Markdown("Explore different AI models with real-time inference and visualization")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Model Selection")
                    model_type = gr.Dropdown(
                        choices=list(self.models.keys()),
                        value="simple_classifier",
                        label="Select Model",
                        info="Choose a model to test"
                    )
                    
                    gr.Markdown("## Input Parameters")
                    input_size = gr.Slider(
                        minimum=1, maximum=100, value=10, step=1,
                        label="Input Size",
                        info="Number of input features"
                    )
                    
                    batch_size = gr.Slider(
                        minimum=1, maximum=128, value=32, step=1,
                        label="Batch Size",
                        info="Number of samples to process"
                    )
                    
                    noise_level = gr.Slider(
                        minimum=0.0, maximum=1.0, value=0.1, step=0.01,
                        label="Noise Level",
                        info="Add noise to input data"
                    )
                    
                    run_inference_btn = gr.Button("🚀 Run Inference", variant="primary")
                    clear_btn = gr.Button("🗑️ Clear Results")
                
                with gr.Column(scale=2):
                    gr.Markdown("## Inference Results")
                    
                    with gr.Row():
                        with gr.Column():
                            inference_output = gr.JSON(label="Model Output")
                            confidence_score = gr.Gauge(
                                label="Confidence Score",
                                minimum=0, maximum=1, value=0.5
                            )
                        
                        with gr.Column():
                            processing_time = gr.Number(label="Processing Time (ms)")
                            memory_usage = gr.Number(label="Memory Usage (MB)")
                    
                    gr.Markdown("## Performance Metrics")
                    performance_chart = gr.Plot(label="Performance Over Time")
            
            # Event handlers
            def run_inference(model_type, input_size, batch_size, noise_level):
                start_time = time.time()
                
                try:
                    # Generate input data
                    if model_type == "simple_classifier":
                        X = torch.randn(batch_size, input_size) + noise_level * torch.randn(batch_size, input_size)
                        model = self.models[model_type]
                        with torch.no_grad():
                            output = model(X)
                            predictions = torch.argmax(output, dim=1)
                            confidence = torch.max(output, dim=1)[0].mean().item()
                    elif model_type == "regression_model":
                        X = torch.randn(batch_size, min(input_size, 8)) + noise_level * torch.randn(batch_size, min(input_size, 8))
                        model = self.models[model_type]
                        with torch.no_grad():
                            output = model(X)
                            predictions = output.squeeze()
                            confidence = 1.0 - torch.std(output).item()
                    else:
                        X = torch.randn(batch_size, min(input_size, 20)) + noise_level * torch.randn(batch_size, min(input_size, 20))
                        model = self.models[model_type]
                        with torch.no_grad():
                            output = model(X)
                            predictions = output
                            confidence = 0.8
                    
                    processing_time_ms = (time.time() - start_time) * 1000
                    memory_mb = torch.cuda.memory_allocated() / 1024**2 if torch.cuda.is_available() else 0
                    
                    # Update performance metrics
                    self.performance_metrics["inference_times"].append(processing_time_ms)
                    self.performance_metrics["accuracy_scores"].append(confidence)
                    
                    # Create performance chart
                    fig = self._create_performance_chart()
                    
                    return {
                        "model_type": model_type,
                        "predictions": predictions.tolist()[:10],  # Show first 10
                        "confidence": confidence,
                        "processing_time": processing_time_ms,
                        "memory_usage": memory_mb
                    }, confidence, processing_time_ms, memory_mb, fig
                    
                except Exception as e:
                    logger.error(f"Inference error: {e}")
                    return {"error": str(e)}, 0.0, 0.0, 0.0, None
            
            def clear_results():
                return None, 0.5, 0.0, 0.0, None
            
            # Connect events
            run_inference_btn.click(
                fn=run_inference,
                inputs=[model_type, input_size, batch_size, noise_level],
                outputs=[inference_output, confidence_score, processing_time, memory_usage, performance_chart]
            )
            
            clear_btn.click(
                fn=clear_results,
                outputs=[inference_output, confidence_score, processing_time, memory_usage, performance_chart]
            )
        
        return demo
    
    def create_visualization_demo(self) -> gr.Blocks:
        """Create interactive visualization demo."""
        
        with gr.Blocks(title="Data Visualization Demo", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 📊 Interactive Data Visualization Demo")
            gr.Markdown("Explore data with interactive charts and dynamic visualizations")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Chart Configuration")
                    
                    chart_type = gr.Dropdown(
                        choices=["scatter", "line", "bar", "histogram", "heatmap", "3d_scatter"],
                        value="scatter",
                        label="Chart Type",
                        info="Select visualization type"
                    )
                    
                    data_source = gr.Dropdown(
                        choices=list(self.demo_data.keys()),
                        value="classification",
                        label="Data Source",
                        info="Choose data to visualize"
                    )
                    
                    color_scheme = gr.Dropdown(
                        choices=["viridis", "plasma", "inferno", "magma", "cividis"],
                        value="viridis",
                        label="Color Scheme",
                        info="Select color palette"
                    )
                    
                    opacity = gr.Slider(
                        minimum=0.1, maximum=1.0, value=0.7, step=0.1,
                        label="Opacity",
                        info="Adjust transparency"
                    )
                    
                    animate_btn = gr.Button("🎬 Animate Chart", variant="primary")
                    export_btn = gr.Button("💾 Export Chart")
                
                with gr.Column(scale=2):
                    gr.Markdown("## Interactive Visualization")
                    main_chart = gr.Plot(label="Dynamic Chart")
                    
                    gr.Markdown("## Chart Statistics")
                    stats_output = gr.JSON(label="Data Statistics")
            
            # Event handlers
            def update_chart(chart_type, data_source, color_scheme, opacity):
                try:
                    data = self.demo_data[data_source]
                    
                    if chart_type == "scatter":
                        if data_source == "classification":
                            fig = px.scatter(
                                x=data["X"][:, 0],
                                y=data["X"][:, 1],
                                color=data["y"],
                                color_continuous_scale=color_scheme,
                                opacity=opacity,
                                title=f"{data_source.title()} Data Scatter Plot"
                            )
                        else:
                            fig = px.scatter(
                                x=data["X"][:, 0],
                                y=data["X"][:, 1],
                                color_continuous_scale=color_scheme,
                                opacity=opacity,
                                title=f"{data_source.title()} Data Scatter Plot"
                            )
                    
                    elif chart_type == "line":
                        if data_source == "time_series":
                            fig = px.line(
                                x=data["time"],
                                y=data["values"],
                                title="Time Series Data"
                            )
                        else:
                            fig = px.line(
                                y=data["X"][:50, 0],
                                title=f"{data_source.title()} Data Line Plot"
                            )
                    
                    elif chart_type == "bar":
                        if data_source == "classification":
                            class_counts = np.bincount(data["y"])
                            fig = px.bar(
                                x=list(range(len(class_counts))),
                                y=class_counts,
                                title="Class Distribution",
                                color_discrete_sequence=[color_scheme]
                            )
                        else:
                            fig = px.bar(
                                y=data["X"][:20, 0],
                                title=f"{data_source.title()} Data Bar Chart"
                            )
                    
                    elif chart_type == "histogram":
                        fig = px.histogram(
                            x=data["X"].flatten()[:1000],
                            nbins=30,
                            title=f"{data_source.title()} Data Distribution",
                            color_discrete_sequence=[color_scheme]
                        )
                    
                    elif chart_type == "heatmap":
                        corr_matrix = np.corrcoef(data["X"][:100, :10].T)
                        fig = px.imshow(
                            corr_matrix,
                            title="Correlation Matrix",
                            color_continuous_scale=color_scheme
                        )
                    
                    elif chart_type == "3d_scatter":
                        fig = px.scatter_3d(
                            x=data["X"][:200, 0],
                            y=data["X"][:200, 1],
                            z=data["X"][:200, 2],
                            color=data["y"][:200] if "y" in data else None,
                            title=f"{data_source.title()} 3D Scatter Plot"
                        )
                    
                    # Update layout
                    fig.update_layout(
                        template=self.config.theme,
                        height=500,
                        showlegend=True
                    )
                    
                    # Calculate statistics
                    stats = {
                        "data_shape": data["X"].shape,
                        "mean": float(np.mean(data["X"])),
                        "std": float(np.std(data["X"])),
                        "min": float(np.min(data["X"])),
                        "max": float(np.max(data["X"])),
                        "chart_type": chart_type,
                        "data_source": data_source
                    }
                    
                    return fig, stats
                    
                except Exception as e:
                    logger.error(f"Chart update error: {e}")
                    return None, {"error": str(e)}
            
            def animate_chart():
                # Create animated chart
                frames = []
                data = self.demo_data["time_series"]
                
                for i in range(0, len(data["time"]), 10):
                    fig = px.line(
                        x=data["time"][:i+1],
                        y=data["values"][:i+1],
                        title="Animated Time Series"
                    )
                    fig.update_layout(height=500)
                    frames.append(fig)
                
                return frames[0] if frames else None
            
            def export_chart():
                return "Chart exported successfully! (Feature to be implemented)"
            
            # Connect events
            chart_type.change(
                fn=update_chart,
                inputs=[chart_type, data_source, color_scheme, opacity],
                outputs=[main_chart, stats_output]
            )
            
            data_source.change(
                fn=update_chart,
                inputs=[chart_type, data_source, color_scheme, opacity],
                outputs=[main_chart, stats_output]
            )
            
            color_scheme.change(
                fn=update_chart,
                inputs=[chart_type, data_source, color_scheme, opacity],
                outputs=[main_chart, stats_output]
            )
            
            opacity.change(
                fn=update_chart,
                inputs=[chart_type, data_source, color_scheme, opacity],
                outputs=[main_chart, stats_output]
            )
            
            animate_btn.click(
                fn=animate_chart,
                outputs=[main_chart]
            )
            
            export_btn.click(
                fn=export_chart,
                outputs=[stats_output]
            )
            
            # Initial chart
            initial_fig, initial_stats = update_chart("scatter", "classification", "viridis", 0.7)
            main_chart.value = initial_fig
            stats_output.value = initial_stats
        
        return demo
    
    def create_performance_monitoring_demo(self) -> gr.Blocks:
        """Create performance monitoring demo."""
        
        with gr.Blocks(title="Performance Monitoring Demo", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 📈 Performance Monitoring Demo")
            gr.Markdown("Real-time performance tracking and optimization insights")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Monitoring Controls")
                    
                    enable_monitoring = gr.Checkbox(
                        value=True,
                        label="Enable Real-time Monitoring",
                        info="Start/stop performance tracking"
                    )
                    
                    monitoring_interval = gr.Slider(
                        minimum=1, maximum=10, value=2,
                        step=1, label="Update Interval (seconds)"
                    )
                    
                    metrics_to_track = gr.CheckboxGroup(
                        choices=["CPU", "GPU", "Memory", "Network", "Disk"],
                        value=["CPU", "Memory"],
                        label="Metrics to Track"
                    )
                    
                    start_stress_test = gr.Button("🔥 Start Stress Test", variant="primary")
                    stop_stress_test = gr.Button("⏹️ Stop Stress Test", variant="stop")
                
                with gr.Column(scale=2):
                    gr.Markdown("## Performance Metrics")
                    
                    with gr.Row():
                        cpu_gauge = gr.Gauge(label="CPU Usage", minimum=0, maximum=100, value=0)
                        memory_gauge = gr.Gauge(label="Memory Usage", minimum=0, maximum=100, value=0)
                    
                    with gr.Row():
                        gpu_gauge = gr.Gauge(label="GPU Usage", minimum=0, maximum=100, value=0)
                        network_gauge = gr.Gauge(label="Network I/O", minimum=0, maximum=100, value=0)
                    
                    performance_chart = gr.Plot(label="Performance Over Time")
                    alerts_output = gr.JSON(label="System Alerts")
            
            # Performance monitoring variables
            monitoring_active = gr.State(False)
            stress_test_active = gr.State(False)
            
            # Event handlers
            def toggle_monitoring(enable, interval, metrics):
                if enable:
                    return gr.update(value=True), f"Monitoring started with {interval}s interval"
                else:
                    return gr.update(value=False), "Monitoring stopped"
            
            def start_stress_test():
                # Simulate stress test
                return gr.update(value=True), "Stress test started - generating load..."
            
            def stop_stress_test():
                return gr.update(value=False), "Stress test stopped"
            
            def update_performance_metrics():
                # Simulate performance metrics
                import psutil
                
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                gpu_percent = 0  # Would need GPU monitoring library
                network_percent = 0  # Would need network monitoring
                
                # Create performance chart
                fig = self._create_performance_chart()
                
                # Generate alerts
                alerts = []
                if cpu_percent > 80:
                    alerts.append({"level": "warning", "message": "High CPU usage detected"})
                if memory_percent > 85:
                    alerts.append({"level": "critical", "message": "High memory usage detected"})
                
                return cpu_percent, memory_percent, gpu_percent, network_percent, fig, alerts
            
            # Connect events
            enable_monitoring.change(
                fn=toggle_monitoring,
                inputs=[enable_monitoring, monitoring_interval, metrics_to_track],
                outputs=[monitoring_active, alerts_output]
            )
            
            start_stress_test.click(
                fn=start_stress_test,
                outputs=[stress_test_active, alerts_output]
            )
            
            stop_stress_test.click(
                fn=stop_stress_test,
                outputs=[stress_test_active, alerts_output]
            )
            
            # Auto-update performance metrics
            demo.load(update_performance_metrics, outputs=[
                cpu_gauge, memory_gauge, gpu_gauge, network_gauge,
                performance_chart, alerts_output
            ])
        
        return demo
    
    def _create_performance_chart(self) -> go.Figure:
        """Create performance monitoring chart."""
        if not self.performance_metrics["inference_times"]:
            return go.Figure()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Inference Time", "Accuracy Score", "Memory Usage", "Performance Trend"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Inference time
        fig.add_trace(
            go.Scatter(
                y=self.performance_metrics["inference_times"],
                mode="lines+markers",
                name="Inference Time (ms)",
                line=dict(color=self.config.colors[0])
            ),
            row=1, col=1
        )
        
        # Accuracy score
        fig.add_trace(
            go.Scatter(
                y=self.performance_metrics["accuracy_scores"],
                mode="lines+markers",
                name="Accuracy Score",
                line=dict(color=self.config.colors[1])
            ),
            row=1, col=2
        )
        
        # Memory usage (simulated)
        memory_usage = [np.random.randint(100, 500) for _ in range(len(self.performance_metrics["inference_times"]))]
        fig.add_trace(
            go.Scatter(
                y=memory_usage,
                mode="lines+markers",
                name="Memory Usage (MB)",
                line=dict(color=self.config.colors[2])
            ),
            row=2, col=1
        )
        
        # Performance trend
        trend = np.cumsum(self.performance_metrics["accuracy_scores"])
        fig.add_trace(
            go.Scatter(
                y=trend,
                mode="lines+markers",
                name="Cumulative Performance",
                line=dict(color=self.config.colors[3])
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title="Performance Metrics Dashboard",
            template=self.config.theme,
            showlegend=True
        )
        
        return fig
    
    def create_main_demo_interface(self) -> gr.Blocks:
        """Create the main demo interface with all demos."""
        
        with gr.Blocks(
            title="Interactive AI Demos",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1400px !important;
                margin: 0 auto;
            }
            .demo-header {
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            """
        ) as main_interface:
            
            gr.Markdown("""
            <div class="demo-header">
                <h1>🎨 Interactive AI Demos</h1>
                <p>Explore cutting-edge AI capabilities with interactive demos and real-time visualization</p>
            </div>
            """)
            
            # Create tabs for different demos
            with gr.Tabs():
                with gr.TabItem("🤖 Model Inference", id=0):
                    self.create_model_inference_demo()
                
                with gr.TabItem("📊 Data Visualization", id=1):
                    self.create_visualization_demo()
                
                with gr.TabItem("📈 Performance Monitoring", id=2):
                    self.create_performance_monitoring_demo()
                
                with gr.TabItem("ℹ️ About", id=3):
                    gr.Markdown("""
                    ## About Interactive AI Demos
                    
                    This application showcases various AI capabilities through interactive Gradio interfaces:
                    
                    ### 🚀 Features
                    - **Real-time Model Inference**: Test different AI models with dynamic parameters
                    - **Interactive Visualizations**: Explore data with various chart types and configurations
                    - **Performance Monitoring**: Track system performance and model metrics
                    - **Dynamic Updates**: Real-time parameter adjustment and result visualization
                    
                    ### 🛠️ Technologies
                    - **Gradio**: Modern web interface framework
                    - **PyTorch**: Deep learning framework
                    - **Plotly**: Interactive visualization library
                    - **NumPy/Pandas**: Data manipulation and analysis
                    
                    ### 📱 Usage
                    1. Select a demo from the tabs above
                    2. Adjust parameters using the interactive controls
                    3. Run inference or generate visualizations
                    4. Monitor performance and analyze results
                    
                    ### 🔧 Customization
                    - Modify model parameters in real-time
                    - Choose from multiple visualization styles
                    - Adjust performance monitoring settings
                    - Export results and charts
                    """)
        
        return main_interface

def main():
    """Main function to launch the interactive demos."""
    
    # Create demo application
    demos = InteractiveGradioDemos()
    main_interface = demos.create_main_demo_interface()
    
    # Launch the application
    main_interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True,
        show_error=True,
        height=800,
        show_tips=True
    )

if __name__ == "__main__":
    main()
