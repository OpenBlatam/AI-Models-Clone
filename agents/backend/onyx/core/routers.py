"""
Enhanced API Routers
===================

Modular router system with clean separation of concerns,
comprehensive validation, and proper error handling.
"""

import asyncio
import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import StreamingResponse
import structlog

from .schemas import (
    ContentGenerationRequest, ContentGenerationResponse,
    BulkContentRequest, DataResponse, PaginatedResponse,
    PaginationParams, SearchRequest, BaseResponse
)

logger = structlog.get_logger(__name__)

# =============================================================================
# CONTENT GENERATION ROUTER
# =============================================================================

content_router = APIRouter(prefix="/content", tags=["Content Generation"])


@content_router.post(
    "/generate",
    response_model=ContentGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate content",
    description="Generate AI-powered content based on request parameters"
)
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks
) -> ContentGenerationResponse:
    """
    Generate AI-powered content with comprehensive validation and quality metrics.
    
    This endpoint creates high-quality content based on:
    - Content type and topic
    - Target audience and tone
    - SEO keywords and requirements
    - Quality and readability scores
    """
    start_time = time.time()
    
    try:
        # Log request for monitoring
        logger.info(
            "Content generation started",
            content_type=request.content_type,
            topic=request.topic,
            language=request.language,
            word_count=request.word_count
        )
        
        # Simulate AI content generation (replace with actual AI service)
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Generate mock content based on request
        content = f"""
        # {request.topic}
        
        This is a {request.content_type.value} about {request.topic} written in a {request.tone.value} tone.
        
        {request.description}
        
        Target audience: {request.target_audience or 'General audience'}
        
        Keywords: {', '.join(request.keywords) if request.keywords else 'None specified'}
        
        {"Call to action: Take action now!" if request.include_cta else ""}
        """.strip()
        
        # Calculate metrics
        word_count = len(content.split())
        execution_time = (time.time() - start_time) * 1000
        
        # Schedule background tasks
        background_tasks.add_task(
            _log_content_generation,
            request.content_type,
            word_count,
            execution_time
        )
        
        response = ContentGenerationResponse(
            success=True,
            message="Content generated successfully",
            execution_time_ms=execution_time,
            content=content,
            content_type=request.content_type,
            word_count=word_count,
            quality_score=0.85,
            seo_score=0.78,
            readability_score=0.92,
            keywords_used=request.keywords[:5],  # Use first 5 keywords
            suggestions=[
                "Consider adding more specific examples",
                "Include relevant statistics",
                "Add subheadings for better structure"
            ]
        )
        
        logger.info(
            "Content generation completed",
            content_type=request.content_type,
            word_count=word_count,
            execution_time_ms=execution_time
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "Content generation failed",
            error=str(e),
            content_type=request.content_type,
            topic=request.topic
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@content_router.post(
    "/generate/bulk",
    response_model=DataResponse,
    summary="Bulk content generation",
    description="Generate multiple pieces of content in a single request"
)
async def generate_bulk_content(
    request: BulkContentRequest,
    background_tasks: BackgroundTasks
) -> DataResponse:
    """
    Generate multiple pieces of content efficiently with batch processing.
    
    Features:
    - Parallel processing for better performance
    - Batch optimization
    - Individual error handling
    - Progress tracking
    """
    start_time = time.time()
    
    try:
        logger.info(
            "Bulk content generation started",
            batch_size=len(request.requests),
            batch_id=request.batch_id,
            priority=request.priority
        )
        
        # Process requests in parallel
        tasks = []
        for i, content_request in enumerate(request.requests):
            task = _generate_single_content(content_request, i)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({
                    "index": i,
                    "topic": request.requests[i].topic,
                    "error": str(result)
                })
            else:
                successful_results.append(result)
        
        execution_time = (time.time() - start_time) * 1000
        
        # Schedule background tasks
        background_tasks.add_task(
            _log_bulk_generation,
            len(successful_results),
            len(failed_results),
            execution_time
        )
        
        response_data = {
            "batch_id": request.batch_id,
            "total_requested": len(request.requests),
            "successful": len(successful_results),
            "failed": len(failed_results),
            "results": successful_results,
            "errors": failed_results,
            "execution_time_ms": execution_time
        }
        
        return DataResponse(
            success=len(failed_results) == 0,
            message=f"Bulk generation completed: {len(successful_results)} successful, {len(failed_results)} failed",
            data=response_data,
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error("Bulk content generation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk generation failed: {str(e)}"
        )


@content_router.get(
    "/history",
    response_model=PaginatedResponse,
    summary="Content generation history",
    description="Get paginated history of generated content"
)
async def get_content_history(
    pagination: PaginationParams = Depends(),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    search: Optional[str] = Query(None, description="Search in topics")
) -> PaginatedResponse:
    """Get paginated content generation history with filtering."""
    
    # Simulate database query
    await asyncio.sleep(0.05)
    
    # Mock data
    total_items = 250
    mock_items = []
    
    for i in range(pagination.offset, min(pagination.offset + pagination.size, total_items)):
        mock_items.append({
            "id": f"content_{i}",
            "topic": f"Topic {i}",
            "content_type": "blog_post",
            "word_count": 500 + (i * 10),
            "quality_score": 0.8 + (i % 20) * 0.01,
            "created_at": "2024-01-01T00:00:00Z"
        })
    
    # Apply filters
    if content_type:
        mock_items = [item for item in mock_items if item["content_type"] == content_type]
    
    if search:
        mock_items = [item for item in mock_items if search.lower() in item["topic"].lower()]
    
    total_pages = (total_items + pagination.size - 1) // pagination.size
    
    return PaginatedResponse(
        success=True,
        message="Content history retrieved successfully",
        data=mock_items,
        pagination={
            "page": pagination.page,
            "size": pagination.size,
            "total": total_items,
            "pages": total_pages,
            "has_next": pagination.page < total_pages,
            "has_prev": pagination.page > 1
        }
    )


# =============================================================================
# ANALYTICS ROUTER
# =============================================================================

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get(
    "/performance",
    response_model=DataResponse,
    summary="Performance analytics",
    description="Get detailed performance analytics and metrics"
)
async def get_performance_analytics(
    period: str = Query("24h", regex="^(1h|24h|7d|30d)$", description="Analytics period"),
    include_details: bool = Query(False, description="Include detailed metrics")
) -> DataResponse:
    """Get comprehensive performance analytics."""
    
    # Simulate analytics calculation
    await asyncio.sleep(0.1)
    
    analytics_data = {
        "period": period,
        "total_requests": 1250,
        "successful_requests": 1190,
        "failed_requests": 60,
        "success_rate": 95.2,
        "average_response_time_ms": 245,
        "median_response_time_ms": 180,
        "p95_response_time_ms": 450,
        "content_types": {
            "blog_post": 450,
            "social_media": 380,
            "product_description": 290,
            "email_campaign": 130
        },
        "languages": {
            "en": 80.5,
            "es": 12.3,
            "fr": 4.2,
            "de": 2.1,
            "other": 0.9
        }
    }
    
    if include_details:
        analytics_data["hourly_breakdown"] = [
            {"hour": i, "requests": 50 + (i * 5), "avg_response_time": 200 + (i * 10)}
            for i in range(24)
        ]
    
    return DataResponse(
        success=True,
        message=f"Performance analytics for {period}",
        data=analytics_data
    )


@analytics_router.get(
    "/quality",
    response_model=DataResponse,
    summary="Content quality analytics",
    description="Get content quality metrics and trends"
)
async def get_quality_analytics() -> DataResponse:
    """Get content quality analytics and trends."""
    
    quality_data = {
        "overall_quality_score": 0.847,
        "quality_trend": "improving",
        "quality_by_type": {
            "blog_post": {"avg_score": 0.89, "count": 450},
            "social_media": {"avg_score": 0.82, "count": 380},
            "product_description": {"avg_score": 0.91, "count": 290},
            "email_campaign": {"avg_score": 0.78, "count": 130}
        },
        "seo_metrics": {
            "avg_seo_score": 0.76,
            "keyword_optimization": 0.83,
            "readability_score": 0.88
        },
        "improvement_suggestions": [
            "Focus on improving email campaign quality",
            "Increase keyword density in social media content",
            "Enhance readability for technical content"
        ]
    }
    
    return DataResponse(
        success=True,
        message="Quality analytics retrieved successfully",
        data=quality_data
    )


# =============================================================================
# SEARCH ROUTER
# =============================================================================

search_router = APIRouter(prefix="/search", tags=["Search"])


@search_router.post(
    "/content",
    response_model=PaginatedResponse,
    summary="Search content",
    description="Advanced content search with filters and ranking"
)
async def search_content(
    request: SearchRequest,
    pagination: PaginationParams = Depends()
) -> PaginatedResponse:
    """
    Advanced content search with full-text search, filters, and relevance ranking.
    
    Features:
    - Full-text search across content
    - Advanced filtering options
    - Relevance scoring
    - Faceted search results
    """
    start_time = time.time()
    
    try:
        logger.info(
            "Content search started",
            query=request.query,
            filters=request.filters,
            sort_by=request.sort_by
        )
        
        # Simulate search processing
        await asyncio.sleep(0.1)
        
        # Mock search results
        total_results = 156
        search_results = []
        
        for i in range(pagination.offset, min(pagination.offset + pagination.size, total_results)):
            relevance_score = 0.95 - (i * 0.01)
            search_results.append({
                "id": f"result_{i}",
                "title": f"Search Result {i} - {request.query}",
                "content_type": "blog_post",
                "excerpt": f"This content matches your search for '{request.query}' and provides relevant information...",
                "relevance_score": relevance_score,
                "word_count": 500 + (i * 25),
                "created_at": "2024-01-01T00:00:00Z",
                "tags": ["relevant", "quality", request.query.lower()],
                "quality_score": 0.8 + (relevance_score * 0.2)
            })
        
        execution_time = (time.time() - start_time) * 1000
        total_pages = (total_results + pagination.size - 1) // pagination.size
        
        # Add search metadata
        search_meta = {
            "query": request.query,
            "total_results": total_results,
            "execution_time_ms": execution_time,
            "facets": {
                "content_types": {
                    "blog_post": 89,
                    "social_media": 34,
                    "product_description": 23,
                    "email_campaign": 10
                },
                "quality_ranges": {
                    "high (0.8+)": 124,
                    "medium (0.6-0.8)": 28,
                    "low (<0.6)": 4
                }
            }
        }
        
        return PaginatedResponse(
            success=True,
            message=f"Found {total_results} results for '{request.query}'",
            data=search_results,
            pagination={
                "page": pagination.page,
                "size": pagination.size,
                "total": total_results,
                "pages": total_pages,
                "has_next": pagination.page < total_pages,
                "has_prev": pagination.page > 1
            },
            meta=search_meta
        )
        
    except Exception as e:
        logger.error("Content search failed", error=str(e), query=request.query)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _generate_single_content(request: ContentGenerationRequest, index: int) -> dict:
    """Generate a single piece of content (helper for bulk generation)."""
    await asyncio.sleep(0.05)  # Simulate processing
    
    content = f"Generated content for: {request.topic}"
    word_count = len(content.split())
    
    return {
        "index": index,
        "topic": request.topic,
        "content": content,
        "content_type": request.content_type,
        "word_count": word_count,
        "quality_score": 0.85,
        "seo_score": 0.78,
        "readability_score": 0.92
    }


async def _log_content_generation(content_type: str, word_count: int, execution_time: float) -> None:
    """Background task to log content generation metrics."""
    logger.info(
        "Content generation metrics logged",
        content_type=content_type,
        word_count=word_count,
        execution_time_ms=execution_time
    )


async def _log_bulk_generation(successful: int, failed: int, execution_time: float) -> None:
    """Background task to log bulk generation metrics."""
    logger.info(
        "Bulk generation metrics logged",
        successful_count=successful,
        failed_count=failed,
        execution_time_ms=execution_time
    )


# =============================================================================
# ROUTER COLLECTION
# =============================================================================

def get_api_routers() -> List[APIRouter]:
    """Get all API routers for inclusion in the main app."""
    return [
        content_router,
        analytics_router,
        search_router
    ] 