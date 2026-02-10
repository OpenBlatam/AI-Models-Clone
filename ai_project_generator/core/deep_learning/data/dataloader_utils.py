"""
DataLoader Utilities - Functional Data Loading Helpers
=======================================================

Functional programming patterns for creating and configuring DataLoaders.
"""

import logging
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np

from .datasets import get_default_collate_fn

logger = logging.getLogger(__name__)


def create_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    pin_memory: bool = True,
    drop_last: bool = False,
    prefetch_factor: int = 2,
    collate_fn: Optional[callable] = None
) -> DataLoader:
    """
    Create a DataLoader with optimal settings for GPU training.
    
    Args:
        dataset: PyTorch Dataset
        batch_size: Batch size
        shuffle: Whether to shuffle data
        num_workers: Number of worker processes
        pin_memory: Pin memory for faster GPU transfer
        drop_last: Drop last incomplete batch
        prefetch_factor: Number of batches to prefetch
        collate_fn: Custom collate function
        
    Returns:
        Configured DataLoader
    """
    if collate_fn is None:
        collate_fn = get_default_collate_fn()
    
    # Optimize num_workers based on system
    if num_workers == -1:
        num_workers = min(8, torch.get_num_threads())
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory and torch.cuda.is_available(),
        drop_last=drop_last,
        prefetch_factor=prefetch_factor if num_workers > 0 else None,
        collate_fn=collate_fn,
        persistent_workers=num_workers > 0
    )
    
    logger.info(
        f"Created DataLoader: batch_size={batch_size}, "
        f"num_workers={num_workers}, pin_memory={pin_memory}"
    )
    
    return dataloader


def train_val_test_split(
    dataset: Dataset,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: Optional[int] = 42
) -> Tuple[Dataset, Dataset, Dataset]:
    """
    Split dataset into train, validation, and test sets.
    
    Args:
        dataset: Full dataset
        train_ratio: Proportion for training set
        val_ratio: Proportion for validation set
        test_ratio: Proportion for test set
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset)
        
    Raises:
        ValueError: If ratios don't sum to 1.0
    """
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError("Ratios must sum to 1.0")
    
    if seed is not None:
        generator = torch.Generator().manual_seed(seed)
    else:
        generator = None
    
    total_size = len(dataset)
    train_size = int(train_ratio * total_size)
    val_size = int(val_ratio * total_size)
    test_size = total_size - train_size - val_size
    
    train_dataset, val_dataset, test_dataset = random_split(
        dataset,
        [train_size, val_size, test_size],
        generator=generator
    )
    
    logger.info(
        f"Dataset split: train={len(train_dataset)}, "
        f"val={len(val_dataset)}, test={len(test_dataset)}"
    )
    
    return train_dataset, val_dataset, test_dataset


def get_data_stats(dataloader: DataLoader) -> Dict[str, Any]:
    """
    Compute statistics about the dataset.
    
    Args:
        dataloader: DataLoader to analyze
        
    Returns:
        Dictionary with dataset statistics
    """
    stats = {
        'num_batches': len(dataloader),
        'batch_size': dataloader.batch_size,
        'num_samples': len(dataloader.dataset),
        'num_workers': dataloader.num_workers,
        'pin_memory': dataloader.pin_memory,
    }
    
    # Try to get sample to determine shape
    try:
        sample = next(iter(dataloader))
        if isinstance(sample, dict):
            stats['sample_keys'] = list(sample.keys())
            for key, value in sample.items():
                if isinstance(value, torch.Tensor):
                    stats[f'{key}_shape'] = list(value.shape)
        elif isinstance(sample, (tuple, list)):
            stats['num_outputs'] = len(sample)
            for i, item in enumerate(sample):
                if isinstance(item, torch.Tensor):
                    stats[f'output_{i}_shape'] = list(item.shape)
    except Exception as e:
        logger.warning(f"Could not get sample stats: {e}")
    
    return stats



