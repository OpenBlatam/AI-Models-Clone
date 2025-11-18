"""
Deep Learning Module - Modular Deep Learning Code Generation
============================================================

Organized into specialized sub-modules following best practices:
- models: Model architectures (Transformer, CNN, RNN, etc.) with nn.Module
- training: Training utilities with mixed precision, gradient accumulation
- data: Data loaders and datasets with functional programming patterns
- evaluation: Metrics and model evaluation
- inference: Model inference and Gradio integration
- config: YAML configuration management
- utils: Device management, experiment tracking, debugging

Legacy generators for code generation:
- generator_config: Centralized generator configuration
- generator_registry: Registry and Factory for generators
- generation_strategy: Generation strategies
"""

from .models import BaseModel, TransformerModel, create_model, initialize_weights
from .data import BaseDataset, TextDataset, ImageDataset, create_dataloader, train_val_test_split
from .training import Trainer, TrainingConfig, EarlyStopping, create_optimizer, create_scheduler
from .evaluation import Metrics, compute_classification_metrics, compute_regression_metrics, evaluate_model
from .inference import InferenceEngine, create_gradio_app, batch_inference
from .config import ConfigManager, load_config, save_config, merge_configs
from .utils.device_utils import get_device, set_seed, enable_anomaly_detection
from .utils.experiment_tracking import ExperimentTracker

__all__ = [
    "BaseModel", "TransformerModel", "create_model", "initialize_weights",
    "BaseDataset", "TextDataset", "ImageDataset", "create_dataloader", "train_val_test_split",
    "Trainer", "TrainingConfig", "EarlyStopping", "create_optimizer", "create_scheduler",
    "Metrics", "compute_classification_metrics", "compute_regression_metrics", "evaluate_model",
    "InferenceEngine", "create_gradio_app", "batch_inference",
    "ConfigManager", "load_config", "save_config", "merge_configs",
    "get_device", "set_seed", "enable_anomaly_detection", "ExperimentTracker",
]

def _try_import(module_path: str, attributes: list, module_name: str = None):
    """Helper to conditionally import and add to __all__."""
    try:
        module = __import__(module_path, fromlist=attributes, level=1)
        imported = {}
        for attr in attributes:
            imported[attr] = getattr(module, attr)
        globals().update(imported)
        __all__.extend(attributes)
        return True
    except (ImportError, AttributeError):
        for attr in attributes:
            globals()[attr] = None
        return False

_optional_modules = [
    ('.models', ['CNNModel', 'RNNModel', 'TransformersModelWrapper', 'create_transformers_model',
                 'DiffusionModelWrapper', 'create_diffusion_model'], 'extended_models'),
    ('.data', ['get_image_augmentation', 'Mixup', 'CutMix'], 'augmentation'),
    ('.training', ['ModelCheckpoint', 'MetricsLogger', 'CallbackList'], 'callbacks'),
    ('.pipelines', ['TrainingPipeline', 'InferencePipeline'], 'pipelines'),
    ('.helpers', ['count_parameters', 'get_model_summary', 'freeze_layers', 'unfreeze_layers',
                  'plot_training_curves', 'plot_confusion_matrix'], 'helpers'),
    ('.core', ['BaseComponent', 'ComponentRegistry', 'Factory'], 'core'),
    ('.presets', ['get_model_preset', 'get_training_preset', 'get_optimizer_preset',
                  'get_data_preset', 'list_presets'], 'presets'),
    ('.templates', ['get_training_template', 'get_inference_template', 'get_config_template',
                    'generate_project_structure'], 'templates'),
    ('.integration', ['HuggingFaceHubIntegration', 'MLflowIntegration'], 'integrations'),
    ('.architecture', ['ModelBuilder', 'TrainingBuilder', 'TrainingStrategy', 'StandardTrainingStrategy',
                       'FastTrainingStrategy', 'DataStrategy', 'StandardDataStrategy',
                       'CrossValidationDataStrategy', 'EventPublisher', 'TrainingObserver'], 'architecture'),
    ('.services', ['ModelService', 'TrainingService', 'InferenceService', 'DataService'], 'services'),
    ('.losses', ['FocalLoss', 'LabelSmoothingLoss', 'DiceLoss', 'CombinedLoss', 'create_loss'], 'losses'),
    ('.optimization', ['quantize_model', 'quantize_model_for_mobile', 'prune_model',
                       'get_pruning_sparsity', 'iterative_pruning', 'KnowledgeDistillation',
                       'DistillationTrainer'], 'optimization'),
    ('.transformers', ['load_pretrained_model', 'load_tokenizer', 'setup_lora', 'TokenizedDataset'], 'transformers_utils'),
    ('.diffusion', ['create_diffusion_pipeline', 'DiffusionPipelineWrapper'], 'diffusion_utils'),
    ('.deployment', ['export_to_onnx', 'load_onnx_model', 'export_to_torchscript', 'create_model_api'], 'deployment'),
    ('.testing', ['ModelTester', 'create_test_suite', 'benchmark_model'], 'testing'),
    ('.monitoring', ['ModelMonitor', 'DriftDetector', 'PerformanceMonitor'], 'monitoring'),
    ('.visualization', ['plot_training_history', 'visualize_model_architecture', 'plot_attention_weights',
                        'visualize_feature_maps', 'plot_confusion_matrix_advanced'], 'visualization'),
    ('.security', ['validate_inputs', 'sanitize_inputs', 'detect_adversarial', 'ModelEncryption'], 'security'),
    ('.experimentation', ['HyperparameterSearch', 'ExperimentComparator', 'ABTester', 'create_experiment_config'], 'experimentation'),
    ('.accelerators', ['setup_accelerator', 'optimize_for_gpu', 'setup_multi_gpu', 'get_accelerator_info',
                       'enable_mixed_precision', 'optimize_batch_size'], 'accelerators'),
    ('.documentation', ['generate_model_docs', 'generate_training_docs', 'generate_api_docs',
                        'create_project_readme'], 'documentation'),
    ('.benchmarking', ['benchmark_inference', 'benchmark_training', 'compare_models', 'BenchmarkSuite'], 'benchmarking'),
    ('.serialization', ['save_model_complete', 'load_model_complete', 'serialize_config',
                        'deserialize_config', 'ModelVersionManager'], 'serialization'),
    ('.logging', ['setup_logging', 'TrainingLogger', 'PerformanceLogger', 'ErrorTracker'], 'logging'),
    ('.reporting', ['generate_training_report', 'generate_model_report', 'generate_experiment_report',
                    'ReportGenerator'], 'reporting'),
    ('.conversion', ['convert_model_format', 'convert_data_format', 'convert_config_format',
                     'FormatConverter'], 'conversion'),
    ('.validation', ['validate_dataset', 'validate_model_config', 'validate_training_config',
                     'ValidationSuite'], 'validation'),
    ('.postprocessing', ['format_predictions', 'aggregate_predictions', 'apply_threshold',
                         'PostProcessor'], 'postprocessing'),
    ('.workflow', ['Workflow', 'Pipeline', 'Task', 'TaskStatus', 'WorkflowExecutor'], 'workflow'),
    ('.automation', ['AutoML', 'AutoTrainer', 'AutoPipeline', 'automated_model_selection'], 'automation'),
]

