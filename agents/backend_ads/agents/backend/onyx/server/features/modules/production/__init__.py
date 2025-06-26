"""
Production Module - Enterprise-Grade Production Configuration.

This module consolidates all production functionality from legacy files:
- production_final_quantum.py (40KB)
- production_master.py (26KB) 
- production_app_ultra.py (34KB)
- quantum_prod.py (33KB)
- ultra_prod.py (25KB)
- production_enterprise.py (19KB)
- production_final.py (33KB)
- production_optimized.py (22KB)

Into a single, modular, enterprise-grade production system.
"""

from typing import Dict, Any, Optional, List, Union
import structlog

from .config import ProductionSettings, ProductionLevel, DeploymentEnvironment
from .app import create_production_app, ProductionApp
from .deployment import DeploymentManager, DockerConfig, KubernetesConfig
from .monitoring import ProductionMonitor, MetricsCollector, HealthChecker
from .middleware import ProductionMiddleware, PerformanceMiddleware
from .exceptions import ProductionException, DeploymentError
from .utils import ProductionUtils, SystemOptimizer

logger = structlog.get_logger(__name__)

# Global production instances
_global_app: Optional[ProductionApp] = None
_global_monitor: Optional[ProductionMonitor] = None
_deployment_manager: Optional[DeploymentManager] = None


def create_production_system(config: Optional[ProductionSettings] = None) -> Dict[str, Any]:
    """
    Factory function to create a complete production system.
    
    Args:
        config: Optional production configuration
        
    Returns:
        Dict[str, Any]: Dictionary containing all production components
    """
    if config is None:
        config = ProductionSettings()
    
    # Create production components
    app = create_production_app(config)
    monitor = ProductionMonitor(config)
    deployment_manager = DeploymentManager(config)
    metrics_collector = MetricsCollector(config)
    health_checker = HealthChecker(config)
    system_optimizer = SystemOptimizer(config)
    
    system = {
        "app": app,
        "monitor": monitor,
        "deployment_manager": deployment_manager,
        "metrics_collector": metrics_collector,
        "health_checker": health_checker,
        "system_optimizer": system_optimizer,
        "config": config
    }
    
    logger.info("Production system created",
               level=config.production_level.value,
               environment=config.environment.value,
               features_enabled=len([k for k, v in config.get_enabled_features().items() if v]))
    
    return system


def get_global_production_app(config: Optional[ProductionSettings] = None) -> ProductionApp:
    """Get or create the global production app instance."""
    global _global_app
    
    if _global_app is None:
        if config is None:
            config = ProductionSettings()
        _global_app = create_production_app(config)
        logger.info("Global production app created")
    
    return _global_app


def get_global_monitor(config: Optional[ProductionSettings] = None) -> ProductionMonitor:
    """Get or create the global production monitor."""
    global _global_monitor
    
    if _global_monitor is None:
        if config is None:
            config = ProductionSettings()
        _global_monitor = ProductionMonitor(config)
        logger.info("Global production monitor created")
    
    return _global_monitor


async def initialize_production_system(
    config: Optional[ProductionSettings] = None,
    database_url: Optional[str] = None,
    redis_url: Optional[str] = None,
    enable_monitoring: bool = True
) -> Dict[str, Any]:
    """
    Initialize the complete production system with all services.
    
    Args:
        config: Production configuration
        database_url: Database connection URL
        redis_url: Redis connection URL  
        enable_monitoring: Whether to enable monitoring
        
    Returns:
        Dict[str, Any]: Initialization results
    """
    if config is None:
        config = ProductionSettings()
    
    system = create_production_system(config)
    results = {}
    
    # Initialize application
    try:
        await system["app"].initialize(database_url=database_url, redis_url=redis_url)
        results["app"] = "initialized"
    except Exception as e:
        logger.error("App initialization failed", error=str(e))
        results["app"] = f"failed: {e}"
    
    # Initialize monitoring
    if enable_monitoring:
        try:
            await system["monitor"].initialize()
            results["monitor"] = "initialized"
        except Exception as e:
            logger.error("Monitor initialization failed", error=str(e))
            results["monitor"] = f"failed: {e}"
    
    # Initialize health checker
    try:
        await system["health_checker"].initialize()
        results["health_checker"] = "initialized"
    except Exception as e:
        logger.error("Health checker initialization failed", error=str(e))
        results["health_checker"] = f"failed: {e}"
    
    # Initialize metrics collector
    try:
        await system["metrics_collector"].initialize()
        results["metrics_collector"] = "initialized"
    except Exception as e:
        logger.error("Metrics collector initialization failed", error=str(e))
        results["metrics_collector"] = f"failed: {e}"
    
    logger.info("Production system initialization completed", results=results)
    return results


