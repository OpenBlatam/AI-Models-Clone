"""
Quality Control AI - Sistema de Control de Calidad con Detección de Defectos por Cámara
Enhanced with PyTorch, Transformers, and Diffusion Models
"""

__version__ = "2.0.0"
__author__ = "Blatam Academy"

# Core components
from .core.camera_controller import CameraController
from .core.object_detector import ObjectDetector
from .core.anomaly_detector import AnomalyDetector
from .core.anomaly_detector_enhanced import EnhancedAnomalyDetector
from .core.defect_classifier import DefectClassifier
from .core.video_analyzer import VideoAnalyzer

# PyTorch models
from .core.models import (
    AnomalyAutoencoder,
    create_autoencoder,
    DefectViTClassifier,
    create_defect_classifier,
    DiffusionAnomalyDetector,
    create_diffusion_detector,
)

# Services
from .services.quality_inspector import QualityInspector
from .services.defect_analyzer import DefectAnalyzer
from .services.alert_system import AlertSystem, Alert, AlertLevel

# Utils
from .utils.visualization import QualityVisualizer
from .utils.report_generator import ReportGenerator
from .utils.performance_optimizer import PerformanceOptimizer, measure_time
from .utils.gradio_interface import QualityControlGradioInterface, create_gradio_app

# Training
from .training import ModelTrainer, train_autoencoder, train_classifier

# Configuration
from .config.training_config import Config, create_default_config_file

# Fast/Optimized components
from .core.fast_inspector import FastQualityInspector
from .core.models.optimized_models import create_fast_autoencoder, optimize_for_inference
from .utils.fast_inference import FastPreprocessor, BatchProcessor
from .utils.performance_benchmark import PerformanceBenchmark

__all__ = [
    # Core
    "CameraController",
    "ObjectDetector",
    "AnomalyDetector",
    "EnhancedAnomalyDetector",
    "DefectClassifier",
    "VideoAnalyzer",
    # Services
    "QualityInspector",
    "DefectAnalyzer",
    "AlertSystem",
    "Alert",
    "AlertLevel",
    # Utils
    "QualityVisualizer",
    "ReportGenerator",
    "PerformanceOptimizer",
    "measure_time",
    "QualityControlGradioInterface",
    "create_gradio_app",
    # Models
    "AnomalyAutoencoder",
    "create_autoencoder",
    "DefectViTClassifier",
    "create_defect_classifier",
    "DiffusionAnomalyDetector",
    "create_diffusion_detector",
    # Training
    "ModelTrainer",
    "train_autoencoder",
    "train_classifier",
    # Config
    "Config",
    "create_default_config_file",
    # Fast/Optimized
    "FastQualityInspector",
    "create_fast_autoencoder",
    "optimize_for_inference",
    "FastPreprocessor",
    "BatchProcessor",
    "PerformanceBenchmark",
]

