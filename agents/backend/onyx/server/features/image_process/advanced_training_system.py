#!/usr/bin/env python3
"""
Advanced Training System with Gradient Accumulation

This module integrates all components with advanced training capabilities:
- Tokenization and sequence handling
- Data loading with advanced augmentation
- Fine-tuning (LoRA, P-tuning)
- Attention mechanisms and positional encodings
- Gradient accumulation for large batch sizes
- Mixed precision training
- Performance monitoring
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import GradScaler, autocast
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
import numpy as np
import logging
from dataclasses import dataclass
from tqdm import tqdm
import time
import gc

logger = logging.getLogger(__name__)

# Import our custom modules
try:
    from text_tokenization import TextTokenizer, SequenceHandler
    from text_data_loader import TextDataLoader
    from lora_finetuning import LoRAConfig, LoRALayer, LoRAModel
    from ptuning_module import PTuningConfig, PTuningModel
    from advanced_transformer_system import AdvancedTransformerModel
    from performance_monitor import PerformanceMonitor
    MODULES_AVAILABLE = True
except ImportError:
    # Create dummy classes for demonstration
    class TextTokenizer:
        def __init__(self, vocab_size=50000, max_length=512):
            self.vocab_size = vocab_size
            self.max_length = max_length
        def save(self, path): pass
    
    class TextDataLoader:
        def __init__(self, tokenizer, batch_size=32, num_workers=4, pin_memory=True, persistent_workers=True):
            self.tokenizer = tokenizer
            self.batch_size = batch_size
        def create_dataloader(self, data_path): return None
    
    class LoRAConfig:
        def __init__(self, rank=16, alpha=32.0, dropout=0.1):
            self.rank = rank
            self.alpha = alpha
            self.dropout = dropout
    
    class LoRALayer: pass
    class LoRAModel: pass
    class PTuningConfig:
        def __init__(self, prefix_length=10, hidden_size=256):
            self.prefix_length = prefix_length
            self.hidden_size = hidden_size
    class PTuningModel: pass
    class AdvancedTransformerModel:
        def __init__(self, vocab_size=50000, max_length=512, hidden_size=768, num_layers=12, num_heads=12, dropout=0.1):
            pass
    class PerformanceMonitor:
        def __init__(self): pass
        def record_step(self, loss): pass
        def log_memory_usage(self): pass
        def log_epoch_summary(self, epoch): pass
    
    MODULES_AVAILABLE = False
    logger.warning("Some modules not available, using dummy implementations for demonstration")


@dataclass
class TrainingConfig:
    """Configuration for advanced training."""
    # Model architecture
    vocab_size: int = 50000
    max_length: int = 512
    hidden_size: int = 768
    num_layers: int = 12
    num_heads: int = 12
    dropout: float = 0.1
    
    # Training parameters
    batch_size: int = 32
    effective_batch_size: int = 128  # Target effective batch size
    gradient_accumulation_steps: int = 4  # Steps to accumulate gradients
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    num_epochs: int = 100
    warmup_steps: int = 1000
    max_grad_norm: float = 1.0
    
    # Mixed precision
    use_mixed_precision: bool = True
    fp16: bool = True
    bf16: bool = False
    
    # LoRA configuration
    use_lora: bool = True
    lora_rank: int = 16
    lora_alpha: float = 32.0
    lora_dropout: float = 0.1
    
    # P-tuning configuration
    use_ptuning: bool = False
    ptuning_prefix_length: int = 10
    ptuning_hidden_size: int = 256
    
    # Data loading
    num_workers: int = 4
    pin_memory: bool = True
    persistent_workers: bool = True
    
    # Performance
    use_compile: bool = True
    profile_memory: bool = True
    log_every: int = 100
    save_every: int = 1000


class GradientAccumulator:
    """Handles gradient accumulation for large effective batch sizes."""
    
    def __init__(self, model: nn.Module, config: TrainingConfig):
        self.model = model
        self.config = config
        self.accumulation_steps = config.gradient_accumulation_steps
        self.current_step = 0
        
        # Validate configuration
        if self.accumulation_steps < 1:
            raise ValueError("gradient_accumulation_steps must be >= 1")
        
        # Calculate actual batch size
        self.actual_batch_size = config.batch_size
        self.effective_batch_size = self.actual_batch_size * self.accumulation_steps
        
        logger.info(f"Gradient accumulation: {self.actual_batch_size} * {self.accumulation_steps} = {self.effective_batch_size}")
    
    def should_step(self) -> bool:
        """Check if optimizer step should be performed."""
        return (self.current_step + 1) % self.accumulation_steps == 0
    
    def step(self, optimizer: optim.Optimizer, scaler: Optional[GradScaler] = None):
        """Perform optimizer step if accumulation is complete."""
        if self.should_step():
            if scaler is not None:
                scaler.step(optimizer)
                scaler.update()
            else:
                optimizer.step()
            optimizer.zero_grad()
            self.current_step = 0
        else:
            self.current_step += 1
    
    def get_effective_batch_size(self) -> int:
        """Get the effective batch size."""
        return self.effective_batch_size


class AdvancedTrainer:
    """Advanced trainer with gradient accumulation and mixed precision."""
    
    def __init__(self, model: nn.Module, config: TrainingConfig):
        self.model = model
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Move model to device
        self.model.to(self.device)
        
        # Compile model if enabled
        if config.use_compile and hasattr(torch, 'compile'):
            try:
                self.model = torch.compile(self.model)
                logger.info("Model compiled successfully")
            except Exception as e:
                logger.warning(f"Model compilation failed: {e}")
        
        # Initialize components
        self._setup_optimizer()
        self._setup_scheduler()
        self._setup_mixed_precision()
        self._setup_gradient_accumulator()
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Training state
        self.global_step = 0
        self.epoch = 0
        self.best_loss = float('inf')
        
        logger.info(f"Advanced trainer initialized on {self.device}")
    
    def _setup_optimizer(self):
        """Setup optimizer with weight decay."""
        # Separate parameters for weight decay
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {
                'params': [p for n, p in self.model.named_parameters() 
                          if not any(nd in n for nd in no_decay)],
                'weight_decay': self.config.weight_decay,
            },
            {
                'params': [p for n, p in self.model.named_parameters() 
                          if any(nd in n for nd in no_decay)],
                'weight_decay': 0.0,
            }
        ]
        
        self.optimizer = optim.AdamW(
            optimizer_grouped_parameters,
            lr=self.config.learning_rate,
            betas=(0.9, 0.999),
            eps=1e-8
        )
    
    def _setup_scheduler(self):
        """Setup learning rate scheduler with warmup."""
        self.scheduler = optim.lr_scheduler.OneCycleLR(
            self.optimizer,
            max_lr=self.config.learning_rate,
            total_steps=self.config.num_epochs * self.config.gradient_accumulation_steps,
            pct_start=self.config.warmup_steps / (self.config.num_epochs * self.config.gradient_accumulation_steps),
            anneal_strategy='cos'
        )
    
    def _setup_mixed_precision(self):
        """Setup mixed precision training."""
        self.use_mixed_precision = self.config.use_mixed_precision and self.device.type == 'cuda'
        
        if self.use_mixed_precision:
            if self.config.fp16:
                self.scaler = GradScaler()
                self.dtype = torch.float16
                logger.info("Using FP16 mixed precision")
            elif self.config.bf16:
                self.scaler = None
                self.dtype = torch.bfloat16
                logger.info("Using BF16 mixed precision")
            else:
                self.scaler = None
                self.dtype = torch.float32
                logger.info("Using FP32 precision")
        else:
            self.scaler = None
            self.dtype = torch.float32
            logger.info("Using FP32 precision")
    
    def _setup_gradient_accumulator(self):
        """Setup gradient accumulator."""
        self.gradient_accumulator = GradientAccumulator(self.model, self.config)
    
    def train_step(self, batch: Tuple[torch.Tensor, torch.Tensor]) -> Dict[str, float]:
        """Single training step with gradient accumulation."""
        self.model.train()
        
        # Unpack batch
        input_ids, labels = batch
        input_ids = input_ids.to(self.device)
        labels = labels.to(self.device)
        
        # Mixed precision forward pass
        with autocast(enabled=self.use_mixed_precision, dtype=self.dtype):
            outputs = self.model(input_ids)
            loss = nn.CrossEntropyLoss()(outputs.view(-1, outputs.size(-1)), labels.view(-1))
            
            # Scale loss for gradient accumulation
            loss = loss / self.config.gradient_accumulation_steps
        
        # Backward pass
        if self.scaler is not None:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()
        
        # Gradient accumulation step
        self.gradient_accumulator.step(self.optimizer, self.scaler)
        
        # Update learning rate
        if self.gradient_accumulator.should_step():
            self.scheduler.step()
            self.global_step += 1
        
        # Performance monitoring
        self.performance_monitor.record_step(loss.item() * self.config.gradient_accumulation_steps)
        
        return {
            "loss": loss.item() * self.config.gradient_accumulation_steps,
            "lr": self.optimizer.param_groups[0]['lr'],
            "effective_batch_size": self.gradient_accumulator.get_effective_batch_size()
        }
    
    def train(self, dataloader: DataLoader, num_epochs: Optional[int] = None) -> Dict[str, List[float]]:
        """Training loop with gradient accumulation."""
        if num_epochs is None:
            num_epochs = self.config.num_epochs
        
        all_losses = []
        all_learning_rates = []
        
        logger.info(f"Starting training for {num_epochs} epochs")
        logger.info(f"Effective batch size: {self.gradient_accumulator.get_effective_batch_size()}")
        
        for epoch in range(num_epochs):
            self.epoch = epoch
            epoch_losses = []
            epoch_start_time = time.time()
            
            # Training loop
            progress_bar = tqdm(dataloader, desc=f"Epoch {epoch + 1}/{num_epochs}")
            
            for batch_idx, batch in enumerate(progress_bar):
                try:
                    step_metrics = self.train_step(batch)
                    epoch_losses.append(step_metrics["loss"])
                    
                    # Update progress bar
                    avg_loss = np.mean(epoch_losses[-100:]) if len(epoch_losses) > 0 else 0
                    progress_bar.set_postfix({
                        'loss': f'{avg_loss:.4f}',
                        'lr': f'{step_metrics["lr"]:.2e}',
                        'step': self.global_step
                    })
                    
                    # Logging
                    if self.global_step % self.config.log_every == 0:
                        self._log_training_metrics(step_metrics, epoch, batch_idx)
                    
                    # Save checkpoint
                    if self.global_step % self.config.save_every == 0:
                        self._save_checkpoint(f"checkpoint_step_{self.global_step}.pt")
                    
                    # Performance monitoring
                    if self.config.profile_memory and self.global_step % 100 == 0:
                        self.performance_monitor.log_memory_usage()
                    
                except Exception as e:
                    logger.error(f"Error in training step: {e}")
                    continue
            
            # Epoch completion
            epoch_time = time.time() - epoch_start_time
            avg_epoch_loss = np.mean(epoch_losses) if epoch_losses else 0
            
            all_losses.append(avg_epoch_loss)
            all_learning_rates.append(self.optimizer.param_groups[0]['lr'])
            
            logger.info(f"Epoch {epoch + 1} completed in {epoch_time:.2f}s")
            logger.info(f"Average loss: {avg_epoch_loss:.4f}")
            logger.info(f"Learning rate: {self.optimizer.param_groups[0]['lr']:.2e}")
            
            # Save best model
            if avg_epoch_loss < self.best_loss:
                self.best_loss = avg_epoch_loss
                self._save_checkpoint("best_model.pt")
                logger.info(f"New best model saved with loss: {self.best_loss:.4f}")
            
            # Performance summary
            self.performance_monitor.log_epoch_summary(epoch + 1)
            
            # Memory cleanup
            if self.device.type == 'cuda':
                torch.cuda.empty_cache()
                gc.collect()
        
        logger.info("Training completed!")
        return {
            "losses": all_losses,
            "learning_rates": all_learning_rates,
            "best_loss": self.best_loss
        }
    
    def _log_training_metrics(self, metrics: Dict[str, float], epoch: int, batch_idx: int):
        """Log training metrics."""
        logger.info(
            f"Epoch {epoch + 1}, Batch {batch_idx}, Step {self.global_step}, "
            f"Loss: {metrics['loss']:.4f}, LR: {metrics['lr']:.2e}"
        )
    
    def _save_checkpoint(self, filename: str):
        """Save model checkpoint."""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'config': self.config,
            'global_step': self.global_step,
            'epoch': self.epoch,
            'best_loss': self.best_loss,
            'gradient_accumulator_state': {
                'current_step': self.gradient_accumulator.current_step
            }
        }
        
        torch.save(checkpoint, filename)
        logger.info(f"Checkpoint saved: {filename}")
    
    def load_checkpoint(self, filename: str):
        """Load model checkpoint."""
        checkpoint = torch.load(filename, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        self.global_step = checkpoint['global_step']
        self.epoch = checkpoint['epoch']
        self.best_loss = checkpoint['best_loss']
        
        # Restore gradient accumulator state
        if 'gradient_accumulator_state' in checkpoint:
            self.gradient_accumulator.current_step = checkpoint['gradient_accumulator_state']['current_step']
        
        logger.info(f"Checkpoint loaded: {filename}")
        logger.info(f"Resuming from step {self.global_step}, epoch {self.epoch}")


class TrainingPipeline:
    """Complete training pipeline integrating all components."""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.tokenizer = None
        self.data_loader = None
        self.model = None
        self.trainer = None
        
        logger.info("Initializing training pipeline...")
    
    def setup_components(self):
        """Setup all training components."""
        # Initialize tokenizer
        self.tokenizer = TextTokenizer(
            vocab_size=self.config.vocab_size,
            max_length=self.config.max_length
        )
        
        # Initialize data loader
        self.data_loader = TextDataLoader(
            tokenizer=self.tokenizer,
            batch_size=self.config.batch_size,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
            persistent_workers=self.config.persistent_workers
        )
        
        # Initialize model
        self.model = AdvancedTransformerModel(
            vocab_size=self.config.vocab_size,
            max_length=self.config.max_length,
            hidden_size=self.config.hidden_size,
            num_layers=self.config.num_layers,
            num_heads=self.config.num_heads,
            dropout=self.config.dropout
        )
        
        # Apply LoRA if enabled
        if self.config.use_lora:
            lora_config = LoRAConfig(
                rank=self.config.lora_rank,
                alpha=self.config.lora_alpha,
                dropout=self.config.lora_dropout
            )
            self.model = LoRAModel(self.model, lora_config)
            logger.info("LoRA applied to model")
        
        # Apply P-tuning if enabled
        if self.config.use_ptuning:
            ptuning_config = PTuningConfig(
                prefix_length=self.config.ptuning_prefix_length,
                hidden_size=self.config.ptuning_hidden_size
            )
            self.model = PTuningModel(self.model, ptuning_config)
            logger.info("P-tuning applied to model")
        
        # Initialize trainer
        self.trainer = AdvancedTrainer(self.model, self.config)
        
        logger.info("All components initialized successfully")
    
    def train(self, data_path: str, num_epochs: Optional[int] = None) -> Dict[str, List[float]]:
        """Run complete training pipeline."""
        if not all([self.tokenizer, self.data_loader, self.model, self.trainer]):
            raise RuntimeError("Components not initialized. Call setup_components() first.")
        
        # Load and prepare data
        logger.info(f"Loading data from: {data_path}")
        train_dataloader = self.data_loader.create_dataloader(data_path)
        
        # Start training
        logger.info("Starting training...")
        results = self.trainer.train(train_dataloader, num_epochs)
        
        return results
    
    def save_pipeline(self, save_dir: str):
        """Save complete pipeline."""
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        # Save tokenizer
        self.tokenizer.save(save_dir + "/tokenizer")
        
        # Save model
        torch.save(self.model.state_dict(), save_dir + "/model.pt")
        
        # Save trainer checkpoint
        self.trainer._save_checkpoint(save_dir + "/trainer_checkpoint.pt")
        
        # Save configuration
        import json
        with open(save_dir + "/config.json", 'w') as f:
            json.dump(self.config.__dict__, f, indent=2)
        
        logger.info(f"Pipeline saved to: {save_dir}")


# Example usage
if __name__ == "__main__":
    # Configuration
    config = TrainingConfig(
        batch_size=16,
        effective_batch_size=128,
        gradient_accumulation_steps=8,
        use_mixed_precision=True,
        use_lora=True,
        use_compile=True
    )
    
    # Create pipeline
    pipeline = TrainingPipeline(config)
    pipeline.setup_components()
    
    # Train (example data path)
    # results = pipeline.train("path/to/training/data.txt")
    
    print("Advanced training system with gradient accumulation ready!")

