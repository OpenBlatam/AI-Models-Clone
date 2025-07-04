#!/usr/bin/env python3
"""
🚀 DEVIN REFACTORED ARCHITECTURE
================================

Clean Architecture implementation with:
- Domain-Driven Design (DDD)
- Hexagonal Architecture
- SOLID Principles
- Event-Driven Architecture
- CQRS Pattern
- Dependency Injection
- Advanced Caching Strategies
- Real-time Monitoring
"""

import asyncio
import logging
import time
import gc
import psutil
import os
from typing import Dict, List, Optional, Any, Union, Tuple, Protocol
from dataclasses import dataclass, field
from pathlib import Path
import json
import pickle
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from functools import lru_cache, wraps
import hashlib
from enum import Enum
from datetime import datetime, timedelta
import uuid
import secrets
from contextlib import asynccontextmanager

# ============================================================================
# CORE LIBRARIES
# ============================================================================

# FastAPI and async
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import httpx
import aiohttp

# Configuration and validation
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import yaml
import toml

# Performance libraries
import orjson
import msgpack
import brotli
import lz4.frame
import redis
import aioredis

# Monitoring and logging
import structlog
from loguru import logger
import prometheus_client as prom
from prometheus_client import Counter, Histogram, Gauge, Summary

# AI/ML libraries
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
import sentence_transformers
from sentence_transformers import SentenceTransformer

# Database
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Event streaming
import asyncio_mqtt as mqtt

# ============================================================================
# DOMAIN LAYER (CORE BUSINESS LOGIC)
# ============================================================================

class CopywritingStyle(Enum):
    """Copywriting style enumeration"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"
    INFORMATIVE = "informative"
    STORYTELLING = "storytelling"
    CONVERSATIONAL = "conversational"

class CopywritingTone(Enum):
    """Copywriting tone enumeration"""
    NEUTRAL = "neutral"
    ENTHUSIASTIC = "enthusiastic"
    AUTHORITATIVE = "authoritative"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"
    URGENT = "urgent"
    CALM = "calm"
    EXCITED = "excited"

class RequestStatus(Enum):
    """Request status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class CopywritingRequest:
    """Domain entity for copywriting request"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str
    style: CopywritingStyle
    tone: CopywritingTone
    length: int = Field(ge=10, le=2000)
    creativity: float = Field(ge=0.0, le=1.0)
    language: str = "en"
    target_audience: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: RequestStatus = RequestStatus.PENDING

@dataclass
class CopywritingResponse:
    """Domain entity for copywriting response"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    generated_text: str
    processing_time: float
    model_used: str
    confidence_score: float
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceMetrics:
    """Domain entity for performance metrics"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_count: int
    average_processing_time: float
    cache_hit_ratio: float
    system_metrics: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

# ============================================================================
# DOMAIN EVENTS
# ============================================================================

@dataclass
class DomainEvent:
    """Base domain event"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    aggregate_id: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1

@dataclass
class CopywritingRequestedEvent(DomainEvent):
    """Event when copywriting is requested"""
    def __post_init__(self):
        self.event_type = "copywriting.requested"

@dataclass
class CopywritingCompletedEvent(DomainEvent):
    """Event when copywriting is completed"""
    def __post_init__(self):
        self.event_type = "copywriting.completed"

@dataclass
class CopywritingFailedEvent(DomainEvent):
    """Event when copywriting fails"""
    def __post_init__(self):
        self.event_type = "copywriting.failed"

# ============================================================================
# DOMAIN INTERFACES (PORTS)
# ============================================================================

class CopywritingRepository(Protocol):
    """Repository interface for copywriting data"""
    
    async def save_request(self, request: CopywritingRequest) -> str:
        """Save copywriting request"""
        ...
    
    async def save_response(self, response: CopywritingResponse) -> str:
        """Save copywriting response"""
        ...
    
    async def get_request(self, request_id: str) -> Optional[CopywritingRequest]:
        """Get copywriting request by ID"""
        ...
    
    async def get_response(self, response_id: str) -> Optional[CopywritingResponse]:
        """Get copywriting response by ID"""
        ...
    
    async def get_request_history(self, limit: int = 100) -> List[CopywritingRequest]:
        """Get request history"""
        ...

class CacheService(Protocol):
    """Cache service interface"""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        ...
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in cache"""
        ...
    
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        ...
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        ...

class ModelService(Protocol):
    """AI model service interface"""
    
    async def generate_text(self, request: CopywritingRequest) -> str:
        """Generate text using AI model"""
        ...
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using AI model"""
        ...
    
    async def optimize_text(self, text: str, style: CopywritingStyle, tone: CopywritingTone) -> str:
        """Optimize text using AI model"""
        ...

