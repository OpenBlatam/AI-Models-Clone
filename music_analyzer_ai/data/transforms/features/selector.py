"""
Feature Selector Module

Selects specific features by indices.
"""

from typing import Union, List
import logging
import numpy as np

logger = logging.getLogger(__name__)


class FeatureSelector:
    """
    Select specific features by indices.
    
    Args:
        indices: List or array of feature indices to select.
    """
    
    def __init__(self, indices: Union[List[int], np.ndarray]):
        self.indices = np.array(indices)
        logger.debug(f"Initialized FeatureSelector with {len(self.indices)} indices")
    
    def __call__(self, features: np.ndarray) -> np.ndarray:
        """
        Select features.
        
        Args:
            features: Input features array.
        
        Returns:
            Selected features array.
        """
        return features[:, self.indices]



