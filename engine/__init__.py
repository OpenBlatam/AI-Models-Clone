"""
MODULAR ADS - Engine Module
=========================

Motor de optimización modular para el sistema de ads.
Gestión de librerías, handlers y performance optimization.
"""

import json
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from ..types import PerformanceTier, Score
from ..config import get_config, OptimizationConfig
from ..utils import TimeUtils, DecoratorUtils

logger = logging.getLogger(__name__)

@dataclass
class LibraryInfo:
    """Información de una librería de optimización"""
    name: str
    available: bool
    score: int
    speed_multiplier: float
    description: str
    handler: Optional[Any] = None

class LibraryScanner:
    """Escáner modular de librerías de optimización"""
    
    def __init__(self):
        self.config = get_config()
        self.scanned_libraries: Dict[str, LibraryInfo] = {}
        self._scan_all_libraries()
    
    def _scan_all_libraries(self):
        """Escanear todas las librerías disponibles"""
        required_libs = self.config.engine.required_libraries
        
        for lib_name in required_libs:
            lib_info = self._scan_library(lib_name)
            self.scanned_libraries[lib_name] = lib_info
        
        logger.info(f"Escaneadas {len(self.scanned_libraries)} librerías")
    
    def _scan_library(self, library_name: str) -> LibraryInfo:
        """Escanear una librería específica"""
        config_info = OptimizationConfig.get_library_info(library_name)
        
        try:
            # Intentar importar la librería
            __import__(library_name)
            
            return LibraryInfo(
                name=library_name,
                available=True,
                score=config_info["score"],
                speed_multiplier=config_info["speed_multiplier"],
                description=config_info["description"]
            )
        
        except ImportError:
            return LibraryInfo(
                name=library_name,
                available=False,
                score=0,
                speed_multiplier=1.0,
                description=config_info["description"]
            )
    
    def get_available_libraries(self) -> List[str]:
        """Obtener librerías disponibles"""
        return [name for name, info in self.scanned_libraries.items() if info.available]
    
    def get_library_info(self, library_name: str) -> Optional[LibraryInfo]:
        """Obtener información de una librería"""
        return self.scanned_libraries.get(library_name)
    
    def calculate_total_score(self) -> Score:
        """Calcular score total de optimización"""
        total_score = sum(
            info.score for info in self.scanned_libraries.values() 
            if info.available
        )
        return min(total_score, 100.0)
    
    def get_performance_tier(self) -> PerformanceTier:
        """Determinar tier de performance"""
        score = self.calculate_total_score()
        
        for tier in PerformanceTier:
            if score >= tier.threshold:
                return tier
        
        return PerformanceTier.STANDARD

class OptimizedHandlers:
    """Gestión de handlers optimizados"""
    
    def __init__(self, scanner: LibraryScanner):
        self.scanner = scanner
        self.handlers: Dict[str, Dict[str, Any]] = {}
        self._setup_all_handlers()
    
    def _setup_all_handlers(self):
        """Configurar todos los handlers"""
        self.handlers["json"] = self._setup_json_handler()
        self.handlers["hash"] = self._setup_hash_handler()
        self.handlers["compression"] = self._setup_compression_handler()
        self.handlers["async"] = self._setup_async_handler()
        
        logger.info(f"Configurados {len(self.handlers)} handlers optimizados")
    
    def _setup_json_handler(self) -> Dict[str, Any]:
        """Configurar handler JSON optimizado"""
        orjson_info = self.scanner.get_library_info("orjson")
        
        if orjson_info and orjson_info.available:
            import orjson
            return {
                "dumps": lambda x: orjson.dumps(x).decode(),
                "loads": orjson.loads,
                "name": "orjson",
                "speed": orjson_info.speed_multiplier
            }
        else:
            return {
                "dumps": json.dumps,
                "loads": json.loads,
                "name": "json",
                "speed": 1.0
            }
    
    def _setup_hash_handler(self) -> Dict[str, Any]:
        """Configurar handler hash optimizado"""
        blake3_info = self.scanner.get_library_info("blake3")
        
        if blake3_info and blake3_info.available:
            import blake3
            return {
                "hash": lambda x: blake3.blake3(x.encode()).hexdigest()[:16],
                "name": "blake3",
                "speed": blake3_info.speed_multiplier
            }
        else:
            import hashlib
            return {
                "hash": lambda x: hashlib.sha256(x.encode()).hexdigest()[:16],
                "name": "sha256",
                "speed": 1.0
            }
    
    def _setup_compression_handler(self) -> Dict[str, Any]:
        """Configurar handler compresión optimizado"""
        lz4_info = self.scanner.get_library_info("lz4")
        
        if lz4_info and lz4_info.available:
            import lz4.frame
            return {
                "compress": lz4.frame.compress,
                "decompress": lz4.frame.decompress,
                "name": "lz4",
                "speed": lz4_info.speed_multiplier
            }
        else:
            import gzip
            return {
                "compress": gzip.compress,
                "decompress": gzip.decompress,
                "name": "gzip",
                "speed": 2.0
            }
    
    def _setup_async_handler(self) -> Dict[str, Any]:
        """Configurar handler async optimizado"""
        uvloop_info = self.scanner.get_library_info("uvloop")
        
        if uvloop_info and uvloop_info.available:
            try:
                import uvloop
                uvloop.install()
                return {
                    "name": "uvloop",
                    "speed": uvloop_info.speed_multiplier,
                    "installed": True
                }
            except Exception as e:
                logger.warning(f"Error instalando uvloop: {e}")
        
        return {
            "name": "asyncio",
            "speed": 1.0,
            "installed": False
        }
    
    def get_handler(self, handler_type: str) -> Optional[Dict[str, Any]]:
        """Obtener handler específico"""
        return self.handlers.get(handler_type)

