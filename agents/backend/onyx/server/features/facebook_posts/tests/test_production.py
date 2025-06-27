"""
🧪 Production Tests
==================

Tests comprehensivos para el sistema NLP de producción.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime
import uuid

# Import production modules
from ..nlp.core.engine import ProductionNLPEngine, RequestContext
from ..nlp.utils.cache import ProductionCache, generate_cache_key


class TestProductionNLPEngine:
    """Tests para el motor NLP de producción."""
    
    @pytest.fixture
    async def engine(self):
        """Fixture del motor."""
        engine = ProductionNLPEngine()
        yield engine
        await engine.shutdown()
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_success(self, engine):
        """Test análisis de sentimientos exitoso."""
        text = "I love this amazing product! It's fantastic!"
        
        result = await engine.analyze_text(text, ["sentiment"])
        
        assert "sentiment" in result
        assert result["sentiment"]["success"] is True
        assert "polarity" in result["sentiment"]
        assert "label" in result["sentiment"]
        assert result["sentiment"]["polarity"] > 0  # Texto positivo
    
    @pytest.mark.asyncio
    async def test_analyze_engagement_success(self, engine):
        """Test análisis de engagement exitoso."""
        text = "What do you think about this? Share your thoughts! 🤔"
        
        result = await engine.analyze_text(text, ["engagement"])
        
        assert "engagement" in result
        assert result["engagement"]["success"] is True
        assert result["engagement"]["engagement_score"] > 0.5  # Tiene pregunta y emoji
    
    @pytest.mark.asyncio
    async def test_multiple_analyzers(self, engine):
        """Test múltiples analizadores."""
        text = "Amazing product! What do you think? 😍"
        
        result = await engine.analyze_text(text, ["sentiment", "engagement", "emotion"])
        
        assert "sentiment" in result
        assert "engagement" in result
        assert "emotion" in result
        assert all(r["success"] for r in result.values() if isinstance(r, dict) and "success" in r)
    
    @pytest.mark.asyncio
    async def test_empty_text_validation(self, engine):
        """Test validación de texto vacío."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await engine.analyze_text("", ["sentiment"])
    
    @pytest.mark.asyncio
    async def test_text_too_long_validation(self, engine):
        """Test validación de texto muy largo."""
        long_text = "a" * 10001  # Más del límite
        
        with pytest.raises(ValueError, match="Text too long"):
            await engine.analyze_text(long_text, ["sentiment"])
    
    @pytest.mark.asyncio
    async def test_request_context_tracking(self, engine):
        """Test tracking de contexto de request."""
        context = RequestContext(user_id="test_user")
        
        result = await engine.analyze_text("Test text", ["sentiment"], context)
        
        assert "_metadata" in result
        assert result["_metadata"]["request_id"] == context.request_id
        assert "processing_time_ms" in result["_metadata"]
    
    @pytest.mark.asyncio
    async def test_metrics_recording(self, engine):
        """Test registro de métricas."""
        initial_total = engine.metrics["total_requests"]
        initial_successful = engine.metrics["successful_requests"]
        
        await engine.analyze_text("Test text", ["sentiment"])
        
        assert engine.metrics["total_requests"] == initial_total + 1
        assert engine.metrics["successful_requests"] == initial_successful + 1
    
    @pytest.mark.asyncio
    async def test_error_handling_and_metrics(self, engine):
        """Test manejo de errores y métricas."""
        initial_failed = engine.metrics["failed_requests"]
        
        # Simular error interno
        with patch.object(engine, '_analyze_sentiment', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                await engine.analyze_text("Test", ["sentiment"])
        
        assert engine.metrics["failed_requests"] == initial_failed + 1
    
    @pytest.mark.asyncio
    async def test_health_check(self, engine):
        """Test health check."""
        health = await engine.health_check()
        
        assert "status" in health
        assert "timestamp" in health
        assert "metrics" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, engine):
        """Test obtener métricas."""
        metrics = await engine.get_metrics()
        
        assert "requests" in metrics
        assert "performance" in metrics
        assert "status" in metrics
        assert "total" in metrics["requests"]
        assert "successful" in metrics["requests"]
        assert "failed" in metrics["requests"]


