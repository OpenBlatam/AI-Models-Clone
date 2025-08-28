"""
🚀 OPTIMIZED IMAGE PROCESSING SYSTEM
====================================

Advanced image processing system with deep learning capabilities,
performance optimization, and enterprise-grade features.
"""

import asyncio
import json
import time
import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import hashlib
import pickle
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from collections import defaultdict, deque
import weakref
import base64
import io
import os
import traceback

# Core dependencies
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torch.cuda.amp import autocast, GradScaler
from torch.nn.parallel import DataParallel, DistributedDataParallel
from torch.utils.tensorboard import SummaryWriter
import torchvision.transforms as transforms
from PIL import Image, ImageOps, ImageFile
import cv2

# Advanced ML libraries
try:
    from transformers import (
        AutoModel, AutoTokenizer, AutoImageProcessor,
        pipeline, TrainingArguments, Trainer
    )
    from diffusers import (
        StableDiffusionPipeline, DDIMScheduler,
        UNet2DConditionModel, AutoencoderKL
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Performance monitoring
try:
    from prometheus_client import Counter, Histogram, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Web framework
try:
    from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Response
    from pydantic import BaseModel, Field, root_validator
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Progress bars
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# =============================================================================
# 🎯 ENUMS AND CONFIGURATION
# =============================================================================

class OptimizationProfile(str, Enum):
    """Optimization profiles for different use cases."""
    ULTRA_FAST = "ultra_fast"
    QUALITY_FIRST = "quality_first"
    BALANCED = "balanced"
    MEMORY_EFFICIENT = "memory_efficient"
    ENTERPRISE = "enterprise"
    RESEARCH = "research"
    MOBILE = "mobile"
    SERVER = "server"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME = "real_time"

class DeviceType(str, Enum):
    """Available device types."""
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"
    XPU = "xpu"

class MemoryFormat(str, Enum):
    """Memory formats for optimization."""
    CONTIGUOUS = "contiguous"
    CHANNELS_LAST = "channels_last"
    CHANNELS_FIRST = "channels_first"

class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CacheStrategy(str, Enum):
    """Caching strategies."""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"

# =============================================================================
# 📊 DATACLASSES
# =============================================================================

@dataclass
class ImageProcessConfig:
    """Advanced configuration for image processing."""
    
    # Performance settings
    optimization_profile: OptimizationProfile = OptimizationProfile.BALANCED
    device_type: DeviceType = DeviceType.CUDA
    memory_format: MemoryFormat = MemoryFormat.CHANNELS_LAST
    use_mixed_precision: bool = True
    use_compile: bool = True
    use_gradient_checkpointing: bool = False
    
    # Memory and resource limits
    max_batch_size: int = 32
    max_image_size: int = 2048
    max_memory_usage: int = 8 * 1024 * 1024 * 1024  # 8GB
    cache_size: int = 1000
    cache_ttl_hours: int = 24
    
    # Model settings
    model_name: str = "microsoft/DialoGPT-medium"
    diffusion_model: str = "runwayml/stable-diffusion-v1-5"
    use_quantization: bool = False
    quantization_bits: int = 8
    
    # Processing settings
    enable_ocr: bool = True
    enable_object_detection: bool = True
    enable_face_detection: bool = True
    enable_image_generation: bool = True
    enable_style_transfer: bool = True
    
    # Quality settings
    jpeg_quality: int = 95
    png_compression: int = 9
    resize_algorithm: str = "lanczos"
    
    # Monitoring settings
    enable_metrics: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'optimization_profile': self.optimization_profile.value,
            'device_type': self.device_type.value,
            'memory_format': self.memory_format.value,
            'use_mixed_precision': self.use_mixed_precision,
            'use_compile': self.use_compile,
            'use_gradient_checkpointing': self.use_gradient_checkpointing,
            'max_batch_size': self.max_batch_size,
            'max_image_size': self.max_image_size,
            'max_memory_usage': self.max_memory_usage,
            'cache_size': self.cache_size,
            'cache_ttl_hours': self.cache_ttl_hours,
            'model_name': self.model_name,
            'diffusion_model': self.diffusion_model,
            'use_quantization': self.use_quantization,
            'quantization_bits': self.quantization_bits,
            'enable_ocr': self.enable_ocr,
            'enable_object_detection': self.enable_object_detection,
            'enable_face_detection': self.enable_face_detection,
            'enable_image_generation': self.enable_image_generation,
            'enable_style_transfer': self.enable_style_transfer,
            'jpeg_quality': self.jpeg_quality,
            'png_compression': self.png_compression,
            'resize_algorithm': self.resize_algorithm,
            'enable_metrics': self.enable_metrics,
            'enable_logging': self.enable_logging,
            'log_level': self.log_level
        }

