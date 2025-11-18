"""
Métricas y estadísticas del sistema (optimizado)

Proporciona endpoints para monitorear el rendimiento y estado del sistema.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from ..dependencies import get_db
from ..models import PublishedChat, ChatVote, ChatRemix, ChatView
from ..config import settings
from .cache import get_cache_stats

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"]
)


@router.get(
    "",
    summary="Métricas del sistema",
    description="Obtiene métricas generales del sistema incluyendo cache, base de datos y estadísticas"
)
async def get_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Obtiene métricas del sistema (optimizado).
    
    Incluye:
    - Estadísticas de cache
    - Estadísticas de base de datos
    - Contadores de entidades
    - Información del sistema
    
    Returns:
        Diccionario con métricas del sistema
    """
    try:
        # Estadísticas de cache
        cache_stats = get_cache_stats()
        
        # Estadísticas de base de datos
        total_chats = db.query(func.count(PublishedChat.id)).scalar() or 0
        total_votes = db.query(func.count(ChatVote.id)).scalar() or 0
        total_remixes = db.query(func.count(ChatRemix.id)).scalar() or 0
        total_views = db.query(func.count(ChatView.id)).scalar() or 0
        
        # Chats públicos
        public_chats = db.query(func.count(PublishedChat.id)).filter(
            PublishedChat.is_public == True
        ).scalar() or 0
        
        # Chats destacados
        featured_chats = db.query(func.count(PublishedChat.id)).filter(
            PublishedChat.is_featured == True
        ).scalar() or 0
        
        # Usuarios únicos
        unique_users = db.query(func.count(func.distinct(PublishedChat.user_id))).scalar() or 0
        
        # Score promedio
        avg_score_result = db.query(func.avg(PublishedChat.score)).filter(
            PublishedChat.is_public == True
        ).scalar()
        avg_score = float(avg_score_result) if avg_score_result else 0.0
        
        # Verificar conexión de base de datos
        db_status = "connected"
        try:
            db.execute(text("SELECT 1"))
        except Exception:
            db_status = "disconnected"
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cache": cache_stats,
            "database": {
                "status": db_status,
                "stats": {
                    "total_chats": total_chats,
                    "public_chats": public_chats,
                    "featured_chats": featured_chats,
                    "total_votes": total_votes,
                    "total_remixes": total_remixes,
                    "total_views": total_views,
                    "unique_users": unique_users,
                    "average_score": round(avg_score, 2)
                }
            },
            "system": {
                "app_name": settings.app_name,
                "version": settings.app_version,
                "debug": settings.debug
            }
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}", exc_info=True)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "status": "error"
        }


@router.get(
    "/cache",
    summary="Estadísticas de cache",
    description="Obtiene estadísticas detalladas del sistema de cache"
)
async def get_cache_metrics() -> Dict[str, Any]:
    """
    Obtiene estadísticas del cache (optimizado).
    
    Returns:
        Diccionario con estadísticas de cache
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cache": get_cache_stats()
    }


@router.get(
    "/database",
    summary="Estadísticas de base de datos",
    description="Obtiene estadísticas detalladas de la base de datos"
)
async def get_database_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Obtiene estadísticas de la base de datos (optimizado).
    
    Returns:
        Diccionario con estadísticas de base de datos
    """
    try:
        # Contadores básicos
        total_chats = db.query(func.count(PublishedChat.id)).scalar() or 0
        total_votes = db.query(func.count(ChatVote.id)).scalar() or 0
        total_remixes = db.query(func.count(ChatRemix.id)).scalar() or 0
        total_views = db.query(func.count(ChatView.id)).scalar() or 0
        
        # Estadísticas agregadas
        public_chats = db.query(func.count(PublishedChat.id)).filter(
            PublishedChat.is_public == True
        ).scalar() or 0
        
        featured_chats = db.query(func.count(PublishedChat.id)).filter(
            PublishedChat.is_featured == True
        ).scalar() or 0
        
        unique_users = db.query(func.count(func.distinct(PublishedChat.user_id))).scalar() or 0
        
        # Score promedio
        avg_score_result = db.query(func.avg(PublishedChat.score)).filter(
            PublishedChat.is_public == True
        ).scalar()
        avg_score = float(avg_score_result) if avg_score_result else 0.0
        
        # Votos por tipo
        upvotes = db.query(func.count(ChatVote.id)).filter(
            ChatVote.vote_type == "upvote"
        ).scalar() or 0
        
        downvotes = db.query(func.count(ChatVote.id)).filter(
            ChatVote.vote_type == "downvote"
        ).scalar() or 0
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "counts": {
                "total_chats": total_chats,
                "public_chats": public_chats,
                "featured_chats": featured_chats,
                "total_votes": total_votes,
                "upvotes": upvotes,
                "downvotes": downvotes,
                "total_remixes": total_remixes,
                "total_views": total_views,
                "unique_users": unique_users
            },
            "averages": {
                "average_score": round(avg_score, 2)
            }
        }
    except Exception as e:
        logger.error(f"Error getting database metrics: {e}", exc_info=True)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "status": "error"
        }

