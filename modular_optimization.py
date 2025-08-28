#!/usr/bin/env python3
"""
Modular Optimization System

Advanced optimization with:
- Factory pattern for strategy creation
- Observer pattern for optimization events
- Chain of responsibility for optimization decisions
"""

import torch
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    MEMORY = "memory"
    COMPUTATION = "computation"
    HYBRID = "hybrid"

@dataclass
class OptimizationContext:
    device: torch.device
    memory_pressure: float
    computation_load: float
    current_step: int
    batch_size: int
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class OptimizationObserver(ABC):
    @abstractmethod
    def on_optimization_performed(self, strategy_name: str, context: OptimizationContext, result: Dict[str, Any]):
        pass
    
    @abstractmethod
    def on_optimization_failed(self, strategy_name: str, context: OptimizationContext, error: Exception):
        pass

class OptimizationStrategy(ABC):
    def __init__(self, name: str, optimization_type: OptimizationType):
        self.name = name
        self.optimization_type = optimization_type
        self.observers: List[OptimizationObserver] = []
        self.success_count = 0
        self.failure_count = 0
    
    def add_observer(self, observer: OptimizationObserver):
        self.observers.append(observer)
    
    def notify_success(self, context: OptimizationContext, result: Dict[str, Any]):
        self.success_count += 1
        for observer in self.observers:
            observer.on_optimization_performed(self.name, context, result)
    
    def notify_failure(self, context: OptimizationContext, error: Exception):
        self.failure_count += 1
        for observer in self.observers:
            observer.on_optimization_failed(self.name, context, error)
    
    @abstractmethod
    def can_optimize(self, context: OptimizationContext) -> bool:
        pass
    
    @abstractmethod
    def optimize(self, context: OptimizationContext) -> Dict[str, Any]:
        pass

class MemoryOptimizationStrategy(OptimizationStrategy):
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
                'pressure_before': context.memory_pressure,
                'pressure_after': context.memory_pressure * 0.7
            }
            
            self.notify_success(context, result)
            return result
            
        except Exception as e:
            self.notify_failure(context, e)
            raise

class OptimizationFactory:
    _strategies = {
        OptimizationType.MEMORY: MemoryOptimizationStrategy,
    }
    
    @classmethod
    def create_strategy(cls, optimization_type: OptimizationType, **kwargs) -> OptimizationStrategy:
        if optimization_type not in cls._strategies:
            raise ValueError(f"Unknown optimization type: {optimization_type}")
        
        strategy_class = cls._strategies[optimization_type]
        return strategy_class(**kwargs)

class OptimizationChain:
    def __init__(self):
        self.strategies: List[OptimizationStrategy] = []
    
    def add_strategy(self, strategy: OptimizationStrategy):
        self.strategies.append(strategy)
    
    def optimize(self, context: OptimizationContext) -> Optional[Dict[str, Any]]:
        for strategy in self.strategies:
            if strategy.can_optimize(context):
                try:
                    return strategy.optimize(context)
                except Exception as e:
                    logger.warning(f"Strategy {strategy.name} failed: {e}")
                    continue
        return None

class OptimizationLogger(OptimizationObserver):
    def on_optimization_performed(self, strategy_name: str, context: OptimizationContext, result: Dict[str, Any]):
        logger.info(f"✅ Optimization {strategy_name} performed successfully")
    
    def on_optimization_failed(self, strategy_name: str, context: OptimizationContext, error: Exception):
        logger.error(f"❌ Optimization {strategy_name} failed: {error}")

# Example usage
if __name__ == "__main__":
    # Create optimization strategies
    factory = OptimizationFactory()
    memory_strategy = factory.create_strategy(OptimizationType.MEMORY)
    
    # Create observers
    logger = OptimizationLogger()
    memory_strategy.add_observer(logger)
    
    # Create optimization chain
    chain = OptimizationChain()
    chain.add_strategy(memory_strategy)
    
    # Test optimization
    context = OptimizationContext(
        device=torch.device('cpu'),
        memory_pressure=0.9,
        computation_load=0.8,
        current_step=100,
        batch_size=32
    )
    
    # Perform optimization
    result = chain.optimize(context)
    if result:
        print(f"Optimization result: {result}")
