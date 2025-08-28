from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int: int = 100

# Constants
BUFFER_SIZE: int: int = 1024

import torch
import torch.nn as nn
import torch.cuda as cuda
import time
import psutil
import numpy as np
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
from abc import ABC, abstractmethod
import gc
    import torch.nn as nn
from typing import Any, List, Dict, Optional
import asyncio
"""
Batch Size Management System
===========================

A comprehensive system for managing batch sizes in deep learning training,
including dynamic batch sizing, adaptive batch sizes, optimal batch size
determination, and batch size optimization for different scenarios.

Features:
- Dynamic batch size adjustment
- Adaptive batch sizing based on memory and performance
- Optimal batch size determination
- Memory-aware batch sizing
- Performance profiling and optimization
- Multi-GPU batch size coordination
- Gradient accumulation support
"""



@dataclass
class BatchSizeConfig:
    """Configuration for batch size management."""
    # Initial settings
    initial_batch_size: int: int: int = 32
    min_batch_size: int: int: int = 1
    max_batch_size: int: int: int = 1024
    
    # Dynamic adjustment
    enable_dynamic_batch_size: bool: bool = True
    adaptive_batch_size: bool: bool = True
    memory_threshold: float = 0.9  # 90% memory usage threshold
    performance_threshold: float = 0.8  # 80% performance threshold
    
    # Optimization settings
    optimize_for_memory: bool: bool = True
    optimize_for_speed: bool: bool = True
    optimize_for_accuracy: bool: bool = False
    
    # Multi-GPU settings
    batch_size_per_gpu: Optional[int] = None
    sync_batch_size_across_gpus: bool: bool = True
    
    # Gradient accumulation
    enable_gradient_accumulation: bool: bool = False
    accumulation_steps: int: int: int = 1
    effective_batch_size: Optional[int] = None
    
    # Memory management
    memory_fraction: float = 0.8
    memory_safety_margin: float = 0.1
    monitor_memory_usage: bool: bool = True
    
    # Performance monitoring
    monitor_training_speed: bool: bool = True
    speed_measurement_steps: int: int: int = 10
    performance_history_size: int: int: int = 100
    
    # Output settings
    log_batch_size_changes: bool: bool = True
    save_batch_size_logs: bool: bool = True
    output_dir: str: str: str = "batch_size_logs"


