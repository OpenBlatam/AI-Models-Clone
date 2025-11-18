"""
AI endpoints for document generation and analysis
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.exceptions import AIProviderError, ValidationError
from app.schemas.user import User
from app.schemas.ai import (
    AIGenerationRequest, AIGenerationResponse,
    AIContentAnalysisRequest, AIContentAnalysisResponse,
    AITranslationRequest, AITranslationResponse,
    AISummarizationRequest, AISummarizationResponse,
    AIImprovementRequest, AIImprovementResponse,
    AIBatchRequest, AIBatchResponse,
    AIDocumentGenerationRequest, AIDocumentGenerationResponse,
    AIProviderStatus, AIProvider
)
from app.services.ai_service import ai_service
from app.services.document_service import document_service

router = APIRouter()


@router.post("/generate", response_model=AIGenerationResponse)
async def generate_content(
    request: AIGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AIGenerationResponse:
    """Generate content using AI."""
    try:
        response = await ai_service.generate_content(request)
        return response
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/analyze", response_model=AIContentAnalysisResponse)
async def analyze_content(
    request: AIContentAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AIContentAnalysisResponse:
    """Analyze content using AI."""
    try:
        response = await ai_service.analyze_content(request)
        return response
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/translate", response_model=AITranslationResponse)
async def translate_content(
    request: AITranslationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AITranslationResponse:
    """Translate content using AI."""
    try:
        response = await ai_service.translate_content(request)
        return response
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/summarize", response_model=AISummarizationResponse)
async def summarize_content(
    request: AISummarizationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AISummarizationResponse:
    """Summarize content using AI."""
    try:
        response = await ai_service.summarize_content(request)
        return response
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/improve", response_model=AIImprovementResponse)
async def improve_content(
    request: AIImprovementRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AIImprovementResponse:
    """Improve content using AI."""
    try:
        response = await ai_service.improve_content(request)
        return response
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch", response_model=AIBatchResponse)
async def process_batch(
    request: AIBatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AIBatchResponse:
    """Process multiple AI requests in batch."""
    try:
        response = await ai_service.process_batch(request)
        return response
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/documents/generate", response_model=AIDocumentGenerationResponse)
async def generate_document(
    request: AIDocumentGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AIDocumentGenerationResponse:
    """Generate a complete document using AI."""
    try:
        # Generate content using AI
        ai_response = await ai_service.generate_content(request.ai_settings)
        
        # Create document
        document_data = {
            "title": request.title,
            "description": request.description,
            "content": ai_response.content,
            "document_type": request.document_type,
            "organization_id": request.organization_id,
            "owner_id": current_user.id,
            "template_id": request.template_id,
            "metadata": {
                "ai_generated": True,
                "ai_provider": ai_response.provider.value,
                "ai_model": ai_response.model.value,
                "generation_context": request.context,
                "variables": request.variables
            }
        }
        
        document = await document_service.create_document(db, document_data, current_user.id)
        
        # Calculate quality score (simplified)
        quality_score = 0.8  # Could be calculated based on AI response quality
        
        return AIDocumentGenerationResponse(
            document=document,
            generation=ai_response,
            processing_time=0.0,  # Could be calculated
            quality_score=quality_score
        )
    
    except AIProviderError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/providers/{provider}/status", response_model=AIProviderStatus)
async def get_provider_status(
    provider: AIProvider,
    current_user: User = Depends(get_current_user)
) -> AIProviderStatus:
    """Get status of AI provider."""
    try:
        status = await ai_service.get_provider_status(provider)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/providers/status", response_model=List[AIProviderStatus])
async def get_all_providers_status(
    current_user: User = Depends(get_current_user)
) -> List[AIProviderStatus]:
    """Get status of all AI providers."""
    try:
        statuses = []
        for provider in AIProvider:
            status = await ai_service.get_provider_status(provider)
            statuses.append(status)
        return statuses
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/models")
async def get_available_models(
    provider: AIProvider = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get available AI models."""
    try:
        models = {
            "openai": [
                {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Faster GPT-4"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient"}
            ],
            "anthropic": [
                {"id": "claude-3-opus", "name": "Claude 3 Opus", "description": "Most powerful Claude"},
                {"id": "claude-3-sonnet", "name": "Claude 3 Sonnet", "description": "Balanced performance"},
                {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "description": "Fast and efficient"}
            ],
            "deepseek": [
                {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "General purpose chat"},
                {"id": "deepseek-coder", "name": "DeepSeek Coder", "description": "Code generation"}
            ],
            "google": [
                {"id": "gemini-pro", "name": "Gemini Pro", "description": "Google's advanced model"},
                {"id": "gemini-pro-vision", "name": "Gemini Pro Vision", "description": "Multimodal model"}
            ]
        }
        
        if provider:
            return {provider.value: models.get(provider.value, [])}
        
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/usage/stats")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI usage statistics for current user."""
    try:
        # This would typically query the database for usage statistics
        # For now, returning mock data
        return {
            "total_requests": 150,
            "total_tokens": 50000,
            "total_cost": 25.50,
            "requests_today": 5,
            "tokens_today": 2000,
            "cost_today": 1.20,
            "by_provider": {
                "openai": {"requests": 100, "tokens": 35000, "cost": 18.00},
                "anthropic": {"requests": 30, "tokens": 10000, "cost": 5.50},
                "deepseek": {"requests": 20, "tokens": 5000, "cost": 2.00}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")




