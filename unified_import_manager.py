#!/usr/bin/env python3
"""
🚀 Unified Import Manager - Consolidated Import Management System
================================================================

Consolidates all scattered import patterns into a single, organized system
that eliminates import inconsistencies and provides consistent dependency
management across the entire codebase.
"""

import sys
import importlib
import importlib.util
from typing import Dict, List, Any, Optional, Union, Callable, Type, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# Import Categories and Types
# =============================================================================

class ImportCategory(Enum):
    """Categories for organizing imports."""
    STANDARD_LIBRARY = "standard_library"
    THIRD_PARTY = "third_party"
    LOCAL_MODULES = "local_modules"
    OPTIONAL_DEPENDENCIES = "optional_dependencies"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    MONITORING = "monitoring"
    DATABASE = "database"
    WEB_FRAMEWORK = "web_framework"
    AI_ML = "ai_ml"
    UTILITIES = "utilities"

class ImportPriority(Enum):
    """Import priority levels."""
    CRITICAL = "critical"      # Must be available
    HIGH = "high"              # Important for core functionality
    MEDIUM = "medium"          # Nice to have
    LOW = "low"                # Optional features
    EXPERIMENTAL = "experimental"  # Experimental features

@dataclass
class ImportDefinition:
    """Definition for an import."""
    module_name: str
    import_path: str
    category: ImportCategory
    priority: ImportPriority
    description: str
    version_requirement: Optional[str] = None
    alternative_imports: List[str] = field(default_factory=list)
    is_async: bool = False
    is_optional: bool = False

@dataclass
class ImportResult:
    """Result of an import operation."""
    module_name: str
    success: bool
    imported_module: Optional[Any] = None
    error_message: Optional[str] = None
    import_time_ms: float = 0.0
    fallback_used: bool = False

# =============================================================================
# Core Import Definitions
# =============================================================================

