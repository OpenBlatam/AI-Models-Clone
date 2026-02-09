#!/usr/bin/env python3
"""
FastAPI Application - Presentation Layer
======================================

FastAPI application with comprehensive API endpoints, automatic documentation,
rate limiting, authentication, and advanced features.
"""

import asyncio
import logging
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

from ...domain.entities.linkedin_post import LinkedInPost
from ...domain.value_objects.post_tone import PostTone
from ...domain.value_objects.post_length import PostLength
from ...domain.value_objects.optimization_strategy import OptimizationStrategy
from ...application.use_cases.generate_post_use_case import (
    GeneratePostUseCaseImpl,
    GeneratePostRequest,
    GeneratePostResponse
)
from ...infrastructure.repositories.postgresql_repository import PostgreSQLPostRepository


# Pydantic models for API requests/responses
class GeneratePostRequestModel(BaseModel):
    """Request model for generating a LinkedIn post."""
    
    topic: str = Field(..., min_length=1, max_length=200, description="Post topic")
    tone: str = Field(default="professional", description="Post tone")
    length: str = Field(default="medium", description="Post length")
    include_hashtags: bool = Field(default=True, description="Include hashtags")
    include_call_to_action: bool = Field(default=True, description="Include call to action")
    optimization_strategy: str = Field(default="default", description="Optimization strategy")
    custom_hashtags: Optional[List[str]] = Field(default=None, description="Custom hashtags")
    custom_call_to_action: Optional[str] = Field(default=None, description="Custom call to action")
    target_audience: Optional[str] = Field(default=None, description="Target audience")
    industry_context: Optional[str] = Field(default=None, description="Industry context")
    content_style: Optional[str] = Field(default=None, description="Content style")
    
    @validator('tone')
    def validate_tone(cls, v):
        try:
            PostTone(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid tone: {v}")
    
    @validator('length')
    def validate_length(cls, v):
        try:
            PostLength(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid length: {v}")
    
    @validator('optimization_strategy')
    def validate_strategy(cls, v):
        try:
            OptimizationStrategy(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid optimization strategy: {v}")


class GeneratePostResponseModel(BaseModel):
    """Response model for generated LinkedIn post."""
    
    post_id: str = Field(..., description="Post ID")
    topic: str = Field(..., description="Post topic")
    content: str = Field(..., description="Post content")
    tone: str = Field(..., description="Post tone")
    length: str = Field(..., description="Post length")
    hashtags: List[str] = Field(default_factory=list, description="Post hashtags")
    call_to_action: Optional[str] = Field(default=None, description="Call to action")
    optimization_strategy: str = Field(..., description="Optimization strategy")
    optimization_score: float = Field(..., description="Optimization score")
    engagement_score: float = Field(..., description="Engagement score")
    readiness_score: float = Field(..., description="Readiness score")
    generation_time_ms: float = Field(..., description="Generation time")
    optimization_time_ms: float = Field(..., description="Optimization time")
    cache_hit: bool = Field(..., description="Cache hit")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class PostListResponseModel(BaseModel):
    """Response model for post list."""
    
    posts: List[GeneratePostResponseModel] = Field(..., description="List of posts")
    total_count: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total pages")


class PerformanceMetricsModel(BaseModel):
    """Response model for performance metrics."""
    
    total_posts: int = Field(..., description="Total posts")
    average_score: float = Field(..., description="Average optimization score")
    average_generation_time_ms: float = Field(..., description="Average generation time")
    average_optimization_time_ms: float = Field(..., description="Average optimization time")
    cache_hits: int = Field(..., description="Cache hits")
    cache_misses: int = Field(..., description="Cache misses")
    cache_hit_rate: float = Field(..., description="Cache hit rate")


class SearchRequestModel(BaseModel):
    """Request model for searching posts."""
    
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum results")


class HealthCheckModel(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")
    database_connected: bool = Field(..., description="Database connection status")
    uptime_seconds: float = Field(..., description="Service uptime")


# Rate limiting and authentication
class RateLimiter:
    """Simple rate limiter for API endpoints."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [req_time for req_time in self.requests[client_id] 
                                      if req_time > minute_ago]
        else:
            self.requests[client_id] = []
        
        # Check rate limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True


# Security
security = HTTPBearer()
rate_limiter = RateLimiter(requests_per_minute=60)


def get_client_id(request: Request) -> str:
    """Extract client ID from request."""
    # In a real implementation, you might use API keys or user authentication
    return request.client.host if request.client else "unknown"


def verify_rate_limit(client_id: str) -> bool:
    """Verify rate limit for client."""
    return rate_limiter.is_allowed(client_id)


# FastAPI application
app = FastAPI(
    title="Ultra Library Optimization V7 API",
    description="Advanced LinkedIn post generation and optimization API with quantum computing, neuromorphic processing, and AI-powered features.",
    version="7.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Global variables
repository: Optional[PostgreSQLPostRepository] = None
use_case: Optional[GeneratePostUseCaseImpl] = None
start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global repository, use_case
    
    # Initialize PostgreSQL repository
    connection_string = "postgresql://user:password@localhost/ultra_library_v7"
    repository = PostgreSQLPostRepository(connection_string)
    await repository.initialize()
    
    # Initialize use case
    use_case = GeneratePostUseCaseImpl(repository)
    
    logging.info("FastAPI application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    global repository
    
    if repository:
        await repository.close()
        logging.info("FastAPI application shutdown complete")


# Dependency injection
def get_repository() -> PostgreSQLPostRepository:
    """Get repository instance."""
    if not repository:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    return repository


def get_use_case() -> GeneratePostUseCaseImpl:
    """Get use case instance."""
    if not use_case:
        raise HTTPException(status_code=503, detail="Use case not initialized")
    return use_case


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckModel, tags=["System"])
async def health_check(
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """Health check endpoint."""
    try:
        # Test database connection
        count = await repo.count()
        database_connected = True
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        database_connected = False
    
    return HealthCheckModel(
        status="healthy" if database_connected else "unhealthy",
        timestamp=datetime.utcnow().isoformat(),
        version="7.0.0",
        database_connected=database_connected,
        uptime_seconds=time.time() - start_time
    )


# Main API endpoints
@app.post("/api/v7/posts/generate", response_model=GeneratePostResponseModel, tags=["Posts"])
async def generate_post(
    request: GeneratePostRequestModel,
    repo: PostgreSQLPostRepository = Depends(get_repository),
    use_case: GeneratePostUseCaseImpl = Depends(get_use_case),
    client_id: str = Depends(get_client_id)
):
    """
    Generate a LinkedIn post with advanced optimization.
    
    This endpoint generates LinkedIn posts using various optimization strategies
    including quantum computing, neuromorphic processing, and AI-powered features.
    """
    # Rate limiting
    if not verify_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    try:
        # Convert request model to use case request
        use_case_request = GeneratePostRequest(
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            include_hashtags=request.include_hashtags,
            include_call_to_action=request.include_call_to_action,
            optimization_strategy=request.optimization_strategy,
            custom_hashtags=request.custom_hashtags,
            custom_call_to_action=request.custom_call_to_action,
            target_audience=request.target_audience,
            industry_context=request.industry_context,
            content_style=request.content_style
        )
        
        # Execute use case
        response = await use_case.execute(use_case_request)
        
        # Convert to response model
        return GeneratePostResponseModel(
            post_id=str(response.post.id),
            topic=response.post.topic,
            content=response.post.content,
            tone=response.post.tone.value,
            length=response.post.length.value,
            hashtags=response.post.hashtags,
            call_to_action=response.post.call_to_action,
            optimization_strategy=response.post.optimization_strategy.value,
            optimization_score=response.optimization_score,
            engagement_score=response.engagement_score,
            readiness_score=response.readiness_score,
            generation_time_ms=response.generation_time_ms,
            optimization_time_ms=response.optimization_time_ms,
            cache_hit=response.cache_hit,
            suggestions=response.suggestions,
            warnings=response.warnings,
            created_at=response.post.created_at.isoformat(),
            updated_at=response.post.updated_at.isoformat()
        )
        
    except Exception as e:
        logging.error(f"Failed to generate post: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate post: {str(e)}")


@app.get("/api/v7/posts/{post_id}", response_model=GeneratePostResponseModel, tags=["Posts"])
async def get_post(
    post_id: UUID,
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """Get a specific LinkedIn post by ID."""
    try:
        post = await repo.find_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return GeneratePostResponseModel(
            post_id=str(post.id),
            topic=post.topic,
            content=post.content,
            tone=post.tone.value,
            length=post.length.value,
            hashtags=post.hashtags,
            call_to_action=post.call_to_action,
            optimization_strategy=post.optimization_strategy.value,
            optimization_score=post.optimization_score,
            engagement_score=post.get_engagement_score(),
            readiness_score=1.0 if post.is_ready_for_posting() else 0.5,
            generation_time_ms=post.generation_time_ms,
            optimization_time_ms=post.optimization_time_ms,
            cache_hit=post.cache_hit,
            suggestions=[],
            warnings=[],
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get post: {str(e)}")


@app.get("/api/v7/posts", response_model=PostListResponseModel, tags=["Posts"])
async def list_posts(
    page: int = 1,
    page_size: int = 20,
    topic: Optional[str] = None,
    strategy: Optional[str] = None,
    min_score: Optional[float] = None,
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """List LinkedIn posts with filtering and pagination."""
    try:
        # Get posts based on filters
        if topic:
            posts = await repo.find_by_topic(topic)
        elif strategy:
            posts = await repo.find_by_optimization_strategy(strategy)
        elif min_score:
            posts = await repo.find_high_performing_posts(min_score)
        else:
            posts = await repo.find_recent_posts(limit=1000)
        
        # Pagination
        total_count = len(posts)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_posts = posts[start_idx:end_idx]
        
        # Convert to response models
        post_models = []
        for post in paginated_posts:
            post_models.append(GeneratePostResponseModel(
                post_id=str(post.id),
                topic=post.topic,
                content=post.content,
                tone=post.tone.value,
                length=post.length.value,
                hashtags=post.hashtags,
                call_to_action=post.call_to_action,
                optimization_strategy=post.optimization_strategy.value,
                optimization_score=post.optimization_score,
                engagement_score=post.get_engagement_score(),
                readiness_score=1.0 if post.is_ready_for_posting() else 0.5,
                generation_time_ms=post.generation_time_ms,
                optimization_time_ms=post.optimization_time_ms,
                cache_hit=post.cache_hit,
                suggestions=[],
                warnings=[],
                created_at=post.created_at.isoformat(),
                updated_at=post.updated_at.isoformat()
            ))
        
        return PostListResponseModel(
            posts=post_models,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=(total_count + page_size - 1) // page_size
        )
        
    except Exception as e:
        logging.error(f"Failed to list posts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list posts: {str(e)}")


@app.post("/api/v7/posts/search", response_model=PostListResponseModel, tags=["Posts"])
async def search_posts(
    request: SearchRequestModel,
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """Search LinkedIn posts by content."""
    try:
        posts = await repo.search_posts(request.query, request.limit)
        
        # Convert to response models
        post_models = []
        for post in posts:
            post_models.append(GeneratePostResponseModel(
                post_id=str(post.id),
                topic=post.topic,
                content=post.content,
                tone=post.tone.value,
                length=post.length.value,
                hashtags=post.hashtags,
                call_to_action=post.call_to_action,
                optimization_strategy=post.optimization_strategy.value,
                optimization_score=post.optimization_score,
                engagement_score=post.get_engagement_score(),
                readiness_score=1.0 if post.is_ready_for_posting() else 0.5,
                generation_time_ms=post.generation_time_ms,
                optimization_time_ms=post.optimization_time_ms,
                cache_hit=post.cache_hit,
                suggestions=[],
                warnings=[],
                created_at=post.created_at.isoformat(),
                updated_at=post.updated_at.isoformat()
            ))
        
        return PostListResponseModel(
            posts=post_models,
            total_count=len(post_models),
            page=1,
            page_size=len(post_models),
            total_pages=1
        )
        
    except Exception as e:
        logging.error(f"Failed to search posts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search posts: {str(e)}")


@app.delete("/api/v7/posts/{post_id}", tags=["Posts"])
async def delete_post(
    post_id: UUID,
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """Delete a LinkedIn post."""
    try:
        success = await repo.delete(post_id)
        if not success:
            raise HTTPException(status_code=404, detail="Post not found")
        
        return {"message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to delete post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")


# Analytics and metrics endpoints
@app.get("/api/v7/analytics/performance", response_model=PerformanceMetricsModel, tags=["Analytics"])
async def get_performance_metrics(
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """Get performance metrics for all posts."""
    try:
        metrics = await repo.get_performance_metrics()
        
        return PerformanceMetricsModel(
            total_posts=metrics['total_posts'],
            average_score=metrics['average_score'],
            average_generation_time_ms=metrics['average_generation_time_ms'],
            average_optimization_time_ms=metrics['average_optimization_time_ms'],
            cache_hits=metrics['cache_hits'],
            cache_misses=metrics['cache_misses'],
            cache_hit_rate=metrics['cache_hit_rate']
        )
        
    except Exception as e:
        logging.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")


@app.get("/api/v7/analytics/optimization", tags=["Analytics"])
async def get_optimization_statistics(
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """Get optimization strategy statistics."""
    try:
        stats = await repo.get_optimization_statistics()
        return stats
        
    except Exception as e:
        logging.error(f"Failed to get optimization statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization statistics: {str(e)}")


@app.get("/api/v7/analytics/engagement", tags=["Analytics"])
async def get_engagement_analytics(
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """Get engagement analytics for all posts."""
    try:
        analytics = await repo.get_engagement_analytics()
        return analytics
        
    except Exception as e:
        logging.error(f"Failed to get engagement analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get engagement analytics: {str(e)}")


# System management endpoints
@app.post("/api/v7/system/cleanup", tags=["System"])
async def cleanup_old_posts(
    days_old: int = 365,
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """Clean up old LinkedIn posts."""
    try:
        deleted_count = await repo.cleanup_old_posts(days_old)
        return {"message": f"Cleaned up {deleted_count} old posts"}
        
    except Exception as e:
        logging.error(f"Failed to cleanup old posts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup old posts: {str(e)}")


@app.get("/api/v7/system/export", tags=["System"])
async def export_posts(
    format: str = "json",
    repo: PostgreSQLPostRepository = Depends(get_repository)
):
    """Export all posts in specified format."""
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'csv'")
        
        data = await repo.export_posts(format)
        return {"data": data, "format": format}
        
    except Exception as e:
        logging.error(f"Failed to export posts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export posts: {str(e)}")


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 