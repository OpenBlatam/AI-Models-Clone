"""
Custom Exceptions
=================

Excepciones personalizadas para el sistema de routing.
"""


class RoutingError(Exception):
    """Excepción base para errores de routing."""
    pass


class RouteNotFoundError(RoutingError):
    """Error cuando no se encuentra una ruta."""
    pass


class InvalidNodeError(RoutingError):
    """Error cuando un nodo es inválido."""
    pass


class InvalidStrategyError(RoutingError):
    """Error cuando una estrategia es inválida."""
    pass


class ModelError(Exception):
    """Excepción base para errores de modelos."""
    pass


class ModelNotFoundError(ModelError):
    """Error cuando un modelo no se encuentra."""
    pass


class ModelLoadError(ModelError):
    """Error al cargar un modelo."""
    pass


class ModelInferenceError(ModelError):
    """Error durante inferencia."""
    pass


class TrainingError(Exception):
    """Excepción base para errores de entrenamiento."""
    pass


class ValidationError(Exception):
    """Error de validación."""
    pass


class ConfigurationError(Exception):
    """Error de configuración."""
    pass


class RobotMovementError(Exception):
    """Excepción base para errores de movimiento del robot."""
    pass


class TrajectoryError(RobotMovementError):
    """Error relacionado con trayectorias."""
    pass


class TrajectoryEmptyError(TrajectoryError):
    """Error cuando una trayectoria está vacía."""
    pass


class TrajectoryCollisionError(TrajectoryError):
    """Error cuando una trayectoria tiene colisiones."""
    pass


class TrajectoryInvalidError(TrajectoryError):
    """Error cuando una trayectoria es inválida."""
    pass


class IKError(RobotMovementError):
    """Error de cinemática inversa."""
    pass


class RobotConnectionError(RobotMovementError):
    """Error de conexión con el robot."""
    pass


class RobotNotConnectedError(RobotConnectionError):
    """Error cuando el robot no está conectado."""
    pass


class RobotMovementInProgressError(RobotMovementError):
    """Error cuando ya hay un movimiento en progreso."""
    pass


class AlgorithmNotFoundError(RoutingError):
    """Error cuando no se encuentra un algoritmo."""
    pass