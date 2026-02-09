#!/usr/bin/env python3
"""
Comprehensive Demo for Data Splitting and Cross-Validation System.

This script demonstrates the capabilities of the data splitting and cross-validation
system for diffusion models, including proper train/validation/test splits and
various cross-validation strategies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any
import time
import logging
from enum import Enum
from dataclasses import dataclass, field

# Import the data splitting and CV system
try:
    from core.data_splitting_cross_validation_system import (
        SplitType, CrossValidationType, DataType,
        DataSplitConfig, CrossValidationConfig, DataSplitResult,
        DataSplitter, CrossValidator, DataSplittingCrossValidationSystem,
        create_data_split_config, create_cross_validation_config, create_nested_cv_config
    )
    print("✓ Successfully imported data splitting and CV system")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Creating simplified version for demo...")
    
    # Fallback: Create simplified versions for demo
    from enum import Enum
    from dataclasses import dataclass, field
    
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
        LEAVE_ONE_OUT = "leave_one_out"
        LEAVE_P_OUT = "leave_p_out"
        REPEATED_K_FOLD = "repeated_k_fold"
        REPEATED_STRATIFIED_K_FOLD = "repeated_stratified_k_fold"
    
    class DataType(Enum):
        IMAGES = "images"
        TEXT = "text"
        AUDIO = "audio"
        TABULAR = "tabular"
        TIME_SERIES = "time_series"
        MULTIMODAL = "multimodal"
    
    @dataclass
    class DataSplitConfig:
        split_type: SplitType = SplitType.TRAIN_VAL_TEST
        train_ratio: float = 0.7
        val_ratio: float = 0.15
        test_ratio: float = 0.15
        cv_type: CrossValidationType = CrossValidationType.K_FOLD
        n_folds: int = 5
        n_repeats: int = 1
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
        inner_cv_type: CrossValidationType = CrossValidationType.K_FOLD
        inner_n_folds: int = 3
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
        
        # Initialize system
        self.system = DataSplittingCrossValidationSystem()
        
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
            config = create_data_split_config(
                split_type=split_type,
                train_ratio=train_ratio,
                val_ratio=val_ratio,
                test_ratio=test_ratio,
                random_state=42,
                shuffle=True
            )
            
            # Create splitter
            splitter_name = f"splitter_{name.lower().replace(' ', '_').replace('-', '_')}"
            splitter = self.system.create_data_splitter(splitter_name, config)
            
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
            ("Time Series CV", CrossValidationType.TIME_SERIES_SPLIT, 5, 1),
            ("Shuffle Split CV", CrossValidationType.SHUFFLE_SPLIT, 5, 2),
        ]
        
        for name, cv_type, n_folds, n_repeats in cv_configs:
            print(f"\nTesting {name}...")
            
            # Create configuration
            config = create_cross_validation_config(
                cv_type=cv_type,
                n_folds=n_folds,
                n_repeats=n_repeats,
                random_state=42,
                shuffle=True,
                track_metrics=["loss", "accuracy", "f1_score"]
            )
            
            # Create validator
            validator_name = f"validator_{name.lower().replace(' ', '_').replace('-', '_')}"
            validator = self.system.create_cross_validator(validator_name, config)
            
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
    
    def demo_nested_cross_validation(self):
        """Demonstrate nested cross-validation."""
        print("\n" + "="*60)
        print("DEMO: Nested Cross-Validation")
        print("="*60)
        
        # Create nested CV configuration
        config = create_nested_cv_config(
            outer_cv_type=CrossValidationType.K_FOLD,
            outer_n_folds=5,
            inner_cv_type=CrossValidationType.K_FOLD,
            inner_n_folds=3
        )
        
        # Create validator
        validator_name = "nested_cv_validator"
        validator = self.system.create_cross_validator(validator_name, config)
        
        # Define model factory function
        def create_model():
            return SimpleDiffusionModel().to(self.device)
        
        # Perform nested cross-validation
        try:
            cv_result = validator.cross_validate(
                model_fn=create_model,
                data=self.data_components["data"],
                labels=self.data_components["labels"],
                groups=self.data_components["groups"]
            )
            
            # Display results
            summary = cv_result["summary"]
            print(f"  Nested CV completed with {len(cv_result['folds'])} outer folds")
            
            for metric_name, metric_stats in summary.items():
                print(f"  {metric_name}: {metric_stats['mean']:.4f} ± {metric_stats['std']:.4f}")
            
            print(f"  ✓ Nested CV completed successfully")
            
        except Exception as e:
            print(f"  ✗ Nested CV failed: {e}")
    
    def demo_advanced_splitting(self):
        """Demonstrate advanced splitting strategies."""
        print("\n" + "="*60)
        print("DEMO: Advanced Splitting Strategies")
        print("="*60)
        
        # Test group-based splitting
        print("\nTesting Group-Based Splitting...")
        group_config = create_data_split_config(
            split_type=SplitType.GROUP_BASED,
            train_ratio=0.7,
            val_ratio=0.15,
            test_ratio=0.15,
            group_by="groups",
            random_state=42,
            shuffle=True
        )
        
        group_splitter_name = "group_splitter"
        group_splitter = self.system.create_data_splitter(group_splitter_name, group_config)
        
        try:
            result = group_splitter.split_data(
                data=self.data_components["data"],
                labels=self.data_components["labels"],
                groups=self.data_components["groups"]
            )
            
            sizes = result.get_split_sizes()
            print(f"  Group-based split sizes: {sizes}")
            
            if "group_distribution" in result.data_distribution.get("train", {}):
                train_groups = result.data_distribution["train"]["group_distribution"]
                print(f"  Train group distribution: {train_groups}")
            
            print(f"  ✓ Group-based splitting completed successfully")
            
        except Exception as e:
            print(f"  ✗ Group-based splitting failed: {e}")
        
        # Test time series splitting
        print("\nTesting Time Series Splitting...")
        time_config = create_data_split_config(
            split_type=SplitType.TIME_SERIES,
            train_ratio=0.7,
            val_ratio=0.15,
            test_ratio=0.15,
            time_column="timestamps",
            random_state=42,
            shuffle=False  # No shuffling for time series
        )
        
        time_splitter_name = "time_splitter"
        time_splitter = self.system.create_data_splitter(time_splitter_name, time_config)
        
        try:
            result = time_splitter.split_data(
                data=self.data_components["data"],
                labels=self.data_components["labels"],
                timestamps=self.data_components["timestamps"]
            )
            
            sizes = result.get_split_sizes()
            print(f"  Time series split sizes: {sizes}")
            print(f"  ✓ Time series splitting completed successfully")
            
        except Exception as e:
            print(f"  ✗ Time series splitting failed: {e}")
    
    def demo_integration_with_training(self):
        """Demonstrate integration with training systems."""
        print("\n" + "="*60)
        print("DEMO: Integration with Training Systems")
        print("="*60)
        
        # Create a comprehensive training configuration
        print("Creating comprehensive training configuration...")
        
        # Data splitting configuration
        split_config = create_data_split_config(
            split_type=SplitType.TRAIN_VAL_TEST,
            train_ratio=0.7,
            val_ratio=0.15,
            test_ratio=0.15,
            random_state=42,
            shuffle=True,
            stratify="labels"
        )
        
        # Cross-validation configuration
        cv_config = create_cross_validation_config(
            cv_type=CrossValidationType.STRATIFIED_K_FOLD,
            n_folds=5,
            n_repeats=2,
            random_state=42,
            shuffle=True,
            track_metrics=["loss", "accuracy", "precision", "recall", "f1_score"]
        )
        
        # Create system components
        splitter_name = "training_splitter"
        validator_name = "training_validator"
        
        splitter = self.system.create_data_splitter(splitter_name, split_config)
        validator = self.system.create_cross_validator(validator_name, cv_config)
        
        print(f"  ✓ Created {splitter_name} and {validator_name}")
        
        # Demonstrate workflow
        print("\nDemonstrating training workflow...")
        
        # 1. Split data
        split_result = splitter.split_data(
            data=self.data_components["data"],
            labels=self.data_components["labels"]
        )
        
        print(f"  Data split completed: {split_result.get_split_sizes()}")
        
        # 2. Perform cross-validation on training set
        train_data = self.data_components["data"][split_result.train_indices]
        train_labels = self.data_components["labels"][split_result.train_indices]
        
        def create_model():
            return SimpleDiffusionModel().to(self.device)
        
        cv_result = validator.cross_validate(
            model_fn=create_model,
            data=train_data,
            labels=train_labels
        )
        
        print(f"  Cross-validation completed: {len(cv_result['folds'])} folds")
        
        # 3. Display final results
        summary = cv_result["summary"]
        print("\n  Final CV Results:")
        for metric_name, metric_stats in summary.items():
            print(f"    {metric_name}: {metric_stats['mean']:.4f} ± {metric_stats['std']:.4f}")
        
        print(f"  ✓ Training integration demo completed successfully")
    
    def demo_visualization_and_analysis(self):
        """Demonstrate visualization and analysis capabilities."""
        print("\n" + "="*60)
        print("DEMO: Visualization and Analysis")
        print("="*60)
        
        # Create some sample splits for visualization
        print("Creating sample splits for visualization...")
        
        # Create different split configurations
        split_configs = [
            ("Balanced", SplitType.TRAIN_VAL_TEST, 0.6, 0.2, 0.2),
            ("Large Train", SplitType.TRAIN_VAL_TEST, 0.8, 0.1, 0.1),
            ("Equal Split", SplitType.TRAIN_VAL_TEST, 0.33, 0.33, 0.34),
        ]
        
        for name, split_type, train_ratio, val_ratio, test_ratio in split_configs:
            config = create_data_split_config(
                split_type=split_type,
                train_ratio=train_ratio,
                val_ratio=val_ratio,
                test_ratio=test_ratio,
                random_state=42
            )
            
            splitter_name = f"viz_splitter_{name.lower().replace(' ', '_')}"
            splitter = self.system.create_data_splitter(splitter_name, config)
            
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
            ("Repeated", CrossValidationType.K_FOLD, 5, 3),
        ]
        
        for name, cv_type, n_folds, n_repeats in cv_configs:
            config = create_cross_validation_config(
                cv_type=cv_type,
                n_folds=n_folds,
                n_repeats=n_repeats,
                random_state=42,
                track_metrics=["loss", "accuracy"]
            )
            
            validator_name = f"viz_validator_{name.lower().replace(' ', '_')}"
            validator = self.system.create_cross_validator(validator_name, config)
            
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
            # Plot all results
            self.system.plot_all_results()
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
            self.demo_nested_cross_validation()
            self.demo_advanced_splitting()
            self.demo_integration_with_training()
            self.demo_visualization_and_analysis()
            
            print("\n" + "="*80)
            print("🎉 All demos completed successfully!")
            print("="*80)
            
            # Display system summary
            print("\nSystem Summary:")
            print(f"  Data Splitters: {len(self.system.list_data_splitters())}")
            print(f"  Cross Validators: {len(self.system.list_cross_validators())}")
            print(f"  Split History: {len(self.system.get_split_history())}")
            print(f"  CV History: {len(self.system.get_cv_history())}")
            
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
