#!/usr/bin/env python3
"""
ENHANCED PRODUCTION SYSTEM
High-quality production system with comprehensive quality assurance
"""

import os
import sys
import asyncio
import logging
import threading
import time
import gc
import psutil
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, validator
import orjson
from loguru import logger

# Import our quality improvement systems
from advanced_memory_manager import get_memory_manager, track_memory_async
from unified_connection_pool import get_connection_manager, with_connection
from unified_error_handler import get_error_handler, handle_errors, ErrorCategory
from centralized_config_manager import get_config_manager, get_config, get_config_section
from code_quality_manager import get_quality_manager, analyze_code_quality
from comprehensive_testing_framework import get_testing_framework, run_comprehensive_tests
from security_validation_system import get_security_validator, sanitize_input, validate_password

# Initialize all quality systems
memory_manager = get_memory_manager()
connection_manager = get_connection_manager()
error_handler = get_error_handler()
config_manager = get_config_manager()
quality_manager = get_quality_manager()
testing_framework = get_testing_framework()
security_validator = get_security_validator()

# Enhanced configuration with quality settings
QUALITY_CONFIG = {
    "code_quality": {
        "min_score": 85.0,
        "auto_format": True,
        "strict_linting": True,
        "type_checking": True
    },
    "testing": {
        "min_coverage": 95.0,
        "run_tests_on_startup": True,
        "performance_threshold": 100.0,
        "security_threshold": 90.0
    },
    "security": {
        "input_validation": True,
        "rate_limiting": True,
        "encryption": True,
        "session_management": True
    },
    "monitoring": {
        "real_time_metrics": True,
        "quality_tracking": True,
        "performance_monitoring": True,
        "security_monitoring": True
    }
}

# Load quality configuration
config_manager.load_config_from_dict(QUALITY_CONFIG)

# Memory optimization with quality monitoring
gc.set_threshold(1000, 10, 10)

# Enhanced logging with quality tracking
logging_config = get_config_section("logging")
if logging_config and logging_config.file_path:
    logger.add(
        logging_config.file_path,
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )

# GPU optimization with quality checks
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False

# Performance optimization with quality thresholds
performance_config = get_config_section("performance")
if performance_config:
    CACHE_TTL = performance_config.cache_ttl
    MAX_MEMORY_USAGE = performance_config.max_memory_usage
    BATCH_SIZE = performance_config.batch_size
    QUALITY_THRESHOLD = performance_config.quality_threshold
else:
    CACHE_TTL = 3600
    MAX_MEMORY_USAGE = 1073741824  # 1GB
    BATCH_SIZE = 1000
    QUALITY_THRESHOLD = 85.0

# CPU optimization with quality monitoring
CPU_COUNT = os.cpu_count()
THREAD_POOL = ThreadPoolExecutor(max_workers=CPU_COUNT * 3)
PROCESS_POOL = ProcessPoolExecutor(max_workers=CPU_COUNT)

# Enhanced performance tracking
CACHE = {}
CONNECTION_POOL = {}
RATE_LIMITER = {}
QUALITY_METRICS = {}

# Enhanced configuration with quality validation
CONFIG = {
    "model_quantization": get_config("model.quantization", True),
    "mixed_precision": get_config("model.mixed_precision", True),
    "gradient_accumulation": get_config("model.gradient_accumulation", True),
    "distributed_training": get_config("model.distributed_training", True),
    "batch_inference": get_config("model.batch_inference", True),
    "model_caching": get_config("model.caching", True),
    "prefetching": get_config("model.prefetching", True),
    "parallel_loading": get_config("model.parallel_loading", True),
    "load_balancing": get_config("model.load_balancing", True),
    "auto_scaling": get_config("model.auto_scaling", True),
    "quality_assurance": get_config("quality.enabled", True),
    "security_validation": get_config("security.enabled", True),
    "testing_automation": get_config("testing.enabled", True)
}

# Enhanced security validation patterns
SECURITY_PATTERNS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "password": r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$",
    "api_key": r"^[a-zA-Z0-9]{32,}$",
    "model_name": r"^[a-zA-Z0-9_-]{3,50}$",
    "file_path": r"^[a-zA-Z0-9/._-]+$"
}

