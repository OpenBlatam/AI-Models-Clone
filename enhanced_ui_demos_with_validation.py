"""
🎨 Enhanced UI Interactive Gradio Demos with Comprehensive Error Handling & Validation
====================================================================================

Advanced user interface design with comprehensive error handling and input validation:
- Modern, intuitive design
- Enhanced visual hierarchy
- Interactive elements and animations
- Responsive layouts
- Professional appearance
- Robust error handling with try-except blocks
- Comprehensive input validation
- User feedback systems
- Data loading error handling
- Model inference error handling
- Multi-GPU training with DataParallel and DistributedDataParallel
"""

import gradio as gr
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.distributed as dist
import torch.multiprocessing as mp
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import logging
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json
import re
from pathlib import Path
import os
import gc
import psutil
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
import logging
import time
import os
import gc
import psutil
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import queue
import weakref
import functools
import pickle
import hashlib
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gradio_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Check for GPU availability
try:
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    NUM_GPUS = torch.cuda.device_count() if torch.cuda.is_available() else 0
    logger.info(f"Using device: {DEVICE}")
    logger.info(f"Number of GPUs available: {NUM_GPUS}")
except Exception as e:
    logger.warning(f"Failed to detect device, using CPU: {e}")
    DEVICE = torch.device("cpu")
    NUM_GPUS = 0

@dataclass
class MultiGPUConfig:
    """Configuration for multi-GPU training."""
    
    # Training mode
    training_mode: str = "auto"  # "auto", "single_gpu", "data_parallel", "distributed"
    
    # DataParallel settings
    enable_data_parallel: bool = True
    device_ids: Optional[List[int]] = None  # None for all available GPUs
    
    # Distributed settings
    enable_distributed: bool = False
    backend: str = "nccl"  # "nccl" for GPU, "gloo" for CPU
    init_method: str = "env://"
    world_size: int = -1
    rank: int = -1
    local_rank: int = -1
    
    # Communication settings
    find_unused_parameters: bool = False
    broadcast_buffers: bool = True
    bucket_cap_mb: int = 25
    static_graph: bool = False
    
    # Performance settings
    enable_gradient_as_bucket_view: bool = False
    enable_find_unused_parameters: bool = False
    
    # Monitoring
    enable_gpu_monitoring: bool = True
    sync_bn: bool = False  # Synchronize batch normalization
    
    # Training settings
    batch_size_per_gpu: int = 32
    num_epochs: int = 10
    learning_rate: float = 1e-4
    gradient_accumulation_steps: int = 1
    use_mixed_precision: bool = True
    
    # Memory settings
    pin_memory: bool = True
    num_workers: int = 4
    persistent_workers: bool = True
    prefetch_factor: int = 2

@dataclass
class ValidationConfig:
    """Configuration for input validation."""
    
    # Input validation settings
    max_input_size: int = 1000
    max_batch_size: int = 512
    max_noise_level: float = 5.0
    min_confidence_threshold: float = 0.1
    max_processing_time: float = 30.0  # seconds
    
    # Error handling settings
    show_detailed_errors: bool = False
    log_all_errors: bool = True
    graceful_degradation: bool = True
    retry_failed_operations: bool = True
    max_retry_attempts: int = 3
    
    # User feedback settings
    show_success_messages: bool = True
    show_warning_messages: bool = True
    show_error_messages: bool = True
    auto_clear_messages: bool = True
    message_display_time: int = 5  # seconds

@dataclass
class PyTorchDebugConfig:
    """Configuration for PyTorch debugging tools."""
    
    # Autograd debugging
    enable_autograd_anomaly_detection: bool = True
    enable_autograd_profiler: bool = False
    enable_memory_profiling: bool = True
    
    # Gradient debugging
    enable_gradient_checking: bool = True
    enable_gradient_clipping: bool = True
    max_gradient_norm: float = 1.0
    
    # Model debugging
    enable_model_parameter_tracking: bool = True
    enable_activation_monitoring: bool = False
    enable_weight_gradient_monitoring: bool = True
    
    # Performance debugging
    enable_cuda_memory_tracking: bool = True
    enable_operation_timing: bool = True
    enable_memory_leak_detection: bool = False
    
    # Debug verbosity
    debug_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_gradients: bool = False
    log_activations: bool = False

@dataclass
class EnhancedUIConfig:
    """Configuration for enhanced UI demos."""
    
    # UI settings
    theme: str = "Soft"
    primary_color: str = "#667eea"
    secondary_color: str = "#764ba2"
    accent_color: str = "#f093fb"
    success_color: str = "#4facfe"
    warning_color: str = "#ff9a9e"
    error_color: str = "#e74c3c"
    
    # Layout settings
    max_width: str = "1400px"
    card_radius: str = "16px"
    shadow: str = "0 8px 32px rgba(0, 0, 0, 0.1)"
    
    # Animation settings
    enable_animations: bool = True
    transition_duration: str = "0.3s"

@dataclass
class PerformanceConfig:
    """Configuration for performance optimization features."""
    # Memory management
    enable_memory_optimization: bool = True
    max_memory_usage_mb: float = 2048.0
    enable_garbage_collection: bool = True
    memory_cleanup_threshold: float = 0.8
    
    # Batch processing
    enable_batch_processing: bool = True
    default_batch_size: int = 32
    max_batch_size: int = 128
    enable_parallel_processing: bool = True
    max_workers: int = 4
    
    # Model optimization
    enable_model_optimization: bool = True
    enable_mixed_precision: bool = True
    enable_torch_compile: bool = False
    enable_quantization: bool = False
    enable_pruning: bool = False
    
    # Performance monitoring
    enable_performance_monitoring: bool = True
    performance_history_size: int = 1000
    enable_real_time_monitoring: bool = True
    monitoring_interval: float = 1.0
    
    # Caching
    enable_caching: bool = True
    cache_size_limit: int = 100
    cache_ttl_seconds: int = 3600
    enable_disk_caching: bool = False
    cache_directory: str = "./cache"
    
    # Advanced optimization
    enable_async_processing: bool = True
    enable_prefetching: bool = True
    enable_dynamic_batching: bool = True
    enable_memory_pooling: bool = True

@dataclass
class ProfilingConfig:
    """Configuration for comprehensive code profiling and bottleneck detection."""
    
    # General profiling
    enable_profiling: bool = True
    enable_detailed_profiling: bool = True
    profiling_output_dir: str = "./profiling_results"
    
    # Data loading profiling
    enable_data_loading_profiling: bool = True
    profile_data_preprocessing: bool = True
    profile_data_augmentation: bool = True
    profile_data_transfer: bool = True
    
    # Model profiling
    enable_model_profiling: bool = True
    profile_forward_pass: bool = True
    profile_backward_pass: bool = True
    profile_memory_usage: bool = True
    
    # Performance profiling
    enable_performance_profiling: bool = True
    profile_cpu_usage: bool = True
    profile_gpu_usage: bool = True
    profile_io_operations: bool = True
    
    # Advanced profiling
    enable_memory_profiling: bool = True
    enable_timing_profiling: bool = True
    enable_bottleneck_detection: bool = True
    enable_optimization_suggestions: bool = True
    
    # Profiling intervals
    profiling_interval: float = 0.1  # seconds
    memory_profiling_interval: float = 1.0  # seconds
    detailed_profiling_threshold: float = 0.1  # seconds (only profile operations taking longer than this)

class MultiGPUTrainer:
    """Comprehensive multi-GPU training utilities for DataParallel and DistributedDataParallel."""
    
    def __init__(self, config: MultiGPUConfig):
        """Initialize multi-GPU trainer.
        
        Args:
            config: Multi-GPU configuration
        """
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
        self.is_distributed = False
        self.is_data_parallel = False
        
        # Auto-detect training mode if not specified
        if self.config.training_mode == "auto":
            self._auto_detect_training_mode()
        
        logger.info(f"Multi-GPU Trainer initialized with {self.gpu_count} GPUs")
        logger.info(f"Training mode: {self.config.training_mode}")
    
    def _auto_detect_training_mode(self):
        """Automatically detect the best training mode based on available resources."""
        if self.gpu_count <= 1:
            self.config.training_mode = "single_gpu"
            self.config.enable_data_parallel = False
            self.config.enable_distributed = False
        elif self.gpu_count <= 4:
            self.config.training_mode = "data_parallel"
            self.config.enable_data_parallel = True
            self.config.enable_distributed = False
        else:
            self.config.training_mode = "distributed"
            self.config.enable_data_parallel = False
            self.config.enable_distributed = True
        
        logger.info(f"Auto-detected training mode: {self.config.training_mode}")
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get comprehensive GPU information."""
        try:
            gpu_info = {
                'cuda_available': torch.cuda.is_available(),
                'gpu_count': self.gpu_count,
                'current_device': torch.cuda.current_device() if torch.cuda.is_available() else None,
                'device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                'memory_info': {}
            }
            
            if torch.cuda.is_available():
                for i in range(self.gpu_count):
                    memory_allocated = torch.cuda.memory_allocated(i) / 1024**3  # GB
                    memory_reserved = torch.cuda.memory_reserved(i) / 1024**3  # GB
                    memory_total = torch.cuda.get_device_properties(i).total_memory / 1024**3  # GB
                    
                    gpu_info['memory_info'][f'gpu_{i}'] = {
                        'allocated_gb': round(memory_allocated, 2),
                        'reserved_gb': round(memory_reserved, 2),
                        'total_gb': round(memory_total, 2),
                        'utilization_percent': round((memory_allocated / memory_total) * 100, 1)
                    }
            
            return gpu_info
        except Exception as e:
            logger.error(f"Failed to get GPU info: {e}")
            return {'error': str(e)}
    
    def setup_data_parallel(self, model: nn.Module, device_ids: Optional[List[int]] = None) -> Tuple[nn.Module, bool]:
        """Setup DataParallel training.
        
        Args:
            model: PyTorch model to wrap
            device_ids: List of GPU device IDs to use
            
        Returns:
            Tuple of (wrapped_model, success_status)
        """
        try:
            if not torch.cuda.is_available() or self.gpu_count < 2:
                logger.warning("DataParallel requires at least 2 GPUs")
                return model, False
            
            if device_ids is None:
                device_ids = list(range(self.gpu_count))
            
            # Validate device IDs
            if not all(0 <= gpu_id < self.gpu_count for gpu_id in device_ids):
                logger.error(f"Invalid device IDs: {device_ids}")
                return model, False
            
            # Wrap model with DataParallel
            wrapped_model = torch.nn.DataParallel(
                model,
                device_ids=device_ids,
                output_device=device_ids[0],
                dim=0
            )
            
            self.is_data_parallel = True
            logger.info(f"DataParallel setup completed with devices: {device_ids}")
            return wrapped_model, True
            
        except Exception as e:
            logger.error(f"Failed to setup DataParallel: {e}")
            return model, False
    
    def setup_distributed_data_parallel(self, model: nn.Module, 
                                      backend: str = 'nccl',
                                      init_method: str = 'env://',
                                      world_size: int = None,
                                      rank: int = None,
                                      device_ids: List[int] = None) -> Tuple[nn.Module, bool]:
        """Setup DistributedDataParallel training.
        
        Args:
            model: PyTorch model to wrap
            backend: Communication backend ('nccl' for GPU, 'gloo' for CPU)
            init_method: Process group initialization method
            world_size: Total number of processes
            rank: Process rank
            device_ids: List of GPU device IDs to use
            
        Returns:
            Tuple of (wrapped_model, success_status)
        """
        try:
            if not torch.cuda.is_available() or self.gpu_count < 2:
                logger.warning("DistributedDataParallel requires at least 2 GPUs")
                world_size = self.gpu_count
            if rank is None:
                rank = 0
            if device_ids is None:
                device_ids = [rank]
            
            # Initialize process group if not already initialized
            if not dist.is_initialized():
                dist.init_process_group(
                    backend=backend,
                    init_method=init_method,
                    world_size=world_size,
                    rank=rank
                )
                logger.info(f"Process group initialized: backend={backend}, world_size={world_size}, rank={rank}")
            
            # Set device for current process
            torch.cuda.set_device(device_ids[0])
            model = model.to(f'cuda:{device_ids[0]}')
            
            # Wrap model with DistributedDataParallel
            wrapped_model = torch.nn.parallel.DistributedDataParallel(
                model,
                device_ids=device_ids,
                output_device=device_ids[0],
                find_unused_parameters=self.config.find_unused_parameters,
                broadcast_buffers=self.config.broadcast_buffers,
                bucket_cap_mb=self.config.bucket_cap_mb,
                static_graph=self.config.static_graph,
                gradient_as_bucket_view=self.config.enable_gradient_as_bucket_view
            )
            
            self.is_distributed = True
            logger.info(f"DistributedDataParallel setup completed with devices: {device_ids}")
            return wrapped_model, True
            
        except Exception as e:
            logger.error(f"Failed to setup DistributedDataParallel: {e}")
            return model, False
    
    def setup_multi_gpu(self, model: nn.Module, 
                       strategy: str = 'auto',
                       device_ids: List[int] = None,
                       ddp_backend: str = 'nccl',
                       ddp_init_method: str = 'env://') -> Tuple[nn.Module, bool, Dict[str, Any]]:
        """Setup multi-GPU training with automatic strategy selection.
        
        Args:
            model: PyTorch model to wrap
            strategy: Training strategy ('auto', 'DataParallel', 'DistributedDataParallel')
            device_ids: List of GPU device IDs to use
            ddp_backend: DistributedDataParallel backend
            ddp_init_method: DistributedDataParallel initialization method
            
        Returns:
            Tuple of (wrapped_model, success_status, gpu_info)
        """
        try:
            gpu_info = self.get_gpu_info()
            
            if not gpu_info['cuda_available'] or gpu_info['gpu_count'] < 2:
                logger.warning("Multi-GPU training not available")
                return model, False, gpu_info
            
            # Auto-select strategy if not specified
            if strategy == 'auto':
                if gpu_info['gpu_count'] <= 4:
                    strategy = 'DataParallel'  # Better for small number of GPUs
                else:
                    strategy = 'DistributedDataParallel'  # Better for large number of GPUs
            
            setup_success = False
            
            if strategy.lower() == 'dataparallel':
                model, setup_success = self.setup_data_parallel(model, device_ids)
            elif strategy.lower() in ['distributeddataparallel', 'ddp']:
                model, setup_success = self.setup_distributed_data_parallel(
                    model, ddp_backend, ddp_init_method, device_ids=device_ids
                )
            else:
                logger.error(f"Unknown multi-GPU strategy: {strategy}")
                return model, False, gpu_info
            
            if setup_success:
                logger.info(f"✅ Multi-GPU training setup completed: {strategy}")
                return model, True, gpu_info
            else:
                logger.warning(f"Failed to setup {strategy}, falling back to single GPU")
                return model, False, gpu_info
                
        except Exception as e:
            logger.error(f"Failed to setup multi-GPU training: {e}")
            return model, False, gpu_info
    
    def train_with_multi_gpu(self, model: nn.Module,
                            train_loader: torch.utils.data.DataLoader,
                            optimizer: torch.optim.Optimizer,
                            criterion: nn.Module,
                            num_epochs: int = 10,
                            strategy: str = 'auto',
                            device_ids: List[int] = None,
                            use_mixed_precision: bool = True,
                            gradient_accumulation_steps: int = 1) -> Dict[str, Any]:
        """Train model using multi-GPU training.
        
        Args:
            model: PyTorch model to train
            train_loader: Training data loader
            optimizer: Optimizer
            criterion: Loss function
            num_epochs: Number of training epochs
            strategy: Multi-GPU strategy
            device_ids: GPU device IDs to use
            use_mixed_precision: Whether to use mixed precision training
            gradient_accumulation_steps: Number of steps for gradient accumulation
            
        Returns:
            Training results dictionary
        """
        try:
            # Setup multi-GPU training
            model, setup_success, gpu_info = self.setup_multi_gpu(
                model, strategy, device_ids
            )
            
            if not setup_success:
                logger.warning("Multi-GPU setup failed, using single GPU")
                model = model.to(self.device)
            
            # Setup mixed precision if enabled
            scaler = None
            if use_mixed_precision and torch.cuda.is_available():
                scaler = torch.cuda.amp.GradScaler()
            
            # Training loop
            model.train()
            total_loss = 0.0
            num_batches = 0
            
            for epoch in range(num_epochs):
                epoch_loss = 0.0
                epoch_batches = 0
                
                for batch_idx, (data, target) in enumerate(train_loader):
                    # Move data to device
                    if isinstance(data, (list, tuple)):
                        data = [d.to(self.device) for d in data]
                    else:
                        data = data.to(self.device)
                    
                    if isinstance(target, (list, tuple)):
                        target = [t.to(self.device) for t in target]
                    else:
                        target = target.to(self.device)
                    
                    # Forward pass
                    if scaler is not None:
                        with torch.cuda.amp.autocast():
                            output = model(data)
                            loss = criterion(output, target)
                    else:
                        output = model(data)
                        loss = criterion(output, target)
                    
                    # Scale loss for gradient accumulation
                    loss = loss / gradient_accumulation_steps
                    
                    # Backward pass
                    if scaler is not None:
                        scaler.scale(loss).backward()
                    else:
                        loss.backward()
                    
                    # Gradient accumulation
                    if (batch_idx + 1) % gradient_accumulation_steps == 0:
                        if scaler is not None:
                            scaler.step(optimizer)
                            scaler.update()
                        else:
                            optimizer.step()
                        optimizer.zero_grad()
                    
                    epoch_loss += loss.item() * gradient_accumulation_steps
                    epoch_batches += 1
                    
                    # Log progress
                    if batch_idx % 100 == 0:
                        logger.info(f"Epoch {epoch+1}/{num_epochs}, Batch {batch_idx}/{len(train_loader)}, Loss: {loss.item():.4f}")
                
                avg_epoch_loss = epoch_loss / epoch_batches
                total_loss += avg_epoch_loss
                num_batches += 1
                
                logger.info(f"Epoch {epoch+1}/{num_epochs} completed. Average Loss: {avg_epoch_loss:.4f}")
            
            # Calculate final metrics
            final_loss = total_loss / num_batches
            
            results = {
                'final_loss': final_loss,
                'total_epochs': num_epochs,
                'multi_gpu_enabled': setup_success,
                'strategy_used': strategy,
                'gpu_info': gpu_info,
                'mixed_precision': use_mixed_precision,
                'gradient_accumulation_steps': gradient_accumulation_steps
            }
            
            logger.info(f"Training completed. Final Loss: {final_loss:.4f}")
            return results
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Cleanup multi-GPU training resources."""
        try:
            if self.is_distributed and dist.is_initialized():
                dist.destroy_process_group()
                logger.info("Distributed process group destroyed")
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("GPU cache cleared")
            
            self.is_distributed = False
            self.is_data_parallel = False
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# Enhanced Exception Classes
class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class ModelError(Exception):
    """Custom exception for model-related errors."""
    pass

