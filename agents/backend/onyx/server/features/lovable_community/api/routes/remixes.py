"""
Rutas para operaciones de remixes

Incluye: remix_chat, get_remixes
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status

from ...dependencies import get_chat_service, get_user_id
from ...exceptions import InvalidChatError
from ...helpers import remix_to_response, remixes_to_responses
from ...schemas import RemixChatRequest, RemixResponse
from ...services import ChatService
from ..decorators import handle_errors

router = APIRouter()


@router.post(
    "/chats/{chat_id}/remix",
    response_model=RemixResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Remixar un chat",
    description="Crea un remix de un chat existente"
)
@handle_errors
async def remix_chat(
    chat_id: str,
    request: RemixChatRequest,
    user_id: str = Depends(get_user_id),
    service: ChatService = Depends(get_chat_service)
) -> RemixResponse:
    if request.original_chat_id != chat_id:
        raise InvalidChatError("Chat ID mismatch")
    
    remix_chat_obj, remix = service.remix_chat(
        original_chat_id=chat_id,
        user_id=user_id,
        title=request.title,
        chat_content=request.chat_content,
        description=request.description,
        tags=request.tags
    )
    
    return remix_to_response(remix)


@router.get(
    "/chats/{chat_id}/remixes",
    response_model=List[RemixResponse],
    summary="Obtener remixes",
    description="Obtiene todos los remixes de un chat"
)
@handle_errors
async def get_remixes(
    chat_id: str,
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    service: ChatService = Depends(get_chat_service)
) -> List[RemixResponse]:
    remixes = service.get_remixes(chat_id, limit)
    return remixes_to_responses(remixes)

