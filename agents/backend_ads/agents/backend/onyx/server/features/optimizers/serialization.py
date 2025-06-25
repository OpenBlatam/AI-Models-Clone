"""
Serialization Optimizer - Ultra-Fast Data Serialization.

Consolidates all serialization functionality with automatic format selection
and fallback handling for maximum performance.
"""

import time
from typing import Any, Optional, Dict
import structlog

# Core serialization imports
import orjson
import msgpack

# Optional imports with fallbacks
try:
    import ujson
    UJSON_AVAILABLE = True
except ImportError:
    UJSON_AVAILABLE = False

try:
    import rapidjson
    RAPIDJSON_AVAILABLE = True
except ImportError:
    RAPIDJSON_AVAILABLE = False

from .config import OptimizationConfig

logger = structlog.get_logger(__name__)


class SerializationOptimizer:
    """High-level serialization optimizer with automatic format selection."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.format = config.serialization_format
        self.serializers = {
            "orjson": OrjsonSerializer(),
            "msgpack": MsgpackSerializer(),
            "ujson": UjsonSerializer() if UJSON_AVAILABLE else None,
            "rapidjson": RapidjsonSerializer() if RAPIDJSON_AVAILABLE else None,
            "pickle": PickleSerializer()
        }
        
        # Remove None serializers
        self.serializers = {k: v for k, v in self.serializers.items() if v is not None}
        
        # Metrics tracking
        self.operations_count = 0
        self.total_serialize_time = 0.0
        self.total_deserialize_time = 0.0
        self.errors = 0
        
        logger.info("Serialization optimizer initialized", 
                   format=self.format,
                   available_formats=list(self.serializers.keys()))
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize object using configured format with fallbacks."""
        start_time = time.perf_counter()
        
        try:
            # Try primary format
            if self.format in self.serializers:
                result = self.serializers[self.format].serialize(obj)
                self._record_success(start_time, "serialize")
                return result
            
            # Fallback to orjson if available
            if "orjson" in self.serializers:
                result = self.serializers["orjson"].serialize(obj)
                self._record_success(start_time, "serialize")
                return result
            
            # Ultimate fallback to pickle
            result = self.serializers["pickle"].serialize(obj)
            self._record_success(start_time, "serialize")
            return result
            
        except Exception as e:
            self._record_error(start_time, "serialize", e)
            # Emergency fallback
            import pickle
            return pickle.dumps(obj)
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize data using configured format with fallbacks."""
        start_time = time.perf_counter()
        
        try:
            # Try primary format
            if self.format in self.serializers:
                result = self.serializers[self.format].deserialize(data)
                self._record_success(start_time, "deserialize")
                return result
            
            # Fallback to orjson if available
            if "orjson" in self.serializers:
                result = self.serializers["orjson"].deserialize(data)
                self._record_success(start_time, "deserialize")
                return result
            
            # Ultimate fallback to pickle
            result = self.serializers["pickle"].deserialize(data)
            self._record_success(start_time, "deserialize")
            return result
            
        except Exception as e:
            self._record_error(start_time, "deserialize", e)
            # Emergency fallback
            import pickle
            return pickle.loads(data)
    
    def auto_select_format(self, test_data: Any) -> str:
        """Auto-select the fastest format for given data type."""
        formats_to_test = ["orjson", "msgpack", "ujson", "rapidjson"]
        available_formats = [f for f in formats_to_test if f in self.serializers]
        
        if not available_formats:
            return "pickle"
        
        results = []
        
        for format_name in available_formats:
            try:
                serializer = self.serializers[format_name]
                
                # Test serialization speed
                start = time.perf_counter()
                serialized = serializer.serialize(test_data)
                serialize_time = time.perf_counter() - start
                
                # Test deserialization speed
                start = time.perf_counter()
                deserialized = serializer.deserialize(serialized)
                deserialize_time = time.perf_counter() - start
                
                # Verify correctness
                if deserialized == test_data:
                    total_time = serialize_time + deserialize_time
                    size = len(serialized)
                    results.append((format_name, total_time, size))
                
            except Exception as e:
                logger.warning(f"Format {format_name} failed auto-select test", error=str(e))
        
        if results:
            # Select fastest format (lowest total time)
            best_format = min(results, key=lambda x: x[1])[0]
            logger.info("Auto-selected serialization format", 
                       format=best_format,
                       test_results=results)
            return best_format
        
        return "pickle"  # Safe fallback
    
    def _record_success(self, start_time: float, operation: str):
        """Record successful operation metrics."""
        duration = time.perf_counter() - start_time
        self.operations_count += 1
        
        if operation == "serialize":
            self.total_serialize_time += duration
        else:
            self.total_deserialize_time += duration
    
    def _record_error(self, start_time: float, operation: str, error: Exception):
        """Record error metrics."""
        duration = time.perf_counter() - start_time
        self.errors += 1
        logger.warning(f"Serialization {operation} error", 
                      error=str(error),
                      duration_ms=duration * 1000)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get serialization performance metrics."""
        if self.operations_count == 0:
            return {"operations": 0, "avg_serialize_ms": 0, "avg_deserialize_ms": 0}
        
        return {
            "operations_count": self.operations_count,
            "avg_serialize_ms": (self.total_serialize_time / self.operations_count) * 1000,
            "avg_deserialize_ms": (self.total_deserialize_time / self.operations_count) * 1000,
            "error_rate": self.errors / self.operations_count,
            "current_format": self.format
        }


class OrjsonSerializer:
    """Ultra-fast orjson serializer."""
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize using orjson with fastest options."""
        return orjson.dumps(obj, option=orjson.OPT_FAST_SERIALIZE)
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize using orjson."""
        return orjson.loads(data)


class MsgpackSerializer:
    """Fast binary msgpack serializer."""
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize using msgpack."""
        return msgpack.packb(obj, use_bin_type=True)
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize using msgpack."""
        return msgpack.unpackb(data, raw=False)


class UjsonSerializer:
    """Fast ujson serializer."""
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize using ujson."""
        if not UJSON_AVAILABLE:
            raise ImportError("ujson not available")
        return ujson.dumps(obj).encode('utf-8')
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize using ujson."""
        if not UJSON_AVAILABLE:
            raise ImportError("ujson not available")
        return ujson.loads(data.decode('utf-8'))


class RapidjsonSerializer:
    """Fast rapidjson serializer."""
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize using rapidjson."""
        if not RAPIDJSON_AVAILABLE:
            raise ImportError("rapidjson not available")
        return rapidjson.dumps(obj).encode('utf-8')
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize using rapidjson."""
        if not RAPIDJSON_AVAILABLE:
            raise ImportError("rapidjson not available")
        return rapidjson.loads(data.decode('utf-8'))


class PickleSerializer:
    """Fallback pickle serializer."""
    
    def serialize(self, obj: Any) -> bytes:
        """Serialize using pickle."""
        import pickle
        return pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    
    def deserialize(self, data: bytes) -> Any:
        """Deserialize using pickle."""
        import pickle
        return pickle.loads(data)


# Convenient aliases
UltraFastSerializer = SerializationOptimizer


def create_serializer(config: Optional[OptimizationConfig] = None) -> SerializationOptimizer:
    """Factory function to create optimized serializer."""
    if config is None:
        from .config import OptimizationConfig
        config = OptimizationConfig()
    
    return SerializationOptimizer(config)


__all__ = [
    "SerializationOptimizer",
    "UltraFastSerializer", 
    "OrjsonSerializer",
    "MsgpackSerializer",
    "UjsonSerializer", 
    "RapidjsonSerializer",
    "PickleSerializer",
    "create_serializer"
] 