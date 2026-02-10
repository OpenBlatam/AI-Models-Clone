"""
Base Data Processor
Abstract base class for data processors
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """
    Abstract base class for data processors
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize processor
        
        Args:
            config: Processor configuration
        """
        self.config = config or {}
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Process data
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        pass
    
    def process_batch(self, data_list: List[Any]) -> List[Any]:
        """
        Process batch of data
        
        Args:
            data_list: List of input data
            
        Returns:
            List of processed data
        """
        return [self.process(item) for item in data_list]
    
    def fit(self, data: Any):
        """
        Fit processor on data (for normalization, etc.)
        
        Args:
            data: Training data
        """
        pass


class FeatureProcessor(BaseProcessor):
    """
    Process features
    """
    
    def __init__(self, normalize: bool = True, **kwargs):
        """
        Initialize feature processor
        
        Args:
            normalize: Normalize features
            **kwargs: Additional config
        """
        super().__init__(kwargs)
        self.normalize = normalize
        self.mean = None
        self.std = None
    
    def fit(self, features: List[List[float]]):
        """
        Fit on features to compute mean and std
        
        Args:
            features: List of feature vectors
        """
        import numpy as np
        features_array = np.array(features)
        self.mean = np.mean(features_array, axis=0)
        self.std = np.std(features_array, axis=0)
        self.std = np.where(self.std == 0, 1.0, self.std)
    
    def process(self, features: List[float]) -> List[float]:
        """
        Process features
        
        Args:
            features: Feature vector
            
        Returns:
            Processed features
        """
        import numpy as np
        
        if self.normalize and self.mean is not None and self.std is not None:
            features = (np.array(features) - self.mean) / self.std
            return features.tolist()
        
        return features


class TextProcessor(BaseProcessor):
    """
    Process text data
    """
    
    def __init__(self, tokenizer: Optional[Any] = None, max_length: int = 512, **kwargs):
        """
        Initialize text processor
        
        Args:
            tokenizer: Tokenizer function
            max_length: Maximum sequence length
            **kwargs: Additional config
        """
        super().__init__(kwargs)
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Process text
        
        Args:
            text: Input text
            
        Returns:
            Processed text (tokenized)
        """
        if self.tokenizer:
            return self.tokenizer(
                text,
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=self.max_length
            )
        return {"text": text}


class SequenceProcessor(BaseProcessor):
    """
    Process sequence data
    """
    
    def __init__(self, sequence_length: int = 30, pad_value: float = 0.0, **kwargs):
        """
        Initialize sequence processor
        
        Args:
            sequence_length: Fixed sequence length
            pad_value: Padding value
            **kwargs: Additional config
        """
        super().__init__(kwargs)
        self.sequence_length = sequence_length
        self.pad_value = pad_value
    
    def process(self, sequence: List[List[float]]) -> List[List[float]]:
        """
        Process sequence
        
        Args:
            sequence: Input sequence
            
        Returns:
            Processed sequence (padded/truncated)
        """
        # Pad or truncate
        if len(sequence) < self.sequence_length:
            # Pad
            padding = [[self.pad_value] * len(sequence[0])] * (self.sequence_length - len(sequence))
            sequence = sequence + padding
        elif len(sequence) > self.sequence_length:
            # Truncate
            sequence = sequence[:self.sequence_length]
        
        return sequence













