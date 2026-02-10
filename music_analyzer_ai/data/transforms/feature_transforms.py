"""
Modular Feature Transformations
Individual transform modules for feature processing
"""

from typing import Optional, List, Union
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
    """Normalize features"""
    
    def __init__(self, method: str = "standard"):  # "standard", "minmax", "robust"
        self.method = method
        self.scaler = None
        self._fitted = False
    
    def fit(self, features: np.ndarray):
        """Fit normalizer on data"""
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
        """Normalize features"""
        if not self._fitted:
            raise ValueError("Normalizer not fitted. Call fit() first.")
        
        if self.scaler:
            return self.scaler.transform(features)
        else:
            # Simple normalization
            mean = features.mean(axis=0, keepdims=True)
            std = features.std(axis=0, keepdims=True)
            return (features - mean) / (std + 1e-8)


class FeatureScaler:
    """Scale features by a factor"""
    
    def __init__(self, scale: float = 1.0):
        self.scale = scale
    
    def __call__(self, features: np.ndarray) -> np.ndarray:
        """Scale features"""
        return features * self.scale


class FeatureSelector:
    """Select specific features by indices"""
    
    def __init__(self, indices: Union[List[int], np.ndarray]):
        self.indices = np.array(indices)
    
    def __call__(self, features: np.ndarray) -> np.ndarray:
        """Select features"""
        return features[:, self.indices]


class FeatureCombiner:
    """Combine multiple feature arrays"""
    
    def __init__(self, axis: int = -1):
        self.axis = axis
    
    def __call__(self, *feature_arrays: np.ndarray) -> np.ndarray:
        """Combine features"""
        return np.concatenate(feature_arrays, axis=self.axis)



