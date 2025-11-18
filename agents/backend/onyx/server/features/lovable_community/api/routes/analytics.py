"""
Rutas para analytics y perfiles

Incluye: get_analytics, get_user_profile
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from ...dependencies import get_chat_service
from ...schemas import AnalyticsResponse, UserProfileResponse
from ...services import ChatService
from ..cache import cache_response
from ..decorators import handle_errors, log_request, measure_time

router = APIRouter()


@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Obtener analytics de la comunidad",
    description="Obtiene estadísticas agregadas de toda la comunidad"
)
@cache_response(ttl=300.0)
@log_request
@measure_time
@handle_errors
async def get_analytics(
    period_days: Optional[int] = Query(None, ge=1, description="Número de días para filtrar (opcional)"),
    service: ChatService = Depends(get_chat_service)
) -> AnalyticsResponse:
    analytics = service.get_analytics(period_days)
    period_str = f"{period_days} days" if period_days else "all time"
    return AnalyticsResponse(
        **analytics,
        period=period_str
    )


@router.get(
    "/users/{user_id}/profile",
    response_model=UserProfileResponse,
    summary="Obtener perfil de usuario",
    description="Obtiene el perfil y estadísticas de un usuario"
)
@cache_response(ttl=120.0)
@log_request
@handle_errors
async def get_user_profile(
    user_id: str,
    service: ChatService = Depends(get_chat_service)
) -> UserProfileResponse:
    profile = service.get_user_profile(user_id)
    return UserProfileResponse(**profile)

