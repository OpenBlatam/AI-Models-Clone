"""
Data Module

Provides:
- Dataset classes for music generation
- Data transforms and augmentation
- Data loading utilities
"""

from .dataset import MusicDataset, AudioTextDataset
from .transforms import (
    AudioNormalize,
    AudioTrim,
    AudioPad,
    AudioAugmentation,
    ComposeTransforms,
    create_audio_transform_pipeline
)

__all__ = [
    "MusicDataset",
    "AudioTextDataset",
    "AudioNormalize",
    "AudioTrim",
    "AudioPad",
    "AudioAugmentation",
    "ComposeTransforms",
    "create_audio_transform_pipeline"
]