CORE_IMPORTS = {
    # Standard Library - Critical
    "asyncio": ImportDefinition(
        module_name="asyncio",
        import_path="asyncio",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Asynchronous I/O support",
        is_async=True
    ),
    "typing": ImportDefinition(
        module_name="typing",
        import_path="typing",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Type hints and generic types"
    ),
    "dataclasses": ImportDefinition(
        module_name="dataclasses",
        import_path="dataclasses",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Data classes for structured data"
    ),
    "datetime": ImportDefinition(
        module_name="datetime",
        import_path="datetime",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Date and time handling"
    ),
    "collections": ImportDefinition(
        module_name="collections",
        import_path="collections",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Specialized container datatypes"
    ),
    "contextlib": ImportDefinition(
        module_name="contextlib",
        import_path="contextlib",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Context manager utilities"
    ),
    "enum": ImportDefinition(
        module_name="enum",
        import_path="enum",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Enumeration support"
    ),
    "pathlib": ImportDefinition(
        module_name="pathlib",
        import_path="pathlib",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Object-oriented filesystem paths"
    ),
    "json": ImportDefinition(
        module_name="json",
        import_path="json",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="JSON encoding and decoding"
    ),
    "logging": ImportDefinition(
        module_name="logging",
        import_path="logging",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Logging facility"
    ),
    "time": ImportDefinition(
        module_name="time",
        import_path="time",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Time-related functions"
    ),
    "threading": ImportDefinition(
        module_name="threading",
        import_path="threading",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.CRITICAL,
        description="Thread-based parallelism"
    ),
    "weakref": ImportDefinition(
        module_name="weakref",
        import_path="weakref",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.HIGH,
        description="Weak references"
    ),
    "functools": ImportDefinition(
        module_name="functools",
        import_path="functools",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.HIGH,
        description="Higher-order functions and operations on callable objects"
    ),
    "concurrent.futures": ImportDefinition(
        module_name="concurrent.futures",
        import_path="concurrent.futures",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.HIGH,
        description="Asynchronous execution of callable objects"
    ),
    "multiprocessing": ImportDefinition(
        module_name="multiprocessing",
        import_path="multiprocessing",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.MEDIUM,
        description="Process-based parallelism"
    ),
    "gc": ImportDefinition(
        module_name="gc",
        import_path="gc",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.MEDIUM,
        description="Garbage collector interface"
    ),
    "tracemalloc": ImportDefinition(
        module_name="tracemalloc",
        import_path="tracemalloc",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.MEDIUM,
        description="Trace memory allocations"
    ),
    "pickle": ImportDefinition(
        module_name="pickle",
        import_path="pickle",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.MEDIUM,
        description="Python object serialization"
    ),
    "hashlib": ImportDefinition(
        module_name="hashlib",
        import_path="hashlib",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.MEDIUM,
        description="Secure hash and message digest algorithms"
    ),
    "base64": ImportDefinition(
        module_name="base64",
        import_path="base64",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="Base16, Base32, Base64, Base85 Data Encodings"
    ),
    "statistics": ImportDefinition(
        module_name="statistics",
        import_path="statistics",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="Mathematical statistics functions"
    ),
    "math": ImportDefinition(
        module_name="math",
        import_path="math",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="Mathematical functions"
    ),
    "uuid": ImportDefinition(
        module_name="uuid",
        import_path="uuid",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="UUID objects"
    ),
    "os": ImportDefinition(
        module_name="os",
        import_path="os",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="Miscellaneous operating system interfaces"
    ),
    "sys": ImportDefinition(
        module_name="sys",
        import_path="sys",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="System-specific parameters and functions"
    ),
    "signal": ImportDefinition(
        module_name="signal",
        import_path="signal",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="Set handlers for asynchronous events"
    ),
    "queue": ImportDefinition(
        module_name="queue",
        import_path="queue",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="A synchronized queue class"
    ),
    "inspect": ImportDefinition(
        module_name="inspect",
        import_path="inspect",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="Inspect live objects"
    ),
    "abc": ImportDefinition(
        module_name="abc",
        import_path="abc",
        category=ImportCategory.STANDARD_LIBRARY,
        priority=ImportPriority.LOW,
        description="Abstract base classes"
    ),
    
    # Third Party - Critical
    "fastapi": ImportDefinition(
        module_name="fastapi",
        import_path="fastapi",
        category=ImportCategory.WEB_FRAMEWORK,
        priority=ImportPriority.CRITICAL,
        description="Modern, fast web framework for building APIs"
    ),
    "pydantic": ImportDefinition(
        module_name="pydantic",
        import_path="pydantic",
        category=ImportCategory.THIRD_PARTY,
        priority=ImportPriority.CRITICAL,
        description="Data validation using Python type annotations"
    ),
    "structlog": ImportDefinition(
        module_name="structlog",
        import_path="structlog",
        category=ImportCategory.LOGGING,
        priority=ImportPriority.CRITICAL,
        description="Structured logging for Python"
    ),
    
    # Third Party - High Priority
    "psutil": ImportDefinition(
        module_name="psutil",
        import_path="psutil",
        category=ImportCategory.MONITORING,
        priority=ImportPriority.HIGH,
        description="Cross-platform library for retrieving information on running processes and system utilization"
    ),
    "numpy": ImportDefinition(
        module_name="numpy",
        import_path="numpy",
        category=ImportCategory.AI_ML,
        priority=ImportPriority.HIGH,
        description="Fundamental package for array computing with Python"
    ),
    "aiohttp": ImportDefinition(
        module_name="aiohttp",
        import_path="aiohttp",
        category=ImportCategory.WEB_FRAMEWORK,
        priority=ImportPriority.HIGH,
        description="Async HTTP client/server framework",
        is_async=True
    ),
    "httpx": ImportDefinition(
        module_name="httpx",
        import_path="httpx",
        category=ImportCategory.WEB_FRAMEWORK,
        priority=ImportPriority.HIGH,
        description="A fully featured HTTP client for Python",
        is_async=True
    ),
    "aioredis": ImportDefinition(
        module_name="aioredis",
        import_path="aioredis",
        category=ImportCategory.DATABASE,
        priority=ImportPriority.HIGH,
        description="Redis client for Python asyncio",
        is_async=True
    ),
    "asyncpg": ImportDefinition(
        module_name="asyncpg",
        import_path="asyncpg",
        category=ImportCategory.DATABASE,
        priority=ImportPriority.HIGH,
        description="An asyncio PostgreSQL driver",
        is_async=True
    ),
    "motor": ImportDefinition(
        module_name="motor",
        import_path="motor.motor_asyncio",
        category=ImportCategory.DATABASE,
        priority=ImportPriority.HIGH,
        description="Async Python driver for MongoDB",
        is_async=True
    ),
    "aiomysql": ImportDefinition(
        module_name="aiomysql",
        import_path="aiomysql",
        category=ImportCategory.DATABASE,
        priority=ImportPriority.HIGH,
        description="Async MySQL driver for Python",
        is_async=True
    ),
    "aiosqlite": ImportDefinition(
        module_name="aiosqlite",
        import_path="aiosqlite",
        category=ImportCategory.DATABASE,
        priority=ImportPriority.HIGH,
        description="Async SQLite driver for Python",
        is_async=True
    ),
    
    # Third Party - Medium Priority
    "pympler": ImportDefinition(
        module_name="pympler",
        import_path="pympler",
        category=ImportCategory.MONITORING,
        priority=ImportPriority.MEDIUM,
        description="Memory profiling and analysis",
        is_optional=True
    ),
    "objgraph": ImportDefinition(
        module_name="objgraph",
        import_path="objgraph",
        category=ImportCategory.MONITORING,
        priority=ImportPriority.MEDIUM,
        description="Memory profiling and object graph analysis",
        is_optional=True
    ),
    "orjson": ImportDefinition(
        module_name="orjson",
        import_path="orjson",
        category=ImportCategory.PERFORMANCE_OPTIMIZATION,
        priority=ImportPriority.MEDIUM,
        description="Fast, standards-compliant JSON library",
        is_optional=True
    ),
    "uvloop": ImportDefinition(
        module_name="uvloop",
        import_path="uvloop",
        category=ImportCategory.PERFORMANCE_OPTIMIZATION,
        priority=ImportPriority.MEDIUM,
        description="Fast implementation of asyncio event loop",
        is_optional=True
    ),
    "zlib": ImportDefinition(
        module_name="zlib",
        import_path="zlib",
        category=ImportCategory.PERFORMANCE_OPTIMIZATION,
        priority=ImportPriority.MEDIUM,
        description="Compression compatible with gzip"
    ),
    "lz4": ImportDefinition(
        module_name="lz4",
        import_path="lz4",
        category=ImportCategory.PERFORMANCE_OPTIMIZATION,
        priority=ImportPriority.LOW,
        description="LZ4 compression library",
        is_optional=True
    ),
    "brotli": ImportDefinition(
        module_name="brotli",
        import_path="brotli",
        category=ImportCategory.PERFORMANCE_OPTIMIZATION,
        priority=ImportPriority.LOW,
        description="Brotli compression library",
        is_optional=True
    ),
    "zstandard": ImportDefinition(
        module_name="zstandard",
        import_path="zstandard",
        category=ImportCategory.PERFORMANCE_OPTIMIZATION,
        priority=ImportPriority.LOW,
        description="Zstandard compression library",
        is_optional=True
    ),
    
    # AI/ML Libraries
    "torch": ImportDefinition(
        module_name="torch",
        import_path="torch",
        category=ImportCategory.AI_ML,
        priority=ImportPriority.MEDIUM,
        description="PyTorch deep learning framework",
        is_optional=True
    ),
    "transformers": ImportDefinition(
        module_name="transformers",
        import_path="transformers",
        category=ImportCategory.AI_ML,
        priority=ImportPriority.LOW,
        description="State-of-the-art Natural Language Processing",
        is_optional=True
    ),
    "diffusers": ImportDefinition(
        module_name="diffusers",
        import_path="diffusers",
        category=ImportCategory.AI_ML,
        priority=ImportPriority.LOW,
        description="State-of-the-art diffusion models",
        is_optional=True
    ),
    
    # Database and ORM
    "sqlalchemy": ImportDefinition(
        module_name="sqlalchemy",
        import_path="sqlalchemy",
        category=ImportCategory.DATABASE,
        priority=ImportPriority.MEDIUM,
        description="SQL toolkit and Object Relational Mapper",
        is_optional=True
    ),
    "redis": ImportDefinition(
        module_name="redis",
        import_path="redis",
        category=ImportCategory.DATABASE,
        priority=ImportPriority.MEDIUM,
        description="Redis Python client",
        is_optional=True
    ),
    "pymongo": ImportDefinition(
        module_name="pymongo",
        import_path="pymongo",
        category=ImportCategory.DATABASE,
        priority=ImportPriority.LOW,
        description="MongoDB driver for Python",
        is_optional=True
    ),
    
    # Monitoring and Metrics
    "prometheus_client": ImportDefinition(
        module_name="prometheus_client",
        import_path="prometheus_client",
        category=ImportCategory.MONITORING,
        priority=ImportPriority.LOW,
        description="Prometheus client library",
        is_optional=True
    ),
    "sentry_sdk": ImportDefinition(
        module_name="sentry_sdk",
        import_path="sentry_sdk",
        category=ImportCategory.MONITORING,
        priority=ImportPriority.LOW,
        description="Sentry SDK for Python",
        is_optional=True
    ),
    
    # Utilities
    "aiofiles": ImportDefinition(
        module_name="aiofiles",
        import_path="aiofiles",
        category=ImportCategory.UTILITIES,
        priority=ImportPriority.LOW,
        description="File support for asyncio",
        is_async=True,
        is_optional=True
    ),
    "python_multipart": ImportDefinition(
        module_name="python_multipart",
        import_path="python_multipart",
        category=ImportCategory.UTILITIES,
        priority=ImportPriority.LOW,
        description="Streaming multipart parser for Python",
        is_optional=True
    ),
}

