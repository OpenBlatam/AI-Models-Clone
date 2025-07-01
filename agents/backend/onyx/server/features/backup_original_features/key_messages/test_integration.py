"""
Integration test script for Key Messages feature.
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../..'))

from onyx.server.features.key_messages.service import KeyMessageService
from onyx.server.features.key_messages.models import (
    KeyMessageRequest,
    MessageType,
    MessageTone,
    BatchKeyMessageRequest
)

async def test_key_messages_service():
    """Test the Key Messages service functionality."""
    print("🧪 Testing Key Messages Service...")
    
    # Initialize service
    service = KeyMessageService()
    
    # Test 1: Basic message generation
    print("\n📝 Test 1: Basic message generation")
    request = KeyMessageRequest(
        message="Nuestro nuevo producto revoluciona la industria",
        message_type=MessageType.MARKETING,
        tone=MessageTone.PROFESSIONAL,
        target_audience="Profesionales de tecnología",
        keywords=["innovación", "revolución", "tecnología"]
    )
    
    response = await service.generate_response(request)
    print(f"✅ Success: {response.success}")
    if response.success:
        print(f"📄 Generated: {response.data.response}")
        print(f"⏱️  Processing time: {response.processing_time:.3f}s")
    
    # Test 2: Message analysis
    print("\n🔍 Test 2: Message analysis")
    analysis = await service.analyze_message(request)
    print(f"✅ Success: {analysis.success}")
    if analysis.success:
        print(f"📊 Analysis: {analysis.data.response}")
        print(f"⏱️  Processing time: {analysis.processing_time:.3f}s")
    
    # Test 3: Common response (should use cache)
    print("\n🔄 Test 3: Common response (cache test)")
    common_request = KeyMessageRequest(
        message="test_message",
        message_type=MessageType.INFORMATIONAL,
        tone=MessageTone.PROFESSIONAL
    )
    
    response1 = await service.generate_response(common_request)
    response2 = await service.generate_response(common_request)
    
    print(f"✅ First call success: {response1.success}")
    print(f"✅ Second call success: {response2.success}")
    print(f"🔄 From cache: {response2.data.metadata.get('from_cache', False)}")
    
    # Test 4: Batch processing
    print("\n📦 Test 4: Batch processing")
    batch_request = BatchKeyMessageRequest(
        messages=[
            KeyMessageRequest(message="Mensaje 1", message_type=MessageType.MARKETING),
            KeyMessageRequest(message="Mensaje 2", message_type=MessageType.EDUCATIONAL),
            KeyMessageRequest(message="", message_type=MessageType.INFORMATIONAL)  # This will fail
        ],
        batch_size=10
    )
    
    batch_response = await service.generate_batch(batch_request)
    print(f"✅ Batch success: {batch_response.success}")
    print(f"📊 Total processed: {batch_response.total_processed}")
    print(f"❌ Failed count: {batch_response.failed_count}")
    print(f"⏱️  Total processing time: {batch_response.processing_time:.3f}s")
    
    # Test 5: Cache operations
    print("\n💾 Test 5: Cache operations")
    stats = await service.get_cache_stats()
    print(f"📊 Cache size: {stats['cache_size']}")
    print(f"⏰ Cache TTL: {stats['cache_ttl_hours']} hours")
    
    # Test 6: Clear cache
    print("\n🧹 Test 6: Clear cache")
    await service.clear_cache()
    stats_after = await service.get_cache_stats()
    print(f"📊 Cache size after clear: {stats_after['cache_size']}")
    
    print("\n🎉 All tests completed!")

async def test_api_endpoints():
    """Test the API endpoints (requires running server)."""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import httpx
        
        # Test health endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/key-messages/health")
            if response.status_code == 200:
                print("✅ Health endpoint: OK")
            else:
                print(f"❌ Health endpoint: {response.status_code}")
        
        # Test message types endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/key-messages/types")
            if response.status_code == 200:
                types = response.json()
                print(f"✅ Message types: {types}")
            else:
                print(f"❌ Message types endpoint: {response.status_code}")
        
        # Test message tones endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/key-messages/tones")
            if response.status_code == 200:
                tones = response.json()
                print(f"✅ Message tones: {tones}")
            else:
                print(f"❌ Message tones endpoint: {response.status_code}")
                
    except ImportError:
        print("⚠️  httpx not available, skipping API endpoint tests")
    except Exception as e:
        print(f"⚠️  API endpoint tests failed: {e}")

def main():
    """Main test function."""
    print("🚀 Starting Key Messages Integration Tests")
    print("=" * 50)
    
    # Test service functionality
    asyncio.run(test_key_messages_service())
    
    # Test API endpoints (if server is running)
    asyncio.run(test_api_endpoints())
    
    print("\n" + "=" * 50)
    print("✨ Integration tests completed!")

if __name__ == "__main__":
    main() 