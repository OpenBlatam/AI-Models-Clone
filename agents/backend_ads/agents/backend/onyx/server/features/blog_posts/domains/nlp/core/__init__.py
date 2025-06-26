"""Core module for the Modular NLP System."""

# Import all interfaces
from .interfaces import (
    AnalysisType,
    Priority,
    AnalysisResult,
    AnalysisConfig,
    IAnalyzer,
    IAnalyzerManager,
    IEnhancer,
    IEnhancementManager,
    IConfiguration,
    ICache,
    IPlugin,
    INLPEngine,
    AnalysisResults,
    EnhancementConfig,
    Metadata,
)

# Import all exceptions
from .exceptions import (
    NLPException,
    AnalyzerException,
    ConfigurationException,
    PluginException,
    EnhancementException,
    CacheException,
    AnalyzerNotAvailableException,
    AnalyzerTimeoutException,
    InvalidInputException,
    AnalysisFailedException,
    InvalidConfigurationException,
    MissingConfigurationException,
    PluginLoadException,
    PluginInitializationException,
    PluginConflictException,
    EnhancementFailedException,
    UnsupportedEnhancementException,
    CacheConnectionException,
    CacheOperationException,
    DependencyException,
    ResourceException,
    check_dependency,
    check_resource,
)

# Import configuration components
from .config import (
    ConfigSource,
    CacheConfig,
    LoggingConfig,
    PerformanceConfig,
    QualityConfig,
    NLPSystemConfig,
    ConfigurationManager,
    get_config,
    initialize_config,
    reset_config,
)

# Import registry components
from .registry import (
    ComponentInfo,
    ComponentRegistry,
    AnalyzerRegistry,
    get_analyzer_registry,
    reset_registries,
)

__version__ = "1.0.0"
__author__ = "Blatam Academy NLP Team" 