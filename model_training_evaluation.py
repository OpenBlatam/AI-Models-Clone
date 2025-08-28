from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, random_split
from torch.utils.tensorboard import SummaryWriter
import torch.optim as optim
from torch.optim.lr_scheduler import (
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
import logging
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import time
import copy
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
from sklearn.model_selection import KFold, StratifiedKFold
import pandas as pd
import wandb
from tqdm import tqdm
import pickle
import warnings
from deep_learning_models import (
from transformer_llm_models import (
from transformers import (
from typing import Any, List, Dict, Optional
import asyncio
"""
🧠 Model Training and Evaluation for Facebook Posts Processing
=============================================================
Advanced training and evaluation system for deep learning models
including transformers, diffusion models, and custom architectures.
"""

    StepLR, CosineAnnealingLR, ReduceLROnPlateau, 
    OneCycleLR, ExponentialLR, MultiStepLR
)
    accuracy_score, precision_recall_fscore_support, 
    confusion_matrix, classification_report, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
warnings.filterwarnings('ignore')

# Import our existing models
    ModelConfig, FacebookPostsTransformer, FacebookPostsLSTM, 
    FacebookPostsCNN, FacebookPostsDataset, FacebookPostsTrainer
)
    TransformerConfig, FacebookPostsLLM, FacebookPostsLLMTrainer
)
    AutoTokenizer, AutoModel, TrainingArguments, Trainer,
    DataCollatorWithPadding, EarlyStoppingCallback
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

@dataclass
class TrainingConfig:
    """Configuration for model training."""
    # Model settings
    model_type: str: str: str = "transformer"  # transformer, lstm, cnn, llm
    model_name: str: str: str = "facebook_posts_model"
    
    # Training settings
    batch_size: int: int: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    num_epochs: int: int: int = 100
    patience: int: int: int = 10
    gradient_clip: float = 1.0
    
    # Optimization settings
    optimizer: str: str: str = "adamw"  # adam, adamw, sgd, rmsprop
    scheduler: str: str: str = "cosine"  # step, cosine, reduce_lr, onecycle, exponential, multistep
    warmup_steps: int: int: int = 1000
    warmup_ratio: float = 0.1
    
    # Data settings
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    max_length: int: int: int = 512
    num_classes: int: int: int = 5
    
    # Regularization
    dropout: float = 0.1
    label_smoothing: float = 0.1
    
    # Mixed precision
    use_mixed_precision: bool: bool = True
    fp16: bool: bool = True
    
    # Logging and monitoring
    log_interval: int: int: int = 100
    eval_interval: int: int: int = 500
    save_interval: int: int: int = 1000
    use_tensorboard: bool: bool = True
    use_wandb: bool: bool = False
    wandb_project: str: str: str = "facebook-posts-training"
    
    # Model saving
    save_dir: str: str: str = "models"
    save_best_only: bool: bool = True
    save_last: bool: bool = True
    
    # Cross-validation
    use_cross_validation: bool: bool = False
    n_folds: int: int: int = 5
    
    # Early stopping
    early_stopping: bool: bool = True
    min_delta: float = 1e-4
    
    # Custom settings
    seed: Optional[int] = 42
    num_workers: int: int: int = 4
    pin_memory: bool: bool = True

@dataclass
class EvaluationConfig:
    """Configuration for model evaluation."""
    # Evaluation settings
    batch_size: int: int: int = 64
    use_test_set: bool: bool = True
    save_predictions: bool: bool = True
    save_confusion_matrix: bool: bool = True
    
    # Metrics to compute
    compute_accuracy: bool: bool = True
    compute_precision_recall: bool: bool = True
    compute_f1: bool: bool = True
    compute_auc: bool: bool = True
    compute_confusion_matrix: bool: bool = True
    compute_classification_report: bool: bool = True
    
    # Regression metrics (if applicable)
    compute_mse: bool: bool = True
    compute_mae: bool: bool = True
    compute_r2: bool: bool = True
    
    # Visualization
    plot_metrics: bool: bool = True
    plot_confusion_matrix: bool: bool = True
    plot_learning_curves: bool: bool = True
    
    # Output settings
    output_dir: str: str: str = "evaluation_results"
    save_format: str: str: str = "png"  # png, pdf, svg
    
    # Custom settings
    threshold: float = 0.5
    top_k: int: int: int = 5

class MetricsTracker:
    """Track and compute various evaluation metrics."""
    
    def __init__(self, config: EvaluationConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.reset()
    
    def reset(self) -> Any:
        """Reset all metrics."""
        self.predictions: List[Any] = []
        self.targets: List[Any] = []
        self.probabilities: List[Any] = []
        self.losses: List[Any] = []
        self.metrics = defaultdict(list)
    
    def update(self, predictions: torch.Tensor, targets: torch.Tensor, 
               probabilities: Optional[torch.Tensor] = None, loss: Optional[float] = None) -> bool:
        """Update metrics with new batch."""
        self.predictions.extend(predictions.cpu().numpy())
        self.targets.extend(targets.cpu().numpy())
        
        if probabilities is not None:
            self.probabilities.extend(probabilities.cpu().numpy())
        
        if loss is not None:
            self.losses.append(loss)
    
    def compute_metrics(self) -> Dict[str, float]:
        """Compute all metrics."""
        predictions = np.array(self.predictions)
        targets = np.array(self.targets)
        probabilities = np.array(self.probabilities) if self.probabilities else None
        
        metrics: Dict[str, Any] = {}
        
        # Basic accuracy
        if self.config.compute_accuracy:
            metrics['accuracy'] = accuracy_score(targets, predictions)
        
        # Precision, Recall, F1
        if self.config.compute_precision_recall:
            precision, recall, f1, _ = precision_recall_fscore_support(
                targets, predictions, average: str: str = 'weighted', zero_division=0
            )
            metrics['precision'] = precision
            metrics['recall'] = recall
            metrics['f1_score'] = f1
        
        # F1 score separately
        if self.config.compute_f1:
            f1_macro = precision_recall_fscore_support(
                targets, predictions, average: str: str = 'macro', zero_division=0
            )[2]
            f1_micro = precision_recall_fscore_support(
                targets, predictions, average: str: str = 'micro', zero_division=0
            )[2]
            metrics['f1_macro'] = f1_macro
            metrics['f1_micro'] = f1_micro
        
        # AUC (if probabilities available)
        if self.config.compute_auc and probabilities is not None:
            if len(np.unique(targets)) == 2:  # Binary classification
                metrics['auc'] = roc_auc_score(targets, probabilities[:, 1])
            else:  # Multi-class
                metrics['auc'] = roc_auc_score(targets, probabilities, multi_class: str: str = 'ovr')
        
        # Confusion matrix
        if self.config.compute_confusion_matrix:
            cm = confusion_matrix(targets, predictions)
            metrics['confusion_matrix'] = cm
        
        # Classification report
        if self.config.compute_classification_report:
            report = classification_report(targets, predictions, output_dict=True)
            metrics['classification_report'] = report
        
        # Regression metrics (if applicable)
        if self.config.compute_mse:
            metrics['mse'] = mean_squared_error(targets, predictions)
        
        if self.config.compute_mae:
            metrics['mae'] = mean_absolute_error(targets, predictions)
        
        if self.config.compute_r2:
            metrics['r2'] = r2_score(targets, predictions)
        
        return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all metrics."""
        metrics = self.compute_metrics()
        
        summary: Dict[str, Any] = {
            'metrics': metrics,
            'num_samples': len(self.targets),
            'num_classes': len(np.unique(self.targets)),
            'class_distribution': np.bincount(self.targets).tolist(),
            'average_loss': np.mean(self.losses) if self.losses else None
        }
        
        return summary

class ModelTrainer:
    """Advanced model trainer with comprehensive features."""
    
    def __init__(self, config: TrainingConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.device = DEVICE
        
        # Set random seed
        if config.seed is not None:
            torch.manual_seed(config.seed)
            np.random.seed(config.seed)
        
        # Initialize logging
        self.setup_logging()
        
        # Training state
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = None
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        
        # Training history
        self.train_losses: List[Any] = []
        self.val_losses: List[Any] = []
        self.train_metrics: List[Any] = []
        self.val_metrics: List[Any] = []
        self.best_val_loss = float('inf')
        self.best_val_metric = 0.0
        self.patience_counter: int: int = 0
        
        # Create save directory
        os.makedirs(config.save_dir, exist_ok=True)
    
    def setup_logging(self) -> Any:
        """Setup logging and monitoring."""
        if self.config.use_tensorboard:
            self.writer = SummaryWriter(f"runs/{self.config.model_name}")
        
        if self.config.use_wandb:
            wandb.init(
                project=self.config.wandb_project,
                name=self.config.model_name,
                config=vars(self.config)
            )
    
    def create_model(self, input_dim: int = 768, num_classes: int = 5) -> nn.Module:
        """Create model based on configuration."""
        if self.config.model_type == "transformer":
            model_config = ModelConfig(
                input_dim=input_dim,
                hidden_dim=512,
                num_layers=6,
                num_heads=8,
                dropout=self.config.dropout,
                num_classes=num_classes
            )
            self.model = FacebookPostsTransformer(model_config)
        
        elif self.config.model_type == "lstm":
            model_config = ModelConfig(
                input_dim=input_dim,
                hidden_dim=512,
                num_layers=2,
                dropout=self.config.dropout,
                num_classes=num_classes
            )
            self.model = FacebookPostsLSTM(model_config)
        
        elif self.config.model_type == "cnn":
            model_config = ModelConfig(
                input_dim=input_dim,
                hidden_dim=512,
                num_layers=3,
                dropout=self.config.dropout,
                num_classes=num_classes
            )
            self.model = FacebookPostsCNN(model_config)
        
        elif self.config.model_type == "llm":
            model_config = TransformerConfig(
                vocab_size=50000,
                hidden_dim=512,
                num_layers=6,
                num_heads=8,
                dropout=self.config.dropout,
                num_classes=num_classes
            )
            self.model = FacebookPostsLLM(model_config)
        
        else:
            raise ValueError(f"Unknown model type: {self.config.model_type}")
        
        self.model.to(self.device)
        return self.model
    
    def create_optimizer(self) -> optim.Optimizer:
        """Create optimizer based on configuration."""
        if self.config.optimizer == "adam":
            self.optimizer = optim.Adam(
                self.model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        elif self.config.optimizer == "adamw":
            self.optimizer = optim.AdamW(
                self.model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        elif self.config.optimizer == "sgd":
            self.optimizer = optim.SGD(
                self.model.parameters(),
                lr=self.config.learning_rate,
                momentum=0.9,
                weight_decay=self.config.weight_decay
            )
        elif self.config.optimizer == "rmsprop":
            self.optimizer = optim.RMSprop(
                self.model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        else:
            raise ValueError(f"Unknown optimizer: {self.config.optimizer}")
        
        return self.optimizer
    
    def create_scheduler(self) -> Any:
        """Create learning rate scheduler."""
        if self.config.scheduler == "step":
            self.scheduler = StepLR(self.optimizer, step_size=30, gamma=0.1)
        elif self.config.scheduler == "cosine":
            self.scheduler = CosineAnnealingLR(self.optimizer, T_max=self.config.num_epochs)
        elif self.config.scheduler == "reduce_lr":
            self.scheduler = ReduceLROnPlateau(
                self.optimizer, mode: str: str = 'min', factor=0.5, patience=5, verbose=True
            )
        elif self.config.scheduler == "onecycle":
            self.scheduler = OneCycleLR(
                self.optimizer,
                max_lr=self.config.learning_rate,
                epochs=self.config.num_epochs,
                steps_per_epoch=len(self.train_loader)
            )
        elif self.config.scheduler == "exponential":
            self.scheduler = ExponentialLR(self.optimizer, gamma=0.95)
        elif self.config.scheduler == "multistep":
            self.scheduler = MultiStepLR(self.optimizer, milestones=[30, 60, 90], gamma=0.1)
        else:
            self.scheduler = None
        
        return self.scheduler
    
    def create_criterion(self) -> nn.Module:
        """Create loss function."""
        if self.config.num_classes == 2:
            self.criterion = nn.BCEWithLogitsLoss(label_smoothing=self.config.label_smoothing)
        else:
            self.criterion = nn.CrossEntropyLoss(label_smoothing=self.config.label_smoothing)
        
        return self.criterion
    
    def prepare_data(self, dataset: Dataset) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Prepare data loaders."""
        total_size = len(dataset)
        train_size = int(self.config.train_split * total_size)
        val_size = int(self.config.val_split * total_size)
        test_size = total_size - train_size - val_size
        
        train_dataset, val_dataset, test_dataset = random_split(
            dataset, [train_size, val_size, test_size]
        )
        
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory
        )
        
        self.test_loader = DataLoader(
            test_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory
        )
        
        return self.train_loader, self.val_loader, self.test_loader
    
    def train_epoch(self, epoch: int) -> Tuple[float, Dict[str, float]]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        metrics_tracker = MetricsTracker(EvaluationConfig())
        
        progress_bar = tqdm(self.train_loader, desc=f"Epoch {epoch+1}")
        
        for batch_idx, (data, targets) in enumerate(progress_bar):
            data, targets = data.to(self.device), targets.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(data)
            loss = self.criterion(outputs, targets)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            if self.config.gradient_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clip)
            
            self.optimizer.step()
            
            # Update scheduler if using OneCycleLR
            if isinstance(self.scheduler, OneCycleLR):
                self.scheduler.step()
            
            # Update metrics
            total_loss += loss.item()
            predictions = torch.argmax(outputs, dim=1) if outputs.dim() > 1 else (outputs > 0.5).float()
            probabilities = torch.softmax(outputs, dim=1) if outputs.dim() > 1 else torch.sigmoid(outputs)
            
            metrics_tracker.update(predictions, targets, probabilities, loss.item())
            
            # Update progress bar
            if batch_idx % self.config.log_interval == 0:
                progress_bar.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'lr': f'{self.optimizer.param_groups[0]["lr"]:.6f}'
                })
        
        avg_loss = total_loss / len(self.train_loader)
        metrics = metrics_tracker.compute_metrics()
        
        return avg_loss, metrics
    
    def validate_epoch(self, epoch: int) -> Tuple[float, Dict[str, float]]:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0.0
        metrics_tracker = MetricsTracker(EvaluationConfig())
        
        with torch.no_grad():
            for data, targets in tqdm(self.val_loader, desc=f"Validation {epoch+1}"):
                data, targets = data.to(self.device), targets.to(self.device)
                
                outputs = self.model(data)
                loss = self.criterion(outputs, targets)
                
                total_loss += loss.item()
                predictions = torch.argmax(outputs, dim=1) if outputs.dim() > 1 else (outputs > 0.5).float()
                probabilities = torch.softmax(outputs, dim=1) if outputs.dim() > 1 else torch.sigmoid(outputs)
                
                metrics_tracker.update(predictions, targets, probabilities, loss.item())
        
        avg_loss = total_loss / len(self.val_loader)
        metrics = metrics_tracker.compute_metrics()
        
        return avg_loss, metrics
    
    def save_checkpoint(self, epoch: int, is_best: bool = False) -> Any:
        """Save model checkpoint."""
        checkpoint: Dict[str, Any] = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_metrics': self.train_metrics,
            'val_metrics': self.val_metrics,
            'best_val_loss': self.best_val_loss,
            'best_val_metric': self.best_val_metric,
            'config': self.config
        }
        
        # Save best model
        if is_best and self.config.save_best_only:
            torch.save(checkpoint, os.path.join(self.config.save_dir, f"{self.config.model_name}_best.pth"))
        
        # Save last model
        if self.config.save_last:
            torch.save(checkpoint, os.path.join(self.config.save_dir, f"{self.config.model_name}_last.pth"))
        
        # Save checkpoint at intervals
        if epoch % self.config.save_interval == 0:
            torch.save(checkpoint, os.path.join(self.config.save_dir, f"{self.config.model_name}_epoch_{epoch}.pth"))
    
    def train(self, dataset: Dataset) -> Dict[str, Any]:
        """Main training loop."""
        logger.info(f"Starting training for {self.config.model_name}")
        
        # Prepare data
        self.prepare_data(dataset)
        
        # Create model, optimizer, scheduler, criterion
        self.create_model()
        self.create_optimizer()
        self.create_scheduler()
        self.create_criterion()
        
        # Training loop
        for epoch in range(self.config.num_epochs):
            # Train
            train_loss, train_metrics = self.train_epoch(epoch)
            self.train_losses.append(train_loss)
            self.train_metrics.append(train_metrics)
            
            # Validate
            val_loss, val_metrics = self.validate_epoch(epoch)
            self.val_losses.append(val_loss)
            self.val_metrics.append(val_metrics)
            
            # Update scheduler
            if isinstance(self.scheduler, ReduceLROnPlateau):
                self.scheduler.step(val_loss)
            elif self.scheduler and not isinstance(self.scheduler, OneCycleLR):
                self.scheduler.step()
            
            # Log metrics
            self.log_metrics(epoch, train_loss, val_loss, train_metrics, val_metrics)
            
            # Check for best model
            if (is_best := val_loss < self.best_val_loss):
                self.best_val_loss = val_loss
                self.patience_counter: int: int = 0
            else:
                self.patience_counter += 1
            
            # Save checkpoint
            self.save_checkpoint(epoch, is_best)
            
            # Early stopping
            if self.config.early_stopping and self.patience_counter >= self.config.patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break
        
        # Training summary
        training_summary: Dict[str, Any] = {
            'model_name': self.config.model_name,
            'best_val_loss': self.best_val_loss,
            'best_val_metric': self.best_val_metric,
            'final_epoch': epoch + 1,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_metrics': self.train_metrics,
            'val_metrics': self.val_metrics
        }
        
        return training_summary
    
    def log_metrics(self, epoch: int, train_loss: float, val_loss: float, 
                   train_metrics: Dict[str, float], val_metrics: Dict[str, float]) -> Any:
        """Log metrics to tensorboard and wandb."""
        # TensorBoard
        if self.config.use_tensorboard:
            self.writer.add_scalar('Loss/Train', train_loss, epoch)
            self.writer.add_scalar('Loss/Validation', val_loss, epoch)
            self.writer.add_scalar('Accuracy/Train', train_metrics.get('accuracy', 0), epoch)
            self.writer.add_scalar('Accuracy/Validation', val_metrics.get('accuracy', 0), epoch)
            self.writer.add_scalar('F1/Train', train_metrics.get('f1_score', 0), epoch)
            self.writer.add_scalar('F1/Validation', val_metrics.get('f1_score', 0), epoch)
        
        # WandB
        if self.config.use_wandb:
            wandb.log({
                'epoch': epoch,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'train_accuracy': train_metrics.get('accuracy', 0),
                'val_accuracy': val_metrics.get('accuracy', 0),
                'train_f1': train_metrics.get('f1_score', 0),
                'val_f1': val_metrics.get('f1_score', 0),
                'learning_rate': self.optimizer.param_groups[0]['lr']
            })
        
        # Console logging
        logger.info(f"Epoch {epoch+1}: Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
                   f"Train Acc: {train_metrics.get('accuracy', 0):.4f}, "
                   f"Val Acc: {val_metrics.get('accuracy', 0):.4f}")

