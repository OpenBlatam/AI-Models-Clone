"""
Advanced ML Model Integration Package
🤖 Advanced machine learning model integration with optimization
"""

from .advanced_ml_models import (
    AdvancedMLModelManager,
    ModelConfig,
    ModelMetadata,
    ModelCache,
    ModelQuantizer,
    get_model_manager,
    cleanup_model_manager
)

__version__ = "1.0.0"
__author__ = "NotebookLM AI Team"
__description__ = "Advanced ML Model Integration - Optimized model loading and inference"

__all__ = [
    "AdvancedMLModelManager",
    "ModelConfig", 
    "ModelMetadata",
    "ModelCache",
    "ModelQuantizer",
    "get_model_manager",
    "cleanup_model_manager"
]

# Package metadata
PACKAGE_INFO = {
    "name": "advanced-ml-integration",
    "version": __version__,
    "description": __description__,
    "features": [
        "Advanced model loading with caching",
        "Model quantization and optimization",
        "Multi-device support (CPU, GPU, MPS)",
        "Transformer and ONNX model support",
        "Memory usage optimization",
        "Performance monitoring and metrics"
    ],
    "supported_model_types": [
        "Transformer models (Hugging Face)",
        "ONNX models",
        "Custom models (extensible)"
    ],
    "supported_devices": [
        "CPU",
        "CUDA (NVIDIA GPU)",
        "MPS (Apple Silicon)"
    ],
    "supported_precisions": [
        "float32",
        "float16", 
        "int8"
    ]
} 