"""
Hashing Optimizer - Ultra-Fast Data Hashing.

Consolidates all hashing functionality with automatic algorithm selection
and specialized optimizations for different data types.
"""

import time
from typing import Union, Optional, Dict, List
import structlog
import numpy as np

# Core hashing imports
import xxhash

# Optional ultra-fast imports
try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

try:
    import numba
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

from .config import OptimizationConfig

logger = structlog.get_logger(__name__)


class HashingOptimizer:
    """High-level hashing optimizer with automatic algorithm selection."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.algorithm = config.hash_algorithm
        self.hashers = {
            "blake3": Blake3Hasher() if BLAKE3_AVAILABLE else None,
            "xxhash": XxHasher(),
            "sha256": Sha256Hasher()
        }
        
        # Remove None hashers
        self.hashers = {k: v for k, v in self.hashers.items() if v is not None}
        
        # Metrics tracking
        self.operations_count = 0
        self.total_hash_time = 0.0
        self.errors = 0
        
        logger.info("Hashing optimizer initialized",
                   algorithm=self.algorithm,
                   available_algorithms=list(self.hashers.keys()))
    
    def hash_data(self, data: Union[str, bytes], seed: int = 0) -> str:
        """Hash data using configured algorithm with fallbacks."""
        start_time = time.perf_counter()
        
        try:
            # Convert string to bytes if needed
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Try primary algorithm
            if self.algorithm in self.hashers:
                result = self.hashers[self.algorithm].hash_bytes(data, seed)
                self._record_success(start_time)
                return result
            
            # Fallback to xxhash
            if "xxhash" in self.hashers:
                result = self.hashers["xxhash"].hash_bytes(data, seed)
                self._record_success(start_time)
                return result
            
            # Ultimate fallback to sha256
            result = self.hashers["sha256"].hash_bytes(data, seed)
            self._record_success(start_time)
            return result
            
        except Exception as e:
            self._record_error(start_time, e)
            # Emergency fallback
            import hashlib
            return hashlib.sha256(data).hexdigest()
    
    def hash_int(self, data: Union[str, bytes], seed: int = 0) -> int:
        """Hash data and return integer result."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Use xxhash for integer results (most efficient)
        return xxhash.xxh64(data, seed=seed).intdigest()
    
    def hash_large_data(self, data: bytes, chunk_size: int = 1024*1024) -> str:
        """Hash large data in chunks for memory efficiency."""
        if self.algorithm == "blake3" and BLAKE3_AVAILABLE:
            hasher = blake3.blake3()
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                hasher.update(chunk)
            return hasher.hexdigest()
        else:
            # For other algorithms, process in one go (they handle chunking internally)
            return self.hash_data(data)
    
    def hash_array(self, arr: np.ndarray) -> np.ndarray:
        """Fast vectorized array hashing."""
        if NUMBA_AVAILABLE:
            return self._hash_array_numba(arr)
        else:
            return self._hash_array_numpy(arr)
    
    @staticmethod
    @njit(parallel=True, cache=True) if NUMBA_AVAILABLE else lambda x: x
    def _hash_array_numba(arr: np.ndarray) -> np.ndarray:
        """Numba-optimized parallel array hashing."""
        result = np.empty(len(arr), dtype=np.uint64)
        for i in prange(len(arr)):
            x = np.uint64(arr[i])
            # Fast hash function optimized for speed
            x = ((x >> 16) ^ x) * np.uint64(0x45d9f3b)
            x = ((x >> 16) ^ x) * np.uint64(0x45d9f3b) 
            x = (x >> 16) ^ x
            result[i] = x
        return result
    
    @staticmethod
    def _hash_array_numpy(arr: np.ndarray) -> np.ndarray:
        """Numpy fallback for array hashing."""
        return np.array([hash(x) for x in arr], dtype=np.uint64)
    
    def hash_multiple(self, data_list: List[Union[str, bytes]], seed: int = 0) -> List[str]:
        """Hash multiple data items efficiently."""
        results = []
        for data in data_list:
            results.append(self.hash_data(data, seed))
        return results
    
    def benchmark_algorithms(self, test_data: bytes) -> Dict[str, float]:
        """Benchmark all available hashing algorithms."""
        results = {}
        
        for algo_name, hasher in self.hashers.items():
            try:
                # Warm up
                hasher.hash_bytes(test_data, 0)
                
                # Benchmark
                iterations = 1000
                start_time = time.perf_counter()
                
                for _ in range(iterations):
                    hasher.hash_bytes(test_data, 0)
                
                duration = time.perf_counter() - start_time
                results[algo_name] = duration / iterations * 1000  # ms per operation
                
            except Exception as e:
                logger.warning(f"Algorithm {algo_name} failed benchmark", error=str(e))
                results[algo_name] = float('inf')
        
        return results
    
    def auto_select_algorithm(self, test_data: bytes) -> str:
        """Auto-select the fastest algorithm for given data."""
        benchmark_results = self.benchmark_algorithms(test_data)
        
        if benchmark_results:
            fastest = min(benchmark_results.items(), key=lambda x: x[1])
            logger.info("Auto-selected hashing algorithm",
                       algorithm=fastest[0],
                       benchmark_results=benchmark_results)
            return fastest[0]
        
        return "xxhash"  # Safe fallback
    
    def _record_success(self, start_time: float):
        """Record successful operation metrics."""
        duration = time.perf_counter() - start_time
        self.operations_count += 1
        self.total_hash_time += duration
    
    def _record_error(self, start_time: float, error: Exception):
        """Record error metrics."""
        duration = time.perf_counter() - start_time
        self.errors += 1
        logger.warning("Hashing error",
                      error=str(error),
                      duration_ms=duration * 1000)
    
    def get_metrics(self) -> Dict[str, any]:
        """Get hashing performance metrics."""
        if self.operations_count == 0:
            return {"operations": 0, "avg_hash_time_ms": 0}
        
        return {
            "operations_count": self.operations_count,
            "avg_hash_time_ms": (self.total_hash_time / self.operations_count) * 1000,
            "error_rate": self.errors / self.operations_count,
            "current_algorithm": self.algorithm
        }


