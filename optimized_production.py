"""
ONYX Blog Posts - Código de Producción Ultra-Optimizado
======================================================

Sistema optimizado con librerías de máximo rendimiento para entornos críticos.
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from functools import lru_cache
import hashlib

# Librerías ultra-optimizadas
import orjson  # JSON 3x más rápido
import httpx   # HTTP/2 cliente moderno
import redis.asyncio as aioredis
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
import uvloop
from prometheus_client import Counter, Histogram

# Configurar uvloop para mejor rendimiento
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# === MÉTRICAS PROMETHEUS ===
blog_requests = Counter('blog_requests_total', 'Total requests')
blog_duration = Histogram('blog_generation_seconds', 'Generation time')
cache_hits = Counter('cache_hits_total', 'Cache hits')

# === MODELOS OPTIMIZADOS ===
class BlogRequest(BaseModel):
    topic: str = Field(..., min_length=5, max_length=200)
    type: str = Field("technical", regex="^(technical|tutorial|guide|news)$") 
    tone: str = Field("professional", regex="^(professional|casual|friendly)$")
    length: str = Field("medium", regex="^(short|medium|long)$")
    keywords: List[str] = Field(default_factory=list, max_items=5)
    
    class Config:
        frozen = True

class BlogResponse(BaseModel):
    id: str
    title: str
    content: str
    word_count: int
    generation_time: float
    cost_usd: float
    status: str = "completed"

# === CACHE ULTRA-RÁPIDO ===
class ProductionCache:
    def __init__(self):
        self.redis = None
        self.local_cache = {}
        self.hits = 0
        self.misses = 0
    
    async def init(self):
        self.redis = aioredis.from_url(
            "redis://localhost:6379",
            max_connections=20,
            retry_on_timeout=True
        )
    
    async def get(self, key: str) -> Optional[dict]:
        # Cache local primero
        if key in self.local_cache:
            entry = self.local_cache[key]
            if time.time() < entry["expires"]:
                self.hits += 1
                cache_hits.inc()
                return entry["data"]
            del self.local_cache[key]
        
        # Cache Redis
        try:
            data = await self.redis.get(key)
            if data:
                result = orjson.loads(data)
                self.local_cache[key] = {
                    "data": result, 
                    "expires": time.time() + 300
                }
                self.hits += 1
                cache_hits.inc()
                return result
        except:
            pass
        
        self.misses += 1
        return None
    
    async def set(self, key: str, value: dict, ttl: int = 3600):
        try:
            serialized = orjson.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            self.local_cache[key] = {
                "data": value,
                "expires": time.time() + min(ttl, 300)
            }
        except:
            pass

# === CLIENTE AI OPTIMIZADO ===
class AIClient:
    def __init__(self, api_key: str):
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=50),
            timeout=httpx.Timeout(60.0),
            http2=True,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        self.cost = 0.0
    
    async def generate(self, prompt: str) -> dict:
        start = time.time()
        
        response = await self.client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 2500
            }
        )
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data["usage"]["total_tokens"]
        cost = (tokens / 1000) * 0.0006
        self.cost += cost
        
        return {
            "content": content,
            "tokens": tokens,
            "cost": cost,
            "time": time.time() - start
        }

# === GENERADOR OPTIMIZADO ===
class BlogGenerator:
    def __init__(self, ai_client: AIClient, cache: ProductionCache):
        self.ai_client = ai_client
        self.cache = cache
        self.semaphore = asyncio.Semaphore(10)
    
    @lru_cache(maxsize=1000)
    def _cache_key(self, topic: str, type_: str, tone: str) -> str:
        key = f"{topic}:{type_}:{tone}"
        return f"blog:{hashlib.md5(key.encode()).hexdigest()}"
    
    def _build_prompt(self, req: BlogRequest) -> str:
        words = {"short": 300, "medium": 800, "long": 1500}
        
        return f"""Crea un blog {req.type} sobre "{req.topic}".

Especificaciones:
- Tono: {req.tone}
- Palabras: ~{words[req.length]}
- Keywords: {', '.join(req.keywords)}

Formato JSON:
{{
  "title": "Título SEO optimizado",
  "content": "Contenido completo con introducción, desarrollo y conclusión"
}}

