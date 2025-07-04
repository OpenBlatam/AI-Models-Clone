"""
Advanced AI Models Module - Deep Learning, Transformers, Diffusion Models & LLMs
Optimized with latest PyTorch, Transformers, Diffusers, and Gradio libraries.
"""

from .models.transformer_models import (
    AdvancedTransformerModel,
    MultiModalTransformer,
    CustomAttentionMechanism,
    PositionalEncoding
)

from .models.diffusion_models import (
    StableDiffusionPipeline,
    CustomDiffusionModel,
    DiffusionScheduler,
    TextToImagePipeline
)

from .models.llm_models import (
    AdvancedLLMModel,
    LoRAFineTuner,
    CustomTokenizer,
    LLMInferenceEngine
)

from .models.vision_models import (
    VisionTransformer,
    ImageClassificationModel,
    ObjectDetectionModel,
    SegmentationModel
)

from .training.trainer import (
    AdvancedTrainer,
    MixedPrecisionTrainer,
    DistributedTrainer,
    CustomLossFunctions
)

from .data.data_loader import (
    AdvancedDataLoader,
    MultiModalDataset,
    CustomTransforms,
    DataAugmentation
)

from .inference.inference_engine import (
    ModelInferenceEngine,
    BatchInference,
    RealTimeInference,
    ModelOptimization
)

from .utils.model_utils import (
    ModelCheckpointing,
    ExperimentTracking,
    PerformanceProfiling,
    ModelEvaluation
)

from .gradio_interfaces import (
    create_model_demo,
    create_inference_interface,
    create_training_interface,
    create_evaluation_dashboard
)

__version__ = "2.0.0"
__author__ = "Advanced AI Models Team"

__all__ = [
    # Models
    "AdvancedTransformerModel",
    "MultiModalTransformer", 
    "CustomAttentionMechanism",
    "PositionalEncoding",
    "StableDiffusionPipeline",
    "CustomDiffusionModel",
    "DiffusionScheduler",
    "TextToImagePipeline",
    "AdvancedLLMModel",
    "LoRAFineTuner",
    "CustomTokenizer",
    "LLMInferenceEngine",
    "VisionTransformer",
    "ImageClassificationModel",
    "ObjectDetectionModel",
    "SegmentationModel",
    
    # Training
    "AdvancedTrainer",
    "MixedPrecisionTrainer",
    "DistributedTrainer", 
    "CustomLossFunctions",
    
    # Data
    "AdvancedDataLoader",
    "MultiModalDataset",
    "CustomTransforms",
    "DataAugmentation",
    
    # Inference
    "ModelInferenceEngine",
    "BatchInference",
    "RealTimeInference",
    "ModelOptimization",
    
    # Utils
    "ModelCheckpointing",
    "ExperimentTracking",
    "PerformanceProfiling",
    "ModelEvaluation",
    
    # Gradio
    "create_model_demo",
    "create_inference_interface",
    "create_training_interface",
    "create_evaluation_dashboard"
] 