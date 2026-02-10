"""
Data Preprocessing - Advanced Preprocessing Utilities
======================================================

Advanced preprocessing utilities for different data types:
- Text preprocessing
- Image preprocessing
- Normalization
- Feature engineering
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Union
import torch
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """Text preprocessing utilities."""
    
    def __init__(
        self,
        lowercase: bool = True,
        remove_punctuation: bool = False,
        remove_numbers: bool = False,
        remove_stopwords: bool = False,
        max_length: Optional[int] = None
    ):
        """
        Initialize text preprocessor.
        
        Args:
            lowercase: Convert to lowercase
            remove_punctuation: Remove punctuation
            remove_numbers: Remove numbers
            remove_stopwords: Remove stopwords
            max_length: Maximum sequence length
        """
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        self.remove_stopwords = remove_stopwords
        self.max_length = max_length
        
        if remove_stopwords:
            try:
                import nltk
                from nltk.corpus import stopwords
                nltk.download('stopwords', quiet=True)
                self.stopwords = set(stopwords.words('english'))
            except ImportError:
                logger.warning("NLTK not available, stopwords removal disabled")
                self.remove_stopwords = False
                self.stopwords = set()
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess text.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        if self.lowercase:
            text = text.lower()
        
        if self.remove_punctuation:
            import string
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        if self.remove_numbers:
            text = ''.join(c for c in text if not c.isdigit())
        
        if self.remove_stopwords:
            words = text.split()
            text = ' '.join(w for w in words if w not in self.stopwords)
        
        if self.max_length:
            words = text.split()
            text = ' '.join(words[:self.max_length])
        
        return text


class ImagePreprocessor:
    """Image preprocessing utilities."""
    
    def __init__(
        self,
        resize: Optional[tuple] = None,
        normalize: bool = True,
        mean: Optional[List[float]] = None,
        std: Optional[List[float]] = None,
        to_tensor: bool = True
    ):
        """
        Initialize image preprocessor.
        
        Args:
            resize: Target size (width, height)
            normalize: Apply normalization
            mean: Normalization mean (ImageNet default)
            std: Normalization std (ImageNet default)
            to_tensor: Convert to tensor
        """
        self.resize = resize
        self.normalize = normalize
        self.mean = mean or [0.485, 0.456, 0.406]
        self.std = std or [0.229, 0.224, 0.225]
        self.to_tensor = to_tensor
    
    def preprocess(self, image: Union[Image.Image, np.ndarray]) -> torch.Tensor:
        """
        Preprocess image.
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image tensor
        """
        import torchvision.transforms as transforms
        
        # Convert to PIL if needed
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Build transform pipeline
        transform_list = []
        
        if self.resize:
            transform_list.append(transforms.Resize(self.resize))
        
        if self.to_tensor:
            transform_list.append(transforms.ToTensor())
        
        if self.normalize and self.to_tensor:
            transform_list.append(transforms.Normalize(mean=self.mean, std=self.std))
        
        transform = transforms.Compose(transform_list)
        return transform(image)


def normalize_features(
    features: np.ndarray,
    method: str = 'standard',
    mean: Optional[np.ndarray] = None,
    std: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Normalize features.
    
    Args:
        features: Feature array
        method: Normalization method ('standard', 'minmax', 'l2')
        mean: Pre-computed mean (for standard)
        std: Pre-computed std (for standard)
        
    Returns:
        Normalized features
    """
    if method == 'standard':
        if mean is None:
            mean = features.mean(axis=0)
        if std is None:
            std = features.std(axis=0)
        return (features - mean) / (std + 1e-8)
    
    elif method == 'minmax':
        min_val = features.min(axis=0)
        max_val = features.max(axis=0)
        return (features - min_val) / (max_val - min_val + 1e-8)
    
    elif method == 'l2':
        norms = np.linalg.norm(features, axis=1, keepdims=True)
        return features / (norms + 1e-8)
    
    else:
        raise ValueError(f"Unknown normalization method: {method}")



