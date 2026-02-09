"""
API Gateway - Gateway de API Avanzado
Sistema de gateway con rate limiting, middleware y gestión de tráfico
"""

import asyncio
import logging
import json
import time
from typing import List, Dict, Any, Optional, Callable, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import ipaddress
import uuid
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import redis
import jwt
from functools import wraps

logger = logging.getLogger(__name__)

class RateLimitType(Enum):
    """Tipos de rate limiting"""
    IP_BASED = "ip_based"
    USER_BASED = "user_based"
    API_KEY_BASED = "api_key_based"
    GLOBAL = "global"

class MiddlewareType(Enum):
    """Tipos de middleware"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMITING = "rate_limiting"
    LOGGING = "logging"
    CACHING = "caching"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"

@dataclass
class RateLimitRule:
    """Regla de rate limiting"""
    id: str
    name: str
    type: RateLimitType
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    window_size: int
    enabled: bool = True
    paths: List[str] = None
    methods: List[str] = None
    user_roles: List[str] = None
    
    def __post_init__(self):
        if self.paths is None:
            self.paths = ["*"]
        if self.methods is None:
            self.methods = ["*"]
        if self.user_roles is None:
            self.user_roles = ["*"]

@dataclass
class APIKey:
    """Clave de API"""
    key: str
    name: str
    user_id: str
    permissions: List[str]
    rate_limit: RateLimitRule
    expires_at: Optional[str] = None
    is_active: bool = True
    created_at: str = None
    last_used: Optional[str] = None
    usage_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()

@dataclass
class RequestLog:
    """Log de request"""
    id: str
    timestamp: str
    method: str
    path: str
    query_params: Dict[str, Any]
    headers: Dict[str, str]
    ip_address: str
    user_agent: str
    user_id: Optional[str]
    api_key: Optional[str]
    response_status: int
    response_time: float
    request_size: int
    response_size: int
    error_message: Optional[str] = None

class APIGateway:
    """
    Gateway de API avanzado con rate limiting y middleware
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = None
        self.redis_url = redis_url
        
        # Configuraciones
        self.config = {
            "default_rate_limit": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "requests_per_day": 10000,
                "burst_limit": 10
            },
            "cache_ttl": 300,  # 5 minutos
            "log_retention_days": 30,
            "max_request_size": 10 * 1024 * 1024,  # 10MB
            "timeout_seconds": 30
        }
        
        # Almacenamiento en memoria
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.request_logs: List[RequestLog] = []
        self.middleware_stack: List[Dict[str, Any]] = []
        
        # Métricas
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limited_requests": 0,
            "average_response_time": 0.0,
            "requests_by_endpoint": defaultdict(int),
            "requests_by_status": defaultdict(int),
            "requests_by_ip": defaultdict(int)
        }
        
        # Rate limiting storage
        self.rate_limit_storage: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Inicializar reglas por defecto
        self._initialize_default_rules()
    
    async def initialize(self):
        """Inicializar API Gateway"""
        try:
            logger.info("Inicializando API Gateway...")
            
            # Conectar a Redis si está disponible
            try:
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
                logger.info("Conectado a Redis para rate limiting")
            except Exception as e:
                logger.warning(f"No se pudo conectar a Redis: {e}. Usando almacenamiento en memoria.")
                self.redis_client = None
            
            # Configurar middleware por defecto
            await self._setup_default_middleware()
            
            logger.info("API Gateway inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando API Gateway: {e}")
            raise
    
    def _initialize_default_rules(self):
        """Inicializar reglas de rate limiting por defecto"""
        try:
            # Regla por defecto para todos los endpoints
            default_rule = RateLimitRule(
                id="default",
                name="Default Rate Limit",
                type=RateLimitType.IP_BASED,
                requests_per_minute=self.config["default_rate_limit"]["requests_per_minute"],
                requests_per_hour=self.config["default_rate_limit"]["requests_per_hour"],
                requests_per_day=self.config["default_rate_limit"]["requests_per_day"],
                burst_limit=self.config["default_rate_limit"]["burst_limit"],
                window_size=60
            )
            self.rate_limit_rules["default"] = default_rule
            
            # Regla más restrictiva para endpoints de autenticación
            auth_rule = RateLimitRule(
                id="auth",
                name="Authentication Rate Limit",
                type=RateLimitType.IP_BASED,
                requests_per_minute=10,
                requests_per_hour=100,
                requests_per_day=500,
                burst_limit=3,
                window_size=60,
                paths=["/api/auth/*", "/api/login", "/api/register"]
            )
            self.rate_limit_rules["auth"] = auth_rule
            
            # Regla para endpoints de búsqueda
            search_rule = RateLimitRule(
                id="search",
                name="Search Rate Limit",
                type=RateLimitType.USER_BASED,
                requests_per_minute=30,
                requests_per_hour=500,
                requests_per_day=2000,
                burst_limit=5,
                window_size=60,
                paths=["/api/search/*"]
            )
            self.rate_limit_rules["search"] = search_rule
            
            logger.info("Reglas de rate limiting por defecto inicializadas")
            
        except Exception as e:
            logger.error(f"Error inicializando reglas por defecto: {e}")
    
    async def _setup_default_middleware(self):
        """Configurar middleware por defecto"""
        try:
            # Middleware de logging
            await self.add_middleware(
                name="request_logging",
                type=MiddlewareType.LOGGING,
                function=self._log_request_middleware,
                order=1
            )
            
            # Middleware de rate limiting
            await self.add_middleware(
                name="rate_limiting",
                type=MiddlewareType.RATE_LIMITING,
                function=self._rate_limit_middleware,
                order=2
            )
            
            # Middleware de validación de tamaño
            await self.add_middleware(
                name="request_size_validation",
                type=MiddlewareType.VALIDATION,
                function=self._request_size_middleware,
                order=3
            )
            
            logger.info("Middleware por defecto configurado")
            
        except Exception as e:
            logger.error(f"Error configurando middleware por defecto: {e}")
    
    async def add_middleware(self, name: str, type: MiddlewareType, 
                           function: Callable, order: int = 0, 
                           config: Dict[str, Any] = None):
        """Agregar middleware al stack"""
        try:
            middleware = {
                "name": name,
                "type": type,
                "function": function,
                "order": order,
                "config": config or {},
                "enabled": True
            }
            
            self.middleware_stack.append(middleware)
            
            # Ordenar por order
            self.middleware_stack.sort(key=lambda x: x["order"])
            
            logger.info(f"Middleware agregado: {name}")
            
        except Exception as e:
            logger.error(f"Error agregando middleware: {e}")
    
    async def remove_middleware(self, name: str) -> bool:
        """Remover middleware del stack"""
        try:
            for i, middleware in enumerate(self.middleware_stack):
                if middleware["name"] == name:
                    del self.middleware_stack[i]
                    logger.info(f"Middleware removido: {name}")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error removiendo middleware: {e}")
            return False
    
    async def process_request(self, request: Request, call_next: Callable) -> Response:
        """Procesar request a través del middleware stack"""
        try:
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            # Ejecutar middleware en orden
            for middleware in self.middleware_stack:
                if not middleware["enabled"]:
                    continue
                
                try:
                    # Ejecutar middleware
                    result = await middleware["function"](request, call_next, middleware["config"])
                    
                    # Si el middleware retorna una respuesta, usarla
                    if isinstance(result, Response):
                        await self._log_response(request, result, time.time() - start_time, request_id)
                        return result
                    
                except Exception as e:
                    logger.error(f"Error en middleware {middleware['name']}: {e}")
                    # Continuar con el siguiente middleware
            
            # Si ningún middleware retorna respuesta, continuar con el endpoint
            response = await call_next(request)
            
            # Log de respuesta
            await self._log_response(request, response, time.time() - start_time, request_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando request: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "message": str(e)}
            )
    
    async def _log_request_middleware(self, request: Request, call_next: Callable, config: Dict[str, Any]):
        """Middleware de logging de requests"""
        try:
            # Extraer información del request
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            # Extraer user_id y api_key de headers
            user_id = request.headers.get("x-user-id")
            api_key = request.headers.get("x-api-key")
            
            # Crear log de request
            request_log = RequestLog(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                method=request.method,
                path=str(request.url.path),
                query_params=dict(request.query_params),
                headers=dict(request.headers),
                ip_address=client_ip,
                user_agent=user_agent,
                user_id=user_id,
                api_key=api_key,
                response_status=0,  # Se actualizará después
                response_time=0.0,  # Se actualizará después
                request_size=0,  # Se calculará después
                response_size=0  # Se calculará después
            )
            
            # Almacenar en memoria (en producción usar base de datos)
            self.request_logs.append(request_log)
            
            # Mantener solo los últimos 10000 logs
            if len(self.request_logs) > 10000:
                self.request_logs = self.request_logs[-10000:]
            
            # Actualizar métricas
            self.metrics["total_requests"] += 1
            self.metrics["requests_by_endpoint"][str(request.url.path)] += 1
            self.metrics["requests_by_ip"][client_ip] += 1
            
        except Exception as e:
            logger.error(f"Error en middleware de logging: {e}")
    
    async def _rate_limit_middleware(self, request: Request, call_next: Callable, config: Dict[str, Any]):
        """Middleware de rate limiting"""
        try:
            client_ip = request.client.host if request.client else "unknown"
            user_id = request.headers.get("x-user-id")
            api_key = request.headers.get("x-api-key")
            
            # Determinar tipo de rate limiting
            rate_limit_type = RateLimitType.IP_BASED
            identifier = client_ip
            
            if user_id:
                rate_limit_type = RateLimitType.USER_BASED
                identifier = user_id
            elif api_key:
                rate_limit_type = RateLimitType.API_KEY_BASED
                identifier = api_key
            
            # Encontrar regla aplicable
            applicable_rule = await self._find_applicable_rate_limit_rule(
                str(request.url.path), request.method, rate_limit_type
            )
            
            if applicable_rule:
                # Verificar rate limit
                is_allowed = await self._check_rate_limit(identifier, applicable_rule)
                
                if not is_allowed:
                    self.metrics["rate_limited_requests"] += 1
                    
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"Too many requests. Limit: {applicable_rule.requests_per_minute} per minute",
                            "retry_after": 60
                        },
                        headers={"Retry-After": "60"}
                    )
            
        except Exception as e:
            logger.error(f"Error en middleware de rate limiting: {e}")
    
    async def _request_size_middleware(self, request: Request, call_next: Callable, config: Dict[str, Any]):
        """Middleware de validación de tamaño de request"""
        try:
            content_length = request.headers.get("content-length")
            
            if content_length:
                size = int(content_length)
                if size > self.config["max_request_size"]:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Request too large",
                            "message": f"Request size exceeds maximum allowed size of {self.config['max_request_size']} bytes"
                        }
                    )
            
        except Exception as e:
            logger.error(f"Error en middleware de validación de tamaño: {e}")
    
    async def _find_applicable_rate_limit_rule(self, path: str, method: str, 
                                             rate_limit_type: RateLimitType) -> Optional[RateLimitRule]:
        """Encontrar regla de rate limiting aplicable"""
        try:
            for rule in self.rate_limit_rules.values():
                if not rule.enabled:
                    continue
                
                if rule.type != rate_limit_type:
                    continue
                
                # Verificar si el path coincide
                path_matches = False
                for rule_path in rule.paths:
                    if rule_path == "*" or path.startswith(rule_path.replace("*", "")):
                        path_matches = True
                        break
                
                if not path_matches:
                    continue
                
                # Verificar si el método coincide
                method_matches = "*" in rule.methods or method.upper() in [m.upper() for m in rule.methods]
                
                if method_matches:
                    return rule
            
            return None
            
        except Exception as e:
            logger.error(f"Error encontrando regla de rate limiting: {e}")
            return None
    
    async def _check_rate_limit(self, identifier: str, rule: RateLimitRule) -> bool:
        """Verificar rate limit para un identificador"""
        try:
            now = time.time()
            
            # Usar Redis si está disponible, sino usar memoria
            if self.redis_client:
                return await self._check_rate_limit_redis(identifier, rule, now)
            else:
                return await self._check_rate_limit_memory(identifier, rule, now)
            
        except Exception as e:
            logger.error(f"Error verificando rate limit: {e}")
            return True  # En caso de error, permitir el request
    
    async def _check_rate_limit_redis(self, identifier: str, rule: RateLimitRule, now: float) -> bool:
        """Verificar rate limit usando Redis"""
        try:
            # Crear claves para diferentes ventanas de tiempo
            minute_key = f"rate_limit:{identifier}:minute:{int(now // 60)}"
            hour_key = f"rate_limit:{identifier}:hour:{int(now // 3600)}"
            day_key = f"rate_limit:{identifier}:day:{int(now // 86400)}"
            
            # Verificar límites
            minute_count = await self.redis_client.get(minute_key) or 0
            hour_count = await self.redis_client.get(hour_key) or 0
            day_count = await self.redis_client.get(day_key) or 0
            
            if (int(minute_count) >= rule.requests_per_minute or
                int(hour_count) >= rule.requests_per_hour or
                int(day_count) >= rule.requests_per_day):
                return False
            
            # Incrementar contadores
            pipe = self.redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            pipe.incr(day_key)
            pipe.expire(day_key, 86400)
            await pipe.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando rate limit en Redis: {e}")
            return True
    
    async def _check_rate_limit_memory(self, identifier: str, rule: RateLimitRule, now: float) -> bool:
        """Verificar rate limit usando memoria"""
        try:
            # Obtener o crear deque para el identificador
            if identifier not in self.rate_limit_storage:
                self.rate_limit_storage[identifier] = deque()
            
            request_times = self.rate_limit_storage[identifier]
            
            # Limpiar requests antiguos
            minute_ago = now - 60
            hour_ago = now - 3600
            day_ago = now - 86400
            
            while request_times and request_times[0] < minute_ago:
                request_times.popleft()
            
            # Verificar límites
            minute_count = sum(1 for t in request_times if t > minute_ago)
            hour_count = sum(1 for t in request_times if t > hour_ago)
            day_count = sum(1 for t in request_times if t > day_ago)
            
            if (minute_count >= rule.requests_per_minute or
                hour_count >= rule.requests_per_hour or
                day_count >= rule.requests_per_day):
                return False
            
            # Agregar request actual
            request_times.append(now)
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando rate limit en memoria: {e}")
            return True
    
    async def _log_response(self, request: Request, response: Response, 
                          response_time: float, request_id: str):
        """Log de respuesta"""
        try:
            # Buscar el log de request correspondiente
            for log in reversed(self.request_logs):
                if log.id == request_id:
                    log.response_status = response.status_code
                    log.response_time = response_time
                    
                    # Actualizar métricas
                    self.metrics["requests_by_status"][response.status_code] += 1
                    
                    if 200 <= response.status_code < 300:
                        self.metrics["successful_requests"] += 1
                    else:
                        self.metrics["failed_requests"] += 1
                    
                    # Actualizar tiempo promedio de respuesta
                    total_requests = self.metrics["total_requests"]
                    if total_requests > 0:
                        current_avg = self.metrics["average_response_time"]
                        self.metrics["average_response_time"] = (
                            (current_avg * (total_requests - 1) + response_time) / total_requests
                        )
                    
                    break
            
        except Exception as e:
            logger.error(f"Error loggeando respuesta: {e}")
    
    async def create_api_key(self, name: str, user_id: str, 
                           permissions: List[str], 
                           rate_limit_rule_id: str = "default") -> APIKey:
        """Crear nueva clave de API"""
        try:
            # Generar clave única
            api_key = secrets.token_urlsafe(32)
            
            # Obtener regla de rate limiting
            rate_limit_rule = self.rate_limit_rules.get(rate_limit_rule_id)
            if not rate_limit_rule:
                rate_limit_rule = self.rate_limit_rules["default"]
            
            # Crear objeto APIKey
            key_obj = APIKey(
                key=api_key,
                name=name,
                user_id=user_id,
                permissions=permissions,
                rate_limit=rate_limit_rule
            )
            
            # Almacenar
            self.api_keys[api_key] = key_obj
            
            logger.info(f"API key creada: {name} para usuario {user_id}")
            return key_obj
            
        except Exception as e:
            logger.error(f"Error creando API key: {e}")
            raise
    
    async def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validar clave de API"""
        try:
            key_obj = self.api_keys.get(api_key)
            
            if not key_obj or not key_obj.is_active:
                return None
            
            # Verificar expiración
            if key_obj.expires_at:
                expires_at = datetime.fromisoformat(key_obj.expires_at)
                if datetime.now(timezone.utc) > expires_at:
                    return None
            
            # Actualizar último uso
            key_obj.last_used = datetime.now(timezone.utc).isoformat()
            key_obj.usage_count += 1
            
            return key_obj
            
        except Exception as e:
            logger.error(f"Error validando API key: {e}")
            return None
    
    async def revoke_api_key(self, api_key: str) -> bool:
        """Revocar clave de API"""
        try:
            if api_key in self.api_keys:
                self.api_keys[api_key].is_active = False
                logger.info(f"API key revocada: {api_key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error revocando API key: {e}")
            return False
    
    async def get_gateway_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del gateway"""
        try:
            return {
                "metrics": self.metrics,
                "active_api_keys": len([k for k in self.api_keys.values() if k.is_active]),
                "total_api_keys": len(self.api_keys),
                "rate_limit_rules": len(self.rate_limit_rules),
                "middleware_count": len(self.middleware_stack),
                "request_logs_count": len(self.request_logs),
                "redis_connected": self.redis_client is not None,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas del gateway: {e}")
            return {}
    
    async def get_request_logs(self, limit: int = 100, 
                             status_code: int = None,
                             user_id: str = None) -> List[RequestLog]:
        """Obtener logs de requests"""
        try:
            logs = self.request_logs
            
            # Filtrar por status code
            if status_code:
                logs = [log for log in logs if log.response_status == status_code]
            
            # Filtrar por user_id
            if user_id:
                logs = [log for log in logs if log.user_id == user_id]
            
            # Ordenar por timestamp (más recientes primero)
            logs.sort(key=lambda x: x.timestamp, reverse=True)
            
            return logs[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo logs de requests: {e}")
            return []


























