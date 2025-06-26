"""
High-Performance Data Processing Module for Onyx Features.

Ultra-optimized data processing with vectorization, parallel computing,
and advanced analytics using cutting-edge libraries.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

# High-performance data processing libraries
import polars as pl  # Ultra-fast DataFrame processing (Rust-based)
import numpy as np  # Numerical computing
import pandas as pd  # Traditional DataFrame processing
import pyarrow as pa  # Columnar data processing
import dask.dataframe as dd  # Parallel computing
from numba import jit, njit, prange  # JIT compilation
import cupy as cp  # GPU acceleration (if available)
import modin.pandas as mpd  # Distributed pandas
from scipy import stats  # Statistical functions
from sklearn.preprocessing import StandardScaler, MinMaxScaler  # ML preprocessing

# Compression and serialization
import lz4.frame  # Fast compression
import zstandard as zstd  # Modern compression
import msgpack  # Binary serialization
import pickle5  # Enhanced pickle

# System and monitoring
import psutil  # System monitoring
import structlog  # Structured logging

# Import our optimization modules
from .optimization import (
    FastSerializer, VectorizedProcessor, MemoryOptimizer, 
    ProfilerOptimizer, PerformanceMetrics
)
from .protocols import ProcessorProtocol

logger = structlog.get_logger(__name__)

T = TypeVar('T')


@dataclass
class ProcessingConfig:
    """Configuration for data processing operations."""
    enable_gpu: bool = False
    use_polars: bool = True
    use_dask: bool = False
    use_modin: bool = False
    chunk_size: int = 10000
    max_workers: int = psutil.cpu_count()
    compression_algorithm: str = "lz4"  # lz4, zstd, gzip
    enable_jit: bool = True
    memory_limit_gb: float = 8.0
    
    def __post_init__(self):
        # Auto-detect optimal settings
        memory = psutil.virtual_memory()
        if memory.total / (1024**3) > 16:  # More than 16GB RAM
            self.chunk_size = 50000
            self.memory_limit_gb = min(16.0, memory.total / (1024**3) * 0.7)


class HighPerformanceDataProcessor:
    """Ultra-optimized data processor with multiple backend support."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        self.memory_optimizer = MemoryOptimizer()
        self.profiler = ProfilerOptimizer()
        self._gpu_available = self._check_gpu_availability()
        
        # Initialize thread pools
        self.thread_executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=min(4, self.config.max_workers))
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        if not self.config.enable_gpu:
            return False
        
        try:
            import cupy as cp
            cp.cuda.Device(0).compute_capability
            logger.info("GPU acceleration available")
            return True
        except Exception:
            logger.info("GPU acceleration not available")
            return False
    
    @njit(parallel=True, cache=True)
    def _fast_numerical_operations(self, data: np.ndarray, operation: str) -> np.ndarray:
        """JIT-compiled numerical operations for maximum speed."""
        if operation == "normalize":
            mean_val = np.mean(data)
            std_val = np.std(data)
            return (data - mean_val) / std_val
        elif operation == "square":
            return data ** 2
        elif operation == "log":
            return np.log(data + 1e-8)  # Avoid log(0)
        elif operation == "abs":
            return np.abs(data)
        else:
            return data
    
    def process_dataframe_polars(self, data: Union[Dict, List, pl.DataFrame], operations: List[str]) -> pl.DataFrame:
        """Ultra-fast DataFrame processing using Polars (Rust-based)."""
        try:
            # Convert to Polars DataFrame
            if isinstance(data, pl.DataFrame):
                df = data
            elif isinstance(data, dict):
                df = pl.DataFrame(data)
            elif isinstance(data, list):
                df = pl.DataFrame({"data": data})
            else:
                df = pl.DataFrame({"data": [data]})
            
            # Apply operations in optimized order
            for op in operations:
                if op == "filter_nulls":
                    df = df.drop_nulls()
                elif op == "normalize":
                    # Vectorized normalization
                    numeric_cols = [col for col in df.columns if df[col].dtype in [pl.Float64, pl.Float32, pl.Int64, pl.Int32]]
                    for col in numeric_cols:
                        mean_val = df[col].mean()
                        std_val = df[col].std()
                        df = df.with_columns(((pl.col(col) - mean_val) / std_val).alias(col))
                elif op == "sort":
                    if len(df.columns) > 0:
                        df = df.sort(df.columns[0])
                elif op == "group_stats":
                    if len(df.columns) > 1:
                        df = df.group_by(df.columns[0]).agg([
                            pl.col(df.columns[1]).count().alias("count"),
                            pl.col(df.columns[1]).mean().alias("mean"),
                            pl.col(df.columns[1]).std().alias("std")
                        ])
            
            return df
            
        except Exception as e:
            logger.error("Polars processing failed", error=str(e))
            # Fallback to pandas
            return self._fallback_to_pandas(data, operations)
    
    def _fallback_to_pandas(self, data: Any, operations: List[str]) -> pd.DataFrame:
        """Fallback to pandas processing."""
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, list):
            df = pd.DataFrame({"data": data})
        else:
            df = pd.DataFrame({"data": [data]})
        
        # Apply basic operations
        for op in operations:
            if op == "filter_nulls":
                df = df.dropna()
            elif op == "normalize":
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()
            elif op == "sort":
                if len(df.columns) > 0:
                    df = df.sort_values(by=df.columns[0])
        
        return df
    
    async def process_large_dataset_async(
        self, 
        data_source: Union[str, Path, List[Dict]], 
        operations: List[str],
        chunk_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Process large datasets asynchronously with chunking."""
        chunk_size = chunk_size or self.config.chunk_size
        
        self.profiler.start_profiling()
        
        try:
            if isinstance(data_source, (str, Path)):
                # Process file in chunks
                if str(data_source).endswith('.parquet'):
                    df = pl.read_parquet(data_source)
                elif str(data_source).endswith('.csv'):
                    df = pl.read_csv(data_source)
                else:
                    raise ValueError(f"Unsupported file format: {data_source}")
                
                # Process in chunks for memory efficiency
                total_rows = df.height
                results = []
                
                for i in range(0, total_rows, chunk_size):
                    chunk = df.slice(i, min(chunk_size, total_rows - i))
                    processed_chunk = self.process_dataframe_polars(chunk, operations)
                    results.append(processed_chunk)
                
                # Combine results
                final_result = pl.concat(results)
                
            else:
                # Process in-memory data
                df = pl.DataFrame(data_source)
                final_result = self.process_dataframe_polars(df, operations)
            
            metrics = self.profiler.stop_profiling("large_dataset_processing")
            
            return {
                "result": final_result,
                "metrics": metrics.to_dict(),
                "rows_processed": final_result.height,
                "memory_usage": self.memory_optimizer.get_memory_usage()
            }
            
        except Exception as e:
            logger.error("Large dataset processing failed", error=str(e))
            raise
    
    def compress_data(self, data: Any, algorithm: str = None) -> bytes:
        """Compress data using high-performance algorithms."""
        algorithm = algorithm or self.config.compression_algorithm
        
        # Serialize data first
        serialized = FastSerializer.serialize_msgpack(data)
        
        if algorithm == "lz4":
            return lz4.frame.compress(serialized)
        elif algorithm == "zstd":
            compressor = zstd.ZstdCompressor(level=3)  # Fast compression
            return compressor.compress(serialized)
        elif algorithm == "gzip":
            import gzip
            return gzip.compress(serialized)
        else:
            return serialized
    
    def decompress_data(self, compressed_data: bytes, algorithm: str = None) -> Any:
        """Decompress data using high-performance algorithms."""
        algorithm = algorithm or self.config.compression_algorithm
        
        try:
            if algorithm == "lz4":
                decompressed = lz4.frame.decompress(compressed_data)
            elif algorithm == "zstd":
                decompressor = zstd.ZstdDecompressor()
                decompressed = decompressor.decompress(compressed_data)
            elif algorithm == "gzip":
                import gzip
                decompressed = gzip.decompress(compressed_data)
            else:
                decompressed = compressed_data
            
            return FastSerializer.deserialize_msgpack(decompressed)
            
        except Exception as e:
            logger.error("Decompression failed", error=str(e))
            raise
    
    def vectorized_operations(self, data: np.ndarray, operations: List[str]) -> np.ndarray:
        """Apply vectorized operations using JIT compilation."""
        if not self.config.enable_jit:
            return data
        
        result = data.copy()
        
        for op in operations:
            if self._gpu_available and data.size > 100000:
                # Use GPU acceleration for large arrays
                try:
                    gpu_data = cp.asarray(result)
                    if op == "normalize":
                        gpu_result = (gpu_data - cp.mean(gpu_data)) / cp.std(gpu_data)
                    elif op == "square":
                        gpu_result = gpu_data ** 2
                    elif op == "log":
                        gpu_result = cp.log(gpu_data + 1e-8)
                    else:
                        gpu_result = gpu_data
                    
                    result = cp.asnumpy(gpu_result)
                except Exception as e:
                    logger.warning("GPU operation failed, falling back to CPU", error=str(e))
                    result = self._fast_numerical_operations(result, op)
            else:
                # Use JIT-compiled CPU operations
                result = self._fast_numerical_operations(result, op)
        
        return result
    
    async def parallel_batch_processing(
        self, 
        data_batches: List[Any], 
        processor_func: Callable,
        use_processes: bool = False
    ) -> List[Any]:
        """Process batches in parallel using optimal executor."""
        executor = self.process_executor if use_processes else self.thread_executor
        
        loop = asyncio.get_event_loop()
        
        # Submit all tasks
        tasks = [
            loop.run_in_executor(executor, processor_func, batch)
            for batch in data_batches
        ]
        
        # Wait for completion with progress tracking
        results = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results.append(result)
            
            # Log progress for large batches
            if len(data_batches) > 10 and (i + 1) % (len(data_batches) // 10) == 0:
                progress = ((i + 1) / len(data_batches)) * 100
                logger.info(f"Batch processing progress: {progress:.1f}%")
        
        return results
    
    def statistical_analysis(self, data: Union[np.ndarray, pl.DataFrame, pd.DataFrame]) -> Dict[str, Any]:
        """Perform statistical analysis using optimized libraries."""
        try:
            if isinstance(data, pl.DataFrame):
                # Use Polars for ultra-fast statistics
                numeric_cols = [col for col in data.columns if data[col].dtype in [pl.Float64, pl.Float32, pl.Int64, pl.Int32]]
                
                stats_dict = {}
                for col in numeric_cols:
                    col_data = data[col].to_numpy()
                    stats_dict[col] = {
                        "mean": float(np.mean(col_data)),
                        "std": float(np.std(col_data)),
                        "min": float(np.min(col_data)),
                        "max": float(np.max(col_data)),
                        "median": float(np.median(col_data)),
                        "skewness": float(stats.skew(col_data)),
                        "kurtosis": float(stats.kurtosis(col_data))
                    }
                
                return stats_dict
                
            elif isinstance(data, np.ndarray):
                return {
                    "mean": float(np.mean(data)),
                    "std": float(np.std(data)),
                    "min": float(np.min(data)),
                    "max": float(np.max(data)),
                    "median": float(np.median(data)),
                    "skewness": float(stats.skew(data)),
                    "kurtosis": float(stats.kurtosis(data))
                }
            
            else:
                # Convert to numpy for analysis
                if hasattr(data, 'values'):
                    data_array = data.values
                else:
                    data_array = np.array(data)
                
                return self.statistical_analysis(data_array)
                
        except Exception as e:
            logger.error("Statistical analysis failed", error=str(e))
            return {"error": str(e)}
    
    def cleanup(self):
        """Cleanup resources."""
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)


# Factory function
def create_data_processor(config: Optional[ProcessingConfig] = None) -> HighPerformanceDataProcessor:
    """Create optimized data processor instance."""
    return HighPerformanceDataProcessor(config)


# Utility functions for common operations
async def process_json_data_fast(json_data: List[Dict], operations: List[str]) -> Dict[str, Any]:
    """Fast JSON data processing."""
    processor = create_data_processor()
    try:
        df = pl.DataFrame(json_data)
        result = processor.process_dataframe_polars(df, operations)
        return {
            "success": True,
            "data": result.to_dicts(),
            "rows": result.height,
            "columns": result.width
        }
    except Exception as e:
        logger.error("JSON processing failed", error=str(e))
        return {"success": False, "error": str(e)}
    finally:
        processor.cleanup()


def optimize_numeric_array(data: List[Union[int, float]], operations: List[str]) -> np.ndarray:
    """Optimize numeric array processing."""
    processor = create_data_processor()
    try:
        array = np.array(data, dtype=np.float64)
        return processor.vectorized_operations(array, operations)
    finally:
        processor.cleanup()


# Export main components
__all__ = [
    "HighPerformanceDataProcessor",
    "ProcessingConfig",
    "create_data_processor",
    "process_json_data_fast",
    "optimize_numeric_array"
] 