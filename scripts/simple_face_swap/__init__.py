"""
Simple Face Swap - Módulo Refactorizado
========================================
Módulo refactorizado para face swap simple usando PyTorch.
"""

from .model import SimpleFaceSwapModel
from .detector import SimpleFaceDetector
from .dataset import SimpleFaceSwapDataset
from .pipeline import SimpleFaceSwapPipeline
from .trainer import SimpleFaceSwapTrainer, train_simple_model

__version__ = '2.0.0'
__all__ = [
    'SimpleFaceSwapModel',
    'SimpleFaceDetector',
    'SimpleFaceSwapDataset',
    'SimpleFaceSwapPipeline',
    'SimpleFaceSwapTrainer',
    'train_simple_model'
]






