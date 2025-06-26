"""
ONYX BLOG POST - OpenRouter Client Module
=========================================

Cliente para OpenRouter API con soporte para múltiples modelos de IA.
Incluye rate limiting, retry logic y cost tracking.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
import aiohttp
from datetime import datetime, timedelta

from ..models import OpenRouterRequest, OpenRouterResponse, OpenRouterModel

logger = logging.getLogger(__name__)

class OpenRouterError(Exception):
    """Base exception para OpenRouter"""
    pass

class RateLimitError(OpenRouterError):
    """Exception para rate limiting"""
    pass

class AuthenticationError(OpenRouterError):
    """Exception para errores de autenticación"""
    pass

class ModelNotAvailableError(OpenRouterError):
    """Exception cuando el modelo no está disponible"""
    pass

@dataclass
class ModelPricing:
    """Precios por modelo en OpenRouter"""
    prompt_tokens_per_1k: float = 0.0
    completion_tokens_per_1k: float = 0.0
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calcular costo total"""
        prompt_cost = (prompt_tokens / 1000) * self.prompt_tokens_per_1k
        completion_cost = (completion_tokens / 1000) * self.completion_tokens_per_1k
        return prompt_cost + completion_cost

@dataclass
class RateLimiter:
    """Rate limiter para OpenRouter API"""
    requests_per_minute: int = 60
    tokens_per_minute: int = 100000
    
    def __init__(self, requests_per_minute: int = 60, tokens_per_minute: int = 100000):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_times: List[float] = []
        self.token_usage: List[tuple] = []  # (timestamp, tokens)
        self.lock = asyncio.Lock()
    
    async def acquire(self, estimated_tokens: int = 1000):
        """Adquirir permiso para hacer request"""
        async with self.lock:
            current_time = time.time()
            minute_ago = current_time - 60
            
            # Limpiar requests antiguos
            self.request_times = [t for t in self.request_times if t > minute_ago]
            self.token_usage = [(t, tokens) for t, tokens in self.token_usage if t > minute_ago]
            
            # Verificar límites
            if len(self.request_times) >= self.requests_per_minute:
                wait_time = 60 - (current_time - self.request_times[0])
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                return await self.acquire(estimated_tokens)
            
            current_tokens = sum(tokens for _, tokens in self.token_usage)
            if current_tokens + estimated_tokens > self.tokens_per_minute:
                wait_time = 60 - (current_time - self.token_usage[0][0])
                logger.warning(f"Token limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                return await self.acquire(estimated_tokens)
            
            # Registrar request
            self.request_times.append(current_time)
            self.token_usage.append((current_time, estimated_tokens))

class OpenRouterClient:
    """Cliente para OpenRouter API"""
    
    def __init__(
        self,
        api_key: str,
        app_name: str = "onyx-blog-post",
        base_url: str = "https://openrouter.ai/api/v1",
        default_model: str = "openai/gpt-4-turbo",
        rate_limiter: Optional[RateLimiter] = None
    ):
        self.api_key = api_key
        self.app_name = app_name
        self.base_url = base_url
        self.default_model = default_model
        self.rate_limiter = rate_limiter or RateLimiter()
        
        # Pricing por modelo (valores aproximados)
        self.model_pricing = {
            "openai/gpt-4-turbo": ModelPricing(0.01, 0.03),
            "openai/gpt-4o": ModelPricing(0.005, 0.015),
            "anthropic/claude-3-sonnet": ModelPricing(0.003, 0.015),
            "anthropic/claude-3-haiku": ModelPricing(0.00025, 0.00125),
            "google/gemini-pro": ModelPricing(0.0005, 0.0015),
            "mistralai/mistral-large": ModelPricing(0.008, 0.024),
            "meta-llama/llama-3-70b-instruct": ModelPricing(0.0009, 0.0009),
            "cohere/command-r": ModelPricing(0.0005, 0.0015),
        }
        
        # Métricas
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "requests_by_model": {},
            "start_time": time.time()
        }
        
        logger.info(f"OpenRouterClient initialized (app: {app_name})")
    
    @property
    def headers(self) -> Dict[str, str]:
        """Headers para requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://onyx.blatam.com",
            "X-Title": self.app_name
        }
    
    async def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        timeout: int = 60
    ) -> Dict[str, Any]:
        """Hacer request HTTP a OpenRouter"""
        url = f"{self.base_url}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        return response_data
                    elif response.status == 401:
                        raise AuthenticationError("Invalid API key")
                    elif response.status == 429:
                        raise RateLimitError("Rate limit exceeded")
                    elif response.status == 404:
                        raise ModelNotAvailableError("Model not available")
                    else:
                        raise OpenRouterError(f"API error {response.status}: {response_data}")
            
            except aiohttp.ClientError as e:
                raise OpenRouterError(f"Network error: {e}")
    
    async def complete(
        self,
        request: OpenRouterRequest,
        retry_count: int = 3,
        retry_delay: float = 1.0
    ) -> OpenRouterResponse:
        """Completar texto usando OpenRouter"""
        
        self.metrics["total_requests"] += 1
        model = request.model
        self.metrics["requests_by_model"][model] = self.metrics["requests_by_model"].get(model, 0) + 1
        
        # Estimar tokens para rate limiting
        estimated_tokens = self._estimate_tokens(request.messages)
        
        for attempt in range(retry_count + 1):
            try:
                # Rate limiting
                await self.rate_limiter.acquire(estimated_tokens)
                
                # Hacer request
                logger.debug(f"Making OpenRouter request (attempt {attempt + 1}/{retry_count + 1})")
                response_data = await self._make_request("chat/completions", request.to_dict())
                
                # Parsear response
                response = OpenRouterResponse(
                    id=response_data["id"],
                    object=response_data["object"],
                    created=response_data["created"],
                    model=response_data["model"],
                    choices=response_data["choices"],
                    usage=response_data["usage"]
                )
                
                # Actualizar métricas
                self._update_metrics(response, model)
                self.metrics["successful_requests"] += 1
                
                logger.info(f"OpenRouter request successful (tokens: {response.get_tokens_used()})")
                return response
            
            except (RateLimitError, OpenRouterError) as e:
                if attempt < retry_count:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Request failed: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    self.metrics["failed_requests"] += 1
                    logger.error(f"Request failed after {retry_count + 1} attempts: {e}")
                    raise
    
    async def stream_complete(
        self,
        request: OpenRouterRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Completar con streaming"""
        request.stream = True
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=request.to_dict()
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise OpenRouterError(f"Streaming error {response.status}: {error_data}")
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
    
    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Estimar tokens de los mensajes"""
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        # Aproximación: 1 token ≈ 4 caracteres
        return max(100, int(total_chars / 4))
    
    def _update_metrics(self, response: OpenRouterResponse, model: str):
        """Actualizar métricas del cliente"""
        tokens_used = response.get_tokens_used()
        self.metrics["total_tokens"] += tokens_used
        
        # Calcular costo
        pricing = self.model_pricing.get(model, ModelPricing())
        if "usage" in response.__dict__ and response.usage:
            prompt_tokens = response.usage.get("prompt_tokens", 0)
            completion_tokens = response.usage.get("completion_tokens", 0)
            cost = pricing.calculate_cost(prompt_tokens, completion_tokens)
            self.metrics["total_cost"] += cost
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Obtener modelos disponibles"""
        try:
            response_data = await self._make_request("models", {})
            return response_data.get("data", [])
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    async def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un modelo específico"""
        models = await self.get_available_models()
        for model_info in models:
            if model_info.get("id") == model:
                return model_info
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del cliente"""
        uptime = time.time() - self.metrics["start_time"]
        success_rate = 0.0
        if self.metrics["total_requests"] > 0:
            success_rate = (self.metrics["successful_requests"] / self.metrics["total_requests"]) * 100
        
        avg_cost = 0.0
        if self.metrics["successful_requests"] > 0:
            avg_cost = self.metrics["total_cost"] / self.metrics["successful_requests"]
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.metrics["total_requests"],
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "success_rate_percent": success_rate,
            "total_tokens": self.metrics["total_tokens"],
            "total_cost_usd": self.metrics["total_cost"],
            "average_cost_per_request": avg_cost,
            "requests_by_model": self.metrics["requests_by_model"]
        }
    
    async def test_connection(self) -> bool:
        """Probar conexión con OpenRouter"""
        try:
            test_request = OpenRouterRequest(
                model=self.default_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            response = await self.complete(test_request)
            return len(response.get_content()) > 0
        
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def close(self):
        """Cerrar cliente y limpiar recursos"""
        logger.info("OpenRouterClient closing...")
        # Aquí se pueden agregar cleanup tasks si es necesario

class OpenRouterModelManager:
    """Manager para diferentes modelos de OpenRouter"""
    
    def __init__(self, client: OpenRouterClient):
        self.client = client
        self.model_configs = {
            OpenRouterModel.GPT_4_TURBO: {
                "max_tokens": 4096,
                "temperature": 0.7,
                "best_for": ["technical", "detailed_analysis"]
            },
            OpenRouterModel.GPT_4O: {
                "max_tokens": 4096,
                "temperature": 0.7,
                "best_for": ["general", "creative"]
            },
            OpenRouterModel.CLAUDE_3_SONNET: {
                "max_tokens": 4096,
                "temperature": 0.7,
                "best_for": ["analysis", "reasoning"]
            },
            OpenRouterModel.CLAUDE_3_HAIKU: {
                "max_tokens": 4096,
                "temperature": 0.7,
                "best_for": ["quick", "simple"]
            },
            OpenRouterModel.GEMINI_PRO: {
                "max_tokens": 2048,
                "temperature": 0.7,
                "best_for": ["factual", "research"]
            },
            OpenRouterModel.MISTRAL_LARGE: {
                "max_tokens": 4096,
                "temperature": 0.7,
                "best_for": ["multilingual", "coding"]
            },
            OpenRouterModel.LLAMA_3_70B: {
                "max_tokens": 4096,
                "temperature": 0.7,
                "best_for": ["open_source", "general"]
            },
            OpenRouterModel.COHERE_COMMAND_R: {
                "max_tokens": 4096,
                "temperature": 0.7,
                "best_for": ["business", "professional"]
            }
        }
    
    def get_best_model_for_task(self, task_type: str) -> OpenRouterModel:
        """Obtener el mejor modelo para un tipo de tarea"""
        model_scores = {}
        
        for model, config in self.model_configs.items():
            best_for = config.get("best_for", [])
            if task_type in best_for:
                model_scores[model] = len(best_for)  # Menos específico = más versátil
        
        if model_scores:
            return min(model_scores.keys(), key=lambda k: model_scores[k])
        
        # Default fallback
        return OpenRouterModel.GPT_4_TURBO
    
    def get_model_config(self, model: OpenRouterModel) -> Dict[str, Any]:
        """Obtener configuración de un modelo"""
        return self.model_configs.get(model, self.model_configs[OpenRouterModel.GPT_4_TURBO])
    
    async def create_optimized_request(
        self,
        model: OpenRouterModel,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> OpenRouterRequest:
        """Crear request optimizado para el modelo"""
        config = self.get_model_config(model)
        
        # Configuración base del modelo
        request_params = {
            "model": model.value,
            "messages": messages,
            "max_tokens": config.get("max_tokens", 4096),
            "temperature": config.get("temperature", 0.7),
        }
        
        # Override con parámetros personalizados
        request_params.update(kwargs)
        
        return OpenRouterRequest(**request_params)

# Factory function para crear cliente
def create_openrouter_client(
    api_key: str,
    app_name: str = "onyx-blog-post",
    requests_per_minute: int = 60,
    tokens_per_minute: int = 100000,
    default_model: str = "openai/gpt-4-turbo"
) -> OpenRouterClient:
    """Factory para crear cliente OpenRouter"""
    rate_limiter = RateLimiter(requests_per_minute, tokens_per_minute)
    
    return OpenRouterClient(
        api_key=api_key,
        app_name=app_name,
        default_model=default_model,
        rate_limiter=rate_limiter
    )

__all__ = [
    'OpenRouterError',
    'RateLimitError',
    'AuthenticationError',
    'ModelNotAvailableError',
    'ModelPricing',
    'RateLimiter',
    'OpenRouterClient',
    'OpenRouterModelManager',
    'create_openrouter_client',
] 