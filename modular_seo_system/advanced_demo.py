#!/usr/bin/env python3
"""
Advanced Modular SEO System - Comprehensive Demo
Showcases the completely refactored architecture with:
- Plugin System
- Event System  
- Middleware Pipeline
- Advanced Configuration
- Component Registry
"""

import asyncio
import json
import time
from typing import List, Dict, Any

from .core import (
    SEOEngine,
    plugin_manager,
    event_bus,
    middleware_registry,
    config_manager,
    Event,
    EventPriority,
    MiddlewarePriority,
    MiddlewareType,
    ConfigSchema,
)
from .core.configuration import MemoryConfigBackend, FileConfigBackend
from .core.middleware import (
    LoggingMiddleware,
    ValidationMiddleware,
    TransformationMiddleware,
    ErrorHandlingMiddleware,
    MonitoringMiddleware,
)
from .processors.seo_analyzer import SEOAnalyzer
from .cache.memory_cache import MemoryCache


class AdvancedSEODemo:
    """Advanced demo showcasing the refactored modular SEO system."""

    def __init__(self):
        self.engine: SEOEngine = None
        self.demo_texts = [
            "This is a comprehensive sample text for advanced SEO analysis. It contains multiple sentences with proper structure and should provide excellent insights for optimization. The content is well-organized with relevant keywords and follows best practices for search engine optimization.",
            "Digital marketing strategies require sophisticated SEO analysis and continuous optimization. Content optimization involves advanced keyword research, readability improvements, structural enhancements, and performance monitoring. Successful campaigns depend on data-driven decisions and real-time analytics.",
            "Artificial intelligence and machine learning are transforming how we approach content creation and optimization. Advanced algorithms analyze user behavior patterns, search intent, and content performance to provide personalized recommendations and improved engagement metrics.",
        ]

        # Demo configuration
        self.demo_config = {
            "analysis": {
                "enable_all_strategies": True,
                "min_word_count": 200,
                "max_sentence_length": 25,
                "min_sentences": 3,
                "min_keywords": 3,
            },
            "performance": {
                "enable_caching": True,
                "cache_size": 500,
                "cache_ttl": 1800,
                "enable_async": True,
                "max_concurrent": 5,
            },
            "monitoring": {"enable_metrics": True, "enable_logging": True, "log_level": "INFO"},
        }

    async def run_advanced_demo(self):
        """Run the complete advanced demo."""
        print("🚀 ADVANCED MODULAR SEO SYSTEM - COMPREHENSIVE DEMO")
        print("=" * 80)
        print("Showcasing the completely refactored architecture with advanced features")
        print("=" * 80)

        try:
            # Initialize advanced systems
            await self._demo_system_initialization()

            # Demo plugin system
            await self._demo_plugin_system()

            # Demo event system
            await self._demo_event_system()

            # Demo middleware pipeline
            await self._demo_middleware_pipeline()

            # Demo advanced configuration
            await self._demo_advanced_configuration()

            # Demo component integration
            await self._demo_component_integration()

            # Demo performance and monitoring
            await self._demo_performance_monitoring()

            # Demo advanced features
            await self._demo_advanced_features()

            # Cleanup
            await self._demo_cleanup()

        except Exception as e:
            print(f"❌ Advanced demo failed: {e}")
            await self._cleanup()

    async def _demo_system_initialization(self):
        """Demo system initialization with advanced features."""
        print("\n🔧 SYSTEM INITIALIZATION")
        print("-" * 40)

        # Initialize configuration system
        print("📋 Setting up advanced configuration system...")

        # Add configuration backends
        memory_backend = MemoryConfigBackend("demo_memory")
        config_manager.add_backend(memory_backend)

        # Add configuration schema
        seo_schema = ConfigSchema(
            properties={
                "analysis": {"type": "object"},
                "performance": {"type": "object"},
                "monitoring": {"type": "object"},
            },
            required=["analysis", "performance"],
        )
        config_manager.add_schema("seo", seo_schema)

        # Load demo configuration
        await config_manager.save_config(self.demo_config, "demo_memory")
        print("✅ Configuration system initialized")

        # Initialize event system
        print("📡 Starting event system...")
        await event_bus.start()
        print("✅ Event system started")

        # Initialize middleware registry
        print("🔗 Setting up middleware registry...")
        self._setup_middleware()
        print("✅ Middleware registry configured")

        # Initialize plugin manager
        print("🔌 Setting up plugin manager...")
        await self._setup_plugins()
        print("✅ Plugin manager configured")

        # Initialize SEO engine
        print("🚀 Initializing advanced SEO engine...")
        self.engine = SEOEngine(self.demo_config)
        await self.engine.initialize()
        print("✅ Advanced SEO engine initialized")

        print("🎉 All systems initialized successfully!")

    def _setup_middleware(self):
        """Setup middleware components."""
        # Register common middleware
        logging_middleware = LoggingMiddleware("demo_logging", "DEBUG")
        validation_middleware = ValidationMiddleware("demo_validation")
        transformation_middleware = TransformationMiddleware("demo_transformation")
        error_middleware = ErrorHandlingMiddleware("demo_error_handling")
        monitoring_middleware = MonitoringMiddleware("demo_monitoring")

        middleware_registry.register_middleware(logging_middleware)
        middleware_registry.register_middleware(validation_middleware)
        middleware_registry.register_middleware(transformation_middleware)
        middleware_registry.register_middleware(error_middleware)
        middleware_registry.register_middleware(monitoring_middleware)

        # Create analysis pipeline
        analysis_pipeline = middleware_registry.create_pipeline(
            "seo_analysis", "demo_logging", "demo_validation", "demo_transformation", "demo_monitoring"
        )

        # Create error handling pipeline
        error_pipeline = middleware_registry.create_pipeline(
            "error_handling", "demo_logging", "demo_error_handling", "demo_monitoring"
        )

    async def _setup_plugins(self):
        """Setup plugin system."""
        # Create demo plugin directories
        plugin_dirs = ["demo_plugins"]
        plugin_manager.plugin_directories = plugin_dirs

        # Discover plugins
        discovered_plugins = await plugin_manager.discover_plugins()
        print(f"🔍 Discovered {len(discovered_plugins)} plugins")

        # Add plugin lifecycle hooks
        plugin_manager.add_hook("post_load", self._on_plugin_loaded)
        plugin_manager.add_hook("pre_unload", self._on_plugin_unloading)

    async def _demo_plugin_system(self):
        """Demo the plugin system capabilities."""
        print("\n🔌 PLUGIN SYSTEM DEMO")
        print("-" * 40)

        # List available plugins
        plugins = await plugin_manager.list_plugins()
        print(f"📋 Available plugins: {len(plugins)}")

        # Show plugin discovery
        discovered = await plugin_manager.discover_plugins()
        print(f"🔍 Discovered plugins: {len(discovered)}")

        # Demo plugin health checking
        if plugins:
            health_status = await plugin_manager.health_check_all()
            print(f"🏥 Plugin health status: {health_status}")

        print("✅ Plugin system demo completed")

    async def _demo_event_system(self):
        """Demo the event system capabilities."""
        print("\n📡 EVENT SYSTEM DEMO")
        print("-" * 40)

        # Subscribe to events
        subscription = event_bus.subscribe("seo_analysis_completed", self._on_analysis_completed)
        global_subscription = event_bus.subscribe_global(self._on_any_event)

        # Publish demo events
        demo_event = Event(
            name="demo_event",
            source="advanced_demo",
            priority=EventPriority.HIGH,
            data={"message": "Hello from advanced demo!"},
            metadata={"demo": True},
        )

        await event_bus.publish(demo_event)

        # Wait for event processing
        await asyncio.sleep(0.1)

        # Get event statistics
        stats = event_bus.get_stats()
        print(f"📊 Event system stats: {stats['events_published']} events published")

        # Unsubscribe
        event_bus.unsubscribe(subscription)
        event_bus.unsubscribe(global_subscription)

        print("✅ Event system demo completed")

    async def _demo_middleware_pipeline(self):
        """Demo the middleware pipeline capabilities."""
        print("\n🔗 MIDDLEWARE PIPELINE DEMO")
        print("-" * 40)

        # Get available pipelines
        pipelines = middleware_registry.list_pipelines()
        print(f"📋 Available pipelines: {pipelines}")

        # Demo pipeline execution
        if "seo_analysis" in pipelines:
            pipeline = middleware_registry.get_pipeline("seo_analysis")

            # Execute pipeline with demo data
            demo_data = {"text": "Sample text for middleware processing", "metadata": {"demo": True}}
            result = await pipeline.execute(demo_data, {"pipeline": "demo"})

            print(f"🔄 Pipeline execution result: {type(result).__name__}")

            # Get pipeline statistics
            pipeline_stats = pipeline.get_pipeline_stats()
            print(f"📊 Pipeline stats: {pipeline_stats['middleware_count']} middleware components")

        # Show middleware registry stats
        registry_stats = {
            "middleware_count": len(middleware_registry.list_middleware()),
            "pipeline_count": len(middleware_registry.list_pipelines()),
        }
        print(f"🔗 Middleware registry: {registry_stats}")

        print("✅ Middleware pipeline demo completed")

    async def _demo_advanced_configuration(self):
        """Demo the advanced configuration system."""
        print("\n⚙️ ADVANCED CONFIGURATION DEMO")
        print("-" * 40)

        # Show configuration backends
        config_stats = config_manager.get_stats()
        print(f"📋 Configuration backends: {config_stats['backends']}")

        # Demo configuration watching
        await config_manager.watch_config(self._on_config_changed)
        print("👀 Configuration watching enabled")

        # Demo configuration changes
        new_config = self.demo_config.copy()
        new_config["analysis"]["min_word_count"] = 250

        await config_manager.save_config(new_config, "demo_memory")
        print("💾 Configuration updated")

        # Wait for change notification
        await asyncio.sleep(0.1)

        # Export configuration
        yaml_config = await config_manager.export_config("yaml")
        print(f"📄 Configuration exported (YAML): {len(yaml_config)} characters")

        # Reload configuration
        reloaded_config = await config_manager.reload_config()
        print(f"🔄 Configuration reloaded: {len(reloaded_config)} keys")

        print("✅ Advanced configuration demo completed")

    async def _demo_component_integration(self):
        """Demo component integration and orchestration."""
        print("\n🧩 COMPONENT INTEGRATION DEMO")
        print("-" * 40)

        # Show component registry
        from .core.interfaces import component_registry

        all_components = component_registry.get_all_components()
        print(f"📋 Registered components: {len(all_components)}")

        # Show component types
        component_types = component_registry.get_component_types()
        print(f"🔧 Component types: {component_types}")

        # Demo component health check
        health_status = await component_registry.health_check_all()
        print(f"🏥 Component health: {health_status}")

        # Demo SEO analysis with integrated components
        if self.engine:
            print("🔍 Performing integrated SEO analysis...")

            # Single text analysis
            result = await self.engine.analyze_text(self.demo_texts[0])
            print(f"📊 Analysis result: {len(result)} metrics")

            # Batch analysis
            batch_results = await self.engine.analyze_texts_batch(self.demo_texts)
            print(f"📦 Batch analysis: {len(batch_results)} results")

        print("✅ Component integration demo completed")

    async def _demo_performance_monitoring(self):
        """Demo performance monitoring and metrics."""
        print("\n📊 PERFORMANCE MONITORING DEMO")
        print("-" * 40)

        # Get system status
        if self.engine:
            system_status = await self.engine.get_system_status()
            print(f"🖥️ System status: {system_status['status']}")

            # Get metrics
            metrics = await self.engine.get_metrics()
            print(f"📈 System metrics: {len(metrics)} collected")

        # Get event system stats
        event_stats = event_bus.get_stats()
        print(f"📡 Event system performance: {event_stats['handlers_executed']} handlers executed")

        # Get middleware stats
        if "seo_analysis" in middleware_registry.list_pipelines():
            pipeline = middleware_registry.get_pipeline("seo_analysis")
            pipeline_stats = pipeline.get_pipeline_stats()
            print(f"🔗 Middleware performance: {pipeline_stats['middleware_count']} components")

        # Get configuration stats
        config_stats = config_manager.get_stats()
        print(f"⚙️ Configuration performance: avg load time {config_stats['avg_load_time']:.4f}s")

        print("✅ Performance monitoring demo completed")

    async def _demo_advanced_features(self):
        """Demo advanced features and capabilities."""
        print("\n🚀 ADVANCED FEATURES DEMO")
        print("-" * 40)

        # Demo streaming analysis
        if self.engine:
            print("🌊 Demo streaming analysis...")

            async def process_stream_result(result):
                print(f"📊 Stream result: {result['seo_score']:.2f}")

            await self.engine.analyze_texts_streaming(self.demo_texts, callback=process_stream_result)

        # Demo dynamic configuration
        print("⚙️ Demo dynamic configuration...")
        await config_manager.set_config("demo_feature", True)
        current_config = await config_manager.get_config("demo_feature")
        print(f"💡 Dynamic config value: {current_config}")

        # Demo event filtering
        print("🔍 Demo event filtering...")
        filtered_subscription = event_bus.subscribe(
            "demo_event", self._on_filtered_event, filters={"source": "advanced_demo"}
        )

        # Publish filtered event
        filtered_event = Event(name="demo_event", source="advanced_demo", data={"filtered": True})
        await event_bus.publish(filtered_event)

        # Wait and cleanup
        await asyncio.sleep(0.1)
        event_bus.unsubscribe(filtered_subscription)

        print("✅ Advanced features demo completed")

    async def _demo_cleanup(self):
        """Demo cleanup and shutdown."""
        print("\n🧹 DEMO CLEANUP")
        print("-" * 40)

        # Stop event system
        await event_bus.stop()
        print("📡 Event system stopped")

        # Shutdown engine
        if self.engine:
            await self.engine.shutdown()
            print("🚀 SEO engine shutdown")

        # Shutdown plugin manager
        await plugin_manager.shutdown()
        print("🔌 Plugin manager shutdown")

        # Clear middleware registry
        for pipeline_name in middleware_registry.list_pipelines():
            middleware_registry.remove_pipeline(pipeline_name)
        print("🔗 Middleware pipelines cleared")

        print("✅ Cleanup completed")

    async def _cleanup(self):
        """Emergency cleanup."""
        try:
            await self._demo_cleanup()
        except Exception as e:
            print(f"⚠️ Emergency cleanup error: {e}")

    # Event handlers
    async def _on_analysis_completed(self, event: Event):
        """Handle SEO analysis completion events."""
        print(f"🎯 Analysis completed: {event.data.get('text', 'Unknown')[:50]}...")

    async def _on_any_event(self, event: Event):
        """Handle any event (global subscription)."""
        print(f"📡 Global event: {event.name} from {event.source}")

    async def _on_filtered_event(self, event: Event):
        """Handle filtered events."""
        print(f"🔍 Filtered event: {event.name} with data: {event.data}")

    async def _on_config_changed(self, config: Dict[str, Any]):
        """Handle configuration changes."""
        print(f"⚙️ Configuration changed: {len(config)} keys")

    async def _on_plugin_loaded(self, plugin_info):
        """Handle plugin loading."""
        print(f"🔌 Plugin loaded: {plugin_info.name} v{plugin_info.version}")

    async def _on_plugin_unloading(self, plugin_info):
        """Handle plugin unloading."""
        print(f"🔌 Plugin unloading: {plugin_info.name}")


async def main():
    """Main demo function."""
    demo = AdvancedSEODemo()
    await demo.run_advanced_demo()


if __name__ == "__main__":
    asyncio.run(main())
