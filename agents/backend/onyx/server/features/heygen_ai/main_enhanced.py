#!/usr/bin/env python3
"""
Enhanced HeyGen AI FastAPI Application
Main application file that integrates all enhanced components.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import structlog
import time
from datetime import datetime, timezone

# Import our enhanced components
from .core.heygen_ai import HeyGenAI
from .config.settings import get_settings
from .api.routes import router as heygen_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

# Get settings
settings = get_settings()

# =============================================================================
# FastAPI Application Configuration
# =============================================================================

def create_enhanced_app() -> FastAPI:
    """Create the enhanced HeyGen AI FastAPI application."""
    
    app = FastAPI(
        title="Enhanced HeyGen AI API",
        description="""
        Advanced AI-powered video generation and processing API with enhanced capabilities.
        
        ## Enhanced Features
        
        * **Real AI Models**: Stable Diffusion, Coqui TTS, Wav2Lip integration
        * **Advanced Video Generation**: Full pipeline from script to final video
        * **Voice Synthesis**: Multiple TTS engines with voice cloning
        * **Avatar Management**: AI-generated avatars with lip-sync
        * **Performance Monitoring**: Real-time metrics and health checks
        
        ## Quick Start
        
        1. **Health Check**: `GET /api/v1/health`
        2. **Create Video**: `POST /api/v1/videos/create`
        3. **Generate Voice**: `POST /api/v1/voice/generate`
        4. **Generate Avatar**: `POST /api/v1/avatar/generate`
        
        ## Authentication
        
        This API uses Bearer token authentication. Include your token in the Authorization header:
        
        ```
        Authorization: Bearer your-token-here
        ```
        """,
        version="2.0.0",
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json",
        contact={
            "name": "Enhanced HeyGen AI Support",
            "email": "support@heygen-ai.com",
            "url": "https://heygen-ai.com/support"
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    )
    
    # =============================================================================
    # Middleware Setup
    # =============================================================================
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://app.heygen-ai.com",
            "https://api.heygen-ai.com",
            "http://localhost:3000",  # Development only
            "http://localhost:8000"   # Development only
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "X-API-Key"
        ]
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # =============================================================================
    # Request Logging Middleware
    # =============================================================================
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests for monitoring and debugging."""
        start_time = time.time()
        
        # Generate request ID
        request_id = f"req_{int(start_time * 1000)}"
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else "unknown"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=process_time
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                process_time=process_time
            )
            raise
    
    # =============================================================================
    # Route Registration
    # =============================================================================
    
    # Include HeyGen AI routes
    app.include_router(
        heygen_router,
        prefix="/api/v1",
        tags=["heygen-ai"]
    )
    
    # =============================================================================
    # System Routes
    # =============================================================================
    
    @app.get("/", tags=["system"])
    async def root():
        """Root endpoint with system information."""
        return {
            "message": "Enhanced HeyGen AI API",
            "version": "2.0.0",
            "status": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "docs": "/docs" if settings.debug else None,
            "health": "/api/v1/health"
        }
    
    @app.get("/health", tags=["system"])
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "service": "Enhanced HeyGen AI API"
        }
    
    @app.get("/info", tags=["system"])
    async def api_info():
        """API information endpoint."""
        return {
            "name": "Enhanced HeyGen AI API",
            "version": "2.0.0",
            "description": "Advanced AI-powered video generation and processing API",
            "features": [
                "Real AI Models Integration",
                "Advanced Video Generation Pipeline",
                "Voice Synthesis & Cloning",
                "Avatar Management & Lip-sync",
                "Performance Monitoring",
                "Health Checks"
            ],
            "endpoints": {
                "health": "/api/v1/health",
                "status": "/api/v1/status",
                "videos": "/api/v1/videos",
                "voice": "/api/v1/voice",
                "avatar": "/api/v1/avatar"
            },
            "docs": "/docs" if settings.debug else None
        }
    
    # =============================================================================
    # Error Handlers
    # =============================================================================
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        request_id = getattr(request.state, "request_id", "unknown")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "error_code": f"HTTP_{exc.status_code}",
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        request_id = getattr(request.state, "request_id", "unknown")
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Validation error",
                "error_code": "VALIDATION_ERROR",
                "error_details": exc.errors(),
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors."""
        request_id = getattr(request.state, "request_id", "unknown")
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Data validation error",
                "error_code": "VALIDATION_ERROR",
                "error_details": exc.errors(),
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        request_id = getattr(request.state, "request_id", "unknown")
        
        logger.error(
            "Unhandled exception",
            error_type=type(exc).__name__,
            error_message=str(exc),
            request_id=request_id,
            method=request.method,
            url=str(request.url)
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    # =============================================================================
    # Lifecycle Events
    # =============================================================================
    
    @app.on_event("startup")
    async def startup_event():
        """Application startup event."""
        logger.info("Starting Enhanced HeyGen AI API", version="2.0.0")
        
        # Initialize HeyGen AI system
        try:
            # This will be initialized when the first request comes in
            logger.info("Enhanced HeyGen AI system ready for initialization")
        except Exception as e:
            logger.error(f"Failed to initialize HeyGen AI system: {e}")
            raise
        
        logger.info("Enhanced HeyGen AI API started successfully")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown event."""
        logger.info("Shutting down Enhanced HeyGen AI API")
        logger.info("Enhanced HeyGen AI API shutdown completed")
    
    # =============================================================================
    # Development Routes
    # =============================================================================
    
    if settings.debug:
        @app.get("/debug/routes", tags=["debug"])
        async def debug_routes():
            """Debug routes endpoint for development."""
            routes = []
            for route in app.routes:
                if hasattr(route, "methods"):
                    routes.append({
                        "path": route.path,
                        "methods": list(route.methods),
                        "name": getattr(route, "name", "Unknown"),
                        "tags": getattr(route, "tags", [])
                    })
            
            return {
                "total_routes": len(routes),
                "routes": routes
            }
        
        @app.get("/debug/config", tags=["debug"])
        async def debug_config():
            """Debug configuration endpoint for development."""
            return {
                "debug": settings.debug,
                "api_host": settings.api_host,
                "api_port": settings.api_port,
                "api_workers": settings.api_workers,
                "langchain_enabled": settings.langchain_enabled,
                "gpu_enabled": settings.gpu_enabled,
                "supported_languages": settings.supported_languages,
                "video_styles": settings.video_styles,
                "quality_presets": list(settings.video_quality_presets.keys())
            }
    
    return app

# =============================================================================
# Application Factory Functions
# =============================================================================

def create_development_app() -> FastAPI:
    """Create development FastAPI application."""
    return create_enhanced_app()

def create_production_app() -> FastAPI:
    """Create production FastAPI application."""
    return create_enhanced_app()

# =============================================================================
# Main Application Instance
# =============================================================================

# Create the main application instance
app = create_enhanced_app()

# =============================================================================
# Export
# =============================================================================

__all__ = [
    "create_enhanced_app",
    "create_development_app",
    "create_production_app",
    "app"
]

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main_enhanced:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=settings.api_workers if not settings.debug else 1,
        log_level=settings.log_level.lower()
    )

