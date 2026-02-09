"""
Advanced AI Service with Multi-Model Support and Advanced Capabilities
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import torch
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForCausalLM, 
    AutoModelForSeq2SeqLM, pipeline, set_seed
)
from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline
import gradio as gr
from PIL import Image
import requests
from io import BytesIO

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ModelType(Enum):
    """Types of AI models"""
    TEXT_GENERATION = "text_generation"
    TEXT_CLASSIFICATION = "text_classification"
    TEXT_SUMMARIZATION = "text_summarization"
    TEXT_TRANSLATION = "text_translation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    QUESTION_ANSWERING = "question_answering"
    IMAGE_GENERATION = "image_generation"
    IMAGE_CLASSIFICATION = "image_classification"
    IMAGE_CAPTIONING = "image_captioning"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    CODE_GENERATION = "code_generation"
    EMBEDDINGS = "embeddings"

class ModelProvider(Enum):
    """AI model providers"""
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    CUSTOM = "custom"

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    name: str
    model_type: ModelType
    provider: ModelProvider
    model_path: str
    tokenizer_path: Optional[str] = None
    device: str = "auto"
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    do_sample: bool = True
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerationRequest:
    """Request for AI generation"""
    prompt: str
    model_name: str
    model_type: ModelType
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class GenerationResponse:
    """Response from AI generation"""
    generated_text: str
    model_name: str
    model_type: ModelType
    tokens_used: int
    generation_time: float
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    average_tokens_per_request: float
    last_used: datetime
    accuracy: Optional[float] = None

class AdvancedAIService:
    """Advanced AI Service with Multi-Model Support"""
    
    def __init__(self):
        self.models = {}
        self.model_configs = {}
        self.model_performance = {}
        self.generation_cache = {}
        self.embeddings_cache = {}
        self.device = self._get_optimal_device()
        
        # Initialize default models
        self._initialize_default_models()
        
        logger.info("Advanced AI Service initialized")
    
    def _get_optimal_device(self) -> str:
        """Get optimal device for AI models"""
        try:
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        except Exception as e:
            logger.warning(f"Error detecting device: {e}")
            return "cpu"
    
    def _initialize_default_models(self):
        """Initialize default AI models"""
        try:
            default_models = [
                ModelConfig(
                    name="gpt2",
                    model_type=ModelType.TEXT_GENERATION,
                    provider=ModelProvider.HUGGINGFACE,
                    model_path="gpt2",
                    max_length=1024,
                    temperature=0.7
                ),
                ModelConfig(
                    name="distilbert-base-uncased",
                    model_type=ModelType.TEXT_CLASSIFICATION,
                    provider=ModelProvider.HUGGINGFACE,
                    model_path="distilbert-base-uncased-finetuned-sst-2-english",
                    max_length=512
                ),
                ModelConfig(
                    name="t5-small",
                    model_type=ModelType.TEXT_SUMMARIZATION,
                    provider=ModelProvider.HUGGINGFACE,
                    model_path="t5-small",
                    max_length=512
                ),
                ModelConfig(
                    name="facebook/bart-large-cnn",
                    model_type=ModelType.TEXT_SUMMARIZATION,
                    provider=ModelProvider.HUGGINGFACE,
                    model_path="facebook/bart-large-cnn",
                    max_length=1024
                ),
                ModelConfig(
                    name="sentence-transformers/all-MiniLM-L6-v2",
                    model_type=ModelType.EMBEDDINGS,
                    provider=ModelProvider.HUGGINGFACE,
                    model_path="sentence-transformers/all-MiniLM-L6-v2",
                    max_length=512
                )
            ]
            
            for config in default_models:
                self.model_configs[config.name] = config
                self.model_performance[config.name] = ModelPerformance(
                    model_name=config.name,
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    average_response_time=0.0,
                    average_tokens_per_request=0.0,
                    last_used=datetime.utcnow()
                )
            
            logger.info(f"Initialized {len(default_models)} default models")
            
        except Exception as e:
            logger.error(f"Error initializing default models: {e}")
    
    async def load_model(self, model_name: str) -> bool:
        """Load an AI model"""
        try:
            if model_name in self.models:
                logger.info(f"Model {model_name} already loaded")
                return True
            
            config = self.model_configs.get(model_name)
            if not config:
                logger.error(f"Model config not found: {model_name}")
                return False
            
            if not config.enabled:
                logger.warning(f"Model {model_name} is disabled")
                return False
            
            logger.info(f"Loading model: {model_name}")
            start_time = time.time()
            
            if config.model_type == ModelType.TEXT_GENERATION:
                model = await self._load_text_generation_model(config)
            elif config.model_type == ModelType.TEXT_CLASSIFICATION:
                model = await self._load_text_classification_model(config)
            elif config.model_type == ModelType.TEXT_SUMMARIZATION:
                model = await self._load_text_summarization_model(config)
            elif config.model_type == ModelType.EMBEDDINGS:
                model = await self._load_embeddings_model(config)
            elif config.model_type == ModelType.IMAGE_GENERATION:
                model = await self._load_image_generation_model(config)
            else:
                logger.error(f"Unsupported model type: {config.model_type}")
                return False
            
            if model:
                self.models[model_name] = model
                load_time = time.time() - start_time
                logger.info(f"Model {model_name} loaded in {load_time:.2f} seconds")
                return True
            else:
                logger.error(f"Failed to load model: {model_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return False
    
    async def _load_text_generation_model(self, config: ModelConfig):
        """Load text generation model"""
        try:
            tokenizer = AutoTokenizer.from_pretrained(config.model_path)
            model = AutoModelForCausalLM.from_pretrained(
                config.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device != "cuda":
                model = model.to(self.device)
            
            # Set pad token if not exists
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            return {
                'model': model,
                'tokenizer': tokenizer,
                'config': config
            }
            
        except Exception as e:
            logger.error(f"Error loading text generation model: {e}")
            return None
    
    async def _load_text_classification_model(self, config: ModelConfig):
        """Load text classification model"""
        try:
            pipeline_obj = pipeline(
                "text-classification",
                model=config.model_path,
                device=0 if self.device == "cuda" else -1
            )
            
            return {
                'pipeline': pipeline_obj,
                'config': config
            }
            
        except Exception as e:
            logger.error(f"Error loading text classification model: {e}")
            return None
    
    async def _load_text_summarization_model(self, config: ModelConfig):
        """Load text summarization model"""
        try:
            pipeline_obj = pipeline(
                "summarization",
                model=config.model_path,
                device=0 if self.device == "cuda" else -1
            )
            
            return {
                'pipeline': pipeline_obj,
                'config': config
            }
            
        except Exception as e:
            logger.error(f"Error loading text summarization model: {e}")
            return None
    
    async def _load_embeddings_model(self, config: ModelConfig):
        """Load embeddings model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer(config.model_path)
            
            return {
                'model': model,
                'config': config
            }
            
        except Exception as e:
            logger.error(f"Error loading embeddings model: {e}")
            return None
    
    async def _load_image_generation_model(self, config: ModelConfig):
        """Load image generation model"""
        try:
            if "xl" in config.model_path.lower():
                pipeline_obj = StableDiffusionXLPipeline.from_pretrained(
                    config.model_path,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
            else:
                pipeline_obj = StableDiffusionPipeline.from_pretrained(
                    config.model_path,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
            
            if self.device == "cuda":
                pipeline_obj = pipeline_obj.to("cuda")
            
            return {
                'pipeline': pipeline_obj,
                'config': config
            }
            
        except Exception as e:
            logger.error(f"Error loading image generation model: {e}")
            return None
    
    async def generate_text(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text using AI model"""
        try:
            start_time = time.time()
            
            # Check cache first
            cache_key = f"{request.model_name}_{hash(request.prompt)}"
            if cache_key in self.generation_cache:
                cached_response = self.generation_cache[cache_key]
                logger.info(f"Using cached response for {request.model_name}")
                return cached_response
            
            # Load model if not loaded
            if request.model_name not in self.models:
                loaded = await self.load_model(request.model_name)
                if not loaded:
                    raise ValueError(f"Failed to load model: {request.model_name}")
            
            model_data = self.models[request.model_name]
            config = model_data['config']
            
            # Generate based on model type
            if config.model_type == ModelType.TEXT_GENERATION:
                generated_text = await self._generate_text_generation(model_data, request)
            elif config.model_type == ModelType.TEXT_SUMMARIZATION:
                generated_text = await self._generate_text_summarization(model_data, request)
            else:
                raise ValueError(f"Unsupported model type for text generation: {config.model_type}")
            
            generation_time = time.time() - start_time
            
            # Calculate tokens used (approximate)
            tokens_used = len(request.prompt.split()) + len(generated_text.split())
            
            # Calculate confidence (placeholder)
            confidence = 0.8
            
            response = GenerationResponse(
                generated_text=generated_text,
                model_name=request.model_name,
                model_type=config.model_type,
                tokens_used=tokens_used,
                generation_time=generation_time,
                confidence=confidence,
                metadata={
                    'device': self.device,
                    'parameters': request.parameters
                }
            )
            
            # Cache response
            self.generation_cache[cache_key] = response
            
            # Update performance metrics
            await self._update_performance_metrics(request.model_name, generation_time, tokens_used, True)
            
            logger.info(f"Generated text using {request.model_name} in {generation_time:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            await self._update_performance_metrics(request.model_name, 0, 0, False)
            raise
    
    async def _generate_text_generation(self, model_data: Dict, request: GenerationRequest) -> str:
        """Generate text using text generation model"""
        try:
            model = model_data['model']
            tokenizer = model_data['tokenizer']
            config = model_data['config']
            
            # Prepare input
            inputs = tokenizer.encode(request.prompt, return_tensors="pt")
            if self.device != "cuda":
                inputs = inputs.to(self.device)
            
            # Generation parameters
            generation_params = {
                'max_length': config.max_length,
                'temperature': config.temperature,
                'top_p': config.top_p,
                'top_k': config.top_k,
                'repetition_penalty': config.repetition_penalty,
                'do_sample': config.do_sample,
                'pad_token_id': tokenizer.eos_token_id
            }
            
            # Override with request parameters
            generation_params.update(request.parameters)
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(inputs, **generation_params)
            
            # Decode output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove input prompt from output
            if generated_text.startswith(request.prompt):
                generated_text = generated_text[len(request.prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            raise
    
    async def _generate_text_summarization(self, model_data: Dict, request: GenerationRequest) -> str:
        """Generate text using summarization model"""
        try:
            pipeline_obj = model_data['pipeline']
            config = model_data['config']
            
            # Summarization parameters
            summarization_params = {
                'max_length': min(config.max_length, 512),
                'min_length': 50,
                'do_sample': False
            }
            
            # Override with request parameters
            summarization_params.update(request.parameters)
            
            # Generate summary
            result = pipeline_obj(request.prompt, **summarization_params)
            
            if isinstance(result, list) and len(result) > 0:
                return result[0]['summary_text']
            else:
                return str(result)
            
        except Exception as e:
            logger.error(f"Error in text summarization: {e}")
            raise
    
    async def classify_text(self, text: str, model_name: str = "distilbert-base-uncased") -> Dict[str, Any]:
        """Classify text using AI model"""
        try:
            # Load model if not loaded
            if model_name not in self.models:
                loaded = await self.load_model(model_name)
                if not loaded:
                    raise ValueError(f"Failed to load model: {model_name}")
            
            model_data = self.models[model_name]
            pipeline_obj = model_data['pipeline']
            
            # Classify
            result = pipeline_obj(text)
            
            # Update performance metrics
            await self._update_performance_metrics(model_name, 0.1, len(text.split()), True)
            
            return {
                'text': text,
                'model': model_name,
                'classification': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            await self._update_performance_metrics(model_name, 0, 0, False)
            raise
    
    async def generate_embeddings(self, texts: List[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[List[float]]:
        """Generate embeddings for texts"""
        try:
            # Check cache first
            cache_key = f"{model_name}_{hash(tuple(texts))}"
            if cache_key in self.embeddings_cache:
                logger.info(f"Using cached embeddings for {model_name}")
                return self.embeddings_cache[cache_key]
            
            # Load model if not loaded
            if model_name not in self.models:
                loaded = await self.load_model(model_name)
                if not loaded:
                    raise ValueError(f"Failed to load model: {model_name}")
            
            model_data = self.models[model_name]
            model = model_data['model']
            
            # Generate embeddings
            embeddings = model.encode(texts)
            
            # Convert to list
            embeddings_list = embeddings.tolist()
            
            # Cache embeddings
            self.embeddings_cache[cache_key] = embeddings_list
            
            # Update performance metrics
            await self._update_performance_metrics(model_name, 0.1, sum(len(text.split()) for text in texts), True)
            
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            await self._update_performance_metrics(model_name, 0, 0, False)
            raise
    
    async def generate_image(self, prompt: str, model_name: str = "runwayml/stable-diffusion-v1-5", 
                           num_images: int = 1, **kwargs) -> List[Image.Image]:
        """Generate images using AI model"""
        try:
            # Load model if not loaded
            if model_name not in self.models:
                loaded = await self.load_model(model_name)
                if not loaded:
                    raise ValueError(f"Failed to load model: {model_name}")
            
            model_data = self.models[model_name]
            pipeline_obj = model_data['pipeline']
            
            # Generation parameters
            generation_params = {
                'num_images_per_prompt': num_images,
                'guidance_scale': 7.5,
                'num_inference_steps': 50
            }
            generation_params.update(kwargs)
            
            # Generate images
            images = pipeline_obj(prompt, **generation_params).images
            
            # Update performance metrics
            await self._update_performance_metrics(model_name, 5.0, len(prompt.split()), True)
            
            return images
            
        except Exception as e:
            logger.error(f"Error generating images: {e}")
            await self._update_performance_metrics(model_name, 0, 0, False)
            raise
    
    async def _update_performance_metrics(self, model_name: str, response_time: float, tokens: int, success: bool):
        """Update model performance metrics"""
        try:
            if model_name not in self.model_performance:
                self.model_performance[model_name] = ModelPerformance(
                    model_name=model_name,
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    average_response_time=0.0,
                    average_tokens_per_request=0.0,
                    last_used=datetime.utcnow()
                )
            
            perf = self.model_performance[model_name]
            perf.total_requests += 1
            perf.last_used = datetime.utcnow()
            
            if success:
                perf.successful_requests += 1
                # Update averages
                perf.average_response_time = (
                    (perf.average_response_time * (perf.successful_requests - 1) + response_time) / 
                    perf.successful_requests
                )
                perf.average_tokens_per_request = (
                    (perf.average_tokens_per_request * (perf.successful_requests - 1) + tokens) / 
                    perf.successful_requests
                )
            else:
                perf.failed_requests += 1
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    async def add_model_config(self, config: ModelConfig):
        """Add a new model configuration"""
        try:
            self.model_configs[config.name] = config
            self.model_performance[config.name] = ModelPerformance(
                model_name=config.name,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0,
                average_tokens_per_request=0.0,
                last_used=datetime.utcnow()
            )
            
            logger.info(f"Added model config: {config.name}")
            
        except Exception as e:
            logger.error(f"Error adding model config: {e}")
    
    async def remove_model(self, model_name: str):
        """Remove a model"""
        try:
            # Unload model if loaded
            if model_name in self.models:
                del self.models[model_name]
            
            # Remove config
            if model_name in self.model_configs:
                del self.model_configs[model_name]
            
            # Remove performance data
            if model_name in self.model_performance:
                del self.model_performance[model_name]
            
            logger.info(f"Removed model: {model_name}")
            
        except Exception as e:
            logger.error(f"Error removing model: {e}")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            models = []
            
            for name, config in self.model_configs.items():
                model_info = {
                    'name': name,
                    'type': config.model_type.value,
                    'provider': config.provider.value,
                    'enabled': config.enabled,
                    'loaded': name in self.models,
                    'performance': self.model_performance.get(name, {}).__dict__ if name in self.model_performance else {}
                }
                models.append(model_info)
            
            return models
            
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    async def get_model_performance(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get model performance metrics"""
        try:
            if model_name:
                if model_name in self.model_performance:
                    return self.model_performance[model_name].__dict__
                else:
                    return {}
            else:
                return {name: perf.__dict__ for name, perf in self.model_performance.items()}
            
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return {}
    
    async def clear_cache(self):
        """Clear generation and embeddings cache"""
        try:
            self.generation_cache.clear()
            self.embeddings_cache.clear()
            logger.info("AI service cache cleared")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced AI Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'device': self.device,
                'models': {
                    'total_configs': len(self.model_configs),
                    'loaded_models': len(self.models),
                    'enabled_models': len([c for c in self.model_configs.values() if c.enabled])
                },
                'cache': {
                    'generation_cache_size': len(self.generation_cache),
                    'embeddings_cache_size': len(self.embeddings_cache)
                },
                'performance': {
                    'total_requests': sum(p.total_requests for p in self.model_performance.values()),
                    'successful_requests': sum(p.successful_requests for p in self.model_performance.values()),
                    'failed_requests': sum(p.failed_requests for p in self.model_performance.values())
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced AI Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























