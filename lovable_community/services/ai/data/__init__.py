"""
Data Processing Module

Handles all data-related operations organized into sub-modules:
- loaders: Data loading and datasets
- preprocessing: Text preprocessing and cleaning
- augmentation: Data augmentation techniques
"""

# Import from sub-modules
from .loaders import (
    TextDataset,
    BatchProcessor,
    TextSample,
    batch_texts,
    collate_texts
)

from .preprocessing import (
    TextPreprocessor,
    TokenizationUtils,
    FeatureExtractor,
    create_preprocessing_pipeline,
    preprocess_text
)

from .augmentation import (
    DataAugmentation
)

__all__ = [
    # Loaders
    "TextDataset",
    "BatchProcessor",
    "TextSample",
    "batch_texts",
    "collate_texts",
    # Preprocessing
    "TextPreprocessor",
    "TokenizationUtils",
    "FeatureExtractor",
    "create_preprocessing_pipeline",
    "preprocess_text",
    # Augmentation
    "DataAugmentation",
]

