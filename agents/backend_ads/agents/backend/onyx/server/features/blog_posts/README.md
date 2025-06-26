# Blog Posts Module - Modular Architecture

A comprehensive, enterprise-grade blog post management system with AI-powered content generation, SEO optimization, and multi-platform publishing capabilities.

## 🏗️ Architecture Overview

This module follows a **modular architecture** pattern with clear separation of concerns:

```
blog_posts/
├── __init__.py          # Factory functions and service registry
├── config.py           # Configuration management with Pydantic
├── models.py           # Data models and validation
├── core.py             # Core business logic services
├── api.py              # FastAPI router and endpoints
├── exceptions.py       # Custom exception hierarchy
├── utils.py            # Utility functions
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

## 🚀 Key Features

### ✨ Content Management
- **CRUD Operations**: Create, read, update, delete blog posts
- **Status Management**: Draft, review, published, archived states
- **Metadata Handling**: Author, tags, categories, featured images
- **Content Validation**: Comprehensive validation with warnings/errors
- **HTML Sanitization**: Safe content processing with bleach

### 🤖 AI-Powered Content Generation
- **Multi-Provider Support**: OpenAI, Anthropic, and other AI providers
- **Content Types**: Blog posts, articles, social media content
- **Tone Control**: Professional, casual, friendly, formal, creative, technical
- **Language Support**: English, Spanish, French, German, Italian, Portuguese
- **Batch Processing**: Generate multiple contents simultaneously
- **Template System**: Pre-built content templates

### 🔍 SEO Optimization
- **Automated SEO Analysis**: Keyword density, readability scores
- **Meta Tag Generation**: Titles, descriptions, keywords
- **Schema Markup**: Structured data for better search visibility
- **Readability Scoring**: Flesch Reading Ease calculation
- **Content Structure**: Heading analysis and optimization
- **Keyword Extraction**: Automated keyword identification

### 📤 Multi-Platform Publishing
- **Platform Integration**: WordPress, Medium, Ghost, custom platforms
- **Social Media**: Auto-generate social media posts
- **Scheduling**: Schedule publications for optimal timing
- **Notification System**: Email/webhook notifications
- **Analytics Tracking**: View counts, engagement metrics

## 📦 Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Copy the example environment file
cp .env.example .env

# Edit with your configuration
nano .env
```

3. **Configure the module:**
```python
from blog_posts.config import BlogPostConfig

config = BlogPostConfig(
    ai_model="gpt-3.5-turbo",
    openai_api_key="your-api-key",
    enable_seo_optimization=True
)
```

## 🔧 Configuration

### Environment Variables

```bash
# AI Configuration
BLOG_AI_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
BLOG_AI_TEMPERATURE=0.7
BLOG_AI_MAX_TOKENS=2048

# Content Settings
BLOG_MAX_LENGTH=5000
BLOG_MIN_LENGTH=300
BLOG_DEFAULT_LANGUAGE=en
BLOG_DEFAULT_TONE=professional

# SEO Settings
BLOG_SEO_LEVEL=advanced
BLOG_MAX_TITLE_LENGTH=60
BLOG_MAX_DESCRIPTION_LENGTH=160
BLOG_TARGET_KEYWORD_DENSITY=1.5
BLOG_ENABLE_SCHEMA=true

# Performance Settings
BLOG_ENABLE_CACHE=true
BLOG_CACHE_TTL=3600
BLOG_MAX_CONCURRENT=10
BLOG_ENABLE_BATCH=true

# Storage Settings
BLOG_STORAGE_PATH=./blog_content
BLOG_IMAGE_PATH=./blog_images
BLOG_BACKUP_ENABLED=true
```

## 💻 Usage Examples

### Basic Usage

```python
from blog_posts import (
    create_blog_post_system,
    ContentRequest,
    BlogPostMetadata,
    SEOConfig
)

# Initialize the complete system
system = create_blog_post_system()
blog_service = system["blog_service"]
content_generator = system["content_generator"]
seo_optimizer = system["seo_optimizer"]

# Generate AI content
request = ContentRequest(
    topic="Benefits of AI in Modern Marketing",
    target_audience="Marketing professionals",
    keywords=["AI marketing", "automation", "personalization"],
    length_words=1500,
    tone="professional",
    language="en"
)

result = await content_generator.generate_content(request)

if result.success:
    # Create blog post
    metadata = BlogPostMetadata(
        author="AI Assistant",
        tags=["AI", "marketing", "technology"],
        category="Technology"
    )
    
    post = await blog_service.create_post(
        title=result.title,
        content=result.content,
        metadata=metadata,
        seo_data=result.seo_data
    )
    
    print(f"Created post: {post.id}")
```

### SEO Optimization

```python
from blog_posts.models import SEOConfig
from blog_posts.config import SEOLevel

# Configure SEO optimization
seo_config = SEOConfig(
    level=SEOLevel.EXPERT,
    target_keywords=["AI marketing", "automation"],
    keyword_density_target=1.5,
    readability_target=75.0,
    include_schema_markup=True
)

# Optimize existing post
optimized_post = await seo_optimizer.optimize_post(post, seo_config)
print(f"SEO Score: {optimized_post.seo.readability_score}")
```

### Batch Content Generation

```python
# Generate multiple posts
requests = [
    ContentRequest(topic="AI in Healthcare", target_audience="Doctors"),
    ContentRequest(topic="Machine Learning Basics", target_audience="Students"),
    ContentRequest(topic="Future of Automation", target_audience="Business owners")
]

results = await content_generator.generate_batch(requests)

for i, result in enumerate(results):
    if result.success:
        print(f"Generated post {i+1}: {result.word_count} words")
    else:
        print(f"Failed to generate post {i+1}: {result.errors}")
```

