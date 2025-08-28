from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

import os
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification, make_regression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
from data_splitting_cross_validation_system import (
        import shutil
    import time
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for Data Splitting and Cross-Validation System
========================================================

This module provides comprehensive tests for the data splitting and cross-validation system,
including tests for splitting strategies, cross-validation, data leakage detection, and visualization.
"""


# Import the system under test
    SplitStrategy, RandomSplit, StratifiedSplit, TimeSeriesSplit, GroupSplit,
    DataSplitter, CrossValidator, DataSplitManager, CrossValidationManager,
    NestedCrossValidator, DataLeakageDetector, SplitVisualizer, DataSplitFactory,
    validate_split_sizes, calculate_split_indices, check_imbalance,
    save_splits, load_splits
)


class TestSplitStrategies(unittest.TestCase):
    """Test cases for splitting strategies."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=3, 
            n_informative=5, n_redundant=3, random_state=42
        )
        self.groups = np.random.choice([0, 1, 2], size=1000)
    
    def test_random_split(self) -> Any:
        """Test RandomSplit strategy."""
        strategy = RandomSplit(test_size=0.2, random_state=42)
        splitter = DataSplitter(strategy)
        
        train_data, test_data = splitter.split_data(self.X)
        
        self.assertEqual(len(train_data), 800)  # 80% of 1000
        self.assertEqual(len(test_data), 200)   # 20% of 1000
        self.assertEqual(strategy.get_name(), "Random Split")
    
    def test_stratified_split(self) -> Any:
        """Test StratifiedSplit strategy."""
        strategy = StratifiedSplit(test_size=0.2, random_state=42)
        splitter = DataSplitter(strategy)
        
        train_data, test_data = splitter.split_data(self.X, labels=self.y)
        
        # Check that stratification preserved class distribution
        train_labels = self.y[:len(train_data)]
        test_labels = self.y[len(train_data):]
        
        train_dist = np.bincount(train_labels)
        test_dist = np.bincount(test_labels)
        
        # Ratios should be similar
        train_ratios = train_dist / len(train_labels)
        test_ratios = test_dist / len(test_labels)
        
        for i in range(len(train_ratios)):
            self.assertAlmostEqual(train_ratios[i], test_ratios[i], delta=0.1)
        
        self.assertEqual(strategy.get_name(), "Stratified Split")
    
    def test_time_series_split(self) -> Any:
        """Test TimeSeriesSplit strategy."""
        strategy = TimeSeriesSplit(n_splits=3)
        splitter = DataSplitter(strategy)
        
        splits = splitter.split_data(self.X)
        
        self.assertEqual(len(splits), 3)
        for train_data, test_data in splits:
            self.assertGreater(len(train_data), 0)
            self.assertGreater(len(test_data), 0)
            self.assertLess(len(train_data), len(self.X))
        
        self.assertEqual(strategy.get_name(), "Time Series Split")
    
    def test_group_split(self) -> Any:
        """Test GroupSplit strategy."""
        strategy = GroupSplit(test_size=0.2, random_state=42)
        splitter = DataSplitter(strategy)
        
        train_data, test_data = splitter.split_data(self.X, groups=self.groups)
        
        self.assertGreater(len(train_data), 0)
        self.assertGreater(len(test_data), 0)
        self.assertEqual(strategy.get_name(), "Group Split")


