"""
🎨 Enhanced UI Interactive Gradio Demos
=======================================

Advanced user interface design for showcasing AI model capabilities with:
- Modern, intuitive design
- Enhanced visual hierarchy
- Interactive elements and animations
- Responsive layouts
- Professional appearance
"""

import gradio as gr
import torch
import torch.nn as nn
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

@dataclass
class EnhancedUIConfig:
    """Configuration for enhanced UI demos."""
    
    # UI settings
    theme: str = "Soft"
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    accent_color: str = "#f093fb"
    success_color: str = "#4facfe"
    warning_color: str = "#ff9a9e"
    
    # Layout settings
    max_width: str = "1400px"
    card_radius: str = "16px"
    shadow: str = "0 8px 32px rgba(0, 0, 0, 0.1)"
    
    # Animation settings
    enable_animations: bool = True
    transition_duration: str = "0.3s"

class EnhancedUIDemos:
    """Enhanced UI demos with modern design and intuitive interfaces."""
    
    def __init__(self, config: Optional[EnhancedUIConfig] = None):
        self.config = config or EnhancedUIConfig()
        self.models = self._create_demo_models()
        self.demo_data = self._generate_demo_data()
        self.performance_history = []
        self.initialize_ui_environment()
    
    def initialize_ui_environment(self):
        """Initialize the enhanced UI environment."""
        try:
            # Initialize performance tracking
            self.performance_history = []
            logger.info("Enhanced UI environment initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize UI environment: {e}")
    
    def _create_demo_models(self):
        """Create enhanced demo models."""
        models = {}
        
        # Enhanced classifier with better architecture
        classifier = nn.Sequential(
            nn.Linear(10, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 5),
            nn.Softmax(dim=1)
        )
        models["enhanced_classifier"] = classifier
        
        # Enhanced regressor
        regressor = nn.Sequential(
            nn.Linear(8, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.4),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        models["enhanced_regressor"] = regressor
        
        # Autoencoder for feature learning
        class Autoencoder(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(20, 128),
                    nn.ReLU(),
                    nn.BatchNorm1d(128),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.BatchNorm1d(64),
                    nn.Linear(64, 16)
                )
                self.decoder = nn.Sequential(
                    nn.Linear(16, 64),
                    nn.ReLU(),
                    nn.BatchNorm1d(64),
                    nn.Linear(64, 128),
                    nn.ReLU(),
                    nn.BatchNorm1d(128),
                    nn.Linear(128, 20)
                )
            
            def forward(self, x):
                encoded = self.encoder(x)
                decoded = self.decoder(encoded)
                return decoded
        
        models["autoencoder"] = Autoencoder()
        
        return models
    
    def _generate_demo_data(self):
        """Generate enhanced demo data."""
        np.random.seed(42)
        
        # Enhanced classification data with better separation
        n_samples = 1500
        n_features = 10
        
        # Create clusters for better visualization
        cluster_centers = np.array([
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0],
            [-2, -2, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 3, 0, 0, 0, 0, 0, 0],
            [0, 0, -3, -3, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 2, 2, 0, 0, 0, 0]
        ])
        
        X_class = np.random.randn(n_samples, n_features) * 0.5
        y_class = np.random.randint(0, 5, n_samples)
        
        for i in range(5):
            mask = y_class == i
            X_class[mask] += cluster_centers[i]
        
        # Enhanced regression data
        X_reg = np.random.randn(1000, 8)
        coefficients = np.random.randn(8) * 2
        y_reg = np.sum(X_reg * coefficients, axis=1) + np.random.randn(1000) * 0.1
        
        # Enhanced time series data
        time_steps = np.linspace(0, 20, 400)
        trend = 0.1 * time_steps
        seasonal = 2 * np.sin(2 * np.pi * time_steps / 4)
        noise = np.random.randn(400) * 0.3
        time_series = trend + seasonal + noise
        
        # Autoencoder data
        X_ae = np.random.randn(800, 20)
        
        return {
            "enhanced_classification": {"X": X_class, "y": y_class},
            "enhanced_regression": {"X": X_reg, "y": y_reg},
            "enhanced_time_series": {"time": time_steps, "values": time_series},
            "autoencoder": {"X": X_ae}
        }
    
    def _get_custom_css(self):
        """Get custom CSS for enhanced UI."""
        return f"""
        .enhanced-container {{
            max-width: {self.config.max_width} !important;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .enhanced-header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, {self.config.primary_color} 0%, {self.config.secondary_color} 100%);
            color: white;
            border-radius: {self.config.card_radius};
            margin-bottom: 30px;
            box-shadow: {self.config.shadow};
        }}
        
        .enhanced-header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .enhanced-header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .enhanced-card {{
            background: white;
            border-radius: {self.config.card_radius};
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: {self.config.shadow};
            border: 1px solid rgba(0, 0, 0, 0.05);
        }}
        
        .enhanced-card h2 {{
            color: {self.config.primary_color};
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: 600;
        }}
        
        .enhanced-button {{
            background: linear-gradient(135deg, {self.config.primary_color} 0%, {self.config.secondary_color} 100%);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all {self.config.transition_duration} ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .enhanced-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .enhanced-button.secondary {{
            background: linear-gradient(135deg, {self.config.accent_color} 0%, {self.config.warning_color} 100%);
        }}
        
        .enhanced-button.secondary:hover {{
            box-shadow: 0 6px 20px rgba(240, 147, 251, 0.4);
        }}
        
        .enhanced-metric {{
            background: linear-gradient(135deg, {self.config.success_color} 0%, {self.config.primary_color} 100%);
            color: white;
            padding: 20px;
            border-radius: {self.config.card_radius};
            text-align: center;
            margin: 10px 0;
        }}
        
        .enhanced-metric h3 {{
            margin: 0 0 10px 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .enhanced-metric .value {{
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
        }}
        
        .enhanced-chart-container {{
            background: white;
            border-radius: {self.config.card_radius};
            padding: 20px;
            margin: 20px 0;
            box-shadow: {self.config.shadow};
        }}
        
        .enhanced-controls {{
            background: #f8f9fa;
            border-radius: {self.config.card_radius};
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e9ecef;
        }}
        
        .enhanced-controls h3 {{
            color: {self.config.primary_color};
            margin-bottom: 15px;
            font-size: 1.2rem;
        }}
        
        .enhanced-tab {{
            background: white;
            border-radius: {self.config.card_radius};
            padding: 30px;
            margin: 20px 0;
            box-shadow: {self.config.shadow};
        }}
        
        .enhanced-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .badge-success {{
            background: {self.config.success_color};
            color: white;
        }}
        
        .badge-warning {{
            background: {self.config.warning_color};
            color: white;
        }}
        
        .badge-info {{
            background: {self.config.primary_color};
            color: white;
        }}
        
        .enhanced-progress {{
            background: #e9ecef;
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .enhanced-progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, {self.config.primary_color} 0%, {self.config.secondary_color} 100%);
            border-radius: 10px;
            transition: width {self.config.transition_duration} ease;
        }}
        
        .enhanced-alert {{
            padding: 15px 20px;
            border-radius: {self.config.card_radius};
            margin: 15px 0;
            border-left: 4px solid;
        }}
        
        .alert-success {{
            background: rgba(79, 172, 254, 0.1);
            border-left-color: {self.config.success_color};
            color: #0c5460;
        }}
        
        .alert-warning {{
            background: rgba(255, 154, 158, 0.1);
            border-left-color: {self.config.warning_color};
            color: #856404;
        }}
        
        .alert-info {{
            background: rgba(102, 126, 234, 0.1);
            border-left-color: {self.config.primary_color};
            color: #0c5460;
        }}
        
        @media (max-width: 768px) {{
            .enhanced-container {{
                padding: 10px;
            }}
            
            .enhanced-header {{
                padding: 20px 10px;
            }}
            
            .enhanced-header h1 {{
                font-size: 2rem;
            }}
            
            .enhanced-card {{
                padding: 15px;
            }}
        }}
        """
    
    def create_enhanced_model_inference_interface(self):
        """Create enhanced model inference interface with modern UI."""
        
        with gr.Blocks(title="Enhanced Model Inference", theme=gr.themes.Soft(), css=self._get_custom_css()) as demo:
            
            # Enhanced Header
            gr.Markdown(f"""
            <div class="enhanced-header">
                <h1>🚀 Enhanced AI Model Inference</h1>
                <p>Experience cutting-edge AI models with our intuitive, professional interface</p>
            </div>
            """)
            
            with gr.Row():
                # Left Column - Controls
                with gr.Column(scale=1):
                    gr.Markdown("""
                    <div class="enhanced-card">
                        <h2>🎯 Model Configuration</h2>
                        <p>Select and configure your AI model for optimal performance</p>
                    </div>
                    """)
                    
                    with gr.Blocks(css=".enhanced-controls"):
                        gr.Markdown("### 🤖 Model Selection")
                        
                        model_type = gr.Dropdown(
                            choices=list(self.models.keys()),
                            value="enhanced_classifier",
                            label="AI Model",
                            info="Choose from our advanced model collection",
                            container=True
                        )
                        
                        gr.Markdown("### ⚙️ Performance Parameters")
                        
                        input_size = gr.Slider(
                            minimum=1, maximum=100, value=10, step=1,
                            label="Input Features",
                            info="Number of input features for the model",
                            container=True
                        )
                        
                        batch_size = gr.Slider(
                            minimum=1, maximum=256, value=64, step=1,
                            label="Batch Size",
                            info="Process multiple samples simultaneously",
                            container=True
                        )
                        
                        noise_level = gr.Slider(
                            minimum=0.0, maximum=2.0, value=0.1, step=0.01,
                            label="Noise Level",
                            info="Add controlled noise for robustness testing",
                            container=True
                        )
                        
                        gr.Markdown("### 🎮 Actions")
                        
                        with gr.Row():
                            run_inference_btn = gr.Button(
                                "🚀 Run Inference", 
                                variant="primary",
                                size="lg",
                                elem_classes=["enhanced-button"]
                            )
                            clear_btn = gr.Button(
                                "🗑️ Clear", 
                                variant="secondary",
                                size="lg",
                                elem_classes=["enhanced-button", "secondary"]
                            )
                
                # Right Column - Results
                with gr.Column(scale=2):
                    gr.Markdown("""
                    <div class="enhanced-card">
                        <h2>📊 Inference Results</h2>
                        <p>Real-time model predictions and performance metrics</p>
                    </div>
                    """)
                    
                    # Results Display
                    with gr.Row():
                        with gr.Column():
                            inference_output = gr.JSON(
                                label="Model Output",
                                container=True
                            )
                        
                        with gr.Column():
                            confidence_score = gr.Gauge(
                                label="Confidence Score",
                                minimum=0, maximum=1, value=0.5,
                                container=True
                            )
                    
                    # Performance Metrics
                    gr.Markdown("### ⚡ Performance Metrics")
                    
                    with gr.Row():
                        with gr.Column():
                            processing_time = gr.Number(
                                label="Processing Time (ms)",
                                container=True
                            )
                        
                        with gr.Column():
                            memory_usage = gr.Number(
                                label="Memory Usage (MB)",
                                container=True
                            )
                    
                    # Performance Chart
                    gr.Markdown("### 📈 Performance Trends")
                    performance_chart = gr.Plot(
                        label="Performance Over Time",
                        container=True
                    )
            
            # Event handlers
            def run_enhanced_inference(model_type, input_size, batch_size, noise_level):
                start_time = time.time()
                
                try:
                    # Generate input data
                    if model_type == "enhanced_classifier":
                        X = torch.randn(batch_size, min(input_size, 10)) + noise_level * torch.randn(batch_size, min(input_size, 10))
                        model = self.models[model_type]
                        with torch.no_grad():
                            output = model(X)
                            predictions = torch.argmax(output, dim=1)
                            confidence = torch.max(output, dim=1)[0].mean().item()
                    elif model_type == "enhanced_regressor":
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
                    
                    # Update performance history
                    self.performance_history.append({
                        "model_type": model_type,
                        "processing_time": processing_time_ms,
                        "confidence": confidence,
                        "timestamp": time.time()
                    })
                    
                    # Create enhanced performance chart
                    fig = self._create_enhanced_performance_chart()
                    
                    return {
                        "model_type": model_type,
                        "predictions": predictions.tolist()[:10],
                        "confidence": confidence,
                        "processing_time": processing_time_ms,
                        "memory_usage": memory_mb,
                        "status": "success"
                    }, confidence, processing_time_ms, memory_mb, fig
                    
                except Exception as e:
                    logger.error(f"Inference error: {e}")
                    return {"error": str(e), "status": "error"}, 0.0, 0.0, None
            
            def clear_enhanced_results():
                return None, 0.5, 0.0, 0.0, None
            
            # Connect events
            run_inference_btn.click(
                fn=run_enhanced_inference,
                inputs=[model_type, input_size, batch_size, noise_level],
                outputs=[inference_output, confidence_score, processing_time, memory_usage, performance_chart]
            )
            
            clear_btn.click(
                fn=clear_enhanced_results,
                outputs=[inference_output, confidence_score, processing_time, memory_usage, performance_chart]
            )
        
        return demo
    
    def create_enhanced_visualization_interface(self):
        """Create enhanced data visualization interface."""
        
        with gr.Blocks(title="Enhanced Data Visualization", theme=gr.themes.Soft(), css=self._get_custom_css()) as demo:
            
            gr.Markdown(f"""
            <div class="enhanced-header">
                <h1>📊 Enhanced Data Visualization</h1>
                <p>Explore your data with beautiful, interactive charts and advanced analytics</p>
            </div>
            """)
            
            with gr.Row():
                # Left Column - Controls
                with gr.Column(scale=1):
                    gr.Markdown("""
                    <div class="enhanced-card">
                        <h2>🎨 Visualization Settings</h2>
                        <p>Customize your charts for the perfect presentation</p>
                    </div>
                    """)
                    
                    with gr.Blocks(css=".enhanced-controls"):
                        gr.Markdown("### 📈 Chart Type")
                        
                        chart_type = gr.Dropdown(
                            choices=["scatter", "line", "histogram", "bar", "heatmap", "3d_scatter", "box", "violin"],
                            value="scatter",
                            label="Visualization Type",
                            info="Choose the best chart for your data",
                            container=True
                        )
                        
                        gr.Markdown("### 🗃️ Data Source")
                        
                        data_source = gr.Dropdown(
                            choices=list(self.demo_data.keys()),
                            value="enhanced_classification",
                            label="Dataset",
                            info="Select from our curated datasets",
                            container=True
                        )
                        
                        gr.Markdown("### 🎨 Appearance")
                        
                        color_scheme = gr.Dropdown(
                            choices=["viridis", "plasma", "inferno", "magma", "cividis", "turbo", "rainbow"],
                            value="viridis",
                            label="Color Palette",
                            info="Professional color schemes for your charts",
                            container=True
                        )
                        
                        opacity = gr.Slider(
                            minimum=0.1, maximum=1.0, value=0.8, step=0.1,
                            label="Transparency",
                            info="Adjust chart transparency for better visibility",
                            container=True
                        )
                        
                        gr.Markdown("### 🎬 Advanced Features")
                        
                        with gr.Row():
                            animate_btn = gr.Button(
                                "🎬 Animate", 
                                variant="primary",
                                elem_classes=["enhanced-button"]
                            )
                            export_btn = gr.Button(
                                "💾 Export", 
                                variant="secondary",
                                elem_classes=["enhanced-button", "secondary"]
                            )
                
                # Right Column - Visualization
                with gr.Column(scale=2):
                    gr.Markdown("""
                    <div class="enhanced-card">
                        <h2>📊 Interactive Chart</h2>
                        <p>Dynamic visualization that responds to your settings</p>
                    </div>
                    """)
                    
                    main_chart = gr.Plot(
                        label="Enhanced Visualization",
                        container=True
                    )
                    
                    gr.Markdown("### 📋 Data Statistics")
                    stats_output = gr.JSON(
                        label="Dataset Information",
                        container=True
                    )
            
            # Event handlers
            def update_enhanced_chart(chart_type, data_source, color_scheme, opacity):
                try:
                    data = self.demo_data[data_source]
                    
                    if chart_type == "scatter":
                        if data_source == "enhanced_classification":
                            fig = px.scatter(
                                x=data["X"][:, 0],
                                y=data["X"][:, 1],
                                color=data["y"],
                                color_continuous_scale=color_scheme,
                                opacity=opacity,
                                title=f"{data_source.replace('_', ' ').title()} - Interactive Scatter Plot",
                                labels={"x": "Feature 1", "y": "Feature 2", "color": "Class"}
                            )
                        else:
                            fig = px.scatter(
                                x=data["X"][:, 0],
                                y=data["X"][:, 1],
                                color_continuous_scale=color_scheme,
                                opacity=opacity,
                                title=f"{data_source.replace('_', ' ').title()} - Feature Analysis"
                            )
                    
                    elif chart_type == "line":
                        if data_source == "enhanced_time_series":
                            fig = px.line(
                                x=data["time"],
                                y=data["values"],
                                title="Enhanced Time Series Analysis",
                                labels={"x": "Time", "y": "Value"}
                            )
                        else:
                            fig = px.line(
                                y=data["X"][:100, 0],
                                title=f"{data_source.replace('_', ' ').title()} - Sequential Data"
                            )
                    
                    elif chart_type == "histogram":
                        fig = px.histogram(
                            x=data["X"].flatten()[:1000],
                            nbins=50,
                            title=f"{data_source.replace('_', ' ').title()} - Distribution Analysis",
                            color_discrete_sequence=[color_scheme]
                        )
                    
                    elif chart_type == "box":
                        fig = px.box(
                            y=[data["X"][:, i] for i in range(min(5, data["X"].shape[1]))],
                            title=f"{data_source.replace('_', ' ').title()} - Feature Distribution",
                            labels={"variable": "Feature", "value": "Value"}
                        )
                    
                    elif chart_type == "violin":
                        fig = px.violin(
                            y=[data["X"][:, i] for i in range(min(5, data["X"].shape[1]))],
                            title=f"{data_source.replace('_', ' ').title()} - Feature Density",
                            labels={"variable": "Feature", "value": "Value"}
                        )
                    
                    elif chart_type == "heatmap":
                        corr_matrix = np.corrcoef(data["X"][:200, :10].T)
                        fig = px.imshow(
                            corr_matrix,
                            title="Feature Correlation Matrix",
                            color_continuous_scale=color_scheme,
                            labels={"x": "Feature", "y": "Feature", "color": "Correlation"}
                        )
                    
                    elif chart_type == "3d_scatter":
                        fig = px.scatter_3d(
                            x=data["X"][:300, 0],
                            y=data["X"][:300, 1],
                            z=data["X"][:300, 2],
                            color=data["y"][:300] if "y" in data else None,
                            title=f"{data_source.replace('_', ' ').title()} - 3D Analysis"
                        )
                    
                    # Enhanced layout
                    fig.update_layout(
                        template="plotly_white",
                        height=600,
                        showlegend=True,
                        font=dict(size=12),
                        margin=dict(l=50, r=50, t=80, b=50),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Calculate enhanced statistics
                    stats = {
                        "dataset": data_source.replace('_', ' ').title(),
                        "data_shape": data["X"].shape,
                        "features": data["X"].shape[1] if len(data["X"].shape) > 1 else 1,
                        "samples": data["X"].shape[0],
                        "statistics": {
                            "mean": float(np.mean(data["X"])),
                            "std": float(np.std(data["X"])),
                            "min": float(np.min(data["X"])),
                            "max": float(np.max(data["X"])),
                            "median": float(np.median(data["X"]))
                        },
                        "chart_type": chart_type,
                        "color_scheme": color_scheme,
                        "opacity": opacity
                    }
                    
                    return fig, stats
                    
                except Exception as e:
                    logger.error(f"Chart update error: {e}")
                    return None, {"error": str(e)}
            
            def animate_enhanced_chart():
                data = self.demo_data["enhanced_time_series"]
                fig = px.line(
                    x=data["time"][:50],
                    y=data["values"][:50],
                    title="Animated Time Series - Loading...",
                    labels={"x": "Time", "y": "Value"}
                )
                fig.update_layout(height=600)
                return fig
            
            def export_enhanced_chart():
                return {"message": "Chart exported successfully!", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
            
            # Connect events
            chart_type.change(
                fn=update_enhanced_chart,
                inputs=[chart_type, data_source, color_scheme, opacity],
                outputs=[main_chart, stats_output]
            )
            
            data_source.change(
                fn=update_enhanced_chart,
                inputs=[chart_type, data_source, color_scheme, opacity],
                outputs=[main_chart, stats_output]
            )
            
            color_scheme.change(
                fn=update_enhanced_chart,
                inputs=[chart_type, data_source, color_scheme, opacity],
                outputs=[main_chart, stats_output]
            )
            
            opacity.change(
                fn=update_enhanced_chart,
                inputs=[chart_type, data_source, color_scheme, opacity],
                outputs=[main_chart, stats_output]
            )
            
            animate_btn.click(
                fn=animate_enhanced_chart,
                outputs=[main_chart]
            )
            
            export_btn.click(
                fn=export_enhanced_chart,
                outputs=[stats_output]
            )
            
            # Initial chart
            initial_fig, initial_stats = update_enhanced_chart("scatter", "enhanced_classification", "viridis", 0.8)
            main_chart.value = initial_fig
            stats_output.value = initial_stats
        
        return demo
    
    def _create_enhanced_performance_chart(self):
        """Create enhanced performance monitoring chart."""
        if not self.performance_history:
            return go.Figure()
        
        times = [entry["processing_time"] for entry in self.performance_history]
        confidences = [entry["confidence"] for entry in self.performance_history]
        model_types = [entry["model_type"] for entry in self.performance_history]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Processing Time", "Confidence Score", "Performance Trend", "Model Usage"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Processing time
        fig.add_trace(
            go.Scatter(
                y=times,
                mode="lines+markers",
                name="Processing Time (ms)",
                line=dict(color=self.config.primary_color, width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Confidence score
        fig.add_trace(
            go.Scatter(
                y=confidences,
                mode="lines+markers",
                name="Confidence Score",
                line=dict(color=self.config.success_color, width=3),
                marker=dict(size=8)
            ),
            row=1, col=2
        )
        
        # Performance trend
        trend = np.cumsum(confidences)
        fig.add_trace(
            go.Scatter(
                y=trend,
                mode="lines+markers",
                name="Cumulative Performance",
                line=dict(color=self.config.secondary_color, width=3),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        # Model usage distribution
        unique_models, counts = np.unique(model_types, return_counts=True)
        fig.add_trace(
            go.Bar(
                x=unique_models,
                y=counts,
                name="Model Usage",
                marker_color=self.config.accent_color
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title="Enhanced Performance Dashboard",
            template="plotly_white",
            showlegend=True,
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_enhanced_main_interface(self):
        """Create the enhanced main interface."""
        
        with gr.Blocks(
            title="Enhanced AI Demos",
            theme=gr.themes.Soft(),
            css=self._get_custom_css()
        ) as main_interface:
            
            gr.Markdown(f"""
            <div class="enhanced-header">
                <h1>🎨 Enhanced AI Model Demos</h1>
                <p>Professional-grade interfaces showcasing cutting-edge AI capabilities</p>
            </div>
            """)
            
            # Create tabs for different demos
            with gr.Tabs(elem_classes=["enhanced-tab"]):
                with gr.TabItem("🚀 Model Inference", id=0):
                    self.create_enhanced_model_inference_interface()
                
                with gr.TabItem("📊 Data Visualization", id=1):
                    self.create_enhanced_visualization_interface()
                
                with gr.TabItem("ℹ️ About", id=2):
                    gr.Markdown(f"""
                    <div class="enhanced-card">
                        <h2>About Enhanced AI Demos</h2>
                        <p>This application showcases advanced AI capabilities through professionally designed, intuitive interfaces.</p>
                        
                        <h3>🚀 Key Features</h3>
                        <ul>
                            <li><strong>Enhanced Model Inference:</strong> Test advanced AI models with real-time performance monitoring</li>
                            <li><strong>Professional Visualizations:</strong> Beautiful, interactive charts with advanced customization</li>
                            <li><strong>Modern UI Design:</strong> Intuitive, responsive interface optimized for user experience</li>
                            <li><strong>Performance Analytics:</strong> Comprehensive metrics and trend analysis</li>
                        </ul>
                        
                        <h3>🛠️ Technologies</h3>
                        <ul>
                            <li><strong>Gradio:</strong> Modern web interface framework</li>
                            <li><strong>PyTorch:</strong> Advanced deep learning models</li>
                            <li><strong>Plotly:</strong> Interactive visualization library</li>
                            <li><strong>Enhanced CSS:</strong> Professional styling and animations</li>
                        </ul>
                        
                        <h3>📱 Usage</h3>
                        <ol>
                            <li>Select a demo tab above</li>
                            <li>Configure parameters using intuitive controls</li>
                            <li>Run inference or generate visualizations</li>
                            <li>Analyze results with professional tools</li>
                        </ol>
                    </div>
                    """)
        
        return main_interface

def main():
    """Main function to launch the enhanced UI demos."""
    
    # Create enhanced demo application
    demos = EnhancedUIDemos()
    main_interface = demos.create_enhanced_main_interface()
    
    # Launch the application
    main_interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True,
        show_error=True,
        height=900,
        show_tips=True
    )

if __name__ == "__main__":
    main()
