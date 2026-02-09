"""
Advanced Health Checks
=====================

Sistema de health checks para servicios y dependencias.
"""

import asyncio
import time
import logging
from enum import Enum
from typing import Dict, Callable, Optional, Any, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Estado de salud"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Resultado de un health check"""
    name: str
    status: HealthStatus
    message: str = ""
    response_time_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class HealthChecker:
    """
    Health Checker para servicios y dependencias
    
    Ejemplo:
        checker = HealthChecker()
        
        @checker.register("database")
        async def check_database():
            # Verificar conexión a DB
            return HealthStatus.HEALTHY
        
        # En endpoint
        @app.get("/health")
        async def health():
            return checker.check_all()
    """
    
    def __init__(self, service_name: str = "service"):
        self.service_name = service_name
        self.checks: Dict[str, Callable] = {}
        self._lock = asyncio.Lock()
    
    def register(
        self,
        name: str,
        check_func: Optional[Callable] = None,
        timeout: float = 5.0
    ):
        """
        Registra un health check
        
        Args:
            name: Nombre del check
            check_func: Función de check (async o sync)
            timeout: Timeout en segundos
        """
        def decorator(func: Callable):
            async def wrapper() -> HealthCheckResult:
                start_time = time.time()
                try:
                    # Ejecutar con timeout
                    if asyncio.iscoroutinefunction(func):
                        result = await asyncio.wait_for(
                            func(),
                            timeout=timeout
                        )
                    else:
                        result = await asyncio.wait_for(
                            asyncio.to_thread(func),
                            timeout=timeout
                        )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    # Si retorna HealthStatus directamente
                    if isinstance(result, HealthStatus):
                        return HealthCheckResult(
                            name=name,
                            status=result,
                            response_time_ms=response_time
                        )
                    
                    # Si retorna HealthCheckResult
                    if isinstance(result, HealthCheckResult):
                        result.response_time_ms = response_time
                        return result
                    
                    # Si retorna bool
                    if isinstance(result, bool):
                        status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                        return HealthCheckResult(
                            name=name,
                            status=status,
                            response_time_ms=response_time
                        )
                    
                    # Default: asumir healthy
                    return HealthCheckResult(
                        name=name,
                        status=HealthStatus.HEALTHY,
                        response_time_ms=response_time
                    )
                
                except asyncio.TimeoutError:
                    return HealthCheckResult(
                        name=name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Timeout after {timeout}s",
                        response_time_ms=(time.time() - start_time) * 1000
                    )
                
                except Exception as e:
                    logger.error(f"Health check {name} failed: {e}", exc_info=True)
                    return HealthCheckResult(
                        name=name,
                        status=HealthStatus.UNHEALTHY,
                        message=str(e),
                        response_time_ms=(time.time() - start_time) * 1000
                    )
            
            self.checks[name] = wrapper
            return func
        
        if check_func:
            return decorator(check_func)
        return decorator
    
    async def check(self, name: str) -> HealthCheckResult:
        """Ejecuta un health check específico"""
        if name not in self.checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message="Check not registered"
            )
        
        return await self.checks[name]()
    
    async def check_all(self) -> Dict[str, Any]:
        """
        Ejecuta todos los health checks
        
        Returns:
            Dict con estado general y checks individuales
        """
        results = {}
        overall_status = HealthStatus.HEALTHY
        
        # Ejecutar todos los checks en paralelo
        tasks = {name: self.check(name) for name in self.checks}
        check_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        for name, result in zip(tasks.keys(), check_results):
            if isinstance(result, Exception):
                results[name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": str(result),
                    "response_time_ms": 0.0
                }
                overall_status = HealthStatus.UNHEALTHY
            else:
                results[name] = {
                    "status": result.status.value,
                    "message": result.message,
                    "response_time_ms": round(result.response_time_ms, 2),
                    "details": result.details,
                    "timestamp": result.timestamp
                }
                
                # Determinar estado general
                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        return {
            "service": self.service_name,
            "status": overall_status.value,
            "timestamp": time.time(),
            "checks": results
        }
    
    async def is_healthy(self) -> bool:
        """Verifica si el servicio está saludable"""
        result = await self.check_all()
        return result["status"] == HealthStatus.HEALTHY.value


# Health checks predefinidos
async def check_redis(redis_url: str = "redis://localhost:6379") -> HealthStatus:
    """Health check para Redis"""
    try:
        import redis.asyncio as redis
        client = redis.from_url(redis_url)
        await client.ping()
        await client.close()
        return HealthStatus.HEALTHY
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return HealthStatus.UNHEALTHY


async def check_database(db_url: str) -> HealthStatus:
    """Health check para base de datos"""
    try:
        # Adaptar según tu ORM/DB
        # Ejemplo con SQLAlchemy async
        from sqlalchemy.ext.asyncio import create_async_engine
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        await engine.dispose()
        return HealthStatus.HEALTHY
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return HealthStatus.UNHEALTHY




