#!/usr/bin/env python3
"""
OPTIMIZED ADS BACKEND - Ultra Performance Version
===============================================

Backend de ads completamente optimizado con:
- Performance score objetivo 100/100
- Cache inteligente específico para ads
- Circuit breaker para tolerancia a fallos
- Optimizaciones específicas para diferentes tipos de ads
"""

import asyncio
import json
import time
import logging
import hashlib
import threading
import uuid
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdType(Enum):
    """Tipos de ads soportados"""
    FACEBOOK = "facebook"
    GOOGLE = "google"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    YOUTUBE = "youtube"

class CircuitBreaker:
    """Circuit breaker para ads"""
    
    def __init__(self, threshold=3, timeout=30):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = "CLOSED"
        self.lock = threading.Lock()
    
    def protect(self, func):
        async def wrapper(*args, **kwargs):
            with self.lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure < self.timeout:
                        raise Exception("Circuit breaker OPEN")
                    self.state = "HALF_OPEN"
                
                try:
                    result = await func(*args, **kwargs)
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                    return result
                except Exception as e:
                    self.failures += 1
                    self.last_failure = time.time()
                    if self.failures >= self.threshold:
                        self.state = "OPEN"
                    raise
        return wrapper

class OptimizedAdsEngine:
    """Motor optimizado para ads"""
    
    def __init__(self):
        self.libraries = self._scan_libraries()
        self.handlers = self._setup_handlers()
        self.score = self._calculate_score()
        logger.info(f"AdsEngine: {self.score:.1f}/100")
    
    def _scan_libraries(self):
        """Escanear librerías"""
        libs = ["orjson", "blake3", "lz4", "redis", "numba", "polars"]
        available = {}
        for lib in libs:
            try:
                __import__(lib)
                available[lib] = True
            except ImportError:
                available[lib] = False
        
        count = sum(available.values())
        logger.info(f"Libraries: {count}/{len(libs)}")
        return available
    
    def _setup_handlers(self):
        """Setup handlers optimizados"""
        handlers = {}
        
        # JSON
        if self.libraries.get("orjson"):
            import orjson
            handlers["json"] = {
                "dumps": lambda x: orjson.dumps(x).decode(),
                "loads": orjson.loads,
                "name": "orjson",
                "speed": 5.0
            }
        else:
            handlers["json"] = {
                "dumps": json.dumps,
                "loads": json.loads,
                "name": "json",
                "speed": 1.0
            }
        
        # Hash
        if self.libraries.get("blake3"):
            import blake3
            handlers["hash"] = {
                "hash": lambda x: blake3.blake3(x.encode()).hexdigest()[:16],
                "name": "blake3",
                "speed": 8.0
            }
        else:
            handlers["hash"] = {
                "hash": lambda x: hashlib.sha256(x.encode()).hexdigest()[:16],
                "name": "sha256",
                "speed": 1.0
            }
        
        # Compression
        if self.libraries.get("lz4"):
            import lz4.frame
            handlers["compression"] = {
                "compress": lz4.frame.compress,
                "decompress": lz4.frame.decompress,
                "name": "lz4",
                "speed": 10.0
            }
        else:
            import gzip
            handlers["compression"] = {
                "compress": gzip.compress,
                "decompress": gzip.decompress,
                "name": "gzip",
                "speed": 2.0
            }
        
        return handlers
    
    def _calculate_score(self):
        """Calcular score optimización"""
        score = 0
        for handler in self.handlers.values():
            score += handler["speed"] * 4
        
        bonuses = {"polars": 20, "numba": 15, "redis": 10}
        for lib, bonus in bonuses.items():
            if self.libraries.get(lib):
                score += bonus
        
        return min(score, 100.0)

