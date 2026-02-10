"""
Dataset Classes - Functional Programming Approach
=================================================

Dataset classes for different data types following functional programming principles.
"""

import torch
from torch.utils.data import Dataset
from typing import Optional, Tuple, List, Any, Callable
import numpy as np
from pathlib import Path
import logging

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class SimpleDataset(Dataset):
    """
    Simple dataset wrapper for numpy arrays.
    
    Functional approach: Pure data transformation without side effects.
    """
    
    def __init__(
        self,
        data: np.ndarray,
        labels: Optional[np.ndarray] = None,
        transform: Optional[Callable] = None
    ):
        """
        Initialize simple dataset.
        
        Args:
            data: Input data array
            labels: Target labels (optional)
            transform: Optional transform function
        """
        self.data = torch.FloatTensor(data)
        self.labels = torch.LongTensor(labels) if labels is not None else None
        self.transform = transform
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Get item by index.
        
        Args:
            idx: Index
        
        Returns:
            Tuple of (data, label) or (data, None)
        """
        sample = self.data[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        if self.labels is not None:
            return sample, self.labels[idx]
        return sample, None


class TextDataset(Dataset):
    """
    Text dataset for NLP tasks.
    
    Handles tokenization and sequence processing.
    """
    
    def __init__(
        self,
        texts: List[str],
        labels: Optional[List[int]] = None,
        tokenizer: Optional[Callable] = None,
        max_length: int = 512,
        padding: bool = True,
        truncation: bool = True
    ):
        """
        Initialize text dataset.
        
        Args:
            texts: List of text strings
            labels: List of labels (optional)
            tokenizer: Tokenization function
            max_length: Maximum sequence length
            padding: Whether to pad sequences
            truncation: Whether to truncate sequences
        """
        self.texts = texts
        self.labels = torch.LongTensor(labels) if labels is not None else None
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.padding = padding
        self.truncation = truncation
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Get item by index.
        
        Args:
            idx: Index
        
        Returns:
            Tuple of (tokenized_text, label) or (tokenized_text, None)
        """
        text = self.texts[idx]
        
        if self.tokenizer:
            # Use tokenizer if provided
            encoded = self.tokenizer(
                text,
                max_length=self.max_length,
                padding=self.padding,
                truncation=self.truncation,
                return_tensors="pt"
            )
            # Extract input_ids
            tokenized = encoded['input_ids'].squeeze(0)
        else:
            # Simple character-level encoding as fallback
            tokenized = torch.LongTensor([ord(c) for c in text[:self.max_length]])
            if len(tokenized) < self.max_length and self.padding:
                padding = torch.zeros(self.max_length - len(tokenized), dtype=torch.long)
                tokenized = torch.cat([tokenized, padding])
            elif len(tokenized) > self.max_length and self.truncation:
                tokenized = tokenized[:self.max_length]
        
        if self.labels is not None:
            return tokenized, self.labels[idx]
        return tokenized, None


class ImageDataset(Dataset):
    """
    Image dataset for computer vision tasks.
    
    Handles image loading and preprocessing.
    """
    
    def __init__(
        self,
        image_paths: List[Path],
        labels: Optional[List[int]] = None,
        transform: Optional[Callable] = None
    ):
        """
        Initialize image dataset.
        
        Args:
            image_paths: List of image file paths
            labels: List of labels (optional)
            transform: Image transformation pipeline
        """
        self.image_paths = [Path(p) for p in image_paths]
        self.labels = torch.LongTensor(labels) if labels is not None else None
        self.transform = transform
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Get item by index.
        
        Args:
            idx: Index
        
        Returns:
            Tuple of (image, label) or (image, None)
        """
        try:
            from PIL import Image
            
            image_path = self.image_paths[idx]
            image = Image.open(image_path).convert('RGB')
            
            if self.transform:
                image = self.transform(image)
            else:
                # Default: convert to tensor
                import torchvision.transforms as transforms
                transform = transforms.ToTensor()
                image = transform(image)
            
            if self.labels is not None:
                return image, self.labels[idx]
            return image, None
            
        except Exception as e:
            logger.error(f"Error loading image {self.image_paths[idx]}: {e}")
            # Return zero tensor as fallback
            if self.labels is not None:
                return torch.zeros(3, 224, 224), self.labels[idx]
            return torch.zeros(3, 224, 224), None