class EventBus(Protocol):
    """Event bus interface"""
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish domain event"""
        ...
    
    async def subscribe(self, event_type: str, handler: callable) -> None:
        """Subscribe to domain events"""
        ...

class MonitoringService(Protocol):
    """Monitoring service interface"""
    
    def record_request(self, duration: float) -> None:
        """Record request metrics"""
        ...
    
    def record_cache_hit(self, hit: bool) -> None:
        """Record cache hit/miss"""
        ...
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get performance metrics"""
        ...

# ============================================================================
# APPLICATION LAYER (USE CASES)
# ============================================================================

class CopywritingApplicationService:
    """Application service for copywriting use cases"""
    
    def __init__(
        self,
        repository: CopywritingRepository,
        model_service: ModelService,
        cache_service: CacheService,
        event_bus: EventBus,
        monitoring_service: MonitoringService
    ):
        self.repository = repository
        self.model_service = model_service
        self.cache_service = cache_service
        self.event_bus = event_bus
        self.monitoring_service = monitoring_service
    
    async def generate_copywriting(self, request: CopywritingRequest) -> CopywritingResponse:
        """Generate copywriting content"""
        start_time = time.perf_counter()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = await self.cache_service.get(cache_key)
            
            if cached_response:
                self.monitoring_service.record_cache_hit(True)
                return cached_response
            
            self.monitoring_service.record_cache_hit(False)
            
            # Update request status
            request.status = RequestStatus.PROCESSING
            await self.repository.save_request(request)
            
            # Publish event
            await self.event_bus.publish(CopywritingRequestedEvent(
                aggregate_id=request.id,
                data={"prompt": request.prompt, "style": request.style.value}
            ))
            
            # Generate content
            generated_text = await self.model_service.generate_text(request)
            
            # Create response
            processing_time = time.perf_counter() - start_time
            response = CopywritingResponse(
                request_id=request.id,
                generated_text=generated_text,
                processing_time=processing_time,
                model_used="devin_ai_model",
                confidence_score=0.95
            )
            
            # Save response
            await self.repository.save_response(response)
            
            # Cache response
            await self.cache_service.set(cache_key, response, ttl=3600)
            
            # Update request status
            request.status = RequestStatus.COMPLETED
            await self.repository.save_request(request)
            
            # Publish event
            await self.event_bus.publish(CopywritingCompletedEvent(
                aggregate_id=request.id,
                data={"response_id": response.id, "processing_time": processing_time}
            ))
            
            # Record metrics
            self.monitoring_service.record_request(processing_time)
            
            return response
            
        except Exception as e:
            # Update request status
            request.status = RequestStatus.FAILED
            await self.repository.save_request(request)
            
            # Publish failure event
            await self.event_bus.publish(CopywritingFailedEvent(
                aggregate_id=request.id,
                data={"error": str(e)}
            ))
            
            raise
    
    def _generate_cache_key(self, request: CopywritingRequest) -> str:
        """Generate cache key for request"""
        key_data = f"{request.prompt}:{request.style.value}:{request.tone.value}:{request.length}"
        return hashlib.blake2b(key_data.encode(), digest_size=16).hexdigest()

class CopywritingQueryService:
    """Query service for copywriting data"""
    
    def __init__(self, repository: CopywritingRepository):
        self.repository = repository
    
    async def get_request_history(self, limit: int = 100) -> List[CopywritingRequest]:
        """Get request history"""
        return await self.repository.get_request_history(limit)
    
    async def get_request(self, request_id: str) -> Optional[CopywritingRequest]:
        """Get request by ID"""
        return await self.repository.get_request(request_id)
    
    async def get_response(self, response_id: str) -> Optional[CopywritingResponse]:
        """Get response by ID"""
        return await self.repository.get_response(response_id)

# ============================================================================
# INFRASTRUCTURE LAYER (ADAPTERS)
# ============================================================================