# =============================================================================
# Import Manager
# =============================================================================

class UnifiedImportManager:
    """
    🚀 Unified Import Manager - Centralized import management.
    
    Provides consistent import patterns, dependency management, and
    fallback strategies across the entire codebase.
    """
    
    def __init__(self):
        self.imported_modules: Dict[str, Any] = {}
        self.import_results: Dict[str, ImportResult] = {}
        self.failed_imports: Set[str] = set()
        self.optional_imports: Set[str] = set()
        self.import_order: List[str] = []
        
        # Import all core modules
        self._import_core_modules()
    
    def _import_core_modules(self):
        """Import all core modules in priority order."""
        # Sort by priority
        priority_order = [
            ImportPriority.CRITICAL,
            ImportPriority.HIGH,
            ImportPriority.MEDIUM,
            ImportPriority.LOW,
            ImportPriority.EXPERIMENTAL
        ]
        
        for priority in priority_order:
            for module_name, definition in CORE_IMPORTS.items():
                if definition.priority == priority:
                    result = self.import_module(module_name)
                    if result.success:
                        self.import_order.append(module_name)
                    elif definition.is_optional:
                        self.optional_imports.add(module_name)
                    else:
                        self.failed_imports.add(module_name)
    
    def import_module(self, module_name: str) -> ImportResult:
        """Import a module with error handling and fallbacks."""
        if module_name in self.imported_modules:
            return ImportResult(
                module_name=module_name,
                success=True,
                imported_module=self.imported_modules[module_name],
                import_time_ms=0.0
            )
        
        import time
        start_time = time.time()
        
        try:
            # Get import definition
            definition = CORE_IMPORTS.get(module_name)
            if not definition:
                # Try direct import
                module = importlib.import_module(module_name)
                self.imported_modules[module_name] = module
                
                result = ImportResult(
                    module_name=module_name,
                    success=True,
                    imported_module=module,
                    import_time_ms=(time.time() - start_time) * 1000
                )
            else:
                # Use defined import path
                module = importlib.import_module(definition.import_path)
                self.imported_modules[module_name] = module
                
                result = ImportResult(
                    module_name=module_name,
                    success=True,
                    imported_module=module,
                    import_time_ms=(time.time() - start_time) * 1000
                )
            
            self.import_results[module_name] = result
            return result
            
        except ImportError as e:
            # Try alternative imports
            if definition and definition.alternative_imports:
                for alt_import in definition.alternative_imports:
                    try:
                        module = importlib.import_module(alt_import)
                        self.imported_modules[module_name] = module
                        
                        result = ImportResult(
                            module_name=module_name,
                            success=True,
                            imported_module=module,
                            import_time_ms=(time.time() - start_time) * 1000,
                            fallback_used=True
                        )
                        
                        self.import_results[module_name] = result
                        return result
                        
                    except ImportError:
                        continue
            
            # Import failed
            result = ImportResult(
                module_name=module_name,
                success=False,
                error_message=str(e),
                import_time_ms=(time.time() - start_time) * 1000
            )
            
            self.import_results[module_name] = result
            return result
        
        except Exception as e:
            # Other errors
            result = ImportResult(
                module_name=module_name,
                success=False,
                error_message=str(e),
                import_time_ms=(time.time() - start_time) * 1000
            )
            
            self.import_results[module_name] = result
            return result
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """Get an imported module."""
        return self.imported_modules.get(module_name)
    
    def is_module_available(self, module_name: str) -> bool:
        """Check if a module is available."""
        return module_name in self.imported_modules
    
    def get_import_status(self) -> Dict[str, Any]:
        """Get comprehensive import status."""
        total_imports = len(CORE_IMPORTS)
        successful_imports = len(self.imported_modules)
        failed_imports = len(self.failed_imports)
        optional_imports = len(self.optional_imports)
        
        return {
            "total_imports": total_imports,
            "successful_imports": successful_imports,
            "failed_imports": failed_imports,
            "optional_imports": optional_imports,
            "success_rate": (successful_imports / total_imports) * 100 if total_imports > 0 else 0,
            "import_order": self.import_order,
            "failed_modules": list(self.failed_imports),
            "optional_modules": list(self.optional_imports),
            "import_results": {
                name: {
                    "success": result.success,
                    "error": result.error_message,
                    "import_time_ms": result.import_time_ms,
                    "fallback_used": result.fallback_used
                }
                for name, result in self.import_results.items()
            }
        }
    
    def get_modules_by_category(self, category: ImportCategory) -> List[str]:
        """Get modules by category."""
        return [
            name for name, definition in CORE_IMPORTS.items()
            if definition.category == category and name in self.imported_modules
        ]
    
    def get_modules_by_priority(self, priority: ImportPriority) -> List[str]:
        """Get modules by priority."""
        return [
            name for name, definition in CORE_IMPORTS.items()
            if definition.priority == priority and name in self.imported_modules
        ]
    
    def validate_dependencies(self) -> Dict[str, bool]:
        """Validate that all critical dependencies are available."""
        validation_results = {}
        
        for module_name, definition in CORE_IMPORTS.items():
            if definition.priority == ImportPriority.CRITICAL:
                validation_results[module_name] = module_name in self.imported_modules
        
        return validation_results
    
    def get_missing_critical_dependencies(self) -> List[str]:
        """Get list of missing critical dependencies."""
        return [
            name for name, definition in CORE_IMPORTS.items()
            if definition.priority == ImportPriority.CRITICAL and name not in self.imported_modules
        ]
    
    def generate_import_statement(self, module_name: str, imports: List[str] = None) -> str:
        """Generate a proper import statement."""
        if not imports:
            imports = [module_name]
        
        definition = CORE_IMPORTS.get(module_name)
        if definition and definition.import_path != module_name:
            return f"from {definition.import_path} import {', '.join(imports)}"
        else:
            return f"import {', '.join(imports)}"
    
    def generate_requirements_txt(self) -> str:
        """Generate requirements.txt content."""
        requirements = []
        
        for module_name, definition in CORE_IMPORTS.items():
            if definition.priority in [ImportPriority.CRITICAL, ImportPriority.HIGH]:
                if definition.version_requirement:
                    requirements.append(f"{module_name}{definition.version_requirement}")
                else:
                    requirements.append(module_name)
        
        return "\n".join(sorted(requirements))
    
    def cleanup(self):
        """Clean up imported modules."""
        self.imported_modules.clear()
        self.import_results.clear()
        self.failed_imports.clear()
        self.optional_imports.clear()
        self.import_order.clear()

