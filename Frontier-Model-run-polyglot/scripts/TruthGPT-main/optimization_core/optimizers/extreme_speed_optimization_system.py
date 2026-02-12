"""
Backward-compatibility shim for extreme_speed_optimization_system.
Maps extreme speed levels to the unified optimizer architecture.
"""

import warnings
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import torch.nn as nn
from .core.base_truthgpt_optimizer import UnifiedTruthGPTOptimizer, OptimizationLevel

warnings.warn(
    "extreme_speed_optimization_system is deprecated. Please use UnifiedOptimizer instead.",
    DeprecationWarning,
    stacklevel=2
)

class ExtremeSpeedLevel(Enum):
    WARP = "warp"
    HYPERWARP = "hyperwarp"
    LUDICROUS = "ludicrous"
    PLAID = "plaid"
    MAXIMUM = "maximum"
    OVERDRIVE = "overdrive"
    TURBO = "turbo"
    NITRO = "nitro"
    ROCKET = "rocket"
    LIGHTNING = "lightning"
    BLAZING = "blazing"
    INFERNO = "inferno"
    NUCLEAR = "nuclear"
    QUANTUM = "quantum"
    COSMIC = "cosmic"
    DIVINE = "divine"
    INFINITE = "infinite"
    ULTIMATE = "ultimate"
    ABSOLUTE = "absolute"
    PERFECT = "perfect"
    INFINITY = "infinity"

@dataclass
class ExtremeSpeedResult:
    optimized_model: nn.Module
    speed_improvement: float
    memory_reduction: float
    accuracy_preservation: float
    energy_efficiency: float
    optimization_time: float
    level: ExtremeSpeedLevel
    techniques_applied: List[str]
    performance_metrics: Dict[str, float]

class ExtremeSpeedOptimizationSystem:
    """Extreme speed optimization system (Shim)."""
    
    def __init__(self, level: ExtremeSpeedLevel = ExtremeSpeedLevel.WARP, config: Dict[str, Any] = None):
        self.level = level
        self.config = config or {}
        # Map extreme levels to SUPREME in the new system
        self.internal_optimizer = UnifiedTruthGPTOptimizer(
            config=self.config, 
            level=OptimizationLevel.SUPREME
        )

    def optimize_extreme_speed(self, model: nn.Module, **kwargs) -> ExtremeSpeedResult:
        """Apply extreme speed optimizations (Shim)."""
        result = self.internal_optimizer.optimize(model, **kwargs)
        
        return ExtremeSpeedResult(
            optimized_model=result.optimized_model,
            speed_improvement=result.speed_improvement,
            memory_reduction=result.memory_reduction,
            accuracy_preservation=result.accuracy_preservation,
            energy_efficiency=result.energy_efficiency,
            optimization_time=result.optimization_time,
            level=self.level,
            techniques_applied=result.techniques_applied,
            performance_metrics=result.performance_metrics
        )

def create_extreme_speed_system(level="warp", config=None):
    """Factory function for extreme speed system (Shim)."""
    try:
        level_enum = ExtremeSpeedLevel(level.lower())
    except ValueError:
        level_enum = ExtremeSpeedLevel.WARP
    return ExtremeSpeedOptimizationSystem(level=level_enum, config=config)

__all__ = ['ExtremeSpeedLevel', 'ExtremeSpeedResult', 'ExtremeSpeedOptimizationSystem', 'create_extreme_speed_system']
