#!/usr/bin/env python3
"""
🚀 SCRIPT DE INICIO - BLOG POSTS PRODUCCIÓN
==========================================

Script optimizado para ejecutar el sistema en producción con:
- Configuración automática de workers
- Inicialización de servicios
- Monitoreo de salud
- Métricas de rendimiento
"""

import asyncio
import os
import sys
import signal
import time
from typing import Dict, Any
import logging

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Configurar variables de entorno para producción"""
    
    # Detectar entorno
    env = os.getenv("ENVIRONMENT", "development")
    
    # Configuraciones base
    defaults = {
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "WORKERS": str(max(2, os.cpu_count())) if env == "production" else "1",
        "CACHE_TTL": "7200",  # 2 horas
        "AI_TIMEOUT": "30",
        "PROMETHEUS_ENABLED": "true",
        "METRICS_PORT": "9090",
        "LOG_LEVEL": "INFO" if env == "production" else "DEBUG"
    }
    
    # Establecer defaults si no existen
    for key, value in defaults.items():
        if key not in os.environ:
            os.environ[key] = value
    
    logger.info(f"Environment configured for: {env}")
    logger.info(f"Workers: {os.getenv('WORKERS')}")
    logger.info(f"Port: {os.getenv('PORT')}")

async def initialize_services():
    """Inicializar servicios del sistema"""
    
    try:
        # Importar después de configurar environment
        from blog_production import blog_service, cache_manager
        
        logger.info("Initializing blog service...")
        await blog_service.initialize()
        
        logger.info("Services initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        return False

async def health_check():
    """Health check del sistema"""
    
    try:
        from blog_production import blog_service
        
        # Verificar estadísticas
        stats = await blog_service.get_statistics()
        
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "total_generated": stats["total_generated"],
            "error_rate": stats["error_rate"],
            "cache_hit_rate": stats["cache_hit_rate"],
            "optimizations_active": sum(1 for opt in stats["optimizations"].values() if opt)
        }
        
        logger.info(f"Health check: {health_data}")
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

def setup_signal_handlers():
    """Configurar manejadores de señales para shutdown graceful"""
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def run_with_fastapi():
    """Ejecutar con FastAPI"""
    
    try:
        import uvicorn
        from blog_production import app
        
        # Configuración de Uvicorn
        config = uvicorn.Config(
            app=app,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            workers=int(os.getenv("WORKERS", 1)),
            loop="uvloop",
            access_log=os.getenv("ENVIRONMENT") != "production",
            log_level=os.getenv("LOG_LEVEL", "info").lower()
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except ImportError:
        logger.error("FastAPI/Uvicorn not available, running basic server")
        await run_basic_server()

async def run_basic_server():
    """Ejecutar servidor básico sin FastAPI"""
    
    logger.info("Starting basic server...")
    
    # Inicializar servicios
    if not await initialize_services():
        logger.error("Failed to start - service initialization failed")
        return
    
    # Health check inicial
    health = await health_check()
    if health["status"] != "healthy":
        logger.warning("System not fully healthy but continuing...")
    
    # Ejecutar demo
    from blog_production import main
    await main()

async def benchmark_system():
    """Ejecutar benchmark del sistema"""
    
    logger.info("Running system benchmark...")
    
    try:
        from blog_production import run_performance_benchmark
        
        # Benchmark con diferentes cargas
        for load in [10, 50, 100]:
            logger.info(f"Benchmarking with {load} requests...")
            results = await run_performance_benchmark(load)
            
            logger.info(f"Benchmark Results for {load} requests:")
            logger.info(f"  RPS: {results['requests_per_second']}")
            logger.info(f"  Avg Latency: {results['average_latency_ms']}ms")
            logger.info(f"  Cache Hit Rate: {results['cache_hit_rate']}%")
            logger.info(f"  Performance Grade: {results['performance_grade']}")
            
            # Pausa entre benchmarks
            await asyncio.sleep(2)
    
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")

def print_system_info():
    """Mostrar información del sistema"""
    
    print("🚀 BLOG POSTS PRODUCTION SYSTEM")
    print("=" * 50)
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Host: {os.getenv('HOST', '0.0.0.0')}")
    print(f"Port: {os.getenv('PORT', '8000')}")
    print(f"Workers: {os.getenv('WORKERS', '1')}")
    print(f"Cache TTL: {os.getenv('CACHE_TTL', '3600')}s")
    print(f"Prometheus: {os.getenv('PROMETHEUS_ENABLED', 'true')}")
    print("=" * 50)

async def main():
    """Función principal"""
    
    # Configurar entorno
    setup_environment()
    setup_signal_handlers()
    print_system_info()
    
    # Argumentos de línea de comandos
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "benchmark":
            await benchmark_system()
            return
        elif command == "health":
            health = await health_check()
            print(f"Health Status: {health}")
            return
        elif command == "demo":
            await run_basic_server()
            return
    
    # Por defecto, ejecutar con FastAPI si está disponible
    try:
        await run_with_fastapi()
    except ImportError:
        logger.info("FastAPI not available, running demo mode")
        await run_basic_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
       
        de produccion

        