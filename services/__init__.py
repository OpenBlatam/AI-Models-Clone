"""
ONYX BLOG POST - Services Module
===============================

Servicios principales del sistema de blog posts.
Orquesta OpenRouter, LangChain y la integración con Onyx.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime

from ..models import (
    BlogPostRequest, BlogPostResponse, BlogPostStructure, SEOMetadata,
    BlogPostStatus, OnyxIntegration, BlogPostMetrics, BlogPostType
)
from ..openrouter_client import OpenRouterClient, OpenRouterModelManager, create_openrouter_client
from ..langchain_integration import LangChainOrchestrator, create_langchain_orchestrator
from ..config import BlogPostConfiguration, get_config
from ..utils import (
    TextAnalyzer, ContentValidator, JSONParser, HashUtils, MetricsCollector,
    timing_decorator, retry_decorator, ValidationError, ParsingError
)

logger = logging.getLogger(__name__)

class BlogPostServiceError(Exception):
    """Error del servicio de blog posts"""
    pass

class OnyxIntegrationService:
    """Servicio de integración con Onyx"""
    
    def __init__(self, config: BlogPostConfiguration):
        self.config = config
        self.onyx_config = config.onyx_integration
        
    async def validate_user_access(self, user_id: str) -> bool:
        """Validar acceso del usuario"""
        if not self.onyx_config.require_user_authentication:
            return True
        
        # TODO: Implementar validación real con Onyx
        logger.debug(f"Validating user access for {user_id}")
        return True
    
    async def check_user_quota(self, user_id: str) -> bool:
        """Verificar quota del usuario"""
        if not self.onyx_config.enable_user_quotas:
            return True
        
        # TODO: Implementar verificación de quota con Onyx
        logger.debug(f"Checking quota for user {user_id}")
        return True
    
    async def save_blog_post(
        self,
        request: BlogPostRequest,
        response: BlogPostResponse,
        onyx_integration: Optional[OnyxIntegration] = None
    ) -> bool:
        """Guardar blog post en Onyx"""
        if not self.onyx_config.store_blog_posts:
            return True
        
        try:
            # TODO: Implementar guardado real en Onyx
            logger.info(f"Saving blog post {response.request_id} to Onyx")
            
            # Aquí se integraría con la base de datos de Onyx
            # await onyx_db.save_blog_post(...)
            
            return True
        except Exception as e:
            logger.error(f"Error saving blog post to Onyx: {e}")
            return False
    
    async def create_document_set(self, name: str, description: str) -> Optional[str]:
        """Crear document set en Onyx"""
        if not self.onyx_config.auto_create_document_sets:
            return None
        
        try:
            # TODO: Implementar creación de document set en Onyx
            logger.info(f"Creating document set '{name}' in Onyx")
            return f"doc_set_{int(time.time())}"
        except Exception as e:
            logger.error(f"Error creating document set: {e}")
            return None

class BlogPostGenerationService:
    """Servicio de generación de blog posts"""
    
    def __init__(
        self,
        openrouter_client: OpenRouterClient,
        langchain_orchestrator: LangChainOrchestrator,
        config: BlogPostConfiguration
    ):
        self.openrouter = openrouter_client
        self.langchain = langchain_orchestrator
        self.config = config
        self.metrics = MetricsCollector()
        
    @timing_decorator
    @retry_decorator(max_retries=2)
    async def generate_blog_post(
        self,
        request: BlogPostRequest,
        use_langchain: bool = True
    ) -> BlogPostResponse:
        """Generar blog post completo"""
        start_time = time.time()
        
        try:
            # Validar request
            self._validate_request(request)
            
            # Generar contenido usando LangChain
            generation_result = await self.langchain.generate_complete_blog_post(
                request=request,
                include_seo=request.include_seo,
                improve_content=False  # Por ahora
            )
            
            # Parsear resultado
            blog_structure = self._parse_blog_content(generation_result["main_content"])
            seo_metadata = self._parse_seo_metadata(generation_result.get("seo_metadata"))
            
            # Analizar métricas del texto
            full_text = JSONParser.extract_text_from_blog_post(blog_structure.to_dict())
            text_metrics = TextAnalyzer.analyze_text(full_text, request.keywords)
            
            # Calcular quality score
            quality_score = self._calculate_quality_score(blog_structure, text_metrics, request)
            
            # Crear response
            generation_time = (time.time() - start_time) * 1000
            
            response = BlogPostResponse(
                request_id=request.request_id,
                blog_post=blog_structure,
                seo_metadata=seo_metadata,
                word_count=text_metrics.word_count,
                character_count=text_metrics.character_count,
                reading_time_minutes=text_metrics.reading_time_minutes,
                status=BlogPostStatus.COMPLETED,
                model_used=generation_result["model_used"],
                generation_time_ms=generation_time,
                tokens_used=generation_result["total_tokens"],
                cost_usd=generation_result.get("total_cost", 0.0),
                quality_score=quality_score
            )
            
            # Registrar métricas
            self.metrics.record_request(
                request_id=request.request_id,
                blog_type=request.blog_type.value,
                generation_time=generation_time,
                word_count=text_metrics.word_count,
                cost=response.cost_usd,
                success=True
            )
            
            logger.info(f"Blog post generated successfully: {request.request_id} ({text_metrics.word_count} words)")
            return response
            
        except Exception as e:
            generation_time = (time.time() - start_time) * 1000
            
            # Registrar error
            self.metrics.record_error(type(e).__name__, str(e))
            
            # Crear response de error
            error_response = BlogPostResponse(
                request_id=request.request_id,
                blog_post=BlogPostStructure(),
                status=BlogPostStatus.FAILED,
                generation_time_ms=generation_time,
                onyx_metadata={"error": str(e)}
            )
            
            logger.error(f"Blog post generation failed: {request.request_id} - {e}")
            return error_response
    
    def _validate_request(self, request: BlogPostRequest):
        """Validar request de blog post"""
        ContentValidator.validate_topic(request.topic)
        ContentValidator.validate_keywords(request.keywords)
        
        # Validar configuración
        if not self.config.openrouter.api_key:
            raise ValidationError("OpenRouter API key not configured")
    
    def _parse_blog_content(self, content: str) -> BlogPostStructure:
        """Parsear contenido del blog post"""
        try:
            blog_data = JSONParser.parse_blog_post_json(content)
            
            return BlogPostStructure(
                title=blog_data.get("title", ""),
                introduction=blog_data.get("introduction", ""),
                main_sections=blog_data.get("main_sections", []),
                conclusion=blog_data.get("conclusion", ""),
                call_to_action=blog_data.get("call_to_action", "")
            )
        except ParsingError as e:
            logger.error(f"Error parsing blog content: {e}")
            # Fallback: crear estructura básica
            return BlogPostStructure(
                title="Error en generación",
                introduction="El contenido no pudo ser generado correctamente.",
                main_sections=[],
                conclusion="Por favor, intente nuevamente.",
                call_to_action=""
            )
    
    def _parse_seo_metadata(self, seo_content: Optional[str]) -> Optional[SEOMetadata]:
        """Parsear metadata SEO"""
        if not seo_content:
            return None
        
        try:
            seo_data = JSONParser.parse_seo_metadata_json(seo_content)
            
            return SEOMetadata(
                meta_title=seo_data.get("meta_title", ""),
                meta_description=seo_data.get("meta_description", ""),
                keywords=seo_data.get("keywords", []),
                og_title=seo_data.get("og_title", ""),
                og_description=seo_data.get("og_description", ""),
                og_image=seo_data.get("og_image", ""),
                canonical_url=seo_data.get("canonical_url", ""),
                schema_markup=seo_data.get("schema_markup", {})
            )
        except ParsingError as e:
            logger.warning(f"Error parsing SEO metadata: {e}")
            return None
    
    def _calculate_quality_score(
        self,
        blog_structure: BlogPostStructure,
        text_metrics: TextMetrics,
        request: BlogPostRequest
    ) -> float:
        """Calcular score de calidad del blog post"""
        score = 0.0
        max_score = 10.0
        
        # 1. Completitud de estructura (2.5 puntos)
        structure_score = 0.0
        if blog_structure.title:
            structure_score += 0.5
        if blog_structure.introduction:
            structure_score += 0.5
        if blog_structure.main_sections and len(blog_structure.main_sections) > 0:
            structure_score += 1.0
        if blog_structure.conclusion:
            structure_score += 0.3
        if blog_structure.call_to_action:
            structure_score += 0.2
        
        score += structure_score
        
        # 2. Longitud apropiada (2.5 puntos)
        target_min = request.length.min_words
        target_max = request.length.max_words
        actual_words = text_metrics.word_count
        
        if target_min <= actual_words <= target_max:
            length_score = 2.5
        elif actual_words < target_min:
            ratio = actual_words / target_min
            length_score = 2.5 * ratio
        else:  # actual_words > target_max
            ratio = target_max / actual_words
            length_score = 2.5 * ratio
        
        score += length_score
        
        # 3. Legibilidad (2.0 puntos)
        readability_score = min(2.0, text_metrics.readability_score / 5.0 * 2.0)
        score += readability_score
        
        # 4. Densidad de keywords (2.0 puntos)
        keyword_score = 0.0
        if request.keywords and text_metrics.keyword_density:
            densities = list(text_metrics.keyword_density.values())
            if densities:
                avg_density = sum(densities) / len(densities)
                # Densidad ideal: 1-3%
                if 1.0 <= avg_density <= 3.0:
                    keyword_score = 2.0
                elif avg_density < 1.0:
                    keyword_score = avg_density
                else:  # > 3.0
                    keyword_score = max(0.0, 2.0 - (avg_density - 3.0) * 0.2)
        
        score += keyword_score
        
        # 5. Número de secciones apropiado (1.0 punto)
        sections_count = len(blog_structure.main_sections)
        if 3 <= sections_count <= 7:
            sections_score = 1.0
        elif sections_count < 3:
            sections_score = sections_count / 3.0
        else:  # > 7
            sections_score = max(0.0, 1.0 - (sections_count - 7) * 0.1)
        
        score += sections_score
        
        return min(max_score, score)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del servicio"""
        return self.metrics.get_summary()

