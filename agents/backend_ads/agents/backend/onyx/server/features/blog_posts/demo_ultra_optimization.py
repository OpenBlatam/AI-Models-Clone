#!/usr/bin/env python3
"""
Demo Ultra Blog Optimization - Demonstración de Capacidades Avanzadas

Este script demuestra todas las optimizaciones implementadas para generar
blogs de súper calidad a velocidad máxima.
"""

import asyncio
import time
import json
from typing import List
from datetime import datetime

from domains.content import (
    UltraBlogEngine, 
    GenerationMode, 
    ContentRequest,
    SuperQualityContentGenerator,
    TurboContentGenerator
)
from config import BlogPostConfig


class OptimizationDemo:
    """Demostración completa de optimizaciones ultra."""
    
    def __init__(self):
        # Configuración ultra-optimizada
        self.config = BlogPostConfig(
            # AI Configuration
            ai_model="gpt-4-turbo",
            ai_temperature=0.7,
            ai_max_tokens=4096,
            
            # Performance Settings
            enable_batch_processing=True,
            batch_size=8,
            max_concurrent_generations=16,
            generation_timeout=60,
            
            # Cache Settings
            enable_caching=True,
            cache_ttl=7200,  # 2 horas
            max_cache_size=10000,
            
            # Quality Settings
            enable_html_sanitization=True,
            enable_auto_formatting=True,
            enable_readability_check=True,
            min_readability_score=75.0,
            
            # SEO Settings
            seo_level="expert",
            target_keyword_density=1.5,
            enable_schema_markup=True
        )
        
        # Inicializar motores
        self.ultra_engine = UltraBlogEngine(self.config)
        self.quality_engine = SuperQualityContentGenerator(self.config)
        self.speed_engine = TurboContentGenerator(self.config)
        
        print("🚀 Ultra Blog Optimization Demo Iniciado")
        print("=" * 60)
    
    async def demo_complete(self):
        """Ejecutar demostración completa de todas las capacidades."""
        
        print("\n🎯 INICIANDO DEMO COMPLETO DE OPTIMIZACIÓN ULTRA")
        print("=" * 60)
        
        # Demo 1: Velocidad vs Calidad
        await self._demo_speed_vs_quality()
        
        # Demo 2: Modos de generación
        await self._demo_generation_modes()
        
        # Demo 3: Generación en lote
        await self._demo_batch_generation()
        
        # Demo 4: Optimización adaptativa
        await self._demo_adaptive_optimization()
        
        # Demo 5: Métricas y monitoreo
        await self._demo_metrics_monitoring()
        
        print("\n🏆 DEMO COMPLETO FINALIZADO")
        print("=" * 60)
    
    async def _demo_speed_vs_quality(self):
        """Demostrar diferencias entre velocidad y calidad."""
        
        print("\n📊 DEMO 1: VELOCIDAD vs CALIDAD")
        print("-" * 40)
        
        request = ContentRequest(
            topic="Inteligencia Artificial en el Marketing Digital 2024",
            target_audience="Marketers y empresarios",
            keywords=["IA", "marketing digital", "automatización", "ROI"],
            length_words=1200,
            tone="professional",
            include_seo=True
        )
        
        # Test de velocidad máxima
        print("⚡ Generando con VELOCIDAD MÁXIMA...")
        start_time = time.time()
        speed_result = await self.speed_engine.turbo_generate(request, "ludicrous")
        speed_time = int((time.time() - start_time) * 1000)
        
        print(f"   ✅ Completado en {speed_time}ms")
        print(f"   📝 {speed_result.word_count} palabras")
        
        # Test de calidad máxima
        print("\n💎 Generando con CALIDAD MÁXIMA...")
        start_time = time.time()
        quality_result = await self.quality_engine.generate_super_quality_content(request, "premium")
        quality_time = int((time.time() - start_time) * 1000)
        
        print(f"   ✅ Completado en {quality_time}ms")
        print(f"   📝 {quality_result.word_count} palabras")
        if quality_result.metadata and 'quality_metrics' in quality_result.metadata:
            metrics = quality_result.metadata['quality_metrics']
            print(f"   📊 Calidad: {metrics['overall_score']:.1f}/100")
        
        # Test ultra (velocidad + calidad)
        print("\n🚀 Generando con ULTRA ENGINE (Velocidad + Calidad)...")
        start_time = time.time()
        ultra_result = await self.ultra_engine.generate_ultra_blog(
            request, 
            mode=GenerationMode.LUDICROUS,
            priority="balanced"
        )
        ultra_time = int((time.time() - start_time) * 1000)
        
        print(f"   ✅ Completado en {ultra_time}ms")
        print(f"   📝 {ultra_result.word_count} palabras")
        
        # Comparación
        print(f"\n📈 COMPARACIÓN DE RESULTADOS:")
        print(f"   ⚡ Velocidad Pura: {speed_time}ms")
        print(f"   💎 Calidad Pura: {quality_time}ms")
        print(f"   🚀 Ultra Engine: {ultra_time}ms")
        print(f"   🎯 Eficiencia Ultra: {((speed_time + quality_time) / 2) / ultra_time:.1f}x mejor")
    
    async def _demo_generation_modes(self):
        """Demostrar diferentes modos de generación."""
        
        print("\n🏃‍♂️ DEMO 2: MODOS DE GENERACIÓN")
        print("-" * 40)
        
        request = ContentRequest(
            topic="Blockchain y Criptomonedas para Principiantes",
            target_audience="Inversores novatos",
            length_words=1000,
            tone="friendly"
        )
        
        modes = [
            (GenerationMode.LIGHTNING, "⚡"),
            (GenerationMode.TURBO, "🏎️"),
            (GenerationMode.PREMIUM, "💎"),
            (GenerationMode.ULTRA, "🔥"),
            (GenerationMode.LUDICROUS, "🚀")
        ]
        
        results = []
        
        for mode, emoji in modes:
            print(f"\n{emoji} Probando modo {mode.value.upper()}...")
            start_time = time.time()
            
            try:
                result = await self.ultra_engine.generate_ultra_blog(
                    request, 
                    mode=mode,
                    priority="balanced"
                )
                generation_time = int((time.time() - start_time) * 1000)
                
                print(f"   ✅ {generation_time}ms - {result.word_count} palabras")
                results.append((mode.value, generation_time, result.word_count))
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        # Mostrar resumen
        print(f"\n📊 RESUMEN DE MODOS:")
        for mode_name, time_ms, words in results:
            efficiency = words / time_ms if time_ms > 0 else 0
            print(f"   {mode_name:12} | {time_ms:4}ms | {words:4} palabras | {efficiency:.1f} p/ms")
    
    async def _demo_batch_generation(self):
        """Demostrar generación en lote optimizada."""
        
        print("\n📦 DEMO 3: GENERACIÓN EN LOTE")
        print("-" * 40)
        
        # Crear múltiples requests
        requests = [
            ContentRequest(
                topic="Python para Data Science",
                target_audience="Científicos de datos",
                length_words=800
            ),
            ContentRequest(
                topic="JavaScript Frameworks Modernos",
                target_audience="Desarrolladores frontend",
                length_words=900
            ),
            ContentRequest(
                topic="DevOps y Automatización",
                target_audience="Ingenieros de sistemas",
                length_words=850
            ),
            ContentRequest(
                topic="Machine Learning con TensorFlow",
                target_audience="Desarrolladores ML",
                length_words=950
            ),
            ContentRequest(
                topic="Arquitectura de Microservicios",
                target_audience="Arquitectos de software",
                length_words=1000
            )
        ]
        
        print(f"🎯 Generando {len(requests)} blogs en lote...")
        start_time = time.time()
        
        results = await self.ultra_engine.batch_generate_ultra(
            requests,
            mode=GenerationMode.TURBO,
            priority="speed",
            max_concurrent=8
        )
        
        total_time = int((time.time() - start_time) * 1000)
        successful = len([r for r in results if r.success])
        total_words = sum(r.word_count for r in results if r.success)
        
        print(f"   ✅ {successful}/{len(requests)} blogs generados exitosamente")
        print(f"   ⏱️ Tiempo total: {total_time}ms")
        print(f"   📝 Total palabras: {total_words}")
        print(f"   🚀 Throughput: {successful / (total_time / 1000):.1f} blogs/segundo")
        print(f"   ⚡ Promedio por blog: {total_time / successful:.0f}ms")
        
        # Mostrar detalles individuales
        print(f"\n📋 DETALLE DE BLOGS GENERADOS:")
        for i, result in enumerate(results[:3], 1):  # Solo mostrar primeros 3
            if result.success:
                print(f"   {i}. {result.word_count} palabras - {result.generation_time_ms}ms")
    
    async def _demo_adaptive_optimization(self):
        """Demostrar optimización adaptativa."""
        
        print("\n🧠 DEMO 4: OPTIMIZACIÓN ADAPTATIVA")
        print("-" * 40)
        
        # Simular feedback del usuario
        user_feedback = {
            "prefer_speed": True,
            "prefer_quality": False,
            "satisfaction_score": 8,
            "favorite_mode": "turbo"
        }
        
        print("📝 Aplicando feedback del usuario...")
        print(f"   - Prefiere velocidad: {user_feedback['prefer_speed']}")
        print(f"   - Satisfacción: {user_feedback['satisfaction_score']}/10")
        
        # Aplicar optimización
        await self.ultra_engine.optimize_for_user_preferences(user_feedback)
        print("   ✅ Optimización aplicada")
        
        # Test antes y después
        request = ContentRequest(
            topic="Optimización de Conversiones en E-commerce",
            target_audience="Propietarios de tiendas online",
            length_words=1200
        )
        
        print("\n🔄 Comparando rendimiento optimizado...")
        start_time = time.time()
        result = await self.ultra_engine.generate_ultra_blog(request, priority="speed")
        optimized_time = int((time.time() - start_time) * 1000)
        
        print(f"   ⚡ Tiempo optimizado: {optimized_time}ms")
        print(f"   🎯 Modo seleccionado: {result.metadata.get('speed_mode', 'N/A')}")
    
    async def _demo_metrics_monitoring(self):
        """Demostrar métricas y monitoreo."""
        
        print("\n📊 DEMO 5: MÉTRICAS Y MONITOREO")
        print("-" * 40)
        
        # Obtener dashboard de rendimiento
        dashboard = self.ultra_engine.get_performance_dashboard()
        
        print("📈 Dashboard de Rendimiento:")
        if dashboard.get("status") == "no_data":
            print("   ℹ️ No hay datos suficientes aún")
        else:
            print(f"   📊 Total generaciones: {dashboard.get('total_generations', 0)}")
            print(f"   ⚡ Tiempo promedio: {dashboard.get('average_generation_time_ms', 0):.0f}ms")
            print(f"   💎 Calidad promedio: {dashboard.get('average_quality_score', 0):.1f}/100")
            print(f"   🎯 Efectividad: {dashboard.get('optimization_effectiveness', 'N/A')}")
        
        # Estadísticas de velocidad
        speed_stats = self.speed_engine.get_speed_statistics()
        print(f"\n⚡ Estadísticas de Velocidad:")
        print(f"   🎯 Cache hit rate: {speed_stats.get('cache_hit_rate', 0)*100:.1f}%")
        print(f"   📦 Tamaño de caché: {speed_stats.get('cache_size', 0)}")
        print(f"   🚀 Throughput: {speed_stats.get('average_throughput_per_second', 0):.1f} blogs/seg")
        
        # Recomendaciones
        recommendations = dashboard.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recomendaciones:")
            for rec in recommendations:
                print(f"   • {rec}")
    
    async def demo_quick_benchmark(self):
        """Benchmark rápido para demostrar capacidades."""
        
        print("\n🏁 BENCHMARK RÁPIDO")
        print("=" * 40)
        
        # Test de velocidad con múltiples requests
        requests = [
            ContentRequest(
                topic=f"Tema de Prueba {i+1}",
                target_audience="Audiencia general",
                length_words=500
            ) for i in range(10)
        ]
        
        print(f"🎯 Generando {len(requests)} blogs de prueba...")
        
        # Medir diferentes enfoques
        approaches = [
            ("Ultra Engine TURBO", lambda r: self.ultra_engine.generate_ultra_blog(r, GenerationMode.TURBO)),
            ("Speed Engine", lambda r: self.speed_engine.turbo_generate(r, "ultra")),
            ("Quality Engine", lambda r: self.quality_engine.generate_super_quality_content(r, "premium"))
        ]
        
        for approach_name, generator in approaches:
            print(f"\n🔧 Probando {approach_name}...")
            start_time = time.time()
            
            # Generar solo los primeros 3 para demo rápido
            test_requests = requests[:3]
            
            if "Engine" in approach_name and "Ultra" not in approach_name:
                # Para engines individuales, generar secuencialmente
                results = []
                for req in test_requests:
                    try:
                        result = await generator(req)
                        results.append(result)
                    except Exception as e:
                        print(f"     ❌ Error: {str(e)}")
                        continue
            else:
                # Para Ultra Engine, usar batch
                try:
                    results = await self.ultra_engine.batch_generate_ultra(
                        test_requests, 
                        mode=GenerationMode.TURBO,
                        max_concurrent=3
                    )
                except Exception as e:
                    print(f"     ❌ Error: {str(e)}")
                    continue
            
            total_time = int((time.time() - start_time) * 1000)
            successful = len([r for r in results if hasattr(r, 'success') and r.success])
            
            if successful > 0:
                avg_time = total_time / successful
                total_words = sum(r.word_count for r in results if hasattr(r, 'word_count'))
                print(f"     ✅ {successful} blogs - {total_time}ms total")
                print(f"     ⚡ {avg_time:.0f}ms promedio por blog")
                print(f"     📝 {total_words} palabras total")
            else:
                print(f"     ❌ No se generaron blogs exitosamente")


async def main():
    """Función principal para ejecutar la demo."""
    
    demo = OptimizationDemo()
    
    print("🚀 ULTRA BLOG OPTIMIZATION DEMO")
    print("Selecciona el tipo de demo:")
    print("1. Demo completo (todas las funciones)")
    print("2. Benchmark rápido")
    print("3. Demo específico de velocidad vs calidad")
    
    try:
        # Para propósitos de demo, ejecutamos el benchmark rápido
        choice = "2"
        
        if choice == "1":
            await demo.demo_complete()
        elif choice == "2":
            await demo.demo_quick_benchmark()
        elif choice == "3":
            await demo._demo_speed_vs_quality()
        else:
            print("❌ Opción inválida")
            return
            
        print("\n🎉 ¡Demo completado exitosamente!")
        print("\n💡 Próximos pasos:")
        print("   1. Configura tus temas y audiencias favoritos")
        print("   2. Experimenta con diferentes modos de generación")
        print("   3. Usa el modo LUDICROUS para máxima calidad y velocidad")
        print("   4. Monitorea las métricas para optimización continua")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en demo: {str(e)}")


if __name__ == "__main__":
    # Ejecutar la demo
    asyncio.run(main()) 