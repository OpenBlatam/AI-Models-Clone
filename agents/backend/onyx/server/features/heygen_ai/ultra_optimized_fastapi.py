#!/usr/bin/env python3
"""
Ultra-Optimized FastAPI Application for HeyGen AI
==================================================

This module provides a high-performance FastAPI application with:
- Advanced middleware and optimization
- Connection pooling and async operations
- Performance monitoring and metrics
- Modern Python features and best practices
- Comprehensive error handling and validation
"""

import asyncio
import os
import signal
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# FastAPI ecosystem with performance enhancements
from fastapi import FastAPI, Request, Response, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi

# High-performance ASGI server
import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server

# Performance monitoring and optimization
import structlog
from loguru import logger
import psutil
import asyncio_mqtt as aiomqtt
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.openmetrics.exposition import generate_latest as generate_latest_openmetrics

# Database and caching
from redis.asyncio import Redis
import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Data processing
import polars as pl
import vaex
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validator, ValidationError
from pydantic_settings import BaseSettings

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
# Configuration Classes
# =============================================================================

class FastAPIConfig(BaseSettings):
    """FastAPI configuration with environment variable support."""
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Performance settings
    max_connections: int = Field(default=1000, env="MAX_CONNECTIONS")
    max_requests: int = Field(default=10000, env="MAX_REQUESTS")
    timeout_keep_alive: int = Field(default=5, env="TIMEOUT_KEEP_ALIVE")
    timeout_graceful_shutdown: int = Field(default=30, env="TIMEOUT_GRACEFUL_SHUTDOWN")
    
    # Database settings
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    mongo_url: Optional[str] = Field(default=None, env="MONGO_URL")
    
    # Security settings
    allowed_hosts: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # Monitoring settings
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_health_check: bool = Field(default=True, env="ENABLE_HEALTH_CHECK")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# =============================================================================
# Performance Monitoring
# =============================================================================

class PerformanceMetrics:
    """High-performance metrics collection."""
    
    def __init__(self):
        # Request metrics
        self.request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
        self.request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
        self.active_requests = Gauge('http_active_requests', 'Number of active HTTP requests')
        
        # System metrics
        self.cpu_usage = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('system_memory_usage_bytes', 'Memory usage in bytes')
        self.disk_usage = Gauge('system_disk_usage_bytes', 'Disk usage in bytes')
        
        # Database metrics
        self.db_connection_count = Gauge('database_connections', 'Number of database connections')
        self.db_query_duration = Histogram('database_query_duration_seconds', 'Database query duration')
        
        # Cache metrics
        self.cache_hits = Counter('cache_hits_total', 'Total cache hits')
        self.cache_misses = Counter('cache_misses_total', 'Total cache misses')
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record request metrics."""
        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_db_query(self, duration: float):
        """Record database query metrics."""
        self.db_query_duration.observe(duration)
    
    def record_cache_hit(self):
        """Record cache hit."""
        self.cache_hits.inc()
    
    def record_cache_miss(self):
        """Record cache miss."""
        self.cache_misses.inc()
    
    def update_system_metrics(self):
        """Update system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_usage.set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.disk_usage.set(disk.used)
        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")

# =============================================================================
# Database Manager
# =============================================================================

class DatabaseManager:
    """High-performance database manager."""
    
    def __init__(self, config: FastAPIConfig):
        self.config = config
        self.postgres_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.redis_client: Optional[Redis] = None
        self.sqlalchemy_engine: Optional[Any] = None
        self.sqlalchemy_session: Optional[Any] = None
    
    async def initialize(self):
        """Initialize all database connections."""
        if self.config.redis_url:
            await self._initialize_redis()
        
        if self.config.database_url:
            await self._initialize_postgres()
        
        if self.config.mongo_url:
            await self._initialize_mongo()
    
    async def _initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = Redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection initialized successfully")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            self.redis_client = None
    
    async def _initialize_postgres(self):
        """Initialize PostgreSQL connection pool."""
        try:
            self.postgres_pool = await asyncpg.create_pool(
                self.config.database_url,
                min_size=5,
                max_size=20,
                command_timeout=30
            )
            logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"PostgreSQL initialization failed: {e}")
            self.postgres_pool = None
    
    async def _initialize_mongo(self):
        """Initialize MongoDB connection."""
        try:
            self.mongo_client = AsyncIOMotorClient(self.config.mongo_url)
            await self.mongo_client.admin.command('ping')
            logger.info("MongoDB connection initialized")
        except Exception as e:
            logger.error(f"MongoDB initialization failed: {e}")
            self.mongo_client = None
    
    async def close(self):
        """Close all database connections."""
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        if self.redis_client:
            await self.redis_client.close()

