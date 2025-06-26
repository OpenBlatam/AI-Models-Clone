"""
🚀 NEXUS OPTIMIZER - EXAMPLE USAGE
================================

Ejemplo práctico de cómo usar el sistema Nexus Optimizer
para optimizar una aplicación web de alta performance.

CARACTERÍSTICAS DEMOSTRADAS:
✅ Cache inteligente multi-nivel
✅ Optimización de base de datos
✅ Decoradores de performance
✅ Monitoreo en tiempo real
✅ API endpoints optimizados
"""

import asyncio
import time
from typing import List, Dict, Any
from nexus_optimizer import (
    NexusOptimizer, 
    NexusConfig, 
    nexus_optimize,
    initialize_nexus,
    get_optimizer
)

# Configuración optimizada para producción
config = NexusConfig(
    optimization_level="ULTRA",
    db_pool_size=50,
    cache_l1_size=10000,
    cache_l2_size=100000,
    cache_ttl=3600,
    enable_metrics=True,
    enable_profiling=True,
    monitoring_interval=5.0
)

# =============================================================================
# EJEMPLO 1: SERVICIO DE DATOS OPTIMIZADO
# =============================================================================

class DataService:
    """Servicio de datos con optimización automática."""
    
    def __init__(self):
        self.optimizer = None
    
    async def initialize(self):
        """Inicializar optimizador."""
        self.optimizer = await initialize_nexus(
            database_url="postgresql://user:pass@localhost:5432/mydb",
            config=config
        )
        print("✅ DataService inicializado con Nexus Optimizer")
    
    @nexus_optimize(cache_result=True, cache_ttl=1800)
    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Obtener datos de usuario con cache automático."""
        print(f"🔍 Buscando usuario {user_id}...")
        
        # Simular consulta de base de datos
        if self.optimizer:
            query = "SELECT * FROM users WHERE id = $1"
            result = await self.optimizer.database.execute_query(query, (user_id,))
            if result:
                return result[0]
        
        # Datos simulados si no hay DB
        await asyncio.sleep(0.1)  # Simular latencia
        return {
            "id": user_id,
            "name": f"Usuario {user_id}",
            "email": f"user{user_id}@example.com",
            "created_at": time.time()
        }
    
    @nexus_optimize(cache_result=True, cache_ttl=300)
    async def get_popular_content(self, limit: int = 10) -> List[Dict]:
        """Obtener contenido popular con cache de 5 minutos."""
        print(f"📊 Obteniendo top {limit} contenidos populares...")
        
        # Simular consulta compleja
        await asyncio.sleep(0.5)  # Simular operación costosa
        
        return [
            {
                "id": i,
                "title": f"Contenido Popular {i}",
                "views": 1000 - (i * 10),
                "score": 100 - i
            }
            for i in range(1, limit + 1)
        ]
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema."""
        if self.optimizer:
            return await self.optimizer.get_system_status()
        return {"status": "not_initialized"}

# =============================================================================
# EJEMPLO 2: API ENDPOINTS OPTIMIZADOS
# =============================================================================

