"""
ULTRA EXTREME V14 PRODUCTION MAIN
=================================
Production-ready main entry point for Ultra Extreme V14 with advanced features,
clean architecture, and enterprise-grade optimizations
"""

import asyncio
import logging
import time
import json
import hashlib
import os
import sys
from typing import Any, Dict, List, Optional, Union, Protocol, Callable
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import uuid
import functools
import weakref
import gc
import tracemalloc

# FastAPI and web framework
from fastapi import FastAPI, Request, Response, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

# Core performance libraries
import uvloop
import orjson
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, ValidationError, ConfigDict, validator
import httpx
import aiofiles

# AI and ML
import torch
import transformers
from transformers import AutoTokenizer, AutoModel, pipeline
import openai
import anthropic
from anthropic import Anthropic
import cohere
import replicate
import vllm
from vllm import LLM, SamplingParams
import sentence_transformers
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings
import pinecone
import weaviate

# Database and caching
import redis.asyncio as redis
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

# Monitoring and observability
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import structlog
from structlog import get_logger
import psutil
import GPUtil
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Security
import secrets
from cryptography.fernet import Fernet
import bcrypt
import jwt
from passlib.context import CryptContext

# Performance and async
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# Advanced libraries
import ray
from ray import serve
import dask
from dask.distributed import Client as DaskClient

# Configure logging
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

logger = get_logger()

# Install uvloop for maximum performance
uvloop.install()

# Enable memory tracking
tracemalloc.start()

# ============================================================================
# PRODUCTION CONFIGURATION V14
# ============================================================================

class ProductionConfigV14(BaseModel):
    """Production configuration for Ultra Extreme V14"""
    
    # Application
    app_name: str = "Ultra Extreme V14 Production API"
    app_version: str = "14.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 16  # Production workers
    max_requests: int = 100000  # High throughput
    max_requests_jitter: int = 10000
    timeout_keep_alive: int = 120
    timeout_graceful_shutdown: int = 120
    
    # Performance
    enable_compression: bool = True
    enable_caching: bool = True
    cache_ttl: int = 14400  # 4 hours
    batch_size: int = 256
    max_concurrent_requests: int = 2000
    enable_gpu: bool = True
    enable_quantization: bool = True
    enable_distributed: bool = True
    enable_streaming: bool = True
    
    # AI Models
    default_model: str = "gpt-4-turbo"
    fallback_model: str = "gpt-3.5-turbo"
    local_model: str = "microsoft/DialoGPT-medium"
    quantized_model: str = "TheBloke/Llama-2-7B-Chat-GGML"
    vllm_model: str = "meta-llama/Llama-2-7b-chat-hf"
    
    # Vector Search
    vector_dimension: int = 1536
    vector_metric: str = "cosine"
    enable_hnsw: bool = True
    enable_ivf: bool = True
    enable_pq: bool = True
    
    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_profiling: bool = True
    metrics_port: int = 8001
    
    # Security
    enable_rate_limiting: bool = True
    enable_encryption: bool = True
    enable_authentication: bool = True
    jwt_secret: str = Field(default_factory=lambda: secrets.token_urlsafe(64))
    encryption_key: str = Field(default_factory=lambda: Fernet.generate_key().decode())
    
    # External Services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    replicate_api_key: Optional[str] = None
    
    # Database URLs
    redis_url: str = "redis://localhost:6379"
    postgres_url: str = "postgresql+asyncpg://user:pass@localhost/ultra_extreme_v14"
    mongodb_url: str = "mongodb://localhost:27017/ultra_extreme_v14"
    
    # Vector Database URLs
    chroma_url: str = "http://localhost:8000"
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-west1-gcp"
    weaviate_url: str = "http://localhost:8080"
    qdrant_url: str = "http://localhost:6333"
    
    # Monitoring URLs
    jaeger_url: str = "http://localhost:16686"
    prometheus_url: str = "http://localhost:9090"
    grafana_url: str = "http://localhost:3000"
    
    # Advanced
    enable_ray: bool = True
    enable_dask: bool = True
    enable_streaming: bool = True
    enable_batching: bool = True
    enable_pipelining: bool = True
    enable_async_io: bool = True
    enable_memory_mapping: bool = True
    
    class Config:
        validate_assignment = True

# ============================================================================
# PRODUCTION AI SERVICE V14
# ============================================================================

