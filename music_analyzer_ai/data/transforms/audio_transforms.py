"""
Modular Audio Transformations
Individual transform modules for audio processing
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


class AudioNormalizer:
    """Normalize audio to [-1, 1] range"""
    
    def __init__(self, method: str = "peak"):  # "peak" or "rms"
        self.method = method
    
    def __call__(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio"""
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


class AudioResampler:
    """Resample audio to target sample rate"""
    
    def __init__(self, target_sr: int = 22050):
        self.target_sr = target_sr
    
    def __call__(self, audio: np.ndarray, sr: int) -> Tuple[np.ndarray, int]:
        """Resample audio"""
        if not LIBROSA_AVAILABLE:
            raise ImportError("Librosa required for resampling")
        
        if sr == self.target_sr:
            return audio, sr
        
        resampled = librosa.resample(audio, orig_sr=sr, target_sr=self.target_sr)
        return resampled, self.target_sr


class AudioTrimmer:
    """Trim silence from audio"""
    
    def __init__(self, top_db: float = 20.0):
        self.top_db = top_db
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Trim silence"""
        if not LIBROSA_AVAILABLE:
            raise ImportError("Librosa required for trimming")
        
        trimmed, _ = librosa.effects.trim(audio, top_db=self.top_db)
        return trimmed


class AudioPadder:
    """Pad audio to target length"""
    
    def __init__(self, target_length: int, mode: str = "constant", value: float = 0.0):
        self.target_length = target_length
        self.mode = mode
        self.value = value
    
    def __call__(self, audio: np.ndarray) -> np.ndarray:
        """Pad audio"""
        current_length = len(audio)
        
        if current_length >= self.target_length:
            return audio[:self.target_length]
        
        pad_length = self.target_length - current_length
        
        if self.mode == "constant":
            padding = np.full(pad_length, self.value, dtype=audio.dtype)
            return np.concatenate([audio, padding])
        elif self.mode == "reflect":
            return np.pad(audio, (0, pad_length), mode='reflect')
        elif self.mode == "wrap":
            return np.pad(audio, (0, pad_length), mode='wrap')
        else:
            raise ValueError(f"Unknown padding mode: {self.mode}")


class AudioAugmenter:
    """Apply audio augmentations"""
    
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
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """Apply augmentations"""
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



