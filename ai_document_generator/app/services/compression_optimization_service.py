"""
Compression optimization service following functional patterns
"""
from typing import Dict, Any, List, Optional, Union, BinaryIO
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
import uuid
import asyncio
import gzip
import brotli
import lz4
import zstandard as zstd
import bz2
import lzma
import time
import json
import io
import os
from pathlib import Path
import psutil

from app.core.logging import get_logger
from app.core.errors import handle_validation_error, handle_internal_error
from app.models.compression import CompressionOptimization, CompressionStats, CompressionAlgorithm
from app.schemas.compression import (
    CompressionOptimizationResponse, CompressionStatsResponse, CompressionAlgorithmResponse,
    CompressionAnalysisResponse, CompressionPerformanceResponse, CompressionTestResponse
)
from app.utils.validators import validate_compression_algorithm, validate_compression_level
from app.utils.helpers import calculate_compression_ratio, format_file_size
from app.utils.cache import cache_compression_data, get_cached_compression_data

logger = get_logger(__name__)

# Compression algorithms configuration
COMPRESSION_ALGORITHMS = {
    "gzip": {
        "name": "GZIP",
        "description": "Standard gzip compression",
        "default_level": 6,
        "min_level": 1,
        "max_level": 9,
        "fast": True,
        "efficient": True
    },
    "brotli": {
        "name": "Brotli",
        "description": "Google's Brotli compression",
        "default_level": 4,
        "min_level": 0,
        "max_level": 11,
        "fast": False,
        "efficient": True
    },
    "lz4": {
        "name": "LZ4",
        "description": "Fast LZ4 compression",
        "default_level": 1,
        "min_level": 1,
        "max_level": 16,
        "fast": True,
        "efficient": False
    },
    "zstd": {
        "name": "Zstandard",
        "description": "Facebook's Zstandard compression",
        "default_level": 3,
        "min_level": 1,
        "max_level": 22,
        "fast": True,
        "efficient": True
    },
    "bz2": {
        "name": "BZ2",
        "description": "Bzip2 compression",
        "default_level": 9,
        "min_level": 1,
        "max_level": 9,
        "fast": False,
        "efficient": True
    },
    "lzma": {
        "name": "LZMA",
        "description": "LZMA compression",
        "default_level": 6,
        "min_level": 0,
        "max_level": 9,
        "fast": False,
        "efficient": True
    }
}

# Compression statistics
_compression_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
    "compressions": 0,
    "decompressions": 0,
    "total_input_bytes": 0,
    "total_output_bytes": 0,
    "total_compression_time": 0,
    "total_decompression_time": 0
})


def compress_data(
    data: Union[str, bytes],
    algorithm: str = "gzip",
    level: Optional[int] = None,
    encoding: str = "utf-8"
) -> bytes:
    """Compress data using specified algorithm."""
    try:
        # Validate algorithm
        if algorithm not in COMPRESSION_ALGORITHMS:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")
        
        # Set default level if not provided
        if level is None:
            level = COMPRESSION_ALGORITHMS[algorithm]["default_level"]
        
        # Validate level
        min_level = COMPRESSION_ALGORITHMS[algorithm]["min_level"]
        max_level = COMPRESSION_ALGORITHMS[algorithm]["max_level"]
        level = max(min_level, min(level, max_level))
        
        # Convert string to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode(encoding)
        else:
            data_bytes = data
        
        # Compress based on algorithm
        start_time = time.time()
        
        if algorithm == "gzip":
            compressed = gzip.compress(data_bytes, compresslevel=level)
        elif algorithm == "brotli":
            compressed = brotli.compress(data_bytes, quality=level)
        elif algorithm == "lz4":
            compressed = lz4.compress(data_bytes, compression=level)
        elif algorithm == "zstd":
            cctx = zstd.ZstdCompressor(level=level)
            compressed = cctx.compress(data_bytes)
        elif algorithm == "bz2":
            compressed = bz2.compress(data_bytes, compresslevel=level)
        elif algorithm == "lzma":
            compressed = lzma.compress(data_bytes, preset=level)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        compression_time = time.time() - start_time
        
        # Update statistics
        _compression_stats[algorithm]["compressions"] += 1
        _compression_stats[algorithm]["total_input_bytes"] += len(data_bytes)
        _compression_stats[algorithm]["total_output_bytes"] += len(compressed)
        _compression_stats[algorithm]["total_compression_time"] += compression_time
        
        logger.debug(f"Compressed {len(data_bytes)} bytes to {len(compressed)} bytes using {algorithm} in {compression_time:.3f}s")
        
        return compressed
    
    except Exception as e:
        logger.error(f"Failed to compress data with {algorithm}: {e}")
        raise


