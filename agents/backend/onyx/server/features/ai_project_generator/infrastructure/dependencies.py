"""
Dependencies - Dependencies para inyección de dependencias
==========================================================

Dependencies para FastAPI que proporcionan instancias de servicios.
"""

from functools import lru_cache
from typing import Optional

from ..factories.service_factory import ServiceFactory
from ..factories.infrastructure_factory import InfrastructureFactory
from ..factories.repository_factory import RepositoryFactory
from ..services.project_service import ProjectService
from ..services.generation_service import GenerationService
from ..infrastructure.cache import CacheService, get_cache_service
from ..infrastructure.events import EventPublisher
from ..infrastructure.workers import WorkerService, get_worker_service
from ..core.project_generator import ProjectGenerator
from ..core.continuous_generator import ContinuousGenerator


# Cache de instancias
_cache_service: Optional[CacheService] = None
_worker_service: Optional[WorkerService] = None
_event_publisher: Optional[EventPublisher] = None
_project_generator: Optional[ProjectGenerator] = None
_continuous_generator: Optional[ContinuousGenerator] = None


def get_cache_service_dependency() -> CacheService:
    """Dependency para cache service"""
    global _cache_service
    if _cache_service is None:
        _cache_service = get_cache_service()
    return _cache_service


def get_worker_service_dependency() -> WorkerService:
    """Dependency para worker service"""
    global _worker_service
    if _worker_service is None:
        _worker_service = get_worker_service()
    return _worker_service


def get_event_publisher_dependency() -> EventPublisher:
    """Dependency para event publisher"""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher


def get_project_generator_dependency() -> Optional[ProjectGenerator]:
    """Dependency para project generator"""
    global _project_generator
    if _project_generator is None:
        # Lazy initialization
        try:
            from ..core.project_generator import ProjectGenerator
            _project_generator = ProjectGenerator()
        except Exception:
            pass
    return _project_generator


def get_continuous_generator_dependency() -> Optional[ContinuousGenerator]:
    """Dependency para continuous generator"""
    global _continuous_generator
    if _continuous_generator is None:
        # Lazy initialization
        try:
            from ..core.continuous_generator import ContinuousGenerator
            _continuous_generator = ContinuousGenerator()
        except Exception:
            pass
    return _continuous_generator


def get_project_service() -> ProjectService:
    """Dependency para project service - Usa factory para crear con dependencias"""
    return ServiceFactory.create_project_service(
        cache_service=get_cache_service_dependency(),
        event_publisher=get_event_publisher_dependency(),
        project_generator=get_project_generator_dependency(),
        continuous_generator=get_continuous_generator_dependency()
    )


def get_generation_service() -> GenerationService:
    """Dependency para generation service - Usa factory para crear con dependencias"""
    return ServiceFactory.create_generation_service(
        project_generator=get_project_generator_dependency(),
        worker_service=get_worker_service_dependency(),
        event_publisher=get_event_publisher_dependency(),
        cache_service=get_cache_service_dependency()
    )


def get_validation_service():
    """Dependency para validation service"""
    from ..services.validation_service import ValidationService
    return ValidationService()


def get_export_service():
    """Dependency para export service"""
    from ..services.export_service import ExportService
    return ExportService()


def get_deployment_service():
    """Dependency para deployment service"""
    from ..services.deployment_service import DeploymentService
    return DeploymentService()


def get_analytics_service():
    """Dependency para analytics service"""
    from ..services.analytics_service import AnalyticsService
    return AnalyticsService()

