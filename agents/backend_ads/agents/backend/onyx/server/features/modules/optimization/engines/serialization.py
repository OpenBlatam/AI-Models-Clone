"""
Serialization Engine - Ultra-Fast Data Serialization.

Consolidates serialization functionality from:
- ultra_performance_optimizers.py
- core_optimizers.py  
- nexus_optimizer.py
"""

import time
from typing import Any, Union, Tuple
import structlog

from ..config import OptimizationSettings, SerializationFormat
from ..exceptions import SerializationError, handle_serialization_error

logger = structlog.get_logger(__name__)

# Optional high-performance libraries
try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    ORJSON_AVAILABLE = False

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

try:
    import xxhash
    XXHASH_AVAILABLE = True
except ImportError:
    XXHASH_AVAILABLE = False

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False


class SerializationEngine:
    """Ultra-fast serialization engine with automatic format selection."""
    
    def __init__(self, config: OptimizationSettings):
        self.config = config
        self.format = self._determine_best_format()
        self.stats = {
            "serializations": 0,
            "deserializations": 0,
            "total_time_ms": 0.0,
            "errors": 0
        }
    
    def _determine_best_format(self) -> SerializationFormat:
        """Determine the best available serialization format."""
        if self.config.serialization_format != SerializationFormat.AUTO:
            return self.config.serialization_format
        
        # Auto-select best available format
        if ORJSON_AVAILABLE:
            return SerializationFormat.ORJSON
        elif MSGPACK_AVAILABLE:
            return SerializationFormat.MSGPACK
        else:
            return SerializationFormat.JSON
    
    def serialize(self, obj: Any, compress: bool = None) -> bytes:
        """Serialize object using optimal format."""
        if compress is None:
            compress = self.config.enable_compression
        
        start_time = time.perf_counter()
        
        try:
            # Core serialization
            if self.format == SerializationFormat.ORJSON:
                data = orjson.dumps(obj, option=orjson.OPT_FAST_SERIALIZE)
            elif self.format == SerializationFormat.MSGPACK:
                data = msgpack.packb(obj, use_bin_type=True)
            else:  # JSON fallback
                import json
                data = json.dumps(obj, separators=(',', ':')).encode('utf-8')
            
            # Optional compression
            if compress and len(data) > 1024:  # Only compress if > 1KB
                data = self._compress_data(data)
            
            # Update stats
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.stats["serializations"] += 1
            self.stats["total_time_ms"] += duration_ms
            
            return data
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.warning("Serialization failed", format=self.format.value, error=str(e))
            raise handle_serialization_error(e, self.format.value)
    
    def deserialize(self, data: bytes, compressed: bool = False) -> Any:
        """Deserialize data using optimal format."""
        start_time = time.perf_counter()
        
        try:
            # Decompress if needed
            if compressed:
                data = self._decompress_data(data)
            
            # Core deserialization
            if self.format == SerializationFormat.ORJSON:
                result = orjson.loads(data)
            elif self.format == SerializationFormat.MSGPACK:
                result = msgpack.unpackb(data, raw=False)
            else:  # JSON fallback
                import json
                result = json.loads(data.decode('utf-8'))
            
            # Update stats
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.stats["deserializations"] += 1
            self.stats["total_time_ms"] += duration_ms
            
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.warning("Deserialization failed", format=self.format.value, error=str(e))
            raise handle_serialization_error(e, self.format.value)
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using best available algorithm."""
        try:
            if LZ4_AVAILABLE:
                return lz4.frame.compress(data, compression_level=self.config.compression_level)
            else:
                import gzip
                return gzip.compress(data, compresslevel=self.config.compression_level)
        except Exception as e:
            logger.warning("Compression failed, returning uncompressed", error=str(e))
            return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data."""
        try:
            if LZ4_AVAILABLE:
                return lz4.frame.decompress(data)
            else:
                import gzip
                return gzip.decompress(data)
        except Exception as e:
            logger.warning("Decompression failed", error=str(e))
            raise SerializationError(f"Decompression failed: {e}")
    
    @staticmethod
    def hash_fast(data: Union[str, bytes], seed: int = 42) -> str:
        """Ultra-fast hashing using best available algorithm."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            if BLAKE3_AVAILABLE:
                return blake3.blake3(data).hexdigest()
            elif XXHASH_AVAILABLE:
                return xxhash.xxh64(data, seed=seed).hexdigest()
            else:
                import hashlib
                return hashlib.sha256(data).hexdigest()
        except Exception:
            # Ultimate fallback
            import hashlib
            return hashlib.md5(data).hexdigest()
    
    def get_stats(self) -> dict:
        """Get serialization performance statistics."""
        total_ops = self.stats["serializations"] + self.stats["deserializations"]
        avg_time = self.stats["total_time_ms"] / total_ops if total_ops > 0 else 0
        
        return {
            "format_used": self.format.value,
            "total_operations": total_ops,
            "serializations": self.stats["serializations"],
            "deserializations": self.stats["deserializations"],
            "avg_time_ms": avg_time,
            "error_count": self.stats["errors"],
            "libraries_available": {
                "orjson": ORJSON_AVAILABLE,
                "msgpack": MSGPACK_AVAILABLE,
                "xxhash": XXHASH_AVAILABLE,
                "blake3": BLAKE3_AVAILABLE,
                "lz4": LZ4_AVAILABLE
            }
        } 