@dataclass
class ProcessingResult:
    """Result of image processing operation."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    memory_usage: float = 0.0
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'processing_time': self.processing_time,
            'memory_usage': self.memory_usage,
            'quality_score': self.quality_score,
            'metadata': self.metadata
        }

# =============================================================================
# 🔧 PROTOCOLS AND INTERFACES
# =============================================================================

from typing import Protocol

class PerformanceMonitorProtocol(Protocol):
    """Protocol for performance monitoring."""
    def start_monitoring(self) -> None: ...
    def stop_monitoring(self) -> None: ...
    def record_metric(self, name: str, value: float) -> None: ...
    def get_metrics(self) -> Dict[str, float]: ...

class MemoryTrackerProtocol(Protocol):
    """Protocol for memory tracking."""
    def track_memory(self) -> float: ...
    def get_memory_usage(self) -> Dict[str, float]: ...
    def optimize_memory(self) -> None: ...

class ModelManagerProtocol(Protocol):
    """Protocol for model management."""
    def load_model(self, model_name: str) -> Any: ...
    def unload_model(self, model_name: str) -> None: ...
    def get_model_info(self, model_name: str) -> Dict[str, Any]: ...

class ErrorHandlerProtocol(Protocol):
    """Protocol for error handling."""
    def handle_error(self, error: Exception, context: str) -> None: ...
    def get_error_stats(self) -> Dict[str, Any]: ...

# =============================================================================
# 🚀 CORE COMPONENTS
# =============================================================================

class PerformanceMonitor:
    """Advanced performance monitoring system."""
    
    def __init__(self, config: ImageProcessConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.start_time: Optional[float] = None
        self._lock = threading.Lock()
        
        # Initialize Prometheus metrics if available
        if PROMETHEUS_AVAILABLE and config.enable_metrics:
            self.request_counter = Counter(
                'image_process_requests_total',
                'Total requests',
                ['endpoint', 'status']
            )
            self.latency_histogram = Histogram(
                'image_process_request_duration_seconds',
                'Request duration',
                ['endpoint']
            )
        else:
            self.request_counter = None
            self.latency_histogram = None
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        with self._lock:
            self.start_time = time.time()
            self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        with self._lock:
            if self.start_time:
                total_time = time.time() - self.start_time
                self.logger.info(f"Performance monitoring stopped. Total time: {total_time:.2f}s")
                self.start_time = None
    
    def record_metric(self, name: str, value: float) -> None:
        """Record a performance metric."""
        with self._lock:
            self.metrics[name].append(value)
            if len(self.metrics[name]) > 1000:  # Keep last 1000 values
                self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current metrics summary."""
        with self._lock:
            summary = {}
            for name, values in self.metrics.items():
                if values:
                    summary[f"{name}_mean"] = np.mean(values)
                    summary[f"{name}_std"] = np.std(values)
                    summary[f"{name}_min"] = np.min(values)
                    summary[f"{name}_max"] = np.max(values)
                    summary[f"{name}_count"] = len(values)
            return summary

