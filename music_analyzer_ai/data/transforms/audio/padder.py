"""
Audio Padder Module

Pads audio to target length.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


class AudioPadder:
    """
    Pad audio to target length.
    
    Args:
        target_length: Target length in samples.
        mode: Padding mode ("constant", "reflect", "wrap").
        value: Value for constant padding.
    """
    
    def __init__(self, target_length: int, mode: str = "constant", value: float = 0.0):
        self.target_length = target_length
        self.mode = mode
        self.value = value
        logger.debug(f"Initialized AudioPadder with target_length={target_length}, mode='{mode}'")
    
    def __call__(self, audio: np.ndarray) -> np.ndarray:
        """
        Pad audio to target length.
        
        Args:
            audio: Input audio array.
        
        Returns:
            Padded audio array.
        """
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



