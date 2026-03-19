"""
Training Utilities Module

This module contains utilities for training, evaluation, and optimization.
"""

from __future__ import annotations

import importlib

__all__ = [
    'TruthGPTTrainingUtils',
    'TruthGPTAdvancedTraining',
    'TruthGPTOptimizationUtils',
    'TruthGPTEvaluationUtils',
    'TruthGPTAdvancedEvaluation',
]

_LAZY_IMPORTS = {
    'TruthGPTTrainingUtils': 'optimization_core.modules.truthgpt.training',
    'TruthGPTAdvancedTraining': 'optimization_core.modules.truthgpt.advanced_training',
    'TruthGPTOptimizationUtils': 'optimization_core.modules.truthgpt.optimization_utils',
    'TruthGPTEvaluationUtils': 'optimization_core.modules.truthgpt.evaluation',
    'TruthGPTAdvancedEvaluation': 'optimization_core.modules.truthgpt.advanced_evaluation',
}

_import_cache = {}


def __getattr__(name: str):
    """Lazy import system for training utility modules."""
    if name.startswith('_'):
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    
    if name in _import_cache:
        return _import_cache[name]
    
    module_path = _LAZY_IMPORTS[name]
    try:
        # Use absolute imports to avoid __package__ ambiguity
        module = importlib.import_module(module_path)
        obj = getattr(module, name)
        _import_cache[name] = obj
        return obj
    except (ImportError, AttributeError) as e:
        raise AttributeError(
            f"module '{__name__}' has no attribute '{name}'. "
            f"Failed to import: {e}"
        ) from e



