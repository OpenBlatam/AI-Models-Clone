"""
Data Validation
Validates datasets and data loaders
"""

from typing import List, Dict, Any, Optional
import torch
from torch.utils.data import Dataset, DataLoader
import logging

from ml.common.validators import InputValidator
from ml.common.errors import DataError, ValidationError

logger = logging.getLogger(__name__)


class DatasetValidator:
    """Validate datasets"""
    
    @staticmethod
    def validate_dataset(
        dataset: Dataset,
        num_samples: int = 5,
        check_labels: bool = True
    ) -> Dict[str, Any]:
        """
        Validate dataset
        
        Args:
            dataset: PyTorch dataset
            num_samples: Number of samples to check
            check_labels: Whether to check labels
            
        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'num_samples': len(dataset),
            'sample_shapes': []
        }
        
        if len(dataset) == 0:
            results['valid'] = False
            results['errors'].append("Dataset is empty")
            return results
        
        # Check samples
        for i in range(min(num_samples, len(dataset))):
            try:
                sample = dataset[i]
                
                # Check structure
                if not isinstance(sample, dict):
                    results['warnings'].append(f"Sample {i} is not a dictionary")
                    continue
                
                # Check image
                if 'image' in sample:
                    image = sample['image']
                    if isinstance(image, torch.Tensor):
                        results['sample_shapes'].append({
                            'index': i,
                            'image_shape': tuple(image.shape)
                        })
                        
                        # Validate tensor
                        if not InputValidator.validate_tensor(image):
                            results['errors'].append(f"Invalid image tensor at index {i}")
                            results['valid'] = False
                
                # Check labels if requested
                if check_labels:
                    for key in ['conditions', 'metrics', 'labels']:
                        if key in sample:
                            label = sample[key]
                            if isinstance(label, torch.Tensor):
                                if not InputValidator.validate_tensor(label):
                                    results['errors'].append(
                                        f"Invalid label '{key}' tensor at index {i}"
                                    )
                                    results['valid'] = False
                                
            except Exception as e:
                results['valid'] = False
                results['errors'].append(f"Error accessing sample {i}: {e}")
        
        return results
    
    @staticmethod
    def validate_data_loader(
        data_loader: DataLoader,
        num_batches: int = 3
    ) -> Dict[str, Any]:
        """
        Validate data loader
        
        Args:
            data_loader: PyTorch DataLoader
            num_batches: Number of batches to check
            
        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'batch_size': data_loader.batch_size,
            'num_workers': data_loader.num_workers
        }
        
        try:
            for batch_idx, batch in enumerate(data_loader):
                if batch_idx >= num_batches:
                    break
                
                # Validate batch
                if not InputValidator.validate_batch(batch, required_keys=['image']):
                    results['valid'] = False
                    results['errors'].append(f"Invalid batch {batch_idx}")
                
                # Check batch size
                if 'image' in batch:
                    actual_batch_size = batch['image'].shape[0]
                    if actual_batch_size != data_loader.batch_size and batch_idx == len(data_loader) - 1:
                        # Last batch can be smaller
                        pass
                    elif actual_batch_size != data_loader.batch_size:
                        results['warnings'].append(
                            f"Batch {batch_idx} size mismatch: "
                            f"{actual_batch_size} != {data_loader.batch_size}"
                        )
                
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f"Error iterating data loader: {e}")
        
        return results