class CircuitBreaker:
    """Circuit breaker modular para tolerancia a fallos"""
    
    def __init__(self, threshold: int = 3, timeout: float = 30.0):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
        
        logger.info(f"CircuitBreaker inicializado (threshold={threshold}, timeout={timeout}s)")
    
    def protect(self, func: Callable) -> Callable:
        """Decorador para proteger función con circuit breaker"""
        async def async_wrapper(*args, **kwargs):
            with self.lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure < self.timeout:
                        raise Exception(f"Circuit breaker OPEN - esperando {self.timeout}s")
                    self.state = "HALF_OPEN"
                
                try:
                    result = await func(*args, **kwargs)
                    
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                        logger.info("Circuit breaker recuperado - estado CLOSED")
                    
                    return result
                
                except Exception as e:
                    self.failures += 1
                    self.last_failure = time.time()
                    
                    if self.failures >= self.threshold:
                        self.state = "OPEN"
                        logger.error(f"Circuit breaker OPEN después de {self.failures} fallos")
                    
                    raise
        
        def sync_wrapper(*args, **kwargs):
            # Similar para funciones síncronas
            with self.lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure < self.timeout:
                        raise Exception(f"Circuit breaker OPEN - esperando {self.timeout}s")
                    self.state = "HALF_OPEN"
                
                try:
                    result = func(*args, **kwargs)
                    
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                    
                    return result
                
                except Exception as e:
                    self.failures += 1
                    self.last_failure = time.time()
                    
                    if self.failures >= self.threshold:
                        self.state = "OPEN"
                    
                    raise
        
        import asyncio
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    def get_state(self) -> Dict[str, Any]:
        """Obtener estado del circuit breaker"""
        return {
            "state": self.state,
            "failures": self.failures,
            "threshold": self.threshold,
            "timeout": self.timeout,
            "last_failure": self.last_failure
        }

