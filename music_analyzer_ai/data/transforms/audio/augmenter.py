"""
Audio Augmenter Module

Applies audio augmentations.
"""

from typing import Optional, Tuple
import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("Librosa not available")


class AudioAugmenter:
    """
    Apply audio augmentations.
    
    Args:
        time_stretch: Optional tuple (min_rate, max_rate) for time stretching.
        pitch_shift: Optional tuple (min_steps, max_steps) for pitch shifting.
        add_noise: Optional noise level.
        volume_scale: Optional tuple (min_scale, max_scale) for volume scaling.
    """
    
    def __init__(
        self,
        time_stretch: Optional[Tuple[float, float]] = None,
        pitch_shift: Optional[Tuple[int, int]] = None,
        add_noise: Optional[float] = None,
        volume_scale: Optional[Tuple[float, float]] = None
    ):
        self.time_stretch = time_stretch
        self.pitch_shift = pitch_shift
        self.add_noise = add_noise
        self.volume_scale = volume_scale
        logger.debug(f"Initialized AudioAugmenter with time_stretch={time_stretch}, pitch_shift={pitch_shift}")
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """
        Apply augmentations to audio.
        
        Args:
            audio: Input audio array.
            sr: Sample rate.
        
        Returns:
            Augmented audio array.
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("Librosa required for augmentation")
        
        augmented = audio.copy()
        
        # Time stretching
        if self.time_stretch:
            rate = np.random.uniform(self.time_stretch[0], self.time_stretch[1])
            augmented = librosa.effects.time_stretch(augmented, rate=rate)
        
        # Pitch shifting
        if self.pitch_shift:
            n_steps = np.random.randint(self.pitch_shift[0], self.pitch_shift[1] + 1)
            augmented = librosa.effects.pitch_shift(augmented, sr=sr, n_steps=n_steps)
        
        # Add noise
        if self.add_noise:
            noise = np.random.normal(0, self.add_noise, augmented.shape)
            augmented = augmented + noise
        
        # Volume scaling
        if self.volume_scale:
            scale = np.random.uniform(self.volume_scale[0], self.volume_scale[1])
            augmented = augmented * scale
        
        return augmented



