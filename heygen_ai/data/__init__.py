"""
Data Module for HeyGen AI
==========================

This module contains data processing pipelines following best practices:
- Functional programming for data processing
- Efficient data loading with DataLoader
- Proper train/validation/test splits
- Data augmentation utilities
"""

from typing import Any, Dict, List, Optional

import torch
from torch.utils.data import Dataset, DataLoader


class BaseDataset(Dataset):
    """Base class for all datasets.
    
    Provides common functionality:
    - Length tracking
    - Item indexing
    - Data transformation
    """
    
    def __init__(self, data: List[Any], transform: Optional[Any] = None):
        """Initialize dataset.
        
        Args:
            data: List of data samples
            transform: Optional transform function
        """
        self.data = data
        self.transform = transform
    
    def __len__(self) -> int:
        """Return dataset length."""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get item by index.
        
        Args:
            idx: Item index
        
        Returns:
            Data sample dictionary
        """
        sample = self.data[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample


# Import dataloader utilities
from .dataloaders import (
    create_dataloader,
    collate_text_sequences,
    split_dataset,
)

__all__ = [
    "BaseDataset",
    "create_dataloader",
    "collate_text_sequences",
    "split_dataset",
]
