#!/usr/bin/env python3
"""
🔬 Experiment Tracking Example for Gradio App
=============================================

Comprehensive example demonstrating experiment tracking with TensorBoard and Weights & Biases.
Shows various use cases and integration patterns.
"""

import sys
import os
import json
import time
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from experiment_tracking_system import (
    ExperimentTracker, ExperimentConfig, create_experiment_config,
    experiment_context, track_experiment, start_tensorboard_server,
    compare_experiments, get_tensorboard_url
)

# =============================================================================
# EXAMPLE MODELS AND TRAINING FUNCTIONS
# =============================================================================

class SimpleModel(nn.Module):
    """Simple neural network for demonstration"""
    
    def __init__(self, input_size: int = 10, hidden_size: int = 64, num_classes: int = 2):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x


class ConvModel(nn.Module):
    """Convolutional neural network for demonstration"""
    
    def __init__(self, num_classes: int = 2):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x


def generate_sample_data(num_samples: int = 1000, input_size: int = 10) -> tuple:
    """Generate sample training data"""
    # Generate features
    X = torch.randn(num_samples, input_size)
    
    # Generate labels (simple classification task)
    y = torch.randint(0, 2, (num_samples,))
    
    # Add some correlation between features and labels
    for i in range(num_samples):
        if y[i] == 1:
            X[i, :5] += 0.5  # Add bias for positive class
    
    return X, y


def calculate_metrics(outputs: torch.Tensor, targets: torch.Tensor) -> Dict[str, float]:
    """Calculate various metrics"""
    _, predicted = torch.max(outputs, 1)
    correct = (predicted == targets).sum().item()
    total = targets.size(0)
    
    accuracy = correct / total
    
    # Calculate precision, recall, F1 for binary classification
    if outputs.size(1) == 2:
        # Convert to binary
        binary_pred = (predicted == 1).float()
        binary_target = (targets == 1).float()
        
        tp = (binary_pred * binary_target).sum().item()
        fp = (binary_pred * (1 - binary_target)).sum().item()
        fn = ((1 - binary_pred) * binary_target).sum().item()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    else:
        precision = recall = f1 = 0.0
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }


# =============================================================================
# TRAINING FUNCTIONS WITH EXPERIMENT TRACKING
# =============================================================================

