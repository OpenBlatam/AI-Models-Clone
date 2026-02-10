"""
Time Stretch Augmentation Module

Implements time stretching augmentation for audio.
"""

from typing import Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("Librosa not available")


class TimeStretchAugmentation:
    """
    Time stretching augmentation.
    
    Args:
        rate_range: Tuple of (min_rate, max_rate) for time stretching.
    """
    
    def __init__(self, rate_range: Tuple[float, float] = (0.8, 1.2)):
        self.rate_range = rate_range
        logger.debug(f"Initialized TimeStretchAugmentation with rate_range={rate_range}")
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """
        Apply time stretching.
        
        Args:
            audio: Input audio array.
            sr: Sample rate.
        
        Returns:
            Time-stretched audio array.
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("Librosa required")
        
        rate = np.random.uniform(self.rate_range[0], self.rate_range[1])
        return librosa.effects.time_stretch(audio, rate=rate)



