"""
Enhanced Blaze AI - Main Application Entry Point

This module provides the main entry point for the Enhanced Blaze AI system,
integrating all enhanced features with a clean, modular architecture.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Enhanced features imports
try:
    from enhanced_features.security import SecurityMiddleware, SecurityConfig
    from enhanced_features.monitoring import PerformanceMonitor, MonitoringConfig
    from enhanced_features.rate_limiting import RateLimiter, RateLimitConfig
    from enhanced_features.error_handling import ErrorHandlingOrchestrator, ErrorHandlingConfig
    from enhanced_features.health import HealthChecker, SystemHealth
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Enhanced features not available: {e}")
    ENHANCED_FEATURES_AVAILABLE = False

# Core application modules
from core.config import AppConfig, load_config
from core.logging import setup_logging
from core.exceptions import BlazeAIError, ServiceUnavailableError
from api.routes import create_api_router
from api.middleware import create_middleware_stack

# Configure logging
logger = logging.getLogger(__name__)


class BlazeAIApplication:
    """
    Main application class for Enhanced Blaze AI.
    
    This class encapsulates the application lifecycle and provides
    a clean interface for managing the enhanced features.
    """
    
    def __init__(self, config: AppConfig):
        """Initialize the Blaze AI application."""
        self.config = config
        self.app = None
        self.enhanced_features = {}
        self.health_checker = None
        
    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application."""
        # Create FastAPI instance with metadata
        self.app = FastAPI(
            title="Enhanced Blaze AI",
            description="Enterprise-Grade AI Platform with Advanced Features",
            version="2.1.0",
            docs_url=None,  # Custom docs endpoint
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        
        # Setup application lifecycle
        self.app.router.lifespan_context = self._create_lifespan_context()
        
        # Configure middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        # Setup exception handlers
        self._setup_exception_handlers()
        
        # Setup enhanced features if available
        if ENHANCED_FEATURES_AVAILABLE:
            self._setup_enhanced_features()
        
        return self.app
    
    def _create_lifespan_context(self):
        """Create application lifespan context manager."""
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info("🚀 Starting Enhanced Blaze AI...")
            await self._startup()
            yield
            # Shutdown
            logger.info("🛑 Shutting down Enhanced Blaze AI...")
            await self._shutdown()
        
        return lifespan
    
    async def _startup(self):
        """Application startup tasks."""
        try:
            # Initialize enhanced features
            if ENHANCED_FEATURES_AVAILABLE:
                await self._initialize_enhanced_features()
            
            # Initialize health checker
            self.health_checker = SystemHealth() if ENHANCED_FEATURES_AVAILABLE else None
            
            logger.info("✅ Enhanced Blaze AI startup completed")
            
        except Exception as e:
            logger.error(f"❌ Startup failed: {e}")
            raise
    
    async def _shutdown(self):
        """Application shutdown tasks."""
        try:
            # Cleanup enhanced features
            if ENHANCED_FEATURES_AVAILABLE:
                await self._cleanup_enhanced_features()
            
            logger.info("✅ Enhanced Blaze AI shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Shutdown failed: {e}")
    
    def _setup_middleware(self):
        """Configure application middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        if self.config.security.trusted_hosts:
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=self.config.security.trusted_hosts
            )
        
        # Enhanced security middleware
        if ENHANCED_FEATURES_AVAILABLE:
            security_config = SecurityConfig(
                jwt_secret_key=self.config.security.jwt_secret_key,
                jwt_algorithm=self.config.security.jwt_algorithm,
                jwt_expiration_minutes=self.config.security.jwt_expiration_minutes,
                api_key_header=self.config.security.api_key_header,
                rate_limit_enabled=self.config.security.rate_limit_enabled,
                threat_detection_enabled=self.config.security.threat_detection_enabled,
                input_validation_enabled=self.config.security.input_validation_enabled
            )
            
            security_middleware = SecurityMiddleware(security_config)
            self.app.add_middleware(security_middleware)
    
    def _setup_routes(self):
        """Configure application routes."""
        # API routes
        api_router = create_api_router()
        self.app.include_router(api_router, prefix="/api/v1")
        
        # Health check routes
        self._setup_health_routes()
        
        # Enhanced feature routes
        if ENHANCED_FEATURES_AVAILABLE:
            self._setup_enhanced_routes()
        
        # Documentation routes
        self._setup_docs_routes()
    
    def _setup_health_routes(self):
        """Setup health check endpoints."""
        @self.app.get("/health")
        async def health_check():
            """Basic health check endpoint."""
            return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
        
        @self.app.get("/health/detailed")
        async def detailed_health_check():
            """Detailed health check with enhanced features."""
            if self.health_checker:
                return await self.health_checker.get_system_health()
            return {"status": "healthy", "enhanced_features": False}
    
    def _setup_enhanced_routes(self):
        """Setup enhanced feature endpoints."""
        # Monitoring endpoints
        @self.app.get("/metrics")
        async def get_metrics():
            """Get application metrics."""
            if "monitoring" in self.enhanced_features:
                return await self.enhanced_features["monitoring"].get_metrics()
            return {"error": "Monitoring not available"}
        
        @self.app.get("/metrics/prometheus")
        async def get_prometheus_metrics():
            """Get Prometheus-formatted metrics."""
            if "monitoring" in self.enhanced_features:
                return await self.enhanced_features["monitoring"].get_prometheus_metrics()
            return {"error": "Monitoring not available"}
        
        # Rate limiting endpoints
        @self.app.get("/rate-limits/status")
        async def get_rate_limit_status():
            """Get current rate limit status."""
            if "rate_limiting" in self.enhanced_features:
                return await self.enhanced_features["rate_limiting"].get_status()
            return {"error": "Rate limiting not available"}
        
        # Security endpoints
        @self.app.get("/security/threats")
        async def get_security_threats():
            """Get recent security threats."""
            if "security" in self.enhanced_features:
                return await self.enhanced_features["security"].get_recent_threats()
            return {"error": "Security monitoring not available"}
    
    def _setup_docs_routes(self):
        """Setup documentation endpoints."""
        @self.app.get("/docs")
        async def custom_docs():
            """Custom documentation endpoint."""
            return {"message": "API Documentation", "docs_url": "/redoc"}
    
    def _setup_exception_handlers(self):
        """Setup custom exception handlers."""
        @self.app.exception_handler(BlazeAIError)
        async def blaze_ai_exception_handler(request: Request, exc: BlazeAIError):
            """Handle BlazeAI-specific exceptions."""
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.error_type,
                    "message": str(exc),
                    "details": exc.details,
                    "request_id": getattr(request.state, 'request_id', None)
                }
            )
        
        @self.app.exception_handler(ServiceUnavailableError)
        async def service_unavailable_handler(request: Request, exc: ServiceUnavailableError):
            """Handle service unavailable exceptions."""
            return JSONResponse(
                status_code=503,
                content={
                    "error": "service_unavailable",
                    "message": str(exc),
                    "retry_after": exc.retry_after
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle general exceptions."""
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred"
                }
            )
    
    async def _initialize_enhanced_features(self):
        """Initialize enhanced features."""
        try:
            # Initialize monitoring
            monitoring_config = MonitoringConfig(
                metrics_enabled=self.config.monitoring.metrics_enabled,
                system_metrics_enabled=self.config.monitoring.system_metrics_enabled,
                profiling_enabled=self.config.monitoring.profiling_enabled,
                alerting_enabled=self.config.monitoring.alerting_enabled,
                prometheus_enabled=self.config.monitoring.prometheus_enabled
            )
            
            self.enhanced_features["monitoring"] = PerformanceMonitor(monitoring_config)
            await self.enhanced_features["monitoring"].start()
            
            # Initialize rate limiting
            rate_limit_config = RateLimitConfig(
                default_limit=self.config.rate_limiting.default_limit,
                default_window=self.config.rate_limiting.default_window,
                storage_type=self.config.rate_limiting.storage_type,
                redis_url=self.config.rate_limiting.redis_url,
                adaptive_throttling=self.config.rate_limiting.adaptive_throttling
            )
            
            self.enhanced_features["rate_limiting"] = RateLimiter(rate_limit_config)
            
            # Initialize error handling
            error_handling_config = ErrorHandlingConfig(
                circuit_breaker_enabled=self.config.error_handling.circuit_breaker_enabled,
                retry_enabled=self.config.error_handling.retry_enabled,
                error_recovery_enabled=self.config.error_handling.error_recovery_enabled,
                max_retries=self.config.error_handling.max_retries,
                retry_delay=self.config.error_handling.retry_delay
            )
            
            self.enhanced_features["error_handling"] = ErrorHandlingOrchestrator(error_handling_config)
            
            # Initialize security (already done in middleware setup)
            logger.info("✅ Enhanced features initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize enhanced features: {e}")
            raise
    
    async def _cleanup_enhanced_features(self):
        """Cleanup enhanced features."""
        try:
            for feature_name, feature in self.enhanced_features.items():
                if hasattr(feature, 'stop'):
                    await feature.stop()
                elif hasattr(feature, 'cleanup'):
                    await feature.cleanup()
            
            logger.info("✅ Enhanced features cleaned up successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup enhanced features: {e}")


def create_app(config: Optional[AppConfig] = None) -> FastAPI:
    """Factory function to create the FastAPI application."""
    if config is None:
        config = load_config()
    
    app_instance = BlazeAIApplication(config)
    return app_instance.create_app()


def main():
    """Main entry point for the application."""
    try:
        # Load configuration
        config = load_config()
        
        # Setup logging
        setup_logging(config.logging)
        
        # Create application
        app = create_app(config)
        
        # Run server
        uvicorn.run(
            app,
            host=config.server.host,
            port=config.server.port,
            reload=config.server.reload,
            log_level=config.logging.level.lower()
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    main() 