"""
Optimized DataLoader - Performance Optimized
============================================

Optimized DataLoader with advanced performance improvements.
"""

import torch
from torch.utils.data import DataLoader, Dataset
from typing import Optional, Dict, Any
import logging
import os

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


def create_optimized_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: Optional[int] = None,
    pin_memory: bool = True,
    persistent_workers: bool = True,
    prefetch_factor: int = 4,
    drop_last: bool = False,
    **kwargs
) -> DataLoader:
    """
    Create an optimized DataLoader with best performance settings.
    
    Args:
        dataset: PyTorch dataset
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of workers (auto-detected if None)
        pin_memory: Pin memory for faster GPU transfer
        persistent_workers: Keep workers alive between epochs
        prefetch_factor: Prefetch factor (higher = more memory, faster)
        drop_last: Drop last incomplete batch
        **kwargs: Additional DataLoader arguments
    
    Returns:
        Optimized DataLoader
    """
    # Auto-detect optimal num_workers
    if num_workers is None:
        if torch.cuda.is_available():
            # Use 2-4 workers per GPU
            num_workers = min(4, torch.cuda.device_count() * 2)
        else:
            num_workers = min(4, os.cpu_count() or 1)
    
    # Optimize pin_memory based on device
    if not torch.cuda.is_available():
        pin_memory = False
        logger.debug("CUDA not available, disabling pin_memory")
    
    # Create DataLoader with optimized settings
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers and num_workers > 0,
        prefetch_factor=prefetch_factor if num_workers > 0 else None,
        drop_last=drop_last,
        # Additional optimizations
        generator=torch.Generator() if shuffle else None,
        **kwargs
    )
    
    logger.info(
        f"✅ Optimized DataLoader created: "
        f"batch_size={batch_size}, num_workers={num_workers}, "
        f"pin_memory={pin_memory}, prefetch_factor={prefetch_factor}"
    )
    
    return dataloader


def optimize_existing_dataloader(
    dataloader: DataLoader,
    **overrides
) -> Dict[str, Any]:
    """
    Get optimization recommendations for existing DataLoader.
    
    Args:
        dataloader: Existing DataLoader
        **overrides: Override recommendations
    
    Returns:
        Dictionary with optimization recommendations
    """
    recommendations = {
        "num_workers": dataloader.num_workers or 4,
        "pin_memory": dataloader.pin_memory,
        "prefetch_factor": getattr(dataloader, 'prefetch_factor', 2),
        "persistent_workers": getattr(dataloader, 'persistent_workers', False),
    }
    
    # Update with overrides
    recommendations.update(overrides)
    
    # Auto-optimize based on system
    if torch.cuda.is_available():
        recommendations["pin_memory"] = True
        recommendations["num_workers"] = min(4, torch.cuda.device_count() * 2)
        recommendations["prefetch_factor"] = 4
        recommendations["persistent_workers"] = True
    
    logger.info(f"DataLoader optimization recommendations: {recommendations}")
    
    return recommendations



