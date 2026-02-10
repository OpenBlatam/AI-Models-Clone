"""
Pitch Shift Augmentation Module

Implements pitch shifting augmentation for audio.
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


class PitchShiftAugmentation:
    """
    Pitch shifting augmentation.
    
    Args:
        n_steps_range: Tuple of (min_steps, max_steps) for pitch shifting.
    """
    
    def __init__(self, n_steps_range: Tuple[int, int] = (-3, 3)):
        self.n_steps_range = n_steps_range
        logger.debug(f"Initialized PitchShiftAugmentation with n_steps_range={n_steps_range}")
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """
        Apply pitch shifting.
        
        Args:
            audio: Input audio array.
            sr: Sample rate.
        
        Returns:
            Pitch-shifted audio array.
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("Librosa required")
        
        n_steps = np.random.randint(self.n_steps_range[0], self.n_steps_range[1] + 1)
        return librosa.effects.pitch_shift(audio, sr=sr, n_steps=n_steps)



