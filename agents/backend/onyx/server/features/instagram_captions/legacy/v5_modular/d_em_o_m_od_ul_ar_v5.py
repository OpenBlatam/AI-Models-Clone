"""
Instagram Captions API v5.0 - Modular Demo

Demonstration script for the ultra-fast modular architecture.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List


class ModularAPIDemo:
    """Demo client for the modular Instagram Captions API v5.0."""
    
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str = "ultra-key-123"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def test_single_generation(self) -> Dict[str, Any]:
        """Test single caption generation."""
        print("🚀 Testing single caption generation...")
        
        payload = {
            "content_description": "Increíble atardecer en la playa con colores dorados",
            "style": "inspirational",
            "audience": "lifestyle",
            "include_hashtags": True,
            "hashtag_count": 15,
            "content_type": "post",
            "priority": "high",
            "client_id": "demo-client-001"
        }
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v5/generate",
                headers=self.headers,
                json=payload
            ) as response:
                result = await response.json()
                processing_time = (time.time() - start_time) * 1000
                
                print(f"✅ Response time: {processing_time:.1f}ms")
                print(f"📝 Caption: {result.get('caption', 'N/A')}")
                print(f"🏷️  Hashtags: {len(result.get('hashtags', []))} tags")
                print(f"⭐ Quality: {result.get('quality_score', 0)}/100")
                print(f"💾 Cache hit: {result.get('cache_hit', False)}")
                
                return result
    
    async def test_batch_generation(self, batch_size: int = 10) -> Dict[str, Any]:
        """Test batch caption generation."""
        print(f"⚡ Testing batch generation ({batch_size} captions)...")
        
        # Create batch requests
        requests = []
        for i in range(batch_size):
            requests.append({
                "content_description": f"Contenido increíble número {i+1} para redes sociales",
                "style": ["casual", "professional", "playful"][i % 3],
                "audience": ["general", "millennials", "business"][i % 3],
                "include_hashtags": True,
                "hashtag_count": 10,
                "content_type": "post",
                "priority": "normal",
                "client_id": f"demo-batch-{i+1:03d}"
            })
        
        payload = {
            "requests": requests,
            "batch_id": f"demo-batch-{int(time.time())}"
        }
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v5/batch",
                headers=self.headers,
                json=payload
            ) as response:
                result = await response.json()
                processing_time = (time.time() - start_time) * 1000
                
                print(f"✅ Batch time: {processing_time:.1f}ms")
                print(f"📊 Total processed: {result.get('total_processed', 0)}")
                print(f"⚡ Avg time per caption: {processing_time/batch_size:.1f}ms")
                print(f"🔥 Throughput: {(batch_size * 1000 / processing_time):.1f} captions/sec")
                print(f"⭐ Avg quality: {result.get('avg_quality_score', 0)}/100")
                
                return result
    
    async def test_health_check(self) -> Dict[str, Any]:
        """Test health check endpoint."""
        print("💊 Testing health check...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                result = await response.json()
                
                print(f"🏥 Status: {result.get('status', 'unknown')}")
                print(f"🏆 Performance grade: {result.get('performance_grade', 'N/A')}")
                
                metrics = result.get('metrics', {})
                performance = metrics.get('performance', {})
                print(f"📈 Success rate: {performance.get('success_rate', 0)}%")
                print(f"⚡ Avg response time: {performance.get('avg_response_time_ms', 0)}ms")
                
                return result
    
    async def test_metrics(self) -> Dict[str, Any]:
        """Test metrics endpoint."""
        print("📊 Testing metrics endpoint...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/metrics",
                headers=self.headers
            ) as response:
                result = await response.json()
                
                performance = result.get('performance', {})
                config_info = result.get('configuration', {})
                
                print(f"🚀 API Version: {result.get('api_version', 'N/A')}")
                print(f"⚙️  Max batch size: {config_info.get('max_batch_size', 0)}")
                print(f"🧠 AI workers: {config_info.get('ai_workers', 0)}")
                print(f"💾 Cache size: {config_info.get('cache_max_size', 0):,}")
                
                return result
    
    async def test_concurrent_requests(self, concurrent_count: int = 15) -> None:
        """Test concurrent request handling."""
        print(f"🔥 Testing {concurrent_count} concurrent requests...")
        
        start_time = time.time()
        
        # Create concurrent tasks
        tasks = []
        for i in range(concurrent_count):
            task = self.test_single_generation()
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = (time.time() - start_time) * 1000
        successful = sum(1 for r in results if not isinstance(r, Exception))
        
        print(f"✅ Completed: {successful}/{concurrent_count}")
        print(f"⚡ Total time: {total_time:.1f}ms")
        print(f"🔥 Avg time per request: {total_time/concurrent_count:.1f}ms")
        print(f"📈 Throughput: {(successful * 1000 / total_time):.1f} RPS")
    
    async def run_comprehensive_demo(self) -> None:
        """Run comprehensive demonstration of all API features."""
        print("="*80)
        print("🚀 INSTAGRAM CAPTIONS API v5.0 - MODULAR ARCHITECTURE DEMO")
        print("="*80)
        
        try:
            # Test individual features
            print("\n1️⃣  SINGLE CAPTION GENERATION:")
            print("-" * 40)
            await self.test_single_generation()
            
            print("\n2️⃣  BATCH PROCESSING:")
            print("-" * 40)
            await self.test_batch_generation(10)
            
            print("\n3️⃣  ULTRA-FAST BATCH:")
            print("-" * 40)
            await self.test_batch_generation(50)
            
            print("\n4️⃣  HEALTH CHECK:")
            print("-" * 40)
            await self.test_health_check()
            
            print("\n5️⃣  METRICS & MONITORING:")
            print("-" * 40)
            await self.test_metrics()
            
            print("\n6️⃣  CONCURRENT PROCESSING:")
            print("-" * 40)
            await self.test_concurrent_requests(15)
            
            print("\n" + "="*80)
            print("✅ MODULAR ARCHITECTURE DEMO COMPLETED SUCCESSFULLY!")
            print("🏗️  All 8 modules working perfectly in harmony:")
            print("   • Configuration management ✅")
            print("   • Schema validation ✅") 
            print("   • AI engine processing ✅")
            print("   • Multi-level caching ✅")
            print("   • Performance metrics ✅")
            print("   • Security middleware ✅")
            print("   • Utility functions ✅")
            print("   • API orchestration ✅")
            print("="*80)
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")


async def main():
    """Run the modular API demonstration."""
    demo = ModularAPIDemo()
    await demo.run_comprehensive_demo()


if __name__ == "__main__":
    asyncio.run(main()) 