# Enhanced Deep Learning Models with quality tracking
class QualityAwareTransformerModel(nn.Module):
    """Transformer model with quality monitoring."""
    
    def __init__(self, vocab_size: int, d_model: int = 512, nhead: int = 8, num_layers: int = 6):
        super().__init__()
        self.quality_metrics = {"inference_count": 0, "avg_inference_time": 0.0}
        
        # Enhanced model architecture with quality monitoring
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model, nhead, batch_first=True),
            num_layers
        )
        self.output_layer = nn.Linear(d_model, vocab_size)
        
        # Quality-aware initialization
        self._initialize_with_quality()
    
    def _initialize_with_quality(self):
        """Initialize model with quality-aware techniques."""
        # Xavier initialization for better convergence
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    @track_memory_async
    def forward(self, x):
        """Forward pass with quality monitoring."""
        start_time = time.time()
        
        # Input validation
        if not isinstance(x, torch.Tensor):
            raise ValueError("Input must be a torch.Tensor")
        
        # Enhanced forward pass
        embedded = self.embedding(x)
        transformed = self.transformer(embedded)
        output = self.output_layer(transformed)
        
        # Quality metrics update
        inference_time = time.time() - start_time
        self.quality_metrics["inference_count"] += 1
        self.quality_metrics["avg_inference_time"] = (
            (self.quality_metrics["avg_inference_time"] * (self.quality_metrics["inference_count"] - 1) + inference_time) /
            self.quality_metrics["inference_count"]
        )
        
        return output
    
    def get_quality_metrics(self):
        """Get model quality metrics."""
        return self.quality_metrics

class QualityAwareDiffusionModel(nn.Module):
    """Diffusion model with quality monitoring."""
    
    def __init__(self, in_channels: int = 3, out_channels: int = 3):
        super().__init__()
        self.quality_metrics = {"generation_count": 0, "avg_generation_time": 0.0}
        
        # Enhanced diffusion architecture
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Conv2d(128, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, out_channels, 3, padding=1),
            nn.Sigmoid()
        )
        
        self._initialize_with_quality()
    
    def _initialize_with_quality(self):
        """Initialize with quality-aware techniques."""
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    @track_memory_async
    def forward(self, x, t):
        """Forward pass with quality monitoring."""
        start_time = time.time()
        
        # Input validation
        if not isinstance(x, torch.Tensor) or not isinstance(t, torch.Tensor):
            raise ValueError("Inputs must be torch.Tensors")
        
        # Enhanced forward pass
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        
        # Quality metrics update
        generation_time = time.time() - start_time
        self.quality_metrics["generation_count"] += 1
        self.quality_metrics["avg_generation_time"] = (
            (self.quality_metrics["avg_generation_time"] * (self.quality_metrics["generation_count"] - 1) + generation_time) /
            self.quality_metrics["generation_count"]
        )
        
        return decoded
    
    def get_quality_metrics(self):
        """Get model quality metrics."""
        return self.quality_metrics

