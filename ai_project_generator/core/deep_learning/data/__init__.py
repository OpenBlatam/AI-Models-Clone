"""
Data Module - Data Loading and Preprocessing Pipelines
=======================================================

This module provides functional programming patterns for data processing:
- Dataset classes
- DataLoader configurations
- Data preprocessing and augmentation
- Data validation and splitting
"""

from typing import Optional, Dict, Any, Callable, Tuple
import torch
from torch.utils.data import Dataset, DataLoader

from .datasets import BaseDataset, TextDataset, ImageDataset, get_default_collate_fn
from .dataloader_utils import create_dataloader, train_val_test_split

# Try to import optimized dataloader
try:
    from .optimized_dataloader import (
        create_optimized_dataloader,
        get_optimal_num_workers,
        get_optimal_prefetch_factor,
        benchmark_dataloader
    )
    OPTIMIZED_DATALOADER_AVAILABLE = True
except ImportError:
    OPTIMIZED_DATALOADER_AVAILABLE = False
    create_optimized_dataloader = None
    get_optimal_num_workers = None
    get_optimal_prefetch_factor = None
    benchmark_dataloader = None

# Try to import augmentation
try:
    from .augmentation import (
        get_image_augmentation,
        Mixup,
        CutMix
    )
    AUGMENTATION_AVAILABLE = True
except ImportError:
    AUGMENTATION_AVAILABLE = False
    get_image_augmentation = None
    Mixup = None
    CutMix = None

__all__ = [
    "BaseDataset",
    "TextDataset",
    "ImageDataset",
    "create_dataloader",
    "train_val_test_split",
    "get_default_collate_fn",
]

if AUGMENTATION_AVAILABLE:
    __all__.extend(["get_image_augmentation", "Mixup", "CutMix"])

if OPTIMIZED_DATALOADER_AVAILABLE:
    __all__.extend([
        "create_optimized_dataloader",
        "get_optimal_num_workers",
        "get_optimal_prefetch_factor",
        "benchmark_dataloader"
    ])

# Try to import preprocessing
try:
    from .preprocessing import (
        TextPreprocessor,
        ImagePreprocessor,
        normalize_features
    )
    PREPROCESSING_AVAILABLE = True
except ImportError:
    PREPROCESSING_AVAILABLE = False
    TextPreprocessor = None
    ImagePreprocessor = None
    normalize_features = None

if PREPROCESSING_AVAILABLE:
    __all__.extend([
        "TextPreprocessor",
        "ImagePreprocessor",
        "normalize_features"
    ])

