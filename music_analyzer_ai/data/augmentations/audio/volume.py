"""
Volume Augmentation Module

Implements volume scaling augmentation for audio.
"""

from typing import Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)


class VolumeAugmentation:
    """
    Volume scaling augmentation.
    
    Args:
        scale_range: Tuple of (min_scale, max_scale) for volume scaling.
    """
    
    def __init__(self, scale_range: Tuple[float, float] = (0.5, 1.5)):
        self.scale_range = scale_range
        logger.debug(f"Initialized VolumeAugmentation with scale_range={scale_range}")
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """
        Scale volume.
        
        Args:
            audio: Input audio array.
            sr: Sample rate (not used, kept for compatibility).
        
        Returns:
            Volume-scaled audio array.
        """
        scale = np.random.uniform(self.scale_range[0], self.scale_range[1])
        return audio * scale



