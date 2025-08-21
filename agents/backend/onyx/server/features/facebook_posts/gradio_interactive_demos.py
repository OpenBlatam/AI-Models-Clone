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
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import io
import base64
import json
import time
from typing import Dict, Any, List, Tuple, Optional, Union
import warnings
    from deep_learning_framework import DeepLearningFramework, FrameworkConfig, TaskType
    from evaluation_metrics import EvaluationManager, MetricConfig, MetricType
    from gradient_clipping_nan_handling import NumericalStabilityManager
    from early_stopping_scheduling import TrainingManager
    from efficient_data_loading import EfficientDataLoader
    from data_splitting_validation import DataSplitter
    from training_evaluation import TrainingManager as TrainingEvalManager
    from diffusion_models import DiffusionModel, DiffusionConfig
    from advanced_transformers import AdvancedTransformerModel
    from llm_training import AdvancedLLMTrainer
    from model_finetuning import ModelFineTuner
    from custom_modules import AdvancedNeuralNetwork
    from weight_initialization import AdvancedWeightInitializer
    from normalization_techniques import AdvancedLayerNorm
    from loss_functions import AdvancedCrossEntropyLoss
    from optimization_algorithms import AdvancedAdamW
    from attention_mechanisms import MultiHeadAttention
    from tokenization_sequence import AdvancedTokenizer
    from framework_utils import MetricsTracker, ModelAnalyzer, PerformanceMonitor
    from deep_learning_integration import DeepLearningIntegration, IntegrationConfig, IntegrationType, ComponentType
from typing import Any, List, Dict, Optional
import logging
import asyncio
#!/usr/bin/env python3
"""
Interactive Gradio Demos for Deep Learning
Comprehensive interactive demos for model inference and visualization.
"""

warnings.filterwarnings('ignore')

# Import our custom modules
try:
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")