SOLO JSON válido:"""
    
    def _parse_response(self, content: str) -> dict:
        cleaned = content.strip()
        if "```json" in cleaned:
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            cleaned = cleaned[start:end] if start >= 0 and end > 0 else cleaned
        
        try:
            return orjson.loads(cleaned)
        except:
            return {"title": "Blog Generado", "content": content}
    
    async def generate(self, req: BlogRequest) -> BlogResponse:
        request_id = str(uuid.uuid4())
        cache_key = self._cache_key(req.topic, req.type, req.tone)
        
        # Intentar cache
        cached = await self.cache.get(cache_key)
        if cached:
            return BlogResponse(**cached)
        
        # Generar nuevo
        async with self.semaphore:
            with blog_duration.time():
                prompt = self._build_prompt(req)
                ai_result = await self.ai_client.generate(prompt)
                parsed = self._parse_response(ai_result["content"])
                
                response = BlogResponse(
                    id=request_id,
                    title=parsed["title"],
                    content=parsed["content"],
                    word_count=len(parsed["content"].split()),
                    generation_time=ai_result["time"],
                    cost_usd=ai_result["cost"]
                )
                
                # Cachear
                await self.cache.set(cache_key, response.dict())
                return response

# === SISTEMA PRINCIPAL ===
class ProductionBlogSystem:
    def __init__(self, api_key: str):
        self.cache = ProductionCache()
        self.ai_client = AIClient(api_key)
        self.generator = BlogGenerator(self.ai_client, self.cache)
    
    async def init(self):
        await self.cache.init()
    
    async def generate_blog(self, req: BlogRequest) -> BlogResponse:
        blog_requests.inc()
        return await self.generator.generate(req)
    
    async def batch_generate(self, requests: List[BlogRequest]) -> List[BlogResponse]:
        if len(requests) > 5:
            raise ValueError("Máximo 5 blogs por lote")
        
        tasks = [self.generator.generate(req) for req in requests]
        return await asyncio.gather(*tasks)
    
    def stats(self) -> dict:
        total = self.cache.hits + self.cache.misses
        hit_rate = (self.cache.hits / total * 100) if total > 0 else 0
        
        return {
            "cache_hit_rate": hit_rate,
            "total_cost": self.ai_client.cost,
            "cache_hits": self.cache.hits,
            "cache_misses": self.cache.misses
        }

# === API FASTAPI ===
app = FastAPI(title="Production Blog System", version="1.0")
blog_system = None

@app.on_event("startup")
async def startup():
    global blog_system
    api_key = "your-openrouter-key"  # Variable de entorno
    blog_system = ProductionBlogSystem(api_key)
    await blog_system.init()

@app.post("/generate", response_model=BlogResponse)
async def generate_blog(request: BlogRequest):
    return await blog_system.generate_blog(request)

@app.post("/batch", response_model=List[BlogResponse])
async def batch_generate(requests: List[BlogRequest]):
    return await blog_system.batch_generate(requests)

@app.get("/stats")
async def get_stats():
    return blog_system.stats()

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

# === DEMO ===
async def demo():
    system = ProductionBlogSystem("test-key")
    await system.init()
    
    # Generar blog
    req = BlogRequest(
        topic="Python para Data Science",
        type="tutorial",
        tone="professional",
        keywords=["python", "data", "science"]
    )
    
    result = await system.generate_blog(req)
    print(f"✓ Blog: {result.title}")
    print(f"✓ Palabras: {result.word_count}")
    print(f"✓ Tiempo: {result.generation_time:.2f}s")
    print(f"✓ Costo: ${result.cost_usd:.4f}")
    
    # Estadísticas
    stats = system.stats()
    print(f"✓ Hit rate: {stats['cache_hit_rate']:.1f}%")

if __name__ == "__main__":
    print("🚀 Sistema de Blogs de Producción")
    print("Optimizaciones:")
    print("- orjson: JSON 3x más rápido")
    print("- httpx: HTTP/2 + pooling")
    print("- uvloop: Event loop 2x más rápido")
    print("- Redis: Cache distribuido")
    print("- Semáforos: Control concurrencia")
    print("- Prometheus: Métricas")
    
    # asyncio.run(demo())
    
    # Producción:
    # uvicorn optimized_production:app --host 0.0.0.0 --port 8000 --workers 4 