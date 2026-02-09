"""
Circuit Breaker Pattern
======================

Implementación del patrón Circuit Breaker para servicios resilientes.
"""

import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Estados del Circuit Breaker"""
    CLOSED = "closed"      # Normal, requests pasan
    OPEN = "open"          # Fallando, requests bloqueados
    HALF_OPEN = "half_open"  # Probando si el servicio se recuperó


class CircuitBreaker:
    """
    Circuit Breaker para proteger servicios externos
    
    Ejemplo:
        breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=Exception
        )
        
        @breaker
        async def call_external_service():
            # Tu código aquí
            pass
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception,
        name: str = "circuit_breaker"
    ):
        """
        Args:
            failure_threshold: Número de fallos antes de abrir
            timeout: Tiempo en segundos antes de intentar half-open
            expected_exception: Excepción que cuenta como fallo
            name: Nombre del circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitBreakerState.CLOSED
        self._lock = asyncio.Lock()
    
    async def _should_attempt_reset(self) -> bool:
        """Verifica si debe intentar reset (half-open)"""
        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                return elapsed >= self.timeout
        return False
    
    async def _on_success(self):
        """Maneja éxito"""
        async with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Éxito en half-open, cerrar el circuito
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit breaker {self.name} CLOSED (recovered)")
            elif self.state == CircuitBreakerState.CLOSED:
                # Reset contador en estado normal
                self.failure_count = 0
    
    async def _on_failure(self, error: Exception):
        """Maneja fallo"""
        async with self._lock:
            if isinstance(error, self.expected_exception):
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    logger.warning(
                        f"Circuit breaker {self.name} OPEN "
                        f"(failures: {self.failure_count})"
                    )
    
    async def _call(self, func: Callable, *args, **kwargs) -> Any:
        """Ejecuta función con circuit breaker"""
        # Verificar si debe resetear
        if await self._should_attempt_reset():
            async with self._lock:
                if self.state == CircuitBreakerState.OPEN:
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info(f"Circuit breaker {self.name} HALF_OPEN (testing)")
        
        # Si está abierto, rechazar inmediatamente
        if self.state == CircuitBreakerState.OPEN:
            raise Exception(
                f"Circuit breaker {self.name} is OPEN. "
                f"Service unavailable."
            )
        
        # Intentar ejecutar
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await self._on_success()
            return result
        
        except self.expected_exception as e:
            await self._on_failure(e)
            raise
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self._call(func, *args, **kwargs)
        
        return wrapper


# Instancia global para uso fácil
default_circuit_breaker = CircuitBreaker()




