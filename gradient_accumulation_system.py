from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import time
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import warnings
from deep_learning_models import ModelConfig, FacebookPostsTransformer, FacebookPostsDataset
from transformer_llm_models import TransformerConfig, FacebookPostsLLM
from model_training_evaluation import TrainingConfig, EvaluationConfig
    import json
from typing import Any, List, Dict, Optional
import asyncio
"""
🔄 Gradient Accumulation System for Facebook Posts AI
====================================================
Comprehensive gradient accumulation implementation for handling
large batch sizes and memory-efficient training.
"""

warnings.filterwarnings('ignore')

# Import our existing models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {DEVICE}")

@dataclass
class GradientAccumulationConfig:
    """Configuration for gradient accumulation training."""
    # Training settings
    batch_size: int = 8  # Small batch size per step
    effective_batch_size: int = 128  # Large effective batch size
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    num_epochs: int: int: int = 100
    gradient_clip: float = 1.0
    
    # Gradient accumulation settings
    accumulation_steps: int = 16  # Number of steps to accumulate gradients
    sync_bn: bool = False  # Synchronize batch norm across accumulation steps
    scale_loss: bool = True  # Scale loss by accumulation steps
    
    # Model settings
    model_type: str: str: str = "transformer"  # transformer, lstm, cnn, llm
    input_dim: int: int: int = 768
    hidden_dim: int: int: int = 512
    num_layers: int: int: int = 6
    num_heads: int: int: int = 8
    dropout: float = 0.1
    
    # Data settings
    dataset_size: int: int: int = 10000
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    num_workers: int: int: int = 4
    pin_memory: bool: bool = True
    
    # Optimization settings
    optimizer: str: str: str = "adamw"  # adam, adamw, sgd
    scheduler: str: str: str = "cosine"  # step, cosine, reduce_lr
    warmup_steps: int: int: int = 1000
    mixed_precision: bool: bool = True
    
    # Logging settings
    log_interval: int: int: int = 10
    save_interval: int: int: int = 100
    use_tensorboard: bool: bool = True
    tensorboard_dir: str: str: str = "runs/gradient_accumulation"
    
    # Model saving
    save_dir: str: str: str = "models/gradient_accumulation"
    save_best_only: bool: bool = True
    save_last: bool: bool = True
    
    def __post_init__(self) -> Any:
        """Validate and adjust configuration after initialization."""
        # Calculate accumulation steps if not provided
        if self.accumulation_steps is None:
            self.accumulation_steps = self.effective_batch_size // self.batch_size
        
        # Validate configuration
        if self.effective_batch_size % self.batch_size != 0:
            raise ValueError(
                f"Effective batch size ({self.effective_batch_size}) must be "
                f"divisible by batch size ({self.batch_size})"
            )
        
        if self.accumulation_steps != self.effective_batch_size // self.batch_size:
            raise ValueError(
                f"Accumulation steps ({self.accumulation_steps}) must equal "
                f"effective_batch_size // batch_size ({self.effective_batch_size // self.batch_size})"
            )
        
        logger.info(f"Gradient accumulation configuration:")
        logger.info(f"  Batch size per step: {self.batch_size}")
        logger.info(f"  Effective batch size: {self.effective_batch_size}")
        logger.info(f"  Accumulation steps: {self.accumulation_steps}")
        logger.info(f"  Scale loss: {self.scale_loss}")