# =============================================================================
# Middleware Classes
# =============================================================================

class PerformanceMiddleware:
    """High-performance middleware for request/response optimization."""
    
    def __init__(self, metrics: PerformanceMetrics):
        self.metrics = metrics
    
    async def __call__(self, request: Request, call_next):
        """Process request with performance monitoring."""
        start_time = time.time()
        
        # Increment active requests
        self.metrics.active_requests.inc()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            self.metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
                duration=duration
            )
            
            return response
        
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            self.metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status=500,
                duration=duration
            )
            raise
        finally:
            # Decrement active requests
            self.metrics.active_requests.dec()

class CacheMiddleware:
    """High-performance caching middleware."""
    
    def __init__(self, redis_client: Optional[Redis]):
        self.redis_client = redis_client
    
    async def __call__(self, request: Request, call_next):
        """Process request with caching."""
        if not self.redis_client or request.method != "GET":
            return await call_next(request)
        
        # Generate cache key
        cache_key = f"cache:{request.url.path}:{hash(str(request.query_params))}"
        
        try:
            # Try to get from cache
            cached_response = await self.redis_client.get(cache_key)
            if cached_response:
                return JSONResponse(
                    content=cached_response,
                    status_code=200,
                    headers={"X-Cache": "HIT"}
                )
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        # Process request
        response = await call_next(request)
        
        # Cache successful GET responses
        if response.status_code == 200 and request.method == "GET":
            try:
                await self.redis_client.setex(
                    cache_key,
                    300,  # 5 minutes TTL
                    response.body.decode()
                )
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")
        
        return response

# =============================================================================
# Pydantic Models
# =============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = Field(default="healthy")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uptime: float = Field(description="Application uptime in seconds")
    version: str = Field(default="2.0.0")
    environment: str = Field(default="production")

class PerformanceResponse(BaseModel):
    """Performance metrics response model."""
    cpu_usage: float = Field(description="CPU usage percentage")
    memory_usage: float = Field(description="Memory usage in bytes")
    disk_usage: float = Field(description="Disk usage in bytes")
    active_connections: int = Field(description="Active database connections")
    cache_hit_rate: float = Field(description="Cache hit rate")

class DataProcessingRequest(BaseModel):
    """Data processing request model."""
    data: List[Dict[str, Any]] = Field(description="Data to process")
    operations: List[str] = Field(default=[], description="Operations to perform")
    cache_result: bool = Field(default=True, description="Whether to cache the result")

class DataProcessingResponse(BaseModel):
    """Data processing response model."""
    processed_count: int = Field(description="Number of processed records")
    processing_time: float = Field(description="Processing time in seconds")
    result_summary: Dict[str, Any] = Field(description="Processing result summary")

# =============================================================================
# FastAPI Application
# =============================================================================

