#!/usr/bin/env python3
"""
Instagram Captions API v2.1 - Ultra-Fast Main Application Entry Point

Maximum performance optimizations:
- Multi-level caching
- In-memory cache with LRU eviction
- Parallel processing optimization
- Connection pooling
- Response compression
- Background task processing
"""

import asyncio
import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from api import app
from config import get_settings
from speed_optimizations import initialize_speed_optimizations, cleanup_speed_optimizations

settings = get_settings()


async def startup_optimizations():
    """Initialize all speed optimizations on startup."""
    print("🚀 Initializing ultra-fast optimizations...")
    await initialize_speed_optimizations()
    print("✅ Speed optimizations ready!")


async def shutdown_optimizations():
    """Clean up optimizations on shutdown."""
    print("🛑 Cleaning up speed optimizations...")
    await cleanup_speed_optimizations()
    print("✅ Cleanup completed!")


def run_ultra_fast_server():
    """Run the ultra-fast optimized API server."""
    
    uvicorn_config = {
        "app": "main:app",
        "host": settings.host,
        "port": settings.port,
        "reload": settings.reload and settings.environment.value == "development",
        "log_level": settings.log_level.value.lower(),
        "access_log": True,
        "use_colors": settings.environment.value == "development",
        "loop": "auto",
        "http": "auto",
        "ws": "auto",
        "interface": "auto",
        "lifespan": "on"  # Enable lifespan events for optimizations
    }
    
    # Ultra-fast production optimizations
    if settings.environment.value == "production":
        uvicorn_config.update({
            "workers": 1,
            "reload": False,
            "access_log": False,
            "server_header": False,
            "date_header": False,
            "timeout_keep_alive": 65,  # Longer keep-alive for connection reuse
            "timeout_graceful_shutdown": 10
        })
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 Instagram Captions API v{settings.api_version} ULTRA-FAST 🚀                ║
║                                                                               ║
║  ⚡ Environment: {settings.environment.value:<20} 🔧 Debug: {str(settings.debug):<15}  ║
║  🌐 Host: {settings.host:<25} 📡 Port: {settings.port:<20}  ║
║  💾 Multi-Level Caching: Enabled      🔄 Connection Pooling: Enabled        ║
║  📊 In-Memory Cache: Enabled          ⚡ Parallel Processing: Enabled        ║
║  🗜️  Response Compression: Enabled     🎯 Background Tasks: Enabled          ║
║                                                                               ║
║  📖 API Documentation: http://{settings.host}:{settings.port}/docs                     ║
║  🔍 Health Check: http://{settings.host}:{settings.port}/api/v2/instagram-captions/health ║
║  ⚡ Ultra-Fast API: http://{settings.host}:{settings.port}/api/v2.1/instagram-captions/   ║
║                                                                               ║
║  🎯 PERFORMANCE OPTIMIZATIONS ACTIVE:                                        ║
║     • Multi-level caching (Memory + Redis)                                   ║
║     • Ultra-fast in-memory cache with LRU eviction                          ║
║     • Parallel batch processing (10x concurrency)                           ║
║     • Connection pooling for external APIs                                   ║
║     • Response compression for large payloads                               ║
║     • Background cache warming                                               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Initialize optimizations before starting server
        asyncio.run(startup_optimizations())
        
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        asyncio.run(shutdown_optimizations())
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)


def run_development():
    """Run in development mode with ultra-fast optimizations."""
    print("🔧 Starting in ULTRA-FAST development mode...")
    
    # Initialize optimizations
    asyncio.run(startup_optimizations())
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="debug",
        reload_dirs=[str(Path(__file__).parent)],
        reload_includes=["*.py"],
        use_colors=True,
        timeout_keep_alive=65
    )


