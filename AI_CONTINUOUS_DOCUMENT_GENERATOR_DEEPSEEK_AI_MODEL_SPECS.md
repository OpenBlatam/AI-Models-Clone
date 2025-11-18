# Especificaciones de Integración con Modelos de IA Avanzados (DeepSeek)

## Resumen

Este documento define las especificaciones técnicas para integrar y optimizar el sistema de generación continua de documentos con modelos de IA avanzados como DeepSeek, incluyendo arquitectura, APIs, y funcionalidades específicas.

## 1. Arquitectura de Integración con DeepSeek

### 1.1 Componentes del Sistema DeepSeek

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DEEPSEEK AI INTEGRATION LAYER                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   DEEPSEEK      │  │   MODEL         │  │   OPTIMIZATION  │                │
│  │   API CLIENT    │  │   MANAGER       │  │   ENGINE        │                │
│  │                 │  │                 │  │                 │                │
│  │ • Authentication│  │ • Model         │  │ • Prompt        │                │
│  │ • Rate Limiting │  │   Selection     │  │   Engineering   │                │
│  │ • Error         │  │ • Version       │  │ • Parameter     │                │
│  │   Handling      │  │   Control       │  │   Tuning        │                │
│  │ • Retry Logic   │  │ • Load          │  │ • Context       │                │
│  │ • Caching       │  │   Balancing     │  │   Management    │                │
│  │ • Monitoring    │  │ • Health        │  │ • Response      │                │
│  │                 │  │   Monitoring    │  │   Processing    │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   PROMPT        │  │   CONTEXT       │  │   RESPONSE      │                │
│  │   ENGINEERING   │  │   MANAGER       │  │   PROCESSOR     │                │
│  │                 │  │                 │  │                 │                │
│  │ • Template      │  │ • Conversation  │  │ • Parsing       │                │
│  │   System        │  │   History       │  │ • Validation    │                │
│  │ • Dynamic       │  │ • Memory        │  │ • Formatting    │                │
│  │   Adaptation    │  │   Management    │  │ • Quality       │                │
│  │ • Few-shot      │  │ • Context       │  │   Scoring       │                │
│  │   Learning      │  │   Compression   │  │ • Error         │                │
│  │ • Chain of      │  │ • Relevance     │  │   Handling      │                │
│  │   Thought       │  │   Filtering     │  │ • Post-         │                │
│  │ • Role-based    │  │ • Temporal      │  │   Processing    │                │
│  │   Prompting     │  │   Awareness     │  │ • Enhancement   │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   MULTI-MODAL   │  │   STREAMING     │  │   FINE-TUNING   │                │
│  │   PROCESSING    │  │   RESPONSES     │  │   MANAGER       │                │
│  │                 │  │                 │  │                 │                │
│  │ • Text          │  │ • Real-time     │  │ • Custom        │                │
│  │   Processing    │  │   Streaming     │  │   Datasets      │                │
│  │ • Code          │  │ • Chunk         │  │ • Training      │                │
│  │   Generation    │  │   Processing    │  │   Pipelines     │                │
│  │ • Image         │  │ • Progress      │  │ • Model         │                │
│  │   Analysis      │  │   Tracking      │  │   Versioning    │                │
│  │ • Document      │  │ • Error         │  │ • Performance   │                │
│  │   Parsing       │  │   Recovery      │  │   Monitoring    │                │
│  │ • Audio         │  │ • Quality       │  │ • Deployment    │                │
│  │   Processing    │  │   Control       │  │ • Rollback      │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Modelos de Datos para DeepSeek

### 2.1 Estructuras de Integración

