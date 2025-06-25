"""
Onyx Core Module - Refactored ultra-optimized core components.

This module provides the foundational components for the Onyx ultra-optimized
production system with quantum-level performance optimizations.
"""

from .config import config, QuantumConfig
from .optimizer import quantum_optimizer, QuantumOptimizer
from .detector import detector, LibraryDetector
from .middleware import QuantumMiddleware
from .monitoring import QuantumMonitor

__all__ = [
    'config',
    'QuantumConfig',
    'quantum_optimizer', 
    'QuantumOptimizer',
    'detector',
    'LibraryDetector',
    'QuantumMiddleware',
    'QuantumMonitor'
]

__version__ = "8.0.0-quantum" 