"""
Optimizers Module - Unified High-Performance Optimization System.

This module provides a comprehensive optimization framework with specialized
optimizers for different domains: serialization, hashing, networking, ML,
database operations, and more.

Architecture:
- Core optimizers: Basic functionality (serialization, hashing, compression)
- Specialized optimizers: Domain-specific optimizations (network, ML, database)
- Unified optimizer: Coordinates all optimizers with intelligent orchestration
- Configuration system: Centralized configuration with auto-tuning
"""

from typing import Optional, Dict, Any, List
import logging

# Core optimizers
from .config import OptimizationConfig, OptimizationLevel, FEATURES
from .serialization import SerializationOptimizer
from .hashing import HashingOptimizer
from .core import UnifiedOptimizer

# Specialized optimizers
try:
    from .database import DatabaseOptimizer, DatabaseConfig
    DATABASE_OPTIMIZER_AVAILABLE = True
except ImportError:
    DATABASE_OPTIMIZER_AVAILABLE = False
    DatabaseOptimizer = None
    DatabaseConfig = None

try:
    from .network import NetworkOptimizer, NetworkConfig
    NETWORK_OPTIMIZER_AVAILABLE = True
except ImportError:
    NETWORK_OPTIMIZER_AVAILABLE = False
    NetworkOptimizer = None
    NetworkConfig = None

try:
    from .ml import MLOptimizer, MLConfig
    ML_OPTIMIZER_AVAILABLE = True
except ImportError:
    ML_OPTIMIZER_AVAILABLE = False
    MLOptimizer = None
    MLConfig = None

logger = logging.getLogger(__name__)


