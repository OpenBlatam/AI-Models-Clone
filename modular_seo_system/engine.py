"""
Main SEO Engine - Orchestrates all modular components
Provides a unified interface for SEO analysis
"""

import asyncio
import hashlib
import time
from typing import Any, Dict, List, Optional

from .core.component_registry import component_registry
from .core.interfaces import TextProcessor, CacheProvider, MetricsProvider
from .processors.seo_analyzer import SEOAnalyzer
from .cache.memory_cache import MemoryCache


class SEOEngine:
    """Main SEO engine that orchestrates all modular components."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._initialized = False
        self._components_initialized = False

        # Component references
        self._processors: List[TextProcessor] = []
        self._caches: List[CacheProvider] = []
        self._metrics: Optional[MetricsProvider] = None

        # Processing pipeline
        self._processing_pipeline: List[str] = []

        # Configuration defaults
        self._default_config = {
            "enable_caching": True,
            "enable_metrics": True,
            "enable_async": True,
            "batch_size": 8,
            "max_concurrent": 10,
            "cache_strategy": "lru",
            "cache_size": 1000,
            "cache_ttl": 3600,
        }

        # Update with provided config
        self._default_config.update(self.config)

    async def initialize(self) -> bool:
        """Initialize the SEO engine and all components."""
        try:
            print("🚀 Initializing Modular SEO Engine...")

            # Initialize components
            await self._initialize_components()

            # Setup processing pipeline
            self._setup_processing_pipeline()

            # Register with component registry
            component_registry.register(self, "engine")

            self._initialized = True
            print("✅ SEO Engine initialized successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize SEO engine: {e}")
            return False

    async def shutdown(self) -> bool:
        """Shutdown the SEO engine and all components."""
        try:
            print("🔄 Shutting down SEO Engine...")

            # Unregister from component registry
            component_registry.unregister(self.name)

            # Shutdown all components
            await component_registry.shutdown_all()

            self._initialized = False
            print("✅ SEO Engine shutdown successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to shutdown SEO engine: {e}")
            return False

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using the processing pipeline."""
        if not self._initialized:
            raise RuntimeError("SEO Engine not initialized. Call initialize() first.")

        start_time = time.time()

        try:
            # Check cache first
            if self._default_config["enable_caching"]:
                cached_result = await self._get_from_cache(text)
                if cached_result:
                    return cached_result

            # Process text through pipeline
            result = await self._process_text_pipeline(text)

            # Cache result
            if self._default_config["enable_caching"]:
                await self._store_in_cache(text, result)

            # Record metrics
            if self._metrics:
                processing_time = time.time() - start_time
                self._metrics.record_timing("text_analysis", processing_time)
                self._metrics.increment_counter("texts_processed")

            result["processing_time"] = time.time() - start_time
            result["timestamp"] = start_time
            result["engine_version"] = "2.0.0"

            return result

        except Exception as e:
            # Record error metrics
            if self._metrics:
                self._metrics.increment_counter("analysis_errors")

            raise

    async def analyze_texts_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts in batch."""
        if not self._initialized:
            raise RuntimeError("SEO Engine not initialized. Call initialize() first.")

        if not texts:
            return []

        # Process in batches
        batch_size = self._default_config["batch_size"]
        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            # Process batch concurrently
            batch_results = await asyncio.gather(*[self.analyze_text(text) for text in batch], return_exceptions=True)

            # Handle results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results.append(
                        {
                            "error": str(result),
                            "index": i + j,
                            "text_preview": batch[j][:100] + "..." if len(batch[j]) > 100 else batch[j],
                        }
                    )
                else:
                    results.append(result)

        return results

    async def analyze_texts_streaming(self, texts: List[str]):
        """Analyze texts with streaming results."""
        if not self._initialized:
            raise RuntimeError("SEO Engine not initialized. Call initialize() first.")

        for i, text in enumerate(texts):
            try:
                result = await self.analyze_text(text)
                yield {"index": i, "result": result}
            except Exception as e:
                yield {"index": i, "error": str(e)}

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        if not self._initialized:
            return {"status": "not_initialized"}

        # Get component health
        component_health = await component_registry.health_check_all()

        # Get component metadata
        components = component_registry.get_all_components()
        component_metadata = {name: component.get_metadata() for name, component in components.items()}

        # Get system metrics
        system_metrics = {}
        if self._metrics:
            system_metrics = await self._metrics.get_stats()

        return {
            "status": "running",
            "initialized": self._initialized,
            "components_health": component_health,
            "components_metadata": component_metadata,
            "system_metrics": system_metrics,
            "processing_pipeline": self._processing_pipeline,
            "configuration": self._default_config.copy(),
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        if not self._metrics:
            return {"error": "Metrics not available"}

        return await self._metrics.get_stats()

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the engine."""
        self._default_config.update(config)

        # Apply configuration to components
        if self._components_initialized:
            asyncio.create_task(self._apply_configuration())

    async def _initialize_components(self) -> bool:
        """Initialize all system components."""
        try:
            print("  📦 Initializing components...")

            # Initialize SEO Analyzer
            seo_analyzer = SEOAnalyzer()
            await seo_analyzer.initialize()
            self._processors.append(seo_analyzer)

            # Initialize Memory Cache
            if self._default_config["enable_caching"]:
                memory_cache = MemoryCache()
                memory_cache.configure(
                    {
                        "strategy": self._default_config["cache_strategy"],
                        "max_size": self._default_config["cache_size"],
                        "ttl": self._default_config["cache_ttl"],
                    }
                )
                await memory_cache.initialize()
                self._caches.append(memory_cache)

            # Initialize Metrics (placeholder for now)
            if self._default_config["enable_metrics"]:
                # This would be a real metrics provider
                self._metrics = None

            self._components_initialized = True
            print("  ✅ Components initialized successfully!")
            return True

        except Exception as e:
            print(f"  ❌ Failed to initialize components: {e}")
            return False

    def _setup_processing_pipeline(self) -> None:
        """Setup the text processing pipeline."""
        self._processing_pipeline = ["seo_analysis"]

        # Add additional processors if available
        for processor in self._processors:
            capabilities = processor.get_capabilities()
            self._processing_pipeline.extend(capabilities)

        # Remove duplicates
        self._processing_pipeline = list(dict.fromkeys(self._processing_pipeline))

    async def _process_text_pipeline(self, text: str) -> Dict[str, Any]:
        """Process text through the processing pipeline."""
        # For now, use the SEO analyzer directly
        # In a more complex system, this would route through multiple processors

        if not self._processors:
            raise RuntimeError("No processors available")

        # Use the first processor (SEO analyzer)
        processor = self._processors[0]
        return await processor.process(text)

    async def _get_from_cache(self, text: str) -> Optional[Dict[str, Any]]:
        """Get result from cache."""
        if not self._caches:
            return None

        cache_key = self._generate_cache_key(text)

        for cache in self._caches:
            try:
                result = await cache.get(cache_key)
                if result:
                    return result
            except Exception:
                continue

        return None

    async def _store_in_cache(self, text: str, result: Dict[str, Any]) -> None:
        """Store result in cache."""
        if not self._caches:
            return

        cache_key = self._generate_cache_key(text)

        for cache in self._caches:
            try:
                await cache.set(cache_key, result)
                break  # Store in first available cache
            except Exception:
                continue

    def _generate_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()

    async def _apply_configuration(self) -> None:
        """Apply configuration to components."""
        # This would update component configurations
        pass

    @property
    def name(self) -> str:
        """Get engine name."""
        return "modular_seo_engine"

    @property
    def version(self) -> str:
        """Get engine version."""
        return "2.0.0"

    async def health_check(self) -> bool:
        """Check engine health."""
        if not self._initialized:
            return False

        # Check component health
        component_health = await component_registry.health_check_all()
        return all(component_health.values())

    def get_status(self) -> Dict[str, Any]:
        """Get engine status."""
        return {
            "name": self.name,
            "version": self.version,
            "initialized": self._initialized,
            "components_initialized": self._components_initialized,
            "processors_count": len(self._processors),
            "caches_count": len(self._caches),
            "metrics_available": self._metrics is not None,
        }
