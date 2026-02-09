"""
Graceful Shutdown
================

Manejo de shutdown graceful para servicios FastAPI.
"""

import asyncio
import signal
import logging
from typing import List, Callable, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """
    Maneja shutdown graceful de la aplicación
    
    Ejemplo:
        shutdown = GracefulShutdown()
        
        @shutdown.register
        async def cleanup_connections():
            # Cerrar conexiones
            pass
        
        # En lifespan
        async with shutdown.lifespan():
            # Tu aplicación
            pass
    """
    
    def __init__(self, timeout: float = 30.0):
        """
        Args:
            timeout: Tiempo máximo para shutdown en segundos
        """
        self.timeout = timeout
        self.cleanup_tasks: List[Callable] = []
        self.shutdown_event = asyncio.Event()
        self._shutdown_initiated = False
    
    def register(self, func: Callable):
        """Registra función de cleanup"""
        self.cleanup_tasks.append(func)
        return func
    
    async def cleanup(self):
        """Ejecuta todas las tareas de cleanup"""
        if self._shutdown_initiated:
            return
        
        self._shutdown_initiated = True
        logger.info("Initiating graceful shutdown...")
        
        # Ejecutar cleanup tasks en paralelo
        tasks = []
        for task in self.cleanup_tasks:
            try:
                if asyncio.iscoroutinefunction(task):
                    tasks.append(asyncio.create_task(task()))
                else:
                    tasks.append(asyncio.create_task(asyncio.to_thread(task)))
            except Exception as e:
                logger.error(f"Error registering cleanup task: {e}")
        
        # Esperar todas las tareas con timeout
        if tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Cleanup timeout after {self.timeout}s")
        
        logger.info("Graceful shutdown completed")
    
    @asynccontextmanager
    async def lifespan(self):
        """Context manager para lifespan de FastAPI"""
        # Setup
        logger.info("Starting application...")
        
        # Setup signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.cleanup())
            )
        
        try:
            yield
        finally:
            # Cleanup
            await self.cleanup()
    
    async def wait_for_shutdown(self):
        """Espera hasta que se inicie shutdown"""
        await self.shutdown_event.wait()


# Instancia global
_global_shutdown: Optional[GracefulShutdown] = None


def get_shutdown_handler() -> GracefulShutdown:
    """Obtiene instancia global de shutdown handler"""
    global _global_shutdown
    if _global_shutdown is None:
        _global_shutdown = GracefulShutdown()
    return _global_shutdown


def shutdown_handler(timeout: float = 30.0) -> GracefulShutdown:
    """Crea un nuevo shutdown handler"""
    return GracefulShutdown(timeout=timeout)


# Helper para FastAPI lifespan
def create_lifespan(shutdown: Optional[GracefulShutdown] = None):
    """
    Crea lifespan function para FastAPI
    
    Ejemplo:
        app = FastAPI(lifespan=create_lifespan())
    """
    if shutdown is None:
        shutdown = get_shutdown_handler()
    
    @asynccontextmanager
    async def lifespan(app):
        async with shutdown.lifespan():
            yield
    
    return lifespan