class UltraAdsCache:
    """Cache optimizado para ads"""
    
    def __init__(self, engine):
        self.engine = engine
        self.l1_cache = {}  # Ads rápidos
        self.l2_cache = {}  # Comprimidos
        self.campaign_cache = {}  # Por campaña
        self.timestamps = {}
        self.priorities = {}
        
        self.metrics = {
            "l1_hits": 0, "l2_hits": 0, "campaign_hits": 0,
            "misses": 0, "sets": 0
        }
        
        logger.info("UltraAdsCache inicializado")
    
    async def get(self, key: str, ad_type: str = "general", priority: int = 1):
        """Get optimizado para ads"""
        cache_key = self._generate_key(key)
        
        # L1: Cache rápido
        if cache_key in self.l1_cache:
            self.metrics["l1_hits"] += 1
            return self.l1_cache[cache_key]
        
        # Campaign cache
        campaign_key = f"{ad_type}:{cache_key}"
        if campaign_key in self.campaign_cache:
            self.metrics["campaign_hits"] += 1
            return self.campaign_cache[campaign_key]
        
        # L2: Comprimido
        if cache_key in self.l2_cache:
            try:
                compressed = self.l2_cache[cache_key]
                decompressed = self.engine.handlers["compression"]["decompress"](compressed)
                value = self.engine.handlers["json"]["loads"](decompressed.decode())
                self.metrics["l2_hits"] += 1
                return value
            except Exception:
                del self.l2_cache[cache_key]
        
        self.metrics["misses"] += 1
        return None
    
    async def set(self, key: str, value: Any, ad_type: str = "general", priority: int = 1):
        """Set optimizado para ads"""
        cache_key = self._generate_key(key)
        
        try:
            json_data = self.engine.handlers["json"]["dumps"](value).encode()
            
            # Decisión inteligente por tipo de ad
            if ad_type in ["facebook", "google"] or priority >= 4:
                # Ads importantes van a L1 y campaign cache
                self.l1_cache[cache_key] = value
                campaign_key = f"{ad_type}:{cache_key}"
                self.campaign_cache[campaign_key] = value
            elif len(json_data) < 1024:
                self.l1_cache[cache_key] = value
            else:
                # Comprimir ads grandes
                compressed = self.engine.handlers["compression"]["compress"](json_data)
                self.l2_cache[cache_key] = compressed
            
            self.timestamps[cache_key] = time.time()
            self.priorities[cache_key] = priority
            self.metrics["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache error: {e}")
            return False
    
    def _generate_key(self, key: str):
        """Generar clave"""
        return self.engine.handlers["hash"]["hash"](key)
    
    def get_metrics(self):
        """Métricas de cache"""
        total_hits = self.metrics["l1_hits"] + self.metrics["l2_hits"] + self.metrics["campaign_hits"]
        total_requests = total_hits + self.metrics["misses"]
        hit_rate = (total_hits / max(total_requests, 1)) * 100
        
        return {
            "hit_rate_percent": hit_rate,
            "total_requests": total_requests,
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "campaign_size": len(self.campaign_cache),
            **self.metrics
        }

@dataclass
class OptimizedAdsRequest:
    """Request optimizado para ads"""
    content: str
    ad_type: str = AdType.FACEBOOK.value
    target_audience: str = "general"
    keywords: List[str] = field(default_factory=list)
    priority: int = 1
    use_cache: bool = True
    
    def __post_init__(self):
        if not self.content:
            raise ValueError("Content requerido")
        
        if len(self.content) > 300:
            self.content = self.content[:300]
        
        if len(self.keywords) > 5:
            self.keywords = self.keywords[:5]
    
    def to_cache_key(self):
        """Clave de cache"""
        return f"{self.content[:50]}|{self.ad_type}|{self.target_audience}"

