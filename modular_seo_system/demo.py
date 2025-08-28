#!/usr/bin/env python3
"""
Modular SEO System - Comprehensive Demo
Showcases the completely modular architecture and capabilities
"""

import asyncio
import json
import time
from typing import List

from .engine import SEOEngine


class ModularSEODemo:
    """Demo class for showcasing the modular SEO system."""

    def __init__(self):
        self.engine: SEOEngine = None
        self.demo_texts = [
            "This is a sample text for SEO analysis. It contains multiple sentences and should provide good insights for optimization. The content is structured with proper paragraphs and includes relevant keywords for search engine optimization.",
            "Digital marketing strategies require comprehensive SEO analysis. Content optimization involves keyword research, readability improvements, and structural enhancements. Successful campaigns depend on data-driven decisions and continuous monitoring.",
            "Artificial intelligence transforms how we approach content creation. Machine learning algorithms analyze user behavior patterns and optimize content accordingly. This technology enables personalized experiences and improved engagement metrics.",
        ]

    async def run_demo(self):
        """Run the complete demo."""
        print("🚀 MODULAR SEO SYSTEM - COMPREHENSIVE DEMO")
        print("=" * 60)

        try:
            # Initialize system
            await self._demo_initialization()

            # Demo single text analysis
            await self._demo_single_analysis()

            # Demo batch processing
            await self._demo_batch_processing()

            # Demo streaming
            await self._demo_streaming()

            # Demo system status
            await self._demo_system_status()

            # Demo configuration changes
            await self._demo_configuration()

            # Demo component health
            await self._demo_component_health()

            # Cleanup
            await self._demo_cleanup()

        except Exception as e:
            print(f"❌ Demo failed: {e}")
            await self._cleanup()

    async def _demo_initialization(self):
        """Demo system initialization."""
        print("\n📦 1. SYSTEM INITIALIZATION")
        print("-" * 40)

        # Create engine with custom configuration
        config = {
            "enable_caching": True,
            "enable_metrics": True,
            "batch_size": 4,
            "cache_strategy": "lru",
            "cache_size": 500,
            "cache_ttl": 1800,
        }

        print(f"Configuration: {json.dumps(config, indent=2)}")

        self.engine = SEOEngine(config)

        # Initialize
        print("Initializing engine...")
        success = await self.engine.initialize()

        if success:
            print("✅ Engine initialized successfully!")

            # Show status
            status = self.engine.get_status()
            print(f"Engine Status: {json.dumps(status, indent=2)}")
        else:
            raise RuntimeError("Failed to initialize engine")

    async def _demo_single_analysis(self):
        """Demo single text analysis."""
        print("\n🔍 2. SINGLE TEXT ANALYSIS")
        print("-" * 40)

        text = self.demo_texts[0]
        print(f"Analyzing text: {text[:100]}...")

        start_time = time.time()
        result = await self.engine.analyze_text(text)
        processing_time = time.time() - start_time

        print(f"✅ Analysis completed in {processing_time:.3f}s")
        print(f"SEO Score: {result.get('seo_score', 'N/A')}")
        print(f"Word Count: {result.get('word_count', 'N/A')}")
        print(f"Readability: {result.get('complexity_level', 'N/A')}")

        # Show full result structure
        print("\nFull Analysis Result:")
        print(json.dumps(result, indent=2))

    async def _demo_batch_processing(self):
        """Demo batch text processing."""
        print("\n📦 3. BATCH PROCESSING")
        print("-" * 40)

        print(f"Processing {len(self.demo_texts)} texts in batch...")

        start_time = time.time()
        results = await self.engine.analyze_texts_batch(self.demo_texts)
        total_time = time.time() - start_time

        print(f"✅ Batch processing completed in {total_time:.3f}s")

        # Show summary
        successful = [r for r in results if "error" not in r]
        failed = [r for r in results if "error" in r]

        print(f"Successful analyses: {len(successful)}")
        print(f"Failed analyses: {len(failed)}")

        if successful:
            avg_seo_score = sum(r.get("seo_score", 0) for r in successful) / len(successful)
            print(f"Average SEO Score: {avg_seo_score:.1f}")

        # Show first result as example
        if successful:
            print("\nFirst Result Example:")
            first_result = successful[0]
            print(f"SEO Score: {first_result.get('seo_score', 'N/A')}")
            print(f"Processing Time: {first_result.get('processing_time', 'N/A'):.3f}s")

    async def _demo_streaming(self):
        """Demo streaming text processing."""
        print("\n🌊 4. STREAMING PROCESSING")
        print("-" * 40)

        print("Processing texts with streaming results...")

        start_time = time.time()
        results = []

        async for result in self.engine.analyze_texts_streaming(self.demo_texts):
            if "error" in result:
                print(f"❌ Text {result['index']}: {result['error']}")
            else:
                print(f"✅ Text {result['index']}: SEO Score {result['result'].get('seo_score', 'N/A')}")
                results.append(result)

        total_time = time.time() - start_time
        print(f"✅ Streaming completed in {total_time:.3f}s")
        print(f"Processed {len(results)} texts successfully")

    async def _demo_system_status(self):
        """Demo system status and monitoring."""
        print("\n📊 5. SYSTEM STATUS & MONITORING")
        print("-" * 40)

        # Get system status
        status = await self.engine.get_system_status()

        print("System Status:")
        print(f"  Status: {status.get('status', 'N/A')}")
        print(f"  Initialized: {status.get('initialized', False)}")
        print(f"  Processing Pipeline: {', '.join(status.get('processing_pipeline', []))}")

        # Show component health
        component_health = status.get("components_health", {})
        print(f"\nComponent Health:")
        for component, healthy in component_health.items():
            status_icon = "✅" if healthy else "❌"
            print(f"  {status_icon} {component}")

        # Show configuration
        config = status.get("configuration", {})
        print(f"\nCurrent Configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")

    async def _demo_configuration(self):
        """Demo dynamic configuration changes."""
        print("\n⚙️  6. DYNAMIC CONFIGURATION")
        print("-" * 40)

        print("Updating configuration...")

        # Change configuration
        new_config = {"batch_size": 2, "cache_size": 200, "cache_ttl": 900}

        self.engine.configure(new_config)
        print(f"Applied new configuration: {json.dumps(new_config, indent=2)}")

        # Show updated status
        status = self.engine.get_status()
        print(f"Updated batch size: {status.get('batch_size', 'N/A')}")

        # Test with new configuration
        print("\nTesting with new configuration...")
        test_texts = self.demo_texts[:2]
        results = await self.engine.analyze_texts_batch(test_texts)

        successful = [r for r in results if "error" not in r]
        print(f"✅ Processed {len(successful)} texts with new config")

    async def _demo_component_health(self):
        """Demo component health monitoring."""
        print("\n🏥 7. COMPONENT HEALTH MONITORING")
        print("-" * 40)

        # Check overall health
        health_status = await self.engine.health_check()
        print(f"Overall System Health: {'✅ Healthy' if health_status else '❌ Unhealthy'}")

        # Get detailed component status
        status = await self.engine.get_system_status()
        components = status.get("components_metadata", {})

        print(f"\nComponent Details:")
        for name, metadata in components.items():
            print(f"\n  📦 {name}:")
            print(f"    Version: {metadata.get('version', 'N/A')}")
            print(f"    Type: {metadata.get('type', 'N/A')}")

            if "capabilities" in metadata:
                caps = metadata["capabilities"]
                print(f"    Capabilities: {', '.join(caps)}")

            if "configuration" in metadata:
                config = metadata["configuration"]
                print(f"    Strategy: {config.get('strategy', 'N/A')}")
                print(f"    Max Size: {config.get('max_size', 'N/A')}")

    async def _demo_cleanup(self):
        """Demo system cleanup."""
        print("\n🧹 8. SYSTEM CLEANUP")
        print("-" * 40)

        print("Shutting down system...")
        await self._cleanup()
        print("✅ Demo completed successfully!")

    async def _cleanup(self):
        """Cleanup system resources."""
        if self.engine:
            await self.engine.shutdown()


async def main():
    """Main demo function."""
    demo = ModularSEODemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