async def cleanup_production_system():
    """Cleanup all production services and connections."""
    global _global_app, _global_monitor, _deployment_manager
    
    cleanup_tasks = []
    
    if _global_app:
        cleanup_tasks.append(("app", _global_app.cleanup()))
    
    if _global_monitor:
        cleanup_tasks.append(("monitor", _global_monitor.cleanup()))
    
    if _deployment_manager:
        cleanup_tasks.append(("deployment", _deployment_manager.cleanup()))
    
    # Execute cleanup tasks
    for name, task in cleanup_tasks:
        try:
            await task
            logger.info(f"Production {name} cleaned up")
        except Exception as e:
            logger.warning(f"Failed to cleanup {name}: {e}")
    
    # Reset globals
    _global_app = None
    _global_monitor = None
    _deployment_manager = None
    
    logger.info("Production system cleanup completed")


# Production decorators for optimization
def production_optimize(
    level: ProductionLevel = ProductionLevel.STANDARD,
    enable_caching: bool = True,
    enable_monitoring: bool = True,
    enable_compression: bool = True
):
    """
    Decorator to optimize functions for production with enterprise features.
    
    Args:
        level: Production optimization level
        enable_caching: Whether to enable caching
        enable_monitoring: Whether to monitor performance
        enable_compression: Whether to enable compression
    """
    def decorator(func):
        from functools import wraps
        import time
        import asyncio
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            
            try:
                # Get global monitor for metrics
                if enable_monitoring:
                    monitor = get_global_monitor()
                
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Record metrics
                if enable_monitoring:
                    execution_time = (time.perf_counter() - start_time) * 1000
                    monitor.record_operation(
                        operation=func.__name__,
                        duration_ms=execution_time,
                        level=level.value,
                        success=True
                    )
                
                return result
                
            except Exception as e:
                # Record failure
                if enable_monitoring:
                    execution_time = (time.perf_counter() - start_time) * 1000
                    monitor = get_global_monitor()
                    monitor.record_operation(
                        operation=func.__name__,
                        duration_ms=execution_time,
                        level=level.value,
                        success=False,
                        error=str(e)
                    )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                
                if enable_monitoring:
                    execution_time = (time.perf_counter() - start_time) * 1000
                    monitor = get_global_monitor()
                    monitor.record_operation(
                        operation=func.__name__,
                        duration_ms=execution_time,
                        level=level.value,
                        success=True
                    )
                
                return result
                
            except Exception as e:
                if enable_monitoring:
                    execution_time = (time.perf_counter() - start_time) * 1000
                    monitor = get_global_monitor()
                    monitor.record_operation(
                        operation=func.__name__,
                        duration_ms=execution_time,
                        level=level.value,
                        success=False,
                        error=str(e)
                    )
                raise
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Quick access functions for common production operations
def quick_deploy(
    environment: DeploymentEnvironment = DeploymentEnvironment.STAGING,
    config: Optional[ProductionSettings] = None
) -> Dict[str, Any]:
    """Quick deployment with minimal configuration."""
    if config is None:
        config = ProductionSettings()
    
    deployment_manager = DeploymentManager(config)
    return deployment_manager.quick_deploy(environment)


def get_production_metrics() -> Dict[str, Any]:
    """Get comprehensive production metrics."""
    monitor = get_global_monitor()
    return monitor.get_comprehensive_metrics()


def optimize_production_system() -> Dict[str, Any]:
    """Optimize the production system for maximum performance."""
    config = ProductionSettings()
    optimizer = SystemOptimizer(config)
    return optimizer.optimize_system()


# Export main components
__all__ = [
    # Core configuration
    "ProductionSettings",
    "ProductionLevel",
    "DeploymentEnvironment",
    
    # Main components
    "ProductionApp",
    "ProductionMonitor", 
    "DeploymentManager",
    "MetricsCollector",
    "HealthChecker",
    "SystemOptimizer",
    
    # Middleware
    "ProductionMiddleware",
    "PerformanceMiddleware",
    
    # Exceptions
    "ProductionException",
    "DeploymentError",
    
    # Utilities
    "ProductionUtils",
    
    # Factory functions
    "create_production_system",
    "create_production_app",
    "get_global_production_app",
    "get_global_monitor",
    
    # System management
    "initialize_production_system",
    "cleanup_production_system",
    
    # Decorators
    "production_optimize",
    
    # Quick operations
    "quick_deploy",
    "get_production_metrics",
    "optimize_production_system"
] 