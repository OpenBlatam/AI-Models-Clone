"""
Performance Optimization System

Comprehensive performance optimization for the email sequence training pipeline
including memory optimization, computational efficiency, and training acceleration.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
from torch.nn.parallel import DataParallel, DistributedDataParallel
import torch.distributed as dist
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import time
import psutil
import GPUtil
import gc
import os
from pathlib import Path
import json
import numpy as np
from dataclasses import dataclass
from contextlib import contextmanager
import warnings

from core.training_logger import TrainingLogger, TrainingEventType, LogLevel
from core.error_handling import ErrorHandler, ModelError


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization"""
    
    # Memory optimization
    enable_mixed_precision: bool = True
    enable_gradient_checkpointing: bool = False
    enable_memory_efficient_attention: bool = True
    enable_activation_checkpointing: bool = False
    max_memory_usage: float = 0.8  # 80% of available memory
    
    # Computational optimization
    enable_compile: bool = True
    enable_torch_optimization: bool = True
    enable_cudnn_benchmark: bool = True
    enable_cudnn_deterministic: bool = False
    
    # Data loading optimization
    num_workers: int = 4
    pin_memory: bool = True
    persistent_workers: bool = True
    prefetch_factor: int = 2
    
    # Training optimization
    enable_gradient_accumulation: bool = True
    gradient_accumulation_steps: int = 4
    enable_dynamic_batching: bool = True
    enable_adaptive_learning_rate: bool = True
    
    # Distributed training
    enable_distributed: bool = False
    backend: str = "nccl"
    init_method: str = "env://"
    
    # Monitoring
    enable_performance_monitoring: bool = True
    performance_log_interval: int = 100
    
    # Advanced optimizations
    enable_amp_optimization: bool = True
    enable_fused_optimizers: bool = True
    enable_quantization: bool = False
    enable_pruning: bool = False


