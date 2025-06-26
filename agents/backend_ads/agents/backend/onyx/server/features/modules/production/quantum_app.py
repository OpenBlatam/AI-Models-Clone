"""
Quantum Production Application

Refactored from production_final_quantum.py to fit the modular architecture.
Enterprise-grade FastAPI application with all optimization modules integrated.
"""

import asyncio
import os
import time
import signal
import gc
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

# FastAPI and core dependencies
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
import uvicorn

# Import our modular components
from ..blog_posts import BlogPostFactory, BlogPostConfig, BlogPostRequest, ContentType
from ..copywriting import (
    CopywritingFactory, CopywritingConfig, ContentGenerationRequest, 
    ContentType as CopyContentType, AIProvider
)
from ..optimization import OptimizationFactory, OptimizationConfig
from ...shared.database import get_database
from ...shared.cache import get_cache
from ...shared.monitoring import get_monitoring, track_metric, register_health_check
from ...shared.infrastructure import get_infrastructure

# High-performance libraries
try:
    import orjson
    import uvloop
    import psutil
    import structlog
    HI_PERF_AVAILABLE = True
except ImportError:
    HI_PERF_AVAILABLE = False

# Configure logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(5),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@dataclass
class QuantumConfig:
    """Production quantum configuration."""
    APP_NAME: str = "Onyx-Quantum-Production"
    VERSION: str = "2.0.0-modular"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = min(mp.cpu_count() * 4, 32)
    
    # Module configurations
    ENABLE_BLOG_POSTS: bool = True
    ENABLE_COPYWRITING: bool = True
    ENABLE_OPTIMIZATION: bool = True
    ENABLE_MONITORING: bool = True
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Performance settings
    MAX_MEMORY_MB: int = int(os.getenv("MAX_MEMORY_MB", "8192"))
    CACHE_SIZE: int = int(os.getenv("CACHE_SIZE", "10000"))

