"""
📈 Evaluation Package
====================

This package contains all evaluation utilities for the optimized image processing system.
"""

from .evaluator import Evaluator, EvaluatorConfig
from .metrics_calculator import MetricsCalculator
from .performance_analyzer import PerformanceAnalyzer
from .model_comparison import ModelComparison
from .benchmark_suite import BenchmarkSuite
from .evaluation_report import EvaluationReport

__all__ = [
    'Evaluator',
    'EvaluatorConfig',
    'MetricsCalculator',
    'PerformanceAnalyzer',
    'ModelComparison',
    'BenchmarkSuite',
    'EvaluationReport'
]





