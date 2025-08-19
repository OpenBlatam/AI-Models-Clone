from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
BUFFER_SIZE = 1024

import os
import sys
import asyncio
import signal
import time
import psutil
import gc
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import argparse
import json
    from dotenv import load_dotenv
import uvicorn
import structlog
from fastapi import FastAPI
from config_optimized import get_settings, setup_configuration
from api.optimization.enhanced_connection_pooling import create_enhanced_connection_pool_manager
from api.optimization.performance_optimizer import PerformanceOptimizer, OptimizationLevel
        import logging
            import resource
                import psutil
            from sqlalchemy.ext.asyncio import create_async_engine
            import redis.asyncio as redis
            import httpx
        from api.routes.__main__ import create_app, create_development_app, create_production_app
from typing import Any, List, Dict, Optional
#!/usr/bin/env python3
"""
Optimized Startup Script for HeyGen AI FastAPI Server
Enhanced startup with performance monitoring, health checks, and resource optimization.
"""


# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    load_dotenv()
except ImportError:
    pass



# =============================================================================
# Enhanced Logging
# =============================================================================

def setup_logging():
    """Setup enhanced structured logging."""
    try:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        return structlog.get_logger()
    except Exception:
        logging.basicConfig(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger("heygen_ai")

logger = setup_logging()

# =============================================================================
# System Resource Monitor
# =============================================================================

class SystemResourceMonitor:
    """Monitor system resources during startup and runtime."""
    
    def __init__(self) -> Any:
        self.start_time = datetime.now(timezone.utc)
        self.initial_memory = psutil.virtual_memory()
        self.initial_cpu = psutil.cpu_percent(interval=1)
        self.process = psutil.Process()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        disk = psutil.disk_usage('/')
        
        return {
            "memory_total_gb": memory.total / (1024**3),
            "memory_available_gb": memory.available / (1024**3),
            "memory_used_percent": memory.percent,
            "cpu_percent": cpu_percent,
            "disk_total_gb": disk.total / (1024**3),
            "disk_free_gb": disk.free / (1024**3),
            "disk_used_percent": (disk.used / disk.total) * 100,
            "process_memory_mb": self.process.memory_info().rss / (1024**2),
            "process_cpu_percent": self.process.cpu_percent(),
            "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds()
        }
    
    def log_system_status(self, stage: str):
        """Log system status at different stages."""
        info = self.get_system_info()
        logger.info(f"System status at {stage}", **info)
        
        # Check for potential issues
        warnings = []
        if info["memory_used_percent"] > 90:
            warnings.append("High memory usage")
        if info["cpu_percent"] > 90:
            warnings.append("High CPU usage")
        if info["disk_used_percent"] > 90:
            warnings.append("High disk usage")
        
        if warnings:
            logger.warning(f"System warnings at {stage}", warnings=warnings)

# =============================================================================
# Performance Optimizer
# =============================================================================

class StartupPerformanceOptimizer:
    """Optimize performance during startup."""
    
    def __init__(self, settings) -> Any:
        self.settings = settings
        self.optimizations_applied = []
    
    async def optimize_system(self) -> Any:
        """Apply system optimizations."""
        logger.info("Starting system optimizations")
        
        # Memory optimization
        if self.settings.memory_limit_mb:
            self._set_memory_limit()
        
        # Garbage collection optimization
        self._optimize_garbage_collection()
        
        # Process optimization
        self._optimize_process()
        
        # Network optimization
        self._optimize_network()
        
        logger.info("System optimizations completed", optimizations=self.optimizations_applied)
    
    def _set_memory_limit(self) -> Any:
        """Set memory limit for the process."""
        try:
            memory_limit = self.settings.memory_limit_mb * 1024 * 1024  # Convert to bytes
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
            self.optimizations_applied.append("memory_limit_set")
        except Exception as e:
            logger.warning("Failed to set memory limit", error=str(e))
    
    def _optimize_garbage_collection(self) -> Any:
        """Optimize garbage collection."""
        try:
            # Set garbage collection thresholds
            gc.set_threshold(
                self.settings.gc_threshold,
                self.settings.gc_threshold * 2,
                self.settings.gc_threshold * 4
            )
            
            # Enable generational garbage collection
            gc.enable()
            
            self.optimizations_applied.append("garbage_collection_optimized")
        except Exception as e:
            logger.warning("Failed to optimize garbage collection", error=str(e))
    
    def _optimize_process(self) -> Any:
        """Optimize process settings."""
        try:
            # Set process priority (lower number = higher priority)
            os.nice(0)  # Set to normal priority
            
            # Set CPU affinity if specified
            if hasattr(self.settings, 'cpu_affinity') and self.settings.cpu_affinity:
                process = psutil.Process()
                process.cpu_affinity(self.settings.cpu_affinity)
            
            self.optimizations_applied.append("process_optimized")
        except Exception as e:
            logger.warning("Failed to optimize process", error=str(e))
    
    def _optimize_network(self) -> Any:
        """Optimize network settings."""
        try:
            # These would require root privileges, so we just log the intent
            logger.info("Network optimizations would be applied with proper privileges")
            self.optimizations_applied.append("network_optimization_logged")
        except Exception as e:
            logger.warning("Failed to optimize network", error=str(e))

# =============================================================================
# Health Checker
# =============================================================================

class HealthChecker:
    """Perform health checks during startup."""
    
    def __init__(self, settings) -> Any:
        self.settings = settings
        self.checks_passed = []
        self.checks_failed = []
    
    async def perform_startup_checks(self) -> bool:
        """Perform all startup health checks."""
        logger.info("Starting health checks")
        
        checks = [
            self._check_database_connection,
            self._check_redis_connection,
            self._check_file_permissions,
            self._check_disk_space,
            self._check_memory_availability,
            self._check_network_connectivity
        ]
        
        for check in checks:
            try:
                await check()
                self.checks_passed.append(check.__name__)
            except Exception as e:
                self.checks_failed.append((check.__name__, str(e)))
                logger.error(f"Health check failed: {check.__name__}", error=str(e))
        
        # Log results
        logger.info("Health checks completed", 
                   passed=len(self.checks_passed), 
                   failed=len(self.checks_failed))
        
        if self.checks_failed:
            logger.error("Some health checks failed", failed_checks=self.checks_failed)
            return False
        
        return True
    
    async def _check_database_connection(self) -> Any:
        """Check database connectivity."""
        if not self.settings.database_url:
            return
        
        try:
            engine = create_async_engine(self.settings.database_url)
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            await engine.dispose()
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")
    
    async def _check_redis_connection(self) -> Any:
        """Check Redis connectivity."""
        if not self.settings.redis_url:
            return
        
        try:
            client = redis.from_url(self.settings.redis_url)
            await client.ping()
            await client.close()
        except Exception as e:
            raise Exception(f"Redis connection failed: {str(e)}")
    
    async def _check_file_permissions(self) -> Any:
        """Check file permissions."""
        directories = [
            self.settings.video_output_dir,
            self.settings.temp_dir,
            "logs"
        ]
        
        for directory in directories:
            path = Path(directory)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            
            if not os.access(path, os.W_OK):
                raise Exception(f"No write permission for directory: {directory}")
    
    async def _check_disk_space(self) -> Any:
        """Check available disk space."""
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        
        if free_gb < 1:  # Less than 1GB free
            raise Exception(f"Insufficient disk space: {free_gb:.2f}GB free")
    
    async def _check_memory_availability(self) -> Any:
        """Check available memory."""
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        
        if available_gb < 0.5:  # Less than 500MB available
            raise Exception(f"Insufficient memory: {available_gb:.2f}GB available")
    
    async def _check_network_connectivity(self) -> Any:
        """Check network connectivity."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.get("https://httpbin.org/get")
        except Exception as e:
            logger.warning(f"Network connectivity check failed: {str(e)}")

# =============================================================================
# Optimized Startup Manager
# =============================================================================

class OptimizedStartupManager:
    """Manage the optimized startup process."""
    
    def __init__(self) -> Any:
        self.settings = None
        self.system_monitor = SystemResourceMonitor()
        self.performance_optimizer = None
        self.health_checker = None
        self.connection_pool_manager = None
        self.startup_time = None
    
    async def startup(self) -> FastAPI:
        """Perform optimized startup."""
        self.startup_time = datetime.now(timezone.utc)
        logger.info("Starting optimized HeyGen AI FastAPI server")
        
        try:
            # Step 1: Load configuration
            await self._load_configuration()
            
            # Step 2: Log initial system status
            self.system_monitor.log_system_status("startup_begin")
            
            # Step 3: Apply performance optimizations
            await self._apply_optimizations()
            
            # Step 4: Perform health checks
            await self._perform_health_checks()
            
            # Step 5: Initialize connection pools
            await self._initialize_connections()
            
            # Step 6: Create and configure application
            app = await self._create_application()
            
            # Step 7: Final system status
            self.system_monitor.log_system_status("startup_complete")
            
            startup_duration = (datetime.now(timezone.utc) - self.startup_time).total_seconds()
            logger.info("Optimized startup completed successfully", 
                       startup_duration_seconds=startup_duration)
            
            return app
            
        except Exception as e:
            logger.error("Startup failed", error=str(e))
            raise
    
    async def _load_configuration(self) -> Any:
        """Load and validate configuration."""
        logger.info("Loading configuration")
        self.settings = setup_configuration()
        logger.info("Configuration loaded successfully")
    
    async def _apply_optimizations(self) -> Any:
        """Apply performance optimizations."""
        logger.info("Applying performance optimizations")
        self.performance_optimizer = StartupPerformanceOptimizer(self.settings)
        await self.performance_optimizer.optimize_system()
    
    async def _perform_health_checks(self) -> Any:
        """Perform health checks."""
        logger.info("Performing health checks")
        self.health_checker = HealthChecker(self.settings)
        success = await self.health_checker.perform_startup_checks()
        
        if not success:
            raise Exception("Health checks failed")
    
    async def _initialize_connections(self) -> Any:
        """Initialize connection pools."""
        logger.info("Initializing connection pools")
        
        self.connection_pool_manager = await create_enhanced_connection_pool_manager(
            database_url=self.settings.database_url,
            redis_url=self.settings.redis_url,
            max_database_connections=self.settings.max_database_connections,
            max_redis_connections=self.settings.max_redis_connections,
            health_check_interval=self.settings.health_check_interval,
            auto_scaling=self.settings.auto_scaling_enabled,
            monitoring_enabled=self.settings.enable_metrics
        )
    
    async def _create_application(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        logger.info("Creating FastAPI application")
        
        # Import application creation functions
        
        # Create application based on environment
        if self.settings.environment == "production":
            app = create_production_app()
        elif self.settings.environment == "development":
            app = create_development_app()
        else:
            app = create_app()
        
        # Add startup and shutdown events
        @app.on_event("startup")
        async def startup_event():
            
    """startup_event function."""
logger.info("FastAPI application startup event")
        
        @app.on_event("shutdown")
        async def shutdown_event():
            
    """shutdown_event function."""
logger.info("FastAPI application shutdown event")
            if self.connection_pool_manager:
                await self.connection_pool_manager.close()
        
        return app
    
    async def shutdown(self) -> Any:
        """Perform graceful shutdown."""
        logger.info("Starting graceful shutdown")
        
        try:
            if self.connection_pool_manager:
                await self.connection_pool_manager.close()
            
            # Final system status
            self.system_monitor.log_system_status("shutdown")
            
            uptime = (datetime.now(timezone.utc) - self.startup_time).total_seconds()
            logger.info("Graceful shutdown completed", uptime_seconds=uptime)
            
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))

# =============================================================================
# Command Line Interface
# =============================================================================

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Optimized HeyGen AI FastAPI Server")
    
    parser.add_argument(
        "--host", 
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host to bind to"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("PORT", "8000")),
        help="Port to bind to"
    )
    
    parser.add_argument(
        "--workers", 
        type=int, 
        default=int(os.getenv("WORKERS", "1")),
        help="Number of worker processes"
    )
    
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="Enable auto-reload"
    )
    
    parser.add_argument(
        "--log-level", 
        default=os.getenv("LOG_LEVEL", "info"),
        choices=["debug", "info", "warning", "error"],
        help="Log level"
    )
    
    parser.add_argument(
        "--config", 
        help="Path to configuration file"
    )
    
    return parser.parse_args()

# =============================================================================
# Main Function
# =============================================================================

async def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Create startup manager
    startup_manager = OptimizedStartupManager()
    
    try:
        # Perform startup
        app = await startup_manager.startup()
        
        # Configure uvicorn
        config = uvicorn.Config(
            app,
            host=args.host,
            port=args.port,
            workers=args.workers,
            reload=args.reload,
            log_level=args.log_level,
            access_log=True,
            proxy_headers=True,
            forwarded_allow_ips="*",
            timeout_keep_alive=30,
            timeout_graceful_shutdown=30,
            limit_concurrency=1000,
            limit_max_requests=10000,
            backlog=2048,
            loop="asyncio",
            http="httptools",
            ws="websockets"
        )
        
        # Start server
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", exc_info=True)
        sys.exit(1)
    finally:
        await startup_manager.shutdown()

match __name__:
    case "__main__":
    asyncio.run(main()) 