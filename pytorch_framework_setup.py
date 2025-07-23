#!/usr/bin/env python3
"""
PyTorch Framework Setup - Primary Deep Learning Framework

Centralized configuration and setup for PyTorch as the primary deep learning framework.
This module provides:
- PyTorch environment configuration
- GPU optimization setup
- Framework initialization
- Version compatibility checks
- Performance monitoring
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import autocast, GradScaler
from torch.utils.data import DataLoader
import torch.distributed as dist
from torch.nn.parallel import DataParallel, DistributedDataParallel
import numpy as np
import logging
import os
import sys
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import time
import warnings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)


@dataclass
class PyTorchConfig:
    """PyTorch framework configuration.
    
    Attributes:
        device: Primary device for computation
        use_mixed_precision: Enable mixed precision training
        use_distributed: Enable distributed training
        num_workers: Number of data loader workers
        pin_memory: Pin memory for faster GPU transfer
        deterministic: Enable deterministic behavior
        benchmark: Enable cuDNN benchmark mode
        memory_format: Memory format for tensors
        gradient_clip_norm: Gradient clipping norm
        compile_model: Use torch.compile for optimization
        enable_amp: Enable automatic mixed precision
    """
    
    device: str = "auto"  # "auto", "cuda", "cpu", "mps"
    use_mixed_precision: bool = True
    use_distributed: bool = False
    num_workers: int = 4
    pin_memory: bool = True
    deterministic: bool = False
    benchmark: bool = True
    memory_format: str = "channels_last"  # "channels_last", "contiguous_format"
    gradient_clip_norm: float = 1.0
    compile_model: bool = True
    enable_amp: bool = True
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"


class PyTorchFramework:
    """PyTorch framework manager and configuration.
    
    This class manages PyTorch setup, configuration, and provides
    utilities for optimal deep learning performance.
    """
    
    def __init__(self, config: PyTorchConfig):
        """Initialize PyTorch framework.
        
        Args:
            config: PyTorch configuration
        """
        self.config = config
        self.device = self._setup_device()
        self.scaler = None
        self._setup_framework()
        
        logger.info(f"PyTorch Framework initialized on device: {self.device}")
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU count: {torch.cuda.device_count()}")
    
    def _setup_device(self) -> torch.device:
        """Setup and configure device.
        
        Returns:
            Configured torch device
        """
        if self.config.device == "cuda" and torch.cuda.is_available():
            device = torch.device("cuda")
            # Set memory fraction if needed
            torch.cuda.set_per_process_memory_fraction(0.9)
        elif self.config.device == "mps" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device("mps")
        else:
            device = torch.device("cpu")
        
        return device
    
    def _setup_framework(self) -> None:
        """Setup PyTorch framework configuration."""
        # Set deterministic behavior
        if self.config.deterministic:
            torch.manual_seed(42)
            torch.cuda.manual_seed_all(42)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
        else:
            torch.backends.cudnn.benchmark = self.config.benchmark
        
        # Setup mixed precision
        if self.config.enable_amp and self.device.type == "cuda":
            self.scaler = GradScaler()
        
        # Setup distributed training
        if self.config.use_distributed:
            self._setup_distributed()
    
    def _setup_distributed(self) -> None:
        """Setup distributed training."""
        if not dist.is_available():
            logger.warning("Distributed training not available")
            return
        
        # Initialize process group
        dist.init_process_group(backend='nccl')
        self.device = torch.device(f"cuda:{dist.get_rank()}")
        torch.cuda.set_device(self.device)
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information.
        
        Returns:
            Dictionary with device information
        """
        info = {
            "device": str(self.device),
            "device_type": self.device.type,
            "pytorch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
        
        if torch.cuda.is_available():
            info.update({
                "current_gpu": torch.cuda.current_device(),
                "gpu_name": torch.cuda.get_device_name(),
                "gpu_memory_total": torch.cuda.get_device_properties(0).total_memory,
                "gpu_memory_allocated": torch.cuda.memory_allocated(),
                "gpu_memory_cached": torch.cuda.memory_reserved(),
            })
        
        return info
    
    def optimize_model(self, model: nn.Module) -> nn.Module:
        """Optimize model for performance.
        
        Args:
            model: PyTorch model to optimize
            
        Returns:
            Optimized model
        """
        # Move to device
        model = model.to(self.device)
        
        # Set memory format
        if self.config.memory_format == "channels_last" and hasattr(model, 'to'):
            model = model.to(memory_format=torch.channels_last)
        
        # Compile model if available
        if self.config.compile_model and hasattr(torch, 'compile'):
            try:
                model = torch.compile(model)
                logger.info("Model compiled successfully")
            except Exception as e:
                logger.warning(f"Model compilation failed: {e}")
        
        # Wrap for distributed training
        if self.config.use_distributed and dist.is_available():
            model = DistributedDataParallel(model, device_ids=[self.device])
        elif torch.cuda.device_count() > 1:
            model = DataParallel(model)
        
        return model
    
    def create_dataloader(
        self,
        dataset: torch.utils.data.Dataset,
        batch_size: int,
        shuffle: bool = True,
        **kwargs
    ) -> DataLoader:
        """Create optimized DataLoader.
        
        Args:
            dataset: PyTorch dataset
            batch_size: Batch size
            shuffle: Whether to shuffle data
            **kwargs: Additional DataLoader arguments
            
        Returns:
            Configured DataLoader
        """
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
            **kwargs
        )
    
    def create_optimizer(
        self,
        model: nn.Module,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        optimizer_type: str = "adam"
    ) -> optim.Optimizer:
        """Create optimized optimizer.
        
        Args:
            model: PyTorch model
            learning_rate: Learning rate
            weight_decay: Weight decay
            optimizer_type: Type of optimizer
            
        Returns:
            Configured optimizer
        """
        if optimizer_type.lower() == "adam":
            return optim.Adam(
                model.parameters(),
                lr=learning_rate,
                weight_decay=weight_decay
            )
        elif optimizer_type.lower() == "adamw":
            return optim.AdamW(
                model.parameters(),
                lr=learning_rate,
                weight_decay=weight_decay
            )
        elif optimizer_type.lower() == "sgd":
            return optim.SGD(
                model.parameters(),
                lr=learning_rate,
                weight_decay=weight_decay,
                momentum=0.9
            )
        else:
            raise ValueError(f"Unsupported optimizer type: {optimizer_type}")
    
    def train_step(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer,
        data: torch.Tensor,
        target: torch.Tensor,
        loss_fn: nn.Module,
        use_amp: bool = None
    ) -> Dict[str, float]:
        """Perform a single training step with optimization.
        
        Args:
            model: PyTorch model
            optimizer: Optimizer
            data: Input data
            target: Target labels
            loss_fn: Loss function
            use_amp: Whether to use automatic mixed precision
            
        Returns:
            Dictionary with training metrics
        """
        if use_amp is None:
            use_amp = self.config.enable_amp and self.device.type == "cuda"
        
        model.train()
        optimizer.zero_grad()
        
        # Move data to device
        data = data.to(self.device, non_blocking=True)
        target = target.to(self.device, non_blocking=True)
        
        # Set memory format
        if self.config.memory_format == "channels_last":
            data = data.to(memory_format=torch.channels_last)
        
        if use_amp and self.scaler is not None:
            with autocast():
                output = model(data)
                loss = loss_fn(output, target)
            
            self.scaler.scale(loss).backward()
            
            # Gradient clipping
            if self.config.gradient_clip_norm > 0:
                self.scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    self.config.gradient_clip_norm
                )
            
            self.scaler.step(optimizer)
            self.scaler.update()
        else:
            output = model(data)
            loss = loss_fn(output, target)
            loss.backward()
            
            # Gradient clipping
            if self.config.gradient_clip_norm > 0:
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    self.config.gradient_clip_norm
                )
            
            optimizer.step()
        
        return {
            "loss": loss.item(),
            "output_shape": output.shape,
            "target_shape": target.shape
        }
    
    def evaluate_step(
        self,
        model: nn.Module,
        data: torch.Tensor,
        target: torch.Tensor,
        loss_fn: nn.Module
    ) -> Dict[str, float]:
        """Perform a single evaluation step.
        
        Args:
            model: PyTorch model
            data: Input data
            target: Target labels
            loss_fn: Loss function
            
        Returns:
            Dictionary with evaluation metrics
        """
        model.eval()
        
        with torch.no_grad():
            # Move data to device
            data = data.to(self.device, non_blocking=True)
            target = target.to(self.device, non_blocking=True)
            
            # Set memory format
            if self.config.memory_format == "channels_last":
                data = data.to(memory_format=torch.channels_last)
            
            output = model(data)
            loss = loss_fn(output, target)
        
        return {
            "loss": loss.item(),
            "output_shape": output.shape,
            "target_shape": target.shape
        }
    
    def save_model(
        self,
        model: nn.Module,
        filepath: str,
        optimizer: Optional[optim.Optimizer] = None,
        epoch: int = 0,
        metrics: Optional[Dict[str, float]] = None
    ) -> None:
        """Save model checkpoint.
        
        Args:
            model: PyTorch model
            filepath: Path to save checkpoint
            optimizer: Optimizer state
            epoch: Current epoch
            metrics: Training metrics
        """
        checkpoint = {
            "model_state_dict": model.state_dict(),
            "epoch": epoch,
            "device": str(self.device),
            "config": self.config.__dict__,
        }
        
        if optimizer is not None:
            checkpoint["optimizer_state_dict"] = optimizer.state_dict()
        
        if metrics is not None:
            checkpoint["metrics"] = metrics
        
        torch.save(checkpoint, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(
        self,
        model: nn.Module,
        filepath: str,
        optimizer: Optional[optim.Optimizer] = None
    ) -> Dict[str, Any]:
        """Load model checkpoint.
        
        Args:
            model: PyTorch model
            filepath: Path to checkpoint
            optimizer: Optimizer to load state into
            
        Returns:
            Dictionary with loaded checkpoint data
        """
        checkpoint = torch.load(filepath, map_location=self.device)
        
        model.load_state_dict(checkpoint["model_state_dict"])
        model = model.to(self.device)
        
        if optimizer is not None and "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        
        logger.info(f"Model loaded from {filepath}")
        return checkpoint
    
    def clear_memory(self) -> None:
        """Clear GPU memory."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage.
        
        Returns:
            Dictionary with memory usage information
        """
        if torch.cuda.is_available():
            return {
                "allocated": torch.cuda.memory_allocated() / 1024**3,  # GB
                "reserved": torch.cuda.memory_reserved() / 1024**3,    # GB
                "max_allocated": torch.cuda.max_memory_allocated() / 1024**3,  # GB
                "max_reserved": torch.cuda.max_memory_reserved() / 1024**3,    # GB
            }
        return {"allocated": 0.0, "reserved": 0.0, "max_allocated": 0.0, "max_reserved": 0.0}


def setup_pytorch_framework(
    device: str = "auto",
    use_mixed_precision: bool = True,
    deterministic: bool = False
) -> PyTorchFramework:
    """Setup PyTorch framework with default configuration.
    
    Args:
        device: Device to use
        use_mixed_precision: Enable mixed precision
        deterministic: Enable deterministic behavior
        
    Returns:
        Configured PyTorch framework
    """
    config = PyTorchConfig(
        device=device,
        use_mixed_precision=use_mixed_precision,
        deterministic=deterministic
    )
    
    return PyTorchFramework(config)


def verify_pytorch_installation() -> Dict[str, Any]:
    """Verify PyTorch installation and capabilities.
    
    Returns:
        Dictionary with verification results
    """
    verification = {
        "pytorch_installed": True,
        "version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "mps_available": hasattr(torch.backends, 'mps') and torch.backends.mps.is_available(),
        "compile_available": hasattr(torch, 'compile'),
        "amp_available": True,  # Always available in recent PyTorch versions
    }
    
    if torch.cuda.is_available():
        verification.update({
            "gpu_count": torch.cuda.device_count(),
            "gpu_names": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
            "compute_capability": torch.cuda.get_device_capability(),
        })
    
    return verification


if __name__ == "__main__":
    # Example usage
    print("PyTorch Framework Setup")
    print("=" * 50)
    
    # Verify installation
    verification = verify_pytorch_installation()
    print("Installation Verification:")
    for key, value in verification.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # Setup framework
    framework = setup_pytorch_framework()
    
    # Get device info
    device_info = framework.get_device_info()
    print("Device Information:")
    for key, value in device_info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # Memory usage
    memory_usage = framework.get_memory_usage()
    print("Memory Usage:")
    for key, value in memory_usage.items():
        print(f"  {key}: {value:.2f} GB") 