"""
Dataset Classes - PyTorch Dataset Implementations
=================================================

Functional programming patterns for data loading and preprocessing.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Callable
import torch
from torch.utils.data import Dataset
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class BaseDataset(Dataset, ABC):
    """
    Abstract base class for all datasets.
    
    Provides common functionality and enforces consistent interface.
    """
    
    def __init__(
        self,
        data_path: Path,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None
    ):
        """
        Initialize dataset.
        
        Args:
            data_path: Path to data directory or file
            transform: Optional transform to apply to samples
            target_transform: Optional transform to apply to targets
        """
        self.data_path = Path(data_path)
        self.transform = transform
        self.target_transform = target_transform
        self._validate_path()
    
    def _validate_path(self) -> None:
        """Validate that data path exists."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path not found: {self.data_path}")
    
    @abstractmethod
    def __len__(self) -> int:
        """Return dataset size."""
        raise NotImplementedError
    
    @abstractmethod
    def __getitem__(self, idx: int) -> Tuple[Any, Any]:
        """
        Get item by index.
        
        Args:
            idx: Sample index
            
        Returns:
            Tuple of (sample, target)
        """
        raise NotImplementedError


class TextDataset(BaseDataset):
    """
    Dataset for text data with tokenization support.
    
    Designed for transformer models and LLMs.
    """
    
    def __init__(
        self,
        texts: List[str],
        labels: Optional[List[int]] = None,
        tokenizer: Optional[Callable] = None,
        max_length: int = 512,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None
    ):
        """
        Initialize text dataset.
        
        Args:
            texts: List of text samples
            labels: List of labels (optional)
            tokenizer: Tokenizer function or callable
            max_length: Maximum sequence length
            transform: Optional transform for samples
            target_transform: Optional transform for targets
        """
        super().__init__(data_path=Path("."), transform=transform, target_transform=target_transform)
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        if self.labels is not None and len(self.texts) != len(self.labels):
            raise ValueError("Texts and labels must have the same length")
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get text sample by index.
        
        Args:
            idx: Sample index
            
        Returns:
            Dictionary with tokenized text and optional label
        """
        text = self.texts[idx]
        
        # Apply transform if provided
        if self.transform:
            text = self.transform(text)
        
        # Tokenize if tokenizer is provided
        if self.tokenizer:
            encoded = self.tokenizer(
                text,
                max_length=self.max_length,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            # Remove batch dimension
            encoded = {k: v.squeeze(0) for k, v in encoded.items()}
        else:
            # Fallback: simple tokenization
            encoded = {'input_ids': torch.tensor([hash(text) % 10000])}
        
        result = encoded
        
        # Add label if available
        if self.labels is not None:
            label = self.labels[idx]
            if self.target_transform:
                label = self.target_transform(label)
            result['labels'] = torch.tensor(label, dtype=torch.long)
        
        return result


class ImageDataset(BaseDataset):
    """
    Dataset for image data with augmentation support.
    """
    
    def __init__(
        self,
        image_paths: List[Path],
        labels: Optional[List[int]] = None,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None
    ):
        """
        Initialize image dataset.
        
        Args:
            image_paths: List of paths to image files
            labels: List of labels (optional)
            transform: Optional transform for images
            target_transform: Optional transform for labels
        """
        super().__init__(data_path=Path("."), transform=transform, target_transform=target_transform)
        self.image_paths = [Path(p) for p in image_paths]
        self.labels = labels
        
        # Validate all paths exist
        for path in self.image_paths:
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {path}")
        
        if self.labels is not None and len(self.image_paths) != len(self.labels):
            raise ValueError("Image paths and labels must have the same length")
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        Get image sample by index.
        
        Args:
            idx: Sample index
            
        Returns:
            Tuple of (image_tensor, label) or (image_tensor, None)
        """
        image_path = self.image_paths[idx]
        
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Apply transform if provided
            if self.transform:
                image = self.transform(image)
            else:
                # Default: convert to tensor
                import torchvision.transforms as transforms
                to_tensor = transforms.ToTensor()
                image = to_tensor(image)
            
            result = (image,)
            
            # Add label if available
            if self.labels is not None:
                label = self.labels[idx]
                if self.target_transform:
                    label = self.target_transform(label)
                result = (image, torch.tensor(label, dtype=torch.long))
            
            return result[0] if len(result) == 1 else result
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            raise


def get_default_collate_fn() -> Callable:
    """
    Get default collate function for DataLoader.
    
    Returns:
        Collate function
    """
    def collate_fn(batch):
        """Default collate function that handles dictionaries and tuples."""
        if isinstance(batch[0], dict):
            # Handle dictionary batches (common for transformers)
            return {key: torch.stack([item[key] for item in batch]) for key in batch[0].keys()}
        elif isinstance(batch[0], tuple):
            # Handle tuple batches (common for image datasets)
            return tuple(torch.stack([item[i] for item in batch]) for i in range(len(batch[0])))
        else:
            # Fallback to default collate
            from torch.utils.data.dataloader import default_collate
            return default_collate(batch)
    
    return collate_fn