class TestProductionCache:
    """Tests para el sistema de cache de producción."""
    
    @pytest.fixture
    def cache(self):
        """Fixture del cache."""
        return ProductionCache(default_ttl=60, max_size=100)
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self, cache):
        """Test básico de set y get."""
        key = "test_key"
        value = {"test": "data"}
        
        # Set
        result = await cache.set(key, value)
        assert result is True
        
        # Get
        retrieved = await cache.get(key)
        assert retrieved == value
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, cache):
        """Test cache miss."""
        result = await cache.get("nonexistent_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, cache):
        """Test expiración del cache."""
        key = "expiring_key"
        value = "expiring_value"
        
        # Set con TTL muy corto
        await cache.set(key, value, ttl=1)
        
        # Verificar que existe
        assert await cache.get(key) == value
        
        # Esperar expiración
        await asyncio.sleep(1.1)
        
        # Verificar que expiró
        assert await cache.get(key) is None
    
    @pytest.mark.asyncio
    async def test_cache_metrics(self, cache):
        """Test métricas del cache."""
        # Operaciones para generar métricas
        await cache.set("key1", "value1")
        await cache.get("key1")  # Hit
        await cache.get("nonexistent")  # Miss
        
        stats = cache.get_stats()
        
        assert stats["metrics"]["hits"] >= 1
        assert stats["metrics"]["misses"] >= 1
        assert stats["metrics"]["sets"] >= 1
        assert stats["hit_rate"] > 0
    
    @pytest.mark.asyncio
    async def test_cache_cleanup(self, cache):
        """Test limpieza automática."""
        # Agregar entradas que expiran
        await cache.set("key1", "value1", ttl=1)
        await cache.set("key2", "value2", ttl=1)
        
        # Esperar expiración
        await asyncio.sleep(1.1)
        
        # Ejecutar limpieza
        removed = await cache.cleanup_expired()
        
        assert removed >= 2
    
    @pytest.mark.asyncio
    async def test_cache_eviction(self, cache):
        """Test eviction cuando se alcanza límite."""
        # Llenar cache hasta el límite
        for i in range(cache.max_size + 1):
            await cache.set(f"key_{i}", f"value_{i}")
        
        # Verificar que se hizo eviction
        stats = cache.get_stats()
        assert stats["metrics"]["evictions"] > 0
    
    def test_generate_cache_key(self):
        """Test generación de claves de cache."""
        text = "Test text"
        analyzers = ["sentiment", "engagement"]
        
        key1 = generate_cache_key(text, analyzers)
        key2 = generate_cache_key(text, analyzers)
        
        # Misma entrada debe generar misma clave
        assert key1 == key2
        
        # Diferente entrada debe generar diferente clave
        key3 = generate_cache_key("Different text", analyzers)
        assert key1 != key3


class TestIntegration:
    """Tests de integración del sistema completo."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis(self):
        """Test end-to-end del análisis."""
        engine = ProductionNLPEngine()
        
        try:
            # Análisis completo
            text = "This is an amazing product! What do you think? 😍 #awesome"
            result = await engine.analyze_text(text, ["sentiment", "engagement", "emotion"])
            
            # Verificar estructura de respuesta
            assert "_metadata" in result
            assert "sentiment" in result
            assert "engagement" in result
            assert "emotion" in result
            
            # Verificar que todos los análisis fueron exitosos
            for analyzer in ["sentiment", "engagement", "emotion"]:
                assert result[analyzer]["success"] is True
            
            # Verificar métricas
            metrics = await engine.get_metrics()
            assert metrics["requests"]["total"] >= 1
            
        finally:
            await engine.shutdown()
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test performance bajo carga."""
        engine = ProductionNLPEngine()
        
        try:
            # Múltiples requests concurrentes
            tasks = []
            for i in range(10):
                task = engine.analyze_text(f"Test text {i}", ["sentiment"])
                tasks.append(task)
            
            # Ejecutar todas las tareas
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verificar que todas fueron exitosas
            successful = sum(1 for r in results if not isinstance(r, Exception))
            assert successful == 10
            
            # Verificar métricas
            metrics = await engine.get_metrics()
            assert metrics["requests"]["total"] >= 10
            
        finally:
            await engine.shutdown()


# Tests de performance
class TestPerformance:
    """Tests de performance del sistema."""
    
    @pytest.mark.asyncio
    async def test_latency_benchmark(self):
        """Benchmark de latencia."""
        engine = ProductionNLPEngine()
        
        try:
            start_time = datetime.now()
            
            # Análisis único
            await engine.analyze_text("Performance test text", ["sentiment"])
            
            latency = (datetime.now() - start_time).total_seconds() * 1000
            
            # Verificar que la latencia es razonable (< 100ms)
            assert latency < 100
            
        finally:
            await engine.shutdown()
    
    @pytest.mark.asyncio
    async def test_throughput_benchmark(self):
        """Benchmark de throughput."""
        engine = ProductionNLPEngine()
        
        try:
            start_time = datetime.now()
            
            # Múltiples análisis
            tasks = []
            for i in range(50):
                task = engine.analyze_text(f"Throughput test {i}", ["sentiment"])
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            total_time = (datetime.now() - start_time).total_seconds()
            throughput = 50 / total_time
            
            # Verificar throughput mínimo (> 10 requests/second)
            assert throughput > 10
            
        finally:
            await engine.shutdown()


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"]) 