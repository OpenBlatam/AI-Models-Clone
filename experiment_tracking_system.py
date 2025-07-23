#!/usr/bin/env python3
"""
🔬 Experiment Tracking System for Gradio App
============================================

Comprehensive experiment tracking system integrating TensorBoard and Weights & Biases.
Provides unified logging, visualization, and experiment management capabilities.
"""

import os
import json
import time
import logging
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import threading
import queue

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from torch.utils.tensorboard import SummaryWriter

# Import wandb with error handling
try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    print("Warning: Weights & Biases not available. Install with: pip install wandb")

logger = logging.getLogger(__name__)

# =============================================================================
# EXPERIMENT TRACKING CONFIGURATION
# =============================================================================

@dataclass
class ExperimentConfig:
    """Configuration for experiment tracking"""
    
    # Experiment metadata
    experiment_name: str = "gradio_experiment"
    project_name: str = "blatam_academy"
    run_name: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    # Tracking settings
    enable_tensorboard: bool = True
    enable_wandb: bool = True
    log_interval: int = 100  # Log every N steps
    save_interval: int = 1000  # Save model every N steps
    
    # Logging settings
    log_metrics: bool = True
    log_hyperparameters: bool = True
    log_model_architecture: bool = True
    log_gradients: bool = True
    log_images: bool = True
    log_text: bool = True
    
    # File paths
    tensorboard_dir: str = "runs/tensorboard"
    model_save_dir: str = "models"
    config_save_dir: str = "configs"
    
    # Wandb settings
    wandb_entity: Optional[str] = None
    wandb_group: Optional[str] = None
    wandb_job_type: str = "training"
    
    # Advanced settings
    sync_tensorboard: bool = True  # Sync TensorBoard logs to wandb
    resume_run: bool = False
    anonymous: bool = False


@dataclass
class ExperimentMetrics:
    """Container for experiment metrics"""
    
    # Training metrics
    train_loss: List[float] = field(default_factory=list)
    train_accuracy: List[float] = field(default_factory=list)
    train_precision: List[float] = field(default_factory=list)
    train_recall: List[float] = field(default_factory=list)
    train_f1: List[float] = field(default_factory=list)
    
    # Validation metrics
    val_loss: List[float] = field(default_factory=list)
    val_accuracy: List[float] = field(default_factory=list)
    val_precision: List[float] = field(default_factory=list)
    val_recall: List[float] = field(default_factory=list)
    val_f1: List[float] = field(default_factory=list)
    
    # Learning rate
    learning_rate: List[float] = field(default_factory=list)
    
    # System metrics
    gpu_memory: List[float] = field(default_factory=list)
    gpu_utilization: List[float] = field(default_factory=list)
    cpu_usage: List[float] = field(default_factory=list)
    memory_usage: List[float] = field(default_factory=list)
    
    # Timing metrics
    epoch_time: List[float] = field(default_factory=list)
    step_time: List[float] = field(default_factory=list)
    
    # Custom metrics
    custom_metrics: Dict[str, List[float]] = field(default_factory=dict)


# =============================================================================
# EXPERIMENT TRACKER CLASS
# =============================================================================

