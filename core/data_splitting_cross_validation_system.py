#!/usr/bin/env python3
"""
Data Splitting and Cross-Validation System for Diffusion Models.

This module provides comprehensive data splitting and cross-validation capabilities
specifically designed for diffusion model training, including proper train/validation/test
splits and various cross-validation strategies.
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Iterator
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import json
import time
import random
from sklearn.model_selection import (
    KFold, StratifiedKFold, GroupKFold, TimeSeriesSplit,
    train_test_split, ShuffleSplit, StratifiedShuffleSplit
)
from sklearn.utils import check_random_state
import pandas as pd
from collections import defaultdict, Counter
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SplitType(Enum):
    """Types of data splits."""
    TRAIN_VAL_TEST = "train_val_test"
    TRAIN_TEST = "train_test"
    CROSS_VALIDATION = "cross_validation"
    NESTED_CROSS_VALIDATION = "nested_cross_validation"
    TIME_SERIES = "time_series"
    GROUP_BASED = "group_based"

class CrossValidationType(Enum):
    """Types of cross-validation strategies."""
    K_FOLD = "k_fold"
    STRATIFIED_K_FOLD = "stratified_k_fold"
    GROUP_K_FOLD = "group_k_fold"
    TIME_SERIES_SPLIT = "time_series_split"
    SHUFFLE_SPLIT = "shuffle_split"
    STRATIFIED_SHUFFLE_SPLIT = "stratified_shuffle_split"
    LEAVE_ONE_OUT = "leave_one_out"
    LEAVE_P_OUT = "leave_p_out"
    REPEATED_K_FOLD = "repeated_k_fold"
    REPEATED_STRATIFIED_K_FOLD = "repeated_stratified_k_fold"

class DataType(Enum):
    """Types of data for splitting."""
    IMAGES = "images"
    TEXT = "text"
    AUDIO = "audio"
    TABULAR = "tabular"
    TIME_SERIES = "time_series"
    MULTIMODAL = "multimodal"

@dataclass
class DataSplitConfig:
    """Configuration for data splitting."""
    split_type: SplitType = SplitType.TRAIN_VAL_TEST
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    
    # Cross-validation parameters
    cv_type: CrossValidationType = CrossValidationType.K_FOLD
    n_folds: int = 5
    n_repeats: int = 1
    
    # Advanced parameters
    random_state: Optional[int] = 42
    shuffle: bool = True
    stratify: Optional[str] = None
    group_by: Optional[str] = None
    time_column: Optional[str] = None
    
    # Validation parameters
    ensure_min_samples: int = 10
    ensure_class_balance: bool = True
    max_imbalance_ratio: float = 0.8

@dataclass
class CrossValidationConfig:
    """Configuration for cross-validation."""
    cv_type: CrossValidationType = CrossValidationType.K_FOLD
    n_folds: int = 5
    n_repeats: int = 1
    random_state: Optional[int] = 42
    shuffle: bool = True
    stratify: Optional[str] = None
    group_by: Optional[str] = None
    time_column: Optional[str] = None
    
    # Nested CV parameters
    inner_cv_type: CrossValidationType = CrossValidationType.K_FOLD
    inner_n_folds: int = 3
    
    # Performance tracking
    track_metrics: List[str] = field(default_factory=lambda: ["loss", "accuracy"])
    save_predictions: bool = True
    save_models: bool = False

@dataclass
class DataSplitResult:
    """Result of data splitting operation."""
    train_indices: List[int]
    val_indices: Optional[List[int]] = None
    test_indices: Optional[List[int]] = None
    
    # Metadata
    split_info: Dict[str, Any] = field(default_factory=dict)
    data_distribution: Dict[str, Any] = field(default_factory=dict)
    
    def get_split_sizes(self) -> Dict[str, int]:
        """Get sizes of each split."""
        sizes = {"train": len(self.train_indices)}
        if self.val_indices is not None:
            sizes["val"] = len(self.val_indices)
        if self.test_indices is not None:
            sizes["test"] = len(self.test_indices)
        return sizes
    
    def get_split_ratios(self) -> Dict[str, float]:
        """Get ratios of each split."""
        total = len(self.train_indices)
        if self.val_indices is not None:
            total += len(self.val_indices)
        if self.test_indices is not None:
            total += len(self.test_indices)
        
        ratios = {"train": len(self.train_indices) / total}
        if self.val_indices is not None:
            ratios["val"] = len(self.val_indices) / total
        if self.test_indices is not None:
            ratios["test"] = len(self.test_indices) / total
        return ratios

class DataSplitter:
    """Advanced data splitter for diffusion models."""
    
    def __init__(self, config: DataSplitConfig):
        self.config = config
        self.random_state = check_random_state(config.random_state)
        self.splits_history = []
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate the configuration."""
        if self.config.split_type == SplitType.TRAIN_VAL_TEST:
            total_ratio = self.config.train_ratio + self.config.val_ratio + self.config.test_ratio
            if abs(total_ratio - 1.0) > 1e-6:
                raise ValueError(f"Train, validation, and test ratios must sum to 1.0, got {total_ratio}")
        
        if self.config.n_folds < 2:
            raise ValueError(f"Number of folds must be at least 2, got {self.config.n_folds}")
        
        if self.config.n_repeats < 1:
            raise ValueError(f"Number of repeats must be at least 1, got {self.config.n_repeats}")
    
    def split_data(self, 
                   data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                   labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                   groups: Optional[Union[np.ndarray, List]] = None,
                   **kwargs) -> DataSplitResult:
        """Split data according to configuration."""
        if self.config.split_type == SplitType.TRAIN_VAL_TEST:
            return self._split_train_val_test(data, labels, groups, **kwargs)
        elif self.config.split_type == SplitType.TRAIN_TEST:
            return self._split_train_test(data, labels, groups, **kwargs)
        elif self.config.split_type == SplitType.CROSS_VALIDATION:
            return self._split_cross_validation(data, labels, groups, **kwargs)
        else:
            raise ValueError(f"Unsupported split type: {self.config.split_type}")
    
    def _split_train_val_test(self, 
                             data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                             labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                             groups: Optional[Union[np.ndarray, List]] = None,
                             **kwargs) -> DataSplitResult:
        """Split data into train, validation, and test sets."""
        n_samples = len(data)
        
        # First split: separate test set
        test_size = int(n_samples * self.config.test_ratio)
        remaining_size = n_samples - test_size
        
        # Second split: separate validation set from remaining data
        val_size = int(remaining_size * (self.config.val_ratio / (1 - self.config.test_ratio)))
        train_size = remaining_size - val_size
        
        # Create indices
        indices = list(range(n_samples))
        if self.config.shuffle:
            self.random_state.shuffle(indices)
        
        # Split indices
        test_indices = indices[:test_size]
        val_indices = indices[test_size:test_size + val_size]
        train_indices = indices[test_size + val_size:]
        
        # Create result
        result = DataSplitResult(
            train_indices=train_indices,
            val_indices=val_indices,
            test_indices=test_indices
        )
        
        # Add metadata
        result.split_info = {
            "split_type": self.config.split_type.value,
            "n_samples": n_samples,
            "train_size": train_size,
            "val_size": val_size,
            "test_size": test_size,
            "random_state": self.config.random_state
        }
        
        # Analyze data distribution
        result.data_distribution = self._analyze_split_distribution(
            data, labels, groups, train_indices, val_indices, test_indices
        )
        
        # Store in history
        self.splits_history.append(result)
        
        return result
    
    def _split_train_test(self, 
                          data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                          labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                          groups: Optional[Union[np.ndarray, List]] = None,
                          **kwargs) -> DataSplitResult:
        """Split data into train and test sets."""
        n_samples = len(data)
        test_size = int(n_samples * self.config.test_ratio)
        
        # Create indices
        indices = list(range(n_samples))
        if self.config.shuffle:
            self.random_state.shuffle(indices)
        
        # Split indices
        test_indices = indices[:test_size]
        train_indices = indices[test_size:]
        
        # Create result
        result = DataSplitResult(
            train_indices=train_indices,
            test_indices=test_indices
        )
        
        # Add metadata
        result.split_info = {
            "split_type": self.config.split_type.value,
            "n_samples": n_samples,
            "train_size": len(train_indices),
            "test_size": len(test_indices),
            "random_state": self.config.random_state
        }
        
        # Analyze data distribution
        result.data_distribution = self._analyze_split_distribution(
            data, labels, groups, train_indices, None, test_indices
        )
        
        # Store in history
        self.splits_history.append(result)
        
        return result
    
    def _split_cross_validation(self, 
                               data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                               labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                               groups: Optional[Union[np.ndarray, List]] = None,
                               **kwargs) -> DataSplitResult:
        """Create cross-validation splits."""
        # For CV, we return the first fold as a sample
        # The actual CV splits are handled by the CrossValidator class
        cv_result = self._create_cv_splits(data, labels, groups)
        
        # Return first fold as sample
        first_fold = cv_result[0]
        result = DataSplitResult(
            train_indices=first_fold["train"],
            val_indices=first_fold["val"]
        )
        
        # Add metadata
        result.split_info = {
            "split_type": self.config.split_type.value,
            "cv_type": self.config.cv_type.value,
            "n_folds": self.config.n_folds,
            "n_repeats": self.config.n_repeats,
            "random_state": self.config.random_state
        }
        
        # Store in history
        self.splits_history.append(result)
        
        return result
    
    def _create_cv_splits(self, 
                          data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                          labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                          groups: Optional[Union[np.ndarray, List]] = None) -> List[Dict[str, List[int]]]:
        """Create cross-validation splits."""
        n_samples = len(data)
        splits = []
        
        if self.config.cv_type == CrossValidationType.K_FOLD:
            cv = KFold(
                n_splits=self.config.n_folds,
                shuffle=self.config.shuffle,
                random_state=self.config.random_state
            )
        elif self.config.cv_type == CrossValidationType.STRATIFIED_K_FOLD:
            if labels is None:
                raise ValueError("Labels required for stratified k-fold")
            cv = StratifiedKFold(
                n_splits=self.config.n_folds,
                shuffle=self.config.shuffle,
                random_state=self.config.random_state
            )
        elif self.config.cv_type == CrossValidationType.GROUP_K_FOLD:
            if groups is None:
                raise ValueError("Groups required for group k-fold")
            cv = GroupKFold(n_splits=self.config.n_folds)
        elif self.config.cv_type == CrossValidationType.TIME_SERIES_SPLIT:
            cv = TimeSeriesSplit(n_splits=self.config.n_folds)
        elif self.config.cv_type == CrossValidationType.SHUFFLE_SPLIT:
            cv = ShuffleSplit(
                n_splits=self.config.n_repeats,
                test_size=1.0 / self.config.n_folds,
                random_state=self.config.random_state
            )
        elif self.config.cv_type == CrossValidationType.STRATIFIED_SHUFFLE_SPLIT:
            if labels is None:
                raise ValueError("Labels required for stratified shuffle split")
            cv = StratifiedShuffleSplit(
                n_splits=self.config.n_repeats,
                test_size=1.0 / self.config.n_folds,
                random_state=self.config.random_state
            )
        else:
            raise ValueError(f"Unsupported CV type: {self.config.cv_type}")
        
        # Generate splits
        for repeat in range(self.config.n_repeats):
            if self.config.cv_type in [CrossValidationType.SHUFFLE_SPLIT, CrossValidationType.STRATIFIED_SHUFFLE_SPLIT]:
                # For shuffle splits, we generate n_folds splits per repeat
                for _ in range(self.config.n_folds):
                    if self.config.cv_type == CrossValidationType.STRATIFIED_SHUFFLE_SPLIT:
                        train_idx, val_idx = next(cv.split(data, labels))
                    else:
                        train_idx, val_idx = next(cv.split(data))
                    splits.append({
                        "train": train_idx.tolist(),
                        "val": val_idx.tolist(),
                        "repeat": repeat
                    })
            else:
                # For other CV types
                if self.config.cv_type == CrossValidationType.STRATIFIED_K_FOLD:
                    split_generator = cv.split(data, labels)
                elif self.config.cv_type == CrossValidationType.GROUP_K_FOLD:
                    split_generator = cv.split(data, labels, groups)
                else:
                    split_generator = cv.split(data)
                
                for fold, (train_idx, val_idx) in enumerate(split_generator):
                    splits.append({
                        "train": train_idx.tolist(),
                        "val": val_idx.tolist(),
                        "fold": fold,
                        "repeat": repeat
                    })
        
        return splits
    
    def _analyze_split_distribution(self, 
                                   data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                                   labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                                   groups: Optional[Union[np.ndarray, List]] = None,
                                   train_indices: List[int] = None,
                                   val_indices: List[int] = None,
                                   test_indices: List[int] = None) -> Dict[str, Any]:
        """Analyze the distribution of data across splits."""
        analysis = {}
        
        # Basic statistics
        if train_indices:
            analysis["train"] = {"size": len(train_indices)}
        if val_indices:
            analysis["val"] = {"size": len(val_indices)}
        if test_indices:
            analysis["test"] = {"size": len(test_indices)}
        
        # Label distribution analysis
        if labels is not None:
            labels = np.array(labels)
            for split_name, indices in [("train", train_indices), ("val", val_indices), ("test", test_indices)]:
                if indices:
                    split_labels = labels[indices]
                    unique_labels, counts = np.unique(split_labels, return_counts=True)
                    analysis[split_name]["label_distribution"] = dict(zip(unique_labels.tolist(), counts.tolist()))
                    analysis[split_name]["n_classes"] = len(unique_labels)
        
        # Group distribution analysis
        if groups is not None:
            groups = np.array(groups)
            for split_name, indices in [("train", train_indices), ("val", val_indices), ("test", test_indices)]:
                if indices:
                    split_groups = groups[indices]
                    unique_groups, counts = np.unique(split_groups, return_counts=True)
                    analysis[split_name]["group_distribution"] = dict(zip(unique_groups.tolist(), counts.tolist()))
                    analysis[split_name]["n_groups"] = len(unique_groups)
        
        return analysis
    
    def plot_split_distribution(self, save_path: Optional[str] = None):
        """Plot the distribution of data across splits."""
        if not self.splits_history:
            logger.warning("No splits to plot")
            return
        
        latest_split = self.splits_history[-1]
        distribution = latest_split.data_distribution
        
        # Create subplots
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Split sizes
        split_names = list(distribution.keys())
        split_sizes = [distribution[name]["size"] for name in split_names]
        
        axes[0].pie(split_sizes, labels=split_names, autopct='%1.1f%%', startangle=90)
        axes[0].set_title("Data Split Distribution")
        
        # Plot 2: Label distribution (if available)
        if any("label_distribution" in distribution[name] for name in split_names):
            axes[1].set_title("Label Distribution Across Splits")
            
            # Get all unique labels
            all_labels = set()
            for split_name in split_names:
                if "label_distribution" in distribution[split_name]:
                    all_labels.update(distribution[split_name]["label_distribution"].keys())
            
            all_labels = sorted(all_labels)
            
            # Create stacked bar chart
            x = np.arange(len(all_labels))
            width = 0.25
            
            for i, split_name in enumerate(split_names):
                if "label_distribution" in distribution[split_name]:
                    counts = [distribution[split_name]["label_distribution"].get(label, 0) for label in all_labels]
                    axes[1].bar(x + i * width, counts, width, label=split_name)
            
            axes[1].set_xlabel("Labels")
            axes[1].set_ylabel("Count")
            axes[1].set_xticks(x + width)
            axes[1].set_xticklabels(all_labels)
            axes[1].legend()
            axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        plt.close()