# =============================================================================
# Global Instance and Utilities
# =============================================================================

# Global import manager instance
_import_manager: Optional[UnifiedImportManager] = None

def get_import_manager() -> UnifiedImportManager:
    """Get or create global import manager instance."""
    global _import_manager
    if _import_manager is None:
        _import_manager = UnifiedImportManager()
    return _import_manager

def import_module(module_name: str) -> ImportResult:
    """Import module using global manager."""
    return get_import_manager().import_module(module_name)

def get_module(module_name: str) -> Optional[Any]:
    """Get module from global manager."""
    return get_import_manager().get_module(module_name)

def is_module_available(module_name: str) -> bool:
    """Check if module is available in global manager."""
    return get_import_manager().is_module_available(module_name)

def get_import_status() -> Dict[str, Any]:
    """Get import status from global manager."""
    return get_import_manager().get_import_status()

def validate_dependencies() -> Dict[str, bool]:
    """Validate dependencies using global manager."""
    return get_import_manager().validate_dependencies()

# =============================================================================
# Convenience Functions
# =============================================================================

def safe_import(module_name: str, default_value: Any = None) -> Any:
    """Safely import a module with a default fallback."""
    try:
        return get_module(module_name) or default_value
    except Exception:
        return default_value

def conditional_import(module_name: str, condition: bool = True) -> Optional[Any]:
    """Conditionally import a module."""
    if condition:
        return get_module(module_name)
    return None

