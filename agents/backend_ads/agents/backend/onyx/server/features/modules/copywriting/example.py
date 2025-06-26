"""
Copywriting Module Usage Examples.

Comprehensive examples showing how to use the AI-powered copywriting system
for various content generation scenarios.
"""

import asyncio
from typing import List
from modules.copywriting import (
    create_copywriting_system,
    create_copywriting_service,
    create_content_generator,
    ContentRequest,
    ContentType,
    ContentTone,
    ContentLanguage,
    CopywritingConfig,
    ContentBatch,
    ABTestExperiment,
    ABTestVariant
)


async def basic_content_generation():
    """Basic content generation example."""
    print("🚀 Basic Content Generation Example")
    print("=" * 50)
    
    # Create a copywriting service
    service = create_copywriting_service()
    
    # Create a content request
    request = ContentRequest(
        content_type=ContentType.AD_COPY,
        tone=ContentTone.PROFESSIONAL,
        language=ContentLanguage.ENGLISH,
        target_audience="Small business owners looking to grow online",
        key_message="AI-powered marketing tools save time and increase ROI",
        keywords=["AI marketing", "automation", "ROI", "small business"],
        brand_voice="Helpful and trustworthy technology partner",
        call_to_action="Start your free 14-day trial",
        max_length=250,
        include_hashtags=True,
        urgency_level=3
    )
    
    # Generate content
    try:
        result = await service.generate_content(request)
        
        print(f"✅ Generated Content:")
        print(f"   Content: {result.content}")
        print(f"   Type: {result.content_type}")
        print(f"   Tone: {result.tone}")
        print(f"   Confidence: {result.confidence_score:.2f}")
        print(f"   Generation Time: {result.generation_time_ms:.0f}ms")
        
        if result.metrics:
            print(f"   Readability: {result.metrics.readability_score:.1f}")
            print(f"   Sentiment: {result.metrics.sentiment_score:.2f}")
            print(f"   Engagement Prediction: {result.metrics.engagement_prediction:.2f}")
            print(f"   Word Count: {result.metrics.word_count}")
        
        if result.alternatives:
            print(f"   Alternatives: {len(result.alternatives)} variants generated")
            for i, alt in enumerate(result.alternatives[:2], 1):
                print(f"     {i}. {alt[:100]}...")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()


async def multi_language_content():
    """Multi-language content generation example."""
    print("🌍 Multi-Language Content Generation")
    print("=" * 50)
    
    service = create_copywriting_service()
    
    languages = [
        (ContentLanguage.ENGLISH, "AI-powered marketing tools"),
        (ContentLanguage.SPANISH, "Herramientas de marketing con IA"),
        (ContentLanguage.FRENCH, "Outils marketing alimentés par l'IA")
    ]
    
    for language, message in languages:
        request = ContentRequest(
            content_type=ContentType.SOCIAL_POST,
            tone=ContentTone.FRIENDLY,
            language=language,
            target_audience="Marketing professionals",
            key_message=message,
            max_length=150,
            include_emojis=True
        )
        
        try:
            result = await service.generate_content(request)
            print(f"🌐 {language.value.upper()}: {result.content}")
        except Exception as e:
            print(f"❌ {language.value}: Error - {e}")
    
    print()


async def batch_processing_example():
    """Batch content generation example."""
    print("📦 Batch Processing Example")
    print("=" * 50)
    
    service = create_copywriting_service()
    
    # Create multiple requests
    requests = [
        ContentRequest(
            content_type=ContentType.EMAIL_SUBJECT,
            target_audience="Newsletter subscribers",
            key_message="Weekly AI updates and insights",
            tone=ContentTone.PROFESSIONAL
        ),
        ContentRequest(
            content_type=ContentType.SOCIAL_POST,
            target_audience="Tech enthusiasts",
            key_message="Latest AI breakthrough announcement",
            tone=ContentTone.PLAYFUL,
            include_hashtags=True
        ),
        ContentRequest(
            content_type=ContentType.PRODUCT_DESCRIPTION,
            target_audience="Software developers",
            key_message="Code completion AI that understands context",
            tone=ContentTone.AUTHORITATIVE,
            max_length=300
        ),
        ContentRequest(
            content_type=ContentType.AD_COPY,
            target_audience="Marketing managers",
            key_message="Automate your content creation workflow",
            tone=ContentTone.URGENT,
            call_to_action="Book a demo today",
            urgency_level=4
        )
    ]
    
    # Create batch request
    batch = ContentBatch(requests=requests)
    
    try:
        results = await service.process_batch(batch)
        
        print(f"📊 Batch Results:")
        print(f"   Total: {results.total_count}")
        print(f"   Completed: {results.completed_count}")
        print(f"   Failed: {results.failed_count}")
        print(f"   Status: {results.status}")
        
        print(f"\n📝 Generated Content:")
        for i, result in enumerate(results.results, 1):
            print(f"   {i}. [{result.content_type}] {result.content[:80]}...")
    
    except Exception as e:
        print(f"❌ Batch Error: {e}")
    
    print()


