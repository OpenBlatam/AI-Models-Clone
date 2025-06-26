"""
Example Usage of the Blog Posts Module.

This file demonstrates how to use the modular blog post management system
with various features including content generation, SEO optimization, and publishing.
"""

import asyncio
from typing import List

from blog_posts import (
    create_blog_post_system,
    ContentRequest,
    BlogPostMetadata,
    SEOConfig,
    PublishingConfig,
    ContentLanguage,
    ContentTone,
    SEOLevel,
    BlogPostStatus
)


async def example_basic_usage():
    """Example of basic blog post creation and management."""
    print("=== Basic Blog Post Management ===")
    
    # Initialize the complete system
    system = create_blog_post_system()
    blog_service = system["blog_service"]
    
    # Create blog post metadata
    metadata = BlogPostMetadata(
        author="John Doe",
        tags=["technology", "AI", "automation"],
        category="Technology",
        excerpt="An introduction to AI in modern business"
    )
    
    # Create a blog post
    post = await blog_service.create_post(
        title="The Future of AI in Business Automation",
        content="""
        # The Future of AI in Business Automation
        
        Artificial Intelligence is revolutionizing how businesses operate across all industries.
        From customer service chatbots to predictive analytics, AI technologies are becoming
        essential tools for competitive advantage.
        
        ## Key Benefits of AI Automation
        
        1. **Increased Efficiency**: Automating repetitive tasks allows employees to focus on strategic work
        2. **Cost Reduction**: AI systems can operate 24/7 without breaks or benefits
        3. **Improved Accuracy**: Machine learning algorithms can identify patterns humans might miss
        4. **Scalability**: AI solutions can handle increased workload without proportional cost increases
        
        ## Implementation Strategies
        
        When implementing AI automation, businesses should:
        
        - Start with simple, well-defined processes
        - Ensure proper data quality and governance
        - Train employees on new AI tools and workflows
        - Monitor performance and iterate based on results
        
        ## Conclusion
        
        The future of business belongs to organizations that can effectively integrate AI automation
        into their operations while maintaining human oversight and creativity.
        """,
        metadata=metadata
    )
    
    print(f"✅ Created blog post: {post.id}")
    print(f"   Title: {post.title}")
    print(f"   Status: {post.status}")
    print(f"   Word Count: {post.metadata.word_count}")
    print(f"   Reading Time: {post.metadata.read_time_minutes} minutes")
    print(f"   Slug: {post.slug}")
    
    # List all posts
    posts = await blog_service.list_posts(limit=5)
    print(f"\n📄 Total posts in system: {len(posts)}")
    
    return post


async def example_ai_content_generation():
    """Example of AI-powered content generation."""
    print("\n=== AI Content Generation ===")
    
    system = create_blog_post_system()
    content_generator = system["content_generator"]
    
    # Create content generation request
    request = ContentRequest(
        topic="Benefits of Remote Work for Software Development Teams",
        target_audience="Software development managers and team leads",
        keywords=["remote work", "software development", "productivity", "team collaboration"],
        length_words=1200,
        tone=ContentTone.PROFESSIONAL,
        language=ContentLanguage.ENGLISH,
        include_outline=True,
        include_seo=True
    )
    
    print("🤖 Generating AI content...")
    result = await content_generator.generate_content(request)
    
    if result.success:
        print(f"✅ Content generated successfully!")
        print(f"   Title: {result.title}")
        print(f"   Word Count: {result.word_count}")
        print(f"   Generation Time: {result.generation_time_ms}ms")
        print(f"   Outline: {result.outline}")
        
        if result.seo_data:
            print(f"   SEO Title: {result.seo_data.title}")
            print(f"   Meta Description: {result.seo_data.meta_description}")
            print(f"   Keywords: {result.seo_data.keywords}")
        
        # Show first 200 characters of content
        content_preview = result.content[:200] + "..." if len(result.content) > 200 else result.content
        print(f"   Content Preview: {content_preview}")
        
        return result
    else:
        print(f"❌ Content generation failed: {result.errors}")
        return None


async def example_batch_generation():
    """Example of batch content generation."""
    print("\n=== Batch Content Generation ===")
    
    system = create_blog_post_system()
    content_generator = system["content_generator"]
    
    # Create multiple content requests
    requests = [
        ContentRequest(
            topic="Introduction to Machine Learning",
            target_audience="Beginners in data science",
            tone=ContentTone.FRIENDLY,
            length_words=800
        ),
        ContentRequest(
            topic="Cloud Computing Security Best Practices",
            target_audience="IT security professionals",
            tone=ContentTone.TECHNICAL,
            length_words=1000
        ),
        ContentRequest(
            topic="The Impact of Social Media on Marketing",
            target_audience="Marketing professionals",
            tone=ContentTone.PROFESSIONAL,
            length_words=900
        )
    ]
    
    print(f"🚀 Generating {len(requests)} posts in batch...")
    results = await content_generator.generate_batch(requests)
    
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"✅ Batch generation completed:")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {len(failed)}")
    
    for i, result in enumerate(successful):
        print(f"   Post {i+1}: {result.title} ({result.word_count} words)")
    
    return successful


