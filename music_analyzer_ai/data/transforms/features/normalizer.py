"""
Feature Normalizer Module

Normalizes features using various methods.
"""

from typing import Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("Scikit-learn not available")


class FeatureNormalizer:
    """
    Normalize features.
    
    Args:
        method: Normalization method ("standard", "minmax", "robust").
    """
    
    def __init__(self, method: str = "standard"):  # "standard", "minmax", "robust"
        self.method = method
        self.scaler = None
        self._fitted = False
        logger.debug(f"Initialized FeatureNormalizer with method='{method}'")
    
    def fit(self, features: np.ndarray):
        """
        Fit normalizer on data.
        
        Args:
            features: Training features array.
        """
        if not SKLEARN_AVAILABLE:
            # Simple normalization without sklearn
            self._fitted = True
            return
        
        if self.method == "standard":
            self.scaler = StandardScaler()
        elif self.method == "minmax":
            self.scaler = MinMaxScaler()
        elif self.method == "robust":
            self.scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown normalization method: {self.method}")
        
        self.scaler.fit(features)
        self._fitted = True
    
    def __call__(self, features: np.ndarray) -> np.ndarray:
        """
        Normalize features.
        
        Args:
            features: Input features array.
        
        Returns:
            Normalized features array.
        """
        if not self._fitted:
            raise ValueError("Normalizer not fitted. Call fit() first.")
        
        if self.scaler:
            return self.scaler.transform(features)
        else:
            # Simple normalization
            mean = features.mean(axis=0, keepdims=True)
            std = features.std(axis=0, keepdims=True)
            return (features - mean) / (std + 1e-8)



