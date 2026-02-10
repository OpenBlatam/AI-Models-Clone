"""
Recovery Dataset
PyTorch datasets for recovery data
"""

import torch
from torch.utils.data import Dataset
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RecoveryDataset(Dataset):
    """
    Base dataset for recovery data
    """
    
    def __init__(
        self,
        data: List[Dict[str, Any]],
        feature_keys: List[str],
        target_key: Optional[str] = None,
        transform: Optional[callable] = None
    ):
        """
        Initialize dataset
        
        Args:
            data: List of data samples
            feature_keys: Keys for feature extraction
            target_key: Key for target (if supervised)
            transform: Optional transform function
        """
        self.data = data
        self.feature_keys = feature_keys
        self.target_key = target_key
        self.transform = transform
    
    def __len__(self) -> int:
        """Get dataset length"""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get item by index
        
        Args:
            idx: Index
            
        Returns:
            Dictionary with features and optionally target
        """
        sample = self.data[idx]
        
        # Extract features
        features = []
        for key in self.feature_keys:
            if key in sample:
                features.append(float(sample[key]))
            else:
                features.append(0.0)
        
        features_tensor = torch.tensor(features, dtype=torch.float32)
        
        result = {"features": features_tensor}
        
        # Add target if available
        if self.target_key and self.target_key in sample:
            target = torch.tensor(float(sample[self.target_key]), dtype=torch.float32)
            result["target"] = target
        
        # Apply transform
        if self.transform:
            result = self.transform(result)
        
        return result


class SequenceDataset(Dataset):
    """
    Dataset for sequence data (LSTM, Transformer)
    """
    
    def __init__(
        self,
        sequences: List[np.ndarray],
        targets: Optional[List[float]] = None,
        sequence_length: int = 30,
        transform: Optional[callable] = None
    ):
        """
        Initialize sequence dataset
        
        Args:
            sequences: List of sequences
            targets: Optional targets
            sequence_length: Fixed sequence length
            transform: Optional transform
        """
        self.sequences = sequences
        self.targets = targets
        self.sequence_length = sequence_length
        self.transform = transform
    
    def __len__(self) -> int:
        """Get dataset length"""
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get item by index
        
        Args:
            idx: Index
            
        Returns:
            Dictionary with sequence and optionally target
        """
        sequence = self.sequences[idx]
        
        # Pad or truncate to fixed length
        if len(sequence) < self.sequence_length:
            # Pad with zeros
            padding = np.zeros((self.sequence_length - len(sequence), sequence.shape[1]))
            sequence = np.vstack([sequence, padding])
        elif len(sequence) > self.sequence_length:
            # Truncate
            sequence = sequence[:self.sequence_length]
        
        sequence_tensor = torch.tensor(sequence, dtype=torch.float32)
        
        result = {"sequence": sequence_tensor}
        
        if self.targets is not None:
            target = torch.tensor(float(self.targets[idx]), dtype=torch.float32)
            result["target"] = target
        
        if self.transform:
            result = self.transform(result)
        
        return result


class TextDataset(Dataset):
    """
    Dataset for text data (sentiment analysis, etc.)
    """
    
    def __init__(
        self,
        texts: List[str],
        labels: Optional[List[int]] = None,
        tokenizer: Optional[callable] = None,
        max_length: int = 512
    ):
        """
        Initialize text dataset
        
        Args:
            texts: List of texts
            labels: Optional labels
            tokenizer: Tokenizer function
            max_length: Maximum sequence length
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self) -> int:
        """Get dataset length"""
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """
        Get item by index
        
        Args:
            idx: Index
            
        Returns:
            Dictionary with tokenized text and optionally label
        """
        text = self.texts[idx]
        
        result = {"text": text}
        
        # Tokenize if tokenizer available
        if self.tokenizer:
            tokenized = self.tokenizer(
                text,
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=self.max_length
            )
            result.update({
                "input_ids": tokenized["input_ids"].squeeze(0),
                "attention_mask": tokenized["attention_mask"].squeeze(0)
            })
        
        if self.labels is not None:
            result["label"] = torch.tensor(self.labels[idx], dtype=torch.long)
        
        return result


def create_recovery_dataset(
    data: List[Dict[str, Any]],
    feature_keys: List[str],
    target_key: Optional[str] = None
) -> RecoveryDataset:
    """Factory for recovery dataset"""
    return RecoveryDataset(data, feature_keys, target_key)


def create_sequence_dataset(
    sequences: List[np.ndarray],
    targets: Optional[List[float]] = None,
    sequence_length: int = 30
) -> SequenceDataset:
    """Factory for sequence dataset"""
    return SequenceDataset(sequences, targets, sequence_length)


def create_text_dataset(
    texts: List[str],
    labels: Optional[List[int]] = None,
    tokenizer: Optional[callable] = None
) -> TextDataset:
    """Factory for text dataset"""
    return TextDataset(texts, labels, tokenizer)













