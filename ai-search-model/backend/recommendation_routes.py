"""
Recommendation Routes - Rutas de Recomendaciones
API endpoints para el sistema de recomendaciones
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from models.recommendation_engine import RecommendationEngine
from models.cache_system import CacheSystem
from models.notification_system import NotificationSystem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

# Instancias globales (se inicializarán en main.py)
recommendation_engine: Optional[RecommendationEngine] = None
cache_system: Optional[CacheSystem] = None
notification_system: Optional[NotificationSystem] = None

def get_recommendation_engine() -> RecommendationEngine:
    """Dependency para obtener el motor de recomendaciones"""
    if recommendation_engine is None:
        raise HTTPException(status_code=503, detail="Recommendation engine not initialized")
    return recommendation_engine

def get_cache_system() -> CacheSystem:
    """Dependency para obtener el sistema de cache"""
    if cache_system is None:
        raise HTTPException(status_code=503, detail="Cache system not initialized")
    return cache_system

def get_notification_system() -> NotificationSystem:
    """Dependency para obtener el sistema de notificaciones"""
    if notification_system is None:
        raise HTTPException(status_code=503, detail="Notification system not initialized")
    return notification_system

@router.post("/interaction")
async def add_search_interaction(
    user_id: str,
    query: str,
    results: List[Dict[str, Any]],
    clicked_docs: Optional[List[str]] = None,
    engine: RecommendationEngine = Depends(get_recommendation_engine),
    notifications: NotificationSystem = Depends(get_notification_system)
):
    """Agregar interacción de búsqueda del usuario"""
    try:
        await engine.add_search_interaction(user_id, query, results, clicked_docs)
        
        # Enviar notificación si hay documentos clickeados
        if clicked_docs:
            await notifications.send_recommendation_notification(
                user_id, len(clicked_docs)
            )
        
        return {
            "success": True,
            "message": "Interacción agregada exitosamente",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error agregando interacción: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    recommendation_type: str = Query("hybrid", regex="^(collaborative|content_based|trending|hybrid)$"),
    engine: RecommendationEngine = Depends(get_recommendation_engine),
    cache: CacheSystem = Depends(get_cache_system)
):
    """Obtener recomendaciones para un usuario"""
    try:
        # Crear clave de cache
        cache_key = f"recommendations:{user_id}:{recommendation_type}:{limit}"
        
        # Intentar obtener del cache
        cached_recommendations = await cache.get(cache_key)
        if cached_recommendations:
            return {
                "user_id": user_id,
                "recommendations": cached_recommendations,
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # Generar recomendaciones
        recommendations = await engine.get_recommendations(
            user_id, limit, recommendation_type
        )
        
        # Almacenar en cache por 30 minutos
        await cache.set(
            cache_key, 
            recommendations, 
            ttl=1800,
            tags=["recommendations", f"user:{user_id}"]
        )
        
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{document_id}")
async def get_similar_documents(
    document_id: str,
    limit: int = Query(5, ge=1, le=20),
    engine: RecommendationEngine = Depends(get_recommendation_engine),
    cache: CacheSystem = Depends(get_cache_system)
):
    """Obtener documentos similares a uno dado"""
    try:
        # Crear clave de cache
        cache_key = f"similar:{document_id}:{limit}"
        
        # Intentar obtener del cache
        cached_similar = await cache.get(cache_key)
        if cached_similar:
            return {
                "document_id": document_id,
                "similar_documents": cached_similar,
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # Obtener documentos similares
        similar_docs = await engine.get_similar_documents(document_id, limit)
        
        # Almacenar en cache por 1 hora
        await cache.set(
            cache_key,
            similar_docs,
            ttl=3600,
            tags=["similar", f"document:{document_id}"]
        )
        
        return {
            "document_id": document_id,
            "similar_documents": similar_docs,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo documentos similares: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending")
async def get_trending_content(
    time_range: str = Query("7d", regex="^(1d|7d|30d)$"),
    limit: int = Query(10, ge=1, le=50),
    engine: RecommendationEngine = Depends(get_recommendation_engine),
    cache: CacheSystem = Depends(get_cache_system)
):
    """Obtener contenido trending"""
    try:
        # Crear clave de cache
        cache_key = f"trending:{time_range}:{limit}"
        
        # Intentar obtener del cache
        cached_trending = await cache.get(cache_key)
        if cached_trending:
            return {
                "trending_content": cached_trending,
                "time_range": time_range,
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # Obtener contenido trending
        trending = await engine.get_trending_content(time_range, limit)
        
        # Almacenar en cache por 15 minutos
        await cache.set(
            cache_key,
            trending,
            ttl=900,
            tags=["trending", f"range:{time_range}"]
        )
        
        return {
            "trending_content": trending,
            "time_range": time_range,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo contenido trending: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=10),
    engine: RecommendationEngine = Depends(get_recommendation_engine),
    cache: CacheSystem = Depends(get_cache_system)
):
    """Obtener sugerencias de búsqueda"""
    try:
        # Crear clave de cache
        cache_key = f"suggestions:{query}:{limit}"
        
        # Intentar obtener del cache
        cached_suggestions = await cache.get(cache_key)
        if cached_suggestions:
            return {
                "query": query,
                "suggestions": cached_suggestions,
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # Obtener sugerencias
        suggestions = await engine.get_search_suggestions(query, limit)
        
        # Almacenar en cache por 1 hora
        await cache.set(
            cache_key,
            suggestions,
            ttl=3600,
            tags=["suggestions", f"query:{query}"]
        )
        
        return {
            "query": query,
            "suggestions": suggestions,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_recommendation_stats(
    engine: RecommendationEngine = Depends(get_recommendation_engine),
    cache: CacheSystem = Depends(get_cache_system)
):
    """Obtener estadísticas del sistema de recomendaciones"""
    try:
        engine_stats = engine.get_recommendation_stats()
        cache_stats = cache.get_stats()
        
        return {
            "engine_stats": engine_stats,
            "cache_stats": cache_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user/{user_id}/feedback")
async def add_user_feedback(
    user_id: str,
    document_id: str,
    rating: float = Query(..., ge=0.0, le=5.0),
    feedback_type: str = Query("rating", regex="^(rating|like|dislike|view)$"),
    engine: RecommendationEngine = Depends(get_recommendation_engine),
    cache: CacheSystem = Depends(get_cache_system)
):
    """Agregar feedback del usuario sobre un documento"""
    try:
        # Actualizar perfil del usuario con el feedback
        if user_id not in engine.user_profiles:
            engine.user_profiles[user_id] = {
                "interests": {},
                "viewed_documents": set(),
                "document_ratings": {},
                "search_patterns": [],
                "created_at": datetime.now().isoformat()
            }
        
        user_profile = engine.user_profiles[user_id]
        
        # Actualizar rating del documento
        if feedback_type == "rating":
            user_profile["document_ratings"][document_id] = rating
        elif feedback_type == "like":
            user_profile["document_ratings"][document_id] = 5.0
        elif feedback_type == "dislike":
            user_profile["document_ratings"][document_id] = 1.0
        elif feedback_type == "view":
            user_profile["viewed_documents"].add(document_id)
            if document_id not in user_profile["document_ratings"]:
                user_profile["document_ratings"][document_id] = 3.0  # Rating neutral por defecto
        
        # Invalidar cache de recomendaciones para este usuario
        await cache.invalidate_pattern(f"recommendations:{user_id}:*")
        
        return {
            "success": True,
            "message": "Feedback agregado exitosamente",
            "user_id": user_id,
            "document_id": document_id,
            "rating": rating,
            "feedback_type": feedback_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error agregando feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache")
async def clear_recommendation_cache(
    cache: CacheSystem = Depends(get_cache_system)
):
    """Limpiar cache de recomendaciones"""
    try:
        # Eliminar solo entradas relacionadas con recomendaciones
        deleted_count = await cache.delete_by_tags(["recommendations", "similar", "trending", "suggestions"])
        
        return {
            "success": True,
            "message": f"Cache limpiado: {deleted_count} entradas eliminadas",
            "deleted_count": deleted_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error limpiando cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_recommendation_models(
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Entrenar modelos de recomendación"""
    try:
        # Guardar modelos actualizados
        await engine.save_models()
        
        return {
            "success": True,
            "message": "Modelos de recomendación entrenados y guardados",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error entrenando modelos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Obtener perfil del usuario"""
    try:
        if user_id not in engine.user_profiles:
            return {
                "user_id": user_id,
                "profile": None,
                "message": "Usuario no encontrado",
                "timestamp": datetime.now().isoformat()
            }
        
        user_profile = engine.user_profiles[user_id]
        
        # Convertir sets a listas para serialización JSON
        profile_data = {
            "user_id": user_id,
            "interests": user_profile.get("interests", {}),
            "viewed_documents_count": len(user_profile.get("viewed_documents", set())),
            "document_ratings_count": len(user_profile.get("document_ratings", {})),
            "search_patterns_count": len(user_profile.get("search_patterns", [])),
            "created_at": user_profile.get("created_at"),
            "top_interests": dict(list(user_profile.get("interests", {}).items())[:10]),
            "recent_searches": user_profile.get("search_patterns", [])[-10:]
        }
        
        return {
            "user_id": user_id,
            "profile": profile_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo perfil de usuario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


























