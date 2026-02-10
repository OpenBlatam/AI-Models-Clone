"""
Audio Trimmer Module

Trims silence from audio.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("Librosa not available")


class AudioTrimmer:
    """
    Trim silence from audio.
    
    Args:
        top_db: Threshold in dB below reference to consider as silence.
    """
    
    def __init__(self, top_db: float = 20.0):
        self.top_db = top_db
        logger.debug(f"Initialized AudioTrimmer with top_db={top_db}")
    
    def __call__(self, audio: np.ndarray, sr: int = 22050) -> np.ndarray:
        """
        Trim silence from audio.
        
        Args:
            audio: Input audio array.
            sr: Sample rate.
        
        Returns:
            Trimmed audio array.
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("Librosa required for trimming")
        
        trimmed, _ = librosa.effects.trim(audio, top_db=self.top_db)
        return trimmed



