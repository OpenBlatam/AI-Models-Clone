#!/usr/bin/env python3
"""
Comprehensive Evaluation Metrics Framework for SEO Deep Learning System
- Task-specific evaluation metrics
- SEO-specific ranking and relevance metrics
- Multi-task evaluation capabilities
- Advanced statistical analysis
- Visualization and reporting
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
import logging
import time
import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    classification_report, mean_squared_error, mean_absolute_error,
    r2_score, log_loss, cohen_kappa_score, matthews_corrcoef,
    precision_recall_curve, roc_curve, auc
)
from sklearn.preprocessing import label_binarize
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class EvaluationConfig:
    """Configuration for evaluation metrics"""
    # Task type
    task_type: str = "classification"  # "classification", "regression", "ranking", "multitask", "seo"
    
    # Classification metrics
    classification_metrics: List[str] = field(default_factory=lambda: [
        "accuracy", "precision", "recall", "f1", "auc", "ap", "confusion_matrix"
    ])
    average_method: str = "weighted"  # "micro", "macro", "weighted", "binary"
    
    # Regression metrics
    regression_metrics: List[str] = field(default_factory=lambda: [
        "mse", "rmse", "mae", "r2", "mape", "smape"
    ])
    
    # Ranking metrics
    ranking_metrics: List[str] = field(default_factory=lambda: [
        "ndcg", "mrr", "map", "precision_at_k", "recall_at_k"
    ])
    k_values: List[int] = field(default_factory=lambda: [1, 3, 5, 10])
    
    # SEO-specific metrics
    seo_metrics: List[str] = field(default_factory=lambda: [
        "ranking_accuracy", "click_through_rate", "bounce_rate", "time_on_page",
        "conversion_rate", "organic_traffic", "keyword_density", "content_quality"
    ])
    
    # Multi-task metrics
    multitask_metrics: List[str] = field(default_factory=lambda: [
        "task_accuracy", "overall_accuracy", "task_f1", "overall_f1"
    ])
    
    # Statistical analysis
    statistical_analysis: bool = True
    confidence_intervals: bool = True
    bootstrap_samples: int = 1000
    confidence_level: float = 0.95
    
    # Visualization
    create_plots: bool = True
    save_plots: bool = True
    plot_format: str = "png"
    dpi: int = 300
    
    # Output
    save_results: bool = True
    output_format: str = "json"  # "json", "csv", "excel"
    verbose: bool = True

@dataclass
class EvaluationResult:
    """Container for evaluation results"""
    task_type: str
    metrics: Dict[str, float]
    predictions: Optional[np.ndarray] = None
    targets: Optional[np.ndarray] = None
    probabilities: Optional[np.ndarray] = None
    confidence_intervals: Optional[Dict[str, Tuple[float, float]]] = None
    statistical_tests: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)

class ClassificationMetrics:
    """Comprehensive classification metrics"""
    
    @staticmethod
    def calculate_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate accuracy score"""
        return accuracy_score(y_true, y_pred)
    
    @staticmethod
    def calculate_precision(y_true: np.ndarray, y_pred: np.ndarray, average: str = "weighted") -> float:
        """Calculate precision score"""
        return precision_score(y_true, y_pred, average=average, zero_division=0)
    
    @staticmethod
    def calculate_recall(y_true: np.ndarray, y_pred: np.ndarray, average: str = "weighted") -> float:
        """Calculate recall score"""
        return recall_score(y_true, y_pred, average=average, zero_division=0)
    
    @staticmethod
    def calculate_f1(y_true: np.ndarray, y_pred: np.ndarray, average: str = "weighted") -> float:
        """Calculate F1 score"""
        return f1_score(y_true, y_pred, average=average, zero_division=0)
    
    @staticmethod
    def calculate_auc(y_true: np.ndarray, y_prob: np.ndarray, average: str = "weighted") -> float:
        """Calculate AUC score"""
        if len(np.unique(y_true)) == 2:
            return roc_auc_score(y_true, y_prob[:, 1])
        else:
            return roc_auc_score(y_true, y_prob, average=average, multi_class='ovr')
    
    @staticmethod
    def calculate_average_precision(y_true: np.ndarray, y_prob: np.ndarray, average: str = "weighted") -> float:
        """Calculate average precision score"""
        if len(np.unique(y_true)) == 2:
            return average_precision_score(y_true, y_prob[:, 1])
        else:
            return average_precision_score(y_true, y_prob, average=average)
    
    @staticmethod
    def calculate_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Calculate confusion matrix"""
        return confusion_matrix(y_true, y_pred)
    
    @staticmethod
    def calculate_cohen_kappa(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Cohen's Kappa"""
        return cohen_kappa_score(y_true, y_pred)
    
    @staticmethod
    def calculate_matthews_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Matthews Correlation Coefficient"""
        return matthews_corrcoef(y_true, y_pred)
    
    @staticmethod
    def calculate_log_loss(y_true: np.ndarray, y_prob: np.ndarray) -> float:
        """Calculate log loss"""
        return log_loss(y_true, y_prob)
    
    @staticmethod
    def calculate_all_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: Optional[np.ndarray] = None,
                            average: str = "weighted") -> Dict[str, float]:
        """Calculate all classification metrics"""
        metrics = {
            'accuracy': ClassificationMetrics.calculate_accuracy(y_true, y_pred),
            'precision': ClassificationMetrics.calculate_precision(y_true, y_pred, average),
            'recall': ClassificationMetrics.calculate_recall(y_true, y_pred, average),
            'f1': ClassificationMetrics.calculate_f1(y_true, y_pred, average),
            'cohen_kappa': ClassificationMetrics.calculate_cohen_kappa(y_true, y_pred),
            'matthews_correlation': ClassificationMetrics.calculate_matthews_correlation(y_true, y_pred)
        }
        
        if y_prob is not None:
            metrics.update({
                'auc': ClassificationMetrics.calculate_auc(y_true, y_prob, average),
                'average_precision': ClassificationMetrics.calculate_average_precision(y_true, y_prob, average),
                'log_loss': ClassificationMetrics.calculate_log_loss(y_true, y_prob)
            })
        
        return metrics

class RegressionMetrics:
    """Comprehensive regression metrics"""
    
    @staticmethod
    def calculate_mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Squared Error"""
        return mean_squared_error(y_true, y_pred)
    
    @staticmethod
    def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Root Mean Squared Error"""
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    @staticmethod
    def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Error"""
        return mean_absolute_error(y_true, y_pred)
    
    @staticmethod
    def calculate_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R-squared score"""
        return r2_score(y_true, y_pred)
    
    @staticmethod
    def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Percentage Error"""
        return np.mean(np.abs((y_true - y_pred) / np.where(y_true != 0, y_true, 1))) * 100
    
    @staticmethod
    def calculate_smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Symmetric Mean Absolute Percentage Error"""
        return 100 * np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))
    
    @staticmethod
    def calculate_pearson_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Pearson correlation coefficient"""
        return pearsonr(y_true, y_pred)[0]
    
    @staticmethod
    def calculate_spearman_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Spearman correlation coefficient"""
        return spearmanr(y_true, y_pred)[0]
    
    @staticmethod
    def calculate_kendall_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Kendall correlation coefficient"""
        return kendalltau(y_true, y_pred)[0]
    
    @staticmethod
    def calculate_all_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate all regression metrics"""
        return {
            'mse': RegressionMetrics.calculate_mse(y_true, y_pred),
            'rmse': RegressionMetrics.calculate_rmse(y_true, y_pred),
            'mae': RegressionMetrics.calculate_mae(y_true, y_pred),
            'r2': RegressionMetrics.calculate_r2(y_true, y_pred),
            'mape': RegressionMetrics.calculate_mape(y_true, y_pred),
            'smape': RegressionMetrics.calculate_smape(y_true, y_pred),
            'pearson_correlation': RegressionMetrics.calculate_pearson_correlation(y_true, y_pred),
            'spearman_correlation': RegressionMetrics.calculate_spearman_correlation(y_true, y_pred),
            'kendall_correlation': RegressionMetrics.calculate_kendall_correlation(y_true, y_pred)
        }

class RankingMetrics:
    """Comprehensive ranking metrics"""
    
    @staticmethod
    def calculate_ndcg(y_true: np.ndarray, y_pred: np.ndarray, k: int = 10) -> float:
        """Calculate Normalized Discounted Cumulative Gain at k"""
        def dcg_at_k(y_true, y_pred, k):
            order = np.argsort(y_pred)[::-1]
            y_true = np.take(y_true, order[:k])
            gain = 2 ** y_true - 1
            discounts = np.log2(np.arange(2, len(gain) + 2))
            return np.sum(gain / discounts)
        
        dcg = dcg_at_k(y_true, y_pred, k)
        idcg = dcg_at_k(y_true, y_true, k)
        return dcg / idcg if idcg > 0 else 0.0
    
    @staticmethod
    def calculate_mrr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Reciprocal Rank"""
        order = np.argsort(y_pred)[::-1]
        for i, idx in enumerate(order):
            if y_true[idx] == 1:
                return 1.0 / (i + 1)
        return 0.0
    
    @staticmethod
    def calculate_map(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Average Precision"""
        order = np.argsort(y_pred)[::-1]
        ap = 0.0
        num_relevant = np.sum(y_true)
        
        if num_relevant == 0:
            return 0.0
        
        relevant_count = 0
        for i, idx in enumerate(order):
            if y_true[idx] == 1:
                relevant_count += 1
                ap += relevant_count / (i + 1)
        
        return ap / num_relevant
    
    @staticmethod
    def calculate_precision_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int) -> float:
        """Calculate Precision at k"""
        order = np.argsort(y_pred)[::-1]
        y_true = np.take(y_true, order[:k])
        return np.sum(y_true) / k
    
    @staticmethod
    def calculate_recall_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int) -> float:
        """Calculate Recall at k"""
        order = np.argsort(y_pred)[::-1]
        y_true = np.take(y_true, order[:k])
        total_relevant = np.sum(y_true)
        return np.sum(y_true) / total_relevant if total_relevant > 0 else 0.0
    
    @staticmethod
    def calculate_all_metrics(y_true: np.ndarray, y_pred: np.ndarray, k_values: List[int] = None) -> Dict[str, float]:
        """Calculate all ranking metrics"""
        if k_values is None:
            k_values = [1, 3, 5, 10]
        
        metrics = {
            'mrr': RankingMetrics.calculate_mrr(y_true, y_pred),
            'map': RankingMetrics.calculate_map(y_true, y_pred)
        }
        
        for k in k_values:
            metrics[f'ndcg@{k}'] = RankingMetrics.calculate_ndcg(y_true, y_pred, k)
            metrics[f'precision@{k}'] = RankingMetrics.calculate_precision_at_k(y_true, y_pred, k)
            metrics[f'recall@{k}'] = RankingMetrics.calculate_recall_at_k(y_true, y_pred, k)
        
        return metrics

class SEOMetrics:
    """SEO-specific evaluation metrics"""
    
    @staticmethod
    def calculate_ranking_accuracy(y_true: np.ndarray, y_pred: np.ndarray, tolerance: float = 0.1) -> float:
        """Calculate ranking accuracy within tolerance"""
        return np.mean(np.abs(y_true - y_pred) <= tolerance)
    
    @staticmethod
    def calculate_click_through_rate(clicks: np.ndarray, impressions: np.ndarray) -> float:
        """Calculate Click-Through Rate"""
        return np.sum(clicks) / np.sum(impressions) if np.sum(impressions) > 0 else 0.0
    
    @staticmethod
    def calculate_bounce_rate(bounces: np.ndarray, sessions: np.ndarray) -> float:
        """Calculate Bounce Rate"""
        return np.sum(bounces) / np.sum(sessions) if np.sum(sessions) > 0 else 0.0
    
    @staticmethod
    def calculate_time_on_page(time_spent: np.ndarray, page_views: np.ndarray) -> float:
        """Calculate Average Time on Page"""
        return np.sum(time_spent) / np.sum(page_views) if np.sum(page_views) > 0 else 0.0
    
    @staticmethod
    def calculate_conversion_rate(conversions: np.ndarray, sessions: np.ndarray) -> float:
        """Calculate Conversion Rate"""
        return np.sum(conversions) / np.sum(sessions) if np.sum(sessions) > 0 else 0.0
    
    @staticmethod
    def calculate_organic_traffic(organic_sessions: np.ndarray, total_sessions: np.ndarray) -> float:
        """Calculate Organic Traffic Percentage"""
        return np.sum(organic_sessions) / np.sum(total_sessions) if np.sum(total_sessions) > 0 else 0.0
    
    @staticmethod
    def calculate_keyword_density(text: str, keyword: str) -> float:
        """Calculate Keyword Density"""
        words = text.lower().split()
        keyword_count = text.lower().count(keyword.lower())
        return keyword_count / len(words) if len(words) > 0 else 0.0
    
    @staticmethod
    def calculate_content_quality_score(readability_score: float, word_count: int, 
                                      keyword_density: float, internal_links: int) -> float:
        """Calculate Content Quality Score"""
        # Normalize components
        readability_norm = min(readability_score / 100, 1.0)
        word_count_norm = min(word_count / 2000, 1.0)  # Optimal around 2000 words
        keyword_density_norm = min(keyword_density / 0.02, 1.0)  # Optimal around 2%
        internal_links_norm = min(internal_links / 10, 1.0)  # Optimal around 10 links
        
        # Weighted average
        return (0.3 * readability_norm + 0.3 * word_count_norm + 
                0.2 * keyword_density_norm + 0.2 * internal_links_norm)
    
    @staticmethod
    def calculate_all_metrics(ranking_data: Dict[str, np.ndarray], 
                            traffic_data: Dict[str, np.ndarray],
                            content_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate all SEO metrics"""
        metrics = {}
        
        # Ranking metrics
        if 'y_true' in ranking_data and 'y_pred' in ranking_data:
            metrics['ranking_accuracy'] = SEOMetrics.calculate_ranking_accuracy(
                ranking_data['y_true'], ranking_data['y_pred']
            )
        
        # Traffic metrics
        if 'clicks' in traffic_data and 'impressions' in traffic_data:
            metrics['click_through_rate'] = SEOMetrics.calculate_click_through_rate(
                traffic_data['clicks'], traffic_data['impressions']
            )
        
        if 'bounces' in traffic_data and 'sessions' in traffic_data:
            metrics['bounce_rate'] = SEOMetrics.calculate_bounce_rate(
                traffic_data['bounces'], traffic_data['sessions']
            )
        
        if 'time_spent' in traffic_data and 'page_views' in traffic_data:
            metrics['time_on_page'] = SEOMetrics.calculate_time_on_page(
                traffic_data['time_spent'], traffic_data['page_views']
            )
        
        if 'conversions' in traffic_data and 'sessions' in traffic_data:
            metrics['conversion_rate'] = SEOMetrics.calculate_conversion_rate(
                traffic_data['conversions'], traffic_data['sessions']
            )
        
        if 'organic_sessions' in traffic_data and 'total_sessions' in traffic_data:
            metrics['organic_traffic'] = SEOMetrics.calculate_organic_traffic(
                traffic_data['organic_sessions'], traffic_data['total_sessions']
            )
        
        # Content metrics
        if 'text' in content_data and 'keyword' in content_data:
            metrics['keyword_density'] = SEOMetrics.calculate_keyword_density(
                content_data['text'], content_data['keyword']
            )
        
        if all(key in content_data for key in ['readability_score', 'word_count', 'keyword_density', 'internal_links']):
            metrics['content_quality_score'] = SEOMetrics.calculate_content_quality_score(
                content_data['readability_score'],
                content_data['word_count'],
                content_data['keyword_density'],
                content_data['internal_links']
            )
        
        return metrics

class MultiTaskMetrics:
    """Multi-task evaluation metrics"""
    
    @staticmethod
    def calculate_task_accuracy(y_true: Dict[str, np.ndarray], y_pred: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Calculate accuracy for each task"""
        task_accuracies = {}
        for task_name in y_true.keys():
            if task_name in y_pred:
                task_accuracies[task_name] = accuracy_score(y_true[task_name], y_pred[task_name])
        return task_accuracies
    
    @staticmethod
    def calculate_overall_accuracy(y_true: Dict[str, np.ndarray], y_pred: Dict[str, np.ndarray]) -> float:
        """Calculate overall accuracy across all tasks"""
        all_true = []
        all_pred = []
        for task_name in y_true.keys():
            if task_name in y_pred:
                all_true.extend(y_true[task_name])
                all_pred.extend(y_pred[task_name])
        return accuracy_score(all_true, all_pred) if all_true else 0.0
    
    @staticmethod
    def calculate_task_f1(y_true: Dict[str, np.ndarray], y_pred: Dict[str, np.ndarray], 
                         average: str = "weighted") -> Dict[str, float]:
        """Calculate F1 score for each task"""
        task_f1_scores = {}
        for task_name in y_true.keys():
            if task_name in y_pred:
                task_f1_scores[task_name] = f1_score(y_true[task_name], y_pred[task_name], 
                                                   average=average, zero_division=0)
        return task_f1_scores
    
    @staticmethod
    def calculate_overall_f1(y_true: Dict[str, np.ndarray], y_pred: Dict[str, np.ndarray], 
                           average: str = "weighted") -> float:
        """Calculate overall F1 score across all tasks"""
        all_true = []
        all_pred = []
        for task_name in y_true.keys():
            if task_name in y_pred:
                all_true.extend(y_true[task_name])
                all_pred.extend(y_pred[task_name])
        return f1_score(all_true, all_pred, average=average, zero_division=0) if all_true else 0.0
    
    @staticmethod
    def calculate_all_metrics(y_true: Dict[str, np.ndarray], y_pred: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Calculate all multi-task metrics"""
        return {
            'task_accuracy': MultiTaskMetrics.calculate_task_accuracy(y_true, y_pred),
            'overall_accuracy': MultiTaskMetrics.calculate_overall_accuracy(y_true, y_pred),
            'task_f1': MultiTaskMetrics.calculate_task_f1(y_true, y_pred),
            'overall_f1': MultiTaskMetrics.calculate_overall_f1(y_true, y_pred)
        }

class StatisticalAnalysis:
    """Statistical analysis for evaluation results"""
    
    @staticmethod
    def calculate_confidence_intervals(metric_values: List[float], confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence intervals using bootstrap"""
        if len(metric_values) < 2:
            return (metric_values[0], metric_values[0])
        
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bound = np.percentile(metric_values, lower_percentile)
        upper_bound = np.percentile(metric_values, upper_percentile)
        
        return (lower_bound, upper_bound)
    
    @staticmethod
    def bootstrap_confidence_intervals(y_true: np.ndarray, y_pred: np.ndarray, 
                                     metric_func: Callable, n_bootstrap: int = 1000,
                                     confidence_level: float = 0.95) -> Dict[str, Tuple[float, float]]:
        """Calculate bootstrap confidence intervals for metrics"""
        n_samples = len(y_true)
        bootstrap_metrics = []
        
        for _ in range(n_bootstrap):
            indices = np.random.choice(n_samples, n_samples, replace=True)
            bootstrap_true = y_true[indices]
            bootstrap_pred = y_pred[indices]
            
            try:
                metric_value = metric_func(bootstrap_true, bootstrap_pred)
                bootstrap_metrics.append(metric_value)
            except:
                continue
        
        if not bootstrap_metrics:
            return {}
        
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bound = np.percentile(bootstrap_metrics, lower_percentile)
        upper_bound = np.percentile(bootstrap_metrics, upper_percentile)
        
        return {
            'confidence_interval': (lower_bound, upper_bound),
            'mean': np.mean(bootstrap_metrics),
            'std': np.std(bootstrap_metrics)
        }
    
    @staticmethod
    def perform_statistical_tests(y_true: np.ndarray, y_pred: np.ndarray, 
                                baseline_pred: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Perform statistical tests on predictions"""
        tests = {}
        
        # Correlation analysis
        if baseline_pred is not None:
            correlation, p_value = pearsonr(y_pred, baseline_pred)
            tests['correlation_with_baseline'] = {
                'correlation': correlation,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        
        # Distribution analysis
        tests['prediction_distribution'] = {
            'mean': np.mean(y_pred),
            'std': np.std(y_pred),
            'skewness': stats.skew(y_pred),
            'kurtosis': stats.kurtosis(y_pred)
        }
        
        # Error analysis
        errors = y_true - y_pred
        tests['error_analysis'] = {
            'mean_error': np.mean(errors),
            'std_error': np.std(errors),
            'skewness_error': stats.skew(errors),
            'kurtosis_error': stats.kurtosis(errors)
        }
        
        return tests

class EvaluationVisualizer:
    """Visualization for evaluation results"""
    
    @staticmethod
    def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, 
                            class_names: Optional[List[str]] = None, 
                            save_path: Optional[str] = None):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_roc_curve(y_true: np.ndarray, y_prob: np.ndarray, 
                      class_names: Optional[List[str]] = None,
                      save_path: Optional[str] = None):
        """Plot ROC curve"""
        if len(np.unique(y_true)) == 2:
            fpr, tpr, _ = roc_curve(y_true, y_prob[:, 1])
            auc_score = auc(fpr, tpr)
            
            plt.figure(figsize=(8, 6))
            plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc_score:.3f})')
            plt.plot([0, 1], [0, 1], 'k--', label='Random')
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('ROC Curve')
            plt.legend()
            plt.grid(True)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.show()
        else:
            # Multi-class ROC
            y_true_bin = label_binarize(y_true, classes=np.unique(y_true))
            n_classes = y_true_bin.shape[1]
            
            plt.figure(figsize=(8, 6))
            for i in range(n_classes):
                fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
                auc_score = auc(fpr, tpr)
                class_name = class_names[i] if class_names else f'Class {i}'
                plt.plot(fpr, tpr, label=f'{class_name} (AUC = {auc_score:.3f})')
            
            plt.plot([0, 1], [0, 1], 'k--', label='Random')
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('Multi-class ROC Curves')
            plt.legend()
            plt.grid(True)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.show()
    
    @staticmethod
    def plot_precision_recall_curve(y_true: np.ndarray, y_prob: np.ndarray,
                                  save_path: Optional[str] = None):
        """Plot Precision-Recall curve"""
        precision, recall, _ = precision_recall_curve(y_true, y_prob[:, 1])
        ap_score = average_precision_score(y_true, y_prob[:, 1])
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, label=f'PR Curve (AP = {ap_score:.3f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_regression_results(y_true: np.ndarray, y_pred: np.ndarray,
                              save_path: Optional[str] = None):
        """Plot regression results"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Scatter plot
        axes[0, 0].scatter(y_true, y_pred, alpha=0.6)
        axes[0, 0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        axes[0, 0].set_xlabel('True Values')
        axes[0, 0].set_ylabel('Predictions')
        axes[0, 0].set_title('Prediction vs True Values')
        axes[0, 0].grid(True)
        
        # Residuals plot
        residuals = y_true - y_pred
        axes[0, 1].scatter(y_pred, residuals, alpha=0.6)
        axes[0, 1].axhline(y=0, color='r', linestyle='--')
        axes[0, 1].set_xlabel('Predictions')
        axes[0, 1].set_ylabel('Residuals')
        axes[0, 1].set_title('Residuals Plot')
        axes[0, 1].grid(True)
        
        # Residuals histogram
        axes[1, 0].hist(residuals, bins=30, alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Residuals')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Residuals Distribution')
        axes[1, 0].grid(True)
        
        # Q-Q plot
        stats.probplot(residuals, dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title('Q-Q Plot of Residuals')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_ranking_metrics(metrics: Dict[str, float], k_values: List[int],
                           save_path: Optional[str] = None):
        """Plot ranking metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # NDCG@k
        ndcg_values = [metrics.get(f'ndcg@{k}', 0) for k in k_values]
        axes[0, 0].plot(k_values, ndcg_values, 'o-', linewidth=2, markersize=8)
        axes[0, 0].set_xlabel('k')
        axes[0, 0].set_ylabel('NDCG@k')
        axes[0, 0].set_title('NDCG@k')
        axes[0, 0].grid(True)
        
        # Precision@k
        precision_values = [metrics.get(f'precision@{k}', 0) for k in k_values]
        axes[0, 1].plot(k_values, precision_values, 's-', linewidth=2, markersize=8)
        axes[0, 1].set_xlabel('k')
        axes[0, 1].set_ylabel('Precision@k')
        axes[0, 1].set_title('Precision@k')
        axes[0, 1].grid(True)
        
        # Recall@k
        recall_values = [metrics.get(f'recall@{k}', 0) for k in k_values]
        axes[1, 0].plot(k_values, recall_values, '^-', linewidth=2, markersize=8)
        axes[1, 0].set_xlabel('k')
        axes[1, 0].set_ylabel('Recall@k')
        axes[1, 0].set_title('Recall@k')
        axes[1, 0].grid(True)
        
        # Overall metrics
        overall_metrics = ['mrr', 'map']
        overall_values = [metrics.get(metric, 0) for metric in overall_metrics]
        axes[1, 1].bar(overall_metrics, overall_values, alpha=0.7)
        axes[1, 1].set_ylabel('Score')
        axes[1, 1].set_title('Overall Ranking Metrics')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