def train_model_with_tracking(model: nn.Module, train_data: tuple, val_data: tuple,
                             config: ExperimentConfig, num_epochs: int = 10) -> Dict[str, Any]:
    """Train model with comprehensive experiment tracking"""
    
    X_train, y_train = train_data
    X_val, y_val = val_data
    
    # Setup training components
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.learning_rate if hasattr(config, 'learning_rate') else 0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
    
    # Use experiment context manager
    with experiment_context(config) as tracker:
        
        # Log hyperparameters
        hyperparams = {
            'learning_rate': optimizer.param_groups[0]['lr'],
            'batch_size': 32,
            'num_epochs': num_epochs,
            'model_type': model.__class__.__name__,
            'optimizer': 'Adam',
            'scheduler': 'StepLR',
            'criterion': 'CrossEntropyLoss'
        }
        tracker.log_hyperparameters(hyperparams)
        
        # Log model architecture
        tracker.log_model_architecture(model, input_shape=(X_train.shape[1],))
        
        # Training loop
        for epoch in range(num_epochs):
            epoch_start_time = time.time()
            tracker.log_epoch(epoch)
            
            # Training phase
            model.train()
            train_losses = []
            train_metrics_list = []
            
            for step in range(0, len(X_train), 32):
                batch_X = X_train[step:step+32]
                batch_y = y_train[step:step+32]
                
                step_start_time = time.time()
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                step_time = time.time() - step_start_time
                
                # Calculate metrics
                metrics = calculate_metrics(outputs, batch_y)
                train_losses.append(loss.item())
                train_metrics_list.append(metrics)
                
                # Log training step
                tracker.log_training_step(
                    loss=loss.item(),
                    accuracy=metrics['accuracy'],
                    learning_rate=optimizer.param_groups[0]['lr'],
                    step_time=step_time
                )
                
                # Log gradients occasionally
                if step % 100 == 0:
                    tracker.log_gradients(model)
                
                # Log system metrics occasionally
                if step % 200 == 0:
                    if torch.cuda.is_available():
                        gpu_memory = torch.cuda.memory_allocated() / 1024**3  # GB
                        gpu_utilization = 50.0 + np.random.random() * 30  # Simulated
                    else:
                        gpu_memory = gpu_utilization = 0.0
                    
                    tracker.log_system_metrics(
                        gpu_memory=gpu_memory,
                        gpu_utilization=gpu_utilization,
                        cpu_usage=30.0 + np.random.random() * 20,
                        memory_usage=40.0 + np.random.random() * 15
                    )
            
            # Validation phase
            model.eval()
            val_losses = []
            val_metrics_list = []
            
            with torch.no_grad():
                for step in range(0, len(X_val), 32):
                    batch_X = X_val[step:step+32]
                    batch_y = y_val[step:step+32]
                    
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    metrics = calculate_metrics(outputs, batch_y)
                    
                    val_losses.append(loss.item())
                    val_metrics_list.append(metrics)
            
            # Calculate average metrics
            avg_train_loss = np.mean(train_losses)
            avg_train_metrics = {
                key: np.mean([m[key] for m in train_metrics_list]) 
                for key in train_metrics_list[0].keys()
            }
            
            avg_val_loss = np.mean(val_losses)
            avg_val_metrics = {
                key: np.mean([m[key] for m in val_metrics_list]) 
                for key in val_metrics_list[0].keys()
            }
            
            # Log validation metrics
            tracker.log_validation_step(
                loss=avg_val_loss,
                accuracy=avg_val_metrics['accuracy'],
                precision=avg_val_metrics['precision'],
                recall=avg_val_metrics['recall'],
                f1=avg_val_metrics['f1']
            )
            
            # Log epoch time
            epoch_time = time.time() - epoch_start_time
            tracker.log_epoch(epoch, epoch_time)
            
            # Update learning rate
            scheduler.step()
            
            # Save checkpoint
            tracker.log_model_checkpoint(
                model, optimizer, epoch=epoch,
                metrics={
                    'train_loss': avg_train_loss,
                    'val_loss': avg_val_loss,
                    'train_accuracy': avg_train_metrics['accuracy'],
                    'val_accuracy': avg_val_metrics['accuracy']
                }
            )
            
            print(f"Epoch {epoch+1}/{num_epochs}: "
                  f"Train Loss: {avg_train_loss:.4f}, "
                  f"Val Loss: {avg_val_loss:.4f}, "
                  f"Val Acc: {avg_val_metrics['accuracy']:.4f}")
        
        # Get final summary
        summary = tracker.get_experiment_summary()
        return summary


