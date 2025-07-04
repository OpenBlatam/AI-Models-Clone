"""
ULTRA EXTREME V8 PRODUCTION SERVICES
====================================
Production-ready services with advanced features
"""

import asyncio
import logging
import time
import json
import pickle
import gzip
import lz4.frame
import zstandard as zstd
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import uuid

# Core performance libraries
import uvloop
import orjson
from pydantic import BaseModel, Field, validator
import httpx
import aiofiles
import aioredis
import motor
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# AI/ML & Quantum libraries
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import transformers
from transformers import AutoTokenizer, AutoModel, pipeline, TrainingArguments, Trainer
import accelerate
import bitsandbytes as bnb
from optimum import AutoModelForCausalLM, AutoModelForSeq2SeqLM
import sentence_transformers
from sentence_transformers import SentenceTransformer, util
import openai
import anthropic
import cohere
import langchain
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Vector databases
import chromadb
from chromadb.config import Settings
import qdrant_client
from qdrant_client import QdrantClient
import pinecone
import weaviate
import faiss
import numpy as np
import pandas as pd

# Monitoring & Observability
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary, Info
import structlog
from structlog import get_logger
import loguru
from loguru import logger
import psutil
import GPUtil
from memory_profiler import profile

# Performance optimization
import numba
from numba import jit, cuda
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# Security
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import argon2
import jwt
from datetime import datetime, timedelta

# Testing & Quality
import pytest
import pytest_asyncio
from pytest_benchmark.fixture import BenchmarkFixture
import coverage

# Configuration
uvloop.install()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Global logger
logger = get_logger()

