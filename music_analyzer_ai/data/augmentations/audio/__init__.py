"""
Audio Augmentations Submodule
Aggregates various audio augmentation components.
"""

from .time_stretch import TimeStretchAugmentation
from .pitch_shift import PitchShiftAugmentation
from .noise import NoiseAugmentation
from .volume import VolumeAugmentation
from .masking import TimeMaskAugmentation, FrequencyMaskAugmentation

__all__ = [
    "TimeStretchAugmentation",
    "PitchShiftAugmentation",
    "NoiseAugmentation",
    "VolumeAugmentation",
    "TimeMaskAugmentation",
    "FrequencyMaskAugmentation",
]



