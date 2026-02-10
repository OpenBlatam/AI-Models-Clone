"""
Data Samplers
Specialized samplers for data loading
"""

import torch
from torch.utils.data import Sampler, WeightedRandomSampler
from typing import List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BalancedSampler(Sampler):
    """
    Balanced sampler for imbalanced datasets
    """
    
    def __init__(
        self,
        dataset,
        num_samples: Optional[int] = None,
    ):
        """
        Initialize balanced sampler
        
        Args:
            dataset: Dataset with targets
            num_samples: Number of samples (None = use dataset length)
        """
        self.dataset = dataset
        self.num_samples = num_samples or len(dataset)
        
        # Get class distribution
        if hasattr(dataset, 'targets'):
            targets = np.array(dataset.targets)
        else:
            # Extract targets from dataset
            targets = np.array([dataset[i][1] for i in range(len(dataset))])
        
        # Compute class weights
        classes, counts = np.unique(targets, return_counts=True)
        class_weights = 1.0 / counts
        sample_weights = class_weights[targets]
        
        # Normalize
        sample_weights = sample_weights / sample_weights.sum()
        
        self.weights = torch.from_numpy(sample_weights).double()
    
    def __iter__(self):
        """Generate indices"""
        return iter(
            torch.multinomial(self.weights, self.num_samples, replacement=True).tolist()
        )
    
    def __len__(self):
        """Return number of samples"""
        return self.num_samples


class WeightedSampler(WeightedRandomSampler):
    """
    Weighted random sampler wrapper
    """
    
    def __init__(
        self,
        weights: List[float],
        num_samples: int,
        replacement: bool = True,
    ):
        """
        Initialize weighted sampler
        
        Args:
            weights: Sample weights
            num_samples: Number of samples
            replacement: Sample with replacement
        """
        weights_tensor = torch.tensor(weights, dtype=torch.double)
        super().__init__(weights_tensor, num_samples, replacement=replacement)