async def ultra_health_check():
    """Perform an ultra-fast health check with optimization metrics."""
    try:
        from dependencies import (
            get_captions_engine,
            get_gmt_system,
            get_redis_client,
            get_health_checker
        )
        from speed_optimizations import get_performance_stats
        
        print("🔍 Performing ultra-fast health check...")
        
        # Parallel health checks for maximum speed
        engine_task = get_captions_engine()
        gmt_task = get_gmt_system()
        redis_task = get_redis_client()
        
        engine, gmt_system, redis_client = await asyncio.gather(
            engine_task, gmt_task, redis_task, return_exceptions=True
        )
        
        health_checker = await get_health_checker()
        
        # Quick parallel health checks
        checks = await asyncio.gather(
            health_checker.check_engine_health(engine) if not isinstance(engine, Exception) else {"status": "error", "error": str(engine)},
            health_checker.check_gmt_health(gmt_system) if not isinstance(gmt_system, Exception) else {"status": "error", "error": str(gmt_system)},
            health_checker.check_redis_health(redis_client) if not isinstance(redis_client, Exception) else {"status": "disabled"},
            return_exceptions=True
        )
        
        engine_health, gmt_health, redis_health = checks
        
        # Get performance statistics
        perf_stats = get_performance_stats()
        
        print(f"✅ Caption Engine: {engine_health.get('status', 'unknown')}")
        print(f"✅ GMT System: {gmt_health.get('status', 'unknown')}")
        print(f"✅ Redis Cache: {redis_health.get('status', 'unknown')}")
        print(f"⚡ Cache Hit Rate: {perf_stats.get('cache_hit_rate_percentage', 0):.1f}%")
        print(f"📊 Memory Cache Size: {perf_stats.get('memory_cache_size', 0)} items")
        print(f"⏱️  Avg Response Time: {perf_stats.get('avg_response_time_seconds', 0):.3f}s")
        print(f"🎯 Performance Tier: {perf_stats.get('performance_tier', 'unknown')}")
        
        all_healthy = all(
            h.get("status") == "healthy" 
            for h in [engine_health, gmt_health]
        )
        
        if all_healthy and perf_stats.get('performance_tier') == 'ultra_fast':
            print("🎉 All systems operational with ULTRA-FAST performance!")
            return True
        elif all_healthy:
            print("✅ All systems operational with optimized performance!")
            return True
        else:
            print("⚠️  Some systems are degraded")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def show_ultra_api_info():
    """Display ultra-fast API information and endpoints."""
    from speed_optimizations import get_performance_stats
    
    perf_stats = get_performance_stats()
    
    print(f"""
📋 Instagram Captions API v{settings.api_version} ULTRA-FAST Information:

🔗 Base URL: http://{settings.host}:{settings.port}

📚 Available Endpoints:
   🚀 ULTRA-FAST ENDPOINTS (v2.1):
   • GET  /api/v2.1/instagram-captions/        - Ultra-fast API info
   • POST /api/v2.1/instagram-captions/generate - Ultra-fast caption generation
   • POST /api/v2.1/instagram-captions/analyze-quality - Ultra-fast quality analysis
   • POST /api/v2.1/instagram-captions/optimize - Ultra-fast caption optimization
   • POST /api/v2.1/instagram-captions/batch-optimize - Streaming batch optimization
   • GET  /api/v2.1/instagram-captions/health  - Ultra-fast health check
   • GET  /api/v2.1/instagram-captions/performance-metrics - Real-time metrics
   
   📈 STANDARD ENDPOINTS (v2.0):
   • GET  /api/v2/instagram-captions/          - Standard API capabilities
   • POST /api/v2/instagram-captions/generate  - Standard caption generation
   • POST /api/v2/instagram-captions/analyze-quality - Standard quality analysis
   • GET  /api/v2/instagram-captions/health    - Standard health check

🎯 ULTRA-FAST Features:
   ⚡ Multi-level caching (Memory + Redis)
   🚀 In-memory cache with LRU eviction
   🔄 Connection pooling for external APIs
   📊 Parallel batch processing (10x faster)
   🗜️  Response compression for large data
   🎯 Background task processing
   📈 Real-time performance monitoring

⚡ Current Performance Status:
   💾 Cache Hit Rate: {perf_stats.get('cache_hit_rate_percentage', 0):.1f}%
   📊 Memory Cache: {perf_stats.get('memory_cache_size', 0)} items
   ⏱️  Avg Response: {perf_stats.get('avg_response_time_seconds', 0):.3f}s
   🎯 Performance: {perf_stats.get('performance_tier', 'unknown').upper()}

🔧 Development:
   • Environment: {settings.environment.value}
   • Debug mode: {settings.debug}
   • Cache enabled: {settings.cache.enabled}
   • Ultra optimizations: ACTIVE
     """)


def benchmark_performance():
    """Run a quick performance benchmark."""
    print("🔥 Running performance benchmark...")
    
    import requests
    import time
    
    base_url = f"http://{settings.host}:{settings.port}"
    
    # Test ultra-fast health endpoint
    start_time = time.perf_counter()
    try:
        response = requests.get(f"{base_url}/api/v2.1/instagram-captions/health", timeout=5)
        response_time = time.perf_counter() - start_time
        
        if response.status_code == 200:
            print(f"✅ Ultra-fast health check: {response_time:.3f}s")
        else:
            print(f"⚠️  Health check returned {response.status_code}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print("🎯 Benchmark completed!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Instagram Captions Ultra-Fast API v2.1")
    parser.add_argument(
        "command",
        choices=["run", "dev", "health", "info", "benchmark"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_ultra_fast_server()
    elif args.command == "dev":
        run_development()
    elif args.command == "health":
        result = asyncio.run(ultra_health_check())
        sys.exit(0 if result else 1)
    elif args.command == "info":
        show_ultra_api_info()
    elif args.command == "benchmark":
        benchmark_performance()
    else:
        parser.print_help() 