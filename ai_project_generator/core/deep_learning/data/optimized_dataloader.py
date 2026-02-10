"""
Optimized DataLoader - Performance Optimizations
================================================

Optimized DataLoader configurations and utilities for maximum performance:
- Optimal worker configuration
- Memory pinning
- Prefetch optimization
- Batch size optimization
"""

import logging
from typing import Optional, Dict, Any
import torch
from torch.utils.data import DataLoader, Dataset
import os

logger = logging.getLogger(__name__)


def get_optimal_num_workers(
    dataset_size: int,
    batch_size: int,
    min_workers: int = 2,
    max_workers: int = 8
) -> int:
    """
    Calculate optimal number of workers for DataLoader.
    
    Args:
        dataset_size: Size of dataset
        batch_size: Batch size
        min_workers: Minimum workers
        max_workers: Maximum workers
        
    Returns:
        Optimal number of workers
    """
    # Get CPU count
    cpu_count = os.cpu_count() or 4
    
    # Calculate based on dataset and batch size
    if dataset_size < 1000:
        num_workers = min(2, cpu_count)
    elif dataset_size < 10000:
        num_workers = min(4, cpu_count)
    else:
        # More workers for larger datasets
        num_workers = min(max_workers, cpu_count)
    
    # Ensure within bounds
    num_workers = max(min_workers, min(num_workers, max_workers))
    
    logger.info(f"Optimal num_workers: {num_workers} (dataset_size={dataset_size}, cpu_count={cpu_count})")
    return num_workers


def get_optimal_prefetch_factor(
    num_workers: int,
    batch_size: int
) -> int:
    """
    Calculate optimal prefetch factor.
    
    Args:
        num_workers: Number of workers
        batch_size: Batch size
        
    Returns:
        Optimal prefetch factor
    """
    if num_workers == 0:
        return None
    
    # Prefetch more for larger batch sizes
    if batch_size >= 64:
        prefetch = 4
    elif batch_size >= 32:
        prefetch = 3
    else:
        prefetch = 2
    
    return prefetch


def create_optimized_dataloader(
    dataset: Dataset,
    batch_size: int,
    shuffle: bool = True,
    pin_memory: Optional[bool] = None,
    drop_last: bool = False,
    persistent_workers: Optional[bool] = None,
    **kwargs
) -> DataLoader:
    """
    Create optimized DataLoader with automatic configuration.
    
    Args:
        dataset: PyTorch Dataset
        batch_size: Batch size
        shuffle: Whether to shuffle
        pin_memory: Pin memory (auto-detected if None)
        drop_last: Drop last incomplete batch
        persistent_workers: Keep workers alive (auto-detected if None)
        **kwargs: Additional DataLoader arguments
        
    Returns:
        Optimized DataLoader
    """
    # Auto-detect pin_memory
    if pin_memory is None:
        pin_memory = torch.cuda.is_available()
    
    # Auto-detect persistent_workers
    if persistent_workers is None:
        persistent_workers = True  # Better for performance
    
    # Calculate optimal workers
    num_workers = kwargs.pop('num_workers', None)
    if num_workers is None:
        num_workers = get_optimal_num_workers(len(dataset), batch_size)
    
    # Calculate optimal prefetch
    prefetch_factor = kwargs.pop('prefetch_factor', None)
    if prefetch_factor is None and num_workers > 0:
        prefetch_factor = get_optimal_prefetch_factor(num_workers, batch_size)
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=drop_last,
        persistent_workers=persistent_workers if num_workers > 0 else False,
        prefetch_factor=prefetch_factor,
        **kwargs
    )
    
    logger.info(
        f"Created optimized DataLoader: "
        f"batch_size={batch_size}, num_workers={num_workers}, "
        f"pin_memory={pin_memory}, prefetch_factor={prefetch_factor}"
    )
    
    return dataloader


def benchmark_dataloader(
    dataloader: DataLoader,
    num_batches: int = 10
) -> Dict[str, float]:
    """
    Benchmark DataLoader performance.
    
    Args:
        dataloader: DataLoader to benchmark
        num_batches: Number of batches to test
        
    Returns:
        Dictionary with performance metrics
    """
    import time
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Warmup
    for i, batch in enumerate(dataloader):
        if i >= 2:
            break
        if isinstance(batch, dict):
            batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v
                    for k, v in batch.items()}
        elif isinstance(batch, (tuple, list)):
            batch = tuple(v.to(device) if isinstance(v, torch.Tensor) else v
                        for v in batch)
    
    # Benchmark
    start_time = time.time()
    batch_times = []
    
    for i, batch in enumerate(dataloader):
        if i >= num_batches:
            break
        
        batch_start = time.time()
        
        # Move to device
        if isinstance(batch, dict):
            batch = {k: v.to(device) if isinstance(v, torch.Tensor) else v
                    for k, v in batch.items()}
        elif isinstance(batch, (tuple, list)):
            batch = tuple(v.to(device) if isinstance(v, torch.Tensor) else v
                        for v in batch)
        else:
            batch = batch.to(device)
        
        if device.type == 'cuda':
            torch.cuda.synchronize()
        
        batch_time = time.time() - batch_start
        batch_times.append(batch_time)
    
    total_time = time.time() - start_time
    
    results = {
        'total_time': total_time,
        'avg_batch_time': sum(batch_times) / len(batch_times),
        'min_batch_time': min(batch_times),
        'max_batch_time': max(batch_times),
        'batches_per_second': num_batches / total_time,
        'samples_per_second': (num_batches * dataloader.batch_size) / total_time
    }
    
    logger.info(f"DataLoader benchmark results: {results}")
    return results



