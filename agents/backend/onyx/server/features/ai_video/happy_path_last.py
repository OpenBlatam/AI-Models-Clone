"""
🎯 HAPPY PATH LAST - IMPROVED READABILITY PATTERN
================================================

Sistema que implementa el principio "happy path last" donde todas las condiciones
de error se manejan primero y la lógica principal se coloca al final para mejorar
la legibilidad del código.
"""

import logging
import time
import asyncio
from typing import (
    Any, Optional, Union, Dict, List, Tuple, Callable, 
    TypeVar, Generic, Protocol, runtime_checkable
)
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
import numpy as np
import functools
import inspect

from .error_handling import (
    AIVideoError, ErrorCategory, ErrorSeverity, ErrorContext,
    ValidationError, SystemError, ConfigurationError
)

# =============================================================================
# HAPPY PATH PATTERNS
# =============================================================================

class HappyPathPattern(Enum):
    """Patrones de happy path."""
    VALIDATION_FIRST = auto()
    ERROR_HANDLING_FIRST = auto()
    RESOURCE_CHECK_FIRST = auto()
    GUARD_CLAUSE_FIRST = auto()
    CLEANUP_LAST = auto()

@dataclass
class HappyPathResult:
    """Resultado del happy path."""
    success: bool
    value: Any
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

# =============================================================================
# HAPPY PATH DECORATORS
# =============================================================================

def happy_path_last(
    validators: List[Callable] = None,
    error_handlers: List[Callable] = None,
    cleanup_handlers: List[Callable] = None
):
    """Decorador para implementar happy path last."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Validaciones al inicio
            if validators:
                for validator in validators:
                    try:
                        result = validator(*args, **kwargs)
                        if not result:
                            return {"error": f"Validation failed in {func.__name__}"}
                    except Exception as e:
                        return {"error": f"Validation error: {e}"}
            
            # 2. Manejo de errores al inicio
            if error_handlers:
                for handler in error_handlers:
                    try:
                        result = handler(*args, **kwargs)
                        if result is not None:
                            return result
                    except Exception as e:
                        return {"error": f"Error handler failed: {e}"}
            
            # 3. Happy path al final
            try:
                result = func(*args, **kwargs)
                
                # 4. Cleanup al final
                if cleanup_handlers:
                    for handler in cleanup_handlers:
                        try:
                            handler(*args, **kwargs)
                        except Exception as e:
                            logging.warning(f"Cleanup handler failed: {e}")
                
                return result
            except Exception as e:
                return {"error": f"Function execution failed: {e}"}
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 1. Validaciones al inicio
            if validators:
                for validator in validators:
                    try:
                        if asyncio.iscoroutinefunction(validator):
                            result = await validator(*args, **kwargs)
                        else:
                            result = validator(*args, **kwargs)
                        
                        if not result:
                            return {"error": f"Validation failed in {func.__name__}"}
                    except Exception as e:
                        return {"error": f"Validation error: {e}"}
            
            # 2. Manejo de errores al inicio
            if error_handlers:
                for handler in error_handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            result = await handler(*args, **kwargs)
                        else:
                            result = handler(*args, **kwargs)
                        
                        if result is not None:
                            return result
                    except Exception as e:
                        return {"error": f"Error handler failed: {e}"}
            
            # 3. Happy path al final
            try:
                result = await func(*args, **kwargs)
                
                # 4. Cleanup al final
                if cleanup_handlers:
                    for handler in cleanup_handlers:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(*args, **kwargs)
                            else:
                                handler(*args, **kwargs)
                        except Exception as e:
                            logging.warning(f"Cleanup handler failed: {e}")
                
                return result
            except Exception as e:
                return {"error": f"Function execution failed: {e}"}
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator

# =============================================================================
# HAPPY PATH PATTERNS
# =============================================================================

class HappyPathPatterns:
    """Patrones para implementar happy path last."""
    
    @staticmethod
    def validation_first_pattern(func: Callable) -> Callable:
        """Patrón: validaciones primero, happy path al final."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Validaciones al inicio
            if not _validate_inputs(*args, **kwargs):
                return {"error": "Input validation failed"}
            
            if not _validate_resources(*args, **kwargs):
                return {"error": "Resource validation failed"}
            
            if not _validate_state(*args, **kwargs):
                return {"error": "State validation failed"}
            
            # 2. Happy path al final
            return func(*args, **kwargs)
        
        return wrapper
    
    @staticmethod
    def error_handling_first_pattern(func: Callable) -> Callable:
        """Patrón: manejo de errores primero, happy path al final."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Manejo de errores al inicio
            error_result = _handle_common_errors(*args, **kwargs)
            if error_result is not None:
                return error_result
            
            error_result = _handle_system_errors(*args, **kwargs)
            if error_result is not None:
                return error_result
            
            error_result = _handle_business_errors(*args, **kwargs)
            if error_result is not None:
                return error_result
            
            # 2. Happy path al final
            return func(*args, **kwargs)
        
        return wrapper
    
    @staticmethod
    def guard_clause_first_pattern(func: Callable) -> Callable:
        """Patrón: guard clauses primero, happy path al final."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Guard clauses al inicio
            if _is_none_or_empty(*args, **kwargs):
                return {"error": "Input is None or empty"}
            
            if _is_invalid_format(*args, **kwargs):
                return {"error": "Invalid format"}
            
            if _is_insufficient_resources(*args, **kwargs):
                return {"error": "Insufficient resources"}
            
            if _is_system_overloaded(*args, **kwargs):
                return {"error": "System overloaded"}
            
            # 2. Happy path al final
            return func(*args, **kwargs)
        
        return wrapper

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _validate_inputs(*args, **kwargs) -> bool:
    """Validar inputs."""
    for arg in args:
        if arg is None:
            return False
    
    for value in kwargs.values():
        if value is None:
            return False
    
    return True

