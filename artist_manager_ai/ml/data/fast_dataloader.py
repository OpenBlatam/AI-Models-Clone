"""
Fast DataLoader
===============

Optimized DataLoader configurations for speed.
"""

import torch
from torch.utils.data import DataLoader
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def create_fast_dataloader(
    dataset: torch.utils.data.Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: Optional[int] = None,
    pin_memory: Optional[bool] = None,
    prefetch_factor: int = 2,
    persistent_workers: bool = True,
    drop_last: bool = False
) -> DataLoader:
    """
    Create optimized DataLoader for speed.
    
    Args:
        dataset: PyTorch dataset
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of workers (auto-detect if None)
        pin_memory: Pin memory (auto-detect if None)
        prefetch_factor: Prefetch factor
        persistent_workers: Keep workers alive
        drop_last: Drop last incomplete batch
    
    Returns:
        Optimized DataLoader
    """
    # Auto-detect optimal settings
    if num_workers is None:
        num_workers = min(4, torch.get_num_threads())
    
    if pin_memory is None:
        pin_memory = torch.cuda.is_available()
    
    # Create DataLoader with optimized settings
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        prefetch_factor=prefetch_factor if num_workers > 0 else None,
        persistent_workers=persistent_workers if num_workers > 0 else False,
        drop_last=drop_last,
        pin_memory_device="cuda" if pin_memory and torch.cuda.is_available() else None
    )
    
    logger.info(
        f"Fast DataLoader created: "
        f"workers={num_workers}, pin_memory={pin_memory}, "
        f"prefetch={prefetch_factor}"
    )
    
    return dataloader


def optimize_existing_dataloader(
    dataloader: DataLoader,
    num_workers: Optional[int] = None,
    pin_memory: Optional[bool] = None
) -> DataLoader:
    """
    Optimize existing DataLoader.
    
    Args:
        dataloader: Existing DataLoader
        num_workers: New number of workers
        pin_memory: New pin_memory setting
    
    Returns:
        Optimized DataLoader
    """
    return create_fast_dataloader(
        dataset=dataloader.dataset,
        batch_size=dataloader.batch_size,
        shuffle=dataloader.shuffle,
        num_workers=num_workers or dataloader.num_workers,
        pin_memory=pin_memory if pin_memory is not None else dataloader.pin_memory,
        drop_last=dataloader.drop_last
    )




