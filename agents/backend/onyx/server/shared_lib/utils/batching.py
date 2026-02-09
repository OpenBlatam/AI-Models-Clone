"""
Request Batching
================

Sistema de batching para optimizar múltiples requests.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Callable, Optional, TypeVar, Generic
from dataclasses import dataclass
from collections import deque

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchConfig:
    """Configuración de batching"""
    max_batch_size: int = 10
    max_wait_time: float = 0.1  # segundos
    max_queue_size: int = 1000


class BatchProcessor(Generic[T, R]):
    """
    Procesador de batches
    
    Ejemplo:
        async def process_users(user_ids: List[str]) -> List[User]:
            # Procesar batch de users
            return users
        
        processor = BatchProcessor(
            process_users,
            BatchConfig(max_batch_size=50, max_wait_time=0.2)
        )
        
        # Usar
        user = await processor.process("user-123")
    """
    
    def __init__(
        self,
        batch_func: Callable[[List[T]], R],
        config: Optional[BatchConfig] = None
    ):
        """
        Args:
            batch_func: Función que procesa un batch
            config: Configuración del batch
        """
        self.batch_func = batch_func
        self.config = config or BatchConfig()
        
        self.queue: deque = deque()
        self.pending: Dict[asyncio.Future, T] = {}
        self._lock = asyncio.Lock()
        self._processing = False
        self._last_batch_time = time.time()
    
    async def process(self, item: T) -> R:
        """
        Procesa un item (puede ser agregado a batch)
        
        Args:
            item: Item a procesar
            
        Returns:
            Resultado del procesamiento
        """
        # Verificar queue size
        if len(self.queue) >= self.config.max_queue_size:
            raise Exception("Batch queue is full")
        
        # Crear future para este item
        future = asyncio.Future()
        
        async with self._lock:
            self.queue.append((item, future))
            self.pending[future] = item
        
        # Iniciar procesamiento si no está corriendo
        if not self._processing:
            asyncio.create_task(self._process_batches())
        
        # Esperar resultado
        try:
            return await future
        finally:
            async with self._lock:
                self.pending.pop(future, None)
    
    async def _process_batches(self):
        """Procesa batches continuamente"""
        self._processing = True
        
        try:
            while True:
                await asyncio.sleep(self.config.max_wait_time)
                
                async with self._lock:
                    # Verificar si hay items para procesar
                    if not self.queue:
                        # Verificar si hay items pendientes
                        if not self.pending:
                            break
                        continue
                    
                    # Tomar batch
                    batch_size = min(
                        self.config.max_batch_size,
                        len(self.queue)
                    )
                    
                    batch_items = []
                    batch_futures = []
                    
                    for _ in range(batch_size):
                        if self.queue:
                            item, future = self.queue.popleft()
                            batch_items.append(item)
                            batch_futures.append(future)
                
                # Procesar batch fuera del lock
                if batch_items:
                    try:
                        if asyncio.iscoroutinefunction(self.batch_func):
                            results = await self.batch_func(batch_items)
                        else:
                            results = await asyncio.to_thread(
                                self.batch_func,
                                batch_items
                            )
                        
                        # Distribuir resultados
                        if isinstance(results, (list, tuple)):
                            for future, result in zip(batch_futures, results):
                                if not future.done():
                                    future.set_result(result)
                        else:
                            # Si retorna un solo resultado, dar a todos
                            for future in batch_futures:
                                if not future.done():
                                    future.set_result(results)
                    
                    except Exception as e:
                        # Error en batch, fallar todos los futures
                        for future in batch_futures:
                            if not future.done():
                                future.set_exception(e)
        
        finally:
            self._processing = False


class RequestBatcher:
    """
    Batcher genérico para requests
    
    Ejemplo:
        batcher = RequestBatcher(
            max_batch_size=10,
            max_wait_time=0.1
        )
        
        # Agregar requests
        result1 = await batcher.add_request("key1", fetch_data, "arg1")
        result2 = await batcher.add_request("key2", fetch_data, "arg2")
    """
    
    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        self.processors: Dict[str, BatchProcessor] = {}
        self._lock = asyncio.Lock()
    
    async def add_request(
        self,
        key: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Agrega request a batch
        
        Args:
            key: Key única para agrupar requests similares
            func: Función a ejecutar
            *args, **kwargs: Argumentos para la función
            
        Returns:
            Resultado del request
        """
        async with self._lock:
            if key not in self.processors:
                # Crear processor para este key
                async def batch_func(items: List[tuple]) -> List[Any]:
                    # items es lista de (args, kwargs)
                    results = []
                    for args_tuple, kwargs_dict in items:
                        if asyncio.iscoroutinefunction(func):
                            result = await func(*args_tuple, **kwargs_dict)
                        else:
                            result = await asyncio.to_thread(
                                func,
                                *args_tuple,
                                **kwargs_dict
                            )
                        results.append(result)
                    return results
                
                self.processors[key] = BatchProcessor(
                    batch_func,
                    self.config
                )
            
            processor = self.processors[key]
        
        # Procesar item
        return await processor.process((args, kwargs))


# Instancia global
default_batcher = RequestBatcher()




