#!/usr/bin/env python3
"""
🎯 DEVIN CLEAN ARCHITECTURE DEMO
=================================

Demo script showcasing the clean architecture implementation:
- Domain Layer (Core Business Logic)
- Application Layer (Use Cases)
- Infrastructure Layer (External Concerns)
- Presentation Layer (API Controllers)
- Dependency Injection
- SOLID Principles
"""

import asyncio
import time
from typing import Dict, Any

# Import our clean architecture components
from devin_clean_architecture import (
    CopywritingRequest, CopywritingStyle, CopywritingTone,
    GenerateCopywritingUseCase, InMemoryRepository,
    DevinAIService, InMemoryCacheService, AsyncEventPublisher,
    ServiceContainer
)

class CleanArchitectureDemo:
    """Demo class for clean architecture"""
    
    def __init__(self):
        self.container = ServiceContainer()
        self.demo_results = []
    
    async def run_demo(self):
        """Run the complete demo"""
        print("🏗️ DEVIN CLEAN ARCHITECTURE DEMO")
        print("=" * 50)
        
        # Demo 1: Basic copywriting generation
        await self.demo_basic_generation()
        
        # Demo 2: Different styles and tones
        await self.demo_style_variations()
        
        # Demo 3: Caching demonstration
        await self.demo_caching()
        
        # Demo 4: Event publishing
        await self.demo_events()
        
        # Demo 5: Performance comparison
        await self.demo_performance()
        
        # Show results
        self.show_results()
    
    async def demo_basic_generation(self):
        """Demo basic copywriting generation"""
        print("\n📝 Demo 1: Basic Copywriting Generation")
        print("-" * 40)
        
        request = CopywritingRequest(
            prompt="Create a compelling product description for a new smartphone",
            style=CopywritingStyle.PROFESSIONAL,
            tone=CopywritingTone.ENTHUSIASTIC,
            length=150,
            creativity=0.8,
            target_audience="Tech enthusiasts",
            keywords=["smartphone", "innovation", "performance"]
        )
        
        start_time = time.time()
        response = await self.container.generate_use_case.execute(request)
        processing_time = time.time() - start_time
        
        print(f"✅ Generated content in {processing_time:.3f}s")
        print(f"📊 Confidence: {response.confidence_score}")
        print(f"📝 Content: {response.generated_text[:200]}...")
        
        self.demo_results.append({
            "demo": "Basic Generation",
            "processing_time": processing_time,
            "confidence": response.confidence_score
        })
    
    async def demo_style_variations(self):
        """Demo different styles and tones"""
        print("\n🎨 Demo 2: Style and Tone Variations")
        print("-" * 40)
        
        styles_to_test = [
            (CopywritingStyle.CREATIVE, CopywritingTone.HUMOROUS),
            (CopywritingStyle.TECHNICAL, CopywritingTone.AUTHORITATIVE),
            (CopywritingStyle.PERSUASIVE, CopywritingTone.URGENT)
        ]
        
        base_prompt = "Write about the benefits of renewable energy"
        
        for style, tone in styles_to_test:
            request = CopywritingRequest(
                prompt=base_prompt,
                style=style,
                tone=tone,
                length=100,
                creativity=0.7
            )
            
            start_time = time.time()
            response = await self.container.generate_use_case.execute(request)
            processing_time = time.time() - start_time
            
            print(f"🎯 {style.value.title()} + {tone.value.title()}: {processing_time:.3f}s")
            print(f"   {response.generated_text[:100]}...")
            
            self.demo_results.append({
                "demo": f"{style.value.title()} + {tone.value.title()}",
                "processing_time": processing_time,
                "confidence": response.confidence_score
            })
    
    async def demo_caching(self):
        """Demo caching functionality"""
        print("\n💾 Demo 3: Caching Demonstration")
        print("-" * 40)
        
        request = CopywritingRequest(
            prompt="Explain the benefits of clean architecture",
            style=CopywritingStyle.INFORMATIVE,
            tone=CopywritingTone.NEUTRAL,
            length=120
        )
        
        # First request (cache miss)
        start_time = time.time()
        response1 = await self.container.generate_use_case.execute(request)
        first_time = time.time() - start_time
        
        # Second request (cache hit)
        start_time = time.time()
        response2 = await self.container.generate_use_case.execute(request)
        second_time = time.time() - start_time
        
        speedup = first_time / second_time if second_time > 0 else 0
        
        print(f"🔄 First request: {first_time:.3f}s")
        print(f"⚡ Second request: {second_time:.3f}s")
        print(f"🚀 Speedup: {speedup:.1f}x")
        print(f"✅ Same content: {response1.generated_text == response2.generated_text}")
        
        self.demo_results.append({
            "demo": "Caching",
            "first_request": first_time,
            "second_request": second_time,
            "speedup": speedup
        })
    
    async def demo_events(self):
        """Demo event publishing"""
        print("\n📢 Demo 4: Event Publishing")
        print("-" * 40)
        
        # Create a custom event publisher for demo
        class DemoEventPublisher:
            def __init__(self):
                self.events = []
            
            async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
                self.events.append({"type": event_type, "data": data})
                print(f"📢 Event: {event_type} - {data}")
        
        # Replace event publisher for demo
        original_publisher = self.container.event_publisher
        demo_publisher = DemoEventPublisher()
        self.container.event_publisher = demo_publisher
        
        # Generate content to trigger events
        request = CopywritingRequest(
            prompt="Create a demo event",
            style=CopywritingStyle.CREATIVE,
            tone=CopywritingTone.ENTHUSIASTIC,
            length=80
        )
        
        await self.container.generate_use_case.execute(request)
        
        print(f"📊 Total events published: {len(demo_publisher.events)}")
        
        # Restore original publisher
        self.container.event_publisher = original_publisher
        
        self.demo_results.append({
            "demo": "Event Publishing",
            "events_count": len(demo_publisher.events)
        })
    
    async def demo_performance(self):
        """Demo performance characteristics"""
        print("\n⚡ Demo 5: Performance Analysis")
        print("-" * 40)
        
        # Test multiple requests
        requests = []
        for i in range(5):
            request = CopywritingRequest(
                prompt=f"Generate content for item {i+1}",
                style=CopywritingStyle.PROFESSIONAL,
                tone=CopywritingTone.NEUTRAL,
                length=100
            )
            requests.append(request)
        
        # Process requests
        start_time = time.time()
        responses = []
        for request in requests:
            response = await self.container.generate_use_case.execute(request)
            responses.append(response)
        total_time = time.time() - start_time
        
        avg_time = total_time / len(requests)
        avg_confidence = sum(r.confidence_score for r in responses) / len(responses)
        
        print(f"📊 Total requests: {len(requests)}")
        print(f"⏱️ Total time: {total_time:.3f}s")
        print(f"📈 Average time per request: {avg_time:.3f}s")
        print(f"🎯 Average confidence: {avg_confidence:.2f}")
        print(f"🚀 Requests per second: {len(requests) / total_time:.1f}")
        
        self.demo_results.append({
            "demo": "Performance",
            "total_requests": len(requests),
            "total_time": total_time,
            "avg_time": avg_time,
            "avg_confidence": avg_confidence,
            "rps": len(requests) / total_time
        })
    
    def show_results(self):
        """Show demo results summary"""
        print("\n📊 DEMO RESULTS SUMMARY")
        print("=" * 50)
        
        for result in self.demo_results:
            demo_name = result["demo"]
            print(f"\n🎯 {demo_name}:")
            
            for key, value in result.items():
                if key != "demo":
                    if isinstance(value, float):
                        print(f"   {key}: {value:.3f}")
                    else:
                        print(f"   {key}: {value}")
        
        # Architecture benefits
        print("\n🏗️ CLEAN ARCHITECTURE BENEFITS")
        print("=" * 50)
        benefits = [
            "✅ Separation of Concerns",
            "✅ Dependency Inversion",
            "✅ Testability",
            "✅ Maintainability",
            "✅ Scalability",
            "✅ SOLID Principles",
            "✅ Domain-Driven Design",
            "✅ Event-Driven Architecture"
        ]
        
        for benefit in benefits:
            print(benefit)
        
        print("\n🎉 Demo completed successfully!")

async def main():
    """Main demo function"""
    demo = CleanArchitectureDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main()) 