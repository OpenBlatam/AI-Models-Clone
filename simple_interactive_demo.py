"""
🎯 Simple Interactive Gradio Demo
=================================

A streamlined version of the interactive demos for quick testing and demonstration.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleInteractiveDemo:
    """Simplified interactive demo for quick testing."""
    
    def __init__(self):
        self.models = self._create_demo_models()
        self.demo_data = self._generate_demo_data()
        self.performance_history = []
    
    def _create_demo_models(self):
        """Create simple demo models."""
        models = {}
        
        # Simple classifier
        classifier = nn.Sequential(
            nn.Linear(5, 16),
            nn.ReLU(),
            nn.Linear(16, 3),
            nn.Softmax(dim=1)
        )
        models["classifier"] = classifier
        
        # Simple regressor
        regressor = nn.Sequential(
            nn.Linear(3, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )
        models["regressor"] = regressor
        
        return models
    
    def _generate_demo_data(self):
        """Generate simple demo data."""
        np.random.seed(42)
        
        # Classification data
        X_class = np.random.randn(100, 5)
        y_class = np.random.randint(0, 3, 100)
        
        # Regression data
        X_reg = np.random.randn(80, 3)
        y_reg = np.sum(X_reg * np.random.randn(3), axis=1) + np.random.randn(80) * 0.1
        
        # Time series data
        time_steps = np.linspace(0, 5, 50)
        time_series = np.sin(time_steps) + np.random.randn(50) * 0.2
        
        return {
            "classification": {"X": X_class, "y": y_class},
            "regression": {"X": X_reg, "y": y_reg},
            "time_series": {"time": time_steps, "values": time_series}
        }
    
    def run_model_inference(self, model_type, input_size, noise_level):
        """Run model inference with given parameters."""
        start_time = time.time()
        
        try:
            if model_type == "classifier":
                # Generate input data
                X = torch.randn(1, min(input_size, 5)) + noise_level * torch.randn(1, min(input_size, 5))
                model = self.models[model_type]
                
                with torch.no_grad():
                    output = model(X)
                    prediction = torch.argmax(output, dim=1).item()
                    confidence = torch.max(output, dim=1)[0].item()
                
                result = {
                    "model_type": "Classification",
                    "prediction": f"Class {prediction}",
                    "confidence": f"{confidence:.3f}",
                    "input_shape": X.shape,
                    "output_probabilities": output.squeeze().tolist()
                }
                
            elif model_type == "regressor":
                # Generate input data
                X = torch.randn(1, min(input_size, 3)) + noise_level * torch.randn(1, min(input_size, 3))
                model = self.models[model_type]
                
                with torch.no_grad():
                    output = model(X)
                    prediction = output.squeeze().item()
                
                result = {
                    "model_type": "Regression",
                    "prediction": f"{prediction:.3f}",
                    "input_shape": X.shape,
                    "input_features": X.squeeze().tolist()
                }
            
            processing_time = (time.time() - start_time) * 1000
            
            # Update performance history
            self.performance_history.append({
                "model_type": model_type,
                "processing_time": processing_time,
                "timestamp": time.time()
            })
            
            return result, processing_time, self._create_performance_chart()
            
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return {"error": str(e)}, 0.0, None
    
    def create_visualization(self, chart_type, data_source, color_scheme):
        """Create interactive visualization."""
        try:
            data = self.demo_data[data_source]
            
            if chart_type == "scatter":
                if data_source == "classification":
                    fig = px.scatter(
                        x=data["X"][:, 0],
                        y=data["X"][:, 1],
                        color=data["y"],
                        title=f"{data_source.title()} Scatter Plot",
                        color_continuous_scale=color_scheme
                    )
                else:
                    fig = px.scatter(
                        x=data["X"][:, 0],
                        y=data["X"][:, 1],
                        title=f"{data_source.title()} Scatter Plot",
                        color_continuous_scale=color_scheme
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
                        y=data["X"][:30, 0],
                        title=f"{data_source.title()} Line Plot"
                    )
            
            elif chart_type == "histogram":
                fig = px.histogram(
                    x=data["X"].flatten()[:200],
                    nbins=20,
                    title=f"{data_source.title()} Distribution",
                    color_discrete_sequence=[color_scheme]
                )
            
            elif chart_type == "bar":
                if data_source == "classification":
                    class_counts = np.bincount(data["y"])
                    fig = px.bar(
                        x=list(range(len(class_counts))),
                        y=class_counts,
                        title="Class Distribution"
                    )
                else:
                    fig = px.bar(
                        y=data["X"][:15, 0],
                        title=f"{data_source.title()} Bar Chart"
                    )
            
            # Update layout
            fig.update_layout(
                template="plotly_white",
                height=400,
                showlegend=True
            )
            
            # Calculate basic statistics
            stats = {
                "data_shape": data["X"].shape,
                "mean": float(np.mean(data["X"])),
                "std": float(np.std(data["X"])),
                "min": float(np.min(data["X"])),
                "max": float(np.max(data["X"]))
            }
            
            return fig, stats
            
        except Exception as e:
            logger.error(f"Visualization error: {e}")
            return None, {"error": str(e)}
    
    def _create_performance_chart(self):
        """Create performance monitoring chart."""
        if not self.performance_history:
            return go.Figure()
        
        times = [entry["processing_time"] for entry in self.performance_history]
        model_types = [entry["model_type"] for entry in self.performance_history]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            y=times,
            mode="lines+markers",
            name="Processing Time (ms)",
            line=dict(color="#1f77b4")
        ))
        
        fig.update_layout(
            title="Model Performance Over Time",
            xaxis_title="Inference Run",
            yaxis_title="Processing Time (ms)",
            template="plotly_white",
            height=300
        )
        
        return fig
    
    def create_interface(self):
        """Create the main Gradio interface."""
        
        with gr.Blocks(
            title="Simple Interactive AI Demo",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
                margin: 0 auto;
            }
            """
        ) as interface:
            
            gr.Markdown("# 🎯 Simple Interactive AI Demo")
            gr.Markdown("Quick demonstration of AI model inference and visualization capabilities")
            
            with gr.Tabs():
                # Tab 1: Model Inference
                with gr.TabItem("🤖 Model Inference"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("## Model Configuration")
                            
                            model_type = gr.Dropdown(
                                choices=["classifier", "regressor"],
                                value="classifier",
                                label="Model Type",
                                info="Choose a model to test"
                            )
                            
                            input_size = gr.Slider(
                                minimum=1, maximum=10, value=5, step=1,
                                label="Input Size",
                                info="Number of input features"
                            )
                            
                            noise_level = gr.Slider(
                                minimum=0.0, maximum=1.0, value=0.1, step=0.01,
                                label="Noise Level",
                                info="Add noise to input data"
                            )
                            
                            run_btn = gr.Button("🚀 Run Inference", variant="primary")
                            clear_btn = gr.Button("🗑️ Clear Results")
                        
                        with gr.Column(scale=2):
                            gr.Markdown("## Inference Results")
                            
                            inference_output = gr.JSON(label="Model Output")
                            processing_time = gr.Number(label="Processing Time (ms)")
                            performance_chart = gr.Plot(label="Performance History")
                    
                    # Event handlers for inference
                    def run_inference(model_type, input_size, noise_level):
                        return self.run_model_inference(model_type, input_size, noise_level)
                    
                    def clear_results():
                        return None, 0.0, None
                    
                    run_btn.click(
                        fn=run_inference,
                        inputs=[model_type, input_size, noise_level],
                        outputs=[inference_output, processing_time, performance_chart]
                    )
                    
                    clear_btn.click(
                        fn=clear_results,
                        outputs=[inference_output, processing_time, performance_chart]
                    )
                
                # Tab 2: Data Visualization
                with gr.TabItem("📊 Data Visualization"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("## Visualization Settings")
                            
                            chart_type = gr.Dropdown(
                                choices=["scatter", "line", "histogram", "bar"],
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
                                choices=["viridis", "plasma", "inferno", "magma"],
                                value="viridis",
                                label="Color Scheme",
                                info="Select color palette"
                            )
                        
                        with gr.Column(scale=2):
                            gr.Markdown("## Interactive Chart")
                            main_chart = gr.Plot(label="Dynamic Visualization")
                            
                            gr.Markdown("## Data Statistics")
                            stats_output = gr.JSON(label="Data Information")
                    
                    # Event handlers for visualization
                    def update_chart(chart_type, data_source, color_scheme):
                        return self.create_visualization(chart_type, data_source, color_scheme)
                    
                    # Connect events
                    chart_type.change(
                        fn=update_chart,
                        inputs=[chart_type, data_source, color_scheme],
                        outputs=[main_chart, stats_output]
                    )
                    
                    data_source.change(
                        fn=update_chart,
                        inputs=[chart_type, data_source, color_scheme],
                        outputs=[main_chart, stats_output]
                    )
                    
                    color_scheme.change(
                        fn=update_chart,
                        inputs=[chart_type, data_source, color_scheme],
                        outputs=[main_chart, stats_output]
                    )
                    
                    # Initial chart
                    initial_fig, initial_stats = self.create_visualization("scatter", "classification", "viridis")
                    main_chart.value = initial_fig
                    stats_output.value = initial_stats
                
                # Tab 3: About
                with gr.TabItem("ℹ️ About"):
                    gr.Markdown("""
                    ## Simple Interactive AI Demo
                    
                    This is a streamlined version of the interactive AI demos that showcases:
                    
                    ### 🚀 Features
                    - **Model Inference**: Test classification and regression models
                    - **Data Visualization**: Interactive charts with various data types
                    - **Performance Monitoring**: Track inference times and model performance
                    - **Real-time Updates**: Dynamic parameter adjustment and visualization
                    
                    ### 🛠️ Technologies
                    - **Gradio**: Modern web interface
                    - **PyTorch**: Deep learning models
                    - **Plotly**: Interactive charts
                    - **NumPy**: Data manipulation
                    
                    ### 📱 Usage
                    1. Select a demo tab above
                    2. Adjust parameters using the controls
                    3. Run inference or generate visualizations
                    4. Monitor performance and analyze results
                    """)
        
        return interface

def main():
    """Main function to launch the simple demo."""
    
    # Create demo application
    demo = SimpleInteractiveDemo()
    interface = demo.create_interface()
    
    # Launch the application
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True,
        show_error=True,
        height=700
    )

if __name__ == "__main__":
    main()
