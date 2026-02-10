"""
Noise Augmentation Module

Implements additive noise augmentation for audio.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


class NoiseAugmentation:
    """
    Additive noise augmentation.
    
    Args:
        noise_factor: Noise level factor.
    """
    
    def __init__(self, noise_factor: float = 0.01):
        self.noise_factor = noise_factor
        logger.debug(f"Initialized NoiseAugmentation with noise_factor={noise_factor}")
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """
        Add noise.
        
        Args:
            audio: Input audio array.
            sr: Sample rate (not used, kept for compatibility).
        
        Returns:
            Audio with added noise.
        """
        noise = np.random.normal(0, self.noise_factor, audio.shape)
        return audio + noise



