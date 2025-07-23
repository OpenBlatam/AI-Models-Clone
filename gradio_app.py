"""
🚀 Gradio Integration for Model Inference & Evaluation
=====================================================

Production-ready Gradio app for interactive model inference and evaluation.
Supports classification and regression tasks, metrics, and visualization.
Enhanced with comprehensive multi-GPU training support using DataParallel and DistributedDataParallel.
"""

import gradio as gr
import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
from torch.nn.parallel import DataParallel, DistributedDataParallel
from torch.utils.data import DataLoader, TensorDataset, DistributedSampler
from torch.cuda.amp import autocast, GradScaler
import numpy as np
import logging
import traceback
import os
import time
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import threading
import queue
import matplotlib.pyplot as plt

from .production_transformers import DeviceManager
from .model_training import ModelTrainer, TrainingConfig, ModelType, TrainingMode
from .evaluation_metrics import (
    create_evaluation_metrics, create_metric_config, TaskType, MetricType
)

# Import code profiling system
try:
    from code_profiling_system import (
        CodeProfiler, DataLoadingProfiler, PreprocessingProfiler,
        ProfilingConfig, ProfilingResult, profile_function,
        profile_data_loading, profile_preprocessing
    )
    CODE_PROFILING_AVAILABLE = True
except ImportError:
    CODE_PROFILING_AVAILABLE = False
    print("Warning: Code profiling system not available. Install required dependencies.")

# Import experiment tracking system
try:
    from experiment_tracking_system import (
        ExperimentTracker, ExperimentConfig, create_experiment_config,
        experiment_context, track_experiment, start_tensorboard_server,
        compare_experiments, get_tensorboard_url
    )
    EXPERIMENT_TRACKING_AVAILABLE = True
except ImportError:
    EXPERIMENT_TRACKING_AVAILABLE = False
    print("Warning: Experiment tracking system not available. Install required dependencies.")

