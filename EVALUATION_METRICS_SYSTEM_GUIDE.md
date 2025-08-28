# Evaluation Metrics System Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Classification Metrics](#classification-metrics)
4. [Regression Metrics](#regression-metrics)
5. [Object Detection Metrics](#object-detection-metrics)
6. [Segmentation Metrics](#segmentation-metrics)
7. [Time Series Metrics](#time-series-metrics)
8. [Metric Calculator](#metric-calculator)
9. [Visualization Tools](#visualization-tools)
10. [Statistical Testing](#statistical-testing)
11. [Utility Functions](#utility-functions)
12. [Best Practices](#best-practices)
13. [Examples](#examples)
14. [Troubleshooting](#troubleshooting)

## System Overview

The Evaluation Metrics System provides comprehensive evaluation metrics for various machine learning tasks, ensuring appropriate metrics are used for specific problems. It supports classification, regression, object detection, segmentation, and time series forecasting with task-specific metrics and visualization tools.

### Key Features

- **Task-Specific Metrics**: Appropriate metrics for each ML problem type
- **Comprehensive Coverage**: Classification, regression, detection, segmentation, time series
- **Statistical Testing**: Significance testing for model comparison
- **Visualization Tools**: Plots and charts for metric analysis
- **Custom Metrics**: Easy addition of custom evaluation metrics
- **Multi-Class Support**: Handles binary, multi-class, and multi-label problems
- **Performance Optimization**: Efficient computation for large datasets
- **Production Ready**: Well-tested with comprehensive error handling

## Core Components

### 1. BaseMetric (Abstract Base Class)

Abstract base class for all evaluation metrics:

```python
from evaluation_metrics_system import BaseMetric

class CustomMetric(BaseMetric):
    def __init__(self, name: str, task_type: str):
        super().__init__(name, task_type)
    
    def compute(self, y_true: Any, y_pred: Any, **kwargs) -> float:
        # Custom metric computation
        return metric_value
```

### 2. Task-Specific Metric Classes

- **ClassificationMetrics**: Accuracy, precision, recall, F1, AUC, etc.
- **RegressionMetrics**: MSE, MAE, R², RMSE, MAPE, etc.
- **ObjectDetectionMetrics**: mAP, IoU, precision-recall curves
- **SegmentationMetrics**: Dice coefficient, IoU, pixel accuracy
- **TimeSeriesMetrics**: MASE, SMAPE, directional accuracy

### 3. MetricCalculator

Main class for computing and managing evaluation metrics:

```python
from evaluation_metrics_system import MetricCalculator

calculator = MetricCalculator('classification', average='weighted')
results = calculator.compute_metrics(y_true, y_pred, y_pred_proba)
```

### 4. MetricVisualizer

Visualization tools for metrics analysis:

```python
from evaluation_metrics_system import MetricVisualizer

visualizer = MetricVisualizer()
visualizer.plot_confusion_matrix(y_true, y_pred)
visualizer.plot_roc_curve(y_true, y_pred_proba)
```

### 5. StatisticalTesting

Statistical significance testing for model comparison:

```python
from evaluation_metrics_system import StatisticalTesting

stats_test = StatisticalTesting()
result = stats_test.paired_t_test(scores1, scores2)
```

## Classification Metrics

### 1. Basic Classification Metrics

```python
from evaluation_metrics_system import ClassificationMetrics

metrics = ClassificationMetrics(average='weighted')

# Basic metrics
accuracy = metrics.accuracy(y_true, y_pred)
precision = metrics.precision(y_true, y_pred)
recall = metrics.recall(y_true, y_pred)
f1 = metrics.f1_score(y_true, y_pred)
```

**Parameters:**
- `average`: 'micro', 'macro', 'weighted', 'binary'
- `zero_division`: How to handle division by zero

### 2. Advanced Classification Metrics

```python
# F-beta score
f2_score = metrics.f_beta_score(y_true, y_pred, beta=2.0)

# ROC AUC
roc_auc = metrics.roc_auc(y_true, y_pred_proba, multi_class='ovr')

# Precision-Recall AUC
pr_auc = metrics.pr_auc(y_true, y_pred_proba)

# Log loss
log_loss_val = metrics.log_loss(y_true, y_pred_proba)
```

### 3. Confusion Matrix Metrics

```python
cm_metrics = metrics.confusion_matrix_metrics(y_true, y_pred)

# Available metrics
sensitivity = cm_metrics['sensitivity']
specificity = cm_metrics['specificity']
ppv = cm_metrics['positive_predictive_value']
npv = cm_metrics['negative_predictive_value']
balanced_acc = cm_metrics['balanced_accuracy']
```

### 4. Additional Classification Metrics

```python
# Matthews correlation coefficient
mcc = metrics.matthews_correlation(y_true, y_pred)

# Cohen's kappa
kappa = metrics.cohen_kappa(y_true, y_pred)

# Hamming loss (for multi-label)
hamming = metrics.hamming_loss(y_true, y_pred)

# Jaccard score
jaccard = metrics.jaccard_score(y_true, y_pred)
```

## Regression Metrics

### 1. Basic Regression Metrics

```python
from evaluation_metrics_system import RegressionMetrics

metrics = RegressionMetrics()

# Basic metrics
mse = metrics.mse(y_true, y_pred)
rmse = metrics.rmse(y_true, y_pred)
mae = metrics.mae(y_true, y_pred)
r2 = metrics.r2_score(y_true, y_pred)
```

### 2. Advanced Regression Metrics

```python
# Adjusted R²
adjusted_r2 = metrics.adjusted_r2(y_true, y_pred, n_features=10)

# Percentage errors
mape = metrics.mape(y_true, y_pred)
smape = metrics.smape(y_true, y_pred)

# Robust loss functions
huber = metrics.huber_loss(y_true, y_pred, delta=1.0)
log_cosh = metrics.log_cosh_loss(y_true, y_pred)
```

### 3. Correlation Metrics

```python
# Correlation coefficients
pearson = metrics.pearson_correlation(y_true, y_pred)
spearman = metrics.spearman_correlation(y_true, y_pred)

# Explained variance
explained_var = metrics.explained_variance(y_true, y_pred)
```

### 4. Additional Regression Metrics

```python
# Maximum error
max_err = metrics.max_error(y_true, y_pred)

# Mean absolute deviation
mad = metrics.mean_absolute_deviation(y_true, y_pred)
```

## Object Detection Metrics

### 1. IoU Calculation

```python
from evaluation_metrics_system import ObjectDetectionMetrics

metrics = ObjectDetectionMetrics(iou_threshold=0.5)

# Calculate IoU between two bounding boxes
box1 = np.array([0, 0, 10, 10])  # [x1, y1, x2, y2]
box2 = np.array([5, 5, 15, 15])
iou = metrics.calculate_iou(box1, box2)
```

### 2. mAP Calculation

```python
# Calculate mAP
ground_truth = [[box1], [box2]]  # List of ground truth boxes per image
predictions = [[box1], [box2]]   # List of predicted boxes per image

map_results = metrics.calculate_map(ground_truth, predictions)

# Available metrics
mAP = map_results['mAP']
mAP_50 = map_results['mAP_50']
mAP_75 = map_results['mAP_75']
mAP_90 = map_results['mAP_90']
```

## Segmentation Metrics

### 1. Basic Segmentation Metrics

```python
from evaluation_metrics_system import SegmentationMetrics

metrics = SegmentationMetrics(num_classes=3, ignore_index=255)

# Pixel accuracy
pixel_acc = metrics.pixel_accuracy(y_true, y_pred)
mean_pixel_acc = metrics.mean_pixel_accuracy(y_true, y_pred)
```

### 2. Advanced Segmentation Metrics

```python
# Dice coefficient
dice = metrics.dice_coefficient(y_true, y_pred)
mean_dice = metrics.mean_dice_coefficient(y_true, y_pred)

# IoU score
iou = metrics.iou_score(y_true, y_pred)
mean_iou = metrics.mean_iou_score(y_true, y_pred)
```

## Time Series Metrics

### 1. Time Series Forecasting Metrics

```python
from evaluation_metrics_system import TimeSeriesMetrics

metrics = TimeSeriesMetrics()

# MASE (Mean Absolute Scaled Error)
mase = metrics.mase(y_true, y_pred, y_train, seasonality=1)

# SMAPE (Symmetric Mean Absolute Percentage Error)
smape = metrics.smape(y_true, y_pred)

# Directional accuracy
directional_acc = metrics.directional_accuracy(y_true, y_pred)

# Theil's U statistic
theil_u = metrics.theil_u(y_true, y_pred)
```

## Metric Calculator

### 1. Basic Usage

```python
from evaluation_metrics_system import MetricCalculator

# Create calculator for specific task
calculator = MetricCalculator('classification', average='weighted')

# Compute all available metrics
results = calculator.compute_metrics(y_true, y_pred, y_pred_proba)
```

### 2. Available Task Types

- `'classification'`: Classification metrics
- `'regression'`: Regression metrics
- `'object_detection'`: Object detection metrics
- `'segmentation'`: Segmentation metrics
- `'time_series'`: Time series metrics

### 3. Custom Metrics

```python
# Add custom metric
def custom_metric(y_true, y_pred):
    return np.mean(y_true == y_pred)

calculator.add_custom_metric('custom_accuracy', custom_metric)
results = calculator.compute_metrics(y_true, y_pred)
```

### 4. Model Comparison

```python
# Compare multiple models
model_results = {
    'Model A': {'accuracy': 0.85, 'f1_score': 0.83},
    'Model B': {'accuracy': 0.87, 'f1_score': 0.85},
    'Model C': {'accuracy': 0.82, 'f1_score': 0.80}
}

comparison = calculator.compare_models(model_results, 'accuracy')
print(f"Best model: {comparison['best_model']}")
print(f"Best score: {comparison['best_score']}")
```

## Visualization Tools

### 1. Confusion Matrix

```python
from evaluation_metrics_system import MetricVisualizer

visualizer = MetricVisualizer()

# Plot confusion matrix
visualizer.plot_confusion_matrix(
    y_true, y_pred, 
    class_names=['Class 0', 'Class 1', 'Class 2'],
    title="Classification Results"
)
```

### 2. ROC and PR Curves

```python
# ROC curve
visualizer.plot_roc_curve(y_true, y_pred_proba, title="ROC Curve")

# Precision-Recall curve
visualizer.plot_precision_recall_curve(
    y_true, y_pred_proba, 
    title="Precision-Recall Curve"
)
```

### 3. Model Comparison

```python
# Compare models for specific metric
model_results = {
    'Model A': {'accuracy': 0.85, 'f1_score': 0.83},
    'Model B': {'accuracy': 0.87, 'f1_score': 0.85},
    'Model C': {'accuracy': 0.82, 'f1_score': 0.80}
}

visualizer.plot_metrics_comparison(
    model_results, 'accuracy', 
    title="Model Accuracy Comparison"
)
```

### 4. Regression Results

```python
# Plot regression results
visualizer.plot_regression_results(
    y_true, y_pred, 
    title="Regression Analysis"
)
```

## Statistical Testing

### 1. Paired T-Test

```python
from evaluation_metrics_system import StatisticalTesting

stats_test = StatisticalTesting()

# Compare two models
result = stats_test.paired_t_test(scores1, scores2, alpha=0.05)

print(f"T-statistic: {result['t_statistic']}")
print(f"P-value: {result['p_value']}")
print(f"Significant: {result['significant']}")
```

### 2. Wilcoxon Test

```python
# Non-parametric test
result = stats_test.wilcoxon_test(scores1, scores2, alpha=0.05)
```

### 3. Mann-Whitney Test

```python
# Independent samples test
result = stats_test.mann_whitney_test(scores1, scores2, alpha=0.05)
```

## Utility Functions

### 1. Task-Specific Evaluation

```python
from evaluation_metrics_system import (
    evaluate_classification, evaluate_regression,
    evaluate_object_detection, evaluate_segmentation,
    evaluate_time_series
)

# Classification evaluation
results = evaluate_classification(y_true, y_pred, y_pred_proba)

# Regression evaluation
results = evaluate_regression(y_true, y_pred)

# Object detection evaluation
results = evaluate_object_detection(ground_truth, predictions)

# Segmentation evaluation
results = evaluate_segmentation(y_true, y_pred, num_classes=3)

# Time series evaluation
results = evaluate_time_series(y_true, y_pred, y_train)
```

### 2. Get Task Metrics

```python
from evaluation_metrics_system import get_task_metrics

# Get appropriate metrics for task
calculator = get_task_metrics('classification', average='weighted')
```

## Best Practices

### 1. Metric Selection Guidelines

#### For Classification Tasks
```python
# Binary classification
metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc', 'pr_auc']

# Multi-class classification
metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'cohen_kappa']

# Imbalanced datasets
metrics = ['balanced_accuracy', 'f1_score', 'roc_auc', 'pr_auc']

# Multi-label classification
metrics = ['hamming_loss', 'jaccard_score', 'f1_score']
```

#### For Regression Tasks
```python
# General regression
metrics = ['mse', 'rmse', 'mae', 'r2_score', 'pearson_correlation']

# Percentage errors important
metrics = ['mape', 'smape', 'rmse', 'r2_score']

# Robust evaluation
metrics = ['huber_loss', 'log_cosh_loss', 'r2_score']
```

#### For Object Detection
```python
# Standard evaluation
metrics = ['mAP', 'mAP_50', 'mAP_75']

# Real-time applications
metrics = ['mAP_50', 'inference_time']
```

#### For Segmentation
```python
# Standard evaluation
metrics = ['pixel_accuracy', 'mean_iou_score', 'dice_coefficient']

# Medical imaging
metrics = ['dice_coefficient', 'mean_iou_score', 'sensitivity', 'specificity']
```

#### For Time Series
```python
# Forecasting evaluation
metrics = ['mase', 'smape', 'rmse', 'directional_accuracy']

# Financial time series
metrics = ['directional_accuracy', 'theil_u', 'smape']
```

### 2. Evaluation Workflow

```python
# 1. Choose appropriate metrics
calculator = MetricCalculator('classification', average='weighted')

# 2. Compute metrics
results = calculator.compute_metrics(y_true, y_pred, y_pred_proba)

# 3. Visualize results
visualizer = MetricVisualizer()
visualizer.plot_confusion_matrix(y_true, y_pred)
visualizer.plot_roc_curve(y_true, y_pred_proba)

# 4. Compare models
model_results = {
    'Model A': results,
    'Model B': other_results
}
comparison = calculator.compare_models(model_results, 'f1_score')

# 5. Statistical testing
stats_test = StatisticalTesting()
test_result = stats_test.paired_t_test(scores1, scores2)
```

### 3. Custom Metric Creation

```python
# Create custom metric
def custom_balanced_accuracy(y_true, y_pred):
    from sklearn.metrics import balanced_accuracy_score
    return balanced_accuracy_score(y_true, y_pred)

# Add to calculator
calculator = MetricCalculator('classification')
calculator.add_custom_metric('balanced_accuracy', custom_balanced_accuracy)

# Use in evaluation
results = calculator.compute_metrics(y_true, y_pred)
```

## Examples

### 1. Classification Evaluation

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from evaluation_metrics_system import (
    MetricCalculator, MetricVisualizer, StatisticalTesting
)

# Create data
X, y = make_classification(n_samples=1000, n_features=10, n_classes=3, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Get predictions
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# Evaluate
calculator = MetricCalculator('classification', average='weighted')
results = calculator.compute_metrics(y_test, y_pred, y_pred_proba)

print("Classification Results:")
for metric, value in results.items():
    print(f"{metric}: {value:.4f}")

# Visualize
visualizer = MetricVisualizer()
visualizer.plot_confusion_matrix(y_test, y_pred)
visualizer.plot_roc_curve(y_test, y_pred_proba)
```

### 2. Regression Evaluation

```python
from sklearn.datasets import make_regression
from sklearn.ensemble import RandomForestRegressor

# Create data
X, y = make_regression(n_samples=1000, n_features=10, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Get predictions
y_pred = model.predict(X_test)

# Evaluate
calculator = MetricCalculator('regression')
results = calculator.compute_metrics(y_test, y_pred)

print("Regression Results:")
for metric, value in results.items():
    print(f"{metric}: {value:.4f}")

# Visualize
visualizer = MetricVisualizer()
visualizer.plot_regression_results(y_test, y_pred)
```

### 3. Model Comparison

```python
# Train multiple models
models = {
    'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
    'RandomForest2': RandomForestClassifier(n_estimators=200, random_state=42)
}

model_results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    calculator = MetricCalculator('classification')
    results = calculator.compute_metrics(y_test, y_pred, y_pred_proba)
    model_results[name] = results

# Compare models
comparison = calculator.compare_models(model_results, 'f1_score')
print(f"Best model: {comparison['best_model']}")
print(f"Best F1 score: {comparison['best_score']:.4f}")

# Visualize comparison
visualizer = MetricVisualizer()
visualizer.plot_metrics_comparison(model_results, 'f1_score')
```

### 4. Statistical Testing

```python
# Perform statistical testing
stats_test = StatisticalTesting()

# Get scores from cross-validation
scores1 = [0.85, 0.87, 0.83, 0.86, 0.84]  # Model A
scores2 = [0.82, 0.84, 0.81, 0.83, 0.82]  # Model B

# Paired t-test
result = stats_test.paired_t_test(scores1, scores2)
print(f"T-statistic: {result['t_statistic']:.4f}")
print(f"P-value: {result['p_value']:.4f}")
print(f"Significant difference: {result['significant']}")

# Wilcoxon test
result = stats_test.wilcoxon_test(scores1, scores2)
print(f"Wilcoxon statistic: {result['statistic']:.4f}")
print(f"P-value: {result['p_value']:.4f}")
```

### 5. Custom Metrics

```python
# Define custom metric
def custom_f2_score(y_true, y_pred):
    from sklearn.metrics import f1_score
    return f1_score(y_true, y_pred, average='weighted', beta=2)

# Add to calculator
calculator = MetricCalculator('classification')
calculator.add_custom_metric('f2_score', custom_f2_score)

# Use in evaluation
results = calculator.compute_metrics(y_test, y_pred)
print(f"Custom F2 score: {results['f2_score']:.4f}")
```

### 6. Time Series Evaluation

```python
# Create time series data
np.random.seed(42)
y_train = np.random.randn(100)
y_true = np.random.randn(50)
y_pred = y_true + np.random.randn(50) * 0.1

# Evaluate time series
calculator = MetricCalculator('time_series')
results = calculator.compute_metrics(y_true, y_pred, y_train=y_train)

print("Time Series Results:")
for metric, value in results.items():
    print(f"{metric}: {value:.4f}")
```

## Troubleshooting

### Common Issues

1. **Metric Computation Errors**
   ```python
   # Check data types
   y_true = np.array(y_true)
   y_pred = np.array(y_pred)
   
   # Check shapes
   assert y_true.shape == y_pred.shape
   
   # Check for NaN values
   assert not np.isnan(y_true).any()
   assert not np.isnan(y_pred).any()
   ```

2. **Classification Metrics Issues**
   ```python
   # For binary classification
   if len(np.unique(y_true)) == 2:
       # Use binary metrics
       roc_auc = metrics.roc_auc(y_true, y_pred_proba[:, 1])
   else:
       # Use multi-class metrics
       roc_auc = metrics.roc_auc(y_true, y_pred_proba, multi_class='ovr')
   ```

3. **Regression Metrics Issues**
   ```python
   # Check for zero values in MAPE
   if np.any(y_true == 0):
       # Use SMAPE instead
       error = metrics.smape(y_true, y_pred)
   else:
       error = metrics.mape(y_true, y_pred)
   ```

4. **Object Detection Issues**
   ```python
   # Ensure proper box format
   # Boxes should be [x1, y1, x2, y2]
   assert box.shape == (4,)
   assert box[2] > box[0]  # x2 > x1
   assert box[3] > box[1]  # y2 > y1
   ```

5. **Segmentation Issues**
   ```python
   # Check for ignore index
   mask = y_true != ignore_index
   y_true_valid = y_true[mask]
   y_pred_valid = y_pred[mask]
   ```

### Performance Optimization

1. **Large Datasets**
   ```python
   # Use batch processing
   batch_size = 1000
   results = []
   
   for i in range(0, len(y_true), batch_size):
       batch_true = y_true[i:i+batch_size]
       batch_pred = y_pred[i:i+batch_size]
       batch_result = calculator.compute_metrics(batch_true, batch_pred)
       results.append(batch_result)
   ```

2. **Memory Issues**
   ```python
   # Use generators for large datasets
   def data_generator():
       for i in range(0, len(y_true), batch_size):
           yield y_true[i:i+batch_size], y_pred[i:i+batch_size]
   ```

3. **Parallel Processing**
   ```python
   # Use multiprocessing for multiple models
   from multiprocessing import Pool
   
   def evaluate_model(model_data):
       model, X, y = model_data
       y_pred = model.predict(X)
       return calculator.compute_metrics(y, y_pred)
   
   with Pool() as pool:
       results = pool.map(evaluate_model, model_data_list)
   ```

This comprehensive guide covers all aspects of the Evaluation Metrics System, from basic usage to advanced techniques. The system ensures appropriate metrics are used for specific machine learning tasks with proper evaluation and comparison capabilities. 