def decompress_data(
    compressed_data: bytes,
    algorithm: str = "gzip",
    encoding: str = "utf-8"
) -> Union[str, bytes]:
    """Decompress data using specified algorithm."""
    try:
        # Validate algorithm
        if algorithm not in COMPRESSION_ALGORITHMS:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")
        
        # Decompress based on algorithm
        start_time = time.time()
        
        if algorithm == "gzip":
            decompressed = gzip.decompress(compressed_data)
        elif algorithm == "brotli":
            decompressed = brotli.decompress(compressed_data)
        elif algorithm == "lz4":
            decompressed = lz4.decompress(compressed_data)
        elif algorithm == "zstd":
            dctx = zstd.ZstdDecompressor()
            decompressed = dctx.decompress(compressed_data)
        elif algorithm == "bz2":
            decompressed = bz2.decompress(compressed_data)
        elif algorithm == "lzma":
            decompressed = lzma.decompress(compressed_data)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        decompression_time = time.time() - start_time
        
        # Update statistics
        _compression_stats[algorithm]["decompressions"] += 1
        _compression_stats[algorithm]["total_decompression_time"] += decompression_time
        
        logger.debug(f"Decompressed {len(compressed_data)} bytes to {len(decompressed)} bytes using {algorithm} in {decompression_time:.3f}s")
        
        # Return as string if original was string
        try:
            return decompressed.decode(encoding)
        except UnicodeDecodeError:
            return decompressed
    
    except Exception as e:
        logger.error(f"Failed to decompress data with {algorithm}: {e}")
        raise