class TestDataSplitManager(unittest.TestCase):
    """Test cases for DataSplitManager."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=3, 
            n_informative=5, n_redundant=3, random_state=42
        )
    
    def test_split_manager_initialization(self) -> Any:
        """Test DataSplitManager initialization."""
        manager = DataSplitManager(
            train_size=0.7,
            val_size=0.15,
            test_size=0.15,
            random_state: int: int = 42
        )
        
        self.assertEqual(manager.train_size, 0.7)
        self.assertEqual(manager.val_size, 0.15)
        self.assertEqual(manager.test_size, 0.15)
        self.assertEqual(manager.random_state, 42)
    
    def test_invalid_split_sizes(self) -> Any:
        """Test that invalid split sizes raise an error."""
        with self.assertRaises(ValueError):
            DataSplitManager(train_size=0.5, val_size=0.3, test_size=0.3)
    
    def test_three_way_split(self) -> Any:
        """Test three-way splitting."""
        manager = DataSplitManager(
            train_size=0.7,
            val_size=0.15,
            test_size=0.15,
            random_state: int: int = 42
        )
        
        train_data, val_data, test_data = manager.split_three_way(
            self.X, self.y, stratify: bool = True
        )
        
        # Check sizes
        self.assertEqual(len(train_data[0]), 700)  # 70% of 1000
        self.assertEqual(len(val_data[0]), 150)    # 15% of 1000
        self.assertEqual(len(test_data[0]), 150)   # 15% of 1000
        
        # Check that all data is used
        total_samples = len(train_data[0]) + len(val_data[0]) + len(test_data[1])
        self.assertEqual(total_samples, 1000)
    
    def test_split_with_validation(self) -> Any:
        """Test train/validation splitting."""
        manager = DataSplitManager(
            train_size=0.8,
            val_size=0.2,
            test_size=0.0,
            random_state: int: int = 42
        )
        
        train_data, val_data = manager.split_with_validation(
            self.X, self.y, stratify: bool = True
        )
        
        # Check sizes
        self.assertEqual(len(train_data[0]), 800)  # 80% of 1000
        self.assertEqual(len(val_data[0]), 200)    # 20% of 1000


class TestCrossValidator(unittest.TestCase):
    """Test cases for CrossValidator."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=3, 
            n_informative=5, n_redundant=3, random_state=42
        )
        self.groups = np.random.choice([0, 1, 2, 3, 4], size=1000)
    
    def test_kfold_cv(self) -> Any:
        """Test K-fold cross-validation."""
        cv = CrossValidator(fold_type='kfold', n_folds=5, random_state=42)
        cv_splits = cv.get_cv_splits(len(self.X))
        
        fold_sizes: List[Any] = []
        for train_idx, val_idx in cv_splits.split(self.X):
            fold_sizes.append((len(train_idx), len(val_idx)))
        
        # Check that we have 5 folds
        self.assertEqual(len(fold_sizes), 5)
        
        # Check that each fold has reasonable sizes
        for train_size, val_size in fold_sizes:
            self.assertGreater(train_size, 0)
            self.assertGreater(val_size, 0)
            self.assertEqual(train_size + val_size, 1000)
    
    def test_stratified_cv(self) -> Any:
        """Test stratified cross-validation."""
        cv = CrossValidator(fold_type='stratified', n_folds=5, random_state=42)
        cv_splits = cv.get_cv_splits(len(self.X), labels=self.y)
        
        fold_sizes: List[Any] = []
        for train_idx, val_idx in cv_splits.split(self.X, self.y):
            fold_sizes.append((len(train_idx), len(val_idx)))
        
        # Check that we have 5 folds
        self.assertEqual(len(fold_sizes), 5)
        
        # Check stratification
        for train_idx, val_idx in cv_splits.split(self.X, self.y):
            train_labels = self.y[train_idx]
            val_labels = self.y[val_idx]
            
            train_dist = np.bincount(train_labels)
            val_dist = np.bincount(val_labels)
            
            # Ratios should be similar
            train_ratios = train_dist / len(train_labels)
            val_ratios = val_dist / len(val_labels)
            
            for i in range(len(train_ratios)):
                self.assertAlmostEqual(train_ratios[i], val_ratios[i], delta=0.1)
    
    def test_group_cv(self) -> Any:
        """Test group cross-validation."""
        cv = CrossValidator(fold_type='group', n_folds=3, random_state=42)
        cv_splits = cv.get_cv_splits(len(self.X), groups=self.groups)
        
        fold_sizes: List[Any] = []
        for train_idx, val_idx in cv_splits.split(self.X, groups=self.groups):
            fold_sizes.append((len(train_idx), len(val_idx)))
        
        # Check that we have 3 folds
        self.assertEqual(len(fold_sizes), 3)
        
        # Check that groups are not split
        for train_idx, val_idx in cv_splits.split(self.X, groups=self.groups):
            train_groups = set(self.groups[train_idx])
            val_groups = set(self.groups[val_idx])
            
            # No overlap in groups
            self.assertEqual(len(train_groups.intersection(val_groups)), 0)
    
    def test_invalid_cv_type(self) -> Any:
        """Test that invalid CV type raises an error."""
        cv = CrossValidator(fold_type='invalid')
        with self.assertRaises(ValueError):
            cv.get_cv_splits(len(self.X))


