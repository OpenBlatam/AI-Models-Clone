"""
ONYX BLOG POST - Utils Module
============================

Utilidades y funciones helper para el sistema de blog posts.
Incluye validación, parseo, métricas y herramientas de integración.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from functools import wraps
import unicodedata

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Error de validación"""
    pass

class ParsingError(Exception):
    """Error de parsing"""
    pass

@dataclass
class TextMetrics:
    """Métricas de texto"""
    word_count: int = 0
    character_count: int = 0
    paragraph_count: int = 0
    sentence_count: int = 0
    reading_time_minutes: int = 0
    readability_score: float = 0.0
    keyword_density: Dict[str, float] = field(default_factory=dict)

class TextAnalyzer:
    """Analizador de texto para blog posts"""
    
    @staticmethod
    def count_words(text: str) -> int:
        """Contar palabras en el texto"""
        if not text:
            return 0
        # Remover HTML tags si los hay
        clean_text = re.sub(r'<[^>]+>', '', text)
        words = re.findall(r'\b\w+\b', clean_text.lower())
        return len(words)
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """Contar oraciones en el texto"""
        if not text:
            return 0
        # Contar puntos, signos de exclamación e interrogación
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    @staticmethod
    def count_paragraphs(text: str) -> int:
        """Contar párrafos en el texto"""
        if not text:
            return 0
        paragraphs = text.split('\n\n')
        return len([p for p in paragraphs if p.strip()])
    
    @staticmethod
    def calculate_reading_time(word_count: int, wpm: int = 200) -> int:
        """Calcular tiempo de lectura en minutos"""
        if word_count <= 0:
            return 0
        return max(1, round(word_count / wpm))
    
    @staticmethod
    def calculate_keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
        """Calcular densidad de keywords"""
        if not text or not keywords:
            return {}
        
        text_lower = text.lower()
        total_words = TextAnalyzer.count_words(text)
        
        if total_words == 0:
            return {}
        
        density = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = text_lower.count(keyword_lower)
            density[keyword] = (count / total_words) * 100
        
        return density
    
    @staticmethod
    def calculate_readability_score(text: str) -> float:
        """Calcular score de legibilidad (aproximado)"""
        if not text:
            return 0.0
        
        words = TextAnalyzer.count_words(text)
        sentences = TextAnalyzer.count_sentences(text)
        
        if sentences == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        
        # Score simplificado: menor es mejor (más legible)
        # Basado en longitud promedio de oraciones
        if avg_sentence_length <= 12:
            return 9.0  # Muy legible
        elif avg_sentence_length <= 17:
            return 7.0  # Legible
        elif avg_sentence_length <= 25:
            return 5.0  # Moderadamente legible
        else:
            return 3.0  # Difícil de leer
    
    @classmethod
    def analyze_text(cls, text: str, keywords: Optional[List[str]] = None) -> TextMetrics:
        """Análisis completo de texto"""
        if keywords is None:
            keywords = []
        
        word_count = cls.count_words(text)
        character_count = len(text)
        paragraph_count = cls.count_paragraphs(text)
        sentence_count = cls.count_sentences(text)
        reading_time = cls.calculate_reading_time(word_count)
        readability_score = cls.calculate_readability_score(text)
        keyword_density = cls.calculate_keyword_density(text, keywords)
        
        return TextMetrics(
            word_count=word_count,
            character_count=character_count,
            paragraph_count=paragraph_count,
            sentence_count=sentence_count,
            reading_time_minutes=reading_time,
            readability_score=readability_score,
            keyword_density=keyword_density
        )

