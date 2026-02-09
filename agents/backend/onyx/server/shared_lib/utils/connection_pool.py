"""
Connection Pooling
=================

Pool de conexiones optimizado para servicios.
"""

import asyncio
import time
import logging
from typing import Generic, TypeVar, Callable, Optional
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class PoolConfig:
    """Configuración del pool"""
    min_size: int = 2
    max_size: int = 10
    max_idle_time: float = 300.0  # 5 minutos
    connection_timeout: float = 5.0
    health_check_interval: float = 60.0


class ConnectionPool(Generic[T]):
    """
    Pool de conexiones genérico
    
    Ejemplo:
        async def create_connection():
            return await connect_to_db()
        
        async def close_connection(conn):
            await conn.close()
        
        pool = ConnectionPool(
            create_connection,
            close_connection,
            PoolConfig(min_size=2, max_size=10)
        )
        
        # Usar
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
    """
    
    def __init__(
        self,
        create_connection: Callable[[], T],
        close_connection: Callable[[T], None],
        config: Optional[PoolConfig] = None
    ):
        """
        Args:
            create_connection: Función para crear conexión
            close_connection: Función para cerrar conexión
            config: Configuración del pool
        """
        self.create_connection = create_connection
        self.close_connection = close_connection
        self.config = config or PoolConfig()
        
        self.pool: deque = deque()
        self.active_connections = 0
        self._lock = asyncio.Lock()
        self._waiters: deque = deque()
        self._last_health_check = time.time()
    
    async def _create_new_connection(self) -> T:
        """Crea una nueva conexión"""
        try:
            if asyncio.iscoroutinefunction(self.create_connection):
                return await asyncio.wait_for(
                    self.create_connection(),
                    timeout=self.config.connection_timeout
                )
            else:
                return await asyncio.wait_for(
                    asyncio.to_thread(self.create_connection),
                    timeout=self.config.connection_timeout
                )
        except asyncio.TimeoutError:
            raise Exception(f"Connection timeout after {self.config.connection_timeout}s")
    
    async def _cleanup_idle_connections(self):
        """Limpia conexiones idle"""
        now = time.time()
        if now - self._last_health_check < self.config.health_check_interval:
            return
        
        self._last_health_check = now
        
        async with self._lock:
            # Remover conexiones idle
            while self.pool:
                conn, last_used = self.pool[0]
                if now - last_used > self.config.max_idle_time:
                    self.pool.popleft()
                    try:
                        if asyncio.iscoroutinefunction(self.close_connection):
                            await self.close_connection(conn)
                        else:
                            await asyncio.to_thread(self.close_connection, conn)
                    except Exception as e:
                        logger.error(f"Error closing idle connection: {e}")
                else:
                    break
    
    async def acquire(self):
        """Adquiere una conexión del pool"""
        await self._cleanup_idle_connections()
        
        # Intentar obtener del pool
        async with self._lock:
            if self.pool:
                conn, _ = self.pool.popleft()
                self.active_connections += 1
                return ConnectionContext(self, conn)
            
            # Si no hay en pool y no excedemos max_size, crear nueva
            if self.active_connections < self.config.max_size:
                try:
                    conn = await self._create_new_connection()
                    self.active_connections += 1
                    return ConnectionContext(self, conn)
                except Exception as e:
                    logger.error(f"Error creating connection: {e}")
                    raise
        
        # Esperar hasta que haya conexión disponible
        waiter = asyncio.Future()
        self._waiters.append(waiter)
        
        async with self._lock:
            # Verificar de nuevo después de obtener lock
            if self.pool:
                conn, _ = self.pool.popleft()
                self.active_connections += 1
                if not waiter.done():
                    waiter.cancel()
                return ConnectionContext(self, conn)
        
        # Esperar
        try:
            await waiter
            return await self.acquire()
        except asyncio.CancelledError:
            raise Exception("Connection pool exhausted")
    
    async def release(self, conn: T):
        """Libera una conexión de vuelta al pool"""
        async with self._lock:
            self.active_connections -= 1
            
            # Si hay waiters, darles la conexión
            if self._waiters:
                waiter = self._waiters.popleft()
                if not waiter.done():
                    waiter.set_result(None)
                return
            
            # Agregar al pool si hay espacio
            if len(self.pool) < self.config.max_size:
                self.pool.append((conn, time.time()))
            else:
                # Pool lleno, cerrar conexión
                try:
                    if asyncio.iscoroutinefunction(self.close_connection):
                        await self.close_connection(conn)
                    else:
                        await asyncio.to_thread(self.close_connection, conn)
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
    
    async def close_all(self):
        """Cierra todas las conexiones"""
        async with self._lock:
            # Cerrar conexiones en pool
            while self.pool:
                conn, _ = self.pool.popleft()
                try:
                    if asyncio.iscoroutinefunction(self.close_connection):
                        await self.close_connection(conn)
                    else:
                        await asyncio.to_thread(self.close_connection, conn)
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            self.pool.clear()
            self.active_connections = 0


class ConnectionContext:
    """Context manager para conexiones del pool"""
    
    def __init__(self, pool: ConnectionPool, connection: T):
        self.pool = pool
        self.connection = connection
    
    def __enter__(self):
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.pool.release(self.connection))
        return False
    
    async def __aenter__(self):
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pool.release(self.connection)
        return False




