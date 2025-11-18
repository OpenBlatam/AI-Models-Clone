"""
Addiction Recovery AI - Sistema de IA para ayudar a dejar adicciones
Enhanced with PyTorch, Transformers, and Deep Learning
Ultra-Modular Layered Architecture V8 with Complete Component Separation
"""

__version__ = "3.11.0"
__author__ = "Blatam Academy"

# Core components
from .core.addiction_analyzer import AddictionAnalyzer
from .core.recovery_planner import RecoveryPlanner
from .core.progress_tracker import ProgressTracker
from .core.relapse_prevention import RelapsePrevention

# Deep Learning Models
from .core.models import (
    RecoverySentimentAnalyzer,
    RecoveryProgressPredictor,
    RelapseRiskPredictor,
    LLMRecoveryCoach,
    T5RecoveryCoach,
    EnhancedAddictionAnalyzer,
    create_sentiment_analyzer,
    create_progress_predictor,
    create_relapse_predictor,
    create_llm_coach,
    create_t5_coach,
    create_enhanced_analyzer
)

# Diffusion Models for Visualization
try:
    from .core.models.diffusion_models import (
        RecoveryProgressVisualizer,
        RecoveryChartGenerator,
        create_progress_visualizer,
        create_chart_generator
    )
    DIFFUSION_AVAILABLE = True
except ImportError:
    DIFFUSION_AVAILABLE = False

# Fast Inference Engines
try:
    from .core.models.fast_inference import (
        FastInferenceEngine,
        CachedTransformer,
        OptimizedDataLoader,
        create_fast_engine,
        create_cached_transformer
    )
    FAST_INFERENCE_AVAILABLE = True
except ImportError:
    FAST_INFERENCE_AVAILABLE = False

# Quantized Models
try:
    from .core.models.quantized_models import (
        QuantizedModel,
        OptimizedTransformer,
        create_quantized_model,
        create_optimized_transformer
    )
    QUANTIZED_AVAILABLE = True
except ImportError:
    QUANTIZED_AVAILABLE = False

# Advanced Gradio
try:
    from .utils.advanced_gradio import (
        AdvancedRecoveryGradio,
        create_advanced_gradio_app
    )
    ADVANCED_GRADIO_AVAILABLE = True
except ImportError:
    ADVANCED_GRADIO_AVAILABLE = False

# Debugging Tools
from .utils.debugging_tools import (
    ModelDebugger,
    PerformanceProfiler,
    TrainingMonitor,
    create_model_debugger,
    create_profiler,
    create_training_monitor
)

# Modular Architecture - Base Classes
from .core.base.base_model import (
    BaseModel,
    BasePredictor,
    BaseGenerator,
    BaseAnalyzer
)
from .core.base.base_trainer import (
    BaseTrainer,
    BaseEvaluator
)

