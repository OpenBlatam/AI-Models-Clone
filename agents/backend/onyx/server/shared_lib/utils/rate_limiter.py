"""
Advanced Rate Limiting
=====================

Implementaciones avanzadas de rate limiting:
- Token Bucket
- Sliding Window
- Fixed Window
"""

import asyncio
import time
import logging
from typing import Dict, Optional
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RateLimitResult:
    """Resultado de rate limit check"""
    allowed: bool
    remaining: int
    reset_time: float
    retry_after: Optional[float] = None


class TokenBucket:
    """
    Token Bucket Algorithm
    
    Permite bursts mientras mantiene rate promedio.
    """
    
    def __init__(
        self,
        capacity: int,
        refill_rate: float,  # tokens por segundo
        initial_tokens: Optional[int] = None
    ):
        """
        Args:
            capacity: Capacidad máxima del bucket
            refill_rate: Tokens agregados por segundo
            initial_tokens: Tokens iniciales (default: capacity)
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = initial_tokens if initial_tokens is not None else capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> RateLimitResult:
        """
        Intenta consumir tokens
        
        Args:
            tokens: Número de tokens a consumir
            
        Returns:
            RateLimitResult
        """
        async with self._lock:
            # Refill tokens basado en tiempo transcurrido
            now = time.time()
            elapsed = now - self.last_refill
            tokens_to_add = elapsed * self.refill_rate
            
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Verificar si hay suficientes tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return RateLimitResult(
                    allowed=True,
                    remaining=int(self.tokens),
                    reset_time=now + (self.capacity - self.tokens) / self.refill_rate
                )
            else:
                # Calcular cuándo habrá suficientes tokens
                needed = tokens - self.tokens
                retry_after = needed / self.refill_rate
                
                return RateLimitResult(
                    allowed=False,
                    remaining=int(self.tokens),
                    reset_time=now + (self.capacity - self.tokens) / self.refill_rate,
                    retry_after=retry_after
                )


class SlidingWindow:
    """
    Sliding Window Algorithm
    
    Más preciso que fixed window, pero más complejo.
    """
    
    def __init__(
        self,
        max_requests: int,
        window_seconds: float
    ):
        """
        Args:
            max_requests: Máximo de requests permitidos
            window_seconds: Tamaño de la ventana en segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()
        self._lock = asyncio.Lock()
    
    async def consume(self) -> RateLimitResult:
        """Intenta consumir un request"""
        async with self._lock:
            now = time.time()
            
            # Remover requests fuera de la ventana
            cutoff = now - self.window_seconds
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            
            # Verificar límite
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                remaining = self.max_requests - len(self.requests)
                
                # Calcular reset time (cuando el request más viejo expire)
                reset_time = self.requests[0] + self.window_seconds if self.requests else now
                
                return RateLimitResult(
                    allowed=True,
                    remaining=remaining,
                    reset_time=reset_time
                )
            else:
                # Calcular retry_after
                oldest_request = self.requests[0]
                retry_after = oldest_request + self.window_seconds - now
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=oldest_request + self.window_seconds,
                    retry_after=max(0, retry_after)
                )


class RateLimiter:
    """
    Rate Limiter con múltiples algoritmos
    
    Ejemplo:
        limiter = RateLimiter(
            max_requests=100,
            window_seconds=60,
            algorithm="sliding_window"
        )
        
        result = await limiter.check()
        if not result.allowed:
            raise HTTPException(429, "Rate limit exceeded")
    """
    
    def __init__(
        self,
        max_requests: int,
        window_seconds: float = 60.0,
        algorithm: str = "sliding_window",
        burst_capacity: Optional[int] = None
    ):
        """
        Args:
            max_requests: Máximo de requests permitidos
            window_seconds: Ventana de tiempo en segundos
            algorithm: "sliding_window" o "token_bucket"
            burst_capacity: Para token_bucket, capacidad de burst
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        if algorithm == "token_bucket":
            refill_rate = max_requests / window_seconds
            capacity = burst_capacity if burst_capacity else max_requests
            self.algorithm = TokenBucket(capacity, refill_rate)
        else:  # sliding_window
            self.algorithm = SlidingWindow(max_requests, window_seconds)
    
    async def check(self) -> RateLimitResult:
        """Verifica si el request está permitido"""
        if isinstance(self.algorithm, TokenBucket):
            return await self.algorithm.consume(1)
        else:
            return await self.algorithm.consume()
    
    async def is_allowed(self) -> bool:
        """Verifica si está permitido (método simple)"""
        result = await self.check()
        return result.allowed