class ModelEvaluator:
    """Comprehensive model evaluator with task-specific metrics"""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.results = {}
        
    def evaluate_classification(self, y_true: np.ndarray, y_pred: np.ndarray, 
                              y_prob: Optional[np.ndarray] = None) -> EvaluationResult:
        """Evaluate classification model"""
        metrics = ClassificationMetrics.calculate_all_metrics(y_true, y_pred, y_prob, self.config.average_method)
        
        # Statistical analysis
        confidence_intervals = {}
        statistical_tests = {}
        
        if self.config.statistical_analysis:
            if y_prob is not None:
                confidence_intervals = StatisticalAnalysis.bootstrap_confidence_intervals(
                    y_true, y_pred, lambda y_t, y_p: f1_score(y_t, y_p, average=self.config.average_method),
                    self.config.bootstrap_samples, self.config.confidence_level
                )
            
            statistical_tests = StatisticalAnalysis.perform_statistical_tests(y_true, y_pred)
        
        # Visualization
        if self.config.create_plots:
            if 'confusion_matrix' in self.config.classification_metrics:
                save_path = f"confusion_matrix.{self.config.plot_format}" if self.config.save_plots else None
                EvaluationVisualizer.plot_confusion_matrix(y_true, y_pred, save_path=save_path)
            
            if y_prob is not None:
                save_path = f"roc_curve.{self.config.plot_format}" if self.config.save_plots else None
                EvaluationVisualizer.plot_roc_curve(y_true, y_prob, save_path=save_path)
                
                save_path = f"pr_curve.{self.config.plot_format}" if self.config.save_plots else None
                EvaluationVisualizer.plot_precision_recall_curve(y_true, y_prob, save_path=save_path)
        
        return EvaluationResult(
            task_type="classification",
            metrics=metrics,
            predictions=y_pred,
            targets=y_true,
            probabilities=y_prob,
            confidence_intervals=confidence_intervals,
            statistical_tests=statistical_tests
        )
    
    def evaluate_regression(self, y_true: np.ndarray, y_pred: np.ndarray) -> EvaluationResult:
        """Evaluate regression model"""
        metrics = RegressionMetrics.calculate_all_metrics(y_true, y_pred)
        
        # Statistical analysis
        confidence_intervals = {}
        statistical_tests = {}
        
        if self.config.statistical_analysis:
            confidence_intervals = StatisticalAnalysis.bootstrap_confidence_intervals(
                y_true, y_pred, lambda y_t, y_p: r2_score(y_t, y_p),
                self.config.bootstrap_samples, self.config.confidence_level
            )
            
            statistical_tests = StatisticalAnalysis.perform_statistical_tests(y_true, y_pred)
        
        # Visualization
        if self.config.create_plots:
            save_path = f"regression_results.{self.config.plot_format}" if self.config.save_plots else None
            EvaluationVisualizer.plot_regression_results(y_true, y_pred, save_path=save_path)
        
        return EvaluationResult(
            task_type="regression",
            metrics=metrics,
            predictions=y_pred,
            targets=y_true,
            confidence_intervals=confidence_intervals,
            statistical_tests=statistical_tests
        )
    
    def evaluate_ranking(self, y_true: np.ndarray, y_pred: np.ndarray) -> EvaluationResult:
        """Evaluate ranking model"""
        metrics = RankingMetrics.calculate_all_metrics(y_true, y_pred, self.config.k_values)
        
        # Visualization
        if self.config.create_plots:
            save_path = f"ranking_metrics.{self.config.plot_format}" if self.config.save_plots else None
            EvaluationVisualizer.plot_ranking_metrics(metrics, self.config.k_values, save_path=save_path)
        
        return EvaluationResult(
            task_type="ranking",
            metrics=metrics,
            predictions=y_pred,
            targets=y_true
        )
    
    def evaluate_seo(self, ranking_data: Dict[str, np.ndarray], 
                    traffic_data: Dict[str, np.ndarray],
                    content_data: Dict[str, Any]) -> EvaluationResult:
        """Evaluate SEO model"""
        metrics = SEOMetrics.calculate_all_metrics(ranking_data, traffic_data, content_data)
        
        return EvaluationResult(
            task_type="seo",
            metrics=metrics
        )
    
    def evaluate_multitask(self, y_true: Dict[str, np.ndarray], 
                          y_pred: Dict[str, np.ndarray]) -> EvaluationResult:
        """Evaluate multi-task model"""
        metrics = MultiTaskMetrics.calculate_all_metrics(y_true, y_pred)
        
        return EvaluationResult(
            task_type="multitask",
            metrics=metrics,
            predictions=y_pred,
            targets=y_true
        )
    
    def evaluate(self, y_true: Union[np.ndarray, Dict[str, np.ndarray]], 
                y_pred: Union[np.ndarray, Dict[str, np.ndarray]],
                y_prob: Optional[np.ndarray] = None,
                **kwargs) -> EvaluationResult:
        """Main evaluation method"""
        
        if self.config.task_type == "classification":
            return self.evaluate_classification(y_true, y_pred, y_prob)
        elif self.config.task_type == "regression":
            return self.evaluate_regression(y_true, y_pred)
        elif self.config.task_type == "ranking":
            return self.evaluate_ranking(y_true, y_pred)
        elif self.config.task_type == "seo":
            return self.evaluate_seo(kwargs.get('ranking_data', {}),
                                   kwargs.get('traffic_data', {}),
                                   kwargs.get('content_data', {}))
        elif self.config.task_type == "multitask":
            return self.evaluate_multitask(y_true, y_pred)
        else:
            raise ValueError(f"Unknown task type: {self.config.task_type}")
    
    def save_results(self, result: EvaluationResult, save_path: str):
        """Save evaluation results"""
        if self.config.save_results:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            if self.config.output_format == "json":
                # Convert numpy arrays to lists for JSON serialization
                result_dict = {
                    'task_type': result.task_type,
                    'metrics': result.metrics,
                    'confidence_intervals': result.confidence_intervals,
                    'statistical_tests': result.statistical_tests,
                    'timestamp': result.timestamp
                }
                
                with open(save_path, 'w') as f:
                    json.dump(result_dict, f, indent=2, default=str)
            
            elif self.config.output_format == "csv":
                # Save metrics as CSV
                metrics_df = pd.DataFrame([result.metrics])
                metrics_df.to_csv(save_path, index=False)
            
            logger.info(f"Evaluation results saved to {save_path}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get evaluation summary"""
        return {
            'task_type': self.config.task_type,
            'results': self.results,
            'config': self.config.__dict__
        }

# Example usage
if __name__ == "__main__":
    # Example: Classification evaluation
    config = EvaluationConfig(
        task_type="classification",
        classification_metrics=["accuracy", "precision", "recall", "f1", "auc"],
        average_method="weighted",
        create_plots=True,
        save_plots=True
    )
    
    evaluator = ModelEvaluator(config)
    
    # Generate sample data
    np.random.seed(42)
    y_true = np.random.randint(0, 3, 1000)
    y_pred = np.random.randint(0, 3, 1000)
    y_prob = np.random.rand(1000, 3)
    y_prob = y_prob / y_prob.sum(axis=1, keepdims=True)
    
    # Evaluate
    result = evaluator.evaluate(y_true, y_pred, y_prob)
    
    print("Classification Evaluation Results:")
    for metric, value in result.metrics.items():
        print(f"{metric}: {value:.4f}")
    
    # Save results
    evaluator.save_results(result, "evaluation_results.json") 