#!/usr/bin/env python3
"""
Enhanced DataLoader Utilities for Blaze AI
Provides efficient data loading with proper splits and cross-validation support
"""

import torch
from torch.utils.data import DataLoader, Dataset, Subset, random_split, WeightedRandomSampler
from torch.utils.data.distributed import DistributedSampler
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
import logging
from pathlib import Path
import json
import pickle
from collections import defaultdict
import warnings

# Import our data splitting utilities
try:
    from .data_splitting_and_validation import DataSplitter, DataSplitConfig, CrossValidator
except ImportError:
    from data_splitting_and_validation import DataSplitter, DataSplitConfig, CrossValidator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DataLoaderConfig:
    """Configuration for enhanced DataLoader creation"""
    
    # Basic settings
    batch_size: int = 32
    shuffle: bool = True
    num_workers: int = 4
    pin_memory: bool = True
    drop_last: bool = False
    persistent_workers: bool = True
    
    # Advanced settings
    prefetch_factor: int = 2
    timeout: int = 0
    worker_init_fn: Optional[Callable] = None
    
    # Memory optimization
    pin_memory_device: str = "cuda"
    memory_format: torch.memory_format = torch.contiguous_format
    
    # Distributed training
    distributed: bool = False
    world_size: int = 1
    rank: int = 0
    
    # Data augmentation
    augment_train: bool = True
    augment_val: bool = False
    augment_test: bool = False
    
    # Sampling strategies
    use_weighted_sampling: bool = False
    class_weights: Optional[Dict[int, float]] = None
    
    # Validation settings
    val_batch_size: Optional[int] = None
    test_batch_size: Optional[int] = None
    
    def __post_init__(self):
        """Set default batch sizes if not specified"""
        if self.val_batch_size is None:
            self.val_batch_size = self.batch_size
        if self.test_batch_size is None:
            self.test_batch_size = self.batch_size


