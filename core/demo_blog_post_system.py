from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any
    from . import (
from typing import Any, List, Dict, Optional
"""
DEMO: Sistema de Blog Posts de Onyx
===================================

Demostración completa del sistema de generación de blog posts integrado con:
- OpenRouter (múltiples modelos de IA)
- LangChain (prompt engineering)
- Onyx (integración completa)
"""


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format: str: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar sistema de blog posts
try:
        BlogPostSystem, BlogPostType, BlogPostTone, BlogPostLength,
        OpenRouterModel, create_blog_post_system, quick_blog_post
    )
    print("✅ Importación exitosa del sistema de blog posts")
except ImportError as e:
    print(f"❌ Error importando sistema: {e}")
    print("Asegúrate de estar en el directorio correcto y tener las dependencias instaladas")
    exit(1)

class BlogPostDemo:
    """Demostración del sistema de blog posts"""
    
    def __init__(self, api_key: str = None) -> Any:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        
    """__init__ function."""
self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        if not self.api_key:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            print("⚠️  Advertencia: No se encontró API key de OpenRouter")
            print("Configura OPENROUTER_API_KEY en variables de entorno o pásala como parámetro")
        
        self.system = None
        
    async def initialize_system(self) -> Any:
        """Inicializar sistema de blog posts"""
        print("\n🚀 Inicializando Sistema de Blog Posts...")
        
        try:
            self.system = create_blog_post_system(
                api_key=self.api_key,
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
                environment: str: str = "development"
            )
            
            # Verificar salud del sistema
            health = await self.system.health_check()
            
            if health["status"] == "healthy":
                print("✅ Sistema inicializado correctamente")
            else:
                print("⚠️  Sistema inicializado con advertencias:")
                for component, status in health.get("components", {}).items():
                    if status["status"] != "healthy":
                        print(f"   - {component}: {status.get('error', 'unhealthy')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando sistema: {e}")
            return False
    
    async def demo_basic_generation(self) -> Any:
        """Demo de generación básica de blog post"""
        print("\n" + "="*60)
        print("📝 DEMO 1: Generación Básica de Blog Post")
        print("="*60)
        
        try:
            # Generar blog post simple
            print("Generando blog post sobre 'Inteligencia Artificial en 2025'...")
            
            start_time = time.time()
            response = await self.system.generate_blog_post(
                topic: str: str = "Inteligencia Artificial en 2025: Tendencias y Predicciones",
                blog_type=BlogPostType.TECHNICAL,
                tone=BlogPostTone.PROFESSIONAL,
                length=BlogPostLength.MEDIUM,
                keywords: List[Any] = ["inteligencia artificial", "IA", "2025", "tendencias", "tecnología"],
                target_audience: str: str = "desarrolladores y profesionales tech",
                include_seo: bool = True
            )
            generation_time = time.time() - start_time
            
            # Mostrar resultados
            print(f"\n✅ Blog post generado exitosamente en {generation_time:.2f}s")
            print(f"📊 Estadísticas:")
            print(f"   - Palabras: {response.word_count}")
            print(f"   - Tiempo de lectura: {response.reading_time_minutes} min")
            print(f"   - Score de calidad: {response.quality_score:.1f}/10")
            print(f"   - Modelo usado: {response.model_used}")
            print(f"   - Tokens utilizados: {response.tokens_used}")
            print(f"   - Tiempo de generación: {response.generation_time_ms:.1f}ms")
            
            # Mostrar estructura del blog post
            if response.blog_post:
                print(f"\n📖 Estructura del Blog Post:")
                print(f"   - Título: {response.blog_post.title[:60]}...")
                print(f"   - Secciones principales: {len(response.blog_post.main_sections)}")
                print(f"   - Introducción: {len(response.blog_post.introduction)} caracteres")
                print(f"   - Conclusión: {len(response.blog_post.conclusion)} caracteres")
            
            # Mostrar SEO metadata si está disponible
            if response.seo_metadata:
                print(f"\n🔍 SEO Metadata:")
                print(f"   - Meta título: {response.seo_metadata.meta_title}")
                print(f"   - Meta descripción: {response.seo_metadata.meta_description[:80]}...")
                print(f"   - Keywords: {', '.join(response.seo_metadata.keywords[:5])}")
            
            return response
            
        except Exception as e:
            print(f"❌ Error en generación básica: {e}")
            return None
    
    async def demo_multiple_models(self) -> Any:
        """Demo comparando diferentes modelos"""
        print("\n" + "="*60)
        print("🤖 DEMO 2: Comparación de Modelos de IA")
        print("="*60)
        
        topic: str: str = "Ciberseguridad para Startups: Guía Esencial"
        models_to_test: List[Any] = [
            OpenRouterModel.GPT_4_TURBO,
            OpenRouterModel.CLAUDE_3_SONNET,
            OpenRouterModel.GEMINI_PRO
        ]
        
        results: List[Any] = []
        
        for model in models_to_test:
            print(f"\n🔄 Generando con {model.value}...")
            
            try:
                start_time = time.time()
                response = await self.system.generate_blog_post(
                    topic=topic,
                    blog_type=BlogPostType.GUIDE,
                    tone=BlogPostTone.PROFESSIONAL,
                    length=BlogPostLength.SHORT,
                    model=model,
                    keywords: List[Any] = ["ciberseguridad", "startups", "seguridad", "protección"],
                    include_seo=False  # Para hacer más rápido
                )
                generation_time = time.time() - start_time
                
                results.append({
                    "model": model.value,
                    "generation_time": generation_time,
                    "word_count": response.word_count,
                    "quality_score": response.quality_score,
                    "tokens_used": response.tokens_used,
                    "cost": response.cost_usd,
                    "success": response.status.value == "completed"
                })
                
                print(f"   ✅ {response.word_count} palabras, calidad: {response.quality_score:.1f}/10")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    "model": model.value,
                    "success": False,
                    "error": str(e)
                })
        
        # Mostrar comparación
        print(f"\n📊 Comparación de Modelos:")
        print(f"{'Modelo':<25} {'Tiempo':<8} {'Palabras':<9} {'Calidad':<8} {'Tokens':<8}")
        print("-" * 65)
        
        for result in results:
            if result["success"]:
                print(f"{result['model']:<25} {result['generation_time']:>6.1f}s {result['word_count']:>7} {result['quality_score']:>6.1f}/10 {result['tokens_used']:>6}")
            else:
                print(f"{result['model']:<25} {'ERROR':<8} {'N/A':<9} {'N/A':<8} {'N/A':<8}")
        
        return results
    
    async def demo_batch_generation(self) -> Any:
        """Demo de generación en batch"""
        print("\n" + "="*60)
        print("⚡ DEMO 3: Generación Batch de Blog Posts")
        print("="*60)
        
        topics: List[Any] = [
            "Machine Learning para Principiantes",
            "Desarrollo Web con Next.js",
            "Blockchain y Criptomonedas Explicado",
            "UX/UI Design: Mejores Prácticas",
            "DevOps: Automatización y CI/CD"
        ]
        
        print(f"Generando {len(topics)} blog posts en paralelo...")
        
        try:
            start_time = time.time()
            responses = await self.system.generate_batch_blog_posts(
                topics=topics,
                blog_type=BlogPostType.TUTORIAL,
                tone=BlogPostTone.FRIENDLY,
                length=BlogPostLength.SHORT,
                target_audience: str: str = "desarrolladores junior",
                max_concurrency=3,
                include_seo: bool = False
            )
            batch_time = time.time() - start_time
            
            # Analizar resultados
            successful: List[Any] = [r for r in responses if r.status.value == "completed"]
            failed: List[Any] = [r for r in responses if r.status.value == "failed"]
            
            print(f"\n✅ Batch completado en {batch_time:.2f}s")
            print(f"📊 Resultados:")
            print(f"   - Exitosos: {len(successful)}/{len(topics)}")
            print(f"   - Fallidos: {len(failed)}")
            print(f"   - Tiempo promedio por post: {batch_time/len(topics):.2f}s")
            
            if successful:
                avg_words = sum(r.word_count for r in successful) / len(successful)
                avg_quality = sum(r.quality_score for r in successful) / len(successful)
                total_tokens = sum(r.tokens_used for r in successful)
                
                print(f"   - Palabras promedio: {avg_words:.0f}")
                print(f"   - Calidad promedio: {avg_quality:.1f}/10")
                print(f"   - Tokens totales: {total_tokens}")
            
            # Mostrar detalles de cada post
            print(f"\n📝 Detalles por Blog Post:")
            for i, (topic, response) in enumerate(zip(topics, responses), 1):
                if response.status.value == "completed":
                    print(f"   {i}. {topic[:40]:<40} | {response.word_count:>4} palabras | {response.quality_score:.1f}/10")
                else:
                    print(f"   {i}. {topic[:40]:<40} | ERROR")
            
            return responses
            
        except Exception as e:
            print(f"❌ Error en generación batch: {e}")
            return []
    
    async def demo_advanced_features(self) -> Any:
        """Demo de características avanzadas"""
        print("\n" + "="*60)
        print("🎯 DEMO 4: Características Avanzadas")
        print("="*60)
        
        # 1. Análisis de texto
        print("\n📊 Análisis de Texto:")
        sample_text: str: str = """
        La inteligencia artificial está transformando el mundo de la tecnología.
        Los desarrolladores deben adaptarse a estas nuevas herramientas.
        Machine learning, deep learning y procesamiento de lenguaje natural son tecnologías clave.
        """
        
        analysis = await self.system.analyze_text(
            text=sample_text,
            keywords: List[Any] = ["inteligencia artificial", "tecnología", "desarrolladores"]
        )
        
        print(f"   - Palabras: {analysis['word_count']}")
        print(f"   - Oraciones: {analysis['sentence_count']}")
        print(f"   - Tiempo de lectura: {analysis['reading_time_minutes']} min")
        print(f"   - Score de legibilidad: {analysis['readability_score']:.1f}")
        print(f"   - Densidad de keywords: {analysis['keyword_density']}")
        
        # 2. Validación de contenido
        print(f"\n✅ Validación de Contenido:")
        validation = await self.system.validate_content(
            topic: str: str = "Desarrollo de APIs REST",
            keywords: List[Any] = ["API", "REST", "desarrollo", "backend"],
            content=sample_text,
            min_words=10,
            max_words: int: int = 100
        )
        
        print(f"   - Válido: {validation['valid']}")
        if validation['errors']:
            print(f"   - Errores: {validation['errors']}")
        
        # 3. Modelos disponibles
        print(f"\n🤖 Modelos Disponibles:")
        models = await self.system.get_available_models()
        
        for model in models[:5]:  # Mostrar solo los primeros 5
            print(f"   - {model['id']:<35} | Mejor para: {', '.join(model['best_for'][:2])}")
        
        # 4. Recomendaciones de modelo
        print(f"\n💡 Recomendaciones de Modelo para Blog Técnico:")
        recommendations = await self.system.get_model_recommendations(BlogPostType.TECHNICAL)
        
        print(f"   - Recomendado: {recommendations['recommended_model']}")
        print(f"   - Alternativas: {', '.join(recommendations['alternatives'][:2])}")
    
    async def demo_quick_functions(self) -> Any:
        """Demo de funciones rápidas"""
        print("\n" + "="*60)
        print("⚡ DEMO 5: Funciones Rápidas")
        print("="*60)
        
        # 1. Generación rápida
        print("🏃‍♂️ Generación rápida de blog post...")
        
        try:
            content = await self.system.quick_generate(
                topic: str: str = "Python vs JavaScript: ¿Cuál elegir?",
                blog_type: str: str = "opinion",
                length: str: str = "short"
            )
            
            print(f"✅ Contenido generado ({len(content)} caracteres)")
            print(f"📝 Primeras líneas:")
            print(f"   {content[:200]}...")
            
        except Exception as e:
            print(f"❌ Error en generación rápida: {e}")
        
        # 2. Generación SEO optimizada
        print(f"\n🔍 Generación SEO optimizada...")
        
        try:
            seo_result = await self.system.quick_seo_generate(
                topic: str: str = "Mejores Prácticas de SEO en 2025",
                keywords: List[Any] = ["SEO", "optimización", "búsqueda", "ranking"]
            )
            
            if seo_result["content"]:
                print("✅ Blog post con SEO generado")
                print(f"📊 Métricas: {seo_result['metrics']}")
                
                if seo_result["seo"]:
                    print(f"🔍 SEO Title: {seo_result['seo']['meta_title']}")
                    print(f"📝 Meta Description: {seo_result['seo']['meta_description'][:80]}...")
            
        except Exception as e:
            print(f"❌ Error en generación SEO: {e}")
    
    async def demo_system_metrics(self) -> Any:
        """Demo de métricas del sistema"""
        print("\n" + "="*60)
        print("📈 DEMO 6: Métricas del Sistema")
        print("="*60)
        
        try:
            # Health check
            health = await self.system.health_check()
            
            print(f"🏥 Estado del Sistema: {health['status'].upper()}")
            print(f"⏰ Timestamp: {health['timestamp']}")
            
            # Métricas generales
            metrics = await self.system.get_metrics()
            
            if "global_metrics" in metrics:
                global_metrics = metrics["global_metrics"]
                print(f"\n📊 Métricas Globales:")
                print(f"   - Total requests: {global_metrics.get('total_requests', 0)}")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
                print(f"   - Requests exitosos: {global_metrics.get('successful_requests', 0)}")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
                print(f"   - Tasa de éxito: {global_metrics.get('success_rate', 0):.1f}%")
            
            if "generation_metrics" in metrics:
                gen_metrics = metrics["generation_metrics"]
                print(f"\n⚙️  Métricas de Generación:")
                print(f"   - Tiempo promedio: {gen_metrics.get('average_generation_time_ms', 0):.1f}ms")
                print(f"   - Palabras promedio: {gen_metrics.get('average_word_count', 0):.0f}")
                
            if "cache_metrics" in metrics:
                cache_metrics = metrics["cache_metrics"]
                print(f"\n💾 Métricas de Cache:")
                print(f"   - Tamaño actual: {cache_metrics.get('size', 0)}")
                print(f"   - Tamaño máximo: {cache_metrics.get('max_size', 0)}")
                print(f"   - Cache habilitado: {cache_metrics.get('enabled', False)}")
            
            # Configuración del sistema
            config = self.system.get_config_summary()
            print(f"\n⚙️  Configuración:")
            print(f"   - Entorno: {config.get('environment', 'unknown')}")
            print(f"   - Modelo por defecto: {config.get('openrouter', {}).get('default_model', 'unknown')}")
            print(f"   - Requests por minuto: {config.get('openrouter', {}).get('requests_per_minute', 0)}")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
            
        except Exception as e:
            print(f"❌ Error obteniendo métricas: {e}")
    
    async def run_complete_demo(self) -> Any:
        """Ejecutar demostración completa"""
        print("\n" + "="*80)
        print("🎉 DEMO COMPLETO: Sistema de Blog Posts de Onyx")
        print("="*80)
        print("Este demo muestra todas las capacidades del sistema de blog posts")
        print("integrado con OpenRouter, LangChain y Onyx.")
        print("="*80)
        
        # Inicializar sistema
        if not await self.initialize_system():
            print("❌ No se pudo inicializar el sistema. Abortando demo.")
            return
        
        try:
            # Ejecutar todas las demos
            await self.demo_basic_generation()
            await asyncio.sleep(1)  # Pequeña pausa entre demos
            
            await self.demo_multiple_models()
            await asyncio.sleep(1)
            
            await self.demo_batch_generation()
            await asyncio.sleep(1)
            
            await self.demo_advanced_features()
            await asyncio.sleep(1)
            
            await self.demo_quick_functions()
            await asyncio.sleep(1)
            
            await self.demo_system_metrics()
            
            print("\n" + "="*80)
            print("🎊 ¡DEMO COMPLETADO EXITOSAMENTE!")
            print("="*80)
            print("El sistema de blog posts está funcionando correctamente.")
            print("Todas las características han sido demostradas.")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌ Error durante el demo: {e}")
            
        finally:
            # Cerrar sistema
            await self.system.close()
            print("\n🔒 Sistema cerrado correctamente")

