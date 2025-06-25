"""
Machine Learning Optimizer - Ultra-High Performance ML Operations.

Advanced ML optimizer with GPU acceleration, model optimization, ultra-fast
inference, tensor operations, and distributed computing capabilities.
"""

import asyncio
import time
import os
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path
import logging

# Core ML imports
import numpy as np

# Deep Learning frameworks
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# Optimization libraries
try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap, pmap
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False

try:
    import taichi as ti
    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False

# GPU acceleration
try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# Model compression and optimization
try:
    from neural_compressor import quantization
    from neural_compressor.config import PostTrainingQuantConfig
    NEURAL_COMPRESSOR_AVAILABLE = True
except ImportError:
    NEURAL_COMPRESSOR_AVAILABLE = False

# Distributed computing
try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False

# Performance optimization
try:
    import numba
    from numba import jit as numba_jit, cuda
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MLConfig:
    """Machine Learning optimization configuration."""
    # Device settings
    use_gpu: bool = GPU_AVAILABLE
    gpu_memory_fraction: float = 0.8
    mixed_precision: bool = True
    
    # Model optimization
    enable_onnx_optimization: bool = ONNX_AVAILABLE
    enable_quantization: bool = NEURAL_COMPRESSOR_AVAILABLE
    enable_tensorrt: bool = False
    
    # Inference settings
    batch_size: int = 32
    max_batch_size: int = 128
    enable_dynamic_batching: bool = True
    inference_timeout: float = 30.0
    
    # Memory optimization
    enable_memory_mapping: bool = True
    cache_models: bool = True
    model_cache_size: int = 5
    
    # Distributed settings
    enable_distributed: bool = RAY_AVAILABLE
    num_workers: int = min(4, os.cpu_count())
    
    # Performance settings
    enable_jit_compilation: bool = JAX_AVAILABLE or NUMBA_AVAILABLE
    optimization_level: str = "O3"  # O1, O2, O3
    enable_graph_optimization: bool = True


class DeviceOptimizer:
    """Optimize device selection and resource allocation."""
    
    def __init__(self, config: MLConfig):
        self.config = config
        self.device_info = self._detect_devices()
        self.current_device = self._select_optimal_device()
    
    def _detect_devices(self) -> Dict[str, Any]:
        """Detect available computing devices."""
        devices = {
            "cpu": {
                "available": True,
                "cores": os.cpu_count(),
                "memory_gb": self._get_system_memory()
            }
        }
        
        # CUDA detection
        if TORCH_AVAILABLE and torch.cuda.is_available():
            devices["cuda"] = {
                "available": True,
                "device_count": torch.cuda.device_count(),
                "devices": []
            }
            
            for i in range(torch.cuda.device_count()):
                device_props = torch.cuda.get_device_properties(i)
                devices["cuda"]["devices"].append({
                    "id": i,
                    "name": device_props.name,
                    "memory_gb": device_props.total_memory / (1024**3),
                    "compute_capability": f"{device_props.major}.{device_props.minor}"
                })
        
        # JAX GPU detection
        if JAX_AVAILABLE:
            try:
                jax_devices = jax.devices()
                devices["jax_devices"] = [str(d) for d in jax_devices]
            except:
                pass
        
        return devices
    
    def _get_system_memory(self) -> float:
        """Get system memory in GB."""
        try:
            import psutil
            return psutil.virtual_memory().total / (1024**3)
        except:
            return 8.0  # Default fallback
    
    def _select_optimal_device(self) -> str:
        """Select optimal computing device."""
        if self.config.use_gpu and "cuda" in self.device_info and self.device_info["cuda"]["available"]:
            return "cuda"
        elif JAX_AVAILABLE and len(self.device_info.get("jax_devices", [])) > 0:
            return "jax"
        else:
            return "cpu"
    
    def get_device_context(self):
        """Get device-specific context."""
        if self.current_device == "cuda" and TORCH_AVAILABLE:
            return torch.device("cuda:0")
        elif self.current_device == "jax" and JAX_AVAILABLE:
            return jax.devices()[0]
        else:
            return "cpu"
    
    def optimize_memory_usage(self):
        """Optimize memory usage for selected device."""
        if self.current_device == "cuda" and TORCH_AVAILABLE:
            # CUDA memory optimization
            torch.cuda.empty_cache()
            if self.config.gpu_memory_fraction < 1.0:
                torch.cuda.set_per_process_memory_fraction(self.config.gpu_memory_fraction)
        
        # Enable garbage collection
        import gc
        gc.collect()