class CrossValidator:
    """Advanced cross-validator for diffusion models."""
    
    def __init__(self, config: CrossValidationConfig):
        self.config = config
        self.random_state = check_random_state(config.random_state)
        self.cv_results = []
        self.best_models = {}
        
    def cross_validate(self, 
                       model_fn: Callable,
                       data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                       labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                       groups: Optional[Union[np.ndarray, List]] = None,
                       **kwargs) -> Dict[str, Any]:
        """Perform cross-validation."""
        logger.info(f"Starting {self.config.cv_type.value} cross-validation with {self.config.n_folds} folds")
        
        # Create CV splits
        splits = self._create_cv_splits(data, labels, groups)
        
        # Initialize results storage
        cv_results = {
            "cv_type": self.config.cv_type.value,
            "n_folds": self.config.n_folds,
            "n_repeats": self.config.n_repeats,
            "folds": [],
            "summary": {}
        }
        
        # Track metrics across folds
        all_metrics = defaultdict(list)
        
        # Perform CV
        for fold_idx, split in enumerate(splits):
            logger.info(f"Processing fold {fold_idx + 1}/{len(splits)}")
            
            # Train and evaluate model
            fold_result = self._evaluate_fold(
                model_fn, data, labels, groups, split, fold_idx, **kwargs
            )
            
            cv_results["folds"].append(fold_result)
            
            # Accumulate metrics
            for metric_name, metric_value in fold_result["metrics"].items():
                all_metrics[metric_name].append(metric_value)
        
        # Calculate summary statistics
        cv_results["summary"] = self._calculate_summary_statistics(all_metrics)
        
        # Store results
        self.cv_results.append(cv_results)
        
        logger.info("Cross-validation completed successfully")
        return cv_results
    
    def _create_cv_splits(self, 
                          data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                          labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                          groups: Optional[Union[np.ndarray, List]] = None) -> List[Dict[str, List[int]]]:
        """Create cross-validation splits."""
        n_samples = len(data)
        splits = []
        
        if self.config.cv_type == CrossValidationType.K_FOLD:
            cv = KFold(
                n_splits=self.config.n_folds,
                shuffle=self.config.shuffle,
                random_state=self.config.random_state
            )
        elif self.config.cv_type == CrossValidationType.STRATIFIED_K_FOLD:
            if labels is None:
                raise ValueError("Labels required for stratified k-fold")
            cv = StratifiedKFold(
                n_splits=self.config.n_folds,
                shuffle=self.config.shuffle,
                random_state=self.config.random_state
            )
        elif self.config.cv_type == CrossValidationType.GROUP_K_FOLD:
            if groups is None:
                raise ValueError("Groups required for group k-fold")
            cv = GroupKFold(n_splits=self.config.n_folds)
        elif self.config.cv_type == CrossValidationType.TIME_SERIES_SPLIT:
            cv = TimeSeriesSplit(n_splits=self.config.n_folds)
        elif self.config.cv_type == CrossValidationType.SHUFFLE_SPLIT:
            cv = ShuffleSplit(
                n_splits=self.config.n_repeats,
                test_size=1.0 / self.config.n_folds,
                random_state=self.config.random_state
            )
        elif self.config.cv_type == CrossValidationType.STRATIFIED_SHUFFLE_SPLIT:
            if labels is None:
                raise ValueError("Labels required for stratified shuffle split")
            cv = StratifiedShuffleSplit(
                n_splits=self.config.n_repeats,
                test_size=1.0 / self.config.n_folds,
                random_state=self.config.random_state
            )
        else:
            raise ValueError(f"Unsupported CV type: {self.config.cv_type}")
        
        # Generate splits
        for repeat in range(self.config.n_repeats):
            if self.config.cv_type in [CrossValidationType.SHUFFLE_SPLIT, CrossValidationType.STRATIFIED_SHUFFLE_SPLIT]:
                # For shuffle splits, we generate n_folds splits per repeat
                for fold in range(self.config.n_folds):
                    if self.config.cv_type == CrossValidationType.STRATIFIED_SHUFFLE_SPLIT:
                        train_idx, val_idx = next(cv.split(data, labels))
                    else:
                        train_idx, val_idx = next(cv.split(data))
                    splits.append({
                        "train": train_idx.tolist(),
                        "val": val_idx.tolist(),
                        "fold": fold,
                        "repeat": repeat
                    })
            else:
                # For other CV types
                if self.config.cv_type == CrossValidationType.STRATIFIED_K_FOLD:
                    split_generator = cv.split(data, labels)
                elif self.config.cv_type == CrossValidationType.GROUP_K_FOLD:
                    split_generator = cv.split(data, labels, groups)
                else:
                    split_generator = cv.split(data)
                
                for fold, (train_idx, val_idx) in enumerate(split_generator):
                    splits.append({
                        "train": train_idx.tolist(),
                        "val": val_idx.tolist(),
                        "fold": fold,
                        "repeat": repeat
                    })
        
        return splits
    
    def _evaluate_fold(self, 
                       model_fn: Callable,
                       data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                       labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                       groups: Optional[Union[np.ndarray, List]] = None,
                       split: Dict[str, List[int]] = None,
                       fold_idx: int = 0,
                       **kwargs) -> Dict[str, Any]:
        """Evaluate a single fold."""
        # Extract train/val data
        train_data = self._get_subset(data, split["train"])
        val_data = self._get_subset(data, split["val"])
        
        train_labels = None
        val_labels = None
        if labels is not None:
            train_labels = self._get_subset(labels, split["train"])
            val_labels = self._get_subset(labels, split["val"])
        
        # Train model
        model = model_fn()
        train_result = self._train_model(model, train_data, train_labels, **kwargs)
        
        # Evaluate model
        val_result = self._evaluate_model(model, val_data, val_labels, **kwargs)
        
        # Store best model if requested
        if self.config.save_models:
            model_key = f"fold_{fold_idx}"
            self.best_models[model_key] = model.state_dict().copy()
        
        # Combine results
        fold_result = {
            "fold": fold_idx,
            "split": split,
            "train_result": train_result,
            "val_result": val_result,
            "metrics": val_result["metrics"],
            "model_info": {
                "n_parameters": sum(p.numel() for p in model.parameters()),
                "model_state": model.state_dict() if self.config.save_models else None
            }
        }
        
        return fold_result
    
    def _get_subset(self, data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame], 
                    indices: List[int]) -> Union[torch.Tensor, np.ndarray, List, pd.DataFrame]:
        """Get subset of data based on indices."""
        if isinstance(data, torch.Tensor):
            return data[indices]
        elif isinstance(data, np.ndarray):
            return data[indices]
        elif isinstance(data, pd.DataFrame):
            return data.iloc[indices]
        elif isinstance(data, list):
            return [data[i] for i in indices]
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def _train_model(self, 
                     model: nn.Module,
                     train_data: Any,
                     train_labels: Any,
                     **kwargs) -> Dict[str, Any]:
        """Train a model on training data."""
        # This is a placeholder - in practice, you would implement actual training
        # For now, we'll return a mock result
        return {
            "training_time": 0.0,
            "n_epochs": 0,
            "final_loss": 0.0
        }
    
    def _evaluate_model(self, 
                        model: nn.Module,
                        val_data: Any,
                        val_labels: Any,
                        **kwargs) -> Dict[str, Any]:
        """Evaluate a model on validation data."""
        # This is a placeholder - in practice, you would implement actual evaluation
        # For now, we'll return mock metrics
        metrics = {}
        for metric_name in self.config.track_metrics:
            if metric_name == "loss":
                metrics[metric_name] = random.uniform(0.1, 0.5)
            elif metric_name == "accuracy":
                metrics[metric_name] = random.uniform(0.7, 0.95)
            else:
                metrics[metric_name] = random.uniform(0.0, 1.0)
        
        return {
            "metrics": metrics,
            "predictions": None if not self.config.save_predictions else [],
            "evaluation_time": 0.0
        }
    
    def _calculate_summary_statistics(self, all_metrics: Dict[str, List[float]]) -> Dict[str, Any]:
        """Calculate summary statistics across all folds."""
        summary = {}
        
        for metric_name, metric_values in all_metrics.items():
            metric_values = np.array(metric_values)
            summary[metric_name] = {
                "mean": float(np.mean(metric_values)),
                "std": float(np.std(metric_values)),
                "min": float(np.min(metric_values)),
                "max": float(np.max(metric_values)),
                "median": float(np.median(metric_values)),
                "values": metric_values.tolist()
            }
        
        return summary
    
    def plot_cv_results(self, save_path: Optional[str] = None):
        """Plot cross-validation results."""
        if not self.cv_results:
            logger.warning("No CV results to plot")
            return
        
        latest_cv = self.cv_results[-1]
        summary = latest_cv["summary"]
        
        # Create subplots
        n_metrics = len(summary)
        fig, axes = plt.subplots(1, n_metrics, figsize=(5 * n_metrics, 5))
        if n_metrics == 1:
            axes = [axes]
        
        # Plot each metric
        for i, (metric_name, metric_stats) in enumerate(summary.items()):
            values = metric_stats["values"]
            
            # Box plot
            axes[i].boxplot(values)
            axes[i].set_title(f"{metric_name.replace('_', ' ').title()}")
            axes[i].set_ylabel("Value")
            axes[i].set_xticklabels([f"CV\n(n={len(values)})"])
            
            # Add statistics text
            stats_text = f"Mean: {metric_stats['mean']:.4f}\nStd: {metric_stats['std']:.4f}"
            axes[i].text(0.02, 0.98, stats_text, transform=axes[i].transAxes, 
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle(f"Cross-Validation Results: {latest_cv['cv_type']}")
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        plt.close()
    
    def get_best_model(self, metric_name: str = "loss", criterion: str = "min") -> Optional[Dict[str, Any]]:
        """Get the best model based on a specific metric."""
        if not self.cv_results:
            return None
        
        latest_cv = self.cv_results[-1]
        summary = latest_cv["summary"]
        
        if metric_name not in summary:
            logger.warning(f"Metric {metric_name} not found in CV results")
            return None
        
        metric_stats = summary[metric_name]
        
        if criterion == "min":
            best_idx = np.argmin(metric_stats["values"])
        elif criterion == "max":
            best_idx = np.argmax(metric_stats["values"])
        else:
            raise ValueError(f"Unsupported criterion: {criterion}")
        
        best_fold = latest_cv["folds"][best_idx]
        
        return {
            "fold_idx": best_idx,
            "metric_value": metric_stats["values"][best_idx],
            "model_state": best_fold["model_info"]["model_state"],
            "fold_info": best_fold
        }

class DataSplittingCrossValidationSystem:
    """Complete system for data splitting and cross-validation."""
    
    def __init__(self):
        self.data_splitters = {}
        self.cross_validators = {}
        self.split_history = []
        self.cv_history = []
    
    def create_data_splitter(self, name: str, config: DataSplitConfig) -> DataSplitter:
        """Create a data splitter with given configuration."""
        splitter = DataSplitter(config)
        self.data_splitters[name] = splitter
        logger.info(f"Created data splitter: {name}")
        return splitter
    
    def create_cross_validator(self, name: str, config: CrossValidationConfig) -> CrossValidator:
        """Create a cross-validator with given configuration."""
        validator = CrossValidator(config)
        self.cross_validators[name] = validator
        logger.info(f"Created cross-validator: {name}")
        return validator
    
    def get_data_splitter(self, name: str) -> Optional[DataSplitter]:
        """Get a data splitter by name."""
        return self.data_splitters.get(name)
    
    def get_cross_validator(self, name: str) -> Optional[CrossValidator]:
        """Get a cross-validator by name."""
        return self.cross_validators.get(name)
    
    def list_data_splitters(self) -> List[str]:
        """List all available data splitters."""
        return list(self.data_splitters.keys())
    
    def list_cross_validators(self) -> List[str]:
        """List all available cross-validators."""
        return list(self.cross_validators.keys())
    
    def remove_data_splitter(self, name: str):
        """Remove a data splitter."""
        if name in self.data_splitters:
            del self.data_splitters[name]
            logger.info(f"Removed data splitter: {name}")
    
    def remove_cross_validator(self, name: str):
        """Remove a cross-validator."""
        if name in self.cross_validators:
            del self.cross_validators[name]
            logger.info(f"Removed cross-validator: {name}")
    
    def split_data_with_splitter(self, 
                                splitter_name: str,
                                data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                                labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                                groups: Optional[Union[np.ndarray, List]] = None,
                                **kwargs) -> Optional[DataSplitResult]:
        """Split data using a specific splitter."""
        splitter = self.get_data_splitter(splitter_name)
        if not splitter:
            logger.error(f"Data splitter {splitter_name} not found")
            return None
        
        result = splitter.split_data(data, labels, groups, **kwargs)
        self.split_history.append({
            "splitter_name": splitter_name,
            "timestamp": time.time(),
            "result": result
        })
        
        return result
    
    def cross_validate_with_validator(self, 
                                    validator_name: str,
                                    model_fn: Callable,
                                    data: Union[torch.Tensor, np.ndarray, List, pd.DataFrame],
                                    labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                                    groups: Optional[Union[np.ndarray, List]] = None,
                                    **kwargs) -> Optional[Dict[str, Any]]:
        """Perform cross-validation using a specific validator."""
        validator = self.get_cross_validator(validator_name)
        if not validator:
            logger.error(f"Cross-validator {validator_name} not found")
            return None
        
        result = validator.cross_validate(model_fn, data, labels, groups, **kwargs)
        self.cv_history.append({
            "validator_name": validator_name,
            "timestamp": time.time(),
            "result": result
        })
        
        return result
    
    def get_split_history(self) -> List[Dict[str, Any]]:
        """Get the history of all data splits."""
        return self.split_history.copy()
    
    def get_cv_history(self) -> List[Dict[str, Any]]:
        """Get the history of all cross-validations."""
        return self.cv_history.copy()
    
    def plot_all_results(self, save_dir: Optional[str] = None):
        """Plot results from all splitters and validators."""
        if save_dir:
            Path(save_dir).mkdir(exist_ok=True)
        
        # Plot split distributions
        for name, splitter in self.data_splitters.items():
            if splitter.splits_history:
                save_path = None
                if save_dir:
                    save_path = Path(save_dir) / f"split_distribution_{name}.png"
                splitter.plot_split_distribution(save_path)
        
        # Plot CV results
        for name, validator in self.cross_validators.items():
            if validator.cv_results:
                save_path = None
                if save_dir:
                    save_path = Path(save_dir) / f"cv_results_{name}.png"
                validator.plot_cv_results(save_path)

# ============================================================================
# Utility Functions
# ============================================================================

def create_data_split_config(
    split_type: SplitType = SplitType.TRAIN_VAL_TEST,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    **kwargs
) -> DataSplitConfig:
    """Create a data split configuration."""
    config = DataSplitConfig(
        split_type=split_type,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        **kwargs
    )
    return config

def create_cross_validation_config(
    cv_type: CrossValidationType = CrossValidationType.K_FOLD,
    n_folds: int = 5,
    n_repeats: int = 1,
    **kwargs
) -> CrossValidationConfig:
    """Create a cross-validation configuration."""
    config = CrossValidationConfig(
        cv_type=cv_type,
        n_folds=n_folds,
        n_repeats=n_repeats,
        **kwargs
    )
    return config

def create_nested_cv_config(
    outer_cv_type: CrossValidationType = CrossValidationType.K_FOLD,
    outer_n_folds: int = 5,
    inner_cv_type: CrossValidationType = CrossValidationType.K_FOLD,
    inner_n_folds: int = 3,
    **kwargs
) -> CrossValidationConfig:
    """Create a nested cross-validation configuration."""
    config = CrossValidationConfig(
        cv_type=outer_cv_type,
        n_folds=outer_n_folds,
        inner_cv_type=inner_cv_type,
        inner_n_folds=inner_n_folds,
        **kwargs
    )
    return config 