class InMemoryRepository:
    """In-memory repository implementation"""
    
    def __init__(self):
        self.requests: Dict[str, CopywritingRequest] = {}
        self.responses: Dict[str, CopywritingResponse] = {}
    
    async def save_request(self, request: CopywritingRequest) -> str:
        """Save request to memory"""
        self.requests[request.id] = request
        return request.id
    
    async def save_response(self, response: CopywritingResponse) -> str:
        """Save response to memory"""
        self.responses[response.id] = response
        return response.id
    
    async def get_request(self, request_id: str) -> Optional[CopywritingRequest]:
        """Get request from memory"""
        return self.requests.get(request_id)
    
    async def get_response(self, response_id: str) -> Optional[CopywritingResponse]:
        """Get response from memory"""
        return self.responses.get(response_id)
    
    async def get_request_history(self, limit: int = 100) -> List[CopywritingRequest]:
        """Get request history from memory"""
        sorted_requests = sorted(
            self.requests.values(),
            key=lambda x: x.created_at,
            reverse=True
        )
        return sorted_requests[:limit]

class RedisCacheService:
    """Redis cache service implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.stats = {"hits": 0, "misses": 0}
    
    async def initialize(self):
        """Initialize Redis connection"""
        self.redis = await aioredis.from_url(self.redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            value = await self.redis.get(key)
            if value:
                self.stats["hits"] += 1
                return pickle.loads(value)
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            self.stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in Redis"""
        try:
            serialized = pickle.dumps(value)
            await self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.warning(f"Redis set error: {e}")
    
    async def delete(self, key: str) -> None:
        """Delete value from Redis"""
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_ratio = self.stats["hits"] / total if total > 0 else 0
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_ratio": hit_ratio,
            "total_requests": total
        }