class EnhancedDataset(Dataset):
    """Enhanced dataset with built-in splitting and cross-validation support"""
    
    def __init__(
        self, 
        data: Union[np.ndarray, pd.DataFrame, List, torch.Tensor],
        labels: Optional[Union[np.ndarray, List, torch.Tensor]] = None,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None,
        split_config: Optional[DataSplitConfig] = None
    ):
        """
        Initialize enhanced dataset
        
        Args:
            data: Input data
            labels: Target labels
            transform: Data transformation function
            target_transform: Target transformation function
            split_config: Configuration for data splitting
        """
        self.data = self._convert_to_tensor(data)
        self.labels = self._convert_to_tensor(labels) if labels is not None else None
        self.transform = transform
        self.target_transform = target_transform
        self.split_config = split_config or DataSplitConfig()
        
        # Initialize data splitter
        self.splitter = DataSplitter(self.split_config)
        self.splits = None
        self.split_datasets = {}
        
        # Validate data
        self._validate_data()
    
    def _convert_to_tensor(self, data: Union[np.ndarray, pd.DataFrame, List, torch.Tensor]) -> torch.Tensor:
        """Convert data to torch.Tensor"""
        if isinstance(data, torch.Tensor):
            return data
        elif isinstance(data, np.ndarray):
            return torch.from_numpy(data)
        elif isinstance(data, pd.DataFrame):
            return torch.from_numpy(data.values)
        elif isinstance(data, List):
            return torch.tensor(data)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
    
    def _validate_data(self):
        """Validate dataset consistency"""
        if self.labels is not None and len(self.data) != len(self.labels):
            raise ValueError(f"Data length ({len(self.data)}) != labels length ({len(self.labels)})")
        
        logger.info(f"Dataset initialized with {len(self.data)} samples")
        if self.labels is not None:
            unique_labels, counts = torch.unique(self.labels, return_counts=True)
            logger.info(f"Label distribution: {dict(zip(unique_labels.tolist(), counts.tolist()))}")
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Get item at index"""
        sample = self.data[idx]
        label = self.labels[idx] if self.labels is not None else None
        
        # Apply transforms
        if self.transform is not None:
            sample = self.transform(sample)
        
        if self.target_transform is not None and label is not None:
            label = self.target_transform(label)
        
        if label is not None:
            return sample, label
        else:
            return sample
    
    def create_splits(
        self, 
        groups: Optional[Union[np.ndarray, List]] = None,
        **kwargs
    ) -> Dict[str, 'EnhancedDataset']:
        """Create train/validation/test splits"""
        logger.info("Creating dataset splits...")
        
        # Convert data to numpy for splitting
        data_np = self.data.cpu().numpy()
        labels_np = self.labels.cpu().numpy() if self.labels is not None else None
        
        # Create splits
        splits = self.splitter.split_data(data_np, labels_np, groups, **kwargs)
        
        # Create subset datasets
        self.split_datasets = {
            'train': Subset(self, splits['train_idx']),
            'val': Subset(self, splits['val_idx']),
            'test': Subset(self, splits['test_idx'])
        }
        
        # Store split indices
        self.splits = splits
        
        logger.info(f"Dataset splits created: Train={len(self.split_datasets['train'])}, "
                   f"Val={len(self.split_datasets['val'])}, Test={len(self.split_datasets['test'])}")
        
        return self.split_datasets
    
    def get_split_dataset(self, split_name: str) -> Optional[Dataset]:
        """Get dataset for a specific split"""
        if split_name not in self.split_datasets:
            raise ValueError(f"Split '{split_name}' not found. Available splits: {list(self.split_datasets.keys())}")
        
        return self.split_datasets[split_name]
    
    def create_cross_validation_folds(
        self, 
        n_splits: int = 5,
        cv_type: str = "stratified",
        groups: Optional[Union[np.ndarray, List]] = None
    ) -> List[Dict[str, Dataset]]:
        """Create cross-validation folds"""
        logger.info(f"Creating {n_splits}-fold {cv_type} cross-validation...")
        
        # Update split config
        cv_config = DataSplitConfig(n_splits=n_splits)
        cv_validator = CrossValidator(cv_config)
        
        # Convert data to numpy for cross-validation
        data_np = self.data.cpu().numpy()
        labels_np = self.labels.cpu().numpy() if self.labels is not None else None
        
        # Perform cross-validation
        cv_results = cv_validator.cross_validate(data_np, labels_np, groups, cv_type)
        
        # Create fold datasets
        fold_datasets = []
        for fold_split in cv_results['fold_splits']:
            fold_dataset = {
                'train': Subset(self, fold_split['train_idx']),
                'val': Subset(self, fold_split['val_idx'])
            }
            fold_datasets.append(fold_dataset)
        
        logger.info(f"Cross-validation folds created: {len(fold_datasets)} folds")
        return fold_datasets


class EnhancedDataLoaderFactory:
    """Factory for creating optimized DataLoaders"""
    
    def __init__(self, config: DataLoaderConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def create_dataloader(
        self, 
        dataset: Dataset, 
        split_type: str = "train",
        **kwargs
    ) -> DataLoader:
        """
        Create optimized DataLoader for a specific split
        
        Args:
            dataset: PyTorch dataset
            split_type: Type of split ('train', 'val', 'test')
            **kwargs: Additional arguments to override config
        
        Returns:
            Optimized DataLoader
        """
        # Determine batch size based on split type
        if split_type == "train":
            batch_size = kwargs.get('batch_size', self.config.batch_size)
            shuffle = kwargs.get('shuffle', self.config.shuffle)
        elif split_type == "val":
            batch_size = kwargs.get('batch_size', self.config.val_batch_size)
            shuffle = kwargs.get('shuffle', False)  # Usually no shuffle for validation
        elif split_type == "test":
            batch_size = kwargs.get('batch_size', self.config.test_batch_size)
            shuffle = kwargs.get('shuffle', False)  # Usually no shuffle for test
        else:
            raise ValueError(f"Unknown split type: {split_type}")
        
        # Create sampler if using weighted sampling
        sampler = None
        if self.config.use_weighted_sampling and split_type == "train":
            sampler = self._create_weighted_sampler(dataset)
            shuffle = False  # Sampler and shuffle are mutually exclusive
        
        # Create distributed sampler if needed
        if self.config.distributed:
            sampler = DistributedSampler(
                dataset,
                num_replicas=self.config.world_size,
                rank=self.config.rank,
                shuffle=shuffle
            )
            shuffle = False
        
        # Create DataLoader
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            sampler=sampler,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
            drop_last=self.config.drop_last,
            persistent_workers=self.config.persistent_workers,
            prefetch_factor=self.config.prefetch_factor,
            timeout=self.config.timeout,
            worker_init_fn=self.config.worker_init_fn
        )
        
        logger.info(f"Created {split_type} DataLoader: batch_size={batch_size}, "
                   f"num_workers={self.config.num_workers}, pin_memory={self.config.pin_memory}")
        
        return dataloader
    
    def _create_weighted_sampler(self, dataset: Dataset) -> WeightedRandomSampler:
        """Create weighted random sampler for imbalanced datasets"""
        if self.config.class_weights is None:
            raise ValueError("Class weights must be provided for weighted sampling")
        
        # Get labels from dataset
        if hasattr(dataset, 'labels'):
            labels = dataset.labels
        elif hasattr(dataset, 'targets'):
            labels = dataset.targets
        else:
            # Try to extract labels from the first few samples
            labels = []
            for i in range(min(100, len(dataset))):
                try:
                    _, label = dataset[i]
                    labels.append(label)
                except (ValueError, IndexError):
                    continue
            
            if not labels:
                raise ValueError("Could not extract labels for weighted sampling")
        
        # Convert labels to tensor if needed
        if not isinstance(labels, torch.Tensor):
            labels = torch.tensor(labels)
        
        # Create sample weights
        sample_weights = torch.zeros(len(dataset))
        for class_idx, weight in self.config.class_weights.items():
            mask = (labels == class_idx)
            sample_weights[mask] = weight
        
        return WeightedRandomSampler(
            weights=sample_weights,
            num_samples=len(dataset),
            replacement=True
        )
    
    def create_split_dataloaders(
        self, 
        enhanced_dataset: EnhancedDataset,
        **kwargs
    ) -> Dict[str, DataLoader]:
        """Create DataLoaders for all splits"""
        if not enhanced_dataset.split_datasets:
            raise ValueError("Dataset splits not created. Call create_splits() first.")
        
        dataloaders = {}
        for split_name, split_dataset in enhanced_dataset.split_datasets.items():
            dataloaders[split_name] = self.create_dataloader(
                split_dataset, 
                split_type=split_name,
                **kwargs
            )
        
        return dataloaders
    
    def create_cv_dataloaders(
        self, 
        enhanced_dataset: EnhancedDataset,
        n_folds: int = 5,
        cv_type: str = "stratified",
        **kwargs
    ) -> List[Dict[str, DataLoader]]:
        """Create DataLoaders for cross-validation folds"""
        # Create cross-validation folds
        fold_datasets = enhanced_dataset.create_cross_validation_folds(n_folds, cv_type)
        
        # Create DataLoaders for each fold
        fold_dataloaders = []
        for fold_idx, fold_dataset in enumerate(fold_datasets):
            fold_dataloader = {
                'train': self.create_dataloader(fold_dataset['train'], 'train', **kwargs),
                'val': self.create_dataloader(fold_dataset['val'], 'val', **kwargs)
            }
            fold_dataloaders.append(fold_dataloader)
            
            logger.info(f"Created DataLoaders for fold {fold_idx + 1}")
        
        return fold_dataloaders


class DataLoaderOptimizer:
    """Optimizes DataLoader performance and memory usage"""
    
    @staticmethod
    def optimize_for_gpu(
        config: DataLoaderConfig,
        gpu_memory_gb: float = 8.0,
        gpu_memory_fraction: float = 0.8
    ) -> DataLoaderConfig:
        """Optimize DataLoader configuration for GPU training"""
        logger.info(f"Optimizing DataLoader for GPU with {gpu_memory_gb}GB memory...")
        
        # Calculate optimal batch size based on GPU memory
        available_memory = gpu_memory_gb * gpu_memory_fraction
        
        # Estimate memory per sample (this is a rough estimate)
        # In practice, you'd want to profile your specific model and data
        estimated_memory_per_sample = 0.001  # GB per sample (adjust based on your data)
        
        optimal_batch_size = int(available_memory / estimated_memory_per_sample)
        optimal_batch_size = max(1, min(optimal_batch_size, 128))  # Clamp between 1 and 128
        
        # Update configuration
        config.batch_size = optimal_batch_size
        config.val_batch_size = optimal_batch_size
        config.test_batch_size = optimal_batch_size
        
        # Optimize number of workers
        if torch.cuda.is_available():
            config.num_workers = min(8, torch.cuda.device_count() * 2)
            config.pin_memory = True
            config.persistent_workers = True
        else:
            config.num_workers = min(4, os.cpu_count() or 4)
            config.pin_memory = False
            config.persistent_workers = False
        
        logger.info(f"Optimized batch size: {optimal_batch_size}, num_workers: {config.num_workers}")
        return config
    
    @staticmethod
    def profile_dataloader(
        dataloader: DataLoader,
        num_batches: int = 10
    ) -> Dict[str, float]:
        """Profile DataLoader performance"""
        logger.info(f"Profiling DataLoader performance over {num_batches} batches...")
        
        import time
        
        # Warm up
        for i, batch in enumerate(dataloader):
            if i >= 2:
                break
        
        # Profile
        start_time = time.time()
        batch_times = []
        
        for i, batch in enumerate(dataloader):
            if i >= num_batches:
                break
            
            batch_start = time.time()
            _ = batch  # Just iterate, don't process
            batch_time = time.time() - batch_start
            batch_times.append(batch_time)
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        avg_batch_time = np.mean(batch_times)
        std_batch_time = np.std(batch_times)
        samples_per_second = (num_batches * dataloader.batch_size) / total_time
        
        profile_results = {
            'total_time': total_time,
            'avg_batch_time': avg_batch_time,
            'std_batch_time': std_batch_time,
            'samples_per_second': samples_per_second,
            'throughput_gb_per_second': samples_per_second * 0.001  # Rough estimate
        }
        
        logger.info(f"Profile results: {samples_per_second:.1f} samples/sec, "
                   f"avg batch time: {avg_batch_time:.3f}s ± {std_batch_time:.3f}s")
        
        return profile_results


def demonstrate_enhanced_dataloader():
    """Demonstrate enhanced DataLoader functionality"""
    logger.info("Demonstrating enhanced DataLoader utilities...")
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    n_classes = 3
    
    # Generate synthetic data
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, n_classes, n_samples)
    
    logger.info(f"Generated {n_samples} samples with {n_features} features and {n_classes} classes")
    
    # 1. Create enhanced dataset
    logger.info("\n1. Creating Enhanced Dataset")
    dataset = EnhancedDataset(X, y)
    
    # 2. Create data splits
    logger.info("\n2. Creating Data Splits")
    split_datasets = dataset.create_splits()
    
    # 3. Configure DataLoader
    logger.info("\n3. Configuring Enhanced DataLoader")
    dataloader_config = DataLoaderConfig(
        batch_size=32,
        num_workers=2,
        pin_memory=True,
        persistent_workers=True
    )
    
    # 4. Create DataLoader factory
    factory = EnhancedDataLoaderFactory(dataloader_config)
    
    # 5. Create DataLoaders for all splits
    logger.info("\n4. Creating DataLoaders for All Splits")
    split_dataloaders = factory.create_split_dataloaders(dataset)
    
    # 6. Demonstrate usage
    logger.info("\n5. Demonstrating DataLoader Usage")
    for split_name, dataloader in split_dataloaders.items():
        logger.info(f"\n{split_name.upper()} DataLoader:")
        logger.info(f"  Batch size: {dataloader.batch_size}")
        logger.info(f"  Number of batches: {len(dataloader)}")
        logger.info(f"  Total samples: {len(dataloader.dataset)}")
        
        # Get first batch
        first_batch = next(iter(dataloader))
        if isinstance(first_batch, (list, tuple)):
            data, labels = first_batch
            logger.info(f"  First batch shape: data={data.shape}, labels={labels.shape}")
        else:
            logger.info(f"  First batch shape: {first_batch.shape}")
    
    # 7. Cross-validation
    logger.info("\n6. Creating Cross-Validation DataLoaders")
    cv_dataloaders = factory.create_cv_dataloaders(dataset, n_folds=3)
    
    logger.info(f"Created {len(cv_dataloaders)} cross-validation folds")
    for fold_idx, fold_dataloaders in enumerate(cv_dataloaders):
        logger.info(f"  Fold {fold_idx + 1}: "
                   f"Train={len(fold_dataloaders['train'].dataset)}, "
                   f"Val={len(fold_dataloaders['val'].dataset)}")
    
    # 8. Performance profiling
    logger.info("\n7. Profiling DataLoader Performance")
    profile_results = DataLoaderOptimizer.profile_dataloader(split_dataloaders['train'], num_batches=5)
    
    logger.info("Enhanced DataLoader demonstration completed!")
    
    return {
        'dataset': dataset,
        'split_datasets': split_datasets,
        'split_dataloaders': split_dataloaders,
        'cv_dataloaders': cv_dataloaders,
        'profile_results': profile_results
    }


if __name__ == "__main__":
    # Run demonstration
    results = demonstrate_enhanced_dataloader()
    
    # Print summary
    print("\n" + "="*60)
    print("ENHANCED DATALOADER SUMMARY")
    print("="*60)
    
    print(f"\nDataset Information:")
    print(f"  Total samples: {len(results['dataset'])}")
    print(f"  Features: {results['dataset'].data.shape[1]}")
    print(f"  Classes: {len(torch.unique(results['dataset'].labels))}")
    
    print(f"\nDataLoader Information:")
    for split_name, dataloader in results['split_dataloaders'].items():
        print(f"  {split_name.upper()}: {len(dataloader.dataset)} samples, "
              f"{len(dataloader)} batches, batch_size={dataloader.batch_size}")
    
    print(f"\nCross-Validation:")
    print(f"  Folds: {len(results['cv_dataloaders'])}")
    
    print(f"\nPerformance Profile:")
    profile = results['profile_results']
    print(f"  Throughput: {profile['samples_per_second']:.1f} samples/sec")
    print(f"  Avg batch time: {profile['avg_batch_time']:.3f}s")
    
    print("\n" + "="*60)
