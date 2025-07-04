from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np

@dataclass
class OptimizationResult:
    """Resultado de optimización ultra-extrema"""
    success: bool
    optimal_parameters: np.ndarray
    optimal_value: float
    convergence_history: List[float]
    quantum_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    neural_metrics: Dict[str, float]
    execution_time: float
    iterations: int
    model_size_mb: float
    memory_usage_gb: float 