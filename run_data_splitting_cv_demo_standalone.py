#!/usr/bin/env python3
"""
Standalone Demo for Data Splitting and Cross-Validation System.

This script demonstrates the capabilities of the data splitting and cross-validation
system for diffusion models without importing from the core module system.
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import time
import logging
from enum import Enum
from dataclasses import dataclass, field
import random
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Core System Implementation (copied directly to avoid imports)
# ============================================================================

class SplitType(Enum):
    TRAIN_VAL_TEST = "train_val_test"
    TRAIN_TEST = "train_test"
    CROSS_VALIDATION = "cross_validation"
    NESTED_CROSS_VALIDATION = "nested_cross_validation"
    TIME_SERIES = "time_series"
    GROUP_BASED = "group_based"

class CrossValidationType(Enum):
    K_FOLD = "k_fold"
    STRATIFIED_K_FOLD = "stratified_k_fold"
    GROUP_K_FOLD = "group_k_fold"
    TIME_SERIES_SPLIT = "time_series_split"
    SHUFFLE_SPLIT = "shuffle_split"
    STRATIFIED_SHUFFLE_SPLIT = "stratified_shuffle_split"

@dataclass
class DataSplitConfig:
    split_type: SplitType = SplitType.TRAIN_VAL_TEST
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    random_state: Optional[int] = 42
    shuffle: bool = True
    stratify: Optional[str] = None
    group_by: Optional[str] = None
    time_column: Optional[str] = None
    ensure_min_samples: int = 10
    ensure_class_balance: bool = True
    max_imbalance_ratio: float = 0.8

@dataclass
class CrossValidationConfig:
    cv_type: CrossValidationType = CrossValidationType.K_FOLD
    n_folds: int = 5
    n_repeats: int = 1
    random_state: Optional[int] = 42
    shuffle: bool = True
    stratify: Optional[str] = None
    group_by: Optional[str] = None
    time_column: Optional[str] = None
    track_metrics: List[str] = field(default_factory=lambda: ["loss", "accuracy"])
    save_predictions: bool = True
    save_models: bool = False

@dataclass
class DataSplitResult:
    train_indices: List[int]
    val_indices: Optional[List[int]] = None
    test_indices: Optional[List[int]] = None
    split_info: Dict[str, Any] = field(default_factory=dict)
    data_distribution: Dict[str, Any] = field(default_factory=dict)
    
    def get_split_sizes(self) -> Dict[str, int]:
        sizes = {"train": len(self.train_indices)}
        if self.val_indices is not None:
            sizes["val"] = len(self.val_indices)
        if self.test_indices is not None:
            sizes["test"] = len(self.test_indices)
        return sizes
    
    def get_split_ratios(self) -> Dict[str, float]:
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
        self.random_state = random.Random(config.random_state if config.random_state else 42)
        self.splits_history = []
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate the configuration."""
        if self.config.split_type == SplitType.TRAIN_VAL_TEST:
            total_ratio = self.config.train_ratio + self.config.val_ratio + self.config.test_ratio
            if abs(total_ratio - 1.0) > 1e-6:
                raise ValueError(f"Train, validation, and test ratios must sum to 1.0, got {total_ratio}")
    
    def split_data(self, 
                   data: Union[torch.Tensor, np.ndarray, List],
                   labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                   groups: Optional[Union[np.ndarray, List]] = None,
                   **kwargs) -> DataSplitResult:
        """Split data according to configuration."""
        if self.config.split_type == SplitType.TRAIN_VAL_TEST:
            return self._split_train_val_test(data, labels, groups, **kwargs)
        elif self.config.split_type == SplitType.TRAIN_TEST:
            return self._split_train_test(data, labels, groups, **kwargs)
        else:
            raise ValueError(f"Unsupported split type: {self.config.split_type}")
    
    def _split_train_val_test(self, 
                             data: Union[torch.Tensor, np.ndarray, List],
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
                          data: Union[torch.Tensor, np.ndarray, List],
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
    
    def _analyze_split_distribution(self, 
                                   data: Union[torch.Tensor, np.ndarray, List],
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
        self.random_state = random.Random(config.random_state if config.random_state else 42)
        self.cv_results = []
        self.best_models = {}
        
    def cross_validate(self, 
                       model_fn: Callable,
                       data: Union[torch.Tensor, np.ndarray, List],
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
                          data: Union[torch.Tensor, np.ndarray, List],
                          labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                          groups: Optional[Union[np.ndarray, List]] = None) -> List[Dict[str, List[int]]]:
        """Create cross-validation splits."""
        n_samples = len(data)
        splits = []
        
        # Simple k-fold implementation
        fold_size = n_samples // self.config.n_folds
        
        for fold in range(self.config.n_folds):
            start_idx = fold * fold_size
            end_idx = start_idx + fold_size if fold < self.config.n_folds - 1 else n_samples
            
            val_indices = list(range(start_idx, end_idx))
            train_indices = list(range(0, start_idx)) + list(range(end_idx, n_samples))
            
            splits.append({
                "train": train_indices,
                "val": val_indices,
                "fold": fold,
                "repeat": 0
            })
        
        return splits
    
    def _evaluate_fold(self, 
                       model_fn: Callable,
                       data: Union[torch.Tensor, np.ndarray, List],
                       labels: Optional[Union[torch.Tensor, np.ndarray, List]] = None,
                       groups: Optional[Union[np.ndarray, List]] = None,
                       split: Dict[str, List[int]] = None,
                       fold_idx: int = 0,
                       **kwargs) -> Dict[str, Any]:
        """Evaluate a single fold."""
        # This is a simplified version - in practice, you would implement actual training
        # For testing, we'll just return mock results
        fold_result = {
            "fold": fold_idx,
            "split": split,
            "train_result": {"training_time": 0.0, "n_epochs": 0, "final_loss": 0.0},
            "val_result": {"metrics": {}, "evaluation_time": 0.0},
            "metrics": {},
            "model_info": {"n_parameters": 1000, "model_state": None}
        }
        
        # Mock metrics
        for metric_name in self.config.track_metrics:
            if metric_name == "loss":
                fold_result["metrics"][metric_name] = random.uniform(0.1, 0.5)
            elif metric_name == "accuracy":
                fold_result["metrics"][metric_name] = random.uniform(0.7, 0.95)
            else:
                fold_result["metrics"][metric_name] = random.uniform(0.0, 1.0)
        
        return fold_result
    
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

# ============================================================================
# Demo Classes
# ============================================================================

class MockDiffusionDataset:
    """Mock dataset for demonstration purposes."""
    
    def __init__(self, n_samples=1000, n_classes=5, n_groups=10):
        self.n_samples = n_samples
        self.n_classes = n_classes
        self.n_groups = n_groups
        
        # Generate mock data
        self.data = torch.randn(n_samples, 64, 64, 3)  # Mock images
        self.labels = torch.randint(0, n_classes, (n_samples,))
        self.groups = torch.randint(0, n_groups, (n_samples,))
        self.timestamps = torch.arange(n_samples, dtype=torch.float32)
        
        print(f"✓ Created mock dataset: {n_samples} samples, {n_classes} classes, {n_groups} groups")
    
    def __len__(self):
        return self.n_samples
    
    def get_data(self):
        """Get all data components."""
        return {
            "data": self.data,
            "labels": self.labels,
            "groups": self.groups,
            "timestamps": self.timestamps
        }

class SimpleDiffusionModel(nn.Module):
    """Simple diffusion model for demonstration purposes."""
    
    def __init__(self, input_dim=64, hidden_dim=128, output_dim=64):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Time embedding
        self.time_embed = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Main network
        self.net = nn.Sequential(
            nn.Linear(input_dim + hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x, t):
        # Time embedding
        t = t.float().unsqueeze(-1) / 1000.0
        t_emb = self.time_embed(t)
        
        # Concatenate input with time embedding
        x_t = torch.cat([x, t_emb], dim=-1)
        
        # Forward pass
        return self.net(x_t)

class DataSplittingCVDemo:
    """Demo class for data splitting and cross-validation."""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Create mock dataset
        self.dataset = MockDiffusionDataset(n_samples=1000, n_classes=5, n_groups=10)
        self.data_components = self.dataset.get_data()
        
        print("✓ Demo system initialized successfully")
    
    def demo_data_splitting(self):
        """Demonstrate various data splitting strategies."""
        print("\n" + "="*60)
        print("DEMO: Data Splitting Strategies")
        print("="*60)
        
        # Test different split configurations
        split_configs = [
            ("Standard Train-Val-Test", SplitType.TRAIN_VAL_TEST, 0.7, 0.15, 0.15),
            ("Train-Test Only", SplitType.TRAIN_TEST, 0.8, 0.0, 0.2),
            ("Balanced Split", SplitType.TRAIN_VAL_TEST, 0.6, 0.2, 0.2),
            ("Large Training Set", SplitType.TRAIN_VAL_TEST, 0.8, 0.1, 0.1),
        ]
        
        for name, split_type, train_ratio, val_ratio, test_ratio in split_configs:
            print(f"\nTesting {name}...")
            
            # Create configuration
            config = DataSplitConfig(
                split_type=split_type,
                train_ratio=train_ratio,
                val_ratio=val_ratio,
                test_ratio=test_ratio,
                random_state=42,
                shuffle=True
            )
            
            # Create splitter
            splitter = DataSplitter(config)
            
            # Split data
            result = splitter.split_data(
                data=self.data_components["data"],
                labels=self.data_components["labels"],
                groups=self.data_components["groups"]
            )
            
            # Display results
            sizes = result.get_split_sizes()
            ratios = result.get_split_ratios()
            
            print(f"  Split sizes: {sizes}")
            print(f"  Split ratios: {ratios}")
            
            # Analyze distribution
            if "label_distribution" in result.data_distribution.get("train", {}):
                train_labels = result.data_distribution["train"]["label_distribution"]
                print(f"  Train label distribution: {train_labels}")
            
            print(f"  ✓ {name} completed successfully")
    
    def demo_cross_validation(self):
        """Demonstrate various cross-validation strategies."""
        print("\n" + "="*60)
        print("DEMO: Cross-Validation Strategies")
        print("="*60)
        
        # Test different CV configurations
        cv_configs = [
            ("K-Fold CV", CrossValidationType.K_FOLD, 5, 1),
            ("Stratified K-Fold CV", CrossValidationType.STRATIFIED_K_FOLD, 5, 1),
            ("Repeated K-Fold CV", CrossValidationType.K_FOLD, 5, 3),
        ]
        
        for name, cv_type, n_folds, n_repeats in cv_configs:
            print(f"\nTesting {name}...")
            
            # Create configuration
            config = CrossValidationConfig(
                cv_type=cv_type,
                n_folds=n_folds,
                n_repeats=n_repeats,
                random_state=42,
                shuffle=True,
                track_metrics=["loss", "accuracy", "f1_score"]
            )
            
            # Create validator
            validator = CrossValidator(config)
            
            # Define model factory function
            def create_model():
                return SimpleDiffusionModel().to(self.device)
            
            # Perform cross-validation
            try:
                cv_result = validator.cross_validate(
                    model_fn=create_model,
                    data=self.data_components["data"],
                    labels=self.data_components["labels"],
                    groups=self.data_components["groups"]
                )
                
                # Display results
                summary = cv_result["summary"]
                print(f"  CV completed with {len(cv_result['folds'])} folds")
                
                for metric_name, metric_stats in summary.items():
                    print(f"  {metric_name}: {metric_stats['mean']:.4f} ± {metric_stats['std']:.4f}")
                
                print(f"  ✓ {name} completed successfully")
                
            except Exception as e:
                print(f"  ✗ {name} failed: {e}")
    
    def demo_visualization(self):
        """Demonstrate visualization capabilities."""
        print("\n" + "="*60)
        print("DEMO: Visualization and Analysis")
        print("="*60)
        
        # Create sample splits for visualization
        print("Creating sample splits for visualization...")
        
        # Create different split configurations
        split_configs = [
            ("Balanced", SplitType.TRAIN_VAL_TEST, 0.6, 0.2, 0.2),
            ("Large Train", SplitType.TRAIN_VAL_TEST, 0.8, 0.1, 0.1),
            ("Equal Split", SplitType.TRAIN_VAL_TEST, 0.33, 0.33, 0.34),
        ]
        
        for name, split_type, train_ratio, val_ratio, test_ratio in split_configs:
            config = DataSplitConfig(
                split_type=split_type,
                train_ratio=train_ratio,
                val_ratio=val_ratio,
                test_ratio=test_ratio,
                random_state=42
            )
            
            splitter = DataSplitter(config)
            
            # Split data
            splitter.split_data(
                data=self.data_components["data"],
                labels=self.data_components["labels"]
            )
        
        # Create CV results for visualization
        print("Creating CV results for visualization...")
        
        cv_configs = [
            ("K-Fold", CrossValidationType.K_FOLD, 5, 1),
            ("Stratified", CrossValidationType.STRATIFIED_K_FOLD, 5, 1),
        ]
        
        for name, cv_type, n_folds, n_repeats in cv_configs:
            config = CrossValidationConfig(
                cv_type=cv_type,
                n_folds=n_folds,
                n_repeats=n_repeats,
                random_state=42,
                track_metrics=["loss", "accuracy"]
            )
            
            validator = CrossValidator(config)
            
            # Perform CV
            def create_model():
                return SimpleDiffusionModel().to(self.device)
            
            try:
                validator.cross_validate(
                    model_fn=create_model,
                    data=self.data_components["data"],
                    labels=self.data_components["labels"]
                )
            except Exception as e:
                print(f"  Warning: CV for {name} failed: {e}")
        
        # Generate visualizations
        print("Generating visualizations...")
        
        try:
            # Plot split distributions
            for i, (name, split_type, train_ratio, val_ratio, test_ratio) in enumerate(split_configs):
                config = DataSplitConfig(
                    split_type=split_type,
                    train_ratio=train_ratio,
                    val_ratio=val_ratio,
                    test_ratio=test_ratio,
                    random_state=42
                )
                
                splitter = DataSplitter(config)
                splitter.split_data(
                    data=self.data_components["data"],
                    labels=self.data_components["labels"]
                )
                
                # Plot and save
                splitter.plot_split_distribution(save_path=f"split_distribution_{i+1}.png")
            
            # Plot CV results
            for i, (name, cv_type, n_folds, n_repeats) in enumerate(cv_configs):
                config = CrossValidationConfig(
                    cv_type=cv_type,
                    n_folds=n_folds,
                    n_repeats=n_repeats,
                    random_state=42,
                    track_metrics=["loss", "accuracy"]
                )
                
                validator = CrossValidator(config)
                
                try:
                    validator.cross_validate(
                        model_fn=create_model,
                        data=self.data_components["data"],
                        labels=self.data_components["labels"]
                    )
                    
                    # Plot and save
                    validator.plot_cv_results(save_path=f"cv_results_{i+1}.png")
                except Exception as e:
                    print(f"  Warning: CV visualization for {name} failed: {e}")
            
            print("  ✓ All visualizations generated successfully")
            
        except Exception as e:
            print(f"  ✗ Visualization generation failed: {e}")
    
    def run_all_demos(self):
        """Run all demonstration functions."""
        print("🚀 Starting Data Splitting and Cross-Validation Demo")
        print("="*80)
        
        try:
            # Run all demos
            self.demo_data_splitting()
            self.demo_cross_validation()
            self.demo_visualization()
            
            print("\n" + "="*80)
            print("🎉 All demos completed successfully!")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function to run the demo."""
    print("Data Splitting and Cross-Validation System Demo")
    print("="*60)
    
    # Create and run demo
    demo = DataSplittingCVDemo()
    demo.run_all_demos()

if __name__ == "__main__":
    main()