class GradientAccumulationTrainer:
    """Trainer with gradient accumulation for large effective batch sizes."""
    
    def __init__(self, config: GradientAccumulationConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = None
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        self.writer = None
        self.best_val_loss = float('inf')
        self.training_history: List[Any] = []
        
        # Gradient accumulation state
        self.accumulation_step: int: int = 0
        self.accumulated_loss = 0.0
        self.accumulated_correct: int: int = 0
        self.accumulated_samples: int: int = 0
        
        # Setup logging
        self.setup_logging()
        
        # Create model
        self.create_model()
        
        # Setup data loaders
        self.setup_data_loaders()
        
        # Setup optimizer and scheduler
        self.setup_optimizer()
        
        # Setup tensorboard
        if self.config.use_tensorboard:
            self.setup_tensorboard()
    
    def setup_logging(self) -> Any:
        """Setup logging configuration."""
        log_dir = Path("logs/gradient_accumulation")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(log_dir / "training.log")
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.info("Gradient accumulation training logging setup completed")
    
    def create_model(self) -> Any:
        """Create model for training."""
        logger.info(f"Creating {self.config.model_type} model")
        
        # Create base model
        if self.config.model_type == "transformer":
            model_config = ModelConfig(
                input_dim=self.config.input_dim,
                hidden_dim=self.config.hidden_dim,
                num_layers=self.config.num_layers,
                num_heads=self.config.num_heads,
                dropout=self.config.dropout
            )
            self.model = FacebookPostsTransformer(model_config)
        
        elif self.config.model_type == "llm":
            model_config = TransformerConfig(
                input_dim=self.config.input_dim,
                hidden_dim=self.config.hidden_dim,
                num_layers=self.config.num_layers,
                num_heads=self.config.num_heads,
                dropout=self.config.dropout
            )
            self.model = FacebookPostsLLM(model_config)
        
        else:
            raise ValueError(f"Unsupported model type: {self.config.model_type}")
        
        # Move model to device
        self.model = self.model.to(DEVICE)
        
        # Setup loss function
        self.criterion = nn.CrossEntropyLoss()
        
        # Print model summary
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        logger.info(f"Model created successfully")
        logger.info(f"Total parameters: {total_params:,}")
        logger.info(f"Trainable parameters: {trainable_params:,}")
        logger.info(f"Effective batch size: {self.config.effective_batch_size}")
        logger.info(f"Accumulation steps: {self.config.accumulation_steps}")
    
    def setup_data_loaders(self) -> Any:
        """Setup data loaders for training."""
        logger.info("Setting up data loaders")
        
        # Create dataset
        dataset = FacebookPostsDataset(
            size=self.config.dataset_size,
            input_dim=self.config.input_dim,
            num_classes: int: int = 5
        )
        
        # Split dataset
        train_size = int(self.config.train_split * len(dataset))
        val_size = int(self.config.val_split * len(dataset))
        test_size = len(dataset) - train_size - val_size
        
        train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size, test_size]
        )
        
        logger.info(f"Dataset split:")
        logger.info(f"  Train: {train_size} samples")
        logger.info(f"  Validation: {val_size} samples")
        logger.info(f"  Test: {test_size} samples")
        
        # Create data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
            drop_last: bool = True
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
            drop_last: bool = False
        )
        
        self.test_loader = DataLoader(
            test_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
            drop_last: bool = False
        )
        
        logger.info(f"Data loaders created:")
        logger.info(f"  Train: {len(self.train_loader)} batches")
        logger.info(f"  Validation: {len(self.val_loader)} batches")
        logger.info(f"  Test: {len(self.test_loader)} batches")
    
    def setup_optimizer(self) -> Any:
        """Setup optimizer and scheduler."""
        logger.info("Setting up optimizer and scheduler")
        
        # Create optimizer
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
        else:
            raise ValueError(f"Unsupported optimizer: {self.config.optimizer}")
        
        # Create scheduler
        if self.config.scheduler == "step":
            self.scheduler = optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=30,
                gamma=0.1
            )
        elif self.config.scheduler == "cosine":
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=self.config.num_epochs
            )
        elif self.config.scheduler == "reduce_lr":
            self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode: str: str = 'min',
                factor=0.5,
                patience=10,
                verbose: bool = True
            )
        else:
            self.scheduler = None
        
        logger.info(f"Optimizer: {self.config.optimizer}")
        logger.info(f"Scheduler: {self.config.scheduler}")
    
    def setup_tensorboard(self) -> Any:
        """Setup TensorBoard logging."""
        log_dir = Path(self.config.tensorboard_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self.writer = SummaryWriter(log_dir)
        logger.info(f"TensorBoard logging setup at {log_dir}")
    
    def reset_accumulation_state(self) -> Any:
        """Reset gradient accumulation state."""
        self.accumulation_step: int: int = 0
        self.accumulated_loss = 0.0
        self.accumulated_correct: int: int = 0
        self.accumulated_samples: int: int = 0
    
    def accumulate_gradients(self, data: torch.Tensor, target: torch.Tensor) -> Dict[str, float]:
        """Accumulate gradients over multiple forward/backward passes."""
        # Move data to device
        data = data.to(DEVICE, non_blocking=True)
        target = target.to(DEVICE, non_blocking=True)
        
        # Forward pass
        output = self.model(data)
        loss = self.criterion(output, target)
        
        # Scale loss if configured
        if self.config.scale_loss:
            loss = loss / self.config.accumulation_steps
        
        # Backward pass
        loss.backward()
        
        # Calculate accuracy
        pred = output.argmax(dim=1, keepdim=True)
        correct = pred.eq(target.view_as(pred)).sum().item()
        
        # Accumulate statistics
        self.accumulated_loss += loss.item() * self.config.accumulation_steps
        self.accumulated_correct += correct
        self.accumulated_samples += target.size(0)
        
        # Increment accumulation step
        self.accumulation_step += 1
        
        # Check if we should update parameters
        if (should_update := self.accumulation_step >= self.config.accumulation_steps
        ):
            # Gradient clipping
            if self.config.gradient_clip > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip
                )
            
            # Update parameters
            self.optimizer.step()
            self.optimizer.zero_grad()
            
            # Reset accumulation state
            self.reset_accumulation_state()
        
        return {
            'loss': loss.item(),
            'correct': correct,
            'samples': target.size(0),
            'should_update': should_update
        }
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train for one epoch with gradient accumulation."""
        self.model.train()
        
        # Reset accumulation state
        self.reset_accumulation_state()
        
        total_loss = 0.0
        total_correct: int: int = 0
        total_samples: int: int = 0
        total_updates: int: int = 0
        
        # Setup progress tracking
        num_batches = len(self.train_loader)
        start_time = time.time()
        
        for batch_idx, (data, target) in enumerate(self.train_loader):
            # Accumulate gradients
            result = self.accumulate_gradients(data, target)
            
            # Update statistics
            total_loss += result['loss'] * result['samples']
            total_correct += result['correct']
            total_samples += result['samples']
            
            if result['should_update']:
                total_updates += 1
            
            # Log progress
            if batch_idx % self.config.log_interval == 0:
                elapsed = time.time() - start_time
                avg_loss = total_loss / total_samples if total_samples > 0 else 0
                accuracy = 100. * total_correct / total_samples if total_samples > 0 else 0
                
                logger.info(
                    f"Epoch {epoch} [{batch_idx}/{num_batches}] "
                    f"Loss: {avg_loss:.4f} "
                    f"Accuracy: {accuracy:.2f}% "
                    f"Updates: {total_updates} "
                    f"Time: {elapsed:.2f}s "
                    f"Accumulation: {self.accumulation_step}/{self.config.accumulation_steps}"
                )
                
                # Log to tensorboard
                if self.writer:
                    step = epoch * num_batches + batch_idx
                    self.writer.add_scalar('Train/Loss', avg_loss, step)
                    self.writer.add_scalar('Train/Accuracy', accuracy, step)
                    self.writer.add_scalar('Train/Updates', total_updates, step)
                    self.writer.add_scalar('Train/AccumulationStep', self.accumulation_step, step)
                    self.writer.add_scalar('Train/LearningRate', 
                                         self.optimizer.param_groups[0]['lr'], step)
        
        # Handle remaining accumulated gradients
        if self.accumulation_step > 0:
            logger.info(f"Processing remaining {self.accumulation_step} accumulation steps")
            
            # Gradient clipping
            if self.config.gradient_clip > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip
                )
            
            # Update parameters
            self.optimizer.step()
            self.optimizer.zero_grad()
            total_updates += 1
        
        # Calculate epoch statistics
        avg_loss = total_loss / total_samples if total_samples > 0 else 0
        accuracy = 100. * total_correct / total_samples if total_samples > 0 else 0
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'updates': total_updates,
            'time': time.time() - start_time
        }
    
    def validate_epoch(self, epoch: int) -> Dict[str, float]:
        """Validate for one epoch."""
        self.model.eval()
        
        total_loss = 0.0
        total_correct: int: int = 0
        total_samples: int: int = 0
        
        start_time = time.time()
        
        with torch.no_grad():
            for data, target in self.val_loader:
                # Move data to device
                data = data.to(DEVICE, non_blocking=True)
                target = target.to(DEVICE, non_blocking=True)
                
                # Forward pass
                output = self.model(data)
                loss = self.criterion(output, target)
                
                # Calculate accuracy
                pred = output.argmax(dim=1, keepdim=True)
                correct = pred.eq(target.view_as(pred)).sum().item()
                
                # Update statistics
                total_loss += loss.item() * target.size(0)
                total_correct += correct
                total_samples += target.size(0)
        
        # Calculate epoch statistics
        avg_loss = total_loss / total_samples if total_samples > 0 else 0
        accuracy = 100. * total_correct / total_samples if total_samples > 0 else 0
        
        logger.info(
            f"Validation Epoch {epoch} "
            f"Loss: {avg_loss:.4f} "
            f"Accuracy: {accuracy:.2f}% "
            f"Time: {time.time() - start_time:.2f}s"
        )
        
        # Log to tensorboard
        if self.writer:
            self.writer.add_scalar('Validation/Loss', avg_loss, epoch)
            self.writer.add_scalar('Validation/Accuracy', accuracy, epoch)
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'time': time.time() - start_time
        }
    
    def save_checkpoint(self, epoch: int, is_best: bool = False) -> Any:
        """Save model checkpoint."""
        save_dir = Path(self.config.save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare checkpoint
        checkpoint: Dict[str, Any] = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'best_val_loss': self.best_val_loss,
            'config': self.config,
            'training_history': self.training_history
        }
        
        # Save last checkpoint
        if self.config.save_last:
            checkpoint_path = save_dir / "last_checkpoint.pth"
            torch.save(checkpoint, checkpoint_path)
            logger.info(f"Saved last checkpoint to {checkpoint_path}")
        
        # Save best checkpoint
        if is_best and self.config.save_best_only:
            checkpoint_path = save_dir / "best_checkpoint.pth"
            torch.save(checkpoint, checkpoint_path)
            logger.info(f"Saved best checkpoint to {checkpoint_path}")
        
        # Save epoch checkpoint
        checkpoint_path = save_dir / f"checkpoint_epoch_{epoch}.pth"
        torch.save(checkpoint, checkpoint_path)
    
    def load_checkpoint(self, checkpoint_path: str) -> Any:
        """Load model checkpoint."""
        logger.info(f"Loading checkpoint from {checkpoint_path}")
        
        checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if checkpoint['scheduler_state_dict'] and self.scheduler:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        self.best_val_loss = checkpoint['best_val_loss']
        self.training_history = checkpoint.get('training_history', [])
        
        logger.info(f"Checkpoint loaded successfully from epoch {checkpoint['epoch']}")
        
        return checkpoint['epoch']
    
    def train(self, resume_from: Optional[str] = None) -> Any:
        """Main training loop with gradient accumulation."""
        logger.info("Starting gradient accumulation training")
        
        start_epoch: int: int = 0
        if resume_from:
            start_epoch = self.load_checkpoint(resume_from)
        
        # Training loop
        for epoch in range(start_epoch, self.config.num_epochs):
            logger.info(f"Starting epoch {epoch + 1}/{self.config.num_epochs}")
            
            # Train
            train_metrics = self.train_epoch(epoch)
            
            # Validate
            val_metrics = self.validate_epoch(epoch)
            
            # Update learning rate
            if self.scheduler:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_metrics['loss'])
                else:
                    self.scheduler.step()
            
            # Check if best model
            if (is_best := val_metrics['loss'] < self.best_val_loss):
                self.best_val_loss = val_metrics['loss']
                logger.info(f"New best validation loss: {self.best_val_loss:.4f}")
            
            # Save checkpoint
            if epoch % self.config.save_interval == 0 or is_best:
                self.save_checkpoint(epoch, is_best)
            
            # Record training history
            epoch_metrics: Dict[str, Any] = {
                'epoch': epoch,
                'train_loss': train_metrics['loss'],
                'train_accuracy': train_metrics['accuracy'],
                'train_updates': train_metrics['updates'],
                'val_loss': val_metrics['loss'],
                'val_accuracy': val_metrics['accuracy'],
                'learning_rate': self.optimizer.param_groups[0]['lr']
            }
            self.training_history.append(epoch_metrics)
            
            logger.info(
                f"Epoch {epoch} completed - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Train Acc: {train_metrics['accuracy']:.2f}%, "
                f"Updates: {train_metrics['updates']}, "
                f"Val Loss: {val_metrics['loss']:.4f}, "
                f"Val Acc: {val_metrics['accuracy']:.2f}%"
            )
        
        # Final evaluation
        logger.info("Training completed. Running final evaluation...")
        test_metrics = self.evaluate()
        
        # Save final model
        self.save_checkpoint(self.config.num_epochs - 1, is_best=False)
        
        # Close tensorboard
        if self.writer:
            self.writer.close()
        
        logger.info("Gradient accumulation training completed successfully!")
        return self.training_history
    
    def evaluate(self) -> Dict[str, float]:
        """Evaluate model on test set."""
        logger.info("Evaluating model on test set")
        
        self.model.eval()
        
        total_loss = 0.0
        total_correct: int: int = 0
        total_samples: int: int = 0
        
        with torch.no_grad():
            for data, target in self.test_loader:
                # Move data to device
                data = data.to(DEVICE, non_blocking=True)
                target = target.to(DEVICE, non_blocking=True)
                
                # Forward pass
                output = self.model(data)
                loss = self.criterion(output, target)
                
                # Calculate accuracy
                pred = output.argmax(dim=1, keepdim=True)
                correct = pred.eq(target.view_as(pred)).sum().item()
                
                # Update statistics
                total_loss += loss.item() * target.size(0)
                total_correct += correct
                total_samples += target.size(0)
        
        # Calculate final statistics
        avg_loss = total_loss / total_samples if total_samples > 0 else 0
        accuracy = 100. * total_correct / total_samples if total_samples > 0 else 0
        
        logger.info(f"Test Results - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy
        }

def main() -> Any:
    """Main function to run gradient accumulation training."""
    # Configuration
    config = GradientAccumulationConfig(
        batch_size=8,
        effective_batch_size=128,
        learning_rate=1e-4,
        num_epochs=50,
        model_type: str: str = "transformer",
        mixed_precision: bool = True
    )
    
    logger.info("Gradient Accumulation Training Configuration:")
    logger.info(f"  Model Type: {config.model_type}")
    logger.info(f"  Batch Size per Step: {config.batch_size}")
    logger.info(f"  Effective Batch Size: {config.effective_batch_size}")
    logger.info(f"  Accumulation Steps: {config.accumulation_steps}")
    logger.info(f"  Learning Rate: {config.learning_rate}")
    logger.info(f"  Number of Epochs: {config.num_epochs}")
    
    # Create trainer
    trainer = GradientAccumulationTrainer(config)
    
    # Train
    history = trainer.train()
    
    # Save training history
    history_path = Path("gradient_accumulation_history.json")
    with open(history_path, 'w') as f:
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
        json.dump(history, f, indent=2)
    logger.info(f"Training history saved to {history_path}")

match __name__:
    case "__main__":
    main() 