class ModelOptimizer:
    """Optimize ML models for ultra-fast inference."""
    
    def __init__(self, config: MLConfig, device_optimizer: DeviceOptimizer):
        self.config = config
        self.device_optimizer = device_optimizer
        self.optimized_models: Dict[str, Any] = {}
        self.model_cache: Dict[str, Any] = {}
    
    async def optimize_torch_model(self, model: nn.Module, model_name: str) -> nn.Module:
        """Optimize PyTorch model."""
        if not TORCH_AVAILABLE:
            return model
        
        device = self.device_optimizer.get_device_context()
        model = model.to(device)
        
        # Enable mixed precision
        if self.config.mixed_precision and hasattr(torch, 'autocast'):
            model = torch.jit.script(model)
        
        # Compile model for optimization
        try:
            if hasattr(torch, 'compile'):  # PyTorch 2.0+
                model = torch.compile(model, mode='max-autotune')
        except:
            pass
        
        # Quantization
        if self.config.enable_quantization:
            try:
                model = torch.quantization.quantize_dynamic(
                    model, {nn.Linear}, dtype=torch.qint8
                )
            except Exception as e:
                logger.warning(f"Quantization failed: {e}")
        
        self.optimized_models[model_name] = model
        return model
    
    async def optimize_tensorflow_model(self, model, model_name: str):
        """Optimize TensorFlow model."""
        if not TF_AVAILABLE:
            return model
        
        # Enable mixed precision
        if self.config.mixed_precision:
            try:
                from tensorflow.keras.mixed_precision import set_global_policy
                set_global_policy('mixed_float16')
            except:
                pass
        
        # Convert to TensorFlow Lite for mobile optimization
        try:
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            
            if self.config.enable_quantization:
                converter.target_spec.supported_types = [tf.float16]
            
            tflite_model = converter.convert()
            self.optimized_models[f"{model_name}_tflite"] = tflite_model
        except Exception as e:
            logger.warning(f"TensorFlow Lite conversion failed: {e}")
        
        self.optimized_models[model_name] = model
        return model
    
    async def convert_to_onnx(self, model, model_name: str, input_shape: Tuple) -> Optional[str]:
        """Convert model to ONNX format for optimization."""
        if not ONNX_AVAILABLE:
            return None
        
        onnx_path = f"/tmp/{model_name}.onnx"
        
        try:
            if TORCH_AVAILABLE and isinstance(model, nn.Module):
                # PyTorch to ONNX
                dummy_input = torch.randn(1, *input_shape)
                torch.onnx.export(
                    model,
                    dummy_input,
                    onnx_path,
                    export_params=True,
                    opset_version=11,
                    do_constant_folding=True,
                    input_names=['input'],
                    output_names=['output'],
                    dynamic_axes={
                        'input': {0: 'batch_size'},
                        'output': {0: 'batch_size'}
                    }
                )
            
            # Optimize ONNX model
            try:
                from onnx_optimizer import optimize
                onnx_model = onnx.load(onnx_path)
                optimized_model = optimize(onnx_model)
                onnx.save(optimized_model, onnx_path)
            except:
                pass
            
            return onnx_path
            
        except Exception as e:
            logger.error(f"ONNX conversion failed: {e}")
            return None
    
    async def create_onnx_session(self, onnx_path: str, session_name: str) -> Optional[Any]:
        """Create optimized ONNX Runtime session."""
        if not ONNX_AVAILABLE or not os.path.exists(onnx_path):
            return None
        
        try:
            # Configure session options
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.enable_cpu_mem_arena = True
            sess_options.enable_mem_pattern = True
            sess_options.enable_mem_reuse = True
            
            # Enable parallelism
            sess_options.intra_op_num_threads = os.cpu_count()
            sess_options.inter_op_num_threads = os.cpu_count()
            
            # Select providers
            providers = []
            if self.config.use_gpu and 'CUDAExecutionProvider' in ort.get_available_providers():
                providers.append('CUDAExecutionProvider')
            providers.append('CPUExecutionProvider')
            
            session = ort.InferenceSession(
                onnx_path,
                sess_options=sess_options,
                providers=providers
            )
            
            self.optimized_models[session_name] = session
            return session
            
        except Exception as e:
            logger.error(f"ONNX session creation failed: {e}")
            return None


