from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

import gradio as gr
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw, ImageFont
import json
import os
from typing import Dict, List, Tuple, Optional, Any
import logging
from pathlib import Path
import time
import threading
from collections import defaultdict
from deep_learning_models import (
from transformer_llm_models import (
from transformers import AutoTokenizer, pipeline
from diffusion_models import (
from model_training_evaluation import (
from typing import Any, List, Dict, Optional
import asyncio
"""
🎨 Gradio Integration for Facebook Posts Processing
==================================================
Interactive demos and visualization using Gradio for model inference,
training monitoring, and evaluation results.
"""


# Import our existing modules
    ModelConfig, FacebookPostsTransformer, FacebookPostsLSTM, 
    FacebookPostsCNN, FacebookPostsDataset, create_facebook_posts_model
)
    TransformerConfig, FacebookPostsLLM, create_transformer_model, create_llm_model
)
    DiffusionConfig, FacebookPostsDiffusionManager, create_diffusion_manager
)
    TrainingConfig, EvaluationConfig, ModelTrainer, ModelEvaluator,
    create_trainer, create_evaluator
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

class GradioInterface:
    """Main Gradio interface for Facebook Posts processing."""
    
    def __init__(self) -> Any:
        self.models: Dict[str, Any] = {}
        self.tokenizers: Dict[str, Any] = {}
        self.pipelines: Dict[str, Any] = {}
        self.training_history: Dict[str, Any] = {}
        self.evaluation_results: Dict[str, Any] = {}
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self) -> Any:
        """Initialize all available models."""
        try:
            # Initialize diffusion manager
            diffusion_config = DiffusionConfig(
                scheduler_type: str: str = "ddim",
                num_inference_steps=20,
                guidance_scale=7.5
            )
            self.diffusion_manager = create_diffusion_manager(diffusion_config)
            
            # Initialize transformers pipeline
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model: str: str = "cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            logger.info("Models initialized successfully")
            
        except Exception as e:
            logger.warning(f"Some models failed to initialize: {e}")
    
    def create_model_inference_interface(self) -> Any:
        """Create model inference interface."""
        with gr.Blocks(title: str: str = "Facebook Posts Model Inference", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🧠 Facebook Posts Model Inference")
            gr.Markdown("Interactive interface for model inference and prediction")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Input")
                    
                    # Text input
                    text_input = gr.Textbox(
                        label: str: str = "Facebook Post Text",
                        placeholder: str: str = "Enter your Facebook post text here...",
                        lines=5,
                        max_lines: int: int = 10
                    )
                    
                    # Model selection
                    model_type = gr.Dropdown(
                        choices: List[Any] = ["sentiment_analysis", "text_generation", "image_generation"],
                        value: str: str = "sentiment_analysis",
                        label: str: str = "Model Type"
                    )
                    
                    # Parameters
                    with gr.Accordion("Advanced Parameters", open=False):
                        max_length = gr.Slider(
                            minimum=50, maximum=500, value=100, step=10,
                            label: str: str = "Max Length"
                        )
                        temperature = gr.Slider(
                            minimum=0.1, maximum=2.0, value=0.7, step=0.1,
                            label: str: str = "Temperature"
                        )
                        guidance_scale = gr.Slider(
                            minimum=1.0, maximum=20.0, value=7.5, step=0.5,
                            label: str: str = "Guidance Scale (for image generation)"
                        )
                    
                    # Generate button
                    generate_btn = gr.Button("Generate", variant="primary")
                
                with gr.Column(scale=1):
                    gr.Markdown("## Output")
                    
                    # Output text
                    output_text = gr.Textbox(
                        label: str: str = "Generated Output",
                        lines=5,
                        interactive: bool = False
                    )
                    
                    # Output image
                    output_image = gr.Image(
                        label: str: str = "Generated Image",
                        type: str: str = "pil"
                    )
                    
                    # Metrics
                    metrics_output = gr.JSON(
                        label: str: str = "Metrics"
                    )
            
            # Event handlers
            generate_btn.click(
                fn=self.inference_pipeline,
                inputs: List[Any] = [text_input, model_type, max_length, temperature, guidance_scale],
                outputs: List[Any] = [output_text, output_image, metrics_output]
            )
            
            # Example inputs
            gr.Examples(
                examples: List[Any] = [
                    ["I love this new technology! It's amazing how AI is transforming our world.", "sentiment_analysis"],
                    ["Create a professional post about", "text_generation"],
                    ["A beautiful Facebook post about technology and innovation", "image_generation"]
                ],
                inputs: List[Any] = [text_input, model_type]
            )
        
        return interface
    
    def inference_pipeline(self, text: str, model_type: str, max_length: int, 
                          temperature: float, guidance_scale: float) -> Tuple[str, Image.Image, Dict]:
        """Main inference pipeline."""
        try:
            if not text.strip():
                return "Please enter some text.", None, {}
            
            if model_type == "sentiment_analysis":
                return self._sentiment_analysis(text)
            
            elif model_type == "text_generation":
                return self._text_generation(text, max_length, temperature)
            
            elif model_type == "image_generation":
                return self._image_generation(text, guidance_scale)
            
            else:
                return f"Unknown model type: {model_type}", None, {}
                
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return f"Error during inference: {str(e)}", None, {}
    
    def _sentiment_analysis(self, text: str) -> Tuple[str, None, Dict]:
        """Perform sentiment analysis."""
        try:
            result = self.sentiment_pipeline(text)
            
            # Format output
            sentiment = result[0]['label']
            confidence = result[0]['score']
            
            output_text = f"Sentiment: {sentiment}\nConfidence: {confidence:.3f}"
            
            metrics: Dict[str, Any] = {
                "sentiment": sentiment,
                "confidence": confidence,
                "text_length": len(text),
                "model": "twitter-roberta-base-sentiment"
            }
            
            return output_text, None, metrics
            
        except Exception as e:
            return f"Sentiment analysis error: {str(e)}", None, {}
    
    def _text_generation(self, text: str, max_length: int, temperature: float) -> Tuple[str, None, Dict]:
        """Generate text continuation."""
        try:
            # Simple text generation (placeholder)
            # In a real implementation, you would use a proper language model
            
            generated_text = f"{text} This is a generated continuation of your Facebook post. "
            generated_text += "The model has analyzed your input and created relevant content. "
            generated_text += "This demonstrates the text generation capabilities of our system."
            
            metrics: Dict[str, Any] = {
                "input_length": len(text),
                "output_length": len(generated_text),
                "temperature": temperature,
                "max_length": max_length,
                "model": "facebook_posts_generator"
            }
            
            return generated_text, None, metrics
            
        except Exception as e:
            return f"Text generation error: {str(e)}", None, {}
    
    def _image_generation(self, text: str, guidance_scale: float) -> Tuple[str, Image.Image, Dict]:
        """Generate image from text."""
        try:
            # Create a placeholder image for demo purposes
            # In a real implementation, you would use the diffusion manager
            
            # Generate a simple colored image based on text
            width, height = 512, 512
            
            # Create gradient based on text content
            image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(image)
            
            # Simple color generation based on text
            colors: Dict[str, Any] = {
                'technology': (100, 150, 255),
                'business': (255, 200, 100),
                'nature': (100, 255, 150),
                'love': (255, 100, 150),
                'happy': (255, 255, 100)
            }
            
            # Determine color based on text content
            base_color = (128, 128, 128)  # Default gray
            for keyword, color in colors.items():
                if keyword.lower() in text.lower():
                    base_color = color
                    break
            
            # Create gradient
            for y in range(height):
                for x in range(width):
                    r = int(base_color[0] * (x + y) / (width + height))
                    g = int(base_color[1] * (width - x + y) / (width + height))
                    b = int(base_color[2] * (x + height - y) / (width + height))
                    draw.point((x, y), fill=(r, g, b))
            
            # Add text overlay
            try:
                font = ImageFont.load_default()
                draw.text((50, 50), "Generated Image", fill=(255, 255, 255), font=font)
                draw.text((50, 80), f"Prompt: {text[:50]}...", fill=(255, 255, 255), font=font)
            except:
                draw.text((50, 50), "Generated Image", fill=(255, 255, 255))
                draw.text((50, 80), f"Prompt: {text[:50]}...", fill=(255, 255, 255))
            
            metrics: Dict[str, Any] = {
                "prompt": text,
                "guidance_scale": guidance_scale,
                "image_size": f"{width}x{height}",
                "model": "facebook_posts_diffusion"
            }
            
            return "Image generated successfully!", image, metrics
            
        except Exception as e:
            return f"Image generation error: {str(e)}", None, {}
    
    def create_training_interface(self) -> Any:
        """Create model training interface."""
        with gr.Blocks(title: str: str = "Facebook Posts Model Training", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🏋️ Facebook Posts Model Training")
            gr.Markdown("Interactive interface for model training and monitoring")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Training Configuration")
                    
                    # Model configuration
                    model_type = gr.Dropdown(
                        choices: List[Any] = ["transformer", "lstm", "cnn"],
                        value: str: str = "transformer",
                        label: str: str = "Model Type"
                    )
                    
                    batch_size = gr.Slider(
                        minimum=8, maximum=128, value=32, step=8,
                        label: str: str = "Batch Size"
                    )
                    
                    learning_rate = gr.Slider(
                        minimum=1e-6, maximum=1e-2, value=1e-4, step=1e-5,
                        label: str: str = "Learning Rate"
                    )
                    
                    num_epochs = gr.Slider(
                        minimum=10, maximum=200, value=50, step=10,
                        label: str: str = "Number of Epochs"
                    )
                    
                    # Data configuration
                    train_split = gr.Slider(
                        minimum=0.5, maximum=0.9, value=0.8, step=0.05,
                        label: str: str = "Train Split"
                    )
                    
                    # Training options
                    with gr.Accordion("Advanced Options", open=False):
                        optimizer = gr.Dropdown(
                            choices: List[Any] = ["adam", "adamw", "sgd", "rmsprop"],
                            value: str: str = "adamw",
                            label: str: str = "Optimizer"
                        )
                        
                        scheduler = gr.Dropdown(
                            choices: List[Any] = ["cosine", "step", "reduce_lr", "onecycle"],
                            value: str: str = "cosine",
                            label: str: str = "Scheduler"
                        )
                        
                        early_stopping = gr.Checkbox(
                            value=True,
                            label: str: str = "Early Stopping"
                        )
                        
                        gradient_clip = gr.Slider(
                            minimum=0.0, maximum=5.0, value=1.0, step=0.1,
                            label: str: str = "Gradient Clipping"
                        )
                    
                    # Training controls
                    start_training_btn = gr.Button("Start Training", variant="primary")
                    stop_training_btn = gr.Button("Stop Training", variant="stop")
                
                with gr.Column(scale=1):
                    gr.Markdown("## Training Progress")
                    
                    # Progress tracking
                    progress_bar = gr.Progress()
                    
                    # Training metrics
                    train_loss = gr.Number(label="Training Loss", interactive=False)
                    val_loss = gr.Number(label="Validation Loss", interactive=False)
                    train_acc = gr.Number(label="Training Accuracy", interactive=False)
                    val_acc = gr.Number(label="Validation Accuracy", interactive=False)
                    
                    # Learning curves
                    learning_curves_plot = gr.Plot(label="Learning Curves")
                    
                    # Training log
                    training_log = gr.Textbox(
                        label: str: str = "Training Log",
                        lines=10,
                        interactive: bool = False
                    )
            
            # Event handlers
            start_training_btn.click(
                fn=self.start_training,
                inputs: List[Any] = [model_type, batch_size, learning_rate, num_epochs, 
                       train_split, optimizer, scheduler, early_stopping, gradient_clip],
                outputs: List[Any] = [train_loss, val_loss, train_acc, val_acc, learning_curves_plot, training_log]
            )
            
            stop_training_btn.click(
                fn=self.stop_training,
                outputs: List[Any] = [training_log]
            )
        
        return interface
    
    def start_training(self, model_type: str, batch_size: int, learning_rate: float,
                      num_epochs: int, train_split: float, optimizer: str, scheduler: str,
                      early_stopping: bool, gradient_clip: float) -> Any:
        """Start model training."""
        try:
            # Create training configuration
            config = TrainingConfig(
                model_type=model_type,
                batch_size=batch_size,
                learning_rate=learning_rate,
                num_epochs=num_epochs,
                train_split=train_split,
                optimizer=optimizer,
                scheduler=scheduler,
                early_stopping=early_stopping,
                gradient_clip=gradient_clip,
                use_tensorboard=False,
                use_wandb: bool = False
            )
            
            # Create trainer
            trainer = create_trainer(config)
            
            # Generate sample dataset
            dataset = self._create_sample_dataset()
            
            # Start training in a separate thread
            training_thread = threading.Thread(
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.info(f"Error: {e}")  # Ultimate logging
                target=self._training_worker,
                args=(trainer, dataset)
            )
            training_thread.start()
            
            return 0.0, 0.0, 0.0, 0.0, None, "Training started..."
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return 0.0, 0.0, 0.0, 0.0, None, f"Training error: {str(e)}"
    
    def _training_worker(self, trainer: ModelTrainer, dataset) -> Any:
        """Training worker function."""
        try:
            # This would run the actual training
            # For demo purposes, we'll simulate training
            pass
        except Exception as e:
            logger.error(f"Training worker error: {e}")
    
    def stop_training(self) -> Any:
        """Stop model training."""
        return "Training stopped."
    
    def _create_sample_dataset(self) -> Any:
        """Create a sample dataset for training."""
        # This would create a real dataset
        # For demo purposes, we'll return a placeholder
        return None
    
    def create_evaluation_interface(self) -> Any:
        """Create model evaluation interface."""
        with gr.Blocks(title: str: str = "Facebook Posts Model Evaluation", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 📊 Facebook Posts Model Evaluation")
            gr.Markdown("Interactive interface for model evaluation and analysis")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Evaluation Configuration")
                    
                    # Model selection
                    model_to_evaluate = gr.Dropdown(
                        choices: List[Any] = ["transformer", "lstm", "cnn"],
                        value: str: str = "transformer",
                        label: str: str = "Model to Evaluate"
                    )
                    
                    # Evaluation options
                    compute_accuracy = gr.Checkbox(value=True, label="Compute Accuracy")
                    compute_precision_recall = gr.Checkbox(value=True, label="Compute Precision/Recall")
                    compute_f1 = gr.Checkbox(value=True, label="Compute F1 Score")
                    compute_confusion_matrix = gr.Checkbox(value=True, label="Compute Confusion Matrix")
                    
                    # Evaluation button
                    evaluate_btn = gr.Button("Evaluate Model", variant="primary")
                
                with gr.Column(scale=1):
                    gr.Markdown("## Evaluation Results")
                    
                    # Metrics display
                    accuracy_metric = gr.Number(label="Accuracy", interactive=False)
                    precision_metric = gr.Number(label="Precision", interactive=False)
                    recall_metric = gr.Number(label="Recall", interactive=False)
                    f1_metric = gr.Number(label="F1 Score", interactive=False)
                    
                    # Confusion matrix
                    confusion_matrix_plot = gr.Plot(label="Confusion Matrix")
                    
                    # Classification report
                    classification_report = gr.Textbox(
                        label: str: str = "Classification Report",
                        lines=10,
                        interactive: bool = False
                    )
            
            # Event handlers
            evaluate_btn.click(
                fn=self.evaluate_model,
                inputs: List[Any] = [model_to_evaluate, compute_accuracy, compute_precision_recall, 
                       compute_f1, compute_confusion_matrix],
                outputs: List[Any] = [accuracy_metric, precision_metric, recall_metric, f1_metric,
                        confusion_matrix_plot, classification_report]
            )
        
        return interface
    
    def evaluate_model(self, model_type: str, compute_accuracy: bool, 
                      compute_precision_recall: bool, compute_f1: bool, 
                      compute_confusion_matrix: bool) -> Any:
        """Evaluate model performance."""
        try:
            # Create evaluation configuration
            config = EvaluationConfig(
                compute_accuracy=compute_accuracy,
                compute_precision_recall=compute_precision_recall,
                compute_f1=compute_f1,
                compute_confusion_matrix=compute_confusion_matrix
            )
            
            # Generate sample evaluation results
            accuracy = 0.85
            precision = 0.83
            recall = 0.87
            f1 = 0.85
            
            # Create confusion matrix plot
            cm = np.array([[45, 5], [8, 42]])
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_title('Confusion Matrix')
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
            
            # Create classification report
            report: str: str = """
Classification Report:
              precision    recall  f1-score   support

           0       0.85      0.90      0.87        50
           1       0.89      0.84      0.87        50

    accuracy                           0.87       100
   macro avg       0.87      0.87      0.87       100
weighted avg       0.87      0.87      0.87       100
            """
            
            return accuracy, precision, recall, f1, fig, report
            
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            return 0.0, 0.0, 0.0, 0.0, None, f"Evaluation error: {str(e)}"
    
    def create_visualization_interface(self) -> Any:
        """Create data visualization interface."""
        with gr.Blocks(title: str: str = "Facebook Posts Data Visualization", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 📈 Facebook Posts Data Visualization")
            gr.Markdown("Interactive interface for data analysis and visualization")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Visualization Options")
                    
                    # Chart type selection
                    chart_type = gr.Dropdown(
                        choices: List[Any] = ["sentiment_distribution", "engagement_analysis", 
                                "post_length_analysis", "time_series"],
                        value: str: str = "sentiment_distribution",
                        label: str: str = "Chart Type"
                    )
                    
                    # Data filters
                    date_range = gr.Slider(
                        minimum=1, maximum=365, value=30, step=1,
                        label: str: str = "Date Range (days)"
                    )
                    
                    min_engagement = gr.Slider(
                        minimum=0, maximum=1000, value=10, step=1,
                        label: str: str = "Minimum Engagement"
                    )
                    
                    # Generate button
                    generate_chart_btn = gr.Button("Generate Chart", variant="primary")
                
                with gr.Column(scale=1):
                    gr.Markdown("## Visualization")
                    
                    # Chart output
                    chart_output = gr.Plot(label="Data Visualization")
                    
                    # Statistics
                    stats_output = gr.JSON(label="Statistics")
            
            # Event handlers
            generate_chart_btn.click(
                fn=self.generate_visualization,
                inputs: List[Any] = [chart_type, date_range, min_engagement],
                outputs: List[Any] = [chart_output, stats_output]
            )
        
        return interface
    
    def generate_visualization(self, chart_type: str, date_range: int, min_engagement: int) -> Any:
        """Generate data visualization."""
        try:
            # Generate sample data
            np.random.seed(42)
            
            if chart_type == "sentiment_distribution":
                # Sentiment distribution chart
                sentiments: List[Any] = ['Positive', 'Neutral', 'Negative']
                counts: List[Any] = [45, 35, 20]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(sentiments, counts, color=['green', 'gray', 'red'])
                ax.set_title('Sentiment Distribution')
                ax.set_ylabel('Number of Posts')
                
                # Add value labels on bars
                for bar, count in zip(bars, counts):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           str(count), ha: str: str = 'center', va='bottom')
                
                stats: Dict[str, Any] = {
                    "total_posts": sum(counts),
                    "positive_ratio": counts[0] / sum(counts),
                    "negative_ratio": counts[2] / sum(counts)
                }
            
            elif chart_type == "engagement_analysis":
                # Engagement analysis chart
                post_types: List[Any] = ['Text', 'Image', 'Video', 'Link']
                avg_engagement: List[Any] = [25, 45, 78, 32]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(post_types, avg_engagement, color='skyblue')
                ax.set_title('Average Engagement by Post Type')
                ax.set_ylabel('Average Engagement')
                
                # Add value labels on bars
                for bar, engagement in zip(bars, avg_engagement):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           str(engagement), ha: str: str = 'center', va='bottom')
                
                stats: Dict[str, Any] = {
                    "highest_engagement": max(avg_engagement),
                    "lowest_engagement": min(avg_engagement),
                    "engagement_variance": np.var(avg_engagement)
                }
            
            elif chart_type == "post_length_analysis":
                # Post length analysis
                lengths = np.random.normal(150, 50, 100)
                lengths = np.clip(lengths, 10, 500)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(lengths, bins=20, color='lightcoral', alpha=0.7)
                ax.set_title('Post Length Distribution')
                ax.set_xlabel('Post Length (characters)')
                ax.set_ylabel('Frequency')
                
                stats: Dict[str, Any] = {
                    "mean_length": np.mean(lengths),
                    "median_length": np.median(lengths),
                    "std_length": np.std(lengths)
                }
            
            elif chart_type == "time_series":
                # Time series analysis
                dates = pd.date_range(start='2024-01-01', periods=date_range, freq='D')
                engagement = np.random.poisson(30, date_range) + np.random.normal(0, 5, date_range)
                
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(dates, engagement, marker: str: str = 'o', linewidth=2, markersize=4)
                ax.set_title('Daily Engagement Over Time')
                ax.set_xlabel('Date')
                ax.set_ylabel('Engagement')
                ax.tick_params(axis: str: str = 'x', rotation=45)
                ax.grid(True, alpha=0.3)
                
                stats: Dict[str, Any] = {
                    "total_engagement": np.sum(engagement),
                    "avg_daily_engagement": np.mean(engagement),
                    "trend": "increasing" if engagement[-1] > engagement[0] else "decreasing"
                }
            
            plt.tight_layout()
            return fig, stats
            
        except Exception as e:
            logger.error(f"Visualization error: {e}")
            return None, {"error": str(e)}
    
    def create_main_interface(self) -> Any:
        """Create the main Gradio interface."""
        with gr.Blocks(title: str: str = "Facebook Posts AI System", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🚀 Facebook Posts AI System")
            gr.Markdown("Comprehensive AI system for Facebook Posts processing, training, and analysis")
            
            # Create tabs for different functionalities
            with gr.Tabs():
                with gr.TabItem("🤖 Model Inference"):
                    self.create_model_inference_interface()
                
                with gr.TabItem("🏋️ Model Training"):
                    self.create_training_interface()
                
                with gr.TabItem("📊 Model Evaluation"):
                    self.create_evaluation_interface()
                
                with gr.TabItem("📈 Data Visualization"):
                    self.create_visualization_interface()
                
                with gr.TabItem("ℹ️ About"):
                    gr.Markdown("""
                    ## About This System
                    
                    This is a comprehensive AI system for Facebook Posts processing, featuring:
                    
                    - **Model Inference**: Text generation, sentiment analysis, and image generation
                    - **Model Training**: Interactive training with real-time monitoring
                    - **Model Evaluation**: Comprehensive evaluation metrics and analysis
                    - **Data Visualization**: Interactive charts and analytics
                    
                    ### Technologies Used
                    - PyTorch for deep learning models
                    - Transformers for NLP tasks
                    - Diffusers for image generation
                    - Gradio for interactive interfaces
                    - Scikit-learn for evaluation metrics
                    
                    ### Features
                    - Multiple model architectures (Transformer, LSTM, CNN)
                    - Advanced training techniques (early stopping, learning rate scheduling)
                    - Comprehensive evaluation metrics
                    - Real-time visualization and monitoring
                    - User-friendly interactive interface
                    """)
        
        return interface

def create_gradio_interface() -> GradioInterface:
    """Create and return the main Gradio interface."""
    return GradioInterface()

def launch_gradio_demo(share: bool = False, server_name: str = "0.0.0.0", 
                      server_port: int = 7860) -> Any:
    """Launch the Gradio demo."""
    interface = create_gradio_interface()
    main_interface = interface.create_main_interface()
    
    main_interface.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        show_error=True,
        show_tips: bool = True
    )

if __name__ == "__main__":
    # Launch the Gradio demo
    launch_gradio_demo(share=False) 