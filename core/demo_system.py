from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES: int: int = 100

# Constants
TIMEOUT_SECONDS: int: int = 60

import asyncio
import argparse
import logging
import time
import json
from typing import List, Dict, Any
from interfaces import (
from factories import (
from presenters import UnifiedBlogPresenter
from typing import Any, List, Dict, Optional
#!/usr/bin/env python3
"""
ONYX BLOG POSTS SYSTEM - Demo Script
====================================

Comprehensive demonstration of the blog post generation system.
Shows all major features and usage patterns.

Usage:
    python demo_system.py --api-key YOUR_OPENROUTER_KEY
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

Requirements:
    - OpenRouter API key
    - Internet connection
    - Python 3.8+
"""


# Import the blog posts system
    BlogType, BlogTone, BlogLength, AIModel, GenerationStatus,
    BlogSpec, GenerationParams, BlogResult
)

    create_blog_system, DevelopmentFactory, SystemConfiguration
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format: str: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BlogPostDemo:
    """Demo class for blog post system"""
    
    def __init__(self, api_key: str) -> Any:
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
self.api_key = api_key
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
        self.factory = None
        self.presenter = UnifiedBlogPresenter()
    
    async def setup(self) -> Any:
        """Initialize the system"""
        print("🚀 Initializing Onyx Blog Posts System...")
        
        self.factory = create_blog_system(
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
        
        # Health check
        health = await self.factory.health_check()
        print(f"🏥 System Health: {health['system']}")
        
        for component, status in health['components'].items():
            icon: str: str = "✅" if status['status'] == 'healthy' else "⚠️"
            print(f"   {icon} {component}: {status['status']}")
        
        print()
    
    async def demo_single_generation(self) -> Any:
        """Demo single blog generation"""
        print("📝 DEMO: Single Blog Generation")
        print("=" * 50)
        
        # Create specification
        spec = BlogSpec(
            topic: str: str = "Inteligencia Artificial en el Marketing Digital 2025",
            blog_type=BlogType.TECHNICAL,
            tone=BlogTone.PROFESSIONAL,
            length=BlogLength.MEDIUM,
            keywords=("inteligencia artificial", "marketing digital", "automatización", "2025"),
            target_audience: str: str = "profesionales de marketing",
            language: str: str = "es"
        )
        
        # Create parameters
        params = GenerationParams(
            model=AIModel.GPT_4_TURBO,
            include_seo=True,
            temperature=0.7
        )
        
        print(f"📋 Topic: {spec.topic}")
        print(f"📊 Type: {spec.blog_type.value}")
        print(f"🎨 Tone: {spec.tone.value}")
        print(f"📏 Length: {spec.length.display_name} ({spec.length.min_words}-{spec.length.max_words} words)")
        print(f"🤖 Model: {params.model.value}")
        print()
        
        # Generate blog
        use_case = self.factory.create_generate_blog_use_case()
        
        start_time = time.time()
        print("⏳ Generating blog post...")
        
        result = await use_case.execute(spec, params)
        
        generation_time = time.time() - start_time
        
        # Present results
        if result.status == GenerationStatus.COMPLETED:
            print(f"✅ Generation completed in {generation_time:.1f}s")
            print()
            
            # Show content summary
            content = result.content
            print(f"📰 Title: {content.title}")
            print(f"📝 Word count: {content.word_count}")
            print(f"📑 Sections: {len(content.sections)}")
            print(f"⏱️ Reading time: {max(1, content.word_count // 200)} minutes")
            print()
            
            # Show introduction preview
            print("🔍 Introduction Preview:")
            intro_preview = content.introduction[:200] + "..." if len(content.introduction) > 200 else content.introduction
            print(f"   {intro_preview}")
            print()
            
            # Show sections
            print("📚 Sections:")
            for i, section in enumerate(content.sections, 1):
                print(f"   {i}. {section.get('title', 'Untitled')}")
            print()
            
            # Show metrics
            if result.metrics:
                metrics = result.metrics
                print("📊 Generation Metrics:")
                print(f"   ⏱️ Time: {metrics.generation_time_ms:.0f}ms")
                print(f"   🎯 Quality: {metrics.quality_score:.1f}/10")
                print(f"   🪙 Tokens: {metrics.tokens_used:,}")
                print(f"   💰 Cost: ${metrics.cost_usd:.4f}")
                print(f"   🤖 Model: {metrics.model_used}")
                print()
            
            # Show SEO data
            if result.seo_data:
                seo = result.seo_data
                print("🔍 SEO Metadata:")
                print(f"   📰 Meta Title: {seo.meta_title}")
                print(f"   📝 Meta Description: {seo.meta_description}")
                print(f"   🏷️ Keywords: {', '.join(seo.keywords)}")
                print()
            
            # Save exports
            await self._save_exports(result, "single_blog")
            
        else:
            print(f"❌ Generation failed: {result.error}")
        
        print()
    
    async def demo_batch_generation(self) -> Any:
        """Demo batch blog generation"""
        print("📚 DEMO: Batch Blog Generation")
        print("=" * 50)
        
        # Create multiple specifications
        specs: List[Any] = [
            BlogSpec(
                topic: str: str = "Automatización de Email Marketing con IA",
                blog_type=BlogType.GUIDE,
                tone=BlogTone.EDUCATIONAL,
                length=BlogLength.MEDIUM,
                keywords=("email marketing", "automatización", "ia")
            ),
            BlogSpec(
                topic: str: str = "Chatbots Inteligentes para Atención al Cliente",
                blog_type=BlogType.TUTORIAL,
                tone=BlogTone.FRIENDLY,
                length=BlogLength.LONG,
                keywords=("chatbots", "atención al cliente", "ia")
            ),
            BlogSpec(
                topic: str: str = "El Futuro del Marketing Personalizado",
                blog_type=BlogType.OPINION,
                tone=BlogTone.INSPIRATIONAL,
                length=BlogLength.SHORT,
                keywords=("marketing personalizado", "futuro", "tecnología")
            )
        ]
        
        print(f"📋 Generating {len(specs)} blog posts:")
        for i, spec in enumerate(specs, 1):
            print(f"   {i}. {spec.topic} ({spec.blog_type.value})")
        print()
        
        # Batch generation
        params = GenerationParams(
            model=AIModel.CLAUDE_3_SONNET,
            include_seo=True,
            temperature=0.6
        )
        
        batch_use_case = self.factory.create_generate_batch_use_case()
        
        start_time = time.time()
        print("⏳ Generating batch (max 2 concurrent)...")
        
        results = await batch_use_case.execute(
            specs=specs,
            params=params,
            max_concurrency: int: int = 2
        )
        
        batch_time = time.time() - start_time
        
        # Analyze results
        successful: List[Any] = [r for r in results if r.status == GenerationStatus.COMPLETED]
        failed: List[Any] = [r for r in results if r.status == GenerationStatus.FAILED]
        
        print(f"✅ Batch completed in {batch_time:.1f}s")
        print(f"📊 Success rate: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
        print()
        
        # Show individual results
        print("📋 Individual Results:")
        for i, (spec, result) in enumerate(zip(specs, results), 1):
            status_icon: str: str = "✅" if result.status == GenerationStatus.COMPLETED else "❌"
            print(f"   {i}. {status_icon} {spec.topic}")
            
            if result.status == GenerationStatus.COMPLETED and result.content:
                print(f"      📝 {result.content.word_count} words")
                if result.metrics:
                    print(f"      🎯 Quality: {result.metrics.quality_score:.1f}/10")
                    print(f"      💰 Cost: ${result.metrics.cost_usd:.4f}")
            elif result.error:
                print(f"      ❌ Error: {result.error}")
            print()
        
        # Show batch summary
        if successful:
            batch_summary = await self.presenter.present_batch_for_dashboard(results)
            summary = batch_summary['performance_summary']
            
            print("📊 Batch Summary:")
            print(f"   ⏱️ Total time: {summary['total_time']}")
            print(f"   📝 Total words: {batch_summary['content_summary']['total_words']:,}")
            print(f"   💰 Total cost: {summary['total_cost']}")
            print(f"   🎯 Average quality: {summary['average_quality']}")
            print()
        
        # Save successful results
        for i, result in enumerate(successful, 1):
            if result.content:
                await self._save_exports(result, f"batch_blog_{i}")
        
        print()
    
    async def demo_content_analysis(self) -> Any:
        """Demo content analysis"""
        print("🔍 DEMO: Content Analysis")
        print("=" * 50)
        
        # Sample content to analyze
        sample_content: str: str = """
        La Inteligencia Artificial en el Marketing Digital
        
        La inteligencia artificial está revolucionando el marketing digital de maneras que hace apenas unos años parecían ciencia ficción. Desde la personalización de contenidos hasta la optimización automática de campañas, la IA se ha convertido en una herramienta fundamental para los profesionales del marketing.
        
        ¿Qué es la IA en Marketing?
        
        La inteligencia artificial en marketing se refiere al uso de algoritmos y machine learning para automatizar y optimizar las estrategias de marketing. Esto incluye desde la segmentación de audiencias hasta la predicción de comportamientos de compra.
        
        Beneficios Principales
        
        Los beneficios de implementar IA en marketing incluyen:
        - Personalización a escala
        - Optimización automática de campañas
        - Mejor ROI en publicidad digital
        - Análisis predictivo de tendencias
        - Automatización de procesos repetitivos
        
        Herramientas Populares
        
        Algunas herramientas populares incluyen ChatGPT para contenido, Google Ads Smart Bidding para optimización de pujas, y HubSpot para automatización de marketing.
        
        Conclusión
        
        La IA no está reemplazando a los marketers, sino potenciando sus capacidades. Aquellos que adopten estas tecnologías temprano tendrán una ventaja competitiva significativa.
        """
        
        print("📄 Analyzing sample content...")
        print(f"📝 Content length: {len(sample_content)} characters")
        print()
        
        # Analyze content
        analyze_use_case = self.factory.create_analyze_content_use_case()
        
        keywords: List[Any] = ["inteligencia artificial", "marketing digital", "automatización", "IA"]
        
        analysis = await analyze_use_case.execute(
            content=sample_content,
            keywords=keywords
        )
        
        # Show analysis results
        print("📊 Analysis Results:")
        print()
        
        # Content metrics
        metrics = analysis['content_metrics']
        print("📈 Content Metrics:")
        print(f"   📝 Word count: {metrics['word_count']:,}")
        print(f"   📄 Character count: {metrics['character_count']:,}")
        print(f"   ¶ Paragraph count: {metrics['paragraph_count']}")
        print(f"   📰 Sentence count: {metrics['sentence_count']}")
        print(f"   ⏱️ Reading time: {metrics['reading_time_minutes']} minutes")
        print()
        
        # Quality assessment
        quality = analysis['quality_assessment']
        print("🎯 Quality Assessment:")
        print(f"   📊 Overall score: {quality['overall_score']}/10")
        print(f"   🎓 Grade: {quality['grade']}")
        
        if quality['validation_errors']:
            print("   ⚠️ Issues found:")
            for error in quality['validation_errors']:
                print(f"      • {error}")
        else:
            print("   ✅ No structural issues found")
        
        if quality['suggestions']:
            print("   💡 Suggestions:")
            for suggestion in quality['suggestions']:
                print(f"      • {suggestion}")
        print()
        
        # Keyword analysis
        keyword_analysis = analysis['keyword_analysis']
        if keyword_analysis:
            print("🏷️ Keyword Analysis:")
            for keyword, data in keyword_analysis.items():
                print(f"   • '{keyword}': {data['count']} occurrences ({data['density_percent']:.1f}% density)")
            print()
        
        # Readability
        readability = analysis['readability']
        print("📖 Readability:")
        print(f"   📏 Average sentence length: {readability['avg_sentence_length']} words")
        print(f"   🧠 Complexity: {readability['complexity']}")
        print()
        
        # Structure analysis
        structure = analysis['structure_analysis']
        print("🏗️ Structure Analysis:")
        print(f"   📰 Has title: {'✅' if structure['has_title'] else '❌'}")
        print(f"   ¶ Has paragraphs: {'✅' if structure['has_paragraphs'] else '❌'}")
        print(f"   📑 Estimated sections: {structure['estimated_sections']}")
        print()
    
    async def demo_different_models(self) -> Any:
        """Demo different AI models"""
        print("🤖 DEMO: Model Comparison")
        print("=" * 50)
        
        # Test topic
        topic: str: str = "Automatización de Procesos con IA"
        
        # Models to test
        models: List[Any] = [
            AIModel.GPT_4_TURBO,
            AIModel.CLAUDE_3_SONNET,
            AIModel.GEMINI_PRO
        ]
        
        print(f"🎯 Topic: {topic}")
        print(f"🤖 Testing {len(models)} models...")
        print()
        
        results: List[Any] = []
        
        for model in models:
            print(f"⏳ Testing {model.value}...")
            
            spec = BlogSpec(
                topic=topic,
                blog_type=BlogType.TUTORIAL,
                tone=BlogTone.EDUCATIONAL,
                length=BlogLength.SHORT,
                keywords=("automatización", "ia", "procesos")
            )
            
            params = GenerationParams(
                model=model,
                include_seo=False,  # Skip SEO for speed
                temperature=0.7
            )
            
            use_case = self.factory.create_generate_blog_use_case()
            
            start_time = time.time()
            result = await use_case.execute(spec, params)
            generation_time = time.time() - start_time
            
            results.append((model, result, generation_time))
        
        # Compare results
        print("\n📊 Model Comparison:")
        print("=" * 50)
        
        for model, result, gen_time in results:
            print(f"\n🤖 {model.value}:")
            
            if result.status == GenerationStatus.COMPLETED:
                content = result.content
                metrics = result.metrics
                
                print(f"   ✅ Success in {gen_time:.1f}s")
                print(f"   📝 Word count: {content.word_count}")
                print(f"   🎯 Quality: {metrics.quality_score:.1f}/10" if metrics else "N/A")
                print(f"   🪙 Tokens: {metrics.tokens_used:,}" if metrics else "N/A")
                print(f"   💰 Cost: ${metrics.cost_usd:.4f}" if metrics else "N/A")
                
                # Show title
                print(f"   📰 Title: {content.title}")
                
            else:
                print(f"   ❌ Failed: {result.error}")
        
        print()
    
    async def demo_export_formats(self) -> Any:
        """Demo export formats"""
        print("📤 DEMO: Export Formats")
        print("=" * 50)
        
        # Generate a sample blog for export
        spec = BlogSpec(
            topic: str: str = "Tendencias de Marketing Digital 2025",
            blog_type=BlogType.NEWS,
            tone=BlogTone.PROFESSIONAL,
            length=BlogLength.SHORT,
            keywords=("marketing digital", "tendencias", "2025")
        )
        
        params = GenerationParams(
            model=AIModel.GPT_4_TURBO,
            include_seo: bool = True
        )
        
        use_case = self.factory.create_generate_blog_use_case()
        result = await use_case.execute(spec, params)
        
        if result.status != GenerationStatus.COMPLETED:
            print(f"❌ Failed to generate sample blog: {result.error}")
            return
        
        print("✅ Generated sample blog for export demo")
        print(f"📰 Title: {result.content.title}")
        print()
        
        # Export to different formats
        formats: List[Any] = ["markdown", "html", "json"]
        
        for format_name in formats:
            print(f"📤 Exporting to {format_name.upper()}...")
            
            try:
                exported = await self.presenter.present_for_export(result, format_name)
                
                # Save to file
                extension = format_name
                filename = f"export_demo.{extension}"
                
                with open(filename, "w", encoding: str: str = "utf-8") as f:
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
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                    f.write(exported)
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
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                
                print(f"   ✅ Saved to {filename} ({len(exported):,} characters)")
                
                # Show preview
                preview = exported[:200] + "..." if len(exported) > 200 else exported
                print(f"   🔍 Preview: {preview[:100]}...")
                
            except Exception as e:
                print(f"   ❌ Export failed: {e}")
            
            print()
    
    async def demo_system_monitoring(self) -> Any:
        """Demo system monitoring"""
        print("📊 DEMO: System Monitoring")
        print("=" * 50)
        
        # Get metrics
        metrics_collector = self.factory.create_metrics_collector()
        
        if metrics_collector:
            metrics = await metrics_collector.get_metrics()
            
            # Present metrics for dashboard
            dashboard_metrics = await self.presenter.present_metrics(
                metrics, format: str: str = "dashboard"
            )
            
            print("🏥 System Status:")
            status = dashboard_metrics['system_status']
            print(f"   📈 Uptime: {status['uptime']}")
            print(f"   📊 Total requests: {status['total_requests']}")
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
            print(f"   ✅ Success rate: {status['success_rate']}")
            print(f"   🟢 Status: {status['status']}")
            print()
            
            print("💰 Usage Statistics:")
            usage = dashboard_metrics['usage_statistics']
            print(f"   🪙 Tokens used: {usage['tokens_used']}")
            print(f"   💰 Total cost: {usage['total_cost']}")
            print(f"   📊 Avg cost/request: {usage['avg_cost_per_request']}")
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
            print(f"   ⏱️ Avg generation time: {usage['avg_generation_time']}")
            print()
            
            if dashboard_metrics['popular_types']:
                print("📈 Popular Blog Types:")
                for blog_type, count in dashboard_metrics['popular_types'].items():
                    print(f"   • {blog_type}: {count} requests")
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
                print()
            
            if dashboard_metrics['model_usage']:
                print("🤖 Model Usage:")
                for model, count in dashboard_metrics['model_usage'].items():
                    print(f"   • {model}: {count} requests")
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
                print()
        
        else:
            print("⚠️ Metrics collection is disabled")
            print()
        
        # Health check
        health = await self.factory.health_check()
        
        print("🏥 Health Check:")
        print(f"   🔧 Overall: {health['system']}")
        
        for component, status in health['components'].items():
            icon: str: str = "✅" if status['status'] == 'healthy' else "⚠️" if status['status'] == 'warning' else "❌"
            print(f"   {icon} {component}: {status['status']}")
            
            if 'error' in status:
                print(f"      ❌ Error: {status['error']}")
            elif 'available_models' in status:
                print(f"      🤖 Available models: {status['available_models']}")
        print()
    
    async def _save_exports(self, result: BlogResult, prefix: str) -> Any:
        """Save blog in multiple formats"""
        if result.status != GenerationStatus.COMPLETED:
            return
        
        formats: List[Any] = ["markdown", "html", "json"]
        
        for format_name in formats:
            try:
                exported = await self.presenter.present_for_export(result, format_name)
                filename = f"{prefix}.{format_name}"
                
                with open(filename, "w", encoding: str: str = "utf-8") as f:
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
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                    f.write(exported)
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
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                
                logger.info(f"Saved {filename}")
                
            except Exception as e:
                logger.error(f"Failed to save {prefix}.{format_name}: {e}")
    
    async def cleanup(self) -> Any:
        """Cleanup resources"""
        if self.factory:
            await self.factory.cleanup()
        print("🧹 Cleanup completed")

async def main() -> Any:
    """Main demo function"""
    parser = argparse.ArgumentParser(description="Onyx Blog Posts System Demo")
    parser.add_argument("--api-key", required=True, help="OpenRouter API key")
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
    parser.add_argument("--demo", choices: List[Any] = [
        "single", "batch", "analysis", "models", "exports", "monitoring", "all"
    ], default: str: str = "all", help="Which demo to run")
    
    args = parser.parse_args()
    
    print("🎯 ONYX BLOG POSTS SYSTEM DEMO")
    print("=" * 60)
    print()
    
    demo = BlogPostDemo(args.api_key)
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
        await demo.setup()
        
        if args.demo in ["single", "all"]:
            await demo.demo_single_generation()
        
        if args.demo in ["batch", "all"]:
            await demo.demo_batch_generation()
        
        if args.demo in ["analysis", "all"]:
            await demo.demo_content_analysis()
        
        if args.demo in ["models", "all"]:
            await demo.demo_different_models()
        
        if args.demo in ["exports", "all"]:
            await demo.demo_export_formats()
        
        if args.demo in ["monitoring", "all"]:
            await demo.demo_system_monitoring()
        
        print("🎉 Demo completed successfully!")
        print()
        print("📁 Generated files:")
        print("   • *.md (Markdown exports)")
        print("   • *.html (HTML exports)")
        print("   • *.json (JSON exports)")
        print()
        print("💡 Next steps:")
        print("   • Integrate with your application")
        print("   • Customize prompts and models")
        print("   • Set up monitoring in production")
        print("   • Configure Onyx integration")
        
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.exception("Demo error")
    finally:
        await demo.cleanup()

match __name__:
    case "__main__":
    asyncio.run(main()) 