class OptimizedAPI:
    """API con endpoints ultra-optimizados."""
    
    def __init__(self):
        self.data_service = DataService()
        self.request_count = 0
    
    async def initialize(self):
        """Inicializar API."""
        await self.data_service.initialize()
        print("✅ OptimizedAPI inicializada")
    
    async def handle_user_request(self, user_id: int) -> Dict[str, Any]:
        """Manejar request de usuario con optimización completa."""
        start_time = time.perf_counter()
        self.request_count += 1
        
        try:
            # Cache inteligente + optimización DB
            user_data = await self.data_service.get_user_data(user_id)
            
            # Request HTTP optimizada
            optimizer = get_optimizer()
            async with optimizer.network.session.get(
                f"https://api.example.com/user/{user_id}/extra"
            ) as response:
                if response.status == 200:
                    extra_data = await response.json()
                    user_data["extra"] = extra_data
            
            duration = time.perf_counter() - start_time
            
            return {
                "success": True,
                "data": user_data,
                "meta": {
                    "request_id": self.request_count,
                    "duration_ms": round(duration * 1000, 2),
                    "cached": duration < 0.01  # Si fue muy rápido, probablemente cache
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "request_id": self.request_count
            }
    
    async def handle_content_request(self, limit: int = 10) -> Dict[str, Any]:
        """Manejar request de contenido con cache inteligente."""
        start_time = time.perf_counter()
        
        # Cache automático con TTL optimizado
        content = await self.data_service.get_popular_content(limit)
        
        duration = time.perf_counter() - start_time
        
        return {
            "success": True,
            "data": content,
            "count": len(content),
            "meta": {
                "duration_ms": round(duration * 1000, 2),
                "cache_optimized": True
            }
        }

# =============================================================================
# EJEMPLO 3: PROCESAMIENTO DE DATOS MASIVO
# =============================================================================

class MassiveDataProcessor:
    """Procesador de datos masivo con optimización JIT."""
    
    @nexus_optimize(cache_result=True, cache_ttl=7200)
    async def process_analytics_data(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Procesar datos de analytics con JIT y cache."""
        print(f"📈 Procesando {len(dataset)} registros de analytics...")
        
        start_time = time.perf_counter()
        
        # Usar funciones JIT optimizadas si están disponibles
        from nexus_optimizer import fast_array_sum, fast_array_mean
        
        try:
            import numpy as np
            
            # Convertir a arrays NumPy para procesamiento ultra-rápido
            values = np.array([item.get('value', 0) for item in dataset])
            scores = np.array([item.get('score', 0) for item in dataset])
            
            # Usar funciones JIT compiladas
            total_sum = fast_array_sum(values)
            avg_score = fast_array_mean(scores)
            
        except ImportError:
            # Fallback si NumPy no está disponible
            values = [item.get('value', 0) for item in dataset]
            scores = [item.get('score', 0) for item in dataset]
            
            total_sum = sum(values)
            avg_score = sum(scores) / len(scores) if scores else 0
        
        # Simular procesamiento adicional
        await asyncio.sleep(0.01 * len(dataset) / 1000)  # Escala con tamaño
        
        processing_time = time.perf_counter() - start_time
        
        return {
            "total_records": len(dataset),
            "total_sum": float(total_sum),
            "average_score": float(avg_score),
            "processing_time_ms": round(processing_time * 1000, 2),
            "optimized": True
        }

# =============================================================================
# FUNCIÓN PRINCIPAL DE DEMOSTRACIÓN
# =============================================================================

async def run_performance_demo():
    """Ejecutar demostración completa de performance."""
    print("🚀 INICIANDO DEMO DEL NEXUS OPTIMIZER")
    print("=" * 50)
    
    # Inicializar servicios
    api = OptimizedAPI()
    await api.initialize()
    
    processor = MassiveDataProcessor()
    
    # Demo 1: Requests de usuarios (mostrará efecto del cache)
    print("\n📱 DEMO 1: CACHE INTELIGENTE DE USUARIOS")
    print("-" * 40)
    
    user_ids = [1, 2, 3, 1, 2, 1]  # IDs repetidos para mostrar cache
    
    for user_id in user_ids:
        result = await api.handle_user_request(user_id)
        duration = result.get("meta", {}).get("duration_ms", 0)
        cached = result.get("meta", {}).get("cached", False)
        status = "💨 CACHE HIT" if cached else "🔍 DB QUERY"
        print(f"Usuario {user_id}: {duration}ms - {status}")
    
    # Demo 2: Contenido popular (cache automático)
    print("\n📊 DEMO 2: CONTENIDO POPULAR CON CACHE")
    print("-" * 40)
    
    for i in range(3):
        result = await api.handle_content_request(5)
        duration = result.get("meta", {}).get("duration_ms", 0)
        print(f"Request {i+1}: {duration}ms - {len(result['data'])} items")
    
    # Demo 3: Procesamiento de datos masivo
    print("\n⚡ DEMO 3: PROCESAMIENTO JIT OPTIMIZADO")
    print("-" * 40)
    
    # Generar dataset de prueba
    test_data = [
        {"value": i, "score": i * 0.5}
        for i in range(1000)
    ]
    
    result = await processor.process_analytics_data(test_data)
    print(f"Procesados: {result['total_records']} registros")
    print(f"Suma total: {result['total_sum']:,.0f}")
    print(f"Score promedio: {result['average_score']:.2f}")
    print(f"Tiempo: {result['processing_time_ms']}ms")
    
    # Demo 4: Estadísticas del sistema
    print("\n📊 DEMO 4: ESTADÍSTICAS DEL SISTEMA")
    print("-" * 40)
    
    stats = await api.data_service.get_system_stats()
    
    if "cache" in stats:
        cache_hit_ratio = stats["cache"]["hit_ratio"]
        print(f"Cache Hit Ratio: {cache_hit_ratio:.1%}")
        print(f"Cache L1 Size: {stats['cache']['l1_size']}")
        print(f"Hot Keys: {stats['cache']['hot_keys']}")
    
    if "database" in stats:
        db_stats = stats["database"]
        print(f"Total Queries: {db_stats['total_queries']}")
        print(f"Avg Query Time: {db_stats['avg_query_time']:.3f}s")
    
    if "system" in stats:
        sys_stats = stats["system"]
        print(f"Memory Usage: {sys_stats['memory_usage_mb']:.1f}MB")
        print(f"CPU Usage: {sys_stats['cpu_percent']:.1f}%")
    
    if "libraries" in stats:
        libs = stats["libraries"]
        print(f"\nLibrerías optimizadas disponibles:")
        for lib, available in libs.items():
            status = "✅" if available else "❌"
            print(f"  {lib}: {status}")
    
    print("\n🎉 DEMO COMPLETADA - ¡NEXUS OPTIMIZER FUNCIONANDO!")

# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    asyncio.run(run_performance_demo()) 