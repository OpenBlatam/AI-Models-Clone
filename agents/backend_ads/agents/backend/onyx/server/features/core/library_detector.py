"""
Library Detector - Intelligent detection of available optimization libraries.
"""

import importlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class LibraryInfo:
    """Information about an optimization library."""
    name: str
    available: bool
    version: Optional[str] = None
    performance_factor: float = 1.0  # Performance multiplier
    description: str = ""
    fallback: Optional[str] = None

class LibraryDetector:
    """Intelligent detection and management of optimization libraries."""
    
    OPTIMIZATION_LIBRARIES = {
        # Event loops
        "uvloop": LibraryInfo(
            name="uvloop",
            available=False,
            performance_factor=3.0,
            description="Ultra-fast event loop (2-4x faster)",
            fallback="asyncio"
        ),
        
        # JSON serialization
        "orjson": LibraryInfo(
            name="orjson",
            available=False,
            performance_factor=4.0,
            description="Ultra-fast JSON (3-5x faster than json)",
            fallback="ujson"
        ),
        "ujson": LibraryInfo(
            name="ujson",
            available=False,
            performance_factor=2.5,
            description="Fast JSON library",
            fallback="json"
        ),
        "rapidjson": LibraryInfo(
            name="rapidjson",
            available=False,
            performance_factor=3.0,
            description="C++ JSON library",
            fallback="json"
        ),
        "simdjson": LibraryInfo(
            name="simdjson",
            available=False,
            performance_factor=5.0,
            description="SIMD-accelerated JSON parsing",
            fallback="orjson"
        ),
        
        # Hashing
        "blake3": LibraryInfo(
            name="blake3",
            available=False,
            performance_factor=10.0,
            description="Fastest cryptographic hash",
            fallback="xxhash"
        ),
        "xxhash": LibraryInfo(
            name="xxhash",
            available=False,
            performance_factor=8.0,
            description="Extremely fast non-cryptographic hash",
            fallback="mmh3"
        ),
        "mmh3": LibraryInfo(
            name="mmh3",
            available=False,
            performance_factor=6.0,
            description="MurmurHash3 implementation",
            fallback="hashlib"
        ),
        
        # Compression
        "blosc2": LibraryInfo(
            name="blosc2",
            available=False,
            performance_factor=8.0,
            description="Multi-threaded compression",
            fallback="lz4"
        ),
        "lz4": LibraryInfo(
            name="lz4",
            available=False,
            performance_factor=6.0,
            description="Ultra-fast compression",
            fallback="zstandard"
        ),
        "zstandard": LibraryInfo(
            name="zstandard",
            available=False,
            performance_factor=4.0,
            description="Facebook's Zstd compression",
            fallback="gzip"
        ),
        "cramjam": LibraryInfo(
            name="cramjam",
            available=False,
            performance_factor=7.0,
            description="Rust compression bindings",
            fallback="lz4"
        ),
        
        # Data processing
        "polars": LibraryInfo(
            name="polars",
            available=False,
            performance_factor=50.0,
            description="Lightning-fast DataFrame library (10-100x faster than pandas)",
            fallback="pyarrow"
        ),
        "pyarrow": LibraryInfo(
            name="pyarrow",
            available=False,
            performance_factor=10.0,
            description="Apache Arrow for columnar data",
            fallback="pandas"
        ),
        "duckdb": LibraryInfo(
            name="duckdb",
            available=False,
            performance_factor=20.0,
            description="In-process OLAP database",
            fallback="sqlite3"
        ),
        
        # JIT compilation
        "numba": LibraryInfo(
            name="numba",
            available=False,
            performance_factor=15.0,
            description="JIT compiler for numerical code",
            fallback=None
        ),
        
        # System monitoring
        "psutil": LibraryInfo(
            name="psutil",
            available=False,
            performance_factor=1.0,
            description="System and process monitoring",
            fallback=None
        ),
        "pympler": LibraryInfo(
            name="pympler",
            available=False,
            performance_factor=1.0,
            description="Memory profiling and analysis",
            fallback=None
        ),
    }
    
    def __init__(self):
        self.available_libraries: Dict[str, LibraryInfo] = {}
        self.detect_all()
    
    def detect_library(self, name: str) -> bool:
        """Detect if a specific library is available."""
        try:
            module = importlib.import_module(name)
            version = getattr(module, '__version__', 'unknown')
            
            if name in self.OPTIMIZATION_LIBRARIES:
                lib_info = self.OPTIMIZATION_LIBRARIES[name]
                lib_info.available = True
                lib_info.version = version
                self.available_libraries[name] = lib_info
                logger.info(f"✅ {name} v{version} detected")
                return True
            
        except ImportError:
            logger.debug(f"❌ {name} not available")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error detecting {name}: {e}")
            return False
        
        return False
    
    def detect_all(self) -> Dict[str, LibraryInfo]:
        """Detect all optimization libraries."""
        logger.info("🔍 Detecting optimization libraries...")
        
        for lib_name in self.OPTIMIZATION_LIBRARIES.keys():
            self.detect_library(lib_name)
        
        detected_count = len(self.available_libraries)
        total_count = len(self.OPTIMIZATION_LIBRARIES)
        
        logger.info(f"📊 Detected {detected_count}/{total_count} optimization libraries")
        
        return self.available_libraries
    
    def get_best_library(self, category: str) -> Optional[LibraryInfo]:
        """Get the best available library for a category."""
        category_libs = {
            "json": ["simdjson", "orjson", "rapidjson", "ujson"],
            "hash": ["blake3", "xxhash", "mmh3"],
            "compression": ["blosc2", "cramjam", "lz4", "zstandard"],
            "data": ["polars", "pyarrow", "duckdb"],
            "eventloop": ["uvloop"],
            "jit": ["numba"],
            "monitoring": ["psutil", "pympler"]
        }
        
        if category not in category_libs:
            return None
        
        for lib_name in category_libs[category]:
            if lib_name in self.available_libraries:
                return self.available_libraries[lib_name]
        
        return None
    
    def get_performance_score(self) -> float:
        """Calculate overall performance score based on available libraries."""
        if not self.available_libraries:
            return 1.0
        
        total_factor = 1.0
        for lib_info in self.available_libraries.values():
            total_factor *= (1.0 + (lib_info.performance_factor - 1.0) * 0.1)
        
        return min(total_factor, 10.0)  # Cap at 10x improvement
    
    def get_recommendations(self) -> List[str]:
        """Get recommendations for missing high-impact libraries."""
        recommendations = []
        
        high_impact_libs = [
            ("orjson", "JSON serialization 3-5x faster"),
            ("uvloop", "Event loop 2-4x faster"),
            ("blake3", "Fastest cryptographic hashing"),
            ("polars", "DataFrame processing 10-100x faster"),
            ("blosc2", "Multi-threaded compression"),
            ("numba", "JIT compilation for numerical code")
        ]
        
        for lib_name, description in high_impact_libs:
            if lib_name not in self.available_libraries:
                recommendations.append(f"pip install {lib_name}  # {description}")
        
        return recommendations
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        return {
            "total_libraries": len(self.OPTIMIZATION_LIBRARIES),
            "available_libraries": len(self.available_libraries),
            "performance_score": self.get_performance_score(),
            "libraries": {
                name: {
                    "available": info.available,
                    "version": info.version,
                    "performance_factor": info.performance_factor,
                    "description": info.description
                }
                for name, info in self.OPTIMIZATION_LIBRARIES.items()
            },
            "recommendations": self.get_recommendations(),
            "best_choices": {
                category: self.get_best_library(category).name if self.get_best_library(category) else None
                for category in ["json", "hash", "compression", "data", "eventloop", "jit", "monitoring"]
            }
        }

# Global detector instance
detector = LibraryDetector() 