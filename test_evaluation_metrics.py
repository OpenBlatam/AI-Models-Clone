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
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from evaluation_metrics_system import (
            from sklearn.metrics import balanced_accuracy_score
    import time
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for Evaluation Metrics System
=======================================

This module provides comprehensive tests for the evaluation metrics system,
including tests for classification, regression, object detection, segmentation,
and time series metrics.
"""


# Import the system under test
    BaseMetric, ClassificationMetrics, RegressionMetrics, ObjectDetectionMetrics,
    SegmentationMetrics, TimeSeriesMetrics, MetricCalculator, MetricVisualizer,
    StatisticalTesting, get_task_metrics, evaluate_classification, evaluate_regression,
    evaluate_object_detection, evaluate_segmentation, evaluate_time_series
)


class TestClassificationMetrics(unittest.TestCase):
    """Test cases for ClassificationMetrics class."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=3, 
            n_informative=5, n_redundant=3, random_state=42
        )
        
        # Create a simple classifier
        self.classifier = RandomForestClassifier(n_estimators=10, random_state=42)
        self.classifier.fit(self.X, self.y)
        
        # Get predictions
        self.y_pred = self.classifier.predict(self.X)
        self.y_pred_proba = self.classifier.predict_proba(self.X)
        
        # Create metrics instance
        self.metrics = ClassificationMetrics(average='weighted')
    
    def test_accuracy(self) -> Any:
        """Test accuracy calculation."""
        accuracy = self.metrics.accuracy(self.y, self.y_pred)
        self.assertIsInstance(accuracy, float)
        self.assertGreaterEqual(accuracy, 0.0)
        self.assertLessEqual(accuracy, 1.0)
    
    def test_precision(self) -> Any:
        """Test precision calculation."""
        precision = self.metrics.precision(self.y, self.y_pred)
        self.assertIsInstance(precision, float)
        self.assertGreaterEqual(precision, 0.0)
        self.assertLessEqual(precision, 1.0)
    
    def test_recall(self) -> Any:
        """Test recall calculation."""
        recall = self.metrics.recall(self.y, self.y_pred)
        self.assertIsInstance(recall, float)
        self.assertGreaterEqual(recall, 0.0)
        self.assertLessEqual(recall, 1.0)
    
    def test_f1_score(self) -> Any:
        """Test F1 score calculation."""
        f1 = self.metrics.f1_score(self.y, self.y_pred)
        self.assertIsInstance(f1, float)
        self.assertGreaterEqual(f1, 0.0)
        self.assertLessEqual(f1, 1.0)
    
    def test_f_beta_score(self) -> Any:
        """Test F-beta score calculation."""
        f2 = self.metrics.f_beta_score(self.y, self.y_pred, beta=2.0)
        self.assertIsInstance(f2, float)
        self.assertGreaterEqual(f2, 0.0)
        self.assertLessEqual(f2, 1.0)
    
    def test_roc_auc(self) -> Any:
        """Test ROC AUC calculation."""
        # Binary classification for ROC AUC
        y_binary = (self.y == 0).astype(int)
        y_proba_binary = self.y_pred_proba[:, 0]
        
        roc_auc = self.metrics.roc_auc(y_binary, y_proba_binary.reshape(-1, 1))
        self.assertIsInstance(roc_auc, float)
        self.assertGreaterEqual(roc_auc, 0.0)
        self.assertLessEqual(roc_auc, 1.0)
    
    def test_pr_auc(self) -> Any:
        """Test Precision-Recall AUC calculation."""
        # Binary classification for PR AUC
        y_binary = (self.y == 0).astype(int)
        y_proba_binary = self.y_pred_proba[:, 0]
        
        pr_auc = self.metrics.pr_auc(y_binary, y_proba_binary.reshape(-1, 1))
        self.assertIsInstance(pr_auc, float)
        self.assertGreaterEqual(pr_auc, 0.0)
        self.assertLessEqual(pr_auc, 1.0)
    
    def test_log_loss(self) -> Any:
        """Test log loss calculation."""
        log_loss_val = self.metrics.log_loss(self.y, self.y_pred_proba)
        self.assertIsInstance(log_loss_val, float)
        self.assertGreaterEqual(log_loss_val, 0.0)
    
    def test_confusion_matrix_metrics(self) -> Any:
        """Test confusion matrix metrics."""
        cm_metrics = self.metrics.confusion_matrix_metrics(self.y, self.y_pred)
        
        self.assertIsInstance(cm_metrics, dict)
        expected_keys: List[Any] = [
            'true_negatives', 'false_positives', 'false_negatives', 'true_positives',
            'sensitivity', 'specificity', 'positive_predictive_value',
            'negative_predictive_value', 'balanced_accuracy'
        ]
        
        for key in expected_keys:
            self.assertIn(key, cm_metrics)
            self.assertIsInstance(cm_metrics[key], (int, float))
    
    def test_matthews_correlation(self) -> Any:
        """Test Matthews correlation coefficient."""
        # Binary classification for Matthews correlation
        y_binary = (self.y == 0).astype(int)
        y_pred_binary = (self.y_pred == 0).astype(int)
        
        mcc = self.metrics.matthews_correlation(y_binary, y_pred_binary)
        self.assertIsInstance(mcc, float)
        self.assertGreaterEqual(mcc, -1.0)
        self.assertLessEqual(mcc, 1.0)
    
    def test_cohen_kappa(self) -> Any:
        """Test Cohen's kappa."""
        kappa = self.metrics.cohen_kappa(self.y, self.y_pred)
        self.assertIsInstance(kappa, float)
        self.assertGreaterEqual(kappa, -1.0)
        self.assertLessEqual(kappa, 1.0)
    
    def test_hamming_loss(self) -> Any:
        """Test Hamming loss."""
        hamming = self.metrics.hamming_loss(self.y, self.y_pred)
        self.assertIsInstance(hamming, float)
        self.assertGreaterEqual(hamming, 0.0)
        self.assertLessEqual(hamming, 1.0)
    
    def test_jaccard_score(self) -> Any:
        """Test Jaccard score."""
        jaccard = self.metrics.jaccard_score(self.y, self.y_pred)
        self.assertIsInstance(jaccard, float)
        self.assertGreaterEqual(jaccard, 0.0)
        self.assertLessEqual(jaccard, 1.0)


