"""
Library Detector - Intelligent detection of quantum optimization libraries.
"""

import importlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class LibraryInfo:
    """Information about a quantum optimization library."""
    name: str
    available: bool = False
    version: Optional[str] = None
    performance_factor: float = 1.0
    description: str = ""
    category: str = "general"
    quantum_features: List[str] = None

    def __post_init__(self):
        if self.quantum_features is None:
            self.quantum_features = []

class QuantumLibraryDetector:
    """Quantum-level library detection and optimization scoring."""
    
    QUANTUM_LIBRARIES = {
        # Event loops
        "uvloop": LibraryInfo(
            name="uvloop",
            performance_factor=4.0,
            description="Ultra-fast event loop (2-4x faster)",
            category="eventloop",
            quantum_features=["async_optimization", "c_implementation"]
        ),
        
        # JSON serialization
        "orjson": LibraryInfo(
            name="orjson",
            performance_factor=5.0,
            description="Ultra-fast JSON (5-10x faster than json)",
            category="serialization",
            quantum_features=["rust_implementation", "simd_optimization"]
        ),
        "msgspec": LibraryInfo(
            name="msgspec",
            performance_factor=6.0,
            description="Rust-based serialization (fastest available)",
            category="serialization",
            quantum_features=["rust_implementation", "zero_copy", "schema_validation"]
        ),
        "simdjson": LibraryInfo(
            name="simdjson",
            performance_factor=8.0,
            description="SIMD-accelerated JSON parsing",
            category="serialization",
            quantum_features=["simd_optimization", "parallel_parsing"]
        ),
        "ujson": LibraryInfo(
            name="ujson",
            performance_factor=3.0,
            description="Fast JSON library",
            category="serialization",
            quantum_features=["c_implementation"]
        ),
        
        # Hashing
        "blake3": LibraryInfo(
            name="blake3",
            performance_factor=10.0,
            description="Fastest cryptographic hash",
            category="hashing",
            quantum_features=["rust_implementation", "simd_optimization", "parallel_hashing"]
        ),
        "xxhash": LibraryInfo(
            name="xxhash",
            performance_factor=8.0,
            description="Extremely fast non-cryptographic hash",
            category="hashing",
            quantum_features=["c_implementation", "streaming_hash"]
        ),
        "mmh3": LibraryInfo(
            name="mmh3",
            performance_factor=6.0,
            description="MurmurHash3 implementation",
            category="hashing",
            quantum_features=["c_implementation"]
        ),
        
        # Compression
        "blosc2": LibraryInfo(
            name="blosc2",
            performance_factor=12.0,
            description="Multi-threaded compression with SIMD",
            category="compression",
            quantum_features=["multi_threading", "simd_optimization", "multiple_codecs"]
        ),
        "cramjam": LibraryInfo(
            name="cramjam",
            performance_factor=10.0,
            description="Rust compression bindings (ultra-fast)",
            category="compression",
            quantum_features=["rust_implementation", "multiple_algorithms"]
        ),
        "lz4": LibraryInfo(
            name="lz4",
            performance_factor=8.0,
            description="Ultra-fast compression",
            category="compression",
            quantum_features=["c_implementation", "streaming_compression"]
        ),
        "zstandard": LibraryInfo(
            name="zstandard",
            performance_factor=6.0,
            description="Facebook's Zstd compression",
            category="compression",
            quantum_features=["adaptive_compression", "dictionary_support"]
        ),
        
        # Data processing
        "polars": LibraryInfo(
            name="polars",
            performance_factor=100.0,
            description="Lightning-fast DataFrame library (100x faster than pandas)",
            category="dataframes",
            quantum_features=["rust_implementation", "lazy_evaluation", "columnar_processing", "simd_optimization"]
        ),
        "pyarrow": LibraryInfo(
            name="pyarrow",
            performance_factor=20.0,
            description="Apache Arrow for columnar data",
            category="dataframes",
            quantum_features=["columnar_format", "zero_copy", "simd_optimization"]
        ),
        "duckdb": LibraryInfo(
            name="duckdb",
            performance_factor=50.0,
            description="In-process OLAP database",
            category="database",
            quantum_features=["vectorized_execution", "columnar_storage", "parallel_processing"]
        ),
        
        # JIT compilation
        "numba": LibraryInfo(
            name="numba",
            performance_factor=20.0,
            description="JIT compiler for numerical code",
            category="jit",
            quantum_features=["llvm_compilation", "parallel_execution", "gpu_support"]
        ),
        
        # System monitoring
        "psutil": LibraryInfo(
            name="psutil",
            performance_factor=2.0,
            description="System and process monitoring",
            category="monitoring",
            quantum_features=["cross_platform", "real_time_monitoring"]
        ),
        
        # Caching
        "diskcache": LibraryInfo(
            name="diskcache",
            performance_factor=5.0,
            description="Disk-based cache with memory mapping",
            category="caching",
            quantum_features=["memory_mapping", "persistent_cache", "atomic_operations"]
        ),
    }
    
    def __init__(self):
        self.available_libraries: Dict[str, LibraryInfo] = {}
        self.quantum_score = 0.0
        self.detect_all()
    
    def detect_library(self, name: str) -> bool:
        """Detect if a specific library is available."""
        try:
            module = importlib.import_module(name)
            version = getattr(module, '__version__', 'unknown')
            
            if name in self.QUANTUM_LIBRARIES:
                lib_info = self.QUANTUM_LIBRARIES[name]
                lib_info.available = True
                lib_info.version = version
                self.available_libraries[name] = lib_info
                logger.info(f"✅ Quantum library {name} v{version} detected")
                return True
            
        except ImportError:
            logger.debug(f"❌ {name} not available")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error detecting {name}: {e}")
            return False
        
        return False
    
    def detect_all(self) -> Dict[str, LibraryInfo]:
        """Detect all quantum optimization libraries."""
        logger.info("🌌 Detecting quantum optimization libraries...")
        
        for lib_name in self.QUANTUM_LIBRARIES.keys():
            self.detect_library(lib_name)
        
        self.quantum_score = self._calculate_quantum_score()
        
        detected_count = len(self.available_libraries)
        total_count = len(self.QUANTUM_LIBRARIES)
        
        logger.info(f"🚀 Detected {detected_count}/{total_count} quantum libraries")
        logger.info(f"⚡ Quantum optimization score: {self.quantum_score:.1f}x")
        
        return self.available_libraries
    
    def _calculate_quantum_score(self) -> float:
        """Calculate quantum optimization score."""
        if not self.available_libraries:
            return 1.0
        
        total_factor = 1.0
        category_bonuses = {
            "serialization": 0.3,
            "compression": 0.2,
            "dataframes": 0.4,
            "hashing": 0.15,
            "jit": 0.35
        }
        
        # Base performance calculation
        for lib_info in self.available_libraries.values():
            factor_contribution = (lib_info.performance_factor - 1.0) * 0.05
            total_factor += factor_contribution
        
        # Category bonuses
        categories_covered = set()
        for lib_info in self.available_libraries.values():
            categories_covered.add(lib_info.category)
        
        for category in categories_covered:
            if category in category_bonuses:
                total_factor += category_bonuses[category]
        
        # Quantum features bonus
        quantum_features_count = sum(
            len(lib.quantum_features) for lib in self.available_libraries.values()
        )
        quantum_bonus = min(1.0, quantum_features_count * 0.02)
        total_factor += quantum_bonus
        
        return min(total_factor, 20.0)  # Cap at 20x improvement
    
    def get_best_library(self, category: str) -> Optional[LibraryInfo]:
        """Get the best available library for a category."""
        category_libs = [
            lib for lib in self.available_libraries.values()
            if lib.category == category and lib.available
        ]
        
        if not category_libs:
            return None
        
        return max(category_libs, key=lambda x: x.performance_factor)
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get recommendations for missing high-impact libraries."""
        recommendations = []
        
        high_impact_libs = [
            ("msgspec", "Fastest serialization (Rust-based)"),
            ("polars", "100x faster DataFrames"),
            ("blake3", "Fastest cryptographic hashing"),
            ("cramjam", "Ultra-fast compression (Rust)"),
            ("uvloop", "4x faster event loop"),
            ("numba", "JIT compilation for numerical code"),
            ("simdjson", "SIMD JSON parsing"),
            ("blosc2", "Multi-threaded compression with SIMD")
        ]
        
        for lib_name, description in high_impact_libs:
            if lib_name not in self.available_libraries:
                recommendations.append(f"pip install {lib_name}  # {description}")
        
        return recommendations
    
    def get_quantum_features(self) -> List[str]:
        """Get all available quantum features."""
        features = set()
        for lib in self.available_libraries.values():
            features.update(lib.quantum_features)
        return sorted(list(features))
    
    def get_category_coverage(self) -> Dict[str, Dict[str, Any]]:
        """Get coverage by category."""
        categories = {}
        
        for lib in self.QUANTUM_LIBRARIES.values():
            category = lib.category
            if category not in categories:
                categories[category] = {
                    "total_libraries": 0,
                    "available_libraries": 0,
                    "best_performance": 1.0,
                    "libraries": []
                }
            
            categories[category]["total_libraries"] += 1
            categories[category]["libraries"].append(lib.name)
            
            if lib.available:
                categories[category]["available_libraries"] += 1
                categories[category]["best_performance"] = max(
                    categories[category]["best_performance"],
                    lib.performance_factor
                )
        
        return categories
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive quantum status report."""
        return {
            "quantum_score": self.quantum_score,
            "total_libraries": len(self.QUANTUM_LIBRARIES),
            "available_libraries": len(self.available_libraries),
            "coverage_percentage": (len(self.available_libraries) / len(self.QUANTUM_LIBRARIES)) * 100,
            "quantum_features": self.get_quantum_features(),
            "category_coverage": self.get_category_coverage(),
            "recommendations": self.get_optimization_recommendations(),
            "best_libraries": {
                category: self.get_best_library(category).name if self.get_best_library(category) else None
                for category in ["serialization", "compression", "dataframes", "hashing", "jit", "eventloop"]
            },
            "libraries": {
                name: {
                    "available": info.available,
                    "version": info.version,
                    "performance_factor": info.performance_factor,
                    "description": info.description,
                    "category": info.category,
                    "quantum_features": info.quantum_features
                }
                for name, info in self.QUANTUM_LIBRARIES.items()
            }
        }

# Global detector instance
detector = QuantumLibraryDetector() 