class ContentValidator:
    """Validador de contenido para blog posts"""
    
    @staticmethod
    def validate_topic(topic: str) -> bool:
        """Validar topic del blog post"""
        if not topic or not topic.strip():
            raise ValidationError("Topic no puede estar vacío")
        
        if len(topic.strip()) < 5:
            raise ValidationError("Topic debe tener al menos 5 caracteres")
        
        if len(topic) > 200:
            raise ValidationError("Topic no debe exceder 200 caracteres")
        
        return True
    
    @staticmethod
    def validate_keywords(keywords: List[str], max_keywords: int = 20) -> bool:
        """Validar keywords"""
        if len(keywords) > max_keywords:
            raise ValidationError(f"Máximo {max_keywords} keywords permitidas")
        
        for keyword in keywords:
            if not keyword.strip():
                raise ValidationError("Keywords no pueden estar vacías")
            
            if len(keyword) > 50:
                raise ValidationError("Keywords no deben exceder 50 caracteres")
        
        return True
    
    @staticmethod
    def validate_content_length(content: str, min_words: int, max_words: int) -> bool:
        """Validar longitud del contenido"""
        word_count = TextAnalyzer.count_words(content)
        
        if word_count < min_words:
            raise ValidationError(f"Contenido debe tener al menos {min_words} palabras (actual: {word_count})")
        
        if word_count > max_words:
            raise ValidationError(f"Contenido no debe exceder {max_words} palabras (actual: {word_count})")
        
        return True
    
    @staticmethod
    def validate_json_structure(content: str, required_fields: List[str]) -> bool:
        """Validar estructura JSON del contenido"""
        try:
            data = json.loads(content)
            
            for field in required_fields:
                if field not in data:
                    raise ValidationError(f"Campo requerido '{field}' no encontrado en JSON")
            
            return True
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"JSON inválido: {e}")
    
    @staticmethod
    def sanitize_content(content: str) -> str:
        """Sanitizar contenido"""
        if not content:
            return ""
        
        # Normalizar unicode
        content = unicodedata.normalize('NFKC', content)
        
        # Remover caracteres de control
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        # Limpiar espacios excesivos
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    @staticmethod
    def check_content_filter(content: str, blocked_keywords: List[str]) -> bool:
        """Verificar filtro de contenido"""
        content_lower = content.lower()
        
        for blocked_word in blocked_keywords:
            if blocked_word.lower() in content_lower:
                raise ValidationError(f"Contenido contiene palabra bloqueada: {blocked_word}")
        
        return True

class JSONParser:
    """Parser especializado para respuestas JSON de blog posts"""
    
    @staticmethod
    def parse_blog_post_json(content: str) -> Dict[str, Any]:
        """Parsear JSON de blog post"""
        try:
            # Limpiar contenido
            content = content.strip()
            
            # Buscar JSON en el contenido si está embebido
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group()
            
            data = json.loads(content)
            
            # Validar estructura básica
            required_fields = ["title", "introduction", "main_sections", "conclusion"]
            for field in required_fields:
                if field not in data:
                    raise ParsingError(f"Campo requerido '{field}' no encontrado")
            
            # Validar main_sections
            if not isinstance(data["main_sections"], list):
                raise ParsingError("main_sections debe ser una lista")
            
            for i, section in enumerate(data["main_sections"]):
                if not isinstance(section, dict):
                    raise ParsingError(f"Sección {i} debe ser un diccionario")
                
                if "title" not in section or "content" not in section:
                    raise ParsingError(f"Sección {i} debe tener 'title' y 'content'")
            
            return data
            
        except json.JSONDecodeError as e:
            raise ParsingError(f"Error parsing JSON: {e}")
    
    @staticmethod
    def parse_seo_metadata_json(content: str) -> Dict[str, Any]:
        """Parsear JSON de metadata SEO"""
        try:
            data = json.loads(content.strip())
            
            # Campos esperados para SEO
            expected_fields = ["meta_title", "meta_description", "keywords"]
            
            for field in expected_fields:
                if field not in data:
                    logger.warning(f"Campo SEO '{field}' no encontrado")
            
            return data
            
        except json.JSONDecodeError as e:
            raise ParsingError(f"Error parsing SEO JSON: {e}")
    
    @staticmethod
    def extract_text_from_blog_post(blog_data: Dict[str, Any]) -> str:
        """Extraer texto completo del blog post"""
        parts = []
        
        if "title" in blog_data:
            parts.append(blog_data["title"])
        
        if "introduction" in blog_data:
            parts.append(blog_data["introduction"])
        
        if "main_sections" in blog_data:
            for section in blog_data["main_sections"]:
                if isinstance(section, dict):
                    if "title" in section:
                        parts.append(section["title"])
                    if "content" in section:
                        parts.append(section["content"])
        
        if "conclusion" in blog_data:
            parts.append(blog_data["conclusion"])
        
        if "call_to_action" in blog_data:
            parts.append(blog_data["call_to_action"])
        
        return " ".join(parts)

