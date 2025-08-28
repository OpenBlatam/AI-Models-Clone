#!/usr/bin/env python3
"""
Modular Optimization Strategies Module

Advanced optimization strategies with:
- Factory pattern for strategy creation
- Observer pattern for optimization events
- Command pattern for optimization actions
- Chain of responsibility for optimization decisions
"""

import torch
import torch.nn as nn
import numpy as np
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """Types of optimization strategies."""
    MEMORY = "memory"
    COMPUTATION = "computation"
    COMMUNICATION = "communication"
    HYBRID = "hybrid"

@dataclass
class OptimizationContext:
    """Context for optimization decisions."""
    device: torch.device
    memory_pressure: float
    computation_load: float
    communication_overhead: float
    current_step: int
    batch_size: int
    model_size: int
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class OptimizationObserver(ABC):
    """Abstract observer for optimization events."""
    
    @abstractmethod
    def on_optimization_performed(self, strategy_name: str, context: OptimizationContext, result: Dict[str, Any]):
        """Called when optimization is performed."""
        pass
    
    @abstractmethod
    def on_optimization_failed(self, strategy_name: str, context: OptimizationContext, error: Exception):
        """Called when optimization fails."""
        pass

class OptimizationStrategy(ABC):
    """Abstract base class for optimization strategies."""
    
    def __init__(self, name: str, optimization_type: OptimizationType):
        self.name = name
        self.optimization_type = optimization_type
        self.observers: List[OptimizationObserver] = []
        self.success_count = 0
        self.failure_count = 0
        self.last_used = None
    
    def add_observer(self, observer: OptimizationObserver):
        """Add an observer to this strategy."""
        self.observers.append(observer)
    
    def remove_observer(self, observer: OptimizationOptimizationObserver):
        """Remove an observer from this strategy."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_success(self, context: OptimizationContext, result: Dict[str, Any]):
        """Notify observers of successful optimization."""
        self.success_count += 1
        self.last_used = time.time()
        for observer in self.observers:
            observer.on_optimization_performed(self.name, context, result)
    
    def notify_failure(self, context: OptimizationContext, error: Exception):
        """Notify observers of failed optimization."""
        self.failure_count += 1
        for observer in self.observers:
            observer.on_optimization_failed(self.name, context, error)
    
    @abstractmethod
    def can_optimize(self, context: OptimizationContext) -> bool:
        """Check if this strategy can optimize the given context."""
        pass
    
    @abstractmethod
    def optimize(self, context: OptimizationContext) -> Dict[str, Any]:
        """Perform optimization."""
        pass
    
    def get_success_rate(self) -> float:
        """Get the success rate of this strategy."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

class MemoryOptimizationStrategy(OptimizationStrategy):
    """Memory optimization strategy."""
    
    def __init__(self, threshold: float = 0.8):
        super().__init__("MemoryOptimization", OptimizationType.MEMORY)
        self.threshold = threshold
    
    def can_optimize(self, context: OptimizationContext) -> bool:
        return context.memory_pressure > self.threshold
    
    def optimize(self, context: OptimizationContext) -> Dict[str, Any]:
        try:
            if context.device.type == 'cuda':
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            result = {
                'memory_freed': True,
                'device': str(context.device),
                'pressure_before': context.memory_pressure,
                'pressure_after': context.memory_pressure * 0.7  # Estimate
            }
            
            self.notify_success(context, result)
            return result
            
        except Exception as e:
            self.notify_failure(context, e)
            raise

