from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import torch
from torch.utils.data import Dataset, DataLoader, random_split
from typing import Dict, Any, Tuple, List, Optional, Callable
import numpy as np
from functools import partial
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Functional Data Processing for Deep Learning Framework
Uses pure functions instead of classes for data operations
"""


def create_tensor_dataset(data: np.ndarray, labels: np.ndarray) -> torch.utils.data.TensorDataset:
    """Create tensor dataset from numpy arrays."""
    return torch.utils.data.TensorDataset(
        torch.FloatTensor(data),
        torch.LongTensor(labels)
    )

def create_data_loader(dataset: Dataset, batch_size: int = 32, 
                      shuffle: bool = True, num_workers: int = 4) -> DataLoader:
    """Create data loader with standard configuration."""
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory: bool = True
    )

def split_dataset(dataset: Dataset, train_ratio: float = 0.7, 
                 val_ratio: float = 0.15, test_ratio: float = 0.15) -> Tuple[Dataset, Dataset, Dataset]:
    """Split dataset into train/val/test sets."""
    total_size = len(dataset)
    train_size = int(train_ratio * total_size)
    val_size = int(val_ratio * total_size)
    test_size = total_size - train_size - val_size
    
    return random_split(dataset, [train_size, val_size, test_size])

def normalize_data(data: np.ndarray, scaler: Optional[StandardScaler] = None) -> Tuple[np.ndarray, StandardScaler]:
    """Normalize data using StandardScaler."""
    if scaler is None:
        scaler = StandardScaler()
        data_normalized = scaler.fit_transform(data)
    else:
        data_normalized = scaler.transform(data)
    
    return data_normalized, scaler

def encode_labels(labels: np.ndarray, encoder: Optional[LabelEncoder] = None) -> Tuple[np.ndarray, LabelEncoder]:
    """Encode categorical labels."""
    if encoder is None:
        encoder = LabelEncoder()
        labels_encoded = encoder.fit_transform(labels)
    else:
        labels_encoded = encoder.transform(labels)
    
    return labels_encoded, encoder

def load_csv_data(filepath: str, target_column: str, 
                  feature_columns: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Load data from CSV file."""
    df = pd.read_csv(filepath)
    
    if feature_columns is None:
        feature_columns: List[Any] = [col for col in df.columns if col != target_column]
    
    X = df[feature_columns].values
    y = df[target_column].values
    
    return X, y

def preprocess_data(X: np.ndarray, y: np.ndarray, 
                   normalize: bool = True, encode_labels: bool = True) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """Preprocess data with normalization and label encoding."""
    preprocessing_info: Dict[str, Any] = {}
    
    # Normalize features
    if normalize:
        X, scaler = normalize_data(X)
        preprocessing_info['scaler'] = scaler
    
    # Encode labels
    if encode_labels and y.dtype == 'object':
        y, encoder = encode_labels(y)
        preprocessing_info['label_encoder'] = encoder
    
    return X, y, preprocessing_info

def create_data_loaders(X: np.ndarray, y: np.ndarray, 
                       batch_size: int = 32, train_ratio: float = 0.7,
                       val_ratio: float = 0.15, test_ratio: float = 0.15) -> Dict[str, DataLoader]:
    """Create train/val/test data loaders."""
    
    # Preprocess data
    X_processed, y_processed, preprocessing_info = preprocess_data(X, y)
    
    # Create dataset
    dataset = create_tensor_dataset(X_processed, y_processed)
    
    # Split dataset
    train_dataset, val_dataset, test_dataset = split_dataset(
        dataset, train_ratio, val_ratio, test_ratio
    )
    
    # Create data loaders
    train_loader = create_data_loader(train_dataset, batch_size, shuffle=True)
    val_loader = create_data_loader(val_dataset, batch_size, shuffle=False)
    test_loader = create_data_loader(test_dataset, batch_size, shuffle=False)
    
    return {
        'train_loader': train_loader,
        'val_loader': val_loader,
        'test_loader': test_loader,
        'preprocessing_info': preprocessing_info
    }

