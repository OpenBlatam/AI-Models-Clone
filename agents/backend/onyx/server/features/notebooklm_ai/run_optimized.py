#!/usr/bin/env python3
"""
Simple Runner for Optimized NotebookLM AI System
Quick execution with performance monitoring
"""

import asyncio
import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def run_basic_optimization():
    """Run basic optimization"""
    print("🚀 Starting NotebookLM AI Optimization...")
    
    try:
        from optimized_main import OptimizedNotebookLMAI
        
        ai_system = OptimizedNotebookLMAI()
        
        # Load configuration
        print("📋 Loading configuration...")
        config_result = await ai_system.load_configuration()
        print(f"✅ Configuration: {config_result.get('config_loaded', False)}")
        
        # Setup middleware
        print("🔧 Setting up middleware...")
        middleware_result = await ai_system.setup_middleware()
        print(f"✅ Middleware: {middleware_result.get('middleware_configured', False)}")
        
        # Optimize system
        print("⚡ Optimizing system...")
        optimization_result = await ai_system.optimize_system()
        print(f"✅ Optimization: {optimization_result.get('status', 'failed')}")
        
        # Get performance metrics
        metrics = ai_system.get_performance_metrics()
        print(f"📊 Performance - CPU: {metrics['cpu_percent']:.1f}%, "
              f"Memory: {metrics['memory_usage_mb']:.1f}MB")
        
        print("🎉 Basic optimization completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def run_ultra_optimization():
    """Run ultra optimization"""
    print("🚀 Starting Ultra Optimization...")
    
    try:
        from ultra_optimized_runner import UltraOptimizedRunner
        
        with UltraOptimizedRunner() as runner:
            # Optimize resources
            print("⚡ Optimizing resources...")
            await runner.optimize_memory()
            await runner.optimize_cpu()
            await runner.optimize_io()
            
            # Run optimized operations
            print("🔍 Running optimized scanning...")
            targets = [f"target{i}.com" for i in range(100)]
            scan_result = await runner.run_optimized_scan(targets)
            print(f"✅ Scan: {scan_result['throughput']:.2f} targets/sec")
            
            # Process batch data
            print("📦 Processing batch data...")
            data = [{"id": i, "payload": f"data_{i}"} for i in range(1000)]
            process_result = await runner.process_ultra_batch(data)
            print(f"✅ Processing: {process_result['throughput']:.2f} items/sec")
            
            # Get metrics
            metrics = await runner.get_ultra_metrics()
            print(f"📊 Memory: {metrics['performance']['memory_rss_mb']:.2f}MB, "
                  f"CPU: {metrics['performance']['cpu_percent']:.1f}%")
        
        print("🎉 Ultra optimization completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def run_performance_monitoring():
    """Run performance monitoring"""
    print("📊 Starting Performance Monitoring...")
    
    try:
        from performance_monitor import OptimizedPerformanceMonitor
        
        monitor = OptimizedPerformanceMonitor(monitor_interval=1.0)
        
        # Start monitoring
        await monitor.start_monitoring()
        
        # Monitor for 10 seconds
        for i in range(10):
            await asyncio.sleep(1)
            
            current = monitor.get_current_metrics()
            if current:
                print(f"📈 CPU: {current['cpu_percent']:.1f}%, "
                      f"Memory: {current['memory_mb']:.1f}MB")
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        # Get summary
        summary = monitor.get_performance_summary()
        if summary:
            print(f"📊 Summary - CPU avg: {summary['cpu']['average']:.1f}%, "
                  f"Memory avg: {summary['memory']['average_percent']:.1f}%")
        
        print("✅ Performance monitoring completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Main runner"""
    print("=" * 50)
    print("🎯 NotebookLM AI Optimization Runner")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "basic"
    
    start_time = time.time()
    
    if mode == "basic":
        success = await run_basic_optimization()
    elif mode == "ultra":
        success = await run_ultra_optimization()
    elif mode == "monitor":
        success = await run_performance_monitoring()
    elif mode == "all":
        print("🔄 Running all optimizations...")
        success1 = await run_basic_optimization()
        success2 = await run_ultra_optimization()
        success3 = await run_performance_monitoring()
        success = success1 and success2 and success3
    else:
        print(f"❌ Unknown mode: {mode}")
        print("Available modes: basic, ultra, monitor, all")
        return
    
    duration = time.time() - start_time
    
    if success:
        print(f"✅ All operations completed successfully in {duration:.2f} seconds")
    else:
        print(f"❌ Some operations failed after {duration:.2f} seconds")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 