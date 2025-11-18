"""
Manejo centralizado de errores
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Manejo centralizado de errores"""
    
    @staticmethod
    def handle_generation_error(error: Exception, context: Optional[Dict] = None) -> HTTPException:
        """Maneja errores durante la generación"""
        error_msg = str(error)
        logger.error(f"Generation error: {error_msg}", extra=context)
        
        if "CUDA" in error_msg or "out of memory" in error_msg.lower():
            return HTTPException(
                status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                detail="GPU memory insufficient. Try using a smaller model or reducing duration."
            )
        
        if "model" in error_msg.lower() and "not found" in error_msg.lower():
            return HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model not available. Please check configuration."
            )
        
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating music: {error_msg}"
        )
    
    @staticmethod
    def handle_audio_processing_error(error: Exception, context: Optional[Dict] = None) -> HTTPException:
        """Maneja errores durante el procesamiento de audio"""
        error_msg = str(error)
        logger.error(f"Audio processing error: {error_msg}", extra=context)
        
        if "file not found" in error_msg.lower():
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found"
            )
        
        if "format" in error_msg.lower() or "codec" in error_msg.lower():
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported audio format"
            )
        
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio: {error_msg}"
        )
    
    @staticmethod
    def handle_validation_error(error: ValueError, context: Optional[Dict] = None) -> HTTPException:
        """Maneja errores de validación"""
        error_msg = str(error)
        logger.warning(f"Validation error: {error_msg}", extra=context)
        
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    @staticmethod
    def handle_cache_error(error: Exception, context: Optional[Dict] = None) -> Optional[Any]:
        """Maneja errores de caché de forma silenciosa"""
        error_msg = str(error)
        logger.warning(f"Cache error (non-critical): {error_msg}", extra=context)
        # Los errores de caché no deberían detener el proceso
        return None