class TestCrossValidationManager(unittest.TestCase):
    """Test cases for CrossValidationManager."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=3, 
            n_informative=5, n_redundant=3, random_state=42
        )
    
    def test_cv_manager_initialization(self) -> Any:
        """Test CrossValidationManager initialization."""
        manager = CrossValidationManager(
            cv_type: str: str = 'stratified',
            n_folds=5,
            n_repeats=2,
            random_state: int: int = 42
        )
        
        self.assertEqual(manager.cv_type, 'stratified')
        self.assertEqual(manager.n_folds, 5)
        self.assertEqual(manager.n_repeats, 2)
        self.assertEqual(manager.random_state, 42)
    
    def test_perform_cv(self) -> Any:
        """Test performing cross-validation."""
        manager = CrossValidationManager(
            cv_type: str: str = 'stratified',
            n_folds=3,
            random_state: int: int = 42
        )
        
        results = manager.perform_cv(self.X, self.y)
        
        # Check results structure
        self.assertIn('cv_type', results)
        self.assertIn('n_folds', results)
        self.assertIn('fold_results', results)
        
        # Check that we have 3 folds
        self.assertEqual(len(results['fold_results']), 3)
        
        # Check each fold
        for fold_result in results['fold_results']:
            self.assertIn('fold', fold_result)
            self.assertIn('train_indices', fold_result)
            self.assertIn('val_indices', fold_result)
            self.assertIn('train_data', fold_result)
            self.assertIn('val_data', fold_result)
            self.assertIn('train_labels', fold_result)
            self.assertIn('val_labels', fold_result)
            
            # Check that indices are valid
            self.assertGreater(len(fold_result['train_indices']), 0)
            self.assertGreater(len(fold_result['val_indices']), 0)
            
            # Check that no overlap in indices
            train_set = set(fold_result['train_indices'])
            val_set = set(fold_result['val_indices'])
            self.assertEqual(len(train_set.intersection(val_set)), 0)


class TestNestedCrossValidator(unittest.TestCase):
    """Test cases for NestedCrossValidator."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=500, n_features=10, n_classes=3, 
            n_informative=5, n_redundant=3, random_state=42
        )
    
    def test_nested_cv_initialization(self) -> Any:
        """Test NestedCrossValidator initialization."""
        outer_cv = CrossValidationManager('stratified', 3, random_state=42)
        inner_cv = CrossValidationManager('stratified', 2, random_state=42)
        
        nested_cv = NestedCrossValidator(outer_cv, inner_cv)
        
        self.assertEqual(nested_cv.outer_cv, outer_cv)
        self.assertEqual(nested_cv.inner_cv, inner_cv)
    
    def test_perform_nested_cv(self) -> Any:
        """Test performing nested cross-validation."""
        outer_cv = CrossValidationManager('stratified', 3, random_state=42)
        inner_cv = CrossValidationManager('stratified', 2, random_state=42)
        
        nested_cv = NestedCrossValidator(outer_cv, inner_cv)
        
        results = nested_cv.perform_nested_cv(self.X, self.y)
        
        # Check results structure
        self.assertIn('nested_results', results)
        self.assertIn('outer_cv_type', results)
        self.assertIn('inner_cv_type', results)
        
        # Check that we have 3 outer folds
        self.assertEqual(len(results['nested_results']), 3)
        
        # Check each nested result
        for nested_result in results['nested_results']:
            self.assertIn('outer_fold', nested_result)
            self.assertIn('inner_results', nested_result)
            self.assertIn('best_params', nested_result)


class TestDataLeakageDetector(unittest.TestCase):
    """Test cases for DataLeakageDetector."""
    
    def setUp(self) -> Any:
        # Create test data with some duplicates
        self.train_data: List[Any] = [f"sample_{i}" for i in range(100)]
        self.val_data: List[Any] = [f"sample_{i}" for i in range(80, 120)]  # Overlap with train
        self.test_data: List[Any] = [f"sample_{i}" for i in range(110, 150)]  # Overlap with val
        
        self.train_labels = np.random.choice([0, 1, 2], size=100)
        self.val_labels = np.random.choice([0, 1, 2], size=40)
        self.test_labels = np.random.choice([0, 1, 2], size=40)
    
    def test_check_duplicates(self) -> Any:
        """Test duplicate detection."""
        results = DataLeakageDetector.check_duplicates(
            self.train_data, self.val_data, self.test_data
        )
        
        # Check that overlaps are detected
        self.assertIn('train_val_overlap', results)
        self.assertIn('train_test_overlap', results)
        self.assertIn('val_test_overlap', results)
        
        # Should have some overlap
        self.assertGreater(results['train_val_overlap'], 0)
        self.assertGreater(results['val_test_overlap'], 0)
    
    def test_check_distribution_shift(self) -> Any:
        """Test distribution shift detection."""
        # Create imbalanced labels
        train_labels = np.concatenate([
            np.zeros(70), np.ones(20), np.full(10, 2)
        ])
        val_labels = np.concatenate([
            np.zeros(20), np.ones(10), np.full(10, 2)
        ])
        
        results = DataLeakageDetector.check_distribution_shift(
            train_labels, val_labels
        )
        
        # Check that distribution differences are calculated
        self.assertIn('label_0_diff', results)
        self.assertIn('label_1_diff', results)
        self.assertIn('label_2_diff', results)
        
        # Should have some distribution differences
        for key in ['label_0_diff', 'label_1_diff', 'label_2_diff']:
            self.assertGreaterEqual(results[key], 0)


