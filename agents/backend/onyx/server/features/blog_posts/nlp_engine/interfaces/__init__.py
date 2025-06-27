"""
🔌 INTERFACES MODULE - Ports & Contracts
========================================

Define los contratos (interfaces/protocols) que deben implementar
las capas de infraestructura.
"""

# Analyzer interfaces
from .analyzers import (
    IAnalyzer, 
    IAnalyzerFactory, 
    IAdvancedAnalyzer, 
    IConfigurableAnalyzer
)

# Cache interfaces
from .cache import (
    ICacheRepository, 
    IDistributedCache, 
    ICacheKeyGenerator,
    ICacheEvictionPolicy,
    ICacheSerializer
)

# Metrics interfaces
from .metrics import (
    IMetricsCollector, 
    IPerformanceMonitor, 
    IHealthChecker,
    IAlertManager,
    IStructuredLogger,
    IMetricsExporter
)

# Config interfaces
from .config import (
    IConfigurationService, 
    IEnvironmentConfigLoader, 
    IFileConfigLoader,
    ISecretManager,
    IConfigValidator,
    IConfigMerger,
    IConfigTransformer
)

__all__ = [
    # Analyzer interfaces
    'IAnalyzer',
    'IAnalyzerFactory', 
    'IAdvancedAnalyzer', 
    'IConfigurableAnalyzer',
    
    # Cache interfaces
    'ICacheRepository',
    'IDistributedCache', 
    'ICacheKeyGenerator',
    'ICacheEvictionPolicy',
    'ICacheSerializer',
    
    # Metrics interfaces
    'IMetricsCollector',
    'IPerformanceMonitor', 
    'IHealthChecker',
    'IAlertManager',
    'IStructuredLogger',
    'IMetricsExporter',
    
    # Config interfaces
    'IConfigurationService',
    'IEnvironmentConfigLoader', 
    'IFileConfigLoader',
    'ISecretManager',
    'IConfigValidator',
    'IConfigMerger',
    'IConfigTransformer'
] 