# Ultra-Modular Layered Architecture V3
try:
    from .core.layers import (
        # Data Layer
        DataProcessor,
        NormalizationProcessor,
        TokenizationProcessor,
        PaddingProcessor,
        DataValidator,
        DatasetFactory,
        DataPipeline,
        DataLoaderFactory,
        # Model Layer
        ModelConfig,
        ModelRegistry,
        ModelBuilder,
        ModelFactory,
        ModelLoader,
        # Training Layer
        TrainingConfig,
        OptimizerFactory,
        SchedulerFactory,
        TrainingPipeline,
        TrainerFactory,
        # Inference Layer
        InferenceEngine,
        BatchProcessor,
        PredictorFactory,
        InferencePipeline,
        # Service Layer
        ServiceConfig,
        ServiceRegistry,
        ServiceContainer,
        ServiceFactory,
        # Interface Layer
        RequestProcessor,
        ResponseFormatter,
        APIHandler,
        InterfaceFactory,
        # Dependency Injection
        DependencyContainer,
        get_container,
        reset_container,
        inject_dependencies,
        register_service,
    )
    LAYERED_ARCHITECTURE_AVAILABLE = True
    
    # Micro-Modules - Ultra-Granular Components (V6 - Maximum Specialization)
    from .core.layers.micro_modules import (
        # Normalizers (from normalizers.py)
        NormalizerBase,
        StandardNormalizer,
        MinMaxNormalizer,
        RobustNormalizer,
        UnitVectorNormalizer,
        NormalizerFactory,
        # Tokenizers (from tokenizers.py)
        TokenizerBase,
        SimpleTokenizer,
        CharacterTokenizer,
        HuggingFaceTokenizer,
        BPETokenizer,
        TokenizerFactory,
        # Padders (from padders.py)
        PadderBase,
        ZeroPadder,
        RepeatPadder,
        ReflectPadder,
        CircularPadder,
        CustomPadder,
        PadderFactory,
        # Augmenters (from augmenters.py)
        AugmenterBase,
        NoiseAugmenter,
        DropoutAugmenter,
        ScaleAugmenter,
        ShiftAugmenter,
        FlipAugmenter,
        MixupAugmenter,
        CutoutAugmenter,
        ComposeAugmenter,
        AugmenterFactory,
        # Validators
        Validator,
        TensorValidator,
        ShapeValidator,
        RangeValidator,
        # Model Components - Specialized Initializers (from initializers.py)
        InitializerBase,
        XavierInitializer,
        KaimingInitializer,
        OrthogonalInitializer,
        UniformInitializer,
        NormalInitializer,
        ZeroInitializer,
        OnesInitializer,
        InitializerFactory,
        # Model Components - Specialized Compilers (from compilers.py)
        CompilerBase,
        TorchCompileCompiler,
        TorchScriptCompiler,
        TorchScriptScriptCompiler,
        OptimizeForInferenceCompiler,
        CompilerFactory,
        # Model Components - Specialized Optimizers (from optimizers.py)
        OptimizerBase,
        MixedPrecisionOptimizer,
        TorchScriptOptimizer,
        PruningOptimizer,
        FuseOptimizer,
        OptimizerFactory,
        # Model Components - Specialized Quantizers (from quantizers.py)
        QuantizerBase,
        DynamicQuantizer,
        StaticQuantizer,
        QATQuantizer,
        QuantizerFactory,
        # Loss Functions - Specialized (from losses.py)
        LossBase,
        MSELoss,
        MAELoss,
        BCELoss,
        CrossEntropyLoss,
        SmoothL1Loss,
        FocalLoss,
        LossFactory,
        # Model Components - Backward Compatibility
        ModelInitializer,
        ModelCompiler,
        ModelOptimizer,
        ModelQuantizer,
        # Training Components
        LossCalculator,
        GradientManager,
        LearningRateManager,
        CheckpointManager,
        # Inference Components
        BatchProcessor,
        CacheManager,
        OutputFormatter,
        PostProcessor,
    )
    MICRO_MODULES_AVAILABLE = True
except ImportError as e:
    LAYERED_ARCHITECTURE_AVAILABLE = False
    MICRO_MODULES_AVAILABLE = False
    logger.warning(f"Layered architecture not available: {e}")

# Import logger if not already imported
if 'logger' not in globals():
    import logging
    logger = logging.getLogger(__name__)

# Model Modules
from .core.models.modules import (
    MultiHeadAttention,
    SelfAttention,
    CrossAttention,
    TransformerBlock,
    EncoderBlock,
    DecoderBlock,
    PositionalEncoding,
    LearnablePositionalEncoding,
    TokenEmbedding,
    EmbeddingLayer,
    FeedForward,
    ResidualFeedForward,
    GatedFeedForward,
    LayerNorm,
    RMSNorm,
    AdaptiveLayerNorm
)

# Data Processors
from .core.data.processors import (
    BaseProcessor,
    FeatureProcessor,
    TextProcessor,
    SequenceProcessor
)

# Training Callbacks
from .core.training.callbacks import (
    BaseCallback,
    EarlyStoppingCallback,
    LearningRateSchedulerCallback,
    CheckpointCallback
)

