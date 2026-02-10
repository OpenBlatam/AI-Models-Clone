"""
Audio Resampler Module

Resamples audio to target sample rate.
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


class AudioResampler:
    """
    Resample audio to target sample rate.
    
    Args:
        target_sr: Target sample rate.
    """
    
    def __init__(self, target_sr: int = 22050):
        self.target_sr = target_sr
        logger.debug(f"Initialized AudioResampler with target_sr={target_sr}")
    
    def __call__(self, audio: np.ndarray, sr: int) -> Tuple[np.ndarray, int]:
        """
        Resample audio.
        
        Args:
            audio: Input audio array.
            sr: Current sample rate.
        
        Returns:
            Tuple of (resampled audio, new sample rate).
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("Librosa required for resampling")
        
        if sr == self.target_sr:
            return audio, sr
        
        resampled = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sr)
        return resampled, self.target_sr



