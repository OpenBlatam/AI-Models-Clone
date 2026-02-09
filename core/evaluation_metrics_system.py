from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import os
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict, Counter
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import (
from sklearn.preprocessing import label_binarize
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import logging
        from sklearn.metrics import cohen_kappa_score
        from sklearn.metrics import jaccard_score
        from sklearn.metrics import explained_variance_score
from typing import Any, List, Dict, Optional
import asyncio
"""
Evaluation Metrics System
=========================

This module provides comprehensive evaluation metrics for various machine learning tasks,
including classification, regression, object detection, segmentation, and more.

Features:
- Task-specific metrics for different ML problems
- Comprehensive classification metrics (accuracy, precision, recall, F1, AUC, etc.)
- Regression metrics (MSE, MAE, R², RMSE, MAPE, etc.)
- Object detection metrics (mAP, IoU, precision-recall curves)
- Segmentation metrics (Dice coefficient, IoU, pixel accuracy)
- Time series metrics (MASE, SMAPE, directional accuracy)
- Custom metric creation and combination
- Visualization tools for metrics
- Statistical significance testing
- Multi-class and multi-label support
"""

    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    classification_report, mean_squared_error, mean_absolute_error,
    r2_score, mean_absolute_percentage_error, log_loss,
    precision_recall_curve, roc_curve, auc
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)


class BaseMetric(ABC):
    """Abstract base class for all evaluation metrics."""
    
    def __init__(self, name: str, task_type: str) -> Any:
        
    """__init__ function."""
self.name = name
        self.task_type = task_type
        self.history: List[Any] = []
    
    @abstractmethod
    def compute(self, y_true: Any, y_pred: Any, **kwargs) -> float:
        """Compute the metric value."""
        pass
    
    def update(self, y_true: Any, y_pred: Any, **kwargs) -> bool:
        """Update metric with new data."""
        value = self.compute(y_true, y_pred, **kwargs)
        self.history.append(value)
        return value
    
    def get_history(self) -> List[float]:
        """Get metric history."""
        return self.history.copy()
    
    def reset(self) -> Any:
        """Reset metric history."""
        self.history: List[Any] = []
    
    def get_name(self) -> str:
        """Get metric name."""
        return self.name
    
    def get_task_type(self) -> str:
        """Get task type."""
        return self.task_type


class ClassificationMetrics:
    """Comprehensive classification metrics."""
    
    def __init__(self, average: str: str: str = 'weighted', zero_division: int = 0) -> Any:
        
    """__init__ function."""