class PerformanceMonitor:
    """Performance monitoring and analysis"""
    
    def __init__(self, logger: Optional[TrainingLogger] = None):
        self.logger = logger
        self.performance_metrics = {
            "memory_usage": [],
            "gpu_usage": [],
            "training_time": [],
            "throughput": [],
            "efficiency": []
        }
        self.start_time = None
        self.batch_count = 0
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.batch_count = 0
    
    def record_metrics(self, batch_size: int, training_time: float):
        """Record performance metrics"""
        
        # Memory usage
        memory_usage = psutil.virtual_memory().percent / 100.0
        
        # GPU usage
        gpu_usage = 0.0
        if torch.cuda.is_available():
            gpu_usage = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
        
        # Throughput (samples per second)
        throughput = batch_size / training_time if training_time > 0 else 0
        
        # Efficiency (throughput per GPU memory usage)
        efficiency = throughput / (gpu_usage + 1e-8)
        
        # Store metrics
        self.performance_metrics["memory_usage"].append(memory_usage)
        self.performance_metrics["gpu_usage"].append(gpu_usage)
        self.performance_metrics["training_time"].append(training_time)
        self.performance_metrics["throughput"].append(throughput)
        self.performance_metrics["efficiency"].append(efficiency)
        
        self.batch_count += 1
        
        # Log metrics periodically
        if self.logger and self.batch_count % 100 == 0:
            self.logger.log_info(
                f"Performance - Throughput: {throughput:.2f} samples/s, "
                f"GPU Usage: {gpu_usage:.2%}, Memory: {memory_usage:.2%}"
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        
        if not self.performance_metrics["training_time"]:
            return {}
        
        summary = {}
        for metric_name, values in self.performance_metrics.items():
            if values:
                summary[f"{metric_name}_mean"] = np.mean(values)
                summary[f"{metric_name}_max"] = np.max(values)
                summary[f"{metric_name}_min"] = np.min(values)
                summary[f"{metric_name}_std"] = np.std(values)
        
        # Overall statistics
        total_time = time.time() - self.start_time if self.start_time else 0
        summary["total_training_time"] = total_time
        summary["total_batches"] = self.batch_count
        summary["average_batch_time"] = total_time / self.batch_count if self.batch_count > 0 else 0
        
        return summary


class MemoryOptimizer:
    """Memory optimization utilities"""
    
    def __init__(self, config: PerformanceConfig, logger: Optional[TrainingLogger] = None):
        self.config = config
        self.logger = logger
        self.scaler = GradScaler() if config.enable_amp_optimization else None
    
    def optimize_model_memory(self, model: nn.Module) -> nn.Module:
        """Apply memory optimizations to model"""
        
        try:
            # Enable gradient checkpointing if configured
            if self.config.enable_gradient_checkpointing:
                model = self._apply_gradient_checkpointing(model)
            
            # Enable activation checkpointing if configured
            if self.config.enable_activation_checkpointing:
                model = self._apply_activation_checkpointing(model)
            
            # Enable memory efficient attention if available
            if self.config.enable_memory_efficient_attention:
                model = self._apply_memory_efficient_attention(model)
            
            # Compile model if enabled
            if self.config.enable_compile and hasattr(torch, 'compile'):
                model = torch.compile(model)
            
            if self.logger:
                self.logger.log_info("Memory optimizations applied to model")
            
            return model
            
        except Exception as e:
            if self.logger:
                self.logger.log_error(e, "Memory optimization", "optimize_model_memory")
            return model
    
    def _apply_gradient_checkpointing(self, model: nn.Module) -> nn.Module:
        """Apply gradient checkpointing to model"""
        
        # Apply to transformer layers if they exist
        for module in model.modules():
            if hasattr(module, 'gradient_checkpointing'):
                module.gradient_checkpointing = True
        
        return model
    
    def _apply_activation_checkpointing(self, model: nn.Module) -> nn.Module:
        """Apply activation checkpointing to model"""
        
        # This would be implemented based on specific model architecture
        # For now, we'll use a generic approach
        return model
    
    def _apply_memory_efficient_attention(self, model: nn.Module) -> nn.Module:
        """Apply memory efficient attention if available"""
        
        # Check if memory efficient attention is available
        try:
            from transformers.models.bert.modeling_bert import BertSelfAttention
            # Apply memory efficient attention to attention layers
            for module in model.modules():
                if isinstance(module, BertSelfAttention):
                    module.use_memory_efficient_attention = True
        except ImportError:
            pass
        
        return model
    
    @contextmanager
    def mixed_precision_context(self):
        """Mixed precision training context"""
        
        if not self.config.enable_mixed_precision:
            yield
            return
        
        try:
            with autocast():
                yield
        except Exception as e:
            if self.logger:
                self.logger.log_error(e, "Mixed precision", "mixed_precision_context")
            yield
    
    def optimize_gradients(self, loss: torch.Tensor, optimizer: optim.Optimizer):
        """Optimize gradient computation"""
        
        if self.config.enable_amp_optimization and self.scaler:
            # Scale loss for mixed precision
            scaled_loss = self.scaler.scale(loss)
            scaled_loss.backward()
            
            # Unscale gradients
            self.scaler.unscale_(optimizer)
            
            # Step optimizer
            self.scaler.step(optimizer)
            self.scaler.update()
        else:
            # Standard backward pass
            loss.backward()
            optimizer.step()
    
    def clear_memory(self):
        """Clear memory and garbage collect"""
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        gc.collect()
        
        if self.logger:
            self.logger.log_info("Memory cleared")


class DataLoaderOptimizer:
    """DataLoader optimization utilities"""
    
    def __init__(self, config: PerformanceConfig, logger: Optional[TrainingLogger] = None):
        self.config = config
        self.logger = logger
    
    def optimize_dataloader(self, dataloader: DataLoader) -> DataLoader:
        """Optimize DataLoader for performance"""
        
        try:
            # Update DataLoader with optimized settings
            dataloader.num_workers = self.config.num_workers
            dataloader.pin_memory = self.config.pin_memory
            dataloader.persistent_workers = self.config.persistent_workers
            dataloader.prefetch_factor = self.config.prefetch_factor
            
            if self.logger:
                self.logger.log_info(f"DataLoader optimized with {self.config.num_workers} workers")
            
            return dataloader
            
        except Exception as e:
            if self.logger:
                self.logger.log_error(e, "DataLoader optimization", "optimize_dataloader")
            return dataloader
    
    def create_optimized_dataloader(
        self,
        dataset,
        batch_size: int,
        shuffle: bool = True,
        **kwargs
    ) -> DataLoader:
        """Create an optimized DataLoader"""
        
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=self.config.num_workers,
            pin_memory=self.config.pin_memory,
            persistent_workers=self.config.persistent_workers,
            prefetch_factor=self.config.prefetch_factor,
            **kwargs
        )