def _validate_resources(*args, **kwargs) -> bool:
    """Validar recursos."""
    import psutil
    
    # Verificar memoria
    available_memory = psutil.virtual_memory().available / (1024 * 1024 * 1024)  # GB
    if available_memory < 1.0:  # Mínimo 1GB
        return False
    
    # Verificar CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    if cpu_percent > 90.0:
        return False
    
    return True

def _validate_state(*args, **kwargs) -> bool:
    """Validar estado del sistema."""
    # Implementar validaciones de estado específicas
    return True

def _handle_common_errors(*args, **kwargs) -> Optional[Dict[str, Any]]:
    """Manejar errores comunes."""
    # Verificar errores comunes
    return None

def _handle_system_errors(*args, **kwargs) -> Optional[Dict[str, Any]]:
    """Manejar errores del sistema."""
    # Verificar errores del sistema
    return None

def _handle_business_errors(*args, **kwargs) -> Optional[Dict[str, Any]]:
    """Manejar errores de negocio."""
    # Verificar errores de negocio
    return None

def _is_none_or_empty(*args, **kwargs) -> bool:
    """Verificar si inputs son None o vacíos."""
    for arg in args:
        if arg is None:
            return True
        
        if isinstance(arg, (str, list, tuple, dict, set)) and len(arg) == 0:
            return True
        
        if isinstance(arg, np.ndarray) and arg.size == 0:
            return True
    
    return False

def _is_invalid_format(*args, **kwargs) -> bool:
    """Verificar formato inválido."""
    # Implementar validaciones de formato
    return False

def _is_insufficient_resources(*args, **kwargs) -> bool:
    """Verificar recursos insuficientes."""
    import psutil
    
    available_memory = psutil.virtual_memory().available / (1024 * 1024 * 1024)
    return available_memory < 1.0

def _is_system_overloaded(*args, **kwargs) -> bool:
    """Verificar si sistema está sobrecargado."""
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    return cpu_percent > 90.0

# =============================================================================
# HAPPY PATH EXAMPLES
# =============================================================================