### Publishing

```python
from blog_posts.models import PublishingConfig

# Configure publishing
publishing_config = PublishingConfig(
    platforms=["wordpress", "medium"],
    social_media_posts=True,
    send_notifications=True,
    seo_optimizations=True
)

# Publish the post
results = await publishing_service.publish_post(post, publishing_config)
print(f"Published to {len(results)} platforms")
```

## 🌐 API Endpoints

### Blog Post Management

```http
# Create blog post
POST /blog-posts/
{
    "title": "My Blog Post",
    "content": "Post content...",
    "author": "John Doe",
    "tags": ["technology", "AI"],
    "category": "Tech"
}

# Get blog post
GET /blog-posts/{post_id}

# List blog posts
GET /blog-posts/?status=published&limit=10&offset=0

# Update blog post
PUT /blog-posts/{post_id}
{
    "title": "Updated Title",
    "status": "published"
}

# Delete blog post
DELETE /blog-posts/{post_id}

# Publish blog post
POST /blog-posts/{post_id}/publish
{
    "platforms": ["wordpress", "medium"],
    "social_media_posts": true
}
```

### Content Generation

```http
# Generate content
POST /blog-posts/generate
{
    "topic": "AI in Marketing",
    "target_audience": "Marketing professionals",
    "keywords": ["AI", "marketing", "automation"],
    "length_words": 1500,
    "tone": "professional",
    "language": "en",
    "include_seo": true
}

# Batch generation
POST /blog-posts/generate/batch
[
    {
        "topic": "Topic 1",
        "target_audience": "Audience 1"
    },
    {
        "topic": "Topic 2", 
        "target_audience": "Audience 2"
    }
]
```

### SEO Optimization

```http
# Optimize SEO
POST /blog-posts/{post_id}/optimize-seo
{
    "level": "expert",
    "target_keywords": ["AI", "marketing"],
    "keyword_density_target": 1.5,
    "readability_target": 75.0,
    "include_schema_markup": true
}
```

## 🧪 Testing

```python
import pytest
from blog_posts import create_blog_post_service, ContentRequest

@pytest.mark.asyncio
async def test_create_blog_post():
    service = create_blog_post_service()
    
    metadata = BlogPostMetadata(
        author="Test Author",
        tags=["test"]
    )
    
    post = await service.create_post(
        title="Test Post",
        content="This is test content with more than fifty words to pass validation. " * 3,
        metadata=metadata
    )
    
    assert post.title == "Test Post"
    assert post.metadata.author == "Test Author"
    assert post.status == BlogPostStatus.DRAFT

@pytest.mark.asyncio
async def test_content_generation():
    from blog_posts import create_content_generator
    
    generator = create_content_generator()
    request = ContentRequest(
        topic="Test Topic",
        target_audience="Test Audience"
    )
    
    result = await generator.generate_content(request)
    assert result.success
    assert result.content is not None
    assert result.word_count > 0
```

Run tests:
```bash
pytest
```

## 🔍 Monitoring & Observability

The module includes comprehensive monitoring:

- **Structured Logging**: All operations logged with correlation IDs
- **Performance Metrics**: Generation times, success rates, error rates
- **Health Checks**: Service availability monitoring
- **Error Tracking**: Detailed error reporting with context

## 🎯 Best Practices

### 1. Service Initialization
```python
# Use factory functions for service creation
blog_service = create_blog_post_service(config)

# Or create complete system
system = create_blog_post_system(config)
```

### 2. Error Handling
```python
try:
    post = await blog_service.create_post(title, content, metadata)
except BlogPostException as e:
    logger.error("Blog operation failed", error=e.to_dict())
except Exception as e:
    logger.error("Unexpected error", error=str(e))
```

### 3. Configuration Management
```python
# Use environment-specific configs
config = BlogPostConfig()  # Loads from environment

# Override for testing
test_config = BlogPostConfig(
    ai_model="mock",
    enable_caching=False
)
```

### 4. Async Operations
```python
# Use async/await for all I/O operations
result = await content_generator.generate_content(request)

# Use batch operations for multiple items
results = await content_generator.generate_batch(requests)
```

## 🔄 Integration with Main App

```python
# In your main FastAPI app
from fastapi import FastAPI
from blog_posts.api import router

app = FastAPI()
app.include_router(router, prefix="/api/v1")

# Initialize services at startup
@app.on_event("startup")
async def startup():
    from blog_posts import create_blog_post_system
    app.state.blog_system = create_blog_post_system()
```

## 📊 Performance Considerations

- **Caching**: Enabled by default for frequently accessed content
- **Async Processing**: All I/O operations are asynchronous
- **Batch Operations**: Efficient processing of multiple items
- **Connection Pooling**: Optimized database and API connections
- **Rate Limiting**: Built-in protection against API abuse

## 🛡️ Security Features

- **Content Sanitization**: HTML cleaning with bleach
- **Input Validation**: Comprehensive validation with pydantic
- **Error Sanitization**: No sensitive data in error messages
- **Rate Limiting**: API endpoint protection
- **Authentication Ready**: Easy integration with auth systems

## 📚 Extension Points

The modular architecture makes it easy to extend:

1. **Custom AI Providers**: Implement new content generators
2. **Publishing Platforms**: Add new publishing integrations
3. **SEO Analyzers**: Implement advanced SEO analysis
4. **Content Processors**: Add new content transformation logic
5. **Storage Backends**: Support different storage systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the modular patterns
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This module is part of the Onyx Features system and follows the same licensing terms.

---

**Ready to create amazing blog content with AI! 🚀** 