```python
# app/models/deepseek_integration.py
from enum import Enum
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import json

class DeepSeekModel(Enum):
    """Modelos disponibles de DeepSeek"""
    DEEPSEEK_CODER = "deepseek-coder"
    DEEPSEEK_CHAT = "deepseek-chat"
    DEEPSEEK_MATH = "deepseek-math"
    DEEPSEEK_REASONER = "deepseek-reasoner"
    DEEPSEEK_VL = "deepseek-vl"  # Vision-Language
    DEEPSEEK_AUDIO = "deepseek-audio"

class PromptType(Enum):
    """Tipos de prompts"""
    SYSTEM_PROMPT = "system_prompt"
    USER_PROMPT = "user_prompt"
    ASSISTANT_PROMPT = "assistant_prompt"
    FEW_SHOT_PROMPT = "few_shot_prompt"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    ROLE_BASED_PROMPT = "role_based_prompt"

class ResponseFormat(Enum):
    """Formatos de respuesta"""
    JSON = "json"
    MARKDOWN = "markdown"
    XML = "xml"
    YAML = "yaml"
    CODE = "code"
    TEXT = "text"
    STRUCTURED = "structured"

@dataclass
class DeepSeekConfig:
    """Configuración de DeepSeek"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    api_key: str = ""
    base_url: str = "https://api.deepseek.com/v1"
    model: DeepSeekModel = DeepSeekModel.DEEPSEEK_CHAT
    temperature: float = 0.7
    max_tokens: int = 4000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    stream: bool = False
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    rate_limit_per_minute: int = 60
    rate_limit_per_day: int = 10000
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class PromptTemplate:
    """Plantilla de prompt"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    prompt_type: PromptType = PromptType.SYSTEM_PROMPT
    template: str = ""
    variables: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ConversationContext:
    """Contexto de conversación"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    user_id: str = ""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context_window: int = 8000
    memory_type: str = "sliding_window"  # sliding_window, summary, key_points
    summary: Optional[str] = None
    key_points: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class DeepSeekRequest:
    """Request a DeepSeek"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model: DeepSeekModel = DeepSeekModel.DEEPSEEK_CHAT
    messages: List[Dict[str, str]] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 4000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    stream: bool = False
    response_format: ResponseFormat = ResponseFormat.TEXT
    user_id: str = ""
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DeepSeekResponse:
    """Response de DeepSeek"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    model: str = ""
    content: str = ""
    finish_reason: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    response_time: float = 0.0
    quality_score: float = 0.0
    confidence_score: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class StreamingResponse:
    """Response en streaming"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    chunk_content: str = ""
    chunk_index: int = 0
    is_final: bool = False
    progress_percentage: float = 0.0
    estimated_remaining_tokens: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FineTuningJob:
    """Job de fine-tuning"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    base_model: DeepSeekModel = DeepSeekModel.DEEPSEEK_CHAT
    training_data: List[Dict[str, Any]] = field(default_factory=list)
    validation_data: List[Dict[str, Any]] = field(default_factory=list)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    epochs: int = 3
    learning_rate: float = 5e-5
    batch_size: int = 4
    max_length: int = 2048
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    fine_tuned_model_id: Optional[str] = None
    training_loss: Optional[float] = None
    validation_loss: Optional[float] = None
    error_message: Optional[str] = None

@dataclass
class ModelPerformance:
    """Rendimiento del modelo"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model: DeepSeekModel = DeepSeekModel.DEEPSEEK_CHAT
    metric_name: str = ""
    metric_value: float = 0.0
    evaluation_dataset: str = ""
    evaluation_timestamp: datetime = field(default_factory=datetime.now)
    baseline_comparison: Optional[float] = None
    improvement_percentage: Optional[float] = None
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
```

## 3. Motor de Integración DeepSeek

### 3.1 Clase Principal del Motor

