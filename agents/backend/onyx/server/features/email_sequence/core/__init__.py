"""
Email Sequence Core Components

This module contains the core engine and orchestration components
for the email sequence system with optimized performance.
"""

from .email_sequence_engine import EmailSequenceEngine
from .sequence_manager import SequenceManager
from .personalization_engine import PersonalizationEngine
from .analytics_engine import AnalyticsEngine
from .optimization_engine import OptimizationEngine

__all__ = [
    "EmailSequenceEngine",
    "SequenceManager",
    "PersonalizationEngine", 
    "AnalyticsEngine",
    "OptimizationEngine"
] 