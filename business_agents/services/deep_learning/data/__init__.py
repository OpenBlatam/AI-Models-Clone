"""Data loading utilities for deep learning service."""

from .datasets import SimpleDataset, TextDataset, ImageDataset
from .dataloader import create_dataloader, split_dataset, create_dataloaders

# Optional optimized dataloader
try:
    from .optimized_dataloader import (
        create_optimized_dataloader,
        optimize_existing_dataloader
    )
    OPTIMIZED_DATALOADER_AVAILABLE = True
except ImportError:
    OPTIMIZED_DATALOADER_AVAILABLE = False
    create_optimized_dataloader = None
    optimize_existing_dataloader = None

__all__ = [
    "SimpleDataset",
    "TextDataset",
    "ImageDataset",
    "create_dataloader",
    "split_dataset",
    "create_dataloaders",
]

if OPTIMIZED_DATALOADER_AVAILABLE:
    __all__.extend([
        "create_optimized_dataloader",
        "optimize_existing_dataloader",
    ])