class ExperimentTracker:
    """Unified experiment tracker for TensorBoard and Weights & Biases"""
    
    def __init__(self, config: ExperimentConfig = None):
        """Initialize experiment tracker"""
        self.config = config or ExperimentConfig()
        self.metrics = ExperimentMetrics()
        self.step = 0
        self.epoch = 0
        self.start_time = time.time()
        
        # Initialize TensorBoard
        self.tensorboard_writer = None
        if self.config.enable_tensorboard:
            self._init_tensorboard()
        
        # Initialize Weights & Biases
        self.wandb_run = None
        if self.config.enable_wandb and WANDB_AVAILABLE:
            self._init_wandb()
        
        # Create directories
        self._create_directories()
        
        logger.info(f"Experiment tracker initialized: {self.config.experiment_name}")
    
    def _init_tensorboard(self):
        """Initialize TensorBoard writer"""
        try:
            tensorboard_path = Path(self.config.tensorboard_dir) / self.config.experiment_name
            tensorboard_path.mkdir(parents=True, exist_ok=True)
            
            self.tensorboard_writer = SummaryWriter(
                log_dir=str(tensorboard_path),
                comment=f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            logger.info(f"TensorBoard initialized: {tensorboard_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize TensorBoard: {e}")
            self.config.enable_tensorboard = False
    
    def _init_wandb(self):
        """Initialize Weights & Biases"""
        try:
            if not WANDB_AVAILABLE:
                raise ImportError("wandb not available")
            
            # Configure wandb
            wandb_config = {
                "experiment_name": self.config.experiment_name,
                "project_name": self.config.project_name,
                "enable_tensorboard": self.config.enable_tensorboard,
                "log_interval": self.config.log_interval,
                "save_interval": self.config.save_interval,
            }
            
            # Initialize wandb run
            self.wandb_run = wandb.init(
                project=self.config.project_name,
                name=self.config.run_name or f"{self.config.experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                entity=self.config.wandb_entity,
                group=self.config.wandb_group,
                job_type=self.config.wandb_job_type,
                tags=self.config.tags,
                notes=self.config.notes,
                config=wandb_config,
                resume=self.config.resume_run,
                anonymous=self.config.anonymous,
                sync_tensorboard=self.config.sync_tensorboard
            )
            
            logger.info(f"Weights & Biases initialized: {self.wandb_run.name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Weights & Biases: {e}")
            self.config.enable_wandb = False
    
    def _create_directories(self):
        """Create necessary directories"""
        try:
            Path(self.config.model_save_dir).mkdir(parents=True, exist_ok=True)
            Path(self.config.config_save_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
    
    def log_hyperparameters(self, hyperparams: Dict[str, Any]):
        """Log hyperparameters"""
        try:
            if self.config.log_hyperparameters:
                # Log to TensorBoard
                if self.tensorboard_writer:
                    for key, value in hyperparams.items():
                        self.tensorboard_writer.add_text(f"hyperparameters/{key}", str(value), 0)
                
                # Log to wandb
                if self.wandb_run:
                    wandb.config.update(hyperparams)
                
                # Save to file
                config_path = Path(self.config.config_save_dir) / f"{self.config.experiment_name}_config.json"
                with open(config_path, 'w') as f:
                    json.dump(hyperparams, f, indent=2, default=str)
                
                logger.info(f"Hyperparameters logged: {len(hyperparams)} parameters")
                
        except Exception as e:
            logger.error(f"Failed to log hyperparameters: {e}")
    
    def log_model_architecture(self, model: nn.Module, input_shape: Tuple[int, ...] = None):
        """Log model architecture"""
        try:
            if self.config.log_model_architecture:
                # Log to TensorBoard
                if self.tensorboard_writer and input_shape:
                    dummy_input = torch.randn(1, *input_shape)
                    self.tensorboard_writer.add_graph(model, dummy_input)
                
                # Log to wandb
                if self.wandb_run:
                    wandb.watch(model, log="all", log_freq=self.config.log_interval)
                
                # Save model summary
                model_summary = str(model)
                if self.tensorboard_writer:
                    self.tensorboard_writer.add_text("model/architecture", model_summary, 0)
                
                logger.info("Model architecture logged")
                
        except Exception as e:
            logger.error(f"Failed to log model architecture: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None, prefix: str = ""):
        """Log metrics to TensorBoard and wandb"""
        try:
            if not self.config.log_metrics:
                return
            
            current_step = step if step is not None else self.step
            
            # Log to TensorBoard
            if self.tensorboard_writer:
                for key, value in metrics.items():
                    full_key = f"{prefix}/{key}" if prefix else key
                    self.tensorboard_writer.add_scalar(full_key, value, current_step)
            
            # Log to wandb
            if self.wandb_run:
                wandb_metrics = {f"{prefix}/{key}" if prefix else key: value for key, value in metrics.items()}
                wandb.log(wandb_metrics, step=current_step)
            
            # Store in local metrics
            self._store_metrics(metrics, prefix)
            
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")
    
    def _store_metrics(self, metrics: Dict[str, float], prefix: str = ""):
        """Store metrics in local container"""
        try:
            for key, value in metrics.items():
                full_key = f"{prefix}_{key}" if prefix else key
                
                if hasattr(self.metrics, full_key):
                    getattr(self.metrics, full_key).append(value)
                elif full_key in self.metrics.custom_metrics:
                    self.metrics.custom_metrics[full_key].append(value)
                else:
                    self.metrics.custom_metrics[full_key] = [value]
                    
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    def log_gradients(self, model: nn.Module, step: Optional[int] = None):
        """Log gradient information"""
        try:
            if not self.config.log_gradients:
                return
            
            current_step = step if step is not None else self.step
            
            # Log to TensorBoard
            if self.tensorboard_writer:
                for name, param in model.named_parameters():
                    if param.grad is not None:
                        self.tensorboard_writer.add_histogram(
                            f"gradients/{name}", param.grad, current_step
                        )
                        self.tensorboard_writer.add_scalar(
                            f"gradient_norms/{name}", param.grad.norm().item(), current_step
                        )
            
            # Log to wandb
            if self.wandb_run:
                for name, param in model.named_parameters():
                    if param.grad is not None:
                        wandb.log({
                            f"gradients/{name}": wandb.Histogram(param.grad.cpu().numpy()),
                            f"gradient_norms/{name}": param.grad.norm().item()
                        }, step=current_step)
            
        except Exception as e:
            logger.error(f"Failed to log gradients: {e}")
    
    def log_images(self, images: torch.Tensor, step: Optional[int] = None, 
                   title: str = "images", max_images: int = 16):
        """Log images to TensorBoard and wandb"""
        try:
            if not self.config.log_images:
                return
            
            current_step = step if step is not None else self.step
            
            # Limit number of images
            if images.shape[0] > max_images:
                images = images[:max_images]
            
            # Log to TensorBoard
            if self.tensorboard_writer:
                self.tensorboard_writer.add_images(title, images, current_step)
            
            # Log to wandb
            if self.wandb_run:
                wandb.log({title: [wandb.Image(img) for img in images]}, step=current_step)
            
        except Exception as e:
            logger.error(f"Failed to log images: {e}")
    
    def log_text(self, text: str, step: Optional[int] = None, title: str = "text"):
        """Log text to TensorBoard and wandb"""
        try:
            if not self.config.log_text:
                return
            
            current_step = step if step is not None else self.step
            
            # Log to TensorBoard
            if self.tensorboard_writer:
                self.tensorboard_writer.add_text(title, text, current_step)
            
            # Log to wandb
            if self.wandb_run:
                wandb.log({title: wandb.Html(text)}, step=current_step)
            
        except Exception as e:
            logger.error(f"Failed to log text: {e}")
    
    def log_model_checkpoint(self, model: nn.Module, optimizer: torch.optim.Optimizer = None,
                           epoch: int = None, step: int = None, metrics: Dict[str, float] = None):
        """Save model checkpoint"""
        try:
            current_epoch = epoch if epoch is not None else self.epoch
            current_step = step if step is not None else self.step
            
            # Create checkpoint
            checkpoint = {
                'epoch': current_epoch,
                'step': current_step,
                'model_state_dict': model.state_dict(),
                'config': self.config.__dict__,
                'metrics': metrics or {},
                'timestamp': datetime.now().isoformat()
            }
            
            if optimizer:
                checkpoint['optimizer_state_dict'] = optimizer.state_dict()
            
            # Save checkpoint
            checkpoint_path = Path(self.config.model_save_dir) / f"{self.config.experiment_name}_epoch_{current_epoch}_step_{current_step}.pt"
            torch.save(checkpoint, checkpoint_path)
            
            # Log to wandb
            if self.wandb_run:
                wandb.save(str(checkpoint_path))
            
            logger.info(f"Model checkpoint saved: {checkpoint_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model checkpoint: {e}")
    
    def log_system_metrics(self, gpu_memory: float = None, gpu_utilization: float = None,
                          cpu_usage: float = None, memory_usage: float = None):
        """Log system metrics"""
        try:
            system_metrics = {}
            
            if gpu_memory is not None:
                system_metrics['gpu_memory'] = gpu_memory
            if gpu_utilization is not None:
                system_metrics['gpu_utilization'] = gpu_utilization
            if cpu_usage is not None:
                system_metrics['cpu_usage'] = cpu_usage
            if memory_usage is not None:
                system_metrics['memory_usage'] = memory_usage
            
            if system_metrics:
                self.log_metrics(system_metrics, prefix="system")
                
        except Exception as e:
            logger.error(f"Failed to log system metrics: {e}")
    
    def log_training_step(self, loss: float, accuracy: float = None, 
                         learning_rate: float = None, step_time: float = None):
        """Log training step metrics"""
        try:
            training_metrics = {'loss': loss}
            
            if accuracy is not None:
                training_metrics['accuracy'] = accuracy
            if learning_rate is not None:
                training_metrics['learning_rate'] = learning_rate
            if step_time is not None:
                training_metrics['step_time'] = step_time
            
            self.log_metrics(training_metrics, prefix="train")
            self.step += 1
            
        except Exception as e:
            logger.error(f"Failed to log training step: {e}")
    
    def log_validation_step(self, loss: float, accuracy: float = None, 
                           precision: float = None, recall: float = None, f1: float = None):
        """Log validation step metrics"""
        try:
            validation_metrics = {'loss': loss}
            
            if accuracy is not None:
                validation_metrics['accuracy'] = accuracy
            if precision is not None:
                validation_metrics['precision'] = precision
            if recall is not None:
                validation_metrics['recall'] = recall
            if f1 is not None:
                validation_metrics['f1'] = f1
            
            self.log_metrics(validation_metrics, prefix="val")
            
        except Exception as e:
            logger.error(f"Failed to log validation step: {e}")
    
    def log_epoch(self, epoch: int, epoch_time: float = None):
        """Log epoch information"""
        try:
            self.epoch = epoch
            
            if epoch_time is not None:
                self.log_metrics({'epoch_time': epoch_time}, prefix="epoch")
            
            # Log to wandb
            if self.wandb_run:
                wandb.log({'epoch': epoch}, step=self.step)
            
        except Exception as e:
            logger.error(f"Failed to log epoch: {e}")
    
    def create_plots(self) -> Dict[str, plt.Figure]:
        """Create visualization plots from logged metrics"""
        try:
            plots = {}
            
            # Set style
            plt.style.use('seaborn-v0_8')
            
            # Training loss plot
            if self.metrics.train_loss:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(self.metrics.train_loss, label='Training Loss', color='blue')
                if self.metrics.val_loss:
                    ax.plot(self.metrics.val_loss, label='Validation Loss', color='red')
                ax.set_xlabel('Step')
                ax.set_ylabel('Loss')
                ax.set_title('Training and Validation Loss')
                ax.legend()
                ax.grid(True)
                plots['loss'] = fig
            
            # Accuracy plot
            if self.metrics.train_accuracy:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(self.metrics.train_accuracy, label='Training Accuracy', color='blue')
                if self.metrics.val_accuracy:
                    ax.plot(self.metrics.val_accuracy, label='Validation Accuracy', color='red')
                ax.set_xlabel('Step')
                ax.set_ylabel('Accuracy')
                ax.set_title('Training and Validation Accuracy')
                ax.legend()
                ax.grid(True)
                plots['accuracy'] = fig
            
            # Learning rate plot
            if self.metrics.learning_rate:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(self.metrics.learning_rate, color='green')
                ax.set_xlabel('Step')
                ax.set_ylabel('Learning Rate')
                ax.set_title('Learning Rate Schedule')
                ax.grid(True)
                plots['learning_rate'] = fig
            
            # System metrics plot
            if self.metrics.gpu_memory or self.metrics.cpu_usage:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                
                if self.metrics.gpu_memory:
                    ax1.plot(self.metrics.gpu_memory, label='GPU Memory', color='purple')
                if self.metrics.cpu_usage:
                    ax1.plot(self.metrics.cpu_usage, label='CPU Usage', color='orange')
                ax1.set_ylabel('Usage (%)')
                ax1.set_title('System Resource Usage')
                ax1.legend()
                ax1.grid(True)
                
                if self.metrics.gpu_utilization:
                    ax2.plot(self.metrics.gpu_utilization, label='GPU Utilization', color='red')
                if self.metrics.memory_usage:
                    ax2.plot(self.metrics.memory_usage, label='Memory Usage', color='brown')
                ax2.set_xlabel('Step')
                ax2.set_ylabel('Usage (%)')
                ax2.legend()
                ax2.grid(True)
                
                plots['system_metrics'] = fig
            
            return plots
            
        except Exception as e:
            logger.error(f"Failed to create plots: {e}")
            return {}
    
    def log_plots(self, plots: Dict[str, plt.Figure], step: Optional[int] = None):
        """Log plots to TensorBoard and wandb"""
        try:
            current_step = step if step is not None else self.step
            
            for name, fig in plots.items():
                # Log to TensorBoard
                if self.tensorboard_writer:
                    self.tensorboard_writer.add_figure(f"plots/{name}", fig, current_step)
                
                # Log to wandb
                if self.wandb_run:
                    wandb.log({f"plots/{name}": wandb.Image(fig)}, step=current_step)
                
                plt.close(fig)
            
        except Exception as e:
            logger.error(f"Failed to log plots: {e}")
    
    def get_experiment_summary(self) -> Dict[str, Any]:
        """Get experiment summary"""
        try:
            total_time = time.time() - self.start_time
            
            summary = {
                'experiment_name': self.config.experiment_name,
                'project_name': self.config.project_name,
                'total_time': total_time,
                'total_steps': self.step,
                'total_epochs': self.epoch,
                'tensorboard_enabled': self.config.enable_tensorboard,
                'wandb_enabled': self.config.enable_wandb and WANDB_AVAILABLE,
                'wandb_run_id': self.wandb_run.id if self.wandb_run else None,
                'wandb_run_url': self.wandb_run.url if self.wandb_run else None,
                'metrics_count': len(self.metrics.__dict__),
                'custom_metrics_count': len(self.metrics.custom_metrics)
            }
            
            # Add final metrics if available
            if self.metrics.train_loss:
                summary['final_train_loss'] = self.metrics.train_loss[-1]
            if self.metrics.val_loss:
                summary['final_val_loss'] = self.metrics.val_loss[-1]
            if self.metrics.train_accuracy:
                summary['final_train_accuracy'] = self.metrics.train_accuracy[-1]
            if self.metrics.val_accuracy:
                summary['final_val_accuracy'] = self.metrics.val_accuracy[-1]
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get experiment summary: {e}")
            return {}
    
    def finish(self):
        """Finish experiment tracking"""
        try:
            # Create and log final plots
            plots = self.create_plots()
            self.log_plots(plots)
            
            # Log experiment summary
            summary = self.get_experiment_summary()
            self.log_text(json.dumps(summary, indent=2), title="experiment_summary")
            
            # Close TensorBoard writer
            if self.tensorboard_writer:
                self.tensorboard_writer.close()
            
            # Finish wandb run
            if self.wandb_run:
                wandb.finish()
            
            logger.info(f"Experiment tracking finished: {self.config.experiment_name}")
            
        except Exception as e:
            logger.error(f"Failed to finish experiment tracking: {e}")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_experiment_config(experiment_name: str = None, **kwargs) -> ExperimentConfig:
    """Create experiment configuration with default values"""
    config = ExperimentConfig()
    
    if experiment_name:
        config.experiment_name = experiment_name
    
    # Update with provided kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config


def get_tensorboard_url(log_dir: str) -> str:
    """Get TensorBoard URL for the given log directory"""
    try:
        import socket
        hostname = socket.gethostname()
        port = 6006  # Default TensorBoard port
        return f"http://{hostname}:{port}"
    except Exception:
        return "http://localhost:6006"


def start_tensorboard_server(log_dir: str, port: int = 6006, host: str = "0.0.0.0"):
    """Start TensorBoard server"""
    try:
        import subprocess
        import threading
        
        def run_tensorboard():
            cmd = [
                "tensorboard",
                "--logdir", log_dir,
                "--port", str(port),
                "--host", host,
                "--reload_multifile", "true"
            ]
            subprocess.run(cmd)
        
        # Start TensorBoard in a separate thread
        thread = threading.Thread(target=run_tensorboard, daemon=True)
        thread.start()
        
        logger.info(f"TensorBoard server started on {host}:{port}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start TensorBoard server: {e}")
        return False


def compare_experiments(experiment_names: List[str], metric: str = "val_loss") -> plt.Figure:
    """Compare multiple experiments"""
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for exp_name in experiment_names:
            # Load metrics from file (simplified - in practice, you'd load from actual logs)
            # This is a placeholder for demonstration
            steps = list(range(100))
            values = [0.1 * np.exp(-i/50) + 0.01 * np.random.random() for i in steps]
            ax.plot(steps, values, label=exp_name, alpha=0.7)
        
        ax.set_xlabel('Step')
        ax.set_ylabel(metric.replace('_', ' ').title())
        ax.set_title(f'Experiment Comparison: {metric}')
        ax.legend()
        ax.grid(True)
        
        return fig
        
    except Exception as e:
        logger.error(f"Failed to compare experiments: {e}")
        return None


# =============================================================================
# DECORATORS AND CONTEXT MANAGERS
# =============================================================================

def track_experiment(config: ExperimentConfig = None):
    """Decorator to track experiment"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = ExperimentTracker(config)
            
            try:
                # Log function call
                tracker.log_text(f"Function called: {func.__name__}", title="function_call")
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log result
                tracker.log_text(f"Function completed: {func.__name__}", title="function_completion")
                
                return result
                
            finally:
                tracker.finish()
        
        return wrapper
    return decorator


class experiment_context:
    """Context manager for experiment tracking"""
    
    def __init__(self, config: ExperimentConfig = None):
        self.config = config
        self.tracker = None
    
    def __enter__(self):
        self.tracker = ExperimentTracker(self.config)
        return self.tracker
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tracker:
            self.tracker.finish()


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_training_with_tracking():
    """Example of training with experiment tracking"""
    
    # Create experiment configuration
    config = create_experiment_config(
        experiment_name="example_training",
        project_name="gradio_demo",
        enable_tensorboard=True,
        enable_wandb=True,
        log_interval=10,
        save_interval=100
    )
    
    # Use context manager for experiment tracking
    with experiment_context(config) as tracker:
        
        # Log hyperparameters
        hyperparams = {
            'learning_rate': 0.001,
            'batch_size': 32,
            'num_epochs': 10,
            'model_type': 'linear'
        }
        tracker.log_hyperparameters(hyperparams)
        
        # Create model
        model = nn.Linear(10, 2)
        tracker.log_model_architecture(model, input_shape=(10,))
        
        # Simulate training
        for epoch in range(10):
            tracker.log_epoch(epoch)
            
            for step in range(100):
                # Simulate training step
                loss = 0.1 * np.exp(-step/50) + 0.01 * np.random.random()
                accuracy = 0.8 + 0.2 * np.exp(-step/50) + 0.05 * np.random.random()
                
                tracker.log_training_step(
                    loss=loss,
                    accuracy=accuracy,
                    learning_rate=0.001,
                    step_time=0.01
                )
                
                # Log system metrics occasionally
                if step % 20 == 0:
                    tracker.log_system_metrics(
                        gpu_memory=50.0 + np.random.random() * 10,
                        gpu_utilization=60.0 + np.random.random() * 20,
                        cpu_usage=30.0 + np.random.random() * 15,
                        memory_usage=40.0 + np.random.random() * 10
                    )
                
                # Log gradients occasionally
                if step % 50 == 0:
                    tracker.log_gradients(model)
            
            # Simulate validation
            val_loss = 0.08 * np.exp(-epoch/5) + 0.02 * np.random.random()
            val_accuracy = 0.85 + 0.15 * np.exp(-epoch/5) + 0.03 * np.random.random()
            
            tracker.log_validation_step(
                loss=val_loss,
                accuracy=val_accuracy,
                precision=0.82 + np.random.random() * 0.1,
                recall=0.80 + np.random.random() * 0.1,
                f1=0.81 + np.random.random() * 0.1
            )
            
            # Save checkpoint
            tracker.log_model_checkpoint(model, epoch=epoch)
        
        # Get summary
        summary = tracker.get_experiment_summary()
        print("Experiment Summary:", json.dumps(summary, indent=2))


if __name__ == "__main__":
    # Run example
    example_training_with_tracking() 