async def example_seo_optimization():
    """Example of SEO optimization."""
    print("\n=== SEO Optimization ===")
    
    system = create_blog_post_system()
    blog_service = system["blog_service"]
    seo_optimizer = system["seo_optimizer"]
    
    # Create a test post
    metadata = BlogPostMetadata(
        author="SEO Expert",
        tags=["SEO", "digital marketing", "search optimization"]
    )
    
    post = await blog_service.create_post(
        title="Complete Guide to SEO Optimization",
        content="""
        Search Engine Optimization (SEO) is crucial for online visibility.
        This comprehensive guide covers all aspects of SEO optimization
        including keyword research, on-page optimization, and technical SEO.
        
        Understanding how search engines work is the foundation of good SEO.
        Search engines use complex algorithms to rank websites based on
        relevance and authority.
        
        Keyword research helps identify what terms your audience searches for.
        On-page optimization ensures your content is properly structured.
        Technical SEO focuses on website performance and crawlability.
        """,
        metadata=metadata
    )
    
    # Configure SEO optimization
    seo_config = SEOConfig(
        level=SEOLevel.EXPERT,
        target_keywords=["SEO optimization", "search engines", "keyword research"],
        keyword_density_target=1.8,
        readability_target=75.0,
        include_schema_markup=True
    )
    
    print("🔍 Optimizing SEO...")
    optimized_post = await seo_optimizer.optimize_post(post, seo_config)
    
    if optimized_post.seo:
        print(f"✅ SEO optimization completed:")
        print(f"   SEO Title: {optimized_post.seo.title}")
        print(f"   Meta Description: {optimized_post.seo.meta_description}")
        print(f"   Keyword Density: {optimized_post.seo.keyword_density}%")
        print(f"   Readability Score: {optimized_post.seo.readability_score}")
        print(f"   Schema Markup: {'Yes' if optimized_post.seo.schema_markup else 'No'}")
    
    return optimized_post


async def example_publishing():
    """Example of multi-platform publishing."""
    print("\n=== Multi-Platform Publishing ===")
    
    system = create_blog_post_system()
    blog_service = system["blog_service"]
    publishing_service = system["publishing_service"]
    
    # Get an existing post (create one if needed)
    posts = await blog_service.list_posts(limit=1)
    if not posts:
        metadata = BlogPostMetadata(author="Publisher")
        post = await blog_service.create_post(
            title="Test Publishing Post",
            content="This is a test post for publishing demonstration.",
            metadata=metadata
        )
    else:
        post = posts[0]
    
    # Configure publishing
    publishing_config = PublishingConfig(
        platforms=["wordpress", "medium", "dev.to"],
        social_media_posts=True,
        send_notifications=True,
        seo_optimizations=True
    )
    
    print(f"📤 Publishing post '{post.title}' to multiple platforms...")
    
    # First publish in the blog service
    await blog_service.publish_post(post.id)
    
    # Then publish to external platforms
    results = await publishing_service.publish_post(post, publishing_config)
    
    print(f"✅ Publishing completed:")
    for platform, result in results.items():
        if result.get("success"):
            print(f"   ✅ {platform}: Published successfully")
        else:
            print(f"   ❌ {platform}: {result.get('error', 'Unknown error')}")
    
    return results


async def example_full_workflow():
    """Example of a complete blog post workflow."""
    print("\n=== Complete Blog Post Workflow ===")
    
    system = create_blog_post_system()
    blog_service = system["blog_service"]
    content_generator = system["content_generator"]
    seo_optimizer = system["seo_optimizer"]
    publishing_service = system["publishing_service"]
    
    # Step 1: Generate AI content
    request = ContentRequest(
        topic="10 Tips for Effective Team Communication",
        target_audience="Team managers and project leaders",
        keywords=["team communication", "collaboration", "productivity"],
        tone=ContentTone.PROFESSIONAL,
        length_words=1000,
        include_seo=True
    )
    
    print("1. 🤖 Generating content with AI...")
    generation_result = await content_generator.generate_content(request)
    
    if not generation_result.success:
        print("❌ Content generation failed")
        return
    
    # Step 2: Create blog post
    print("2. 📝 Creating blog post...")
    metadata = BlogPostMetadata(
        author="AI Assistant",
        tags=["communication", "teamwork", "management"],
        category="Business"
    )
    
    post = await blog_service.create_post(
        title=generation_result.title,
        content=generation_result.content,
        metadata=metadata,
        seo_data=generation_result.seo_data
    )
    
    # Step 3: Optimize SEO
    print("3. 🔍 Optimizing SEO...")
    seo_config = SEOConfig(
        level=SEOLevel.ADVANCED,
        target_keywords=request.keywords,
        readability_target=70.0
    )
    
    optimized_post = await seo_optimizer.optimize_post(post, seo_config)
    await blog_service.update_post(post.id, seo=optimized_post.seo)
    
    # Step 4: Publish
    print("4. 📤 Publishing...")
    await blog_service.publish_post(post.id)
    
    publishing_config = PublishingConfig(
        platforms=["wordpress"],
        social_media_posts=True
    )
    
    publishing_results = await publishing_service.publish_post(optimized_post, publishing_config)
    
    print(f"✅ Complete workflow finished!")
    print(f"   Post ID: {post.id}")
    print(f"   Title: {post.title}")
    print(f"   Status: {BlogPostStatus.PUBLISHED}")
    print(f"   SEO Score: {optimized_post.seo.readability_score if optimized_post.seo else 'N/A'}")
    print(f"   Published to: {len(publishing_results)} platforms")
    
    return post


async def main():
    """Run all examples."""
    print("🚀 Blog Posts Module Examples")
    print("=" * 50)
    
    try:
        # Run examples
        await example_basic_usage()
        await example_ai_content_generation()
        await example_batch_generation()
        await example_seo_optimization()
        await example_publishing()
        await example_full_workflow()
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 