```python
# app/services/deepseek/deepseek_integration_engine.py
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
import aiohttp
import json
import hashlib
import hmac
from collections import defaultdict, deque

from ..models.deepseek_integration import *
from ..core.database import get_database
from ..core.cache import get_cache
from ..core.encryption import EncryptionService
from ..core.analytics import AnalyticsEngine

logger = logging.getLogger(__name__)

class DeepSeekIntegrationEngine:
    """
    Motor de integración con DeepSeek AI
    """
    
    def __init__(self):
        self.db = get_database()
        self.cache = get_cache()
        self.encryption_service = EncryptionService()
        self.analytics = AnalyticsEngine()
        
        # Configuración
        self.config = DeepSeekConfig()
        self.rate_limiter = defaultdict(lambda: deque())
        self.request_cache = {}
        
        # Estadísticas
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0
        }
    
    async def initialize(self, api_key: str, base_url: str = None):
        """
        Inicializa el motor con credenciales
        """
        try:
            self.config.api_key = await self.encryption_service.encrypt(api_key)
            if base_url:
                self.config.base_url = base_url
            
            # Probar conexión
            test_result = await self._test_connection()
            if not test_result["success"]:
                raise ValueError(f"Connection test failed: {test_result['error']}")
            
            logger.info("DeepSeek integration engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing DeepSeek engine: {e}")
            raise
    
    async def generate_text(
        self,
        prompt: str,
        model: DeepSeekModel = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
        response_format: ResponseFormat = ResponseFormat.TEXT,
        user_id: str = "",
        session_id: str = ""
    ) -> Union[DeepSeekResponse, AsyncGenerator[StreamingResponse, None]]:
        """
        Genera texto usando DeepSeek
        """
        try:
            # Configurar parámetros
            model = model or self.config.model
            temperature = temperature or self.config.temperature
            max_tokens = max_tokens or self.config.max_tokens
            
            # Verificar rate limiting
            if not await self._check_rate_limit(user_id):
                raise ValueError("Rate limit exceeded")
            
            # Crear request
            request = DeepSeekRequest(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                response_format=response_format,
                user_id=user_id,
                session_id=session_id
            )
            
            # Guardar request
            await self._save_request(request)
            
            # Hacer llamada a API
            if stream:
                return self._stream_generation(request)
            else:
                return await self._generate_single(request)
                
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def generate_with_context(
        self,
        prompt: str,
        context: ConversationContext,
        model: DeepSeekModel = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False
    ) -> Union[DeepSeekResponse, AsyncGenerator[StreamingResponse, None]]:
        """
        Genera texto con contexto de conversación
        """
        try:
            # Construir mensajes con contexto
            messages = await self._build_contextual_messages(prompt, context)
            
            # Crear request
            request = DeepSeekRequest(
                model=model or self.config.model,
                messages=messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                stream=stream,
                user_id=context.user_id,
                session_id=context.session_id
            )
            
            # Guardar request
            await self._save_request(request)
            
            # Hacer llamada a API
            if stream:
                return self._stream_generation(request)
            else:
                return await self._generate_single(request)
                
        except Exception as e:
            logger.error(f"Error generating with context: {e}")
            raise
    
    async def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        model: DeepSeekModel = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Genera salida estructurada según esquema
        """
        try:
            # Construir prompt estructurado
            structured_prompt = await self._build_structured_prompt(prompt, output_schema)
            
            # Generar respuesta
            response = await self.generate_text(
                prompt=structured_prompt,
                model=model,
                temperature=temperature,
                response_format=ResponseFormat.JSON
            )
            
            # Parsear y validar respuesta
            parsed_response = await self._parse_structured_response(response.content, output_schema)
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"Error generating structured output: {e}")
            raise
    
    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        model: DeepSeekModel = DeepSeekModel.DEEPSEEK_CODER,
        temperature: float = 0.2,
        include_tests: bool = True,
        include_documentation: bool = True
    ) -> Dict[str, Any]:
        """
        Genera código usando DeepSeek Coder
        """
        try:
            # Construir prompt de código
            code_prompt = await self._build_code_prompt(
                prompt, language, include_tests, include_documentation
            )
            
            # Generar código
            response = await self.generate_text(
                prompt=code_prompt,
                model=model,
                temperature=temperature,
                response_format=ResponseFormat.CODE
            )
            
            # Extraer y formatear código
            code_result = await self._extract_code_from_response(response.content, language)
            
            return {
                "code": code_result["code"],
                "tests": code_result.get("tests", ""),
                "documentation": code_result.get("documentation", ""),
                "language": language,
                "quality_score": await self._evaluate_code_quality(code_result["code"], language),
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise
    
    async def analyze_document(
        self,
        document_content: str,
        analysis_type: str = "comprehensive",
        model: DeepSeekModel = None
    ) -> Dict[str, Any]:
        """
        Analiza documento usando DeepSeek
        """
        try:
            # Construir prompt de análisis
            analysis_prompt = await self._build_analysis_prompt(document_content, analysis_type)
            
            # Generar análisis
            response = await self.generate_text(
                prompt=analysis_prompt,
                model=model or self.config.model,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parsear análisis
            analysis_result = await self._parse_analysis_response(response.content, analysis_type)
            
            return {
                "analysis": analysis_result,
                "quality_score": await self._evaluate_analysis_quality(analysis_result),
                "response": response
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            raise
    
    async def create_fine_tuning_job(
        self,
        name: str,
        training_data: List[Dict[str, Any]],
        base_model: DeepSeekModel = DeepSeekModel.DEEPSEEK_CHAT,
        hyperparameters: Dict[str, Any] = None
    ) -> str:
        """
        Crea job de fine-tuning
        """
        try:
            logger.info(f"Creating fine-tuning job: {name}")
            
            # Crear job
            job = FineTuningJob(
                name=name,
                base_model=base_model,
                training_data=training_data,
                hyperparameters=hyperparameters or {}
            )
            
            # Validar datos de entrenamiento
            await self._validate_training_data(training_data)
            
            # Guardar job
            job_id = await self._save_fine_tuning_job(job)
            
            # Iniciar entrenamiento
            await self._start_fine_tuning(job_id)
            
            logger.info(f"Fine-tuning job created: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error creating fine-tuning job: {e}")
            raise
    
    async def get_fine_tuning_status(self, job_id: str) -> Dict[str, Any]:
        """
        Obtiene estado de fine-tuning
        """
        try:
            # Obtener job
            job = await self._get_fine_tuning_job(job_id)
            if not job:
                raise ValueError("Fine-tuning job not found")
            
            return {
                "id": job.id,
                "name": job.name,
                "status": job.status,
                "progress": job.progress,
                "base_model": job.base_model.value,
                "epochs": job.epochs,
                "learning_rate": job.learning_rate,
                "batch_size": job.batch_size,
                "training_loss": job.training_loss,
                "validation_loss": job.validation_loss,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "fine_tuned_model_id": job.fine_tuned_model_id,
                "error_message": job.error_message
            }
            
        except Exception as e:
            logger.error(f"Error getting fine-tuning status: {e}")
            raise
    
    async def evaluate_model_performance(
        self,
        model: DeepSeekModel,
        test_dataset: List[Dict[str, Any]],
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evalúa rendimiento del modelo
        """
        try:
            logger.info(f"Evaluating model performance: {model.value}")
            
            metrics = metrics or ["accuracy", "bleu", "rouge", "perplexity"]
            results = {}
            
            for metric in metrics:
                metric_value = await self._calculate_metric(model, test_dataset, metric)
                results[metric] = metric_value
                
                # Guardar métrica
                performance = ModelPerformance(
                    model=model,
                    metric_name=metric,
                    metric_value=metric_value,
                    evaluation_dataset="test_dataset"
                )
                await self._save_model_performance(performance)
            
            # Calcular score general
            overall_score = await self._calculate_overall_score(results)
            
            return {
                "model": model.value,
                "metrics": results,
                "overall_score": overall_score,
                "evaluation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model performance: {e}")
            raise
    
    # Métodos de streaming
    async def _stream_generation(self, request: DeepSeekRequest) -> AsyncGenerator[StreamingResponse, None]:
        """
        Genera respuesta en streaming
        """
        try:
            # Hacer llamada streaming a API
            async with aiohttp.ClientSession() as session:
                headers = await self._get_headers()
                payload = await self._build_api_payload(request)
                
                async with session.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise ValueError(f"API error {response.status}: {error_text}")
                    
                    chunk_index = 0
                    async for line in response.content:
                        if line:
                            line = line.decode('utf-8').strip()
                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    break
                                
                                try:
                                    chunk_data = json.loads(data)
                                    if 'choices' in chunk_data and chunk_data['choices']:
                                        choice = chunk_data['choices'][0]
                                        if 'delta' in choice and 'content' in choice['delta']:
                                            chunk_content = choice['delta']['content']
                                            
                                            # Crear streaming response
                                            streaming_response = StreamingResponse(
                                                request_id=request.id,
                                                chunk_content=chunk_content,
                                                chunk_index=chunk_index,
                                                is_final=False,
                                                progress_percentage=min(100, (chunk_index / 100) * 100)
                                            )
                                            
                                            yield streaming_response
                                            chunk_index += 1
                                            
                                except json.JSONDecodeError:
                                    continue
            
            # Enviar chunk final
            final_response = StreamingResponse(
                request_id=request.id,
                chunk_content="",
                chunk_index=chunk_index,
                is_final=True,
                progress_percentage=100.0
            )
            yield final_response
            
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
    
    # Métodos de utilidad
    async def _test_connection(self) -> Dict[str, Any]:
        """
        Prueba conexión con DeepSeek API
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = await self._get_headers()
                payload = {
                    "model": self.config.model.value,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
                
                async with session.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_headers(self) -> Dict[str, str]:
        """
        Obtiene headers para API calls
        """
        api_key = await self.encryption_service.decrypt(self.config.api_key)
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "DocumentGenerator/1.0"
        }
    
    async def _build_api_payload(self, request: DeepSeekRequest) -> Dict[str, Any]:
        """
        Construye payload para API call
        """
        payload = {
            "model": request.model.value,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
            "stream": request.stream
        }
        
        if request.stop_sequences:
            payload["stop"] = request.stop_sequences
        
        return payload
    
    async def _check_rate_limit(self, user_id: str) -> bool:
        """
        Verifica rate limiting
        """
        now = datetime.now()
        user_requests = self.rate_limiter[user_id]
        
        # Limpiar requests antiguos
        while user_requests and (now - user_requests[0]).seconds > 60:
            user_requests.popleft()
        
        # Verificar límite
        if len(user_requests) >= self.config.rate_limit_per_minute:
            return False
        
        # Agregar request actual
        user_requests.append(now)
        return True
    
    async def _build_contextual_messages(
        self, 
        prompt: str, 
        context: ConversationContext
    ) -> List[Dict[str, str]]:
        """
        Construye mensajes con contexto
        """
        messages = []
        
        # Agregar mensajes del contexto
        for message in context.messages[-10:]:  # Últimos 10 mensajes
            messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        # Agregar prompt actual
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return messages
    
    async def _build_structured_prompt(
        self, 
        prompt: str, 
        output_schema: Dict[str, Any]
    ) -> str:
        """
        Construye prompt para salida estructurada
        """
        schema_str = json.dumps(output_schema, indent=2)
        
        structured_prompt = f"""
{prompt}

Please respond with a JSON object that matches the following schema:

{schema_str}

Ensure your response is valid JSON and follows the schema exactly.
"""
        
        return structured_prompt
    
    async def _build_code_prompt(
        self, 
        prompt: str, 
        language: str, 
        include_tests: bool, 
        include_documentation: bool
    ) -> str:
        """
        Construye prompt para generación de código
        """
        code_prompt = f"""
Generate {language} code for the following requirement:

{prompt}

Requirements:
- Use best practices for {language}
- Write clean, readable, and efficient code
"""
        
        if include_tests:
            code_prompt += "\n- Include comprehensive unit tests"
        
        if include_documentation:
            code_prompt += "\n- Include detailed documentation and comments"
        
        code_prompt += "\n\nFormat the response as:\n```{language}\n[CODE HERE]\n```"
        
        if include_tests:
            code_prompt += "\n\n```{language}\n[TESTS HERE]\n```"
        
        return code_prompt
    
    async def _build_analysis_prompt(self, document_content: str, analysis_type: str) -> str:
        """
        Construye prompt para análisis de documento
        """
        analysis_prompt = f"""
Analyze the following document and provide a {analysis_type} analysis:

{document_content}

Please provide:
1. Summary of key points
2. Quality assessment
3. Areas for improvement
4. Technical accuracy
5. Overall recommendations

Format your response in a structured way.
"""
        
        return analysis_prompt
    
    # Métodos de persistencia
    async def _save_request(self, request: DeepSeekRequest):
        """Guarda request"""
        # Implementar guardado en base de datos
        pass
    
    async def _save_response(self, response: DeepSeekResponse):
        """Guarda response"""
        # Implementar guardado en base de datos
        pass
    
    async def _save_fine_tuning_job(self, job: FineTuningJob) -> str:
        """Guarda job de fine-tuning"""
        # Implementar guardado en base de datos
        pass
    
    async def _get_fine_tuning_job(self, job_id: str) -> Optional[FineTuningJob]:
        """Obtiene job de fine-tuning"""
        # Implementar consulta a base de datos
        pass
    
    async def _save_model_performance(self, performance: ModelPerformance):
        """Guarda rendimiento del modelo"""
        # Implementar guardado en base de datos
        pass
    
    async def _validate_training_data(self, training_data: List[Dict[str, Any]]):
        """Valida datos de entrenamiento"""
        # Implementar validación
        pass
    
    async def _start_fine_tuning(self, job_id: str):
        """Inicia fine-tuning"""
        # Implementar inicio de fine-tuning
        pass
    
    async def _generate_single(self, request: DeepSeekRequest) -> DeepSeekResponse:
        """Genera respuesta única"""
        # Implementar generación única
        pass
    
    async def _parse_structured_response(self, content: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea respuesta estructurada"""
        # Implementar parsing
        pass
    
    async def _extract_code_from_response(self, content: str, language: str) -> Dict[str, str]:
        """Extrae código de respuesta"""
        # Implementar extracción de código
        pass
    
    async def _evaluate_code_quality(self, code: str, language: str) -> float:
        """Evalúa calidad del código"""
        # Implementar evaluación de código
        pass
    
    async def _parse_analysis_response(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Parsea respuesta de análisis"""
        # Implementar parsing de análisis
        pass
    
    async def _evaluate_analysis_quality(self, analysis: Dict[str, Any]) -> float:
        """Evalúa calidad del análisis"""
        # Implementar evaluación de análisis
        pass
    
    async def _calculate_metric(self, model: DeepSeekModel, dataset: List[Dict[str, Any]], metric: str) -> float:
        """Calcula métrica específica"""
        # Implementar cálculo de métricas
        pass
    
    async def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calcula score general"""
        # Implementar cálculo de score general
        pass
```