class OptimizationEngine:
    """Motor principal de optimización modular"""
    
    def __init__(self):
        self.config = get_config()
        self.scanner = LibraryScanner()
        self.handlers = OptimizedHandlers(self.scanner)
        self.circuit_breaker = CircuitBreaker(
            threshold=self.config.engine.circuit_breaker_threshold,
            timeout=self.config.engine.circuit_breaker_timeout
        ) if self.config.engine.enable_circuit_breaker else None
        
        self.metrics = {
            "startup_time": time.time(),
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0
        }
        
        logger.info("OptimizationEngine inicializado")
        self._show_optimization_status()
    
    def _show_optimization_status(self):
        """Mostrar estado de optimización"""
        available_libs = self.scanner.get_available_libraries()
        total_score = self.scanner.calculate_total_score()
        tier = self.scanner.get_performance_tier()
        
        print(f"\n{'='*60}")
        print("🚀 MODULAR ADS OPTIMIZATION ENGINE")
        print(f"{'='*60}")
        print(f"📊 Optimization Score: {total_score:.1f}/100 ({tier.display_name})")
        print(f"📚 Available Libraries: {len(available_libs)}/{len(self.scanner.scanned_libraries)}")
        
        for lib_name, lib_info in self.scanner.scanned_libraries.items():
            status = "✅" if lib_info.available else "❌"
            print(f"   {status} {lib_name}: {lib_info.description}")
        
        print(f"\n🔥 Optimized Handlers:")
        for handler_type, handler_info in self.handlers.handlers.items():
            speed = handler_info.get("speed", 1.0)
            name = handler_info.get("name", "unknown")
            print(f"   {handler_type}: {name} ({speed:.1f}x)")
        
        if self.circuit_breaker:
            print(f"⚡ Circuit Breaker: Enabled (threshold={self.circuit_breaker.threshold})")
        
        print(f"{'='*60}")
    
    def get_optimization_score(self) -> Score:
        """Obtener score de optimización"""
        return self.scanner.calculate_total_score()
    
    def get_performance_tier(self) -> PerformanceTier:
        """Obtener tier de performance"""
        return self.scanner.get_performance_tier()
    
    def get_handler(self, handler_type: str) -> Optional[Dict[str, Any]]:
        """Obtener handler optimizado"""
        return self.handlers.get_handler(handler_type)
    
    @DecoratorUtils.measure_time
    async def benchmark_operation(self, operation_name: str, iterations: int = 1000) -> Dict[str, float]:
        """Benchmark de operaciones optimizadas"""
        json_handler = self.get_handler("json")
        hash_handler = self.get_handler("hash")
        compression_handler = self.get_handler("compression")
        
        # Test data
        test_data = {"content": "test ad content", "type": "facebook", "keywords": ["test", "benchmark"]}
        test_string = "benchmark test string for hashing and compression operations"
        
        # JSON benchmark
        start_time = time.time()
        for _ in range(iterations):
            json_str = json_handler["dumps"](test_data)
            json_handler["loads"](json_str)
        json_time = (time.time() - start_time) * 1000
        
        # Hash benchmark
        start_time = time.time()
        for _ in range(iterations):
            hash_handler["hash"](test_string)
        hash_time = (time.time() - start_time) * 1000
        
        # Compression benchmark
        start_time = time.time()
        for _ in range(iterations):
            compressed = compression_handler["compress"](test_string.encode())
            compression_handler["decompress"](compressed)
        compression_time = (time.time() - start_time) * 1000
        
        return {
            "json_ops_per_sec": (iterations * 2) / (json_time / 1000),  # dumps + loads
            "hash_ops_per_sec": iterations / (hash_time / 1000),
            "compression_ops_per_sec": (iterations * 2) / (compression_time / 1000),  # compress + decompress
            "json_time_ms": json_time,
            "hash_time_ms": hash_time,
            "compression_time_ms": compression_time
        }
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del motor"""
        uptime = time.time() - self.metrics["startup_time"]
        
        return {
            "optimization_score": self.get_optimization_score(),
            "performance_tier": self.get_performance_tier().display_name,
            "available_libraries": len(self.scanner.get_available_libraries()),
            "total_libraries": len(self.scanner.scanned_libraries),
            "uptime_seconds": uptime,
            "uptime_formatted": TimeUtils.format_duration(uptime),
            "total_operations": self.metrics["total_operations"],
            "successful_operations": self.metrics["successful_operations"],
            "failed_operations": self.metrics["failed_operations"],
            "success_rate": (self.metrics["successful_operations"] / max(self.metrics["total_operations"], 1)) * 100,
            "circuit_breaker": self.circuit_breaker.get_state() if self.circuit_breaker else None,
            "handlers": {
                handler_type: {
                    "name": handler_info.get("name"),
                    "speed_multiplier": handler_info.get("speed", 1.0)
                }
                for handler_type, handler_info in self.handlers.handlers.items()
            }
        }
    
    def record_operation(self, success: bool = True):
        """Registrar operación para estadísticas"""
        self.metrics["total_operations"] += 1
        if success:
            self.metrics["successful_operations"] += 1
        else:
            self.metrics["failed_operations"] += 1

# Instancia global del motor
_engine_instance: Optional[OptimizationEngine] = None

def get_engine() -> OptimizationEngine:
    """Obtener instancia global del motor"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = OptimizationEngine()
    return _engine_instance

def set_engine(engine: OptimizationEngine):
    """Establecer instancia global del motor"""
    global _engine_instance
    _engine_instance = engine

__all__ = [
    'LibraryInfo',
    'LibraryScanner',
    'OptimizedHandlers',
    'CircuitBreaker',
    'OptimizationEngine',
    'get_engine',
    'set_engine',
] 