async def content_analysis_example():
    """Content analysis example."""
    print("🔍 Content Analysis Example")
    print("=" * 50)
    
    service = create_copywriting_service()
    
    sample_content = """
    Transform your business with our revolutionary AI-powered marketing platform! 
    🚀 Save 80% of your time while boosting engagement by 300%. Our cutting-edge 
    technology analyzes customer behavior, optimizes campaigns in real-time, and 
    delivers personalized experiences that convert. Join over 10,000 satisfied 
    customers who've already discovered the future of marketing. Don't wait - 
    your competitors are already ahead! Start your FREE trial today and see 
    results in just 24 hours. Limited time offer expires soon! Act now! 
    #AIMarketing #MarketingAutomation #DigitalTransformation
    """
    
    try:
        analyzer = service.content_analyzer
        metrics = await analyzer.analyze_content(
            content=sample_content,
            keywords=["AI", "marketing", "automation", "engagement"]
        )
        
        print(f"📊 Analysis Results:")
        print(f"   Readability Score: {metrics.readability_score:.1f}/100")
        print(f"   Sentiment Score: {metrics.sentiment_score:.2f} (-1 to 1)")
        print(f"   Engagement Prediction: {metrics.engagement_prediction:.2f}")
        print(f"   Word Count: {metrics.word_count}")
        print(f"   Character Count: {metrics.character_count}")
        print(f"   Reading Time: {metrics.reading_time_minutes:.1f} minutes")
        print(f"   CTA Strength: {metrics.call_to_action_strength:.2f}")
        print(f"   Urgency Score: {metrics.urgency_score:.2f}")
        
        if metrics.emotional_triggers:
            print(f"   Emotional Triggers: {', '.join(metrics.emotional_triggers)}")
        
        if metrics.keyword_density:
            print(f"   Keyword Density:")
            for keyword, density in metrics.keyword_density.items():
                print(f"     {keyword}: {density:.1f}%")
    
    except Exception as e:
        print(f"❌ Analysis Error: {e}")
    
    print()


async def ab_testing_example():
    """A/B testing example."""
    print("🧪 A/B Testing Example")
    print("=" * 50)
    
    service = create_copywriting_service()
    
    # Original content request
    original_request = ContentRequest(
        content_type=ContentType.EMAIL_SUBJECT,
        target_audience="E-commerce customers",
        key_message="Special discount on popular items",
        tone=ContentTone.PROFESSIONAL,
        max_length=60
    )
    
    try:
        # Create A/B test experiment
        experiment = await service.create_ab_test(
            name="Email Subject Line Test",
            description="Testing different tones for discount email subject",
            original_request=original_request,
            variants=3,
            duration_hours=48
        )
        
        print(f"🧪 A/B Test Created:")
        print(f"   Experiment ID: {experiment.id}")
        print(f"   Name: {experiment.name}")
        print(f"   Variants: {len(experiment.variants)}")
        print(f"   Duration: {experiment.duration_hours} hours")
        
        print(f"\n📝 Variants:")
        for i, variant in enumerate(experiment.variants, 1):
            print(f"   {i}. [{variant.variant_name}] {variant.content.content}")
        
        # Simulate performance data
        print(f"\n📊 Simulating Performance Data...")
        for variant in experiment.variants:
            # Simulate metrics
            variant.update_metrics(
                impressions=1000 + (hash(variant.id) % 500),
                clicks=50 + (hash(variant.id) % 30),
                conversions=5 + (hash(variant.id) % 10)
            )
            
            print(f"   {variant.variant_name}:")
            print(f"     CTR: {variant.click_through_rate:.2%}")
            print(f"     Conversion Rate: {variant.conversion_rate:.2%}")
        
        # Determine winner
        winner = experiment.get_winner()
        if winner:
            print(f"\n🏆 Winner: {winner.variant_name}")
            print(f"   Content: {winner.content.content}")
            print(f"   Conversion Rate: {winner.conversion_rate:.2%}")
    
    except Exception as e:
        print(f"❌ A/B Test Error: {e}")
    
    print()