class TestRegressionMetrics(unittest.TestCase):
    """Test cases for RegressionMetrics class."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_regression(
            n_samples=1000, n_features=10, n_informative=5, 
            noise=0.1, random_state=42
        )
        
        # Create a simple regressor
        self.regressor = RandomForestRegressor(n_estimators=10, random_state=42)
        self.regressor.fit(self.X, self.y)
        
        # Get predictions
        self.y_pred = self.regressor.predict(self.X)
        
        # Create metrics instance
        self.metrics = RegressionMetrics()
    
    def test_mse(self) -> Any:
        """Test Mean Squared Error calculation."""
        mse = self.metrics.mse(self.y, self.y_pred)
        self.assertIsInstance(mse, float)
        self.assertGreaterEqual(mse, 0.0)
    
    def test_rmse(self) -> Any:
        """Test Root Mean Squared Error calculation."""
        rmse = self.metrics.rmse(self.y, self.y_pred)
        self.assertIsInstance(rmse, float)
        self.assertGreaterEqual(rmse, 0.0)
    
    def test_mae(self) -> Any:
        """Test Mean Absolute Error calculation."""
        mae = self.metrics.mae(self.y, self.y_pred)
        self.assertIsInstance(mae, float)
        self.assertGreaterEqual(mae, 0.0)
    
    def test_r2_score(self) -> Any:
        """Test R² score calculation."""
        r2 = self.metrics.r2_score(self.y, self.y_pred)
        self.assertIsInstance(r2, float)
        self.assertLessEqual(r2, 1.0)
    
    def test_adjusted_r2(self) -> Any:
        """Test adjusted R² score calculation."""
        adjusted_r2 = self.metrics.adjusted_r2(self.y, self.y_pred, n_features=10)
        self.assertIsInstance(adjusted_r2, float)
        self.assertLessEqual(adjusted_r2, 1.0)
    
    def test_mape(self) -> Any:
        """Test Mean Absolute Percentage Error calculation."""
        mape = self.metrics.mape(self.y, self.y_pred)
        self.assertIsInstance(mape, float)
        self.assertGreaterEqual(mape, 0.0)
    
    def test_smape(self) -> Any:
        """Test Symmetric Mean Absolute Percentage Error calculation."""
        smape = self.metrics.smape(self.y, self.y_pred)
        self.assertIsInstance(smape, float)
        self.assertGreaterEqual(smape, 0.0)
    
    def test_huber_loss(self) -> Any:
        """Test Huber loss calculation."""
        huber = self.metrics.huber_loss(self.y, self.y_pred, delta=1.0)
        self.assertIsInstance(huber, float)
        self.assertGreaterEqual(huber, 0.0)
    
    def test_log_cosh_loss(self) -> Any:
        """Test Log-Cosh loss calculation."""
        log_cosh = self.metrics.log_cosh_loss(self.y, self.y_pred)
        self.assertIsInstance(log_cosh, float)
        self.assertGreaterEqual(log_cosh, 0.0)
    
    def test_pearson_correlation(self) -> Any:
        """Test Pearson correlation calculation."""
        pearson = self.metrics.pearson_correlation(self.y, self.y_pred)
        self.assertIsInstance(pearson, float)
        self.assertGreaterEqual(pearson, -1.0)
        self.assertLessEqual(pearson, 1.0)
    
    def test_spearman_correlation(self) -> Any:
        """Test Spearman correlation calculation."""
        spearman = self.metrics.spearman_correlation(self.y, self.y_pred)
        self.assertIsInstance(spearman, float)
        self.assertGreaterEqual(spearman, -1.0)
        self.assertLessEqual(spearman, 1.0)
    
    def test_max_error(self) -> Any:
        """Test maximum error calculation."""
        max_err = self.metrics.max_error(self.y, self.y_pred)
        self.assertIsInstance(max_err, float)
        self.assertGreaterEqual(max_err, 0.0)
    
    def test_mean_absolute_deviation(self) -> Any:
        """Test Mean Absolute Deviation calculation."""
        mad = self.metrics.mean_absolute_deviation(self.y, self.y_pred)
        self.assertIsInstance(mad, float)
        self.assertGreaterEqual(mad, 0.0)
    
    def test_explained_variance(self) -> Any:
        """Test explained variance calculation."""
        explained_var = self.metrics.explained_variance(self.y, self.y_pred)
        self.assertIsInstance(explained_var, float)
        self.assertLessEqual(explained_var, 1.0)


class TestObjectDetectionMetrics(unittest.TestCase):
    """Test cases for ObjectDetectionMetrics class."""
    
    def setUp(self) -> Any:
        # Create test bounding boxes
        self.box1 = np.array([0, 0, 10, 10])  # [x1, y1, x2, y2]
        self.box2 = np.array([5, 5, 15, 15])
        self.box3 = np.array([20, 20, 30, 30])  # No overlap
        
        # Create metrics instance
        self.metrics = ObjectDetectionMetrics(iou_threshold=0.5)
    
    def test_calculate_iou(self) -> Any:
        """Test IoU calculation."""
        # Test overlapping boxes
        iou = self.metrics.calculate_iou(self.box1, self.box2)
        self.assertIsInstance(iou, float)
        self.assertGreaterEqual(iou, 0.0)
        self.assertLessEqual(iou, 1.0)
        
        # Test non-overlapping boxes
        iou_no_overlap = self.metrics.calculate_iou(self.box1, self.box3)
        self.assertEqual(iou_no_overlap, 0.0)
        
        # Test identical boxes
        iou_identical = self.metrics.calculate_iou(self.box1, self.box1)
        self.assertEqual(iou_identical, 1.0)
    
    def test_calculate_map(self) -> Any:
        """Test mAP calculation."""
        # Create simple ground truth and predictions
        ground_truth: List[Any] = [[self.box1], [self.box2]]
        predictions: List[Any] = [[self.box1], [self.box2]]
        
        map_results = self.metrics.calculate_map(ground_truth, predictions)
        
        self.assertIsInstance(map_results, dict)
        self.assertIn('mAP', map_results)
        self.assertIn('mAP_50', map_results)
        self.assertIn('mAP_75', map_results)
        self.assertIn('mAP_90', map_results)
        
        for key, value in map_results.items():
            self.assertIsInstance(value, float)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)


class TestSegmentationMetrics(unittest.TestCase):
    """Test cases for SegmentationMetrics class."""
    
    def setUp(self) -> Any:
        # Create test segmentation masks
        self.y_true = np.random.randint(0, 3, size=(100, 100))
        self.y_pred = np.random.randint(0, 3, size=(100, 100))
        
        # Create metrics instance
        self.metrics = SegmentationMetrics(num_classes=3)
    
    def test_pixel_accuracy(self) -> Any:
        """Test pixel accuracy calculation."""
        accuracy = self.metrics.pixel_accuracy(self.y_true, self.y_pred)
        self.assertIsInstance(accuracy, float)
        self.assertGreaterEqual(accuracy, 0.0)
        self.assertLessEqual(accuracy, 1.0)
    
    def test_mean_pixel_accuracy(self) -> Any:
        """Test mean pixel accuracy calculation."""
        mean_accuracy = self.metrics.mean_pixel_accuracy(self.y_true, self.y_pred)
        self.assertIsInstance(mean_accuracy, float)
        self.assertGreaterEqual(mean_accuracy, 0.0)
        self.assertLessEqual(mean_accuracy, 1.0)
    
    def test_dice_coefficient(self) -> Any:
        """Test Dice coefficient calculation."""
        # Create binary masks for Dice coefficient
        y_true_binary = (self.y_true == 1).astype(int)
        y_pred_binary = (self.y_pred == 1).astype(int)
        
        dice = self.metrics.dice_coefficient(y_true_binary, y_pred_binary)
        self.assertIsInstance(dice, float)
        self.assertGreaterEqual(dice, 0.0)
        self.assertLessEqual(dice, 1.0)
    
    def test_mean_dice_coefficient(self) -> Any:
        """Test mean Dice coefficient calculation."""
        mean_dice = self.metrics.mean_dice_coefficient(self.y_true, self.y_pred)
        self.assertIsInstance(mean_dice, float)
        self.assertGreaterEqual(mean_dice, 0.0)
        self.assertLessEqual(mean_dice, 1.0)
    
    def test_iou_score(self) -> Any:
        """Test IoU score calculation."""
        # Create binary masks for IoU
        y_true_binary = (self.y_true == 1).astype(int)
        y_pred_binary = (self.y_pred == 1).astype(int)
        
        iou = self.metrics.iou_score(y_true_binary, y_pred_binary)
        self.assertIsInstance(iou, float)
        self.assertGreaterEqual(iou, 0.0)
        self.assertLessEqual(iou, 1.0)
    
    def test_mean_iou_score(self) -> Any:
        """Test mean IoU score calculation."""
        mean_iou = self.metrics.mean_iou_score(self.y_true, self.y_pred)
        self.assertIsInstance(mean_iou, float)
        self.assertGreaterEqual(mean_iou, 0.0)
        self.assertLessEqual(mean_iou, 1.0)


class TestTimeSeriesMetrics(unittest.TestCase):
    """Test cases for TimeSeriesMetrics class."""
    
    def setUp(self) -> Any:
        # Create test time series data
        np.random.seed(42)
        self.y_train = np.random.randn(100)
        self.y_true = np.random.randn(50)
        self.y_pred = self.y_true + np.random.randn(50) * 0.1
        
        # Create metrics instance
        self.metrics = TimeSeriesMetrics()
    
    def test_mase(self) -> Any:
        """Test MASE calculation."""
        mase = self.metrics.mase(self.y_true, self.y_pred, self.y_train, seasonality=1)
        self.assertIsInstance(mase, float)
        self.assertGreaterEqual(mase, 0.0)
    
    def test_smape(self) -> Any:
        """Test SMAPE calculation."""
        smape = self.metrics.smape(self.y_true, self.y_pred)
        self.assertIsInstance(smape, float)
        self.assertGreaterEqual(smape, 0.0)
    
    def test_directional_accuracy(self) -> Any:
        """Test directional accuracy calculation."""
        # Create data with clear trends
        y_true_trend = np.arange(10)
        y_pred_trend = np.arange(10) + 0.1
        
        directional_acc = self.metrics.directional_accuracy(y_true_trend, y_pred_trend)
        self.assertIsInstance(directional_acc, float)
        self.assertGreaterEqual(directional_acc, 0.0)
        self.assertLessEqual(directional_acc, 1.0)
    
    def test_theil_u(self) -> Any:
        """Test Theil's U statistic calculation."""
        theil_u = self.metrics.theil_u(self.y_true, self.y_pred)
        self.assertIsInstance(theil_u, float)
        self.assertGreaterEqual(theil_u, 0.0)


