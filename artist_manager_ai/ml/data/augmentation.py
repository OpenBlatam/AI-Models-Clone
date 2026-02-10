"""
Data Augmentation
================

Data augmentation techniques for training data.
"""

import torch
import numpy as np
from typing import Dict, Any, List, Optional, Callable
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class DataAugmentation:
    """
    Data augmentation for training data.
    
    Techniques:
    - Noise injection
    - Feature scaling
    - Time shifting
    - Feature masking
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize augmentation.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
        self._logger = logger
    
    def add_noise(
        self,
        x: torch.Tensor,
        noise_level: float = 0.01,
        noise_type: str = "gaussian"
    ) -> torch.Tensor:
        """
        Add noise to input.
        
        Args:
            x: Input tensor
            noise_level: Noise level (std for gaussian, prob for dropout)
            noise_type: Type of noise ("gaussian", "dropout")
        
        Returns:
            Augmented tensor
        """
        if noise_type == "gaussian":
            noise = torch.randn_like(x) * noise_level
            return x + noise
        elif noise_type == "dropout":
            mask = torch.rand_like(x) > noise_level
            return x * mask.float()
        else:
            raise ValueError(f"Unknown noise type: {noise_type}")
    
    def scale_features(
        self,
        x: torch.Tensor,
        scale_range: tuple = (0.9, 1.1)
    ) -> torch.Tensor:
        """
        Scale features randomly.
        
        Args:
            x: Input tensor
            scale_range: Range for scaling (min, max)
        
        Returns:
            Scaled tensor
        """
        scale = torch.empty(x.shape[0], 1).uniform_(*scale_range)
        if x.device.type == "cuda":
            scale = scale.cuda()
        return x * scale
    
    def time_shift(
        self,
        x: torch.Tensor,
        max_shift: int = 2
    ) -> torch.Tensor:
        """
        Shift temporal features.
        
        Args:
            x: Input tensor [batch, seq_len, features]
            max_shift: Maximum shift amount
        
        Returns:
            Shifted tensor
        """
        if x.dim() != 3:
            return x
        
        batch_size, seq_len, features = x.shape
        shifts = torch.randint(-max_shift, max_shift + 1, (batch_size,))
        
        shifted = []
        for i in range(batch_size):
            shift = shifts[i].item()
            if shift == 0:
                shifted.append(x[i])
            elif shift > 0:
                # Shift right
                shifted.append(torch.cat([
                    x[i, shift:],
                    x[i, -shift:].clone()
                ], dim=0))
            else:
                # Shift left
                shifted.append(torch.cat([
                    x[i, :shift].clone(),
                    x[i, :shift]
                ], dim=0))
        
        return torch.stack(shifted)
    
    def feature_masking(
        self,
        x: torch.Tensor,
        mask_prob: float = 0.1
    ) -> torch.Tensor:
        """
        Randomly mask features.
        
        Args:
            x: Input tensor
            mask_prob: Probability of masking a feature
        
        Returns:
            Masked tensor
        """
        mask = torch.rand_like(x) > mask_prob
        return x * mask.float()
    
    def augment(
        self,
        x: torch.Tensor,
        techniques: Optional[List[str]] = None,
        **kwargs
    ) -> torch.Tensor:
        """
        Apply augmentation techniques.
        
        Args:
            x: Input tensor
            techniques: List of techniques to apply
            **kwargs: Technique-specific parameters
        
        Returns:
            Augmented tensor
        """
        if techniques is None:
            techniques = ["noise"]
        
        augmented = x.clone()
        
        for technique in techniques:
            if technique == "noise":
                noise_level = kwargs.get("noise_level", 0.01)
                noise_type = kwargs.get("noise_type", "gaussian")
                augmented = self.add_noise(augmented, noise_level, noise_type)
            elif technique == "scale":
                scale_range = kwargs.get("scale_range", (0.9, 1.1))
                augmented = self.scale_features(augmented, scale_range)
            elif technique == "time_shift":
                max_shift = kwargs.get("max_shift", 2)
                augmented = self.time_shift(augmented, max_shift)
            elif technique == "mask":
                mask_prob = kwargs.get("mask_prob", 0.1)
                augmented = self.feature_masking(augmented, mask_prob)
        
        return augmented


class AugmentedDataset(torch.utils.data.Dataset):
    """Dataset with augmentation."""
    
    def __init__(
        self,
        base_dataset: torch.utils.data.Dataset,
        augmentation: Optional[DataAugmentation] = None,
        augment_prob: float = 0.5
    ):
        """
        Initialize augmented dataset.
        
        Args:
            base_dataset: Base dataset
            augmentation: Augmentation instance
            augment_prob: Probability of applying augmentation
        """
        self.base_dataset = base_dataset
        self.augmentation = augmentation or DataAugmentation()
        self.augment_prob = augment_prob
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.base_dataset)
    
    def __getitem__(self, idx: int) -> tuple:
        """
        Get item with optional augmentation.
        
        Args:
            idx: Index
        
        Returns:
            (features, target) tuple
        """
        features, target = self.base_dataset[idx]
        
        # Apply augmentation with probability
        if torch.rand(1).item() < self.augment_prob:
            features = self.augmentation.augment(features.unsqueeze(0)).squeeze(0)
        
        return features, target




