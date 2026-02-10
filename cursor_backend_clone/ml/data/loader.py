"""
Data Loader Factory - Factory para DataLoaders
==============================================

Factory para crear DataLoaders con diferentes configuraciones.
"""

import logging
from typing import Optional, Dict, Any
import torch
from torch.utils.data import DataLoader

from .dataset import CodeDataset
from .collator import DataCollator

logger = logging.getLogger(__name__)


class DataLoaderFactory:
    """Factory para crear DataLoaders"""
    
    @staticmethod
    def create(
        dataset: CodeDataset,
        batch_size: int = 8,
        shuffle: bool = True,
        num_workers: int = 0,
        pin_memory: bool = True,
        collate_fn: Optional[callable] = None,
        **kwargs
    ) -> DataLoader:
        """Crear DataLoader"""
        if collate_fn is None:
            collate_fn = DataCollator(dataset.tokenizer)
        
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=pin_memory and torch.cuda.is_available(),
            collate_fn=collate_fn,
            **kwargs
        )
    
    @staticmethod
    def create_train_val_loaders(
        train_dataset: CodeDataset,
        val_dataset: CodeDataset,
        batch_size: int = 8,
        train_shuffle: bool = True,
        val_shuffle: bool = False,
        **kwargs
    ) -> tuple[DataLoader, DataLoader]:
        """Crear train y validation loaders"""
        train_loader = DataLoaderFactory.create(
            train_dataset,
            batch_size=batch_size,
            shuffle=train_shuffle,
            **kwargs
        )
        
        val_loader = DataLoaderFactory.create(
            val_dataset,
            batch_size=batch_size,
            shuffle=val_shuffle,
            **kwargs
        )
        
        return train_loader, val_loader


