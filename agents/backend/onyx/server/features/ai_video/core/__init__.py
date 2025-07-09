"""
AI Video Core Module
===================

This module provides the core components for AI video generation with a modular architecture:

- Models: Base classes and implementations for video generation models
- Data Loading: Dataset classes and data preprocessing utilities
- Training: Training loops, loss functions, and optimization
- Evaluation: Metrics calculation and model assessment
- Orchestrator: High-level pipeline coordination

All components follow clean architecture principles with clear separation of concerns.
"""

# Version information
__version__ = "2.0.0"
__author__ = "AI Video System"
__description__ = "Modular AI Video Generation Core Components"

# Import all core components
from .models import (
    BaseVideoModel,
    ModelConfig,
    DiffusionVideoModel,
    GANVideoModel,
    TransformerVideoModel,
    ModelFactory,
    create_model,
    load_model,
    get_model_info
)

from .data_loader import (
    BaseVideoDataset,
    VideoFileDataset,
    CachedVideoDataset,
    DataConfig,
    VideoTransform,
    VideoAugmentation,
    DataLoaderFactory,
    create_dataset,
    create_data_loader,
    create_train_val_test_loaders,
    get_dataset_info
)

from .training import (
    BaseLoss,
    MSELoss,
    L1Loss,
    PerceptualLoss,
    AdversarialLoss,
    TrainingConfig,
    TrainingCallback,
    ProgressCallback,
    LoggingCallback,
    CheckpointCallback,
    VideoTrainer,
    LossFactory,
    create_trainer,
    train_model
)

from .evaluation import (
    BaseMetric,
    PSNRMetric,
    SSIMMetric,
    LPIPSMetric,
    EvaluationConfig,
    VideoEvaluator,
    MetricFactory,
    create_evaluator,
    evaluate_model,
    compare_models
)

from .orchestrator import (
    PipelineConfig,
    VideoPipeline,
    PipelineFactory,
    run_training_pipeline,
    run_evaluation_pipeline,
    run_full_pipeline
)

# Convenience imports for common use cases
__all__ = [
    # Models
    "BaseVideoModel",
    "ModelConfig",
    "DiffusionVideoModel", 
    "GANVideoModel",
    "TransformerVideoModel",
    "ModelFactory",
    "create_model",
    "load_model",
    "get_model_info",
    
    # Data Loading
    "BaseVideoDataset",
    "VideoFileDataset",
    "CachedVideoDataset",
    "DataConfig",
    "VideoTransform",
    "VideoAugmentation",
    "DataLoaderFactory",
    "create_dataset",
    "create_data_loader",
    "create_train_val_test_loaders",
    "get_dataset_info",
    
    # Training
    "BaseLoss",
    "MSELoss",
    "L1Loss",
    "PerceptualLoss",
    "AdversarialLoss",
    "TrainingConfig",
    "TrainingCallback",
    "ProgressCallback",
    "LoggingCallback",
    "CheckpointCallback",
    "VideoTrainer",
    "LossFactory",
    "create_trainer",
    "train_model",
    
    # Evaluation
    "BaseMetric",
    "PSNRMetric",
    "SSIMMetric",
    "LPIPSMetric",
    "EvaluationConfig",
    "VideoEvaluator",
    "MetricFactory",
    "create_evaluator",
    "evaluate_model",
    "compare_models",
    
    # Orchestrator
    "PipelineConfig",
    "VideoPipeline",
    "PipelineFactory",
    "run_training_pipeline",
    "run_evaluation_pipeline",
    "run_full_pipeline"
]


def get_core_info():
    """Get information about the core module."""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "models": [
                "BaseVideoModel",
                "DiffusionVideoModel",
                "GANVideoModel", 
                "TransformerVideoModel"
            ],
            "data_loading": [
                "BaseVideoDataset",
                "VideoFileDataset",
                "CachedVideoDataset"
            ],
            "training": [
                "VideoTrainer",
                "BaseLoss",
                "TrainingCallback"
            ],
            "evaluation": [
                "VideoEvaluator",
                "BaseMetric",
                "PSNRMetric",
                "SSIMMetric"
            ],
            "orchestrator": [
                "VideoPipeline",
                "PipelineFactory"
            ]
        }
    }


def create_complete_pipeline(model_type: str = "diffusion",
                           data_dir: str = "data/videos",
                           experiment_name: str = None) -> VideoPipeline:
    """
    Create a complete AI video generation pipeline.
    
    Args:
        model_type: Type of model to use ("diffusion", "gan", "transformer")
        data_dir: Directory containing video data
        experiment_name: Name for the experiment (auto-generated if None)
    
    Returns:
        Configured VideoPipeline instance
    """
    return PipelineFactory.create_full_pipeline(
        model_type=model_type,
        data_dir=data_dir,
        experiment_name=experiment_name
    )


def quick_start_example():
    """
    Quick start example demonstrating the modular architecture.
    
    This example shows how to:
    1. Create a model
    2. Set up data loading
    3. Train the model
    4. Evaluate the model
    """
    print("🚀 AI Video Core - Quick Start Example")
    print("=" * 50)
    
    # 1. Create model configuration
    model_config = ModelConfig(
        model_type="diffusion",
        model_name="quick_start_model",
        frame_size=(64, 64),
        num_frames=8
    )
    
    # 2. Create data configuration
    data_config = DataConfig(
        data_dir="data/videos",
        frame_size=(64, 64),
        num_frames=8,
        batch_size=4
    )
    
    # 3. Create training configuration
    training_config = TrainingConfig(
        num_epochs=5,
        batch_size=4,
        learning_rate=1e-4
    )
    
    # 4. Create evaluation configuration
    evaluation_config = EvaluationConfig(
        batch_size=4,
        num_samples=10
    )
    
    # 5. Create pipeline configuration
    pipeline_config = PipelineConfig(
        mode="full",
        experiment_name="quick_start_example",
        model_config=model_config,
        data_config=data_config,
        training_config=training_config,
        evaluation_config=evaluation_config
    )
    
    # 6. Create and run pipeline
    pipeline = VideoPipeline(pipeline_config)
    
    try:
        results = pipeline.run()
        print(f"✅ Pipeline completed: {results['pipeline_metadata']['status']}")
        
        # Print summary
        summary = pipeline.get_summary()
        print(f"📊 Model parameters: {summary['model_info']['parameters']:,}")
        print(f"📈 Final training loss: {summary['training_results']['final_train_loss']:.4f}")
        
        if summary['evaluation_results']:
            print(f"📊 Evaluation metrics: {summary['evaluation_results']}")
    
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        print("💡 Make sure you have video data in the 'data/videos' directory")


def list_available_components():
    """List all available components in the core module."""
    info = get_core_info()
    
    print("🔧 Available Core Components")
    print("=" * 40)
    
    for category, components in info['components'].items():
        print(f"\n📁 {category.replace('_', ' ').title()}:")
        for component in components:
            print(f"   • {component}")
    
    print(f"\n📦 Total components: {sum(len(comps) for comps in info['components'].values())}")
    print(f"🔢 Version: {info['version']}")


# Module initialization
if __name__ == "__main__":
    print("🎯 AI Video Core Module")
    print("=" * 30)
    
    # Show available components
    list_available_components()
    
    print("\n🚀 Quick Start:")
    print("   from core import create_complete_pipeline")
    print("   pipeline = create_complete_pipeline('diffusion', 'data/videos')")
    print("   results = pipeline.run()")
    
    print("\n📚 Documentation:")
    print("   Check individual module docstrings for detailed usage")
    print("   Run quick_start_example() for a complete example") 