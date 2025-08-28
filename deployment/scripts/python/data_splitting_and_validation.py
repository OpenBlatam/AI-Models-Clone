#!/usr/bin/env python3
"""
Data Splitting and Validation Utilities for Blaze AI
Implements proper train/validation/test splits and cross-validation strategies
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from sklearn.model_selection import (
    train_test_split, KFold, StratifiedKFold, GroupKFold, 
    TimeSeriesSplit, ShuffleSplit, StratifiedShuffleSplit
)
from sklearn.preprocessing import LabelEncoder
import logging
from pathlib import Path
import json
import pickle
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DataSplitConfig:
    """Configuration for data splitting strategies"""
    
    # Split ratios
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    
    # Cross-validation settings
    n_splits: int = 5
    shuffle: bool = True
    random_state: int = 42
    
    # Stratification settings
    stratify: bool = True
    group_by: Optional[str] = None
    
    # Time series settings
    is_time_series: bool = False
    time_column: Optional[str] = None
    
    # Validation settings
    validate_splits: bool = True
    min_samples_per_split: int = 10
    
    # Output settings
    save_splits: bool = True
    splits_dir: str = "./data_splits"
    
    def __post_init__(self):
        """Validate configuration"""
        total_ratio = self.train_ratio + self.val_ratio + self.test_ratio
        if abs(total_ratio - 1.0) > 1e-6:
            raise ValueError(f"Split ratios must sum to 1.0, got {total_ratio}")
        
        if self.n_splits < 2:
            raise ValueError(f"n_splits must be >= 2, got {self.n_splits}")
        
        if self.min_samples_per_split < 1:
            raise ValueError(f"min_samples_per_split must be >= 1, got {self.min_samples_per_split}")


class DataSplitter:
    """Handles data splitting for deep learning workflows"""
    
    def __init__(self, config: DataSplitConfig):
        self.config = config
        self.splits = {}
        self.split_info = {}
        
        # Create splits directory
        if self.config.save_splits:
            Path(self.config.splits_dir).mkdir(parents=True, exist_ok=True)
    
    def split_data(
        self, 
        data: Union[pd.DataFrame, np.ndarray, List, torch.Tensor],
        labels: Optional[Union[np.ndarray, List, torch.Tensor]] = None,
        groups: Optional[Union[np.ndarray, List]] = None,
        **kwargs
    ) -> Dict[str, Union[np.ndarray, torch.Tensor, List]]:
        """
        Split data into train/validation/test sets
        
        Args:
            data: Input data to split
            labels: Target labels for stratification
            groups: Group identifiers for group-based splitting
            **kwargs: Additional arguments for specific split methods
            
        Returns:
            Dictionary containing train, validation, and test splits
        """
        logger.info("Starting data splitting process...")
        
        # Convert data to numpy array if needed
        if isinstance(data, torch.Tensor):
            data_np = data.cpu().numpy()
        elif isinstance(data, pd.DataFrame):
            data_np = data.values
        elif isinstance(data, List):
            data_np = np.array(data)
        else:
            data_np = data
        
        # Convert labels to numpy array if needed
        if labels is not None:
            if isinstance(labels, torch.Tensor):
                labels_np = labels.cpu().numpy()
            elif isinstance(labels, List):
                labels_np = np.array(labels)
            else:
                labels_np = labels
        else:
            labels_np = None
        
        # Determine split method based on configuration
        if self.config.is_time_series:
            splits = self._time_series_split(data_np, labels_np, **kwargs)
        elif self.config.group_by and groups is not None:
            splits = self._group_split(data_np, labels_np, groups, **kwargs)
        elif self.config.stratify and labels_np is not None:
            splits = self._stratified_split(data_np, labels_np, **kwargs)
        else:
            splits = self._random_split(data_np, labels_np, **kwargs)
        
        # Validate splits
        if self.config.validate_splits:
            self._validate_splits(splits, data_np, labels_np)
        
        # Store splits
        self.splits = splits
        self._store_split_info(data_np, labels_np)
        
        # Save splits if configured
        if self.config.save_splits:
            self._save_splits(splits)
        
        logger.info("Data splitting completed successfully")
        return splits
    
    def _random_split(
        self, 
        data: np.ndarray, 
        labels: Optional[np.ndarray] = None
    ) -> Dict[str, np.ndarray]:
        """Random split without stratification"""
        logger.info("Using random split strategy")
        
        # First split: train vs (val + test)
        train_size = self.config.train_ratio
        temp_size = self.config.val_ratio + self.config.test_ratio
        
        train_idx, temp_idx = train_test_split(
            range(len(data)),
            train_size=train_size,
            test_size=temp_size,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle
        )
        
        # Second split: validation vs test
        val_ratio_adjusted = self.config.val_ratio / temp_size
        val_idx, test_idx = train_test_split(
            temp_idx,
            train_size=val_ratio_adjusted,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle
        )
        
        return {
            'train': data[train_idx],
            'val': data[val_idx],
            'test': data[test_idx],
            'train_idx': train_idx,
            'val_idx': val_idx,
            'test_idx': test_idx
        }
    
    def _stratified_split(
        self, 
        data: np.ndarray, 
        labels: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Stratified split maintaining class distribution"""
        logger.info("Using stratified split strategy")
        
        # First split: train vs (val + test)
        train_size = self.config.train_ratio
        temp_size = self.config.val_ratio + self.config.test_ratio
        
        train_idx, temp_idx = train_test_split(
            range(len(data)),
            train_size=train_size,
            test_size=temp_size,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle,
            stratify=labels
        )
        
        # Second split: validation vs test
        val_ratio_adjusted = self.config.val_ratio / temp_size
        temp_labels = labels[temp_idx]
        
        val_idx, test_idx = train_test_split(
            temp_idx,
            train_size=val_ratio_adjusted,
            random_state=self.config.random_state,
            shuffle=self.config.shuffle,
            stratify=temp_labels
        )
        
        return {
            'train': data[train_idx],
            'val': data[val_idx],
            'test': data[test_idx],
            'train_idx': train_idx,
            'val_idx': val_idx,
            'test_idx': test_idx
        }
    
    def _group_split(
        self, 
        data: np.ndarray, 
        labels: Optional[np.ndarray], 
        groups: Union[np.ndarray, List]
    ) -> Dict[str, np.ndarray]:
        """Group-based split ensuring groups don't overlap between splits"""
        logger.info("Using group-based split strategy")
        
        # Convert groups to numpy array
        if isinstance(groups, List):
            groups = np.array(groups)
        
        unique_groups = np.unique(groups)
        n_groups = len(unique_groups)
        
        # Calculate group sizes for each split
        train_groups = int(n_groups * self.config.train_ratio)
        val_groups = int(n_groups * self.config.val_ratio)
        test_groups = n_groups - train_groups - val_groups
        
        # Shuffle groups
        if self.config.shuffle:
            np.random.seed(self.config.random_state)
            np.random.shuffle(unique_groups)
        
        # Assign groups to splits
        train_group_ids = unique_groups[:train_groups]
        val_group_ids = unique_groups[train_groups:train_groups + val_groups]
        test_group_ids = unique_groups[train_groups + val_groups:]
        
        # Get indices for each split
        train_idx = np.where(np.isin(groups, train_group_ids))[0]
        val_idx = np.where(np.isin(groups, val_group_ids))[0]
        test_idx = np.where(np.isin(groups, test_group_ids))[0]
        
        return {
            'train': data[train_idx],
            'val': data[val_idx],
            'test': data[test_idx],
            'train_idx': train_idx,
            'val_idx': val_idx,
            'test_idx': test_idx
        }
    
    def _time_series_split(
        self, 
        data: np.ndarray, 
        labels: Optional[np.ndarray],
        **kwargs
    ) -> Dict[str, np.ndarray]:
        """Time series split maintaining temporal order"""
        logger.info("Using time series split strategy")
        
        n_samples = len(data)
        
        # Calculate split indices
        train_end = int(n_samples * self.config.train_ratio)
        val_end = train_end + int(n_samples * self.config.val_ratio)
        
        train_idx = list(range(train_end))
        val_idx = list(range(train_end, val_end))
        test_idx = list(range(val_end, n_samples))
        
        return {
            'train': data[train_idx],
            'val': data[val_idx],
            'test': data[test_idx],
            'train_idx': train_idx,
            'val_idx': val_idx,
            'test_idx': test_idx
        }
    
    def _validate_splits(
        self, 
        splits: Dict[str, np.ndarray], 
        data: np.ndarray, 
        labels: Optional[np.ndarray]
    ):
        """Validate that splits meet requirements"""
        logger.info("Validating data splits...")
        
        # Check minimum samples per split
        for split_name, split_data in splits.items():
            if isinstance(split_data, np.ndarray) and len(split_data) < self.config.min_samples_per_split:
                raise ValueError(
                    f"{split_name} split has {len(split_data)} samples, "
                    f"minimum required is {self.config.min_samples_per_split}"
                )
        
        # Check for overlap in indices
        train_idx = splits.get('train_idx', [])
        val_idx = splits.get('val_idx', [])
        test_idx = splits.get('test_idx', [])
        
        if set(train_idx) & set(val_idx):
            raise ValueError("Train and validation indices overlap")
        if set(train_idx) & set(test_idx):
            raise ValueError("Train and test indices overlap")
        if set(val_idx) & set(test_idx):
            raise ValueError("Validation and test indices overlap")
        
        # Check total samples
        total_split_samples = len(train_idx) + len(val_idx) + len(test_idx)
        if total_split_samples != len(data):
            raise ValueError(
                f"Total split samples ({total_split_samples}) "
                f"doesn't match original data ({len(data)})"
            )
        
        logger.info("Data splits validation passed")
    
    def _store_split_info(self, data: np.ndarray, labels: Optional[np.ndarray]):
        """Store information about the splits"""
        self.split_info = {
            'total_samples': len(data),
            'split_ratios': {
                'train': self.config.train_ratio,
                'val': self.config.val_ratio,
                'test': self.config.test_ratio
            },
            'split_sizes': {
                'train': len(self.splits['train']),
                'val': len(self.splits['val']),
                'test': len(self.splits['test'])
            }
        }
        
        if labels is not None:
            # Add label distribution information
            unique_labels, label_counts = np.unique(labels, return_counts=True)
            self.split_info['label_distribution'] = dict(zip(unique_labels, label_counts))
            
            # Add per-split label distribution
            for split_name in ['train', 'val', 'test']:
                split_labels = labels[self.splits[f'{split_name}_idx']]
                unique_split_labels, split_label_counts = np.unique(split_labels, return_counts=True)
                self.split_info[f'{split_name}_label_distribution'] = dict(
                    zip(unique_split_labels, split_label_counts)
                )
    
    def _save_splits(self, splits: Dict[str, np.ndarray]):
        """Save splits to disk"""
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # Save split indices
        indices_file = Path(self.config.splits_dir) / f"split_indices_{timestamp}.pkl"
        with open(indices_file, 'wb') as f:
            pickle.dump({
                'train_idx': splits['train_idx'],
                'val_idx': splits['val_idx'],
                'test_idx': splits['test_idx']
            }, f)
        
        # Save split info
        info_file = Path(self.config.splits_dir) / f"split_info_{timestamp}.json"
        with open(info_file, 'w') as f:
            json.dump(self.split_info, f, indent=2, default=str)
        
        logger.info(f"Splits saved to {self.config.splits_dir}")