# Inference Predictors
from .core.inference.predictors import (
    TensorPredictor,
    FeaturePredictor
)

# Validation
from .core.validation.validators import (
    InputValidator,
    ModelValidator,
    validate_input,
    validate_features,
    validate_text
)

# Testing
from .core.testing.model_tester import (
    ModelTester,
    create_model_tester
)

# Monitoring
from .core.monitoring.health_check import (
    SystemHealthMonitor,
    ModelHealthMonitor,
    create_system_monitor,
    create_model_monitor
)

# Error Handling
from .core.errors.custom_exceptions import (
    RecoveryAIError,
    ModelError,
    ModelLoadError,
    ModelInferenceError,
    ModelTrainingError,
    DataError,
    DataValidationError,
    DataProcessingError,
    ConfigurationError,
    InferenceError,
    CUDAOutOfMemoryError,
    ValidationError
)

from .core.errors.error_handler import (
    ErrorHandler,
    handle_errors,
    safe_inference
)

# Integration
from .core.integration.integrated_pipeline import (
    IntegratedPipeline,
    create_integrated_pipeline
)

# Logging
from .core.logging.structured_logger import (
    StructuredFormatter,
    ModelLogger,
    create_model_logger
)

# Benchmarking
from .core.benchmarking.benchmark import (
    ModelBenchmark,
    create_benchmark
)

# Additional Utilities
from .core.utils.performance_utils import (
    PerformanceOptimizer,
    enable_optimizations,
    profile_model
)

from .core.utils.model_initialization import (
    init_weights_xavier,
    init_weights_kaiming,
    init_weights_orthogonal,
    init_weights_normal,
    init_weights_zero,
    initialize_model
)

# Visualization
from .core.visualization.visualizer import (
    TrainingVisualizer,
    ModelVisualizer,
    create_training_visualizer,
    create_model_visualizer
)

# Security
from .core.security.model_security import (
    ModelSecurity,
    compute_model_hash,
    verify_model_integrity,
    sanitize_input
)

# Caching
from .core.caching.smart_cache import (
    SmartCache,
    create_smart_cache
)

# Advanced Metrics
from .core.metrics.advanced_metrics import (
    AdvancedMetrics,
    calculate_regression_metrics,
    calculate_classification_metrics,
    calculate_correlation
)

# Serialization
from .core.serialization.model_serializer import (
    ModelSerializer,
    save_model,
    load_model
)

# Export
from .core.export.model_exporter import (
    ModelExporter,
    export_to_onnx,
    export_to_torchscript
)

# Helpers
from .core.helpers.helper_functions import (
    get_device,
    count_parameters,
    freeze_layers,
    unfreeze_layers,
    set_learning_rate,
    get_learning_rate,
    format_number
)

# CI/CD
from .core.ci_cd.deployment_utils import (
    DeploymentConfig,
    HealthCheck,
    get_deployment_config,
    check_system_health,
    check_model_health
)
from .core.factories.model_factory import (
    ModelFactory,
    ModelBuilder
)
from .core.factories.trainer_factory import (
    TrainerFactory
)
from .core.config.config_loader import (
    ConfigLoader,
    get_config
)
from .core.data.data_loader_factory import (
    DataLoaderFactory
)
from .core.plugins.plugin_manager import (
    Plugin,
    PluginManager,
    get_plugin_manager
)

# Experiment Tracking
try:
    from .core.experiments.experiment_tracker import (
        ExperimentTracker,
        create_tracker
    )
    EXPERIMENT_TRACKING_AVAILABLE = True
except ImportError:
    EXPERIMENT_TRACKING_AVAILABLE = False

# Data Processing
from .core.data.datasets.recovery_dataset import (
    RecoveryDataset,
    SequenceDataset,
    TextDataset,
    create_recovery_dataset,
    create_sequence_dataset,
    create_text_dataset
)