class TestMetricCalculator(unittest.TestCase):
    """Test cases for MetricCalculator class."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=3, random_state=42
        )
        
        # Create classifier and get predictions
        self.classifier = RandomForestClassifier(n_estimators=10, random_state=42)
        self.classifier.fit(self.X, self.y)
        self.y_pred = self.classifier.predict(self.X)
        self.y_pred_proba = self.classifier.predict_proba(self.X)
    
    def test_classification_calculator(self) -> Any:
        """Test classification metric calculator."""
        calculator = MetricCalculator('classification', average='weighted')
        
        results = calculator.compute_metrics(self.y, self.y_pred, self.y_pred_proba)
        
        self.assertIsInstance(results, dict)
        expected_metrics: List[Any] = ['accuracy', 'precision', 'recall', 'f1_score', 'f2_score']
        
        for metric in expected_metrics:
            self.assertIn(metric, results)
            self.assertIsInstance(results[metric], float)
    
    def test_regression_calculator(self) -> Any:
        """Test regression metric calculator."""
        # Create regression data
        X_reg, y_reg = make_regression(n_samples=1000, n_features=10, random_state=42)
        regressor = RandomForestRegressor(n_estimators=10, random_state=42)
        regressor.fit(X_reg, y_reg)
        y_pred_reg = regressor.predict(X_reg)
        
        calculator = MetricCalculator('regression')
        results = calculator.compute_metrics(y_reg, y_pred_reg)
        
        self.assertIsInstance(results, dict)
        expected_metrics: List[Any] = ['mse', 'rmse', 'mae', 'r2_score', 'mape']
        
        for metric in expected_metrics:
            self.assertIn(metric, results)
            self.assertIsInstance(results[metric], float)
    
    def test_add_custom_metric(self) -> Any:
        """Test adding custom metric."""
        calculator = MetricCalculator('classification')
        
        def custom_metric(y_true, y_pred) -> Any:
            return np.mean(y_true == y_pred)
        
        calculator.add_custom_metric('custom_accuracy', custom_metric)
        results = calculator.compute_metrics(self.y, self.y_pred)
        
        self.assertIn('custom_accuracy', results)
        self.assertIsInstance(results['custom_accuracy'], float)
    
    def test_get_results(self) -> Optional[Dict[str, Any]]:
        """Test getting results."""
        calculator = MetricCalculator('classification')
        calculator.compute_metrics(self.y, self.y_pred)
        
        results = calculator.get_results()
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)
    
    def test_get_best_metric(self) -> Optional[Dict[str, Any]]:
        """Test getting best metric."""
        calculator = MetricCalculator('classification')
        calculator.compute_metrics(self.y, self.y_pred)
        
        best_value, best_index = calculator.get_best_metric('accuracy', mode='max')
        self.assertIsInstance(best_value, float)
        self.assertIsInstance(best_index, int)
    
    def test_compare_models(self) -> Any:
        """Test model comparison."""
        calculator = MetricCalculator('classification')
        
        # Create mock model results
        model_results: Dict[str, Any] = {
            'model1': {'accuracy': 0.85, 'f1_score': 0.83},
            'model2': {'accuracy': 0.87, 'f1_score': 0.85},
            'model3': {'accuracy': 0.82, 'f1_score': 0.80}
        }
        
        comparison = calculator.compare_models(model_results, 'accuracy')
        
        self.assertIsInstance(comparison, dict)
        self.assertIn('best_model', comparison)
        self.assertIn('best_score', comparison)
        self.assertIn('worst_model', comparison)
        self.assertIn('worst_score', comparison)
        self.assertIn('scores', comparison)


class TestMetricVisualizer(unittest.TestCase):
    """Test cases for MetricVisualizer class."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=2, random_state=42
        )
        
        # Create classifier and get predictions
        self.classifier = RandomForestClassifier(n_estimators=10, random_state=42)
        self.classifier.fit(self.X, self.y)
        self.y_pred = self.classifier.predict(self.X)
        self.y_pred_proba = self.classifier.predict_proba(self.X)
        
        # Create visualizer
        self.visualizer = MetricVisualizer()
    
    def test_plot_confusion_matrix(self) -> Any:
        """Test confusion matrix plotting."""
        try:
            self.visualizer.plot_confusion_matrix(self.y, self.y_pred)
            plt.close()
        except Exception as e:
            self.fail(f"Confusion matrix plotting failed: {e}")
    
    def test_plot_roc_curve(self) -> Any:
        """Test ROC curve plotting."""
        try:
            self.visualizer.plot_roc_curve(self.y, self.y_pred_proba)
            plt.close()
        except Exception as e:
            self.fail(f"ROC curve plotting failed: {e}")
    
    def test_plot_precision_recall_curve(self) -> Any:
        """Test precision-recall curve plotting."""
        try:
            self.visualizer.plot_precision_recall_curve(self.y, self.y_pred_proba)
            plt.close()
        except Exception as e:
            self.fail(f"Precision-recall curve plotting failed: {e}")
    
    def test_plot_metrics_comparison(self) -> Any:
        """Test metrics comparison plotting."""
        model_results: Dict[str, Any] = {
            'Model A': {'accuracy': 0.85, 'f1_score': 0.83},
            'Model B': {'accuracy': 0.87, 'f1_score': 0.85},
            'Model C': {'accuracy': 0.82, 'f1_score': 0.80}
        }
        
        try:
            self.visualizer.plot_metrics_comparison(model_results, 'accuracy')
            plt.close()
        except Exception as e:
            self.fail(f"Metrics comparison plotting failed: {e}")
    
    def test_plot_regression_results(self) -> Any:
        """Test regression results plotting."""
        # Create regression data
        X_reg, y_reg = make_regression(n_samples=1000, n_features=10, random_state=42)
        regressor = RandomForestRegressor(n_estimators=10, random_state=42)
        regressor.fit(X_reg, y_reg)
        y_pred_reg = regressor.predict(X_reg)
        
        try:
            self.visualizer.plot_regression_results(y_reg, y_pred_reg)
            plt.close()
        except Exception as e:
            self.fail(f"Regression results plotting failed: {e}")


