#!/usr/bin/env python3
"""
Enhanced HeyGen AI Demo Runner v2.1
Demonstrates all new features: caching, async queues, webhooks, rate limiting, and metrics.
"""

import asyncio
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import structlog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()

class EnhancedHeyGenDemo:
    """Enhanced HeyGen AI demo runner with all v2.1 features."""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        
        # Import components
        try:
            from .core.heygen_ai import get_heygen_ai
            from .core.cache_manager import get_cache_manager
            from .core.async_queue_manager import get_queue_manager
            from .core.webhook_manager import get_webhook_manager
            from .core.rate_limiter import get_rate_limiter
            from .core.metrics_collector import get_metrics_collector
            
            self.heygen_ai = get_heygen_ai()
            self.cache_manager = get_cache_manager()
            self.queue_manager = get_queue_manager()
            self.webhook_manager = get_webhook_manager()
            self.rate_limiter = get_rate_limiter()
            self.metrics_collector = get_metrics_collector()
            
        except ImportError as e:
            logger.error(f"Failed to import components: {e}")
            raise
    
    async def run_all_demos(self):
        """Run all demonstration scenarios."""
        logger.info("🚀 Starting Enhanced HeyGen AI Demo v2.1")
        
        try:
            # Wait for system initialization
            await self._wait_for_initialization()
            
            # Run demo scenarios
            await self.demo_system_health()
            await self.demo_cache_system()
            await self.demo_async_queues()
            await self.demo_webhooks()
            await self.demo_rate_limiting()
            await self.demo_metrics_collection()
            await self.demo_full_video_pipeline()
            await self.demo_performance_optimization()
            
            # Final summary
            await self.demo_summary()
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise
    
    async def _wait_for_initialization(self):
        """Wait for the system to be fully initialized."""
        logger.info("⏳ Waiting for system initialization...")
        
        max_wait = 30  # seconds
        start_wait = time.time()
        
        while not self.heygen_ai.is_initialized:
            if time.time() - start_wait > max_wait:
                raise TimeoutError("System initialization timeout")
            
            await asyncio.sleep(1)
        
        logger.info("✅ System initialized successfully")
    
    async def demo_system_health(self):
        """Demonstrate system health monitoring."""
        logger.info("🏥 Demo: System Health Monitoring")
        
        try:
            # Get health status
            health = await self.heygen_ai.health_check()
            
            # Get system stats
            stats = await self.heygen_ai.get_system_stats()
            
            self.results["system_health"] = {
                "health_status": health,
                "system_stats": stats,
                "timestamp": time.time()
            }
            
            logger.info(f"✅ System Health: {health['status']}")
            logger.info(f"📊 System Stats: {stats['system']['version']} - Uptime: {stats['system']['uptime_hours']}h")
            
        except Exception as e:
            logger.error(f"❌ System health demo failed: {e}")
            self.results["system_health"] = {"error": str(e)}
    
    async def demo_cache_system(self):
        """Demonstrate intelligent caching system."""
        logger.info("💾 Demo: Intelligent Caching System")
        
        try:
            # Test cache operations
            test_data = {"message": "Hello from cache demo", "timestamp": time.time()}
            
            # Store data with different priorities
            await self.cache_manager.set(
                "demo_high_priority",
                test_data,
                cache_type="api_response",
                priority="high",
                ttl_seconds=60,
                tags=["demo", "high_priority"]
            )
            
            await self.cache_manager.set(
                "demo_low_priority",
                test_data,
                cache_type="api_response",
                priority="low",
                ttl_seconds=30,
                tags=["demo", "low_priority"]
            )
            
            # Retrieve data
            cached_high = await self.cache_manager.get("demo_high_priority")
            cached_low = await self.cache_manager.get("demo_low_priority")
            
            # Get cache statistics
            cache_stats = await self.cache_manager.get_stats()
            
            self.results["cache_system"] = {
                "high_priority_cached": cached_high is not None,
                "low_priority_cached": cached_low is not None,
                "cache_stats": cache_stats,
                "timestamp": time.time()
            }
            
            logger.info(f"✅ Cache Demo: High priority cached: {cached_high is not None}")
            logger.info(f"📊 Cache Stats: Memory: {cache_stats['memory_usage_mb']:.2f}MB, Disk: {cache_stats['disk_usage_mb']:.2f}MB")
            
        except Exception as e:
            logger.error(f"❌ Cache demo failed: {e}")
            self.results["cache_system"] = {"error": str(e)}
    
    async def demo_async_queues(self):
        """Demonstrate async task queues."""
        logger.info("🔄 Demo: Async Task Queues")
        
        try:
            # Submit different types of tasks
            video_task_id = await self.queue_manager.submit_task(
                task_type="video_generation",
                payload={"demo": True, "type": "video"},
                priority="high",
                user_id="demo_user"
            )
            
            voice_task_id = await self.queue_manager.submit_task(
                task_type="voice_synthesis",
                payload={"demo": True, "type": "voice"},
                priority="normal",
                user_id="demo_user"
            )
            
            # Get queue statistics
            queue_stats = await self.queue_manager.get_queue_stats()
            
            # Get task statuses
            video_status = await self.queue_manager.get_task_status(video_task_id)
            voice_status = await self.queue_manager.get_task_status(voice_task_id)
            
            self.results["async_queues"] = {
                "video_task_id": video_task_id,
                "voice_task_id": voice_task_id,
                "video_status": video_status,
                "voice_status": voice_status,
                "queue_stats": queue_stats,
                "timestamp": time.time()
            }
            
            logger.info(f"✅ Queue Demo: Video task {video_task_id[:8]}... submitted")
            logger.info(f"📊 Queue Stats: {queue_stats['queue_size']} pending, {queue_stats['active_tasks']} active")
            
        except Exception as e:
            logger.error(f"❌ Queue demo failed: {e}")
            self.results["async_queues"] = {"error": str(e)}
    
    async def demo_webhooks(self):
        """Demonstrate webhook system."""
        logger.info("🔗 Demo: Webhook System")
        
        try:
            # Register a demo webhook endpoint
            endpoint_id = self.webhook_manager.register_endpoint(
                url="https://httpbin.org/post",
                events=["video.completed", "task.started"],
                secret="demo_secret"
            )
            
            # Send test events
            video_event_id = await self.webhook_manager.send_event(
                "video.completed",
                {"demo": True, "video_id": "demo_123", "status": "completed"}
            )
            
            task_event_id = await self.webhook_manager.send_event(
                "task.started",
                {"demo": True, "task_id": "demo_task", "type": "video_generation"}
            )
            
            # Get webhook statistics
            webhook_stats = self.webhook_manager.get_stats()
            
            self.results["webhooks"] = {
                "endpoint_id": endpoint_id,
                "video_event_id": video_event_id,
                "task_event_id": task_event_id,
                "webhook_stats": webhook_stats,
                "timestamp": time.time()
            }
            
            logger.info(f"✅ Webhook Demo: Endpoint {endpoint_id[:8]}... registered")
            logger.info(f"📊 Webhook Stats: {webhook_stats['total_events']} events, {webhook_stats['active_endpoints']} endpoints")
            
        except Exception as e:
            logger.error(f"❌ Webhook demo failed: {e}")
            self.results["webhooks"] = {"error": str(e)}
    
    async def demo_rate_limiting(self):
        """Demonstrate adaptive rate limiting."""
        logger.info("🚦 Demo: Adaptive Rate Limiting")
        
        try:
            # Test rate limiting for different users
            users = ["demo_user_1", "demo_user_2", "demo_user_3"]
            results = {}
            
            for user_id in users:
                allowed, info = await self.rate_limiter.check_rate_limit(
                    user_id=user_id,
                    endpoint="demo_endpoint",
                    request_weight=1
                )
                
                results[user_id] = {
                    "allowed": allowed,
                    "tier": info["user_tier"],
                    "current_requests": info["current_requests"],
                    "limit": info["limit"]
                }
            
            # Get rate limiting statistics
            rate_limit_stats = self.rate_limiter.get_system_stats()
            
            self.results["rate_limiting"] = {
                "user_results": results,
                "system_stats": rate_limit_stats,
                "timestamp": time.time()
            }
            
            allowed_users = sum(1 for r in results.values() if r["allowed"])
            logger.info(f"✅ Rate Limiting Demo: {allowed_users}/{len(users)} users allowed")
            logger.info(f"📊 Rate Limit Stats: {rate_limit_stats['total_users']} users, {rate_limit_stats['blocked_users']} blocked")
            
        except Exception as e:
            logger.error(f"❌ Rate limiting demo failed: {e}")
            self.results["rate_limiting"] = {"error": str(e)}
    
    async def demo_metrics_collection(self):
        """Demonstrate metrics collection."""
        logger.info("📊 Demo: Metrics Collection")
        
        try:
            # Record some demo metrics
            self.metrics_collector.record_video_generation("demo", "high", "1080p", 5.0)
            self.metrics_collector.record_voice_synthesis("demo", "coqui_tts", "en", 2.0)
            self.metrics_collector.record_cache_operation("demo_cache", True)
            
            # Get metrics summary
            metrics_summary = self.metrics_collector.get_metrics_summary()
            
            # Get Prometheus format metrics
            prometheus_metrics = self.metrics_collector.get_metrics()
            
            self.results["metrics_collection"] = {
                "metrics_summary": metrics_summary,
                "prometheus_metrics_length": len(prometheus_metrics),
                "timestamp": time.time()
            }
            
            logger.info(f"✅ Metrics Demo: {len(metrics_summary)} metrics collected")
            logger.info(f"📊 Prometheus Metrics: {len(prometheus_metrics)} characters")
            
        except Exception as e:
            logger.error(f"❌ Metrics demo failed: {e}")
            self.results["metrics_collection"] = {"error": str(e)}
    
    async def demo_full_video_pipeline(self):
        """Demonstrate full video generation pipeline."""
        logger.info("🎬 Demo: Full Video Generation Pipeline")
        
        try:
            # Create a demo video request
            from .api.models import VideoRequest
            
            demo_request = VideoRequest(
                script="Welcome to the Enhanced HeyGen AI demo! This system showcases advanced AI video generation capabilities.",
                avatar_id="demo_avatar_001",
                voice_id="demo_voice_001",
                language="en",
                resolution="1080p",
                quality_preset="high",
                enable_expressions=True,
                enable_effects=False
            )
            
            # Submit video generation task
            response = await self.heygen_ai.create_video(
                request=demo_request,
                user_id="demo_user",
                priority="high",
                enable_webhooks=True
            )
            
            self.results["video_pipeline"] = {
                "video_id": response.video_id,
                "status": response.status,
                "task_id": response.task_id,
                "timestamp": time.time()
            }
            
            logger.info(f"✅ Video Pipeline Demo: Task {response.task_id[:8]}... submitted")
            logger.info(f"📊 Video Status: {response.status}")
            
        except Exception as e:
            logger.error(f"❌ Video pipeline demo failed: {e}")
            self.results["video_pipeline"] = {"error": str(e)}
    
    async def demo_performance_optimization(self):
        """Demonstrate performance optimization features."""
        logger.info("⚡ Demo: Performance Optimization")
        
        try:
            # Test cache performance
            cache_start = time.time()
            for i in range(10):
                await self.cache_manager.set(
                    f"perf_test_{i}",
                    {"data": f"test_data_{i}", "iteration": i},
                    cache_type="api_response",
                    priority="medium",
                    ttl_seconds=300
                )
            cache_set_time = time.time() - cache_start
            
            # Test cache retrieval
            cache_get_start = time.time()
            for i in range(10):
                await self.cache_manager.get(f"perf_test_{i}")
            cache_get_time = time.time() - cache_get_start
            
            # Get performance metrics
            performance_metrics = {
                "cache_set_time": cache_set_time,
                "cache_get_time": cache_get_time,
                "cache_operations_per_second": 20 / (cache_set_time + cache_get_time)
            }
            
            self.results["performance_optimization"] = {
                "performance_metrics": performance_metrics,
                "timestamp": time.time()
            }
            
            logger.info(f"✅ Performance Demo: Cache set: {cache_set_time:.3f}s, get: {cache_get_time:.3f}s")
            logger.info(f"📊 Performance: {performance_metrics['cache_operations_per_second']:.1f} ops/sec")
            
        except Exception as e:
            logger.error(f"❌ Performance demo failed: {e}")
            self.results["performance_optimization"] = {"error": str(e)}
    
    async def demo_summary(self):
        """Provide a comprehensive demo summary."""
        logger.info("📋 Demo Summary")
        
        total_time = time.time() - self.start_time
        
        # Count successful demos
        successful_demos = sum(1 for result in self.results.values() if "error" not in result)
        total_demos = len(self.results)
        
        # Generate summary
        summary = {
            "demo_results": self.results,
            "summary": {
                "total_demos": total_demos,
                "successful_demos": successful_demos,
                "failed_demos": total_demos - successful_demos,
                "success_rate": successful_demos / total_demos if total_demos > 0 else 0,
                "total_time_seconds": total_time,
                "timestamp": time.time()
            }
        }
        
        # Save results to file
        output_file = Path("demo_results_v2.1.json")
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🎉 ENHANCED HEYGEN AI DEMO v2.1 COMPLETED")
        logger.info("=" * 60)
        logger.info(f"✅ Successful Demos: {successful_demos}/{total_demos}")
        logger.info(f"⏱️  Total Time: {total_time:.2f} seconds")
        logger.info(f"📁 Results saved to: {output_file}")
        logger.info("=" * 60)
        
        # Print component status
        logger.info("🔧 Component Status:")
        logger.info(f"   • HeyGen AI Core: {'✅' if self.heygen_ai.is_initialized else '❌'}")
        logger.info(f"   • Cache Manager: {'✅' if self.cache_manager else '❌'}")
        logger.info(f"   • Queue Manager: {'✅' if self.queue_manager else '❌'}")
        logger.info(f"   • Webhook Manager: {'✅' if self.webhook_manager else '❌'}")
        logger.info(f"   • Rate Limiter: {'✅' if self.rate_limiter else '❌'}")
        logger.info(f"   • Metrics Collector: {'✅' if self.metrics_collector else '❌'}")
        
        self.results["summary"] = summary
        return summary

async def main():
    """Main demo runner."""
    try:
        demo = EnhancedHeyGenDemo()
        await demo.run_all_demos()
        
    except Exception as e:
        logger.error(f"Demo runner failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
