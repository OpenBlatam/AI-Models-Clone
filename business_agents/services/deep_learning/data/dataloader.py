"""
DataLoader Utilities - Efficient Data Loading
============================================

Utilities for creating efficient DataLoaders with best practices.
"""

import torch
from torch.utils.data import DataLoader, Dataset, random_split
from typing import Optional, Tuple, Dict, Any
import logging

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


def create_dataloader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    pin_memory: bool = True,
    persistent_workers: bool = True,
    prefetch_factor: int = 2,
    drop_last: bool = False,
    **kwargs
) -> DataLoader:
    """
    Create an efficient DataLoader with best practices.
    
    Args:
        dataset: PyTorch dataset
        batch_size: Batch size
        shuffle: Whether to shuffle data
        num_workers: Number of worker processes for data loading
        pin_memory: Pin memory for faster GPU transfer
        persistent_workers: Keep workers alive between epochs
        prefetch_factor: Number of batches prefetched per worker
        drop_last: Drop last incomplete batch
        **kwargs: Additional DataLoader arguments
    
    Returns:
        DataLoader instance
    
    Example:
        >>> dataset = SimpleDataset(data, labels)
        >>> loader = create_dataloader(dataset, batch_size=32, num_workers=4)
    """
    # Determine if CUDA is available for pin_memory
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
        **kwargs
    )
    
    logger.debug(
        f"Created DataLoader: batch_size={batch_size}, "
        f"num_workers={num_workers}, pin_memory={pin_memory}"
    )
    
    return dataloader


def split_dataset(
    dataset: Dataset,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Tuple[Dataset, Dataset, Dataset]:
    """
    Split dataset into train/validation/test sets.
    
    Args:
        dataset: Full dataset
        train_ratio: Proportion for training set
        val_ratio: Proportion for validation set
        test_ratio: Proportion for test set
        seed: Random seed for reproducibility
    
    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset)
    
    Example:
        >>> train, val, test = split_dataset(full_dataset, 0.7, 0.15, 0.15)
    """
    # Validate ratios
    total_ratio = train_ratio + val_ratio + test_ratio
    if abs(total_ratio - 1.0) > 1e-6:
        raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")
    
    # Calculate sizes
    total_size = len(dataset)
    train_size = int(train_ratio * total_size)
    val_size = int(val_ratio * total_size)
    test_size = total_size - train_size - val_size
    
    # Split dataset
    train_dataset, val_dataset, test_dataset = random_split(
        dataset,
        [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(seed)
    )
    
    logger.info(
        f"Dataset split: train={len(train_dataset)}, "
        f"val={len(val_dataset)}, test={len(test_dataset)}"
    )
    
    return train_dataset, val_dataset, test_dataset


def create_dataloaders(
    train_dataset: Dataset,
    val_dataset: Optional[Dataset] = None,
    test_dataset: Optional[Dataset] = None,
    batch_size: int = 32,
    num_workers: int = 4,
    pin_memory: bool = True,
    **kwargs
) -> Dict[str, DataLoader]:
    """
    Create multiple DataLoaders for train/val/test.
    
    Args:
        train_dataset: Training dataset
        val_dataset: Validation dataset (optional)
        test_dataset: Test dataset (optional)
        batch_size: Batch size
        num_workers: Number of workers
        pin_memory: Pin memory
        **kwargs: Additional DataLoader arguments
    
    Returns:
        Dictionary with 'train', 'val', 'test' DataLoaders
    """
    loaders = {}
    
    # Training loader (shuffled)
    loaders['train'] = create_dataloader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        **kwargs
    )
    
    # Validation loader (not shuffled)
    if val_dataset is not None:
        loaders['val'] = create_dataloader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            **kwargs
        )
    
    # Test loader (not shuffled)
    if test_dataset is not None:
        loaders['test'] = create_dataloader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            **kwargs
        )
    
    return loaders