def lazy_import(module_name: str) -> Callable[[], Any]:
    """Create a lazy import function."""
    def _lazy_import():
        return get_module(module_name)
    return _lazy_import

# =============================================================================
# Example Usage
# =============================================================================

def example_usage():
    """Example of how to use the unified import manager."""
    
    # Get import manager
    manager = get_import_manager()
    
    # Check import status
    status = manager.get_import_status()
    print(f"Import Status: {status['success_rate']:.1f}% success rate")
    
    # Get modules by category
    web_framework_modules = manager.get_modules_by_category(ImportCategory.WEB_FRAMEWORK)
    print(f"Web Framework Modules: {web_framework_modules}")
    
    # Get modules by priority
    critical_modules = manager.get_modules_by_priority(ImportPriority.CRITICAL)
    print(f"Critical Modules: {critical_modules}")
    
    # Validate dependencies
    validation = manager.validate_dependencies()
    missing_critical = manager.get_missing_critical_dependencies()
    
    if missing_critical:
        print(f"Missing Critical Dependencies: {missing_critical}")
    else:
        print("All critical dependencies are available")
    
    # Generate requirements.txt
    requirements = manager.generate_requirements_txt()
    print("Requirements.txt content:")
    print(requirements)
    
    # Use safe import
    numpy = safe_import("numpy")
    if numpy:
        print("NumPy is available")
    else:
        print("NumPy is not available")
    
    # Use conditional import
    torch = conditional_import("torch", condition=True)
    if torch:
        print("PyTorch is available")
    
    # Use lazy import
    lazy_torch = lazy_import("torch")
    # torch_module = lazy_torch()  # Only imported when called

if __name__ == "__main__":
    # Run example
    example_usage()