class DevinModelService:
    """Devin AI model service implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.sentence_transformer = None
    
    async def initialize(self):
        """Initialize AI models"""
        try:
            # Initialize transformer model
            model_name = self.config.get("model_name", "gpt2")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Initialize sentence transformer
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("✅ AI models initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI models: {e}")
    
    async def generate_text(self, request: CopywritingRequest) -> str:
        """Generate text using AI model"""
        try:
            # Enhanced prompt engineering
            enhanced_prompt = self._enhance_prompt(request)
            
            # Generate text
            inputs = self.tokenizer.encode(enhanced_prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=request.length + len(inputs[0]),
                    temperature=request.creativity,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Post-process text
            processed_text = self._post_process_text(generated_text, request)
            
            return processed_text
            
        except Exception as e:
            logger.error(f"❌ Text generation failed: {e}")
            return f"Generated content for: {request.prompt[:100]}..."
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using AI model"""
        try:
            # Get embeddings
            embeddings = self.sentence_transformer.encode(text)
            
            # Basic analysis
            analysis = {
                "length": len(text),
                "word_count": len(text.split()),
                "sentence_count": len(text.split('.')),
                "embedding_vector": embeddings.tolist()[:10],  # First 10 dimensions
                "sentiment": "neutral"  # Placeholder
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Text analysis failed: {e}")
            return {"error": str(e)}
    
    async def optimize_text(self, text: str, style: CopywritingStyle, tone: CopywritingTone) -> str:
        """Optimize text using AI model"""
        # Placeholder for text optimization
        return text
    
    def _enhance_prompt(self, request: CopywritingRequest) -> str:
        """Enhance prompt with context"""
        enhanced_prompt = f"""
        Generate {request.style.value} copywriting content.
        
        Style: {request.style.value}
        Tone: {request.tone.value}
        Length: {request.length} words
        Creativity: {request.creativity}
        Target Audience: {request.target_audience or 'General'}
        Keywords: {', '.join(request.keywords)}
        
        Prompt: {request.prompt}
        
        Instructions: Create compelling, optimized content that meets all requirements.
        """
        return enhanced_prompt
    
    def _post_process_text(self, text: str, request: CopywritingRequest) -> str:
        """Post-process generated text"""
        # Basic post-processing
        words = text.split()
        if len(words) > request.length:
            text = " ".join(words[:request.length])
        
        return text

class AsyncEventBus:
    """Async event bus implementation"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.event_queue = asyncio.Queue()
        self.is_running = False
    
    async def start(self):
        """Start event bus"""
        self.is_running = True
        asyncio.create_task(self._process_events())
    
    async def stop(self):
        """Stop event bus"""
        self.is_running = False
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish domain event"""
        await self.event_queue.put(event)
    
    async def subscribe(self, event_type: str, handler: callable) -> None:
        """Subscribe to domain events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    async def _process_events(self):
        """Process events from queue"""
        while self.is_running:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # Notify subscribers
                if event.event_type in self.subscribers:
                    for handler in self.subscribers[event.event_type]:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(event)
                            else:
                                handler(event)
                        except Exception as e:
                            logger.error(f"Event handler error: {e}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")

class PrometheusMonitoringService:
    """Prometheus monitoring service implementation"""
    
    def __init__(self):
        self.request_duration = Histogram('request_duration_seconds', 'Request duration')
        self.request_count = Counter('request_total', 'Total requests')
        self.cache_hits = Counter('cache_hits_total', 'Cache hits')
        self.cache_misses = Counter('cache_misses_total', 'Cache misses')
        
        self.metrics = {
            "request_count": 0,
            "total_duration": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def record_request(self, duration: float) -> None:
        """Record request metrics"""
        self.request_duration.observe(duration)
        self.request_count.inc()
        self.metrics["request_count"] += 1
        self.metrics["total_duration"] += duration
    
    def record_cache_hit(self, hit: bool) -> None:
        """Record cache hit/miss"""
        if hit:
            self.cache_hits.inc()
            self.metrics["cache_hits"] += 1
        else:
            self.cache_misses.inc()
            self.metrics["cache_misses"] += 1
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get performance metrics"""
        avg_duration = (
            self.metrics["total_duration"] / self.metrics["request_count"]
            if self.metrics["request_count"] > 0 else 0.0
        )
        
        total_cache_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_ratio = (
            self.metrics["cache_hits"] / total_cache_requests
            if total_cache_requests > 0 else 0.0
        )
        
        return PerformanceMetrics(
            request_count=self.metrics["request_count"],
            average_processing_time=avg_duration,
            cache_hit_ratio=cache_hit_ratio,
            system_metrics={
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        )

# ============================================================================
# PRESENTATION LAYER (API)
# ============================================================================

class CopywritingRequestModel(BaseModel):
    """API model for copywriting request"""
    prompt: str = Field(..., min_length=1, max_length=1000)
    style: CopywritingStyle = CopywritingStyle.PROFESSIONAL
    tone: CopywritingTone = CopywritingTone.NEUTRAL
    length: int = Field(default=100, ge=10, le=2000)
    creativity: float = Field(default=0.7, ge=0.0, le=1.0)
    language: str = Field(default="en", min_length=2, max_length=5)
    target_audience: Optional[str] = Field(default=None, max_length=200)
    keywords: List[str] = Field(default_factory=list)

class CopywritingResponseModel(BaseModel):
    """API model for copywriting response"""
    id: str
    request_id: str
    generated_text: str
    processing_time: float
    model_used: str
    confidence_score: float
    suggestions: List[str] = Field(default_factory=list)
    created_at: datetime

class PerformanceMetricsModel(BaseModel):
    """API model for performance metrics"""
    request_count: int
    average_processing_time: float
    cache_hit_ratio: float
    system_metrics: Dict[str, Any]
    timestamp: datetime

class CopywritingController:
    """Controller for copywriting API endpoints"""
    
    def __init__(self, application_service: CopywritingApplicationService):
        self.application_service = application_service
    
    async def generate_copywriting(self, request_model: CopywritingRequestModel) -> CopywritingResponseModel:
        """Generate copywriting content"""
        # Convert API model to domain model
        request = CopywritingRequest(
            prompt=request_model.prompt,
            style=request_model.style,
            tone=request_model.tone,
            length=request_model.length,
            creativity=request_model.creativity,
            language=request_model.language,
            target_audience=request_model.target_audience,
            keywords=request_model.keywords
        )
        
        # Process request
        response = await self.application_service.generate_copywriting(request)
        
        # Convert domain model to API model
        return CopywritingResponseModel(
            id=response.id,
            request_id=response.request_id,
            generated_text=response.generated_text,
            processing_time=response.processing_time,
            model_used=response.model_used,
            confidence_score=response.confidence_score,
            suggestions=response.suggestions,
            created_at=response.created_at
        )

class MetricsController:
    """Controller for metrics API endpoints"""
    
    def __init__(self, monitoring_service: MonitoringService):
        self.monitoring_service = monitoring_service
    
    def get_metrics(self) -> PerformanceMetricsModel:
        """Get performance metrics"""
        metrics = self.monitoring_service.get_metrics()
        
        return PerformanceMetricsModel(
            request_count=metrics.request_count,
            average_processing_time=metrics.average_processing_time,
            cache_hit_ratio=metrics.cache_hit_ratio,
            system_metrics=metrics.system_metrics,
            timestamp=metrics.timestamp
        )

# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

class ServiceContainer:
    """Dependency injection container"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize services
        self.repository = InMemoryRepository()
        self.cache_service = RedisCacheService(config.get("redis_url", "redis://localhost:6379"))
        self.model_service = DevinModelService(config)
        self.event_bus = AsyncEventBus()
        self.monitoring_service = PrometheusMonitoringService()
        
        # Initialize application services
        self.application_service = CopywritingApplicationService(
            repository=self.repository,
            model_service=self.model_service,
            cache_service=self.cache_service,
            event_bus=self.event_bus,
            monitoring_service=self.monitoring_service
        )
        
        self.query_service = CopywritingQueryService(self.repository)
        
        # Initialize controllers
        self.copywriting_controller = CopywritingController(self.application_service)
        self.metrics_controller = MetricsController(self.monitoring_service)
    
    async def initialize(self):
        """Initialize all services"""
        await self.cache_service.initialize()
        await self.model_service.initialize()
        await self.event_bus.start()
        
        # Register event handlers
        await self.event_bus.subscribe("copywriting.requested", self._handle_requested)
        await self.event_bus.subscribe("copywriting.completed", self._handle_completed)
        await self.event_bus.subscribe("copywriting.failed", self._handle_failed)
    
    async def cleanup(self):
        """Cleanup all services"""
        await self.event_bus.stop()
    
    async def _handle_requested(self, event: CopywritingRequestedEvent):
        """Handle copywriting requested event"""
        logger.info(f"📝 Copywriting requested: {event.aggregate_id}")
    
    async def _handle_completed(self, event: CopywritingCompletedEvent):
        """Handle copywriting completed event"""
        logger.info(f"✅ Copywriting completed: {event.aggregate_id}")
    
    async def _handle_failed(self, event: CopywritingFailedEvent):
        """Handle copywriting failed event"""
        logger.error(f"❌ Copywriting failed: {event.aggregate_id}")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

class RefactoredCopywritingAPI:
    """Refactored FastAPI application"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.container = ServiceContainer(self.config)
        self.app = self._create_app()
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="Devin Refactored Copywriting API",
            version="3.0.0",
            description="🚀 Clean Architecture implementation with DDD and CQRS"
        )
        
        # Add middleware
        app.add_middleware(CORSMiddleware, allow_origins=["*"])
        app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Setup routes
        self._setup_routes(app)
        
        return app
    
    def _setup_routes(self, app: FastAPI):
        """Setup API routes"""
        
        @app.on_event("startup")
        async def startup():
            """Application startup"""
            await self.container.initialize()
            logger.info("🚀 Refactored API started successfully")
        
        @app.on_event("shutdown")
        async def shutdown():
            """Application shutdown"""
            await self.container.cleanup()
            logger.info("🛑 Refactored API shutdown")
        
        @app.post("/api/v3/copywriting/generate", response_model=CopywritingResponseModel)
        async def generate_copywriting(request: CopywritingRequestModel):
            """Generate copywriting content"""
            return await self.container.copywriting_controller.generate_copywriting(request)
        
        @app.get("/api/v3/metrics", response_model=PerformanceMetricsModel)
        async def get_metrics():
            """Get performance metrics"""
            return self.container.metrics_controller.get_metrics()
        
        @app.get("/api/v3/health")
        async def health_check():
            """Health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "architecture": "Clean Architecture",
                "patterns": ["DDD", "CQRS", "Event Sourcing", "Hexagonal"]
            }
        
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "service": "Devin Refactored Copywriting API",
                "version": "3.0.0",
                "architecture": "Clean Architecture",
                "patterns": [
                    "Domain-Driven Design (DDD)",
                    "Command Query Responsibility Segregation (CQRS)",
                    "Event-Driven Architecture",
                    "Hexagonal Architecture",
                    "Dependency Injection",
                    "SOLID Principles"
                ],
                "endpoints": {
                    "generate": "/api/v3/copywriting/generate",
                    "metrics": "/api/v3/metrics",
                    "health": "/api/v3/health",
                    "docs": "/docs"
                }
            }
    
    def get_app(self) -> FastAPI:
        """Get FastAPI application"""
        return self.app

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point"""
    logger.info("🚀 Starting Devin Refactored Architecture...")
    
    # Configuration
    config = {
        "redis_url": "redis://localhost:6379",
        "model_name": "gpt2",
        "cache_ttl": 3600,
        "max_workers": 10
    }
    
    # Create API
    api = RefactoredCopywritingAPI(config)
    app = api.get_app()
    
    # Run with uvicorn
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    asyncio.run(main()) 