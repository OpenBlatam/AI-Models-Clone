"""
Dataset Classes
===============

PyTorch dataset classes for event and routine data.
"""

import torch
from torch.utils.data import Dataset
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EventDataset(Dataset):
    """
    Dataset for event duration prediction.
    
    Features:
    - Event type (one-hot encoded)
    - Day of week (one-hot encoded)
    - Month (one-hot encoded)
    - Location type
    - Historical patterns
    """
    
    def __init__(
        self,
        events: List[Dict[str, Any]],
        feature_extractor: Optional[Any] = None
    ):
        """
        Initialize dataset.
        
        Args:
            events: List of event dictionaries
            feature_extractor: Feature extractor instance
        """
        self.events = events
        self.feature_extractor = feature_extractor
        
        # Extract features and targets
        self.features = []
        self.targets = []
        
        for event in events:
            try:
                # Extract features
                if feature_extractor:
                    features = feature_extractor.extract_event_features(event)
                else:
                    features = self._extract_features_simple(event)
                
                # Extract target (duration in hours)
                target = self._extract_duration(event)
                
                if features is not None and target is not None:
                    self.features.append(features)
                    self.targets.append(target)
            except Exception as e:
                logger.warning(f"Error processing event: {str(e)}")
                continue
    
    def _extract_features_simple(self, event: Dict[str, Any]) -> Optional[torch.Tensor]:
        """Simple feature extraction."""
        try:
            # Basic features
            features = []
            
            # Event type (simple encoding)
            event_type = event.get("type", "other")
            type_map = {"concert": 0, "interview": 1, "photoshoot": 2, "rehearsal": 3, "meeting": 4}
            features.append(type_map.get(event_type, 5) / 10.0)
            
            # Day of week
            if "start_time" in event:
                start = datetime.fromisoformat(event["start_time"])
                features.append(start.weekday() / 6.0)
                features.append(start.month / 12.0)
                features.append(start.hour / 23.0)
            else:
                features.extend([0.5, 0.5, 0.5])
            
            # Location (simple)
            location = event.get("location", "")
            features.append(1.0 if location else 0.0)
            
            # Pad to fixed size
            while len(features) < 32:
                features.append(0.0)
            
            return torch.tensor(features[:32], dtype=torch.float32)
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return None
    
    def _extract_duration(self, event: Dict[str, Any]) -> Optional[float]:
        """Extract duration in hours."""
        try:
            if "start_time" in event and "end_time" in event:
                start = datetime.fromisoformat(event["start_time"])
                end = datetime.fromisoformat(event["end_time"])
                duration = (end - start).total_seconds() / 3600.0
                return max(0.1, duration)  # Minimum 0.1 hours
            return None
        except Exception:
            return None
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.features)
    
    def __getitem__(self, idx: int) -> tuple:
        """
        Get item by index.
        
        Args:
            idx: Index
        
        Returns:
            (features, target) tuple
        """
        return (
            self.features[idx],
            torch.tensor(self.targets[idx], dtype=torch.float32)
        )


class RoutineDataset(Dataset):
    """
    Dataset for routine completion prediction.
    
    Features:
    - Routine type
    - Time of day
    - Day of week
    - Historical completion patterns
    """
    
    def __init__(
        self,
        routines: List[Dict[str, Any]],
        feature_extractor: Optional[Any] = None
    ):
        """
        Initialize dataset.
        
        Args:
            routines: List of routine dictionaries with history
            feature_extractor: Feature extractor instance
        """
        self.routines = routines
        self.feature_extractor = feature_extractor
        
        # Extract features and targets
        self.features = []
        self.targets = []
        
        for routine in routines:
            try:
                # Extract features
                if feature_extractor:
                    features = feature_extractor.extract_routine_features(routine)
                else:
                    features = self._extract_features_simple(routine)
                
                # Extract target (completion: 1.0 or 0.0)
                target = 1.0 if routine.get("completed", False) else 0.0
                
                if features is not None:
                    self.features.append(features)
                    self.targets.append(target)
            except Exception as e:
                logger.warning(f"Error processing routine: {str(e)}")
                continue
    
    def _extract_features_simple(self, routine: Dict[str, Any]) -> Optional[torch.Tensor]:
        """Simple feature extraction."""
        try:
            features = []
            
            # Routine type
            routine_type = routine.get("type", "other")
            type_map = {"exercise": 0, "practice": 1, "meal": 2, "rest": 3}
            features.append(type_map.get(routine_type, 4) / 10.0)
            
            # Time features
            if "scheduled_time" in routine:
                try:
                    time_str = routine["scheduled_time"]
                    hour = int(time_str.split(":")[0]) if ":" in time_str else 12
                    features.append(hour / 23.0)
                except:
                    features.append(0.5)
            else:
                features.append(0.5)
            
            # Day of week
            if "day_of_week" in routine:
                features.append(routine["day_of_week"] / 6.0)
            else:
                features.append(0.5)
            
            # Historical completion rate
            history = routine.get("completion_history", [])
            if history:
                completed = sum(1 for h in history if h.get("completed", False))
                features.append(completed / len(history))
            else:
                features.append(0.5)
            
            # Pad to fixed size
            while len(features) < 16:
                features.append(0.0)
            
            # Create sequence (for LSTM)
            # Repeat features to create sequence
            seq_features = torch.tensor(features[:16], dtype=torch.float32)
            seq_features = seq_features.unsqueeze(0).repeat(7, 1)  # [seq_len=7, features]
            
            return seq_features
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return None
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.features)
    
    def __getitem__(self, idx: int) -> tuple:
        """
        Get item by index.
        
        Args:
            idx: Index
        
        Returns:
            (features, target) tuple
        """
        return (
            self.features[idx],
            torch.tensor(self.targets[idx], dtype=torch.float32)
        )




