"""
🎯 APPLICATION USE CASES - Casos de Uso de la Aplicación
=======================================================

Use Cases que orquestan la lógica de dominio y coordinan
las operaciones del sistema.
"""

import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional, AsyncGenerator
import logging

from ..core.entities import AnalysisResult, TextFingerprint, ProcessingMetrics
from ..core.enums import AnalysisType, ProcessingTier, AnalysisStatus, ErrorType
from ..core.domain_services import AnalysisOrchestrator, TextProcessor, ScoreValidator
from ..interfaces.analyzers import IAnalyzerFactory
from ..interfaces.cache import ICacheRepository
from ..interfaces.metrics import IMetricsCollector, IStructuredLogger
from ..interfaces.config import IConfigurationService
from .dto import AnalysisRequest, AnalysisResponse, BatchAnalysisRequest


class AnalyzeTextUseCase:
    """Use Case principal para análisis de texto individual."""
    
    def __init__(
        self,
        analyzer_factory: IAnalyzerFactory,
        cache_repository: ICacheRepository,
        metrics_collector: IMetricsCollector,
        config_service: IConfigurationService,
        logger: Optional[IStructuredLogger] = None
    ):
        self._analyzer_factory = analyzer_factory
        self._cache_repository = cache_repository
        self._metrics_collector = metrics_collector
        self._config_service = config_service
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._text_processor = TextProcessor()
        self._score_validator = ScoreValidator()
        self._orchestrator = AnalysisOrchestrator()
    
    async def execute(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Ejecutar análisis de texto con orchestración completa.
        
        Args:
            request: AnalysisRequest con parámetros del análisis
            
        Returns:
            AnalysisResponse con resultados
        """
        start_time = time.time_ns()
        request_id = request.request_id or self._generate_request_id()
        
        # Log del request
        if hasattr(self._logger, 'log_analysis_request'):
            self._logger.log_analysis_request(
                request_id=request_id,
                text_length=len(request.text),
                analysis_types=[at.name for at in request.analysis_types],
                tier=request.processing_tier.value if request.processing_tier else "auto"
            )
        
        try:
            # Preprocesamiento del texto
            sanitized_text = self._text_processor.sanitize_text(request.text)
            fingerprint = TextFingerprint.create(sanitized_text)
            
            # Determinar tier óptimo si no se especificó
            processing_tier = request.processing_tier or self._orchestrator.determine_optimal_tier(
                text_length=len(sanitized_text),
                analysis_types=request.analysis_types
            )
            
            # Priorizar tipos de análisis
            prioritized_types = self._orchestrator.prioritize_analysis_types(
                request.analysis_types, 
                processing_tier
            )
            
            # Verificar cache si está habilitado
            cache_key = None
            if request.use_cache:
                cache_key = self._generate_cache_key(fingerprint, prioritized_types, processing_tier)
                cached_result = await self._try_get_from_cache(cache_key)
                
                if cached_result:
                    # Cache hit - preparar response
                    response = self._create_success_response(
                        request_id, cached_result, cache_hit=True
                    )
                    
                    # Log y métricas
                    duration_ms = (time.time_ns() - start_time) / 1_000_000
                    self._record_metrics(duration_ms, True, True)
                    self._log_response(request_id, True, duration_ms, True)
                    
                    return response
            
            # Crear resultado de análisis
            analysis_result = AnalysisResult(fingerprint=fingerprint)
            analysis_result.status = AnalysisStatus.PROCESSING
            
            # Ejecutar análisis
            await self._perform_analysis(
                analysis_result, 
                sanitized_text, 
                prioritized_types, 
                processing_tier
            )
            
            # Completar análisis
            end_time = time.time_ns()
            metrics = ProcessingMetrics(
                start_time_ns=start_time,
                end_time_ns=end_time,
                cache_hit=False,
                cache_level="computed",
                model_used=self._get_models_used(prioritized_types, processing_tier),
                tier=processing_tier
            )
            
            analysis_result.complete(metrics)
            
            # Guardar en cache si es válido
            if request.use_cache and cache_key and analysis_result.is_valid():
                await self._save_to_cache(cache_key, analysis_result)
            
            # Preparar response
            response = self._create_success_response(
                request_id, analysis_result, cache_hit=False
            )
            
            # Métricas y logging
            duration_ms = metrics.duration_ms
            self._record_metrics(duration_ms, True, False)
            self._log_response(request_id, True, duration_ms, False)
            
            return response
            
        except Exception as e:
            # Manejar errores
            error_msg = f"Analysis failed: {str(e)}"
            duration_ms = (time.time_ns() - start_time) / 1_000_000
            
            # Log error
            self._log_response(request_id, False, duration_ms, False, error_msg)
            self._record_metrics(duration_ms, False, False)
            
            return AnalysisResponse.error_response(
                request_id=request_id,
                errors=[error_msg],
                metadata={'duration_ms': duration_ms}
            )
    
    async def _perform_analysis(
        self,
        analysis_result: AnalysisResult,
        text: str,
        analysis_types: List[AnalysisType],
        processing_tier: ProcessingTier
    ) -> None:
        """Ejecutar análisis para todos los tipos solicitados."""
        
        # Crear tareas de análisis
        analysis_tasks = []
        
        for analysis_type in analysis_types:
            analyzer = self._analyzer_factory.create_analyzer(analysis_type, processing_tier)
            
            if analyzer:
                task = self._analyze_with_analyzer(analyzer, text, analysis_type)
                analysis_tasks.append(task)
            else:
                # No hay analizador disponible
                analysis_result.add_error(
                    ErrorType.PROCESSING_ERROR,
                    f"No analyzer available for {analysis_type.name} at tier {processing_tier.value}"
                )
        
        # Ejecutar análisis en paralelo
        if analysis_tasks:
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Procesar resultados
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    analysis_result.add_error(
                        ErrorType.PROCESSING_ERROR,
                        f"Analysis failed: {str(result)}"
                    )
                else:
                    analysis_type, score = result
                    
                    # Validar score usando domain service
                    if self._validate_score(score, analysis_type, len(text)):
                        analysis_result.add_score(
                            analysis_type,
                            score.value,
                            score.confidence,
                            score.method,
                            score.metadata
                        )
                    else:
                        analysis_result.add_error(
                            ErrorType.VALIDATION_ERROR,
                            f"Invalid score for {analysis_type.name}: {score.value}"
                        )
    
    async def _analyze_with_analyzer(self, analyzer, text: str, analysis_type: AnalysisType):
        """Ejecutar análisis con un analizador específico."""
        context = {
            'analysis_type': analysis_type,
            'text_length': len(text),
            'tier': analyzer.get_performance_tier().value
        }
        
        score = await analyzer.analyze(text, context)
        return analysis_type, score
    
    def _validate_score(self, score, analysis_type: AnalysisType, text_length: int) -> bool:
        """Validar score usando domain services."""
        if analysis_type == AnalysisType.SENTIMENT:
            return self._score_validator.validate_sentiment_score(score.value, score.method)
        elif analysis_type == AnalysisType.QUALITY_ASSESSMENT:
            return self._score_validator.validate_quality_score(score.value, text_length)
        else:
            return 0 <= score.value <= 100
    
    async def _try_get_from_cache(self, cache_key: str) -> Optional[AnalysisResult]:
        """Intentar obtener resultado del cache."""
        try:
            return await self._cache_repository.get(cache_key)
        except Exception as e:
            # Log error pero continúa sin cache
            if hasattr(self._logger, 'log_structured'):
                self._logger.log_structured('WARNING', f"Cache get failed: {e}")
            return None
    
    async def _save_to_cache(self, cache_key: str, result: AnalysisResult) -> None:
        """Guardar resultado en cache."""
        try:
            ttl = self._get_cache_ttl(result.metrics.tier if result.metrics else ProcessingTier.BALANCED)
            await self._cache_repository.set(cache_key, result, ttl)
        except Exception as e:
            # Log error pero continúa
            if hasattr(self._logger, 'log_structured'):
                self._logger.log_structured('WARNING', f"Cache set failed: {e}")
    
    def _generate_cache_key(
        self, 
        fingerprint: TextFingerprint, 
        analysis_types: List[AnalysisType],
        tier: ProcessingTier
    ) -> str:
        """Generar clave de cache determinística."""
        types_str = ",".join(sorted(at.name for at in analysis_types))
        types_hash = hash(types_str) % 100000  # Hash simple
        return f"nlp:{fingerprint.short_hash}:{types_hash}:{tier.value}"
    
    def _get_cache_ttl(self, tier: ProcessingTier) -> int:
        """Obtener TTL de cache según tier."""
        ttl_map = {
            ProcessingTier.ULTRA_FAST: 3600,    # 1 hora
            ProcessingTier.BALANCED: 7200,      # 2 horas
            ProcessingTier.HIGH_QUALITY: 14400, # 4 horas
            ProcessingTier.RESEARCH_GRADE: 28800 # 8 horas
        }
        return ttl_map.get(tier, 3600)
    
    def _get_models_used(self, analysis_types: List[AnalysisType], tier: ProcessingTier) -> str:
        """Obtener string de modelos utilizados."""
        models = []
        for analysis_type in analysis_types:
            analyzer = self._analyzer_factory.create_analyzer(analysis_type, tier)
            if analyzer:
                models.append(analyzer.get_name())
        return ",".join(models) if models else "none"
    
    def _create_success_response(
        self, 
        request_id: str, 
        analysis_result: AnalysisResult,
        cache_hit: bool
    ) -> AnalysisResponse:
        """Crear response exitoso."""
        return AnalysisResponse.success_response(
            request_id=request_id,
            analysis_results=analysis_result.to_dict(),
            metadata={
                'cache_hit': cache_hit,
                'processing_tier': analysis_result.metrics.tier.value if analysis_result.metrics else None,
                'performance_grade': analysis_result.get_performance_grade()
            },
            metrics={
                'duration_ms': analysis_result.metrics.duration_ms if analysis_result.metrics else None,
                'cache_hit': cache_hit,
                'models_used': analysis_result.metrics.model_used if analysis_result.metrics else None
            }
        )
    
    def _generate_request_id(self) -> str:
        """Generar ID único de request."""
        return f"req_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
    
    def _record_metrics(self, duration_ms: float, success: bool, cache_hit: bool) -> None:
        """Registrar métricas."""
        try:
            self._metrics_collector.record_histogram('analysis_duration_ms', duration_ms)
            self._metrics_collector.increment_counter('analysis_total', 1, {'success': str(success)})
            if cache_hit:
                self._metrics_collector.increment_counter('cache_hits')
            else:
                self._metrics_collector.increment_counter('cache_misses')
        except Exception:
            pass  # No fallar por métricas
    
    def _log_response(
        self, 
        request_id: str, 
        success: bool, 
        duration_ms: float, 
        cache_hit: bool, 
        error: Optional[str] = None
    ) -> None:
        """Log de response."""
        try:
            if hasattr(self._logger, 'log_analysis_response'):
                self._logger.log_analysis_response(
                    request_id=request_id,
                    success=success,
                    duration_ms=duration_ms,
                    cache_hit=cache_hit,
                    error=error
                )
        except Exception:
            pass  # No fallar por logging


class BatchAnalysisUseCase:
    """Use Case para análisis en lote."""
    
    def __init__(self, analyze_text_use_case: AnalyzeTextUseCase):
        self._analyze_text_use_case = analyze_text_use_case
        self._logger = logging.getLogger(self.__class__.__name__)
    
    async def execute(self, request: BatchAnalysisRequest) -> List[AnalysisResponse]:
        """
        Ejecutar análisis en lote con control de concurrencia.
        
        Args:
            request: BatchAnalysisRequest con parámetros
            
        Returns:
            Lista de AnalysisResponse
        """
        # Crear semáforo para control de concurrencia
        semaphore = asyncio.Semaphore(request.max_concurrency)
        
        async def analyze_with_semaphore(text: str, index: int) -> AnalysisResponse:
            async with semaphore:
                analysis_request = AnalysisRequest(
                    text=text,
                    analysis_types=request.analysis_types,
                    processing_tier=request.processing_tier,
                    client_id=request.client_id,
                    request_id=f"{request.request_id}_{index}" if request.request_id else None,
                    use_cache=request.use_cache,
                    timeout_seconds=request.timeout_seconds / len(request.texts)  # Distribuir timeout
                )
                return await self._analyze_text_use_case.execute(analysis_request)
        
        # Crear tareas para todos los textos
        tasks = [
            analyze_with_semaphore(text, i) 
            for i, text in enumerate(request.texts)
        ]
        
        # Ejecutar en paralelo
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convertir excepciones en responses de error
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_response = AnalysisResponse.error_response(
                        request_id=f"{request.request_id}_{i}" if request.request_id else f"batch_{i}",
                        errors=[f"Batch analysis failed: {str(result)}"]
                    )
                    final_results.append(error_response)
                else:
                    final_results.append(result)
            
            return final_results
            
        except Exception as e:
            # Error general en el lote
            self._logger.error(f"Batch analysis failed: {e}")
            
            # Retornar respuestas de error para todos
            return [
                AnalysisResponse.error_response(
                    request_id=f"{request.request_id}_{i}" if request.request_id else f"batch_{i}",
                    errors=[f"Batch processing failed: {str(e)}"]
                )
                for i in range(len(request.texts))
            ]


class StreamAnalysisUseCase:
    """Use Case para análisis en streaming."""
    
    def __init__(self, analyze_text_use_case: AnalyzeTextUseCase):
        self._analyze_text_use_case = analyze_text_use_case
        self._logger = logging.getLogger(self.__class__.__name__)
    
    async def execute_stream(
        self,
        texts_stream: AsyncGenerator[str, None],
        analysis_types: List[AnalysisType],
        processing_tier: Optional[ProcessingTier] = None,
        client_id: str = "stream_client"
    ) -> AsyncGenerator[AnalysisResponse, None]:
        """
        Ejecutar análisis en streaming.
        
        Args:
            texts_stream: Generador asíncrono de textos
            analysis_types: Tipos de análisis a realizar
            processing_tier: Tier de procesamiento
            client_id: ID del cliente
            
        Yields:
            AnalysisResponse para cada texto procesado
        """
        session_id = f"stream_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        counter = 0
        
        try:
            async for text in texts_stream:
                counter += 1
                
                # Crear request para el texto
                request = AnalysisRequest(
                    text=text,
                    analysis_types=analysis_types,
                    processing_tier=processing_tier,
                    client_id=client_id,
                    request_id=f"{session_id}_{counter}",
                    use_cache=True  # Cache beneficioso en streams
                )
                
                # Procesar y yield resultado
                try:
                    response = await self._analyze_text_use_case.execute(request)
                    yield response
                    
                except Exception as e:
                    # Yield error response pero continúa el stream
                    error_response = AnalysisResponse.error_response(
                        request_id=f"{session_id}_{counter}",
                        errors=[f"Stream analysis failed: {str(e)}"]
                    )
                    yield error_response
                    
        except Exception as e:
            # Error en el stream completo
            self._logger.error(f"Stream analysis failed: {e}")
            
            # Yield error final
            yield AnalysisResponse.error_response(
                request_id=f"{session_id}_error",
                errors=[f"Stream processing failed: {str(e)}"]
            ) 