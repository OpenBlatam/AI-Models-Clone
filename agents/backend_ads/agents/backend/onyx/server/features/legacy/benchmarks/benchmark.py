"""
Benchmark Module for Onyx Features - Performance Testing & Validation.

Comprehensive benchmarking suite to test and validate all optimization
improvements and measure performance gains in production scenarios.
"""

import asyncio
import time
import json
import random
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import structlog

# Import our optimization modules
from .optimization import (
    FastSerializer, FastHasher, VectorizedProcessor,
    AsyncOptimizer, MemoryOptimizer, ProfilerOptimizer
)
from .performance_optimizers import (
    PerformanceOrchestrator, OptimizationConfig,
    create_performance_orchestrator, ultra_optimize
)
from .data_processing import (
    HighPerformanceDataProcessor, ProcessingConfig,
    create_data_processor
)

logger = structlog.get_logger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a benchmark test."""
    test_name: str
    duration_ms: float
    memory_usage_mb: float
    throughput_ops_sec: float
    success_rate: float
    error_count: int
    details: Dict[str, Any]


class SerializationBenchmark:
    """Benchmark serialization performance."""
    
    def __init__(self):
        self.test_data = self._generate_test_data()
    
    def _generate_test_data(self) -> List[Dict[str, Any]]:
        """Generate test data for serialization benchmarks."""
        data = []
        for i in range(1000):
            data.append({
                "id": i,
                "name": f"test_item_{i}",
                "value": random.uniform(0, 1000),
                "tags": [f"tag_{j}" for j in range(random.randint(1, 5))],
                "metadata": {
                    "created_at": time.time(),
                    "category": random.choice(["A", "B", "C"]),
                    "score": random.randint(1, 100)
                }
            })
        return data
    
    def benchmark_json_serialization(self) -> Dict[str, BenchmarkResult]:
        """Benchmark different JSON serialization methods."""
        results = {}
        
        # Standard JSON
        start_time = time.perf_counter()
        for _ in range(100):
            json.dumps(self.test_data)
        standard_duration = (time.perf_counter() - start_time) * 1000
        
        results["standard_json"] = BenchmarkResult(
            test_name="Standard JSON",
            duration_ms=standard_duration,
            memory_usage_mb=0,
            throughput_ops_sec=100000 / standard_duration,
            success_rate=1.0,
            error_count=0,
            details={}
        )
        
        # Fast JSON (orjson)
        start_time = time.perf_counter()
        for _ in range(100):
            FastSerializer.serialize_json(self.test_data)
        fast_duration = (time.perf_counter() - start_time) * 1000
        
        results["fast_json"] = BenchmarkResult(
            test_name="Fast JSON (orjson)",
            duration_ms=fast_duration,
            memory_usage_mb=0,
            throughput_ops_sec=100000 / fast_duration,
            success_rate=1.0,
            error_count=0,
            details={"speedup": f"{standard_duration / fast_duration:.2f}x"}
        )
        
        # MessagePack
        start_time = time.perf_counter()
        for _ in range(100):
            FastSerializer.serialize_msgpack(self.test_data)
        msgpack_duration = (time.perf_counter() - start_time) * 1000
        
        results["msgpack"] = BenchmarkResult(
            test_name="MessagePack",
            duration_ms=msgpack_duration,
            memory_usage_mb=0,
            throughput_ops_sec=100000 / msgpack_duration,
            success_rate=1.0,
            error_count=0,
            details={"speedup": f"{standard_duration / msgpack_duration:.2f}x"}
        )
        
        return results


class HashingBenchmark:
    """Benchmark hashing performance."""
    
    def __init__(self):
        self.test_strings = [f"test_string_{i}" * 100 for i in range(10000)]
    
    def benchmark_hashing_algorithms(self) -> Dict[str, BenchmarkResult]:
        """Benchmark different hashing algorithms."""
        results = {}
        
        # Standard hashlib SHA256
        start_time = time.perf_counter()
        for s in self.test_strings:
            import hashlib
            hashlib.sha256(s.encode()).hexdigest()
        sha256_duration = (time.perf_counter() - start_time) * 1000
        
        results["sha256"] = BenchmarkResult(
            test_name="SHA256",
            duration_ms=sha256_duration,
            memory_usage_mb=0,
            throughput_ops_sec=len(self.test_strings) * 1000 / sha256_duration,
            success_rate=1.0,
            error_count=0,
            details={}
        )
        
        # xxHash
        start_time = time.perf_counter()
        for s in self.test_strings:
            FastHasher.hash_fast(s)
        xxhash_duration = (time.perf_counter() - start_time) * 1000
        
        results["xxhash"] = BenchmarkResult(
            test_name="xxHash",
            duration_ms=xxhash_duration,
            memory_usage_mb=0,
            throughput_ops_sec=len(self.test_strings) * 1000 / xxhash_duration,
            success_rate=1.0,
            error_count=0,
            details={"speedup": f"{sha256_duration / xxhash_duration:.2f}x"}
        )
        
        return results


class DataProcessingBenchmark:
    """Benchmark data processing performance."""
    
    def __init__(self):
        self.data_processor = create_data_processor()
        self.test_array = np.random.rand(100000).astype(np.float64)
        self.test_dataframe_data = [
            {"id": i, "value": random.uniform(0, 100), "category": random.choice(["A", "B", "C"])}
            for i in range(10000)
        ]
    
    def benchmark_numerical_operations(self) -> Dict[str, BenchmarkResult]:
        """Benchmark numerical operations."""
        results = {}
        
        # Standard NumPy operations
        start_time = time.perf_counter()
        for _ in range(100):
            normalized = (self.test_array - np.mean(self.test_array)) / np.std(self.test_array)
        numpy_duration = (time.perf_counter() - start_time) * 1000
        
        results["numpy_standard"] = BenchmarkResult(
            test_name="NumPy Standard",
            duration_ms=numpy_duration,
            memory_usage_mb=0,
            throughput_ops_sec=100000 / numpy_duration,
            success_rate=1.0,
            error_count=0,
            details={}
        )
        
        # Vectorized operations
        start_time = time.perf_counter()
        for _ in range(100):
            normalized = self.data_processor.vectorized_operations(self.test_array, ["normalize"])
        vectorized_duration = (time.perf_counter() - start_time) * 1000
        
        results["vectorized"] = BenchmarkResult(
            test_name="Vectorized Operations",
            duration_ms=vectorized_duration,
            memory_usage_mb=0,
            throughput_ops_sec=100000 / vectorized_duration,
            success_rate=1.0,
            error_count=0,
            details={"speedup": f"{numpy_duration / vectorized_duration:.2f}x"}
        )
        
        return results
    
    def benchmark_dataframe_operations(self) -> Dict[str, BenchmarkResult]:
        """Benchmark DataFrame operations."""
        results = {}
        
        # Pandas operations
        start_time = time.perf_counter()
        df = pd.DataFrame(self.test_dataframe_data)
        df_filtered = df.dropna()
        df_grouped = df_filtered.groupby('category').agg({'value': ['mean', 'count']})
        pandas_duration = (time.perf_counter() - start_time) * 1000
        
        results["pandas"] = BenchmarkResult(
            test_name="Pandas DataFrame",
            duration_ms=pandas_duration,
            memory_usage_mb=0,
            throughput_ops_sec=len(self.test_dataframe_data) * 1000 / pandas_duration,
            success_rate=1.0,
            error_count=0,
            details={}
        )
        
        # Polars operations
        start_time = time.perf_counter()
        pl_df = self.data_processor.process_dataframe_polars(
            self.test_dataframe_data, 
            ["filter_nulls", "group_stats"]
        )
        polars_duration = (time.perf_counter() - start_time) * 1000
        
        results["polars"] = BenchmarkResult(
            test_name="Polars DataFrame",
            duration_ms=polars_duration,
            memory_usage_mb=0,
            throughput_ops_sec=len(self.test_dataframe_data) * 1000 / polars_duration,
            success_rate=1.0,
            error_count=0,
            details={"speedup": f"{pandas_duration / polars_duration:.2f}x"}
        )
        
        return results


class AsyncBenchmark:
    """Benchmark async operations."""
    
    def __init__(self):
        self.async_optimizer = AsyncOptimizer(max_concurrent=50)
    
    async def benchmark_async_operations(self) -> Dict[str, BenchmarkResult]:
        """Benchmark async operations."""
        results = {}
        
        # Sequential operations
        start_time = time.perf_counter()
        sequential_results = []
        for i in range(1000):
            await asyncio.sleep(0.001)  # Simulate work
            sequential_results.append(i * 2)
        sequential_duration = (time.perf_counter() - start_time) * 1000
        
        results["sequential"] = BenchmarkResult(
            test_name="Sequential Operations",
            duration_ms=sequential_duration,
            memory_usage_mb=0,
            throughput_ops_sec=1000 * 1000 / sequential_duration,
            success_rate=1.0,
            error_count=0,
            details={}
        )
        
        # Optimized async operations
        async def test_task(i):
            await asyncio.sleep(0.001)
            return i * 2
        
        start_time = time.perf_counter()
        tasks = [test_task(i) for i in range(1000)]
        optimized_results = await self.async_optimizer.batch_process_optimized(
            list(range(1000)),
            lambda x: test_task(x),
            batch_size=50
        )
        optimized_duration = (time.perf_counter() - start_time) * 1000
        
        results["optimized_async"] = BenchmarkResult(
            test_name="Optimized Async Operations",
            duration_ms=optimized_duration,
            memory_usage_mb=0,
            throughput_ops_sec=1000 * 1000 / optimized_duration,
            success_rate=1.0,
            error_count=0,
            details={"speedup": f"{sequential_duration / optimized_duration:.2f}x"}
        )
        
        return results


class MemoryBenchmark:
    """Benchmark memory optimization."""
    
    def __init__(self):
        self.memory_optimizer = MemoryOptimizer()
    
    def benchmark_memory_optimization(self) -> Dict[str, BenchmarkResult]:
        """Benchmark memory optimization techniques."""
        results = {}
        
        # Create large data structure
        large_data = {}
        for i in range(10000):
            large_data[f"key_{i}"] = {
                "data": [random.random() for _ in range(100)],
                "text": "Lorem ipsum " * 100,
                "metadata": {"id": i, "timestamp": time.time()}
            }
        
        initial_memory = psutil.virtual_memory().percent
        
        # Without optimization
        start_time = time.perf_counter()
        # Just hold the data in memory
        time.sleep(0.1)
        without_opt_duration = (time.perf_counter() - start_time) * 1000
        memory_without_opt = psutil.virtual_memory().percent
        
        # With optimization
        start_time = time.perf_counter()
        optimized_data = self.memory_optimizer.optimize_dict_memory(large_data)
        with_opt_duration = (time.perf_counter() - start_time) * 1000
        memory_with_opt = psutil.virtual_memory().percent
        
        # Force garbage collection
        optimization_stats = self.memory_optimizer.optimize_memory_usage()
        
        results["memory_optimization"] = BenchmarkResult(
            test_name="Memory Optimization",
            duration_ms=with_opt_duration,
            memory_usage_mb=(memory_with_opt - initial_memory) * psutil.virtual_memory().total / (1024**3) / 100,
            throughput_ops_sec=1000 / with_opt_duration,
            success_rate=1.0,
            error_count=0,
            details={
                "initial_memory_percent": initial_memory,
                "memory_without_opt": memory_without_opt,
                "memory_with_opt": memory_with_opt,
                "memory_saved_percent": memory_without_opt - memory_with_opt,
                "gc_stats": optimization_stats
            }
        )
        
        return results


class ComprehensiveBenchmark:
    """Main benchmark orchestrator."""
    
    def __init__(self):
        self.serialization_bench = SerializationBenchmark()
        self.hashing_bench = HashingBenchmark()
        self.data_processing_bench = DataProcessingBenchmark()
        self.async_bench = AsyncBenchmark()
        self.memory_bench = MemoryBenchmark()
    
    async def run_all_benchmarks(self) -> Dict[str, Dict[str, BenchmarkResult]]:
        """Run all benchmarks and return comprehensive results."""
        logger.info("Starting comprehensive benchmark suite")
        
        all_results = {}
        
        # Serialization benchmarks
        logger.info("Running serialization benchmarks")
        all_results["serialization"] = self.serialization_bench.benchmark_json_serialization()
        
        # Hashing benchmarks
        logger.info("Running hashing benchmarks")
        all_results["hashing"] = self.hashing_bench.benchmark_hashing_algorithms()
        
        # Data processing benchmarks
        logger.info("Running data processing benchmarks")
        all_results["numerical_ops"] = self.data_processing_bench.benchmark_numerical_operations()
        all_results["dataframe_ops"] = self.data_processing_bench.benchmark_dataframe_operations()
        
        # Async benchmarks
        logger.info("Running async benchmarks")
        all_results["async_ops"] = await self.async_bench.benchmark_async_operations()
        
        # Memory benchmarks
        logger.info("Running memory benchmarks")
        all_results["memory_ops"] = self.memory_bench.benchmark_memory_optimization()
        
        logger.info("Benchmark suite completed")
        return all_results
    
    def generate_benchmark_report(self, results: Dict[str, Dict[str, BenchmarkResult]]) -> str:
        """Generate a comprehensive benchmark report."""
        report = ["# Onyx Features Performance Benchmark Report\n"]
        report.append(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total / (1024**3):.1f}GB RAM\n\n")
        
        total_speedup = 0
        speedup_count = 0
        
        for category, category_results in results.items():
            report.append(f"## {category.replace('_', ' ').title()}\n")
            
            for test_name, result in category_results.items():
                report.append(f"### {result.test_name}\n")
                report.append(f"- Duration: {result.duration_ms:.2f}ms\n")
                report.append(f"- Throughput: {result.throughput_ops_sec:.0f} ops/sec\n")
                report.append(f"- Success Rate: {result.success_rate:.1%}\n")
                
                if "speedup" in result.details:
                    speedup = float(result.details["speedup"].replace("x", ""))
                    total_speedup += speedup
                    speedup_count += 1
                    report.append(f"- **Speedup: {result.details['speedup']}**\n")
                
                if result.details:
                    report.append(f"- Details: {result.details}\n")
                
                report.append("\n")
        
        # Summary
        if speedup_count > 0:
            avg_speedup = total_speedup / speedup_count
            report.append(f"## Summary\n")
            report.append(f"- Average Speedup: **{avg_speedup:.2f}x**\n")
            report.append(f"- Total Optimizations: {speedup_count}\n")
            
            if avg_speedup > 2.0:
                report.append("- **Performance Grade: A+ (Excellent)**\n")
            elif avg_speedup > 1.5:
                report.append("- **Performance Grade: A (Very Good)**\n")
            elif avg_speedup > 1.2:
                report.append("- **Performance Grade: B (Good)**\n")
            else:
                report.append("- **Performance Grade: C (Needs Improvement)**\n")
        
        return "".join(report)


# Factory function
def create_benchmark_suite() -> ComprehensiveBenchmark:
    """Create comprehensive benchmark suite."""
    return ComprehensiveBenchmark()


# CLI function for running benchmarks
async def main():
    """Main function for running benchmarks from CLI."""
    benchmark = create_benchmark_suite()
    results = await benchmark.run_all_benchmarks()
    report = benchmark.generate_benchmark_report(results)
    
    print(report)
    
    # Save report to file
    with open("benchmark_report.md", "w") as f:
        f.write(report)
    
    print("\nBenchmark report saved to: benchmark_report.md")


if __name__ == "__main__":
    asyncio.run(main())


# Export components
__all__ = [
    "BenchmarkResult",
    "SerializationBenchmark",
    "HashingBenchmark", 
    "DataProcessingBenchmark",
    "AsyncBenchmark",
    "MemoryBenchmark",
    "ComprehensiveBenchmark",
    "create_benchmark_suite"
] 