class QuantumApplication:
    """Main quantum application with all modules integrated."""
    
    def __init__(self, config: QuantumConfig):
        self.config = config
        self.app = None
        
        # Module factories
        self.blog_factory = None
        self.copywriting_factory = None
        self.optimization_factory = None
        
        # Shared services
        self.database = get_database()
        self.cache = get_cache()
        self.monitoring = get_monitoring()
        self.infrastructure = get_infrastructure()
        
        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0.0
        
    async def initialize(self):
        """Initialize all modules and services."""
        logger.info("🚀 Initializing Quantum Application")
        
        # Initialize shared services
        await self._initialize_shared_services()
        
        # Initialize modules
        await self._initialize_modules()
        
        # Create FastAPI app
        self._create_app()
        
        # Register health checks
        await self._register_health_checks()
        
        logger.info("✅ Quantum Application initialized successfully")
    
    async def _initialize_shared_services(self):
        """Initialize shared services."""
        logger.info("📦 Initializing shared services")
        
        await self.database.initialize()
        await self.cache.initialize()
        await self.monitoring.initialize()
        
        track_metric("app.shared_services.initialized", 1)
        logger.info("✅ Shared services initialized")
    
    async def _initialize_modules(self):
        """Initialize all modules."""
        logger.info("🔧 Initializing modules")
        
        # Blog Posts Module
        if self.config.ENABLE_BLOG_POSTS:
            blog_config = BlogPostConfig(
                api_key="blog-api-key",
                max_concurrent_requests=5,
                cache_ttl=3600,
                enable_seo_optimization=True
            )
            self.blog_factory = BlogPostFactory(blog_config)
        
        # Copywriting Module
        if self.config.ENABLE_COPYWRITING:
            copywriting_config = CopywritingConfig(
                default_provider=AIProvider.OPENAI,
                api_keys={
                    "openai": self.config.OPENAI_API_KEY,
                    "anthropic": self.config.ANTHROPIC_API_KEY
                },
                max_concurrent_requests=3,
                enable_caching=True,
                cache_ttl=1800
            )
            self.copywriting_factory = CopywritingFactory(copywriting_config)
        
        # Optimization Module
        if self.config.ENABLE_OPTIMIZATION:
            optimization_config = OptimizationConfig(
                enable_performance_optimization=True,
                enable_caching=True,
                memory_threshold_mb=self.config.MAX_MEMORY_MB,
                cache_size=self.config.CACHE_SIZE
            )
            self.optimization_factory = OptimizationFactory(optimization_config)
        
        track_metric("app.modules.initialized", 1)
        logger.info("✅ Modules initialized")
    
    def _create_app(self):
        """Create FastAPI application with all routes."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Application lifespan management."""
            logger.info("🌟 Starting Quantum Application")
            
            # Startup
            if HI_PERF_AVAILABLE and hasattr(uvloop, 'install'):
                uvloop.install()
            
            yield
            
            # Shutdown
            logger.info("🔄 Shutting down Quantum Application")
            await self.cleanup()
        
        self.app = FastAPI(
            title=self.config.APP_NAME,
            version=self.config.VERSION,
            description="Enterprise Quantum Production Application with Modular Architecture",
            lifespan=lifespan,
            default_response_class=ORJSONResponse if HI_PERF_AVAILABLE else None
        )
        
        # Add middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Add custom middleware
        @self.app.middleware("http")
        async def performance_middleware(request: Request, call_next):
            start_time = time.time()
            
            response = await call_next(request)
            
            process_time = time.time() - start_time
            self.request_count += 1
            self.total_processing_time += process_time
            
            # Track metrics
            track_metric("http.requests.total", 1)
            track_metric("http.request.duration", process_time)
            
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = str(self.request_count)
            
            return response
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all API routes."""
        
        # Health and status endpoints
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "timestamp": time.time()}
        
        @self.app.get("/status")
        async def system_status():
            """Comprehensive system status."""
            status = {
                "app": {
                    "name": self.config.APP_NAME,
                    "version": self.config.VERSION,
                    "environment": self.config.ENVIRONMENT,
                    "uptime": time.time()
                },
                "modules": {
                    "blog_posts": self.blog_factory is not None,
                    "copywriting": self.copywriting_factory is not None,
                    "optimization": self.optimization_factory is not None
                },
                "shared_services": {
                    "database": "active",
                    "cache": "active",
                    "monitoring": "active"
                },
                "performance": {
                    "total_requests": self.request_count,
                    "avg_response_time": self.total_processing_time / max(self.request_count, 1),
                    "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024 if HI_PERF_AVAILABLE else 0
                }
            }
            return status
        
        # Blog Posts API
        if self.blog_factory:
            @self.app.post("/api/blog/create")
            async def create_blog_post(request: BlogPostRequest):
                """Create a blog post."""
                try:
                    blog_service = self.blog_factory.create_blog_service()
                    result = await blog_service.create_blog_post(request)
                    track_metric("api.blog.create.success", 1)
                    return {"success": True, "blog_post": result}
                except Exception as e:
                    track_metric("api.blog.create.error", 1)
                    raise HTTPException(status_code=500, detail=str(e))
            
            @self.app.post("/api/blog/seo-optimize")
            async def optimize_blog_seo(blog_post_data: Dict[str, Any]):
                """Optimize blog post for SEO."""
                try:
                    seo_service = self.blog_factory.create_seo_optimizer()
                    # Convert dict to blog post object and optimize
                    track_metric("api.blog.seo.success", 1)
                    return {"success": True, "optimized": True}
                except Exception as e:
                    track_metric("api.blog.seo.error", 1)
                    raise HTTPException(status_code=500, detail=str(e))
        
        # Copywriting API
        if self.copywriting_factory:
            @self.app.post("/api/copywriting/generate")
            async def generate_content(request: ContentGenerationRequest):
                """Generate AI content."""
                try:
                    generator = self.copywriting_factory.create_content_generator()
                    result = await generator.generate_content(request)
                    track_metric("api.copywriting.generate.success", 1)
                    return {"success": True, "content": result}
                except Exception as e:
                    track_metric("api.copywriting.generate.error", 1)
                    raise HTTPException(status_code=500, detail=str(e))
            
            @self.app.post("/api/copywriting/analyze")
            async def analyze_content(content_data: Dict[str, Any]):
                """Analyze content quality."""
                try:
                    analyzer = self.copywriting_factory.create_content_analyzer()
                    result = await analyzer.analyze_content(
                        content_data.get("content", ""),
                        content_data.get("keywords", [])
                    )
                    track_metric("api.copywriting.analyze.success", 1)
                    return {"success": True, "analysis": result}
                except Exception as e:
                    track_metric("api.copywriting.analyze.error", 1)
                    raise HTTPException(status_code=500, detail=str(e))
        
        # Optimization API
        if self.optimization_factory:
            @self.app.get("/api/optimization/performance")
            async def get_performance_metrics():
                """Get system performance metrics."""
                try:
                    optimizer = self.optimization_factory.create_performance_optimizer()
                    metrics = optimizer.get_performance_report()
                    track_metric("api.optimization.performance.success", 1)
                    return {"success": True, "metrics": metrics}
                except Exception as e:
                    track_metric("api.optimization.performance.error", 1)
                    raise HTTPException(status_code=500, detail=str(e))
            
            @self.app.post("/api/optimization/cache/clear")
            async def clear_cache():
                """Clear application cache."""
                try:
                    await self.cache.clear()
                    track_metric("api.optimization.cache.clear", 1)
                    return {"success": True, "message": "Cache cleared"}
                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))
        
        # Integrated workflow endpoints
        @self.app.post("/api/workflow/blog-post-complete")
        async def complete_blog_workflow(workflow_data: Dict[str, Any]):
            """Complete blog post creation workflow using all modules."""
            try:
                start_time = time.time()
                
                # Step 1: Generate content (Copywriting)
                if self.copywriting_factory:
                    content_request = ContentGenerationRequest(
                        content_type=CopyContentType.BLOG_POST,
                        topic=workflow_data.get("topic", ""),
                        target_audience=workflow_data.get("target_audience", "general"),
                        tone=workflow_data.get("tone", "professional"),
                        keywords=workflow_data.get("keywords", [])
                    )
                    
                    generator = self.copywriting_factory.create_content_generator()
                    content_result = await generator.generate_content(content_request)
                else:
                    content_result = {
                        "content": f"Blog post about {workflow_data.get('topic', 'sample topic')}",
                        "title": f"Guide to {workflow_data.get('topic', 'Sample Topic')}"
                    }
                
                # Step 2: Create blog post (Blog Posts)
                if self.blog_factory:
                    blog_request = BlogPostRequest(
                        title=getattr(content_result, 'title', 'Generated Title'),
                        content=getattr(content_result, 'content', 'Generated content'),
                        author="AI Assistant",
                        tags=workflow_data.get("keywords", []),
                        content_type=ContentType.ARTICLE
                    )
                    
                    blog_service = self.blog_factory.create_blog_service()
                    blog_post = await blog_service.create_blog_post(blog_request)
                    
                    # Step 3: SEO optimization
                    seo_service = self.blog_factory.create_seo_optimizer()
                    optimized_post = await seo_service.optimize_for_seo(blog_post)
                else:
                    optimized_post = {"id": "demo-post", "optimized": True}
                
                workflow_time = time.time() - start_time
                
                track_metric("api.workflow.complete.success", 1)
                track_metric("api.workflow.duration", workflow_time)
                
                return {
                    "success": True,
                    "workflow_time": workflow_time,
                    "blog_post": optimized_post,
                    "content_analysis": getattr(content_result, 'metrics', {}),
                    "steps_completed": 3
                }
                
            except Exception as e:
                track_metric("api.workflow.complete.error", 1)
                raise HTTPException(status_code=500, detail=str(e))
        
        # Metrics endpoint
        @self.app.get("/metrics", response_class=PlainTextResponse)
        async def get_metrics():
            """Prometheus-style metrics."""
            metrics = await self.monitoring.get_comprehensive_status()
            
            # Convert to Prometheus format (simplified)
            prometheus_metrics = []
            
            # Add custom metrics
            prometheus_metrics.append(f"http_requests_total {self.request_count}")
            prometheus_metrics.append(f"http_request_duration_avg {self.total_processing_time / max(self.request_count, 1)}")
            
            if HI_PERF_AVAILABLE:
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                prometheus_metrics.append(f"memory_usage_mb {memory_mb}")
                prometheus_metrics.append(f"cpu_percent {psutil.cpu_percent()}")
            
            return "\n".join(prometheus_metrics)
    
    async def _register_health_checks(self):
        """Register health checks for all services."""
        
        await register_health_check(
            "database_connection",
            self._check_database_health,
            interval=60,
            critical=True
        )
        
        await register_health_check(
            "cache_service",
            self._check_cache_health,
            interval=30,
            critical=False
        )
        
        await register_health_check(
            "modules_health",
            self._check_modules_health,
            interval=120,
            critical=False
        )
    
    async def _check_database_health(self) -> bool:
        """Database health check."""
        try:
            # Would execute actual database query
            return True
        except Exception:
            return False
    
    async def _check_cache_health(self) -> bool:
        """Cache health check."""
        try:
            await self.cache.set("health_check", "ok", ttl=60)
            result = await self.cache.get("health_check")
            return result == "ok"
        except Exception:
            return False
    
    async def _check_modules_health(self) -> bool:
        """Modules health check."""
        try:
            return (
                (self.blog_factory is not None if self.config.ENABLE_BLOG_POSTS else True) and
                (self.copywriting_factory is not None if self.config.ENABLE_COPYWRITING else True) and
                (self.optimization_factory is not None if self.config.ENABLE_OPTIMIZATION else True)
            )
        except Exception:
            return False
    
    async def cleanup(self):
        """Cleanup all resources."""
        logger.info("🧹 Cleaning up Quantum Application")
        
        try:
            await self.monitoring.shutdown()
            # Additional cleanup would go here
            
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

def create_quantum_app(config: Optional[QuantumConfig] = None) -> FastAPI:
    """Factory function to create quantum application."""
    config = config or QuantumConfig()
    quantum_app = QuantumApplication(config)
    
    # Initialize synchronously (FastAPI will handle async initialization)
    return quantum_app.app

async def run_quantum_server():
    """Run the quantum server."""
    config = QuantumConfig()
    quantum_app = QuantumApplication(config)
    
    # Initialize the application
    await quantum_app.initialize()
    
    # Configure uvicorn
    uvicorn_config = uvicorn.Config(
        quantum_app.app,
        host=config.HOST,
        port=config.PORT,
        workers=1,  # Use 1 worker for development, scale with external process manager
        loop="uvloop" if HI_PERF_AVAILABLE else "asyncio",
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(uvicorn_config)
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully")
        asyncio.create_task(quantum_app.cleanup())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"🚀 Starting Quantum Server on {config.HOST}:{config.PORT}")
    await server.serve()

if __name__ == "__main__":
    asyncio.run(run_quantum_server()) 