async def template_usage_example():
    """Template usage example."""
    print("📝 Template Usage Example")
    print("=" * 50)
    
    system = create_copywriting_system()
    template_service = system["template_service"]
    
    # Create a custom template
    from modules.copywriting.models import ContentTemplate
    
    template = ContentTemplate(
        name="Product Launch Social Media",
        description="Template for announcing new product launches on social platforms",
        content_type=ContentType.SOCIAL_POST,
        tone=ContentTone.PLAYFUL,
        language=ContentLanguage.ENGLISH,
        template="""🚀 Introducing {product_name}! 
        
{key_benefit} 

Perfect for {target_audience} who want to {desired_outcome}.

{special_offer}

{call_to_action} 🔗

#{primary_hashtag} #{secondary_hashtag} #Innovation""",
        category="product_launch",
        tags=["social_media", "product", "announcement"]
    )
    
    try:
        # Generate content from template
        result = await template_service.generate_from_template(
            template=template,
            variables={
                "product_name": "AI Writer Pro 2.0",
                "key_benefit": "Write compelling copy 10x faster with advanced AI",
                "target_audience": "content creators and marketers",
                "desired_outcome": "scale their content production",
                "special_offer": "🎉 Launch week: 50% off first month!",
                "call_to_action": "Start your free trial",
                "primary_hashtag": "AIWriting",
                "secondary_hashtag": "ContentCreation"
            }
        )
        
        print(f"📝 Generated from Template:")
        print(f"   Template: {template.name}")
        print(f"   Content:\n{result.content}")
        print(f"   Variables Used: {len(template.variables)}")
    
    except Exception as e:
        print(f"❌ Template Error: {e}")
    
    print()


async def performance_monitoring_example():
    """Performance monitoring example."""
    print("📊 Performance Monitoring Example")
    print("=" * 50)
    
    service = create_copywriting_service()
    
    # Generate some content to create stats
    requests = [
        ContentRequest(
            content_type=ContentType.AD_COPY,
            target_audience="Tech users",
            key_message="Revolutionary AI assistant"
        ),
        ContentRequest(
            content_type=ContentType.SOCIAL_POST,
            target_audience="Social media users",
            key_message="Share your AI success story"
        )
    ]
    
    # Process requests
    for request in requests:
        try:
            await service.generate_content(request)
        except:
            pass  # Ignore errors for demo
    
    try:
        # Get performance statistics
        stats = await service.get_performance_stats()
        
        print(f"🎯 Performance Statistics:")
        print(f"   Total Requests: {stats.get('total_requests', 0)}")
        print(f"   Successful Requests: {stats.get('successful_requests', 0)}")
        print(f"   Failed Requests: {stats.get('failed_requests', 0)}")
        print(f"   Success Rate: {stats.get('success_rate', 0):.1%}")
        print(f"   Average Generation Time: {stats.get('avg_generation_time', 0):.0f}ms")
        print(f"   Cache Hit Rate: {stats.get('cache_hit_rate', 0):.1%}")
        
        if 'provider_stats' in stats:
            print(f"\n🤖 AI Provider Statistics:")
            for provider, provider_stats in stats['provider_stats'].items():
                print(f"   {provider}:")
                print(f"     Requests: {provider_stats.get('requests', 0)}")
                print(f"     Success Rate: {provider_stats.get('success_rate', 0):.1%}")
                print(f"     Avg Response Time: {provider_stats.get('avg_response_time', 0):.0f}ms")
    
    except Exception as e:
        print(f"❌ Stats Error: {e}")
    
    print()