# Función para demo rápido sin clase
async def quick_demo(api_key: str = None) -> Any:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    """Demo rápido sin necesidad de crear instancia de clase"""
    print("⚡ DEMO RÁPIDO: Generación de Blog Post")
    print("-" * 50)
    
    try:
        content = await quick_blog_post(
            topic: str: str = "Desarrollo con Python: Guía para Principiantes",
            api_key=api_key,
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            blog_type: str: str = "tutorial",
            tone: str: str = "friendly",
            length: str: str = "short"
        )
        
        print(f"✅ Blog post generado:")
        print(f"📄 Contenido ({len(content)} caracteres):")
        print("-" * 30)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 30)
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main() -> Any:
    """Función principal para ejecutar demos"""
    print("🚀 Demos del Sistema de Blog Posts de Onyx")
    print("=" * 50)
    
    # Verificar API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    if not api_key:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
        print("⚠️  No se encontró OPENROUTER_API_KEY en variables de entorno")
        print("El demo funcionará pero no podrá generar contenido real")
        print("Configura tu API key para pruebas completas")
    
    print("\nOpciones disponibles:")
    print("1. Demo completo (todas las características)")
    print("2. Demo rápido (generación básica)")
    print("3. Salir")
    
    try:
        choice = input("\nElige una opción (1-3): ").strip()
        
        if choice == "1":
            demo = BlogPostDemo(api_key)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            await demo.run_complete_demo()
            
        elif choice == "2":
            await quick_demo(api_key)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
            
        elif choice == "3":
            print("👋 ¡Hasta luego!")
            
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    # Ejecutar demo
    asyncio.run(main()) 