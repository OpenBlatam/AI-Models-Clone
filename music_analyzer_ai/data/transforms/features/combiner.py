"""
Feature Combiner Module

Combines multiple feature arrays.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


class FeatureCombiner:
    """
    Combine multiple feature arrays.
    
    Args:
        axis: Axis along which to concatenate (default: -1).
    """
    
    def __init__(self, axis: int = -1):
        self.axis = axis
        logger.debug(f"Initialized FeatureCombiner with axis={axis}")
    
    def __call__(self, *feature_arrays: np.ndarray) -> np.ndarray:
        """
        Combine features.
        
        Args:
            *feature_arrays: Variable number of feature arrays to combine.
        
        Returns:
            Combined features array.
        """
        return np.concatenate(feature_arrays, axis=self.axis)