# Evaluation
from .core.evaluation.metrics import (
    MetricsCalculator,
    ModelEvaluator,
    create_evaluator
)

# Checkpointing
from .core.checkpointing.checkpoint_manager import (
    CheckpointManager,
    create_checkpoint_manager
)

# Ultra-Fast Optimization
from .core.optimization.ultra_fast_inference import (
    UltraFastInference,
    AsyncInferenceEngine,
    EmbeddingCache,
    BatchOptimizer,
    create_ultra_fast_inference,
    create_async_engine,
    create_embedding_cache
)

# Memory Optimization
from .core.optimization.memory_optimizer import (
    MemoryOptimizer,
    GradientCheckpointing,
    optimize_model_memory,
    clear_memory_cache,
    get_memory_stats
)

# Pipeline Optimization
from .core.optimization.pipeline_optimizer import (
    InferencePipeline,
    StreamingInference,
    create_inference_pipeline,
    create_streaming_inference
)

# Utilities
from .utils.model_utils import (
    count_parameters,
    get_model_size,
    freeze_model,
    unfreeze_model,
    freeze_layers,
    get_layer_output_shape,
    compare_models,
    export_model,
    load_model_from_checkpoint
)

from .utils.data_utils import (
    normalize_features,
    split_data,
    create_sequences,
    augment_data,
    balance_dataset,
    create_cross_validation_splits
)

# Training
from .training.recovery_trainer import RecoveryModelTrainer, create_trainer
from .training.lora_trainer import LoRATrainer, apply_lora_to_model, get_lora_parameters
from .training.distributed_trainer import DistributedTrainer, setup_distributed, cleanup_distributed
from .training.evaluator import ModelEvaluator

# Gradio Interface
from .utils.gradio_recovery import RecoveryGradioInterface, create_recovery_gradio_app

# Fast components
from .core.fast_analyzer import FastRecoveryAnalyzer, create_fast_analyzer
from .core.ultra_fast_engine import UltraFastRecoveryEngine, create_ultra_fast_engine

