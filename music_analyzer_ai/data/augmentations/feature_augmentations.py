"""
Modular Feature Augmentations
Individual augmentation modules for features
"""

from typing import Optional, Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)


class FeatureNoiseAugmentation:
    """Additive noise to features"""
    
    def __init__(self, noise_std: float = 0.01):
        self.noise_std = noise_std
    
    def __call__(self, features: np.ndarray) -> np.ndarray:
        """Add noise to features"""
        noise = np.random.normal(0, self.noise_std, features.shape)
        return features + noise


class FeatureScaleAugmentation:
    """Scale features by random factor"""
    
    def __init__(self, scale_range: Tuple[float, float] = (0.9, 1.1)):
        self.scale_range = scale_range
    
    def __call__(self, features: np.ndarray) -> np.ndarray:
        """Scale features"""
        scale = np.random.uniform(self.scale_range[0], self.scale_range[1])
        return features * scale


class FeatureShiftAugmentation:
    """Shift features by random offset"""
    
    def __init__(self, shift_range: Tuple[float, float] = (-0.1, 0.1)):
        self.shift_range = shift_range
    
    def __call__(self, features: np.ndarray) -> np.ndarray:
        """Shift features"""
        shift = np.random.uniform(self.shift_range[0], self.shift_range[1])
        return features + shift