async def analyze_compression_performance(
    test_data: Optional[Union[str, bytes]] = None,
    algorithms: Optional[List[str]] = None
) -> CompressionAnalysisResponse:
    """Analyze compression performance for different algorithms."""
    try:
        if test_data is None:
            # Generate test data
            test_data = generate_test_data()
        
        if algorithms is None:
            algorithms = list(COMPRESSION_ALGORITHMS.keys())
        
        results = []
        original_size = len(test_data) if isinstance(test_data, bytes) else len(test_data.encode())
        
        for algorithm in algorithms:
            if algorithm not in COMPRESSION_ALGORITHMS:
                continue
            
            try:
                # Test compression
                compressed = compress_data(test_data, algorithm)
                compressed_size = len(compressed)
                
                # Test decompression
                decompressed = decompress_data(compressed, algorithm)
                
                # Verify integrity
                if isinstance(test_data, str):
                    integrity_check = decompressed == test_data
                else:
                    integrity_check = decompressed == test_data
                
                # Calculate metrics
                compression_ratio = calculate_compression_ratio(original_size, compressed_size)
                compression_speed = original_size / _compression_stats[algorithm]["total_compression_time"] if _compression_stats[algorithm]["total_compression_time"] > 0 else 0
                decompression_speed = compressed_size / _compression_stats[algorithm]["total_decompression_time"] if _compression_stats[algorithm]["total_decompression_time"] > 0 else 0
                
                results.append({
                    "algorithm": algorithm,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": compression_ratio,
                    "compression_speed_mbps": compression_speed / 1024 / 1024,
                    "decompression_speed_mbps": decompression_speed / 1024 / 1024,
                    "integrity_check": integrity_check,
                    "algorithm_info": COMPRESSION_ALGORITHMS[algorithm]
                })
            
            except Exception as e:
                results.append({
                    "algorithm": algorithm,
                    "error": str(e),
                    "algorithm_info": COMPRESSION_ALGORITHMS[algorithm]
                })
        
        # Find best algorithms
        best_compression = max([r for r in results if "compression_ratio" in r], key=lambda x: x["compression_ratio"], default=None)
        best_speed = max([r for r in results if "compression_speed_mbps" in r], key=lambda x: x["compression_speed_mbps"], default=None)
        best_balanced = find_best_balanced_algorithm(results)
        
        return CompressionAnalysisResponse(
            test_data_size=original_size,
            algorithms_tested=len(algorithms),
            results=results,
            best_compression=best_compression,
            best_speed=best_speed,
            best_balanced=best_balanced,
            analyzed_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to analyze compression performance: {e}")
        raise handle_internal_error(f"Failed to analyze compression performance: {str(e)}")


def generate_test_data(
    data_type: str = "mixed",
    size_mb: float = 1.0
) -> str:
    """Generate test data for compression analysis."""
    try:
        size_bytes = int(size_mb * 1024 * 1024)
        
        if data_type == "text":
            # Generate repetitive text
            base_text = "The quick brown fox jumps over the lazy dog. " * 100
            return (base_text * (size_bytes // len(base_text) + 1))[:size_bytes]
        
        elif data_type == "json":
            # Generate JSON data
            json_data = {
                "users": [
                    {
                        "id": i,
                        "name": f"User {i}",
                        "email": f"user{i}@example.com",
                        "data": "x" * 100
                    }
                    for i in range(size_bytes // 200)
                ]
            }
            return json.dumps(json_data)
        
        elif data_type == "mixed":
            # Generate mixed content
            content = ""
            for i in range(size_bytes // 100):
                content += f"Line {i}: " + "x" * 50 + "\n"
                if i % 10 == 0:
                    content += json.dumps({"id": i, "data": "y" * 30}) + "\n"
            return content[:size_bytes]
        
        else:
            # Generate random-like data
            import random
            import string
            return ''.join(random.choices(string.ascii_letters + string.digits, k=size_bytes))
    
    except Exception as e:
        logger.error(f"Failed to generate test data: {e}")
        return "Test data generation failed"


def find_best_balanced_algorithm(
    results: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Find the best balanced algorithm considering both compression ratio and speed."""
    try:
        valid_results = [r for r in results if "compression_ratio" in r and "compression_speed_mbps" in r]
        
        if not valid_results:
            return None
        
        # Calculate balanced score (compression ratio * speed)
        for result in valid_results:
            compression_score = result["compression_ratio"] / 100  # Normalize to 0-1
            speed_score = min(result["compression_speed_mbps"] / 100, 1)  # Normalize to 0-1
            result["balanced_score"] = compression_score * 0.7 + speed_score * 0.3
        
        return max(valid_results, key=lambda x: x["balanced_score"])
    
    except Exception as e:
        logger.error(f"Failed to find best balanced algorithm: {e}")
        return None


async def optimize_compression_settings(
    optimization_request: Dict[str, Any],
    db: AsyncSession
) -> CompressionOptimizationResponse:
    """Optimize compression settings based on usage patterns."""
    try:
        optimizations = []
        
        # Analyze current compression usage
        usage_analysis = await analyze_compression_usage()
        
        # Optimize algorithm selection
        algorithm_optimizations = await optimize_algorithm_selection(usage_analysis)
        optimizations.extend(algorithm_optimizations)
        
        # Optimize compression levels
        level_optimizations = await optimize_compression_levels(usage_analysis)
        optimizations.extend(level_optimizations)
        
        # Optimize compression policies
        policy_optimizations = await optimize_compression_policies(usage_analysis)
        optimizations.extend(policy_optimizations)
        
        return CompressionOptimizationResponse(
            optimizations=optimizations,
            total_optimizations=len(optimizations),
            usage_analysis=usage_analysis,
            optimized_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to optimize compression settings: {e}")
        raise handle_internal_error(f"Failed to optimize compression settings: {str(e)}")


async def analyze_compression_usage() -> Dict[str, Any]:
    """Analyze current compression usage patterns."""
    try:
        usage_stats = {}
        
        for algorithm, stats in _compression_stats.items():
            if stats["compressions"] > 0:
                avg_compression_ratio = 1 - (stats["total_output_bytes"] / stats["total_input_bytes"])
                avg_compression_speed = stats["total_input_bytes"] / stats["total_compression_time"] if stats["total_compression_time"] > 0 else 0
                avg_decompression_speed = stats["total_output_bytes"] / stats["total_decompression_time"] if stats["total_decompression_time"] > 0 else 0
                
                usage_stats[algorithm] = {
                    "compressions": stats["compressions"],
                    "decompressions": stats["decompressions"],
                    "total_input_bytes": stats["total_input_bytes"],
                    "total_output_bytes": stats["total_output_bytes"],
                    "avg_compression_ratio": avg_compression_ratio,
                    "avg_compression_speed_mbps": avg_compression_speed / 1024 / 1024,
                    "avg_decompression_speed_mbps": avg_decompression_speed / 1024 / 1024,
                    "total_compression_time": stats["total_compression_time"],
                    "total_decompression_time": stats["total_decompression_time"]
                }
        
        return usage_stats
    
    except Exception as e:
        logger.error(f"Failed to analyze compression usage: {e}")
        return {}


async def optimize_algorithm_selection(
    usage_analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Optimize algorithm selection based on usage patterns."""
    try:
        optimizations = []
        
        # Find most used algorithm
        most_used = max(usage_analysis.items(), key=lambda x: x[1]["compressions"], default=None)
        
        if most_used:
            algorithm, stats = most_used
            
            # Check if current algorithm is optimal
            if algorithm == "gzip" and stats["avg_compression_ratio"] < 0.6:
                optimizations.append({
                    "type": "algorithm_optimization",
                    "current_algorithm": algorithm,
                    "recommended_algorithm": "brotli",
                    "reason": "Low compression ratio with gzip, brotli would be more efficient",
                    "expected_improvement": "20-30% better compression"
                })
            
            elif algorithm == "brotli" and stats["avg_compression_speed_mbps"] < 10:
                optimizations.append({
                    "type": "algorithm_optimization",
                    "current_algorithm": algorithm,
                    "recommended_algorithm": "gzip",
                    "reason": "Slow compression with brotli, gzip would be faster",
                    "expected_improvement": "2-3x faster compression"
                })
            
            elif algorithm == "gzip" and stats["avg_compression_speed_mbps"] > 50:
                optimizations.append({
                    "type": "algorithm_optimization",
                    "current_algorithm": algorithm,
                    "recommended_algorithm": "lz4",
                    "reason": "High speed requirements, lz4 would be even faster",
                    "expected_improvement": "3-5x faster compression"
                })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize algorithm selection: {e}")
        return []


async def optimize_compression_levels(
    usage_analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Optimize compression levels based on usage patterns."""
    try:
        optimizations = []
        
        for algorithm, stats in usage_analysis.items():
            if algorithm in COMPRESSION_ALGORITHMS:
                algorithm_info = COMPRESSION_ALGORITHMS[algorithm]
                
                # Check if compression level needs optimization
                if stats["avg_compression_ratio"] < 0.5 and algorithm_info["max_level"] > algorithm_info["default_level"]:
                    optimizations.append({
                        "type": "level_optimization",
                        "algorithm": algorithm,
                        "current_level": algorithm_info["default_level"],
                        "recommended_level": min(algorithm_info["default_level"] + 2, algorithm_info["max_level"]),
                        "reason": "Low compression ratio, higher level would improve compression",
                        "expected_improvement": "10-20% better compression"
                    })
                
                elif stats["avg_compression_speed_mbps"] < 5 and algorithm_info["min_level"] < algorithm_info["default_level"]:
                    optimizations.append({
                        "type": "level_optimization",
                        "algorithm": algorithm,
                        "current_level": algorithm_info["default_level"],
                        "recommended_level": max(algorithm_info["default_level"] - 2, algorithm_info["min_level"]),
                        "reason": "Slow compression, lower level would improve speed",
                        "expected_improvement": "2-3x faster compression"
                    })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize compression levels: {e}")
        return []


async def optimize_compression_policies(
    usage_analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Optimize compression policies based on usage patterns."""
    try:
        optimizations = []
        
        # Analyze compression patterns
        total_compressions = sum(stats["compressions"] for stats in usage_analysis.values())
        total_input_bytes = sum(stats["total_input_bytes"] for stats in usage_analysis.values())
        
        if total_compressions > 0:
            avg_data_size = total_input_bytes / total_compressions
            
            # Recommend compression policies based on data size
            if avg_data_size < 1024:  # Less than 1KB
                optimizations.append({
                    "type": "policy_optimization",
                    "policy": "skip_compression",
                    "condition": "data_size < 1KB",
                    "reason": "Small data sizes don't benefit from compression",
                    "expected_improvement": "Reduced CPU usage"
                })
            
            elif avg_data_size > 1024 * 1024:  # More than 1MB
                optimizations.append({
                    "type": "policy_optimization",
                    "policy": "use_high_compression",
                    "condition": "data_size > 1MB",
                    "reason": "Large data sizes benefit from high compression",
                    "expected_improvement": "Better storage efficiency"
                })
            
            # Recommend streaming compression for large data
            if avg_data_size > 10 * 1024 * 1024:  # More than 10MB
                optimizations.append({
                    "type": "policy_optimization",
                    "policy": "streaming_compression",
                    "condition": "data_size > 10MB",
                    "reason": "Large data should use streaming compression",
                    "expected_improvement": "Reduced memory usage"
                })
        
        return optimizations
    
    except Exception as e:
        logger.error(f"Failed to optimize compression policies: {e}")
        return []


async def create_compression_performance_report(
    db: AsyncSession
) -> CompressionPerformanceResponse:
    """Create comprehensive compression performance report."""
    try:
        # Analyze compression performance
        compression_analysis = await analyze_compression_performance()
        
        # Analyze usage patterns
        usage_analysis = await analyze_compression_usage()
        
        # Get optimization recommendations
        optimization_response = await optimize_compression_settings({}, db)
        
        # Calculate performance metrics
        total_compressions = sum(stats["compressions"] for stats in usage_analysis.values())
        total_bytes_saved = sum(stats["total_input_bytes"] - stats["total_output_bytes"] for stats in usage_analysis.values())
        total_compression_time = sum(stats["total_compression_time"] for stats in usage_analysis.values())
        
        # Calculate performance score
        performance_score = 100
        
        if compression_analysis.best_compression and compression_analysis.best_compression["compression_ratio"] < 0.5:
            performance_score -= 20
        
        if compression_analysis.best_speed and compression_analysis.best_speed["compression_speed_mbps"] < 10:
            performance_score -= 15
        
        if total_compression_time > 60:  # More than 1 minute total compression time
            performance_score -= 10
        
        performance_score = max(0, performance_score)
        
        # Generate recommendations
        recommendations = []
        
        if compression_analysis.best_compression and compression_analysis.best_compression["compression_ratio"] < 0.6:
            recommendations.append("Consider using higher compression algorithms for better efficiency")
        
        if compression_analysis.best_speed and compression_analysis.best_speed["compression_speed_mbps"] < 20:
            recommendations.append("Consider using faster compression algorithms for better performance")
        
        if len(optimization_response.optimizations) > 0:
            recommendations.append(f"Found {len(optimization_response.optimizations)} compression optimization opportunities")
        
        return CompressionPerformanceResponse(
            performance_score=performance_score,
            total_compressions=total_compressions,
            total_bytes_saved=total_bytes_saved,
            total_compression_time=total_compression_time,
            compression_analysis=compression_analysis,
            usage_analysis=usage_analysis,
            optimization_recommendations=optimization_response,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to create compression performance report: {e}")
        raise handle_internal_error(f"Failed to create compression performance report: {str(e)}")


async def test_compression_algorithms(
    test_data: Union[str, bytes],
    algorithms: Optional[List[str]] = None
) -> CompressionTestResponse:
    """Test compression algorithms with specific data."""
    try:
        if algorithms is None:
            algorithms = list(COMPRESSION_ALGORITHMS.keys())
        
        test_results = []
        original_size = len(test_data) if isinstance(test_data, bytes) else len(test_data.encode())
        
        for algorithm in algorithms:
            if algorithm not in COMPRESSION_ALGORITHMS:
                continue
            
            try:
                # Test compression
                start_time = time.time()
                compressed = compress_data(test_data, algorithm)
                compression_time = time.time() - start_time
                
                # Test decompression
                start_time = time.time()
                decompressed = decompress_data(compressed, algorithm)
                decompression_time = time.time() - start_time
                
                # Verify integrity
                if isinstance(test_data, str):
                    integrity_check = decompressed == test_data
                else:
                    integrity_check = decompressed == test_data
                
                # Calculate metrics
                compression_ratio = calculate_compression_ratio(original_size, len(compressed))
                compression_speed = original_size / compression_time if compression_time > 0 else 0
                decompression_speed = len(compressed) / decompression_time if decompression_time > 0 else 0
                
                test_results.append({
                    "algorithm": algorithm,
                    "original_size": original_size,
                    "compressed_size": len(compressed),
                    "compression_ratio": compression_ratio,
                    "compression_time": compression_time,
                    "decompression_time": decompression_time,
                    "compression_speed_mbps": compression_speed / 1024 / 1024,
                    "decompression_speed_mbps": decompression_speed / 1024 / 1024,
                    "integrity_check": integrity_check,
                    "success": True
                })
            
            except Exception as e:
                test_results.append({
                    "algorithm": algorithm,
                    "error": str(e),
                    "success": False
                })
        
        # Find best results
        successful_results = [r for r in test_results if r["success"]]
        best_compression = max(successful_results, key=lambda x: x["compression_ratio"], default=None)
        best_speed = max(successful_results, key=lambda x: x["compression_speed_mbps"], default=None)
        
        return CompressionTestResponse(
            test_data_size=original_size,
            algorithms_tested=len(algorithms),
            successful_tests=len(successful_results),
            test_results=test_results,
            best_compression=best_compression,
            best_speed=best_speed,
            tested_at=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to test compression algorithms: {e}")
        raise handle_internal_error(f"Failed to test compression algorithms: {str(e)}")


async def get_compression_stats(
    algorithm: Optional[str] = None
) -> Dict[str, CompressionStatsResponse]:
    """Get compression statistics."""
    try:
        stats = {}
        
        if algorithm:
            algorithms = [algorithm] if algorithm in _compression_stats else []
        else:
            algorithms = list(_compression_stats.keys())
        
        for alg in algorithms:
            if alg in _compression_stats:
                alg_stats = _compression_stats[alg]
                
                if alg_stats["compressions"] > 0:
                    avg_compression_ratio = 1 - (alg_stats["total_output_bytes"] / alg_stats["total_input_bytes"])
                    avg_compression_speed = alg_stats["total_input_bytes"] / alg_stats["total_compression_time"] if alg_stats["total_compression_time"] > 0 else 0
                    avg_decompression_speed = alg_stats["total_output_bytes"] / alg_stats["total_decompression_time"] if alg_stats["total_decompression_time"] > 0 else 0
                    
                    stats[alg] = CompressionStatsResponse(
                        algorithm=alg,
                        compressions=alg_stats["compressions"],
                        decompressions=alg_stats["decompressions"],
                        total_input_bytes=alg_stats["total_input_bytes"],
                        total_output_bytes=alg_stats["total_output_bytes"],
                        avg_compression_ratio=round(avg_compression_ratio, 4),
                        avg_compression_speed_mbps=round(avg_compression_speed / 1024 / 1024, 2),
                        avg_decompression_speed_mbps=round(avg_decompression_speed / 1024 / 1024, 2),
                        total_compression_time=round(alg_stats["total_compression_time"], 3),
                        total_decompression_time=round(alg_stats["total_decompression_time"], 3)
                    )
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get compression stats: {e}")
        return {}


async def clear_compression_stats(
    algorithm: Optional[str] = None
) -> Dict[str, str]:
    """Clear compression statistics."""
    try:
        if algorithm:
            if algorithm in _compression_stats:
                _compression_stats[algorithm] = {
                    "compressions": 0,
                    "decompressions": 0,
                    "total_input_bytes": 0,
                    "total_output_bytes": 0,
                    "total_compression_time": 0,
                    "total_decompression_time": 0
                }
                return {"message": f"Compression stats cleared for {algorithm}"}
            else:
                return {"message": f"No stats found for {algorithm}"}
        else:
            _compression_stats.clear()
            return {"message": "All compression stats cleared"}
    
    except Exception as e:
        logger.error(f"Failed to clear compression stats: {e}")
        return {"error": str(e)}