def augment_image_data(images: torch.Tensor, 
                      rotation_range: float = 10.0,
                      horizontal_flip: bool = True,
                      vertical_flip: bool = False) -> torch.Tensor:
    """Apply data augmentation to image data."""
    augmented_images: List[Any] = []
    
    for image in images:
        # Random rotation
        if rotation_range > 0:
            angle = torch.rand(1).item() * 2 * rotation_range - rotation_range
            image = torch.rot90(image, k=int(angle // 90))
        
        # Random horizontal flip
        if horizontal_flip and torch.rand(1).item() > 0.5:
            image = torch.flip(image, dims=[-1])
        
        # Random vertical flip
        if vertical_flip and torch.rand(1).item() > 0.5:
            image = torch.flip(image, dims=[-2])
        
        augmented_images.append(image)
    
    return torch.stack(augmented_images)

def create_custom_dataset(data: torch.Tensor, labels: torch.Tensor,
                         transform: Optional[Callable] = None) -> torch.utils.data.TensorDataset:
    """Create custom dataset with optional transforms."""
    if transform is not None:
        data = transform(data)
    
    return torch.utils.data.TensorDataset(data, labels)

def get_dataset_info(dataset: Dataset) -> Dict[str, Any]:
    """Get information about dataset."""
    if hasattr(dataset, 'tensors'):
        # TensorDataset
        data_tensor = dataset.tensors[0]
        labels_tensor = dataset.tensors[1]
        
        return {
            'num_samples': len(dataset),
            'input_shape': data_tensor.shape[1:],
            'num_classes': len(torch.unique(labels_tensor)),
            'class_distribution': torch.bincount(labels_tensor).tolist(),
            'data_type': str(data_tensor.dtype),
            'labels_type': str(labels_tensor.dtype)
        }
    else:
        # Generic dataset
        sample_data, sample_label = dataset[0]
        return {
            'num_samples': len(dataset),
            'input_shape': sample_data.shape,
            'label_shape': sample_label.shape if hasattr(sample_label, 'shape') else None,
            'data_type': str(sample_data.dtype),
            'labels_type': str(type(sample_label))
        }

def create_balanced_sampler(labels: torch.Tensor) -> torch.utils.data.WeightedRandomSampler:
    """Create balanced sampler for imbalanced datasets."""
    class_counts = torch.bincount(labels)
    class_weights = 1.0 / class_counts
    sample_weights = class_weights[labels]
    
    return torch.utils.data.WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(labels),
        replacement: bool = True
    )

def create_data_loader_with_sampler(dataset: Dataset, sampler: torch.utils.data.Sampler,
                                   batch_size: int = 32, num_workers: int = 4) -> DataLoader:
    """Create data loader with custom sampler."""
    return DataLoader(
        dataset,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=num_workers,
        pin_memory: bool = True
    )

def extract_features_from_data_loader(data_loader: DataLoader) -> Tuple[np.ndarray, np.ndarray]:
    """Extract all features and labels from data loader."""
    all_features: List[Any] = []
    all_labels: List[Any] = []
    
    for features, labels in data_loader:
        all_features.append(features.numpy())
        all_labels.append(labels.numpy())
    
    return np.concatenate(all_features), np.concatenate(all_labels)

def create_memory_efficient_loader(dataset: Dataset, batch_size: int = 32,
                                 shuffle: bool = True, num_workers: int = 4) -> DataLoader:
    """Create memory-efficient data loader."""
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=False,  # Disable pin_memory for memory efficiency
        persistent_workers=True if num_workers > 0 else False
    )

# Usage examples
if __name__ == "__main__":
    # Create dummy data
    X = np.random.randn(1000, 784)
    y = np.random.randint(0, 10, 1000)
    
    # Create data loaders
    loaders = create_data_loaders(X, y, batch_size=32)
    
    # Get dataset information
    train_info = get_dataset_info(loaders['train_loader'].dataset)
    print(f"Train dataset info: {train_info}")
    
    # Extract features
    X_train, y_train = extract_features_from_data_loader(loaders['train_loader'])
    print(f"Extracted features shape: {X_train.shape}")
    print(f"Extracted labels shape: {y_train.shape}") 