# Metrics
REQUEST_COUNT = Counter('ultra_extreme_requests_total', 'Total requests', ['service', 'method'])
REQUEST_DURATION = Histogram('ultra_extreme_request_duration_seconds', 'Request duration', ['service', 'method'])
BATCH_SIZE = Gauge('ultra_extreme_batch_size', 'Current batch size')
CACHE_HIT_RATIO = Gauge('ultra_extreme_cache_hit_ratio', 'Cache hit ratio')
GPU_MEMORY_USAGE = Gauge('ultra_extreme_gpu_memory_bytes', 'GPU memory usage')
CPU_USAGE = Gauge('ultra_extreme_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('ultra_extreme_memory_usage_bytes', 'Memory usage')
ERROR_COUNT = Counter('ultra_extreme_errors_total', 'Total errors', ['service', 'type'])

@dataclass
class ServiceConfig:
    """Service configuration"""
    service_name: str
    use_gpu: bool = True
    use_quantization: bool = True
    use_cache: bool = True
    use_batch_processing: bool = True
    use_real_time_optimization: bool = True
    use_quantum_optimization: bool = False
    cache_ttl: int = 3600
    batch_size: int = 32
    max_concurrent_requests: int = 100
    enable_monitoring: bool = True
    enable_security: bool = True
    enable_compression: bool = True
    compression_level: int = 9
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0

class UltraExtremeAIService:
    """Ultra-extreme AI service with advanced features"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.logger = get_logger()
        self.device = torch.device("cuda" if config.use_gpu and torch.cuda.is_available() else "cpu")
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.vector_db = None
        self.cache = {}
        
        # Initialize components
        self._init_models()
        self._init_vector_db()
        self._init_monitoring()
        
    def _init_models(self):
        """Initialize AI models with quantization"""
        try:
            # Text generation models
            if self.config.use_quantization:
                self.models['gpt2'] = AutoModelForCausalLM.from_pretrained(
                    "gpt2",
                    torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                    device_map="auto" if self.device.type == "cuda" else None,
                    load_in_8bit=True
                )
                self.tokenizers['gpt2'] = AutoTokenizer.from_pretrained("gpt2")
                
            # Embedding models
            self.models['embedding'] = SentenceTransformer(
                'all-MiniLM-L6-v2',
                device=str(self.device)
            )
            
            # Translation models
            self.models['translation'] = AutoModelForSeq2SeqLM.from_pretrained(
                "Helsinki-NLP/opus-mt-en-es",
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None
            )
            self.tokenizers['translation'] = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-es")
            
            # Sentiment analysis pipeline
            self.pipelines['sentiment'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if self.device.type == "cuda" else -1
            )
            
            # Text classification pipeline
            self.pipelines['classification'] = pipeline(
                "text-classification",
                model="facebook/bart-large-mnli",
                device=0 if self.device.type == "cuda" else -1
            )
            
            self.logger.info("AI models initialized successfully")
            
        except Exception as e:
            self.logger.error("AI model initialization failed", error=str(e))
            raise
            
    def _init_vector_db(self):
        """Initialize vector database"""
        try:
            self.vector_db = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=f"./chroma_db_{self.config.service_name}"
            ))
            self.logger.info("Vector database initialized")
        except Exception as e:
            self.logger.warning("Vector database initialization failed", error=str(e))
            
    def _init_monitoring(self):
        """Initialize monitoring"""
        if self.config.enable_monitoring:
            # Start GPU monitoring
            if self.device.type == "cuda":
                asyncio.create_task(self._monitor_gpu())
                
            # Start system monitoring
            asyncio.create_task(self._monitor_system())
            
    async def _monitor_gpu(self):
        """Monitor GPU usage"""
        while True:
            try:
                if torch.cuda.is_available():
                    memory_allocated = torch.cuda.memory_allocated()
                    GPU_MEMORY_USAGE.set(memory_allocated)
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error("GPU monitoring error", error=str(e))
                await asyncio.sleep(30)
                
    async def _monitor_system(self):
        """Monitor system resources"""
        while True:
            try:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                CPU_USAGE.set(cpu_percent)
                MEMORY_USAGE.set(memory.used)
                
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error("System monitoring error", error=str(e))
                await asyncio.sleep(30)
                
    @profile
    async def generate_text(self, prompt: str, max_length: int = 100, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text with ultra-optimization"""
        start_time = time.time()
        REQUEST_COUNT.labels(service=self.config.service_name, method="generate_text").inc()
        
        try:
            # Check cache
            cache_key = f"text_gen:{hash(prompt)}:{max_length}:{temperature}"
            if self.config.use_cache and cache_key in self.cache:
                CACHE_HIT_RATIO.inc()
                return self.cache[cache_key]
                
            # Generate text
            inputs = self.tokenizers['gpt2'].encode(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.models['gpt2'].generate(
                    inputs,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizers['gpt2'].eos_token_id
                )
                
            generated_text = self.tokenizers['gpt2'].decode(outputs[0], skip_special_tokens=True)
            
            result = {
                "generated_text": generated_text,
                "prompt": prompt,
                "max_length": max_length,
                "temperature": temperature,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache result
            if self.config.use_cache:
                self.cache[cache_key] = result
                
            # Update metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(service=self.config.service_name, method="generate_text").observe(duration)
            
            self.logger.info(
                "Text generation completed",
                duration=duration,
                prompt_length=len(prompt),
                generated_length=len(generated_text)
            )
            
            return result
            
        except Exception as e:
            ERROR_COUNT.labels(service=self.config.service_name, type="text_generation").inc()
            self.logger.error("Text generation failed", error=str(e))
            raise
            
    async def get_embeddings(self, texts: Union[str, List[str]]) -> Dict[str, Any]:
        """Get text embeddings with batch processing"""
        start_time = time.time()
        REQUEST_COUNT.labels(service=self.config.service_name, method="get_embeddings").inc()
        
        try:
            if isinstance(texts, str):
                texts = [texts]
                
            # Check cache
            cache_key = f"embeddings:{hash(str(texts))}"
            if self.config.use_cache and cache_key in self.cache:
                CACHE_HIT_RATIO.inc()
                return self.cache[cache_key]
                
            # Get embeddings
            embeddings = self.models['embedding'].encode(texts, convert_to_tensor=True)
            embeddings_list = embeddings.cpu().numpy().tolist()
            
            result = {
                "embeddings": embeddings_list,
                "texts": texts,
                "dimensions": len(embeddings_list[0]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in vector database
            if self.vector_db:
                collection = self.vector_db.get_or_create_collection("text_embeddings")
                collection.add(
                    documents=texts,
                    embeddings=embeddings_list,
                    metadatas=[{"service": self.config.service_name} for _ in texts],
                    ids=[f"emb_{uuid.uuid4()}" for _ in texts]
                )
                
            # Cache result
            if self.config.use_cache:
                self.cache[cache_key] = result
                
            # Update metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(service=self.config.service_name, method="get_embeddings").observe(duration)
            
            self.logger.info(
                "Embeddings generated",
                duration=duration,
                text_count=len(texts),
                dimensions=len(embeddings_list[0])
            )
            
            return result
            
        except Exception as e:
            ERROR_COUNT.labels(service=self.config.service_name, type="embedding_generation").inc()
            self.logger.error("Embedding generation failed", error=str(e))
            raise
            
    async def translate_text(self, text: str, target_language: str = "es") -> Dict[str, Any]:
        """Translate text with optimization"""
        start_time = time.time()
        REQUEST_COUNT.labels(service=self.config.service_name, method="translate_text").inc()
        
        try:
            # Check cache
            cache_key = f"translation:{hash(text)}:{target_language}"
            if self.config.use_cache and cache_key in self.cache:
                CACHE_HIT_RATIO.inc()
                return self.cache[cache_key]
                
            # Translate text
            inputs = self.tokenizers['translation'](text, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.models['translation'].generate(**inputs)
                translated_text = self.tokenizers['translation'].decode(outputs[0], skip_special_tokens=True)
                
            result = {
                "original_text": text,
                "translated_text": translated_text,
                "target_language": target_language,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache result
            if self.config.use_cache:
                self.cache[cache_key] = result
                
            # Update metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(service=self.config.service_name, method="translate_text").observe(duration)
            
            return result
            
        except Exception as e:
            ERROR_COUNT.labels(service=self.config.service_name, type="translation").inc()
            self.logger.error("Translation failed", error=str(e))
            raise
            
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment"""
        start_time = time.time()
        REQUEST_COUNT.labels(service=self.config.service_name, method="analyze_sentiment").inc()
        
        try:
            # Check cache
            cache_key = f"sentiment:{hash(text)}"
            if self.config.use_cache and cache_key in self.cache:
                CACHE_HIT_RATIO.inc()
                return self.cache[cache_key]
                
            # Analyze sentiment
            result_pipeline = self.pipelines['sentiment'](text)
            
            result = {
                "text": text,
                "sentiment": result_pipeline[0]['label'],
                "confidence": result_pipeline[0]['score'],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache result
            if self.config.use_cache:
                self.cache[cache_key] = result
                
            # Update metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(service=self.config.service_name, method="analyze_sentiment").observe(duration)
            
            return result
            
        except Exception as e:
            ERROR_COUNT.labels(service=self.config.service_name, type="sentiment_analysis").inc()
            self.logger.error("Sentiment analysis failed", error=str(e))
            raise
            
    async def batch_process(self, texts: List[str], operation: str) -> List[Dict[str, Any]]:
        """Batch process multiple texts"""
        if not self.config.use_batch_processing:
            # Process individually
            tasks = []
            for text in texts:
                if operation == "embedding":
                    tasks.append(self.get_embeddings(text))
                elif operation == "sentiment":
                    tasks.append(self.analyze_sentiment(text))
                elif operation == "translation":
                    tasks.append(self.translate_text(text))
                    
            return await asyncio.gather(*tasks)
            
        # Process in batches
        batch_size = self.config.batch_size
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            if operation == "embedding":
                batch_result = await self.get_embeddings(batch)
                results.extend(batch_result["embeddings"])
            elif operation == "sentiment":
                batch_results = await asyncio.gather(*[self.analyze_sentiment(text) for text in batch])
                results.extend(batch_results)
            elif operation == "translation":
                batch_results = await asyncio.gather(*[self.translate_text(text) for text in batch])
                results.extend(batch_results)
                
        BATCH_SIZE.set(len(results))
        
        self.logger.info(
            "Batch processing completed",
            operation=operation,
            total_texts=len(texts),
            batch_size=batch_size,
            results_count=len(results)
        )
        
        return results
        
    @jit(nopython=True)
    def _fast_similarity(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        """Fast similarity calculation with Numba JIT"""
        return np.dot(embeddings1, embeddings2.T) / (
            np.linalg.norm(embeddings1, axis=1, keepdims=True) *
            np.linalg.norm(embeddings2, axis=1, keepdims=True)
        )
        
    async def find_similar_texts(self, query_text: str, texts: List[str], top_k: int = 5) -> Dict[str, Any]:
        """Find similar texts using embeddings"""
        start_time = time.time()
        REQUEST_COUNT.labels(service=self.config.service_name, method="find_similar").inc()
        
        try:
            # Get embeddings
            query_embedding = await self.get_embeddings(query_text)
            text_embeddings = await self.get_embeddings(texts)
            
            # Calculate similarities
            query_emb = np.array(query_embedding["embeddings"][0])
            text_embs = np.array(text_embeddings["embeddings"])
            
            similarities = self._fast_similarity(query_emb.reshape(1, -1), text_embs).flatten()
            
            # Get top-k similar texts
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            result = {
                "query_text": query_text,
                "similar_texts": [
                    {
                        "text": texts[i],
                        "similarity": float(similarities[i]),
                        "rank": rank + 1
                    }
                    for rank, i in enumerate(top_indices)
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Update metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(service=self.config.service_name, method="find_similar").observe(duration)
            
            return result
            
        except Exception as e:
            ERROR_COUNT.labels(service=self.config.service_name, type="similarity_search").inc()
            self.logger.error("Similarity search failed", error=str(e))
            raise
            
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        metrics = {
            "service": self.config.service_name,
            "system": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "gpu": {},
            "models": {},
            "cache": {
                "size": len(self.cache),
                "hit_ratio": CACHE_HIT_RATIO._value.get()
            },
            "requests": {
                "total": REQUEST_COUNT._metrics,
                "duration": REQUEST_DURATION._metrics,
                "errors": ERROR_COUNT._metrics
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # GPU metrics
        if self.device.type == "cuda":
            metrics["gpu"] = {
                "memory_allocated": torch.cuda.memory_allocated(),
                "memory_reserved": torch.cuda.memory_reserved(),
                "memory_usage_percent": torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100
            }
            
        # Model metrics
        for model_name, model in self.models.items():
            if hasattr(model, 'num_parameters'):
                metrics["models"][model_name] = {
                    "parameters": model.num_parameters(),
                    "device": str(next(model.parameters()).device)
                }
                
        return metrics
        
    async def cleanup(self):
        """Cleanup resources"""
        # Clear cache
        self.cache.clear()
        
        # Save vector database
        if self.vector_db:
            self.vector_db.persist()
            
        self.logger.info("AI service cleanup completed")

class UltraExtremeCacheService:
    """Ultra-extreme cache service with advanced features"""
    
    def __init__(self, config: ServiceConfig, redis_client: aioredis.Redis):
        self.config = config
        self.redis_client = redis_client
        self.logger = get_logger()
        self.local_cache = {}
        self.compression_stats = {"compressed": 0, "uncompressed": 0}
        
    async def get(self, key: str, use_local_cache: bool = True) -> Optional[Any]:
        """Get value from cache with optimization"""
        start_time = time.time()
        
        try:
            # Check local cache first
            if use_local_cache and key in self.local_cache:
                CACHE_HIT_RATIO.inc()
                return self.local_cache[key]
                
            # Get from Redis
            value = await self.redis_client.get(key)
            if value:
                # Decompress if needed
                if value.startswith(b'COMPRESSED:'):
                    compressed_data = value[11:]  # Remove prefix
                    decompressed_data = zstd.decompress(compressed_data)
                    result = orjson.loads(decompressed_data)
                    self.compression_stats["uncompressed"] += 1
                else:
                    result = orjson.loads(value)
                    
                # Store in local cache
                if use_local_cache:
                    self.local_cache[key] = result
                    
                CACHE_HIT_RATIO.inc()
                return result
                
            return None
            
        except Exception as e:
            self.logger.error("Cache get failed", error=str(e))
            return None
            
    async def set(self, key: str, value: Any, ttl: int = 3600, compress: bool = True) -> bool:
        """Set value in cache with compression"""
        start_time = time.time()
        
        try:
            # Serialize value
            serialized = orjson.dumps(value)
            
            # Compress if enabled
            if compress and self.config.enable_compression:
                compressed = zstd.compress(serialized, level=self.config.compression_level)
                if len(compressed) < len(serialized):
                    final_value = b'COMPRESSED:' + compressed
                    self.compression_stats["compressed"] += 1
                else:
                    final_value = serialized
            else:
                final_value = serialized
                
            # Store in Redis
            await self.redis_client.setex(key, ttl, final_value)
            
            # Store in local cache
            self.local_cache[key] = value
            
            return True
            
        except Exception as e:
            self.logger.error("Cache set failed", error=str(e))
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.redis_client.delete(key)
            self.local_cache.pop(key, None)
            return True
        except Exception as e:
            self.logger.error("Cache delete failed", error=str(e))
            return False
            
    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            await self.redis_client.flushdb()
            self.local_cache.clear()
            return True
        except Exception as e:
            self.logger.error("Cache clear failed", error=str(e))
            return False
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = await self.redis_client.info()
            return {
                "redis": {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                },
                "local_cache": {
                    "size": len(self.local_cache),
                    "keys": list(self.local_cache.keys())
                },
                "compression": self.compression_stats
            }
        except Exception as e:
            self.logger.error("Cache stats failed", error=str(e))
            return {}

class UltraExtremeDatabaseService:
    """Ultra-extreme database service with connection pooling"""
    
    def __init__(self, config: ServiceConfig, database_url: str):
        self.config = config
        self.database_url = database_url
        self.logger = get_logger()
        self.engine = None
        self.session_factory = None
        self.pool = None
        
    async def connect(self):
        """Connect to database with connection pooling"""
        try:
            self.engine = create_async_engine(
                self.database_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")
                
            self.logger.info("Database connected successfully")
            
        except Exception as e:
            self.logger.error("Database connection failed", error=str(e))
            raise
            
    async def disconnect(self):
        """Disconnect from database"""
        if self.engine:
            await self.engine.dispose()
            self.logger.info("Database disconnected")
            
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute database query"""
        start_time = time.time()
        REQUEST_COUNT.labels(service=self.config.service_name, method="database_query").inc()
        
        try:
            async with self.session_factory() as session:
                result = await session.execute(query, params or {})
                rows = result.fetchall()
                
                # Convert to dictionaries
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            ERROR_COUNT.labels(service=self.config.service_name, type="database_error").inc()
            self.logger.error("Database query failed", error=str(e))
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(service=self.config.service_name, method="database_query").observe(duration)

# Main execution
async def main():
    """Main execution function"""
    # Configuration
    config = ServiceConfig(
        service_name="ultra_extreme_v8",
        use_gpu=True,
        use_quantization=True,
        use_cache=True,
        use_batch_processing=True,
        use_real_time_optimization=True,
        enable_monitoring=True,
        enable_security=True,
        enable_compression=True
    )
    
    # Initialize services
    ai_service = UltraExtremeAIService(config)
    
    # Initialize Redis for cache
    redis_client = aioredis.from_url("redis://localhost:6379")
    cache_service = UltraExtremeCacheService(config, redis_client)
    
    # Initialize database
    db_service = UltraExtremeDatabaseService(config, "postgresql+asyncpg://user:pass@localhost/db")
    await db_service.connect()
    
    try:
        # Test services
        test_texts = [
            "This is a test text for AI processing.",
            "Another text to test batch processing.",
            "Third text for performance testing."
        ]
        
        # Test AI service
        generated_text = await ai_service.generate_text("Generate a creative story about AI")
        embeddings = await ai_service.get_embeddings(test_texts[0])
        sentiment = await ai_service.analyze_sentiment(test_texts[0])
        batch_results = await ai_service.batch_process(test_texts, "sentiment")
        
        # Test cache service
        await cache_service.set("test_key", {"data": "test_value"})
        cached_value = await cache_service.get("test_key")
        cache_stats = await cache_service.get_stats()
        
        # Get performance metrics
        ai_metrics = await ai_service.get_performance_metrics()
        
        # Log results
        logger.info("Service tests completed", 
                   generated_text_length=len(generated_text["generated_text"]),
                   embeddings_dimensions=embeddings["dimensions"],
                   sentiment_result=sentiment["sentiment"],
                   batch_results_count=len(batch_results),
                   cache_stats=cache_stats)
        
    finally:
        # Cleanup
        await ai_service.cleanup()
        await db_service.disconnect()
        await redis_client.close()

if __name__ == "__main__":
    asyncio.run(main()) 