async def advanced_configuration_example():
    """Advanced configuration example."""
    print("⚙️ Advanced Configuration Example")
    print("=" * 50)
    
    # Create custom configuration
    config = CopywritingConfig(
        # AI Provider Settings
        primary_ai_provider="openai",
        fallback_ai_provider="local",
        ai_model="gpt-4",
        ai_temperature=0.8,
        ai_max_tokens=1500,
        
        # Content Settings
        default_tone=ContentTone.FRIENDLY,
        max_content_length=2000,
        min_content_length=100,
        
        # Performance Settings
        enable_caching=True,
        cache_ttl=7200,  # 2 hours
        max_cache_size=2000,
        cache_compression=True,
        max_concurrent_generations=15,
        enable_batch_processing=True,
        batch_size=10,
        
        # Quality Control
        enable_content_filtering=True,
        profanity_filter=True,
        spam_detection=True,
        duplicate_detection=True,
        min_readability_score=65.0,
        
        # A/B Testing
        enable_ab_testing=True,
        max_variants=5,
        ab_test_duration_hours=72,
        
        # Monitoring
        enable_performance_tracking=True,
        enable_usage_analytics=True,
        log_level="INFO"
    )
    
    # Create service with custom config
    service = create_copywriting_service(config)
    
    print(f"⚙️ Configuration Settings:")
    print(f"   AI Model: {config.ai_model}")
    print(f"   Temperature: {config.ai_temperature}")
    print(f"   Cache TTL: {config.cache_ttl}s")
    print(f"   Max Cache Size: {config.max_cache_size}")
    print(f"   Batch Size: {config.batch_size}")
    print(f"   Min Readability: {config.min_readability_score}")
    print(f"   Content Filtering: {config.enable_content_filtering}")
    print(f"   A/B Testing: {config.enable_ab_testing}")
    
    # Test with custom config
    request = ContentRequest(
        content_type=ContentType.BLOG_TITLE,
        target_audience="AI enthusiasts",
        key_message="The future of artificial intelligence in content creation"
    )
    
    try:
        result = await service.generate_content(request)
        print(f"\n📝 Generated with Custom Config:")
        print(f"   Content: {result.content}")
        print(f"   Model Used: {result.model_used}")
        print(f"   Generation Time: {result.generation_time_ms:.0f}ms")
    
    except Exception as e:
        print(f"❌ Custom Config Error: {e}")
    
    print()


async def error_handling_example():
    """Error handling example."""
    print("🛡️ Error Handling Example")
    print("=" * 50)
    
    from modules.copywriting.exceptions import (
        ContentGenerationError,
        RateLimitError,
        ValidationError,
        AIProviderError
    )
    
    # Create service with potentially problematic config
    config = CopywritingConfig(
        openai_api_key="invalid-key",  # This will cause errors
        ai_timeout=1  # Very short timeout
    )
    
    service = create_copywriting_service(config)
    
    request = ContentRequest(
        content_type=ContentType.AD_COPY,
        target_audience="Test audience",
        key_message="Test message"
    )
    
    try:
        result = await service.generate_content(request)
        print(f"✅ Unexpected success: {result.content}")
    
    except RateLimitError as e:
        print(f"🚫 Rate Limited: {e.message}")
        print(f"   Retry after: {e.details.get('retry_after', 'unknown')} seconds")
    
    except AIProviderError as e:
        print(f"🤖 AI Provider Error: {e.message}")
        print(f"   Provider: {e.details.get('provider', 'unknown')}")
        print(f"   Status Code: {e.details.get('status_code', 'unknown')}")
    
    except ContentGenerationError as e:
        print(f"📝 Content Generation Failed: {e.message}")
        print(f"   Error Code: {e.error_code}")
    
    except ValidationError as e:
        print(f"✅ Validation Error: {e.message}")
        print(f"   Field: {e.details.get('field', 'unknown')}")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    
    print()


async def main():
    """Run all examples."""
    print("🎯 Copywriting Module Examples")
    print("=" * 70)
    print("Demonstrating comprehensive AI-powered content generation")
    print("=" * 70)
    print()
    
    examples = [
        basic_content_generation,
        multi_language_content,
        batch_processing_example,
        content_analysis_example,
        ab_testing_example,
        template_usage_example,
        performance_monitoring_example,
        advanced_configuration_example,
        error_handling_example
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"❌ Example failed: {e}")
            print()
    
    print("✅ All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    # Run examples
    asyncio.run(main()) 