# Interactive Demo System Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Demo Configuration](#demo-configuration)
4. [Model Inference Demos](#model-inference-demos)
5. [Visualization Demos](#visualization-demos)
6. [Experiment Demos](#experiment-demos)
7. [Demo System Management](#demo-system-management)
8. [Custom Demo Creation](#custom-demo-creation)
9. [Deployment and Hosting](#deployment-and-hosting)
10. [Best Practices](#best-practices)
11. [Examples](#examples)
12. [Troubleshooting](#troubleshooting)

## System Overview

The Interactive Demo System provides comprehensive web-based interfaces using Gradio for exploring and demonstrating all capabilities of the AI/ML framework. It offers user-friendly, interactive demos for model inference, visualization, and experimentation.

### Key Features

- **Web-Based Interfaces**: Interactive demos accessible through web browsers
- **Model Inference**: Real-time text generation, image generation, and classification
- **Visualization Tools**: Interactive plots and charts for training analysis
- **Experiment Management**: Hyperparameter tuning and model comparison
- **User-Friendly Design**: Intuitive interfaces with examples and documentation
- **Real-Time Processing**: Live model inference and visualization updates
- **Customizable**: Easy to extend and customize for specific use cases
- **Production Ready**: Built for deployment and public access

## Core Components

### 1. DemoConfig

Configuration management for all demo components:

```python
from interactive_demo_system import DemoConfig

config = DemoConfig()
config.demo_port = 7860
config.demo_host = "0.0.0.0"
config.demo_share = False
config.demo_debug = False
config.demo_show_error = True

# Paths
config.models_path = "./models"
config.data_path = "./data"
config.demos_path = "./demos"

# Performance settings
config.max_examples = 10
config.batch_size = 1
config.device = "cpu"

# Visualization settings
config.plot_theme = "plotly_white"
config.figure_size = (800, 600)
config.dpi = 100
```

### 2. ModelInferenceDemo

Interactive demos for model inference:

```python
from interactive_demo_system import ModelInferenceDemo

model_demo = ModelInferenceDemo(config)

# Create text generation demo
text_demo = model_demo.create_text_generation_demo()

# Create image generation demo
image_demo = model_demo.create_image_generation_demo()

# Create classification demo
classification_demo = model_demo.create_classification_demo()
```

### 3. VisualizationDemo

Interactive visualization tools:

```python
from interactive_demo_system import VisualizationDemo

viz_demo = VisualizationDemo(config)

# Create training visualization demo
training_viz = viz_demo.create_training_visualization_demo()

# Create model comparison demo
model_comp = viz_demo.create_model_comparison_demo()
```

### 4. ExperimentDemo

Interactive experiment management:

```python
from interactive_demo_system import ExperimentDemo

exp_demo = ExperimentDemo(config)

# Create hyperparameter tuning demo
hp_tuning = exp_demo.create_hyperparameter_tuning_demo()
```

### 5. InteractiveDemoSystem

Main demo system orchestrator:

```python
from interactive_demo_system import InteractiveDemoSystem

demo_system = InteractiveDemoSystem(config)

# Launch the complete demo system
demo_system.launch(share=True, debug=False)
```

## Demo Configuration

### 1. Server Configuration

```python
config = DemoConfig()

# Server settings
config.demo_port = 7860          # Port for the demo server
config.demo_host = "0.0.0.0"     # Host address (0.0.0.0 for all interfaces)
config.demo_share = False         # Enable public sharing
config.demo_debug = False         # Enable debug mode
config.demo_show_error = True     # Show error messages
```

### 2. Performance Configuration

```python
# Performance settings
config.max_examples = 10          # Maximum examples per demo
config.batch_size = 1             # Batch size for inference
config.device = "cpu"             # Device for model inference (cpu, cuda, mps)
```

### 3. Visualization Configuration

```python
# Visualization settings
config.plot_theme = "plotly_white"    # Plot theme (plotly_white, plotly_dark, etc.)
config.figure_size = (800, 600)       # Default figure size
config.dpi = 100                      # Figure DPI
```

### 4. Path Configuration

```python
# Path settings
config.models_path = "./models"       # Path for model storage
config.data_path = "./data"           # Path for data storage
config.demos_path = "./demos"         # Path for demo assets
```

## Model Inference Demos

### 1. Text Generation Demo

Interactive text generation with different models and parameters:

```python
from interactive_demo_system import ModelInferenceDemo

model_demo = ModelInferenceDemo(config)
text_demo = model_demo.create_text_generation_demo()

# Demo features:
# - Multiple model types (GPT-2 Style, BERT Style, Transformer, Basic)
# - Adjustable parameters (max_length, temperature, top_p, top_k)
# - Real-time generation
# - Example prompts
```

**Usage Example:**
```python
# Generate text with custom parameters
result = text_demo.fn(
    prompt="The future of artificial intelligence",
    max_length=100,
    temperature=0.7,
    model_type="GPT-2 Style",
    top_p=0.9,
    top_k=50
)
print(result)
```

### 2. Image Generation Demo

Interactive image generation using diffusion models:

```python
image_demo = model_demo.create_image_generation_demo()

# Demo features:
# - Text-to-image generation
# - Adjustable image sizes (256x256, 512x512, 768x768, 1024x1024)
# - Configurable generation parameters (steps, guidance scale, seed)
# - Real-time image generation
# - Metadata output
```

**Usage Example:**
```python
# Generate image with custom parameters
img_result, metadata = image_demo.fn(
    prompt="A beautiful sunset over mountains",
    image_size="512x512",
    num_steps=50,
    guidance_scale=7.5,
    seed=42
)

# img_result is a numpy array (image)
# metadata is a JSON string with generation details
```

### 3. Text Classification Demo

Interactive text classification with different models:

```python
classification_demo = model_demo.create_classification_demo()

# Demo features:
# - Multiple classification types (Sentiment Analysis, Topic Classification, Language Detection)
# - Real-time classification
# - Confidence scores and detailed analysis
# - Example texts
```

**Usage Example:**
```python
# Classify text sentiment
result = classification_demo.fn(
    text="I love this amazing product! It's wonderful and makes me so happy.",
    model_type="Sentiment Analysis"
)

# Result includes:
# - sentiment: "Positive"
# - confidence: 0.85
# - positive_score: 3
# - negative_score: 0
# - analysis: "Detected positive sentiment with 85.0% confidence."
```

## Visualization Demos

### 1. Training Visualization Demo

Interactive training progress visualization:

```python
from interactive_demo_system import VisualizationDemo

viz_demo = VisualizationDemo(config)
training_viz = viz_demo.create_training_visualization_demo()

# Demo features:
# - Training and validation loss plots
# - Accuracy progression plots
# - Learning rate schedule visualization
# - Interactive parameter adjustment
# - Real-time plot generation
```

**Usage Example:**
```python
# Generate training visualization
loss_fig, acc_fig, lr_fig = training_viz.fn(
    epochs=20,
    learning_rate=0.01,
    batch_size=32,
    model_type="CNN",
    dataset_size=10000
)

# Returns three Plotly figures:
# - loss_fig: Training and validation loss
# - acc_fig: Training accuracy
# - lr_fig: Learning rate schedule
```

### 2. Model Comparison Demo

Interactive model comparison and analysis:

```python
model_comp = viz_demo.create_model_comparison_demo()

# Demo features:
# - Multiple datasets (MNIST, CIFAR-10, IMDB, SST-2, AG News)
# - Multiple metrics (accuracy, precision, recall, f1_score)
# - Multiple models (CNN, RNN, Transformer, MLP, BERT, GPT)
# - Interactive comparison charts
# - Performance analysis
```

**Usage Example:**
```python
# Compare models on different datasets
fig = model_comp.fn(
    dataset="MNIST",
    metric="accuracy",
    models=["CNN", "RNN", "Transformer"]
)

# Returns a Plotly figure with model comparison
```

## Experiment Demos

### 1. Hyperparameter Tuning Demo

Interactive hyperparameter exploration:

```python
from interactive_demo_system import ExperimentDemo

exp_demo = ExperimentDemo(config)
hp_tuning = exp_demo.create_hyperparameter_tuning_demo()

# Demo features:
# - Multiple learning rates
# - Multiple batch sizes
# - Multiple model types
# - Interactive heatmaps
# - Detailed results table
# - Performance analysis
```

**Usage Example:**
```python
# Perform hyperparameter tuning
heatmap_fig, results_df = hp_tuning.fn(
    learning_rates=[0.001, 0.01, 0.05],
    batch_sizes=[32, 64, 128],
    model_types=["CNN", "Transformer"],
    epochs=20
)

# Returns:
# - heatmap_fig: Interactive heatmap of results
# - results_df: Detailed DataFrame with all results
```

## Demo System Management

### 1. Complete Demo System

Launch the complete interactive demo system:

```python
from interactive_demo_system import InteractiveDemoSystem

# Create demo system
demo_system = InteractiveDemoSystem(config)

# Launch with all demos
demo_system.launch(share=True, debug=False)
```

### 2. Quick Demo Creation

Create specific types of demos:

```python
from interactive_demo_system import create_quick_demo, launch_demo

# Create specific demo types
text_demo = create_quick_demo("text")      # Text generation only
image_demo = create_quick_demo("image")    # Image generation only
viz_demo = create_quick_demo("visualization")  # Visualization only
exp_demo = create_quick_demo("experiment")     # Experiments only
all_demo = create_quick_demo("all")        # All demos

# Quick launch
launch_demo("all", share=True, debug=False)
```

### 3. Demo System Structure

The demo system is organized into tabs:

```
🤖 AI/ML Framework Interactive Demos
├── 🎯 Model Inference
│   ├── Text Generation
│   ├── Image Generation
│   └── Text Classification
├── 📊 Visualization
│   ├── Training Visualization
│   └── Model Comparison
├── 🧪 Experiments
│   └── Hyperparameter Tuning
└── ℹ️ Framework Info
    └── Framework Overview
```

## Custom Demo Creation

### 1. Creating Custom Demos

Extend the demo system with custom functionality:

```python
class CustomDemo:
    def __init__(self, config: DemoConfig):
        self.config = config
    
    def create_custom_demo(self) -> gr.Interface:
        def custom_function(input_text: str, parameter: float) -> str:
            # Custom logic here
            return f"Processed: {input_text} with parameter {parameter}"
        
        interface = gr.Interface(
            fn=custom_function,
            inputs=[
                gr.Textbox(label="Input Text"),
                gr.Slider(minimum=0, maximum=1, value=0.5, label="Parameter")
            ],
            outputs=gr.Textbox(label="Output"),
            title="Custom Demo",
            description="A custom demo for specific functionality."
        )
        
        return interface
```

### 2. Integrating Custom Demos

Add custom demos to the main system:

```python
class ExtendedInteractiveDemoSystem(InteractiveDemoSystem):
    def __init__(self, config: DemoConfig = None):
        super().__init__(config)
        self.custom_demo = CustomDemo(config)
    
    def _create_demo_blocks(self) -> gr.Blocks:
        with gr.Blocks(title="Extended AI/ML Framework Demos") as blocks:
            # ... existing tabs ...
            
            # Add custom tab
            with gr.Tab("🔧 Custom"):
                custom_interface = self.custom_demo.create_custom_demo()
        
        return blocks
```

### 3. Custom Visualization

Create custom visualization demos:

```python
def create_custom_visualization_demo(self) -> gr.Interface:
    def custom_plot(data_type: str, size: int) -> go.Figure:
        # Generate custom data
        x = np.linspace(0, 10, size)
        if data_type == "sine":
            y = np.sin(x)
        elif data_type == "cosine":
            y = np.cos(x)
        else:
            y = x ** 2
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers'))
        fig.update_layout(
            title=f'Custom {data_type} Plot',
            xaxis_title='X',
            yaxis_title='Y',
            template=self.config.plot_theme
        )
        return fig
    
    interface = gr.Interface(
        fn=custom_plot,
        inputs=[
            gr.Dropdown(choices=["sine", "cosine", "quadratic"], value="sine"),
            gr.Slider(minimum=10, maximum=1000, value=100, step=10)
        ],
        outputs=gr.Plot(),
        title="Custom Visualization Demo"
    )
    
    return interface
```

## Deployment and Hosting

### 1. Local Deployment

Deploy demos locally for development:

```python
# Basic local deployment
demo_system = InteractiveDemoSystem()
demo_system.launch(share=False, debug=True)

# Local deployment with custom settings
config = DemoConfig()
config.demo_port = 8080
config.demo_host = "127.0.0.1"
config.demo_debug = True

demo_system = InteractiveDemoSystem(config)
demo_system.launch(share=False, debug=True)
```

### 2. Public Deployment

Deploy demos for public access:

```python
# Public deployment with sharing
demo_system = InteractiveDemoSystem()
demo_system.launch(share=True, debug=False)

# Custom public deployment
config = DemoConfig()
config.demo_share = True
config.demo_port = 7860

demo_system = InteractiveDemoSystem(config)
demo_system.launch(share=True, debug=False)
```

### 3. Production Deployment

Deploy demos in production environments:

```python
# Production configuration
config = DemoConfig()
config.demo_host = "0.0.0.0"
config.demo_port = 7860
config.demo_share = False
config.demo_debug = False
config.demo_show_error = False

# Use with production servers (Gunicorn, uWSGI, etc.)
demo_system = InteractiveDemoSystem(config)

# For production, you might want to use Gradio's built-in server
# or integrate with Flask/FastAPI
```

### 4. Docker Deployment

Deploy demos using Docker:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy demo system
COPY interactive_demo_system.py .
COPY integration_system.py .
# ... copy other framework files

# Expose port
EXPOSE 7860

# Run demo
CMD ["python", "interactive_demo_system.py"]
```

```bash
# Build and run Docker container
docker build -t ai-ml-demos .
docker run -p 7860:7860 ai-ml-demos
```

## Best Practices

### 1. Demo Design

```python
# Good demo design practices
def create_well_designed_demo(self) -> gr.Interface:
    def demo_function(input_param: str, numeric_param: float) -> Dict[str, Any]:
        try:
            # Process input
            result = self.process_input(input_param, numeric_param)
            
            # Return structured output
            return {
                "status": "success",
                "result": result,
                "metadata": {
                    "input_param": input_param,
                    "numeric_param": numeric_param,
                    "processing_time": time.time()
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "metadata": {}
            }
    
    interface = gr.Interface(
        fn=demo_function,
        inputs=[
            gr.Textbox(
                label="Input Parameter",
                placeholder="Enter your input here...",
                lines=2
            ),
            gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.5,
                step=0.1,
                label="Numeric Parameter"
            )
        ],
        outputs=gr.JSON(label="Results"),
        title="Well-Designed Demo",
        description="A demo following best practices.",
        examples=[
            ["Example input 1", 0.3],
            ["Example input 2", 0.7]
        ]
    )
    
    return interface
```

### 2. Error Handling

```python
# Robust error handling in demos
def create_robust_demo(self) -> gr.Interface:
    def robust_function(input_data: str) -> str:
        try:
            # Validate input
            if not input_data.strip():
                return "Error: Please provide input data."
            
            # Process input
            result = self.process_data(input_data)
            
            # Validate output
            if result is None:
                return "Error: Processing failed."
            
            return f"Success: {result}"
            
        except ValueError as e:
            return f"Validation Error: {str(e)}"
        except Exception as e:
            return f"Processing Error: {str(e)}"
    
    interface = gr.Interface(
        fn=robust_function,
        inputs=gr.Textbox(label="Input Data"),
        outputs=gr.Textbox(label="Result"),
        title="Robust Demo"
    )
    
    return interface
```

### 3. Performance Optimization

```python
# Performance optimization for demos
class OptimizedDemo:
    def __init__(self, config: DemoConfig):
        self.config = config
        self.cache = {}  # Simple caching
    
    def create_optimized_demo(self) -> gr.Interface:
        def optimized_function(input_data: str, use_cache: bool = True) -> str:
            # Check cache
            if use_cache and input_data in self.cache:
                return f"Cached result: {self.cache[input_data]}"
            
            # Process data
            result = self.process_data(input_data)
            
            # Cache result
            if use_cache:
                self.cache[input_data] = result
            
            return f"Processed: {result}"
        
        interface = gr.Interface(
            fn=optimized_function,
            inputs=[
                gr.Textbox(label="Input Data"),
                gr.Checkbox(label="Use Cache", value=True)
            ],
            outputs=gr.Textbox(label="Result"),
            title="Optimized Demo"
        )
        
        return interface
```

## Examples

### 1. Complete Demo System

```python
from interactive_demo_system import InteractiveDemoSystem, DemoConfig

# Create configuration
config = DemoConfig()
config.demo_port = 7860
config.demo_share = True
config.demo_debug = False

# Create and launch demo system
demo_system = InteractiveDemoSystem(config)
demo_system.launch(share=True, debug=False)
```

### 2. Custom Text Generation Demo

```python
from interactive_demo_system import ModelInferenceDemo, DemoConfig

config = DemoConfig()
model_demo = ModelInferenceDemo(config)

# Create custom text generation demo
def custom_text_generation(prompt: str, style: str, length: int) -> str:
    styles = {
        "formal": "formal and professional",
        "casual": "casual and friendly",
        "technical": "technical and detailed"
    }
    
    style_desc = styles.get(style, "neutral")
    return f"Generated text in {style_desc} style: {prompt} [continued...]"

# Create interface
import gradio as gr

interface = gr.Interface(
    fn=custom_text_generation,
    inputs=[
        gr.Textbox(label="Prompt", placeholder="Enter your prompt..."),
        gr.Dropdown(choices=["formal", "casual", "technical"], value="formal"),
        gr.Slider(minimum=10, maximum=200, value=50, step=10)
    ],
    outputs=gr.Textbox(label="Generated Text"),
    title="Custom Text Generation",
    description="Generate text in different styles."
)

interface.launch()
```

### 3. Advanced Visualization Demo

```python
from interactive_demo_system import VisualizationDemo, DemoConfig
import plotly.graph_objects as go
import numpy as np

config = DemoConfig()
viz_demo = VisualizationDemo(config)

# Create advanced visualization
def advanced_visualization(data_type: str, complexity: int) -> go.Figure:
    x = np.linspace(0, 10, 100)
    
    if data_type == "multi_series":
        fig = go.Figure()
        for i in range(complexity):
            y = np.sin(x + i * 0.5) * np.exp(-x / 5)
            fig.add_trace(go.Scatter(
                x=x, y=y, 
                mode='lines', 
                name=f'Series {i+1}'
            ))
    else:
        y = np.sin(x) * np.exp(-x / complexity)
        fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines'))
    
    fig.update_layout(
        title=f'Advanced {data_type} Visualization',
        xaxis_title='X',
        yaxis_title='Y',
        template=config.plot_theme
    )
    
    return fig

# Create interface
interface = gr.Interface(
    fn=advanced_visualization,
    inputs=[
        gr.Dropdown(choices=["single", "multi_series"], value="single"),
        gr.Slider(minimum=1, maximum=10, value=5, step=1)
    ],
    outputs=gr.Plot(),
    title="Advanced Visualization Demo"
)

interface.launch()
```

### 4. Interactive Experiment Demo

```python
from interactive_demo_system import ExperimentDemo, DemoConfig
import pandas as pd

config = DemoConfig()
exp_demo = ExperimentDemo(config)

# Create interactive experiment
def interactive_experiment(experiment_type: str, iterations: int) -> Tuple[go.Figure, pd.DataFrame]:
    # Simulate experiment results
    results = []
    for i in range(iterations):
        result = {
            'iteration': i + 1,
            'performance': np.random.normal(0.8, 0.1),
            'time': np.random.exponential(1.0),
            'accuracy': np.random.beta(8, 2)
        }
        results.append(result)
    
    df = pd.DataFrame(results)
    
    # Create visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['iteration'], 
        y=df['performance'],
        mode='lines+markers',
        name='Performance'
    ))
    fig.update_layout(
        title=f'{experiment_type} Experiment Results',
        xaxis_title='Iteration',
        yaxis_title='Performance',
        template=config.plot_theme
    )
    
    return fig, df

# Create interface
interface = gr.Interface(
    fn=interactive_experiment,
    inputs=[
        gr.Dropdown(choices=["Training", "Optimization", "Evaluation"], value="Training"),
        gr.Slider(minimum=5, maximum=50, value=20, step=5)
    ],
    outputs=[
        gr.Plot(label="Experiment Results"),
        gr.Dataframe(label="Detailed Data")
    ],
    title="Interactive Experiment Demo"
)

interface.launch()
```

## Troubleshooting

### Common Issues

1. **Demo Not Launching**
   ```python
   # Check port availability
   config = DemoConfig()
   config.demo_port = 7861  # Try different port
   
   # Check host settings
   config.demo_host = "127.0.0.1"  # Use localhost only
   
   # Enable debug mode
   config.demo_debug = True
   ```

2. **Model Loading Issues**
   ```python
   # Check model paths
   config.models_path = "./models"
   config.data_path = "./data"
   
   # Ensure directories exist
   import os
   os.makedirs(config.models_path, exist_ok=True)
   os.makedirs(config.data_path, exist_ok=True)
   ```

3. **Performance Issues**
   ```python
   # Optimize performance settings
   config.max_examples = 5  # Reduce examples
   config.batch_size = 1    # Use smaller batches
   config.device = "cpu"    # Use CPU if GPU is slow
   ```

4. **Visualization Issues**
   ```python
   # Check visualization settings
   config.plot_theme = "plotly_white"
   config.figure_size = (600, 400)  # Smaller figures
   config.dpi = 72  # Lower DPI
   ```

### Debug Mode

Enable debug mode for troubleshooting:

```python
config = DemoConfig()
config.demo_debug = True
config.demo_show_error = True

demo_system = InteractiveDemoSystem(config)
demo_system.launch(debug=True)
```

### Error Logging

Add error logging to demos:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def demo_with_logging(input_data: str) -> str:
    try:
        logger.info(f"Processing input: {input_data}")
        result = process_data(input_data)
        logger.info(f"Processing successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return f"Error: {str(e)}"
```

This comprehensive guide covers all aspects of the Interactive Demo System, from basic usage to advanced customization and deployment. The system provides user-friendly interfaces for exploring all capabilities of the AI/ML framework. 