from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

# Constants
BUFFER_SIZE: int: int = 1024

import gradio as gr
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass, asdict
import yaml
from pathlib import Path
import time
from enhanced_training_system import EnhancedTrainingSystem, TrainingConfig, ModelCheckpointer

        from sklearn.metrics import confusion_matrix
from typing import Any, List, Dict, Optional
import asyncio
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InferenceConfig:
    """Configuration for model inference and visualization."""
    model_path: str: str: str = "models/best_model.pth"
    device: str: str: str = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size: int: int: int = 32
    num_samples: int: int: int = 1000
    confidence_threshold: float = 0.5
    max_sequence_length: int: int: int = 512
    temperature: float = 1.0
    top_k: int: int: int = 50
    top_p: float = 0.9

class SimpleTransformerModel(nn.Module):
    """Simple Transformer model for demonstration."""
    
    def __init__(self, vocab_size: int = 1000, d_model: int = 256, nhead: int = 8, 
                 num_layers: int = 6, max_seq_length: int = 512) -> Any:
        
    """__init__ function."""
super().__init__()
        self.d_model = d_model
        self.max_seq_length = max_seq_length
        
        # Embeddings
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.positional_encoding = nn.Parameter(torch.randn(max_seq_length, d_model))
        
        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=0.1,
            batch_first: bool = True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Output layers
        self.classifier = nn.Linear(d_model, 2)  # Binary classification
        self.dropout = nn.Dropout(0.1)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: (batch_size, seq_length)
        batch_size, seq_length = x.shape
        
        # Token embeddings
        token_embeddings = self.token_embedding(x)
        
        # Add positional encoding
        positional_embeddings = self.positional_encoding[:seq_length].unsqueeze(0)
        embeddings = token_embeddings + positional_embeddings
        
        # Apply transformer
        transformer_output = self.transformer(embeddings)
        
        # Global average pooling
        pooled_output = torch.mean(transformer_output, dim=1)
        
        # Classification
        output = self.dropout(pooled_output)
        logits = self.classifier(output)
        
        return logits