class TestSplitVisualizer(unittest.TestCase):
    """Test cases for SplitVisualizer."""
    
    def setUp(self) -> Any:
        # Create test data
        self.train_labels = np.random.choice([0, 1, 2], size=700, p=[0.6, 0.3, 0.1])
        self.val_labels = np.random.choice([0, 1, 2], size=150, p=[0.6, 0.3, 0.1])
        self.test_labels = np.random.choice([0, 1, 2], size=150, p=[0.6, 0.3, 0.1])
    
    def test_plot_split_distribution(self) -> Any:
        """Test plotting split distribution."""
        # This test just ensures the function runs without error
        try:
            SplitVisualizer.plot_split_distribution(
                self.train_labels, self.val_labels, self.test_labels
            )
            plt.close()  # Close the plot to free memory
        except Exception as e:
            self.fail(f"Plotting failed with error: {e}")
    
    def test_plot_cv_results(self) -> Any:
        """Test plotting CV results."""
        # Create mock CV results
        cv_results: Dict[str, Any] = {
            'fold_results': [
                {'fold': 1, 'metric': 0.85},
                {'fold': 2, 'metric': 0.87},
                {'fold': 3, 'metric': 0.83},
                {'fold': 4, 'metric': 0.86},
                {'fold': 5, 'metric': 0.84}
            ]
        }
        
        try:
            SplitVisualizer.plot_cv_results(cv_results, "Accuracy")
            plt.close()  # Close the plot to free memory
        except Exception as e:
            self.fail(f"CV plotting failed with error: {e}")