class MemoryTracker:
    """Advanced memory tracking and optimization."""
    
    def __init__(self, config: ImageProcessConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.memory_history: List[float] = []
        self._lock = threading.Lock()
    
    def track_memory(self) -> float:
        """Track current memory usage."""
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**3  # GB
            memory_reserved = torch.cuda.memory_reserved() / 1024**3  # GB
        else:
            memory_allocated = 0.0
            memory_reserved = 0.0
        
        with self._lock:
            self.memory_history.append(memory_allocated)
            if len(self.memory_history) > 1000:
                self.memory_history = self.memory_history[-1000:]
        
        return memory_allocated
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get detailed memory usage information."""
        if torch.cuda.is_available():
            return {
                'allocated_gb': torch.cuda.memory_allocated() / 1024**3,
                'reserved_gb': torch.cuda.memory_reserved() / 1024**3,
                'max_allocated_gb': torch.cuda.max_memory_allocated() / 1024**3,
                'max_reserved_gb': torch.cuda.max_memory_reserved() / 1024**3,
                'memory_efficiency': torch.cuda.memory_allocated() / max(torch.cuda.memory_reserved(), 1)
            }
        else:
            return {
                'allocated_gb': 0.0,
                'reserved_gb': 0.0,
                'max_allocated_gb': 0.0,
                'max_reserved_gb': 0.0,
                'memory_efficiency': 0.0
            }
    
    def optimize_memory(self) -> None:
        """Optimize memory usage."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.logger.info("Memory cache cleared")

class ErrorHandler:
    """Advanced error handling and recovery system."""
    
    def __init__(self, config: ImageProcessConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.error_stats: Dict[str, int] = defaultdict(int)
        self.error_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
    
    def handle_error(self, error: Exception, context: str) -> None:
        """Handle and log errors."""
        error_type = type(error).__name__
        error_msg = str(error)
        
        with self._lock:
            self.error_stats[error_type] += 1
            self.error_history.append({
                'timestamp': datetime.now().isoformat(),
                'error_type': error_type,
                'error_message': error_msg,
                'context': context,
                'traceback': traceback.format_exc()
            })
            
            # Keep only last 1000 errors
            if len(self.error_history) > 1000:
                self.error_history = self.error_history[-1000:]
        
        self.logger.error(f"Error in {context}: {error_type}: {error_msg}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        with self._lock:
            return {
                'total_errors': sum(self.error_stats.values()),
                'error_types': dict(self.error_stats),
                'recent_errors': self.error_history[-10:] if self.error_history else []
            }

class ModelCache:
    """Intelligent model caching system."""
    
    def __init__(self, config: ImageProcessConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.cache: Dict[str, Any] = {}
        self.cache_metadata: Dict[str, Dict[str, Any]] = {}
        self.access_count: Dict[str, int] = defaultdict(int)
        self.last_access: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self._lock:
            if key in self.cache:
                self.access_count[key] += 1
                self.last_access[key] = time.time()
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Set item in cache."""
        with self._lock:
            # Implement cache eviction if needed
            if len(self.cache) >= self.config.cache_size:
                self._evict_oldest()
            
            self.cache[key] = value
            self.cache_metadata[key] = metadata or {}
            self.access_count[key] = 1
            self.last_access[key] = time.time()
    
    def _evict_oldest(self) -> None:
        """Evict oldest items from cache."""
        if not self.last_access:
            return
        
        oldest_key = min(self.last_access.keys(), key=lambda k: self.last_access[k])
        del self.cache[oldest_key]
        del self.cache_metadata[oldest_key]
        del self.access_count[oldest_key]
        del self.last_access[oldest_key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'size': len(self.cache),
                'max_size': self.config.cache_size,
                'hit_rate': sum(self.access_count.values()) / max(len(self.cache), 1),
                'most_accessed': sorted(self.access_count.items(), key=lambda x: x[1], reverse=True)[:5]
            }

# =============================================================================
# 🧠 DEEP LEARNING MODELS
# =============================================================================

class ImageProcessingModel(nn.Module):
    """Base class for image processing models."""
    
    def __init__(self, config: ImageProcessConfig):
        super().__init__()
        self.config = config
        self.device = torch.device(config.device_type if torch.cuda.is_available() else "cpu")
        self.logger = logging.getLogger(__name__)
        
        # Initialize model components
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize model components."""
        raise NotImplementedError
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        raise NotImplementedError
    
    def to_device(self) -> None:
        """Move model to appropriate device."""
        self.to(self.device)
        if self.config.use_compile and hasattr(torch, 'compile'):
            self = torch.compile(self)
        if self.config.use_gradient_checkpointing:
            self.gradient_checkpointing_enable()

class OCRModel(ImageProcessingModel):
    """OCR model for text extraction."""
    
    def _initialize_model(self) -> None:
        """Initialize OCR model."""
        if TRANSFORMERS_AVAILABLE:
            try:
                self.processor = AutoImageProcessor.from_pretrained("microsoft/trocr-base-handwritten")
                self.model = AutoModel.from_pretrained("microsoft/trocr-base-handwritten")
                self.pipeline = pipeline("image-to-text", model=self.model, processor=self.processor)
            except Exception as e:
                self.logger.warning(f"Failed to load OCR model: {e}")
                self.pipeline = None
        else:
            self.pipeline = None
    
    def forward(self, image: torch.Tensor) -> str:
        """Extract text from image."""
        if self.pipeline is None:
            return ""
        
        try:
            # Convert tensor to PIL Image
            if isinstance(image, torch.Tensor):
                image = transforms.ToPILImage()(image)
            
            result = self.pipeline(image)
            return result[0]['generated_text'] if result else ""
        except Exception as e:
            self.logger.error(f"OCR processing failed: {e}")
            return ""

class ObjectDetectionModel(ImageProcessingModel):
    """Object detection model."""
    
    def _initialize_model(self) -> None:
        """Initialize object detection model."""
        if TRANSFORMERS_AVAILABLE:
            try:
                self.processor = AutoImageProcessor.from_pretrained("facebook/detr-resnet-50")
                self.model = AutoModel.from_pretrained("facebook/detr-resnet-50")
                self.pipeline = pipeline("object-detection", model=self.model, processor=self.processor)
            except Exception as e:
                self.logger.warning(f"Failed to load object detection model: {e}")
                self.pipeline = None
        else:
            self.pipeline = None
    
    def forward(self, image: torch.Tensor) -> List[Dict[str, Any]]:
        """Detect objects in image."""
        if self.pipeline is None:
            return []
        
        try:
            if isinstance(image, torch.Tensor):
                image = transforms.ToPILImage()(image)
            
            results = self.pipeline(image)
            return results if results else []
        except Exception as e:
            self.logger.error(f"Object detection failed: {e}")
            return []

class DiffusionModel(ImageProcessingModel):
    """Diffusion model for image generation."""
    
    def _initialize_model(self) -> None:
        """Initialize diffusion model."""
        if TRANSFORMERS_AVAILABLE:
            try:
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    self.config.diffusion_model,
                    torch_dtype=torch.float16 if self.config.use_mixed_precision else torch.float32
                )
                self.pipeline.to(self.device)
            except Exception as e:
                self.logger.warning(f"Failed to load diffusion model: {e}")
                self.pipeline = None
        else:
            self.pipeline = None
    
    def forward(self, prompt: str, **kwargs) -> Optional[torch.Tensor]:
        """Generate image from prompt."""
        if self.pipeline is None:
            return None
        
        try:
            with autocast() if self.config.use_mixed_precision else torch.no_grad():
                result = self.pipeline(prompt, **kwargs)
                return result.images[0] if result.images else None
        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            return None

# =============================================================================
# 🚀 MAIN OPTIMIZED IMAGE PROCESSING SYSTEM
# =============================================================================

class OptimizedImageProcessor:
    """Main optimized image processing system."""
    
    def __init__(self, config: Optional[ImageProcessConfig] = None):
        self.config = config or ImageProcessConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.performance_monitor = PerformanceMonitor(self.config)
        self.memory_tracker = MemoryTracker(self.config)
        self.error_handler = ErrorHandler(self.config)
        self.model_cache = ModelCache(self.config)
        
        # Initialize models
        self.models: Dict[str, ImageProcessingModel] = {}
        self._initialize_models()
        
        # Setup logging
        if self.config.enable_logging:
            logging.basicConfig(level=getattr(logging, self.config.log_level))
        
        self.logger.info("Optimized Image Processing System initialized")
    
    def _initialize_models(self) -> None:
        """Initialize all required models."""
        try:
            if self.config.enable_ocr:
                self.models['ocr'] = OCRModel(self.config)
                self.models['ocr'].to_device()
            
            if self.config.enable_object_detection:
                self.models['object_detection'] = ObjectDetectionModel(self.config)
                self.models['object_detection'].to_device()
            
            if self.config.enable_image_generation:
                self.models['diffusion'] = DiffusionModel(self.config)
                self.models['diffusion'].to_device()
                
        except Exception as e:
            self.error_handler.handle_error(e, "Model initialization")
    
    def process_image(self, image_data: Union[str, bytes, torch.Tensor], 
                     operations: List[str]) -> ProcessingResult:
        """Process image with specified operations."""
        start_time = time.time()
        
        try:
            # Start monitoring
            self.performance_monitor.start_monitoring()
            initial_memory = self.memory_tracker.track_memory()
            
            # Convert input to tensor
            image_tensor = self._prepare_image(image_data)
            
            results = {}
            
            # Perform requested operations
            for operation in operations:
                if operation == 'ocr' and 'ocr' in self.models:
                    results['ocr'] = self.models['ocr'](image_tensor)
                elif operation == 'object_detection' and 'object_detection' in self.models:
                    results['object_detection'] = self.models['object_detection'](image_tensor)
                elif operation == 'metadata':
                    results['metadata'] = self._extract_metadata(image_tensor)
            
            # Calculate processing metrics
            processing_time = time.time() - start_time
            final_memory = self.memory_tracker.track_memory()
            memory_usage = final_memory - initial_memory
            
            # Stop monitoring
            self.performance_monitor.stop_monitoring()
            
            return ProcessingResult(
                success=True,
                data=results,
                processing_time=processing_time,
                memory_usage=memory_usage,
                quality_score=self._calculate_quality_score(results),
                metadata=self._get_processing_metadata()
            )
            
        except Exception as e:
            self.error_handler.handle_error(e, "Image processing")
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def _prepare_image(self, image_data: Union[str, bytes, torch.Tensor]) -> torch.Tensor:
        """Prepare image data for processing."""
        if isinstance(image_data, torch.Tensor):
            return image_data
        
        if isinstance(image_data, str):
            # Assume base64 or URL
            if image_data.startswith('http'):
                # Download from URL
                import requests
                response = requests.get(image_data)
                image_data = response.content
            else:
                # Decode base64
                image_data = base64.b64decode(image_data)
        
        if isinstance(image_data, bytes):
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            image = image.convert('RGB')
            
            # Resize if needed
            if max(image.size) > self.config.max_image_size:
                ratio = self.config.max_image_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, getattr(Image, self.config.resize_algorithm.upper()))
            
            # Convert to tensor
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            return transform(image).unsqueeze(0)
        
        raise ValueError("Unsupported image data format")
    
    def _extract_metadata(self, image_tensor: torch.Tensor) -> Dict[str, Any]:
        """Extract basic image metadata."""
        return {
            'shape': list(image_tensor.shape),
            'dtype': str(image_tensor.dtype),
            'device': str(image_tensor.device),
            'min_value': float(image_tensor.min()),
            'max_value': float(image_tensor.max()),
            'mean_value': float(image_tensor.mean()),
            'std_value': float(image_tensor.std())
        }
    
    def _calculate_quality_score(self, results: Dict[str, Any]) -> float:
        """Calculate quality score based on results."""
        score = 0.0
        
        if 'ocr' in results and results['ocr']:
            score += 0.3
        
        if 'object_detection' in results and results['object_detection']:
            score += 0.4
        
        if 'metadata' in results:
            score += 0.3
        
        return min(score, 1.0)
    
    def _get_processing_metadata(self) -> Dict[str, Any]:
        """Get processing metadata."""
        return {
            'config': self.config.to_dict(),
            'performance_metrics': self.performance_monitor.get_metrics(),
            'memory_usage': self.memory_tracker.get_memory_usage(),
            'cache_stats': self.model_cache.get_cache_stats(),
            'error_stats': self.error_handler.get_error_stats()
        }
    
    def generate_image(self, prompt: str, **kwargs) -> ProcessingResult:
        """Generate image using diffusion model."""
        if 'diffusion' not in self.models:
            return ProcessingResult(success=False, error="Diffusion model not available")
        
        start_time = time.time()
        
        try:
            self.performance_monitor.start_monitoring()
            initial_memory = self.memory_tracker.track_memory()
            
            result = self.models['diffusion'](prompt, **kwargs)
            
            processing_time = time.time() - start_time
            final_memory = self.memory_tracker.track_memory()
            memory_usage = final_memory - initial_memory
            
            self.performance_monitor.stop_monitoring()
            
            return ProcessingResult(
                success=result is not None,
                data={'generated_image': result},
                processing_time=processing_time,
                memory_usage=memory_usage,
                quality_score=1.0 if result is not None else 0.0,
                metadata=self._get_processing_metadata()
            )
            
        except Exception as e:
            self.error_handler.handle_error(e, "Image generation")
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'status': 'operational',
            'config': self.config.to_dict(),
            'performance': self.performance_monitor.get_metrics(),
            'memory': self.memory_tracker.get_memory_usage(),
            'cache': self.model_cache.get_cache_stats(),
            'errors': self.error_handler.get_error_stats(),
            'models_loaded': list(self.models.keys()),
            'device_info': {
                'cuda_available': torch.cuda.is_available(),
                'cuda_device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
                'current_device': str(torch.cuda.current_device()) if torch.cuda.is_available() else 'cpu'
            }
        }

# =============================================================================
# 🎯 UTILITY FUNCTIONS
# =============================================================================

def create_optimized_processor(config: Optional[ImageProcessConfig] = None) -> OptimizedImageProcessor:
    """Create an optimized image processor instance."""
    return OptimizedImageProcessor(config)

def optimize_config_for_profile(profile: OptimizationProfile) -> ImageProcessConfig:
    """Optimize configuration for specific profile."""
    config = ImageProcessConfig()
    
    if profile == OptimizationProfile.ULTRA_FAST:
        config.use_mixed_precision = True
        config.use_compile = True
        config.max_batch_size = 64
        config.cache_size = 2000
        config.jpeg_quality = 80
        config.png_compression = 6
    
    elif profile == OptimizationProfile.QUALITY_FIRST:
        config.use_mixed_precision = False
        config.use_compile = False
        config.max_batch_size = 8
        config.jpeg_quality = 100
        config.png_compression = 9
    
    elif profile == OptimizationProfile.MEMORY_EFFICIENT:
        config.use_mixed_precision = True
        config.use_gradient_checkpointing = True
        config.max_batch_size = 4
        config.cache_size = 100
        config.use_quantization = True
    
    elif profile == OptimizationProfile.ENTERPRISE:
        config.enable_metrics = True
        config.enable_logging = True
        config.log_level = "DEBUG"
        config.cache_size = 5000
        config.cache_ttl_hours = 48
    
    config.optimization_profile = profile
    return config

def get_device_info() -> Dict[str, Any]:
    """Get comprehensive device information."""
    info = {
        'cuda_available': torch.cuda.is_available(),
        'cuda_version': torch.version.cuda if torch.cuda.is_available() else None,
        'device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0,
        'current_device': torch.cuda.current_device() if torch.cuda.is_available() else None,
        'device_names': []
    }
    
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            info['device_names'].append(torch.cuda.get_device_name(i))
    
    return info

# =============================================================================
# 🚀 EXPORTS
# =============================================================================

__all__ = [
    'OptimizedImageProcessor',
    'ImageProcessConfig',
    'ProcessingResult',
    'OptimizationProfile',
    'DeviceType',
    'MemoryFormat',
    'ErrorSeverity',
    'CacheStrategy',
    'PerformanceMonitor',
    'MemoryTracker',
    'ErrorHandler',
    'ModelCache',
    'ImageProcessingModel',
    'OCRModel',
    'ObjectDetectionModel',
    'DiffusionModel',
    'create_optimized_processor',
    'optimize_config_for_profile',
    'get_device_info'
]