class ComputationOptimizationStrategy(OptimizationStrategy):
    """Computation optimization strategy."""
    
    def __init__(self, threshold: float = 0.7):
        super().__init__("ComputationOptimization", OptimizationType.COMPUTATION)
        self.threshold = threshold
    
    def can_optimize(self, context: OptimizationContext) -> bool:
        return context.computation_load > self.threshold
    
    def optimize(self, context: OptimizationContext) -> Dict[str, Any]:
        try:
            # Simulate computation optimization
            result = {
                'computation_optimized': True,
                'load_before': context.computation_load,
                'load_after': context.computation_load * 0.8,
                'batch_size_adjusted': max(1, context.batch_size // 2)
            }
            
            self.notify_success(context, result)
            return result
            
        except Exception as e:
            self.notify_failure(context, e)
            raise

class HybridOptimizationStrategy(OptimizationStrategy):
    """Hybrid optimization strategy combining multiple approaches."""
    
    def __init__(self):
        super().__init__("HybridOptimization", OptimizationType.HYBRID)
        self.sub_strategies = [
            MemoryOptimizationStrategy(),
            ComputationOptimizationStrategy()
        ]
    
    def can_optimize(self, context: OptimizationContext) -> bool:
        return any(strategy.can_optimize(context) for strategy in self.sub_strategies)
    
    def optimize(self, context: OptimizationContext) -> Dict[str, Any]:
        try:
            results = {}
            for strategy in self.sub_strategies:
                if strategy.can_optimize(context):
                    result = strategy.optimize(context)
                    results[strategy.name] = result
            
            result = {
                'hybrid_optimization': True,
                'strategies_applied': list(results.keys()),
                'results': results
            }
            
            self.notify_success(context, result)
            return result
            
        except Exception as e:
            self.notify_failure(context, e)
            raise

class OptimizationFactory:
    """Factory for creating optimization strategies."""
    
    _strategies = {
        OptimizationType.MEMORY: MemoryOptimizationStrategy,
        OptimizationType.COMPUTATION: ComputationOptimizationStrategy,
        OptimizationType.HYBRID: HybridOptimizationStrategy
    }
    
    @classmethod
    def create_strategy(cls, optimization_type: OptimizationType, **kwargs) -> OptimizationStrategy:
        """Create a strategy of the specified type."""
        if optimization_type not in cls._strategies:
            raise ValueError(f"Unknown optimization type: {optimization_type}")
        
        strategy_class = cls._strategies[optimization_type]
        return strategy_class(**kwargs)
    
    @classmethod
    def create_all_strategies(cls) -> List[OptimizationStrategy]:
        """Create all available strategies."""
        return [cls.create_strategy(opt_type) for opt_type in OptimizationType]

class OptimizationChain:
    """Chain of responsibility for optimization decisions."""
    
    def __init__(self):
        self.strategies: List[OptimizationStrategy] = []
        self.current_index = 0
    
    def add_strategy(self, strategy: OptimizationStrategy):
        """Add a strategy to the chain."""
        self.strategies.append(strategy)
    
    def optimize(self, context: OptimizationContext) -> Optional[Dict[str, Any]]:
        """Try to optimize using the chain of strategies."""
        for strategy in self.strategies:
            if strategy.can_optimize(context):
                try:
                    return strategy.optimize(context)
                except Exception as e:
                    logger.warning(f"Strategy {strategy.name} failed: {e}")
                    continue
        
        return None

class OptimizationLogger(OptimizationObserver):
    """Observer that logs optimization events."""
    
    def on_optimization_performed(self, strategy_name: str, context: OptimizationContext, result: Dict[str, Any]):
        logger.info(f"✅ Optimization {strategy_name} performed successfully")
        logger.info(f"   Context: {context}")
        logger.info(f"   Result: {result}")
    
    def on_optimization_failed(self, strategy_name: str, context: OptimizationContext, error: Exception):
        logger.error(f"❌ Optimization {strategy_name} failed")
        logger.error(f"   Context: {context}")
        logger.error(f"   Error: {error}")

class OptimizationMetrics(OptimizationObserver):
    """Observer that tracks optimization metrics."""
    
    def __init__(self):
        self.metrics = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'strategy_performance': {},
            'last_optimization': None
        }
    
    def on_optimization_performed(self, strategy_name: str, context: OptimizationContext, result: Dict[str, Any]):
        self.metrics['total_optimizations'] += 1
        self.metrics['successful_optimizations'] += 1
        self.metrics['last_optimization'] = time.time()
        
        if strategy_name not in self.metrics['strategy_performance']:
            self.metrics['strategy_performance'][strategy_name] = {
                'successes': 0,
                'failures': 0,
                'last_used': None
            }
        
        self.metrics['strategy_performance'][strategy_name]['successes'] += 1
        self.metrics['strategy_performance'][strategy_name]['last_used'] = time.time()
    
    def on_optimization_failed(self, strategy_name: str, context: OptimizationContext, error: Exception):
        self.metrics['total_optimizations'] += 1
        self.metrics['failed_optimizations'] += 1
        self.metrics['last_optimization'] = time.time()
        
        if strategy_name not in self.metrics['strategy_performance']:
            self.metrics['strategy_performance'][strategy_name] = {
                'successes': 0,
                'failures': 0,
                'last_used': None
            }
        
        self.metrics['strategy_performance'][strategy_name]['failures'] += 1
        self.metrics['strategy_performance'][strategy_name]['last_used'] = time.time()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get optimization metrics summary."""
        return self.metrics.copy()

# Example usage
if __name__ == "__main__":
    # Create optimization strategies
    factory = OptimizationFactory()
    strategies = factory.create_all_strategies()
    
    # Create observers
    logger = OptimizationLogger()
    metrics = OptimizationMetrics()
    
    # Add observers to strategies
    for strategy in strategies:
        strategy.add_observer(logger)
        strategy.add_observer(metrics)
    
    # Create optimization chain
    chain = OptimizationChain()
    for strategy in strategies:
        chain.add_strategy(strategy)
    
    # Test optimization
    context = OptimizationContext(
        device=torch.device('cpu'),
        memory_pressure=0.9,
        computation_load=0.8,
        communication_overhead=0.1,
        current_step=100,
        batch_size=32,
        model_size=1000000
    )
    
    # Perform optimization
    result = chain.optimize(context)
    if result:
        print(f"Optimization result: {result}")
    
    # Get metrics
    summary = metrics.get_summary()
    print(f"Optimization metrics: {summary}")
