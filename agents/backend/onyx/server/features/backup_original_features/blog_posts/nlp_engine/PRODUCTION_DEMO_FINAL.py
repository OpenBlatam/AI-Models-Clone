"""
🚀 PRODUCTION DEMO FINAL - Ultra-Optimized NLP Engine
====================================================

Demo de producción enterprise ultra-optimizado.
"""

import asyncio
import time
from typing import Dict, Any, List

# Core NLP Engine
from . import NLPEngine, AnalysisType, ProcessingTier

# Optimized modules
from .optimized import (
    get_optimized_serializer,
    get_optimized_cache,
    get_optimized_processor,
    get_optimized_client
)


class ProductionNLPDemo:
    """Demo de producción enterprise ultra-optimizado."""
    
    def __init__(self):
        self.nlp_engine = None
        self.serializer = get_optimized_serializer()
        self.cache = get_optimized_cache()
        self.processor = get_optimized_processor()
        self.client = get_optimized_client()
    
    async def initialize(self):
        """Inicializar componentes."""
        print("🚀 Inicializando demo de producción...")
        
        # Inicializar motor NLP
        self.nlp_engine = NLPEngine()
        await self.nlp_engine.initialize()
        
        # Inicializar cache L2
        await self.cache.initialize_l2()
        
        print("✅ Inicialización completa")
    
    async def demo_single_analysis(self, text: str) -> Dict[str, Any]:
        """Demo de análisis individual."""
        start_time = time.perf_counter()
        
        # Análisis con motor NLP
        analysis_result = await self.nlp_engine.analyze(
            text=text,
            analysis_types=[AnalysisType.SENTIMENT, AnalysisType.QUALITY_ASSESSMENT],
            tier=ProcessingTier.ULTRA_FAST
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            "success": True,
            "analysis": {
                "sentiment_score": analysis_result.get_sentiment_score(),
                "quality_score": analysis_result.get_quality_score(),
                "performance_grade": analysis_result.get_performance_grade()
            },
            "performance": {
                "duration_ms": duration_ms
            }
        }
    
    async def demo_batch_analysis(self, texts: List[str]) -> Dict[str, Any]:
        """Demo de análisis en lote."""
        start_time = time.perf_counter()
        
        def analyze_text(text: str) -> Dict[str, Any]:
            word_count = len(text.split())
            sentiment_score = 0.7 if "bueno" in text.lower() else 0.3
            quality_score = min(1.0, word_count / 50.0)
            
            return {
                "text_preview": text[:50] + "..." if len(text) > 50 else text,
                "sentiment_score": sentiment_score,
                "quality_score": quality_score,
                "performance_grade": "A" if quality_score > 0.8 else "B"
            }
        
        results = await self.processor.process_batch_async(
            texts, analyze_text, max_concurrency=50
        )
        
        valid_results = [r for r in results if r is not None]
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            "success": True,
            "total_texts": len(texts),
            "successful": len(valid_results),
            "results": valid_results,
            "performance": {
                "total_duration_ms": duration_ms,
                "throughput_texts_per_second": len(texts) / (duration_ms / 1000)
            }
        }
    
    async def run_production_demo(self):
        """Ejecutar demo completo."""
        print("=" * 60)
        print("🚀 DEMO DE PRODUCCIÓN - MOTOR NLP ULTRA-OPTIMIZADO")
        print("=" * 60)
        
        await self.initialize()
        
        # Test data
        test_texts = [
            "Este es un texto de prueba excelente.",
            "El producto es bueno y lo recomiendo.",
            "No me gustó el servicio.",
            "La calidad es muy buena.",
            "Estoy satisfecho con la compra."
        ] * 10
        
        # Single analysis test
        print("\n🎯 Test de análisis individual...")
        single_result = await self.demo_single_analysis(test_texts[0])
        
        # Batch analysis test
        print("📦 Test de análisis en lote...")
        batch_result = await self.demo_batch_analysis(test_texts[:20])
        
        # Results
        print("\n" + "=" * 60)
        print("📈 RESULTADOS")
        print("=" * 60)
        
        print(f"⚡ Análisis Individual:")
        print(f"   • Latencia: {single_result['performance']['duration_ms']:.2f}ms")
        print(f"   • Sentiment: {single_result['analysis']['sentiment_score']:.2f}")
        print(f"   • Quality: {single_result['analysis']['quality_score']:.2f}")
        
        print(f"\n📦 Análisis en Lote:")
        print(f"   • Textos: {batch_result['total_texts']}")
        print(f"   • Exitosos: {batch_result['successful']}")
        print(f"   • Throughput: {batch_result['performance']['throughput_texts_per_second']:.1f} textos/s")
        
        print(f"\n🎉 DEMO COMPLETADO")
        
        return {
            "single_analysis": single_result,
            "batch_analysis": batch_result
        }


async def main():
    """Función principal."""
    demo = ProductionNLPDemo()
    
    try:
        await demo.run_production_demo()
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 