class BlogPostMainService:
    """Servicio principal del sistema de blog posts"""
    
    def __init__(self, config: Optional[BlogPostConfiguration] = None):
        self.config = config or get_config()
        
        # Inicializar clientes
        self.openrouter_client = create_openrouter_client(
            api_key=self.config.openrouter.api_key,
            app_name=self.config.openrouter.app_name,
            requests_per_minute=self.config.openrouter.requests_per_minute,
            tokens_per_minute=self.config.openrouter.tokens_per_minute,
            default_model=self.config.openrouter.default_model
        )
        
        self.langchain_orchestrator = create_langchain_orchestrator(self.openrouter_client)
        
        # Servicios especializados
        self.generation_service = BlogPostGenerationService(
            self.openrouter_client,
            self.langchain_orchestrator,
            self.config
        )
        
        self.onyx_service = OnyxIntegrationService(self.config)
        
        # Cache simple
        self.cache: Dict[str, BlogPostResponse] = {}
        
        # Métricas globales
        self.global_metrics = BlogPostMetrics()
        
        logger.info("BlogPostMainService initialized successfully")
    
    async def generate_blog_post(
        self,
        request: BlogPostRequest,
        onyx_integration: Optional[OnyxIntegration] = None
    ) -> BlogPostResponse:
        """Generar blog post con integración completa"""
        
        # 1. Validar acceso si hay integración Onyx
        if onyx_integration and onyx_integration.user_id:
            user_valid = await self.onyx_service.validate_user_access(onyx_integration.user_id)
            if not user_valid:
                raise BlogPostServiceError("User access denied")
            
            quota_ok = await self.onyx_service.check_user_quota(onyx_integration.user_id)
            if not quota_ok:
                raise BlogPostServiceError("User quota exceeded")
        
        # 2. Verificar cache
        if self.config.cache.enable_cache:
            cache_key = self._generate_cache_key(request)
            if cache_key in self.cache:
                cached_response = self.cache[cache_key]
                logger.info(f"Returning cached blog post: {request.request_id}")
                return cached_response
        
        # 3. Generar blog post
        response = await self.generation_service.generate_blog_post(request)
        
        # 4. Agregar metadata de Onyx
        if onyx_integration:
            response.onyx_metadata.update(onyx_integration.to_dict())
        
        # 5. Guardar en Onyx si está configurado
        if self.config.onyx_integration.store_blog_posts:
            await self.onyx_service.save_blog_post(request, response, onyx_integration)
        
        # 6. Guardar en cache
        if self.config.cache.enable_cache and response.status == BlogPostStatus.COMPLETED:
            cache_key = self._generate_cache_key(request)
            self.cache[cache_key] = response
            
            # Limitar tamaño de cache
            if len(self.cache) > self.config.cache.max_cache_size:
                # Remover entrada más antigua (implementación simple)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
        
        # 7. Actualizar métricas globales
        self.global_metrics.update_metrics(response)
        
        return response
    
    def _generate_cache_key(self, request: BlogPostRequest) -> str:
        """Generar clave de cache para el request"""
        return HashUtils.generate_request_hash(
            topic=request.topic,
            blog_type=request.blog_type.value,
            tone=request.tone.value,
            length=request.length.display_name,
            keywords=request.keywords
        )
    
    async def generate_batch_blog_posts(
        self,
        requests: List[BlogPostRequest],
        max_concurrency: int = 5
    ) -> List[BlogPostResponse]:
        """Generar múltiples blog posts en batch"""
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def generate_one(req):
            async with semaphore:
                return await self.generate_blog_post(req)
        
        tasks = [generate_one(req) for req in requests]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convertir excepciones a responses de error
        result = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                error_response = BlogPostResponse(
                    request_id=requests[i].request_id,
                    blog_post=BlogPostStructure(),
                    status=BlogPostStatus.FAILED,
                    onyx_metadata={"error": str(response)}
                )
                result.append(error_response)
            else:
                result.append(response)
        
        return result
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar salud del sistema"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Verificar OpenRouter
        try:
            openrouter_ok = await self.openrouter_client.test_connection()
            health["components"]["openrouter"] = {
                "status": "healthy" if openrouter_ok else "unhealthy",
                "metrics": self.openrouter_client.get_metrics()
            }
        except Exception as e:
            health["components"]["openrouter"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Verificar configuración
        config_errors = self.config.validate_config()
        health["components"]["configuration"] = {
            "status": "healthy" if not config_errors else "unhealthy",
            "errors": config_errors
        }
        
        # Métricas generales
        health["metrics"] = {
            "global": self.global_metrics.__dict__,
            "generation_service": self.generation_service.get_metrics()
        }
        
        # Estado general
        unhealthy_components = [
            comp for comp in health["components"].values()
            if comp["status"] == "unhealthy"
        ]
        
        if unhealthy_components:
            health["status"] = "unhealthy"
        
        return health
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas completas del sistema"""
        return {
            "global_metrics": self.global_metrics.__dict__,
            "generation_metrics": self.generation_service.get_metrics(),
            "openrouter_metrics": self.openrouter_client.get_metrics(),
            "cache_metrics": {
                "size": len(self.cache),
                "max_size": self.config.cache.max_cache_size,
                "enabled": self.config.cache.enable_cache
            },
            "config_summary": self.config.to_dict()
        }
    
    async def close(self):
        """Cerrar servicios y limpiar recursos"""
        await self.openrouter_client.close()
        self.cache.clear()
        logger.info("BlogPostMainService closed")

# Factory function
async def create_blog_post_service(
    config: Optional[BlogPostConfiguration] = None
) -> BlogPostMainService:
    """Factory para crear servicio de blog posts"""
    service = BlogPostMainService(config)
    
    # Verificar conexión inicial
    health = await service.health_check()
    if health["status"] == "unhealthy":
        logger.warning("Blog post service started with health issues")
    
    return service

__all__ = [
    'BlogPostServiceError',
    'OnyxIntegrationService',
    'BlogPostGenerationService',
    'BlogPostMainService',
    'create_blog_post_service',
] 