class ComputationalOptimizer:
    """Computational optimization utilities"""
    
    def __init__(self, config: PerformanceConfig, logger: Optional[TrainingLogger] = None):
        self.config = config
        self.logger = logger
        self._apply_torch_optimizations()
    
    def _apply_torch_optimizations(self):
        """Apply PyTorch optimizations"""
        
        try:
            if self.config.enable_torch_optimization:
                # Enable optimizations
                torch.backends.cudnn.benchmark = self.config.enable_cudnn_benchmark
                torch.backends.cudnn.deterministic = self.config.enable_cudnn_deterministic
                
                # Set number of threads
                torch.set_num_threads(min(8, os.cpu_count() or 1))
                
                if self.logger:
                    self.logger.log_info("PyTorch optimizations applied")
                    
        except Exception as e:
            if self.logger:
                self.logger.log_error(e, "PyTorch optimization", "apply_torch_optimizations")
    
    def optimize_optimizer(self, optimizer: optim.Optimizer) -> optim.Optimizer:
        """Optimize optimizer for better performance"""
        
        try:
            if self.config.enable_fused_optimizers:
                # Use fused optimizers if available
                if isinstance(optimizer, optim.AdamW):
                    # AdamW is already optimized
                    pass
                elif isinstance(optimizer, optim.Adam):
                    # Consider switching to AdamW
                    if self.logger:
                        self.logger.log_info("Consider using AdamW for better performance")
            
            return optimizer
            
        except Exception as e:
            if self.logger:
                self.logger.log_error(e, "Optimizer optimization", "optimize_optimizer")
            return optimizer
    
    def enable_quantization(self, model: nn.Module) -> nn.Module:
        """Enable model quantization for inference"""
        
        if not self.config.enable_quantization:
            return model
        
        try:
            # Dynamic quantization for better performance
            model = torch.quantization.quantize_dynamic(
                model, {nn.Linear}, dtype=torch.qint8
            )
            
            if self.logger:
                self.logger.log_info("Model quantization applied")
            
            return model
            
        except Exception as e:
            if self.logger:
                self.logger.log_error(e, "Quantization", "enable_quantization")
            return model


class DistributedOptimizer:
    """Distributed training optimization"""
    
    def __init__(self, config: PerformanceConfig, logger: Optional[TrainingLogger] = None):
        self.config = config
        self.logger = logger
        self.is_distributed = False
    
    def setup_distributed_training(self, rank: int = -1, world_size: int = -1):
        """Setup distributed training"""
        
        if not self.config.enable_distributed:
            return
        
        try:
            if rank >= 0 and world_size > 0:
                # Initialize process group
                dist.init_process_group(
                    backend=self.config.backend,
                    init_method=self.config.init_method,
                    rank=rank,
                    world_size=world_size
                )
                self.is_distributed = True
                
                if self.logger:
                    self.logger.log_info(f"Distributed training initialized (rank {rank}/{world_size})")
                    
        except Exception as e:
            if self.logger:
                self.logger.log_error(e, "Distributed setup", "setup_distributed_training")
    
    def wrap_model(self, model: nn.Module, device_ids: List[int] = None) -> nn.Module:
        """Wrap model for distributed training"""
        
        if not self.is_distributed:
            # Use DataParallel for single machine multi-GPU
            if torch.cuda.device_count() > 1 and device_ids:
                model = DataParallel(model, device_ids=device_ids)
                if self.logger:
                    self.logger.log_info(f"DataParallel applied to {len(device_ids)} GPUs")
            return model
        
        # Use DistributedDataParallel for distributed training
        model = DistributedDataParallel(model)
        if self.logger:
            self.logger.log_info("DistributedDataParallel applied")
        
        return model
    
    def cleanup(self):
        """Cleanup distributed training"""
        
        if self.is_distributed:
            dist.destroy_process_group()
            self.is_distributed = False