class HashUtils:
    """Utilidades para hashing y cache keys"""
    
    @staticmethod
    def generate_request_hash(
        topic: str,
        blog_type: str,
        tone: str,
        length: str,
        keywords: List[str]
    ) -> str:
        """Generar hash único para un request"""
        # Crear string único del request
        request_str = f"{topic}|{blog_type}|{tone}|{length}|{','.join(sorted(keywords))}"
        
        # Generar hash MD5
        return hashlib.md5(request_str.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_cache_key(prefix: str, identifier: str) -> str:
        """Generar clave de cache"""
        return f"{prefix}:{identifier}"
    
    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generar ID corto único"""
        import secrets
        return secrets.token_urlsafe(length)[:length]

class MetricsCollector:
    """Recolector de métricas del sistema"""
    
    def __init__(self):
        self.metrics = {
            "requests": [],
            "generation_times": [],
            "word_counts": [],
            "costs": [],
            "errors": [],
            "start_time": time.time()
        }
    
    def record_request(
        self,
        request_id: str,
        blog_type: str,
        generation_time: float,
        word_count: int,
        cost: float,
        success: bool
    ):
        """Registrar métricas de un request"""
        self.metrics["requests"].append({
            "id": request_id,
            "blog_type": blog_type,
            "timestamp": time.time(),
            "generation_time": generation_time,
            "word_count": word_count,
            "cost": cost,
            "success": success
        })
        
        if success:
            self.metrics["generation_times"].append(generation_time)
            self.metrics["word_counts"].append(word_count)
            self.metrics["costs"].append(cost)
    
    def record_error(self, error_type: str, error_message: str):
        """Registrar error"""
        self.metrics["errors"].append({
            "type": error_type,
            "message": error_message,
            "timestamp": time.time()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de métricas"""
        total_requests = len(self.metrics["requests"])
        successful_requests = len(self.metrics["generation_times"])
        failed_requests = len(self.metrics["errors"])
        
        avg_generation_time = 0.0
        avg_word_count = 0.0
        total_cost = 0.0
        
        if successful_requests > 0:
            avg_generation_time = sum(self.metrics["generation_times"]) / successful_requests
            avg_word_count = sum(self.metrics["word_counts"]) / successful_requests
            total_cost = sum(self.metrics["costs"])
        
        uptime = time.time() - self.metrics["start_time"]
        
        return {
            "uptime_seconds": uptime,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0.0,
            "average_generation_time_ms": avg_generation_time,
            "average_word_count": avg_word_count,
            "total_cost_usd": total_cost,
            "average_cost_per_request": total_cost / successful_requests if successful_requests > 0 else 0.0
        }

# Decoradores útiles
def timing_decorator(func: Callable) -> Callable:
    """Decorador para medir tiempo de ejecución"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000  # en ms
            logger.debug(f"{func.__name__} executed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {execution_time:.2f}ms: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            logger.debug(f"{func.__name__} executed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {execution_time:.2f}ms: {e}")
            raise
    
    # Detectar si es función async
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def retry_decorator(max_retries: int = 3, delay: float = 1.0):
    """Decorador para retry automático"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts")
                        raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)
                        logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}, retrying in {wait_time}s")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts")
                        raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def format_duration(seconds: float) -> str:
    """Formatear duración en formato legible"""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def format_size(bytes_size: int) -> str:
    """Formatear tamaño en formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}TB"

__all__ = [
    'ValidationError',
    'ParsingError',
    'TextMetrics',
    'TextAnalyzer',
    'ContentValidator',
    'JSONParser',
    'HashUtils',
    'MetricsCollector',
    'timing_decorator',
    'retry_decorator',
    'format_duration',
    'format_size',
] 