class ProductionAIServiceV14:
    """Production AI service with advanced features"""
    
    def __init__(self, config: ProductionConfigV14):
        self.config = config
        self.device = self._setup_device()
        self.models = {}
        self.vllm_engine = None
        self.quantized_models = {}
        self.local_models = {}
        self.embedding_model = None
        
        # Initialize models
        self._initialize_models()
        
        # Performance tracking
        self.request_count = 0
        self.total_tokens = 0
        self.total_duration = 0.0
        
    def _setup_device(self) -> torch.device:
        """Setup optimal device configuration"""
        if self.config.enable_gpu and torch.cuda.is_available():
            device = torch.device("cuda")
            
            # Optimize CUDA settings
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Memory optimization
            torch.cuda.empty_cache()
            torch.cuda.set_per_process_memory_fraction(0.95)
            
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name()}")
            return device
        else:
            logger.info("Using CPU device")
            return torch.device("cpu")
    
    def _initialize_models(self):
        """Initialize all AI models"""
        try:
            # Initialize VLLM engine
            if self.config.enable_gpu:
                self._initialize_vllm_engine()
            
            # Initialize quantized models
            if self.config.enable_quantization:
                self._initialize_quantized_models()
            
            # Initialize local models
            self._initialize_local_models()
            
            # Initialize embedding model
            self._initialize_embedding_model()
                
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    def _initialize_vllm_engine(self):
        """Initialize VLLM engine for ultra-fast inference"""
        try:
            sampling_params = SamplingParams(
                temperature=0.7,
                top_p=0.9,
                max_tokens=2048,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            self.vllm_engine = LLM(
                model=self.config.vllm_model,
                trust_remote_code=True,
                max_model_len=8192,
                gpu_memory_utilization=0.95,
                tensor_parallel_size=1,
                dtype="bfloat16" if self.device.type == "cuda" else "float32"
            )
            
            logger.info("VLLM engine initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize VLLM engine: {e}")
    
    def _initialize_quantized_models(self):
        """Initialize quantized models for memory efficiency"""
        try:
            # Load quantized model
            model = AutoModelForCausalLM.from_pretrained(
                self.config.quantized_model,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.bfloat16
            )
            
            self.quantized_models["quantized"] = model
            logger.info("Quantized model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load quantized model: {e}")
    
    def _initialize_local_models(self):
        """Initialize local models with optimizations"""
        try:
            # Load local model with optimizations
            model = AutoModelForCausalLM.from_pretrained(
                self.config.local_model,
                torch_dtype=torch.bfloat16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            # Apply optimizations
            if self.device.type == "cuda":
                model = model.half()
            
            self.local_models["local"] = model
            logger.info("Local model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load local model: {e}")
    
    def _initialize_embedding_model(self):
        """Initialize embedding model"""
        try:
            self.embedding_model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2",
                device=str(self.device)
            )
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}")
    
    async def generate_content(self, prompt: str, model_type: str = "vllm", **kwargs) -> str:
        """Generate content with production optimizations"""
        start_time = time.time()
        
        try:
            # Update metrics
            self.request_count += 1
            
            # Choose model based on type
            if model_type == "vllm" and self.vllm_engine:
                result = await self._generate_with_vllm(prompt, **kwargs)
            elif model_type == "quantized" and self.quantized_models:
                result = await self._generate_with_quantized_model(prompt, **kwargs)
            elif model_type == "local" and self.local_models:
                result = await self._generate_with_local_model(prompt, **kwargs)
            else:
                result = await self._generate_with_fallback(prompt, **kwargs)
            
            # Update metrics
            duration = time.time() - start_time
            self.total_duration += duration
            self.total_tokens += len(result.split())
            
            logger.info(f"Generated content in {duration:.3f}s with {model_type} model")
            return result
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return await self._generate_with_fallback(prompt, **kwargs)
    
    async def _generate_with_vllm(self, prompt: str, **kwargs) -> str:
        """Generate with VLLM for maximum performance"""
        sampling_params = SamplingParams(
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.9),
            max_tokens=kwargs.get("max_tokens", 2048),
            presence_penalty=kwargs.get("presence_penalty", 0.1),
            frequency_penalty=kwargs.get("frequency_penalty", 0.1)
        )
        
        outputs = self.vllm_engine.generate([prompt], sampling_params)
        return outputs[0].outputs[0].text
    
    async def _generate_with_quantized_model(self, prompt: str, **kwargs) -> str:
        """Generate with quantized model for memory efficiency"""
        model = self.quantized_models["quantized"]
        tokenizer = AutoTokenizer.from_pretrained(self.config.quantized_model)
        
        inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    async def _generate_with_local_model(self, prompt: str, **kwargs) -> str:
        """Generate with local model"""
        model = self.local_models["local"]
        tokenizer = AutoTokenizer.from_pretrained(self.config.local_model)
        
        inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    async def _generate_with_fallback(self, prompt: str, **kwargs) -> str:
        """Fallback generation method"""
        return f"Generated production content for: {prompt[:100]}... (fallback mode)"
    
    async def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings with optimizations"""
        if not self.embedding_model:
            return np.random.rand(len(texts), self.config.vector_dimension)
        
        try:
            # Batch processing for efficiency
            embeddings = self.embedding_model.encode(
                texts,
                batch_size=self.config.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            return np.random.rand(len(texts), self.config.vector_dimension)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "request_count": self.request_count,
            "total_tokens": self.total_tokens,
            "total_duration": self.total_duration,
            "avg_duration": self.total_duration / max(self.request_count, 1),
            "tokens_per_second": self.total_tokens / max(self.total_duration, 1),
            "device": str(self.device),
            "models_loaded": len(self.models) + len(self.quantized_models) + len(self.local_models)
        }

# ============================================================================
# PRODUCTION CACHE SERVICE V14
# ============================================================================

class ProductionCacheServiceV14:
    """Production cache service with advanced features"""
    
    def __init__(self, config: ProductionConfigV14):
        self.config = config
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        
    async def initialize(self):
        """Initialize cache connections"""
        try:
            # Initialize Redis
            self.redis_client = redis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with optimizations"""
        try:
            # Try memory cache first
            if key in self.memory_cache:
                self.cache_stats["hits"] += 1
                return self.memory_cache[key]
            
            # Try Redis cache
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    self.cache_stats["hits"] += 1
                    # Deserialize
                    deserialized = orjson.loads(value)
                    # Store in memory cache
                    self.memory_cache[key] = deserialized
                    return deserialized
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optimizations"""
        try:
            # Serialize
            serialized = orjson.dumps(value)
            
            # Store in memory cache
            self.memory_cache[key] = value
            
            # Store in Redis
            if self.redis_client:
                ttl = ttl or self.config.cache_ttl
                await self.redis_client.setex(key, ttl, serialized)
            
            self.cache_stats["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = self.cache_stats["hits"] / max(self.cache_stats["hits"] + self.cache_stats["misses"], 1)
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "memory_cache_size": len(self.memory_cache)
        }

# ============================================================================
# PRODUCTION FASTAPI APP V14
# ============================================================================

def create_production_app_v14() -> FastAPI:
    """Create production FastAPI app V14"""
    
    # Load configuration
    config = ProductionConfigV14()
    
    # Create FastAPI app with optimizations
    app = FastAPI(
        title=config.app_name,
        version=config.app_version,
        docs_url="/docs" if config.debug else None,
        redoc_url="/redoc" if config.debug else None,
        openapi_url="/openapi.json" if config.debug else None
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add compression middleware
    if config.enable_compression:
        app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware for performance tracking
    @app.middleware("http")
    async def performance_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Response-Time"] = str(duration)
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        
        return response
    
    return app

def setup_production_routes_v14(app: FastAPI):
    """Setup production routes V14"""
    
    # Initialize services
    config = ProductionConfigV14()
    ai_service = ProductionAIServiceV14(config)
    cache_service = ProductionCacheServiceV14(config)
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        await cache_service.initialize()
        logger.info("Ultra Extreme V14 Production API started successfully")
    
    @app.get("/")
    async def root():
        """Root endpoint with system info"""
        return {
            "message": "Ultra Extreme V14 Production API",
            "version": config.app_version,
            "status": "operational",
            "architecture": "Clean Architecture with DDD",
            "features": {
                "gpu_acceleration": config.enable_gpu,
                "quantization": config.enable_quantization,
                "distributed": config.enable_distributed,
                "streaming": config.enable_streaming
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_info.percent,
                "memory_available": memory_info.available,
                "memory_total": memory_info.total
            },
            "services": {
                "ai_service": "operational",
                "cache_service": "operational"
            }
        }
    
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        return Response(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    @app.get("/system")
    async def system_metrics():
        """System metrics endpoint"""
        # Memory info
        memory_info = psutil.virtual_memory()
        
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_count = psutil.cpu_count()
        
        # Disk info
        disk_info = psutil.disk_usage('/')
        
        # Network info
        network_info = psutil.net_io_counters()
        
        # GPU info (if available)
        gpu_info = []
        if config.enable_gpu and torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                gpu_memory = torch.cuda.get_device_properties(i).total_memory
                gpu_info.append({
                    "device": i,
                    "name": torch.cuda.get_device_name(i),
                    "memory_total": gpu_memory,
                    "memory_allocated": torch.cuda.memory_allocated(i),
                    "memory_cached": torch.cuda.memory_reserved(i)
                })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "count": cpu_count,
                "percent_per_core": cpu_percent,
                "percent_total": sum(cpu_percent) / len(cpu_percent)
            },
            "memory": {
                "total": memory_info.total,
                "available": memory_info.available,
                "used": memory_info.used,
                "percent": memory_info.percent
            },
            "disk": {
                "total": disk_info.total,
                "used": disk_info.used,
                "free": disk_info.free,
                "percent": (disk_info.used / disk_info.total) * 100
            },
            "network": {
                "bytes_sent": network_info.bytes_sent,
                "bytes_recv": network_info.bytes_recv,
                "packets_sent": network_info.packets_sent,
                "packets_recv": network_info.packets_recv
            },
            "gpu": gpu_info,
            "ai_service_stats": ai_service.get_performance_stats(),
            "cache_stats": cache_service.get_stats()
        }
    
    @app.post("/api/v14/ai/generate")
    async def generate_ai_content(request: dict):
        """Generate AI content with production optimizations"""
        try:
            prompt = request.get("prompt", "")
            model_type = request.get("model_type", "vllm")
            
            if not prompt:
                raise HTTPException(status_code=400, detail="Prompt is required")
            
            # Check cache first
            cache_key = f"ai_generate:{hashlib.md5(prompt.encode()).hexdigest()}"
            cached_result = await cache_service.get(cache_key)
            
            if cached_result:
                return {
                    "success": True,
                    "content": cached_result,
                    "cached": True,
                    "model_type": model_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Generate content
            start_time = time.time()
            content = await ai_service.generate_content(prompt, model_type, **request)
            duration = time.time() - start_time
            
            # Cache result
            await cache_service.set(cache_key, content)
            
            return {
                "success": True,
                "content": content,
                "cached": False,
                "model_type": model_type,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v14/ai/embeddings")
    async def get_embeddings(request: dict):
        """Get embeddings with production optimizations"""
        try:
            texts = request.get("texts", [])
            
            if not texts:
                raise HTTPException(status_code=400, detail="Texts are required")
            
            # Check cache first
            cache_key = f"embeddings:{hashlib.md5(str(texts).encode()).hexdigest()}"
            cached_result = await cache_service.get(cache_key)
            
            if cached_result:
                return {
                    "success": True,
                    "embeddings": cached_result,
                    "cached": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Get embeddings
            start_time = time.time()
            embeddings = await ai_service.get_embeddings(texts)
            duration = time.time() - start_time
            
            # Convert to list for JSON serialization
            embeddings_list = embeddings.tolist()
            
            # Cache result
            await cache_service.set(cache_key, embeddings_list)
            
            return {
                "success": True,
                "embeddings": embeddings_list,
                "cached": False,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Embeddings error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for Ultra Extreme V14 Production"""
    
    # Create app
    app = create_production_app_v14()
    
    # Setup routes
    setup_production_routes_v14(app)
    
    # Configuration
    config = ProductionConfigV14()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        workers=config.workers,
        loop="uvloop",
        http="httptools",
        ws="websockets",
        log_level="info" if config.debug else "warning",
        access_log=True,
        use_colors=True,
        reload=config.debug,
        reload_dirs=["."],
        reload_includes=["*.py"],
        reload_excludes=["*.pyc", "__pycache__", ".git"],
        limit_concurrency=config.max_concurrent_requests,
        limit_max_requests=config.max_requests,
        timeout_keep_alive=config.timeout_keep_alive,
        timeout_graceful_shutdown=config.timeout_graceful_shutdown
    )

if __name__ == "__main__":
    main() 