class PerformanceOptimizer:
    """Main performance optimizer class"""
    
    def __init__(
        self,
        config: PerformanceConfig,
        logger: Optional[TrainingLogger] = None,
        device: str = "auto"
    ):
        self.config = config
        self.logger = logger
        
        # Setup device
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # Initialize components
        self.memory_optimizer = MemoryOptimizer(config, logger)
        self.data_optimizer = DataLoaderOptimizer(config, logger)
        self.comp_optimizer = ComputationalOptimizer(config, logger)
        self.dist_optimizer = DistributedOptimizer(config, logger)
        self.monitor = PerformanceMonitor(logger)
        
        if self.logger:
            self.logger.log_info(f"Performance optimizer initialized on {self.device}")
    
    def optimize_model(self, model: nn.Module) -> nn.Module:
        """Apply all optimizations to model"""
        
        try:
            # Move model to device
            model = model.to(self.device)
            
            # Apply memory optimizations
            model = self.memory_optimizer.optimize_model_memory(model)
            
            # Apply quantization if enabled
            model = self.comp_optimizer.enable_quantization(model)
            
            # Wrap for distributed training
            if torch.cuda.is_available():
                device_ids = list(range(torch.cuda.device_count()))
                model = self.dist_optimizer.wrap_model(model, device_ids)
            
            if self.logger:
                self.logger.log_info("Model optimization completed")
            
            return model
            
        except Exception as e:
            if self.logger:
                self.logger.log_error(e, "Model optimization", "optimize_model")
            return model
    
    def optimize_dataloader(self, dataloader: DataLoader) -> DataLoader:
        """Optimize DataLoader"""
        
        return self.data_optimizer.optimize_dataloader(dataloader)
    
    def optimize_optimizer(self, optimizer: optim.Optimizer) -> optim.Optimizer:
        """Optimize optimizer"""
        
        return self.comp_optimizer.optimize_optimizer(optimizer)
    
    def setup_distributed(self, rank: int = -1, world_size: int = -1):
        """Setup distributed training"""
        
        self.dist_optimizer.setup_distributed_training(rank, world_size)
    
    def start_monitoring(self):
        """Start performance monitoring"""
        
        self.monitor.start_monitoring()
    
    def record_performance(self, batch_size: int, training_time: float):
        """Record performance metrics"""
        
        self.monitor.record_metrics(batch_size, training_time)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        
        return self.monitor.get_performance_summary()
    
    @contextmanager
    def optimization_context(self):
        """Context manager for optimization"""
        
        try:
            yield self
        finally:
            # Cleanup
            self.memory_optimizer.clear_memory()
            if self.dist_optimizer.is_distributed:
                self.dist_optimizer.cleanup()
    
    def optimize_training_step(
        self,
        model: nn.Module,
        inputs: torch.Tensor,
        targets: torch.Tensor,
        loss_fn: Callable,
        optimizer: optim.Optimizer
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Optimized training step"""
        
        start_time = time.time()
        
        try:
            # Mixed precision context
            with self.memory_optimizer.mixed_precision_context():
                # Forward pass
                outputs = model(inputs)
                loss = loss_fn(outputs, targets)
                
                # Optimized backward pass
                self.memory_optimizer.optimize_gradients(loss, optimizer)
            
            # Record performance
            training_time = time.time() - start_time
            batch_size = inputs.size(0)
            self.record_performance(batch_size, training_time)
            
            # Calculate metrics
            metrics = {
                "loss": loss.item(),
                "training_time": training_time,
                "batch_size": batch_size
            }
            
            return loss, metrics
            
        except Exception as e:
            if self.logger:
                self.logger.log_error(e, "Optimized training step", "optimize_training_step")
            raise
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        
        recommendations = []
        
        # Check memory usage
        if torch.cuda.is_available():
            memory_usage = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
            if memory_usage > 0.8:
                recommendations.append("Consider enabling gradient checkpointing to reduce memory usage")
        
        # Check if mixed precision is enabled
        if not self.config.enable_mixed_precision:
            recommendations.append("Enable mixed precision training for better performance")
        
        # Check number of workers
        if self.config.num_workers < 4:
            recommendations.append("Increase number of DataLoader workers for better I/O performance")
        
        # Check if compilation is enabled
        if not self.config.enable_compile and hasattr(torch, 'compile'):
            recommendations.append("Enable torch.compile for better performance")
        
        return recommendations


# Utility functions
def create_performance_optimizer(
    logger: Optional[TrainingLogger] = None,
    device: str = "auto",
    **config_kwargs
) -> PerformanceOptimizer:
    """Create a performance optimizer with default settings"""
    
    config = PerformanceConfig(**config_kwargs)
    return PerformanceOptimizer(config, logger, device)


def get_optimal_batch_size(
    model: nn.Module,
    input_size: Tuple[int, ...],
    target_memory_usage: float = 0.8
) -> int:
    """Find optimal batch size for given memory constraints"""
    
    if not torch.cuda.is_available():
        return 32  # Default for CPU
    
    # Start with a small batch size
    batch_size = 1
    max_batch_size = 1024
    
    while batch_size <= max_batch_size:
        try:
            # Create dummy inputs
            inputs = torch.randn(batch_size, *input_size).cuda()
            targets = torch.randint(0, 2, (batch_size,)).cuda()
            
            # Forward pass
            with torch.no_grad():
                outputs = model(inputs)
            
            # Check memory usage
            memory_usage = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
            
            if memory_usage > target_memory_usage:
                break
            
            batch_size *= 2
            
        except RuntimeError:
            # Out of memory
            break
        finally:
            # Clear memory
            torch.cuda.empty_cache()
    
    return max(1, batch_size // 2)


def benchmark_model_performance(
    model: nn.Module,
    dataloader: DataLoader,
    num_iterations: int = 100
) -> Dict[str, float]:
    """Benchmark model performance"""
    
    model.eval()
    device = next(model.parameters()).device
    
    total_time = 0.0
    total_samples = 0
    
    with torch.no_grad():
        for i, (inputs, targets) in enumerate(dataloader):
            if i >= num_iterations:
                break
            
            inputs = inputs.to(device)
            targets = targets.to(device)
            
            start_time = time.time()
            outputs = model(inputs)
            end_time = time.time()
            
            total_time += end_time - start_time
            total_samples += inputs.size(0)
    
    throughput = total_samples / total_time if total_time > 0 else 0
    
    return {
        "throughput": throughput,
        "avg_batch_time": total_time / num_iterations if num_iterations > 0 else 0,
        "total_samples": total_samples,
        "total_time": total_time
    }


if __name__ == "__main__":
    # Example usage
    import torch.nn as nn
    
    # Simple model for testing
    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = nn.Linear(10, 2)
        
        def forward(self, x):
            return self.linear(x)
    
    # Create performance optimizer
    optimizer = create_performance_optimizer(
        enable_mixed_precision=True,
        enable_compile=True,
        num_workers=4
    )
    
    # Create model and optimize
    model = TestModel()
    model = optimizer.optimize_model(model)
    
    # Get optimal batch size
    optimal_batch_size = get_optimal_batch_size(model, (10,))
    print(f"Optimal batch size: {optimal_batch_size}")
    
    # Benchmark performance
    from torch.utils.data import DataLoader, TensorDataset
    
    dataset = TensorDataset(torch.randn(1000, 10), torch.randint(0, 2, (1000,)))
    dataloader = DataLoader(dataset, batch_size=32)
    
    benchmark_results = benchmark_model_performance(model, dataloader)
    print(f"Benchmark results: {benchmark_results}")
    
    # Get optimization recommendations
    recommendations = optimizer.get_optimization_recommendations()
    print(f"Optimization recommendations: {recommendations}") 