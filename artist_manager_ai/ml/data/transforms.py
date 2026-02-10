"""
Data Transforms
===============

Advanced data transformation utilities following PyTorch best practices.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Callable, Optional, Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Compose:
    """Compose multiple transforms."""
    
    def __init__(self, transforms: List[Callable]):
        """
        Initialize compose.
        
        Args:
            transforms: List of transform functions
        """
        self.transforms = transforms
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """Apply all transforms."""
        for transform in self.transforms:
            x = transform(x)
        return x


class Normalize:
    """Normalize tensor."""
    
    def __init__(
        self,
        mean: Optional[torch.Tensor] = None,
        std: Optional[torch.Tensor] = None
    ):
        """
        Initialize normalizer.
        
        Args:
            mean: Mean values
            std: Standard deviation values
        """
        self.mean = mean
        self.std = std
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """Normalize tensor."""
        if self.mean is not None and self.std is not None:
            return (x - self.mean) / (self.std + 1e-8)
        return x


class RandomNoise:
    """Add random noise."""
    
    def __init__(self, std: float = 0.01):
        """
        Initialize noise transform.
        
        Args:
            std: Noise standard deviation
        """
        self.std = std
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """Add noise."""
        noise = torch.randn_like(x) * self.std
        return x + noise


class RandomScale:
    """Random scaling."""
    
    def __init__(self, scale_range: Tuple[float, float] = (0.9, 1.1)):
        """
        Initialize random scale.
        
        Args:
            scale_range: Scale range (min, max)
        """
        self.scale_range = scale_range
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """Apply random scaling."""
        scale = torch.empty(1).uniform_(*self.scale_range)
        return x * scale


class ToTensor:
    """Convert to tensor."""
    
    def __call__(self, x: np.ndarray) -> torch.Tensor:
        """Convert numpy array to tensor."""
        if isinstance(x, np.ndarray):
            return torch.from_numpy(x).float()
        return torch.tensor(x, dtype=torch.float32)


class FeatureSelector:
    """Select specific features."""
    
    def __init__(self, feature_indices: List[int]):
        """
        Initialize feature selector.
        
        Args:
            feature_indices: Indices of features to select
        """
        self.feature_indices = feature_indices
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """Select features."""
        return x[..., self.feature_indices]


class OneHotEncoder:
    """One-hot encode categorical features."""
    
    def __init__(self, num_classes: int):
        """
        Initialize one-hot encoder.
        
        Args:
            num_classes: Number of classes
        """
        self.num_classes = num_classes
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """One-hot encode."""
        return torch.nn.functional.one_hot(x.long(), self.num_classes).float()


def create_default_transforms(
    normalize: bool = True,
    add_noise: bool = False,
    noise_std: float = 0.01
) -> Compose:
    """
    Create default transforms.
    
    Args:
        normalize: Whether to normalize
        add_noise: Whether to add noise
        noise_std: Noise standard deviation
    
    Returns:
        Composed transforms
    """
    transforms = []
    
    if normalize:
        transforms.append(Normalize())
    
    if add_noise:
        transforms.append(RandomNoise(std=noise_std))
    
    return Compose(transforms)