@track_experiment()
def train_with_decorator(model: nn.Module, train_data: tuple, val_data: tuple,
                        num_epochs: int = 5) -> Dict[str, Any]:
    """Example of using the @track_experiment decorator"""
    
    print("Training with decorator-based tracking...")
    
    # Simple training loop for demonstration
    X_train, y_train = train_data
    X_val, y_val = val_data
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        total_loss = 0
        for step in range(0, len(X_train), 32):
            batch_X = X_train[step:step+32]
            batch_y = y_train[step:step+32]
            
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        # Validation
        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for step in range(0, len(X_val), 32):
                batch_X = X_val[step:step+32]
                batch_y = y_val[step:step+32]
                
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item()
                
                _, predicted = torch.max(outputs, 1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()
        
        print(f"Epoch {epoch+1}: Train Loss: {total_loss/len(X_train)*32:.4f}, "
              f"Val Loss: {val_loss/len(X_val)*32:.4f}, "
              f"Val Acc: {correct/total:.4f}")
    
    return {"final_accuracy": correct/total}


def train_with_custom_metrics(model: nn.Module, train_data: tuple, val_data: tuple,
                             config: ExperimentConfig) -> Dict[str, Any]:
    """Train model with custom metrics and visualizations"""
    
    X_train, y_train = train_data
    X_val, y_val = val_data
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    with experiment_context(config) as tracker:
        
        # Log hyperparameters
        tracker.log_hyperparameters({
            'learning_rate': 0.001,
            'batch_size': 32,
            'model_type': 'CustomMetricsModel'
        })
        
        # Training loop
        for epoch in range(10):
            model.train()
            
            for step in range(0, len(X_train), 32):
                batch_X = X_train[step:step+32]
                batch_y = y_train[step:step+32]
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                # Log custom metrics
                if step % 50 == 0:
                    # Calculate gradient norm
                    total_norm = 0
                    for p in model.parameters():
                        if p.grad is not None:
                            param_norm = p.grad.data.norm(2)
                            total_norm += param_norm.item() ** 2
                    total_norm = total_norm ** (1. / 2)
                    
                    # Calculate parameter statistics
                    param_stats = {}
                    for name, param in model.named_parameters():
                        param_stats[f'{name}_mean'] = param.data.mean().item()
                        param_stats[f'{name}_std'] = param.data.std().item()
                    
                    # Log custom metrics
                    custom_metrics = {
                        'gradient_norm': total_norm,
                        'loss': loss.item(),
                        **param_stats
                    }
                    tracker.log_metrics(custom_metrics, prefix="custom")
            
            # Log sample predictions as text
            model.eval()
            with torch.no_grad():
                sample_outputs = model(X_val[:10])
                sample_preds = torch.softmax(sample_outputs, dim=1)
                
                prediction_text = "Sample Predictions:\n"
                for i in range(5):
                    pred_class = torch.argmax(sample_preds[i]).item()
                    confidence = sample_preds[i][pred_class].item()
                    prediction_text += f"Sample {i}: Class {pred_class} (Confidence: {confidence:.3f})\n"
                
                tracker.log_text(prediction_text, title="sample_predictions")
        
        return {"status": "completed"}


# =============================================================================
# VISUALIZATION AND ANALYSIS FUNCTIONS
# =============================================================================

def create_training_visualizations(tracker: ExperimentTracker) -> Dict[str, plt.Figure]:
    """Create comprehensive training visualizations"""
    
    plots = {}
    
    # Create custom plots
    if tracker.metrics.train_loss and tracker.metrics.val_loss:
        fig, (ax1, ax2) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss comparison
        ax1[0].plot(tracker.metrics.train_loss, label='Training Loss', color='blue')
        ax1[0].plot(tracker.metrics.val_loss, label='Validation Loss', color='red')
        ax1[0].set_title('Training vs Validation Loss')
        ax1[0].set_xlabel('Step')
        ax1[0].set_ylabel('Loss')
        ax1[0].legend()
        ax1[0].grid(True)
        
        # Accuracy comparison
        if tracker.metrics.train_accuracy and tracker.metrics.val_accuracy:
            ax1[1].plot(tracker.metrics.train_accuracy, label='Training Accuracy', color='blue')
            ax1[1].plot(tracker.metrics.val_accuracy, label='Validation Accuracy', color='red')
            ax1[1].set_title('Training vs Validation Accuracy')
            ax1[1].set_xlabel('Step')
            ax1[1].set_ylabel('Accuracy')
            ax1[1].legend()
            ax1[1].grid(True)
        
        # Learning rate
        if tracker.metrics.learning_rate:
            ax2[0].plot(tracker.metrics.learning_rate, color='green')
            ax2[0].set_title('Learning Rate Schedule')
            ax2[0].set_xlabel('Step')
            ax2[0].set_ylabel('Learning Rate')
            ax2[0].grid(True)
        
        # System metrics
        if tracker.metrics.gpu_memory or tracker.metrics.cpu_usage:
            if tracker.metrics.gpu_memory:
                ax2[1].plot(tracker.metrics.gpu_memory, label='GPU Memory', color='purple')
            if tracker.metrics.cpu_usage:
                ax2[1].plot(tracker.metrics.cpu_usage, label='CPU Usage', color='orange')
            ax2[1].set_title('System Resource Usage')
            ax2[1].set_xlabel('Step')
            ax2[1].set_ylabel('Usage')
            ax2[1].legend()
            ax2[1].grid(True)
        
        plt.tight_layout()
        plots['training_overview'] = fig
    
    return plots


def analyze_experiment_results(tracker: ExperimentTracker) -> Dict[str, Any]:
    """Analyze experiment results and provide insights"""
    
    analysis = {
        'total_steps': len(tracker.metrics.train_loss) if tracker.metrics.train_loss else 0,
        'total_epochs': tracker.epoch,
        'final_train_loss': tracker.metrics.train_loss[-1] if tracker.metrics.train_loss else None,
        'final_val_loss': tracker.metrics.val_loss[-1] if tracker.metrics.val_loss else None,
        'best_val_accuracy': max(tracker.metrics.val_accuracy) if tracker.metrics.val_accuracy else None,
        'convergence_analysis': {},
        'performance_insights': []
    }
    
    # Analyze convergence
    if tracker.metrics.train_loss and tracker.metrics.val_loss:
        train_loss = tracker.metrics.train_loss
        val_loss = tracker.metrics.val_loss
        
        # Check for overfitting
        if len(train_loss) > 10 and len(val_loss) > 10:
            early_train = np.mean(train_loss[:10])
            late_train = np.mean(train_loss[-10:])
            early_val = np.mean(val_loss[:10])
            late_val = np.mean(val_loss[-10:])
            
            train_improvement = early_train - late_train
            val_improvement = early_val - late_val
            
            if val_improvement < train_improvement * 0.5:
                analysis['convergence_analysis']['overfitting'] = True
                analysis['performance_insights'].append("Potential overfitting detected")
            else:
                analysis['convergence_analysis']['overfitting'] = False
                analysis['performance_insights'].append("Good generalization")
        
        # Check for convergence
        if len(train_loss) > 20:
            recent_loss = train_loss[-20:]
            loss_std = np.std(recent_loss)
            if loss_std < 0.01:
                analysis['convergence_analysis']['converged'] = True
                analysis['performance_insights'].append("Model appears to have converged")
            else:
                analysis['convergence_analysis']['converged'] = False
                analysis['performance_insights'].append("Model may need more training")
    
    # Analyze learning rate
    if tracker.metrics.learning_rate:
        lr_changes = len(set(tracker.metrics.learning_rate))
        analysis['convergence_analysis']['lr_schedule_used'] = lr_changes > 1
        if lr_changes > 1:
            analysis['performance_insights'].append("Learning rate schedule was effective")
    
    return analysis


# =============================================================================
# MAIN EXAMPLE FUNCTIONS
# =============================================================================

def example_basic_training():
    """Basic training example with experiment tracking"""
    print("🔬 Basic Training with Experiment Tracking")
    print("=" * 50)
    
    # Create experiment configuration
    config = create_experiment_config(
        experiment_name="basic_training_example",
        project_name="gradio_demo",
        enable_tensorboard=True,
        enable_wandb=True,
        log_interval=10,
        save_interval=50
    )
    
    # Generate data
    X_train, y_train = generate_sample_data(1000, 10)
    X_val, y_val = generate_sample_data(200, 10)
    
    # Create model
    model = SimpleModel(input_size=10, hidden_size=64, num_classes=2)
    
    # Train with tracking
    summary = train_model_with_tracking(model, (X_train, y_train), (X_val, y_val), config, num_epochs=10)
    
    print("\n📊 Experiment Summary:")
    print(json.dumps(summary, indent=2))
    
    return summary


def example_decorator_training():
    """Example using the @track_experiment decorator"""
    print("\n🔬 Decorator-based Training Example")
    print("=" * 50)
    
    # Generate data
    X_train, y_train = generate_sample_data(500, 10)
    X_val, y_val = generate_sample_data(100, 10)
    
    # Create model
    model = SimpleModel(input_size=10, hidden_size=32, num_classes=2)
    
    # Train with decorator
    result = train_with_decorator(model, (X_train, y_train), (X_val, y_val), num_epochs=5)
    
    print(f"\n📊 Final Result: {result}")
    
    return result


def example_custom_metrics():
    """Example with custom metrics and visualizations"""
    print("\n🔬 Custom Metrics Training Example")
    print("=" * 50)
    
    # Create experiment configuration
    config = create_experiment_config(
        experiment_name="custom_metrics_example",
        project_name="gradio_demo",
        enable_tensorboard=True,
        enable_wandb=True,
        log_interval=5
    )
    
    # Generate data
    X_train, y_train = generate_sample_data(800, 10)
    X_val, y_val = generate_sample_data(150, 10)
    
    # Create model
    model = SimpleModel(input_size=10, hidden_size=48, num_classes=2)
    
    # Train with custom metrics
    result = train_with_custom_metrics(model, (X_train, y_train), (X_val, y_val), config)
    
    print(f"\n📊 Custom Metrics Result: {result}")
    
    return result


def example_tensorboard_integration():
    """Example demonstrating TensorBoard integration"""
    print("\n🔬 TensorBoard Integration Example")
    print("=" * 50)
    
    # Create configuration with TensorBoard only
    config = create_experiment_config(
        experiment_name="tensorboard_example",
        project_name="gradio_demo",
        enable_tensorboard=True,
        enable_wandb=False,
        log_interval=5
    )
    
    # Generate data
    X_train, y_train = generate_sample_data(600, 10)
    X_val, y_val = generate_sample_data(120, 10)
    
    # Create model
    model = SimpleModel(input_size=10, hidden_size=32, num_classes=2)
    
    # Train with TensorBoard tracking
    with experiment_context(config) as tracker:
        
        # Log hyperparameters
        tracker.log_hyperparameters({
            'learning_rate': 0.001,
            'batch_size': 32,
            'model_type': 'TensorBoardExample'
        })
        
        # Simple training loop
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        for epoch in range(5):
            model.train()
            total_loss = 0
            
            for step in range(0, len(X_train), 32):
                batch_X = X_train[step:step+32]
                batch_y = y_train[step:step+32]
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                
                # Log metrics
                if step % 32 == 0:
                    tracker.log_training_step(loss=loss.item())
            
            # Log epoch
            tracker.log_epoch(epoch)
            
            print(f"Epoch {epoch+1}: Loss: {total_loss/len(X_train)*32:.4f}")
    
    # Get TensorBoard URL
    tensorboard_url = get_tensorboard_url(config.tensorboard_dir)
    print(f"\n📊 TensorBoard URL: {tensorboard_url}")
    print("Run 'tensorboard --logdir runs/tensorboard' to view logs")
    
    return {"tensorboard_url": tensorboard_url}


def example_wandb_integration():
    """Example demonstrating Weights & Biases integration"""
    print("\n🔬 Weights & Biases Integration Example")
    print("=" * 50)
    
    # Create configuration with wandb only
    config = create_experiment_config(
        experiment_name="wandb_example",
        project_name="gradio_demo",
        enable_tensorboard=False,
        enable_wandb=True,
        log_interval=5,
        wandb_entity=None,  # Set to your wandb username if desired
        tags=["example", "gradio", "demo"]
    )
    
    # Generate data
    X_train, y_train = generate_sample_data(700, 10)
    X_val, y_val = generate_sample_data(140, 10)
    
    # Create model
    model = SimpleModel(input_size=10, hidden_size=40, num_classes=2)
    
    # Train with wandb tracking
    with experiment_context(config) as tracker:
        
        # Log hyperparameters
        tracker.log_hyperparameters({
            'learning_rate': 0.001,
            'batch_size': 32,
            'model_type': 'WandBExample',
            'dataset_size': len(X_train)
        })
        
        # Log model architecture
        tracker.log_model_architecture(model, input_shape=(10,))
        
        # Simple training loop
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        for epoch in range(5):
            model.train()
            total_loss = 0
            correct = 0
            total = 0
            
            for step in range(0, len(X_train), 32):
                batch_X = X_train[step:step+32]
                batch_y = y_train[step:step+32]
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                
                # Calculate accuracy
                _, predicted = torch.max(outputs, 1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()
                
                # Log metrics
                if step % 32 == 0:
                    accuracy = correct / total
                    tracker.log_training_step(
                        loss=loss.item(),
                        accuracy=accuracy,
                        learning_rate=optimizer.param_groups[0]['lr']
                    )
            
            # Log epoch
            tracker.log_epoch(epoch)
            
            print(f"Epoch {epoch+1}: Loss: {total_loss/len(X_train)*32:.4f}, "
                  f"Accuracy: {correct/total:.4f}")
    
    print(f"\n📊 Weights & Biases run completed")
    print("Check your wandb dashboard for detailed logs and visualizations")
    
    return {"wandb_run": "completed"}


def example_comparison_analysis():
    """Example of comparing multiple experiments"""
    print("\n🔬 Experiment Comparison Analysis")
    print("=" * 50)
    
    # Create multiple experiments with different configurations
    experiments = [
        ("experiment_1", {"learning_rate": 0.001, "hidden_size": 32}),
        ("experiment_2", {"learning_rate": 0.01, "hidden_size": 64}),
        ("experiment_3", {"learning_rate": 0.0001, "hidden_size": 128})
    ]
    
    results = {}
    
    for exp_name, config_params in experiments:
        print(f"\nRunning {exp_name}...")
        
        # Create configuration
        config = create_experiment_config(
            experiment_name=exp_name,
            project_name="gradio_demo",
            enable_tensorboard=True,
            enable_wandb=True,
            log_interval=10
        )
        
        # Generate data
        X_train, y_train = generate_sample_data(500, 10)
        X_val, y_val = generate_sample_data(100, 10)
        
        # Create model with different parameters
        model = SimpleModel(
            input_size=10,
            hidden_size=config_params["hidden_size"],
            num_classes=2
        )
        
        # Train with tracking
        with experiment_context(config) as tracker:
            
            # Log hyperparameters
            tracker.log_hyperparameters(config_params)
            
            # Simple training loop
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(model.parameters(), lr=config_params["learning_rate"])
            
            for epoch in range(3):  # Shorter training for comparison
                model.train()
                total_loss = 0
                
                for step in range(0, len(X_train), 32):
                    batch_X = X_train[step:step+32]
                    batch_y = y_train[step:step+32]
                    
                    optimizer.zero_grad()
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
                    
                    if step % 32 == 0:
                        tracker.log_training_step(loss=loss.item())
                
                tracker.log_epoch(epoch)
            
            # Store results
            results[exp_name] = {
                'final_loss': tracker.metrics.train_loss[-1] if tracker.metrics.train_loss else None,
                'config': config_params
            }
    
    # Create comparison plot
    fig = compare_experiments(list(results.keys()), "train_loss")
    if fig:
        plt.savefig("experiment_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("\n📊 Comparison plot saved as 'experiment_comparison.png'")
    
    print("\n📊 Experiment Comparison Results:")
    for exp_name, result in results.items():
        print(f"{exp_name}: Final Loss = {result['final_loss']:.4f}, "
              f"Config = {result['config']}")
    
    return results


def main():
    """Run all examples"""
    print("🔬 Experiment Tracking System Examples")
    print("=" * 60)
    
    examples = [
        ("Basic Training", example_basic_training),
        ("Decorator Training", example_decorator_training),
        ("Custom Metrics", example_custom_metrics),
        ("TensorBoard Integration", example_tensorboard_integration),
        ("Weights & Biases Integration", example_wandb_integration),
        ("Experiment Comparison", example_comparison_analysis)
    ]
    
    results = {}
    
    for name, example_func in examples:
        try:
            print(f"\n{'='*20} {name} {'='*20}")
            result = example_func()
            results[name] = result
            print(f"✅ {name} completed successfully")
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results[name] = {"error": str(e)}
    
    print(f"\n{'='*60}")
    print("📊 All Examples Completed")
    print("=" * 60)
    
    # Summary
    successful = sum(1 for r in results.values() if "error" not in r)
    total = len(results)
    
    print(f"Successful: {successful}/{total}")
    
    for name, result in results.items():
        status = "✅" if "error" not in result else "❌"
        print(f"{status} {name}")
    
    return results


if __name__ == "__main__":
    main() 