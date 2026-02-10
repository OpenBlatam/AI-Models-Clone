"""
Base Data Loader Components

Separates data loading concerns into specialized components.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Iterator, List
import logging
import torch
from torch.utils.data import Dataset, DataLoader, Sampler

from ...interfaces.base import IDataLoader

logger = logging.getLogger(__name__)


class BaseDataset(Dataset):
    """
    Base dataset class with common functionality.
    """
    
    def __init__(self, transform: Optional[Any] = None):
        """
        Initialize dataset.
        
        Args:
            transform: Optional transform to apply
        """
        self.transform = transform
        self._data = []
    
    @abstractmethod
    def __len__(self) -> int:
        """Get dataset length."""
        pass
    
    @abstractmethod
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get item by index."""
        pass
    
    def apply_transform(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transform to item."""
        if self.transform is not None:
            return self.transform(item)
        return item


class BaseDataLoaderFactory(ABC):
    """
    Abstract base for data loader factories.
    """
    
    @abstractmethod
    def create_loader(
        self,
        dataset: Dataset,
        **kwargs
    ) -> DataLoader:
        """Create a data loader."""
        pass


class StandardDataLoaderFactory(BaseDataLoaderFactory):
    """
    Standard data loader factory with optimizations.
    """
    
    def create_loader(
        self,
        dataset: Dataset,
        batch_size: int = 32,
        shuffle: bool = True,
        num_workers: Optional[int] = None,
        pin_memory: bool = True,
        drop_last: bool = False,
        persistent_workers: bool = True,
        prefetch_factor: int = 2,
        **kwargs
    ) -> DataLoader:
        """
        Create optimized data loader.
        
        Args:
            dataset: Dataset to load from
            batch_size: Batch size
            shuffle: Whether to shuffle
            num_workers: Number of worker processes
            pin_memory: Pin memory for faster GPU transfer
            drop_last: Drop last incomplete batch
            persistent_workers: Keep workers alive
            prefetch_factor: Number of batches to prefetch
            **kwargs: Additional DataLoader arguments
            
        Returns:
            DataLoader instance
        """
        # Auto-configure num_workers
        if num_workers is None:
            num_workers = self._get_optimal_workers()
        
        # Pin memory only for CUDA
        pin_memory = pin_memory and torch.cuda.is_available()
        
        # Persistent workers only if num_workers > 0
        persistent_workers = persistent_workers and num_workers > 0
        
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=pin_memory,
            drop_last=drop_last,
            persistent_workers=persistent_workers,
            prefetch_factor=prefetch_factor if num_workers > 0 else 2,
            **kwargs
        )
        
        logger.info(
            f"DataLoader created: batch_size={batch_size}, "
            f"num_workers={num_workers}, pin_memory={pin_memory}"
        )
        
        return loader
    
    @staticmethod
    def _get_optimal_workers() -> int:
        """Get optimal number of workers."""
        import os
        cpu_count = os.cpu_count() or 4
        optimal = min(int(cpu_count * 0.75), 8)
        return max(optimal, 1)


__all__ = [
    "BaseDataset",
    "BaseDataLoaderFactory",
    "StandardDataLoaderFactory",
]