class TestStatisticalTesting(unittest.TestCase):
    """Test cases for StatisticalTesting class."""
    
    def setUp(self) -> Any:
        # Create test data
        np.random.seed(42)
        self.scores1 = np.random.normal(0.8, 0.1, 100)
        self.scores2 = np.random.normal(0.75, 0.1, 100)
        
        # Create statistical testing instance
        self.stats_test = StatisticalTesting()
    
    def test_paired_t_test(self) -> Any:
        """Test paired t-test."""
        result = self.stats_test.paired_t_test(self.scores1, self.scores2)
        
        self.assertIsInstance(result, dict)
        self.assertIn('test_type', result)
        self.assertIn('t_statistic', result)
        self.assertIn('p_value', result)
        self.assertIn('significant', result)
        self.assertIn('alpha', result)
        
        self.assertEqual(result['test_type'], 'paired_t_test')
        self.assertIsInstance(result['t_statistic'], float)
        self.assertIsInstance(result['p_value'], float)
        self.assertIsInstance(result['significant'], bool)
        self.assertEqual(result['alpha'], 0.05)
    
    def test_wilcoxon_test(self) -> Any:
        """Test Wilcoxon signed-rank test."""
        result = self.stats_test.wilcoxon_test(self.scores1, self.scores2)
        
        self.assertIsInstance(result, dict)
        self.assertIn('test_type', result)
        self.assertIn('statistic', result)
        self.assertIn('p_value', result)
        self.assertIn('significant', result)
        self.assertIn('alpha', result)
        
        self.assertEqual(result['test_type'], 'wilcoxon_test')
        self.assertIsInstance(result['statistic'], float)
        self.assertIsInstance(result['p_value'], float)
        self.assertIsInstance(result['significant'], bool)
        self.assertEqual(result['alpha'], 0.05)
    
    def test_mann_whitney_test(self) -> Any:
        """Test Mann-Whitney U test."""
        result = self.stats_test.mann_whitney_test(self.scores1, self.scores2)
        
        self.assertIsInstance(result, dict)
        self.assertIn('test_type', result)
        self.assertIn('statistic', result)
        self.assertIn('p_value', result)
        self.assertIn('significant', result)
        self.assertIn('alpha', result)
        
        self.assertEqual(result['test_type'], 'mann_whitney_test')
        self.assertIsInstance(result['statistic'], float)
        self.assertIsInstance(result['p_value'], float)
        self.assertIsInstance(result['significant'], bool)
        self.assertEqual(result['alpha'], 0.05)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=2, random_state=42
        )
        
        # Create classifier and get predictions
        self.classifier = RandomForestClassifier(n_estimators=10, random_state=42)
        self.classifier.fit(self.X, self.y)
        self.y_pred = self.classifier.predict(self.X)
        self.y_pred_proba = self.classifier.predict_proba(self.X)
    
    def test_get_task_metrics(self) -> Optional[Dict[str, Any]]:
        """Test get_task_metrics function."""
        calculator = get_task_metrics('classification', average='weighted')
        self.assertIsInstance(calculator, MetricCalculator)
        self.assertEqual(calculator.task_type, 'classification')
    
    def test_evaluate_classification(self) -> Any:
        """Test evaluate_classification function."""
        results = evaluate_classification(self.y, self.y_pred, self.y_pred_proba)
        
        self.assertIsInstance(results, dict)
        expected_metrics: List[Any] = ['accuracy', 'precision', 'recall', 'f1_score']
        
        for metric in expected_metrics:
            self.assertIn(metric, results)
            self.assertIsInstance(results[metric], float)
    
    def test_evaluate_regression(self) -> Any:
        """Test evaluate_regression function."""
        # Create regression data
        X_reg, y_reg = make_regression(n_samples=1000, n_features=10, random_state=42)
        regressor = RandomForestRegressor(n_estimators=10, random_state=42)
        regressor.fit(X_reg, y_reg)
        y_pred_reg = regressor.predict(X_reg)
        
        results = evaluate_regression(y_reg, y_pred_reg)
        
        self.assertIsInstance(results, dict)
        expected_metrics: List[Any] = ['mse', 'rmse', 'mae', 'r2_score']
        
        for metric in expected_metrics:
            self.assertIn(metric, results)
            self.assertIsInstance(results[metric], float)
    
    def test_evaluate_object_detection(self) -> Any:
        """Test evaluate_object_detection function."""
        # Create simple test data
        ground_truth: List[Any] = [[np.array([0, 0, 10, 10])], [np.array([5, 5, 15, 15])]]
        predictions: List[Any] = [[np.array([0, 0, 10, 10])], [np.array([5, 5, 15, 15])]]
        
        results = evaluate_object_detection(ground_truth, predictions)
        
        self.assertIsInstance(results, dict)
        self.assertIn('mAP', results)
        self.assertIsInstance(results['mAP'], float)
    
    def test_evaluate_segmentation(self) -> Any:
        """Test evaluate_segmentation function."""
        # Create test segmentation masks
        y_true = np.random.randint(0, 3, size=(100, 100))
        y_pred = np.random.randint(0, 3, size=(100, 100))
        
        results = evaluate_segmentation(y_true, y_pred, num_classes=3)
        
        self.assertIsInstance(results, dict)
        expected_metrics: List[Any] = ['pixel_accuracy', 'mean_pixel_accuracy', 'dice_coefficient']
        
        for metric in expected_metrics:
            self.assertIn(metric, results)
            self.assertIsInstance(results[metric], float)
    
    def test_evaluate_time_series(self) -> Any:
        """Test evaluate_time_series function."""
        # Create test time series data
        np.random.seed(42)
        y_train = np.random.randn(100)
        y_true = np.random.randn(50)
        y_pred = y_true + np.random.randn(50) * 0.1
        
        results = evaluate_time_series(y_true, y_pred, y_train)
        
        self.assertIsInstance(results, dict)
        expected_metrics: List[Any] = ['mase', 'smape', 'directional_accuracy']
        
        for metric in expected_metrics:
            self.assertIn(metric, results)
            self.assertIsInstance(results[metric], float)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""
    
    def setUp(self) -> Any:
        # Create test data
        self.X, self.y = make_classification(
            n_samples=1000, n_features=10, n_classes=3, random_state=42
        )
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
    
    def test_complete_classification_evaluation(self) -> Any:
        """Test complete classification evaluation workflow."""
        # Train multiple models
        models: Dict[str, Any] = {
            'RandomForest': RandomForestClassifier(n_estimators=10, random_state=42),
            'RandomForest2': RandomForestClassifier(n_estimators=20, random_state=42)
        }
        
        model_results: Dict[str, Any] = {}
        
        for name, model in models.items():
            # Train model
            model.fit(self.X_train, self.y_train)
            
            # Get predictions
            y_pred = model.predict(self.X_test)
            y_pred_proba = model.predict_proba(self.X_test)
            
            # Evaluate
            results = evaluate_classification(self.y_test, y_pred, y_pred_proba)
            model_results[name] = results
        
        # Compare models
        calculator = MetricCalculator('classification')
        comparison = calculator.compare_models(model_results, 'accuracy')
        
        self.assertIsInstance(comparison, dict)
        self.assertIn('best_model', comparison)
        self.assertIn('best_score', comparison)
        
        # Statistical testing
        stats_test = StatisticalTesting()
        scores1: List[Any] = [model_results['RandomForest']['accuracy']] * 10
        scores2: List[Any] = [model_results['RandomForest2']['accuracy']] * 10
        
        test_result = stats_test.paired_t_test(scores1, scores2)
        self.assertIsInstance(test_result, dict)
        self.assertIn('significant', test_result)
    
    def test_complete_regression_evaluation(self) -> Any:
        """Test complete regression evaluation workflow."""
        # Create regression data
        X_reg, y_reg = make_regression(n_samples=1000, n_features=10, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(
            X_reg, y_reg, test_size=0.2, random_state=42
        )
        
        # Train multiple models
        models: Dict[str, Any] = {
            'RandomForest': RandomForestRegressor(n_estimators=10, random_state=42),
            'RandomForest2': RandomForestRegressor(n_estimators=20, random_state=42)
        }
        
        model_results: Dict[str, Any] = {}
        
        for name, model in models.items():
            # Train model
            model.fit(X_train, y_train)
            
            # Get predictions
            y_pred = model.predict(X_test)
            
            # Evaluate
            results = evaluate_regression(y_test, y_pred)
            model_results[name] = results
        
        # Compare models
        calculator = MetricCalculator('regression')
        comparison = calculator.compare_models(model_results, 'r2_score')
        
        self.assertIsInstance(comparison, dict)
        self.assertIn('best_model', comparison)
        self.assertIn('best_score', comparison)
    
    def test_custom_metric_integration(self) -> Any:
        """Test custom metric integration."""
        calculator = MetricCalculator('classification')
        
        # Add custom metric
        def custom_balanced_accuracy(y_true, y_pred) -> Any:
            return balanced_accuracy_score(y_true, y_pred)
        
        calculator.add_custom_metric('balanced_accuracy', custom_balanced_accuracy)
        
        # Train model and evaluate
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        
        results = calculator.compute_metrics(self.y_test, y_pred)
        
        self.assertIn('balanced_accuracy', results)
        self.assertIsInstance(results['balanced_accuracy'], float)
        self.assertGreaterEqual(results['balanced_accuracy'], 0.0)
        self.assertLessEqual(results['balanced_accuracy'], 1.0)


def run_performance_benchmark() -> Any:
    """Run performance benchmark for the evaluation metrics system."""
    print("Running Evaluation Metrics Performance Benchmark...")
    
    
    # Create large datasets
    X_large, y_large = make_classification(
        n_samples=10000, n_features=100, n_classes=5, random_state=42
    )
    
    # Train model
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_large, y_large)
    y_pred = model.predict(X_large)
    y_pred_proba = model.predict_proba(X_large)
    
    # Benchmark classification metrics
    print("\nBenchmarking Classification Metrics...")
    
    metrics = ClassificationMetrics()
    start_time = time.time()
    
    accuracy = metrics.accuracy(y_large, y_pred)
    precision = metrics.precision(y_large, y_pred)
    recall = metrics.recall(y_large, y_pred)
    f1 = metrics.f1_score(y_large, y_pred)
    roc_auc = metrics.roc_auc(y_large, y_pred_proba)
    
    end_time = time.time()
    classification_time = end_time - start_time
    
    print(f"Classification metrics computed in {classification_time:.4f} seconds")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"ROC AUC: {roc_auc:.4f}")
    
    # Benchmark regression metrics
    print("\nBenchmarking Regression Metrics...")
    
    X_reg, y_reg = make_regression(n_samples=10000, n_features=100, random_state=42)
    regressor = RandomForestRegressor(n_estimators=50, random_state=42)
    regressor.fit(X_reg, y_reg)
    y_pred_reg = regressor.predict(X_reg)
    
    reg_metrics = RegressionMetrics()
    start_time = time.time()
    
    mse = reg_metrics.mse(y_reg, y_pred_reg)
    rmse = reg_metrics.rmse(y_reg, y_pred_reg)
    mae = reg_metrics.mae(y_reg, y_pred_reg)
    r2 = reg_metrics.r2_score(y_reg, y_pred_reg)
    pearson = reg_metrics.pearson_correlation(y_reg, y_pred_reg)
    
    end_time = time.time()
    regression_time = end_time - start_time
    
    print(f"Regression metrics computed in {regression_time:.4f} seconds")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"R²: {r2:.4f}")
    print(f"Pearson Correlation: {pearson:.4f}")
    
    # Benchmark metric calculator
    print("\nBenchmarking Metric Calculator...")
    
    calculator = MetricCalculator('classification')
    start_time = time.time()
    
    results = calculator.compute_metrics(y_large, y_pred, y_pred_proba)
    
    end_time = time.time()
    calculator_time = end_time - start_time
    
    print(f"Metric calculator computed {len(results)} metrics in {calculator_time:.4f} seconds")
    
    # Summary
    print(f"\n{"="*60)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("="*60)
    print(f"Classification Metrics: {classification_time:.4f}s")
    print(f"Regression Metrics: {regression_time:.4f}s")
    print(f"Metric Calculator: {calculator_time:.4f}s")
    print(f"Total Metrics Computed: {len(results)}")


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance benchmark
    print("\n"}="*60)
    run_performance_benchmark() 