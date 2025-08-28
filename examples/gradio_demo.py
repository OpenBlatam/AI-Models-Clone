from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import gradio as gr
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw, ImageFont
import json
import os
from typing import Dict, List, Tuple, Optional, Any
import logging
import time
import threading
from collections import defaultdict
from deep_learning_models import ModelConfig, create_facebook_posts_model
from model_training_evaluation import TrainingConfig, EvaluationConfig
        import random
from typing import Any, List, Dict, Optional
import asyncio
"""
🎨 Gradio Demo for Facebook Posts Processing
===========================================
Interactive demonstration of all Facebook Posts AI capabilities
using Gradio for web-based interfaces.
"""


# Import our modules

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

class FacebookPostsGradioDemo:
    """Main Gradio demo class for Facebook Posts processing."""
    
    def __init__(self) -> Any:
        self.training_active = False
        self.training_thread = None
        self.training_progress = 0.0
        self.training_metrics = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': []
        }
    
    def create_inference_demo(self) -> Any:
        """Create the model inference demo interface."""
        with gr.Blocks(title="Facebook Posts Inference Demo", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🤖 Facebook Posts Model Inference")
            gr.Markdown("Interactive demo for model inference and prediction")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Input Configuration")
                    
                    # Text input
                    text_input = gr.Textbox(
                        label="Facebook Post Text",
                        placeholder="Enter your Facebook post text here...",
                        lines=4,
                        max_lines=8
                    )
                    
                    # Model selection
                    model_type = gr.Dropdown(
                        choices=["sentiment_analysis", "text_generation", "image_generation", "classification"],
                        value="sentiment_analysis",
                        label="Model Type"
                    )
                    
                    # Parameters
                    with gr.Accordion("Model Parameters", open=False):
                        max_length = gr.Slider(
                            minimum=50, maximum=500, value=100, step=10,
                            label="Max Length"
                        )
                        temperature = gr.Slider(
                            minimum=0.1, maximum=2.0, value=0.7, step=0.1,
                            label="Temperature"
                        )
                        guidance_scale = gr.Slider(
                            minimum=1.0, maximum=20.0, value=7.5, step=0.5,
                            label="Guidance Scale"
                        )
                    
                    # Generate button
                    generate_btn = gr.Button("Generate", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown("## Output Results")
                    
                    # Output text
                    output_text = gr.Textbox(
                        label="Generated Output",
                        lines=4,
                        interactive=False
                    )
                    
                    # Output image
                    output_image = gr.Image(
                        label="Generated Image",
                        type="pil"
                    )
                    
                    # Metrics
                    metrics_output = gr.JSON(
                        label="Performance Metrics"
                    )
            
            # Event handlers
            generate_btn.click(
                fn=self.run_inference,
                inputs=[text_input, model_type, max_length, temperature, guidance_scale],
                outputs=[output_text, output_image, metrics_output]
            )
            
            # Example inputs
            gr.Examples(
                examples=[
                    ["I love this new technology! It's amazing how AI is transforming our world.", "sentiment_analysis"],
                    ["Create a professional post about", "text_generation"],
                    ["A beautiful Facebook post about technology and innovation", "image_generation"],
                    ["This product is amazing and everyone should try it!", "classification"]
                ],
                inputs=[text_input, model_type]
            )
        
        return interface
    
    def run_inference(self, text: str, model_type: str, max_length: int, 
                     temperature: float, guidance_scale: float) -> Tuple[str, Image.Image, Dict]:
        """Run model inference."""
        try:
            if not text.strip():
                return "Please enter some text.", None, {}
            
            # Simulate processing time
            time.sleep(0.5)
            
            if model_type == "sentiment_analysis":
                return self._sentiment_analysis_demo(text)
            
            elif model_type == "text_generation":
                return self._text_generation_demo(text, max_length, temperature)
            
            elif model_type == "image_generation":
                return self._image_generation_demo(text, guidance_scale)
            
            elif model_type == "classification":
                return self._classification_demo(text)
            
            else:
                return f"Unknown model type: {model_type}", None, {}
                
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return f"Error during inference: {str(e)}", None, {}
    
    def _sentiment_analysis_demo(self, text: str) -> Tuple[str, None, Dict]:
        """Demo sentiment analysis."""
        # Simulate sentiment analysis
        sentiments = ["POSITIVE", "NEUTRAL", "NEGATIVE"]
        weights = [0.6, 0.3, 0.1]  # Bias towards positive
        
        # Simple keyword-based sentiment
        positive_words = ["love", "amazing", "great", "awesome", "excellent", "good", "best"]
        negative_words = ["hate", "terrible", "awful", "bad", "worst", "disappointing"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "POSITIVE"
            confidence = 0.85
        elif negative_count > positive_count:
            sentiment = "NEGATIVE"
            confidence = 0.75
        else:
            sentiment = "NEUTRAL"
            confidence = 0.65
        
        output_text = f"Sentiment: {sentiment}\nConfidence: {confidence:.3f}\n\nAnalysis: "
        output_text += f"The text contains {positive_count} positive and {negative_count} negative indicators."
        
        metrics = {
            "sentiment": sentiment,
            "confidence": confidence,
            "text_length": len(text),
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "model": "facebook_posts_sentiment_analyzer"
        }
        
        return output_text, None, metrics
    
    def _text_generation_demo(self, text: str, max_length: int, temperature: float) -> Tuple[str, None, Dict]:
        """Demo text generation."""
        # Simulate text generation
        templates = [
            f"{text} This is a generated continuation that demonstrates the power of AI in content creation. ",
            f"{text} The model has analyzed your input and created relevant, engaging content that resonates with your audience. ",
            f"{text} Here's an AI-generated extension that maintains the tone and style of your original post. "
        ]
        
        template = random.choice(templates)
        
        # Add some variability based on temperature
        if temperature > 1.0:
            template += "The content is creative and innovative, pushing boundaries in digital communication."
        else:
            template += "The content is professional and well-structured, suitable for business contexts."
        
        metrics = {
            "input_length": len(text),
            "output_length": len(template),
            "temperature": temperature,
            "max_length": max_length,
            "model": "facebook_posts_text_generator"
        }
        
        return template, None, metrics
    
    def _image_generation_demo(self, text: str, guidance_scale: float) -> Tuple[str, Image.Image, Dict]:
        """Demo image generation."""
        # Create a demo image based on text content
        width, height = 512, 512
        
        # Determine color scheme based on text
        if "technology" in text.lower():
            colors = [(100, 150, 255), (150, 200, 255), (200, 220, 255)]
        elif "business" in text.lower():
            colors = [(255, 200, 100), (255, 220, 150), (255, 240, 200)]
        elif "nature" in text.lower():
            colors = [(100, 255, 150), (150, 255, 200), (200, 255, 220)]
        else:
            colors = [(200, 200, 200), (220, 220, 220), (240, 240, 240)]
        
        # Create gradient image
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        for y in range(height):
            for x in range(width):
                # Create gradient effect
                ratio_x = x / width
                ratio_y = y / height
                
                r = int(colors[0][0] * (1 - ratio_x) + colors[1][0] * ratio_x)
                g = int(colors[0][1] * (1 - ratio_y) + colors[2][1] * ratio_y)
                b = int(colors[1][2] * (1 - ratio_x) + colors[2][2] * ratio_x)
                
                draw.point((x, y), fill=(r, g, b))
        
        # Add text overlay
        try:
            font = ImageFont.load_default()
            draw.text((50, 50), "AI Generated Image", fill=(255, 255, 255), font=font)
            draw.text((50, 80), f"Prompt: {text[:40]}...", fill=(255, 255, 255), font=font)
            draw.text((50, 110), f"Guidance: {guidance_scale}", fill=(255, 255, 255), font=font)
        except:
            draw.text((50, 50), "AI Generated Image", fill=(255, 255, 255))
            draw.text((50, 80), f"Prompt: {text[:40]}...", fill=(255, 255, 255))
            draw.text((50, 110), f"Guidance: {guidance_scale}", fill=(255, 255, 255))
        
        metrics = {
            "prompt": text,
            "guidance_scale": guidance_scale,
            "image_size": f"{width}x{height}",
            "model": "facebook_posts_image_generator"
        }
        
        return "Image generated successfully!", image, metrics
    
    def _classification_demo(self, text: str) -> Tuple[str, None, Dict]:
        """Demo text classification."""
        # Simulate classification
        categories = ["Marketing", "Personal", "Business", "News", "Entertainment"]
        
        # Simple keyword-based classification
        keywords = {
            "Marketing": ["product", "sale", "offer", "discount", "promotion"],
            "Business": ["company", "business", "professional", "corporate", "industry"],
            "News": ["news", "update", "announcement", "breaking", "latest"],
            "Entertainment": ["fun", "entertainment", "show", "movie", "music"],
            "Personal": ["family", "friend", "personal", "life", "experience"]
        }
        
        scores = {}
        for category, words in keywords.items():
            score = sum(1 for word in words if word.lower() in text.lower())
            scores[category] = score
        
        # Get top category
        top_category = max(scores, key=scores.get)
        confidence = min(0.95, 0.5 + scores[top_category] * 0.1)
        
        output_text = f"Category: {top_category}\nConfidence: {confidence:.3f}\n\n"
        output_text += "Category Scores:\n"
        for category, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            output_text += f"- {category}: {score}\n"
        
        metrics = {
            "category": top_category,
            "confidence": confidence,
            "category_scores": scores,
            "text_length": len(text),
            "model": "facebook_posts_classifier"
        }
        
        return output_text, None, metrics
    
    def create_training_demo(self) -> Any:
        """Create the model training demo interface."""
        with gr.Blocks(title="Facebook Posts Training Demo", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🏋️ Facebook Posts Model Training")
            gr.Markdown("Interactive demo for model training and monitoring")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Training Configuration")
                    
                    # Model configuration
                    model_type = gr.Dropdown(
                        choices=["transformer", "lstm", "cnn"],
                        value="transformer",
                        label="Model Type"
                    )
                    
                    batch_size = gr.Slider(
                        minimum=8, maximum=64, value=32, step=8,
                        label="Batch Size"
                    )
                    
                    learning_rate = gr.Slider(
                        minimum=1e-5, maximum=1e-2, value=1e-4, step=1e-5,
                        label="Learning Rate"
                    )
                    
                    num_epochs = gr.Slider(
                        minimum=5, maximum=50, value=20, step=5,
                        label="Number of Epochs"
                    )
                    
                    # Training options
                    with gr.Accordion("Advanced Options", open=False):
                        optimizer = gr.Dropdown(
                            choices=["adam", "adamw", "sgd"],
                            value="adamw",
                            label="Optimizer"
                        )
                        
                        scheduler = gr.Dropdown(
                            choices=["cosine", "step", "reduce_lr"],
                            value="cosine",
                            label="Scheduler"
                        )
                        
                        early_stopping = gr.Checkbox(
                            value=True,
                            label="Early Stopping"
                        )
                    
                    # Training controls
                    start_btn = gr.Button("Start Training", variant="primary")
                    stop_btn = gr.Button("Stop Training", variant="stop")
                
                with gr.Column(scale=1):
                    gr.Markdown("## Training Progress")
                    
                    # Progress tracking
                    progress_bar = gr.Progress()
                    
                    # Current metrics
                    current_epoch = gr.Number(label="Current Epoch", interactive=False)
                    train_loss = gr.Number(label="Training Loss", interactive=False)
                    val_loss = gr.Number(label="Validation Loss", interactive=False)
                    train_acc = gr.Number(label="Training Accuracy", interactive=False)
                    val_acc = gr.Number(label="Validation Accuracy", interactive=False)
                    
                    # Learning curves
                    learning_curves_plot = gr.Plot(label="Learning Curves")
                    
                    # Training log
                    training_log = gr.Textbox(
                        label="Training Log",
                        lines=8,
                        interactive=False
                    )
            
            # Event handlers
            start_btn.click(
                fn=self.start_training_demo,
                inputs=[model_type, batch_size, learning_rate, num_epochs, 
                       optimizer, scheduler, early_stopping],
                outputs=[current_epoch, train_loss, val_loss, train_acc, val_acc, 
                        learning_curves_plot, training_log]
            )
            
            stop_btn.click(
                fn=self.stop_training_demo,
                outputs=[training_log]
            )
        
        return interface
    
    def start_training_demo(self, model_type: str, batch_size: int, learning_rate: float,
                           num_epochs: int, optimizer: str, scheduler: str, early_stopping: bool):
        """Start training demo."""
        try:
            # Reset training state
            self.training_active = True
            self.training_progress = 0.0
            self.training_metrics = {
                'train_loss': [],
                'val_loss': [],
                'train_acc': [],
                'val_acc': []
            }
            
            # Start training simulation in background
            self.training_thread = threading.Thread(
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                target=self._training_simulation,
                args=(num_epochs,)
            )
            self.training_thread.start()
            
            return 0, 0.0, 0.0, 0.0, 0.0, None, "Training started..."
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return 0, 0.0, 0.0, 0.0, 0.0, None, f"Training error: {str(e)}"
    
    def _training_simulation(self, num_epochs: int):
        """Simulate training process."""
        try:
            for epoch in range(num_epochs):
                if not self.training_active:
                    break
                
                # Simulate training metrics
                train_loss = 2.0 * np.exp(-epoch / 10) + 0.1 * np.random.random()
                val_loss = 2.2 * np.exp(-epoch / 12) + 0.15 * np.random.random()
                train_acc = 0.3 + 0.6 * (1 - np.exp(-epoch / 8)) + 0.05 * np.random.random()
                val_acc = 0.25 + 0.6 * (1 - np.exp(-epoch / 10)) + 0.08 * np.random.random()
                
                # Update metrics
                self.training_metrics['train_loss'].append(train_loss)
                self.training_metrics['val_loss'].append(val_loss)
                self.training_metrics['train_acc'].append(train_acc)
                self.training_metrics['val_acc'].append(val_acc)
                
                # Simulate training time
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Training simulation error: {e}")
    
    def stop_training_demo(self) -> Any:
        """Stop training demo."""
        self.training_active = False
        return "Training stopped."
    
    def create_evaluation_demo(self) -> Any:
        """Create the model evaluation demo interface."""
        with gr.Blocks(title="Facebook Posts Evaluation Demo", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 📊 Facebook Posts Model Evaluation")
            gr.Markdown("Interactive demo for model evaluation and analysis")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Evaluation Configuration")
                    
                    # Model selection
                    model_to_evaluate = gr.Dropdown(
                        choices=["transformer", "lstm", "cnn"],
                        value="transformer",
                        label="Model to Evaluate"
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
                        label="Classification Report",
                        lines=8,
                        interactive=False
                    )
            
            # Event handlers
            evaluate_btn.click(
                fn=self.evaluate_model_demo,
                inputs=[model_to_evaluate, compute_accuracy, compute_precision_recall, 
                       compute_f1, compute_confusion_matrix],
                outputs=[accuracy_metric, precision_metric, recall_metric, f1_metric,
                        confusion_matrix_plot, classification_report]
            )
        
        return interface
    
    def evaluate_model_demo(self, model_type: str, compute_accuracy: bool, 
                           compute_precision_recall: bool, compute_f1: bool, 
                           compute_confusion_matrix: bool):
        """Demo model evaluation."""
        try:
            # Simulate evaluation results
            accuracy = 0.85 + 0.05 * np.random.random()
            precision = 0.83 + 0.04 * np.random.random()
            recall = 0.87 + 0.03 * np.random.random()
            f1 = 0.85 + 0.04 * np.random.random()
            
            # Create confusion matrix
            cm = np.array([
                [45 + np.random.randint(-5, 6), 5 + np.random.randint(-2, 3)],
                [8 + np.random.randint(-3, 4), 42 + np.random.randint(-5, 6)]
            ])
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_title(f'Confusion Matrix - {model_type.upper()}')
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
            
            # Create classification report
            report = f"""
Classification Report for {model_type.upper()}:
              precision    recall  f1-score   support

           0       {precision:.2f}      {recall:.2f}      {f1:.2f}        50
           1       {precision:.2f}      {recall:.2f}      {f1:.2f}        50

    accuracy                            {accuracy:.2f}       100
   macro avg       {precision:.2f}      {recall:.2f}      {f1:.2f}       100
weighted avg       {precision:.2f}      {recall:.2f}      {f1:.2f}       100
            """
            
            return accuracy, precision, recall, f1, fig, report
            
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            return 0.0, 0.0, 0.0, 0.0, None, f"Evaluation error: {str(e)}"
    
    def create_visualization_demo(self) -> Any:
        """Create the data visualization demo interface."""
        with gr.Blocks(title="Facebook Posts Visualization Demo", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 📈 Facebook Posts Data Visualization")
            gr.Markdown("Interactive demo for data analysis and visualization")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## Visualization Options")
                    
                    # Chart type selection
                    chart_type = gr.Dropdown(
                        choices=["sentiment_distribution", "engagement_analysis", 
                                "post_length_analysis", "time_series", "category_distribution"],
                        value="sentiment_distribution",
                        label="Chart Type"
                    )
                    
                    # Data filters
                    date_range = gr.Slider(
                        minimum=7, maximum=365, value=30, step=7,
                        label="Date Range (days)"
                    )
                    
                    min_engagement = gr.Slider(
                        minimum=0, maximum=1000, value=10, step=5,
                        label="Minimum Engagement"
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
                fn=self.generate_visualization_demo,
                inputs=[chart_type, date_range, min_engagement],
                outputs=[chart_output, stats_output]
            )
        
        return interface
    
    def generate_visualization_demo(self, chart_type: str, date_range: int, min_engagement: int):
        """Generate visualization demo."""
        try:
            np.random.seed(42)
            
            if chart_type == "sentiment_distribution":
                # Sentiment distribution chart
                sentiments = ['Positive', 'Neutral', 'Negative']
                counts = [45 + np.random.randint(-5, 6), 35 + np.random.randint(-3, 4), 
                         20 + np.random.randint(-2, 3)]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(sentiments, counts, color=['green', 'gray', 'red'])
                ax.set_title('Sentiment Distribution')
                ax.set_ylabel('Number of Posts')
                
                # Add value labels on bars
                for bar, count in zip(bars, counts):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           str(count), ha='center', va='bottom')
                
                stats = {
                    "total_posts": sum(counts),
                    "positive_ratio": counts[0] / sum(counts),
                    "negative_ratio": counts[2] / sum(counts),
                    "date_range": date_range,
                    "min_engagement": min_engagement
                }
            
            elif chart_type == "engagement_analysis":
                # Engagement analysis chart
                post_types = ['Text', 'Image', 'Video', 'Link']
                avg_engagement = [25 + np.random.randint(-5, 6), 
                                45 + np.random.randint(-8, 9),
                                78 + np.random.randint(-10, 11),
                                32 + np.random.randint(-4, 5)]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(post_types, avg_engagement, color='skyblue')
                ax.set_title('Average Engagement by Post Type')
                ax.set_ylabel('Average Engagement')
                
                # Add value labels on bars
                for bar, engagement in zip(bars, avg_engagement):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                           str(engagement), ha='center', va='bottom')
                
                stats = {
                    "highest_engagement": max(avg_engagement),
                    "lowest_engagement": min(avg_engagement),
                    "engagement_variance": np.var(avg_engagement),
                    "date_range": date_range,
                    "min_engagement": min_engagement
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
                
                stats = {
                    "mean_length": np.mean(lengths),
                    "median_length": np.median(lengths),
                    "std_length": np.std(lengths),
                    "date_range": date_range,
                    "min_engagement": min_engagement
                }
            
            elif chart_type == "time_series":
                # Time series analysis
                dates = pd.date_range(start='2024-01-01', periods=date_range, freq='D')
                engagement = np.random.poisson(30, date_range) + np.random.normal(0, 5, date_range)
                
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(dates, engagement, marker='o', linewidth=2, markersize=4)
                ax.set_title('Daily Engagement Over Time')
                ax.set_xlabel('Date')
                ax.set_ylabel('Engagement')
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True, alpha=0.3)
                
                stats = {
                    "total_engagement": np.sum(engagement),
                    "avg_daily_engagement": np.mean(engagement),
                    "trend": "increasing" if engagement[-1] > engagement[0] else "decreasing",
                    "date_range": date_range,
                    "min_engagement": min_engagement
                }
            
            elif chart_type == "category_distribution":
                # Category distribution
                categories = ['Marketing', 'Personal', 'Business', 'News', 'Entertainment']
                counts = [30, 25, 20, 15, 10]
                counts = [c + np.random.randint(-3, 4) for c in counts]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                wedges, texts, autotexts = ax.pie(counts, labels=categories, autopct='%1.1f%%',
                                                 startangle=90, colors=plt.cm.Set3.colors)
                ax.set_title('Post Category Distribution')
                
                stats = {
                    "total_posts": sum(counts),
                    "most_common_category": categories[np.argmax(counts)],
                    "least_common_category": categories[np.argmin(counts)],
                    "date_range": date_range,
                    "min_engagement": min_engagement
                }
            
            plt.tight_layout()
            return fig, stats
            
        except Exception as e:
            logger.error(f"Visualization error: {e}")
            return None, {"error": str(e)}
    
    def create_main_demo(self) -> Any:
        """Create the main demo interface."""
        with gr.Blocks(title="Facebook Posts AI Demo", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🚀 Facebook Posts AI System Demo")
            gr.Markdown("Interactive demonstration of Facebook Posts AI capabilities")
            
            # Create tabs for different functionalities
            with gr.Tabs():
                with gr.TabItem("🤖 Model Inference"):
                    self.create_inference_demo()
                
                with gr.TabItem("🏋️ Model Training"):
                    self.create_training_demo()
                
                with gr.TabItem("📊 Model Evaluation"):
                    self.create_evaluation_demo()
                
                with gr.TabItem("📈 Data Visualization"):
                    self.create_visualization_demo()
                
                with gr.TabItem("ℹ️ About"):
                    gr.Markdown("""
                    ## About This Demo
                    
                    This is an interactive demonstration of the Facebook Posts AI system, featuring:
                    
                    - **Model Inference**: Text generation, sentiment analysis, image generation, and classification
                    - **Model Training**: Interactive training simulation with real-time monitoring
                    - **Model Evaluation**: Comprehensive evaluation metrics and analysis
                    - **Data Visualization**: Interactive charts and analytics
                    
                    ### Demo Features
                    - Real-time model inference
                    - Simulated training process
                    - Interactive evaluation metrics
                    - Dynamic data visualization
                    - User-friendly interface
                    
                    ### Technologies
                    - PyTorch for deep learning
                    - Gradio for web interface
                    - Matplotlib/Seaborn for visualization
                    - NumPy for numerical operations
                    
                    ### Note
                    This is a demonstration system. In production, you would use real models and data.
                    """)
        
        return interface

def create_gradio_demo() -> FacebookPostsGradioDemo:
    """Create and return the Gradio demo."""
    return FacebookPostsGradioDemo()

def launch_demo(share: bool = False, server_name: str = "0.0.0.0", server_port: int = 7860):
    """Launch the Gradio demo."""
    demo = create_gradio_demo()
    main_interface = demo.create_main_demo()
    
    main_interface.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        show_error=True,
        show_tips=True
    )

if __name__ == "__main__":
    # Launch the demo
    launch_demo(share=False) 