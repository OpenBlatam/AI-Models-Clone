"""
Retry Logic with Exponential Backoff
====================================

Implementación de retry con exponential backoff y jitter.
"""

import asyncio
import random
import logging
from typing import Callable, Optional, Type, Tuple, Any
from functools import wraps
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Configuración de retry"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)


class ExponentialBackoff:
    """Calcula delay con exponential backoff"""
    
    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """
        Calcula delay para el intento
        
        Args:
            attempt: Número de intento (0-based)
            
        Returns:
            Delay en segundos
        """
        # Exponential backoff: delay = initial * (base ^ attempt)
        delay = self.initial_delay * (self.exponential_base ** attempt)
        
        # Limitar a max_delay
        delay = min(delay, self.max_delay)
        
        # Agregar jitter (randomización)
        if self.jitter:
            jitter_amount = delay * 0.1  # 10% de jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay)  # No negativo
        
        return delay


def retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable] = None
):
    """
    Decorator para retry con exponential backoff
    
    Ejemplo:
        @retry(RetryConfig(max_attempts=5, initial_delay=2.0))
        async def call_service():
            # Tu código aquí
            pass
    """
    if config is None:
        config = RetryConfig()
    
    backoff = ExponentialBackoff(
        initial_delay=config.initial_delay,
        max_delay=config.max_delay,
        exponential_base=config.exponential_base,
        jitter=config.jitter
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    # Si es el último intento, lanzar excepción
                    if attempt == config.max_attempts - 1:
                        logger.error(
                            f"Retry exhausted for {func.__name__} "
                            f"after {config.max_attempts} attempts"
                        )
                        raise
                    
                    # Calcular delay
                    delay = backoff.get_delay(attempt)
                    
                    logger.warning(
                        f"Retry {attempt + 1}/{config.max_attempts} "
                        f"for {func.__name__} after {delay:.2f}s"
                    )
                    
                    # Callback de retry
                    if on_retry:
                        if asyncio.iscoroutinefunction(on_retry):
                            await on_retry(attempt, delay, e)
                        else:
                            on_retry(attempt, delay, e)
                    
                    # Esperar antes de retry
                    await asyncio.sleep(delay)
            
            # No debería llegar aquí, pero por seguridad
            if last_exception:
                raise last_exception
        
        return wrapper
    
    return decorator


# Función helper para uso directo
async def retry_async(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> Any:
    """
    Ejecuta función con retry
    
    Ejemplo:
        result = await retry_async(
            call_service,
            arg1, arg2,
            config=RetryConfig(max_attempts=5)
        )
    """
    if config is None:
        config = RetryConfig()
    
    backoff = ExponentialBackoff(
        initial_delay=config.initial_delay,
        max_delay=config.max_delay,
        exponential_base=config.exponential_base,
        jitter=config.jitter
    )
    
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        except config.retryable_exceptions as e:
            last_exception = e
            
            if attempt == config.max_attempts - 1:
                raise
            
            delay = backoff.get_delay(attempt)
            await asyncio.sleep(delay)
    
    if last_exception:
        raise last_exception




