"""
AI-powered endpoints for Lovable Community

Endpoints for:
- Semantic search
- Sentiment analysis
- Content moderation
- Text generation
- Recommendations
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..services.ai import (
    EmbeddingService,
    SentimentService,
    ModerationService,
    TextGenerationService,
    RecommendationService
)
from ..services.chat import ChatService
from ..models import PublishedChat
from ..exceptions import ChatNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


def get_embedding_service(db: Session = Depends(get_db)) -> EmbeddingService:
    """Dependency for embedding service"""
    return EmbeddingService(db)


def get_sentiment_service(db: Session = Depends(get_db)) -> SentimentService:
    """Dependency for sentiment service"""
    return SentimentService(db)


def get_moderation_service(db: Session = Depends(get_db)) -> ModerationService:
    """Dependency for moderation service"""
    return ModerationService(db)


def get_text_generation_service() -> TextGenerationService:
    """Dependency for text generation service"""
    return TextGenerationService()


def get_recommendation_service(
    db: Session = Depends(get_db),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> RecommendationService:
    """Dependency for recommendation service"""
    return RecommendationService(db, embedding_service)


@router.post("/embeddings/{chat_id}")
async def create_embedding(
    chat_id: str,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    db: Session = Depends(get_db)
):
    """
    Create or update embedding for a chat
    
    This enables semantic search for the chat.
    """
    try:
        chat = db.query(PublishedChat).filter(PublishedChat.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")
        
        embedding = embedding_service.create_or_update_embedding(chat_id, chat=chat)
        
        return {
            "chat_id": chat_id,
            "embedding_id": embedding.id,
            "model": embedding.embedding_model,
            "dimension": len(embedding.embedding),
            "created_at": embedding.created_at
        }
    except Exception as e:
        logger.error(f"Error creating embedding: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/semantic")
async def semantic_search(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    min_similarity: float = Query(0.5, ge=0.0, le=1.0, description="Minimum similarity score"),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    """
    Semantic search using embeddings
    
    Find chats similar to the query text using semantic similarity.
    """
    try:
        results = embedding_service.find_similar_chats(
            query_text=query,
            limit=limit,
            min_similarity=min_similarity
        )
        
        return {
            "query": query,
            "results": [
                {
                    "chat_id": item["chat_id"],
                    "similarity": item["similarity"],
                    "title": item["chat"].title,
                    "description": item["chat"].description,
                    "score": item["chat"].score
                }
                for item in results
            ],
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error in semantic search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/{chat_id}")
async def analyze_sentiment(
    chat_id: str,
    sentiment_service: SentimentService = Depends(get_sentiment_service),
    db: Session = Depends(get_db)
):
    """
    Analyze sentiment of a chat
    
    Returns sentiment label (positive/negative/neutral) and confidence score.
    """
    try:
        chat = db.query(PublishedChat).filter(PublishedChat.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")
        
        metadata = sentiment_service.analyze_chat_sentiment(chat_id, chat=chat)
        
        return {
            "chat_id": chat_id,
            "sentiment": {
                "label": metadata.sentiment_label,
                "score": metadata.sentiment_score
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/analyze")
async def analyze_text_sentiment(
    text: str = Query(..., description="Text to analyze"),
    sentiment_service: SentimentService = Depends(get_sentiment_service)
):
    """
    Analyze sentiment of arbitrary text
    
    Useful for analyzing text before publishing.
    """
    try:
        result = sentiment_service.analyze_sentiment(text)
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "sentiment": {
                "label": result["label"],
                "score": result["score"]
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing text sentiment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/moderate/{chat_id}")
async def moderate_chat(
    chat_id: str,
    moderation_service: ModerationService = Depends(get_moderation_service),
    db: Session = Depends(get_db)
):
    """
    Moderate a chat for toxic or inappropriate content
    
    Returns moderation results including toxicity score and flags.
    """
    try:
        chat = db.query(PublishedChat).filter(PublishedChat.id == chat_id).first()
        if not chat:
            raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")
        
        metadata = moderation_service.moderate_chat(chat_id, chat=chat)
        
        return {
            "chat_id": chat_id,
            "moderation": {
                "is_toxic": metadata.is_toxic,
                "toxicity_score": metadata.toxicity_score,
                "flags": metadata.moderation_flags
            }
        }
    except Exception as e:
        logger.error(f"Error moderating chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/moderate/check")
async def check_content(
    text: str = Query(..., description="Text to check"),
    moderation_service: ModerationService = Depends(get_moderation_service)
):
    """
    Check text for toxicity before publishing
    
    Returns whether content should be blocked.
    """
    try:
        result = moderation_service.moderate_content(text)
        should_block = moderation_service.should_block_content(text)
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "is_toxic": result["is_toxic"],
            "toxicity_score": result["toxicity_score"],
            "should_block": should_block,
            "flags": result.get("flags", [])
        }
    except Exception as e:
        logger.error(f"Error checking content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_text(
    prompt: str = Query(..., description="Text prompt"),
    max_length: Optional[int] = Query(None, ge=10, le=500, description="Maximum length"),
    temperature: float = Query(0.7, ge=0.0, le=2.0, description="Sampling temperature"),
    text_generation_service: TextGenerationService = Depends(get_text_generation_service)
):
    """
    Generate text using LLM
    
    Useful for text completion, enhancement, or generation.
    """
    try:
        result = text_generation_service.generate_text(
            prompt=prompt,
            max_length=max_length,
            temperature=temperature
        )
        
        return {
            "prompt": prompt,
            "generated_text": result.get("generated_text", ""),
            "model": result.get("model", "unknown")
        }
    except Exception as e:
        logger.error(f"Error generating text: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance/description")
async def enhance_description(
    description: str = Query(..., description="Description to enhance"),
    text_generation_service: TextGenerationService = Depends(get_text_generation_service)
):
    """
    Enhance or embellish a chat description
    
    Improves the description while keeping the same meaning.
    """
    try:
        enhanced = text_generation_service.enhance_description(description)
        
        return {
            "original": description,
            "enhanced": enhanced
        }
    except Exception as e:
        logger.error(f"Error enhancing description: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/tags")
async def generate_tags(
    title: str = Query(..., description="Chat title"),
    description: Optional[str] = Query(None, description="Optional description"),
    text_generation_service: TextGenerationService = Depends(get_text_generation_service)
):
    """
    Generate relevant tags for a chat
    
    Uses AI to suggest tags based on title and description.
    """
    try:
        tags = text_generation_service.generate_tags(title, description)
        
        return {
            "title": title,
            "description": description,
            "suggested_tags": tags
        }
    except Exception as e:
        logger.error(f"Error generating tags: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend/{chat_id}")
async def recommend_similar(
    chat_id: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum recommendations"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get recommendations for chats similar to the given chat
    
    Uses semantic similarity based on embeddings.
    """
    try:
        recommendations = recommendation_service.recommend_similar_chats(
            chat_id=chat_id,
            limit=limit
        )
        
        return {
            "chat_id": chat_id,
            "recommendations": [
                {
                    "chat_id": rec["chat_id"],
                    "similarity": rec["similarity"],
                    "title": rec["chat"].title,
                    "description": rec["chat"].description,
                    "score": rec["chat"].score
                }
                for rec in recommendations
            ],
            "count": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend/user/{user_id}")
async def recommend_for_user(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum recommendations"),
    use_sentiment: bool = Query(True, description="Use sentiment preferences"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get personalized recommendations for a user
    
    Based on user's voting history and preferences.
    """
    try:
        recommendations = recommendation_service.recommend_for_user(
            user_id=user_id,
            limit=limit,
            use_sentiment=use_sentiment
        )
        
        return {
            "user_id": user_id,
            "recommendations": [
                {
                    "chat_id": rec["chat_id"],
                    "similarity": rec.get("similarity", 0.0),
                    "title": rec["chat"].title,
                    "description": rec["chat"].description,
                    "score": rec["chat"].score,
                    "sentiment_match": rec.get("sentiment_match", False)
                }
                for rec in recommendations
            ],
            "count": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Error getting user recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend/tags")
async def recommend_by_tags(
    tags: List[str] = Query(..., description="Tags to search for"),
    limit: int = Query(10, ge=1, le=50, description="Maximum recommendations"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get recommendations based on tags
    
    Returns chats matching the provided tags, ordered by score.
    """
    try:
        chats = recommendation_service.recommend_by_tags(tags, limit=limit)
        
        return {
            "tags": tags,
            "recommendations": [
                {
                    "chat_id": chat.id,
                    "title": chat.title,
                    "description": chat.description,
                    "score": chat.score,
                    "tags": chat.tags
                }
                for chat in chats
            ],
            "count": len(chats)
        }
    except Exception as e:
        logger.error(f"Error getting tag recommendations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))