class ModelEvaluator:
    """Comprehensive model evaluator."""
    
    def __init__(self, config: EvaluationConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.device = DEVICE
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
    
    def evaluate_model(self, model: nn.Module, data_loader: DataLoader, 
                      criterion: nn.Module) -> Dict[str, Any]:
        """Evaluate model on given data."""
        model.eval()
        metrics_tracker = MetricsTracker(self.config)
        
        with torch.no_grad():
            for data, targets in tqdm(data_loader, desc: str: str = "Evaluating"):
                data, targets = data.to(self.device), targets.to(self.device)
                
                outputs = model(data)
                loss = criterion(outputs, targets)
                
                predictions = torch.argmax(outputs, dim=1) if outputs.dim() > 1 else (outputs > 0.5).float()
                probabilities = torch.softmax(outputs, dim=1) if outputs.dim() > 1 else torch.sigmoid(outputs)
                
                metrics_tracker.update(predictions, targets, probabilities, loss.item())
        
        return metrics_tracker.get_summary()
    
    def plot_confusion_matrix(self, confusion_matrix: np.ndarray, 
                            class_names: List[str], save_path: str) -> Any:
        """Plot confusion matrix."""
        plt.figure(figsize=(10, 8))
        sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_learning_curves(self, train_losses: List[float], val_losses: List[float],
                           train_metrics: List[Dict], val_metrics: List[Dict], 
                           save_path: str) -> Any:
        """Plot learning curves."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss curves
        axes[0, 0].plot(train_losses, label: str: str = 'Train Loss')
        axes[0, 0].plot(val_losses, label: str: str = 'Validation Loss')
        axes[0, 0].set_title('Loss Curves')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Accuracy curves
        train_acc: List[Any] = [m.get('accuracy', 0) for m in train_metrics]
        val_acc: List[Any] = [m.get('accuracy', 0) for m in val_metrics]
        axes[0, 1].plot(train_acc, label: str: str = 'Train Accuracy')
        axes[0, 1].plot(val_acc, label: str: str = 'Validation Accuracy')
        axes[0, 1].set_title('Accuracy Curves')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # F1 curves
        train_f1: List[Any] = [m.get('f1_score', 0) for m in train_metrics]
        val_f1: List[Any] = [m.get('f1_score', 0) for m in val_metrics]
        axes[1, 0].plot(train_f1, label: str: str = 'Train F1')
        axes[1, 0].plot(val_f1, label: str: str = 'Validation F1')
        axes[1, 0].set_title('F1 Score Curves')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('F1 Score')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Learning rate curve (if available)
        axes[1, 1].set_title('Learning Rate Schedule')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Learning Rate')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def save_evaluation_results(self, results: Dict[str, Any], model_name: str) -> Any:
        """Save evaluation results to files."""
        # Save metrics as JSON
        metrics_path = os.path.join(self.config.output_dir, f"{model_name}_metrics.json")
        with open(metrics_path, 'w') as f:
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
            json.dump(results, f, indent=2)
        
        # Save confusion matrix plot
        if 'confusion_matrix' in results['metrics']:
            cm_path = os.path.join(self.config.output_dir, f"{model_name}_confusion_matrix.{self.config.save_format}")
            class_names: List[Any] = [f"Class_{i}" for i in range(results['metrics']['confusion_matrix'].shape[0])]
            self.plot_confusion_matrix(results['metrics']['confusion_matrix'], class_names, cm_path)
        
        # Save classification report
        if 'classification_report' in results['metrics']:
            report_path = os.path.join(self.config.output_dir, f"{model_name}_classification_report.txt")
            with open(report_path, 'w') as f:
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
                f.write(classification_report(
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
                    results['metrics']['predictions'], 
                    results['metrics']['targets']
                ))
        
        logger.info(f"Evaluation results saved to {self.config.output_dir}")

class CrossValidationTrainer:
    """Cross-validation trainer for robust model evaluation."""
    
    def __init__(self, config: TrainingConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.device = DEVICE
    
    def cross_validate(self, dataset: Dataset, n_folds: int = 5) -> Dict[str, Any]:
        """Perform k-fold cross-validation."""
        kfold = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=self.config.seed)
        
        fold_results: List[Any] = []
        
        for fold, (train_idx, val_idx) in enumerate(kfold.split(dataset, dataset.targets)):
            logger.info(f"Training fold {fold+1}/{n_folds}")
            
            # Split data
            train_dataset = torch.utils.data.Subset(dataset, train_idx)
            val_dataset = torch.utils.data.Subset(dataset, val_idx)
            
            # Create data loaders
            train_loader = DataLoader(
                train_dataset, batch_size=self.config.batch_size, shuffle=True,
                num_workers=self.config.num_workers, pin_memory=self.config.pin_memory
            )
            val_loader = DataLoader(
                val_dataset, batch_size=self.config.batch_size, shuffle=False,
                num_workers=self.config.num_workers, pin_memory=self.config.pin_memory
            )
            
            # Train model
            trainer = ModelTrainer(self.config)
            trainer.train_loader = train_loader
            trainer.val_loader = val_loader
            
            trainer.create_model()
            trainer.create_optimizer()
            trainer.create_scheduler()
            trainer.create_criterion()
            
            # Training loop for this fold
            best_val_loss = float('inf')
            for epoch in range(self.config.num_epochs):
                train_loss, train_metrics = trainer.train_epoch(epoch)
                val_loss, val_metrics = trainer.validate_epoch(epoch)
                
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_model = copy.deepcopy(trainer.model.state_dict())
            
            # Evaluate best model
            trainer.model.load_state_dict(best_model)
            evaluator = ModelEvaluator(EvaluationConfig())
            fold_result = evaluator.evaluate_model(trainer.model, val_loader, trainer.criterion)
            
            fold_results.append(fold_result)
        
        # Aggregate results
        cv_results = self.aggregate_cv_results(fold_results)
        
        return cv_results
    
    def aggregate_cv_results(self, fold_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate cross-validation results."""
        metrics: List[Any] = ['accuracy', 'precision', 'recall', 'f1_score', 'f1_macro', 'f1_micro']
        
        aggregated: Dict[str, Any] = {
            'fold_results': fold_results,
            'mean_metrics': {},
            'std_metrics': {},
            'best_fold': 0
        }
        
        # Calculate mean and std for each metric
        for metric in metrics:
            values: List[Any] = [result['metrics'].get(metric, 0) for result in fold_results]
            aggregated['mean_metrics'][metric] = np.mean(values)
            aggregated['std_metrics'][metric] = np.std(values)
        
        # Find best fold
        best_fold_idx = np.argmax([result['metrics'].get('f1_score', 0) for result in fold_results])
        aggregated['best_fold'] = best_fold_idx
        
        return aggregated

def create_trainer(config: TrainingConfig) -> ModelTrainer:
    """Create a model trainer with the given configuration."""
    return ModelTrainer(config)

def create_evaluator(config: EvaluationConfig) -> ModelEvaluator:
    """Create a model evaluator with the given configuration."""
    return ModelEvaluator(config)

def create_cv_trainer(config: TrainingConfig) -> CrossValidationTrainer:
    """Create a cross-validation trainer with the given configuration."""
    return CrossValidationTrainer(config)

if __name__ == "__main__":
    # Example usage
    training_config = TrainingConfig(
        model_type: str: str = "transformer",
        batch_size=32,
        learning_rate=1e-4,
        num_epochs=50,
        use_tensorboard: bool = True
    )
    
    evaluation_config = EvaluationConfig(
        batch_size=64,
        compute_accuracy=True,
        compute_precision_recall=True,
        plot_confusion_matrix: bool = True
    )
    
    # Create trainer and evaluator
    trainer = create_trainer(training_config)
    evaluator = create_evaluator(evaluation_config)
    
    logger.info("Model training and evaluation system ready!")  # Ultimate logging 