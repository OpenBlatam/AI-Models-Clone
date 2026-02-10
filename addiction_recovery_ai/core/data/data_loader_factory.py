"""
Data Loader Factory
Factory for creating data loaders with proper train/val/test splits and cross-validation
"""

from typing import Optional, Dict, Any, List, Tuple
from torch.utils.data import Dataset, DataLoader, random_split, Subset
from sklearn.model_selection import KFold, StratifiedKFold
import numpy as np
import logging

logger = logging.getLogger(__name__)


class DataLoaderFactory:
    """
    Factory for creating data loaders with different configurations
    """
    
    @staticmethod
    def create(
        dataset: Dataset,
        config: Optional[Dict[str, Any]] = None,
        split: str = "train"
    ) -> DataLoader:
        """
        Create data loader
        
        Args:
            dataset: PyTorch dataset
            config: Data loader configuration
            split: Data split (train, val, test)
            
        Returns:
            DataLoader instance
        """
        config = config or {}
        
        # Default configurations
        defaults = {
            "train": {
                "batch_size": 32,
                "shuffle": True,
                "num_workers": 4,
                "pin_memory": True,
                "prefetch_factor": 2,
                "persistent_workers": True,
                "drop_last": False
            },
            "val": {
                "batch_size": 32,
                "shuffle": False,
                "num_workers": 4,
                "pin_memory": True,
                "prefetch_factor": 2,
                "persistent_workers": True,
                "drop_last": False
            },
            "test": {
                "batch_size": 32,
                "shuffle": False,
                "num_workers": 4,
                "pin_memory": True,
                "prefetch_factor": 2,
                "persistent_workers": True,
                "drop_last": False
            }
        }
        
        # Merge config with defaults
        loader_config = {**defaults.get(split, defaults["train"]), **config}
        
        return DataLoader(dataset, **loader_config)
    
    @staticmethod
    def create_optimized(
        dataset: Dataset,
        batch_size: int = 64,
        num_workers: int = 4,
        pin_memory: bool = True,
        prefetch_factor: int = 2,
        persistent_workers: bool = True
    ) -> DataLoader:
        """
        Create optimized data loader for inference
        
        Args:
            dataset: PyTorch dataset
            batch_size: Batch size
            num_workers: Number of workers
            pin_memory: Pin memory
            prefetch_factor: Prefetch factor
            persistent_workers: Keep workers alive
            
        Returns:
            Optimized DataLoader
        """
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
            prefetch_factor=prefetch_factor,
            persistent_workers=persistent_workers,
            drop_last=False
        )
    
    @staticmethod
    def split_dataset(
        dataset: Dataset,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: Optional[int] = None
    ) -> Tuple[Dataset, Dataset, Dataset]:
        """
        Split dataset into train/val/test with proper ratios
        
        Args:
            dataset: Full dataset
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            seed: Random seed for reproducibility
            
        Returns:
            Tuple of (train_dataset, val_dataset, test_dataset)
        """
        # Validate ratios
        total_ratio = train_ratio + val_ratio + test_ratio
        if abs(total_ratio - 1.0) > 1e-6:
            raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")
        
        # Set seed
        if seed is not None:
            generator = torch.Generator().manual_seed(seed)
        else:
            generator = None
        
        # Calculate sizes
        total_size = len(dataset)
        train_size = int(train_ratio * total_size)
        val_size = int(val_ratio * total_size)
        test_size = total_size - train_size - val_size
        
        # Split
        train_dataset, val_dataset, test_dataset = random_split(
            dataset,
            [train_size, val_size, test_size],
            generator=generator
        )
        
        logger.info(
            f"Dataset split: train={len(train_dataset)}, "
            f"val={len(val_dataset)}, test={len(test_dataset)}"
        )
        
        return train_dataset, val_dataset, test_dataset
    
    @staticmethod
    def create_cv_splits(
        dataset: Dataset,
        n_splits: int = 5,
        stratified: bool = False,
        labels: Optional[np.ndarray] = None,
        seed: Optional[int] = None
    ) -> List[Tuple[Dataset, Dataset]]:
        """
        Create cross-validation splits
        
        Args:
            dataset: Full dataset
            n_splits: Number of CV folds
            stratified: Use stratified K-Fold (requires labels)
            labels: Labels for stratified splitting
            seed: Random seed
            
        Returns:
            List of (train_dataset, val_dataset) tuples
        """
        if stratified and labels is None:
            raise ValueError("Labels required for stratified K-Fold")
        
        # Create K-Fold splitter
        if stratified:
            kfold = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
            splits = list(kfold.split(np.arange(len(dataset)), labels))
        else:
            kfold = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
            splits = list(kfold.split(np.arange(len(dataset))))
        
        # Create dataset splits
        cv_datasets = []
        for train_indices, val_indices in splits:
            train_dataset = Subset(dataset, train_indices)
            val_dataset = Subset(dataset, val_indices)
            cv_datasets.append((train_dataset, val_dataset))
        
        logger.info(f"Created {n_splits} CV splits")
        
        return cv_datasets
    
    @staticmethod
    def create_data_loaders(
        train_dataset: Dataset,
        val_dataset: Optional[Dataset] = None,
        test_dataset: Optional[Dataset] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, DataLoader]:
        """
        Create data loaders for train/val/test splits
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset (optional)
            test_dataset: Test dataset (optional)
            config: Data loader configuration
            
        Returns:
            Dictionary with 'train', 'val', 'test' data loaders
        """
        loaders = {}
        
        # Training loader
        train_config = config.get('train', {}) if config else {}
        loaders['train'] = DataLoaderFactory.create(
            train_dataset,
            config=train_config,
            split='train'
        )
        
        # Validation loader
        if val_dataset is not None:
            val_config = config.get('val', {}) if config else {}
            loaders['val'] = DataLoaderFactory.create(
                val_dataset,
                config=val_config,
                split='val'
            )
        
        # Test loader
        if test_dataset is not None:
            test_config = config.get('test', {}) if config else {}
            loaders['test'] = DataLoaderFactory.create(
                test_dataset,
                config=test_config,
                split='test'
            )
        
        return loaders