## 4. API Endpoints DeepSeek

### 4.1 Endpoints de Integración

```python
# app/api/deepseek_endpoints.py
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ..models.deepseek_integration import DeepSeekModel, ResponseFormat
from ..services.deepseek.deepseek_integration_engine import DeepSeekIntegrationEngine
from ..core.security import get_current_user

router = APIRouter(prefix="/api/deepseek", tags=["DeepSeek Integration"])

class TextGenerationRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    response_format: str = "text"

class ContextualGenerationRequest(BaseModel):
    prompt: str
    context_id: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False

class StructuredGenerationRequest(BaseModel):
    prompt: str
    output_schema: Dict[str, Any]
    model: Optional[str] = None
    temperature: Optional[float] = 0.3

class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str = "python"
    model: str = "deepseek-coder"
    temperature: Optional[float] = 0.2
    include_tests: bool = True
    include_documentation: bool = True

class DocumentAnalysisRequest(BaseModel):
    document_content: str
    analysis_type: str = "comprehensive"
    model: Optional[str] = None

class FineTuningRequest(BaseModel):
    name: str
    training_data: List[Dict[str, Any]]
    base_model: str = "deepseek-chat"
    hyperparameters: Optional[Dict[str, Any]] = None

@router.post("/generate")
async def generate_text(
    request: TextGenerationRequest,
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Genera texto usando DeepSeek
    """
    try:
        # Generar texto
        if request.stream:
            # Para streaming, retornar generator
            return engine.generate_text(
                prompt=request.prompt,
                model=DeepSeekModel(request.model) if request.model else None,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
                response_format=ResponseFormat(request.response_format),
                user_id=current_user.id
            )
        else:
            # Para respuesta única
            response = await engine.generate_text(
                prompt=request.prompt,
                model=DeepSeekModel(request.model) if request.model else None,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False,
                response_format=ResponseFormat(request.response_format),
                user_id=current_user.id
            )
            
            return {
                "success": True,
                "response": {
                    "id": response.id,
                    "content": response.content,
                    "model": response.model,
                    "finish_reason": response.finish_reason,
                    "usage": response.usage,
                    "response_time": response.response_time,
                    "quality_score": response.quality_score,
                    "confidence_score": response.confidence_score,
                    "tokens_used": response.tokens_used,
                    "cost": response.cost,
                    "created_at": response.created_at.isoformat()
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-with-context")
async def generate_with_context(
    request: ContextualGenerationRequest,
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Genera texto con contexto de conversación
    """
    try:
        # Obtener contexto
        context = await engine._get_conversation_context(request.context_id)
        if not context:
            raise HTTPException(status_code=404, detail="Context not found")
        
        # Generar con contexto
        if request.stream:
            return engine.generate_with_context(
                prompt=request.prompt,
                context=context,
                model=DeepSeekModel(request.model) if request.model else None,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            )
        else:
            response = await engine.generate_with_context(
                prompt=request.prompt,
                context=context,
                model=DeepSeekModel(request.model) if request.model else None,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False
            )
            
            return {
                "success": True,
                "response": {
                    "id": response.id,
                    "content": response.content,
                    "model": response.model,
                    "finish_reason": response.finish_reason,
                    "usage": response.usage,
                    "response_time": response.response_time,
                    "quality_score": response.quality_score,
                    "confidence_score": response.confidence_score,
                    "tokens_used": response.tokens_used,
                    "cost": response.cost,
                    "created_at": response.created_at.isoformat()
                }
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-structured")
async def generate_structured_output(
    request: StructuredGenerationRequest,
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Genera salida estructurada
    """
    try:
        # Generar salida estructurada
        result = await engine.generate_structured_output(
            prompt=request.prompt,
            output_schema=request.output_schema,
            model=DeepSeekModel(request.model) if request.model else None,
            temperature=request.temperature
        )
        
        return {
            "success": True,
            "structured_output": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-code")
async def generate_code(
    request: CodeGenerationRequest,
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Genera código usando DeepSeek Coder
    """
    try:
        # Generar código
        result = await engine.generate_code(
            prompt=request.prompt,
            language=request.language,
            model=DeepSeekModel(request.model),
            temperature=request.temperature,
            include_tests=request.include_tests,
            include_documentation=request.include_documentation
        )
        
        return {
            "success": True,
            "code_result": {
                "code": result["code"],
                "tests": result["tests"],
                "documentation": result["documentation"],
                "language": result["language"],
                "quality_score": result["quality_score"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-document")
async def analyze_document(
    request: DocumentAnalysisRequest,
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Analiza documento usando DeepSeek
    """
    try:
        # Analizar documento
        result = await engine.analyze_document(
            document_content=request.document_content,
            analysis_type=request.analysis_type,
            model=DeepSeekModel(request.model) if request.model else None
        )
        
        return {
            "success": True,
            "analysis_result": {
                "analysis": result["analysis"],
                "quality_score": result["quality_score"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fine-tuning/create")
async def create_fine_tuning_job(
    request: FineTuningRequest,
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Crea job de fine-tuning
    """
    try:
        # Crear job de fine-tuning
        job_id = await engine.create_fine_tuning_job(
            name=request.name,
            training_data=request.training_data,
            base_model=DeepSeekModel(request.base_model),
            hyperparameters=request.hyperparameters
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Fine-tuning job created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fine-tuning/{job_id}/status")
async def get_fine_tuning_status(
    job_id: str,
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Obtiene estado de fine-tuning
    """
    try:
        # Obtener estado
        status = await engine.get_fine_tuning_status(job_id)
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate-model")
async def evaluate_model_performance(
    model: str = Query(...),
    test_dataset: List[Dict[str, Any]] = Body(...),
    metrics: Optional[List[str]] = Query(None),
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Evalúa rendimiento del modelo
    """
    try:
        # Evaluar modelo
        result = await engine.evaluate_model_performance(
            model=DeepSeekModel(model),
            test_dataset=test_dataset,
            metrics=metrics
        )
        
        return {
            "success": True,
            "evaluation_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_available_models(
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Lista modelos disponibles
    """
    try:
        models = [
            {
                "id": model.value,
                "name": model.value,
                "description": f"DeepSeek {model.value} model",
                "capabilities": await engine._get_model_capabilities(model)
            }
            for model in DeepSeekModel
        ]
        
        return {
            "success": True,
            "models": models
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_usage_stats(
    current_user = Depends(get_current_user),
    engine: DeepSeekIntegrationEngine = Depends()
):
    """
    Obtiene estadísticas de uso
    """
    try:
        stats = engine.stats
        
        return {
            "success": True,
            "stats": {
                "total_requests": stats["total_requests"],
                "successful_requests": stats["successful_requests"],
                "failed_requests": stats["failed_requests"],
                "success_rate": stats["successful_requests"] / max(1, stats["total_requests"]) * 100,
                "total_tokens": stats["total_tokens"],
                "total_cost": stats["total_cost"],
                "average_response_time": stats["average_response_time"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 5. Conclusión

Las **Especificaciones de Integración con DeepSeek** proporcionan:

### 🤖 **Integración Completa con DeepSeek**
- **Múltiples modelos** (Chat, Coder, Math, Reasoner, VL, Audio)
- **Generación de texto** con contexto y streaming
- **Generación de código** especializada
- **Análisis de documentos** avanzado

### 🔧 **Funcionalidades Avanzadas**
- **Fine-tuning** de modelos personalizados
- **Salida estructurada** con esquemas JSON
- **Streaming en tiempo real** de respuestas
- **Evaluación de rendimiento** automática

### 📊 **Optimización y Monitoreo**
- **Rate limiting** inteligente
- **Caché de respuestas** para eficiencia
- **Métricas de calidad** automáticas
- **Análisis de costos** y tokens

### 🎯 **Beneficios del Sistema**
- **Calidad superior** con modelos de última generación
- **Flexibilidad** para múltiples casos de uso
- **Escalabilidad** para alto volumen
- **Integración seamless** con el ecosistema existente

Esta integración transforma el sistema en una **plataforma de IA de clase mundial** que aprovecha las capacidades más avanzadas de DeepSeek para generar documentos de calidad excepcional.


















