"""
Validadores reutilizables para endpoints (optimizado)

Incluye funciones de validación para IDs, parámetros, y más.
"""

from typing import Optional, List
from fastapi import HTTPException, status

from ..exceptions import ChatNotFoundError, InvalidChatError
from ..utils import validate_uuid_format, sanitize_string


def validate_chat_id(chat_id: str, raise_on_invalid: bool = True) -> Optional[str]:
    """
    Valida un chat ID.
    
    Args:
        chat_id: ID del chat a validar
        raise_on_invalid: Si debe lanzar excepción o retornar None
        
    Returns:
        Chat ID sanitizado o None
        
    Raises:
        InvalidChatError: Si el ID es inválido y raise_on_invalid=True
    """
    if not chat_id:
        if raise_on_invalid:
            raise InvalidChatError("Chat ID cannot be empty")
        return None
    
    chat_id = sanitize_string(chat_id)
    
    if not chat_id:
        if raise_on_invalid:
            raise InvalidChatError("Chat ID cannot be empty")
        return None
    
    return chat_id


def validate_user_id(user_id: str, raise_on_invalid: bool = True) -> Optional[str]:
    """
    Valida un user ID.
    
    Args:
        user_id: ID del usuario a validar
        raise_on_invalid: Si debe lanzar excepción o retornar None
        
    Returns:
        User ID sanitizado o None
        
    Raises:
        InvalidChatError: Si el ID es inválido y raise_on_invalid=True
    """
    if not user_id:
        if raise_on_invalid:
            raise InvalidChatError("User ID cannot be empty")
        return None
    
    user_id = sanitize_string(user_id)
    
    if not user_id:
        if raise_on_invalid:
            raise InvalidChatError("User ID cannot be empty")
        return None
    
    return user_id


def validate_vote_type(vote_type: str) -> str:
    """
    Valida un tipo de voto.
    
    Args:
        vote_type: Tipo de voto a validar
        
    Returns:
        Tipo de voto validado
        
    Raises:
        InvalidChatError: Si el tipo de voto es inválido
    """
    if not vote_type:
        raise InvalidChatError("Vote type cannot be empty")
    
    vote_type = vote_type.strip().lower()
    
    if vote_type not in ("upvote", "downvote"):
        raise InvalidChatError(f"Invalid vote type: {vote_type}. Must be 'upvote' or 'downvote'")
    
    return vote_type


def validate_period(period: str) -> str:
    """
    Valida un período de tiempo.
    
    Args:
        period: Período a validar (hour, day, week, month)
        
    Returns:
        Período validado
        
    Raises:
        InvalidChatError: Si el período es inválido
    """
    if not period:
        raise InvalidChatError("Period cannot be empty")
    
    period = period.strip().lower()
    
    valid_periods = ("hour", "day", "week", "month")
    if period not in valid_periods:
        raise InvalidChatError(f"Invalid period: {period}. Must be one of: {', '.join(valid_periods)}")
    
    return period


def validate_operation(operation: str) -> str:
    """
    Valida una operación en lote.
    
    Args:
        operation: Operación a validar
        
    Returns:
        Operación validada
        
    Raises:
        InvalidChatError: Si la operación es inválida
    """
    if not operation:
        raise InvalidChatError("Operation cannot be empty")
    
    operation = operation.strip().lower()
    
    valid_operations = ("delete", "feature", "unfeature", "make_public", "make_private")
    if operation not in valid_operations:
        raise InvalidChatError(
            f"Invalid operation: {operation}. "
            f"Must be one of: {', '.join(valid_operations)}"
        )
    
    return operation


def validate_chat_ids(chat_ids: List[str], max_count: int = 100) -> List[str]:
    """
    Valida una lista de chat IDs.
    
    Args:
        chat_ids: Lista de IDs a validar
        max_count: Número máximo de IDs permitidos
        
    Returns:
        Lista de IDs validados y sanitizados
        
    Raises:
        InvalidChatError: Si la lista es inválida
    """
    if not chat_ids:
        raise InvalidChatError("Chat IDs list cannot be empty")
    
    if len(chat_ids) > max_count:
        raise InvalidChatError(f"Maximum {max_count} chat IDs allowed")
    
    # Sanitizar y validar
    sanitized = []
    seen = set()
    
    for chat_id in chat_ids:
        if chat_id:
            chat_id_clean = sanitize_string(chat_id)
            if chat_id_clean and chat_id_clean not in seen:
                sanitized.append(chat_id_clean)
                seen.add(chat_id_clean)
    
    if not sanitized:
        raise InvalidChatError("No valid chat IDs provided")
    
    return sanitized


def validate_sort_by(sort_by: str) -> str:
    """
    Valida un campo de ordenamiento.
    
    Args:
        sort_by: Campo a validar
        
    Returns:
        Campo validado
        
    Raises:
        InvalidChatError: Si el campo es inválido
    """
    if not sort_by:
        return "score"  # Default
    
    sort_by = sort_by.strip().lower()
    
    valid_fields = ("score", "created_at", "vote_count", "remix_count")
    if sort_by not in valid_fields:
        raise InvalidChatError(
            f"Invalid sort field: {sort_by}. "
            f"Must be one of: {', '.join(valid_fields)}"
        )
    
    return sort_by


def validate_order(order: str) -> str:
    """
    Valida un orden (asc/desc).
    
    Args:
        order: Orden a validar
        
    Returns:
        Orden validado
        
    Raises:
        InvalidChatError: Si el orden es inválido
    """
    if not order:
        return "desc"  # Default
    
    order = order.strip().lower()
    
    if order not in ("asc", "desc"):
        raise InvalidChatError(f"Invalid order: {order}. Must be 'asc' or 'desc'")
    
    return order