class Blake3Hasher:
    """Ultra-fast BLAKE3 hasher."""
    
    def hash_bytes(self, data: bytes, seed: int = 0) -> str:
        """Hash bytes using BLAKE3."""
        if not BLAKE3_AVAILABLE:
            raise ImportError("blake3 not available")
        
        if seed == 0:
            return blake3.blake3(data).hexdigest()
        else:
            # BLAKE3 doesn't use seeds in the same way, so we modify data
            return blake3.blake3(data + str(seed).encode()).hexdigest()


class XxHasher:
    """Ultra-fast xxHash hasher."""
    
    def hash_bytes(self, data: bytes, seed: int = 0) -> str:
        """Hash bytes using xxHash64."""
        return xxhash.xxh64(data, seed=seed).hexdigest()
    
    def hash_int(self, data: bytes, seed: int = 0) -> int:
        """Hash bytes and return integer."""
        return xxhash.xxh64(data, seed=seed).intdigest()
    
    def hash_32(self, data: bytes, seed: int = 0) -> str:
        """Hash using xxHash32 for smaller hashes."""
        return xxhash.xxh32(data, seed=seed).hexdigest()


class Sha256Hasher:
    """Standard SHA256 hasher (fallback)."""
    
    def hash_bytes(self, data: bytes, seed: int = 0) -> str:
        """Hash bytes using SHA256."""
        import hashlib
        
        if seed == 0:
            return hashlib.sha256(data).hexdigest()
        else:
            # Include seed in data
            return hashlib.sha256(data + str(seed).encode()).hexdigest()


# Convenient aliases and functions
UltraFastHasher = HashingOptimizer


def hash_fast(data: Union[str, bytes], algorithm: str = "auto", seed: int = 0) -> str:
    """Quick hash function with automatic algorithm selection."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if algorithm == "auto":
        if BLAKE3_AVAILABLE:
            algorithm = "blake3"
        else:
            algorithm = "xxhash"
    
    if algorithm == "blake3" and BLAKE3_AVAILABLE:
        return Blake3Hasher().hash_bytes(data, seed)
    elif algorithm == "xxhash":
        return XxHasher().hash_bytes(data, seed)
    else:
        return Sha256Hasher().hash_bytes(data, seed)


def hash_array_fast(arr: np.ndarray) -> np.ndarray:
    """Quick array hashing function."""
    if NUMBA_AVAILABLE:
        return HashingOptimizer._hash_array_numba(arr)
    else:
        return HashingOptimizer._hash_array_numpy(arr)


def create_hasher(config: Optional[OptimizationConfig] = None) -> HashingOptimizer:
    """Factory function to create optimized hasher."""
    if config is None:
        from .config import OptimizationConfig
        config = OptimizationConfig()
    
    return HashingOptimizer(config)


__all__ = [
    "HashingOptimizer",
    "UltraFastHasher",
    "Blake3Hasher",
    "XxHasher", 
    "Sha256Hasher",
    "hash_fast",
    "hash_array_fast",
    "create_hasher"
] 