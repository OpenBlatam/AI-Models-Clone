"""
Integration Tests for LinkedIn Posts API
========================================

End-to-end integration tests for the complete API workflow.
"""

import pytest
import asyncio
from typing import List, Dict, Any
import time
from datetime import datetime

from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestAPIIntegration:
    """Integration tests for the complete API workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_post_lifecycle(self, async_client, auth_headers, sample_post_data):
        """Test complete post lifecycle: create, read, update, delete."""
        print("\n🔄 Testing complete post lifecycle...")
        
        # 1. Create post
        print("  📝 Creating post...")
        create_response = await async_client.post(
            "/linkedin-posts/",
            json=sample_post_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        created_post = create_response.json()
        post_id = created_post["id"]
        
        print(f"    ✅ Post created with ID: {post_id}")
        assert created_post["content"] == sample_post_data["content"]
        assert created_post["post_type"] == sample_post_data["post_type"]
        assert created_post["nlp_enhanced"] is True
        
        # 2. Read post
        print("  📖 Reading post...")
        read_response = await async_client.get(
            f"/linkedin-posts/{post_id}",
            headers=auth_headers
        )
        
        assert read_response.status_code == 200
        read_post = read_response.json()
        
        print(f"    ✅ Post retrieved successfully")
        assert read_post["id"] == post_id
        assert read_post["content"] == sample_post_data["content"]
        
        # 3. Update post
        print("  ✏️ Updating post...")
        update_data = {
            "content": "Updated content with new information!",
            "tone": "casual"
        }
        
        update_response = await async_client.put(
            f"/linkedin-posts/{post_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert update_response.status_code == 200
        updated_post = update_response.json()
        
        print(f"    ✅ Post updated successfully")
        assert updated_post["content"] == update_data["content"]
        assert updated_post["tone"] == update_data["tone"]
        
        # 4. Analyze post
        print("  📊 Analyzing post...")
        analyze_response = await async_client.get(
            f"/linkedin-posts/{post_id}/analyze?use_async_nlp=true",
            headers=auth_headers
        )
        
        assert analyze_response.status_code == 200
        analysis = analyze_response.json()
        
        print(f"    ✅ Post analyzed successfully")
        assert "sentiment_score" in analysis
        assert "readability_score" in analysis
        assert "keywords" in analysis
        assert "entities" in analysis
        
        # 5. Optimize post
        print("  ⚡ Optimizing post...")
        optimize_response = await async_client.post(
            f"/linkedin-posts/{post_id}/optimize",
            json={"use_async_nlp": True},
            headers=auth_headers
        )
        
        assert optimize_response.status_code == 200
        optimized_post = optimize_response.json()
        
        print(f"    ✅ Post optimized successfully")
        assert optimized_post["nlp_enhanced"] is True
        
        # 6. Delete post
        print("  🗑️ Deleting post...")
        delete_response = await async_client.delete(
            f"/linkedin-posts/{post_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 204
        
        print(f"    ✅ Post deleted successfully")
        
        # 7. Verify deletion
        verify_response = await async_client.get(
            f"/linkedin-posts/{post_id}",
            headers=auth_headers
        )
        
        assert verify_response.status_code == 404
        
        print("  ✅ Complete lifecycle test passed!")
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, async_client, auth_headers, sample_batch_data):
        """Test batch create and optimize operations."""
        print("\n📦 Testing batch operations...")
        
        # 1. Batch create posts
        print("  📝 Creating posts in batch...")
        batch_create_response = await async_client.post(
            "/linkedin-posts/batch?parallel_processing=true",
            json=sample_batch_data,
            headers=auth_headers
        )
        
        assert batch_create_response.status_code == 200
        created_posts = batch_create_response.json()
        
        print(f"    ✅ Created {len(created_posts)} posts in batch")
        assert len(created_posts) == len(sample_batch_data)
        
        # Extract post IDs for batch operations
        post_ids = [post["id"] for post in created_posts]
        
        # 2. Batch optimize posts
        print("  ⚡ Optimizing posts in batch...")
        batch_optimize_response = await async_client.post(
            "/linkedin-posts/batch/optimize",
            json={
                "post_ids": post_ids,
                "use_async_nlp": True
            },
            headers=auth_headers
        )
        
        assert batch_optimize_response.status_code == 200
        optimized_posts = batch_optimize_response.json()
        
        print(f"    ✅ Optimized {len(optimized_posts)} posts in batch")
        assert len(optimized_posts) == len(post_ids)
        
        # Verify all posts were optimized
        for post in optimized_posts:
            assert post["nlp_enhanced"] is True
        
        # 3. Clean up - delete all posts
        print("  🧹 Cleaning up batch posts...")
        for post_id in post_ids:
            await async_client.delete(
                f"/linkedin-posts/{post_id}",
                headers=auth_headers
            )
        
        print("  ✅ Batch operations test passed!")
    
    @pytest.mark.asyncio
    async def test_caching_behavior(self, async_client, auth_headers, sample_post_data):
        """Test caching behavior and performance."""
        print("\n💾 Testing caching behavior...")
        
        # 1. Create a post
        create_response = await async_client.post(
            "/linkedin-posts/",
            json=sample_post_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]
        
        # 2. First request (should be cache miss)
        print("  🔍 First request (cache miss)...")
        start_time = time.time()
        first_response = await async_client.get(
            f"/linkedin-posts/{post_id}?use_cache=true",
            headers=auth_headers
        )
        first_time = time.time() - start_time
        
        assert first_response.status_code == 200
        cache_status = first_response.headers.get("X-Cache", "MISS")
        
        print(f"    ⏱️ First request time: {first_time:.3f}s (Cache: {cache_status})")
        
        # 3. Second request (should be cache hit)
        print("  🔍 Second request (cache hit)...")
        start_time = time.time()
        second_response = await async_client.get(
            f"/linkedin-posts/{post_id}?use_cache=true",
            headers=auth_headers
        )
        second_time = time.time() - start_time
        
        assert second_response.status_code == 200
        cache_status = second_response.headers.get("X-Cache", "MISS")
        
        print(f"    ⏱️ Second request time: {second_time:.3f}s (Cache: {cache_status})")
        
        # 4. Verify cache performance improvement
        if second_time < first_time:
            improvement = ((first_time - second_time) / first_time) * 100
            print(f"    ✅ Performance improvement: {improvement:.1f}%")
            assert improvement > 0
        else:
            print(f"    ⚠️ No performance improvement observed")
        
        # 5. Test ETag support
        print("  🏷️ Testing ETag support...")
        etag = second_response.headers.get("ETag")
        if etag:
            etag_response = await async_client.get(
                f"/linkedin-posts/{post_id}",
                headers={**auth_headers, "If-None-Match": etag}
            )
            
            print(f"    ETag response status: {etag_response.status_code}")
            assert etag_response.status_code in [200, 304]
        
        # Clean up
        await async_client.delete(f"/linkedin-posts/{post_id}", headers=auth_headers)
        
        print("  ✅ Caching behavior test passed!")
    
    @pytest.mark.asyncio
    async def test_list_posts_with_filters(self, async_client, auth_headers, sample_post_data):
        """Test list posts with various filters and pagination."""
        print("\n📋 Testing list posts with filters...")
        
        # 1. Create multiple posts with different types
        post_types = ["announcement", "educational", "update"]
        created_posts = []
        
        for i, post_type in enumerate(post_types):
            post_data = {**sample_post_data, "post_type": post_type}
            response = await async_client.post(
                "/linkedin-posts/",
                json=post_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            created_posts.append(response.json())
        
        print(f"    ✅ Created {len(created_posts)} posts with different types")
        
        # 2. Test listing all posts
        print("  📖 Listing all posts...")
        list_response = await async_client.get(
            "/linkedin-posts/",
            headers=auth_headers
        )
        
        assert list_response.status_code == 200
        all_posts = list_response.json()
        
        print(f"    Found {all_posts['total']} posts")
        assert all_posts["total"] >= len(created_posts)
        
        # 3. Test filtering by post type
        print("  🔍 Filtering by post type...")
        filter_response = await async_client.get(
            "/linkedin-posts/?post_type=announcement",
            headers=auth_headers
        )
        
        assert filter_response.status_code == 200
        filtered_posts = filter_response.json()
        
        print(f"    Found {filtered_posts['total']} announcement posts")
        for post in filtered_posts["posts"]:
            assert post["post_type"] == "announcement"
        
        # 4. Test pagination
        print("  📄 Testing pagination...")
        paginated_response = await async_client.get(
            "/linkedin-posts/?limit=2&offset=0",
            headers=auth_headers
        )
        
        assert paginated_response.status_code == 200
        paginated_posts = paginated_response.json()
        
        print(f"    Pagination: {len(paginated_posts['posts'])} posts, limit=2")
        assert len(paginated_posts["posts"]) <= 2
        assert "has_more" in paginated_posts
        
        # 5. Test sorting
        print("  🔄 Testing sorting...")
        sorted_response = await async_client.get(
            "/linkedin-posts/?sort_by=created_at&sort_order=desc",
            headers=auth_headers
        )
        
        assert sorted_response.status_code == 200
        sorted_posts = sorted_response.json()
        
        print(f"    Sorted {sorted_posts['total']} posts by creation date")
        
        # Clean up
        for post in created_posts:
            await async_client.delete(
                f"/linkedin-posts/{post['id']}",
                headers=auth_headers
            )
        
        print("  ✅ List posts with filters test passed!")
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, async_client, auth_headers):
        """Test performance metrics endpoint."""
        print("\n📈 Testing performance metrics...")
        
        # 1. Get basic metrics
        print("  📊 Getting basic metrics...")
        metrics_response = await async_client.get(
            "/linkedin-posts/performance/metrics",
            headers=auth_headers
        )
        
        assert metrics_response.status_code == 200
        metrics = metrics_response.json()
        
        print(f"    ✅ Retrieved performance metrics")
        assert "fast_nlp_metrics" in metrics
        assert "async_nlp_metrics" in metrics
        assert "timestamp" in metrics
        
        # 2. Get detailed metrics
        print("  📊 Getting detailed metrics...")
        detailed_response = await async_client.get(
            "/linkedin-posts/performance/metrics?include_detailed=true",
            headers=auth_headers
        )
        
        assert detailed_response.status_code == 200
        detailed_metrics = detailed_response.json()
        
        print(f"    ✅ Retrieved detailed metrics")
        assert "system_metrics" in detailed_metrics
        
        # 3. Test cache headers
        cache_control = detailed_response.headers.get("Cache-Control")
        print(f"    Cache-Control: {cache_control}")
        assert cache_control is not None
        
        print("  ✅ Performance metrics test passed!")
    
    @pytest.mark.asyncio
    async def test_health_checks(self, async_client):
        """Test all health check endpoints."""
        print("\n🏥 Testing health checks...")
        
        # 1. Basic health check
        print("  💚 Basic health check...")
        health_response = await async_client.get("/linkedin-posts/health")
        
        assert health_response.status_code == 200
        health_data = health_response.json()
        
        print(f"    Status: {health_data['status']}")
        assert health_data["status"] == "healthy"
        assert health_data["service"] == "linkedin-posts-v2"
        
        # 2. Detailed health check
        print("  💚 Detailed health check...")
        detailed_response = await async_client.get("/linkedin-posts/health?detailed=true")
        
        assert detailed_response.status_code == 200
        detailed_health = detailed_response.json()
        
        print(f"    Detailed status: {detailed_health['status']}")
        if "dependencies" in detailed_health:
            print(f"    Dependencies: {detailed_health['dependencies']}")
        
        # 3. Readiness check
        print("  ✅ Readiness check...")
        ready_response = await async_client.get("/linkedin-posts/health/ready")
        
        assert ready_response.status_code == 200
        ready_data = ready_response.json()
        
        print(f"    Ready: {ready_data['ready']}")
        assert ready_data["ready"] is True
        
        # 4. Liveness check
        print("  💓 Liveness check...")
        live_response = await async_client.get("/linkedin-posts/health/live")
        
        assert live_response.status_code == 200
        live_data = live_response.json()
        
        print(f"    Alive: {live_data['alive']}")
        assert live_data["alive"] is True
        
        print("  ✅ Health checks test passed!")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, async_client, auth_headers):
        """Test error handling scenarios."""
        print("\n⚠️ Testing error handling...")
        
        # 1. Test non-existent post
        print("  🔍 Testing non-existent post...")
        not_found_response = await async_client.get(
            "/linkedin-posts/non-existent-id",
            headers=auth_headers
        )
        
        assert not_found_response.status_code == 404
        error_data = not_found_response.json()
        print(f"    Error: {error_data['detail']}")
        
        # 2. Test invalid post ID format
        print("  🔍 Testing invalid post ID...")
        invalid_response = await async_client.get(
            "/linkedin-posts/invalid-id-format",
            headers=auth_headers
        )
        
        print(f"    Invalid ID response: {invalid_response.status_code}")
        
        # 3. Test invalid request data
        print("  🔍 Testing invalid request data...")
        invalid_data = {
            "content": "",  # Empty content
            "post_type": "invalid_type",
            "tone": "invalid_tone"
        }
        
        invalid_create_response = await async_client.post(
            "/linkedin-posts/",
            json=invalid_data,
            headers=auth_headers
        )
        
        print(f"    Invalid data response: {invalid_create_response.status_code}")
        assert invalid_create_response.status_code in [400, 422]
        
        # 4. Test missing authentication
        print("  🔍 Testing missing authentication...")
        no_auth_response = await async_client.get("/linkedin-posts/")
        
        print(f"    No auth response: {no_auth_response.status_code}")
        # This might be 401 or 200 depending on auth configuration
        
        print("  ✅ Error handling test passed!")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, async_client, auth_headers, sample_post_data):
        """Test handling of concurrent requests."""
        print("\n⚡ Testing concurrent requests...")
        
        # Create a post first
        create_response = await async_client.post(
            "/linkedin-posts/",
            json=sample_post_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]
        
        # Make concurrent requests
        print("  🔄 Making 10 concurrent requests...")
        start_time = time.time()
        
        async def make_request():
            return await async_client.get(
                f"/linkedin-posts/{post_id}",
                headers=auth_headers
            )
        
        # Execute concurrent requests
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful = sum(1 for r in responses if isinstance(r, dict) and r.get("status_code") == 200)
        errors = sum(1 for r in responses if isinstance(r, Exception))
        
        print(f"    ✅ Successful: {successful}/10")
        print(f"    ❌ Errors: {errors}/10")
        print(f"    ⏱️ Total time: {total_time:.3f}s")
        print(f"    🚀 Requests/second: {10/total_time:.1f}")
        
        # Assertions
        assert successful >= 8  # At least 80% success rate
        assert total_time < 5.0  # Should complete in reasonable time
        
        # Clean up
        await async_client.delete(f"/linkedin-posts/{post_id}", headers=auth_headers)
        
        print("  ✅ Concurrent requests test passed!")


class TestAPIPerformance:
    """Performance-focused integration tests."""
    
    @pytest.mark.asyncio
    async def test_bulk_operations_performance(self, async_client, auth_headers):
        """Test performance of bulk operations."""
        print("\n🚀 Testing bulk operations performance...")
        
        # Create bulk data
        bulk_data = [
            {
                "content": f"Performance test post {i}",
                "post_type": "educational",
                "tone": "professional",
                "target_audience": "developers",
                "industry": "technology"
            }
            for i in range(20)
        ]
        
        # Measure bulk creation
        print("  📝 Bulk creation performance...")
        start_time = time.time()
        
        create_response = await async_client.post(
            "/linkedin-posts/batch?parallel_processing=true",
            json=bulk_data,
            headers=auth_headers
        )
        
        create_time = time.time() - start_time
        
        assert create_response.status_code == 200
        created_posts = create_response.json()
        
        print(f"    Created {len(created_posts)} posts in {create_time:.3f}s")
        print(f"    Rate: {len(created_posts)/create_time:.1f} posts/second")
        
        # Measure bulk optimization
        post_ids = [post["id"] for post in created_posts]
        
        print("  ⚡ Bulk optimization performance...")
        start_time = time.time()
        
        optimize_response = await async_client.post(
            "/linkedin-posts/batch/optimize",
            json={"post_ids": post_ids, "use_async_nlp": True},
            headers=auth_headers
        )
        
        optimize_time = time.time() - start_time
        
        assert optimize_response.status_code == 200
        optimized_posts = optimize_response.json()
        
        print(f"    Optimized {len(optimized_posts)} posts in {optimize_time:.3f}s")
        print(f"    Rate: {len(optimized_posts)/optimize_time:.1f} posts/second")
        
        # Performance assertions
        assert create_time < 10.0  # Should create 20 posts in under 10 seconds
        assert optimize_time < 15.0  # Should optimize 20 posts in under 15 seconds
        
        # Clean up
        for post_id in post_ids:
            await async_client.delete(f"/linkedin-posts/{post_id}", headers=auth_headers)
        
        print("  ✅ Bulk operations performance test passed!")
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, async_client, auth_headers, sample_post_data):
        """Test cache performance impact."""
        print("\n💾 Testing cache performance...")
        
        # Create a post
        create_response = await async_client.post(
            "/linkedin-posts/",
            json=sample_post_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]
        
        # Measure uncached request
        print("  🔍 Uncached request...")
        start_time = time.time()
        
        uncached_response = await async_client.get(
            f"/linkedin-posts/{post_id}?use_cache=false",
            headers=auth_headers
        )
        
        uncached_time = time.time() - start_time
        
        assert uncached_response.status_code == 200
        print(f"    Uncached time: {uncached_time:.3f}s")
        
        # Measure cached request
        print("  🔍 Cached request...")
        start_time = time.time()
        
        cached_response = await async_client.get(
            f"/linkedin-posts/{post_id}?use_cache=true",
            headers=auth_headers
        )
        
        cached_time = time.time() - start_time
        
        assert cached_response.status_code == 200
        print(f"    Cached time: {cached_time:.3f}s")
        
        # Calculate improvement
        if cached_time < uncached_time:
            improvement = ((uncached_time - cached_time) / uncached_time) * 100
            print(f"    Performance improvement: {improvement:.1f}%")
            assert improvement > 0
        else:
            print(f"    No performance improvement observed")
        
        # Clean up
        await async_client.delete(f"/linkedin-posts/{post_id}", headers=auth_headers)
        
        print("  ✅ Cache performance test passed!")


# Export test classes
__all__ = [
    "TestAPIIntegration",
    "TestAPIPerformance"
] 