"""
Ultra Optimizer - High-performance operations using best available libraries.
"""

import asyncio
import time
import gc
from typing import Any, Dict, List, Optional, Union, Callable
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp

from .library_detector import detector
from .ultra_config import config

# Import fallbacks
import json
import hashlib
import gzip

class UltraOptimizer:
    """Ultra-performance optimizer using best available libraries."""
    
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=min(32, mp.cpu_count() * 2))
        self._setup_optimized_functions()
        
    def _setup_optimized_functions(self):
        """Setup optimized functions based on available libraries."""
        # JSON serialization
        self._setup_json_functions()
        
        # Hashing functions
        self._setup_hash_functions()
        
        # Compression functions
        self._setup_compression_functions()
        
        # Data processing functions
        self._setup_data_functions()
    
    def _setup_json_functions(self):
        """Setup optimal JSON serialization functions."""
        best_json = detector.get_best_library("json")
        
        if best_json and best_json.name == "simdjson":
            import simdjson
            self.serialize = lambda data: simdjson.dumps(data).encode()
            self.deserialize = lambda data: simdjson.loads(data)
            
        elif best_json and best_json.name == "orjson":
            import orjson
            self.serialize = lambda data: orjson.dumps(data)
            self.deserialize = lambda data: orjson.loads(data)
            
        elif best_json and best_json.name == "rapidjson":
            import rapidjson
            self.serialize = lambda data: rapidjson.dumps(data).encode()
            self.deserialize = lambda data: rapidjson.loads(data)
            
        elif best_json and best_json.name == "ujson":
            import ujson
            self.serialize = lambda data: ujson.dumps(data).encode()
            self.deserialize = lambda data: ujson.loads(data)
            
        else:
            # Fallback to standard json
            self.serialize = lambda data: json.dumps(data).encode()
            self.deserialize = lambda data: json.loads(data)
    
    def _setup_hash_functions(self):
        """Setup optimal hashing functions."""
        best_hash = detector.get_best_library("hash")
        
        if best_hash and best_hash.name == "blake3":
            import blake3
            self.hash_fast = lambda data: blake3.blake3(data.encode()).hexdigest()[:config.HASH_LENGTH]
            
        elif best_hash and best_hash.name == "xxhash":
            import xxhash
            self.hash_fast = lambda data: xxhash.xxh64(data).hexdigest()[:config.HASH_LENGTH]
            
        elif best_hash and best_hash.name == "mmh3":
            import mmh3
            self.hash_fast = lambda data: f"{mmh3.hash(data):08x}"[:config.HASH_LENGTH]
            
        else:
            # Fallback to SHA256
            self.hash_fast = lambda data: hashlib.sha256(data.encode()).hexdigest()[:config.HASH_LENGTH]
    
    def _setup_compression_functions(self):
        """Setup optimal compression functions."""
        best_compression = detector.get_best_library("compression")
        
        if best_compression and best_compression.name == "blosc2":
            import blosc2
            self.compress = lambda data: blosc2.compress(data, clevel=config.COMPRESSION_LEVEL, cname="lz4") if len(data) > 1024 else data
            self.decompress = lambda data: blosc2.decompress(data)
            
        elif best_compression and best_compression.name == "cramjam":
            import cramjam
            self.compress = lambda data: cramjam.lz4.compress_raw(data) if len(data) > 1024 else data
            self.decompress = lambda data: cramjam.lz4.decompress_raw(data)
            
        elif best_compression and best_compression.name == "lz4":
            import lz4.frame
            self.compress = lambda data: lz4.frame.compress(data, compression_level=config.COMPRESSION_LEVEL) if len(data) > 1024 else data
            self.decompress = lambda data: lz4.frame.decompress(data)
            
        elif best_compression and best_compression.name == "zstandard":
            import zstandard as zstd
            compressor = zstd.ZstdCompressor(level=config.COMPRESSION_LEVEL)
            decompressor = zstd.ZstdDecompressor()
            self.compress = lambda data: compressor.compress(data) if len(data) > 1024 else data
            self.decompress = lambda data: decompressor.decompress(data)
            
        else:
            # Fallback to gzip
            self.compress = lambda data: gzip.compress(data, compresslevel=config.COMPRESSION_LEVEL) if len(data) > 1024 else data
            self.decompress = lambda data: gzip.decompress(data)
    
    def _setup_data_functions(self):
        """Setup optimal data processing functions."""
        best_data = detector.get_best_library("data")
        
        if best_data and best_data.name == "polars":
            import polars as pl
            self._process_dataframe = self._process_with_polars
            
        elif best_data and best_data.name == "pyarrow":
            import pyarrow as pa
            self._process_dataframe = self._process_with_arrow
            
        else:
            self._process_dataframe = self._process_with_standard
    
    def _process_with_polars(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process data with Polars (ultra-fast)."""
        import polars as pl
        
        if not data:
            return {"rows": 0, "columns": 0, "processing_time_ms": 0}
        
        start = time.perf_counter()
        df = pl.DataFrame(data)
        
        result = {
            "rows": df.height,
            "columns": df.width,
            "memory_usage_mb": df.estimated_size("mb") if hasattr(df, 'estimated_size') else 0,
            "dtypes": {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)},
            "library": "polars"
        }
        
        result["processing_time_ms"] = (time.perf_counter() - start) * 1000
        return result
    
    def _process_with_arrow(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process data with PyArrow."""
        import pyarrow as pa
        
        if not data:
            return {"rows": 0, "columns": 0, "processing_time_ms": 0}
        
        start = time.perf_counter()
        table = pa.Table.from_pylist(data)
        
        result = {
            "rows": table.num_rows,
            "columns": table.num_columns,
            "memory_usage_mb": table.nbytes / (1024 * 1024),
            "schema": str(table.schema),
            "library": "pyarrow"
        }
        
        result["processing_time_ms"] = (time.perf_counter() - start) * 1000
        return result
    
    def _process_with_standard(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process data with standard Python."""
        if not data:
            return {"rows": 0, "columns": 0, "processing_time_ms": 0}
        
        start = time.perf_counter()
        
        result = {
            "rows": len(data),
            "columns": len(data[0].keys()) if data else 0,
            "memory_usage_mb": len(str(data)) / (1024 * 1024),
            "keys": list(data[0].keys()) if data else [],
            "library": "standard"
        }
        
        result["processing_time_ms"] = (time.perf_counter() - start) * 1000
        return result
    
    async def process_data_async(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Async data processing using best available library."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, self._process_dataframe, data)
    
    def benchmark_operation(self, operation: Callable, data: Any, iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark any operation."""
        start = time.perf_counter()
        
        for _ in range(iterations):
            operation(data)
        
        total_time = time.perf_counter() - start
        
        return {
            "iterations": iterations,
            "total_time_s": total_time,
            "avg_time_ms": (total_time / iterations) * 1000,
            "ops_per_second": iterations / total_time
        }
    
    def get_optimization_info(self) -> Dict[str, Any]:
        """Get information about current optimizations."""
        return {
            "performance_score": detector.get_performance_score(),
            "available_libraries": detector.available_libraries,
            "best_choices": {
                "json": detector.get_best_library("json").name if detector.get_best_library("json") else "json",
                "hash": detector.get_best_library("hash").name if detector.get_best_library("hash") else "hashlib",
                "compression": detector.get_best_library("compression").name if detector.get_best_library("compression") else "gzip",
                "data": detector.get_best_library("data").name if detector.get_best_library("data") else "standard"
            },
            "recommendations": detector.get_recommendations()
        }
    
    def cleanup(self):
        """Cleanup resources."""
        self.thread_pool.shutdown(wait=True)
        gc.collect()

# Global optimizer instance
optimizer = UltraOptimizer() 