def process_video_happy_path_last(video_path: str, batch_size: int, quality: float) -> Dict[str, Any]:
    """
    Procesar video usando happy path last.
    
    Patrón: Todas las validaciones y manejo de errores al inicio,
    lógica principal al final.
    """
    # 1. VALIDACIONES AL INICIO
    if video_path is None:
        return {"error": "video_path is required", "code": "MISSING_PATH"}
    
    if not Path(video_path).exists():
        return {"error": f"Video file not found: {video_path}", "code": "FILE_NOT_FOUND"}
    
    if batch_size <= 0 or batch_size > 32:
        return {"error": f"Invalid batch_size: {batch_size}", "code": "INVALID_BATCH"}
    
    if quality < 0.0 or quality > 1.0:
        return {"error": f"Invalid quality: {quality}", "code": "INVALID_QUALITY"}
    
    # 2. VERIFICACIONES DE RECURSOS AL INICIO
    import psutil
    available_memory = psutil.virtual_memory().available / (1024 * 1024 * 1024)
    if available_memory < 1.0:
        return {"error": "Insufficient memory", "code": "INSUFFICIENT_MEMORY"}
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    if cpu_percent > 90.0:
        return {"error": "System overloaded", "code": "SYSTEM_OVERLOADED"}
    
    # 3. VERIFICACIONES DE ESTADO AL INICIO
    # (Aquí se pueden agregar verificaciones de estado del sistema)
    
    # 4. HAPPY PATH AL FINAL
    print(f"✅ Procesando video: {video_path}")
    print(f"✅ Batch size: {batch_size}")
    print(f"✅ Quality: {quality}")
    
    # Simular procesamiento
    time.sleep(1)
    
    return {
        "success": True,
        "video_path": video_path,
        "batch_size": batch_size,
        "quality": quality,
        "processed": True
    }

