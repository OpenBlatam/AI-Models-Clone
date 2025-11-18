"""
Exceptions for Humanoid Devin Robot (Optimizado)
================================================

Excepciones personalizadas para el robot humanoide.
Incluye jerarquía de excepciones y mensajes de error informativos.
Soporta tanto uso directo como integración con FastAPI.
"""

try:
    from fastapi import HTTPException, status
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    HTTPException = Exception
    status = None


class HumanoidRobotError(Exception):
    """
    Excepción base para errores del robot humanoide.
    
    Esta es la excepción principal que deben capturar los usuarios del sistema.
    """
    pass


class RobotConnectionError(HumanoidRobotError):
    """Error al conectar o desconectar del robot."""
    pass


class RobotControlError(HumanoidRobotError):
    """Error al controlar el robot (movimiento, articulaciones, etc.)."""
    pass


class RobotConfigurationError(HumanoidRobotError):
    """Error en la configuración del robot."""
    pass


class RobotNotInitializedError(HumanoidRobotError):
    """Error cuando el robot no está inicializado."""
    pass


class InvalidCommandError(HumanoidRobotError):
    """Error cuando un comando es inválido."""
    pass


class MovementError(HumanoidRobotError):
    """Error durante el movimiento del robot."""
    pass


class ROS2IntegrationError(HumanoidRobotError):
    """Error en la integración con ROS 2."""
    pass


class MoveIt2Error(HumanoidRobotError):
    """Error en la integración con MoveIt 2."""
    pass


class Nav2Error(HumanoidRobotError):
    """Error en la integración con Nav2."""
    pass


class VisionError(HumanoidRobotError):
    """Error en el procesamiento de visión."""
    pass


class PointCloudError(HumanoidRobotError):
    """Error en el procesamiento de nubes de puntos."""
    pass


class AIModelError(HumanoidRobotError):
    """Error en modelos de IA (TensorFlow, PyTorch)."""
    pass


class ModelError(AIModelError):
    """Alias para compatibilidad con código existente."""
    pass


class PoppyError(HumanoidRobotError):
    """Error en la integración con robot Poppy."""
    pass


class ICubError(HumanoidRobotError):
    """Error en la integración con robot iCub."""
    pass


class TrajectoryError(HumanoidRobotError):
    """Error en la generación o ejecución de trayectorias."""
    pass


class ValidationError(HumanoidRobotError):
    """Error de validación de parámetros."""
    pass


# Clases compatibles con FastAPI (si está disponible)
if FASTAPI_AVAILABLE:
    class HTTPRobotConnectionError(RobotConnectionError, HTTPException):
        """Error de conexión con el robot (compatible con FastAPI)."""
        
        def __init__(self, detail: str = "Failed to connect to robot"):
            super().__init__(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=detail
            )
    
    class HTTPRobotNotInitializedError(RobotNotInitializedError, HTTPException):
        """Error cuando el robot no está inicializado (compatible con FastAPI)."""
        
        def __init__(self, detail: str = "Robot not initialized"):
            super().__init__(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=detail
            )
    
    class HTTPInvalidCommandError(InvalidCommandError, HTTPException):
        """Error cuando un comando es inválido (compatible con FastAPI)."""
        
        def __init__(self, detail: str = "Invalid command"):
            super().__init__(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )
    
    class HTTPMovementError(MovementError, HTTPException):
        """Error durante el movimiento del robot (compatible con FastAPI)."""
        
        def __init__(self, detail: str = "Movement failed"):
            super().__init__(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail
            )
    
    class HTTPModelError(AIModelError, HTTPException):
        """Error relacionado con modelos de IA (compatible con FastAPI)."""
        
        def __init__(self, detail: str = "Model error"):
            super().__init__(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail
            )
    
    class HTTPVisionError(VisionError, HTTPException):
        """Error en procesamiento de visión (compatible con FastAPI)."""
        
        def __init__(self, detail: str = "Vision processing error"):
            super().__init__(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail
            )