class QualityAwareLLMModel(nn.Module):
    """LLM model with quality monitoring."""
    
    def __init__(self, vocab_size: int, hidden_size: int = 768, num_layers: int = 12):
        super().__init__()
        self.quality_metrics = {"completion_count": 0, "avg_completion_time": 0.0}
        
        # Enhanced LLM architecture
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.transformer_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(hidden_size, batch_first=True)
            for _ in range(num_layers)
        ])
        self.output_layer = nn.Linear(hidden_size, vocab_size)
        
        self._initialize_with_quality()
    
    def _initialize_with_quality(self):
        """Initialize with quality-aware techniques."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
    
    @track_memory_async
    def forward(self, x):
        """Forward pass with quality monitoring."""
        start_time = time.time()
        
        # Input validation
        if not isinstance(x, torch.Tensor):
            raise ValueError("Input must be a torch.Tensor")
        
        # Enhanced forward pass
        embedded = self.embedding(x)
        for layer in self.transformer_layers:
            embedded = layer(embedded)
        output = self.output_layer(embedded)
        
        # Quality metrics update
        completion_time = time.time() - start_time
        self.quality_metrics["completion_count"] += 1
        self.quality_metrics["avg_completion_time"] = (
            (self.quality_metrics["avg_completion_time"] * (self.quality_metrics["completion_count"] - 1) + completion_time) /
            self.quality_metrics["completion_count"]
        )
        
        return output
    
    def get_quality_metrics(self):
        """Get model quality metrics."""
        return self.quality_metrics

class EnhancedModelManager:
    """Enhanced model manager with quality assurance."""
    
    def __init__(self):
        self.models: Dict[str, nn.Module] = {}
        self.quality_metrics: Dict[str, Dict[str, Any]] = {}
        self.performance_history: Dict[str, List[float]] = {}
        
    @track_memory_async
    async def create_transformer(self, model_id: str, config: Dict) -> Dict:
        """Create transformer model with quality validation."""
        try:
            # Input validation
            sanitized_config = sanitize_input(config)
            
            # Quality check before creation
            quality_score = await self._assess_model_quality("transformer", sanitized_config)
            if quality_score < QUALITY_THRESHOLD:
                raise ValueError(f"Model quality score {quality_score} below threshold {QUALITY_THRESHOLD}")
            
            # Create model with quality monitoring
            model = QualityAwareTransformerModel(
                vocab_size=sanitized_config.get("vocab_size", 10000),
                d_model=sanitized_config.get("d_model", 512),
                nhead=sanitized_config.get("nhead", 8),
                num_layers=sanitized_config.get("num_layers", 6)
            )
            
            self.models[model_id] = model
            self.quality_metrics[model_id] = {
                "type": "transformer",
                "quality_score": quality_score,
                "created_at": datetime.now().isoformat(),
                "performance_metrics": model.get_quality_metrics()
            }
            
            return {
                "success": True,
                "model_id": model_id,
                "quality_score": quality_score,
                "message": "Transformer model created successfully"
            }
            
        except Exception as e:
            await error_handler.handle_error(e, {"operation": "create_transformer", "model_id": model_id})
            return {"success": False, "error": str(e)}
    
    @track_memory_async
    async def create_diffusion(self, model_id: str, config: Dict) -> Dict:
        """Create diffusion model with quality validation."""
        try:
            # Input validation
            sanitized_config = sanitize_input(config)
            
            # Quality check before creation
            quality_score = await self._assess_model_quality("diffusion", sanitized_config)
            if quality_score < QUALITY_THRESHOLD:
                raise ValueError(f"Model quality score {quality_score} below threshold {QUALITY_THRESHOLD}")
            
            # Create model with quality monitoring
            model = QualityAwareDiffusionModel(
                in_channels=sanitized_config.get("in_channels", 3),
                out_channels=sanitized_config.get("out_channels", 3)
            )
            
            self.models[model_id] = model
            self.quality_metrics[model_id] = {
                "type": "diffusion",
                "quality_score": quality_score,
                "created_at": datetime.now().isoformat(),
                "performance_metrics": model.get_quality_metrics()
            }
            
            return {
                "success": True,
                "model_id": model_id,
                "quality_score": quality_score,
                "message": "Diffusion model created successfully"
            }
            
        except Exception as e:
            await error_handler.handle_error(e, {"operation": "create_diffusion", "model_id": model_id})
            return {"success": False, "error": str(e)}
    
    @track_memory_async
    async def create_llm(self, model_id: str, config: Dict) -> Dict:
        """Create LLM model with quality validation."""
        try:
            # Input validation
            sanitized_config = sanitize_input(config)
            
            # Quality check before creation
            quality_score = await self._assess_model_quality("llm", sanitized_config)
            if quality_score < QUALITY_THRESHOLD:
                raise ValueError(f"Model quality score {quality_score} below threshold {QUALITY_THRESHOLD}")
            
            # Create model with quality monitoring
            model = QualityAwareLLMModel(
                vocab_size=sanitized_config.get("vocab_size", 50000),
                hidden_size=sanitized_config.get("hidden_size", 768),
                num_layers=sanitized_config.get("num_layers", 12)
            )
            
            self.models[model_id] = model
            self.quality_metrics[model_id] = {
                "type": "llm",
                "quality_score": quality_score,
                "created_at": datetime.now().isoformat(),
                "performance_metrics": model.get_quality_metrics()
            }
            
            return {
                "success": True,
                "model_id": model_id,
                "quality_score": quality_score,
                "message": "LLM model created successfully"
            }
            
        except Exception as e:
            await error_handler.handle_error(e, {"operation": "create_llm", "model_id": model_id})
            return {"success": False, "error": str(e)}
    
    async def _assess_model_quality(self, model_type: str, config: Dict) -> float:
        """Assess model quality before creation."""
        quality_score = 100.0
        
        # Check configuration completeness
        required_params = {
            "transformer": ["vocab_size", "d_model", "nhead", "num_layers"],
            "diffusion": ["in_channels", "out_channels"],
            "llm": ["vocab_size", "hidden_size", "num_layers"]
        }
        
        missing_params = [param for param in required_params.get(model_type, []) if param not in config]
        if missing_params:
            quality_score -= len(missing_params) * 10
        
        # Check parameter ranges
        if model_type == "transformer":
            if config.get("d_model", 0) < 128:
                quality_score -= 20
            if config.get("num_layers", 0) < 2:
                quality_score -= 15
        
        return max(quality_score, 0.0)
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive quality report."""
        return {
            "total_models": len(self.models),
            "quality_metrics": self.quality_metrics,
            "average_quality_score": sum(
                metrics.get("quality_score", 0) for metrics in self.quality_metrics.values()
            ) / len(self.quality_metrics) if self.quality_metrics else 0,
            "performance_history": self.performance_history
        }

