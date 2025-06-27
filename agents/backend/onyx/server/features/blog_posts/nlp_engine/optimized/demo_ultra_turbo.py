"""
🧪 DEMO ULTRA TURBO - Maximum Speed NLP Demo
============================================

Demo del sistema ultra-turbo para demostrar velocidades extremas.
"""

import asyncio
import time
from typing import List

from ultra_turbo_engine import get_ultra_turbo_engine


async def demo_ultra_turbo_performance():
    """Demo de rendimiento ultra-turbo."""
    print("🚀 DEMO: SISTEMA NLP ULTRA-TURBO")
    print("=" * 60)
    print("⚡ Target: < 0.005ms latency, > 200K ops/s throughput")
    print("🔥 Optimizations: JIT + Parallel + HyperCache + Vectorization")
    print("=" * 60)
    
    # Create ultra-turbo engine
    engine = get_ultra_turbo_engine()
    await engine.initialize()
    
    # Test data with varying complexity
    test_datasets = {
        "micro_batch": [
            "Producto excelente",
            "Servicio terrible",
            "Calidad regular"
        ],
        "small_batch": [
            f"Texto de prueba {i} con contenido variable para análisis."
            for i in range(10)
        ],
        "medium_batch": [
            f"Análisis número {i} de un producto con características específicas y detalles técnicos."
            for i in range(100)
        ],
        "large_batch": [
            f"Evaluación completa {i} del sistema con múltiples criterios de calidad y rendimiento."
            for i in range(1000)
        ]
    }
    
    print("\n🧪 TESTING ULTRA-TURBO PERFORMANCE:")
    print("-" * 50)
    
    for dataset_name, texts in test_datasets.items():
        print(f"\n⚡ Testing {dataset_name} ({len(texts)} texts)...")
        
        # Test sentiment analysis
        start_time = time.perf_counter()
        sentiment_result = await engine.ultra_turbo_sentiment(texts)
        sentiment_time = time.perf_counter() - start_time
        
        # Test quality analysis
        start_time = time.perf_counter()
        quality_result = await engine.ultra_turbo_quality(texts)
        quality_time = time.perf_counter() - start_time
        
        # Test mixed analysis
        start_time = time.perf_counter()
        mixed_result = await engine.ultra_turbo_mixed(texts)
        mixed_time = time.perf_counter() - start_time
        
        # Display results
        print(f"   📊 Sentiment: {sentiment_time*1000:.3f}ms | {sentiment_result['throughput_ops_per_second']:.0f} ops/s")
        print(f"   📊 Quality:   {quality_time*1000:.3f}ms | {quality_result['throughput_ops_per_second']:.0f} ops/s")
        print(f"   📊 Mixed:     {mixed_time*1000:.3f}ms | {mixed_result['combined_throughput_ops_per_second']:.0f} ops/s")
        
        # Calculate per-text latency
        sentiment_per_text = (sentiment_time * 1000) / len(texts)
        quality_per_text = (quality_time * 1000) / len(texts)
        mixed_per_text = (mixed_time * 1000) / len(texts)
        
        print(f"   ⚡ Latency/text: {sentiment_per_text:.4f}ms (sentiment), {quality_per_text:.4f}ms (quality)")
        
        # Show cache performance
        sentiment_cache_ratio = sentiment_result['cache_stats']['cache_hit_ratio']
        quality_cache_ratio = quality_result['cache_stats']['cache_hit_ratio']
        
        print(f"   💾 Cache hits: {sentiment_cache_ratio:.1%} (sentiment), {quality_cache_ratio:.1%} (quality)")
    
    return True