class MasterOptimizer:
    """
    Master optimizer that coordinates all specialized optimizers.
    
    Provides a unified interface to access all optimization capabilities
    with intelligent resource management and performance monitoring.
    """
    
    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig.for_production()
        
        # Core optimizers (always available)
        self.core = UnifiedOptimizer(self.config)
        self.serialization = SerializationOptimizer(self.config)
        self.hashing = HashingOptimizer(self.config)
        
        # Specialized optimizers (conditional availability)
        self.database = None
        self.network = None
        self.ml = None
        
        # Initialize available specialized optimizers
        self._initialize_specialized_optimizers()
        
        # Performance metrics
        self.metrics = {
            "optimization_level": self.config.level.value,
            "available_optimizers": self._get_available_optimizers(),
            "total_initializations": 0,
            "successful_initializations": 0,
            "failed_initializations": 0
        }
    
    def _initialize_specialized_optimizers(self):
        """Initialize available specialized optimizers."""
        # Database optimizer
        if DATABASE_OPTIMIZER_AVAILABLE:
            try:
                db_config = DatabaseConfig()
                self.database = DatabaseOptimizer(db_config)
                logger.info("Database optimizer initialized")
            except Exception as e:
                logger.warning(f"Database optimizer initialization failed: {e}")
        
        # Network optimizer
        if NETWORK_OPTIMIZER_AVAILABLE:
            try:
                net_config = NetworkConfig()
                self.network = NetworkOptimizer(net_config)
                logger.info("Network optimizer initialized")
            except Exception as e:
                logger.warning(f"Network optimizer initialization failed: {e}")
        
        # ML optimizer
        if ML_OPTIMIZER_AVAILABLE:
            try:
                ml_config = MLConfig()
                self.ml = MLOptimizer(ml_config)
                logger.info("ML optimizer initialized")
            except Exception as e:
                logger.warning(f"ML optimizer initialization failed: {e}")
    
    def _get_available_optimizers(self) -> List[str]:
        """Get list of available optimizers."""
        optimizers = ["core", "serialization", "hashing"]
        
        if self.database is not None:
            optimizers.append("database")
        if self.network is not None:
            optimizers.append("network")
        if self.ml is not None:
            optimizers.append("ml")
        
        return optimizers
    
    async def initialize_all(self, **kwargs) -> Dict[str, Any]:
        """Initialize all available optimizers."""
        results = {}
        
        # Initialize core optimizers
        try:
            core_results = await self.core.initialize()
            results["core"] = core_results
            self.metrics["successful_initializations"] += 1
        except Exception as e:
            results["core"] = {"error": str(e)}
            self.metrics["failed_initializations"] += 1
        
        # Initialize database optimizer
        if self.database is not None:
            try:
                db_configs = kwargs.get('database_configs', {})
                if db_configs:
                    db_results = await self.database.initialize(db_configs)
                    results["database"] = db_results
                    self.metrics["successful_initializations"] += 1
            except Exception as e:
                results["database"] = {"error": str(e)}
                self.metrics["failed_initializations"] += 1
        
        # Initialize network optimizer
        if self.network is not None:
            try:
                net_results = await self.network.initialize()
                results["network"] = net_results
                self.metrics["successful_initializations"] += 1
            except Exception as e:
                results["network"] = {"error": str(e)}
                self.metrics["failed_initializations"] += 1
        
        # Initialize ML optimizer
        if self.ml is not None:
            try:
                ml_results = await self.ml.initialize()
                results["ml"] = ml_results
                self.metrics["successful_initializations"] += 1
            except Exception as e:
                results["ml"] = {"error": str(e)}
                self.metrics["failed_initializations"] += 1
        
        self.metrics["total_initializations"] += 1
        
        logger.info("Master optimizer initialization completed", 
                   successful=self.metrics["successful_initializations"],
                   failed=self.metrics["failed_initializations"])
        
        return results
    
    def get_optimizer(self, optimizer_type: str):
        """Get specific optimizer by type."""
        optimizer_map = {
            "core": self.core,
            "serialization": self.serialization,
            "hashing": self.hashing,
            "database": self.database,
            "network": self.network,
            "ml": self.ml
        }
        
        return optimizer_map.get(optimizer_type)
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all optimizers."""
        metrics = {
            "master": self.metrics,
            "features": FEATURES,
            "config": self.config.get_feature_report()
        }
        
        # Core optimizer metrics
        if hasattr(self.core, 'get_comprehensive_metrics'):
            metrics["core"] = self.core.get_comprehensive_metrics()
        
        # Database optimizer metrics
        if self.database is not None:
            try:
                metrics["database"] = self.database.get_performance_metrics()
            except Exception as e:
                metrics["database"] = {"error": str(e)}
        
        # Network optimizer metrics
        if self.network is not None:
            try:
                metrics["network"] = self.network.get_performance_metrics()
            except Exception as e:
                metrics["network"] = {"error": str(e)}
        
        # ML optimizer metrics
        if self.ml is not None:
            try:
                metrics["ml"] = self.ml.get_performance_metrics()
            except Exception as e:
                metrics["ml"] = {"error": str(e)}
        
        return metrics
    
    async def cleanup_all(self):
        """Cleanup all optimizers."""
        cleanup_results = []
        
        # Cleanup in reverse order
        optimizers_to_cleanup = [
            ("ml", self.ml),
            ("network", self.network),
            ("database", self.database),
            ("core", self.core)
        ]
        
        for name, optimizer in optimizers_to_cleanup:
            if optimizer is not None:
                try:
                    if hasattr(optimizer, 'cleanup'):
                        await optimizer.cleanup()
                    cleanup_results.append(f"{name}: success")
                except Exception as e:
                    cleanup_results.append(f"{name}: error - {e}")
        
        logger.info("Master optimizer cleanup completed", results=cleanup_results)


# Factory functions for easy instantiation
def create_master_optimizer(level: OptimizationLevel = OptimizationLevel.ULTRA) -> MasterOptimizer:
    """Create a master optimizer with specified optimization level."""
    if level == OptimizationLevel.BASIC:
        config = OptimizationConfig.for_testing()
    elif level == OptimizationLevel.ADVANCED:
        config = OptimizationConfig.for_development()
    else:  # ULTRA or EXPERIMENTAL
        config = OptimizationConfig.for_production()
        config.level = level
    
    return MasterOptimizer(config)


def create_specialized_optimizer(optimizer_type: str, **kwargs):
    """Create a specific specialized optimizer."""
    if optimizer_type == "database" and DATABASE_OPTIMIZER_AVAILABLE:
        config = DatabaseConfig(**kwargs)
        return DatabaseOptimizer(config)
    elif optimizer_type == "network" and NETWORK_OPTIMIZER_AVAILABLE:
        config = NetworkConfig(**kwargs)
        return NetworkOptimizer(config)
    elif optimizer_type == "ml" and ML_OPTIMIZER_AVAILABLE:
        config = MLConfig(**kwargs)
        return MLOptimizer(config)
    else:
        raise ValueError(f"Optimizer type '{optimizer_type}' not available")


# Main exports
__all__ = [
    # Core classes
    'MasterOptimizer',
    'OptimizationConfig',
    'OptimizationLevel',
    
    # Core optimizers
    'UnifiedOptimizer',
    'SerializationOptimizer', 
    'HashingOptimizer',
    
    # Specialized optimizers (conditional)
    'DatabaseOptimizer',
    'NetworkOptimizer',
    'MLOptimizer',
    
    # Configuration classes
    'DatabaseConfig',
    'NetworkConfig',
    'MLConfig',
    
    # Factory functions
    'create_master_optimizer',
    'create_specialized_optimizer',
    
    # Constants
    'FEATURES',
    'DATABASE_OPTIMIZER_AVAILABLE',
    'NETWORK_OPTIMIZER_AVAILABLE',
    'ML_OPTIMIZER_AVAILABLE'
]


# Module level convenience instance
DEFAULT_MASTER_OPTIMIZER = None


def get_default_master_optimizer() -> MasterOptimizer:
    """Get or create default master optimizer instance."""
    global DEFAULT_MASTER_OPTIMIZER
    
    if DEFAULT_MASTER_OPTIMIZER is None:
        DEFAULT_MASTER_OPTIMIZER = create_master_optimizer(OptimizationLevel.ULTRA)
    
    return DEFAULT_MASTER_OPTIMIZER


# Initialize logging
logger.info("Optimizers module loaded", 
           available_optimizers=len([o for o in [
               DATABASE_OPTIMIZER_AVAILABLE,
               NETWORK_OPTIMIZER_AVAILABLE, 
               ML_OPTIMIZER_AVAILABLE
           ] if o]),
           features_enabled=len([f for f in FEATURES.values() if f])) 