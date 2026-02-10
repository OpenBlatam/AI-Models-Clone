"""
Modular Audio Augmentations
Individual augmentation modules for audio
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


class TimeStretchAugmentation:
    """Time stretching augmentation"""
    
    def __init__(self, rate_range: Tuple[float, float] = (0.8, 1.2)):
        self.rate_range = rate_range
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Apply time stretching"""
        if not LIBROSA_AVAILABLE:
            raise ImportError("Librosa required")
        
        rate = np.random.uniform(self.rate_range[0], self.rate_range[1])
        return librosa.effects.time_stretch(audio, rate=rate)


class PitchShiftAugmentation:
    """Pitch shifting augmentation"""
    
    def __init__(self, n_steps_range: Tuple[int, int] = (-3, 3)):
        self.n_steps_range = n_steps_range
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Apply pitch shifting"""
        if not LIBROSA_AVAILABLE:
            raise ImportError("Librosa required")
        
        n_steps = np.random.randint(self.n_steps_range[0], self.n_steps_range[1] + 1)
        return librosa.effects.pitch_shift(audio, sr=sr, n_steps=n_steps)


class NoiseAugmentation:
    """Additive noise augmentation"""
    
    def __init__(self, noise_factor: float = 0.01):
        self.noise_factor = noise_factor
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Add noise"""
        noise = np.random.normal(0, self.noise_factor, audio.shape)
        return audio + noise


class VolumeAugmentation:
    """Volume scaling augmentation"""
    
    def __init__(self, scale_range: Tuple[float, float] = (0.5, 1.5)):
        self.scale_range = scale_range
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Scale volume"""
        scale = np.random.uniform(self.scale_range[0], self.scale_range[1])
        return audio * scale


class TimeMaskAugmentation:
    """Time masking augmentation (SpecAugment style)"""
    
    def __init__(self, max_mask_length: int = 10):
        self.max_mask_length = max_mask_length
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Apply time mask"""
        masked_audio = audio.copy()
        mask_length = np.random.randint(1, self.max_mask_length + 1)
        mask_start = np.random.randint(0, len(audio) - mask_length)
        masked_audio[mask_start:mask_start + mask_length] = 0
        return masked_audio


class FrequencyMaskAugmentation:
    """Frequency masking augmentation (for spectrograms)"""
    
    def __init__(self, max_mask_freq: int = 10):
        self.max_mask_freq = max_mask_freq
    
    def __call__(self, spectrogram: np.ndarray) -> np.ndarray:
        """Apply frequency mask to spectrogram"""
        masked_spec = spectrogram.copy()
        mask_length = np.random.randint(1, self.max_mask_freq + 1)
        mask_start = np.random.randint(0, spectrogram.shape[0] - mask_length)
        masked_spec[mask_start:mask_start + mask_length, :] = 0
        return masked_spec