# Advanced features
from .core.models.onnx_optimizer import (
    export_to_onnx, optimize_onnx, ONNXRuntimeInference
)
from .core.models.model_optimization import (
    ModelPruner, KnowledgeDistillation, create_lightweight_student
)
from .utils.enhanced_gradio import EnhancedRecoveryGradio, create_enhanced_gradio_app
from .utils.error_handler import (
    ErrorHandler, RecoveryAIError, ModelLoadError, InferenceError, CUDAOutOfMemoryError
)
from .utils.precomputation import (
    EmbeddingCache, FeaturePreprocessor, BatchPreprocessor, precompute_embeddings
)
from .utils.async_inference import (
    AsyncInferenceEngine, InferenceQueue, ParallelInference
)
from .utils.profiler import (
    PerformanceProfiler, ModelProfiler, SystemMonitor
)
from .utils.data_augmentation import (
    FeatureAugmentation, SequenceAugmentation, AugmentationPipeline,
    create_feature_augmentation_pipeline, create_sequence_augmentation_pipeline
)
from .utils.advanced_logging import (
    StructuredLogger, MetricsTracker, TrainingLogger, setup_logging
)
from .core.models.model_ensembling import (
    ModelEnsemble, StackingEnsemble, create_ensemble, create_stacking_ensemble
)
from .utils.hyperparameter_optimization import (
    HyperparameterOptimizer, GridSearchOptimizer
)
from .utils.model_versioning import (
    ModelVersion, ModelRegistry, ModelComparator
)
from .utils.ab_testing import (
    ABTest, MultiVariateTest
)
from .utils.model_interpretability import (
    ModelInterpreter, AttentionVisualizer
)
from .utils.continuous_learning import (
    OnlineLearner, IncrementalLearner, AdaptiveLearningRate
)
from .utils.automl import (
    AutoML, NeuralArchitectureSearch
)
from .utils.model_serving import (
    ModelServer, ModelCache, RateLimiter, retry_on_failure, HealthMonitor
)
from .utils.advanced_validation import (
    DataValidator, AnomalyDetector, DataQualityChecker
)
from .utils.advanced_compression import (
    AdvancedQuantization, ModelCompressor, TensorRTOptimizer
)
from .utils.security import (
    APIKeyManager, InputSanitizer, RateLimiter as SecurityRateLimiter, SecureHash
)
from .config.config_manager import ConfigManager, load_config
from .utils.metrics_dashboard import MetricsDashboard, PerformanceTracker
from .utils.model_utils import (
    count_parameters, get_model_size, freeze_model,
    transfer_weights, get_layer_info, compare_models,
    save_model_checkpoint, load_model_checkpoint
)
from .utils.experiment_tracking import (
    ExperimentTracker, TrainingLogger as ExperimentTrainingLogger
)
from .utils.visualization import (
    ModelVisualizer, ProgressVisualizer
)
from .utils.data_pipeline import (
    RecoveryDataset, SequenceDataset, DataPipeline, DataAugmentationPipeline
)
from .utils.streaming import (
    StreamProcessor, RealTimePredictor
)
from .utils.distributed_inference import (
    DistributedInference
)
from .utils.advanced_caching import (
    LRUCache, PersistentCache, CacheDecorator
)
from .utils.multi_tenant import (
    TenantManager, TenantIsolation
)
from .utils.backup_recovery import (
    ModelBackup, DataBackup
)
from .utils.monitoring_dashboard import (
    SystemMonitor, PerformanceMonitor
)
from .utils.error_recovery import (
    CircuitBreaker, RetryHandler, GracefulDegradation
)
from .utils.analytics import (
    RecoveryAnalytics, CohortAnalysis
)
from .utils.notifications import (
    NotificationManager, NotificationLevel, AlertSystem
)
from .utils.integration import (
    ExternalAPIClient, WebhookHandler, DataExporter
)
from .utils.load_balancer import (
    LoadBalancer, ModelPool
)
from .utils.feature_store import (
    FeatureStore, EmbeddingStore
)
from .utils.scheduler import (
    TaskScheduler, ModelUpdateScheduler
)
from .api.graphql_api import GraphQLAPI
from .utils.message_queue import (
    MessageQueue, EventStream
)
from .utils.api_versioning import (
    APIVersion, VersionRouter, versioned
)
from .utils.service_discovery import (
    ServiceRegistry, ServiceDiscovery
)
from .utils.benchmarking import (
    Benchmark, ModelBenchmark
)
from .utils.advanced_testing import (
    ModelTester, DataTester, MockFactory
)
from .utils.documentation_generator import (
    DocumentationGenerator
)
from .utils.resource_manager import (
    ResourceMonitor, MemoryManager, ResourceLimiter
)
from .utils.advanced_config import (
    ConfigManager, ModelConfig, TrainingConfig, InferenceConfig
)
from .utils.advanced_pipeline import (
    ProcessingPipeline, PipelineStage, BatchProcessor
)
from .utils.session_manager import (
    SessionManager, Session
)
from .utils.advanced_logging import (
    StructuredLogger, JSONFormatter, LogAggregator
)
from .utils.rate_limiter_advanced import (
    AdvancedRateLimiter, TokenBucket, SlidingWindowLimiter
)