for module_path, attributes, _ in _optional_modules:
    _try_import(module_path, attributes)

try:
    from .model_generator import ModelGenerator
    from .training_generator import TrainingGenerator
    from .data_generator import DataGenerator
    from .evaluation_generator import EvaluationGenerator
    from .interface_generator import InterfaceGenerator
    from .config_generator import ConfigGenerator
    from .performance_generator import PerformanceGenerator
    from .utils_generator import UtilsGenerator
    from .deployment_generator import DeploymentGenerator
    from .testing_generator import TestingGenerator
    from .conversion_generator import ConversionGenerator
    from .monitoring_generator import MonitoringGenerator
    from .analysis_generator import AnalysisGenerator
    from .experimentation_generator import ExperimentationGenerator
    from .serialization_generator import SerializationGenerator
    from .validation_generator import ValidationGenerator
    from .security_generator import SecurityGenerator
    from .data_io_generator import DataIOGenerator
    from .reporting_generator import ReportingGenerator
    from .preprocessing_generator import PreprocessingGenerator
    from .postprocessing_generator import PostprocessingGenerator
    
    from .generator_config import GENERATOR_MAP, TRAINING_UTILS, GENERATION_GROUPS
    from .generator_registry import GeneratorRegistry, GeneratorFactory
    from .generation_strategy import (
        GenerationStrategy, CoreModelStrategy, TrainingStrategy,
        InterfaceStrategy, ConfigStrategy, StrategyOrchestrator,
    )
    
    __all__.extend([
        "ModelGenerator", "TrainingGenerator", "DataGenerator", "EvaluationGenerator",
        "InterfaceGenerator", "ConfigGenerator", "PerformanceGenerator", "UtilsGenerator",
        "DeploymentGenerator", "TestingGenerator", "ConversionGenerator", "MonitoringGenerator",
        "AnalysisGenerator", "ExperimentationGenerator", "SerializationGenerator",
        "ValidationGenerator", "SecurityGenerator", "DataIOGenerator", "ReportingGenerator",
        "PreprocessingGenerator", "PostprocessingGenerator",
        "GENERATOR_MAP", "TRAINING_UTILS", "GENERATION_GROUPS",
        "GeneratorRegistry", "GeneratorFactory", "GenerationStrategy",
        "CoreModelStrategy", "TrainingStrategy", "InterfaceStrategy",
        "ConfigStrategy", "StrategyOrchestrator",
    ])
except (ImportError, AttributeError):
    pass