# Enhanced Pydantic models with validation
class EnhancedModelCreate(BaseModel):
    """Enhanced model creation request with validation."""
    name: str = Field(..., description="Model name", min_length=3, max_length=50)
    type: str = Field(..., description="Model type: transformer, diffusion, llm")
    config: Dict[str, Any] = Field(..., description="Model configuration")
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(SECURITY_PATTERNS["model_name"], v):
            raise ValueError("Invalid model name format")
        return v
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['transformer', 'diffusion', 'llm']:
            raise ValueError("Invalid model type")
        return v
    
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps

class EnhancedInferenceRequest(BaseModel):
    """Enhanced inference request with validation."""
    model_id: int = Field(..., description="Model ID", ge=1)
    input_data: Union[List[int], int] = Field(..., description="Input data")
    
    @validator('input_data')
    def validate_input_data(cls, v):
        if isinstance(v, list) and len(v) > 10000:
            raise ValueError("Input data too large")
        return v
    
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps

class EnhancedTrainingRequest(BaseModel):
    """Enhanced training request with validation."""
    model_id: int = Field(..., description="Model ID", ge=1)
    data: List[int] = Field(..., description="Training data", min_items=1)
    epochs: int = Field(default=10, description="Number of epochs", ge=1, le=1000)
    
    @validator('data')
    def validate_data(cls, v):
        if len(v) > 1000000:
            raise ValueError("Training data too large")
        return v
    
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps

