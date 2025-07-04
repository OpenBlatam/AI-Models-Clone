"""
🚀 ULTRA-EXTREME V5 - API GATEWAY
==================================

Ultra-extreme API Gateway with:
- Service discovery ultra-inteligente
- Load balancing ultra-adaptativo
- Circuit breaker ultra-robusto
- Rate limiting ultra-inteligente
- Monitoring ultra-avanzado
- Security ultra-extrema
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog
from prometheus_client import make_asgi_app
import httpx
import redis.asyncio as redis
from pydantic import BaseSettings

# Import our ultra-extreme modules
from .middleware.auth_middleware import AuthMiddleware
from .middleware.rate_limit_middleware import RateLimitMiddleware
from .middleware.circuit_breaker import CircuitBreakerMiddleware
from .middleware.load_balancer import LoadBalancerMiddleware
from .middleware.monitoring_middleware import MonitoringMiddleware
from .routes.content_routes import content_router
from .routes.optimization_routes import optimization_router
from .routes.ai_routes import ai_router
from .routes.health_routes import health_router
from .config.settings import GatewaySettings
from .config.service_discovery import ServiceDiscovery


class UltraExtremeGateway:
    """Ultra-extreme API Gateway"""
    
    def __init__(self):
        self.settings = GatewaySettings()
        self.app = None
        self.service_discovery = None
        self.http_client = None
        self.redis_client = None
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize services
        self._initialize_services()
        
        # Create FastAPI app
        self._create_fastapi_app()
    
    def _setup_logging(self):
        """Setup structured logging"""
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
        
        logging.basicConfig(
            level=getattr(logging, self.settings.LOG_LEVEL),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        self.logger = structlog.get_logger(__name__)
        self.logger.info("Gateway logging configured successfully")
    
    def _initialize_services(self):
        """Initialize all services"""
        self.logger.info("Initializing ultra-extreme gateway services")
        
        # Initialize service discovery
        self.service_discovery = ServiceDiscovery(
            redis_url=self.settings.REDIS_URL,
            service_registry_key=self.settings.SERVICE_REGISTRY_KEY
        )
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=self.settings.HTTP_CONNECT_TIMEOUT,
                read=self.settings.HTTP_READ_TIMEOUT,
                write=self.settings.HTTP_WRITE_TIMEOUT,
                pool=self.settings.HTTP_POOL_TIMEOUT
            ),
            limits=httpx.Limits(
                max_keepalive_connections=self.settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
                max_connections=self.settings.HTTP_MAX_CONNECTIONS,
                keepalive_expiry=self.settings.HTTP_KEEPALIVE_EXPIRY
            )
        )
        
        # Initialize Redis client
        self.redis_client = redis.from_url(
            self.settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=self.settings.REDIS_MAX_CONNECTIONS,
            socket_connect_timeout=self.settings.REDIS_CONNECT_TIMEOUT,
            socket_timeout=self.settings.REDIS_SOCKET_TIMEOUT
        )
        
        self.logger.info("Gateway services initialized successfully")
    
    def _create_fastapi_app(self):
        """Create FastAPI application"""
        self.logger.info("Creating ultra-extreme gateway application")
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.logger.info("Starting ultra-extreme gateway")
            
            # Start service discovery
            await self.service_discovery.start()
            
            # Start health monitoring
            asyncio.create_task(self._health_monitoring_loop())
            
            yield
            
            # Shutdown
            self.logger.info("Shutting down ultra-extreme gateway")
            
            # Stop service discovery
            await self.service_discovery.stop()
            
            # Close HTTP client
            await self.http_client.aclose()
            
            # Close Redis client
            await self.redis_client.close()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Ultra-Extreme V5 Gateway",
            description="Ultra-extreme API Gateway with advanced features",
            version="5.0.0",
            debug=self.settings.DEBUG,
            lifespan=lifespan
        )
        
        # Add middleware
        self._add_middleware()
        
        # Add exception handlers
        self._add_exception_handlers()
        
        # Add routes
        self._add_routes()
        
        # Add Prometheus metrics
        if self.settings.PROMETHEUS_ENABLED:
            metrics_app = make_asgi_app()
            self.app.mount("/metrics", metrics_app)
        
        self.logger.info("Gateway application created successfully")
    
    def _add_middleware(self):
        """Add middleware to FastAPI app"""
        # CORS middleware
        if self.settings.CORS_ENABLED:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.settings.CORS_ORIGINS,
                allow_credentials=True,
                allow_methods=self.settings.CORS_METHODS,
                allow_headers=self.settings.CORS_HEADERS,
            )
        
        # Gzip middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Custom middleware
        self.app.add_middleware(MonitoringMiddleware)
        self.app.add_middleware(LoadBalancerMiddleware, service_discovery=self.service_discovery)
        self.app.add_middleware(CircuitBreakerMiddleware, redis_client=self.redis_client)
        
        if self.settings.RATE_LIMIT_ENABLED:
            self.app.add_middleware(RateLimitMiddleware, redis_client=self.redis_client)
        
        if self.settings.AUTH_ENABLED:
            self.app.add_middleware(AuthMiddleware)
    
    def _add_exception_handlers(self):
        """Add exception handlers to FastAPI app"""
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            """Handle validation exceptions"""
            self.logger.error("Validation error", errors=exc.errors())
            
            return JSONResponse(
                status_code=422,
                content={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Request validation failed",
                        "details": exc.errors()
                    }
                }
            )
        
        @self.app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            """Handle HTTP exceptions"""
            self.logger.error("HTTP exception", status_code=exc.status_code, detail=exc.detail)
            
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": f"HTTP_{exc.status_code}",
                        "message": exc.detail
                    }
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle general exceptions"""
            self.logger.error("Unexpected error", error=str(exc), exc_info=True)
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred"
                    }
                }
            )
    
    def _add_routes(self):
        """Add routes to FastAPI app"""
        # Include routers
        self.app.include_router(health_router, prefix="/health", tags=["health"])
        self.app.include_router(content_router, prefix="/api/v1/content", tags=["content"])
        self.app.include_router(optimization_router, prefix="/api/v1/optimization", tags=["optimization"])
        self.app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
        
        # Root endpoint
        @self.app.get("/", tags=["root"])
        async def root():
            """Root endpoint"""
            return {
                "name": "Ultra-Extreme V5 Gateway",
                "version": "5.0.0",
                "description": "Ultra-extreme API Gateway with advanced features",
                "status": "running",
                "services": await self.service_discovery.get_available_services()
            }
        
        # Service discovery endpoint
        @self.app.get("/services", tags=["services"])
        async def get_services():
            """Get available services"""
            return {
                "services": await self.service_discovery.get_available_services(),
                "health": await self.service_discovery.get_services_health()
            }
    
    async def _health_monitoring_loop(self):
        """Health monitoring loop"""
        while True:
            try:
                # Check services health
                health_status = await self.service_discovery.check_services_health()
                
                # Log health status
                if health_status["unhealthy_services"]:
                    self.logger.warning(
                        "Unhealthy services detected",
                        unhealthy_services=health_status["unhealthy_services"]
                    )
                else:
                    self.logger.info("All services healthy")
                
                # Wait before next check
                await asyncio.sleep(self.settings.HEALTH_CHECK_INTERVAL)
                
            except Exception as e:
                self.logger.error("Error in health monitoring", error=str(e))
                await asyncio.sleep(60)  # Wait longer on error
    
    async def start(self):
        """Start the gateway"""
        self.logger.info("Starting ultra-extreme gateway")
        
        # Start the server
        config = uvicorn.Config(
            app=self.app,
            host=self.settings.HOST,
            port=self.settings.PORT,
            workers=self.settings.WORKERS,
            log_level=self.settings.LOG_LEVEL.lower(),
            access_log=True,
            use_colors=True,
            loop="uvloop" if self.settings.USE_UVLOOP else "asyncio"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application"""
        return self.app


# Global gateway instance
gateway_instance = None


def get_gateway() -> UltraExtremeGateway:
    """Get the gateway instance"""
    global gateway_instance
    if gateway_instance is None:
        gateway_instance = UltraExtremeGateway()
    return gateway_instance


def get_app() -> FastAPI:
    """Get the FastAPI application"""
    return get_gateway().get_app()


# For direct execution
if __name__ == "__main__":
    # Create and start the gateway
    gateway = UltraExtremeGateway()
    
    try:
        asyncio.run(gateway.start())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error starting gateway: {e}")
        sys.exit(1) 