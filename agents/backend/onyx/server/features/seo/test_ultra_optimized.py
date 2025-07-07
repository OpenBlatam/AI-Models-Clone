"""
Test Ultra-Optimizado para el Servicio SEO con las librerías más rápidas.
Demuestra las mejoras de rendimiento y eficiencia.
"""

import asyncio
import time
import psutil
import tracemalloc
from typing import List, Dict, Any
import orjson
from loguru import logger
import httpx
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import statistics

from service_ultra_optimized import UltraOptimizedSEOService, SEOScrapeRequest
from api_ultra_optimized import app
from fastapi.testclient import TestClient


class UltraOptimizedTester:
    """Tester ultra-optimizado para el servicio SEO."""
    
    def __init__(self):
        self.seo_service = UltraOptimizedSEOService()
        self.test_urls = [
            "https://www.google.com",
            "https://www.github.com",
            "https://www.stackoverflow.com",
            "https://www.wikipedia.org",
            "https://www.reddit.com",
            "https://www.youtube.com",
            "https://www.amazon.com",
            "https://www.microsoft.com",
            "https://www.apple.com",
            "https://www.netflix.com"
        ]
        self.results = []
        self.memory_snapshots = []
        
        # Configurar logging
        logger.add("logs/ultra_test.log", rotation="50 MB", compression="zstd")
    
    async def run_performance_test(self):
        """Ejecuta test de rendimiento ultra-optimizado."""
        logger.info("🚀 Iniciando Test Ultra-Optimizado de Rendimiento SEO")
        
        # Iniciar monitoreo de memoria
        tracemalloc.start()
        process = psutil.Process()
        
        # Test 1: Rendimiento individual
        await self.test_individual_performance()
        
        # Test 2: Rendimiento en lote
        await self.test_batch_performance()
        
        # Test 3: Test de caché
        await self.test_cache_performance()
        
        # Test 4: Test de memoria
        await self.test_memory_usage()
        
        # Test 5: Test de concurrencia
        await self.test_concurrency()
        
        # Test 6: Test de API
        await self.test_api_performance()
        
        # Generar reporte
        await self.generate_performance_report()
        
        # Limpiar recursos
        await self.seo_service.close()
        tracemalloc.stop()
    
    async def test_individual_performance(self):
        """Test de rendimiento individual ultra-optimizado."""
        logger.info("📊 Test de Rendimiento Individual")
        
        times = []
        memory_usage = []
        
        for i, url in enumerate(self.test_urls[:5]):
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss
            
            try:
                request = SEOScrapeRequest(url=url)
                result = await self.seo_service.scrape(request)
                
                end_time = time.perf_counter()
                end_memory = psutil.Process().memory_info().rss
                
                processing_time = end_time - start_time
                memory_delta = (end_memory - start_memory) / 1024 / 1024  # MB
                
                times.append(processing_time)
                memory_usage.append(memory_delta)
                
                logger.info(f"URL {i+1}: {url}")
                logger.info(f"  ⏱️  Tiempo: {processing_time:.3f}s")
                logger.info(f"  💾 Memoria: {memory_delta:.2f}MB")
                logger.info(f"  ✅ Éxito: {result.success}")
                logger.info(f"  📊 Score SEO: {result.data.get('analysis', {}).get('score', 0)}")
                
            except Exception as e:
                logger.error(f"Error en URL {url}: {e}")
        
        # Estadísticas
        avg_time = statistics.mean(times)
        avg_memory = statistics.mean(memory_usage)
        
        logger.info(f"📈 Estadísticas Individuales:")
        logger.info(f"  ⏱️  Tiempo promedio: {avg_time:.3f}s")
        logger.info(f"  💾 Memoria promedio: {avg_memory:.2f}MB")
        logger.info(f"  🚀 Tiempo mínimo: {min(times):.3f}s")
        logger.info(f"  🐌 Tiempo máximo: {max(times):.3f}s")
    
    async def test_batch_performance(self):
        """Test de rendimiento en lote ultra-optimizado."""
        logger.info("📦 Test de Rendimiento en Lote")
        
        batch_sizes = [5, 10, 20]
        
        for batch_size in batch_sizes:
            logger.info(f"🔄 Procesando lote de {batch_size} URLs")
            
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss
            
            # Crear requests
            requests = [
                SEOScrapeRequest(url=url) 
                for url in self.test_urls[:batch_size]
            ]
            
            # Procesar en paralelo
            tasks = [self.seo_service.scrape(req) for req in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss
            
            processing_time = end_time - start_time
            memory_delta = (end_memory - start_memory) / 1024 / 1024
            success_count = sum(1 for r in results if isinstance(r, object) and hasattr(r, 'success') and r.success)
            
            throughput = batch_size / processing_time
            
            logger.info(f"📊 Resultados para lote de {batch_size}:")
            logger.info(f"  ⏱️  Tiempo total: {processing_time:.3f}s")
            logger.info(f"  💾 Memoria: {memory_delta:.2f}MB")
            logger.info(f"  ✅ Éxitos: {success_count}/{batch_size}")
            logger.info(f"  🚀 Throughput: {throughput:.2f} URLs/s")
    
    async def test_cache_performance(self):
        """Test de rendimiento del caché ultra-optimizado."""
        logger.info("💾 Test de Rendimiento del Caché")
        
        # URL de prueba
        test_url = self.test_urls[0]
        
        # Primera llamada (cache miss)
        start_time = time.perf_counter()
        request1 = SEOScrapeRequest(url=test_url)
        result1 = await self.seo_service.scrape(request1)
        first_call_time = time.perf_counter() - start_time
        
        # Segunda llamada (cache hit)
        start_time = time.perf_counter()
        request2 = SEOScrapeRequest(url=test_url)
        result2 = await self.seo_service.scrape(request2)
        second_call_time = time.perf_counter() - start_time
        
        # Estadísticas del caché
        cache_stats = self.seo_service.get_cache_stats()
        
        speedup = first_call_time / second_call_time if second_call_time > 0 else 0
        
        logger.info(f"📊 Resultados del Caché:")
        logger.info(f"  ⏱️  Primera llamada: {first_call_time:.3f}s")
        logger.info(f"  ⚡ Segunda llamada: {second_call_time:.3f}s")
        logger.info(f"  🚀 Speedup: {speedup:.2f}x")
        logger.info(f"  💾 Hit rate: {cache_stats.get('hit_rate', 0):.2%}")
        logger.info(f"  📦 Tamaño caché: {cache_stats.get('cache_size', 0)}")
        logger.info(f"  🗜️  Ratio compresión: {cache_stats.get('compression_ratio', 0):.2%}")
    
    async def test_memory_usage(self):
        """Test de uso de memoria ultra-optimizado."""
        logger.info("🧠 Test de Uso de Memoria")
        
        # Tomar snapshot inicial
        snapshot1 = tracemalloc.take_snapshot()
        start_memory = psutil.Process().memory_info().rss
        
        # Procesar múltiples URLs
        requests = [SEOScrapeRequest(url=url) for url in self.test_urls[:10]]
        tasks = [self.seo_service.scrape(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Tomar snapshot final
        snapshot2 = tracemalloc.take_snapshot()
        end_memory = psutil.Process().memory_info().rss
        
        # Análisis de memoria
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        memory_delta = (end_memory - start_memory) / 1024 / 1024
        
        logger.info(f"📊 Análisis de Memoria:")
        logger.info(f"  💾 Delta memoria: {memory_delta:.2f}MB")
        logger.info(f"  📈 Memoria final: {end_memory / 1024 / 1024:.2f}MB")
        
        # Top 3 diferencias de memoria
        logger.info(f"🔍 Top 3 diferencias de memoria:")
        for stat in top_stats[:3]:
            logger.info(f"  📄 {stat.traceback.format()[:100]}...")
            logger.info(f"     +{stat.size_diff / 1024:.2f}KB")
    
    async def test_concurrency(self):
        """Test de concurrencia ultra-optimizado."""
        logger.info("🔄 Test de Concurrencia")
        
        concurrency_levels = [5, 10, 20, 50]
        
        for concurrency in concurrency_levels:
            logger.info(f"🔄 Probando con {concurrency} conexiones concurrentes")
            
            start_time = time.perf_counter()
            
            # Crear semáforo para limitar concurrencia
            semaphore = asyncio.Semaphore(concurrency)
            
            async def process_url(url: str):
                async with semaphore:
                    try:
                        request = SEOScrapeRequest(url=url)
                        return await self.seo_service.scrape(request)
                    except Exception as e:
                        return {"error": str(e)}
            
            # Procesar URLs concurrentemente
            tasks = [process_url(url) for url in self.test_urls[:20]]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            success_count = sum(1 for r in results if isinstance(r, object) and hasattr(r, 'success') and r.success)
            throughput = len(results) / processing_time
            
            logger.info(f"📊 Resultados para {concurrency} concurrentes:")
            logger.info(f"  ⏱️  Tiempo total: {processing_time:.3f}s")
            logger.info(f"  ✅ Éxitos: {success_count}/{len(results)}")
            logger.info(f"  🚀 Throughput: {throughput:.2f} URLs/s")
    
    async def test_api_performance(self):
        """Test de rendimiento de la API ultra-optimizada."""
        logger.info("🌐 Test de Rendimiento de la API")
        
        client = TestClient(app)
        
        # Test endpoints individuales
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/cache/stats", "GET"),
            ("/system/info", "GET"),
            ("/metrics", "GET")
        ]
        
        for endpoint, method in endpoints:
            start_time = time.perf_counter()
            
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            end_time = time.perf_counter()
            response_time = end_time - start_time
            
            logger.info(f"🌐 {method} {endpoint}:")
            logger.info(f"  ⏱️  Tiempo: {response_time:.3f}s")
            logger.info(f"  📊 Status: {response.status_code}")
        
        # Test de scraping vía API
        test_url = self.test_urls[0]
        start_time = time.perf_counter()
        
        response = client.post("/scrape", json={
            "url": test_url,
            "options": {}
        })
        
        end_time = time.perf_counter()
        api_response_time = end_time - start_time
        
        logger.info(f"🌐 POST /scrape:")
        logger.info(f"  ⏱️  Tiempo: {api_response_time:.3f}s")
        logger.info(f"  📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"  ✅ Éxito: {data.get('success', False)}")
            logger.info(f"  📊 Score SEO: {data.get('data', {}).get('analysis', {}).get('score', 0)}")
    
    async def generate_performance_report(self):
        """Genera reporte de rendimiento ultra-optimizado."""
        logger.info("📋 Generando Reporte de Rendimiento")
        
        # Obtener estadísticas finales
        cache_stats = self.seo_service.get_cache_stats()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        report = {
            "timestamp": time.time(),
            "test_summary": {
                "total_urls_tested": len(self.test_urls),
                "cache_performance": {
                    "hit_rate": cache_stats.get("hit_rate", 0),
                    "compression_ratio": cache_stats.get("compression_ratio", 0),
                    "cache_size": cache_stats.get("cache_size", 0)
                },
                "memory_usage": {
                    "final_memory_mb": final_memory,
                    "memory_efficient": final_memory < 500  # Menos de 500MB
                },
                "optimization_features": [
                    "Selectolax parser (ultra-rápido)",
                    "OrJSON serialization",
                    "Zstandard compression",
                    "Connection pooling",
                    "Async throttling",
                    "Memory monitoring",
                    "Cache optimization"
                ]
            }
        }
        
        # Guardar reporte
        async with aiofiles.open("logs/performance_report.json", "w") as f:
            await f.write(orjson.dumps(report, option=orjson.OPT_INDENT_2).decode())
        
        logger.info("📋 Reporte guardado en logs/performance_report.json")
        logger.info("🎉 Test Ultra-Optimizado Completado")


async def main():
    """Función principal del test ultra-optimizado."""
    tester = UltraOptimizedTester()
    await tester.run_performance_test()


if __name__ == "__main__":
    asyncio.run(main()) 