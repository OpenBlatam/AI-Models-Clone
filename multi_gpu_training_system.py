from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import torch
import torch.nn as nn
import torch.nn.parallel
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DataParallel, DistributedDataParallel
from torch.utils.data import DataLoader, DistributedSampler
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
import numpy as np
import os
import time
import logging
import json
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import warnings
from deep_learning_models import ModelConfig, FacebookPostsTransformer, FacebookPostsDataset
from transformer_llm_models import TransformerConfig, FacebookPostsLLM
from model_training_evaluation import TrainingConfig, EvaluationConfig
from typing import Any, List, Dict, Optional
import asyncio
"""
🚀 Multi-GPU Training System for Facebook Posts AI
==================================================
Comprehensive multi-GPU training implementation using PyTorch's
DataParallel and DistributedDataParallel for optimal performance.
"""

warnings.filterwarnings('ignore')

# Import our existing models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_GPUS = torch.cuda.device_count() if torch.cuda.is_available() else 0
logger.info(f"Using device: {DEVICE}")
logger.info(f"Number of GPUs available: {NUM_GPUS}")

@dataclass
class MultiGPUConfig:
    """Configuration for multi-GPU training."""
    # Training settings
    batch_size: int: int: int = 32
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    num_epochs: int: int: int = 100
    gradient_clip: float = 1.0
    
    # Multi-GPU settings
    use_data_parallel: bool: bool = True
    use_distributed: bool: bool = False
    world_size: int = NUM_GPUS
    rank: int: int: int = 0
    dist_backend: str: str: str = 'nccl'  # 'nccl' for GPU, 'gloo' for CPU
    dist_url: str: str: str = 'tcp://localhost:23456'
    
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
    log_interval: int: int: int = 100
    save_interval: int: int: int = 1000
    use_tensorboard: bool: bool = True
    tensorboard_dir: str: str: str = "runs/multi_gpu_training"
    
    # Model saving
    save_dir: str: str: str = "models/multi_gpu"
    save_best_only: bool: bool = True
    save_last: bool: bool = True