class OptimizedAdsService:
    """Servicio de ads ultra-optimizado"""
    
    def __init__(self):
        self.engine = OptimizedAdsEngine()
        self.cache = UltraAdsCache(self.engine)
        
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_time": 0.0,
            "ads_by_type": {},
            "start_time": time.time()
        }
        
        # Templates por tipo de ad
        self.templates = {
            AdType.FACEBOOK.value: "🎯 {content} para {audience}. ¡Descubre más!",
            AdType.GOOGLE.value: "{content} - {audience}. Más información.",
            AdType.INSTAGRAM.value: "✨ {content} 📸 {audience} #ads",
            AdType.LINKEDIN.value: "Profesional: {content} para {audience}.",
            AdType.TWITTER.value: "🚀 {content} para {audience} #marketing",
            AdType.YOUTUBE.value: "🎥 {content} - Video para {audience}"
        }
        
        logger.info("OptimizedAdsService inicializado")
        self._show_status()
    
    async def generate_ad(self, request: OptimizedAdsRequest):
        """Generación de ads optimizada"""
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        # Track por tipo
        ad_type = request.ad_type
        self.metrics["ads_by_type"][ad_type] = self.metrics["ads_by_type"].get(ad_type, 0) + 1
        
        try:
            # Check cache
            if request.use_cache:
                cache_key = request.to_cache_key()
                cached = await self.cache.get(cache_key, request.ad_type, request.priority)
                if cached:
                    response_time = (time.time() - start_time) * 1000
                    self._record_success(response_time)
                    
                    return {
                        "ad_content": cached["ad_content"],
                        "ad_type": request.ad_type,
                        "response_time_ms": response_time,
                        "cache_hit": True,
                        "optimization_score": self.engine.score
                    }
            
            # Generar ad
            ad_content = await self._generate_ad_content(request)
            response_time = (time.time() - start_time) * 1000
            
            result = {
                "ad_content": ad_content,
                "ad_type": request.ad_type,
                "word_count": len(ad_content.split()),
                "target_audience": request.target_audience
            }
            
            # Cache result
            if request.use_cache:
                await self.cache.set(cache_key, result, request.ad_type, request.priority)
            
            self._record_success(response_time)
            
            return {
                "ad_content": ad_content,
                "ad_type": request.ad_type,
                "response_time_ms": response_time,
                "cache_hit": False,
                "optimization_score": self.engine.score,
                "word_count": result["word_count"]
            }
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            logger.error(f"Ad generation failed: {e}")
            raise
    
    async def _generate_ad_content(self, request: OptimizedAdsRequest):
        """Generar contenido del ad"""
        template = self.templates.get(request.ad_type, self.templates[AdType.FACEBOOK.value])
        
        ad_content = template.format(
            content=request.content,
            audience=request.target_audience
        )
        
        if request.keywords:
            ad_content += f" {', '.join(request.keywords[:3])}"
        
        # Delay mínimo
        await asyncio.sleep(0.001)
        
        return ad_content
    
    async def batch_generate_ads(self, requests: List[OptimizedAdsRequest]):
        """Generación batch de ads"""
        tasks = [self.generate_ad(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "results": results,
            "total_count": len(results),
            "successful_count": sum(1 for r in results if not isinstance(r, Exception)),
            "optimization_score": self.engine.score
        }
    
    def _record_success(self, response_time: float):
        """Registrar éxito"""
        self.metrics["successful_requests"] += 1
        self.metrics["total_time"] += response_time
    
    async def health_check(self):
        """Health check para ads"""
        try:
            test_request = OptimizedAdsRequest(
                content="Health check ad test",
                ad_type=AdType.FACEBOOK.value,
                use_cache=False
            )
            
            start_time = time.time()
            response = await self.generate_ad(test_request)
            test_time = (time.time() - start_time) * 1000
            
            avg_time = self.metrics["total_time"] / max(self.metrics["successful_requests"], 1)
            success_rate = (self.metrics["successful_requests"] / max(self.metrics["total_requests"], 1)) * 100
            
            return {
                "status": "healthy",
                "optimization_score": self.engine.score,
                "test_response_time_ms": test_time,
                "avg_response_time_ms": avg_time,
                "success_rate_percent": success_rate,
                "total_requests": self.metrics["total_requests"],
                "ads_by_type": self.metrics["ads_by_type"],
                "cache_metrics": self.cache.get_metrics(),
                "handlers": {
                    "json": self.engine.handlers["json"]["name"],
                    "hash": self.engine.handlers["hash"]["name"],
                    "compression": self.engine.handlers["compression"]["name"]
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _show_status(self):
        """Mostrar estado"""
        print(f"\n{'='*60}")
        print("🚀 OPTIMIZED ADS BACKEND")
        print(f"{'='*60}")
        print(f"📊 Score: {self.engine.score:.1f}/100")
        print(f"🔥 JSON: {self.engine.handlers['json']['name']}")
        print(f"🔥 Hash: {self.engine.handlers['hash']['name']}")
        print(f"🔥 Compression: {self.engine.handlers['compression']['name']}")
        print(f"🎯 Ad Types: {len(self.templates)} soportados")
        print(f"📚 Libraries: {sum(self.engine.libraries.values())}/{len(self.engine.libraries)}")
        print(f"{'='*60}")

async def ads_demo():
    """Demo optimizado para ads"""
    print("🚀 OPTIMIZED ADS DEMO")
    print("="*40)
    
    ads_service = OptimizedAdsService()
    
    # Health check
    health = await ads_service.health_check()
    print(f"\n🏥 Status: {health['status']}")
    print(f"📊 Score: {health['optimization_score']:.1f}/100")
    print(f"⚡ Test: {health['test_response_time_ms']:.1f}ms")
    
    # Test ads
    requests = [
        OptimizedAdsRequest(
            content="Producto revolucionario IA",
            ad_type=AdType.FACEBOOK.value,
            target_audience="empresarios",
            keywords=["IA", "innovación"],
            priority=5
        ),
        OptimizedAdsRequest(
            content="Oferta limitada 50% off",
            ad_type=AdType.GOOGLE.value,
            target_audience="compradores",
            keywords=["oferta", "descuento"],
            priority=4
        ),
        OptimizedAdsRequest(
            content="Tendencia viral marketing",
            ad_type=AdType.INSTAGRAM.value,
            target_audience="millennials",
            keywords=["viral", "trending"],
            priority=3
        )
    ]
    
    print(f"\n🎯 ADS TESTING:")
    print("-" * 25)
    
    for i, req in enumerate(requests, 1):
        response = await ads_service.generate_ad(req)
        print(f"\n{i}. {req.ad_type.upper()}")
        print(f"   Content: {response['ad_content'][:50]}...")
        print(f"   Time: {response['response_time_ms']:.1f}ms")
        print(f"   Cache: {'✅' if response['cache_hit'] else '❌'}")
        print(f"   Score: {response['optimization_score']:.1f}")
    
    # Cache test
    print(f"\n🔄 CACHE TEST:")
    cache_test = await ads_service.generate_ad(requests[0])
    print(f"   Time: {cache_test['response_time_ms']:.1f}ms")
    print(f"   Hit: {'✅' if cache_test['cache_hit'] else '❌'}")
    
    # Final metrics
    final_health = await ads_service.health_check()
    cache_metrics = final_health["cache_metrics"]
    
    print(f"\n📊 METRICS:")
    print(f"   Hit Rate: {cache_metrics['hit_rate_percent']:.1f}%")
    print(f"   Success Rate: {final_health['success_rate_percent']:.1f}%")
    print(f"   Ads by Type: {final_health['ads_by_type']}")
    print(f"   Handlers: {final_health['handlers']}")
    
    print(f"\n🎉 ADS OPTIMIZATION COMPLETED!")

if __name__ == "__main__":
    asyncio.run(ads_demo()) 