class CrossValidator:
    """Handles cross-validation for deep learning workflows"""
    
    def __init__(self, config: DataSplitConfig):
        self.config = config
        self.cv_results = {}
        self.fold_splits = {}
    
    def cross_validate(
        self, 
        data: Union[np.ndarray, pd.DataFrame, List],
        labels: Optional[Union[np.ndarray, List]] = None,
        groups: Optional[Union[np.ndarray, List]] = None,
        cv_type: str = "kfold"
    ) -> Dict[str, Any]:
        """
        Perform cross-validation
        
        Args:
            data: Input data
            labels: Target labels
            groups: Group identifiers
            cv_type: Type of cross-validation ('kfold', 'stratified', 'group', 'timeseries')
            
        Returns:
            Dictionary containing cross-validation results
        """
        logger.info(f"Starting {cv_type} cross-validation...")
        
        # Convert data to numpy array
        if isinstance(data, torch.Tensor):
            data_np = data.cpu().numpy()
        elif isinstance(data, pd.DataFrame):
            data_np = data.values
        elif isinstance(data, List):
            data_np = np.array(data)
        else:
            data_np = data
        
        # Convert labels to numpy array
        if labels is not None:
            if isinstance(labels, torch.Tensor):
                labels_np = labels.cpu().numpy()
            elif isinstance(labels, List):
                labels_np = np.array(labels)
            else:
                labels_np = labels
        else:
            labels_np = None
        
        # Select cross-validation strategy
        if cv_type == "kfold":
            cv_strategy = KFold(
                n_splits=self.config.n_splits,
                shuffle=self.config.shuffle,
                random_state=self.config.random_state
            )
        elif cv_type == "stratified":
            if labels_np is None:
                raise ValueError("Labels required for stratified cross-validation")
            cv_strategy = StratifiedKFold(
                n_splits=self.config.n_splits,
                shuffle=self.config.shuffle,
                random_state=self.config.random_state
            )
        elif cv_type == "group":
            if groups is None:
                raise ValueError("Groups required for group cross-validation")
            cv_strategy = GroupKFold(n_splits=self.config.n_splits)
        elif cv_type == "timeseries":
            cv_strategy = TimeSeriesSplit(n_splits=self.config.n_splits)
        else:
            raise ValueError(f"Unknown cross-validation type: {cv_type}")
        
        # Perform cross-validation
        fold_splits = []
        fold_metrics = []
        
        if cv_type == "group":
            cv_iter = cv_strategy.split(data_np, labels_np, groups)
        else:
            cv_iter = cv_strategy.split(data_np, labels_np) if labels_np is not None else cv_strategy.split(data_np)
        
        for fold, (train_idx, val_idx) in enumerate(cv_iter):
            logger.info(f"Processing fold {fold + 1}/{self.config.n_splits}")
            
            # Store fold split
            fold_split = {
                'fold': fold + 1,
                'train_idx': train_idx,
                'val_idx': val_idx,
                'train_data': data_np[train_idx],
                'val_data': data_np[val_idx]
            }
            
            if labels_np is not None:
                fold_split['train_labels'] = labels_np[train_idx]
                fold_split['val_labels'] = labels_np[val_idx]
            
            fold_splits.append(fold_split)
            
            # Calculate fold metrics (placeholder for actual model evaluation)
            fold_metric = self._calculate_fold_metrics(fold_split)
            fold_metrics.append(fold_metric)
        
        # Store results
        self.fold_splits = fold_splits
        self.cv_results = {
            'cv_type': cv_type,
            'n_splits': self.config.n_splits,
            'fold_splits': fold_splits,
            'fold_metrics': fold_metrics,
            'summary': self._calculate_cv_summary(fold_metrics)
        }
        
        logger.info("Cross-validation completed successfully")
        return self.cv_results
    
    def _calculate_fold_metrics(self, fold_split: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for a single fold (placeholder)"""
        # This would typically involve training a model and evaluating it
        # For now, return basic information
        return {
            'fold': fold_split['fold'],
            'train_samples': len(fold_split['train_idx']),
            'val_samples': len(fold_split['val_idx']),
            'train_ratio': len(fold_split['train_idx']) / (len(fold_split['train_idx']) + len(fold_split['val_idx']))
        }
    
    def _calculate_cv_summary(self, fold_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics across all folds"""
        if not fold_metrics:
            return {}
        
        # Extract numeric values for summary
        train_samples = [m['train_samples'] for m in fold_metrics]
        val_samples = [m['val_samples'] for m in fold_metrics]
        train_ratios = [m['train_ratio'] for m in fold_metrics]
        
        return {
            'mean_train_samples': np.mean(train_samples),
            'std_train_samples': np.std(train_samples),
            'mean_val_samples': np.mean(val_samples),
            'std_val_samples': np.std(val_samples),
            'mean_train_ratio': np.mean(train_ratios),
            'std_train_ratio': np.std(train_ratios)
        }
    
    def get_fold_data(self, fold: int) -> Dict[str, np.ndarray]:
        """Get data for a specific fold"""
        if fold < 1 or fold > self.config.n_splits:
            raise ValueError(f"Fold must be between 1 and {self.config.n_splits}")
        
        fold_data = self.fold_splits[fold - 1]
        return {
            'train_data': fold_data['train_data'],
            'val_data': fold_data['val_data'],
            'train_idx': fold_data['train_idx'],
            'val_idx': fold_data['val_idx']
        }


class DataSplitVisualizer:
    """Visualize data splits and cross-validation results"""
    
    @staticmethod
    def plot_split_distribution(
        splits: Dict[str, np.ndarray],
        labels: Optional[np.ndarray] = None,
        save_path: Optional[str] = None
    ):
        """Plot distribution of data across splits"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Sample counts
        split_names = ['train', 'val', 'test']
        split_counts = [len(splits[split]) for split in split_names]
        
        axes[0].bar(split_names, split_counts, color=['#2E86AB', '#A23B72', '#F18F01'])
        axes[0].set_title('Sample Counts by Split')
        axes[0].set_ylabel('Number of Samples')
        
        # Add count labels on bars
        for i, count in enumerate(split_counts):
            axes[0].text(i, count + max(split_counts) * 0.01, str(count), 
                        ha='center', va='bottom', fontweight='bold')
        
        # Label distribution if available
        if labels is not None:
            unique_labels, label_counts = np.unique(labels, return_counts=True)
            
            # Create stacked bar chart for each split
            split_label_counts = []
            for split_name in split_names:
                split_labels = labels[splits[f'{split_name}_idx']]
                split_unique, split_counts = np.unique(split_labels, return_counts=True)
                split_label_counts.append(split_counts)
            
            # Plot stacked bars
            bottom = np.zeros(len(split_names))
            for i, label in enumerate(unique_labels):
                values = [split_label_counts[j][i] if i < len(split_label_counts[j]) else 0 
                         for j in range(len(split_names))]
                axes[1].bar(split_names, values, bottom=bottom, label=f'Class {label}')
                bottom += values
            
            axes[1].set_title('Label Distribution by Split')
            axes[1].set_ylabel('Number of Samples')
            axes[1].legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Split distribution plot saved to {save_path}")
        
        plt.show()
    
    @staticmethod
    def plot_cv_results(
        cv_results: Dict[str, Any],
        save_path: Optional[str] = None
    ):
        """Plot cross-validation results"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Fold sample distribution
        fold_splits = cv_results['fold_splits']
        fold_numbers = [split['fold'] for split in fold_splits]
        train_samples = [split['train_samples'] for split in fold_splits]
        val_samples = [split['val_samples'] for split in fold_splits]
        
        x = np.arange(len(fold_numbers))
        width = 0.35
        
        axes[0].bar(x - width/2, train_samples, width, label='Train', color='#2E86AB')
        axes[0].bar(x + width/2, val_samples, width, label='Validation', color='#A23B72')
        
        axes[0].set_xlabel('Fold')
        axes[0].set_ylabel('Number of Samples')
        axes[0].set_title('Sample Distribution Across Folds')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(fold_numbers)
        axes[0].legend()
        
        # Add value labels on bars
        for i, (train, val) in enumerate(zip(train_samples, val_samples)):
            axes[0].text(i - width/2, train + max(train_samples) * 0.01, str(train), 
                        ha='center', va='bottom', fontsize=8)
            axes[0].text(i + width/2, val + max(val_samples) * 0.01, str(val), 
                        ha='center', va='bottom', fontsize=8)
        
        # Summary statistics
        summary = cv_results['summary']
        if summary:
            summary_stats = [
                f"Mean Train: {summary['mean_train_samples']:.1f} ± {summary['std_train_samples']:.1f}",
                f"Mean Val: {summary['mean_val_samples']:.1f} ± {summary['std_val_samples']:.1f}",
                f"Mean Train Ratio: {summary['mean_train_ratio']:.3f} ± {summary['std_train_ratio']:.3f}"
            ]
            
            axes[1].text(0.1, 0.8, '\n'.join(summary_stats), 
                        transform=axes[1].transAxes, fontsize=12,
                        verticalalignment='top', fontfamily='monospace',
                        bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
            
            axes[1].set_title('Cross-Validation Summary')
            axes[1].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"CV results plot saved to {save_path}")
        
        plt.show()


def demonstrate_data_splitting():
    """Demonstrate data splitting and cross-validation functionality"""
    logger.info("Demonstrating data splitting and validation utilities...")
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    n_classes = 3
    
    # Generate synthetic data
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, n_classes, n_samples)
    groups = np.random.randint(0, 100, n_samples)  # 100 groups
    
    logger.info(f"Generated {n_samples} samples with {n_features} features and {n_classes} classes")
    
    # 1. Basic random split
    logger.info("\n1. Basic Random Split")
    config_random = DataSplitConfig(
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        stratify=False
    )
    
    splitter_random = DataSplitter(config_random)
    splits_random = splitter_random.split_data(X, y)
    
    logger.info(f"Random split sizes: Train={len(splits_random['train'])}, "
                f"Val={len(splits_random['val'])}, Test={len(splits_random['test'])}")
    
    # 2. Stratified split
    logger.info("\n2. Stratified Split")
    config_stratified = DataSplitConfig(
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        stratify=True
    )
    
    splitter_stratified = DataSplitter(config_stratified)
    splits_stratified = splitter_stratified.split_data(X, y)
    
    logger.info(f"Stratified split sizes: Train={len(splits_stratified['train'])}, "
                f"Val={len(splits_stratified['val'])}, Test={len(splits_stratified['test'])}")
    
    # 3. Group-based split
    logger.info("\n3. Group-based Split")
    config_group = DataSplitConfig(
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        group_by='groups'
    )
    
    splitter_group = DataSplitter(config_group)
    splits_group = splitter_group.split_data(X, y, groups=groups)
    
    logger.info(f"Group-based split sizes: Train={len(splits_group['train'])}, "
                f"Val={len(splits_group['val'])}, Test={len(splits_group['test'])}")
    
    # 4. Cross-validation
    logger.info("\n4. Cross-Validation")
    config_cv = DataSplitConfig(n_splits=5)
    
    cv_stratified = CrossValidator(config_cv)
    cv_results = cv_stratified.cross_validate(X, y, cv_type="stratified")
    
    logger.info(f"Cross-validation completed with {cv_results['n_splits']} folds")
    
    # 5. Visualization
    logger.info("\n5. Creating visualizations...")
    
    # Plot stratified split distribution
    DataSplitVisualizer.plot_split_distribution(
        splits_stratified, y, 
        save_path="./stratified_split_distribution.png"
    )
    
    # Plot cross-validation results
    DataSplitVisualizer.plot_cv_results(
        cv_results, 
        save_path="./cross_validation_results.png"
    )
    
    logger.info("Data splitting and validation demonstration completed!")
    
    return {
        'random_splits': splits_random,
        'stratified_splits': splits_stratified,
        'group_splits': splits_group,
        'cv_results': cv_results
    }


if __name__ == "__main__":
    # Run demonstration
    results = demonstrate_data_splitting()
    
    # Print summary
    print("\n" + "="*50)
    print("DATA SPLITTING AND VALIDATION SUMMARY")
    print("="*50)
    
    for method, splits in results.items():
        if 'splits' in method:
            print(f"\n{method.replace('_', ' ').title()}:")
            print(f"  Train: {len(splits['train'])} samples")
            print(f"  Val:   {len(splits['val'])} samples")
            print(f"  Test:  {len(splits['test'])} samples")
        elif 'cv_results' in method:
            print(f"\nCross-Validation Results:")
            print(f"  Folds: {splits['n_splits']}")
            print(f"  Type:  {splits['cv_type']}")
    
    print("\n" + "="*50)
