"""
Masking Augmentation Module

Implements time and frequency masking augmentations (SpecAugment style).
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


class TimeMaskAugmentation:
    """
    Time masking augmentation (SpecAugment style).
    
    Args:
        max_mask_length: Maximum length of time mask.
    """
    
    def __init__(self, max_mask_length: int = 10):
        self.max_mask_length = max_mask_length
        logger.debug(f"Initialized TimeMaskAugmentation with max_mask_length={max_mask_length}")
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """
        Apply time mask.
        
        Args:
            audio: Input audio array.
            sr: Sample rate (not used, kept for compatibility).
        
        Returns:
            Time-masked audio array.
        """
        masked_audio = audio.copy()
        mask_length = np.random.randint(1, self.max_mask_length + 1)
        mask_start = np.random.randint(0, len(audio) - mask_length)
        masked_audio[mask_start:mask_start + mask_length] = 0
        return masked_audio


class FrequencyMaskAugmentation:
    """
    Frequency masking augmentation (for spectrograms).
    
    Args:
        max_mask_freq: Maximum number of frequency bins to mask.
    """
    
    def __init__(self, max_mask_freq: int = 10):
        self.max_mask_freq = max_mask_freq
        logger.debug(f"Initialized FrequencyMaskAugmentation with max_mask_freq={max_mask_freq}")
    
    def __call__(self, spectrogram: np.ndarray) -> np.ndarray:
        """
        Apply frequency mask to spectrogram.
        
        Args:
            spectrogram: Input spectrogram array [freq_bins, time_frames].
        
        Returns:
            Frequency-masked spectrogram array.
        """
        masked_spec = spectrogram.copy()
        mask_length = np.random.randint(1, self.max_mask_freq + 1)
        mask_start = np.random.randint(0, spectrogram.shape[0] - mask_length)
        masked_spec[mask_start:mask_start + mask_length, :] = 0
        return masked_spec



