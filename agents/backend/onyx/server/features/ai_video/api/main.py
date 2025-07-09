#!/usr/bin/env python3
"""
FastAPI Main Application - AI Video System

Main FastAPI application with lifespan context manager for startup/shutdown,
modern dependency injection, and comprehensive error handling.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import dependencies and routes
from .dependencies import create_app, lifespan, app_state
from .routes import video_router, system_router

# Import core components
from ..core.error_handler import error_handler, ErrorContext
from ..core.exceptions import AIVideoError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create FastAPI application with lifespan
app = FastAPI(
    title="AI Video System API",
    description="Advanced AI video generation system with performance optimization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # Use lifespan context manager instead of on_event
)


# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)


# Request/Response middleware
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Middleware for request tracking and error handling."""
    # Increment active requests
    app_state.increment_requests()
    
    # Add request ID to headers if not present
    if "X-Request-ID" not in request.headers:
        import uuid
        request.headers.__dict__["_list"].append(
            (b"x-request-id", str(uuid.uuid4()).encode())
        )
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        # Handle unexpected errors
        error_context = ErrorContext(
            operation=request.url.path,
            user_id=request.headers.get("X-User-ID"),
            request_id=request.headers.get("X-Request-ID")
        )
        
        error = error_handler.handle_error(e, error_context)
        logger.error(f"Request failed: {error.message}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "details": {"type": type(e).__name__},
                "timestamp": asyncio.get_event_loop().time()
            }
        )
    finally:
        # Decrement active requests
        app_state.decrement_requests()


# Exception handlers
@app.exception_handler(AIVideoError)
async def ai_video_error_handler(request: Request, exc: AIVideoError):
    """Handle AI Video system errors."""
    error_context = ErrorContext(
        operation=request.url.path,
        user_id=request.headers.get("X-User-ID"),
        request_id=request.headers.get("X-Request-ID")
    )
    
    error = error_handler.handle_error(exc, error_context)
    
    return JSONResponse(
        status_code=400,
        content={
            "error": error.message,
            "error_code": error.error_code or "AI_VIDEO_ERROR",
            "details": error.details,
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    error_context = ErrorContext(
        operation=request.url.path,
        user_id=request.headers.get("X-User-ID"),
        request_id=request.headers.get("X-Request-ID")
    )
    
    logger.error(f"Validation Error: {exc.errors()}", extra={"context": error_context.to_dict()})
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "details": {"errors": exc.errors()},
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    error_context = ErrorContext(
        operation=request.url.path,
        user_id=request.headers.get("X-User-ID"),
        request_id=request.headers.get("X-Request-ID")
    )
    
    logger.error(f"HTTP Exception: {exc.detail}", extra={"context": error_context.to_dict()})
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    error_context = ErrorContext(
        operation=request.url.path,
        user_id=request.headers.get("X-User-ID"),
        request_id=request.headers.get("X-Request-ID")
    )
    
    error = error_handler.handle_error(exc, error_context)
    logger.error(f"Generic Exception: {error.message}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "details": {"type": type(exc).__name__},
            "timestamp": asyncio.get_event_loop().time()
        }
    )


# Include routers
app.include_router(video_router, prefix="/api/v1/videos", tags=["videos"])
app.include_router(system_router, prefix="/api/v1/system", tags=["system"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Video System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/system/health",
        "status": "/api/v1/system/status"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "version": "1.0.0",
        "uptime": app_state.get_uptime(),
        "active_requests": app_state.active_requests
    }


# OpenAPI customization
def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI Video System API",
        version="1.0.0",
        description="Advanced AI video generation system with performance optimization",
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Development server configuration
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 