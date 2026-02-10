"""
Dataset Module for Music Generation

Implements:
- Efficient data loading with PyTorch Dataset
- Proper data preprocessing
- Audio-text pair handling
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
import torch
from torch.utils.data import Dataset
import numpy as np
import json

logger = logging.getLogger(__name__)


class MusicDataset(Dataset):
    """
    Dataset for music generation training.
    
    Handles loading and preprocessing of audio-text pairs
    following best practices for data loading.
    """
    
    def __init__(
        self,
        data_path: str,
        sample_rate: int = 32000,
        max_duration: int = 30,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None
    ):
        """
        Initialize music dataset.
        
        Args:
            data_path: Path to data directory or JSON file
            sample_rate: Target sample rate
            max_duration: Maximum duration in seconds
            transform: Optional transform function for audio
            target_transform: Optional transform function for targets
        """
        self.data_path = Path(data_path)
        self.sample_rate = sample_rate
        self.max_duration = max_duration
        self.transform = transform
        self.target_transform = target_transform
        self.data = self._load_data()
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load data from path."""
        if self.data_path.is_file() and self.data_path.suffix == '.json':
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif self.data_path.is_dir():
            # Load from directory structure
            data = []
            for file in self.data_path.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data.extend(json.load(f))
                except Exception as e:
                    logger.warning(f"Error loading {file}: {e}")
            return data
        else:
            raise ValueError(f"Invalid data path: {self.data_path}")
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get item from dataset.
        
        Args:
            idx: Index
            
        Returns:
            Dictionary with 'text', 'audio', and metadata
        """
        item = self.data[idx]
        
        # Load audio if path provided
        if 'audio_path' in item:
            import torchaudio
            try:
                audio, sr = torchaudio.load(item['audio_path'])
                # Resample if needed
                if sr != self.sample_rate:
                    resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                    audio = resampler(audio)
                # Trim to max duration
                max_samples = self.max_duration * self.sample_rate
                if audio.shape[1] > max_samples:
                    audio = audio[:, :max_samples]
            except Exception as e:
                logger.error(f"Error loading audio from {item['audio_path']}: {e}")
                # Return zero audio as fallback
                audio = torch.zeros((1, self.sample_rate * self.max_duration))
        else:
            # Use preprocessed audio array
            audio = torch.from_numpy(np.array(item['audio'])).float()
            if len(audio.shape) == 1:
                audio = audio.unsqueeze(0)
        
        # Apply transform if provided
        if self.transform:
            audio = self.transform(audio)
        
        result = {
            'text': item['text'],
            'audio': audio,
            'metadata': item.get('metadata', {})
        }
        
        # Apply target transform if provided
        if self.target_transform:
            result = self.target_transform(result)
        
        return result


class AudioTextDataset(Dataset):
    """
    Simple audio-text pair dataset.
    
    For cases where data is already preprocessed.
    """
    
    def __init__(
        self,
        texts: List[str],
        audio_arrays: List[np.ndarray],
        transform: Optional[Callable] = None
    ):
        """
        Initialize simple dataset.
        
        Args:
            texts: List of text prompts
            audio_arrays: List of audio arrays
            transform: Optional transform function
        """
        if len(texts) != len(audio_arrays):
            raise ValueError("Texts and audio arrays must have same length")
        
        self.texts = texts
        self.audio_arrays = audio_arrays
        self.transform = transform
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get item from dataset."""
        audio = torch.from_numpy(self.audio_arrays[idx]).float()
        
        if self.transform:
            audio = self.transform(audio)
        
        return {
            'text': self.texts[idx],
            'audio': audio
        }



