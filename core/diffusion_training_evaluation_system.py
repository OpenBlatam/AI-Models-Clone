#!/usr/bin/env python3
"""
Diffusion Model Training and Evaluation System

This module provides a comprehensive system for training and evaluating diffusion models
with proper monitoring, metrics tracking, and evaluation capabilities.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, random_split
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.cuda.amp import GradScaler, autocast

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from enum import Enum
import warnings
from tqdm import tqdm
import pickle
import gc

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enums and Types
class TrainingMode(Enum):
    """Training modes for diffusion models."""
    UNCONDITIONAL = "unconditional"
    CONDITIONAL = "conditional"
    INPAINTING = "inpainting"
    CONTROLNET = "controlnet"
    REFINER = "refiner"

class EvaluationMetric(Enum):
    """Evaluation metrics for diffusion models."""
    FID = "fid"  # Fréchet Inception Distance
    LPIPS = "lpips"  # Learned Perceptual Image Patch Similarity
    SSIM = "ssim"  # Structural Similarity Index
    PSNR = "psnr"  # Peak Signal-to-Noise Ratio
    MSE = "mse"  # Mean Squared Error
    MAE = "mae"  # Mean Absolute Error
    CLIP_SCORE = "clip_score"  # CLIP-based similarity score
    CUSTOM = "custom"

class CheckpointStrategy(Enum):
    """Checkpoint saving strategies."""
    BEST_METRIC = "best_metric"
    LAST_N = "last_n"
    EVERY_N_STEPS = "every_n_steps"
    EVERY_N_EPOCHS = "every_n_epochs"

# Configuration Classes
@dataclass
class TrainingConfig:
    """Configuration for diffusion model training."""
    # Model configuration
    model_name: str = "runwayml/stable-diffusion-v1-5"
    model_type: TrainingMode = TrainingMode.CONDITIONAL
    
    # Training hyperparameters
    batch_size: int = 4
    learning_rate: float = 1e-5
    num_epochs: int = 100
    gradient_accumulation_steps: int = 4
    max_grad_norm: float = 1.0
    weight_decay: float = 1e-2
    
    # Diffusion configuration
    num_train_timesteps: int = 1000
    beta_start: float = 0.00085
    beta_end: float = 0.012
    
    # Data configuration
    image_size: int = 512
    center_crop: bool = True
    random_flip: bool = True
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    
    # Optimization
    mixed_precision: bool = True
    gradient_checkpointing: bool = True
    
    # Debugging and monitoring
    enable_autograd_anomaly: bool = False  # Enable autograd.detect_anomaly() for debugging
    autograd_anomaly_mode: str = "default"  # "default", "trace", "detect"
    enable_gradient_debugging: bool = False  # Enable gradient debugging tools
    enable_memory_profiling: bool = False  # Enable memory profiling
    enable_performance_profiling: bool = False  # Enable performance profiling
    
    # Logging and checkpointing
    logging_steps: int = 10
    save_steps: int = 1000
    save_total_limit: Optional[int] = None
    eval_steps: int = 500
    warmup_steps: int = 0
    
    # Distributed training
    distributed: bool = False
    local_rank: int = 0
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    seed: int = 42

@dataclass
class EvaluationConfig:
    """Configuration for model evaluation."""
    # Evaluation metrics
    metrics: List[EvaluationMetric] = field(default_factory=lambda: [
        EvaluationMetric.FID, EvaluationMetric.LPIPS, EvaluationMetric.SSIM
    ])
    
    # Evaluation settings
    batch_size: int = 8
    num_samples: int = 1000
    save_generated_images: bool = True
    save_metrics: bool = True
    
    # Metric-specific settings
    fid_features: int = 2048
    lpips_model: str = "alex"
    ssim_window_size: int = 11
    
    # Output settings
    output_dir: str = "evaluation_results"
    save_format: str = "png"

@dataclass
class TrainingMetrics:
    """Container for training metrics."""
    train_loss: List[float] = field(default_factory=list)
    val_loss: List[float] = field(default_factory=list)
    learning_rate: List[float] = field(default_factory=list)
    gradient_norm: List[float] = field(default_factory=list)
    epoch_times: List[float] = field(default_factory=list)
    step_times: List[float] = field(default_factory=list)
    
    def add_train_loss(self, loss: float):
        self.train_loss.append(loss)
    
    def add_val_loss(self, loss: float):
        self.val_loss.append(loss)
    
    def add_lr(self, lr: float):
        self.learning_rate.append(lr)
    
    def add_grad_norm(self, norm: float):
        self.gradient_norm.append(norm)
    
    def add_epoch_time(self, time: float):
        self.epoch_times.append(time)
    
    def add_step_time(self, time: float):
        self.step_times.append(time)
    
    def get_latest_train_loss(self) -> Optional[float]:
        return self.train_loss[-1] if self.train_loss else None
    
    def get_latest_val_loss(self) -> Optional[float]:
        return self.val_loss[-1] if self.val_loss else None
    
    def get_best_val_loss(self) -> Optional[float]:
        return min(self.val_loss) if self.val_loss else None

# Core Classes
class DiffusionDataset(Dataset):
    """Base dataset class for diffusion model training."""
    
    def __init__(self, data_dir: str, image_size: int = 512, transform=None):
        self.data_dir = Path(data_dir)
        self.image_size = image_size
        self.transform = transform
        self.samples = self._load_samples()
    
    def _load_samples(self) -> List[Dict[str, Any]]:
        """Load dataset samples. Override in subclasses."""
        raise NotImplementedError
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get a sample. Override in subclasses."""
        raise NotImplementedError