__all__ = [
    # Core
    "AddictionAnalyzer",
    "RecoveryPlanner",
    "ProgressTracker",
    "RelapsePrevention",
    # Models
    "RecoverySentimentAnalyzer",
    "RecoveryProgressPredictor",
    "RelapseRiskPredictor",
    "LLMRecoveryCoach",
    "T5RecoveryCoach",
    "EnhancedAddictionAnalyzer",
    "create_sentiment_analyzer",
    "create_progress_predictor",
    "create_relapse_predictor",
    "create_llm_coach",
    "create_t5_coach",
    "create_enhanced_analyzer",
    # Diffusion Models
    "RecoveryProgressVisualizer",
    "RecoveryChartGenerator",
    "create_progress_visualizer",
    "create_chart_generator",
    "DIFFUSION_AVAILABLE",
    # Fast Inference
    "FastInferenceEngine",
    "CachedTransformer",
    "OptimizedDataLoader",
    "create_fast_engine",
    "create_cached_transformer",
    "FAST_INFERENCE_AVAILABLE",
    # Quantized Models
    "QuantizedModel",
    "OptimizedTransformer",
    "create_quantized_model",
    "create_optimized_transformer",
    "QUANTIZED_AVAILABLE",
    # Advanced Gradio
    "AdvancedRecoveryGradio",
    "create_advanced_gradio_app",
    "ADVANCED_GRADIO_AVAILABLE",
    # Debugging Tools
    "ModelDebugger",
    "PerformanceProfiler",
    "TrainingMonitor",
    "create_model_debugger",
    "create_profiler",
    "create_training_monitor",
    # Modular Architecture
    "BaseModel",
    "BasePredictor",
    "BaseGenerator",
    "BaseAnalyzer",
    "BaseTrainer",
    "BaseEvaluator",
    "ModelFactory",
    "ModelBuilder",
    "TrainerFactory",
    "ConfigLoader",
    "get_config",
    "DataLoaderFactory",
    "Plugin",
    "PluginManager",
    "get_plugin_manager",
    # Model Modules
    "MultiHeadAttention",
    "SelfAttention",
    "CrossAttention",
    "TransformerBlock",
    "EncoderBlock",
    "DecoderBlock",
    "PositionalEncoding",
    "LearnablePositionalEncoding",
    "TokenEmbedding",
    "EmbeddingLayer",
    "FeedForward",
    "ResidualFeedForward",
    "GatedFeedForward",
    "LayerNorm",
    "RMSNorm",
    "AdaptiveLayerNorm",
    # Data Processors
    "BaseProcessor",
    "FeatureProcessor",
    "TextProcessor",
    "SequenceProcessor",
    # Training Callbacks
    "BaseCallback",
    "EarlyStoppingCallback",
    "LearningRateSchedulerCallback",
    "CheckpointCallback",
    # Inference Predictors
    "TensorPredictor",
    "FeaturePredictor",
    # Experiment Tracking
    "ExperimentTracker",
    "create_tracker",
    "EXPERIMENT_TRACKING_AVAILABLE",
    # Data Processing
    "RecoveryDataset",
    "SequenceDataset",
    "TextDataset",
    "create_recovery_dataset",
    "create_sequence_dataset",
    "create_text_dataset",
    # Evaluation
    "MetricsCalculator",
    "ModelEvaluator",
    "create_evaluator",
    # Checkpointing
    "CheckpointManager",
    "create_checkpoint_manager",
    # Ultra-Fast Optimization
    "UltraFastInference",
    "AsyncInferenceEngine",
    "EmbeddingCache",
    "BatchOptimizer",
    "create_ultra_fast_inference",
    "create_async_engine",
    "create_embedding_cache",
    # Memory Optimization
    "MemoryOptimizer",
    "GradientCheckpointing",
    "optimize_model_memory",
    "clear_memory_cache",
    "get_memory_stats",
    # Pipeline Optimization
    "InferencePipeline",
    "StreamingInference",
    "create_inference_pipeline",
    "create_streaming_inference",
    # Utilities
    "count_parameters",
    "get_model_size",
    "freeze_model",
    "unfreeze_model",
    "freeze_layers",
    "get_layer_output_shape",
    "compare_models",
    "export_model",
    "load_model_from_checkpoint",
    "normalize_features",
    "split_data",
    "create_sequences",
    "augment_data",
    "balance_dataset",
    "create_cross_validation_splits",
    # Validation
    "InputValidator",
    "ModelValidator",
    "validate_input",
    "validate_features",
    "validate_text",
    # Testing
    "ModelTester",
    "create_model_tester",
    # Monitoring
    "SystemHealthMonitor",
    "ModelHealthMonitor",
    "create_system_monitor",
    "create_model_monitor",
    # Error Handling
    "RecoveryAIError",
    "ModelError",
    "ModelLoadError",
    "ModelInferenceError",
    "ModelTrainingError",
    "DataError",
    "DataValidationError",
    "DataProcessingError",
    "ConfigurationError",
    "InferenceError",
    "CUDAOutOfMemoryError",
    "ValidationError",
    "ErrorHandler",
    "handle_errors",
    "safe_inference",
    # Integration
    "IntegratedPipeline",
    "create_integrated_pipeline",
    # Logging
    "StructuredFormatter",
    "ModelLogger",
    "create_model_logger",
    # Benchmarking
    "ModelBenchmark",
    "create_benchmark",
    # Additional Utilities
    "PerformanceOptimizer",
    "enable_optimizations",
    "profile_model",
    "init_weights_xavier",
    "init_weights_kaiming",
    "init_weights_orthogonal",
    "init_weights_normal",
    "init_weights_zero",
    "initialize_model",
    # Visualization
    "TrainingVisualizer",
    "ModelVisualizer",
    "create_training_visualizer",
    "create_model_visualizer",
    # Security
    "ModelSecurity",
    "compute_model_hash",
    "verify_model_integrity",
    "sanitize_input",
    # Caching
    "SmartCache",
    "create_smart_cache",
    # Advanced Metrics
    "AdvancedMetrics",
    "calculate_regression_metrics",
    "calculate_classification_metrics",
    "calculate_correlation",
    # Serialization
    "ModelSerializer",
    "save_model",
    "load_model",
    # Export
    "ModelExporter",
    "export_to_onnx",
    "export_to_torchscript",
    # Helpers
    "get_device",
    "count_parameters",
    "freeze_layers",
    "unfreeze_layers",
    "set_learning_rate",
    "get_learning_rate",
    "format_number",
    # CI/CD
    "DeploymentConfig",
    "HealthCheck",
    "get_deployment_config",
    "check_system_health",
    "check_model_health",
    # Training
    "RecoveryModelTrainer",
    "create_trainer",
    "LoRATrainer",
    "apply_lora_to_model",
    "get_lora_parameters",
    "DistributedTrainer",
    "setup_distributed",
    "cleanup_distributed",
    "ModelEvaluator",
    # Gradio
    "RecoveryGradioInterface",
    "create_recovery_gradio_app",
    # Fast
    "FastRecoveryAnalyzer",
    "create_fast_analyzer",
    "UltraFastRecoveryEngine",
    "create_ultra_fast_engine",
    # Advanced
    "export_to_onnx",
    "optimize_onnx",
    "ONNXRuntimeInference",
    "ModelPruner",
    "KnowledgeDistillation",
    "create_lightweight_student",
    "EnhancedRecoveryGradio",
    "create_enhanced_gradio_app",
    "ErrorHandler",
    "RecoveryAIError",
    "ModelLoadError",
    "InferenceError",
    "CUDAOutOfMemoryError",
    # Precomputation
    "EmbeddingCache",
    "FeaturePreprocessor",
    "BatchPreprocessor",
    "precompute_embeddings",
    # Async Inference
    "AsyncInferenceEngine",
    "InferenceQueue",
    "ParallelInference",
    # Profiling
    "PerformanceProfiler",
    "ModelProfiler",
    "SystemMonitor",
    # Data Augmentation
    "FeatureAugmentation",
    "SequenceAugmentation",
    "AugmentationPipeline",
    "create_feature_augmentation_pipeline",
    "create_sequence_augmentation_pipeline",
    # Logging
    "StructuredLogger",
    "MetricsTracker",
    "TrainingLogger",
    "setup_logging",
    # Ensembling
    "ModelEnsemble",
    "StackingEnsemble",
    "create_ensemble",
    "create_stacking_ensemble",
    # Hyperparameter Optimization
    "HyperparameterOptimizer",
    "GridSearchOptimizer",
    # Model Versioning
    "ModelVersion",
    "ModelRegistry",
    "ModelComparator",
    # A/B Testing
    "ABTest",
    "MultiVariateTest",
    # Model Interpretability
    "ModelInterpreter",
    "AttentionVisualizer",
    # Continuous Learning
    "OnlineLearner",
    "IncrementalLearner",
    "AdaptiveLearningRate",
    # AutoML
    "AutoML",
    "NeuralArchitectureSearch",
    # Model Serving
    "ModelServer",
    "ModelCache",
    "RateLimiter",
    "retry_on_failure",
    "HealthMonitor",
    # Advanced Validation
    "DataValidator",
    "AnomalyDetector",
    "DataQualityChecker",
    # Advanced Compression
    "AdvancedQuantization",
    "ModelCompressor",
    "TensorRTOptimizer",
    # Security
    "APIKeyManager",
    "InputSanitizer",
    "SecurityRateLimiter",
    "SecureHash",
    # Configuration
    "ConfigManager",
    "load_config",
    # Metrics Dashboard
    "MetricsDashboard",
    "PerformanceTracker",
    # Model Utils
    "count_parameters",
    "get_model_size",
    "freeze_model",
    "transfer_weights",
    "get_layer_info",
    "compare_models",
    "save_model_checkpoint",
    "load_model_checkpoint",
    # Experiment Tracking
    "ExperimentTracker",
    "ExperimentTrainingLogger",
    # Visualization
    "ModelVisualizer",
    "ProgressVisualizer",
    # Data Pipeline
    "RecoveryDataset",
    "SequenceDataset",
    "DataPipeline",
    "DataAugmentationPipeline",
    # Streaming
    "StreamProcessor",
    "RealTimePredictor",
    # Distributed Inference
    "DistributedInference",
    # Advanced Caching
    "LRUCache",
    "PersistentCache",
    "CacheDecorator",
    # Multi-Tenant
    "TenantManager",
    "TenantIsolation",
    # Backup & Recovery
    "ModelBackup",
    "DataBackup",
    # Monitoring Dashboard
    "SystemMonitor",
    "PerformanceMonitor",
    # Error Recovery
    "CircuitBreaker",
    "RetryHandler",
    "GracefulDegradation",
    # Analytics
    "RecoveryAnalytics",
    "CohortAnalysis",
    # Notifications
    "NotificationManager",
    "NotificationLevel",
    "AlertSystem",
    # Integration
    "ExternalAPIClient",
    "WebhookHandler",
    "DataExporter",
    # Load Balancing
    "LoadBalancer",
    "ModelPool",
    # Feature Store
    "FeatureStore",
    "EmbeddingStore",
    # Scheduling
    "TaskScheduler",
    "ModelUpdateScheduler",
    # GraphQL API
    "GraphQLAPI",
    # Message Queue
    "MessageQueue",
    "EventStream",
    # API Versioning
    "APIVersion",
    "VersionRouter",
    "versioned",
    # Service Discovery
    "ServiceRegistry",
    "ServiceDiscovery",
    # Benchmarking
    "Benchmark",
    "ModelBenchmark",
    # Advanced Testing
    "ModelTester",
    "DataTester",
    "MockFactory",
    # Documentation
    "DocumentationGenerator",
    # Resource Management
    "ResourceMonitor",
    "MemoryManager",
    "ResourceLimiter",
    # Advanced Configuration
    "ConfigManager",
    "ModelConfig",
    "TrainingConfig",
    "InferenceConfig",
    # Advanced Pipeline
    "ProcessingPipeline",
    "PipelineStage",
    "BatchProcessor",
    # Session Management
    "SessionManager",
    "Session",
    # Advanced Logging
    "StructuredLogger",
    "JSONFormatter",
    "LogAggregator",
    # Advanced Rate Limiting
    "AdvancedRateLimiter",
    "TokenBucket",
    "SlidingWindowLimiter",
]