def load_model_happy_path_last(model_path: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cargar modelo usando happy path last.
    
    Patrón: Validaciones al inicio, carga al final.
    """
    # 1. VALIDACIONES AL INICIO
    if model_path is None:
        return {"error": "model_path is required", "code": "MISSING_PATH"}
    
    if not Path(model_path).exists():
        return {"error": f"Model file not found: {model_path}", "code": "FILE_NOT_FOUND"}
    
    if model_config is None:
        return {"error": "model_config is required", "code": "MISSING_CONFIG"}
    
    if not isinstance(model_config, dict):
        return {"error": "model_config must be a dictionary", "code": "INVALID_CONFIG_TYPE"}
    
    # 2. VALIDACIONES DE CONFIGURACIÓN AL INICIO
    required_keys = {"model_type", "batch_size", "learning_rate"}
    missing_keys = required_keys - set(model_config.keys())
    if missing_keys:
        return {"error": f"Missing required keys: {missing_keys}", "code": "MISSING_KEYS"}
    
    batch_size = model_config.get("batch_size")
    if batch_size <= 0 or batch_size > 64:
        return {"error": f"Invalid batch_size in config: {batch_size}", "code": "INVALID_BATCH"}
    
    lr = model_config.get("learning_rate")
    if lr <= 0.0 or lr > 1.0:
        return {"error": f"Invalid learning_rate: {lr}", "code": "INVALID_LR"}
    
    # 3. VERIFICACIONES DE RECURSOS AL INICIO
    import psutil
    available_memory = psutil.virtual_memory().available / (1024 * 1024 * 1024)
    if available_memory < 2.0:  # Mínimo 2GB para modelos
        return {"error": "Insufficient memory for model", "code": "INSUFFICIENT_MEMORY"}
    
    # 4. HAPPY PATH AL FINAL
    print(f"✅ Cargando modelo: {model_path}")
    print(f"✅ Configuración: {model_config}")
    
    # Simular carga de modelo
    time.sleep(2)
    
    return {
        "success": True,
        "model_path": model_path,
        "config": model_config,
        "loaded": True
    }

def process_data_happy_path_last(data: np.ndarray, operation: str = "normalize") -> np.ndarray:
    """
    Procesar datos usando happy path last.
    
    Patrón: Validaciones al inicio, procesamiento al final.
    """
    # 1. VALIDACIONES AL INICIO
    if data is None:
        return np.array([])
    
    if not isinstance(data, np.ndarray):
        return np.array([])
    
    if data.size == 0:
        return np.array([])
    
    # 2. VALIDACIONES DE DATOS AL INICIO
    if np.isnan(data).any() or np.isinf(data).any():
        return np.array([])
    
    # 3. VALIDACIONES DE OPERACIÓN AL INICIO
    valid_operations = {"normalize", "scale", "filter", "transform"}
    if operation not in valid_operations:
        return np.array([])
    
    # 4. VERIFICACIONES DE MEMORIA AL INICIO
    memory_usage = data.nbytes / (1024 * 1024 * 1024)  # GB
    if memory_usage > 1.0:  # Máximo 1GB
        return np.array([])
    
    # 5. HAPPY PATH AL FINAL
    print(f"✅ Procesando datos: {data.shape}")
    print(f"✅ Operación: {operation}")
    
    # Simular procesamiento
    if operation == "normalize":
        result = (data - np.min(data)) / (np.max(data) - np.min(data))
    elif operation == "scale":
        result = data * 2.0
    elif operation == "filter":
        result = data * 0.5
    else:
        result = data
    
    return result

# =============================================================================
# DECORATOR EXAMPLES
# =============================================================================

@happy_path_last(
    validators=[
        lambda video_path, **kwargs: video_path is not None,
        lambda video_path, **kwargs: Path(video_path).exists(),
        lambda batch_size, **kwargs: 0 < batch_size <= 32,
        lambda quality, **kwargs: 0.0 <= quality <= 1.0
    ],
    error_handlers=[
        lambda **kwargs: {"error": "Insufficient memory"} if _is_insufficient_resources() else None,
        lambda **kwargs: {"error": "System overloaded"} if _is_system_overloaded() else None
    ],
    cleanup_handlers=[
        lambda **kwargs: logging.info("Video processing completed")
    ]
)
def process_video_decorated(video_path: str, batch_size: int, quality: float) -> Dict[str, Any]:
    """Procesar video usando decorador happy path last."""
    # HAPPY PATH AL FINAL
    print(f"✅ Procesando video: {video_path}")
    time.sleep(1)
    return {"success": True, "video_path": video_path}

@happy_path_last(
    validators=[
        lambda data, **kwargs: data is not None,
        lambda data, **kwargs: isinstance(data, np.ndarray),
        lambda data, **kwargs: data.size > 0,
        lambda data, **kwargs: not np.isnan(data).any()
    ]
)
def process_data_decorated(data: np.ndarray) -> np.ndarray:
    """Procesar datos usando decorador happy path last."""
    # HAPPY PATH AL FINAL
    print(f"✅ Procesando datos: {data.shape}")
    return data * 2.0

# =============================================================================
# ASYNC EXAMPLES
# =============================================================================

async def async_process_video_happy_path_last(video_path: str, batch_size: int, quality: float) -> Dict[str, Any]:
    """
    Procesar video de forma asíncrona usando happy path last.
    """
    # 1. VALIDACIONES AL INICIO
    if video_path is None:
        return {"error": "video_path is required"}
    
    if not Path(video_path).exists():
        return {"error": f"Video file not found: {video_path}"}
    
    if batch_size <= 0 or batch_size > 32:
        return {"error": f"Invalid batch_size: {batch_size}"}
    
    if quality < 0.0 or quality > 1.0:
        return {"error": f"Invalid quality: {quality}"}
    
    # 2. VERIFICACIONES DE RECURSOS AL INICIO
    import psutil
    available_memory = psutil.virtual_memory().available / (1024 * 1024 * 1024)
    if available_memory < 1.0:
        return {"error": "Insufficient memory"}
    
    # 3. HAPPY PATH AL FINAL
    print(f"✅ Procesando video async: {video_path}")
    
    # Simular procesamiento asíncrono
    await asyncio.sleep(2)
    
    return {
        "success": True,
        "video_path": video_path,
        "batch_size": batch_size,
        "quality": quality,
        "processed": True
    }

@happy_path_last(
    validators=[
        lambda model_path, **kwargs: model_path is not None,
        lambda model_path, **kwargs: Path(model_path).exists(),
        lambda batch_size, **kwargs: 0 < batch_size <= 64
    ]
)
async def async_load_model_decorated(model_path: str, batch_size: int) -> Dict[str, Any]:
    """Cargar modelo de forma asíncrona usando decorador happy path last."""
    # HAPPY PATH AL FINAL
    print(f"✅ Cargando modelo async: {model_path}")
    await asyncio.sleep(1)
    return {"success": True, "model_path": model_path}

# =============================================================================
# COMPLEX EXAMPLES
# =============================================================================

class VideoProcessingPipeline:
    """Pipeline de procesamiento usando happy path last."""
    
    def __init__(self):
        self.loaded_models = set()
        self.processing = False
        self.max_concurrent = 3
        self.current_operations = 0
    
    def process_video_pipeline(self, video_path: str, model_name: str, batch_size: int, quality: float) -> Dict[str, Any]:
        """
        Pipeline completo usando happy path last.
        
        Patrón: Todas las validaciones al inicio, procesamiento al final.
        """
        # 1. VALIDACIONES DE ENTRADA AL INICIO
        if video_path is None:
            return {"error": "video_path is required", "code": "MISSING_PATH"}
        
        if not Path(video_path).exists():
            return {"error": f"Video file not found: {video_path}", "code": "FILE_NOT_FOUND"}
        
        if model_name is None:
            return {"error": "model_name is required", "code": "MISSING_MODEL"}
        
        if batch_size <= 0 or batch_size > 32:
            return {"error": f"Invalid batch_size: {batch_size}", "code": "INVALID_BATCH"}
        
        if quality < 0.0 or quality > 1.0:
            return {"error": f"Invalid quality: {quality}", "code": "INVALID_QUALITY"}
        
        # 2. VALIDACIONES DE FORMATO AL INICIO
        valid_formats = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        if Path(video_path).suffix.lower() not in valid_formats:
            return {"error": f"Unsupported format: {Path(video_path).suffix}", "code": "UNSUPPORTED_FORMAT"}
        
        # 3. VALIDACIONES DE MODELO AL INICIO
        if model_name not in self.loaded_models:
            return {"error": f"Model not loaded: {model_name}", "code": "MODEL_NOT_LOADED"}
        
        # 4. VALIDACIONES DE ESTADO AL INICIO
        if self.processing:
            return {"error": "Already processing another video", "code": "ALREADY_PROCESSING"}
        
        if self.current_operations >= self.max_concurrent:
            return {"error": "Too many concurrent operations", "code": "TOO_MANY_OPERATIONS"}
        
        # 5. VERIFICACIONES DE RECURSOS AL INICIO
        import psutil
        available_memory = psutil.virtual_memory().available / (1024 * 1024 * 1024)
        if available_memory < 2.0:
            return {"error": "Insufficient memory", "code": "INSUFFICIENT_MEMORY"}
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > 85.0:
            return {"error": "System overloaded", "code": "SYSTEM_OVERLOADED"}
        
        # 6. HAPPY PATH AL FINAL
        self.processing = True
        self.current_operations += 1
        
        try:
            print(f"🚀 Iniciando pipeline para: {video_path}")
            print(f"📹 Modelo: {model_name}")
            print(f"⚙️ Batch size: {batch_size}")
            print(f"🎯 Quality: {quality}")
            
            # Simular procesamiento
            time.sleep(3)
            
            return {
                "success": True,
                "video_path": video_path,
                "model_name": model_name,
                "batch_size": batch_size,
                "quality": quality,
                "processed": True
            }
        
        finally:
            self.processing = False
            self.current_operations -= 1
    
    def load_model(self, model_path: str, model_name: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cargar modelo usando happy path last.
        """
        # 1. VALIDACIONES AL INICIO
        if model_path is None:
            return {"error": "model_path is required", "code": "MISSING_PATH"}
        
        if not Path(model_path).exists():
            return {"error": f"Model file not found: {model_path}", "code": "FILE_NOT_FOUND"}
        
        if model_name is None:
            return {"error": "model_name is required", "code": "MISSING_NAME"}
        
        if model_name in self.loaded_models:
            return {"error": f"Model already loaded: {model_name}", "code": "ALREADY_LOADED"}
        
        if model_config is None:
            return {"error": "model_config is required", "code": "MISSING_CONFIG"}
        
        if not isinstance(model_config, dict):
            return {"error": "model_config must be a dictionary", "code": "INVALID_CONFIG_TYPE"}
        
        # 2. VALIDACIONES DE CONFIGURACIÓN AL INICIO
        required_keys = {"model_type", "batch_size", "learning_rate"}
        missing_keys = required_keys - set(model_config.keys())
        if missing_keys:
            return {"error": f"Missing required keys: {missing_keys}", "code": "MISSING_KEYS"}
        
        batch_size = model_config.get("batch_size")
        if batch_size <= 0 or batch_size > 64:
            return {"error": f"Invalid batch_size in config: {batch_size}", "code": "INVALID_BATCH"}
        
        lr = model_config.get("learning_rate")
        if lr <= 0.0 or lr > 1.0:
            return {"error": f"Invalid learning_rate: {lr}", "code": "INVALID_LR"}
        
        # 3. VERIFICACIONES DE RECURSOS AL INICIO
        import psutil
        available_memory = psutil.virtual_memory().available / (1024 * 1024 * 1024)
        if available_memory < 1.0:
            return {"error": "Insufficient memory for model", "code": "INSUFFICIENT_MEMORY"}
        
        # 4. HAPPY PATH AL FINAL
        print(f"📦 Cargando modelo: {model_name}")
        print(f"📁 Archivo: {model_path}")
        print(f"⚙️ Configuración: {model_config}")
        
        # Simular carga
        time.sleep(2)
        
        self.loaded_models.add(model_name)
        
        return {
            "success": True,
            "model_name": model_name,
            "model_path": model_path,
            "config": model_config,
            "loaded": True
        }

# =============================================================================
# COMPARISON EXAMPLES
# =============================================================================

def process_video_mixed_pattern(video_path: str, batch_size: int, quality: float) -> Dict[str, Any]:
    """
    Ejemplo de código con patrón mixto (NO RECOMENDADO).
    
    Este patrón mezcla validaciones con lógica principal, dificultando la lectura.
    """
    print(f"✅ Procesando video: {video_path}")
    
    if video_path is None:
        return {"error": "video_path is required"}
    
    print(f"✅ Batch size: {batch_size}")
    
    if batch_size <= 0 or batch_size > 32:
        return {"error": "Invalid batch size"}
    
    print(f"✅ Quality: {quality}")
    
    if quality < 0.0 or quality > 1.0:
        return {"error": "Invalid quality"}
    
    # Más lógica mezclada con validaciones...
    time.sleep(1)
    
    return {"success": True}

def process_video_happy_path_last_clean(video_path: str, batch_size: int, quality: float) -> Dict[str, Any]:
    """
    Mismo código usando happy path last (RECOMENDADO).
    
    Este patrón es más legible y mantenible.
    """
    # 1. TODAS LAS VALIDACIONES AL INICIO
    if video_path is None:
        return {"error": "video_path is required"}
    
    if not Path(video_path).exists():
        return {"error": "Video file not found"}
    
    if batch_size <= 0 or batch_size > 32:
        return {"error": "Invalid batch size"}
    
    if quality < 0.0 or quality > 1.0:
        return {"error": "Invalid quality"}
    
    # 2. VERIFICACIONES DE RECURSOS AL INICIO
    import psutil
    available_memory = psutil.virtual_memory().available / (1024 * 1024 * 1024)
    if available_memory < 1.0:
        return {"error": "Insufficient memory"}
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    if cpu_percent > 90.0:
        return {"error": "System overloaded"}
    
    # 3. HAPPY PATH AL FINAL - TODA LA LÓGICA PRINCIPAL AQUÍ
    print(f"✅ Procesando video: {video_path}")
    print(f"✅ Batch size: {batch_size}")
    print(f"✅ Quality: {quality}")
    
    # Simular procesamiento
    time.sleep(1)
    
    return {"success": True}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def apply_happy_path_last(func: Callable) -> Callable:
    """Aplicar patrón happy path last a función existente."""
    return HappyPathPatterns.validation_first_pattern(func)

def create_happy_path_validator(conditions: List[Callable]) -> Callable:
    """Crear validador para happy path last."""
    def validator(*args, **kwargs) -> bool:
        for condition in conditions:
            try:
                if not condition(*args, **kwargs):
                    return False
            except Exception:
                return False
        return True
    
    return validator

# =============================================================================
# INITIALIZATION
# =============================================================================

def setup_happy_path_last():
    """Configurar sistema de happy path last."""
    logger = logging.getLogger(__name__)
    logger.info("🎯 Sistema de happy path last inicializado")
    
    return {
        "patterns": HappyPathPatterns,
        "decorators": {
            "happy_path_last": happy_path_last,
            "apply_happy_path_last": apply_happy_path_last
        }
    }

# Configuración automática al importar
happy_path_system = setup_happy_path_last() 