"""
Feature Scaler Module

Scales features by a factor.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)


class FeatureScaler:
    """
    Scale features by a factor.
    
    Args:
        scale: Scaling factor.
    """
    
    def __init__(self, scale: float = 1.0):
        self.scale = scale
        logger.debug(f"Initialized FeatureScaler with scale={scale}")
    
    def __call__(self, features: np.ndarray) -> np.ndarray:
        """
        Scale features.
        
        Args:
            features: Input features array.
        
        Returns:
            Scaled features array.
        """
        return features * self.scale