# Enhanced FastAPI application with quality middleware
app = FastAPI(
    title="Enhanced Blatam Academy Production System",
    description="High-quality AI/ML production system with comprehensive quality assurance",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Enhanced model and database managers
model_manager = EnhancedModelManager()
db_manager = None  # Will be initialized with connection manager

# Enhanced endpoints with quality assurance
@app.get("/health")
async def enhanced_health_check():
    """Enhanced health check with quality metrics."""
    try:
        # System health checks
        memory_usage = memory_manager.get_memory_usage()
        quality_score = await analyze_code_quality(".")
        
        # Security metrics
        security_metrics = security_validator.get_security_metrics()
        
        # Quality metrics
        model_quality = model_manager.get_quality_report()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {
                "memory_usage_mb": memory_usage / 1024 / 1024,
                "cpu_usage_percent": psutil.cpu_percent(),
                "quality_score": quality_score.get("quality_score", 0),
                "security_score": security_metrics.get("overall_security_score", 0)
            },
            "model_metrics": model_quality,
            "security_metrics": security_metrics,
            "quality_metrics": quality_score
        }
    except Exception as e:
        await error_handler.handle_error(e, {"operation": "health_check"})
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/api/v1/models")
@handle_errors(ErrorCategory.DATABASE, operation="get_models")
async def get_models():
    """Get all models with quality metrics."""
    try:
        # Rate limiting
        rate_limit = security_validator.check_rate_limit("get_models")
        if not rate_limit["allowed"]:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        return {
            "models": list(model_manager.models.keys()),
            "quality_report": model_manager.get_quality_report(),
            "rate_limit_info": rate_limit
        }
    except Exception as e:
        await error_handler.handle_error(e, {"operation": "get_models"})
        raise HTTPException(status_code=500, detail="Failed to get models")

