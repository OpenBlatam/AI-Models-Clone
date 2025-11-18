"""
Rutas para operaciones en lote

Incluye: bulk_operation
"""

from fastapi import APIRouter, Depends

from ...dependencies import get_chat_service, get_user_id
from ...schemas import BulkOperationRequest, BulkOperationResponse
from ...services import ChatService
from ...validators import validate_chat_ids, validate_operation, validate_user_id
from ..cache import clear_response_cache
from ..decorators import handle_errors

router = APIRouter()


@router.post(
    "/bulk",
    response_model=BulkOperationResponse,
    summary="Operaciones en lote",
    description="Realiza una operación en lote sobre múltiples chats (máximo 100)"
)
@handle_errors
async def bulk_operation(
    request: BulkOperationRequest,
    user_id: str = Depends(get_user_id),
    service: ChatService = Depends(get_chat_service)
) -> BulkOperationResponse:
    operation = validate_operation(request.operation)
    chat_ids = validate_chat_ids(request.chat_ids, max_count=100)
    validated_user_id = validate_user_id(user_id) if operation == "delete" else None
    
    clear_response_cache()
    
    result = service.bulk_operation(
        chat_ids=chat_ids,
        operation=operation,
        user_id=validated_user_id
    )
    return BulkOperationResponse(**result)

