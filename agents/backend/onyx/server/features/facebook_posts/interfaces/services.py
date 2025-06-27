"""
🎯 Service Interfaces - Clean Architecture
==========================================

Interfaces para servicios de dominio y aplicación.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from ..models.facebook_models import (
    FacebookPostEntity, FacebookPostAnalysis, FacebookPostRequest,
    PostSpecification, FacebookPostContent
)


class ContentGeneratorInterface(ABC):
    """Interface para generación de contenido."""
    
    @abstractmethod
    async def generate_content(self, specification: PostSpecification) -> FacebookPostContent:
        """Generar contenido basado en especificación."""
        pass
    
    @abstractmethod
    async def generate_variations(self, base_content: FacebookPostContent, count: int = 3) -> List[FacebookPostContent]:
        """Generar variaciones de contenido."""
        pass
    
    @abstractmethod
    async def optimize_content(self, content: FacebookPostContent, target_metrics: Dict[str, float]) -> FacebookPostContent:
        """Optimizar contenido para métricas objetivo."""
        pass


class ContentAnalyzerInterface(ABC):
    """Interface para análisis de contenido."""
    
    @abstractmethod
    async def analyze_content(self, post: FacebookPostEntity) -> FacebookPostAnalysis:
        """Analizar contenido de post."""
        pass
    
    @abstractmethod
    async def predict_performance(self, content: FacebookPostContent) -> Dict[str, float]:
        """Predecir performance de contenido."""
        pass
    
    @abstractmethod
    async def get_optimization_suggestions(self, analysis: FacebookPostAnalysis) -> List[str]:
        """Obtener sugerencias de optimización."""
        pass


class LangChainServiceInterface(ABC):
    """Interface para servicio LangChain."""
    
    @abstractmethod
    async def generate_facebook_post(self, **kwargs) -> str:
        """Generar post con LangChain."""
        pass
    
    @abstractmethod
    async def analyze_facebook_post(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar post con LangChain."""
        pass
    
    @abstractmethod
    async def generate_hashtags(self, topic: str, keywords: List[str]) -> List[str]:
        """Generar hashtags relevantes."""
        pass


class NotificationServiceInterface(ABC):
    """Interface para servicio de notificaciones."""
    
    @abstractmethod
    async def notify_post_created(self, post: FacebookPostEntity) -> bool:
        """Notificar creación de post."""
        pass
    
    @abstractmethod
    async def notify_analysis_completed(self, post: FacebookPostEntity, analysis: FacebookPostAnalysis) -> bool:
        """Notificar análisis completado."""
        pass
    
    @abstractmethod
    async def notify_publication_ready(self, post: FacebookPostEntity) -> bool:
        """Notificar que post está listo para publicación."""
        pass 