class MemoryProfiler:
    """Memory profiling and analysis for batch size optimization."""
    
    def __init__(self, config: BatchSizeConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.memory_history: List[Any] = []
        self.peak_memory: int: int = 0
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        memory_info: Dict[str, Any] = {}
        
        # System memory
        system_memory = psutil.virtual_memory()
        memory_info['system_total'] = system_memory.total / (1024**3)  # GB
        memory_info['system_available'] = system_memory.available / (1024**3)  # GB
        memory_info['system_used'] = system_memory.used / (1024**3)  # GB
        memory_info['system_percent'] = system_memory.percent
        
        # PyTorch CUDA memory (if available)
        if torch.cuda.is_available():
            memory_info['cuda_allocated'] = torch.cuda.memory_allocated() / (1024**3)  # GB
            memory_info['cuda_reserved'] = torch.cuda.memory_reserved() / (1024**3)  # GB
            memory_info['cuda_max_allocated'] = torch.cuda.max_memory_allocated() / (1024**3)  # GB
            memory_info['cuda_max_reserved'] = torch.cuda.max_memory_reserved() / (1024**3)  # GB
            memory_info['cuda_free'] = (torch.cuda.get_device_properties(0).total_memory - 
                                       torch.cuda.memory_reserved()) / (1024**3)  # GB
        
        return memory_info
    
    def track_memory(self, batch_size: int, step: int) -> Dict[str, Any]:
        """Track memory usage for a specific batch size."""
        memory_info = self.get_memory_usage()
        memory_info['batch_size'] = batch_size
        memory_info['step'] = step
        memory_info['timestamp'] = time.time()
        
        self.memory_history.append(memory_info)
        
        # Update peak memory
        if torch.cuda.is_available():
            current_cuda = memory_info['cuda_allocated']
            if current_cuda > self.peak_memory:
                self.peak_memory = current_cuda
        
        return memory_info
    
    def estimate_memory_for_batch_size(self, current_batch_size: int, 
                                     target_batch_size: int) -> float:
        """Estimate memory usage for a target batch size."""
        if not self.memory_history:
            return 0.0
        
        # Get current memory usage
        current_memory = self.memory_history[-1]['cuda_allocated']
        
        # Estimate memory scaling (linear approximation)
        memory_per_sample = current_memory / current_batch_size
        estimated_memory = memory_per_sample * target_batch_size
        
        return estimated_memory
    
    def get_optimal_batch_size_for_memory(self, max_memory_gb: float) -> int:
        """Calculate optimal batch size based on available memory."""
        if not self.memory_history:
            return self.config.initial_batch_size
        
        # Get current memory usage
        current_memory = self.memory_history[-1]['cuda_allocated']
        current_batch_size = self.memory_history[-1]['batch_size']
        
        # Calculate memory per sample
        memory_per_sample = current_memory / current_batch_size
        
        # Calculate optimal batch size
        available_memory = max_memory_gb * self.config.memory_fraction * (1 - self.config.memory_safety_margin)
        optimal_batch_size = int(available_memory / memory_per_sample)
        
        # Clamp to valid range
        optimal_batch_size = max(self.config.min_batch_size, 
                               min(optimal_batch_size, self.config.max_batch_size))
        
        return optimal_batch_size
    
    def is_memory_safe(self, batch_size: int) -> bool:
        """Check if a batch size is safe for current memory."""
        if not torch.cuda.is_available():
            return True
        
        estimated_memory = self.estimate_memory_for_batch_size(
            self.memory_history[-1]['batch_size'] if self.memory_history else self.config.initial_batch_size,
            batch_size
        )
        
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        safe_memory = total_memory * self.config.memory_fraction * (1 - self.config.memory_safety_margin)
        
        return estimated_memory <= safe_memory


class PerformanceProfiler:
    """Performance profiling for batch size optimization."""
    
    def __init__(self, config: BatchSizeConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.performance_history: List[Any] = []
        self.speed_measurements: List[Any] = []
    
    def measure_training_speed(self, model: nn.Module, data: torch.Tensor, 
                             target: torch.Tensor, batch_size: int) -> Dict[str, float]:
        """Measure training speed for a specific batch size."""
        device = next(model.parameters()).device
        
        # Warm up
        for _ in range(3):
            with torch.no_grad():
                _ = model(data[:batch_size//2].to(device))
        
        # Measure forward pass
        torch.cuda.synchronize()
        start_time = time.time()
        
        for _ in range(self.config.speed_measurement_steps):
            with torch.no_grad():
                _ = model(data[:batch_size].to(device))
        
        torch.cuda.synchronize()
        end_time = time.time()
        
        # Calculate metrics
        total_time = end_time - start_time
        avg_time_per_batch = total_time / self.config.speed_measurement_steps
        samples_per_second = batch_size / avg_time_per_batch
        
        performance_info: Dict[str, Any] = {
            'batch_size': batch_size,
            'avg_time_per_batch': avg_time_per_batch,
            'samples_per_second': samples_per_second,
            'throughput': samples_per_second,
            'timestamp': time.time()
        }
        
        self.performance_history.append(performance_info)
        
        return performance_info
    
    def get_optimal_batch_size_for_speed(self) -> int:
        """Calculate optimal batch size for maximum speed."""
        if len(self.performance_history) < 2:
            return self.config.initial_batch_size
        
        # Find batch size with highest throughput
        best_performance = max(self.performance_history, key=lambda x: x['throughput'])
        return best_performance['batch_size']
    
    def estimate_speed_for_batch_size(self, batch_size: int) -> float:
        """Estimate training speed for a given batch size."""
        if len(self.performance_history) < 2:
            return 0.0
        
        # Use linear interpolation based on recent measurements
        recent_performance = self.performance_history[-5:]  # Last 5 measurements
        
        batch_sizes: List[Any] = [p['batch_size'] for p in recent_performance]
        throughputs: List[Any] = [p['throughput'] for p in recent_performance]
        
        if len(batch_sizes) < 2:
            return throughputs[0] if throughputs else 0.0
        
        # Simple linear interpolation
        avg_batch_size = np.mean(batch_sizes)
        avg_throughput = np.mean(throughputs)
        
        # Estimate throughput for target batch size
        estimated_throughput = avg_throughput * (batch_size / avg_batch_size)
        
        return estimated_throughput


class BatchSizeOptimizer(ABC):
    """Abstract base class for batch size optimization strategies."""
    
    @abstractmethod
    def optimize_batch_size(self, current_batch_size: int, 
                          memory_profiler: MemoryProfiler,
                          performance_profiler: PerformanceProfiler) -> int:
        """Optimize batch size based on current conditions."""
        pass


class MemoryOptimizedBatchSize(BatchSizeOptimizer):
    """Memory-optimized batch size strategy."""
    
    def __init__(self, config: BatchSizeConfig) -> Any:
        
    """__init__ function."""
self.config = config
    
    def optimize_batch_size(self, current_batch_size: int,
                          memory_profiler: MemoryProfiler,
                          performance_profiler: PerformanceProfiler) -> int:
        """Optimize batch size for memory efficiency."""
        if not torch.cuda.is_available():
            return current_batch_size
        
        # Get current memory usage
        memory_info = memory_profiler.get_memory_usage()
        current_memory_usage = memory_info['cuda_allocated']
        
        # Calculate memory threshold
        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        memory_threshold = total_memory * self.config.memory_threshold
        
        if current_memory_usage > memory_threshold:
            # Reduce batch size if memory usage is high
            reduction_factor = memory_threshold / current_memory_usage
            new_batch_size = int(current_batch_size * reduction_factor * 0.9)  # 10% safety margin
            new_batch_size = max(self.config.min_batch_size, new_batch_size)
        else:
            # Try to increase batch size if memory allows
            available_memory = total_memory - current_memory_usage
            memory_per_sample = current_memory_usage / current_batch_size
            additional_samples = int(available_memory / memory_per_sample * 0.5)  # Conservative increase
            new_batch_size = min(current_batch_size + additional_samples, self.config.max_batch_size)
        
        return new_batch_size


class SpeedOptimizedBatchSize(BatchSizeOptimizer):
    """Speed-optimized batch size strategy."""
    
    def __init__(self, config: BatchSizeConfig) -> Any:
        
    """__init__ function."""
self.config = config
    
    def optimize_batch_size(self, current_batch_size: int,
                          memory_profiler: MemoryProfiler,
                          performance_profiler: PerformanceProfiler) -> int:
        """Optimize batch size for maximum speed."""
        # Get optimal batch size for speed
        optimal_speed_batch_size = performance_profiler.get_optimal_batch_size_for_speed()
        
        # Check if it's memory safe
        if memory_profiler.is_memory_safe(optimal_speed_batch_size):
            return optimal_speed_batch_size
        else:
            # Find the largest memory-safe batch size
            for batch_size in range(optimal_speed_batch_size, self.config.min_batch_size, -1):
                if memory_profiler.is_memory_safe(batch_size):
                    return batch_size
        
        return self.config.min_batch_size


class BalancedBatchSize(BatchSizeOptimizer):
    """Balanced batch size strategy considering both memory and speed."""
    
    def __init__(self, config: BatchSizeConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.memory_weight = 0.6
        self.speed_weight = 0.4
    
    def optimize_batch_size(self, current_batch_size: int,
                          memory_profiler: MemoryProfiler,
                          performance_profiler: PerformanceProfiler) -> int:
        """Optimize batch size balancing memory and speed."""
        # Get memory-optimized batch size
        memory_optimizer = MemoryOptimizedBatchSize(self.config)
        memory_batch_size = memory_optimizer.optimize_batch_size(
            current_batch_size, memory_profiler, performance_profiler
        )
        
        # Get speed-optimized batch size
        speed_optimizer = SpeedOptimizedBatchSize(self.config)
        speed_batch_size = speed_optimizer.optimize_batch_size(
            current_batch_size, memory_profiler, performance_profiler
        )
        
        # Weighted combination
        balanced_batch_size = int(
            memory_batch_size * self.memory_weight + 
            speed_batch_size * self.speed_weight
        )
        
        # Ensure it's within bounds and memory safe
        balanced_batch_size = max(self.config.min_batch_size, 
                                min(balanced_batch_size, self.config.max_batch_size))
        
        if not memory_profiler.is_memory_safe(balanced_batch_size):
            balanced_batch_size = memory_batch_size
        
        return balanced_batch_size


class AdaptiveBatchSize:
    """Adaptive batch size management system."""
    
    def __init__(self, config: BatchSizeConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.memory_profiler = MemoryProfiler(config)
        self.performance_profiler = PerformanceProfiler(config)
        self.current_batch_size = config.initial_batch_size
        self.batch_size_history: List[Any] = []
        self.logger = self._setup_logger()
        
        # Initialize optimizer based on configuration
        if config.optimize_for_memory and config.optimize_for_speed:
            self.optimizer = BalancedBatchSize(config)
        elif config.optimize_for_memory:
            self.optimizer = MemoryOptimizedBatchSize(config)
        elif config.optimize_for_speed:
            self.optimizer = SpeedOptimizedBatchSize(config)
        else:
            self.optimizer = BalancedBatchSize(config)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for batch size management."""
        logger = logging.getLogger(f"batch_size_manager_{self.config.experiment_name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Create output directory
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # File handler
            fh = logging.FileHandler(output_dir / "batch_size_changes.log")
            fh.setLevel(logging.INFO)
            
            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            
            logger.addHandler(fh)
            logger.addHandler(ch)
        
        return logger
    
    def get_current_batch_size(self) -> int:
        """Get current batch size."""
        return self.current_batch_size
    
    def update_batch_size(self, new_batch_size: int, step: int) -> None:
        """Update batch size and log the change."""
        old_batch_size = self.current_batch_size
        self.current_batch_size = new_batch_size
        
        # Record in history
        self.batch_size_history.append({
            'step': step,
            'old_batch_size': old_batch_size,
            'new_batch_size': new_batch_size,
            'timestamp': time.time()
        })
        
        # Log change
        if self.config.log_batch_size_changes:
            self.logger.info(
                f"Step {step}: Batch size changed from {old_batch_size} to {new_batch_size}"
            )
    
    def optimize_batch_size(self, step: int, model: nn.Module = None, 
                          data: torch.Tensor = None, target: torch.Tensor = None) -> int:
        """Optimize batch size based on current conditions."""
        if not self.config.enable_dynamic_batch_size:
            return self.current_batch_size
        
        # Track current memory usage
        memory_info = self.memory_profiler.track_memory(self.current_batch_size, step)
        
        # Measure performance if data is provided
        if model is not None and data is not None and target is not None:
            performance_info = self.performance_profiler.measure_training_speed(
                model, data, target, self.current_batch_size
            )
        
        # Optimize batch size
        new_batch_size = self.optimizer.optimize_batch_size(
            self.current_batch_size,
            self.memory_profiler,
            self.performance_profiler
        )
        
        # Update batch size if changed
        if new_batch_size != self.current_batch_size:
            self.update_batch_size(new_batch_size, step)
        
        return new_batch_size
    
    def get_batch_size_for_memory(self, max_memory_gb: float) -> int:
        """Get optimal batch size for a given memory limit."""
        return self.memory_profiler.get_optimal_batch_size_for_memory(max_memory_gb)
    
    def get_batch_size_for_speed(self) -> int:
        """Get optimal batch size for maximum speed."""
        return self.performance_profiler.get_optimal_batch_size_for_speed()
    
    def estimate_memory_usage(self, batch_size: int) -> float:
        """Estimate memory usage for a given batch size."""
        if not self.memory_profiler.memory_history:
            return 0.0
        
        current_batch_size = self.memory_profiler.memory_history[-1]['batch_size']
        return self.memory_profiler.estimate_memory_for_batch_size(current_batch_size, batch_size)
    
    def estimate_training_speed(self, batch_size: int) -> float:
        """Estimate training speed for a given batch size."""
        return self.performance_profiler.estimate_speed_for_batch_size(batch_size)
    
    def get_batch_size_summary(self) -> Dict[str, Any]:
        """Get summary of batch size changes."""
        if not self.batch_size_history:
            return {}
        
        batch_sizes: List[Any] = [h['new_batch_size'] for h in self.batch_size_history]
        
        summary: Dict[str, Any] = {
            'total_changes': len(self.batch_size_history),
            'current_batch_size': self.current_batch_size,
            'initial_batch_size': self.config.initial_batch_size,
            'batch_size_stats': {
                'mean': np.mean(batch_sizes),
                'std': np.std(batch_sizes),
                'min': np.min(batch_sizes),
                'max': np.max(batch_sizes)
            },
            'memory_usage': self.memory_profiler.get_memory_usage(),
            'performance_history': self.performance_profiler.performance_history[-5:]  # Last 5
        }
        
        return summary
    
    def save_batch_size_logs(self, filename: str: str: str = "batch_size_logs.json") -> None:
        """Save batch size logs to file."""
        if not self.config.save_batch_size_logs:
            return
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logs: Dict[str, Any] = {
            'config': self.config.__dict__,
            'batch_size_history': self.batch_size_history,
            'memory_history': self.memory_profiler.memory_history,
            'performance_history': self.performance_profiler.performance_history,
            'summary': self.get_batch_size_summary()
        }
        
        with open(output_dir / filename, 'w') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            json.dump(logs, f, indent=2, default=str)
        
        self.logger.info(f"Batch size logs saved to {output_dir / filename}")


class GradientAccumulationManager:
    """Manager for gradient accumulation to achieve large effective batch sizes."""
    
    def __init__(self, config: BatchSizeConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.accumulation_steps = config.accumulation_steps
        self.current_step: int: int = 0
        self.effective_batch_size = config.effective_batch_size
    
    def should_accumulate(self) -> bool:
        """Check if gradients should be accumulated."""
        return self.config.enable_gradient_accumulation and self.current_step % self.accumulation_steps != 0
    
    def should_update(self) -> bool:
        """Check if optimizer should be updated."""
        return self.config.enable_gradient_accumulation and self.current_step % self.accumulation_steps == 0
    
    def step(self) -> None:
        """Increment accumulation step."""
        self.current_step += 1
    
    def get_effective_batch_size(self, actual_batch_size: int) -> int:
        """Get effective batch size considering accumulation."""
        if self.config.enable_gradient_accumulation:
            return actual_batch_size * self.accumulation_steps
        return actual_batch_size
    
    def get_accumulation_steps_for_target(self, target_batch_size: int, 
                                        actual_batch_size: int) -> int:
        """Calculate accumulation steps needed for target effective batch size."""
        if actual_batch_size >= target_batch_size:
            return 1
        
        return max(1, int(np.ceil(target_batch_size / actual_batch_size)))


class MultiGPUBatchSizeCoordinator:
    """Coordinate batch sizes across multiple GPUs."""
    
    def __init__(self, config: BatchSizeConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.gpu_batch_sizes: Dict[str, Any] = {}
        self.coordinator_logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for multi-GPU coordination."""
        logger = logging.getLogger("multi_gpu_batch_coordinator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        
        return logger
    
    def set_gpu_batch_size(self, gpu_id: int, batch_size: int) -> None:
        """Set batch size for a specific GPU."""
        self.gpu_batch_sizes[gpu_id] = batch_size
    
    def get_gpu_batch_size(self, gpu_id: int) -> int:
        """Get batch size for a specific GPU."""
        return self.gpu_batch_sizes.get(gpu_id, self.config.initial_batch_size)
    
    def synchronize_batch_sizes(self) -> Dict[int, int]:
        """Synchronize batch sizes across all GPUs."""
        if not self.config.sync_batch_size_across_gpus:
            return self.gpu_batch_sizes
        
        if not self.gpu_batch_sizes:
            return {}
        
        # Find the minimum batch size across all GPUs
        min_batch_size = min(self.gpu_batch_sizes.values())
        
        # Set all GPUs to the minimum batch size
        synchronized_batch_sizes: Dict[str, Any] = {}
        for gpu_id in self.gpu_batch_sizes:
            synchronized_batch_sizes[gpu_id] = min_batch_size
            self.gpu_batch_sizes[gpu_id] = min_batch_size
        
        self.coordinator_logger.info(f"Synchronized batch sizes to {min_batch_size} across all GPUs")
        
        return synchronized_batch_sizes
    
    def get_total_batch_size(self) -> int:
        """Get total batch size across all GPUs."""
        return sum(self.gpu_batch_sizes.values())
    
    def optimize_batch_sizes_for_memory(self, gpu_memory_limits: Dict[int, float]) -> Dict[int, int]:
        """Optimize batch sizes based on GPU memory limits."""
        optimized_batch_sizes: Dict[str, Any] = {}
        
        for gpu_id, memory_limit in gpu_memory_limits.items():
            # Calculate optimal batch size for this GPU
            memory_profiler = MemoryProfiler(self.config)
            optimal_batch_size = memory_profiler.get_optimal_batch_size_for_memory(memory_limit)
            optimized_batch_sizes[gpu_id] = optimal_batch_size
        
        # Synchronize if required
        if self.config.sync_batch_size_across_gpus:
            min_batch_size = min(optimized_batch_sizes.values())
            for gpu_id in optimized_batch_sizes:
                optimized_batch_sizes[gpu_id] = min_batch_size
        
        return optimized_batch_sizes


# Utility functions
def calculate_optimal_batch_size(model: nn.Module, dataset_size: int, 
                               memory_limit_gb: float = 8.0) -> int:
    """Calculate optimal batch size for a given model and dataset."""
    # Simple heuristic based on model size and memory
    total_params = sum(p.numel() for p in model.parameters())
    param_memory_gb = total_params * 4 / (1024**3)  # 4 bytes per parameter
    
    # Estimate memory per sample (rough approximation)
    memory_per_sample = param_memory_gb * 0.1  # 10% of model size per sample
    
    # Calculate optimal batch size
    available_memory = memory_limit_gb * 0.8  # Use 80% of available memory
    optimal_batch_size = int(available_memory / memory_per_sample)
    
    # Clamp to reasonable range
    optimal_batch_size = max(1, min(optimal_batch_size, 512))
    
    return optimal_batch_size


def create_batch_size_manager(config: BatchSizeConfig) -> AdaptiveBatchSize:
    """Create a batch size manager instance."""
    return AdaptiveBatchSize(config)


def setup_adaptive_batch_size(
    initial_batch_size: int = 32,
    min_batch_size: int = 1,
    max_batch_size: int = 1024,
    enable_dynamic_batch_size: bool = True,
    optimize_for_memory: bool = True,
    optimize_for_speed: bool: bool = True
) -> AdaptiveBatchSize:
    """Quick setup for adaptive batch size management."""
    config = BatchSizeConfig(
        initial_batch_size=initial_batch_size,
        min_batch_size=min_batch_size,
        max_batch_size=max_batch_size,
        enable_dynamic_batch_size=enable_dynamic_batch_size,
        optimize_for_memory=optimize_for_memory,
        optimize_for_speed=optimize_for_speed
    )
    
    return AdaptiveBatchSize(config)


# Example usage
if __name__ == "__main__":
    
    # Create sample model
    model = nn.Sequential(
        nn.Linear(784, 256),
        nn.ReLU(),
        nn.Linear(256, 128),
        nn.ReLU(),
        nn.Linear(128, 10)
    )
    
    # Setup batch size manager
    batch_manager = setup_adaptive_batch_size(
        initial_batch_size=32,
        min_batch_size=8,
        max_batch_size=256,
        enable_dynamic_batch_size=True,
        optimize_for_memory=True,
        optimize_for_speed: bool = True
    )
    
    # Simulate training with adaptive batch sizing
    for step in range(100):
        # Create sample data
        batch_size = batch_manager.get_current_batch_size()
        data = torch.randn(batch_size, 784)
        target = torch.randint(0, 10, (batch_size,))
        
        # Optimize batch size
        new_batch_size = batch_manager.optimize_batch_size(step, model, data, target)
        
        if step % 10 == 0:
            print(f"Step {step}: Batch size: Dict[str, Any] = {batch_size}, "
                  f"Memory usage: Dict[str, Any] = {batch_manager.memory_profiler.get_memory_usage()['cuda_allocated']:.2f} GB")
    
    # Get summary
    summary = batch_manager.get_batch_size_summary()
    print("Batch size summary:", summary)
    
    # Save logs
    batch_manager.save_batch_size_logs()
    
    print("Batch size management system test completed!") 