class ImageTextDataset(DiffusionDataset):
    """Dataset for image-text pairs (e.g., Stable Diffusion training)."""
    
    def __init__(self, data_dir: str, tokenizer=None, image_size: int = 512, max_length: int = 77):
        super().__init__(data_dir, image_size)
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.samples = self._load_samples()
    
    def _load_samples(self) -> List[Dict[str, Any]]:
        """Load image-text pairs from directory."""
        samples = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        for image_file in self.data_dir.rglob('*'):
            if image_file.suffix.lower() in image_extensions:
                # Look for corresponding text file
                text_file = image_file.with_suffix('.txt')
                if text_file.exists():
                    with open(text_file, 'r', encoding='utf-8') as f:
                        text = f.read().strip()
                    samples.append({
                        'image_path': str(image_file),
                        'text': text
                    })
        
        return samples
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get image-text pair."""
        sample = self.samples[idx]
        
        # Load and preprocess image
        image = self._load_image(sample['image_path'])
        
        # Tokenize text
        text_tokens = self._tokenize_text(sample['text'])
        
        return {
            'image': image,
            'text_tokens': text_tokens,
            'text': sample['text']
        }
    
    def _load_image(self, image_path: str) -> torch.Tensor:
        """Load and preprocess image."""
        # This is a placeholder - implement actual image loading
        # In practice, you'd use PIL, torchvision, or similar
        return torch.randn(3, self.image_size, self.image_size)
    
    def _tokenize_text(self, text: str) -> torch.Tensor:
        """Tokenize text using the provided tokenizer."""
        if self.tokenizer is None:
            # Return dummy tokens
            return torch.randint(0, 1000, (self.max_length,))
        
        # In practice, you'd use the actual tokenizer
        tokens = self.tokenizer(
            text,
            padding="max_length",
            max_length=self.max_length,
            truncation=True,
            return_tensors="pt"
        )
        return tokens['input_ids'].squeeze(0)

class DiffusionTrainer:
    """Main trainer class for diffusion models."""
    
    def __init__(self, 
                 model: nn.Module,
                 config: TrainingConfig,
                 train_dataset: Dataset,
                 val_dataset: Optional[Dataset] = None,
                 optimizer: Optional[Optimizer] = None,
                 scheduler: Optional[_LRScheduler] = None):
        self.model = model
        self.config = config
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.optimizer = optimizer
        self.scheduler = scheduler
        
        # Setup device and distributed training
        self.device = self._setup_device()
        self.model = self.model.to(self.device)
        
        # Setup training components
        self._setup_training_components()
        
        # Metrics tracking
        self.metrics = TrainingMetrics()
        self.best_val_loss = float('inf')
        self.global_step = 0
        
        # Checkpoint management
        self.checkpoint_dir = Path("checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Mixed precision
        self.scaler = GradScaler() if config.mixed_precision else None
        
        logger.info(f"✅ Trainer initialized on device: {self.device}")
    
    def _setup_device(self) -> torch.device:
        """Setup device for training."""
        if self.config.distributed:
            torch.cuda.set_device(self.config.local_rank)
            dist.init_process_group(backend='nccl')
            return torch.device(f'cuda:{self.config.local_rank}')
        else:
            return torch.device(self.config.device)
    
    def _setup_training_components(self):
        """Setup optimizer, scheduler, and other training components."""
        if self.optimizer is None:
            self.optimizer = torch.optim.AdamW(
                self.model.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        
        if self.scheduler is None:
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=self.config.num_epochs
            )
        
        # Enable gradient checkpointing if specified
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()
    
    def _get_debugging_context(self):
        """Get debugging context manager based on configuration."""
        if self.config.enable_autograd_anomaly:
            # Create autograd anomaly detection context
            if self.config.autograd_anomaly_mode == "trace":
                return torch.autograd.detect_anomaly(mode="trace")
            elif self.config.autograd_anomaly_mode == "detect":
                return torch.autograd.detect_anomaly(mode="detect")
            else:
                return torch.autograd.detect_anomaly()
        else:
            # Return a no-op context manager
            from contextlib import nullcontext
            return nullcontext()
    
    def _debug_gradients(self, step_name: str):
        """Debug gradient information if enabled."""
        if not self.config.enable_gradient_debugging:
            return
        
        logger.info(f"🔍 Gradient debugging for {step_name}:")
        
        # Check for NaN/Inf in gradients
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                grad_norm = param.grad.norm().item()
                grad_has_nan = torch.isnan(param.grad).any().item()
                grad_has_inf = torch.isinf(param.grad).any().item()
                
                if grad_has_nan or grad_has_inf:
                    logger.warning(f"⚠️ Parameter {name}: grad_norm={grad_norm:.6f}, has_nan={grad_has_nan}, has_inf={grad_has_inf}")
                
                # Log gradient statistics
                if step_name == "training_step" and self.global_step % self.config.logging_steps == 0:
                    logger.info(f"📊 {name}: grad_norm={grad_norm:.6f}, grad_mean={param.grad.mean().item():.6f}, grad_std={param.grad.std().item():.6f}")
    
    def _debug_memory_usage(self, step_name: str):
        """Debug memory usage if enabled."""
        if not self.config.enable_memory_profiling:
            return
        
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3  # GB
            reserved = torch.cuda.memory_reserved() / 1024**3   # GB
            logger.info(f"💾 Memory usage at {step_name}: allocated={allocated:.2f}GB, reserved={reserved:.2f}GB")
    
    def _debug_performance(self, step_name: str, start_time: float):
        """Debug performance if enabled."""
        if not self.config.enable_performance_profiling:
            return
        
        step_time = time.time() - start_time
        logger.info(f"⏱️ Performance at {step_name}: {step_time:.4f}s")
    
    def train(self) -> Dict[str, Any]:
        """Main training loop."""
        logger.info("🚀 Starting training...")
        
        # Create data loaders
        train_loader = self._create_data_loader(self.train_dataset, is_train=True)
        val_loader = self._create_data_loader(self.val_dataset, is_train=False) if self.val_dataset else None
        
        # Training loop
        for epoch in range(self.config.num_epochs):
            epoch_start_time = time.time()
            
            # Training phase
            train_loss = self._train_epoch(train_loader, epoch)
            
            # Validation phase
            val_loss = None
            if val_loader:
                val_loss = self._validate_epoch(val_loader, epoch)
            
            # Update learning rate
            if self.scheduler:
                self.scheduler.step()
            
            # Record metrics
            epoch_time = time.time() - epoch_start_time
            self.metrics.add_epoch_time(epoch_time)
            self.metrics.add_train_loss(train_loss)
            if val_loss:
                self.metrics.add_val_loss(val_loss)
            
            # Save checkpoint
            self._save_checkpoint(epoch, val_loss)
            
            # Log progress
            self._log_epoch_progress(epoch, train_loss, val_loss, epoch_time)
        
        # Final evaluation
        final_metrics = self._final_evaluation()
        
        logger.info("🎉 Training completed!")
        return final_metrics
    
    def _create_data_loader(self, dataset: Dataset, is_train: bool) -> DataLoader:
        """Create data loader for training or validation."""
        return DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=is_train,
            num_workers=4 if is_train else 2,
            pin_memory=True,
            drop_last=is_train
        )
    
    def _train_epoch(self, train_loader: DataLoader, epoch: int) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = len(train_loader)
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{self.config.num_epochs}")
        
        for batch_idx, batch in enumerate(progress_bar):
            step_start_time = time.time()
            
            # Forward pass
            loss = self._training_step(batch)
            
            # Backward pass with debugging context
            with self._get_debugging_context():
                if self.config.mixed_precision:
                    self.scaler.scale(loss).backward()
                else:
                    loss.backward()
            
            # Gradient debugging after backward pass
            self._debug_gradients("training_step")
            
            # Gradient accumulation
            if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                # Gradient clipping
                if self.config.max_grad_norm > 0:
                    if self.config.mixed_precision:
                        self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(), 
                        self.config.max_grad_norm
                    )
                
                # Gradient debugging after clipping
                self._debug_gradients("gradient_clipping")
                
                # Optimizer step
                if self.config.mixed_precision:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()
                
                self.optimizer.zero_grad()
                self.global_step += 1
            
            # Record metrics
            total_loss += loss.item()
            step_time = time.time() - step_start_time
            self.metrics.add_step_time(step_time)
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'avg_loss': f'{total_loss/(batch_idx+1):.4f}',
                'lr': f'{self.optimizer.param_groups[0]["lr"]:.2e}'
            })
            
            # Logging
            if self.global_step % self.config.logging_steps == 0:
                self._log_training_step(epoch, batch_idx, loss.item())
        
        return total_loss / num_batches
    
    def _training_step(self, batch: Dict[str, Any]) -> torch.Tensor:
        """Single training step with debugging tools integration."""
        step_start_time = time.time()
        
        # Memory debugging before forward pass
        self._debug_memory_usage("training_step_start")
        
        # Use debugging context for forward and backward pass
        with self._get_debugging_context():
            # This is a placeholder - implement actual training logic
            # based on your specific diffusion model architecture
            
            # Example for conditional diffusion (Stable Diffusion):
            # images = batch['image'].to(self.device)
            # text_tokens = batch['text_tokens'].to(self.device)
            # 
            # # Add noise to images
            # noise = torch.randn_like(images)
            # timesteps = torch.randint(0, self.config.num_train_timesteps, (images.shape[0],))
            # 
            # # Forward pass
            # noise_pred = self.model(images, timesteps, text_tokens)
            # 
            # # Compute loss
            # loss = F.mse_loss(noise_pred, noise)
            
            # For now, return a dummy loss
            loss = torch.tensor(0.1, device=self.device, requires_grad=True)
        
        # Performance debugging
        self._debug_performance("training_step", step_start_time)
        
        # Memory debugging after forward pass
        self._debug_memory_usage("training_step_end")
        
        return loss
    
    def _validate_epoch(self, val_loader: DataLoader, epoch: int) -> float:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0.0
        num_batches = len(val_loader)
        
        with torch.no_grad():
            for batch in val_loader:
                loss = self._validation_step(batch)
                total_loss += loss.item()
        
        return total_loss / num_batches
    
    def _validation_step(self, batch: Dict[str, Any]) -> torch.Tensor:
        """Single validation step with debugging tools integration."""
        step_start_time = time.time()
        
        # Memory debugging before forward pass
        self._debug_memory_usage("validation_step_start")
        
        # Use debugging context for forward pass (no gradients needed)
        with self._get_debugging_context():
            # Similar to training step but without gradient computation
            # This is a placeholder
            loss = torch.tensor(0.1, device=self.device)
        
        # Performance debugging
        self._debug_performance("validation_step", step_start_time)
        
        # Memory debugging after forward pass
        self._debug_memory_usage("validation_step_end")
        
        return loss
    
    def _save_checkpoint(self, epoch: int, val_loss: Optional[float]):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'config': self.config,
            'metrics': self.metrics,
            'best_val_loss': self.best_val_loss,
            'global_step': self.global_step
        }
        
        # Save latest checkpoint
        latest_path = self.checkpoint_dir / "latest_checkpoint.pth"
        torch.save(checkpoint, latest_path)
        
        # Save epoch checkpoint
        epoch_path = self.checkpoint_dir / f"checkpoint_epoch_{epoch}.pth"
        torch.save(checkpoint, epoch_path)
        
        # Save best checkpoint if validation loss improved
        if val_loss and val_loss < self.best_val_loss:
            self.best_val_loss = val_loss
            best_path = self.checkpoint_dir / "best_checkpoint.pth"
            torch.save(checkpoint, best_path)
            logger.info(f"💾 New best checkpoint saved with val_loss: {val_loss:.4f}")
        
        # Clean up old checkpoints
        self._cleanup_old_checkpoints()
    
    def _cleanup_old_checkpoints(self):
        """Remove old checkpoints based on strategy."""
        if self.config.save_total_limit is None:
            return
        
        checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_epoch_*.pth"))
        if len(checkpoints) > self.config.save_total_limit:
            for checkpoint in checkpoints[:-self.config.save_total_limit]:
                checkpoint.unlink()
                logger.info(f"🗑️ Removed old checkpoint: {checkpoint.name}")
    
    def _log_training_step(self, epoch: int, batch_idx: int, loss: float):
        """Log training step information."""
        logger.info(
            f"Epoch {epoch+1}, Batch {batch_idx}, Loss: {loss:.4f}, "
            f"LR: {self.optimizer.param_groups[0]['lr']:.2e}"
        )
    
    def _log_epoch_progress(self, epoch: int, train_loss: float, val_loss: Optional[float], epoch_time: float):
        """Log epoch progress."""
        log_msg = f"Epoch {epoch+1}/{self.config.num_epochs} - "
        log_msg += f"Train Loss: {train_loss:.4f}"
        if val_loss:
            log_msg += f", Val Loss: {val_loss:.4f}"
        log_msg += f", Time: {epoch_time:.2f}s"
        logger.info(log_msg)
    
    def _final_evaluation(self) -> Dict[str, Any]:
        """Perform final evaluation and return metrics."""
        return {
            'final_train_loss': self.metrics.get_latest_train_loss(),
            'final_val_loss': self.metrics.get_latest_val_loss(),
            'best_val_loss': self.metrics.get_best_val_loss(),
            'total_epochs': len(self.metrics.train_loss),
            'total_steps': self.global_step,
            'avg_epoch_time': np.mean(self.metrics.epoch_times),
            'avg_step_time': np.mean(self.metrics.step_times)
        }
    
    def load_checkpoint(self, checkpoint_path: str):
        """Load model from checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if self.scheduler and checkpoint['scheduler_state_dict']:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        self.metrics = checkpoint['metrics']
        self.best_val_loss = checkpoint['best_val_loss']
        self.global_step = checkpoint['global_step']
        
        logger.info(f"✅ Checkpoint loaded from {checkpoint_path}")

    def enable_debugging(self, enable_autograd_anomaly: bool = True, 
                        enable_gradient_debugging: bool = True,
                        enable_memory_profiling: bool = True,
                        enable_performance_profiling: bool = True,
                        autograd_anomaly_mode: str = "default"):
        """Enable debugging tools dynamically."""
        self.config.enable_autograd_anomaly = enable_autograd_anomaly
        self.config.enable_gradient_debugging = enable_gradient_debugging
        self.config.enable_memory_profiling = enable_memory_profiling
        self.config.enable_performance_profiling = enable_performance_profiling
        self.config.autograd_anomaly_mode = autograd_anomaly_mode
        
        logger.info("🔧 Debugging tools enabled:")
        if enable_autograd_anomaly:
            logger.info(f"  - Autograd anomaly detection: {autograd_anomaly_mode} mode")
        if enable_gradient_debugging:
            logger.info("  - Gradient debugging")
        if enable_memory_profiling:
            logger.info("  - Memory profiling")
        if enable_performance_profiling:
            logger.info("  - Performance profiling")
    
    def disable_debugging(self):
        """Disable all debugging tools."""
        self.config.enable_autograd_anomaly = False
        self.config.enable_gradient_debugging = False
        self.config.enable_memory_profiling = False
        self.config.enable_performance_profiling = False
        
        logger.info("🔧 All debugging tools disabled")
    
    def get_debugging_status(self) -> Dict[str, Any]:
        """Get current debugging tools status."""
        return {
            "autograd_anomaly": {
                "enabled": self.config.enable_autograd_anomaly,
                "mode": self.config.autograd_anomaly_mode if self.config.enable_autograd_anomaly else None
            },
            "gradient_debugging": self.config.enable_gradient_debugging,
            "memory_profiling": self.config.enable_memory_profiling,
            "performance_profiling": self.config.enable_performance_profiling
        }
    
    def log_debugging_info(self):
        """Log current debugging configuration and status."""
        status = self.get_debugging_status()
        logger.info("🔍 Current debugging configuration:")
        for key, value in status.items():
            if isinstance(value, dict):
                logger.info(f"  - {key}: {value}")
            else:
                logger.info(f"  - {key}: {value}")
        
        # Log PyTorch version and CUDA availability
        logger.info(f"  - PyTorch version: {torch.__version__}")
        logger.info(f"  - CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"  - CUDA version: {torch.version.cuda}")
            logger.info(f"  - GPU count: {torch.cuda.device_count()}")
            logger.info(f"  - Current GPU: {torch.cuda.current_device()}")
            logger.info(f"  - GPU name: {torch.cuda.get_device_name()}")

class DiffusionEvaluator:
    """Evaluator class for diffusion models."""
    
    def __init__(self, model: nn.Module, config: EvaluationConfig):
        self.model = model
        self.config = config
        self.device = next(model.parameters()).device
        
        # Create output directory
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Metrics storage
        self.metrics_results = {}
        
        logger.info(f"✅ Evaluator initialized with {len(config.metrics)} metrics")
    
    def evaluate(self, test_dataset: Dataset) -> Dict[str, Any]:
        """Evaluate the model on test dataset."""
        logger.info("🔍 Starting model evaluation...")
        
        # Create data loader
        test_loader = DataLoader(
            test_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True
        )
        
        # Generate samples
        generated_samples = self._generate_samples(test_loader)
        
        # Compute metrics
        metrics_results = self._compute_metrics(generated_samples, test_dataset)
        
        # Save results
        if self.config.save_metrics:
            self._save_evaluation_results(metrics_results)
        
        # Generate visualizations
        self._generate_evaluation_plots(metrics_results)
        
        logger.info("✅ Evaluation completed!")
        return metrics_results
    
    def _generate_samples(self, test_loader: DataLoader) -> List[Dict[str, Any]]:
        """Generate samples using the model."""
        self.model.eval()
        generated_samples = []
        
        with torch.no_grad():
            for batch in tqdm(test_loader, desc="Generating samples"):
                # This is a placeholder - implement actual generation logic
                # based on your specific diffusion model
                
                # Example for conditional generation:
                # text_tokens = batch['text_tokens'].to(self.device)
                # generated_image = self.model.generate(text_tokens)
                
                # For now, create dummy samples
                batch_size = batch['image'].shape[0] if 'image' in batch else 1
                dummy_image = torch.randn(batch_size, 3, 512, 512)
                
                generated_samples.append({
                    'generated_image': dummy_image,
                    'text': batch.get('text', ['dummy text'] * batch_size),
                    'original_image': batch.get('image', dummy_image)
                })
        
        return generated_samples
    
    def _compute_metrics(self, generated_samples: List[Dict[str, Any]], 
                        test_dataset: Dataset) -> Dict[str, Any]:
        """Compute evaluation metrics."""
        metrics_results = {}
        
        for metric in self.config.metrics:
            try:
                if metric == EvaluationMetric.FID:
                    metrics_results['fid'] = self._compute_fid(generated_samples)
                elif metric == EvaluationMetric.LPIPS:
                    metrics_results['lpips'] = self._compute_lpips(generated_samples)
                elif metric == EvaluationMetric.SSIM:
                    metrics_results['ssim'] = self._compute_ssim(generated_samples)
                elif metric == EvaluationMetric.PSNR:
                    metrics_results['psnr'] = self._compute_psnr(generated_samples)
                elif metric == EvaluationMetric.MSE:
                    metrics_results['mse'] = self._compute_mse(generated_samples)
                elif metric == EvaluationMetric.MAE:
                    metrics_results['mae'] = self._compute_mae(generated_samples)
                else:
                    logger.warning(f"Metric {metric.value} not implemented yet")
            except Exception as e:
                logger.error(f"Error computing {metric.value}: {e}")
                metrics_results[metric.value] = None
        
        return metrics_results
    
    def _compute_fid(self, generated_samples: List[Dict[str, Any]]) -> float:
        """Compute Fréchet Inception Distance."""
        # This is a placeholder - implement actual FID computation
        # You would typically use a pre-trained Inception model
        return np.random.normal(50, 10)  # Dummy FID score
    
    def _compute_lpips(self, generated_samples: List[Dict[str, Any]]) -> float:
        """Compute LPIPS distance."""
        # This is a placeholder - implement actual LPIPS computation
        return np.random.normal(0.3, 0.1)  # Dummy LPIPS score
    
    def _compute_ssim(self, generated_samples: List[Dict[str, Any]]) -> float:
        """Compute SSIM score."""
        # This is a placeholder - implement actual SSIM computation
        return np.random.normal(0.7, 0.1)  # Dummy SSIM score
    
    def _compute_psnr(self, generated_samples: List[Dict[str, Any]]) -> float:
        """Compute PSNR score."""
        # This is a placeholder - implement actual PSNR computation
        return np.random.normal(25, 5)  # Dummy PSNR score
    
    def _compute_mse(self, generated_samples: List[Dict[str, Any]]) -> float:
        """Compute MSE score."""
        # This is a placeholder - implement actual MSE computation
        return np.random.normal(0.1, 0.05)  # Dummy MSE score
    
    def _compute_mae(self, generated_samples: List[Dict[str, Any]]) -> float:
        """Compute MAE score."""
        # This is a placeholder - implement actual MAE computation
        return np.random.normal(0.2, 0.1)  # Dummy MAE score
    
    def _save_evaluation_results(self, metrics_results: Dict[str, Any]):
        """Save evaluation results to file."""
        results_file = self.output_dir / "evaluation_results.json"
        
        with open(results_file, 'w') as f:
            json.dump(metrics_results, f, indent=2)
        
        logger.info(f"💾 Evaluation results saved to {results_file}")
    
    def _generate_evaluation_plots(self, metrics_results: Dict[str, Any]):
        """Generate evaluation plots and visualizations."""
        # Create summary plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Diffusion Model Evaluation Results', fontsize=16)
        
        # Plot 1: Metric values
        metrics_names = list(metrics_results.keys())
        metrics_values = list(metrics_results.values())
        
        # Filter out None values
        valid_metrics = [(name, value) for name, value in zip(metrics_names, metrics_values) 
                        if value is not None]
        
        if valid_metrics:
            names, values = zip(*valid_metrics)
            axes[0, 0].bar(names, values)
            axes[0, 0].set_title('Evaluation Metrics')
            axes[0, 0].set_ylabel('Score')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Plot 2: Metric distribution (if we have multiple samples)
        if valid_metrics:
            axes[0, 1].hist(values, bins=10, alpha=0.7)
            axes[0, 1].set_title('Metric Distribution')
            axes[0, 1].set_xlabel('Score')
            axes[0, 1].set_ylabel('Frequency')
        
        # Plot 3: Comparison plot (placeholder)
        axes[1, 0].text(0.5, 0.5, 'Comparison Plot\n(Placeholder)', 
                        ha='center', va='center', transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('Model Comparison')
        
        # Plot 4: Summary statistics
        if valid_metrics:
            summary_text = f"Total Metrics: {len(valid_metrics)}\n"
            summary_text += f"Best Metric: {max(values):.4f}\n"
            summary_text += f"Worst Metric: {min(values):.4f}\n"
            summary_text += f"Average: {np.mean(values):.4f}"
            
            axes[1, 1].text(0.1, 0.5, summary_text, transform=axes[1, 1].transAxes,
                           fontsize=12, verticalalignment='center')
            axes[1, 1].set_title('Summary Statistics')
            axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        # Save plot
        plot_file = self.output_dir / "evaluation_plots.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📊 Evaluation plots saved to {plot_file}")

# Utility Functions
def create_training_config(**kwargs) -> TrainingConfig:
    """Create training configuration with custom parameters."""
    config = TrainingConfig()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            logger.warning(f"Unknown config parameter: {key}")
    return config

def create_evaluation_config(**kwargs) -> EvaluationConfig:
    """Create evaluation configuration with custom parameters."""
    config = EvaluationConfig()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            logger.warning(f"Unknown config parameter: {key}")
    return config

def setup_distributed_training(local_rank: int, world_size: int):
    """Setup distributed training environment."""
    torch.cuda.set_device(local_rank)
    dist.init_process_group(backend='nccl', world_size=world_size, rank=local_rank)
    return torch.device(f'cuda:{local_rank}')

def cleanup_distributed_training():
    """Cleanup distributed training environment."""
    if dist.is_initialized():
        dist.destroy_process_group()

# Example usage and testing
if __name__ == "__main__":
    # This section demonstrates how to use the training and evaluation system
    
    # Create a dummy model for demonstration
    class DummyDiffusionModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = nn.Conv2d(3, 3, 3, padding=1)
        
        def forward(self, x, timesteps=None, text_tokens=None):
            return self.conv(x)
    
    # Create dummy datasets
    class DummyDataset(Dataset):
        def __init__(self, size=100):
            self.size = size
        
        def __len__(self):
            return self.size
        
        def __getitem__(self, idx):
            return {
                'image': torch.randn(3, 512, 512),
                'text_tokens': torch.randint(0, 1000, (77,)),
                'text': f'Dummy text {idx}'
            }
    
    # Initialize components
    model = DummyDiffusionModel()
    train_dataset = DummyDataset(100)
    val_dataset = DummyDataset(20)
    
    # Create configurations
    training_config = create_training_config(
        batch_size=2,
        num_epochs=2,
        learning_rate=1e-4
    )
    
    evaluation_config = create_evaluation_config(
        metrics=[EvaluationMetric.MSE, EvaluationMetric.MAE],
        batch_size=4
    )
    
    # Create trainer and evaluator
    trainer = DiffusionTrainer(model, training_config, train_dataset, val_dataset)
    evaluator = DiffusionEvaluator(model, evaluation_config)
    
    # Run training (commented out for demo)
    # training_results = trainer.train()
    # print("Training Results:", training_results)
    
    # Run evaluation (commented out for demo)
    # evaluation_results = evaluator.evaluate(val_dataset)
    # print("Evaluation Results:", evaluation_results)
    
    print("✅ Diffusion Training and Evaluation System initialized successfully!")
    print("📚 Use the trainer and evaluator classes to train and evaluate your diffusion models.")
