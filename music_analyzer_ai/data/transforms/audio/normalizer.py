"""
Audio Normalizer Module

Normalizes audio to target range.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


class AudioNormalizer:
    """
    Normalize audio to [-1, 1] range.
    
    Args:
        method: Normalization method ("peak" or "rms").
    """
    
    def __init__(self, method: str = "peak"):  # "peak" or "rms"
        self.method = method
        logger.debug(f"Initialized AudioNormalizer with method='{method}'")
    
    def __call__(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio.
        
        Args:
            audio: Input audio array.
        
        Returns:
            Normalized audio array.
        """
        if self.method == "peak":
            max_val = np.abs(audio).max()
            if max_val > 0:
                return audio / max_val
            return audio
        elif self.method == "rms":
            rms = np.sqrt(np.mean(audio ** 2))
            if rms > 0:
                return audio / rms
            return audio
        else:
            raise ValueError(f"Unknown normalization method: {self.method}")