# Setup backend logging
logging.basicConfig(
    filename="gradio_app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

# =============================================================================
# MULTI-GPU TRAINING SYSTEM
# =============================================================================

@dataclass
class MultiGPUConfig:
    """Configuration for multi-GPU training"""
    
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


class MultiGPUTrainer:
    """Comprehensive multi-GPU training utilities for DataParallel and DistributedDataParallel."""
    
    def __init__(self, config: MultiGPUConfig = None):
        """Initialize multi-GPU trainer.
        
        Args:
            config: Multi-GPU configuration
        """
        self.config = config or MultiGPUConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Training state
        self.dp_initialized = False
        self.ddp_initialized = False
        self.current_strategy = None
        self.gpu_config = {}
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_queue = queue.Queue()
        
        logger.info(f"MultiGPUTrainer initialized on device: {self.device}")
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get comprehensive GPU information."""
        try:
            gpu_info = {
                'cuda_available': torch.cuda.is_available(),
                'gpu_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
                'current_device': torch.cuda.current_device() if torch.cuda.is_available() else None,
                'device_properties': [],
                'memory_info': {},
                'multi_gpu_available': False
            }
            
            if gpu_info['cuda_available']:
                gpu_info['multi_gpu_available'] = gpu_info['gpu_count'] > 1
                
                # Get device properties
                for i in range(gpu_info['gpu_count']):
                    props = torch.cuda.get_device_properties(i)
                    gpu_info['device_properties'].append({
                        'index': i,
                        'name': props.name,
                        'total_memory_gb': props.total_memory / (1024**3),
                        'compute_capability': f"{props.major}.{props.minor}",
                        'multi_processor_count': props.multi_processor_count
                    })
                
                # Get memory info for current device
                current_device = torch.cuda.current_device()
                gpu_info['memory_info'] = {
                    'allocated_gb': torch.cuda.memory_allocated(current_device) / (1024**3),
                    'reserved_gb': torch.cuda.memory_reserved(current_device) / (1024**3),
                    'total_gb': torch.cuda.get_device_properties(current_device).total_memory / (1024**3)
                }
            
            return gpu_info
            
        except Exception as e:
            logger.error(f"Error getting GPU info: {e}")
            return {'error': str(e)}
    
    def setup_data_parallel(self, model: torch.nn.Module, device_ids: List[int] = None) -> Tuple[torch.nn.Module, bool]:
        """Setup DataParallel for multi-GPU training."""
        try:
            if not torch.cuda.is_available():
                logger.warning("CUDA not available, skipping DataParallel setup")
                return model, False
            
            gpu_count = torch.cuda.device_count()
            if gpu_count < 2:
                logger.warning(f"Only {gpu_count} GPU available, skipping DataParallel setup")
                return model, False
            
            # Determine device IDs
            if device_ids is None:
                device_ids = list(range(gpu_count))
            else:
                device_ids = [i for i in device_ids if i < gpu_count]
            
            if len(device_ids) < 2:
                logger.warning(f"Only {len(device_ids)} valid GPU IDs provided, skipping DataParallel setup")
                return model, False
            
            # Move model to first GPU
            model = model.to(f'cuda:{device_ids[0]}')
            
            # Setup DataParallel
            model = torch.nn.DataParallel(model, device_ids=device_ids)
            
            self.dp_initialized = True
            self.current_strategy = 'DataParallel'
            self.gpu_config = {
                'strategy': 'DataParallel',
                'device_ids': device_ids,
                'gpu_count': len(device_ids),
                'setup_time': datetime.now().isoformat()
            }
            
            logger.info(f"✅ DataParallel setup completed with {len(device_ids)} GPUs: {device_ids}")
            return model, True
            
        except Exception as e:
            logger.error(f"Failed to setup DataParallel: {e}")
            return model, False
    
    def setup_distributed_data_parallel(self, model: torch.nn.Module, 
                                      backend: str = 'nccl',
                                      init_method: str = 'env://',
                                      world_size: int = None,
                                      rank: int = None,
                                      device_ids: List[int] = None) -> Tuple[torch.nn.Module, bool]:
        """Setup DistributedDataParallel for multi-GPU training."""
        try:
            if not torch.cuda.is_available():
                logger.warning("CUDA not available, skipping DistributedDataParallel setup")
                return model, False
            
            gpu_count = torch.cuda.device_count()
            if gpu_count < 2:
                logger.warning(f"Only {gpu_count} GPU available, skipping DistributedDataParallel setup")
                return model, False
            
            # Initialize distributed process group if not already initialized
            if not dist.is_initialized():
                # Set environment variables if not provided
                if world_size is None:
                    world_size = gpu_count
                if rank is None:
                    rank = 0
                
                # Set environment variables for distributed training
                os.environ['WORLD_SIZE'] = str(world_size)
                os.environ['RANK'] = str(rank)
                os.environ['MASTER_ADDR'] = 'localhost'
                os.environ['MASTER_PORT'] = '12355'
                
                # Initialize process group
                dist.init_process_group(
                    backend=backend,
                    init_method=init_method,
                    world_size=world_size,
                    rank=rank
                )
                
                self.ddp_initialized = True
                logger.info(f"✅ Distributed process group initialized: backend={backend}, world_size={world_size}, rank={rank}")
            
            # Determine device IDs
            if device_ids is None:
                device_ids = list(range(gpu_count))
            else:
                device_ids = [i for i in device_ids if i < gpu_count]
            
            if len(device_ids) < 2:
                logger.warning(f"Only {len(device_ids)} valid GPU IDs provided, skipping DistributedDataParallel setup")
                return model, False
            
            # Move model to first GPU
            model = model.to(f'cuda:{device_ids[0]}')
            
            # Setup DistributedDataParallel
            model = torch.nn.parallel.DistributedDataParallel(
                model,
                device_ids=device_ids,
                output_device=device_ids[0],
                find_unused_parameters=False,
                broadcast_buffers=True
            )
            
            self.current_strategy = 'DistributedDataParallel'
            self.gpu_config = {
                'strategy': 'DistributedDataParallel',
                'device_ids': device_ids,
                'gpu_count': len(device_ids),
                'backend': backend,
                'world_size': world_size,
                'rank': rank,
                'setup_time': datetime.now().isoformat()
            }
            
            logger.info(f"✅ DistributedDataParallel setup completed with {len(device_ids)} GPUs: {device_ids}")
            return model, True
            
        except Exception as e:
            logger.error(f"Failed to setup DistributedDataParallel: {e}")
            return model, False
    
    def setup_multi_gpu(self, model: torch.nn.Module, 
                       strategy: str = 'auto',
                       device_ids: List[int] = None,
                       ddp_backend: str = 'nccl',
                       ddp_init_method: str = 'env://') -> Tuple[torch.nn.Module, bool, Dict[str, Any]]:
        """Setup multi-GPU training with automatic strategy selection."""
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
    
    def train_with_multi_gpu(self, model: torch.nn.Module,
                            train_loader: torch.utils.data.DataLoader,
                            optimizer: torch.optim.Optimizer,
                            criterion: torch.nn.Module,
                            num_epochs: int = 10,
                            strategy: str = 'auto',
                            device_ids: List[int] = None,
                            use_mixed_precision: bool = True,
                            gradient_accumulation_steps: int = 1) -> Dict[str, Any]:
        """Train model using multi-GPU with comprehensive monitoring."""
        try:
            # Setup multi-GPU
            model, multi_gpu_success, gpu_info = self.setup_multi_gpu(model, strategy, device_ids)
            
            if not multi_gpu_success:
                logger.warning("Multi-GPU setup failed, using single GPU")
            
            # Setup mixed precision
            scaler = GradScaler() if use_mixed_precision and torch.cuda.is_available() else None
            
            # Training metrics
            training_metrics = {
                'epochs': [],
                'train_losses': [],
                'gpu_utilization': [],
                'memory_usage': [],
                'training_time': [],
                'multi_gpu_info': gpu_info,
                'strategy_used': self.current_strategy
            }
            
            # Start monitoring
            self.start_monitoring()
            
            model.train()
            total_start_time = time.time()
            
            for epoch in range(num_epochs):
                epoch_start_time = time.time()
                epoch_loss = 0.0
                num_batches = 0
                
                # Reset gradients
                optimizer.zero_grad()
                
                for batch_idx, (data, target) in enumerate(train_loader):
                    # Move data to device
                    if isinstance(data, torch.Tensor):
                        data = data.to(self.device)
                    if isinstance(target, torch.Tensor):
                        target = target.to(self.device)
                    
                    # Forward pass with mixed precision
                    if scaler:
                        with autocast():
                            output = model(data)
                            loss = criterion(output, target)
                        
                        # Scale loss and backward pass
                        scaler.scale(loss).backward()
                        
                        # Gradient accumulation
                        if (batch_idx + 1) % gradient_accumulation_steps == 0:
                            scaler.step(optimizer)
                            scaler.update()
                            optimizer.zero_grad()
                    else:
                        output = model(data)
                        loss = criterion(output, target)
                        loss.backward()
                        
                        # Gradient accumulation
                        if (batch_idx + 1) % gradient_accumulation_steps == 0:
                            optimizer.step()
                            optimizer.zero_grad()
                    
                    epoch_loss += loss.item()
                    num_batches += 1
                
                # Calculate epoch metrics
                avg_loss = epoch_loss / num_batches if num_batches > 0 else 0.0
                epoch_time = time.time() - epoch_start_time
                
                # Record metrics
                training_metrics['epochs'].append(epoch + 1)
                training_metrics['train_losses'].append(avg_loss)
                training_metrics['training_time'].append(epoch_time)
                
                # Get GPU metrics
                if torch.cuda.is_available():
                    gpu_metrics = self.get_gpu_metrics()
                    training_metrics['gpu_utilization'].append(gpu_metrics.get('utilization', 0))
                    training_metrics['memory_usage'].append(gpu_metrics.get('memory_used_gb', 0))
                
                logger.info(f"Epoch {epoch + 1}/{num_epochs}: Loss = {avg_loss:.4f}, Time = {epoch_time:.2f}s")
            
            total_time = time.time() - total_start_time
            training_metrics['total_training_time'] = total_time
            training_metrics['final_loss'] = training_metrics['train_losses'][-1] if training_metrics['train_losses'] else 0.0
            
            # Stop monitoring
            self.stop_monitoring()
            
            logger.info(f"✅ Multi-GPU training completed in {total_time:.2f}s")
            return training_metrics
            
        except Exception as e:
            logger.error(f"Multi-GPU training failed: {e}")
            self.stop_monitoring()
            return {'error': str(e)}
    
    def evaluate_with_multi_gpu(self, model: torch.nn.Module,
                               test_loader: torch.utils.data.DataLoader,
                               criterion: torch.nn.Module,
                               strategy: str = 'auto',
                               device_ids: List[int] = None) -> Dict[str, Any]:
        """Evaluate model using multi-GPU with comprehensive monitoring."""
        try:
            # Setup multi-GPU
            model, multi_gpu_success, gpu_info = self.setup_multi_gpu(model, strategy, device_ids)
            
            if not multi_gpu_success:
                logger.warning("Multi-GPU setup failed, using single GPU")
            
            # Evaluation metrics
            evaluation_metrics = {
                'test_loss': 0.0,
                'num_samples': 0,
                'gpu_utilization': [],
                'memory_usage': [],
                'evaluation_time': 0.0,
                'multi_gpu_info': gpu_info,
                'strategy_used': self.current_strategy
            }
            
            # Start monitoring
            self.start_monitoring()
            
            model.eval()
            start_time = time.time()
            
            with torch.no_grad():
                for batch_idx, (data, target) in enumerate(test_loader):
                    # Move data to device
                    if isinstance(data, torch.Tensor):
                        data = data.to(self.device)
                    if isinstance(target, torch.Tensor):
                        target = target.to(self.device)
                    
                    # Forward pass
                    output = model(data)
                    loss = criterion(output, target)
                    
                    # Accumulate metrics
                    evaluation_metrics['test_loss'] += loss.item() * data.size(0)
                    evaluation_metrics['num_samples'] += data.size(0)
                    
                    # Get GPU metrics
                    if torch.cuda.is_available():
                        gpu_metrics = self.get_gpu_metrics()
                        evaluation_metrics['gpu_utilization'].append(gpu_metrics.get('utilization', 0))
                        evaluation_metrics['memory_usage'].append(gpu_metrics.get('memory_used_gb', 0))
            
            # Calculate final metrics
            evaluation_metrics['test_loss'] /= evaluation_metrics['num_samples']
            evaluation_metrics['evaluation_time'] = time.time() - start_time
            
            # Stop monitoring
            self.stop_monitoring()
            
            logger.info(f"✅ Multi-GPU evaluation completed: Loss = {evaluation_metrics['test_loss']:.4f}")
            return evaluation_metrics
            
        except Exception as e:
            logger.error(f"Multi-GPU evaluation failed: {e}")
            self.stop_monitoring()
            return {'error': str(e)}
    
    def get_gpu_metrics(self) -> Dict[str, float]:
        """Get current GPU metrics."""
        try:
            if not torch.cuda.is_available():
                return {}
            
            metrics = {}
            current_device = torch.cuda.current_device()
            
            # Memory metrics
            metrics['memory_allocated_gb'] = torch.cuda.memory_allocated(current_device) / (1024**3)
            metrics['memory_reserved_gb'] = torch.cuda.memory_reserved(current_device) / (1024**3)
            metrics['memory_used_gb'] = metrics['memory_allocated_gb']
            
            # Utilization (simplified - in production you'd use nvidia-ml-py)
            metrics['utilization'] = 0.0  # Placeholder
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting GPU metrics: {e}")
            return {}
    
    def start_monitoring(self):
        """Start GPU monitoring in background thread."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("GPU monitoring started")
    
    def stop_monitoring(self):
        """Stop GPU monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("GPU monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                metrics = self.get_gpu_metrics()
                self.monitoring_queue.put({
                    'timestamp': datetime.now().isoformat(),
                    'metrics': metrics
                })
                time.sleep(1)  # Monitor every second
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                break
    
    def get_multi_gpu_status(self) -> Dict[str, Any]:
        """Get comprehensive multi-GPU status and metrics."""
        try:
            status = {
                'gpu_info': self.get_gpu_info(),
                'current_strategy': self.current_strategy,
                'gpu_config': self.gpu_config,
                'monitoring_active': self.monitoring_active,
                'current_metrics': self.get_gpu_metrics()
            }
            
            # Get monitoring history
            monitoring_history = []
            while not self.monitoring_queue.empty():
                try:
                    monitoring_history.append(self.monitoring_queue.get_nowait())
                except queue.Empty:
                    break
            
            status['monitoring_history'] = monitoring_history
            return status
            
        except Exception as e:
            logger.error(f"Error getting multi-GPU status: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Cleanup multi-GPU resources."""
        try:
            self.stop_monitoring()
            
            if self.ddp_initialized and dist.is_initialized():
                dist.destroy_process_group()
                logger.info("Distributed process group destroyed")
            
            # Clear GPU cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.info("GPU cache cleared")
            
            logger.info("Multi-GPU cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global multi-GPU trainer instance
multi_gpu_trainer = MultiGPUTrainer()

# =============================================================================
# ENHANCED GRADIO FUNCTIONS
# =============================================================================

def load_demo_model(model_path: str = None):
    try:
        model = torch.nn.Linear(10, 2)
        return model
    except Exception as e:
        logging.error(f"Error loading model: {e}\n{traceback.format_exc()}")
        raise RuntimeError("Failed to load model.")

def preprocess_input(input_data: List[float]) -> torch.Tensor:
    try:
        if not isinstance(input_data, list):
            raise ValueError("Input must be a list of 10 floats.")
        if len(input_data) != 10:
            raise ValueError(f"Input must have 10 features, got {len(input_data)}.")
        for i, v in enumerate(input_data):
            if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
                raise ValueError(f"Feature {i+1} is missing or invalid (NaN/Inf). Please provide all 10 valid numbers.")
            if not isinstance(v, (int, float)):
                raise ValueError(f"Feature {i+1} is not a number.")
        return torch.tensor([input_data], dtype=torch.float32)
    except Exception as e:
        logging.error(f"Input validation error: {e}\n{traceback.format_exc()}")
        raise

def predict(model, input_tensor: torch.Tensor) -> Tuple[int, np.ndarray]:
    try:
        with torch.no_grad():
            logits = model(input_tensor)
            if torch.isnan(logits).any() or torch.isinf(logits).any():
                raise ValueError("Model output contains NaN or Inf values. Please check your model.")
            probabilities = torch.softmax(logits, dim=-1).cpu().numpy()[0]
            pred_class = int(np.argmax(probabilities))
        return pred_class, probabilities
    except Exception as e:
        logging.error(f"Model inference error: {e}\n{traceback.format_exc()}")
        raise

def evaluate_sample(model, input_data: List[float], true_label: int = None, debug: bool = False) -> Dict[str, Any]:
    try:
        input_tensor = preprocess_input(input_data)
        pred_class, probabilities = predict(model, input_tensor)
        result = {
            "Predicted Class": pred_class,
            "Probabilities": probabilities.tolist()
        }
        if true_label is not None:
            if not isinstance(true_label, (int, float)) or np.isnan(true_label) or np.isinf(true_label):
                result["Error"] = "True label must be a valid integer."
                return result
            true_label_int = int(true_label)
            if true_label_int < 0 or true_label_int >= len(probabilities):
                result["Error"] = f"True label must be between 0 and {len(probabilities)-1}."
                return result
            try:
                device_manager = DeviceManager()
                evaluator = create_evaluation_metrics(device_manager)
                config = create_metric_config(
                    task_type=TaskType.CLASSIFICATION,
                    metric_types=[MetricType.ACCURACY, MetricType.PRECISION, MetricType.RECALL, MetricType.F1]
                )
                y_true = np.array([true_label_int])
                y_pred = np.array([pred_class])
                y_prob = np.array([probabilities])
                eval_result = evaluator.evaluate(config, y_true, y_pred, y_prob)
                for k, v in eval_result.metrics.items():
                    result[k] = v
            except Exception as e:
                logging.error(f"Metrics calculation error: {e}\n{traceback.format_exc()}")
                result["Error"] = f"Metrics calculation error: {e}"
                if debug:
                    result["Traceback"] = traceback.format_exc()
        return result
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Evaluation error: {e}\n{tb}")
        if debug:
            return {"Error": str(e), "Traceback": tb}
        else:
            return {"Error": str(e)}

def gradio_interface(input_data, true_label, debug):
    try:
        model = gr.themes.utils.get_or_create("demo_model", load_demo_model)
        # Flatten input_data if it's a DataFrame (list of lists)
        if isinstance(input_data, list) and len(input_data) == 1 and isinstance(input_data[0], list):
            input_data = input_data[0]
        return evaluate_sample(model, input_data, true_label, debug)
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Top-level Gradio error: {e}\n{tb}")
        if debug:
            return {"Error": f"Unexpected error: {str(e)}", "Traceback": tb}
        else:
            return {"Error": f"Unexpected error: {str(e)}"}

# =============================================================================
# MULTI-GPU TRAINING INTERFACE
# =============================================================================

def get_gpu_info_interface():
    """Get GPU information for the interface."""
    try:
        gpu_info = multi_gpu_trainer.get_gpu_info()
        return json.dumps(gpu_info, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

def train_model_interface(model_type: str, num_epochs: int, batch_size: int, 
                         learning_rate: float, strategy: str, use_mixed_precision: bool) -> str:
    """Train model using multi-GPU for the interface."""
    try:
        # Create a simple model for demonstration
        if model_type == "linear":
            model = torch.nn.Linear(10, 2)
        elif model_type == "mlp":
            model = torch.nn.Sequential(
                torch.nn.Linear(10, 64),
                torch.nn.ReLU(),
                torch.nn.Linear(64, 32),
                torch.nn.ReLU(),
                torch.nn.Linear(32, 2)
            )
        else:
            model = torch.nn.Linear(10, 2)
        
        # Create dummy dataset
        X = torch.randn(1000, 10)
        y = torch.randint(0, 2, (1000,))
        dataset = TensorDataset(X, y)
        
        # Create data loader
        train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Setup optimizer and loss
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        criterion = torch.nn.CrossEntropyLoss()
        
        # Train with multi-GPU
        training_metrics = multi_gpu_trainer.train_with_multi_gpu(
            model=model,
            train_loader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            num_epochs=num_epochs,
            strategy=strategy,
            use_mixed_precision=use_mixed_precision
        )
        
        return json.dumps(training_metrics, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Training error: {e}")
        return json.dumps({"error": str(e)}, indent=2)

def get_multi_gpu_status_interface() -> str:
    """Get multi-GPU status for the interface."""
    try:
        status = multi_gpu_trainer.get_multi_gpu_status()
        return json.dumps(status, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# =============================================================================
# CODE PROFILING INTERFACE FUNCTIONS
# =============================================================================

def profile_function_interface(function_name: str, profile_type: str, 
                              enable_gpu_profiling: bool, enable_memory_profiling: bool,
                              num_iterations: int) -> str:
    """Profile a specific function for the interface."""
    if not CODE_PROFILING_AVAILABLE:
        return json.dumps({"error": "Code profiling system not available"}, indent=2)
    
    try:
        # Create profiling configuration
        config = ProfilingConfig(
            enable_gpu_profiling=enable_gpu_profiling,
            enable_memory_profiling=enable_memory_profiling,
            num_iterations=num_iterations,
            export_results=True
        )
        
        # Get the function to profile based on function_name
        if function_name == "preprocess_input":
            func = preprocess_input
        elif function_name == "predict":
            func = predict
        elif function_name == "evaluate_sample":
            func = evaluate_sample
        elif function_name == "gradio_interface":
            func = gradio_interface
        else:
            return json.dumps({"error": f"Unknown function: {function_name}"}, indent=2)
        
        # Create profiler and run profiling
        profiler = CodeProfiler(config)
        
        if profile_type == "function":
            result = profiler.profile_function(func, "test_input", config)
        elif profile_type == "data_loading":
            result = profiler.profile_data_loading(func, "test_input", config)
        elif profile_type == "preprocessing":
            result = profiler.profile_preprocessing(func, "test_input", config)
        else:
            return json.dumps({"error": f"Unknown profile type: {profile_type}"}, indent=2)
        
        return json.dumps(result.to_dict(), indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in function profiling: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def profile_data_loading_interface(dataset_size: int, batch_size: int,
                                  enable_gpu_profiling: bool, enable_memory_profiling: bool) -> str:
    """Profile data loading operations for the interface."""
    if not CODE_PROFILING_AVAILABLE:
        return json.dumps({"error": "Code profiling system not available"}, indent=2)
    
    try:
        # Create profiling configuration
        config = ProfilingConfig(
            enable_gpu_profiling=enable_gpu_profiling,
            enable_memory_profiling=enable_memory_profiling,
            num_iterations=10,
            export_results=True
        )
        
        # Create sample data
        sample_data = torch.randn(dataset_size, 10)
        sample_labels = torch.randint(0, 2, (dataset_size,))
        
        # Create DataLoader
        dataset = TensorDataset(sample_data, sample_labels)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Create data loading profiler
        profiler = DataLoadingProfiler(config)
        
        # Profile data loading
        result = profiler.profile_dataloader(dataloader, num_epochs=2)
        
        return json.dumps(result.to_dict(), indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in data loading profiling: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def profile_preprocessing_interface(input_size: int, enable_gpu_profiling: bool,
                                   enable_memory_profiling: bool, num_iterations: int) -> str:
    """Profile preprocessing operations for the interface."""
    if not CODE_PROFILING_AVAILABLE:
        return json.dumps({"error": "Code profiling system not available"}, indent=2)
    
    try:
        # Create profiling configuration
        config = ProfilingConfig(
            enable_gpu_profiling=enable_gpu_profiling,
            enable_memory_profiling=enable_memory_profiling,
            num_iterations=num_iterations,
            export_results=True
        )
        
        # Create sample input data
        sample_input = [float(i) for i in range(input_size)]
        
        # Create preprocessing profiler
        profiler = PreprocessingProfiler(config)
        
        # Profile preprocessing
        result = profiler.profile_preprocessing_function(preprocess_input, sample_input)
        
        return json.dumps(result.to_dict(), indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in preprocessing profiling: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def analyze_bottlenecks_interface(profile_results: str) -> str:
    """Analyze bottlenecks from profiling results for the interface."""
    if not CODE_PROFILING_AVAILABLE:
        return json.dumps({"error": "Code profiling system not available"}, indent=2)
    
    try:
        # Parse profile results
        results = json.loads(profile_results)
        
        # Create profiler for analysis
        profiler = CodeProfiler()
        
        # Analyze bottlenecks
        analysis = profiler.analyze_bottlenecks(results)
        
        return json.dumps(analysis, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error in bottleneck analysis: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def get_profiling_recommendations_interface() -> str:
    """Get profiling recommendations for the interface."""
    if not CODE_PROFILING_AVAILABLE:
        return json.dumps({"error": "Code profiling system not available"}, indent=2)
    
    try:
        # Create profiler for recommendations
        profiler = CodeProfiler()
        
        # Get recommendations
        recommendations = profiler.get_optimization_recommendations()
        
        return json.dumps(recommendations, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error getting profiling recommendations: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def export_profiling_results_interface(profile_results: str, export_format: str) -> str:
    """Export profiling results for the interface."""
    if not CODE_PROFILING_AVAILABLE:
        return json.dumps({"error": "Code profiling system not available"}, indent=2)
    
    try:
        # Parse profile results
        results = json.loads(profile_results)
        
        # Create profiler for export
        profiler = CodeProfiler()
        
        # Export results
        export_path = profiler.export_results(results, export_format)
        
        return json.dumps({"export_path": export_path, "format": export_format}, indent=2)
        
    except Exception as e:
        logger.error(f"Error exporting profiling results: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

# =============================================================================
# EXPERIMENT TRACKING INTERFACE FUNCTIONS
# =============================================================================

def start_experiment_tracking_interface(experiment_name: str, project_name: str,
                                       enable_tensorboard: bool, enable_wandb: bool,
                                       wandb_entity: str, tags: str) -> str:
    """Start experiment tracking for the interface."""
    if not EXPERIMENT_TRACKING_AVAILABLE:
        return json.dumps({"error": "Experiment tracking system not available"}, indent=2)
    
    try:
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        # Create experiment configuration
        config = create_experiment_config(
            experiment_name=experiment_name,
            project_name=project_name,
            enable_tensorboard=enable_tensorboard,
            enable_wandb=enable_wandb,
            wandb_entity=wandb_entity if wandb_entity else None,
            tags=tag_list,
            log_interval=10,
            save_interval=100
        )
        
        # Create global tracker instance
        global experiment_tracker
        experiment_tracker = ExperimentTracker(config)
        
        # Log initial configuration
        experiment_tracker.log_hyperparameters({
            'experiment_name': experiment_name,
            'project_name': project_name,
            'enable_tensorboard': enable_tensorboard,
            'enable_wandb': enable_wandb,
            'tags': tag_list
        })
        
        return json.dumps({
            "status": "started",
            "experiment_name": experiment_name,
            "project_name": project_name,
            "tensorboard_enabled": enable_tensorboard,
            "wandb_enabled": enable_wandb,
            "tags": tag_list
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error starting experiment tracking: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def log_training_metrics_interface(loss: float, accuracy: float, learning_rate: float,
                                  epoch: int, step: int) -> str:
    """Log training metrics for the interface."""
    if not EXPERIMENT_TRACKING_AVAILABLE:
        return json.dumps({"error": "Experiment tracking system not available"}, indent=2)
    
    try:
        global experiment_tracker
        if not hasattr(globals(), 'experiment_tracker') or experiment_tracker is None:
            return json.dumps({"error": "No active experiment tracker"}, indent=2)
        
        # Log training step
        experiment_tracker.log_training_step(
            loss=loss,
            accuracy=accuracy,
            learning_rate=learning_rate
        )
        
        # Log epoch if provided
        if epoch is not None:
            experiment_tracker.log_epoch(epoch)
        
        # Update step counter
        experiment_tracker.step = step
        
        return json.dumps({
            "status": "logged",
            "step": step,
            "epoch": epoch,
            "loss": loss,
            "accuracy": accuracy,
            "learning_rate": learning_rate
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error logging training metrics: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def log_validation_metrics_interface(loss: float, accuracy: float, precision: float,
                                    recall: float, f1: float) -> str:
    """Log validation metrics for the interface."""
    if not EXPERIMENT_TRACKING_AVAILABLE:
        return json.dumps({"error": "Experiment tracking system not available"}, indent=2)
    
    try:
        global experiment_tracker
        if not hasattr(globals(), 'experiment_tracker') or experiment_tracker is None:
            return json.dumps({"error": "No active experiment tracker"}, indent=2)
        
        # Log validation step
        experiment_tracker.log_validation_step(
            loss=loss,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1
        )
        
        return json.dumps({
            "status": "logged",
            "loss": loss,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error logging validation metrics: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def log_model_checkpoint_interface(model_type: str, epoch: int, step: int,
                                  train_loss: float, val_loss: float) -> str:
    """Log model checkpoint for the interface."""
    if not EXPERIMENT_TRACKING_AVAILABLE:
        return json.dumps({"error": "Experiment tracking system not available"}, indent=2)
    
    try:
        global experiment_tracker
        if not hasattr(globals(), 'experiment_tracker') or experiment_tracker is None:
            return json.dumps({"error": "No active experiment tracker"}, indent=2)
        
        # Create a simple model for demonstration
        if model_type == "linear":
            model = torch.nn.Linear(10, 2)
        elif model_type == "mlp":
            model = torch.nn.Sequential(
                torch.nn.Linear(10, 64),
                torch.nn.ReLU(),
                torch.nn.Linear(64, 2)
            )
        else:
            model = torch.nn.Linear(10, 2)
        
        # Log model checkpoint
        experiment_tracker.log_model_checkpoint(
            model=model,
            epoch=epoch,
            step=step,
            metrics={
                'train_loss': train_loss,
                'val_loss': val_loss,
                'model_type': model_type
            }
        )
        
        return json.dumps({
            "status": "checkpoint_saved",
            "model_type": model_type,
            "epoch": epoch,
            "step": step,
            "train_loss": train_loss,
            "val_loss": val_loss
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error logging model checkpoint: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def get_experiment_summary_interface() -> str:
    """Get experiment summary for the interface."""
    if not EXPERIMENT_TRACKING_AVAILABLE:
        return json.dumps({"error": "Experiment tracking system not available"}, indent=2)
    
    try:
        global experiment_tracker
        if not hasattr(globals(), 'experiment_tracker') or experiment_tracker is None:
            return json.dumps({"error": "No active experiment tracker"}, indent=2)
        
        # Get experiment summary
        summary = experiment_tracker.get_experiment_summary()
        
        return json.dumps(summary, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error getting experiment summary: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def finish_experiment_interface() -> str:
    """Finish experiment tracking for the interface."""
    if not EXPERIMENT_TRACKING_AVAILABLE:
        return json.dumps({"error": "Experiment tracking system not available"}, indent=2)
    
    try:
        global experiment_tracker
        if not hasattr(globals(), 'experiment_tracker') or experiment_tracker is None:
            return json.dumps({"error": "No active experiment tracker"}, indent=2)
        
        # Finish experiment
        experiment_tracker.finish()
        
        # Get final summary
        summary = experiment_tracker.get_experiment_summary()
        
        # Clear global tracker
        experiment_tracker = None
        
        return json.dumps({
            "status": "finished",
            "summary": summary
        }, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error finishing experiment: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def start_tensorboard_server_interface(log_dir: str, port: int) -> str:
    """Start TensorBoard server for the interface."""
    if not EXPERIMENT_TRACKING_AVAILABLE:
        return json.dumps({"error": "Experiment tracking system not available"}, indent=2)
    
    try:
        # Start TensorBoard server
        success = start_tensorboard_server(log_dir, port)
        
        if success:
            url = get_tensorboard_url(log_dir)
            return json.dumps({
                "status": "started",
                "url": url,
                "log_dir": log_dir,
                "port": port
            }, indent=2)
        else:
            return json.dumps({"error": "Failed to start TensorBoard server"}, indent=2)
        
    except Exception as e:
        logger.error(f"Error starting TensorBoard server: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

def compare_experiments_interface(experiment_names: str, metric: str) -> str:
    """Compare multiple experiments for the interface."""
    if not EXPERIMENT_TRACKING_AVAILABLE:
        return json.dumps({"error": "Experiment tracking system not available"}, indent=2)
    
    try:
        # Parse experiment names
        exp_list = [name.strip() for name in experiment_names.split(',') if name.strip()]
        
        if len(exp_list) < 2:
            return json.dumps({"error": "At least 2 experiment names required"}, indent=2)
        
        # Create comparison plot
        fig = compare_experiments(exp_list, metric)
        
        if fig:
            # Save plot
            plot_path = f"experiment_comparison_{metric}.png"
            fig.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            return json.dumps({
                "status": "completed",
                "experiment_names": exp_list,
                "metric": metric,
                "plot_path": plot_path
            }, indent=2)
        else:
            return json.dumps({"error": "Failed to create comparison plot"}, indent=2)
        
    except Exception as e:
        logger.error(f"Error comparing experiments: {str(e)}")
        return json.dumps({"error": str(e)}, indent=2)

# =============================================================================
# GRADIO INTERFACE
# =============================================================================

with gr.Blocks(title="Blatam Academy Model Demo") as demo:
    gr.Markdown("""
    # 🤖 Blatam Academy Model Inference & Evaluation
    Upload or input your data, select the task, and get instant predictions and metrics!
    
    ## 🚀 Multi-GPU Training Support
    This app now includes comprehensive multi-GPU training support using DataParallel and DistributedDataParallel.
    """)
    
    with gr.Tab("Model Inference"):
    with gr.Row():
        input_data = gr.Dataframe(
            headers=[f"f{i}" for i in range(10)],
            datatype="number",
            label="Input Features (10 floats)",
            value=[[0.0]*10]
        )
        true_label = gr.Number(label="True Label (optional)", value=None)
        debug_mode = gr.Checkbox(label="Show Debug Info", value=False)
    output = gr.JSON(label="Prediction & Metrics")
    btn = gr.Button("Run Inference & Evaluate")
    btn.click(fn=gradio_interface, inputs=[input_data, true_label, debug_mode], outputs=output)
    
    with gr.Tab("Multi-GPU Training"):
        gr.Markdown("### 🚀 Multi-GPU Training Interface")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Training Configuration")
                model_type = gr.Dropdown(
                    choices=["linear", "mlp"],
                    value="linear",
                    label="Model Type"
                )
                num_epochs = gr.Slider(
                    minimum=1, maximum=50, value=10, step=1,
                    label="Number of Epochs"
                )
                batch_size = gr.Slider(
                    minimum=8, maximum=128, value=32, step=8,
                    label="Batch Size"
                )
                learning_rate = gr.Slider(
                    minimum=1e-5, maximum=1e-2, value=1e-4, step=1e-5,
                    label="Learning Rate"
                )
                strategy = gr.Dropdown(
                    choices=["auto", "DataParallel", "DistributedDataParallel"],
                    value="auto",
                    label="Multi-GPU Strategy"
                )
                use_mixed_precision = gr.Checkbox(
                    value=True,
                    label="Use Mixed Precision"
                )
                train_btn = gr.Button("🚀 Start Multi-GPU Training", variant="primary")
            
            with gr.Column():
                gr.Markdown("#### System Information")
                gpu_info_btn = gr.Button("📊 Get GPU Info")
                gpu_info_output = gr.JSON(label="GPU Information")
                gpu_info_btn.click(fn=get_gpu_info_interface, outputs=gpu_info_output)
                
                status_btn = gr.Button("📈 Get Multi-GPU Status")
                status_output = gr.JSON(label="Multi-GPU Status")
                status_btn.click(fn=get_multi_gpu_status_interface, outputs=status_output)
        
        training_output = gr.JSON(label="Training Results")
        train_btn.click(
            fn=train_model_interface,
            inputs=[model_type, num_epochs, batch_size, learning_rate, strategy, use_mixed_precision],
            outputs=training_output
        )
    
    with gr.Tab("Code Profiling"):
        gr.Markdown("### 🔍 Code Profiling & Performance Analysis")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Function Profiling")
                function_name = gr.Dropdown(
                    choices=["preprocess_input", "predict", "evaluate_sample", "gradio_interface"],
                    value="preprocess_input",
                    label="Function to Profile"
                )
                profile_type = gr.Dropdown(
                    choices=["function", "data_loading", "preprocessing"],
                    value="function",
                    label="Profile Type"
                )
                enable_gpu_profiling = gr.Checkbox(
                    value=True,
                    label="Enable GPU Profiling"
                )
                enable_memory_profiling = gr.Checkbox(
                    value=True,
                    label="Enable Memory Profiling"
                )
                num_iterations = gr.Slider(
                    minimum=1, maximum=100, value=10, step=1,
                    label="Number of Iterations"
                )
                profile_function_btn = gr.Button("🔍 Profile Function", variant="primary")
            
            with gr.Column():
                gr.Markdown("#### Data Loading Profiling")
                dataset_size = gr.Slider(
                    minimum=100, maximum=10000, value=1000, step=100,
                    label="Dataset Size"
                )
                batch_size_profiling = gr.Slider(
                    minimum=8, maximum=256, value=32, step=8,
                    label="Batch Size"
                )
                profile_data_loading_btn = gr.Button("📊 Profile Data Loading", variant="primary")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Preprocessing Profiling")
                input_size = gr.Slider(
                    minimum=5, maximum=100, value=10, step=1,
                    label="Input Size"
                )
                profile_preprocessing_btn = gr.Button("⚙️ Profile Preprocessing", variant="primary")
            
            with gr.Column():
                gr.Markdown("#### Analysis & Export")
                analyze_bottlenecks_btn = gr.Button("🔍 Analyze Bottlenecks")
                get_recommendations_btn = gr.Button("💡 Get Recommendations")
                export_format = gr.Dropdown(
                    choices=["json", "csv", "html"],
                    value="json",
                    label="Export Format"
                )
                export_results_btn = gr.Button("📤 Export Results")
        
        # Outputs
        function_profiling_output = gr.JSON(label="Function Profiling Results")
        data_loading_profiling_output = gr.JSON(label="Data Loading Profiling Results")
        preprocessing_profiling_output = gr.JSON(label="Preprocessing Profiling Results")
        bottleneck_analysis_output = gr.JSON(label="Bottleneck Analysis")
        recommendations_output = gr.JSON(label="Optimization Recommendations")
        export_output = gr.JSON(label="Export Results")
        
        # Event handlers
        profile_function_btn.click(
            fn=profile_function_interface,
            inputs=[function_name, profile_type, enable_gpu_profiling, enable_memory_profiling, num_iterations],
            outputs=function_profiling_output,
            show_progress=True
        )
        
        profile_data_loading_btn.click(
            fn=profile_data_loading_interface,
            inputs=[dataset_size, batch_size_profiling, enable_gpu_profiling, enable_memory_profiling],
            outputs=data_loading_profiling_output,
            show_progress=True
        )
        
        profile_preprocessing_btn.click(
            fn=profile_preprocessing_interface,
            inputs=[input_size, enable_gpu_profiling, enable_memory_profiling, num_iterations],
            outputs=preprocessing_profiling_output,
            show_progress=True
        )
        
        analyze_bottlenecks_btn.click(
            fn=analyze_bottlenecks_interface,
            inputs=[function_profiling_output],
            outputs=bottleneck_analysis_output
        )
        
        get_recommendations_btn.click(
            fn=get_profiling_recommendations_interface,
            outputs=recommendations_output
        )
        
        export_results_btn.click(
            fn=export_profiling_results_interface,
            inputs=[function_profiling_output, export_format],
            outputs=export_output
        )
    
    with gr.Tab("Experiment Tracking"):
        gr.Markdown("### 🔬 Experiment Tracking with TensorBoard & Weights & Biases")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Start Experiment")
                experiment_name = gr.Textbox(
                    value="gradio_experiment",
                    label="Experiment Name"
                )
                project_name = gr.Textbox(
                    value="blatam_academy",
                    label="Project Name"
                )
                enable_tensorboard = gr.Checkbox(
                    value=True,
                    label="Enable TensorBoard"
                )
                enable_wandb = gr.Checkbox(
                    value=True,
                    label="Enable Weights & Biases"
                )
                wandb_entity = gr.Textbox(
                    value="",
                    label="WandB Entity (username, optional)"
                )
                tags = gr.Textbox(
                    value="gradio,demo,experiment",
                    label="Tags (comma-separated)"
                )
                start_experiment_btn = gr.Button("🚀 Start Experiment", variant="primary")
            
            with gr.Column():
                gr.Markdown("#### TensorBoard Server")
                tensorboard_log_dir = gr.Textbox(
                    value="runs/tensorboard",
                    label="Log Directory"
                )
                tensorboard_port = gr.Slider(
                    minimum=6006, maximum=6100, value=6006, step=1,
                    label="Port"
                )
                start_tensorboard_btn = gr.Button("📊 Start TensorBoard Server")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Log Training Metrics")
                train_loss = gr.Slider(
                    minimum=0.0, maximum=10.0, value=0.5, step=0.01,
                    label="Training Loss"
                )
                train_accuracy = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.8, step=0.01,
                    label="Training Accuracy"
                )
                train_learning_rate = gr.Slider(
                    minimum=1e-5, maximum=1e-1, value=1e-3, step=1e-5,
                    label="Learning Rate"
                )
                train_epoch = gr.Slider(
                    minimum=0, maximum=100, value=0, step=1,
                    label="Epoch"
                )
                train_step = gr.Slider(
                    minimum=0, maximum=10000, value=0, step=1,
                    label="Step"
                )
                log_training_btn = gr.Button("📈 Log Training Metrics")
            
            with gr.Column():
                gr.Markdown("#### Log Validation Metrics")
                val_loss = gr.Slider(
                    minimum=0.0, maximum=10.0, value=0.6, step=0.01,
                    label="Validation Loss"
                )
                val_accuracy = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.75, step=0.01,
                    label="Validation Accuracy"
                )
                val_precision = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.8, step=0.01,
                    label="Precision"
                )
                val_recall = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.7, step=0.01,
                    label="Recall"
                )
                val_f1 = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.75, step=0.01,
                    label="F1 Score"
                )
                log_validation_btn = gr.Button("📊 Log Validation Metrics")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Model Checkpoint")
                checkpoint_model_type = gr.Dropdown(
                    choices=["linear", "mlp"],
                    value="linear",
                    label="Model Type"
                )
                checkpoint_epoch = gr.Slider(
                    minimum=0, maximum=100, value=0, step=1,
                    label="Epoch"
                )
                checkpoint_step = gr.Slider(
                    minimum=0, maximum=10000, value=0, step=1,
                    label="Step"
                )
                checkpoint_train_loss = gr.Slider(
                    minimum=0.0, maximum=10.0, value=0.5, step=0.01,
                    label="Training Loss"
                )
                checkpoint_val_loss = gr.Slider(
                    minimum=0.0, maximum=10.0, value=0.6, step=0.01,
                    label="Validation Loss"
                )
                log_checkpoint_btn = gr.Button("💾 Log Model Checkpoint")
            
            with gr.Column():
                gr.Markdown("#### Experiment Management")
                get_summary_btn = gr.Button("📋 Get Experiment Summary")
                finish_experiment_btn = gr.Button("🏁 Finish Experiment")
                
                gr.Markdown("#### Experiment Comparison")
                compare_experiment_names = gr.Textbox(
                    value="experiment_1,experiment_2,experiment_3",
                    label="Experiment Names (comma-separated)"
                )
                compare_metric = gr.Dropdown(
                    choices=["train_loss", "val_loss", "train_accuracy", "val_accuracy"],
                    value="train_loss",
                    label="Metric to Compare"
                )
                compare_experiments_btn = gr.Button("📊 Compare Experiments")
        
        # Outputs
        experiment_start_output = gr.JSON(label="Experiment Start Status")
        tensorboard_output = gr.JSON(label="TensorBoard Server Status")
        training_log_output = gr.JSON(label="Training Metrics Log")
        validation_log_output = gr.JSON(label="Validation Metrics Log")
        checkpoint_output = gr.JSON(label="Checkpoint Status")
        summary_output = gr.JSON(label="Experiment Summary")
        finish_output = gr.JSON(label="Experiment Finish Status")
        comparison_output = gr.JSON(label="Experiment Comparison")
        
        # Event handlers
        start_experiment_btn.click(
            fn=start_experiment_tracking_interface,
            inputs=[experiment_name, project_name, enable_tensorboard, enable_wandb, wandb_entity, tags],
            outputs=experiment_start_output
        )
        
        start_tensorboard_btn.click(
            fn=start_tensorboard_server_interface,
            inputs=[tensorboard_log_dir, tensorboard_port],
            outputs=tensorboard_output
        )
        
        log_training_btn.click(
            fn=log_training_metrics_interface,
            inputs=[train_loss, train_accuracy, train_learning_rate, train_epoch, train_step],
            outputs=training_log_output
        )
        
        log_validation_btn.click(
            fn=log_validation_metrics_interface,
            inputs=[val_loss, val_accuracy, val_precision, val_recall, val_f1],
            outputs=validation_log_output
        )
        
        log_checkpoint_btn.click(
            fn=log_model_checkpoint_interface,
            inputs=[checkpoint_model_type, checkpoint_epoch, checkpoint_step, checkpoint_train_loss, checkpoint_val_loss],
            outputs=checkpoint_output
        )
        
        get_summary_btn.click(
            fn=get_experiment_summary_interface,
            outputs=summary_output
        )
        
        finish_experiment_btn.click(
            fn=finish_experiment_interface,
            outputs=finish_output
        )
        
        compare_experiments_btn.click(
            fn=compare_experiments_interface,
            inputs=[compare_experiment_names, compare_metric],
            outputs=comparison_output
        )
    
    gr.Markdown("""
    ## 📋 Features
    
    ### Model Inference
    - **Predicted Class**: The model's predicted class for your input.
    - **Probabilities**: The softmax probabilities for each class.
    - **Metrics**: If you provide a true label, accuracy, precision, recall, and F1 will be shown.
    - **Error Handling**: Any input or model errors will be shown here in red.
    - **Debug Info**: Enable debug mode to see stack traces for developers.
    
    ### Multi-GPU Training
    - **DataParallel**: Single-node multi-GPU training with automatic data distribution
    - **DistributedDataParallel**: Multi-node distributed training with process groups
    - **Automatic Strategy Selection**: Choose the best multi-GPU strategy based on available hardware
    - **Mixed Precision Training**: Faster training with reduced memory usage
    - **Real-time Monitoring**: GPU utilization and memory tracking
    - **Comprehensive Metrics**: Training loss, time, and performance statistics
    
    ### Code Profiling
    - **Function Profiling**: Detailed analysis of function performance and bottlenecks
    - **Data Loading Profiling**: Optimize data loading and preprocessing pipelines
    - **GPU & Memory Profiling**: Monitor GPU utilization and memory usage
    - **Bottleneck Analysis**: Automatic identification of performance bottlenecks
    - **Optimization Recommendations**: AI-powered suggestions for performance improvements
    - **Export Capabilities**: Export results in JSON, CSV, or HTML formats
    
    ### Experiment Tracking
    - **TensorBoard Integration**: Real-time visualization of training metrics and model graphs
    - **Weights & Biases Integration**: Cloud-based experiment tracking and collaboration
    - **Comprehensive Logging**: Training metrics, validation metrics, model checkpoints
    - **Experiment Comparison**: Compare multiple experiments and configurations
    - **Model Checkpointing**: Automatic saving of model states and configurations
    - **Hyperparameter Tracking**: Log and version all experiment parameters
    """)


def launch_gradio():
    demo.launch()

if __name__ == "__main__":
    launch_gradio() 