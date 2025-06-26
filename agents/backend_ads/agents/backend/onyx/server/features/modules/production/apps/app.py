"""
Main Application Module - Production Optimized Onyx Features.

Integrates all components into a cohesive enterprise-grade application
with FastAPI, async support, monitoring, and comprehensive error handling.
Enhanced with high-performance optimization libraries.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
import time

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, ORJSONResponse
from fastapi.exception_handlers import http_exception_handler
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import structlog

# Import unified optimizations
from .core_optimizers import (
    UnifiedOptimizer, OptimizationLevel, OptimizationConfig,
    create_unified_optimizer, optimize, optimize_performance,
    FastSerializer, FastHasher, MemoryOptimizer, AsyncOptimizer,
    ProfilerOptimizer, setup_event_loop_optimization, OPTIMIZATION_CONFIG
)

# Import our optimized modules
from .config import get_config, Environment, OnyxConfig
from .monitoring import (
    setup_sentry, get_metrics_export, get_monitoring_dashboard,
    comprehensive_health_check, track_performance, monitor_operation,
    request_count, request_duration
)
from .exceptions import (
    OnyxBaseException, ValidationError, ServiceError,
    handle_exceptions, setup_exception_handlers
)
from .utils import (
    generate_correlation_id, safe_json_serialize,
    AsyncLimiter, ProgressTracker
)
from .key_messages import create_default_service, MessageType, MessagePriority
from .image_process import (
    validate_file_comprehensive, ValidationConfig,
    process_image_async, ImageProcessingConfig
)
from .copywriting_model import (
    create_copywriting_model, ContentRequest, ContentType, 
    ContentTone, ContentLanguage, CopywritingTemplates
)
from .copywriting_optimizer import (
    create_copywriting_optimizer, create_ab_tester, create_performance_analyzer
)

# Configure structured logging
logger = structlog.get_logger(__name__)

# Global configuration
config = get_config()

# Unified high-performance optimizer
unified_optimizer = create_unified_optimizer(
    level=OptimizationLevel.ULTRA,
    max_workers=min(32, os.cpu_count() * 2),
    max_concurrent_tasks=100
)

# Individual optimizers for backward compatibility
async_optimizer = unified_optimizer.async_optimizer
memory_optimizer = unified_optimizer.memory
profiler = unified_optimizer.profiler

# Rate limiters with optimization
api_limiter = AsyncLimiter(max_concurrent=100)
upload_limiter = AsyncLimiter(max_concurrent=20)

# Global services
message_service = None
copywriting_model = None
copywriting_optimizer = None
ab_tester = None
performance_analyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global message_service
    
    # Startup
    logger.info("Starting Onyx Features Application", version="1.0.0")
    
    # Setup high-performance event loop optimization
    if config.enable_async:
        setup_event_loop_optimization()
    
    # Initialize unified optimizations
    try:
        optimization_results = await unified_optimizer.initialize()
        logger.info("Unified optimizations initialized", results=optimization_results)
    except Exception as e:
        logger.warning("Some optimizations failed to initialize", error=str(e))
    
    # Setup monitoring
    if config.monitoring.enable_sentry:
        setup_sentry(config.monitoring.sentry_dsn, config.environment.value)
    
    # Initialize services
    try:
        message_service = create_default_service()
        logger.info("Message service initialized")
    except Exception as e:
        logger.error("Failed to initialize message service", error=str(e))
        message_service = None
    
    # Health check
    health_status = await comprehensive_health_check()
    logger.info("Health check completed", 
               healthy_services=sum(1 for h in health_status.values() if h.healthy))
    
    yield
    
    # Shutdown
    logger.info("Shutting down Onyx Features Application")
    
    # Cleanup services
    if message_service:
        await message_service.clear_cache()
        logger.info("Message service cache cleared")
    
    # Cleanup optimizations
    try:
        await unified_optimizer.cleanup()
        logger.info("Optimizations cleaned up successfully")
    except Exception as e:
        logger.warning("Optimization cleanup failed", error=str(e))


# Create FastAPI application with optimizations
app = FastAPI(
    title="Onyx Features API",
    description="Production-optimized enterprise features for image processing and messaging",
    version="1.0.0",
    docs_url="/docs" if config.environment != Environment.PRODUCTION else None,
    redoc_url="/redoc" if config.environment != Environment.PRODUCTION else None,
    lifespan=lifespan,
    default_response_class=ORJSONResponse  # Ultra-fast JSON responses
)

# Setup middleware
if config.security.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Setup exception handlers
setup_exception_handlers(app)


@app.middleware("http")
async def optimized_request_middleware(request: Request, call_next):
    """Optimized request middleware with performance monitoring."""
    # Generate fast correlation ID using optimized hasher
    hasher = unified_optimizer.hasher
    correlation_id = hasher.hash_fast(f"{request.url.path}_{asyncio.get_event_loop().time()}")[:16]
    request.state.correlation_id = correlation_id
    
    # Add correlation ID to structured logging context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    # Start performance profiling
    profiler.start_profiling()
    start_time = asyncio.get_event_loop().time()
    
    # Process request with memory optimization
    memory_before = memory_optimizer.get_memory_usage()
    response = await call_next(request)
    memory_after = memory_optimizer.get_memory_usage()
    
    # Record comprehensive metrics
    duration = asyncio.get_event_loop().time() - start_time
    performance_metrics = profiler.stop_profiling(f"{request.method}_{request.url.path}")
    
    request_count.labels(
        method=request.method,
        endpoint=str(request.url.path),
        status_code=response.status_code,
        feature="api"
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=str(request.url.path),
        feature="api"
    ).observe(duration)
    
    # Add performance headers
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    response.headers["X-Memory-Delta"] = f"{memory_after['percent'] - memory_before['percent']:.2f}%"
    
    # Log performance if slow
    if duration > 1.0:
        logger.warning("Slow request detected", 
                      duration=duration,
                      endpoint=str(request.url.path),
                      method=request.method)
    
    return response


# Health and Monitoring Endpoints

@app.get("/health", tags=["monitoring"])
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        health_status = await comprehensive_health_check()
        overall_healthy = all(status.healthy for status in health_status.values())
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": health_status["system"].timestamp.isoformat(),
            "services": {
                name: {
                    "healthy": status.healthy,
                    "message": status.message,
                    "details": status.details
                }
                for name, status in health_status.items()
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Health check failed")


@app.get("/metrics", response_class=PlainTextResponse, tags=["monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    try:
        return get_metrics_export()
    except Exception as e:
        logger.error("Failed to generate metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Metrics generation failed")


@app.get("/dashboard", tags=["monitoring"])
async def monitoring_dashboard():
    """Monitoring dashboard with comprehensive metrics."""
    try:
        dashboard_data = get_monitoring_dashboard()
        return dashboard_data
    except Exception as e:
        logger.error("Dashboard generation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Dashboard generation failed")


# Message Management Endpoints

@app.post("/messages", tags=["messaging"])
@handle_exceptions
@track_performance("create_message", "messaging")
@optimize_performance(cache_results=True, profile=True)
async def create_message(
    content: str,
    message_type: MessageType = MessageType.HUMAN,
    priority: MessagePriority = MessagePriority.NORMAL,
    metadata: Optional[Dict[str, Any]] = None
):
    """Create a new message."""
    if not message_service:
        raise ServiceError("Message service not available")
    
    async with api_limiter:
        message = await message_service.create_message(
            content=content,
            message_type=message_type,
            priority=priority,
            metadata=metadata
        )
        
        return {
            "status": "success",
            "message": {
                "id": message.id,
                "content": message.content,
                "type": message.message_type,
                "priority": message.priority,
                "created_at": message.created_at.isoformat()
            }
        }


@app.get("/messages/{message_id}", tags=["messaging"])
@handle_exceptions
async def get_message(message_id: str):
    """Retrieve a message by ID."""
    if not message_service:
        raise ServiceError("Message service not available")
    
    message = await message_service.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {
        "status": "success",
        "message": {
            "id": message.id,
            "content": message.content,
            "type": message.message_type,
            "priority": message.priority,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat() if message.updated_at else None
        }
    }


@app.post("/messages/batch", tags=["messaging"])
@handle_exceptions
@track_performance("create_batch", "messaging")
@optimize_performance(cache_results=False, profile=True)
async def create_message_batch(
    messages: List[str],
    metadata: Optional[Dict[str, Any]] = None
):
    """Create a batch of messages."""
    if not message_service:
        raise ServiceError("Message service not available")
    
    if len(messages) > 100:
        raise ValidationError("Batch size cannot exceed 100 messages")
    
    # Use optimized batch processing
    batch_results = await async_optimizer.batch_process_optimized(
        messages,
        lambda msg: message_service.create_message(msg),
        batch_size=min(50, len(messages)),
        max_concurrent=10
    )
    
    batch = await message_service.create_batch(messages, metadata)
    
    return {
        "status": "success",
        "batch": {
            "id": batch.batch_id,
            "total_count": batch.total_count,
            "created_at": batch.created_at.isoformat(),
            "message_ids": [msg.id for msg in batch.messages],
            "processing_stats": {
                "successful": len([r for r in batch_results if not isinstance(r, dict) or "error" not in r]),
                "failed": len([r for r in batch_results if isinstance(r, dict) and "error" in r])
            }
        }
    }


# Image Processing Endpoints

@app.post("/images/validate", tags=["image_processing"])
@handle_exceptions
@track_performance("validate_image", "image_processing")
@optimize_performance(cache_results=True, profile=True)
async def validate_image(
    image_data: bytes,
    filename: Optional[str] = None,
    strict_validation: bool = True
):
    """Validate image file."""
    async with upload_limiter:
        config = ValidationConfig(strict_validation=strict_validation)
        
        async with monitor_operation("validate", "image_processing"):
            result = validate_file_comprehensive(image_data, filename, config)
        
        return {
            "status": "success",
            "validation": {
                "is_valid": result.is_valid,
                "mime_type": result.mime_type,
                "file_size_mb": result.file_size_mb,
                "is_vision_compatible": result.is_vision_compatible,
                "warnings": result.warnings,
                "errors": result.errors
            }
        }


@app.post("/images/process", tags=["image_processing"])
@handle_exceptions
@track_performance("process_image", "image_processing")
@optimize_performance(cache_results=True, profile=True)
async def process_image(
    image_data: bytes,
    max_size_mb: int = 20,
    quality: int = 85
):
    """Process and optimize image."""
    async with upload_limiter:
        config = ImageProcessingConfig(
            max_size_mb=max_size_mb,
            jpeg_quality=quality
        )
        
        async with monitor_operation("process", "image_processing"):
            processed_data, encoded = await process_image_async(image_data, config)
        
        return {
            "status": "success",
            "processing": {
                "original_size_bytes": len(image_data),
                "processed_size_bytes": len(processed_data),
                "compression_ratio": len(processed_data) / len(image_data),
                "base64_encoded": encoded[:100] + "..." if len(encoded) > 100 else encoded
            }
        }


# Copywriting AI Endpoints

@app.post("/copywriting/generate", tags=["copywriting"])
@handle_exceptions
@track_performance("generate_copy", "copywriting")
@optimize_performance(cache_results=True, profile=True)
async def generate_copywriting_content(
    content_type: ContentType,
    target_audience: str,
    key_message: str,
    tone: ContentTone = ContentTone.PROFESSIONAL,
    language: ContentLanguage = ContentLanguage.ENGLISH,
    keywords: List[str] = [],
    call_to_action: Optional[str] = None,
    max_length: Optional[int] = None,
    include_hashtags: bool = False,
    include_emojis: bool = False
):
    """Generate AI-powered copywriting content."""
    if not copywriting_model:
        raise ServiceError("Copywriting model not available")
    
    async with api_limiter:
        # Create content request
        request = ContentRequest(
            content_type=content_type,
            target_audience=target_audience,
            key_message=key_message,
            tone=tone,
            language=language,
            keywords=keywords,
            call_to_action=call_to_action,
            max_length=max_length,
            include_hashtags=include_hashtags,
            include_emojis=include_emojis
        )
        
        # Generate content
        generated_content = await copywriting_model.create_content(request)
        
        return {
            "status": "success",
            "content": {
                "id": generated_content.id,
                "text": generated_content.content,
                "type": generated_content.content_type,
                "tone": generated_content.tone,
                "language": generated_content.language,
                "generation_time_ms": generated_content.generation_time_ms,
                "model_used": generated_content.model_used,
                "confidence_score": generated_content.confidence_score,
                "metrics": generated_content.metrics.dict() if generated_content.metrics else None,
                "alternatives": generated_content.alternatives
            }
        }


@app.post("/copywriting/ab-test", tags=["copywriting"])
@handle_exceptions
@track_performance("ab_test_copy", "copywriting")
@optimize_performance(cache_results=True, profile=True)
async def generate_ab_test_variants(
    content_type: ContentType,
    target_audience: str,
    key_message: str,
    variants: int = 3,
    tone: ContentTone = ContentTone.PROFESSIONAL,
    language: ContentLanguage = ContentLanguage.ENGLISH,
    keywords: List[str] = [],
    call_to_action: Optional[str] = None
):
    """Generate multiple variants for A/B testing."""
    if not copywriting_model:
        raise ServiceError("Copywriting model not available")
    
    if variants > 5:
        raise ValidationError("Maximum 5 variants allowed")
    
    async with api_limiter:
        # Create content request
        request = ContentRequest(
            content_type=content_type,
            target_audience=target_audience,
            key_message=key_message,
            tone=tone,
            language=language,
            keywords=keywords,
            call_to_action=call_to_action
        )
        
        # Generate A/B test variants
        variant_contents = await copywriting_model.a_b_test_content(request, variants)
        
        return {
            "status": "success",
            "ab_test": {
                "test_id": FastHasher.hash_fast(f"{request.json()}_{int(time.time())}")[:12],
                "variants": [
                    {
                        "variant_id": content.id,
                        "text": content.content,
                        "tone": content.tone,
                        "confidence_score": content.confidence_score,
                        "generation_time_ms": content.generation_time_ms,
                        "metrics": content.metrics.dict() if content.metrics else None
                    }
                    for content in variant_contents
                ],
                "total_variants": len(variant_contents),
                "recommended_variant": max(variant_contents, key=lambda x: x.confidence_score).id
            }
        }


@app.post("/copywriting/analyze", tags=["copywriting"])
@handle_exceptions
@track_performance("analyze_copy", "copywriting")
@optimize_performance(cache_results=True, profile=True)
async def analyze_existing_content(
    content: str,
    keywords: List[str] = []
):
    """Analyze existing content for optimization insights."""
    if not copywriting_model:
        raise ServiceError("Copywriting model not available")
    
    async with api_limiter:
        # Analyze content
        metrics = await copywriting_model.analyzer.analyze_content(content, keywords)
        
        return {
            "status": "success",
            "analysis": {
                "content_length": len(content),
                "word_count": metrics.word_count,
                "readability_score": metrics.readability_score,
                "sentiment_score": metrics.sentiment_score,
                "engagement_prediction": metrics.engagement_prediction,
                "reading_time_minutes": metrics.reading_time_minutes,
                "keyword_density": metrics.keyword_density,
                "emotional_triggers": metrics.emotional_triggers,
                "call_to_action_strength": metrics.call_to_action_strength,
                "recommendations": {
                    "readability": "excellent" if metrics.readability_score > 70 else "needs_improvement",
                    "sentiment": "positive" if metrics.sentiment_score > 0.1 else "neutral_or_negative",
                    "engagement": "high" if metrics.engagement_prediction > 0.7 else "medium" if metrics.engagement_prediction > 0.4 else "low",
                    "cta_presence": "strong" if metrics.call_to_action_strength > 0.5 else "weak"
                }
            }
        }


@app.get("/copywriting/templates", tags=["copywriting"])
@handle_exceptions
async def get_copywriting_templates():
    """Get available copywriting templates and content types."""
    return {
        "status": "success",
        "templates": {
            "content_types": [ct.value for ct in ContentType],
            "tones": [tone.value for tone in ContentTone],
            "languages": [lang.value for lang in ContentLanguage],
            "available_templates": {
                content_type.value: list(templates.keys())
                for content_type, templates in CopywritingTemplates.TEMPLATES.items()
            }
        }
    }


@app.get("/copywriting/stats", tags=["copywriting"])
@handle_exceptions
async def get_copywriting_stats():
    """Get copywriting model performance statistics."""
    if not copywriting_model:
        raise ServiceError("Copywriting model not available")
    
    stats = await copywriting_model.get_performance_stats()
    
    return {
        "status": "success",
        "stats": stats
    }


# Admin Endpoints

@app.get("/admin/stats", tags=["admin"])
@handle_exceptions
@optimize_performance(cache_results=True, profile=False)
async def get_system_stats():
    """Get comprehensive system statistics."""
    try:
        # Get optimized system stats
        memory_stats = memory_optimizer.get_memory_usage()
        optimization_suggestions = profiler.get_optimization_suggestions()
        
        stats = {
            "config": {
                "environment": config.environment.value,
                "debug": config.debug,
                "version": config.app_version
            },
            "features": {
                "async_enabled": config.enable_async,
                "monitoring_enabled": config.monitoring.enable_prometheus,
                "sentry_enabled": config.monitoring.enable_sentry,
                "optimization_enabled": True
            },
            "performance": {
                "memory_usage": memory_stats,
                "optimization_config": OPTIMIZATION_CONFIG,
                "suggestions": optimization_suggestions
            }
        }
        
        if message_service:
            message_stats = await message_service.get_service_stats()
            stats["message_service"] = message_stats
        
        # Add optimization stats
        from .startup import get_startup_orchestrator
        orchestrator = get_startup_orchestrator()
        if orchestrator and orchestrator.performance_orchestrator:
            optimization_stats = orchestrator.performance_orchestrator.get_performance_summary()
            stats["optimization"] = optimization_stats
        
        return {"status": "success", "stats": stats}
        
    except Exception as e:
        logger.error("Failed to get system stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get system stats")


@app.post("/admin/cache/clear", tags=["admin"])
@handle_exceptions
async def clear_cache():
    """Clear application caches."""
    try:
        if message_service:
            await message_service.clear_cache()
        
        return {"status": "success", "message": "Caches cleared"}
        
    except Exception as e:
        logger.error("Failed to clear cache", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to clear cache")


# Error handlers
@app.exception_handler(OnyxBaseException)
async def onyx_exception_handler(request: Request, exc: OnyxBaseException):
    """Handle custom Onyx exceptions."""
    logger.error("Onyx exception occurred", 
                error_type=type(exc).__name__,
                error_code=exc.error_code,
                message=str(exc))
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": exc.error_code,
            "message": str(exc),
            "correlation_id": getattr(request.state, "correlation_id", None)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error("Unhandled exception occurred", 
                error=str(exc),
                exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_code": "INTERNAL_ERROR",
            "message": "An internal error occurred",
            "correlation_id": getattr(request.state, "correlation_id", None)
        }
    )


# Application factory
def create_app(config_override: Optional[OnyxConfig] = None) -> FastAPI:
    """
    Application factory with optional configuration override.
    
    Args:
        config_override: Optional configuration override
        
    Returns:
        FastAPI: Configured application instance
    """
    if config_override:
        global config
        config = config_override
    
    logger.info("Application created", 
               environment=config.environment.value,
               debug=config.debug)
    
    return app


# CLI entry point
def main():
    """Main entry point for running the application."""
    host = "0.0.0.0"
    port = 8000
    
    if config.environment == Environment.DEVELOPMENT:
        uvicorn.run(
            "agents.backend.onyx.server.features.app:app",
            host=host,
            port=port,
            reload=True,
            log_level="debug"
        )
    else:
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=config.max_workers,
            access_log=True,
            log_level="info"
        )


if __name__ == "__main__":
    main() 