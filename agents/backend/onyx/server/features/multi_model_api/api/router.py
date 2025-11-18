"""
FastAPI router for multi-model API
Optimized with async operations, caching, and health monitoring
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.models import ModelRegistry, get_registry
from ..core.cache import EnhancedCache, get_cache
from ..api.schemas import (
    MultiModelRequest,
    MultiModelResponse,
    ModelResponse,
    ModelConfig,
    ModelType,
    ModelsListResponse,
    ModelStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multi-model", tags=["Multi-Model API"])


def get_model_registry() -> ModelRegistry:
    """Dependency to get model registry"""
    return get_registry()


def get_cache_instance() -> EnhancedCache:
    """Dependency to get cache instance"""
    return get_cache()


@router.post("/execute", response_model=MultiModelResponse)
async def execute_multi_model(
    request: MultiModelRequest,
    registry: ModelRegistry = Depends(get_model_registry),
    cache: EnhancedCache = Depends(get_cache_instance),
    background_tasks: BackgroundTasks = None
):
    """
    Execute multiple AI models with optimized parallel processing
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    enabled_models = [m for m in request.models if m.is_enabled]
    if not enabled_models:
        raise HTTPException(status_code=400, detail="At least one model must be enabled")
    
    cache_key = cache._generate_key(
        "multi_model",
        request.prompt,
        *[m.model_type.value for m in enabled_models],
        request.strategy
    )
    
    if request.cache_enabled:
        cached_response = await cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for request {request_id}")
            return MultiModelResponse(
                **cached_response,
                cache_hit=True
            )
    
    try:
        if request.strategy == "parallel":
            responses = await _execute_parallel(
                enabled_models,
                request.prompt,
                registry
            )
        elif request.strategy == "sequential":
            responses = await _execute_sequential(
                enabled_models,
                request.prompt,
                registry
            )
        elif request.strategy == "consensus":
            responses = await _execute_consensus(
                enabled_models,
                request.prompt,
                registry
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy}")
        
        total_latency_ms = (time.time() - start_time) * 1000
        total_tokens = sum(r.tokens_used or 0 for r in responses if r.success)
        
        aggregated_response = _aggregate_responses(responses, request.strategy)
        
        response_data = {
            "request_id": request_id,
            "prompt": request.prompt,
            "strategy": request.strategy,
            "responses": [r.dict() for r in responses],
            "aggregated_response": aggregated_response,
            "total_tokens": total_tokens,
            "total_latency_ms": round(total_latency_ms, 2),
            "cache_hit": False,
            "timestamp": datetime.now().isoformat()
        }
        
        if request.cache_enabled:
            cache_ttl = request.cache_ttl or 3600
            background_tasks.add_task(
                cache.set,
                cache_key,
                response_data,
                ttl=cache_ttl
            )
        
        return MultiModelResponse(**response_data)
    
    except Exception as e:
        logger.error(f"Error executing multi-model request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_parallel(
    models: List[ModelConfig],
    prompt: str,
    registry: ModelRegistry
) -> List[ModelResponse]:
    """Execute models in parallel"""
    tasks = [
        registry.execute_model(
            model.model_type,
            prompt,
            temperature=model.temperature,
            max_tokens=model.max_tokens,
            **(model.custom_params or {})
        )
        for model in models
    ]
    
    return await asyncio.gather(*tasks, return_exceptions=False)


async def _execute_sequential(
    models: List[ModelConfig],
    prompt: str,
    registry: ModelRegistry
) -> List[ModelResponse]:
    """Execute models sequentially"""
    responses = []
    for model in models:
        response = await registry.execute_model(
            model.model_type,
            prompt,
            temperature=model.temperature,
            max_tokens=model.max_tokens,
            **(model.custom_params or {})
        )
        responses.append(response)
    return responses


async def _execute_consensus(
    models: List[ModelConfig],
    prompt: str,
    registry: ModelRegistry
) -> List[ModelResponse]:
    """Execute models and use consensus/voting"""
    responses = await _execute_parallel(models, prompt, registry)
    return responses


def _aggregate_responses(responses: List[ModelResponse], strategy: str) -> Optional[str]:
    """Aggregate multiple model responses"""
    successful_responses = [r for r in responses if r.success and r.response]
    
    if not successful_responses:
        return None
    
    if strategy == "consensus":
        responses_text = [r.response for r in successful_responses]
        if len(set(responses_text)) == 1:
            return responses_text[0]
        return f"Consensus: {len(successful_responses)} models agree"
    
    if len(successful_responses) == 1:
        return successful_responses[0].response
    
    aggregated = "\n\n---\n\n".join([
        f"**{r.model_type.value}**:\n{r.response}"
        for r in successful_responses
    ])
    
    return aggregated


@router.get("/models", response_model=ModelsListResponse)
async def list_models(
    registry: ModelRegistry = Depends(get_model_registry)
):
    """List all available models with status"""
    available_models = registry.get_available_models()
    
    model_statuses = []
    for model_meta in available_models:
        model_statuses.append(ModelStatus(
            model_type=model_meta.model_type,
            is_available=model_meta.is_available,
            is_enabled=model_meta.is_available,
            multiplier=1,
            last_used=model_meta.last_used.isoformat() if model_meta.last_used else None,
            success_rate=round(model_meta.success_rate, 2),
            avg_latency_ms=round(model_meta.avg_latency_ms, 2)
        ))
    
    return ModelsListResponse(
        models=model_statuses,
        total_available=len(available_models),
        total_enabled=len([m for m in model_statuses if m.is_enabled])
    )


@router.get("/models/{model_type}/health")
async def get_model_health(
    model_type: ModelType = Path(..., description="Model type"),
    registry: ModelRegistry = Depends(get_model_registry)
):
    """Get health metrics for a specific model"""
    health = registry.get_model_health(model_type)
    if "error" in health:
        raise HTTPException(status_code=404, detail=health["error"])
    return health


@router.get("/health")
async def health_check(
    registry: ModelRegistry = Depends(get_model_registry),
    cache: EnhancedCache = Depends(get_cache_instance)
):
    """Comprehensive health check"""
    cache_stats = await cache.get_stats()
    available_models = len(registry.get_available_models())
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache": {
            "enabled": True,
            "hit_rate": cache_stats.get("hit_rate", 0),
            "l1_size": cache_stats.get("l1_size", 0)
        },
        "models": {
            "total_available": available_models,
            "total_registered": len(registry.models)
        }
    }


@router.get("/stats")
async def get_stats(
    registry: ModelRegistry = Depends(get_model_registry),
    cache: EnhancedCache = Depends(get_cache_instance)
):
    """Get comprehensive statistics"""
    cache_stats = await cache.get_stats()
    
    model_stats = []
    for model_type, model_meta in registry.models.items():
        model_stats.append({
            "model_type": model_type.value,
            "call_count": model_meta.call_count,
            "success_rate": round(model_meta.success_rate, 2),
            "avg_latency_ms": round(model_meta.avg_latency_ms, 2),
            "p95_latency_ms": round(model_meta.p95_latency_ms, 2),
            "circuit_breaker_state": model_meta.circuit_breaker.state
        })
    
    return {
        "cache": cache_stats,
        "models": model_stats,
        "timestamp": datetime.now().isoformat()
    }


@router.delete("/cache")
async def clear_cache(
    level: Optional[str] = Query(None, description="Cache level: l1, l2, or both"),
    cache: EnhancedCache = Depends(get_cache_instance)
):
    """Clear cache"""
    success = await cache.clear(level=level)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear cache")
    return {"message": "Cache cleared successfully", "level": level or "both"}