self.average = average
        self.zero_division = zero_division
    
    def accuracy(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute accuracy score."""
        return accuracy_score(y_true, y_pred)
    
    def precision(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute precision score."""
        return precision_score(y_true, y_pred, average=self.average, zero_division=self.zero_division)
    
    def recall(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute recall score."""
        return recall_score(y_true, y_pred, average=self.average, zero_division=self.zero_division)
    
    def f1_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute F1 score."""
        return f1_score(y_true, y_pred, average=self.average, zero_division=self.zero_division)
    
    def f_beta_score(self, y_true: np.ndarray, y_pred: np.ndarray, beta: float = 2.0) -> float:
        """Compute F-beta score."""
        precision = self.precision(y_true, y_pred)
        recall = self.recall(y_true, y_pred)
        
        if precision + recall == 0:
            return 0.0
        
        return (1 + beta**2) * (precision * recall) / ((beta**2 * precision) + recall)
    
    def roc_auc(self, y_true: np.ndarray, y_pred_proba: np.ndarray, multi_class: str: str: str = 'ovr') -> float:
        """Compute ROC AUC score."""
        if len(np.unique(y_true)) == 2:
            return roc_auc_score(y_true, y_pred_proba[:, 1])
        else:
            return roc_auc_score(y_true, y_pred_proba, multi_class=multi_class)
    
    def pr_auc(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """Compute Precision-Recall AUC score."""
        if len(np.unique(y_true)) == 2:
            return average_precision_score(y_true, y_pred_proba[:, 1])
        else:
            return average_precision_score(y_true, y_pred_proba, average=self.average)
    
    def log_loss(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """Compute log loss."""
        return log_loss(y_true, y_pred_proba)
    
    def confusion_matrix_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Compute confusion matrix based metrics."""
        cm = confusion_matrix(y_true, y_pred)
        
        # Calculate metrics from confusion matrix
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)
        
        metrics: Dict[str, Any] = {
            'true_negatives': tn,
            'false_positives': fp,
            'false_negatives': fn,
            'true_positives': tp,
            'sensitivity': tp / (tp + fn) if (tp + fn) > 0 else 0,
            'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
            'positive_predictive_value': tp / (tp + fp) if (tp + fp) > 0 else 0,
            'negative_predictive_value': tn / (tn + fn) if (tn + fn) > 0 else 0,
            'balanced_accuracy': (tp / (tp + fn) + tn / (tn + fp)) / 2 if (tp + fn) > 0 and (tn + fp) > 0 else 0
        }
        
        return metrics
    
    def matthews_correlation(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Matthews correlation coefficient."""
        cm = confusion_matrix(y_true, y_pred)
        if cm.shape != (2, 2):
            return 0.0
        
        tn, fp, fn, tp = cm.ravel()
        numerator = (tp * tn) - (fp * fn)
        denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def cohen_kappa(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Cohen's kappa."""
        return cohen_kappa_score(y_true, y_pred)
    
    def hamming_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Hamming loss for multi-label classification."""
        return np.mean(y_true != y_pred)
    
    def jaccard_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Jaccard score."""
        return jaccard_score(y_true, y_pred, average=self.average, zero_division=self.zero_division)


class RegressionMetrics:
    """Comprehensive regression metrics."""
    
    def __init__(self) -> Any:
        pass
    
    def mse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Mean Squared Error."""
        return mean_squared_error(y_true, y_pred)
    
    def rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Root Mean Squared Error."""
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    def mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Mean Absolute Error."""
        return mean_absolute_error(y_true, y_pred)
    
    def r2_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute R² score."""
        return r2_score(y_true, y_pred)
    
    def adjusted_r2(self, y_true: np.ndarray, y_pred: np.ndarray, n_features: int) -> float:
        """Compute adjusted R² score."""
        r2 = self.r2_score(y_true, y_pred)
        n = len(y_true)
        return 1 - (1 - r2) * (n - 1) / (n - n_features - 1)
    
    def mape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Mean Absolute Percentage Error."""
        return mean_absolute_percentage_error(y_true, y_pred)
    
    def smape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Symmetric Mean Absolute Percentage Error."""
        return 100 * np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))
    
    def huber_loss(self, y_true: np.ndarray, y_pred: np.ndarray, delta: float = 1.0) -> float:
        """Compute Huber loss."""
        error = y_true - y_pred
        abs_error = np.abs(error)
        quadratic = np.minimum(abs_error, delta)
        linear = abs_error - quadratic
        return np.mean(0.5 * quadratic**2 + delta * linear)
    
    def log_cosh_loss(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Log-Cosh loss."""
        return np.mean(np.log(np.cosh(y_pred - y_true)))
    
    def pearson_correlation(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Pearson correlation coefficient."""
        return pearsonr(y_true, y_pred)[0]
    
    def spearman_correlation(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Spearman correlation coefficient."""
        return spearmanr(y_true, y_pred)[0]
    
    def max_error(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute maximum error."""
        return np.max(np.abs(y_true - y_pred))
    
    def mean_absolute_deviation(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Mean Absolute Deviation."""
        return np.mean(np.abs(y_pred - np.mean(y_true)))
    
    def explained_variance(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute explained variance score."""
        return explained_variance_score(y_true, y_pred)


class ObjectDetectionMetrics:
    """Object detection metrics (mAP, IoU, etc.)."""
    
    def __init__(self, iou_threshold: float = 0.5, class_names: Optional[List[str]] = None) -> Any:
        
    """__init__ function."""
self.iou_threshold = iou_threshold
        self.class_names = class_names or []
    
    def calculate_iou(self, box1: np.ndarray, box2: np.ndarray) -> float:
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        # box format: [x1, y1, x2, y2]
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_map(self, ground_truth: List[List], predictions: List[List], 
                     iou_thresholds: List[float] = None) -> Dict[str, float]:
        """Calculate mean Average Precision (mAP)."""
        if iou_thresholds is None:
            iou_thresholds: List[Any] = [0.5, 0.75, 0.9]
        
        aps: List[Any] = []
        for iou_thresh in iou_thresholds:
            ap = self.calculate_ap(ground_truth, predictions, iou_thresh)
            aps.append(ap)
        
        return {
            'mAP': np.mean(aps),
            'mAP_50': aps[0] if len(aps) > 0 else 0.0,
            'mAP_75': aps[1] if len(aps) > 1 else 0.0,
            'mAP_90': aps[2] if len(aps) > 2 else 0.0
        }
    
    def calculate_ap(self, ground_truth: List[List], predictions: List[List], 
                    iou_threshold: float) -> float:
        """Calculate Average Precision (AP) for a specific IoU threshold."""
        # This is a simplified implementation
        # In practice, you would need more sophisticated logic for AP calculation
        
        matches: int: int = 0
        total_gt = sum(len(gt) for gt in ground_truth)
        total_pred = sum(len(pred) for pred in predictions)
        
        if total_gt == 0 or total_pred == 0:
            return 0.0
        
        for gt_boxes, pred_boxes in zip(ground_truth, predictions):
            for gt_box in gt_boxes:
                for pred_box in pred_boxes:
                    if self.calculate_iou(gt_box, pred_box) >= iou_threshold:
                        matches += 1
                        break
        
        precision = matches / total_pred if total_pred > 0 else 0.0
        recall = matches / total_gt if total_gt > 0 else 0.0
        
        return precision * recall  # Simplified AP calculation


class SegmentationMetrics:
    """Image segmentation metrics."""
    
    def __init__(self, num_classes: int, ignore_index: int = 255) -> Any:
        
    """__init__ function."""
self.num_classes = num_classes
        self.ignore_index = ignore_index
    
    def pixel_accuracy(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute pixel accuracy."""
        mask = y_true != self.ignore_index
        return np.sum((y_true[mask] == y_pred[mask])) / np.sum(mask)
    
    def mean_pixel_accuracy(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute mean pixel accuracy per class."""
        mask = y_true != self.ignore_index
        accuracies: List[Any] = []
        
        for class_id in range(self.num_classes):
            class_mask = (y_true == class_id) & mask
            if np.sum(class_mask) > 0:
                accuracy = np.sum((y_true[class_mask] == y_pred[class_mask])) / np.sum(class_mask)
                accuracies.append(accuracy)
        
        return np.mean(accuracies) if accuracies else 0.0
    
    def dice_coefficient(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Dice coefficient."""
        mask = y_true != self.ignore_index
        intersection = np.sum((y_true[mask] == 1) & (y_pred[mask] == 1))
        union = np.sum(y_true[mask] == 1) + np.sum(y_pred[mask] == 1)
        
        return 2 * intersection / union if union > 0 else 0.0
    
    def mean_dice_coefficient(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute mean Dice coefficient per class."""
        mask = y_true != self.ignore_index
        dice_scores: List[Any] = []
        
        for class_id in range(self.num_classes):
            if class_id == self.ignore_index:
                continue
            
            intersection = np.sum((y_true[mask] == class_id) & (y_pred[mask] == class_id))
            union = np.sum(y_true[mask] == class_id) + np.sum(y_pred[mask] == class_id)
            
            dice = 2 * intersection / union if union > 0 else 0.0
            dice_scores.append(dice)
        
        return np.mean(dice_scores) if dice_scores else 0.0
    
    def iou_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute IoU (Jaccard) score."""
        mask = y_true != self.ignore_index
        intersection = np.sum((y_true[mask] == 1) & (y_pred[mask] == 1))
        union = np.sum((y_true[mask] == 1) | (y_pred[mask] == 1))
        
        return intersection / union if union > 0 else 0.0
    
    def mean_iou_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute mean IoU score per class."""
        mask = y_true != self.ignore_index
        iou_scores: List[Any] = []
        
        for class_id in range(self.num_classes):
            if class_id == self.ignore_index:
                continue
            
            intersection = np.sum((y_true[mask] == class_id) & (y_pred[mask] == class_id))
            union = np.sum((y_true[mask] == class_id) | (y_pred[mask] == class_id))
            
            iou = intersection / union if union > 0 else 0.0
            iou_scores.append(iou)
        
        return np.mean(iou_scores) if iou_scores else 0.0


class TimeSeriesMetrics:
    """Time series forecasting metrics."""
    
    def __init__(self) -> Any:
        pass
    
    def mase(self, y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray, 
             seasonality: int = 1) -> float:
        """Compute Mean Absolute Scaled Error (MASE)."""
        mae = np.mean(np.abs(y_true - y_pred))
        
        # Calculate MAE of naive forecast
        if len(y_train) > seasonality:
            naive_forecast = y_train[:-seasonality]
            actual_values = y_train[seasonality:]
            mae_naive = np.mean(np.abs(actual_values - naive_forecast))
        else:
            mae_naive = np.mean(np.abs(np.diff(y_train)))
        
        return mae / mae_naive if mae_naive > 0 else float('inf')
    
    def smape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Symmetric Mean Absolute Percentage Error."""
        return 100 * np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))
    
    def directional_accuracy(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute directional accuracy."""
        if len(y_true) < 2:
            return 0.0
        
        true_direction = np.diff(y_true) > 0
        pred_direction = np.diff(y_pred) > 0
        
        return np.mean(true_direction == pred_direction)
    
    def theil_u(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Theil's U statistic."""
        if len(y_true) < 2:
            return 0.0
        
        true_diff = np.diff(y_true)
        pred_diff = np.diff(y_pred)
        
        numerator = np.sqrt(np.mean(pred_diff**2))
        denominator = np.sqrt(np.mean(true_diff**2))
        
        return numerator / denominator if denominator > 0 else float('inf')


class MetricCalculator:
    """Main class for calculating and managing evaluation metrics."""
    
    def __init__(self, task_type: str, **kwargs) -> Any:
        
    """__init__ function."""
self.task_type = task_type
        self.metrics: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}
        
        # Initialize task-specific metrics
        if task_type == 'classification':
            self.classification_metrics = ClassificationMetrics(**kwargs)
            self._init_classification_metrics()
        elif task_type == 'regression':
            self.regression_metrics = RegressionMetrics()
            self._init_regression_metrics()
        elif task_type == 'object_detection':
            self.detection_metrics = ObjectDetectionMetrics(**kwargs)
            self._init_detection_metrics()
        elif task_type == 'segmentation':
            self.segmentation_metrics = SegmentationMetrics(**kwargs)
            self._init_segmentation_metrics()
        elif task_type == 'time_series':
            self.time_series_metrics = TimeSeriesMetrics()
            self._init_time_series_metrics()
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    def _init_classification_metrics(self) -> Any:
        """Initialize classification metrics."""
        self.metrics.update({
            'accuracy': self.classification_metrics.accuracy,
            'precision': self.classification_metrics.precision,
            'recall': self.classification_metrics.recall,
            'f1_score': self.classification_metrics.f1_score,
            'f2_score': lambda y_true, y_pred: self.classification_metrics.f_beta_score(y_true, y_pred, beta=2.0),
            'matthews_correlation': self.classification_metrics.matthews_correlation,
            'cohen_kappa': self.classification_metrics.cohen_kappa,
            'hamming_loss': self.classification_metrics.hamming_loss,
            'jaccard_score': self.classification_metrics.jaccard_score
        })
    
    def _init_regression_metrics(self) -> Any:
        """Initialize regression metrics."""
        self.metrics.update({
            'mse': self.regression_metrics.mse,
            'rmse': self.regression_metrics.rmse,
            'mae': self.regression_metrics.mae,
            'r2_score': self.regression_metrics.r2_score,
            'mape': self.regression_metrics.mape,
            'smape': self.regression_metrics.smape,
            'huber_loss': self.regression_metrics.huber_loss,
            'log_cosh_loss': self.regression_metrics.log_cosh_loss,
            'pearson_correlation': self.regression_metrics.pearson_correlation,
            'spearman_correlation': self.regression_metrics.spearman_correlation,
            'max_error': self.regression_metrics.max_error,
            'explained_variance': self.regression_metrics.explained_variance
        })
    
    def _init_detection_metrics(self) -> Any:
        """Initialize object detection metrics."""
        self.metrics.update({
            'mAP': lambda gt, pred: self.detection_metrics.calculate_map(gt, pred)['mAP'],
            'mAP_50': lambda gt, pred: self.detection_metrics.calculate_map(gt, pred)['mAP_50'],
            'mAP_75': lambda gt, pred: self.detection_metrics.calculate_map(gt, pred)['mAP_75']
        })
    
    def _init_segmentation_metrics(self) -> Any:
        """Initialize segmentation metrics."""
        self.metrics.update({
            'pixel_accuracy': self.segmentation_metrics.pixel_accuracy,
            'mean_pixel_accuracy': self.segmentation_metrics.mean_pixel_accuracy,
            'dice_coefficient': self.segmentation_metrics.dice_coefficient,
            'mean_dice_coefficient': self.segmentation_metrics.mean_dice_coefficient,
            'iou_score': self.segmentation_metrics.iou_score,
            'mean_iou_score': self.segmentation_metrics.mean_iou_score
        })
    
    def _init_time_series_metrics(self) -> Any:
        """Initialize time series metrics."""
        self.metrics.update({
            'mase': self.time_series_metrics.mase,
            'smape': self.time_series_metrics.smape,
            'directional_accuracy': self.time_series_metrics.directional_accuracy,
            'theil_u': self.time_series_metrics.theil_u
        })
    
    def add_custom_metric(self, name: str, metric_func: Callable) -> Any:
        """Add a custom metric."""
        self.metrics[name] = metric_func
    
    def compute_metrics(self, y_true: Any, y_pred: Any, y_pred_proba: Optional[Any] = None,
                       **kwargs) -> Dict[str, float]:
        """Compute all available metrics."""
        results: Dict[str, Any] = {}
        
        for metric_name, metric_func in self.metrics.items():
            try:
                if metric_name in ['roc_auc', 'pr_auc', 'log_loss'] and y_pred_proba is not None:
                    results[metric_name] = metric_func(y_true, y_pred_proba)
                elif metric_name == 'mase' and 'y_train' in kwargs:
                    results[metric_name] = metric_func(y_true, y_pred, kwargs['y_train'], 
                                                     kwargs.get('seasonality', 1))
                else:
                    results[metric_name] = metric_func(y_true, y_pred)
            except Exception as e:
                logger.warning(f"Failed to compute {metric_name}: {e}")
                results[metric_name] = float('nan')
        
        self.results = results
        return results
    
    def get_results(self) -> Dict[str, float]:
        """Get the last computed results."""
        return self.results.copy()
    
    def get_best_metric(self, metric_name: str, mode: str: str: str = 'max') -> Tuple[float, int]:
        """Get the best value and index for a specific metric."""
        if metric_name not in self.results:
            raise ValueError(f"Metric {metric_name} not found in results")
        
        value = self.results[metric_name]
        if np.isnan(value):
            return float('nan'), -1
        
        return value, 0  # For single computation, index is always 0
    
    def compare_models(self, model_results: Dict[str, Dict[str, float]], 
                      metric_name: str) -> Dict[str, Any]:
        """Compare multiple models based on a specific metric."""
        comparison: Dict[str, Any] = {
            'best_model': None,
            'best_score': float('-inf'),
            'worst_model': None,
            'worst_score': float('inf'),
            'scores': {}
        }
        
        for model_name, results in model_results.items():
            if metric_name in results:
                score = results[metric_name]
                comparison['scores'][model_name] = score
                
                if score > comparison['best_score']:
                    comparison['best_score'] = score
                    comparison['best_model'] = model_name
                
                if score < comparison['worst_score']:
                    comparison['worst_score'] = score
                    comparison['worst_model'] = model_name
        
        return comparison


class MetricVisualizer:
    """Visualization tools for evaluation metrics."""
    
    def __init__(self) -> Any:
        pass
    
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray, 
                            class_names: Optional[List[str]] = None, 
                            title: str: str: str = "Confusion Matrix") -> Any:
        """Plot confusion matrix."""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names)
        plt.title(title)
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.show()
    
    def plot_roc_curve(self, y_true: np.ndarray, y_pred_proba: np.ndarray, 
                      title: str: str: str = "ROC Curve") -> Any:
        """Plot ROC curve."""
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba[:, 1])
        auc_score = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc_score:.3f})')
        plt.plot([0, 1], [0, 1], 'k--', label: str: str = 'Random')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_precision_recall_curve(self, y_true: np.ndarray, y_pred_proba: np.ndarray,
                                  title: str: str: str = "Precision-Recall Curve") -> Any:
        """Plot precision-recall curve."""
        precision, recall, _ = precision_recall_curve(y_true, y_pred_proba[:, 1])
        ap_score = average_precision_score(y_true, y_pred_proba[:, 1])
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, label=f'PR Curve (AP = {ap_score:.3f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_metrics_comparison(self, model_results: Dict[str, Dict[str, float]], 
                              metric_name: str, title: str = None) -> Any:
        """Plot comparison of models for a specific metric."""
        if title is None:
            title = f"{metric_name} Comparison"
        
        models = list(model_results.keys())
        scores: List[Any] = [model_results[model].get(metric_name, 0) for model in models]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(models, scores)
        plt.title(title)
        plt.ylabel(metric_name)
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{score:.3f}', ha: str: str = 'center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def plot_regression_results(self, y_true: np.ndarray, y_pred: np.ndarray,
                              title: str: str: str = "Regression Results") -> Any:
        """Plot regression results."""
        plt.figure(figsize=(12, 4))
        
        # Scatter plot
        plt.subplot(1, 3, 1)
        plt.scatter(y_true, y_pred, alpha=0.6)
        plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        plt.xlabel('True Values')
        plt.ylabel('Predictions')
        plt.title('Predicted vs True')
        
        # Residuals
        plt.subplot(1, 3, 2)
        residuals = y_true - y_pred
        plt.scatter(y_pred, residuals, alpha=0.6)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('Predictions')
        plt.ylabel('Residuals')
        plt.title('Residuals')
        
        # Residuals distribution
        plt.subplot(1, 3, 3)
        plt.hist(residuals, bins=30, alpha=0.7)
        plt.xlabel('Residuals')
        plt.ylabel('Frequency')
        plt.title('Residuals Distribution')
        
        plt.tight_layout()
        plt.show()


class StatisticalTesting:
    """Statistical significance testing for model comparison."""
    
    def __init__(self) -> Any:
        pass
    
    def paired_t_test(self, scores1: np.ndarray, scores2: np.ndarray, 
                     alpha: float = 0.05) -> Dict[str, Any]:
        """Perform paired t-test."""
        t_stat, p_value = stats.ttest_rel(scores1, scores2)
        
        return {
            'test_type': 'paired_t_test',
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < alpha,
            'alpha': alpha
        }
    
    def wilcoxon_test(self, scores1: np.ndarray, scores2: np.ndarray,
                     alpha: float = 0.05) -> Dict[str, Any]:
        """Perform Wilcoxon signed-rank test."""
        stat, p_value = stats.wilcoxon(scores1, scores2)
        
        return {
            'test_type': 'wilcoxon_test',
            'statistic': stat,
            'p_value': p_value,
            'significant': p_value < alpha,
            'alpha': alpha
        }
    
    def mann_whitney_test(self, scores1: np.ndarray, scores2: np.ndarray,
                         alpha: float = 0.05) -> Dict[str, Any]:
        """Perform Mann-Whitney U test."""
        stat, p_value = stats.mannwhitneyu(scores1, scores2, alternative='two-sided')
        
        return {
            'test_type': 'mann_whitney_test',
            'statistic': stat,
            'p_value': p_value,
            'significant': p_value < alpha,
            'alpha': alpha
        }


# Utility functions
def get_task_metrics(task_type: str, **kwargs) -> MetricCalculator:
    """Get appropriate metrics for a specific task."""
    return MetricCalculator(task_type, **kwargs)


def evaluate_classification(y_true: np.ndarray, y_pred: np.ndarray, 
                          y_pred_proba: Optional[np.ndarray] = None,
                          **kwargs) -> Dict[str, float]:
    """Evaluate classification model."""
    calculator = MetricCalculator('classification', **kwargs)
    return calculator.compute_metrics(y_true, y_pred, y_pred_proba)


def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Evaluate regression model."""
    calculator = MetricCalculator('regression')
    return calculator.compute_metrics(y_true, y_pred)


def evaluate_object_detection(ground_truth: List[List], predictions: List[List],
                            **kwargs) -> Dict[str, float]:
    """Evaluate object detection model."""
    calculator = MetricCalculator('object_detection', **kwargs)
    return calculator.compute_metrics(ground_truth, predictions)


def evaluate_segmentation(y_true: np.ndarray, y_pred: np.ndarray, **kwargs) -> Dict[str, float]:
    """Evaluate segmentation model."""
    calculator = MetricCalculator('segmentation', **kwargs)
    return calculator.compute_metrics(y_true, y_pred)


def evaluate_time_series(y_true: np.ndarray, y_pred: np.ndarray, 
                       y_train: np.ndarray, **kwargs) -> Dict[str, float]:
    """Evaluate time series model."""
    calculator = MetricCalculator('time_series')
    return calculator.compute_metrics(y_true, y_pred, y_train=y_train, **kwargs)


# Example usage
if __name__ == "__main__":
    # Example: Classification evaluation
    np.random.seed(42)
    y_true = np.random.choice([0, 1], size=1000)
    y_pred = np.random.choice([0, 1], size=1000)
    y_pred_proba = np.random.rand(1000, 2)
    y_pred_proba = y_pred_proba / y_pred_proba.sum(axis=1, keepdims=True)
    
    # Evaluate classification
    results = evaluate_classification(y_true, y_pred, y_pred_proba)
    print("Classification Results:")
    for metric, value in results.items():
        print(f"{metric}: {value:.4f}")
    
    # Example: Regression evaluation
    y_true_reg = np.random.randn(1000)
    y_pred_reg = y_true_reg + np.random.randn(1000) * 0.1
    
    results_reg = evaluate_regression(y_true_reg, y_pred_reg)
    print("\nRegression Results:")
    for metric, value in results_reg.items():
        print(f"{metric}: {value:.4f}") 