async def demo_ultra_turbo_features():
    """Demo de características ultra-turbo."""
    print(f"\n🔧 DEMO: CARACTERÍSTICAS ULTRA-TURBO")
    print("=" * 50)
    
    engine = get_ultra_turbo_engine()
    await engine.initialize()
    
    # Test texts with different patterns
    test_texts = [
        "Este producto es absolutamente fantástico y excelente!",
        "La experiencia fue terrible y muy decepcionante.",
        "Calidad excepcional que supera todas las expectativas.",
        "Servicio deficiente con múltiples problemas técnicos.",
        "Innovación increíble que revoluciona completamente la industria."
    ]
    
    print(f"\n⚡ Ultra-Turbo Sentiment Analysis:")
    sentiment_result = await engine.ultra_turbo_sentiment(test_texts)
    
    for i, (text, score) in enumerate(zip(test_texts, sentiment_result['scores'])):
        print(f"   {i+1}. Score: {score:.2f} | {text[:50]}...")
    
    print(f"\n   📊 Average: {sentiment_result['average']:.2f}")
    print(f"   ⚡ Speed: {sentiment_result['throughput_ops_per_second']:.0f} ops/s")
    print(f"   💾 Cache ratio: {sentiment_result['cache_stats']['cache_hit_ratio']:.1%}")
    
    print(f"\n📊 Ultra-Turbo Quality Analysis:")
    quality_result = await engine.ultra_turbo_quality(test_texts)
    
    for i, (text, score) in enumerate(zip(test_texts, quality_result['scores'])):
        print(f"   {i+1}. Quality: {score:.2f} | {text[:50]}...")
    
    print(f"\n   📊 Average: {quality_result['average']:.2f}")
    print(f"   ⚡ Speed: {quality_result['throughput_ops_per_second']:.0f} ops/s")
    print(f"   💾 Cache ratio: {quality_result['cache_stats']['cache_hit_ratio']:.1%}")
    
    # Mixed analysis demo
    print(f"\n🔥 Ultra-Turbo Mixed Analysis:")
    mixed_result = await engine.ultra_turbo_mixed(test_texts)
    
    print(f"   ⚡ Combined speed: {mixed_result['combined_throughput_ops_per_second']:.0f} ops/s")
    print(f"   📊 Total operations: {mixed_result['performance_summary']['total_operations']}")
    print(f"   ⚡ Processing time: {mixed_result['total_processing_time_ms']:.2f}ms")
    
    return mixed_result


async def demo_ultra_turbo_benchmark():
    """Demo de benchmark completo ultra-turbo."""
    print(f"\n🧪 DEMO: BENCHMARK ULTRA-TURBO COMPLETO")
    print("=" * 55)
    
    engine = get_ultra_turbo_engine()
    await engine.initialize()
    
    # Run comprehensive benchmark
    benchmark_sizes = [100, 500, 1000, 2000]
    
    for size in benchmark_sizes:
        print(f"\n🔥 Benchmarking {size} texts...")
        
        benchmark_result = await engine.benchmark_ultra_turbo(size)
        
        print(f"   📊 Sentiment: {benchmark_result['sentiment_benchmark']['throughput_ops_per_second']:.0f} ops/s")
        print(f"   📊 Quality:   {benchmark_result['quality_benchmark']['throughput_ops_per_second']:.0f} ops/s")
        print(f"   🔥 Mixed:     {benchmark_result['mixed_benchmark']['throughput_ops_per_second']:.0f} ops/s")
        
        # Show fastest operation
        fastest_ms = benchmark_result['performance_summary']['fastest_single_operation_ms']
        print(f"   ⚡ Fastest op: {fastest_ms:.4f}ms per text")
        
        # Show peak throughput
        peak_throughput = benchmark_result['performance_summary']['peak_throughput_ops_per_second']
        print(f"   🚀 Peak speed: {peak_throughput:.0f} ops/s")
    
    # Get final system stats
    final_stats = await engine.get_ultra_turbo_stats()
    
    print(f"\n📊 FINAL SYSTEM STATS:")
    print(f"   • Total requests: {final_stats['total_requests']}")
    print(f"   • Overall throughput: {final_stats['overall_throughput_ops_per_second']:.0f} ops/s")
    print(f"   • Average latency: {final_stats['average_latency_ms']:.3f}ms")
    print(f"   • Success rate: {final_stats['success_rate']:.1%}")
    
    # Cache performance
    cache_stats = final_stats['hyper_cache']
    print(f"   • Cache hit ratio: {cache_stats['hit_ratio']:.1%}")
    print(f"   • L1 cache hits: {cache_stats['l1_hit_ratio']:.1%}")
    print(f"   • L2 cache hits: {cache_stats['l2_hit_ratio']:.1%}")
    
    return final_stats


async def main():
    """Función principal del demo ultra-turbo."""
    print("⚡ INICIANDO DEMO SISTEMA ULTRA-TURBO")
    print("🚀 Maximum Speed NLP Engine")
    print("=" * 70)
    
    try:
        # Demo performance
        await demo_ultra_turbo_performance()
        
        # Demo features
        await demo_ultra_turbo_features()
        
        # Demo benchmark
        await demo_ultra_turbo_benchmark()
        
        print(f"\n🎉 DEMO ULTRA-TURBO COMPLETADO EXITOSAMENTE!")
        print(f"✅ Sistema optimizado al máximo rendimiento")
        print(f"⚡ Velocidades extremas demostradas")
        print(f"🔥 Ultra-Turbo engine funcionando perfectamente")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 