class GradioDemoManager:
    """Manager for Gradio interactive demos."""
    
    def __init__(self) -> Any:
        self.models = {}
        self.tokenizers = {}
        self.evaluators = {}
        self.stability_managers = {}
        self.setup_models()
    
    def setup_models(self) -> Any:
        """Setup models for demos."""
        # Simple classification model
        self.models['classification'] = nn.Sequential(
            nn.Linear(784, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 10),
            nn.Softmax(dim=1)
        )
        
        # Simple regression model
        self.models['regression'] = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        
        # Simple text generation model (simplified)
        self.models['text_generation'] = nn.Sequential(
            nn.Linear(100, 256),
            nn.ReLU(),
            nn.Linear(256, 100),
            nn.Softmax(dim=1)
        )
        
        # Setup tokenizer
        self.tokenizers['basic'] = AdvancedTokenizer()
        
        # Setup evaluators
        self.evaluators['classification'] = EvaluationManager(
            MetricConfig(task_type=TaskType.CLASSIFICATION)
        )
        self.evaluators['regression'] = EvaluationManager(
            MetricConfig(task_type=TaskType.REGRESSION)
        )
        self.evaluators['generation'] = EvaluationManager(
            MetricConfig(task_type=TaskType.GENERATION)
        )
    
    def create_classification_demo(self) -> Any:
        """Create classification demo."""
        def classify_digit(image) -> Any:
            """Classify handwritten digit."""
            if image is None:
                return "Please upload an image"
            
            # Preprocess image
            image = image.convert('L')  # Convert to grayscale
            image = image.resize((28, 28))  # Resize to 28x28
            image_array = np.array(image) / 255.0  # Normalize
            image_tensor = torch.FloatTensor(image_array).flatten().unsqueeze(0)
            
            # Make prediction
            with torch.no_grad():
                output = self.models['classification'](image_tensor)
                probabilities = output.squeeze().numpy()
                prediction = np.argmax(probabilities)
                confidence = probabilities[prediction]
            
            # Create visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Original image
            ax1.imshow(image_array, cmap='gray')
            ax1.set_title(f'Predicted: {prediction} (Confidence: {confidence:.3f})')
            ax1.axis('off')
            
            # Probability distribution
            ax2.bar(range(10), probabilities)
            ax2.set_title('Class Probabilities')
            ax2.set_xlabel('Digit')
            ax2.set_ylabel('Probability')
            ax2.set_xticks(range(10))
            
            plt.tight_layout()
            
            # Convert to base64 for Gradio
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            return f"Prediction: {prediction} (Confidence: {confidence:.3f})", buf.getvalue()
        
        demo = gr.Interface(
            fn=classify_digit,
            inputs=gr.Image(type="pil", label="Upload Handwritten Digit"),
            outputs=[
                gr.Textbox(label="Prediction"),
                gr.Image(label="Visualization")
            ],
            title="Handwritten Digit Classification",
            description="Upload a handwritten digit image to classify it (0-9)",
            examples=[
                ["examples/digit_0.png"],
                ["examples/digit_1.png"],
                ["examples/digit_2.png"]
            ]
        )
        
        return demo
    
    def create_regression_demo(self) -> Any:
        """Create regression demo."""
        def predict_value(features) -> Any:
            """Predict continuous value."""
            if features is None:
                return "Please provide input features"
            
            # Parse input features
            try:
                feature_values = [float(x) for x in features.split(',')]
                if len(feature_values) != 10:
                    return "Please provide exactly 10 comma-separated values"
            except ValueError:
                return "Please provide valid numeric values"
            
            # Make prediction
            input_tensor = torch.FloatTensor(feature_values).unsqueeze(0)
            
            with torch.no_grad():
                prediction = self.models['regression'](input_tensor)
                predicted_value = prediction.item()
            
            # Create visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Feature importance (simplified)
            feature_names = [f'F{i+1}' for i in range(10)]
            ax1.bar(feature_names, feature_values)
            ax1.set_title('Input Features')
            ax1.set_xlabel('Feature')
            ax1.set_ylabel('Value')
            ax1.tick_params(axis='x', rotation=45)
            
            # Prediction visualization
            ax2.bar(['Predicted'], [predicted_value], color='green')
            ax2.set_title('Predicted Value')
            ax2.set_ylabel('Value')
            
            plt.tight_layout()
            
            # Convert to base64 for Gradio
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            return f"Predicted Value: {predicted_value:.4f}", buf.getvalue()
        
        demo = gr.Interface(
            fn=predict_value,
            inputs=gr.Textbox(
                label="Input Features",
                placeholder="Enter 10 comma-separated values (e.g., 1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0)"
            ),
            outputs=[
                gr.Textbox(label="Prediction"),
                gr.Image(label="Visualization")
            ],
            title="Regression Prediction",
            description="Enter 10 feature values to predict a continuous output",
            examples=[
                ["1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0"],
                ["0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0"],
                ["-1.0,-0.5,0.0,0.5,1.0,1.5,2.0,2.5,3.0,3.5"]
            ]
        )
        
        return demo
    
    def create_text_generation_demo(self) -> Any:
        """Create text generation demo."""
        def generate_text(prompt, max_length=50) -> Any:
            """Generate text from prompt."""
            if not prompt:
                return "Please provide a prompt"
            
            # Simple text generation (simplified)
            words = prompt.split()
            generated_words = words.copy()
            
            # Generate additional words
            for _ in range(max_length - len(words)):
                # Simple word generation (in practice, use a proper language model)
                next_word = f"word_{len(generated_words)}"
                generated_words.append(next_word)
            
            generated_text = " ".join(generated_words)
            
            # Create visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Word frequency
            word_freq = {}
            for word in generated_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            words_list = list(word_freq.keys())[:10]
            freqs = list(word_freq.values())[:10]
            
            ax1.bar(range(len(words_list)), freqs)
            ax1.set_title('Word Frequency')
            ax1.set_xlabel('Word')
            ax1.set_ylabel('Frequency')
            ax1.set_xticks(range(len(words_list)))
            ax1.set_xticklabels(words_list, rotation=45)
            
            # Text length visualization
            ax2.bar(['Original', 'Generated'], [len(words), len(generated_words)])
            ax2.set_title('Text Length Comparison')
            ax2.set_ylabel('Number of Words')
            
            plt.tight_layout()
            
            # Convert to base64 for Gradio
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            return generated_text, buf.getvalue()
        
        demo = gr.Interface(
            fn=generate_text,
            inputs=[
                gr.Textbox(label="Prompt", placeholder="Enter your text prompt"),
                gr.Slider(minimum=10, maximum=100, value=50, step=1, label="Max Length")
            ],
            outputs=[
                gr.Textbox(label="Generated Text"),
                gr.Image(label="Visualization")
            ],
            title="Text Generation",
            description="Enter a prompt to generate text",
            examples=[
                ["The quick brown fox"],
                ["In a world where"],
                ["The future of artificial intelligence"]
            ]
        )
        
        return demo
    
    def create_model_analysis_demo(self) -> Any:
        """Create model analysis demo."""
        def analyze_model(model_type, input_size=784, hidden_size=512, output_size=10) -> Any:
            """Analyze model architecture and performance."""
            # Create model based on type
            if model_type == "classification":
                model = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_size // 2, output_size)
                )
            elif model_type == "regression":
                model = nn.Sequential(
                    nn.Linear(input_size, hidden_size),
                    nn.ReLU(),
                    nn.Linear(hidden_size, hidden_size // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_size // 2, 1)
                )
            else:
                return "Invalid model type", None
            
            # Analyze model
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # Model architecture
            layer_names = []
            layer_params = []
            for name, layer in model.named_modules():
                if isinstance(layer, nn.Linear):
                    layer_names.append(name)
                    layer_params.append(layer.weight.numel() + layer.bias.numel())
            
            ax1.bar(range(len(layer_names)), layer_params)
            ax1.set_title('Parameters per Layer')
            ax1.set_xlabel('Layer')
            ax1.set_ylabel('Parameters')
            ax1.set_xticks(range(len(layer_names)))
            ax1.set_xticklabels(layer_names, rotation=45)
            
            # Parameter distribution
            all_params = []
            for param in model.parameters():
                all_params.extend(param.data.flatten().numpy())
            
            ax2.hist(all_params, bins=50, alpha=0.7, edgecolor='black')
            ax2.set_title('Parameter Distribution')
            ax2.set_xlabel('Parameter Value')
            ax2.set_ylabel('Frequency')
            
            # Model summary
            summary_data = {
                'Total Parameters': total_params,
                'Trainable Parameters': trainable_params,
                'Model Type': model_type,
                'Input Size': input_size,
                'Hidden Size': hidden_size,
                'Output Size': output_size
            }
            
            ax3.bar(summary_data.keys(), summary_data.values())
            ax3.set_title('Model Summary')
            ax3.tick_params(axis='x', rotation=45)
            
            # Layer sizes
            layer_sizes = [input_size, hidden_size, hidden_size // 2, output_size]
            layer_names = ['Input', 'Hidden 1', 'Hidden 2', 'Output']
            
            ax4.bar(layer_names, layer_sizes)
            ax4.set_title('Layer Sizes')
            ax4.set_ylabel('Size')
            
            plt.tight_layout()
            
            # Convert to base64 for Gradio
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            summary_text = f"""
            Model Analysis Results:
            - Model Type: {model_type}
            - Total Parameters: {total_params:,}
            - Trainable Parameters: {trainable_params:,}
            - Input Size: {input_size}
            - Hidden Size: {hidden_size}
            - Output Size: {output_size}
            """
            
            return summary_text, buf.getvalue()
        
        demo = gr.Interface(
            fn=analyze_model,
            inputs=[
                gr.Dropdown(choices=["classification", "regression"], value="classification", label="Model Type"),
                gr.Slider(minimum=100, maximum=1000, value=784, step=1, label="Input Size"),
                gr.Slider(minimum=100, maximum=1000, value=512, step=1, label="Hidden Size"),
                gr.Slider(minimum=1, maximum=100, value=10, step=1, label="Output Size")
            ],
            outputs=[
                gr.Textbox(label="Analysis Results"),
                gr.Image(label="Visualization")
            ],
            title="Model Analysis",
            description="Analyze model architecture and parameters",
        )
        
        return demo
    
    def create_training_visualization_demo(self) -> Any:
        """Create training visualization demo."""
        def visualize_training(epochs=100, learning_rate=0.001, batch_size=32) -> Any:
            """Visualize training process."""
            # Simulate training data
            np.random.seed(42)
            epochs_list = list(range(epochs))
            
            # Simulate loss curves
            train_loss = 1.0 * np.exp(-epochs_list / 30) + 0.1 * np.random.randn(epochs)
            val_loss = 1.2 * np.exp(-epochs_list / 35) + 0.15 * np.random.randn(epochs)
            
            # Simulate accuracy curves
            train_acc = 1.0 - 0.8 * np.exp(-epochs_list / 25) + 0.05 * np.random.randn(epochs)
            val_acc = 0.95 - 0.75 * np.exp(-epochs_list / 30) + 0.08 * np.random.randn(epochs)
            
            # Simulate learning rate schedule
            lr_schedule = learning_rate * np.exp(-np.array(epochs_list) / 50)
            
            # Create visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # Loss curves
            ax1.plot(epochs_list, train_loss, label='Train Loss', color='blue')
            ax1.plot(epochs_list, val_loss, label='Validation Loss', color='red')
            ax1.set_title('Training and Validation Loss')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.legend()
            ax1.grid(True)
            
            # Accuracy curves
            ax2.plot(epochs_list, train_acc, label='Train Accuracy', color='blue')
            ax2.plot(epochs_list, val_acc, label='Validation Accuracy', color='red')
            ax2.set_title('Training and Validation Accuracy')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Accuracy')
            ax2.legend()
            ax2.grid(True)
            
            # Learning rate schedule
            ax3.plot(epochs_list, lr_schedule, color='green')
            ax3.set_title('Learning Rate Schedule')
            ax3.set_xlabel('Epoch')
            ax3.set_ylabel('Learning Rate')
            ax3.grid(True)
            ax3.set_yscale('log')
            
            # Training metrics distribution
            ax4.hist(train_loss, bins=20, alpha=0.7, label='Train Loss', color='blue', edgecolor='black')
            ax4.hist(val_loss, bins=20, alpha=0.7, label='Val Loss', color='red', edgecolor='black')
            ax4.set_title('Loss Distribution')
            ax4.set_xlabel('Loss')
            ax4.set_ylabel('Frequency')
            ax4.legend()
            
            plt.tight_layout()
            
            # Convert to base64 for Gradio
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            summary_text = f"""
            Training Summary:
            - Total Epochs: {epochs}
            - Initial Learning Rate: {learning_rate}
            - Batch Size: {batch_size}
            - Final Train Loss: {train_loss[-1]:.4f}
            - Final Val Loss: {val_loss[-1]:.4f}
            - Final Train Accuracy: {train_acc[-1]:.4f}
            - Final Val Accuracy: {val_acc[-1]:.4f}
            """
            
            return summary_text, buf.getvalue()
        
        demo = gr.Interface(
            fn=visualize_training,
            inputs=[
                gr.Slider(minimum=10, maximum=200, value=100, step=1, label="Epochs"),
                gr.Slider(minimum=0.0001, maximum=0.01, value=0.001, step=0.0001, label="Learning Rate"),
                gr.Slider(minimum=16, maximum=128, value=32, step=16, label="Batch Size")
            ],
            outputs=[
                gr.Textbox(label="Training Summary"),
                gr.Image(label="Training Visualization")
            ],
            title="Training Visualization",
            description="Visualize training process and metrics",
        )
        
        return demo
    
    def create_evaluation_demo(self) -> Any:
        """Create evaluation metrics demo."""
        def evaluate_predictions(y_true, y_pred, task_type="classification") -> Any:
            """Evaluate predictions with various metrics."""
            try:
                # Parse inputs
                true_values = [float(x.strip()) for x in y_true.split(',')]
                pred_values = [float(x.strip()) for x in y_pred.split(',')]
                
                if len(true_values) != len(pred_values):
                    return "Error: Number of true and predicted values must match", None
                
                # Convert to numpy arrays
                y_true_array = np.array(true_values)
                y_pred_array = np.array(pred_values)
                
                # Calculate metrics based on task type
                if task_type == "classification":
                    # Convert to classes for classification
                    y_true_classes = y_true_array.astype(int)
                    y_pred_classes = y_pred_array.astype(int)
                    
                    # Calculate metrics
                    accuracy = np.mean(y_true_classes == y_pred_classes)
                    
                    # Calculate precision, recall, F1 for each class
                    metrics = {}
                    for class_id in np.unique(y_true_classes):
                        tp = np.sum((y_true_classes == class_id) & (y_pred_classes == class_id))
                        fp = np.sum((y_true_classes != class_id) & (y_pred_classes == class_id))
                        fn = np.sum((y_true_classes == class_id) & (y_pred_classes != class_id))
                        
                        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                        
                        metrics[f'Class_{class_id}'] = {
                            'Precision': precision,
                            'Recall': recall,
                            'F1': f1
                        }
                    
                    metrics['Overall'] = {'Accuracy': accuracy}
                    
                elif task_type == "regression":
                    # Calculate regression metrics
                    mse = np.mean((y_true_array - y_pred_array) ** 2)
                    rmse = np.sqrt(mse)
                    mae = np.mean(np.abs(y_true_array - y_pred_array))
                    r2 = 1 - np.sum((y_true_array - y_pred_array) ** 2) / np.sum((y_true_array - np.mean(y_true_array)) ** 2)
                    
                    metrics = {
                        'MSE': mse,
                        'RMSE': rmse,
                        'MAE': mae,
                        'R²': r2
                    }
                
                # Create visualization
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                
                # Scatter plot
                ax1.scatter(y_true_array, y_pred_array, alpha=0.6)
                ax1.plot([y_true_array.min(), y_true_array.max()], 
                        [y_true_array.min(), y_true_array.max()], 'r--', lw=2)
                ax1.set_xlabel('True Values')
                ax1.set_ylabel('Predicted Values')
                ax1.set_title('True vs Predicted Values')
                ax1.grid(True)
                
                # Metrics bar plot
                if task_type == "classification":
                    metric_names = list(metrics['Overall'].keys())
                    metric_values = list(metrics['Overall'].values())
                else:
                    metric_names = list(metrics.keys())
                    metric_values = list(metrics.values())
                
                ax2.bar(metric_names, metric_values, color='skyblue', edgecolor='black')
                ax2.set_title('Evaluation Metrics')
                ax2.set_ylabel('Score')
                ax2.tick_params(axis='x', rotation=45)
                
                plt.tight_layout()
                
                # Convert to base64 for Gradio
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                plt.close()
                
                # Format results
                results_text = f"Task Type: {task_type}\n\n"
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, dict):
                        results_text += f"{metric_name}:\n"
                        for sub_metric, value in metric_value.items():
                            results_text += f"  {sub_metric}: {value:.4f}\n"
                    else:
                        results_text += f"{metric_name}: {metric_value:.4f}\n"
                
                return results_text, buf.getvalue()
                
            except Exception as e:
                return f"Error: {str(e)}", None
        
        demo = gr.Interface(
            fn=evaluate_predictions,
            inputs=[
                gr.Textbox(label="True Values", placeholder="Enter comma-separated true values"),
                gr.Textbox(label="Predicted Values", placeholder="Enter comma-separated predicted values"),
                gr.Dropdown(choices=["classification", "regression"], value="classification", label="Task Type")
            ],
            outputs=[
                gr.Textbox(label="Evaluation Results"),
                gr.Image(label="Visualization")
            ],
            title="Model Evaluation",
            description="Evaluate model predictions with various metrics",
            examples=[
                ["0,1,0,1,0,1,0,1,0,1", "0,1,0,1,0,1,0,1,0,1", "classification"],
                ["1.0,2.0,3.0,4.0,5.0", "1.1,1.9,3.1,3.9,5.1", "regression"]
            ]
        )
        
        return demo
    
    def create_integration_demo(self) -> Any:
        """Create integration demo."""
        def run_integration_experiment(model_type, task_type, epochs=10, batch_size=32) -> Any:
            """Run integrated experiment."""
            try:
                # Create integration config
                config = IntegrationConfig(
                    integration_type=IntegrationType.FULL,
                    enabled_components=[
                        ComponentType.FRAMEWORK,
                        ComponentType.EVALUATION,
                        ComponentType.STABILITY,
                        ComponentType.TRAINING,
                        ComponentType.DATA_LOADING,
                        ComponentType.DATA_SPLITTING
                    ],
                    task_type=TaskType.CLASSIFICATION if task_type == "classification" else TaskType.REGRESSION,
                    model_name=model_type,
                    learning_rate=1e-3,
                    batch_size=batch_size,
                    num_epochs=epochs,
                    gradient_clipping=True,
                    nan_handling=True,
                    early_stopping=True,
                    learning_rate_scheduling=True,
                    efficient_data_loading=True,
                    data_splitting=True,
                    checkpointing=True,
                    logging=True,
                    visualization=True,
                    save_results=True
                )
                
                # Create integration system
                integration = DeepLearningIntegration(config)
                
                # Create sample dataset
                class SampleDataset(torch.utils.data.Dataset):
                    def __init__(self, num_samples=1000, input_size=784, num_classes=10) -> Any:
                        self.data = torch.randn(num_samples, input_size)
                        self.targets = torch.randint(0, num_classes, (num_samples,))
                    
                    def __len__(self) -> Any:
                        return len(self.data)
                    
                    def __getitem__(self, idx) -> Optional[Dict[str, Any]]:
                        return self.data[idx], self.targets[idx]
                
                # Create sample model
                class SampleModel(nn.Module):
                    def __init__(self, input_size=784, hidden_size=512, num_classes=10) -> Any:
                        super(SampleModel, self).__init__()
                        self.fc1 = nn.Linear(input_size, hidden_size)
                        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
                        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
                        self.relu = nn.ReLU()
                        self.dropout = nn.Dropout(0.2)
                    
                    def forward(self, x) -> Any:
                        x = self.dropout(self.relu(self.fc1(x)))
                        x = self.dropout(self.relu(self.fc2(x)))
                        x = self.fc3(x)
                        return x
                
                # Setup model and data
                dataset = SampleDataset(num_samples=1000, input_size=784, num_classes=10)
                integration.setup_model(SampleModel, input_size=784, hidden_size=512, num_classes=10)
                integration.setup_data(dataset)
                
                # Train
                training_history = integration.train()
                
                # Evaluate
                evaluation_results = integration.evaluate()
                
                # Create visualization
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
                
                # Training loss
                ax1.plot(training_history['epochs'], training_history['train_losses'], label='Train Loss')
                ax1.plot(training_history['epochs'], training_history['val_losses'], label='Val Loss')
                ax1.set_title('Training and Validation Loss')
                ax1.set_xlabel('Epoch')
                ax1.set_ylabel('Loss')
                ax1.legend()
                ax1.grid(True)
                
                # Training accuracy
                ax2.plot(training_history['epochs'], training_history['train_accuracies'], label='Train Accuracy')
                ax2.plot(training_history['epochs'], training_history['val_accuracies'], label='Val Accuracy')
                ax2.set_title('Training and Validation Accuracy')
                ax2.set_xlabel('Epoch')
                ax2.set_ylabel('Accuracy')
                ax2.legend()
                ax2.grid(True)
                
                # Learning rate
                ax3.plot(training_history['epochs'], training_history['learning_rates'])
                ax3.set_title('Learning Rate Schedule')
                ax3.set_xlabel('Epoch')
                ax3.set_ylabel('Learning Rate')
                ax3.grid(True)
                ax3.set_yscale('log')
                
                # Stability scores
                ax4.plot(training_history['epochs'], training_history['stability_scores'])
                ax4.set_title('Numerical Stability Score')
                ax4.set_xlabel('Epoch')
                ax4.set_ylabel('Stability Score')
                ax4.grid(True)
                
                plt.tight_layout()
                
                # Convert to base64 for Gradio
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                plt.close()
                
                # Format results
                results_text = f"""
                Integration Experiment Results:
                
                Configuration:
                - Model Type: {model_type}
                - Task Type: {task_type}
                - Epochs: {epochs}
                - Batch Size: {batch_size}
                
                Training Results:
                - Final Train Loss: {training_history['train_losses'][-1]:.4f}
                - Final Val Loss: {training_history['val_losses'][-1]:.4f}
                - Final Train Accuracy: {training_history['train_accuracies'][-1]:.4f}
                - Final Val Accuracy: {training_history['val_accuracies'][-1]:.4f}
                - Final Stability Score: {training_history['stability_scores'][-1]:.4f}
                
                Evaluation Results:
                {json.dumps(evaluation_results, indent=2)}
                """
                
                return results_text, buf.getvalue()
                
            except Exception as e:
                return f"Error: {str(e)}", None
        
        demo = gr.Interface(
            fn=run_integration_experiment,
            inputs=[
                gr.Dropdown(choices=["simple", "advanced", "transformer"], value="simple", label="Model Type"),
                gr.Dropdown(choices=["classification", "regression"], value="classification", label="Task Type"),
                gr.Slider(minimum=5, maximum=50, value=10, step=1, label="Epochs"),
                gr.Slider(minimum=16, maximum=128, value=32, step=16, label="Batch Size")
            ],
            outputs=[
                gr.Textbox(label="Integration Results"),
                gr.Image(label="Training Visualization")
            ],
            title="Deep Learning Integration Demo",
            description="Run integrated deep learning experiments with all components",
        )
        
        return demo
    
    def create_all_demos(self) -> Any:
        """Create all demos and combine them."""
        demos = [
            ("Classification", self.create_classification_demo()),
            ("Regression", self.create_regression_demo()),
            ("Text Generation", self.create_text_generation_demo()),
            ("Model Analysis", self.create_model_analysis_demo()),
            ("Training Visualization", self.create_training_visualization_demo()),
            ("Evaluation", self.create_evaluation_demo()),
            ("Integration", self.create_integration_demo())
        ]
        
        # Create tabbed interface
        with gr.Blocks(title="Deep Learning Interactive Demos") as demo:
            gr.Markdown("# Deep Learning Interactive Demos")
            gr.Markdown("Explore various deep learning components through interactive demos")
            
            with gr.Tabs():
                for name, demo_interface in demos:
                    with gr.TabItem(name):
                        demo_interface.render()
        
        return demo


def launch_demos():
    """Launch all interactive demos."""
    print("Launching Deep Learning Interactive Demos...")
    
    # Create demo manager
    demo_manager = GradioDemoManager()
    
    # Create combined demo
    combined_demo = demo_manager.create_all_demos()
    
    # Launch the demo
    combined_demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True
    )


if __name__ == "__main__":
    # Launch the demos
    launch_demos() 