class TestDataSplitFactory(unittest.TestCase):
    """Test cases for DataSplitFactory."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=3, 
            n_informative=5, n_redundant=3, random_state=42
        )
    
    def test_create_three_way_split(self) -> Any:
        """Test creating three-way split."""
        train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
            data=self.X,
            labels=self.y,
            train_size=0.7,
            val_size=0.15,
            test_size=0.15,
            stratify=True,
            random_state: int: int = 42
        )
        
        # Check sizes
        self.assertEqual(len(train_data[0]), 700)
        self.assertEqual(len(val_data[0]), 150)
        self.assertEqual(len(test_data[0]), 150)
    
    def test_create_cv_splits(self) -> Any:
        """Test creating CV splits."""
        results = DataSplitFactory.create_cv_splits(
            data=self.X,
            labels=self.y,
            cv_type: str: str = 'stratified',
            n_folds=5,
            random_state: int: int = 42
        )
        
        # Check results
        self.assertIn('cv_type', results)
        self.assertIn('n_folds', results)
        self.assertIn('fold_results', results)
        self.assertEqual(len(results['fold_results']), 5)
    
    def test_create_nested_cv(self) -> Any:
        """Test creating nested CV."""
        results = DataSplitFactory.create_nested_cv(
            data=self.X,
            labels=self.y,
            outer_cv_type: str: str = 'stratified',
            inner_cv_type: str: str = 'stratified',
            outer_folds=3,
            inner_folds=2,
            random_state: int: int = 42
        )
        
        # Check results
        self.assertIn('nested_results', results)
        self.assertIn('outer_cv_type', results)
        self.assertIn('inner_cv_type', results)
        self.assertEqual(len(results['nested_results']), 3)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_validate_split_sizes(self) -> bool:
        """Test split size validation."""
        # Valid splits
        self.assertTrue(validate_split_sizes(0.7, 0.15, 0.15))
        self.assertTrue(validate_split_sizes(0.8, 0.1, 0.1))
        
        # Invalid splits
        self.assertFalse(validate_split_sizes(0.5, 0.3, 0.3))
        self.assertFalse(validate_split_sizes(0.7, 0.2, 0.2))
    
    def test_calculate_split_indices(self) -> Any:
        """Test calculating split indices."""
        indices = calculate_split_indices(
            n_samples=1000,
            train_size=0.7,
            val_size=0.15,
            test_size=0.15,
            random_state: int: int = 42
        )
        
        train_indices, val_indices, test_indices = indices
        
        # Check sizes
        self.assertEqual(len(train_indices), 700)
        self.assertEqual(len(val_indices), 150)
        self.assertEqual(len(test_indices), 150)
        
        # Check no overlap
        train_set = set(train_indices)
        val_set = set(val_indices)
        test_set = set(test_indices)
        
        self.assertEqual(len(train_set.intersection(val_set)), 0)
        self.assertEqual(len(train_set.intersection(test_set)), 0)
        self.assertEqual(len(val_set.intersection(test_set)), 0)
    
    def test_check_imbalance(self) -> Any:
        """Test imbalance checking."""
        # Balanced data
        balanced_labels = np.random.choice([0, 1, 2], size=1000, p=[0.33, 0.33, 0.34])
        results = check_imbalance(balanced_labels)
        
        self.assertIn('imbalance_score', results)
        self.assertIn('is_imbalanced', results)
        self.assertIn('label_ratios', results)
        
        # Should not be imbalanced
        self.assertFalse(results['is_imbalanced'])
        
        # Imbalanced data
        imbalanced_labels = np.concatenate([
            np.zeros(800), np.ones(150), np.full(50, 2)
        ])
        results = check_imbalance(imbalanced_labels)
        
        # Should be imbalanced
        self.assertTrue(results['is_imbalanced'])
        self.assertGreater(results['imbalance_score'], 0.1)


class TestSaveLoadFunctions(unittest.TestCase):
    """Test cases for save/load functions."""
    
    def setUp(self) -> Any:
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test data
        self.train_data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'label': np.random.choice([0, 1], size=100)
        })
        
        self.val_data = pd.DataFrame({
            'feature1': np.random.randn(50),
            'feature2': np.random.randn(50),
            'label': np.random.choice([0, 1], size=50)
        })
        
        self.test_data = pd.DataFrame({
            'feature1': np.random.randn(50),
            'feature2': np.random.randn(50),
            'label': np.random.choice([0, 1], size=50)
        })
    
    def tearDown(self) -> Any:
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_save_load_csv(self) -> Any:
        """Test saving and loading CSV files."""
        save_path = os.path.join(self.temp_dir, "csv_splits")
        
        # Save splits
        save_splits(self.train_data, self.val_data, self.test_data, save_path)
        
        # Load splits
        loaded_train, loaded_val, loaded_test = load_splits(save_path, "csv")
        
        # Check that data is preserved
        pd.testing.assert_frame_equal(self.train_data, loaded_train)
        pd.testing.assert_frame_equal(self.val_data, loaded_val)
        pd.testing.assert_frame_equal(self.test_data, loaded_test)
    
    def test_save_load_numpy(self) -> Any:
        """Test saving and loading NumPy arrays."""
        save_path = os.path.join(self.temp_dir, "numpy_splits")
        
        # Convert to numpy arrays
        train_array = self.train_data.values
        val_array = self.val_data.values
        test_array = self.test_data.values
        
        # Save splits
        save_splits(train_array, val_array, test_array, save_path)
        
        # Load splits
        loaded_train, loaded_val, loaded_test = load_splits(save_path, "npy")
        
        # Check that data is preserved
        np.testing.assert_array_equal(train_array, loaded_train)
        np.testing.assert_array_equal(val_array, loaded_val)
        np.testing.assert_array_equal(test_array, loaded_test)
    
    def test_save_load_text(self) -> Any:
        """Test saving and loading text files."""
        save_path = os.path.join(self.temp_dir, "text_splits")
        
        # Convert to text data
        train_text: List[Any] = [f"sample_{i}" for i in range(100)]
        val_text: List[Any] = [f"sample_{i}" for i in range(100, 150)]
        test_text: List[Any] = [f"sample_{i}" for i in range(150, 200)]
        
        # Save splits
        save_splits(train_text, val_text, test_text, save_path)
        
        # Load splits
        loaded_train, loaded_val, loaded_test = load_splits(save_path, "txt")
        
        # Check that data is preserved
        self.assertEqual(train_text, loaded_train)
        self.assertEqual(val_text, loaded_val)
        self.assertEqual(test_text, loaded_test)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=3, 
            n_informative=5, n_redundant=3, random_state=42
        )
    
    def test_complete_workflow(self) -> Any:
        """Test complete workflow from splitting to evaluation."""
        # 1. Create three-way split
        train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
            data=self.X,
            labels=self.y,
            train_size=0.7,
            val_size=0.15,
            test_size=0.15,
            stratify=True,
            random_state: int: int = 42
        )
        
        # 2. Check for data leakage
        leakage_results = DataLeakageDetector.check_duplicates(
            train_data[0], val_data[0], test_data[0]
        )
        
        # 3. Check imbalance
        imbalance_results = check_imbalance(self.y)
        
        # 4. Perform cross-validation on training data
        cv_results = DataSplitFactory.create_cv_splits(
            data=train_data[0],
            labels=train_data[1],
            cv_type: str: str = 'stratified',
            n_folds=5,
            random_state: int: int = 42
        )
        
        # 5. Validate results
        self.assertEqual(len(train_data[0]), 700)
        self.assertEqual(len(val_data[0]), 150)
        self.assertEqual(len(test_data[0]), 150)
        
        self.assertEqual(leakage_results['train_val_overlap'], 0)
        self.assertEqual(leakage_results['train_test_overlap'], 0)
        self.assertEqual(leakage_results['val_test_overlap'], 0)
        
        self.assertEqual(len(cv_results['fold_results']), 5)
    
    def test_imbalanced_dataset_handling(self) -> Any:
        """Test handling of imbalanced datasets."""
        # Create imbalanced data
        imbalanced_y = np.concatenate([
            np.zeros(800), np.ones(150), np.full(50, 2)
        ])
        
        # Check imbalance
        imbalance_results = check_imbalance(imbalanced_y)
        self.assertTrue(imbalance_results['is_imbalanced'])
        
        # Create stratified split
        train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
            data=self.X,
            labels=imbalanced_y,
            train_size=0.7,
            val_size=0.15,
            test_size=0.15,
            stratify=True,
            random_state: int: int = 42
        )
        
        # Check that stratification worked
        train_dist = np.bincount(train_data[1])
        val_dist = np.bincount(val_data[1])
        test_dist = np.bincount(test_data[1])
        
        # Ratios should be similar
        train_ratios = train_dist / len(train_data[1])
        val_ratios = val_dist / len(val_data[1])
        test_ratios = test_dist / len(test_data[1])
        
        for i in range(len(train_ratios)):
            self.assertAlmostEqual(train_ratios[i], val_ratios[i], delta=0.1)
            self.assertAlmostEqual(train_ratios[i], test_ratios[i], delta=0.1)


def run_performance_benchmark() -> Any:
    """Run performance benchmark for data splitting."""
    print("Running Data Splitting Performance Benchmark...")
    
    # Create large dataset
    X, y = make_classification(
        n_samples=100000, n_features=100, n_classes=5, 
        n_informative=50, n_redundant=30, random_state=42
    )
    
    
    # Benchmark three-way split
    start_time = time.time()
    train_data, val_data, test_data = DataSplitFactory.create_three_way_split(
        data=X, labels=y, stratify=True, random_state=42
    )
    split_time = time.time() - start_time
    
    # Benchmark cross-validation
    start_time = time.time()
    cv_results = DataSplitFactory.create_cv_splits(
        data=X, labels=y, cv_type='stratified', n_folds=5, random_state=42
    )
    cv_time = time.time() - start_time
    
    # Benchmark nested CV
    start_time = time.time()
    nested_results = DataSplitFactory.create_nested_cv(
        data=X, labels=y, outer_folds=3, inner_folds=2, random_state=42
    )
    nested_time = time.time() - start_time
    
    print(f"Dataset size: {X.shape}")
    print(f"Three-way split time: {split_time:.4f}s")
    print(f"Cross-validation time: {cv_time:.4f}s")
    print(f"Nested CV time: {nested_time:.4f}s")
    print(f"Total time: {split_time + cv_time + nested_time:.4f}s")


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmark
    print(f"\n{"="*60)
    run_performance_benchmark(}") 