"""
Unified TruthGPT Optimizers
============================
Consolidated optimizer system to replace duplicate optimizer files.
"""

from typing import Dict, Any

from optimizers.base_truthgpt_optimizer import (
    BaseTruthGPTOptimizer,
    UnifiedTruthGPTOptimizer,
    OptimizationLevel,
    OptimizationResult,
)
from optimizers.component_optimizers import (
    ComponentOptimizer,
    get_component_optimizer,
)

# Factory function for backward compatibility
def create_truthgpt_optimizer(level: str = "basic", config: Dict[str, Any] = None):
    """
    Create a TruthGPT optimizer with the specified level.
    
    Args:
        level: Optimization level (basic, advanced, expert, etc.)
        config: Optional configuration dictionary
    
    Returns:
        UnifiedTruthGPTOptimizer instance
    """
    from typing import Dict, Any
    
    # Map string level to enum
    level_map = {
        'basic': OptimizationLevel.BASIC,
        'advanced': OptimizationLevel.ADVANCED,
        'expert': OptimizationLevel.EXPERT,
        'master': OptimizationLevel.MASTER,
        'legendary': OptimizationLevel.LEGENDARY,
        'transcendent': OptimizationLevel.TRANSCENDENT,
        'divine': OptimizationLevel.DIVINE,
        'omnipotent': OptimizationLevel.OMNIPOTENT,
        'infinite': OptimizationLevel.INFINITE,
        'ultimate': OptimizationLevel.ULTIMATE,
        'supreme': OptimizationLevel.SUPREME,
        'enterprise': OptimizationLevel.ENTERPRISE,
        'ultra_fast': OptimizationLevel.ULTRA_FAST,
        'ultra_speed': OptimizationLevel.ULTRA_SPEED,
        'hyper_speed': OptimizationLevel.HYPER_SPEED,
        'lightning_speed': OptimizationLevel.LIGHTNING_SPEED,
    }
    
    opt_level = level_map.get(level.lower(), OptimizationLevel.BASIC)
    return UnifiedTruthGPTOptimizer(config=config or {}, level=opt_level)


# Backward compatibility aliases
def create_advanced_truthgpt_optimizer(config: Dict[str, Any] = None):
    """Create an advanced TruthGPT optimizer (backward compatibility)."""
    return create_truthgpt_optimizer('advanced', config)


def create_expert_truthgpt_optimizer(config: Dict[str, Any] = None):
    """Create an expert TruthGPT optimizer (backward compatibility)."""
    return create_truthgpt_optimizer('expert', config)


def create_ultimate_truthgpt_optimizer(config: Dict[str, Any] = None):
    """Create an ultimate TruthGPT optimizer (backward compatibility)."""
    return create_truthgpt_optimizer('ultimate', config)


def create_supreme_truthgpt_optimizer(config: Dict[str, Any] = None):
    """Create a supreme TruthGPT optimizer (backward compatibility)."""
    return create_truthgpt_optimizer('supreme', config)


def create_enterprise_truthgpt_optimizer(config: Dict[str, Any] = None):
    """Create an enterprise TruthGPT optimizer (backward compatibility)."""
    return create_truthgpt_optimizer('enterprise', config)


def create_ultra_fast_truthgpt_optimizer(config: Dict[str, Any] = None):
    """Create an ultra-fast TruthGPT optimizer (backward compatibility)."""
    return create_truthgpt_optimizer('ultra_fast', config)


def create_ultra_speed_truthgpt_optimizer(config: Dict[str, Any] = None):
    """Create an ultra-speed TruthGPT optimizer (backward compatibility)."""
    return create_truthgpt_optimizer('ultra_speed', config)


def create_hyper_speed_truthgpt_optimizer(config: Dict[str, Any] = None):
    """Create a hyper-speed TruthGPT optimizer (backward compatibility)."""
    return create_truthgpt_optimizer('hyper_speed', config)


def create_lightning_speed_truthgpt_optimizer(config: Dict[str, Any] = None):
    """Create a lightning-speed TruthGPT optimizer (backward compatibility)."""
    return create_truthgpt_optimizer('lightning_speed', config)


# Generic optimizers
from optimizers.generic_optimizer import (
    UnifiedGenericOptimizer,
    GenericOptimizationLevel,
    GenericOptimizationResult,
    create_generic_optimizer,
)

# Optimization techniques and pipeline
from optimizers.techniques import (
    OptimizationTechnique,
    get_technique,
    register_technique,
    TechniqueRegistry,
)

from optimizers.optimization_pipeline import (
    OptimizationPipeline,
    OptimizationStep,
    build_optimization_pipeline,
    LevelBasedPipelineBuilder,
)

from optimizers.metrics import (
    MetricsCalculator,
    calculate_optimization_metrics,
)

__all__ = [
    # TruthGPT optimizers
    'BaseTruthGPTOptimizer',
    'UnifiedTruthGPTOptimizer',
    'OptimizationLevel',
    'OptimizationResult',
    'ComponentOptimizer',
    'get_component_optimizer',
    'create_truthgpt_optimizer',
    'create_advanced_truthgpt_optimizer',
    'create_expert_truthgpt_optimizer',
    'create_ultimate_truthgpt_optimizer',
    'create_supreme_truthgpt_optimizer',
    'create_enterprise_truthgpt_optimizer',
    'create_ultra_fast_truthgpt_optimizer',
    'create_ultra_speed_truthgpt_optimizer',
    'create_hyper_speed_truthgpt_optimizer',
    'create_lightning_speed_truthgpt_optimizer',
    # Generic optimizers
    'UnifiedGenericOptimizer',
    'GenericOptimizationLevel',
    'GenericOptimizationResult',
    'create_generic_optimizer',
    # Optimization techniques
    'OptimizationTechnique',
    'get_technique',
    'register_technique',
    'TechniqueRegistry',
    # Optimization pipeline
    'OptimizationPipeline',
    'OptimizationStep',
    'build_optimization_pipeline',
    'LevelBasedPipelineBuilder',
    # Metrics
    'MetricsCalculator',
    'calculate_optimization_metrics',
]
