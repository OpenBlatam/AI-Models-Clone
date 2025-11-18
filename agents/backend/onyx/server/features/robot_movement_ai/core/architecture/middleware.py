"""
Middleware Pattern
=================

Sistema de middleware para procesamiento de requests y responses.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Middleware(ABC):
    """Clase base para middleware."""
    
    @abstractmethod
    def process_request(
        self,
        request: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Procesar request.
        
        Args:
            request: Request
            context: Contexto adicional
            
        Returns:
            Request procesado
        """
        pass
    
    @abstractmethod
    def process_response(
        self,
        response: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Procesar response.
        
        Args:
            response: Response
            context: Contexto adicional
            
        Returns:
            Response procesado
        """
        pass
    
    def process_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Exception:
        """
        Procesar error (opcional).
        
        Args:
            error: Error
            context: Contexto adicional
            
        Returns:
            Error procesado
        """
        return error


class MiddlewarePipeline:
    """
    Pipeline de middleware.
    """
    
    def __init__(self):
        """Inicializar pipeline."""
        self.middlewares: List[Middleware] = []
    
    def add_middleware(self, middleware: Middleware) -> 'MiddlewarePipeline':
        """
        Agregar middleware.
        
        Args:
            middleware: Middleware
            
        Returns:
            Self para chaining
        """
        self.middlewares.append(middleware)
        return self
    
    def process_request(
        self,
        request: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Procesar request a través de todos los middlewares.
        
        Args:
            request: Request
            context: Contexto
            
        Returns:
            Request procesado
        """
        current_request = request
        merged_context = context or {}
        
        for middleware in self.middlewares:
            current_request = middleware.process_request(current_request, merged_context)
        
        return current_request
    
    def process_response(
        self,
        response: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Procesar response a través de todos los middlewares (en orden inverso).
        
        Args:
            response: Response
            context: Contexto
            
        Returns:
            Response procesado
        """
        current_response = response
        merged_context = context or {}
        
        # Procesar en orden inverso
        for middleware in reversed(self.middlewares):
            current_response = middleware.process_response(current_response, merged_context)
        
        return current_response
    
    def process_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Exception:
        """
        Procesar error a través de todos los middlewares.
        
        Args:
            error: Error
            context: Contexto
            
        Returns:
            Error procesado
        """
        current_error = error
        merged_context = context or {}
        
        for middleware in self.middlewares:
            current_error = middleware.process_error(current_error, merged_context)
        
        return current_error


# Middlewares predefinidos

class LoggingMiddleware(Middleware):
    """Middleware para logging."""
    
    def process_request(self, request, context=None):
        """Log request."""
        logger.info(f"Request recibido: {type(request).__name__}")
        if hasattr(request, 'start_node') and hasattr(request, 'end_node'):
            logger.info(f"Ruta: {request.start_node} -> {request.end_node}")
        return request
    
    def process_response(self, response, context=None):
        """Log response."""
        logger.info(f"Response generado: {type(response).__name__}")
        if hasattr(response, 'route'):
            logger.info(f"Ruta encontrada: {len(response.route)} nodos")
        return response
    
    def process_error(self, error, context=None):
        """Log error."""
        logger.error(f"Error en middleware: {error}")
        return error


class TimingMiddleware(Middleware):
    """Middleware para medir tiempo."""
    
    def process_request(self, request, context=None):
        """Iniciar timer."""
        if context is None:
            context = {}
        context['start_time'] = time.time()
        return request
    
    def process_response(self, response, context=None):
        """Calcular tiempo."""
        if context and 'start_time' in context:
            elapsed = time.time() - context['start_time']
            logger.info(f"Tiempo de procesamiento: {elapsed:.3f}s")
            if hasattr(response, 'metadata'):
                if response.metadata is None:
                    response.metadata = {}
                response.metadata['processing_time'] = elapsed
        return response


class ValidationMiddleware(Middleware):
    """Middleware para validación."""
    
    def __init__(self, validator_func: Callable):
        """
        Inicializar middleware.
        
        Args:
            validator_func: Función de validación
        """
        self.validator_func = validator_func
    
    def process_request(self, request, context=None):
        """Validar request."""
        if hasattr(request, 'dict'):
            data = request.dict()
        else:
            data = request
        
        result = self.validator_func(data)
        if not result.get('is_valid', True):
            errors = result.get('errors', [])
            raise ValueError(f"Validación fallida: {', '.join(errors)}")
        
        return request


class CachingMiddleware(Middleware):
    """Middleware para caching."""
    
    def __init__(self, cache: Any):
        """
        Inicializar middleware.
        
        Args:
            cache: Instancia de cache
        """
        self.cache = cache
    
    def _get_cache_key(self, request) -> str:
        """Generar clave de cache."""
        if hasattr(request, 'dict'):
            data = request.dict()
        else:
            data = request
        
        import hashlib
        import json
        key_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def process_request(self, request, context=None):
        """Verificar cache."""
        cache_key = self._get_cache_key(request)
        cached = self.cache.get(cache_key)
        
        if cached is not None:
            logger.info("Cache hit")
            if context is None:
                context = {}
            context['cached'] = True
            context['cached_response'] = cached
        
        return request
    
    def process_response(self, response, context=None):
        """Guardar en cache."""
        if context and not context.get('cached'):
            # Obtener request del contexto para generar key
            request = context.get('request')
            if request:
                cache_key = self._get_cache_key(request)
                self.cache.put(cache_key, response)
                logger.info("Response guardado en cache")
        
        return response


class MetricsMiddleware(Middleware):
    """Middleware para métricas."""
    
    def __init__(self, metrics_collector: Any = None):
        """
        Inicializar middleware.
        
        Args:
            metrics_collector: Colector de métricas (opcional)
        """
        self.metrics_collector = metrics_collector
        self.request_count = 0
        self.error_count = 0
    
    def process_request(self, request, context=None):
        """Incrementar contador de requests."""
        self.request_count += 1
        if self.metrics_collector:
            self.metrics_collector.increment('requests.total')
        return request
    
    def process_response(self, response, context=None):
        """Registrar métricas de response."""
        if self.metrics_collector:
            self.metrics_collector.increment('responses.success')
            if hasattr(response, 'metrics'):
                for key, value in response.metrics.items():
                    self.metrics_collector.histogram(f'route.{key}', value)
        return response
    
    def process_error(self, error, context=None):
        """Registrar métricas de error."""
        self.error_count += 1
        if self.metrics_collector:
            self.metrics_collector.increment('responses.error')
        return error
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas."""
        return {
            'request_count': self.request_count,
            'error_count': self.error_count,
            'success_rate': (self.request_count - self.error_count) / max(self.request_count, 1)
        }