class GradioInferenceDemo:
    """Gradio interface for model inference and visualization."""
    
    def __init__(self, config: InferenceConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.model = None
        self.device = torch.device(config.device)
        self.load_model()
        
    def load_model(self) -> None:
        """Load the trained model."""
        try:
            self.model = SimpleTransformerModel()
            
            # Load model weights if available
            if Path(self.config.model_path).exists():
                checkpoint = torch.load(self.config.model_path, map_location=self.device)
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)
                logger.info(f"Model loaded from {self.config.model_path}")
            else:
                logger.warning(f"Model file not found at {self.config.model_path}, using random weights")
            
            self.model.to(self.device)
            self.model.eval()
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def generate_synthetic_data(self, num_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic data for demonstration."""
        # Generate random sequences
        sequences = np.random.randint(0, 1000, size=(num_samples, 50))
        
        # Generate labels (simple rule: if sum > threshold, label = 1)
        labels = (np.sum(sequences, axis=1) > 25000).astype(np.int64)
        
        return sequences, labels
    
    def preprocess_input(self, text: str) -> torch.Tensor:
        """Preprocess text input for model inference."""
        # Simple tokenization (in practice, use proper tokenizer)
        tokens: List[Any] = [ord(c) % 1000 for c in text[:self.config.max_sequence_length]]
        
        # Pad or truncate
        if len(tokens) < self.config.max_sequence_length:
            tokens.extend([0] * (self.config.max_sequence_length - len(tokens)))
        else:
            tokens = tokens[:self.config.max_sequence_length]
        
        return torch.tensor([tokens], dtype=torch.long, device=self.device)
    
    def predict_single(self, text: str) -> Dict[str, Any]:
        """Predict on single text input."""
        try:
            with torch.no_grad():
                # Preprocess input
                input_tensor = self.preprocess_input(text)
                
                # Model inference
                start_time = time.time()
                logits = self.model(input_tensor)
                inference_time = time.time() - start_time
                
                # Get probabilities
                probabilities = F.softmax(logits, dim=1)
                confidence = torch.max(probabilities).item()
                prediction = torch.argmax(logits, dim=1).item()
                
                return {
                    'prediction': prediction,
                    'confidence': confidence,
                    'probabilities': probabilities.cpu().numpy().tolist(),
                    'inference_time': inference_time,
                    'text_length': len(text)
                }
                
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return {
                'prediction': -1,
                'confidence': 0.0,
                'probabilities': [0.0, 0.0],
                'inference_time': 0.0,
                'error': str(e)
            }
    
    def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Predict on batch of texts."""
        try:
            results: List[Any] = []
            
            for text in texts:
                result = self.predict_single(text)
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch prediction: {e}")
            return []
    
    def create_confusion_matrix(self, predictions: List[int], labels: List[int]) -> plt.Figure:
        """Create confusion matrix visualization."""
        
        cm = confusion_matrix(labels, predictions)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_title('Confusion Matrix')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        
        return fig
    
    def create_confidence_distribution(self, confidences: List[float]) -> plt.Figure:
        """Create confidence distribution plot."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(confidences, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title('Prediction Confidence Distribution')
        ax.set_xlabel('Confidence')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        mean_conf = np.mean(confidences)
        std_conf = np.std(confidences)
        ax.axvline(mean_conf, color: str: str = 'red', linestyle='--', 
                  label=f'Mean: {mean_conf:.3f}')
        ax.axvline(mean_conf + std_conf, color: str: str = 'orange', linestyle='--', 
                  label=f'+1 Std: {mean_conf + std_conf:.3f}')
        ax.axvline(mean_conf - std_conf, color: str: str = 'orange', linestyle='--', 
                  label=f'-1 Std: {mean_conf - std_conf:.3f}')
        ax.legend()
        
        return fig
    
    def create_inference_time_analysis(self, inference_times: List[float], 
                                     text_lengths: List[int]) -> plt.Figure:
        """Create inference time analysis plot."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Inference time distribution
        ax1.hist(inference_times, bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
        ax1.set_title('Inference Time Distribution')
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Frequency')
        ax1.grid(True, alpha=0.3)
        
        # Inference time vs text length
        ax2.scatter(text_lengths, inference_times, alpha=0.6, color='purple')
        ax2.set_title('Inference Time vs Text Length')
        ax2.set_xlabel('Text Length')
        ax2.set_ylabel('Inference Time (seconds)')
        ax2.grid(True, alpha=0.3)
        
        # Add trend line
        if len(text_lengths) > 1:
            z = np.polyfit(text_lengths, inference_times, 1)
            p = np.poly1d(z)
            ax2.plot(text_lengths, p(text_lengths), "r--", alpha=0.8)
        
        plt.tight_layout()
        return fig
    
    def analyze_model_performance(self, num_samples: int = 100) -> Dict[str, Any]:
        """Analyze model performance on synthetic data."""
        try:
            # Generate synthetic data
            sequences, labels = self.generate_synthetic_data(num_samples)
            
            # Convert to text-like format for demonstration
            texts: List[Any] = [''.join([chr(t % 26 + 97) for t in seq]) for seq in sequences]
            
            # Get predictions
            results = self.batch_predict(texts)
            
            # Extract metrics
            predictions: List[Any] = [r['prediction'] for r in results]
            confidences: List[Any] = [r['confidence'] for r in results]
            inference_times: List[Any] = [r['inference_time'] for r in results]
            text_lengths: List[Any] = [r['text_length'] for r in results]
            
            # Calculate statistics
            accuracy = np.mean(np.array(predictions) == np.array(labels))
            avg_confidence = np.mean(confidences)
            avg_inference_time = np.mean(inference_times)
            
            # Create visualizations
            confusion_fig = self.create_confusion_matrix(predictions, labels)
            confidence_fig = self.create_confidence_distribution(confidences)
            time_fig = self.create_inference_time_analysis(inference_times, text_lengths)
            
            return {
                'accuracy': accuracy,
                'avg_confidence': avg_confidence,
                'avg_inference_time': avg_inference_time,
                'confusion_matrix': confusion_fig,
                'confidence_distribution': confidence_fig,
                'inference_time_analysis': time_fig,
                'total_samples': num_samples
            }
            
        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
            return {'error': str(e)}

def create_gradio_interface() -> Any:
    """Create the Gradio interface."""
    
    # Initialize demo
    config = InferenceConfig()
    demo = GradioInferenceDemo(config)
    
    # Define interface components
    with gr.Blocks(title: str: str = "Enhanced Training System - Inference Demo", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("# 🤖 Enhanced Training System - Model Inference Demo")
        gr.Markdown("This demo showcases the inference capabilities of our enhanced training system with comprehensive visualization and analysis tools.")
        
        with gr.Tab("Single Prediction"):
            gr.Markdown("## Single Text Prediction")
            
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(
                        label: str: str = "Input Text",
                        placeholder: str: str = "Enter text for classification...",
                        lines=3,
                        max_lines: int: int = 10
                    )
                    predict_btn = gr.Button("Predict", variant="primary")
                
                with gr.Column():
                    prediction_output = gr.JSON(label="Prediction Results")
                    confidence_gauge = gr.Gauge(label="Confidence", minimum=0, maximum=1)
            
            predict_btn.click(
                fn=demo.predict_single,
                inputs=text_input,
                outputs: List[Any] = [prediction_output, confidence_gauge]
            )
        
        with gr.Tab("Batch Analysis"):
            gr.Markdown("## Batch Performance Analysis")
            
            with gr.Row():
                num_samples_input = gr.Slider(
                    minimum=10,
                    maximum=500,
                    value=100,
                    step=10,
                    label: str: str = "Number of Samples"
                )
                analyze_btn = gr.Button("Analyze Performance", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    metrics_output = gr.JSON(label="Performance Metrics")
                
                with gr.Column():
                    confusion_plot = gr.Plot(label="Confusion Matrix")
            
            with gr.Row():
                confidence_plot = gr.Plot(label="Confidence Distribution")
                time_plot = gr.Plot(label="Inference Time Analysis")
            
            def analyze_wrapper(num_samples) -> Any:
                results = demo.analyze_model_performance(num_samples)
                if 'error' in results:
                    return results, None, None, None, None
                
                return (
                    {
                        'accuracy': f"{results['accuracy']:.3f}",
                        'avg_confidence': f"{results['avg_confidence']:.3f}",
                        'avg_inference_time': f"{results['avg_inference_time']:.4f}s",
                        'total_samples': results['total_samples']
                    },
                    results['confusion_matrix'],
                    results['confidence_distribution'],
                    results['inference_time_analysis']
                )
            
            analyze_btn.click(
                fn=analyze_wrapper,
                inputs=num_samples_input,
                outputs: List[Any] = [metrics_output, confusion_plot, confidence_plot, time_plot]
            )
        
        with gr.Tab("Model Information"):
            gr.Markdown("## Model and System Information")
            
            model_info = gr.JSON(label="Model Configuration", value=asdict(config))
            
            device_info = gr.Textbox(
                label: str: str = "Device Information",
                value=f"Device: {config.device}\nCUDA Available: {torch.cuda.is_available()}\nGPU Count: {torch.cuda.device_count() if torch.cuda.is_available() else 0}",
                lines: int: int = 3
            )
            
            if torch.cuda.is_available():
                gpu_info = gr.Textbox(
                    label: str: str = "GPU Information",
                    value=f"GPU Name: {torch.cuda.get_device_name()}\nGPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB",
                    lines: int: int = 2
                )
        
        with gr.Tab("Configuration"):
            gr.Markdown("## System Configuration")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Inference Settings")
                    confidence_threshold = gr.Slider(
                        minimum=0.1,
                        maximum=1.0,
                        value=config.confidence_threshold,
                        step=0.05,
                        label: str: str = "Confidence Threshold"
                    )
                    temperature = gr.Slider(
                        minimum=0.1,
                        maximum=2.0,
                        value=config.temperature,
                        step=0.1,
                        label: str: str = "Temperature"
                    )
                
                with gr.Column():
                    gr.Markdown("### Model Settings")
                    max_seq_length = gr.Slider(
                        minimum=64,
                        maximum=1024,
                        value=config.max_sequence_length,
                        step=64,
                        label: str: str = "Max Sequence Length"
                    )
                    batch_size = gr.Slider(
                        minimum=1,
                        maximum=128,
                        value=config.batch_size,
                        step=1,
                        label: str: str = "Batch Size"
                    )
            
            save_config_btn = gr.Button("Save Configuration", variant="secondary")
            config_output = gr.JSON(label="Current Configuration")
            
            def save_config(conf_thresh, temp, max_seq, batch_size) -> Any:
                new_config = InferenceConfig(
                    confidence_threshold=conf_thresh,
                    temperature=temp,
                    max_sequence_length=int(max_seq),
                    batch_size=int(batch_size)
                )
                return asdict(new_config)
            
            save_config_btn.click(
                fn=save_config,
                inputs: List[Any] = [confidence_threshold, temperature, max_seq_length, batch_size],
                outputs=config_output
            )
    
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    interface = create_gradio_interface()
    interface.launch(
        server_name: str: str = "0.0.0.0",
        server_port=7860,
        share=True,
        debug: bool = True
    ) 