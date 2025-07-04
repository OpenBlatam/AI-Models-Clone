#!/usr/bin/env python3
"""
🏗️ DEVIN CLEAN ARCHITECTURE
============================

Clean Architecture implementation with:
- Domain Layer (Core Business Logic)
- Application Layer (Use Cases)
- Infrastructure Layer (External Concerns)
- Presentation Layer (API Controllers)
- Dependency Injection
- SOLID Principles
- Event-Driven Architecture
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

# FastAPI
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Pydantic
from pydantic import BaseModel, Field

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

class CopywritingTone(Enum):
    """Copywriting tone enumeration"""
    NEUTRAL = "neutral"
    ENTHUSIASTIC = "enthusiastic"
    AUTHORITATIVE = "authoritative"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"
    URGENT = "urgent"

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
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CopywritingResponse:
    """Domain entity for copywriting response"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    generated_text: str
    processing_time: float
    model_used: str
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.now)

# ============================================================================
# DOMAIN INTERFACES (PORTS)
# ============================================================================

class CopywritingRepository(Protocol):
    """Repository interface"""
    async def save_request(self, request: CopywritingRequest) -> str:
        ...
    
    async def save_response(self, response: CopywritingResponse) -> str:
        ...
    
    async def get_request(self, request_id: str) -> Optional[CopywritingRequest]:
        ...
    
    async def get_response(self, response_id: str) -> Optional[CopywritingResponse]:
        ...

class AIService(Protocol):
    """AI service interface"""
    async def generate_text(self, request: CopywritingRequest) -> str:
        ...
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        ...

class CacheService(Protocol):
    """Cache service interface"""
    async def get(self, key: str) -> Optional[Any]:
        ...
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        ...

class EventPublisher(Protocol):
    """Event publisher interface"""
    async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        ...

# ============================================================================
# APPLICATION LAYER (USE CASES)
# ============================================================================

class GenerateCopywritingUseCase:
    """Use case for generating copywriting"""
    
    def __init__(
        self,
        repository: CopywritingRepository,
        ai_service: AIService,
        cache_service: CacheService,
        event_publisher: EventPublisher
    ):
        self.repository = repository
        self.ai_service = ai_service
        self.cache_service = cache_service
        self.event_publisher = event_publisher
    
    async def execute(self, request: CopywritingRequest) -> CopywritingResponse:
        """Execute the use case"""
        start_time = time.time()
        
        # Check cache
        cache_key = self._generate_cache_key(request)
        cached_response = await self.cache_service.get(cache_key)
        
        if cached_response:
            return cached_response
        
        # Generate content
        generated_text = await self.ai_service.generate_text(request)
        
        # Create response
        processing_time = time.time() - start_time
        response = CopywritingResponse(
            request_id=request.id,
            generated_text=generated_text,
            processing_time=processing_time,
            model_used="devin_ai",
            confidence_score=0.95
        )
        
        # Save to repository
        await self.repository.save_request(request)
        await self.repository.save_response(response)
        
        # Cache response
        await self.cache_service.set(cache_key, response)
        
        # Publish event
        await self.event_publisher.publish(
            "copywriting.generated",
            {"request_id": request.id, "response_id": response.id}
        )
        
        return response
    
    def _generate_cache_key(self, request: CopywritingRequest) -> str:
        """Generate cache key"""
        return f"copywriting:{request.prompt}:{request.style.value}:{request.tone.value}"

class GetCopywritingHistoryUseCase:
    """Use case for getting copywriting history"""
    
    def __init__(self, repository: CopywritingRepository):
        self.repository = repository
    
    async def execute(self, limit: int = 100) -> List[CopywritingRequest]:
        """Execute the use case"""
        # This would be implemented in the repository
        return []

# ============================================================================
# INFRASTRUCTURE LAYER (ADAPTERS)
# ============================================================================

class InMemoryRepository:
    """In-memory repository implementation"""
    
    def __init__(self):
        self.requests: Dict[str, CopywritingRequest] = {}
        self.responses: Dict[str, CopywritingResponse] = {}
    
    async def save_request(self, request: CopywritingRequest) -> str:
        self.requests[request.id] = request
        return request.id
    
    async def save_response(self, response: CopywritingResponse) -> str:
        self.responses[response.id] = response
        return response.id
    
    async def get_request(self, request_id: str) -> Optional[CopywritingRequest]:
        return self.requests.get(request_id)
    
    async def get_response(self, response_id: str) -> Optional[CopywritingResponse]:
        return self.responses.get(response_id)

