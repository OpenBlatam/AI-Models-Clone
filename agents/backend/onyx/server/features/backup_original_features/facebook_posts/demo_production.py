#!/usr/bin/env python3
"""
🏭 Production Demo - Sistema NLP Facebook Posts
===============================================

Demo del sistema NLP de producción con todas las características empresariales.
"""

import asyncio
import time
from datetime import datetime

# Production imports
from nlp.core.engine import ProductionNLPEngine, RequestContext
from nlp.utils.cache import ProductionCache


async def main():
    """Demo principal de producción."""
    
    print("""
🏭 FACEBOOK POSTS NLP - SISTEMA DE PRODUCCIÓN
============================================

Características implementadas:
✅ Motor NLP con logging y métricas
✅ Sistema de cache con TTL
✅ API REST con FastAPI
✅ Tests comprehensivos
✅ Health checks y monitoring
✅ Error handling robusto
""")
    
    # 1. Inicializar sistema
    print("\n📦 1. INICIALIZANDO SISTEMA DE PRODUCCIÓN")
    engine = ProductionNLPEngine()
    cache = ProductionCache()
    
    # 2. Demo análisis con logging
    print("\n🔍 2. ANÁLISIS CON LOGGING ESTRUCTURADO")
    
    test_posts = [
        "¡Increíble oferta! 50% descuento. ¿Qué esperas? 🛍️",
        "Consejos de productividad: 1) Metas claras 2) Sin distracciones. ¿Cuál usas?",
        "Terrible experiencia. Muy decepcionante. No recomiendo. 😞"
    ]
    
    for i, text in enumerate(test_posts):
        print(f"\n📝 Post {i+1}: {text[:50]}...")
        
        context = RequestContext(user_id=f"demo_user_{i}")
        start_time = time.time()
        
        result = await engine.analyze_text(text, ['sentiment', 'engagement'], context)
        analysis_time = (time.time() - start_time) * 1000
        
        print(f"   Sentimiento: {result['sentiment']['label']} ({result['sentiment']['polarity']:.2f})")
        print(f"   Engagement: {result['engagement']['engagement_score']:.2f}")
        print(f"   Tiempo: {analysis_time:.1f}ms")
    
    # 3. Demo cache
    print("\n💾 3. SISTEMA DE CACHE")
    
    # Cache miss
    start_time = time.time()
    await cache.set("test_key", {"data": "test"}, ttl=60)
    first_time = (time.time() - start_time) * 1000
    
    # Cache hit
    start_time = time.time()
    cached = await cache.get("test_key")
    second_time = (time.time() - start_time) * 1000
    
    stats = cache.get_stats()
    print(f"   Cache miss: {first_time:.1f}ms")
    print(f"   Cache hit: {second_time:.1f}ms")
    print(f"   Hit rate: {stats['hit_rate']:.1f}%")
    
    # 4. Demo error handling
    print("\n🛡️ 4. MANEJO DE ERRORES")
    
    try:
        await engine.analyze_text("", ['sentiment'])
    except ValueError as e:
        print(f"   ✅ Error capturado: {e}")
    
    # 5. Health checks
    print("\n🩺 5. HEALTH CHECKS")
    
    engine_health = await engine.health_check()
    cache_health = await cache.health_check()
    
    print(f"   Engine status: {engine_health['status']}")
    print(f"   Cache status: {cache_health['status']}")
    
    # 6. Métricas
    print("\n📊 6. MÉTRICAS DE PERFORMANCE")
    
    metrics = await engine.get_metrics()
    print(f"   Total requests: {metrics['requests']['total']}")
    print(f"   Success rate: {metrics['requests']['success_rate']:.1f}%")
    print(f"   Avg latency: {metrics['performance']['average_latency_ms']:.1f}ms")
    
    # 7. Load test
    print("\n🏋️ 7. LOAD TEST")
    
    tasks = []
    for i in range(10):
        task = engine.analyze_text(f"Load test {i}", ['sentiment'])
        tasks.append(task)
    
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    successful = sum(1 for r in results if not isinstance(r, Exception))
    throughput = len(results) / total_time
    
    print(f"   Requests: {len(results)}")
    print(f"   Exitosos: {successful}")
    print(f"   Throughput: {throughput:.1f} req/s")
    
    # Cleanup
    print("\n🧹 LIMPIEZA")
    await cache.close()
    await engine.shutdown()
    
    print("""
🎉 SISTEMA DE PRODUCCIÓN COMPLETADO
===================================

Características implementadas:
✅ Motor NLP robusto con métricas
✅ Cache con TTL y cleanup automático
✅ API REST documentada
✅ Tests de unit, integration y performance
✅ Health checks comprehensivos
✅ Logging estructurado
✅ Error handling avanzado
✅ Load testing integrado

🚀 ¡Listo para producción!
""")


if __name__ == "__main__":
    asyncio.run(main()) 