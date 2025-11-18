"""
Dependencies para FastAPI (refactorizado y mejorado)

Incluye dependencias para base de datos, autenticación, y servicios.
Usa Factory Pattern para crear servicios con Dependency Injection.
Mejorado con type hints completos y logging estructurado.
"""

from typing import Generator, Optional, Annotated
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from .core import get_session_local
from .factories import ServiceFactory
from .services import ChatService
from .exceptions import ChatNotFoundError, InvalidChatError, DatabaseError
from .utils.logging_config import StructuredLogger

logger = StructuredLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos (modularizado).
    
    Yields:
        Session: Sesión de SQLAlchemy
        
    Raises:
        DatabaseError: Si hay error al crear la sesión
    """
    SessionLocal = get_session_local()
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        if db is not None:
            db.rollback()
        logger.exception(
            "Database session error",
            error=str(e),
            error_type=type(e).__name__
        )
        raise DatabaseError(f"Database session error: {str(e)}") from e
    finally:
        if db is not None:
            db.close()


def get_service_factory(
    db: Annotated[Session, Depends(get_db)]
) -> ServiceFactory:
    """
    Dependency para obtener ServiceFactory.
    
    Args:
        db: Sesión de base de datos (inyectada)
        
    Returns:
        ServiceFactory: Factory para crear servicios
    """
    return ServiceFactory(db)


def get_chat_service(
    factory: Annotated[ServiceFactory, Depends(get_service_factory)]
) -> ChatService:
    """
    Dependency para obtener ChatService (refactorizado).
    
    Usa Factory Pattern para crear el servicio con todas sus dependencias.
    El factory automáticamente usa la versión refactorizada si está disponible.
    
    Args:
        factory: ServiceFactory (inyectada)
        
    Returns:
        ChatService: Instancia del servicio con dependencias inyectadas
    """
    return factory.get_chat_service()


def get_user_id(request: Request) -> str:
    """
    Dependency para obtener user_id del request (optimizado).
    
    En producción, esto debería extraer el user_id de un token JWT.
    
    Args:
        request: Request object (inyectado automáticamente por FastAPI)
        
    Returns:
        str: ID del usuario
        
    Raises:
        HTTPException: Si no se puede obtener el user_id y está en modo producción
    """
    # Intentar obtener de header
    user_id: Optional[str] = request.headers.get("X-User-ID")
    if user_id:
        return user_id.strip()
    
    # Intentar obtener de query params
    user_id = request.query_params.get("user_id")
    if user_id:
        return user_id.strip()
    
    # Fallback para desarrollo (en producción debería requerir autenticación)
    from .config import settings
    if not settings.debug:
        logger.warning(
            "No user_id found in request",
            path=request.url.path,
            method=request.method
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    logger.warning(
        "No user_id found in request, using default",
        path=request.url.path,
        method=request.method
    )
    return "user_123"


def get_optional_user_id(request: Request) -> Optional[str]:
    """
    Dependency para obtener user_id opcional del request.
    
    Args:
        request: Request object (inyectado automáticamente por FastAPI)
        
    Returns:
        Optional[str]: ID del usuario o None
    """
    try:
        return get_user_id(request)
    except (HTTPException, Exception):
        return None