class DevinAIService:
    """Devin AI service implementation"""
    
    async def generate_text(self, request: CopywritingRequest) -> str:
        """Generate text using AI"""
        # Enhanced prompt
        enhanced_prompt = f"""
        Generate {request.style.value} copywriting content.
        
        Style: {request.style.value}
        Tone: {request.tone.value}
        Length: {request.length} words
        Creativity: {request.creativity}
        Target Audience: {request.target_audience or 'General'}
        Keywords: {', '.join(request.keywords)}
        
        Prompt: {request.prompt}
        
        Instructions: Create compelling, optimized content.
        """
        
        # Placeholder for AI generation
        return f"Generated {request.style.value} content: {request.prompt[:100]}..."
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text"""
        return {
            "length": len(text),
            "word_count": len(text.split()),
            "sentiment": "positive"
        }

class InMemoryCacheService:
    """In-memory cache service implementation"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        self.cache[key] = value

class AsyncEventPublisher:
    """Async event publisher implementation"""
    
    async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish event"""
        print(f"📢 Event published: {event_type} - {data}")

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
    language: str = Field(default="en")
    target_audience: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)

class CopywritingResponseModel(BaseModel):
    """API model for copywriting response"""
    id: str
    request_id: str
    generated_text: str
    processing_time: float
    model_used: str
    confidence_score: float
    created_at: datetime

class CopywritingController:
    """Controller for copywriting endpoints"""
    
    def __init__(self, generate_use_case: GenerateCopywritingUseCase):
        self.generate_use_case = generate_use_case
    
    async def generate_copywriting(self, request_model: CopywritingRequestModel) -> CopywritingResponseModel:
        """Generate copywriting"""
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
        
        # Execute use case
        response = await self.generate_use_case.execute(request)
        
        # Convert domain model to API model
        return CopywritingResponseModel(
            id=response.id,
            request_id=response.request_id,
            generated_text=response.generated_text,
            processing_time=response.processing_time,
            model_used=response.model_used,
            confidence_score=response.confidence_score,
            created_at=response.created_at
        )

# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

class ServiceContainer:
    """Dependency injection container"""
    
    def __init__(self):
        # Infrastructure services
        self.repository = InMemoryRepository()
        self.ai_service = DevinAIService()
        self.cache_service = InMemoryCacheService()
        self.event_publisher = AsyncEventPublisher()
        
        # Use cases
        self.generate_use_case = GenerateCopywritingUseCase(
            repository=self.repository,
            ai_service=self.ai_service,
            cache_service=self.cache_service,
            event_publisher=self.event_publisher
        )
        
        # Controllers
        self.copywriting_controller = CopywritingController(self.generate_use_case)

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

class CleanArchitectureAPI:
    """Clean Architecture FastAPI application"""
    
    def __init__(self):
        self.container = ServiceContainer()
        self.app = self._create_app()
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="Devin Clean Architecture API",
            version="1.0.0",
            description="🏗️ Clean Architecture implementation"
        )
        
        # Add middleware
        app.add_middleware(CORSMiddleware, allow_origins=["*"])
        
        # Setup routes
        self._setup_routes(app)
        
        return app
    
    def _setup_routes(self, app: FastAPI):
        """Setup API routes"""
        
        @app.post("/api/v1/copywriting/generate", response_model=CopywritingResponseModel)
        async def generate_copywriting(request: CopywritingRequestModel):
            """Generate copywriting content"""
            return await self.container.copywriting_controller.generate_copywriting(request)
        
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "service": "Devin Clean Architecture API",
                "version": "1.0.0",
                "architecture": "Clean Architecture",
                "layers": [
                    "Domain Layer (Core Business Logic)",
                    "Application Layer (Use Cases)",
                    "Infrastructure Layer (External Concerns)",
                    "Presentation Layer (API Controllers)"
                ],
                "principles": [
                    "SOLID Principles",
                    "Dependency Inversion",
                    "Separation of Concerns",
                    "Single Responsibility"
                ]
            }
    
    def get_app(self) -> FastAPI:
        """Get FastAPI application"""
        return self.app

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point"""
    print("🏗️ Starting Devin Clean Architecture...")
    
    # Create API
    api = CleanArchitectureAPI()
    app = api.get_app()
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    asyncio.run(main()) 