"""
Modular Data Augmentations
Separated augmentation strategies
"""

# Import from audio submodule
from .audio import (
    TimeStretchAugmentation,
    PitchShiftAugmentation,
    NoiseAugmentation,
    VolumeAugmentation,
    TimeMaskAugmentation,
    FrequencyMaskAugmentation
)
from .feature_augmentations import (
    FeatureNoiseAugmentation,
    FeatureScaleAugmentation,
    FeatureShiftAugmentation
)
from .augmentation_factory import AugmentationFactory, create_augmentation

__all__ = [
    # Audio augmentations
    "TimeStretchAugmentation",
    "PitchShiftAugmentation",
    "NoiseAugmentation",
    "VolumeAugmentation",
    "TimeMaskAugmentation",
    "FrequencyMaskAugmentation",
    # Feature augmentations
    "FeatureNoiseAugmentation",
    "FeatureScaleAugmentation",
    "FeatureShiftAugmentation",
    # Factory
    "AugmentationFactory",
    "create_augmentation",
]

