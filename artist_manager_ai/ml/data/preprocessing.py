"""
Data Preprocessing
==================

Feature extraction and data preprocessing utilities.
"""

import torch
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Feature extractor for events and routines."""
    
    def __init__(self):
        """Initialize feature extractor."""
        self.event_type_map = {
            "concert": 0, "interview": 1, "photoshoot": 2,
            "rehearsal": 3, "meeting": 4, "other": 5
        }
        self.routine_type_map = {
            "exercise": 0, "practice": 1, "meal": 2, "rest": 3, "other": 4
        }
    
    def extract_event_features(self, event: Dict[str, Any]) -> torch.Tensor:
        """
        Extract features from event.
        
        Args:
            event: Event dictionary
        
        Returns:
            Feature tensor
        """
        features = []
        
        # Event type (one-hot like encoding)
        event_type = event.get("type", "other")
        type_idx = self.event_type_map.get(event_type, 5)
        type_features = [0.0] * 6
        if type_idx < 6:
            type_features[type_idx] = 1.0
        features.extend(type_features)
        
        # Temporal features
        if "start_time" in event:
            try:
                start = datetime.fromisoformat(event["start_time"])
                # Day of week (one-hot like)
                dow_features = [0.0] * 7
                dow_features[start.weekday()] = 1.0
                features.extend(dow_features)
                
                # Month (normalized)
                features.append(start.month / 12.0)
                
                # Hour (normalized)
                features.append(start.hour / 23.0)
            except:
                features.extend([0.0] * 9)
        else:
            features.extend([0.0] * 9)
        
        # Location features
        location = event.get("location", "")
        features.append(1.0 if location else 0.0)
        features.append(len(location) / 100.0 if location else 0.0)
        
        # Description length
        description = event.get("description", "")
        features.append(len(description) / 500.0)
        
        # Pad to 32 features
        while len(features) < 32:
            features.append(0.0)
        
        return torch.tensor(features[:32], dtype=torch.float32)
    
    def extract_routine_features(self, routine: Dict[str, Any]) -> torch.Tensor:
        """
        Extract features from routine.
        
        Args:
            routine: Routine dictionary
        
        Returns:
            Feature tensor sequence [seq_len, features]
        """
        base_features = []
        
        # Routine type
        routine_type = routine.get("type", "other")
        type_idx = self.routine_type_map.get(routine_type, 4)
        type_features = [0.0] * 5
        if type_idx < 5:
            type_features[type_idx] = 1.0
        base_features.extend(type_features)
        
        # Time features
        if "scheduled_time" in routine:
            try:
                time_str = routine["scheduled_time"]
                hour = int(time_str.split(":")[0]) if ":" in time_str else 12
                base_features.append(hour / 23.0)
            except:
                base_features.append(0.5)
        else:
            base_features.append(0.5)
        
        # Day of week
        if "day_of_week" in routine:
            base_features.append(routine["day_of_week"] / 6.0)
        else:
            base_features.append(0.5)
        
        # Historical completion
        history = routine.get("completion_history", [])
        if history:
            completed = sum(1 for h in history if h.get("completed", False))
            base_features.append(completed / len(history))
        else:
            base_features.append(0.5)
        
        # Pad to 16 features
        while len(base_features) < 16:
            base_features.append(0.0)
        
        # Create sequence for LSTM (7 days)
        base_tensor = torch.tensor(base_features[:16], dtype=torch.float32)
        sequence = base_tensor.unsqueeze(0).repeat(7, 1)  # [7, 16]
        
        return sequence


class DataPreprocessor:
    """Data preprocessor with normalization and augmentation."""
    
    def __init__(self, normalize: bool = True):
        """
        Initialize preprocessor.
        
        Args:
            normalize: Whether to normalize features
        """
        self.normalize = normalize
        self.feature_mean: Optional[torch.Tensor] = None
        self.feature_std: Optional[torch.Tensor] = None
    
    def fit(self, features: List[torch.Tensor]):
        """
        Fit preprocessor on data.
        
        Args:
            features: List of feature tensors
        """
        if not self.normalize:
            return
        
        # Stack features
        stacked = torch.stack(features)
        
        # Compute mean and std
        self.feature_mean = stacked.mean(dim=0)
        self.feature_std = stacked.std(dim=0)
        
        # Avoid division by zero
        self.feature_std = torch.clamp(self.feature_std, min=1e-8)
    
    def transform(self, features: torch.Tensor) -> torch.Tensor:
        """
        Transform features.
        
        Args:
            features: Feature tensor
        
        Returns:
            Transformed features
        """
        if not self.normalize or self.feature_mean is None:
            return features
        
        # Normalize
        normalized = (features - self.feature_mean) / self.feature_std
        
        return normalized
    
    def fit_transform(self, features: List[torch.Tensor]) -> List[torch.Tensor]:
        """
        Fit and transform.
        
        Args:
            features: List of feature tensors
        
        Returns:
            Transformed features
        """
        self.fit(features)
        return [self.transform(f) for f in features]