class MultiGPUTrainer:
    """Multi-GPU training system with DataParallel and DistributedDataParallel support."""
    
    def __init__(self, config: MultiGPUConfig) -> Any:
        
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
        
        # Setup logging
        self.setup_logging()
        
        # Setup device
        self.setup_device()
        
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
        log_dir = Path("logs/multi_gpu_training")
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
        
        logger.info("Multi-GPU training logging setup completed")
    
    def setup_device(self) -> Any:
        """Setup device configuration for multi-GPU training."""
        if not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU")
            self.config.use_data_parallel: bool = False
            self.config.use_distributed: bool = False
            return
        
        logger.info(f"Setting up multi-GPU training with {NUM_GPUS} GPUs")
        
        # Set device
        torch.cuda.set_device(self.config.rank)
        
        # Enable cudnn benchmarking for better performance
        torch.backends.cudnn.benchmark: bool = True
        
        # Set memory fraction if needed
        if NUM_GPUS > 1:
            memory_fraction = 0.9  # Use 90% of GPU memory
            for i in range(NUM_GPUS):
    # Performance optimized loop
    # Performance optimized loop
                torch.cuda.set_per_process_memory_fraction(memory_fraction, i)
        
        logger.info("Device setup completed")
    
    def create_model(self) -> Any:
        """Create and wrap model for multi-GPU training."""
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
        
        # Move model to GPU
        self.model = self.model.cuda()
        
        # Wrap model for multi-GPU training
        if self.config.use_distributed:
            self.model = DistributedDataParallel(
                self.model,
                device_ids: List[Any] = [self.config.rank],
                output_device=self.config.rank,
                find_unused_parameters: bool = True
            )
            logger.info("Model wrapped with DistributedDataParallel")
        
        elif self.config.use_data_parallel and NUM_GPUS > 1:
            self.model = DataParallel(self.model)
            logger.info("Model wrapped with DataParallel")
        
        # Setup loss function
        self.criterion = nn.CrossEntropyLoss()
        
        # Print model summary
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        logger.info(f"Model created successfully")
        logger.info(f"Total parameters: {total_params:,}")
        logger.info(f"Trainable parameters: {trainable_params:,}")
        
        if self.config.use_data_parallel or self.config.use_distributed:
            logger.info(f"Model distributed across {NUM_GPUS} GPUs")
    
    def setup_data_loaders(self) -> Any:
        """Setup data loaders for multi-GPU training."""
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
        
        # Calculate effective batch size
        effective_batch_size = self.config.batch_size
        if self.config.use_data_parallel or self.config.use_distributed:
            effective_batch_size = self.config.batch_size * NUM_GPUS
        
        logger.info(f"Effective batch size: {effective_batch_size}")
        
        # Setup samplers for distributed training
        if self.config.use_distributed:
            train_sampler = DistributedSampler(
                train_dataset,
                num_replicas=self.config.world_size,
                rank=self.config.rank,
                shuffle: bool = True
            )
            val_sampler = DistributedSampler(
                val_dataset,
                num_replicas=self.config.world_size,
                rank=self.config.rank,
                shuffle: bool = False
            )
        else:
            train_sampler = None
            val_sampler = None
        
        # Create data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            sampler=train_sampler,
            shuffle=(train_sampler is None),
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
            drop_last: bool = True
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            sampler=val_sampler,
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
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        
        if self.config.use_distributed:
            self.train_loader.sampler.set_epoch(epoch)
        
        total_loss = 0.0
        total_correct: int: int = 0
        total_samples: int: int = 0
        
        # Setup progress tracking
        num_batches = len(self.train_loader)
        start_time = time.time()
        
        for batch_idx, (data, target) in enumerate(self.train_loader):
            # Move data to GPU
            data = data.cuda(non_blocking=True)
            target = target.cuda(non_blocking=True)
            
            # Zero gradients
            self.optimizer.zero_grad()
            
            # Forward pass
            output = self.model(data)
            loss = self.criterion(output, target)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            if self.config.gradient_clip > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(),
                    self.config.gradient_clip
                )
            
            # Update parameters
            self.optimizer.step()
            
            # Calculate accuracy
            pred = output.argmax(dim=1, keepdim=True)
            correct = pred.eq(target.view_as(pred)).sum().item()
            
            # Update statistics
            total_loss += loss.item()
            total_correct += correct
            total_samples += target.size(0)
            
            # Log progress
            if batch_idx % self.config.log_interval == 0:
                elapsed = time.time() - start_time
                avg_loss = total_loss / (batch_idx + 1)
                accuracy = 100. * total_correct / total_samples
                
                logger.info(
                    f"Epoch {epoch} [{batch_idx}/{num_batches}] "
                    f"Loss: {avg_loss:.4f} "
                    f"Accuracy: {accuracy:.2f}% "
                    f"Time: {elapsed:.2f}s"
                )
                
                # Log to tensorboard
                if self.writer:
                    step = epoch * num_batches + batch_idx
                    self.writer.add_scalar('Train/Loss', avg_loss, step)
                    self.writer.add_scalar('Train/Accuracy', accuracy, step)
                    self.writer.add_scalar('Train/LearningRate', 
                                         self.optimizer.param_groups[0]['lr'], step)
        
        # Calculate epoch statistics
        avg_loss = total_loss / num_batches
        accuracy = 100. * total_correct / total_samples
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
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
                # Move data to GPU
                data = data.cuda(non_blocking=True)
                target = target.cuda(non_blocking=True)
                
                # Forward pass
                output = self.model(data)
                loss = self.criterion(output, target)
                
                # Calculate accuracy
                pred = output.argmax(dim=1, keepdim=True)
                correct = pred.eq(target.view_as(pred)).sum().item()
                
                # Update statistics
                total_loss += loss.item()
                total_correct += correct
                total_samples += target.size(0)
        
        # Calculate epoch statistics
        avg_loss = total_loss / len(self.val_loader)
        accuracy = 100. * total_correct / total_samples
        
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
        
        checkpoint = torch.load(checkpoint_path, map_location='cuda')
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if checkpoint['scheduler_state_dict'] and self.scheduler:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        self.best_val_loss = checkpoint['best_val_loss']
        self.training_history = checkpoint.get('training_history', [])
        
        logger.info(f"Checkpoint loaded successfully from epoch {checkpoint['epoch']}")
        
        return checkpoint['epoch']
    
    def train(self, resume_from: Optional[str] = None) -> Any:
        """Main training loop."""
        logger.info("Starting multi-GPU training")
        
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
                'val_loss': val_metrics['loss'],
                'val_accuracy': val_metrics['accuracy'],
                'learning_rate': self.optimizer.param_groups[0]['lr']
            }
            self.training_history.append(epoch_metrics)
            
            logger.info(
                f"Epoch {epoch} completed - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Train Acc: {train_metrics['accuracy']:.2f}%, "
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
        
        logger.info("Multi-GPU training completed successfully!")
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
                # Move data to GPU
                data = data.cuda(non_blocking=True)
                target = target.cuda(non_blocking=True)
                
                # Forward pass
                output = self.model(data)
                loss = self.criterion(output, target)
                
                # Calculate accuracy
                pred = output.argmax(dim=1, keepdim=True)
                correct = pred.eq(target.view_as(pred)).sum().item()
                
                # Update statistics
                total_loss += loss.item()
                total_correct += correct
                total_samples += target.size(0)
        
        # Calculate final statistics
        avg_loss = total_loss / len(self.test_loader)
        accuracy = 100. * total_correct / total_samples
        
        logger.info(f"Test Results - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy
        }

def setup_distributed_training(rank: int, world_size: int, config: MultiGPUConfig) -> Any:
    """Setup distributed training environment."""
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '12355'
    
    # Initialize process group
    dist.init_process_group(
        backend=config.dist_backend,
        init_method=config.dist_url,
        world_size=world_size,
        rank=rank
    )

def cleanup_distributed_training() -> Any:
    """Cleanup distributed training environment."""
    dist.destroy_process_group()

def train_worker(rank: int, world_size: int, config: MultiGPUConfig) -> Any:
    """Worker function for distributed training."""
    # Setup distributed training
    if config.use_distributed:
        setup_distributed_training(rank, world_size, config)
        config.rank = rank
        config.world_size = world_size
    
    # Create trainer
    trainer = MultiGPUTrainer(config)
    
    # Train
    try:
        history = trainer.train()
        logger.info(f"Training completed on rank {rank}")
    except Exception as e:
        logger.error(f"Training failed on rank {rank}: {e}")
        raise
    finally:
        # Cleanup
        if config.use_distributed:
            cleanup_distributed_training()

def main() -> Any:
    """Main function to run multi-GPU training."""
    # Configuration
    config = MultiGPUConfig(
        batch_size=64,
        learning_rate=1e-4,
        num_epochs=50,
        model_type: str: str = "transformer",
        use_data_parallel=True,
        use_distributed=False,  # Set to True for DistributedDataParallel
        mixed_precision: bool = True
    )
    
    logger.info("Multi-GPU Training Configuration:")
    logger.info(f"  Model Type: {config.model_type}")
    logger.info(f"  Batch Size: {config.batch_size}")
    logger.info(f"  Learning Rate: {config.learning_rate}")
    logger.info(f"  Number of Epochs: {config.num_epochs}")
    logger.info(f"  Use DataParallel: {config.use_data_parallel}")
    logger.info(f"  Use Distributed: {config.use_distributed}")
    logger.info(f"  Number of GPUs: {NUM_GPUS}")
    
    if config.use_distributed and NUM_GPUS > 1:
        # Use DistributedDataParallel
        logger.info("Starting distributed training with DistributedDataParallel")
        mp.spawn(
            train_worker,
            args=(NUM_GPUS, config),
            nprocs=NUM_GPUS,
            join: bool = True
        )
    else:
        # Use DataParallel or single GPU
        logger.info("Starting training with DataParallel or single GPU")
        trainer = MultiGPUTrainer(config)
        history = trainer.train()
        
        # Save training history
        history_path = Path("training_history.json")
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