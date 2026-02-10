"""
Custom Collate Functions
Specialized collate functions for data loading
"""

import torch
from torch.utils.data import DataLoader
from typing import Any, List, Dict
import numpy as np


class CustomCollateFn:
    """
    Custom collate functions for different data types
    """
    
    @staticmethod
    def collate_with_padding(batch: List[tuple]) -> tuple:
        """
        Collate function with padding for variable-length sequences
        
        Args:
            batch: List of (input, target) tuples
            
        Returns:
            Batched tensors
        """
        inputs, targets = zip(*batch)
        
        # Pad inputs to same length
        max_len = max(inp.shape[0] for inp in inputs)
        padded_inputs = []
        
        for inp in inputs:
            if inp.dim() == 1:
                padding = torch.zeros(max_len - inp.shape[0])
                padded = torch.cat([inp, padding])
            else:
                padding = torch.zeros(max_len - inp.shape[0], *inp.shape[1:])
                padded = torch.cat([inp, padding], dim=0)
            padded_inputs.append(padded)
        
        return torch.stack(padded_inputs), torch.tensor(targets)
    
    @staticmethod
    def collate_with_metadata(batch: List[tuple]) -> Dict[str, Any]:
        """
        Collate function that preserves metadata
        
        Args:
            batch: List of (input, target, metadata) tuples
            
        Returns:
            Dictionary with batched data and metadata
        """
        inputs, targets, metadata = zip(*batch)
        
        return {
            'inputs': torch.stack(inputs),
            'targets': torch.tensor(targets),
            'metadata': metadata,
        }
    
    @staticmethod
    def collate_multi_input(batch: List[tuple]) -> Dict[str, torch.Tensor]:
        """
        Collate function for multiple inputs
        
        Args:
            batch: List of (input1, input2, ..., target) tuples
            
        Returns:
            Dictionary with batched inputs
        """
        *inputs, targets = zip(*batch)
        
        result = {
            f'input_{i}': torch.stack(inp) for i, inp in enumerate(inputs)
        }
        result['targets'] = torch.tensor(targets)
        
        return result