class UltraOptimizedFastAPI:
    """Ultra-optimized FastAPI application."""
    
    def __init__(self, config: FastAPIConfig):
        self.config = config
        self.app = None
        self.metrics = PerformanceMetrics()
        self.db_manager = DatabaseManager(config)
        self.start_time = time.time()
    
    def create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Application lifespan manager."""
            # Startup
            logger.info("Starting HeyGen AI FastAPI application...")
            await self.db_manager.initialize()
            
            # Start background tasks
            asyncio.create_task(self._update_metrics_periodically())
            
            yield
            
            # Shutdown
            logger.info("Shutting down HeyGen AI FastAPI application...")
            await self.db_manager.close()
        
        # Create FastAPI app
        self.app = FastAPI(
            title="HeyGen AI API",
            description="Ultra-optimized AI processing API",
            version="2.0.0",
            docs_url="/docs" if self.config.reload else None,
            redoc_url="/redoc" if self.config.reload else None,
            lifespan=lifespan
        )
        
        # Add middleware
        self._add_middleware()
        
        # Add routes
        self._add_routes()
        
        # Add exception handlers
        self._add_exception_handlers()
        
        return self.app
    
    def _add_middleware(self):
        """Add performance and security middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=self.config.allowed_hosts
        )
        
        # Gzip compression middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Performance middleware
        self.app.add_middleware(PerformanceMiddleware, self.metrics)
        
        # Cache middleware
        if self.config.redis_url:
            self.app.add_middleware(CacheMiddleware, self.db_manager.redis_client)
    
    def _add_routes(self):
        """Add API routes."""
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint."""
            return {"message": "HeyGen AI API v2.0.0", "status": "running"}
        
        @self.app.get("/health", response_model=HealthCheckResponse)
        async def health_check():
            """Health check endpoint."""
            uptime = time.time() - self.start_time
            return HealthCheckResponse(
                uptime=uptime,
                environment=os.getenv("ENVIRONMENT", "production")
            )
        
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint."""
            if not self.config.enable_metrics:
                raise HTTPException(status_code=404, detail="Metrics disabled")
            
            return Response(
                content=generate_latest(),
                media_type=CONTENT_TYPE_LATEST
            )
        
        @self.app.post("/process", response_model=DataProcessingResponse)
        async def process_data(request: DataProcessingRequest):
            """Process data with high performance."""
            start_time = time.time()
            
            try:
                # Process data using Polars for maximum performance
                df = pl.DataFrame(request.data)
                
                # Apply operations
                for operation in request.operations:
                    if operation == "sort":
                        df = df.sort("id")
                    elif operation == "filter":
                        df = df.filter(pl.col("id") > 0)
                    elif operation == "aggregate":
                        df = df.groupby("category").agg([
                            pl.count().alias("count"),
                            pl.mean("value").alias("avg_value")
                        ])
                
                processing_time = time.time() - start_time
                
                return DataProcessingResponse(
                    processed_count=len(df),
                    processing_time=processing_time,
                    result_summary={
                        "columns": df.columns,
                        "shape": df.shape,
                        "operations_applied": request.operations
                    }
                )
            
            except Exception as e:
                logger.error(f"Data processing failed: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Data processing failed: {str(e)}"
                )
        
        @self.app.get("/performance", response_model=PerformanceResponse)
        async def get_performance():
            """Get current performance metrics."""
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Calculate cache hit rate
                total_requests = (self.metrics.request_count._value.sum() 
                                if hasattr(self.metrics.request_count, '_value') else 0)
                cache_hits = (self.metrics.cache_hits._value.sum() 
                             if hasattr(self.metrics.cache_hits, '_value') else 0)
                cache_hit_rate = cache_hits / total_requests if total_requests > 0 else 0
                
                return PerformanceResponse(
                    cpu_usage=cpu_percent,
                    memory_usage=memory.used,
                    disk_usage=disk.used,
                    active_connections=0,  # TODO: Implement connection tracking
                    cache_hit_rate=cache_hit_rate
                )
            
            except Exception as e:
                logger.error(f"Failed to get performance metrics: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get performance metrics"
                )
    
    def _add_exception_handlers(self):
        """Add global exception handlers."""
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            """Handle validation errors."""
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder({
                    "detail": "Validation error",
                    "errors": exc.errors()
                })
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle general exceptions."""
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder({
                    "detail": "Internal server error",
                    "message": str(exc)
                })
            )
    
    async def _update_metrics_periodically(self):
        """Update system metrics periodically."""
        while True:
            try:
                self.metrics.update_system_metrics()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Failed to update metrics: {e}")
                await asyncio.sleep(60)
    
    def run(self):
        """Run the FastAPI application."""
        app = self.create_app()
        
        config = Config(
            app=app,
            host=self.config.host,
            port=self.config.port,
            workers=self.config.workers,
            reload=self.config.reload,
            timeout_keep_alive=self.config.timeout_keep_alive,
            timeout_graceful_shutdown=self.config.timeout_graceful_shutdown,
            access_log=True,
            log_level="info"
        )
        
        server = Server(config=config)
        server.run()

# =============================================================================
# Main execution
# =============================================================================

def main():
    """Main execution function."""
    # Load configuration
    config = FastAPIConfig()
    
    # Create and run application
    app = UltraOptimizedFastAPI(config)
    app.run()

if __name__ == "__main__":
    main()