class DataLoadingError(Exception):
    """Custom exception for data loading errors."""
    pass

class MemoryError(Exception):
    """Custom exception for memory-related errors."""
    pass

class DeviceError(Exception):
    """Custom exception for device-related errors."""
    pass

class TimeoutError(Exception):
    """Custom exception for operation timeout errors."""
    pass

class InputValidator:
    """Handles input validation for the Gradio apps."""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def validate_model_type(self, model_type: str) -> Tuple[bool, str]:
        """Validate model type selection."""
        try:
            if not model_type or not isinstance(model_type, str):
                return False, "Model type must be a valid string"

            valid_models = ["enhanced_classifier", "enhanced_regressor", "autoencoder"]
            if model_type not in valid_models:
                return False, f"Invalid model type. Must be one of: {', '.join(valid_models)}"

            return True, "Valid model type"

        except Exception as e:
            self.logger.error(f"Model type validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def validate_input_size(self, input_size: Union[int, float]) -> Tuple[bool, str]:
        """Validate input size parameter."""
        try:
            # Convert to int if float
            if isinstance(input_size, float):
                input_size = int(input_size)

            if not isinstance(input_size, int):
                return False, "Input size must be an integer"

            if input_size < 1:
                return False, "Input size must be at least 1"

            if input_size > self.config.max_input_size:
                return False, f"Input size cannot exceed {self.config.max_input_size}"

            return True, "Valid input size"

        except Exception as e:
            self.logger.error(f"Input size validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def validate_batch_size(self, batch_size: Union[int, float]) -> Tuple[bool, str]:
        """Validate batch size parameter."""
        try:
            # Convert to int if float
            if isinstance(batch_size, float):
                batch_size = int(batch_size)

            if not isinstance(batch_size, int):
                return False, "Batch size must be an integer"

            if batch_size < 1:
                return False, "Batch size must be at least 1"

            if batch_size > self.config.max_batch_size:
                return False, f"Batch size cannot exceed {self.config.max_batch_size}"

            return True, "Valid batch size"

        except Exception as e:
            self.logger.error(f"Batch size validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def validate_noise_level(self, noise_level: Union[int, float]) -> Tuple[bool, str]:
        """Validate noise level parameter."""
        try:
            if not isinstance(noise_level, (int, float)):
                return False, "Noise level must be a number"

            if noise_level < 0.0:
                return False, "Noise level cannot be negative"

            if noise_level > self.config.max_noise_level:
                return False, f"Noise level cannot exceed {self.config.max_noise_level}"

            return True, "Valid noise level"

        except Exception as e:
            self.logger.error(f"Noise level validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def validate_chart_type(self, chart_type: str) -> Tuple[bool, str]:
        """Validate chart type selection."""
        try:
            if not chart_type or not isinstance(chart_type, str):
                return False, "Chart type must be a valid string"

            valid_charts = ["scatter", "line", "histogram", "bar", "heatmap", "3d_scatter", "box", "violin"]
            if chart_type not in valid_charts:
                return False, f"Invalid chart type. Must be one of: {', '.join(valid_charts)}"

            return True, "Valid chart type"

        except Exception as e:
            self.logger.error(f"Chart type validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def validate_data_source(self, data_source: str) -> Tuple[bool, str]:
        """Validate data source selection."""
        try:
            if not data_source or not isinstance(data_source, str):
                return False, "Data source must be a valid string"

            valid_sources = ["enhanced_classification", "enhanced_regression", "enhanced_time_series", "autoencoder"]
            if data_source not in valid_sources:
                return False, f"Invalid data source. Must be one of: {', '.join(valid_sources)}"

            return True, "Valid data source"

        except Exception as e:
            self.logger.error(f"Data source validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def validate_color_scheme(self, color_scheme: str) -> Tuple[bool, str]:
        """Validate color scheme selection."""
        try:
            if not color_scheme or not isinstance(color_scheme, str):
                return False, "Color scheme must be a valid string"

            valid_schemes = ["viridis", "plasma", "inferno", "magma", "cividis", "turbo", "rainbow"]
            if color_scheme not in valid_schemes:
                return False, f"Invalid color scheme. Must be one of: {', '.join(valid_schemes)}"

            return True, "Valid color scheme"

        except Exception as e:
            self.logger.error(f"Color scheme validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def validate_opacity(self, opacity: Union[int, float]) -> Tuple[bool, str]:
        """Validate opacity parameter."""
        try:
            if not isinstance(opacity, (int, float)):
                return False, "Opacity must be a number"

            if opacity < 0.1:
                return False, "Opacity must be at least 0.1"

            if opacity > 1.0:
                return False, "Opacity cannot exceed 1.0"

            return True, "Valid opacity"

        except Exception as e:
            self.logger.error(f"Opacity validation error: {e}")
            return False, f"Validation error: {str(e)}"

class ErrorHandler:
    """Handles error processing and user feedback with comprehensive try-except blocks."""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def handle_validation_error(self, error: ValidationError, field_name: str) -> Dict[str, Any]:
        """Handle validation errors and return user-friendly messages."""
        try:
            error_message = str(error)

            if self.config.log_all_errors:
                self.logger.warning(f"Validation error in {field_name}: {error_message}")

            return {
                "status": "error",
                "type": "validation",
                "field": field_name,
                "message": f"Invalid {field_name}: {error_message}",
                "user_message": f"Please check your {field_name} input and try again.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error handling validation error: {e}")
            return {
                "status": "error",
                "type": "system",
                "message": "An unexpected error occurred during validation",
                "user_message": "Please try again or contact support if the problem persists.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def handle_model_error(self, error: ModelError, operation: str) -> Dict[str, Any]:
        """Handle model-related errors and return user-friendly messages."""
        try:
            error_message = str(error)

            if self.config.log_all_errors:
                self.logger.error(f"Model error during {operation}: {error_message}")

            return {
                "status": "error",
                "type": "model",
                "operation": operation,
                "message": f"Model error during {operation}: {error_message}",
                "user_message": f"Unable to complete {operation}. Please try again or check your model configuration.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error handling model error: {e}")
            return {
                "status": "error",
                "type": "system",
                "message": "An unexpected error occurred during model operation",
                "user_message": "Please try again or contact support if the problem persists.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def handle_data_loading_error(self, error: DataLoadingError, operation: str) -> Dict[str, Any]:
        """Handle data loading errors and return user-friendly messages."""
        try:
            error_message = str(error)

            if self.config.log_all_errors:
                self.logger.error(f"Data loading error during {operation}: {error_message}")

            return {
                "status": "error",
                "type": "data_loading",
                "operation": operation,
                "message": f"Data loading error during {operation}: {error_message}",
                "user_message": f"Failed to load data for {operation}. Please check your data source and try again.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error handling data loading error: {e}")
            return {
                "status": "error",
                "type": "system",
                "message": "An unexpected error occurred during data loading",
                "user_message": "Please try again or contact support if the problem persists.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def handle_memory_error(self, error: MemoryError, operation: str) -> Dict[str, Any]:
        """Handle memory-related errors and return user-friendly messages."""
        try:
            error_message = str(error)

            if self.config.log_all_errors:
                self.logger.error(f"Memory error during {operation}: {error_message}")

            return {
                "status": "error",
                "type": "memory",
                "operation": operation,
                "message": f"Memory error during {operation}: {error_message}",
                "user_message": f"Insufficient memory for {operation}. Try reducing batch size or input size.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error handling memory error: {e}")
            return {
                "status": "error",
                "type": "system",
                "message": "An unexpected error occurred during memory operation",
                "user_message": "Please try again or contact support if the problem persists.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def handle_device_error(self, error: DeviceError, operation: str) -> Dict[str, Any]:
        """Handle device-related errors and return user-friendly messages."""
        try:
            error_message = str(error)

            if self.config.log_all_errors:
                self.logger.error(f"Device error during {operation}: {error_message}")

            return {
                "status": "error",
                "type": "device",
                "operation": operation,
                "message": f"Device error during {operation}: {error_message}",
                "user_message": f"Device error during {operation}. Please check your hardware configuration.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error handling device error: {e}")
            return {
                "status": "error",
                "type": "system",
                "message": "An unexpected error occurred during device operation",
                "user_message": "Please try again or contact support if the problem persists.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def handle_timeout_error(self, error: TimeoutError, operation: str) -> Dict[str, Any]:
        """Handle timeout errors and return user-friendly messages."""
        try:
            error_message = str(error)

            if self.config.log_all_errors:
                self.logger.error(f"Timeout error during {operation}: {error_message}")

            return {
                "status": "error",
                "type": "timeout",
                "operation": operation,
                "message": f"Timeout error during {operation}: {error_message}",
                "user_message": f"Operation {operation} timed out. Please try again with smaller parameters.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error handling timeout error: {e}")
            return {
                "status": "error",
                "type": "system",
                "message": "An unexpected error occurred during timeout handling",
                "user_message": "Please try again or contact support if the problem persists.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def handle_system_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Handle system errors and return user-friendly messages."""
        try:
            error_message = str(error)
            error_type = type(error).__name__

            if self.config.log_all_errors:
                self.logger.error(f"System error during {operation}: {error_type}: {error_message}")
                if self.config.show_detailed_errors:
                    self.logger.error(f"Traceback: {traceback.format_exc()}")

            if self.config.graceful_degradation:
                user_message = f"Unable to complete {operation}. Please try again."
            else:
                user_message = f"System error during {operation}. Please contact support."

            return {
                "status": "error",
                "type": "system",
                "operation": operation,
                "error_type": error_type,
                "message": f"System error during {operation}: {error_message}",
                "user_message": user_message,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error handling system error: {e}")
            return {
                "status": "error",
                "type": "system",
                "message": "An unexpected error occurred",
                "user_message": "Please try again or contact support if the problem persists.",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def create_success_message(self, operation: str, details: str = "") -> Dict[str, Any]:
        """Create success message for user feedback."""
        try:
            message = f"Successfully completed {operation}"
            if details:
                message += f": {details}"

            if self.config.log_all_errors:
                self.logger.info(f"Success: {message}")

            return {
                "status": "success",
                "type": "operation",
                "operation": operation,
                "message": message,
                "user_message": message,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error creating success message: {e}")
            return {
                "status": "success",
                "type": "operation",
                "message": f"Operation {operation} completed successfully",
                "user_message": f"Operation {operation} completed successfully",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def create_warning_message(self, operation: str, warning: str) -> Dict[str, Any]:
        """Create warning message for user feedback."""
        try:
            message = f"Warning during {operation}: {warning}"

            if self.config.log_all_errors:
                self.logger.warning(f"Warning: {message}")

            return {
                "status": "warning",
                "type": "operation",
                "operation": operation,
                "message": message,
                "user_message": f"Warning: {warning}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            self.logger.error(f"Error creating warning message: {e}")
            return {
                "status": "warning",
                "type": "operation",
                "message": f"Warning during {operation}",
                "user_message": f"Warning during {operation}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

class PyTorchDebugManager:
    """Manages PyTorch debugging tools and anomaly detection."""
    
    def __init__(self, debug_config: PyTorchDebugConfig):
        self.config = debug_config
        self.logger = logging.getLogger(__name__)
        self.profiler = None
        self.anomaly_detection_enabled = False
        self.gradient_hooks = []
        self.activation_hooks = []
        
        # Initialize debugging tools
        self._initialize_debugging_tools()
    
    def _initialize_debugging_tools(self):
        """Initialize PyTorch debugging tools based on configuration."""
        try:
            # Enable autograd anomaly detection
            if self.config.enable_autograd_anomaly_detection:
                torch.autograd.set_detect_anomaly(True)
                self.anomaly_detection_enabled = True
                self.logger.info("✅ Autograd anomaly detection enabled")
            
            # Enable memory profiling
            if self.config.enable_memory_profiling:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    self.logger.info("✅ CUDA memory profiling enabled")
                else:
                    self.logger.info("✅ CPU memory profiling enabled")
            
            # Set debug level
            if self.config.debug_level == "DEBUG":
                torch.set_default_dtype(torch.float32)
                self.logger.info("✅ PyTorch debug mode enabled")
            
            self.logger.info("PyTorch debugging tools initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PyTorch debugging tools: {e}")
            # Continue without debugging tools
    
    def enable_gradient_monitoring(self, model: nn.Module):
        """Enable gradient monitoring for a model."""
        try:
            if not self.config.enable_weight_gradient_monitoring:
                return
            
            def gradient_hook(name, grad):
                if grad is not None:
                    if torch.isnan(grad).any():
                        self.logger.warning(f"⚠️ NaN gradients detected in {name}")
                    if torch.isinf(grad).any():
                        self.logger.warning(f"⚠️ Infinite gradients detected in {name}")
                    
                    if self.config.log_gradients:
                        grad_norm = grad.norm().item()
                        self.logger.debug(f"📊 Gradient norm for {name}: {grad_norm:.6f}")
                        
                        if self.config.enable_gradient_clipping and grad_norm > self.config.max_gradient_norm:
                            self.logger.info(f"✂️ Clipping gradients for {name} from {grad_norm:.6f} to {self.config.max_gradient_norm}")
            
            # Register hooks for all parameters
            for name, param in model.named_parameters():
                if param.requires_grad:
                    hook = param.register_hook(lambda grad, name=name: gradient_hook(name, grad))
                    self.gradient_hooks.append(hook)
            
            self.logger.info(f"✅ Gradient monitoring enabled for {len(self.gradient_hooks)} parameters")
            
        except Exception as e:
            self.logger.error(f"Failed to enable gradient monitoring: {e}")
    
    def enable_activation_monitoring(self, model: nn.Module):
        """Enable activation monitoring for a model."""
        try:
            if not self.config.enable_activation_monitoring:
                return
            
            def activation_hook(module, input, output):
                if self.config.log_activations:
                    if isinstance(output, torch.Tensor):
                        if torch.isnan(output).any():
                            self.logger.warning(f"⚠️ NaN activations detected in {module.__class__.__name__}")
                        if torch.isinf(output).any():
                            self.logger.warning(f"⚠️ Infinite activations detected in {module.__class__.__name__}")
                        
                        # Log activation statistics
                        mean_act = output.mean().item()
                        std_act = output.std().item()
                        self.logger.debug(f"📊 Activations in {module.__class__.__name__}: mean={mean_act:.6f}, std={std_act:.6f}")
            
            # Register hooks for all modules
            for name, module in model.named_modules():
                if isinstance(module, (nn.Linear, nn.Conv2d, nn.ReLU, nn.Tanh, nn.Sigmoid)):
                    hook = module.register_forward_hook(activation_hook)
                    self.activation_hooks.append(hook)
            
            self.logger.info(f"✅ Activation monitoring enabled for {len(self.activation_hooks)} modules")
            
        except Exception as e:
            self.logger.error(f"Failed to enable activation monitoring: {e}")
    
    def start_profiling(self, model_name: str = "model"):
        """Start PyTorch profiler for performance analysis."""
        try:
            if not self.config.enable_autograd_profiler:
                return None
            
            self.profiler = torch.profiler.profile(
                activities=[
                    torch.profiler.ProfilerActivity.CPU,
                    torch.profiler.ProfilerActivity.CUDA,
                ],
                schedule=torch.profiler.schedule(
                    wait=1,
                    warmup=1,
                    active=3,
                    repeat=2
                ),
                on_trace_ready=torch.profiler.tensorboard_trace_handler(f"./profiler_logs/{model_name}"),
                record_shapes=True,
                with_stack=True,
                profile_memory=True,
                with_flops=True
            )
            
            self.profiler.start()
            self.logger.info(f"✅ PyTorch profiler started for {model_name}")
            return self.profiler
            
        except Exception as e:
            self.logger.error(f"Failed to start profiler: {e}")
            return None
    
    def stop_profiling(self):
        """Stop PyTorch profiler and generate report."""
        try:
            if self.profiler is not None:
                self.profiler.stop()
                self.logger.info("✅ PyTorch profiler stopped")
                
                # Generate summary
                if hasattr(self.profiler, 'key_averages'):
                    summary = self.profiler.key_averages().table(sort_by="cuda_time_total", row_limit=10)
                    self.logger.info(f"📊 Profiler Summary:\n{summary}")
                
                self.profiler = None
                
        except Exception as e:
            self.logger.error(f"Failed to stop profiler: {e}")
    
    def check_memory_usage(self, operation: str = "operation"):
        """Check and log memory usage."""
        try:
            if not self.config.enable_cuda_memory_tracking:
                return
            
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1024**2  # MB
                reserved = torch.cuda.memory_reserved() / 1024**2   # MB
                max_allocated = torch.cuda.max_memory_allocated() / 1024**2  # MB
                
                self.logger.info(f"💾 CUDA Memory for {operation}: "
                               f"Allocated={allocated:.2f}MB, "
                               f"Reserved={reserved:.2f}MB, "
                               f"Max={max_allocated:.2f}MB")
                
                # Check for potential memory leaks
                if self.config.enable_memory_leak_detection and allocated > 1000:  # > 1GB
                    self.logger.warning(f"⚠️ High memory usage detected: {allocated:.2f}MB")
                    
            else:
                # CPU memory monitoring
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024**2
                
                self.logger.info(f"💾 CPU Memory for {operation}: {memory_mb:.2f}MB")
                
        except Exception as e:
            self.logger.error(f"Failed to check memory usage: {e}")
    
    def monitor_operation(self, operation_name: str, func, *args, **kwargs):
        """Monitor an operation with timing and memory tracking."""
        try:
            if not self.config.enable_operation_timing:
                return func(*args, **kwargs)
            
            start_time = time.time()
            start_memory = self._get_current_memory()
            
            # Run the operation
            result = func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = self._get_current_memory()
            
            # Calculate metrics
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Log performance metrics
            self.logger.info(f"⚡ Operation '{operation_name}' completed in {duration:.4f}s, "
                           f"Memory delta: {memory_delta:.2f}MB")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Operation monitoring failed for '{operation_name}': {e}")
            # Re-raise the original exception
            raise
    
    def _get_current_memory(self) -> float:
        """Get current memory usage in MB."""
        try:
            if torch.cuda.is_available():
                return torch.cuda.memory_allocated() / 1024**2
            else:
                process = psutil.Process()
                return process.memory_info().rss / 1024**2
        except Exception:
            return 0.0
    
    def cleanup(self):
        """Clean up debugging tools and hooks."""
        try:
            # Remove gradient hooks
            for hook in self.gradient_hooks:
                hook.remove()
            self.gradient_hooks.clear()
            
            # Remove activation hooks
            for hook in self.activation_hooks:
                hook.remove()
            self.activation_hooks.clear()
            
            # Stop profiler if running
            if self.profiler is not None:
                self.stop_profiling()
            
            # Disable anomaly detection
            if self.anomaly_detection_enabled:
                torch.autograd.set_detect_anomaly(False)
                self.anomaly_detection_enabled = False
            
            self.logger.info("✅ PyTorch debugging tools cleaned up")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup debugging tools: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

class MemoryManager:
    """Manages memory usage and optimization."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.memory_pool = {}
        self.memory_usage_history = []
        self._setup_memory_monitoring()
    
    def _setup_memory_monitoring(self):
        """Setup memory monitoring if enabled."""
        if self.config.enable_memory_optimization:
            self._start_memory_monitor()
    
    def _start_memory_monitor(self):
        """Start background memory monitoring."""
        if self.config.enable_real_time_monitoring:
            def monitor_memory():
                while True:
                    try:
                        self._check_memory_usage()
                        time.sleep(self.config.monitoring_interval)
                    except Exception as e:
                        self.logger.error(f"Memory monitoring error: {e}")
                        break
            
            monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
            monitor_thread.start()
            self.logger.info("✅ Memory monitoring started")
    
    def _check_memory_usage(self):
        """Check current memory usage and optimize if needed."""
        current_memory = self._get_current_memory_usage()
        self.memory_usage_history.append({
            'timestamp': time.time(),
            'memory_mb': current_memory,
            'memory_percent': (current_memory / self.config.max_memory_usage_mb) * 100
        })
        
        # Keep history size manageable
        if len(self.memory_usage_history) > self.config.performance_history_size:
            self.memory_usage_history = self.memory_usage_history[-self.config.performance_history_size:]
        
        # Check if optimization is needed
        if current_memory > self.config.max_memory_usage_mb * self.config.memory_cleanup_threshold:
            self.logger.warning(f"⚠️ High memory usage detected: {current_memory:.2f}MB")
            self._optimize_memory()
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024**2
        else:
            process = psutil.Process()
            return process.memory_info().rss / 1024**2
    
    def _optimize_memory(self):
        """Perform memory optimization."""
        try:
            # Clear GPU cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                self.logger.info("🧹 GPU cache cleared")
            
            # Garbage collection
            if self.config.enable_garbage_collection:
                collected = gc.collect()
                self.logger.info(f"🗑️ Garbage collection: {collected} objects collected")
            
            # Clear memory pool
            if self.config.enable_memory_pooling:
                self._clear_memory_pool()
            
            # Force memory cleanup
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            
            self.logger.info("✅ Memory optimization completed")
        except Exception as e:
            self.logger.error(f"Memory optimization failed: {e}")
    
    def _clear_memory_pool(self):
        """Clear memory pool."""
        pool_size = len(self.memory_pool)
        self.memory_pool.clear()
        if pool_size > 0:
            self.logger.info(f"🧹 Memory pool cleared: {pool_size} objects")
    
    def allocate_memory(self, size_mb: float, purpose: str = "general") -> bool:
        """Check if memory allocation is safe."""
        current_memory = self._get_current_memory_usage()
        if current_memory + size_mb > self.config.max_memory_usage_mb:
            self.logger.warning(f"⚠️ Memory allocation rejected: {size_mb:.2f}MB for {purpose}")
            return False
        return True
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        current_memory = self._get_current_memory_usage()
        return {
            'current_memory_mb': current_memory,
            'max_memory_mb': self.config.max_memory_usage_mb,
            'memory_usage_percent': (current_memory / self.config.max_memory_usage_mb) * 100,
            'pool_size': len(self.memory_pool),
            'history_size': len(self.memory_usage_history),
            'gpu_available': torch.cuda.is_available(),
            'optimization_enabled': self.config.enable_memory_optimization
        }

class BatchProcessor:
    """Handles batch processing and parallelization."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.executor = None
        self._setup_executor()
    
    def _setup_executor(self):
        """Setup thread/process pool executor."""
        if self.config.enable_parallel_processing:
            try:
                if self.config.max_workers > 1:
                    self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
                    self.logger.info(f"✅ Thread pool executor created with {self.config.max_workers} workers")
            except Exception as e:
                self.logger.warning(f"Failed to create executor: {e}")
    
    def process_batch(self, data: List[Any], process_func, batch_size: Optional[int] = None) -> List[Any]:
        """Process data in batches with optional parallelization."""
        if not self.config.enable_batch_processing:
            return [process_func(item) for item in data]
        
        batch_size = batch_size or self.config.default_batch_size
        batch_size = min(batch_size, self.config.max_batch_size)
        
        results = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_results = self._process_batch(batch, process_func)
            results.extend(batch_results)
        
        return results
    
    def _process_batch(self, batch: List[Any], process_func) -> List[Any]:
        """Process a single batch."""
        if self.config.enable_parallel_processing and self.executor:
            try:
                futures = [self.executor.submit(process_func, item) for item in batch]
                return [future.result() for future in futures]
            except Exception as e:
                self.logger.warning(f"Parallel processing failed, falling back to sequential: {e}")
                return [process_func(item) for item in batch]
        else:
            return [process_func(item) for item in batch]
    
    def cleanup(self):
        """Cleanup executor resources."""
        if self.executor:
            self.executor.shutdown(wait=True)
            self.logger.info("✅ Batch processor cleaned up")

class ModelOptimizer:
    """Handles model optimization techniques."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.optimized_models = weakref.WeakValueDictionary()
    
    def optimize_model(self, model: nn.Module, model_name: str = "model") -> nn.Module:
        """Apply various optimization techniques to a model."""
        if not self.config.enable_model_optimization:
            return model
        
        try:
            optimized_model = model
            
            # Mixed precision
            if self.config.enable_mixed_precision:
                optimized_model = self._apply_mixed_precision(optimized_model)
            
            # Torch compile (PyTorch 2.0+)
            if self.config.enable_torch_compile and hasattr(torch, 'compile'):
                optimized_model = self._apply_torch_compile(optimized_model)
            
            # Quantization
            if self.config.enable_quantization:
                optimized_model = self._apply_quantization(optimized_model)
            
            # Pruning
            if self.config.enable_pruning:
                optimized_model = self._apply_pruning(optimized_model)
            
            # Store reference
            self.optimized_models[model_name] = optimized_model
            
            self.logger.info(f"✅ Model '{model_name}' optimized successfully")
            return optimized_model
            
        except Exception as e:
            self.logger.warning(f"Model optimization failed: {e}")
            return model
    
    def _apply_mixed_precision(self, model: nn.Module) -> nn.Module:
        """Apply mixed precision optimization."""
        try:
            model = model.half()  # Convert to float16
            self.logger.info("✅ Mixed precision (FP16) applied")
            return model
        except Exception as e:
            self.logger.warning(f"Mixed precision failed: {e}")
            return model
    
    def _apply_torch_compile(self, model: nn.Module) -> nn.Module:
        """Apply PyTorch 2.0 compile optimization."""
        try:
            if hasattr(torch, 'compile'):
                compiled_model = torch.compile(model)
                self.logger.info("✅ Torch compile optimization applied")
                return compiled_model
        except Exception as e:
            self.logger.warning(f"Torch compile failed: {e}")
        return model
    
    def _apply_quantization(self, model: nn.Module) -> nn.Module:
        """Apply model quantization."""
        try:
            # Dynamic quantization for CPU
            if not torch.cuda.is_available():
                quantized_model = torch.quantization.quantize_dynamic(
                    model, {nn.Linear, nn.Conv2d}, dtype=torch.qint8
                )
                self.logger.info("✅ Dynamic quantization applied")
                return quantized_model
        except Exception as e:
            self.logger.warning(f"Quantization failed: {e}")
        return model
    
    def _apply_pruning(self, model: nn.Module) -> nn.Module:
        """Apply model pruning."""
        try:
            # Simple unstructured pruning
            for name, module in model.named_modules():
                if isinstance(module, nn.Linear):
                    torch.nn.utils.prune.random_unstructured(module, name='weight', amount=0.1)
            self.logger.info("✅ Random pruning applied")
            return model
        except Exception as e:
            self.logger.warning(f"Pruning failed: {e}")
            return model
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        return {
            'optimized_models_count': len(self.optimized_models),
            'mixed_precision_enabled': self.config.enable_mixed_precision,
            'torch_compile_enabled': self.config.enable_torch_compile,
            'quantization_enabled': self.config.enable_quantization,
            'pruning_enabled': self.config.enable_pruning
        }

class PerformanceMonitor:
    """Monitors and tracks performance metrics."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.performance_history = []
        self.metrics = {
            'inference_times': [],
            'memory_usage': [],
            'throughput': [],
            'error_rates': []
        }
        self.start_time = time.time()
    
    def record_metric(self, metric_type: str, value: float, metadata: Optional[Dict] = None):
        """Record a performance metric."""
        if not self.config.enable_performance_monitoring:
            return
        
        timestamp = time.time()
        record = {
            'timestamp': timestamp,
            'metric_type': metric_type,
            'value': value,
            'metadata': metadata or {}
        }
        
        self.performance_history.append(record)
        
        # Keep history size manageable
        if len(self.performance_history) > self.config.performance_history_size:
            self.performance_history = self.performance_history[-self.config.performance_history_size:]
        
        # Update specific metric lists
        if metric_type in self.metrics:
            self.metrics[metric_type].append(value)
            if len(self.metrics[metric_type]) > self.config.performance_history_size:
                self.metrics[metric_type] = self.metrics[metric_type][-self.config.performance_history_size:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.performance_history:
            return {}
        
        uptime = time.time() - self.start_time
        
        summary = {
            'uptime_seconds': uptime,
            'total_metrics_recorded': len(self.performance_history),
            'metrics_by_type': {}
        }
        
        for metric_type, values in self.metrics.items():
            if values:
                summary['metrics_by_type'][metric_type] = {
                    'count': len(values),
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'latest': values[-1] if values else None
                }
        
        return summary
    
    def create_performance_chart(self) -> go.Figure:
        """Create a performance visualization chart."""
        if not self.performance_history:
            return go.Figure()
        
        # Group metrics by type
        metric_data = {}
        for record in self.performance_history:
            metric_type = record['metric_type']
            if metric_type not in metric_data:
                metric_data[metric_type] = {'timestamps': [], 'values': []}
            metric_data[metric_type]['timestamps'].append(record['timestamp'])
            metric_data[metric_type]['values'].append(record['value'])
        
        fig = go.Figure()
        
        for metric_type, data in metric_data.items():
            if data['timestamps'] and data['values']:
                # Convert timestamps to relative time
                relative_times = [t - self.start_time for t in data['timestamps']]
                
                fig.add_trace(go.Scatter(
                    x=relative_times,
                    y=data['values'],
                    mode='lines+markers',
                    name=metric_type.replace('_', ' ').title(),
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title="Performance Metrics Over Time",
            xaxis_title="Time (seconds)",
            yaxis_title="Metric Value",
            hovermode='x unified',
            showlegend=True
        )
        
        return fig

class CacheManager:
    """Manages caching for improved performance."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        self._setup_cache()
    
    def _setup_cache(self):
        """Setup cache directory and configuration."""
        if self.config.enable_disk_caching:
            try:
                cache_dir = Path(self.config.cache_directory)
                cache_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"✅ Cache directory created: {cache_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to create cache directory: {e}")
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a unique cache key."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get item from cache."""
        if not self.config.enable_caching:
            return default
        
        cache_key = self._generate_cache_key(key)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            item = self.memory_cache[cache_key]
            if self._is_cache_item_valid(item):
                self.cache_stats['hits'] += 1
                return item['value']
            else:
                del self.memory_cache[cache_key]
        
        # Check disk cache
        if self.config.enable_disk_caching:
            try:
                disk_item = self._get_from_disk_cache(cache_key)
                if disk_item and self._is_cache_item_valid(disk_item):
                    # Store in memory cache
                    self._store_in_memory_cache(cache_key, disk_item)
                    self.cache_stats['hits'] += 1
                    return disk_item['value']
            except Exception as e:
                self.logger.warning(f"Disk cache read failed: {e}")
        
        self.cache_stats['misses'] += 1
        return default
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store item in cache."""
        if not self.config.enable_caching:
            return False
        
        cache_key = self._generate_cache_key(key)
        ttl = ttl_seconds or self.config.cache_ttl_seconds
        
        cache_item = {
            'value': value,
            'timestamp': time.time(),
            'ttl_seconds': ttl
        }
        
        # Store in memory cache
        success = self._store_in_memory_cache(cache_key, cache_item)
        
        # Store in disk cache
        if self.config.enable_disk_caching and success:
            try:
                self._store_in_disk_cache(cache_key, cache_item)
            except Exception as e:
                self.logger.warning(f"Disk cache write failed: {e}")
        
        return success
    
    def _store_in_memory_cache(self, key: str, item: Dict) -> bool:
        """Store item in memory cache."""
        try:
            # Check cache size limit
            if len(self.memory_cache) >= self.config.cache_size_limit:
                self._evict_oldest_items()
            
            self.memory_cache[key] = item
            return True
        except Exception as e:
            self.logger.warning(f"Memory cache store failed: {e}")
            return False
    
    def _evict_oldest_items(self):
        """Evict oldest cache items."""
        if not self.memory_cache:
            return
        
        # Remove expired items first
        current_time = time.time()
        expired_keys = [
            key for key, item in self.memory_cache.items()
            if not self._is_cache_item_valid(item)
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # If still over limit, remove oldest items
        if len(self.memory_cache) >= self.config.cache_size_limit:
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            items_to_remove = len(self.memory_cache) - self.config.cache_size_limit + 1
            for i in range(items_to_remove):
                if i < len(sorted_items):
                    del self.memory_cache[sorted_items[i][0]]
                    self.cache_stats['evictions'] += 1
    
    def _is_cache_item_valid(self, item: Dict) -> bool:
        """Check if cache item is still valid."""
        current_time = time.time()
        return (current_time - item['timestamp']) < item['ttl_seconds']
    
    def _store_in_disk_cache(self, key: str, item: Dict):
        """Store item in disk cache."""
        if not self.config.enable_disk_caching:
            return
        
        try:
            cache_file = Path(self.config.cache_directory) / f"{key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(item, f)
        except Exception as e:
            self.logger.warning(f"Failed to store in disk cache: {e}")
    
    def _get_from_disk_cache(self, key: str) -> Optional[Dict]:
        """Get item from disk cache."""
        if not self.config.enable_disk_caching:
            return None
        
        try:
            cache_file = Path(self.config.cache_directory) / f"{key}.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to read from disk cache: {e}")
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'memory_cache_size': len(self.memory_cache),
            'cache_size_limit': self.config.cache_size_limit,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'evictions': self.cache_stats['evictions'],
            'hit_rate_percent': hit_rate,
            'total_requests': total_requests,
            'disk_caching_enabled': self.config.enable_disk_caching
        }
    
    def clear_cache(self):
        """Clear all caches."""
        self.memory_cache.clear()
        self.cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
        
        if self.config.enable_disk_caching:
            try:
                cache_dir = Path(self.config.cache_directory)
                for cache_file in cache_dir.glob("*.pkl"):
                    cache_file.unlink()
                self.logger.info("✅ Disk cache cleared")
            except Exception as e:
                self.logger.warning(f"Failed to clear disk cache: {e}")
        
        self.logger.info("✅ All caches cleared")

class PerformanceOptimizer:
    """Main performance optimization orchestrator."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.memory_manager = MemoryManager(config)
        self.batch_processor = BatchProcessor(config)
        self.model_optimizer = ModelOptimizer(config)
        self.performance_monitor = PerformanceMonitor(config)
        self.cache_manager = CacheManager(config)
        
        self.logger.info("✅ Performance optimizer initialized")
    
    def optimize_inference(self, model: nn.Module, data: torch.Tensor, 
                          model_name: str = "model") -> Tuple[torch.Tensor, Dict[str, Any]]:
        """Optimize model inference with comprehensive performance tracking."""
        start_time = time.time()
        start_memory = self.memory_manager._get_current_memory_usage()
        
        try:
            # Check memory availability
            estimated_memory = data.numel() * data.element_size() / 1024**2
            if not self.memory_manager.allocate_memory(estimated_memory, f"{model_name} inference"):
                raise MemoryError(f"Insufficient memory for {model_name} inference")
            
            # Optimize model if not already done
            if model_name not in self.model_optimizer.optimized_models:
                model = self.model_optimizer.optimize_model(model, model_name)
            
            # Use cache if available
            cache_key = f"{model_name}_inference_{hash(data.cpu().numpy().tobytes())}"
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                self.performance_monitor.record_metric('cache_hits', 1, {'model': model_name})
                return cached_result, {'cached': True, 'optimization_applied': True}
            
            # Perform inference
            with torch.no_grad():
                if self.config.enable_batch_processing and data.dim() > 1:
                    # Process in batches
                    batch_size = min(self.config.default_batch_size, data.size(0))
                    outputs = []
                    
                    for i in range(0, data.size(0), batch_size):
                        batch_data = data[i:i + batch_size]
                        batch_output = model(batch_data)
                        outputs.append(batch_output)
                    
                    output = torch.cat(outputs, dim=0)
                else:
                    output = model(data)
            
            # Cache result
            self.cache_manager.set(cache_key, output)
            
            # Record performance metrics
            inference_time = time.time() - start_time
            end_memory = self.memory_manager._get_current_memory_usage()
            memory_delta = end_memory - start_memory
            
            self.performance_monitor.record_metric('inference_times', inference_time, {
                'model': model_name,
                'input_size': list(data.shape),
                'output_size': list(output.shape)
            })
            
            self.performance_monitor.record_metric('memory_usage', memory_delta, {
                'model': model_name,
                'operation': 'inference'
            })
            
            # Calculate throughput
            if inference_time > 0:
                throughput = data.numel() / inference_time
                self.performance_monitor.record_metric('throughput', throughput, {
                    'model': model_name,
                    'unit': 'elements_per_second'
                })
            
            optimization_info = {
                'cached': False,
                'optimization_applied': True,
                'inference_time': inference_time,
                'memory_delta_mb': memory_delta,
                'model_optimizations': self.model_optimizer.get_optimization_stats(),
                'cache_stats': self.cache_manager.get_cache_stats()
            }
            
            return output, optimization_info
            
        except Exception as e:
            # Record error
            self.performance_monitor.record_metric('error_rates', 1, {
                'model': model_name,
                'error_type': type(e).__name__,
                'error_message': str(e)
            })
            
            self.logger.error(f"Inference optimization failed for {model_name}: {e}")
            raise
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            'memory_stats': self.memory_manager.get_memory_stats(),
            'performance_summary': self.performance_monitor.get_performance_summary(),
            'cache_stats': self.cache_manager.get_cache_stats(),
            'optimization_stats': self.model_optimizer.get_optimization_stats(),
            'configuration': {
                'memory_optimization': self.config.enable_memory_optimization,
                'batch_processing': self.config.enable_batch_processing,
                'parallel_processing': self.config.enable_parallel_processing,
                'model_optimization': self.config.enable_model_optimization,
                'caching': self.config.enable_caching
            }
        }
    
    def cleanup(self):
        """Cleanup all performance optimization components."""
        try:
            self.batch_processor.cleanup()
            self.cache_manager.clear_cache()
            self.logger.info("✅ Performance optimizer cleaned up")
        except Exception as e:
            self.logger.error(f"Performance optimizer cleanup failed: {e}")

class EnhancedUIDemosWithValidation:
    """Enhanced UI demos with comprehensive error handling and validation."""

    def __init__(self, ui_config: Optional[EnhancedUIConfig] = None, 
                 validation_config: Optional[ValidationConfig] = None, 
                 debug_config: Optional[PyTorchDebugConfig] = None,
                 performance_config: Optional[PerformanceConfig] = None,
                 multi_gpu_config: Optional[MultiGPUConfig] = None,
                 profiling_config: Optional[ProfilingConfig] = None):
        try:
            self.ui_config = ui_config or EnhancedUIConfig()
            self.validation_config = validation_config or ValidationConfig()
            self.debug_config = debug_config or PyTorchDebugConfig()
            self.performance_config = performance_config or PerformanceConfig()
            self.multi_gpu_config = multi_gpu_config or MultiGPUConfig()
            self.profiling_config = profiling_config or ProfilingConfig()
            
            # Initialize components
            self.validator = InputValidator(self.validation_config)
            self.error_handler = ErrorHandler(self.validation_config)
            self.debug_manager = PyTorchDebugManager(self.debug_config)
            self.performance_optimizer = PerformanceOptimizer(self.performance_config)
            self.multi_gpu_trainer = MultiGPUTrainer(self.multi_gpu_config)
            self.code_profiler = CodeProfiler(self.profiling_config)
            
            # Initialize demo environment with debugging
            self.models = self._create_demo_models()
            self.demo_data = self._generate_demo_data()
            self.performance_history = []
            self.initialize_ui_environment()
            
        except Exception as e:
            logger.error(f"Failed to initialize EnhancedUIDemosWithValidation: {e}")
            raise

    def initialize_ui_environment(self):
        """Initialize the enhanced UI environment."""
        try:
            # Initialize performance tracking
            self.performance_history = []
            logger.info("Enhanced UI environment with validation initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize UI environment: {e}")
            raise

    def _create_demo_models(self):
        """Create enhanced demo models with comprehensive error handling and PyTorch debugging."""
        # Start profiling for model creation
        self.code_profiler.start_profiling("demo_models_creation", "model")
        
        try:
            models = {}
            
            # Check available memory before creating models
            try:
                available_memory = psutil.virtual_memory().available / (1024**3)  # GB
                if available_memory < 2.0:  # Less than 2GB available
                    raise MemoryError(f"Insufficient memory available: {available_memory:.2f}GB")
            except ImportError:
                logger.warning("psutil not available, skipping memory check")
            except Exception as e:
                logger.warning(f"Memory check failed: {e}")
            
            # Enhanced classifier with better architecture and debugging
            try:
                # Profile classifier creation
                classifier = self.code_profiler.profile_sub_operation(
                    "demo_models_creation", "classifier_creation",
                    self._create_classifier_model
                )
                models["enhanced_classifier"] = classifier
                logger.info("✅ Successfully created enhanced classifier with debugging enabled")
                
            except Exception as e:
                logger.error(f"Failed to create enhanced classifier: {e}")
                raise ModelError(f"Failed to create enhanced classifier: {str(e)}")
            
            # Enhanced regressor with debugging
            try:
                # Profile regressor creation
                regressor = self.code_profiler.profile_sub_operation(
                    "demo_models_creation", "regressor_creation",
                    self._create_regressor_model
                )
                models["enhanced_regressor"] = regressor
                logger.info("✅ Successfully created enhanced regressor with debugging enabled")
                
            except Exception as e:
                logger.error(f"Failed to create enhanced regressor: {e}")
                raise ModelError(f"Failed to create enhanced regressor: {str(e)}")
            
            # Autoencoder for feature learning with debugging
            try:
                # Profile autoencoder creation
                autoencoder = self.code_profiler.profile_sub_operation(
                    "demo_models_creation", "autoencoder_creation",
                    self._create_autoencoder_model
                )
                models["autoencoder"] = autoencoder
                logger.info("✅ Successfully created autoencoder with debugging enabled")
                
            except Exception as e:
                logger.error(f"Failed to create autoencoder: {e}")
                raise ModelError(f"Failed to create autoencoder: {str(e)}")
            
            # Check memory usage after model creation
            self.debug_manager.check_memory_usage("model creation")
            
            logger.info(f"✅ Successfully created {len(models)} demo models with PyTorch debugging enabled")
            return models
            
        except Exception as e:
            logger.error(f"Failed to create demo models: {e}")
            raise ModelError(f"Failed to create demo models: {str(e)}")
        finally:
            # End profiling for model creation
            self.code_profiler.end_profiling("demo_models_creation")
    
    def _create_classifier_model(self):
        """Create enhanced classifier model."""
        classifier = nn.Sequential(
            nn.Linear(10, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 5),
            nn.Softmax(dim=1)
        )
        
        # Enable debugging tools for classifier
        self.debug_manager.enable_gradient_monitoring(classifier)
        self.debug_manager.enable_activation_monitoring(classifier)
        
        return classifier
    
    def _create_regressor_model(self):
        """Create enhanced regressor model."""
        regressor = nn.Sequential(
            nn.Linear(8, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.4),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
        # Enable debugging tools for regressor
        self.debug_manager.enable_gradient_monitoring(regressor)
        self.debug_manager.enable_activation_monitoring(regressor)
        
        return regressor
    
    def _create_autoencoder_model(self):
        """Create enhanced autoencoder model."""
        class Autoencoder(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Linear(20, 128),
                    nn.ReLU(),
                    nn.BatchNorm1d(128),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.BatchNorm1d(64),
                    nn.Linear(64, 16)
                )
                self.decoder = nn.Sequential(
                    nn.Linear(16, 64),
                    nn.ReLU(),
                    nn.BatchNorm1d(64),
                    nn.Linear(64, 128),
                    nn.ReLU(),
                    nn.BatchNorm1d(128),
                    nn.Linear(128, 20)
                )
            
            def forward(self, x):
                try:
                    # Enable autograd anomaly detection for this forward pass
                    with torch.autograd.detect_anomaly():
                        encoded = self.encoder(x)
                        decoded = self.decoder(encoded)
                        return decoded
                except Exception as e:
                    logger.error(f"Autoencoder forward pass failed: {e}")
                    raise ModelError(f"Autoencoder inference failed: {str(e)}")
        
        autoencoder = Autoencoder()
        
        # Enable debugging tools for autoencoder
        self.debug_manager.enable_gradient_monitoring(autoencoder)
        self.debug_manager.enable_activation_monitoring(autoencoder)
        
        return autoencoder
            
        except Exception as e:
            logger.error(f"Failed to create demo models: {e}")
            raise ModelError(f"Failed to create demo models: {str(e)}")

    def _generate_demo_data(self):
        """Generate enhanced demo data with comprehensive error handling."""
        # Start profiling for data generation
        self.code_profiler.start_profiling("demo_data_generation", "data_loading")
        
        try:
            # Check available memory before generating data
            try:
                available_memory = psutil.virtual_memory().available / (1024**3)  # GB
                if available_memory < 1.0:  # Less than 1GB available
                    raise MemoryError(f"Insufficient memory for data generation: {available_memory:.2f}GB")
            except ImportError:
                logger.warning("psutil not available, skipping memory check")
            except Exception as e:
                logger.warning(f"Memory check failed: {e}")
            
            np.random.seed(42)
            
            data = {}
            
            # Enhanced classification data with better separation
            try:
                # Profile classification data generation
                classification_data = self.code_profiler.profile_sub_operation(
                    "demo_data_generation", "classification_data_generation",
                    self._generate_classification_data
                )
                data["enhanced_classification"] = classification_data
                logger.info("Successfully generated classification data")
            except Exception as e:
                logger.error(f"Failed to generate classification data: {e}")
                raise DataLoadingError(f"Failed to generate classification data: {str(e)}")
            
            # Enhanced regression data
            try:
                # Profile regression data generation
                regression_data = self.code_profiler.profile_sub_operation(
                    "demo_data_generation", "regression_data_generation",
                    self._generate_regression_data
                )
                data["enhanced_regression"] = regression_data
                logger.info("Successfully generated regression data")
            except Exception as e:
                logger.error(f"Failed to generate regression data: {e}")
                raise DataLoadingError(f"Failed to generate regression data: {str(e)}")
            
            # Enhanced time series data
            try:
                # Profile time series data generation
                time_series_data = self.code_profiler.profile_sub_operation(
                    "demo_data_generation", "time_series_data_generation",
                    self._generate_time_series_data
                )
                data["enhanced_time_series"] = time_series_data
                logger.info("Successfully generated time series data")
            except Exception as e:
                logger.error(f"Failed to generate time series data: {e}")
                raise DataLoadingError(f"Failed to generate time series data: {str(e)}")
            
            # Autoencoder data
            try:
                # Profile autoencoder data generation
                autoencoder_data = self.code_profiler.profile_sub_operation(
                    "demo_data_generation", "autoencoder_data_generation",
                    self._generate_autoencoder_data
                )
                data["autoencoder"] = autoencoder_data
                logger.info("Successfully generated autoencoder data")
            except Exception as e:
                logger.error(f"Failed to generate autoencoder data: {e}")
                raise DataLoadingError(f"Failed to generate autoencoder data: {str(e)}")
            
            logger.info(f"Successfully generated demo data with {len(data)} datasets")
            return data
            
        except Exception as e:
            logger.error(f"Failed to generate demo data: {e}")
            raise DataLoadingError(f"Failed to generate demo data: {str(e)}")
        finally:
            # End profiling for data generation
            self.code_profiler.end_profiling("demo_data_generation")
    
    def _generate_classification_data(self):
        """Generate classification data."""
        n_samples = 1500
        n_features = 10
        
        # Create clusters for better visualization
        cluster_centers = np.array([
            [2, 2, 0, 0, 0, 0, 0, 0, 0, 0],
            [-2, -2, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 3, 3, 0, 0, 0, 0, 0, 0],
            [0, 0, -3, -3, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 2, 2, 0, 0, 0, 0]
        ])
        
        X_class = np.random.randn(n_samples, n_features) * 0.5
        y_class = np.random.randint(0, 5, n_samples)
        
        for i in range(5):
            mask = y_class == i
            X_class[mask] += cluster_centers[i]
        
        return {"X": X_class, "y": y_class}
    
    def _generate_regression_data(self):
        """Generate regression data."""
        X_reg = np.random.randn(1000, 8)
        coefficients = np.random.randn(8) * 2
        y_reg = np.sum(X_reg * coefficients, axis=1) + np.random.randn(1000) * 0.1
        
        return {"X": X_reg, "y": y_reg}
    
    def _generate_time_series_data(self):
        """Generate time series data."""
        time_steps = np.linspace(0, 20, 400)
        trend = 0.1 * time_steps
        seasonal = 2 * np.sin(2 * np.pi * time_steps / 4)
        noise = np.random.randn(400) * 0.3
        time_series = trend + seasonal + noise
        
        return {"time": time_steps, "values": time_series}
    
    def _generate_autoencoder_data(self):
        """Generate autoencoder data."""
        X_ae = np.random.randn(800, 20)
        return {"X": X_ae}

    def _safe_model_inference(self, model, X, model_type: str, timeout_seconds: float = 10.0):
        """Enhanced model inference with performance optimization and profiling."""
        # Start profiling for model inference
        self.code_profiler.start_profiling(f"{model_type}_inference", "model")
        
        start_time = time.time()
        profiler = None
        
        try:
            if self.debug_config.enable_autograd_profiler:
                profiler = self.debug_manager.start_profiling(f"{model_type}_inference")
            
            self.debug_manager.check_memory_usage(f"before {model_type} inference")
            
            # Profile data preprocessing
            preprocessed_X = self.code_profiler.profile_sub_operation(
                f"{model_type}_inference", "data_preprocessing",
                self._preprocess_input_data, X, model_type
            )
            
            # Use performance optimizer for inference
            output, optimization_info = self.code_profiler.profile_sub_operation(
                f"{model_type}_inference", "model_inference",
                self.performance_optimizer.optimize_inference, model, preprocessed_X, model_type
            )
            
            if output is None or torch.isnan(output).any() or torch.isinf(output).any():
                raise ModelError("Model output contains NaN or infinite values")
            
            self.debug_manager.check_memory_usage(f"after {model_type} inference")
            
            # Log optimization results
            logger.info(f"🚀 {model_type} inference optimized: {optimization_info['inference_time']:.4f}s, "
                       f"Memory: {optimization_info['memory_delta_mb']:.2f}MB")
            
            return output
            
        except Exception as e:
            self.error_handler.handle_model_error(e, f"{model_type} inference")
            raise
        finally:
            if profiler is not None:
                self.debug_manager.stop_profiling()
            # End profiling for model inference
            self.code_profiler.end_profiling(f"{model_type}_inference")
    
    def _preprocess_input_data(self, X, model_type: str):
        """Preprocess input data with profiling."""
        try:
            # Convert to tensor if needed
            if not isinstance(X, torch.Tensor):
                X = torch.tensor(X, dtype=torch.float32)
            
            # Add batch dimension if needed
            if X.dim() == 1:
                X = X.unsqueeze(0)
            
            # Move to device
            X = X.to(DEVICE)
            
            return X
            
        except Exception as e:
            logger.error(f"Data preprocessing failed for {model_type}: {e}")
            raise DataLoadingError(f"Data preprocessing failed: {str(e)}")

    def _run_inference_with_debugging(self, model, X, model_type: str):
        """Run model inference with enhanced debugging and anomaly detection."""
        try:
            # Enable autograd anomaly detection for inference
            if self.debug_config.enable_autograd_anomaly_detection:
                with torch.autograd.detect_anomaly():
                    # Set requires_grad for gradient computation during debugging
                    X_debug = X.clone().detach().requires_grad_(True)
                    
                    # Forward pass
                    output = model(X_debug)
                    
                    # Check for gradient anomalies
                    if X_debug.grad is not None:
                        grad_norm = X_debug.grad.norm().item()
                        if torch.isnan(X_debug.grad).any():
                            logger.warning(f"⚠️ NaN gradients detected in {model_type} input")
                        if torch.isinf(X_debug.grad).any():
                            logger.warning(f"⚠️ Infinite gradients detected in {model_type} input")
                        
                        if self.debug_config.log_gradients:
                            logger.debug(f"📊 Input gradient norm for {model_type}: {grad_norm:.6f}")
                    
                    return output
            else:
                # Standard inference without anomaly detection
                return model(X)
                
        except Exception as e:
            logger.error(f"Inference with debugging failed for {model_type}: {e}")
            raise ModelError(f"Inference with debugging failed: {str(e)}")

    def _create_enhanced_performance_chart(self):
        """Create enhanced performance monitoring chart with error handling."""
        try:
            if not self.performance_history:
                return go.Figure()

            # Validate performance history data
            try:
                times = [entry["processing_time"] for entry in self.performance_history]
                confidences = [entry["confidence"] for entry in self.performance_history]
                model_types = [entry["model_type"] for entry in self.performance_history]
                
                # Check for valid data
                if not times or not confidences or not model_types:
                    raise DataLoadingError("Invalid performance history data")
                    
            except Exception as e:
                logger.error(f"Failed to extract performance data: {e}")
                raise DataLoadingError(f"Failed to extract performance data: {str(e)}")

            try:
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=("Processing Time", "Confidence Score", "Performance Trend", "Model Usage"),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}],
                           [{"secondary_y": False}, {"secondary_y": False}]]
                )

                # Processing time
                fig.add_trace(
                    go.Scatter(
                        y=times,
                        mode="lines+markers",
                        name="Processing Time (ms)",
                        line=dict(color=self.ui_config.primary_color, width=3),
                        marker=dict(size=8)
                    ),
                    row=1, col=1
                )

                # Confidence score
                fig.add_trace(
                    go.Scatter(
                        y=confidences,
                        mode="lines+markers",
                        name="Confidence Score",
                        line=dict(color=self.ui_config.success_color, width=3),
                        marker=dict(size=8)
                    ),
                    row=1, col=2
                )

                # Performance trend
                trend = np.cumsum(confidences)
                fig.add_trace(
                    go.Scatter(
                        y=trend,
                        mode="lines+markers",
                        name="Cumulative Performance",
                        line=dict(color=self.ui_config.secondary_color, width=3),
                        marker=dict(size=8)
                    ),
                    row=2, col=1
                )

                # Model usage distribution
                unique_models, counts = np.unique(model_types, return_counts=True)
                fig.add_trace(
                    go.Bar(
                        x=unique_models,
                        y=counts,
                        name="Model Usage",
                        marker_color=self.ui_config.accent_color
                    ),
                    row=2, col=2
                )

                fig.update_layout(
                    height=600,
                    title="Enhanced Performance Dashboard",
                    template="plotly_white",
                    showlegend=True,
                    font=dict(size=12),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )

                return fig

            except Exception as e:
                logger.error(f"Failed to create performance chart: {e}")
                raise DataLoadingError(f"Failed to create performance chart: {str(e)}")

        except Exception as e:
            logger.error(f"Error creating performance chart: {e}")
            return go.Figure()

    def _get_custom_css(self):
        """Get custom CSS for enhanced UI with error handling styles."""
        return f"""
        .enhanced-container {{
            max-width: {self.ui_config.max_width} !important;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .enhanced-header {{
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, {self.ui_config.primary_color} 0%, {self.ui_config.secondary_color} 100%);
            color: white;
            border-radius: {self.ui_config.card_radius};
            margin-bottom: 30px;
            box-shadow: {self.ui_config.shadow};
        }}
        
        .enhanced-header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .enhanced-header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .enhanced-card {{
            background: white;
            border-radius: {self.ui_config.card_radius};
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: {self.ui_config.shadow};
            border: 1px solid rgba(0, 0, 0, 0.05);
        }}
        
        .enhanced-card h2 {{
            color: {self.ui_config.primary_color};
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: 600;
        }}
        
        .enhanced-button {{
            background: linear-gradient(135deg, {self.ui_config.primary_color} 0%, {self.ui_config.secondary_color} 100%);
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all {self.ui_config.transition_duration} ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .enhanced-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .enhanced-button.secondary {{
            background: linear-gradient(135deg, {self.ui_config.accent_color} 0%, {self.ui_config.warning_color} 100%);
        }}
        
        .enhanced-button.secondary:hover {{
            box-shadow: 0 6px 20px rgba(240, 147, 251, 0.4);
        }}
        
        .enhanced-button.error {{
            background: linear-gradient(135deg, {self.ui_config.error_color} 0%, #c0392b 100%);
        }}
        
        .enhanced-button.error:hover {{
            box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
        }}
        
        .enhanced-controls {{
            background: #f8f9fa;
            border-radius: {self.ui_config.card_radius};
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e9ecef;
        }}
        
        .enhanced-controls h3 {{
            color: {self.ui_config.primary_color};
            margin-bottom: 15px;
            font-size: 1.2rem;
        }}
        
        .enhanced-tab {{
            background: white;
            border-radius: {self.ui_config.card_radius};
            padding: 30px;
            margin: 20px 0;
            box-shadow: {self.ui_config.shadow};
        }}
        
        .enhanced-alert {{
            padding: 15px 20px;
            border-radius: {self.ui_config.card_radius};
            margin: 15px 0;
            border-left: 4px solid;
            animation: slideIn 0.3s ease;
        }}
        
        .alert-success {{
            background: rgba(79, 172, 254, 0.1);
            border-left-color: {self.ui_config.success_color};
            color: #0c5460;
        }}
        
        .alert-warning {{
            background: rgba(255, 154, 158, 0.1);
            border-left-color: {self.ui_config.warning_color};
            color: #856404;
        }}
        
        .alert-error {{
            background: rgba(231, 76, 60, 0.1);
            border-left-color: {self.ui_config.error_color};
            color: #721c24;
        }}
        
        .alert-info {{
            background: rgba(102, 126, 234, 0.1);
            border-left-color: {self.ui_config.primary_color};
            color: #0c5460;
        }}
        
        .validation-error {{
            color: {self.ui_config.error_color};
            font-size: 0.9rem;
            margin-top: 5px;
            font-style: italic;
        }}
        
        .input-field {{
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 10px;
            transition: border-color 0.3s ease;
        }}
        
        .input-field:focus {{
            border-color: {self.ui_config.primary_color};
            outline: none;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .input-field.error {{
            border-color: {self.ui_config.error_color};
            background-color: rgba(231, 76, 60, 0.05);
        }}
        
        .input-field.success {{
            border-color: {self.ui_config.success_color};
            background-color: rgba(79, 172, 254, 0.05);
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @media (max-width: 768px) {{
            .enhanced-container {{
                padding: 10px;
            }}
            
            .enhanced-header {{
                padding: 20px 10px;
            }}
            
            .enhanced-header h1 {{
                font-size: 2rem;
            }}
            
            .enhanced-card {{
                padding: 15px;
            }}
        }}
        """

    def create_enhanced_model_inference_interface(self):
        """Create enhanced model inference interface with comprehensive error handling and validation."""
        
        with gr.Blocks(title="Enhanced Model Inference with Comprehensive Error Handling", theme=gr.themes.Soft(), css=self._get_custom_css()) as demo:
            
            # Enhanced Header
            gr.Markdown(f"""
            <div class="enhanced-header">
                <h1>🚀 Enhanced AI Model Inference</h1>
                <p>Experience cutting-edge AI models with comprehensive error handling and validation</p>
            </div>
            """)
            
            # Status Messages Area
            status_area = gr.HTML(
                value="<div class='enhanced-alert alert-info'><strong>ℹ️ Ready:</strong> Ready to run inference. Configure your model and parameters below.</div>",
                label="Status Messages",
                elem_classes=["enhanced-card"]
            )
            
            with gr.Row():
                # Left Column - Controls
                with gr.Column(scale=1):
                    gr.Markdown("""
                    <div class="enhanced-card">
                        <h2>🎯 Model Configuration</h2>
                        <p>Select and configure your AI model for optimal performance</p>
                    </div>
                    """)
                    
                    with gr.Blocks(css=".enhanced-controls"):
                        gr.Markdown("### 🤖 Model Selection")
                        
                        model_type = gr.Dropdown(
                            choices=list(self.models.keys()),
                            value="enhanced_classifier",
                            label="AI Model",
                            info="Choose from our advanced model collection",
                            container=True
                        )
                        
                        gr.Markdown("### ⚙️ Performance Parameters")
                        
                        input_size = gr.Slider(
                            minimum=1, maximum=self.validation_config.max_input_size, value=10, step=1,
                            label="Input Features",
                            info=f"Number of input features for the model (1-{self.validation_config.max_input_size})",
                            container=True
                        )
                        
                        batch_size = gr.Slider(
                            minimum=1, maximum=self.validation_config.max_batch_size, value=64, step=1,
                            label="Batch Size",
                            info=f"Process multiple samples simultaneously (1-{self.validation_config.max_batch_size})",
                            container=True
                        )
                        
                        noise_level = gr.Slider(
                            minimum=0.0, maximum=self.validation_config.max_noise_level, value=0.1, step=0.01,
                            label="Noise Level",
                            info=f"Add controlled noise for robustness testing (0.0-{self.validation_config.max_noise_level})",
                            container=True
                        )
                        
                        gr.Markdown("### 🎮 Actions")
                        
                        with gr.Row():
                            run_inference_btn = gr.Button(
                                "🚀 Run Inference", 
                                variant="primary",
                                size="lg",
                                elem_classes=["enhanced-button"]
                            )
                            clear_btn = gr.Button(
                                "🗑️ Clear", 
                                variant="secondary",
                                size="lg",
                                elem_classes=["enhanced-button", "secondary"]
                            )
                
                # Right Column - Results
                with gr.Column(scale=2):
                    gr.Markdown("""
                    <div class="enhanced-card">
                        <h2>📊 Inference Results</h2>
                        <p>Real-time model predictions and performance metrics</p>
                    </div>
                    """)
                    
                    # Results Display
                    with gr.Row():
                        with gr.Column():
                            inference_output = gr.JSON(
                                label="Model Output",
                                container=True
                            )
                        
                        with gr.Column():
                            confidence_score = gr.Gauge(
                                label="Confidence Score",
                                minimum=0, maximum=1, value=0.5,
                                container=True
                            )
                    
                    # Performance Metrics
                    gr.Markdown("### ⚡ Performance Metrics")
                    
                    with gr.Row():
                        with gr.Column():
                            processing_time = gr.Number(
                                label="Processing Time (ms)",
                                container=True
                            )
                        
                        with gr.Column():
                            memory_usage = gr.Number(
                                label="Memory Usage (MB)",
                                container=True
                            )
                    
                    # Performance Chart
                    gr.Markdown("### 📈 Performance Trends")
                    performance_chart = gr.Plot(
                        label="Performance Over Time",
                        container=True
                    )
            
            # Event handlers with comprehensive error handling and validation
            def run_enhanced_inference_with_validation(model_type, input_size, batch_size, noise_level):
                """Run inference with comprehensive validation and error handling using try-except blocks."""
                start_time = time.time()
                
                try:
                    # Validate all inputs with comprehensive error handling
                    validation_results = []
                    
                    # Validate model type
                    try:
                        is_valid, message = self.validator.validate_model_type(model_type)
                        if not is_valid:
                            raise ValidationError(message)
                        validation_results.append(("Model Type", True, message))
                    except Exception as e:
                        logger.error(f"Model type validation failed: {e}")
                        raise ValidationError(f"Model type validation failed: {str(e)}")
                    
                    # Validate input size
                    try:
                        is_valid, message = self.validator.validate_input_size(input_size)
                        if not is_valid:
                            raise ValidationError(message)
                        validation_results.append(("Input Size", True, message))
                    except Exception as e:
                        logger.error(f"Input size validation failed: {e}")
                        raise ValidationError(f"Input size validation failed: {str(e)}")
                    
                    # Validate batch size
                    try:
                        is_valid, message = self.validator.validate_batch_size(batch_size)
                        if not is_valid:
                            raise ValidationError(message)
                        validation_results.append(("Batch Size", True, message))
                    except Exception as e:
                        logger.error(f"Batch size validation failed: {e}")
                        raise ValidationError(f"Batch size validation failed: {str(e)}")
                    
                    # Validate noise level
                    try:
                        is_valid, message = self.validator.validate_noise_level(noise_level)
                        if not is_valid:
                            raise ValidationError(message)
                        validation_results.append(("Noise Level", True, message))
                    except Exception as e:
                        logger.error(f"Noise level validation failed: {e}")
                        raise ValidationError(f"Noise level validation failed: {str(e)}")
                    
                    # Check processing time limit
                    if time.time() - start_time > self.validation_config.max_processing_time:
                        raise TimeoutError("Processing time exceeded maximum limit")
                    
                    # Run inference with comprehensive error handling
                    try:
                        if model_type == "enhanced_classifier":
                            try:
                                # Generate input data with error handling
                                X = torch.randn(batch_size, min(input_size, 10)) + noise_level * torch.randn(batch_size, min(input_size, 10)
                                
                                # Validate input tensor
                                if torch.isnan(X).any() or torch.isinf(X).any():
                                    raise ValidationError("Generated input contains invalid values")
                                
                                # Get model with error handling
                                if model_type not in self.models:
                                    raise ModelError(f"Model {model_type} not found")
                                
                                model = self.models[model_type]
                                
                                # Run inference safely
                                output = self._safe_model_inference(model, X, model_type)
                                predictions = torch.argmax(output, dim=1)
                                confidence = torch.max(output, dim=1)[0].mean().item()
                                
                            except Exception as e:
                                logger.error(f"Classifier inference failed: {e}")
                                raise ModelError(f"Classifier inference failed: {str(e)}")
                                
                        elif model_type == "enhanced_regressor":
                            try:
                                # Generate input data with error handling
                                X = torch.randn(batch_size, min(input_size, 8)) + noise_level * torch.randn(batch_size, min(input_size, 8)
                                
                                # Validate input tensor
                                if torch.isnan(X).any() or torch.isinf(X).any():
                                    raise ValidationError("Generated input contains invalid values")
                                
                                # Get model with error handling
                                if model_type not in self.models:
                                    raise ModelError(f"Model {model_type} not found")
                                
                                model = self.models[model_type]
                                
                                # Run inference safely
                                output = self._safe_model_inference(model, X, model_type)
                                predictions = output.squeeze()
                                confidence = 1.0 - torch.std(output).item()
                                
                            except Exception as e:
                                logger.error(f"Regressor inference failed: {e}")
                                raise ModelError(f"Regressor inference failed: {str(e)}")
                                
                        else:  # Autoencoder
                            try:
                                # Generate input data with error handling
                                X = torch.randn(batch_size, min(input_size, 20)) + noise_level * torch.randn(batch_size, min(input_size, 20)
                                
                                # Validate input tensor
                                if torch.isnan(X).any() or torch.isinf(X).any():
                                    raise ValidationError("Generated input contains invalid values")
                                
                                # Get model with error handling
                                if model_type not in self.models:
                                    raise ModelError(f"Model {model_type} not found")
                                
                                model = self.models[model_type]
                                
                                # Run inference safely
                                output = self._safe_model_inference(model, X, model_type)
                                predictions = output
                                confidence = 0.8
                                
                            except Exception as e:
                                logger.error(f"Autoencoder inference failed: {e}")
                                raise ModelError(f"Autoencoder inference failed: {str(e)}")
                    
                    except Exception as e:
                        logger.error(f"Model inference failed: {e}")
                        if isinstance(e, (ValidationError, ModelError, MemoryError, TimeoutError)):
                            raise
                        else:
                            raise ModelError(f"Unexpected error during model inference: {str(e)}")
                    
                    # Calculate performance metrics with error handling
                    try:
                        processing_time_ms = (time.time() - start_time) * 1000
                        
                        # Get memory usage with error handling
                        try:
                            if torch.cuda.is_available():
                                memory_mb = torch.cuda.memory_allocated() / 1024**2
                            else:
                                memory_mb = 0
                        except Exception as e:
                            logger.warning(f"Failed to get memory usage: {e}")
                            memory_mb = 0
                        
                        # Update performance history with error handling
                        try:
                            self.performance_history.append({
                                "model_type": model_type,
                                "processing_time": processing_time_ms,
                                "confidence": confidence,
                                "timestamp": time.time()
                            })
                        except Exception as e:
                            logger.warning(f"Failed to update performance history: {e}")
                        
                        # Create enhanced performance chart with error handling
                        try:
                            fig = self._create_enhanced_performance_chart()
                        except Exception as e:
                            logger.warning(f"Failed to create performance chart: {e}")
                            fig = None
                        
                        # Create success message
                        try:
                            success_msg = self.error_handler.create_success_message(
                                "model inference",
                                f"Processed {batch_size} samples in {processing_time_ms:.2f}ms"
                            )
                        except Exception as e:
                            logger.warning(f"Failed to create success message: {e}")
                            success_msg = {"user_message": "Inference completed successfully"}
                        
                        # Update status
                        status_html = f"""
                        <div class='enhanced-alert alert-success'>
                            <strong>✅ Success!</strong> {success_msg['user_message']}
                        </div>
                        """
                        
                        return {
                            "model_type": model_type,
                            "predictions": predictions.tolist()[:10] if hasattr(predictions, 'tolist') else str(predictions)[:100],
                            "confidence": confidence,
                            "processing_time": processing_time_ms,
                            "memory_usage": memory_mb,
                            "status": "success",
                            "validation_results": validation_results
                        }, confidence, processing_time_ms, memory_mb, fig, status_html
                        
                    except Exception as e:
                        logger.error(f"Failed to calculate performance metrics: {e}")
                        raise ModelError(f"Failed to calculate performance metrics: {str(e)}")
                    
                except ValidationError as e:
                    error_info = self.error_handler.handle_validation_error(e, "input parameters")
                    status_html = f"""
                    <div class='enhanced-alert alert-error'>
                        <strong>❌ Validation Error:</strong> {error_info['user_message']}
                    </div>
                    """
                    return error_info, 0.5, 0.0, 0.0, None, status_html
                    
                except ModelError as e:
                    error_info = self.error_handler.handle_model_error(e, "model inference")
                    status_html = f"""
                    <div class='enhanced-alert alert-error'>
                        <strong>❌ Model Error:</strong> {error_info['user_message']}
                    </div>
                    """
                    return error_info, 0.5, 0.0, 0.0, None, status_html
                    
                except MemoryError as e:
                    error_info = self.error_handler.handle_memory_error(e, "model inference")
                    status_html = f"""
                    <div class='enhanced-alert alert-error'>
                        <strong>❌ Memory Error:</strong> {error_info['user_message']}
                    </div>
                    """
                    return error_info, 0.5, 0.0, 0.0, None, status_html
                    
                except TimeoutError as e:
                    error_info = self.error_handler.handle_timeout_error(e, "model inference")
                    status_html = f"""
                    <div class='enhanced-alert alert-error'>
                        <strong>❌ Timeout Error:</strong> {error_info['user_message']}
                    </div>
                    """
                    return error_info, 0.5, 0.0, 0.0, None, status_html
                    
                except Exception as e:
                    error_info = self.error_handler.handle_system_error(e, "model inference")
                    status_html = f"""
                    <div class='enhanced-alert alert-error'>
                        <strong>❌ System Error:</strong> {error_info['user_message']}
                    </div>
                    """
                    return error_info, 0.5, 0.0, 0.0, None, status_html
            
            def clear_enhanced_results():
                """Clear all results and reset status with error handling."""
                try:
                    status_html = """
                    <div class='enhanced-alert alert-info'>
                        <strong>ℹ️ Ready:</strong> All results cleared. Ready for new inference.
                    </div>
                    """
                    return None, 0.5, 0.0, 0.0, None, status_html
                except Exception as e:
                    error_info = self.error_handler.handle_system_error(e, "clearing results")
                    status_html = f"""
                    <div class='enhanced-alert alert-error'>
                        <strong>❌ Error:</strong> {error_info['user_message']}
                    </div>
                    """
                    return None, 0.5, 0.0, 0.0, None, status_html
            
            # Connect events
            run_inference_btn.click(
                fn=run_enhanced_inference_with_validation,
                inputs=[model_type, input_size, batch_size, noise_level],
                outputs=[inference_output, confidence_score, processing_time, memory_usage, performance_chart, status_area]
            )
            
            clear_btn.click(
                fn=clear_enhanced_results,
                outputs=[inference_output, confidence_score, processing_time, memory_usage, performance_chart, status_area]
            )
        
        return demo

    def create_performance_dashboard(self) -> gr.Interface:
        """Create a performance monitoring dashboard."""
        def get_performance_report():
            try:
                report = self.performance_optimizer.get_performance_report()
                return str(report)
            except Exception as e:
                return f"Error getting performance report: {e}"
        
        def get_performance_chart():
            try:
                fig = self.performance_monitor.create_performance_chart()
                return fig
            except Exception as e:
                return f"Error creating performance chart: {e}"
        
        def clear_performance_data():
            try:
                self.performance_optimizer.cleanup()
                return "Performance data cleared successfully"
            except Exception as e:
                return f"Error clearing performance data: {e}"
        
        with gr.Blocks(title="Performance Dashboard", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🚀 Performance Optimization Dashboard")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## 📊 Performance Report")
                    performance_report = gr.Textbox(
                        label="Performance Report",
                        lines=20,
                        interactive=False
                    )
                    refresh_report_btn = gr.Button("🔄 Refresh Report", variant="primary")
                
                with gr.Column():
                    gr.Markdown("## 📈 Performance Chart")
                    performance_chart = gr.Plot(label="Performance Metrics")
                    refresh_chart_btn = gr.Button("🔄 Refresh Chart", variant="primary")
            
            with gr.Row():
                clear_data_btn = gr.Button("🗑️ Clear Performance Data", variant="secondary")
                status_output = gr.Textbox(label="Status", interactive=False)
            
            # Event handlers
            refresh_report_btn.click(
                fn=get_performance_report,
                outputs=performance_report
            )
            
            refresh_chart_btn.click(
                fn=get_performance_chart,
                outputs=performance_chart
            )
            
            clear_data_btn.click(
                fn=clear_performance_data,
                outputs=status_output
            )
            
            # Initial load
            interface.load(
                fn=get_performance_report,
                outputs=performance_report
            )
            
            interface.load(
                fn=get_performance_chart,
                outputs=performance_chart
            )
        
        return interface

    def create_multi_gpu_training_interface(self) -> gr.Interface:
        """Create a comprehensive multi-GPU training interface."""
        
        def get_gpu_info():
            """Get current GPU information."""
            try:
                gpu_info = self.multi_gpu_trainer.get_gpu_info()
                if 'error' in gpu_info:
                    return f"Error getting GPU info: {gpu_info['error']}"
                
                info_text = f"CUDA Available: {gpu_info['cuda_available']}\n"
                info_text += f"GPU Count: {gpu_info['gpu_count']}\n"
                if gpu_info['current_device'] is not None:
                    info_text += f"Current Device: {gpu_info['current_device']}\n"
                if gpu_info['device_name']:
                    info_text += f"Device Name: {gpu_info['device_name']}\n"
                
                if gpu_info['memory_info']:
                    info_text += "\nMemory Information:\n"
                    for gpu_id, mem_info in gpu_info['memory_info'].items():
                        info_text += f"  {gpu_id}:\n"
                        info_text += f"    Allocated: {mem_info['allocated_gb']} GB\n"
                        info_text += f"    Reserved: {mem_info['reserved_gb']} GB\n"
                        info_text += f"    Total: {mem_info['total_gb']} GB\n"
                        info_text += f"    Utilization: {mem_info['utilization_percent']}%\n"
                
                return info_text
            except Exception as e:
                return f"Error getting GPU info: {e}"
        
        def setup_multi_gpu_training(strategy, device_ids_str, backend, init_method, 
                                   world_size, rank, local_rank):
            """Setup multi-GPU training with specified configuration."""
            try:
                # Parse device IDs
                device_ids = None
                if device_ids_str and device_ids_str.strip():
                    device_ids = [int(x.strip()) for x in device_ids_str.split(',')]
                
                # Setup multi-GPU training
                if strategy.lower() == 'dataparallel':
                    success = False
                    if device_ids:
                        _, success = self.multi_gpu_trainer.setup_data_parallel(
                            self.models.get('enhanced_classifier', nn.Linear(10, 5)), 
                            device_ids
                        )
                    else:
                        _, success = self.multi_gpu_trainer.setup_data_parallel(
                            self.models.get('enhanced_classifier', nn.Linear(10, 5))
                        )
                    
                    if success:
                        return f"✅ DataParallel setup completed successfully"
                    else:
                        return "❌ DataParallel setup failed"
                
                elif strategy.lower() in ['distributeddataparallel', 'ddp']:
                    success = False
                    if device_ids:
                        _, success = self.multi_gpu_trainer.setup_distributed_data_parallel(
                            self.models.get('enhanced_classifier', nn.Linear(10, 5)),
                            backend, init_method, world_size, rank, device_ids
                        )
                    else:
                        _, success = self.multi_gpu_trainer.setup_distributed_data_parallel(
                            self.models.get('enhanced_classifier', nn.Linear(10, 5)),
                            backend, init_method, world_size, rank
                        )
                    
                    if success:
                        return f"✅ DistributedDataParallel setup completed successfully"
                    else:
                        return "❌ DistributedDataParallel setup failed"
                
                else:
                    return f"❌ Unknown strategy: {strategy}"
                    
            except Exception as e:
                return f"❌ Setup failed: {e}"
        
        def run_multi_gpu_training(num_epochs, batch_size, learning_rate, 
                                 use_mixed_precision, gradient_accumulation_steps):
            """Run multi-GPU training with specified parameters."""
            try:
                # Create a simple dataset for demonstration
                X = torch.randn(1000, 10)
                y = torch.randint(0, 5, (1000,))
                dataset = torch.utils.data.TensorDataset(X, y)
                train_loader = torch.utils.data.DataLoader(
                    dataset, 
                    batch_size=batch_size, 
                    shuffle=True,
                    num_workers=2,
                    pin_memory=True
                )
                
                # Create model, optimizer, and criterion
                model = nn.Sequential(
                    nn.Linear(10, 128),
                    nn.ReLU(),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, 5),
                    nn.LogSoftmax(dim=1)
                )
                
                optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
                criterion = nn.NLLLoss()
                
                # Run training
                results = self.multi_gpu_trainer.train_with_multi_gpu(
                    model=model,
                    train_loader=train_loader,
                    optimizer=optimizer,
                    criterion=criterion,
                    num_epochs=num_epochs,
                    strategy='auto',
                    use_mixed_precision=use_mixed_precision,
                    gradient_accumulation_steps=gradient_accumulation_steps
                )
                
                if 'error' in results:
                    return f"❌ Training failed: {results['error']}"
                
                # Format results
                result_text = f"✅ Training completed successfully!\n\n"
                result_text += f"Final Loss: {results['final_loss']:.4f}\n"
                result_text += f"Total Epochs: {results['total_epochs']}\n"
                result_text += f"Multi-GPU Enabled: {results['multi_gpu_enabled']}\n"
                result_text += f"Strategy Used: {results['strategy_used']}\n"
                result_text += f"Mixed Precision: {results['mixed_precision']}\n"
                result_text += f"Gradient Accumulation Steps: {results['gradient_accumulation_steps']}\n"
                
                if 'gpu_info' in results:
                    result_text += f"\nGPU Information:\n"
                    gpu_info = results['gpu_info']
                    result_text += f"GPU Count: {gpu_info['gpu_count']}\n"
                    if gpu_info['cuda_available']:
                        result_text += f"CUDA Available: Yes\n"
                    else:
                        result_text += f"CUDA Available: No\n"
                
                return result_text
                
            except Exception as e:
                return f"❌ Training failed: {e}"
        
        def cleanup_multi_gpu():
            """Cleanup multi-GPU training resources."""
            try:
                self.multi_gpu_trainer.cleanup()
                return "✅ Multi-GPU training resources cleaned up successfully"
            except Exception as e:
                return f"❌ Cleanup failed: {e}"
        
        with gr.Blocks(title="Multi-GPU Training Interface", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🚀 Multi-GPU Training Interface")
            gr.Markdown("## DataParallel and DistributedDataParallel Training")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## 🔍 GPU Information")
                    gpu_info_output = gr.Textbox(
                        label="Current GPU Status",
                        lines=15,
                        interactive=False
                    )
                    refresh_gpu_btn = gr.Button("🔄 Refresh GPU Info", variant="primary")
                
                with gr.Column():
                    gr.Markdown("## ⚙️ Multi-GPU Setup")
                    
                    strategy_dropdown = gr.Dropdown(
                        choices=["DataParallel", "DistributedDataParallel", "auto"],
                        value="auto",
                        label="Training Strategy",
                        info="Choose the multi-GPU training strategy"
                    )
                    
                    device_ids_input = gr.Textbox(
                        label="Device IDs (comma-separated)",
                        placeholder="0,1,2,3 or leave empty for auto",
                        info="Specify GPU device IDs to use"
                    )
                    
                    backend_dropdown = gr.Dropdown(
                        choices=["nccl", "gloo"],
                        value="nccl",
                        label="Distributed Backend",
                        info="Communication backend for distributed training"
                    )
                    
                    init_method_input = gr.Textbox(
                        label="Init Method",
                        value="env://",
                        info="Process group initialization method"
                    )
                    
                    world_size_input = gr.Number(
                        label="World Size",
                        value=-1,
                        info="Total number of processes (-1 for auto)"
                    )
                    
                    rank_input = gr.Number(
                        label="Rank",
                        value=0,
                        info="Process rank"
                    )
                    
                    local_rank_input = gr.Number(
                        label="Local Rank",
                        value=0,
                        info="Local process rank"
                    )
                    
                    setup_btn = gr.Button("🔧 Setup Multi-GPU Training", variant="primary")
                    setup_output = gr.Textbox(label="Setup Status", interactive=False)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## 🎯 Training Configuration")
                    
                    epochs_input = gr.Number(
                        label="Number of Epochs",
                        value=5,
                        minimum=1,
                        maximum=100,
                        info="Number of training epochs"
                    )
                    
                    batch_size_input = gr.Number(
                        label="Batch Size per GPU",
                        value=32,
                        minimum=1,
                        maximum=512,
                        info="Batch size for each GPU"
                    )
                    
                    lr_input = gr.Number(
                        label="Learning Rate",
                        value=1e-4,
                        minimum=1e-6,
                        maximum=1e-1,
                        info="Learning rate for training"
                    )
                    
                    mixed_precision_checkbox = gr.Checkbox(
                        label="Use Mixed Precision",
                        value=True,
                        info="Enable mixed precision training for faster training and less memory usage"
                    )
                    
                    grad_accum_input = gr.Number(
                        label="Gradient Accumulation Steps",
                        value=1,
                        minimum=1,
                        maximum=16,
                        info="Number of steps for gradient accumulation"
                    )
                    
                    train_btn = gr.Button("🚀 Start Multi-GPU Training", variant="primary")
                    training_output = gr.Textbox(
                        label="Training Results",
                        lines=20,
                        interactive=False
                    )
                
                with gr.Column():
                    gr.Markdown("## 🧹 Resource Management")
                    
                    cleanup_btn = gr.Button("🗑️ Cleanup Multi-GPU Resources", variant="secondary")
                    cleanup_output = gr.Textbox(label="Cleanup Status", interactive=False)
                    
                    gr.Markdown("### 📚 Training Tips")
                    gr.Markdown("""
                    **DataParallel (2-4 GPUs):**
                    - Simple setup, automatic data distribution
                    - Good for single-machine multi-GPU training
                    - Limited scalability due to single process
                    
                    **DistributedDataParallel (4+ GPUs):**
                    - Better scalability and efficiency
                    - Process-based parallelism
                    - Requires proper process group setup
                    
                    **Best Practices:**
                    - Use mixed precision for faster training
                    - Enable gradient accumulation for large effective batch sizes
                    - Monitor GPU memory usage
                    - Clean up resources after training
                    """)
            
            # Event handlers
            refresh_gpu_btn.click(
                fn=get_gpu_info,
                outputs=gpu_info_output
            )
            
            setup_btn.click(
                fn=setup_multi_gpu_training,
                inputs=[strategy_dropdown, device_ids_input, backend_dropdown, 
                       init_method_input, world_size_input, rank_input, local_rank_input],
                outputs=setup_output
            )
            
            train_btn.click(
                fn=run_multi_gpu_training,
                inputs=[epochs_input, batch_size_input, lr_input, 
                       mixed_precision_checkbox, grad_accum_input],
                outputs=training_output
            )
            
            cleanup_btn.click(
                fn=cleanup_multi_gpu,
                outputs=cleanup_output
            )
            
            # Initial load
            interface.load(
                fn=get_gpu_info,
                outputs=gpu_info_output
            )
        
        return interface

    def create_profiling_interface(self):
        """Create a comprehensive profiling interface for bottleneck detection and optimization."""
        with gr.Blocks(title="Code Profiling & Bottleneck Detection") as interface:
            gr.Markdown("""
            # 🔍 Code Profiling & Bottleneck Detection
            
            Comprehensive profiling system to identify and optimize performance bottlenecks in:
            - **Data Loading & Preprocessing**: I/O operations, data transfer, augmentation
            - **Model Operations**: Forward/backward passes, memory usage, GPU operations
            - **Performance Metrics**: CPU usage, memory consumption, timing analysis
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Profiling Controls")
                    
                    # Profiling configuration
                    enable_profiling = gr.Checkbox(value=True, label="Enable Profiling")
                    enable_detailed_profiling = gr.Checkbox(value=True, label="Detailed Profiling")
                    profiling_interval = gr.Slider(minimum=0.01, maximum=1.0, value=0.1, 
                                                 step=0.01, label="Profiling Interval (s)")
                    
                    # Data loading profiling
                    profile_data_loading = gr.Checkbox(value=True, label="Profile Data Loading")
                    profile_preprocessing = gr.Checkbox(value=True, label="Profile Preprocessing")
                    profile_data_transfer = gr.Checkbox(value=True, label="Profile Data Transfer")
                    
                    # Model profiling
                    profile_model_ops = gr.Checkbox(value=True, label="Profile Model Operations")
                    profile_memory = gr.Checkbox(value=True, label="Profile Memory Usage")
                    
                    # Performance profiling
                    profile_cpu = gr.Checkbox(value=True, label="Profile CPU Usage")
                    profile_gpu = gr.Checkbox(value=True, label="Profile GPU Usage")
                    
                    # Action buttons
                    start_profiling_btn = gr.Button("🚀 Start Profiling", variant="primary")
                    stop_profiling_btn = gr.Button("⏹️ Stop Profiling", variant="stop")
                    generate_report_btn = gr.Button("📋 Generate Report", variant="secondary")
                    save_report_btn = gr.Button("💾 Save Report", variant="secondary")
                    
                with gr.Column(scale=2):
                    gr.Markdown("### 📈 Profiling Results")
                    
                    # Real-time profiling display
                    profiling_output = gr.HTML(
                        value="<div style='padding: 20px; background: #f8f9fa; border-radius: 10px;'>"
                              "<h4>Profiling Status: Ready</h4>"
                              "<p>Click 'Start Profiling' to begin monitoring operations.</p>"
                              "</div>"
                    )
                    
                    # Bottleneck analysis
                    bottleneck_output = gr.HTML(
                        value="<div style='padding: 20px; background: #fff3cd; border-radius: 10px;'>"
                              "<h4>Bottleneck Analysis</h4>"
                              "<p>No bottlenecks detected yet. Start profiling to analyze performance.</p>"
                              "</div>"
                    )
                    
                    # Optimization suggestions
                    optimization_output = gr.HTML(
                        value="<div style='padding: 20px; background: #d1ecf1; border-radius: 10px;'>"
                              "<h4>Optimization Suggestions</h4>"
                              "<p>No suggestions available yet. Start profiling to get recommendations.</p>"
                              "</div>"
                    )
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🎯 Quick Profiling Tests")
                    
                    # Test data loading
                    test_data_loading_btn = gr.Button("Test Data Loading", variant="secondary")
                    
                    # Test model inference
                    test_model_inference_btn = gr.Button("Test Model Inference", variant="secondary")
                    
                    # Test preprocessing
                    test_preprocessing_btn = gr.Button("Test Preprocessing", variant="secondary")
                    
                    # Test memory operations
                    test_memory_btn = gr.Button("Test Memory Operations", variant="secondary")
                
                with gr.Column():
                    gr.Markdown("### 📊 Performance Metrics")
                    
                    # Current metrics display
                    metrics_output = gr.HTML(
                        value="<div style='padding: 20px; background: #e2e3e5; border-radius: 10px;'>"
                              "<h4>Current Metrics</h4>"
                              "<p>Click test buttons to see performance metrics.</p>"
                              "</div>"
                    )
            
            # Event handlers
            def start_profiling():
                """Start comprehensive profiling."""
                try:
                    # Update profiling configuration
                    self.profiling_config.enable_profiling = True
                    self.profiling_config.enable_detailed_profiling = True
                    self.profiling_config.profiling_interval = 0.1
                    
                    return f"""
                    <div style='padding: 20px; background: #d4edda; border-radius: 10px; border: 1px solid #c3e6cb;'>
                        <h4>✅ Profiling Started</h4>
                        <p><strong>Status:</strong> Active</p>
                        <p><strong>Monitoring:</strong> All operations</p>
                        <p><strong>Interval:</strong> 0.1s</p>
                        <p><em>Profiling is now active. All operations will be monitored for bottlenecks.</em></p>
                    </div>
                    """
                except Exception as e:
                    return f"""
                    <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                        <h4>❌ Profiling Failed</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    """
            
            def stop_profiling():
                """Stop profiling and generate summary."""
                try:
                    # Get profiling report
                    report = self.code_profiler.get_profiling_report()
                    
                    if report:
                        summary_html = f"""
                        <div style='padding: 20px; background: #fff3cd; border-radius: 10px; border: 1px solid #ffeaa7;'>
                            <h4>📊 Profiling Summary</h4>
                            <p><strong>Total Operations:</strong> {report.get('total_operations', 0)}</p>
                            <p><strong>Total Duration:</strong> {report.get('total_duration', 0):.2f}s</p>
                            <p><strong>Memory Delta:</strong> {report.get('total_memory_delta_mb', 0):.2f}MB</p>
                        </div>
                        """
                        
                        # Analyze bottlenecks
                        bottlenecks = []
                        for op_name, op_data in report.get('summary', {}).items():
                            if op_data.get('bottlenecks_count', 0) > 0:
                                bottlenecks.append(f"• {op_name}: {op_data['bottlenecks_count']} bottlenecks")
                        
                        bottleneck_html = f"""
                        <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                            <h4>⚠️ Detected Bottlenecks</h4>
                            {'<br>'.join(bottlenecks) if bottlenecks else '<p>No major bottlenecks detected.</p>'}
                        </div>
                        """
                        
                        return summary_html, bottleneck_html
                    else:
                        return """
                        <div style='padding: 20px; background: #e2e3e5; border-radius: 10px;'>
                            <h4>📊 No Profiling Data</h4>
                            <p>No profiling data available. Start profiling to collect metrics.</p>
                        </div>
                        """, """
                        <div style='padding: 20px; background: #e2e3e5; border-radius: 10px;'>
                            <h4>⚠️ No Bottlenecks</h4>
                            <p>No bottleneck data available.</p>
                        </div>
                        """
                        
                except Exception as e:
                    error_html = f"""
                    <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                        <h4>❌ Error Generating Summary</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    """
                    return error_html, error_html
            
            def generate_report():
                """Generate comprehensive profiling report."""
                try:
                    report = self.code_profiler.get_profiling_report()
                    
                    if report:
                        # Create detailed report HTML
                        report_html = f"""
                        <div style='padding: 20px; background: #d1ecf1; border-radius: 10px; border: 1px solid #bee5eb;'>
                            <h4>📋 Comprehensive Profiling Report</h4>
                            <h5>Summary</h5>
                            <ul>
                                <li><strong>Total Operations:</strong> {report.get('total_operations', 0)}</li>
                                <li><strong>Total Duration:</strong> {report.get('total_duration', 0):.2f}s</li>
                                <li><strong>Total Memory Delta:</strong> {report.get('total_memory_delta_mb', 0):.2f}MB</li>
                            </ul>
                            
                            <h5>Operation Details</h5>
                            <table style='width: 100%; border-collapse: collapse;'>
                                <tr style='background: #f8f9fa;'>
                                    <th style='border: 1px solid #dee2e6; padding: 8px; text-align: left;'>Operation</th>
                                    <th style='border: 1px solid #dee2e6; padding: 8px; text-align: left;'>Duration</th>
                                    <th style='border: 1px solid #dee2e6; padding: 8px; text-align: left;'>Memory</th>
                                    <th style='border: 1px solid #dee2e6; padding: 8px; text-align: left;'>Bottlenecks</th>
                                </tr>
                        """
                        
                        for op_name, op_data in report.get('summary', {}).items():
                            report_html += f"""
                                <tr>
                                    <td style='border: 1px solid #dee2e6; padding: 8px;'>{op_name}</td>
                                    <td style='border: 1px solid #dee2e6; padding: 8px;'>{op_data.get('duration', 0):.3f}s</td>
                                    <td style='border: 1px solid #dee2e6; padding: 8px;'>{op_data.get('memory_delta_mb', 0):.2f}MB</td>
                                    <td style='border: 1px solid #dee2e6; padding: 8px;'>{op_data.get('bottlenecks_count', 0)}</td>
                                </tr>
                            """
                        
                        report_html += """
                            </table>
                        </div>
                        """
                        
                        return report_html
                    else:
                        return """
                        <div style='padding: 20px; background: #e2e3e5; border-radius: 10px;'>
                            <h4>📋 No Report Available</h4>
                            <p>No profiling data available to generate report.</p>
                        </div>
                        """
                        
                except Exception as e:
                    return f"""
                    <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                        <h4>❌ Report Generation Failed</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    """
            
            def save_report():
                """Save profiling report to file."""
                try:
                    self.code_profiler.save_profiling_report()
                    return """
                    <div style='padding: 20px; background: #d4edda; border-radius: 10px; border: 1px solid #c3e6cb;'>
                        <h4>✅ Report Saved</h4>
                        <p>Profiling report has been saved to the profiling_results directory.</p>
                    </div>
                    """
                except Exception as e:
                    return f"""
                    <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                        <h4>❌ Save Failed</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    """
            
            def test_data_loading():
                """Test data loading performance."""
                try:
                    # Start profiling for data loading test
                    self.code_profiler.start_profiling("test_data_loading", "data_loading")
                    
                    # Generate test data
                    test_data = self._generate_classification_data()
                    
                    # End profiling
                    self.code_profiler.end_profiling("test_data_loading")
                    
                    # Get report
                    report = self.code_profiler.get_profiling_report("test_data_loading")
                    
                    if report:
                        return f"""
                        <div style='padding: 20px; background: #d1ecf1; border-radius: 10px; border: 1px solid #bee5eb;'>
                            <h4>📊 Data Loading Test Results</h4>
                            <p><strong>Duration:</strong> {report.get('total_duration', 0):.3f}s</p>
                            <p><strong>Memory Delta:</strong> {report.get('memory_delta_mb', 0):.2f}MB</p>
                            <p><strong>Data Size:</strong> {test_data['X'].shape[0]} samples × {test_data['X'].shape[1]} features</p>
                        </div>
                        """
                    else:
                        return """
                        <div style='padding: 20px; background: #e2e3e5; border-radius: 10px;'>
                            <h4>📊 No Test Results</h4>
                            <p>No profiling data available for this test.</p>
                        </div>
                        """
                        
                except Exception as e:
                    return f"""
                    <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                        <h4>❌ Test Failed</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    """
            
            def test_model_inference():
                """Test model inference performance."""
                try:
                    if "enhanced_classifier" not in self.models:
                        return """
                        <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                            <h4>❌ Test Failed</h4>
                            <p>No classifier model available for testing.</p>
                        </div>
                        """
                    
                    # Start profiling for model inference test
                    self.code_profiler.start_profiling("test_model_inference", "model")
                    
                    # Generate test data
                    test_X = np.random.randn(100, 10)
                    
                    # Run inference
                    output = self._safe_model_inference(self.models["enhanced_classifier"], test_X, "test_classifier")
                    
                    # End profiling
                    self.code_profiler.end_profiling("test_model_inference")
                    
                    # Get report
                    report = self.code_profiler.get_profiling_report("test_model_inference")
                    
                    if report:
                        return f"""
                        <div style='padding: 20px; background: #d1ecf1; border-radius: 10px; border: 1px solid #bee5eb;'>
                            <h4>📊 Model Inference Test Results</h4>
                            <p><strong>Duration:</strong> {report.get('total_duration', 0):.3f}s</p>
                            <p><strong>Memory Delta:</strong> {report.get('memory_delta_mb', 0):.2f}MB</p>
                            <p><strong>Output Shape:</strong> {output.shape}</p>
                            <p><strong>Output Range:</strong> [{output.min().item():.3f}, {output.max().item():.3f}]</p>
                        </div>
                        """
                    else:
                        return """
                        <div style='padding: 20px; background: #e2e3e5; border-radius: 10px;'>
                            <h4>📊 No Test Results</h4>
                            <p>No profiling data available for this test.</p>
                        </div>
                        """
                        
                except Exception as e:
                    return f"""
                    <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                        <h4>❌ Test Failed</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    """
            
            def test_preprocessing():
                """Test data preprocessing performance."""
                try:
                    # Start profiling for preprocessing test
                    self.code_profiler.start_profiling("test_preprocessing", "preprocessing")
                    
                    # Generate test data
                    test_X = np.random.randn(1000, 20)
                    
                    # Preprocess data
                    preprocessed_X = self._preprocess_input_data(test_X, "test_preprocessing")
                    
                    # End profiling
                    self.code_profiler.end_profiling("test_preprocessing")
                    
                    # Get report
                    report = self.code_profiler.get_profiling_report("test_preprocessing")
                    
                    if report:
                        return f"""
                        <div style='padding: 20px; background: #d1ecf1; border-radius: 10px; border: 1px solid #bee5eb;'>
                            <h4>📊 Preprocessing Test Results</h4>
                            <p><strong>Duration:</strong> {report.get('total_duration', 0):.3f}s</p>
                            <p><strong>Memory Delta:</strong> {report.get('memory_delta_mb', 0):.2f}MB</p>
                            <p><strong>Input Shape:</strong> {test_X.shape}</p>
                            <p><strong>Output Shape:</strong> {preprocessed_X.shape}</p>
                            <p><strong>Device:</strong> {preprocessed_X.device}</p>
                        </div>
                        """
                    else:
                        return """
                        <div style='padding: 20px; background: #e2e3e5; border-radius: 10px;'>
                            <h4>📊 No Test Results</h4>
                            <p>No profiling data available for this test.</p>
                        </div>
                        """
                        
                except Exception as e:
                    return f"""
                    <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                        <h4>❌ Test Failed</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    """
            
            def test_memory():
                """Test memory operations performance."""
                try:
                    # Start profiling for memory test
                    self.code_profiler.start_profiling("test_memory", "performance")
                    
                    # Perform memory-intensive operation
                    large_array = np.random.randn(10000, 1000)
                    processed_array = large_array * 2 + 1
                    result = np.sum(processed_array)
                    
                    # End profiling
                    self.code_profiler.end_profiling("test_memory")
                    
                    # Get report
                    report = self.code_profiler.get_profiling_report("test_memory")
                    
                    if report:
                        return f"""
                        <div style='padding: 20px; background: #d1ecf1; border-radius: 10px; border: 1px solid #bee5eb;'>
                            <h4>📊 Memory Test Results</h4>
                            <p><strong>Duration:</strong> {report.get('total_duration', 0):.3f}s</p>
                            <p><strong>Memory Delta:</strong> {report.get('memory_delta_mb', 0):.2f}MB</p>
                            <p><strong>Array Size:</strong> {large_array.shape}</p>
                            <p><strong>Result:</strong> {result:.2f}</p>
                        </div>
                        """
                    else:
                        return """
                        <div style='padding: 20px; background: #e2e3e5; border-radius: 10px;'>
                            <h4>📊 No Test Results</h4>
                            <p>No profiling data available for this test.</p>
                        </div>
                        """
                        
                except Exception as e:
                    return f"""
                    <div style='padding: 20px; background: #f8d7da; border-radius: 10px; border: 1px solid #f5c6cb;'>
                        <h4>❌ Test Failed</h4>
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    """
            
            # Connect event handlers
            start_profiling_btn.click(
                fn=start_profiling,
                outputs=profiling_output
            )
            
            stop_profiling_btn.click(
                fn=stop_profiling,
                outputs=[profiling_output, bottleneck_output]
            )
            
            generate_report_btn.click(
                fn=generate_report,
                outputs=optimization_output
            )
            
            save_report_btn.click(
                fn=save_report,
                outputs=optimization_output
            )
            
            test_data_loading_btn.click(
                fn=test_data_loading,
                outputs=metrics_output
            )
            
            test_model_inference_btn.click(
                fn=test_model_inference,
                outputs=metrics_output
            )
            
            test_preprocessing_btn.click(
                fn=test_preprocessing,
                outputs=metrics_output
            )
            
            test_memory_btn.click(
                fn=test_memory,
                outputs=metrics_output
            )
        
        return interface

    def cleanup(self):
        """Enhanced cleanup with performance optimization and profiling."""
        if hasattr(self, 'debug_manager'):
            self.debug_manager.cleanup()
        if hasattr(self, 'performance_optimizer'):
            self.performance_optimizer.cleanup()
        if hasattr(self, 'multi_gpu_trainer'):
            self.multi_gpu_trainer.cleanup()
        if hasattr(self, 'code_profiler'):
            self.code_profiler.cleanup()
        if hasattr(self, 'models'):
            self.models.clear()
        if hasattr(self, 'demo_data'):
            self.demo_data.clear()
        if hasattr(self, 'performance_history'):
            self.performance_history.clear()
        logger.info("✅ Enhanced UI demos with performance optimization, multi-GPU training, and profiling cleaned up successfully")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()

def main():
    """Main function with performance optimization, multi-GPU training, and comprehensive profiling."""
    try:
        # Initialize with performance configuration
        performance_config = PerformanceConfig(
            enable_memory_optimization=True,
            enable_batch_processing=True,
            enable_model_optimization=True,
            enable_caching=True,
            enable_performance_monitoring=True
        )
        
        # Initialize with multi-GPU configuration
        multi_gpu_config = MultiGPUConfig(
            training_mode="auto",
            enable_data_parallel=True,
            enable_distributed=True,
            backend="nccl",
            batch_size_per_gpu=32,
            use_mixed_precision=True,
            gradient_accumulation_steps=1
        )
        
        # Initialize with profiling configuration
        profiling_config = ProfilingConfig(
            enable_profiling=True,
            enable_detailed_profiling=True,
            enable_data_loading_profiling=True,
            enable_model_profiling=True,
            enable_performance_profiling=True,
            enable_bottleneck_detection=True,
            enable_optimization_suggestions=True
        )
        
        demos = EnhancedUIDemosWithValidation(
            performance_config=performance_config,
            multi_gpu_config=multi_gpu_config,
            profiling_config=profiling_config
        )
        
        # Create main interface
        main_interface = demos.create_enhanced_model_inference_interface()
        
        # Create performance dashboard
        performance_dashboard = demos.create_performance_dashboard()
        
        # Create multi-GPU training interface
        multi_gpu_training_interface = demos.create_multi_gpu_training_interface()
        
        # Create profiling interface
        profiling_interface = demos.create_profiling_interface()
        
        # Launch interfaces
        with gr.TabbedInterface(
            [main_interface, performance_dashboard, multi_gpu_training_interface, profiling_interface],
            ["Model Inference", "Performance Dashboard", "Multi-GPU Training", "Code Profiling"],
            title="Enhanced AI Model Demos with Performance Optimization, Multi-GPU Training & Comprehensive Profiling"
        ) as interface:
            interface.launch(
                server_name="0.0.0.0",
                server_port=7860,
                share=False,
                debug=True,
                show_error=True
            )
            
    except Exception as e:
        logger.error(f"Failed to launch application: {e}")
        print(f"Error launching application: {e}")
    finally:
        try:
            if 'demos' in locals():
                demos.cleanup()
        except Exception as cleanup_error:
            logger.error(f"Failed to cleanup during shutdown: {cleanup_error}")

if __name__ == "__main__":
    main()