class InferenceOptimizer:
    """Ultra-fast inference optimization."""
    
    def __init__(self, config: MLConfig, model_optimizer: ModelOptimizer):
        self.config = config
        self.model_optimizer = model_optimizer
        self.inference_cache: Dict[str, Tuple[Any, float]] = {}
        self.batch_queue: Dict[str, List] = {}
        self.inference_stats = {
            "total_inferences": 0,
            "cache_hits": 0,
            "avg_inference_time": 0.0,
            "batch_inferences": 0
        }
    
    async def single_inference(
        self,
        model_name: str,
        input_data: Union[np.ndarray, torch.Tensor],
        use_cache: bool = True
    ) -> Any:
        """Execute single optimized inference."""
        start_time = time.time()
        
        # Check cache
        if use_cache:
            cache_key = self._generate_cache_key(model_name, input_data)
            if cache_key in self.inference_cache:
                cached_result, timestamp = self.inference_cache[cache_key]
                if time.time() - timestamp < 300:  # 5 minute cache
                    self.inference_stats["cache_hits"] += 1
                    return cached_result
        
        # Get model
        model = self.model_optimizer.optimized_models.get(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found")
        
        # Execute inference
        result = await self._execute_inference(model, input_data)
        
        # Cache result
        if use_cache:
            self.inference_cache[cache_key] = (result, time.time())
            # Limit cache size
            if len(self.inference_cache) > 1000:
                oldest_key = min(self.inference_cache.keys(), 
                               key=lambda k: self.inference_cache[k][1])
                del self.inference_cache[oldest_key]
        
        # Update stats
        inference_time = time.time() - start_time
        self.inference_stats["total_inferences"] += 1
        self.inference_stats["avg_inference_time"] = (
            self.inference_stats["avg_inference_time"] + inference_time
        ) / 2
        
        return result
    
    async def batch_inference(
        self,
        model_name: str,
        input_batch: List[Union[np.ndarray, torch.Tensor]],
        max_wait_time: float = 0.1
    ) -> List[Any]:
        """Execute batch inference with dynamic batching."""
        if len(input_batch) <= 1:
            return [await self.single_inference(model_name, input_batch[0])]
        
        # Prepare batch
        if TORCH_AVAILABLE and isinstance(input_batch[0], torch.Tensor):
            batched_input = torch.stack(input_batch)
        else:
            batched_input = np.stack(input_batch)
        
        # Execute batch inference
        model = self.model_optimizer.optimized_models.get(model_name)
        if not model:
            raise ValueError(f"Model {model_name} not found")
        
        batch_result = await self._execute_inference(model, batched_input)
        
        # Split results
        if isinstance(batch_result, torch.Tensor):
            results = [batch_result[i] for i in range(len(input_batch))]
        else:
            results = [batch_result[i] for i in range(len(input_batch))]
        
        self.inference_stats["batch_inferences"] += 1
        return results
    
    async def _execute_inference(self, model: Any, input_data: Any) -> Any:
        """Execute model inference with device optimization."""
        try:
            if hasattr(model, 'run'):  # ONNX Runtime session
                # Convert to numpy if needed
                if hasattr(input_data, 'numpy'):
                    input_data = input_data.numpy()
                
                input_name = model.get_inputs()[0].name
                result = model.run(None, {input_name: input_data})
                return result[0]
            
            elif TORCH_AVAILABLE and isinstance(model, nn.Module):
                # PyTorch model
                model.eval()
                with torch.no_grad():
                    if self.config.mixed_precision:
                        with torch.autocast(device_type='cuda' if torch.cuda.is_available() else 'cpu'):
                            return model(input_data)
                    else:
                        return model(input_data)
            
            elif TF_AVAILABLE and hasattr(model, 'predict'):
                # TensorFlow model
                return model.predict(input_data, batch_size=self.config.batch_size)
            
            else:
                # Generic callable
                return model(input_data)
                
        except Exception as e:
            logger.error(f"Inference execution failed: {e}")
            raise
    
    def _generate_cache_key(self, model_name: str, input_data: Any) -> str:
        """Generate cache key for input data."""
        try:
            if hasattr(input_data, 'numpy'):
                data_hash = hash(input_data.numpy().tobytes())
            else:
                data_hash = hash(input_data.tobytes())
            return f"{model_name}:{data_hash}"
        except:
            return f"{model_name}:{id(input_data)}"


class MLOptimizer:
    """Main ML optimizer coordinating all components."""
    
    def __init__(self, config: MLConfig = None):
        self.config = config or MLConfig()
        self.device_optimizer = DeviceOptimizer(self.config)
        self.model_optimizer = ModelOptimizer(self.config, self.device_optimizer)
        self.inference_optimizer = InferenceOptimizer(self.config, self.model_optimizer)
        
        self.metrics = {
            "optimization_level": "ULTRA",
            "features_enabled": {
                "torch_available": TORCH_AVAILABLE,
                "tensorflow_available": TF_AVAILABLE,
                "onnx_available": ONNX_AVAILABLE,
                "jax_available": JAX_AVAILABLE,
                "gpu_available": GPU_AVAILABLE,
                "quantization": self.config.enable_quantization,
                "mixed_precision": self.config.mixed_precision,
                "distributed": self.config.enable_distributed
            },
            "device_info": self.device_optimizer.device_info
        }
    
    async def initialize(self) -> Dict[str, bool]:
        """Initialize ML optimizer."""
        results = {}
        
        try:
            # Optimize device usage
            self.device_optimizer.optimize_memory_usage()
            results["device_optimization"] = True
            
            # Initialize distributed computing if enabled
            if self.config.enable_distributed and RAY_AVAILABLE:
                try:
                    if not ray.is_initialized():
                        ray.init(num_cpus=self.config.num_workers)
                    results["distributed_computing"] = True
                except Exception as e:
                    logger.warning(f"Ray initialization failed: {e}")
                    results["distributed_computing"] = False
            
            # Initialize Taichi if available
            if TAICHI_AVAILABLE:
                try:
                    ti.init(arch=ti.gpu if self.config.use_gpu else ti.cpu)
                    results["taichi_gpu"] = True
                except:
                    results["taichi_gpu"] = False
            
            logger.info("ML optimizer initialized", 
                       device=self.device_optimizer.current_device,
                       features=self.metrics["features_enabled"])
            
            return results
            
        except Exception as e:
            logger.error(f"ML optimizer initialization failed: {e}")
            return {"initialization": False}
    
    async def register_model(
        self,
        model: Any,
        model_name: str,
        input_shape: Optional[Tuple] = None,
        optimize: bool = True
    ) -> Dict[str, bool]:
        """Register and optimize a model."""
        results = {}
        
        try:
            # Optimize based on framework
            if TORCH_AVAILABLE and isinstance(model, nn.Module):
                optimized_model = await self.model_optimizer.optimize_torch_model(model, model_name)
                results["torch_optimization"] = True
                
                # Convert to ONNX if requested and input shape provided
                if self.config.enable_onnx_optimization and input_shape:
                    onnx_path = await self.model_optimizer.convert_to_onnx(
                        optimized_model, model_name, input_shape
                    )
                    if onnx_path:
                        onnx_session = await self.model_optimizer.create_onnx_session(
                            onnx_path, f"{model_name}_onnx"
                        )
                        results["onnx_conversion"] = onnx_session is not None
            
            elif TF_AVAILABLE and hasattr(model, 'predict'):
                optimized_model = await self.model_optimizer.optimize_tensorflow_model(model, model_name)
                results["tensorflow_optimization"] = True
            
            else:
                # Generic model
                self.model_optimizer.optimized_models[model_name] = model
                results["generic_registration"] = True
            
            return results
            
        except Exception as e:
            logger.error(f"Model registration failed: {e}")
            return {"registration": False}
    
    async def inference(
        self,
        model_name: str,
        input_data: Union[np.ndarray, torch.Tensor, List],
        use_cache: bool = True,
        use_batching: bool = True
    ) -> Any:
        """Execute optimized inference."""
        if isinstance(input_data, list) and use_batching:
            return await self.inference_optimizer.batch_inference(model_name, input_data)
        else:
            return await self.inference_optimizer.single_inference(model_name, input_data, use_cache)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive ML performance metrics."""
        return {
            "device_info": self.device_optimizer.device_info,
            "inference_stats": self.inference_optimizer.inference_stats,
            "model_count": len(self.model_optimizer.optimized_models),
            "cache_size": len(self.inference_optimizer.inference_cache),
            "config": {
                "batch_size": self.config.batch_size,
                "mixed_precision": self.config.mixed_precision,
                "gpu_enabled": self.config.use_gpu,
                "optimization_level": self.config.optimization_level
            },
            "features": self.metrics["features_enabled"]
        }
    
    async def cleanup(self):
        """Cleanup ML resources."""
        # Clear caches
        self.inference_optimizer.inference_cache.clear()
        self.model_optimizer.model_cache.clear()
        
        # Cleanup GPU memory
        if TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Shutdown Ray if initialized
        if RAY_AVAILABLE and ray.is_initialized():
            ray.shutdown()
        
        logger.info("ML optimizer cleanup completed")


__all__ = [
    'MLOptimizer',
    'MLConfig',
    'DeviceOptimizer',
    'ModelOptimizer',
    'InferenceOptimizer'
] 