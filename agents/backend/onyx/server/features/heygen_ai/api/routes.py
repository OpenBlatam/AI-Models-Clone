"""
API Routes for HeyGen AI equivalent.
FastAPI endpoints for video generation and management with LangChain integration.
"""

import asyncio
import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

from .models import *
from ..core import HeyGenAI
from ..config.settings import get_settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["heygen-ai"])

# Get settings
settings = get_settings()

# Initialize HeyGen AI system with OpenRouter API key
heygen_ai = HeyGenAI(openrouter_api_key=settings.openrouter_api_key)


# Dependency to get HeyGen AI instance
def get_heygen_ai() -> HeyGenAI:
    return heygen_ai


# Health Check
@router.get("/health", response_model=HealthResponse)
async def health_check(heygen: HeyGenAI = Depends(get_heygen_ai)):
    """Check system health including LangChain status."""
    try:
        components = heygen.health_check()
        langchain_status = heygen.get_langchain_status()
        overall_status = "healthy" if all(components.values()) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            components=components,
            version="1.0.0",
            uptime=0.0,  # Would calculate actual uptime
            metadata={
                "langchain_status": langchain_status
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


# LangChain Status
@router.get("/langchain/status")
async def get_langchain_status(heygen: HeyGenAI = Depends(get_heygen_ai)):
    """Get LangChain integration status."""
    try:
        return heygen.get_langchain_status()
    except Exception as e:
        logger.error(f"Failed to get LangChain status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get LangChain status")


# Advanced Workflows Status
@router.get("/workflows/available")
async def get_available_workflows(heygen: HeyGenAI = Depends(get_heygen_ai)):
    """Get list of available advanced workflows."""
    try:
        workflows = heygen.get_available_workflows()
        return {
            "available_workflows": workflows,
            "total_count": len(workflows),
            "langchain_required": True
        }
    except Exception as e:
        logger.error(f"Failed to get available workflows: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available workflows")


# Advanced Workflow Endpoints
@router.post("/workflows/educational-series")
async def create_educational_series(
    request: CreateEducationalSeriesRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Create an educational video series using advanced AI workflows."""
    try:
        result = await heygen.create_educational_series(
            topic=request.topic,
            series_length=request.series_length
        )
        
        return {
            "workflow_type": "educational_series",
            "status": "completed",
            "topic": request.topic,
            "series_length": request.series_length,
            "episodes": result.get("episodes", []),
            "series_metadata": result.get("series_metadata", {}),
            "created_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create educational series: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/marketing-campaign")
async def create_marketing_campaign(
    request: CreateMarketingCampaignRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Create a marketing campaign with multiple video variants."""
    try:
        result = await heygen.create_marketing_campaign(
            product_info=request.product_info,
            target_audience=request.target_audience
        )
        
        return {
            "workflow_type": "marketing_campaign",
            "status": "completed",
            "product_info": request.product_info,
            "target_audience": request.target_audience,
            "campaign_scripts": result.get("campaign_scripts", []),
            "brand_analysis": result.get("brand_analysis", {}),
            "audience_analysis": result.get("audience_analysis", {}),
            "created_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create marketing campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/product-demo")
async def create_product_demo(
    request: CreateProductDemoRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Create a product demonstration video with feature analysis."""
    try:
        result = await heygen.create_product_demo(
            product_info=request.product_info
        )
        
        return {
            "workflow_type": "product_demo",
            "status": "completed",
            "product_info": request.product_info,
            "demo_script": result.get("demo_script", ""),
            "product_analysis": result.get("product_analysis", {}),
            "feature_priority": result.get("feature_priority", []),
            "benefit_mapping": result.get("benefit_mapping", {}),
            "cta_variations": result.get("cta_variations", []),
            "created_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create product demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/news-summary")
async def create_news_summary(
    request: CreateNewsSummaryRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Create a news summary video with fact-checking and multi-language support."""
    try:
        result = await heygen.create_news_summary(
            news_topic=request.news_topic,
            target_languages=request.target_languages
        )
        
        return {
            "workflow_type": "news_summary",
            "status": "completed",
            "news_topic": request.news_topic,
            "video_script": result.get("video_script", ""),
            "summary": result.get("summary", ""),
            "translations": result.get("translations", {}),
            "news_research": result.get("news_research", {}),
            "fact_check_results": result.get("fact_check_results", {}),
            "created_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create news summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Video Generation Endpoints
@router.post("/videos/create", response_model=VideoResponse)
async def create_video(
    request: CreateVideoRequest,
    background_tasks: BackgroundTasks,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Create a new video with LangChain integration."""
    try:
        # Convert API request to core request
        core_request = heygen.VideoRequest(
            script=request.script,
            avatar_id=request.avatar_id,
            voice_id=request.voice_id,
            language=request.language.value,
            output_format=request.output_format.value,
            resolution=request.resolution.value,
            duration=request.duration,
            background=str(request.background) if request.background else None,
            custom_settings=request.custom_settings
        )
        
        # Generate video
        response = await heygen.create_video(core_request)
        
        # Convert core response to API response
        return VideoResponse(
            video_id=response.video_id,
            status=VideoStatus.COMPLETED if response.status == "completed" else VideoStatus.FAILED,
            output_url=response.output_url,
            duration=response.duration,
            file_size=response.file_size,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata=response.metadata,
            error_message=response.metadata.get("error") if response.status == "failed" else None
        )
        
    except Exception as e:
        logger.error(f"Failed to create video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/videos/batch", response_model=BatchVideoResponse)
async def batch_create_videos(
    request: BatchCreateVideoRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Create multiple videos in batch with LangChain integration."""
    try:
        # Convert API requests to core requests
        core_requests = []
        for video_request in request.videos:
            core_request = heygen.VideoRequest(
                script=video_request.script,
                avatar_id=video_request.avatar_id,
                voice_id=video_request.voice_id,
                language=video_request.language.value,
                output_format=video_request.output_format.value,
                resolution=video_request.resolution.value,
                duration=video_request.duration,
                background=str(video_request.background) if video_request.background else None,
                custom_settings=video_request.custom_settings
            )
            core_requests.append(core_request)
        
        # Generate videos in batch
        responses = await heygen.batch_create_videos(core_requests)
        
        # Convert responses
        video_responses = []
        completed_count = 0
        failed_count = 0
        
        for response in responses:
            if isinstance(response, Exception):
                failed_count += 1
                video_responses.append(VideoResponse(
                    video_id="unknown",
                    status=VideoStatus.FAILED,
                    error_message=str(response),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                ))
            else:
                if response.status == "completed":
                    completed_count += 1
                else:
                    failed_count += 1
                
                video_responses.append(VideoResponse(
                    video_id=response.video_id,
                    status=VideoStatus.COMPLETED if response.status == "completed" else VideoStatus.FAILED,
                    output_url=response.output_url,
                    duration=response.duration,
                    file_size=response.file_size,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    metadata=response.metadata,
                    error_message=response.metadata.get("error") if response.status == "failed" else None
                ))
        
        return BatchVideoResponse(
            batch_id=f"batch_{datetime.now().timestamp()}",
            videos=video_responses,
            total_count=len(video_responses),
            completed_count=completed_count,
            failed_count=failed_count
        )
        
    except Exception as e:
        logger.error(f"Failed to create batch videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str, heygen: HeyGenAI = Depends(get_heygen_ai)):
    """Get video information by ID."""
    try:
        # This would typically query a database
        # For now, return a placeholder response
        raise HTTPException(status_code=404, detail="Video not found")
        
    except Exception as e:
        logger.error(f"Failed to get video {video_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Script Generation Endpoints with LangChain
@router.post("/scripts/generate", response_model=ScriptResponse)
async def generate_script(
    request: GenerateScriptRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Generate a script using LangChain and OpenRouter."""
    try:
        script = await heygen.generate_script(
            topic=request.topic,
            language=request.language.value,
            style=request.style.value,
            duration=request.duration,
            context=request.additional_context or ""
        )
        
        return ScriptResponse(
            script_id=f"script_{datetime.now().timestamp()}",
            script=script,
            word_count=len(script.split()),
            estimated_duration=len(script.split()) / 150.0,  # Rough estimate
            language=request.language,
            style=request.style,
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to generate script: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scripts/optimize", response_model=ScriptResponse)
async def optimize_script(
    request: OptimizeScriptRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Optimize a script using LangChain."""
    try:
        optimized_script = await heygen.optimize_script(
            script=request.script,
            duration=request.duration,
            style=request.style.value,
            language=request.language.value
        )
        
        return ScriptResponse(
            script_id=f"optimized_{datetime.now().timestamp()}",
            script=optimized_script,
            word_count=len(optimized_script.split()),
            estimated_duration=len(optimized_script.split()) / 150.0,
            language=request.language,
            style=request.style,
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to optimize script: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scripts/analyze", response_model=ScriptAnalysisResponse)
async def analyze_script(
    request: AnalyzeScriptRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Analyze a script using LangChain."""
    try:
        analysis = await heygen.analyze_script(request.script)
        
        return ScriptAnalysisResponse(
            script_id=f"analysis_{datetime.now().timestamp()}",
            word_count=analysis["word_count"],
            estimated_duration=analysis["estimated_duration"],
            readability_score=analysis["readability_score"],
            sentiment=analysis["sentiment"],
            complexity=analysis["complexity"],
            suggestions=analysis["suggestions"]
        )
        
    except Exception as e:
        logger.error(f"Failed to analyze script: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scripts/translate", response_model=TranslationResponse)
async def translate_script(
    request: TranslateScriptRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Translate a script using LangChain."""
    try:
        translated_script = await heygen.translate_script(
            script=request.script,
            target_language=request.target_language.value,
            source_language=request.source_language.value,
            preserve_style=request.preserve_style
        )
        
        return TranslationResponse(
            translation_id=f"translation_{datetime.now().timestamp()}",
            original_script=request.script,
            translated_script=translated_script,
            source_language=request.source_language,
            target_language=request.target_language,
            word_count=len(translated_script.split()),
            confidence_score=0.95  # Placeholder
        )
        
    except Exception as e:
        logger.error(f"Failed to translate script: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# LangChain Agent Endpoints
@router.post("/langchain/chat")
async def chat_with_agent(
    request: ChatRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Chat with LangChain agent for complex workflows."""
    try:
        response = await heygen.chat_with_agent(request.message)
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "agent_used": "langchain_agent"
        }
        
    except Exception as e:
        logger.error(f"Failed to chat with agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Knowledge Base Endpoints
@router.post("/knowledge-base/create")
async def create_knowledge_base(
    request: CreateKnowledgeBaseRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Create a knowledge base using LangChain."""
    try:
        await heygen.create_knowledge_base(
            documents=request.documents,
            name=request.name
        )
        
        return {
            "status": "success",
            "message": f"Knowledge base '{request.name}' created successfully",
            "document_count": len(request.documents),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-base/search")
async def search_knowledge_base(
    request: SearchKnowledgeBaseRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Search knowledge base using LangChain."""
    try:
        results = await heygen.search_knowledge_base(
            query=request.query,
            name=request.name,
            k=request.max_results
        )
        
        return {
            "query": request.query,
            "results": results,
            "result_count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to search knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Voice Management Endpoints
@router.get("/voices", response_model=List[VoiceResponse])
async def get_voices(heygen: HeyGenAI = Depends(get_heygen_ai)):
    """Get list of available voices."""
    try:
        voices = await heygen.get_available_voices()
        
        voice_responses = []
        for voice in voices:
            voice_responses.append(VoiceResponse(
                voice_id=voice["id"],
                name=voice["name"],
                language=LanguageCode(voice["language"]),
                accent=voice["accent"],
                gender=voice["gender"],
                style=voice["style"],
                sample_rate=voice["sample_rate"],
                is_cloned=voice.get("is_cloned", False),
                characteristics=voice["characteristics"]
            ))
        
        return voice_responses
        
    except Exception as e:
        logger.error(f"Failed to get voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voices/clone", response_model=VoiceResponse)
async def clone_voice(
    request: CloneVoiceRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Clone a voice from audio samples."""
    try:
        voice_id = await heygen.voice_engine.clone_voice(
            audio_samples=[str(url) for url in request.audio_samples],
            voice_name=request.voice_name
        )
        
        voice = await heygen.get_voice(voice_id)
        
        return VoiceResponse(
            voice_id=voice["id"],
            name=voice["name"],
            language=LanguageCode(voice["language"]),
            accent=voice["accent"],
            gender=voice["gender"],
            style=voice["style"],
            sample_rate=voice["sample_rate"],
            is_cloned=True,
            characteristics=voice["characteristics"]
        )
        
    except Exception as e:
        logger.error(f"Failed to clone voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Avatar Management Endpoints
@router.get("/avatars", response_model=List[AvatarResponse])
async def get_avatars(heygen: HeyGenAI = Depends(get_heygen_ai)):
    """Get list of available avatars."""
    try:
        avatars = await heygen.get_available_avatars()
        
        avatar_responses = []
        for avatar in avatars:
            avatar_responses.append(AvatarResponse(
                avatar_id=avatar["id"],
                name=avatar["name"],
                gender=avatar["gender"],
                style=avatar["style"],
                age_range=avatar["age_range"],
                ethnicity=avatar["ethnicity"],
                image_url=f"https://example.com/avatars/{avatar['id']}.jpg",  # Placeholder
                is_custom=avatar.get("is_custom", False),
                model_config=avatar["model_config"]
            ))
        
        return avatar_responses
        
    except Exception as e:
        logger.error(f"Failed to get avatars: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/avatars/create", response_model=AvatarResponse)
async def create_avatar(
    request: CreateAvatarRequest,
    heygen: HeyGenAI = Depends(get_heygen_ai)
):
    """Create a custom avatar from an image."""
    try:
        avatar_id = await heygen.avatar_manager.create_custom_avatar(
            image_path=str(request.image_url),
            name=request.name,
            style=request.style.value
        )
        
        avatar = await heygen.get_avatar(avatar_id)
        
        return AvatarResponse(
            avatar_id=avatar["id"],
            name=avatar["name"],
            gender=avatar.get("gender", "unknown"),
            style=avatar["style"],
            age_range=avatar.get("age_range", "unknown"),
            ethnicity=avatar.get("ethnicity", "unknown"),
            image_url=request.image_url,
            is_custom=True,
            model_config=avatar["model_config"]
        )
        
    except Exception as e:
        logger.error(f"Failed to create avatar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handling
@router.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return ErrorResponse(
        error="Internal server error",
        error_code="INTERNAL_ERROR",
        details={"message": str(exc)},
        timestamp=datetime.now().isoformat()
    ) 