@app.post("/api/v1/models")
@handle_errors(ErrorCategory.DATABASE, operation="create_model")
async def create_model(model: EnhancedModelCreate):
    """Create model with enhanced validation."""
    try:
        # Input sanitization
        sanitized_model = sanitize_input(model.dict())
        
        # Rate limiting
        rate_limit = security_validator.check_rate_limit("create_model")
        if not rate_limit["allowed"]:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Model creation based on type
        if sanitized_model["type"] == "transformer":
            result = await model_manager.create_transformer(sanitized_model["name"], sanitized_model["config"])
        elif sanitized_model["type"] == "diffusion":
            result = await model_manager.create_diffusion(sanitized_model["name"], sanitized_model["config"])
        elif sanitized_model["type"] == "llm":
            result = await model_manager.create_llm(sanitized_model["name"], sanitized_model["config"])
        else:
            raise ValueError("Invalid model type")
        
        if result["success"]:
            return {
                "message": "Model created successfully",
                "model_id": sanitized_model["name"],
                "quality_score": result.get("quality_score", 0),
                "rate_limit_info": rate_limit
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        await error_handler.handle_error(e, {"operation": "create_model", "model_data": model.dict()})
        raise HTTPException(status_code=500, detail="Failed to create model")

@app.post("/api/v1/inference/{model_id}")
@handle_errors(ErrorCategory.DATABASE, operation="run_inference")
async def run_inference(model_id: int, request: EnhancedInferenceRequest):
    """Run inference with quality monitoring."""
    try:
        # Input validation
        sanitized_request = sanitize_input(request.dict())
        
        # Rate limiting
        rate_limit = security_validator.check_rate_limit(f"inference_{model_id}")
        if not rate_limit["allowed"]:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Model inference with quality tracking
        model = model_manager.models.get(str(model_id))
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Convert input to tensor
        if isinstance(sanitized_request["input_data"], list):
            input_tensor = torch.tensor(sanitized_request["input_data"], dtype=torch.long)
        else:
            input_tensor = torch.tensor([sanitized_request["input_data"]], dtype=torch.long)
        
        # Run inference with quality monitoring
        with torch.no_grad():
            output = model(input_tensor)
        
        # Get quality metrics
        quality_metrics = model.get_quality_metrics()
        
        return {
            "model_id": model_id,
            "output": output.tolist(),
            "quality_metrics": quality_metrics,
            "rate_limit_info": rate_limit
        }
        
    except Exception as e:
        await error_handler.handle_error(e, {"operation": "run_inference", "model_id": model_id})
        raise HTTPException(status_code=500, detail="Inference failed")

@app.post("/api/v1/training/{model_id}")
@handle_errors(ErrorCategory.DATABASE, operation="train_model")
async def train_model(model_id: int, request: EnhancedTrainingRequest, background_tasks: BackgroundTasks):
    """Train model with quality monitoring."""
    try:
        # Input validation
        sanitized_request = sanitize_input(request.dict())
        
        # Rate limiting
        rate_limit = security_validator.check_rate_limit(f"training_{model_id}")
        if not rate_limit["allowed"]:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Background training task
        def train_background():
            try:
                model = model_manager.models.get(str(model_id))
                if not model:
                    return {"success": False, "error": "Model not found"}
                
                # Training logic with quality monitoring
                optimizer = optim.Adam(model.parameters())
                criterion = nn.CrossEntropyLoss()
                
                data_tensor = torch.tensor(sanitized_request["data"], dtype=torch.long)
                
                for epoch in range(sanitized_request["epochs"]):
                    optimizer.zero_grad()
                    output = model(data_tensor[:-1])
                    loss = criterion(output, data_tensor[1:])
                    loss.backward()
                    optimizer.step()
                
                return {"success": True, "epochs_completed": sanitized_request["epochs"]}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        background_tasks.add_task(train_background)
        
        return {
            "message": "Training started",
            "model_id": model_id,
            "epochs": sanitized_request["epochs"],
            "rate_limit_info": rate_limit
        }
        
    except Exception as e:
        await error_handler.handle_error(e, {"operation": "train_model", "model_id": model_id})
        raise HTTPException(status_code=500, detail="Training failed")

@app.get("/api/v1/system/metrics")
async def get_system_metrics():
    """Get comprehensive system metrics."""
    try:
        # Memory metrics
        memory_metrics = memory_manager.get_memory_usage()
        
        # Quality metrics
        quality_analysis = await analyze_code_quality(".")
        
        # Security metrics
        security_metrics = security_validator.get_security_metrics()
        
        # Model quality metrics
        model_quality = model_manager.get_quality_report()
        
        return {
            "memory_metrics": {
                "usage_mb": memory_metrics / 1024 / 1024,
                "available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "percentage": psutil.virtual_memory().percent
            },
            "quality_metrics": quality_analysis,
            "security_metrics": security_metrics,
            "model_quality": model_quality,
            "performance_metrics": {
                "cpu_percent": psutil.cpu_percent(),
                "thread_count": threading.active_count(),
                "process_count": len(psutil.pids())
            }
        }
        
    except Exception as e:
        await error_handler.handle_error(e, {"operation": "get_system_metrics"})
        raise HTTPException(status_code=500, detail="Failed to get system metrics")

@app.post("/api/v1/quality/analyze")
async def analyze_quality():
    """Analyze code quality."""
    try:
        # Run comprehensive quality analysis
        quality_result = await analyze_code_quality(".")
        
        # Run comprehensive tests
        test_result = await run_comprehensive_tests()
        
        return {
            "quality_analysis": quality_result,
            "test_results": test_result,
            "recommendations": quality_result.get("recommendations", [])
        }
        
    except Exception as e:
        await error_handler.handle_error(e, {"operation": "analyze_quality"})
        raise HTTPException(status_code=500, detail="Quality analysis failed")

def main():
    """Enhanced main function with quality assurance."""
    try:
        # Validate configuration
        config_validation = config_manager.validate_config()
        if not config_validation["valid"]:
            logger.error("Configuration validation failed")
            sys.exit(1)
        
        # Run quality checks on startup
        if CONFIG.get("quality_assurance", True):
            logger.info("Running quality assurance checks...")
            quality_result = asyncio.run(analyze_code_quality("."))
            if quality_result.get("quality_score", 0) < QUALITY_THRESHOLD:
                logger.warning(f"Quality score {quality_result.get('quality_score', 0)} below threshold {QUALITY_THRESHOLD}")
        
        # Run tests on startup
        if CONFIG.get("testing_automation", True):
            logger.info("Running comprehensive tests...")
            test_result = asyncio.run(run_comprehensive_tests())
            logger.info(f"Test results: {test_result.get('total_tests', 0)} tests executed")
        
        # Start the application
        logger.info("Starting Enhanced Production System...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        sys.exit(1)
    
    finally:
        # Cleanup
        if THREAD_POOL:
            THREAD_POOL.shutdown()
        if PROCESS_POOL:
            PROCESS_POOL.shutdown()
        logger.info("Enhanced Production System shutdown complete")

if __name__ == "__main__":
    main() 