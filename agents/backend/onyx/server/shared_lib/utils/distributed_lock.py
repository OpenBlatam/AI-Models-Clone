"""
Distributed Locks
=================

Sistema de locks distribuidos para operaciones críticas.
"""

import asyncio
import time
import uuid
import logging
from typing import Optional, Callable
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class LockBackend:
    """Interface para backends de distributed locks"""
    
    async def acquire(self, key: str, ttl: float, owner: str) -> bool:
        """Intenta adquirir lock"""
        raise NotImplementedError
    
    async def release(self, key: str, owner: str) -> bool:
        """Libera lock"""
        raise NotImplementedError
    
    async def extend(self, key: str, owner: str, ttl: float) -> bool:
        """Extiende TTL del lock"""
        raise NotImplementedError


class RedisLockBackend(LockBackend):
    """Backend de locks usando Redis"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def acquire(self, key: str, ttl: float, owner: str) -> bool:
        """Adquiere lock en Redis"""
        try:
            # SET key owner NX EX ttl
            result = await self.redis.set(
                f"lock:{key}",
                owner,
                nx=True,
                ex=int(ttl)
            )
            return result is True
        except Exception as e:
            logger.error(f"Error acquiring lock: {e}")
            return False
    
    async def release(self, key: str, owner: str) -> bool:
        """Libera lock en Redis"""
        try:
            # Lua script para release atómico
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            result = await self.redis.eval(
                script,
                1,
                f"lock:{key}",
                owner
            )
            return result == 1
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
            return False
    
    async def extend(self, key: str, owner: str, ttl: float) -> bool:
        """Extiende TTL del lock"""
        try:
            script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("expire", KEYS[1], ARGV[2])
            else
                return 0
            end
            """
            result = await self.redis.eval(
                script,
                1,
                f"lock:{key}",
                owner,
                int(ttl)
            )
            return result == 1
        except Exception as e:
            logger.error(f"Error extending lock: {e}")
            return False


class DistributedLock:
    """
    Distributed Lock para operaciones críticas
    
    Ejemplo:
        lock = DistributedLock(redis_backend)
        
        async with lock.acquire("resource:123", ttl=30.0):
            # Operación crítica
            await process_resource("123")
    """
    
    def __init__(
        self,
        backend: LockBackend,
        owner: Optional[str] = None
    ):
        """
        Args:
            backend: Backend para locks (Redis, etc.)
            owner: Owner ID único (default: UUID)
        """
        self.backend = backend
        self.owner = owner or str(uuid.uuid4())
    
    @asynccontextmanager
    async def acquire(
        self,
        key: str,
        ttl: float = 30.0,
        retry: bool = True,
        retry_delay: float = 0.1,
        max_retries: int = 10
    ):
        """
        Adquiere lock con context manager
        
        Args:
            key: Key del lock
            ttl: Time to live en segundos
            retry: Si debe reintentar
            retry_delay: Delay entre reintentos
            max_retries: Máximo de reintentos
        """
        acquired = False
        attempts = 0
        
        while not acquired and attempts < max_retries:
            acquired = await self.backend.acquire(key, ttl, self.owner)
            
            if not acquired:
                if retry and attempts < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    attempts += 1
                else:
                    raise Exception(f"Failed to acquire lock: {key}")
        
        try:
            # Auto-extend si es necesario
            if ttl > 10:
                extend_task = asyncio.create_task(
                    self._auto_extend(key, ttl)
                )
            else:
                extend_task = None
            
            yield
            
        finally:
            if extend_task:
                extend_task.cancel()
            
            await self.backend.release(key, self.owner)
    
    async def _auto_extend(self, key: str, ttl: float):
        """Extiende lock automáticamente"""
        extend_interval = ttl * 0.5  # Extender a mitad del TTL
        
        while True:
            try:
                await asyncio.sleep(extend_interval)
                extended = await self.backend.extend(key, self.owner, ttl)
                if not extended:
                    logger.warning(f"Failed to extend lock: {key}")
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-extend: {e}")
                break
    
    async def try_acquire(self, key: str, ttl: float = 30.0) -> bool:
        """Intenta adquirir lock sin bloquear"""
        return await self.backend.acquire(key, ttl, self.owner)
    
    async def release(self, key: str) -> bool:
        """Libera lock manualmente"""
        return await self.backend.release(key, self.owner)




