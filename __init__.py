"""
ONYX BLOG POSTS SYSTEM
======================

Complete blog post generation system for Onyx platform.
Clean Architecture implementation with OpenRouter and LangChain integration.

This module provides a modular, production-ready blog post generation system
that integrates seamlessly with the Onyx platform while maintaining clean
separation of concerns and dependency inversion.

## Architecture

The system follows Clean Architecture principles:

- **Interfaces**: Abstract contracts and value objects
- **Core**: Pure business logic (domain layer)
- **Adapters**: External integrations (infrastructure layer) 
- **Use Cases**: Application services (application layer)
- **Factories**: Dependency injection (composition root)
- **Presenters**: Data presentation (presentation layer)

## Features

- **8 Blog Types**: technical, tutorial, news, opinion, review, guide, case_study, announcement
- **7 Tones**: professional, casual, friendly, authoritative, conversational, educational, inspirational
- **4 Length Options**: short (300-600), medium (600-1200), long (1200-2500), extended (2500-5000) words
- **6+ AI Models**: GPT-4 Turbo, GPT-4o, Claude-3 Sonnet/Haiku, Gemini Pro, Mistral Large
- **Advanced Features**: SEO generation, quality scoring, batch processing, caching, metrics
- **Onyx Integration**: User authentication, quotas, document sets, persistence

## Quick Start

```python
from onyx.server.features.blog_posts import create_blog_system, BlogSpec, GenerationParams

# Create system
factory = create_blog_system(api_key="your-key", environment="development")
use_case = factory.create_generate_blog_use_case()

# Create specification
spec = BlogSpec(
    topic="AI en Marketing Digital 2025",
    blog_type=BlogType.TECHNICAL,
    tone=BlogTone.PROFESSIONAL,
    length=BlogLength.MEDIUM,
    keywords=("inteligencia artificial", "marketing", "automatización")
)

# Generate blog
params = GenerationParams(model=AIModel.GPT_4_TURBO, include_seo=True)
result = await use_case.execute(spec, params)

# Present result
presenter = factory.create_unified_presenter()
api_response = await presenter.present_for_api(result)
```

## Architecture Modules

### Interfaces (`interfaces/`)
- Domain types and enums (BlogType, BlogTone, BlogLength, AIModel)
- Value objects (BlogSpec, BlogContent, SEOData, GenerationMetrics)
- Abstract interfaces for all layers
- Exception hierarchy

### Core (`core/`)
- BlogContentValidator: Specification and content validation
- BlogQualityAnalyzer: Quality scoring algorithm
- CoreBlogGenerator: Main generation orchestrator
- CoreSEOGenerator: SEO metadata generation
- BlogDomainService: High-level domain service

### Adapters (`adapters/`)
- OpenRouterAdapter: Complete OpenRouter API client
- AdvancedPromptBuilder: LangChain-style prompt templates
- JSONContentParser: AI response parsing
- MemoryCacheAdapter: LRU cache implementation
- OnyxIntegrationAdapter: Onyx platform integration

### Use Cases (`use_cases/`)
- GenerateBlogUseCase: Single blog generation workflow
- GenerateBatchUseCase: Batch processing with concurrency control
- AnalyzeContentUseCase: Content analysis and quality assessment
- BlogPostWorkflowUseCase: Complete generation + analysis workflow

### Factories (`factories/`)
- BlogSystemFactory: Main dependency injection container
- Environment-specific factories (Development, Production, Testing)
- Configuration management and health checking

### Presenters (`presenters/`)
- APIResponsePresenter: REST API response formatting
- DashboardPresenter: UI/dashboard data formatting
- ExportPresenter: Markdown, HTML, JSON export
- UnifiedBlogPresenter: Single interface for all formats

## Performance Features

- **Multi-level Caching**: L1 memory cache with configurable TTL
- **Batch Processing**: Controlled concurrency for multiple blogs
- **Rate Limiting**: Configurable requests and tokens per minute
- **Cost Control**: Per-request and daily cost limits
- **Quality Scoring**: Automated 0-10 content quality analysis
- **Metrics Collection**: Generation time, tokens, costs, success rates

## Integration Features

- **Onyx Platform**: Seamless integration with user auth, quotas, document storage
- **OpenRouter**: Complete API client with 6+ models and cost tracking
- **LangChain**: Advanced prompt engineering and template system
- **Health Monitoring**: Component status and system health checks
- **Error Handling**: Comprehensive error types and retry mechanisms

## Environment Support

### Development
- Lower concurrency limits
- Shorter cache TTL
- Relaxed validation
- Local-only features

### Production  
- Higher performance settings
- Extended cache TTL
- Strict validation
- Full feature set enabled

### Testing
- Minimal configuration
- No external dependencies
- Fast execution

## Usage Examples

### Single Blog Generation
```python
factory = create_blog_system(api_key="key", environment="production")
use_case = factory.create_generate_blog_use_case()

spec = BlogSpec(
    topic="Automatización con IA",
    blog_type=BlogType.GUIDE,
    tone=BlogTone.EDUCATIONAL,
    length=BlogLength.LONG,
    user_id="user123"
)

result = await use_case.execute(spec, GenerationParams(
    model=AIModel.CLAUDE_3_SONNET,
    include_seo=True
))
```

### Batch Processing
```python
specs = [
    BlogSpec(topic="IA en Retail", blog_type=BlogType.CASE_STUDY, ...),
    BlogSpec(topic="Machine Learning", blog_type=BlogType.TUTORIAL, ...),
    BlogSpec(topic="Futuro del AI", blog_type=BlogType.OPINION, ...)
]

batch_use_case = factory.create_generate_batch_use_case()
results = await batch_use_case.execute(specs, params, max_concurrency=3)
```

### Content Analysis
```python
analyze_use_case = factory.create_analyze_content_use_case()
analysis = await analyze_use_case.execute(
    content="Tu contenido existente aquí...",
    keywords=["ia", "automatización"]
)
```

### Health Monitoring
```python
health = await factory.health_check()
metrics = await factory.create_metrics_collector().get_metrics()
```

## Error Handling

The system provides comprehensive error handling:

- **ValidationError**: Input validation failures
- **AIProviderError**: OpenRouter API issues
- **ContentParsingError**: AI response parsing failures
- **QuotaExceededError**: User quota limitations
- **BlogGenerationError**: General generation failures

## Configuration

Environment variables for configuration:

- `OPENROUTER_API_KEY`: OpenRouter API key
- `ONYX_URL`: Onyx platform URL
- `ONYX_API_KEY`: Onyx API key
- `CACHE_MAX_SIZE`: Cache size limit
- `MAX_CONCURRENCY`: Batch processing concurrency
- `ENABLE_CACHING`: Enable/disable caching
- `ENABLE_METRICS`: Enable/disable metrics
- `ENABLE_ONYX_INTEGRATION`: Enable/disable Onyx features

## Testing

The system includes comprehensive testing support:

```python
from onyx.server.features.blog_posts import TestingFactory

factory = TestingFactory()
# All external dependencies mocked for testing
```

## Monitoring & Metrics

Built-in metrics collection:

- Generation time and success rates
- Token usage and costs
- Quality scores and distributions
- Model usage patterns
- System health and uptime

Access via:
```python
metrics = await factory.create_metrics_collector().get_metrics()
```

## Export Formats

Multiple export formats supported:

```python
presenter = UnifiedBlogPresenter()

# Markdown
markdown = await presenter.present_for_export(result, "markdown")

# HTML with SEO
html = await presenter.present_for_export(result, "html") 

# JSON
json_data = await presenter.present_for_export(result, "json")
```

## Integration Examples

### API Endpoint
```python
@app.post("/api/blog/generate")
async def generate_blog(request: BlogRequest):
    factory = create_blog_system(api_key=settings.OPENROUTER_KEY)
    use_case = factory.create_generate_blog_use_case()
    
    result = await use_case.execute(request.spec, request.params)
    
    presenter = UnifiedBlogPresenter()
    return await presenter.present_for_api(result)
```

### Dashboard Integration
```python
async def get_dashboard_data():
    factory = create_blog_system_from_config(config)
    metrics = await factory.create_metrics_collector().get_metrics()
    
    presenter = UnifiedBlogPresenter()
    return await presenter.present_metrics(metrics, format="dashboard")
```

## Dependencies

Core dependencies managed in `requirements.txt`:

- `aiohttp`: HTTP client for OpenRouter
- `openai`: OpenAI API compatibility
- `pydantic`: Data validation and settings
- `jinja2`: Template engine for prompts

Optional dependencies:
- `redis`: Advanced caching (production)
- `prometheus-client`: Advanced metrics
- `sentry-sdk`: Error tracking

## License

This module is part of the Onyx platform and follows the same licensing terms.

## Support

For issues and support:
- Check system health: `await factory.health_check()`
- Monitor metrics: `await metrics_collector.get_metrics()`
- Review logs: Standard Python logging to 'onyx.blog_posts'

## Version

Version: 2.0.0 (Refactored Clean Architecture)
Compatible with: Onyx Platform 3.x+
"""

import logging
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# === EXPORTS ===

# Core interfaces and types
from .interfaces import (
    # Enums
    BlogType, BlogTone, BlogLength, AIModel, GenerationStatus,
    
    # Value Objects  
    BlogSpec, GenerationParams, BlogContent, SEOData,
    GenerationMetrics, BlogResult,
    
    # Core Interfaces
    IBlogGenerator, ISEOGenerator, IContentValidator, IQualityAnalyzer,
    
    # Adapter Interfaces
    IAIProvider, IPromptBuilder, IContentParser, ICacheProvider,
    IMetricsCollector, IOnyxIntegration,
    
    # Use Cases
    IGenerateBlogUseCase, IGenerateBatchUseCase, IAnalyzeContentUseCase,
    
    # Presenters
    IBlogPresenter,
    
    # Exceptions
    BlogGenerationError, ValidationError, AIProviderError,
    ContentParsingError, QuotaExceededError
)

# Core business logic
from .core import (
    BlogContentValidator, BlogQualityAnalyzer, CoreBlogGenerator,
    CoreSEOGenerator, BlogDomainService
)

# External adapters
from .adapters import (
    OpenRouterAdapter, AdvancedPromptBuilder, JSONContentParser,
    MemoryCacheAdapter, SimpleMetricsCollector, OnyxIntegrationAdapter
)

# Use cases
from .use_cases import (
    GenerateBlogUseCase, GenerateBatchUseCase, AnalyzeContentUseCase,
    BlogPostWorkflowUseCase
)

# Factories and configuration
from .factories import (
    SystemConfiguration, BlogSystemFactory, DevelopmentFactory,
    ProductionFactory, TestingFactory, create_blog_system,
    create_blog_system_from_config, quick_blog_generation
)

# Presenters
from .presenters import (
    APIResponsePresenter, DashboardPresenter, ExportPresenter,
    UnifiedBlogPresenter
)

# === VERSION INFO ===

__version__ = "2.0.0"
__author__ = "Onyx Blog Posts Team"
__description__ = "Complete blog post generation system for Onyx platform"

# === CONVENIENCE FUNCTIONS ===

async def create_blog_post(
    topic: str,
    api_key: str,
    blog_type: str = "technical",
    tone: str = "professional", 
    length: str = "medium",
    model: str = "gpt-4-turbo",
    include_seo: bool = True,
    language: str = "es",
    keywords: List[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for quick blog post generation.
    
    Args:
        topic: Blog post topic
        api_key: OpenRouter API key
        blog_type: Type of blog (technical, tutorial, etc.)
        tone: Writing tone (professional, casual, etc.)
        length: Target length (short, medium, long, extended)
        model: AI model to use
        include_seo: Whether to generate SEO metadata
        language: Content language
        keywords: Target keywords
        user_id: User ID for Onyx integration
    
    Returns:
        Dictionary with generation result
    """
    
    # Create factory
    factory = DevelopmentFactory(api_key)
    
    try:
        # Create use case
        use_case = factory.create_generate_blog_use_case()
        
        # Create specification
        spec = BlogSpec(
            topic=topic,
            blog_type=BlogType(blog_type),
            tone=BlogTone(tone),
            length=BlogLength.__members__[length.upper()],
            language=language,
            keywords=tuple(keywords) if keywords else (),
            user_id=user_id
        )
        
        # Create parameters
        params = GenerationParams(
            model=AIModel(f"openai/{model}" if not model.startswith(("openai/", "anthropic/", "google/")) else model),
            include_seo=include_seo
        )
        
        # Generate blog
        result = await use_case.execute(spec, params)
        
        # Present result
        presenter = UnifiedBlogPresenter()
        return await presenter.present_for_api(result)
        
    finally:
        await factory.cleanup()

async def analyze_blog_content(
    content: str,
    keywords: List[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function for content analysis.
    
    Args:
        content: Content to analyze
        keywords: Keywords to check for
        api_key: API key (optional for analysis)
    
    Returns:
        Dictionary with analysis results
    """
    
    # Create factory (testing mode if no API key)
    if api_key:
        factory = DevelopmentFactory(api_key)
    else:
        factory = TestingFactory()
    
    try:
        # Create use case
        use_case = factory.create_analyze_content_use_case()
        
        # Analyze content
        return await use_case.execute(content, keywords or [])
        
    finally:
        await factory.cleanup()

async def get_system_health(api_key: str) -> Dict[str, Any]:
    """
    Get system health status.
    
    Args:
        api_key: OpenRouter API key
    
    Returns:
        Dictionary with health status
    """
    factory = DevelopmentFactory(api_key)
    
    try:
        return await factory.health_check()
    finally:
        await factory.cleanup()

async def get_system_metrics(api_key: str) -> Dict[str, Any]:
    """
    Get system metrics.
    
    Args:
        api_key: OpenRouter API key
    
    Returns:
        Dictionary with system metrics
    """
    factory = DevelopmentFactory(api_key)
    
    try:
        metrics_collector = factory.create_metrics_collector()
        if metrics_collector:
            return await metrics_collector.get_metrics()
        return {}
    finally:
        await factory.cleanup()

# === MODULE METADATA ===

__all__ = [
    # Version info
    "__version__", "__author__", "__description__",
    
    # Enums
    "BlogType", "BlogTone", "BlogLength", "AIModel", "GenerationStatus",
    
    # Value Objects
    "BlogSpec", "GenerationParams", "BlogContent", "SEOData",
    "GenerationMetrics", "BlogResult",
    
    # Core Classes
    "BlogContentValidator", "BlogQualityAnalyzer", "CoreBlogGenerator",
    "CoreSEOGenerator", "BlogDomainService",
    
    # Adapters
    "OpenRouterAdapter", "AdvancedPromptBuilder", "JSONContentParser",
    "MemoryCacheAdapter", "SimpleMetricsCollector", "OnyxIntegrationAdapter",
    
    # Use Cases
    "GenerateBlogUseCase", "GenerateBatchUseCase", "AnalyzeContentUseCase",
    "BlogPostWorkflowUseCase",
    
    # Factories
    "SystemConfiguration", "BlogSystemFactory", "DevelopmentFactory",
    "ProductionFactory", "TestingFactory", "create_blog_system",
    "create_blog_system_from_config", "quick_blog_generation",
    
    # Presenters
    "APIResponsePresenter", "DashboardPresenter", "ExportPresenter",
    "UnifiedBlogPresenter",
    
    # Interfaces
    "IBlogGenerator", "ISEOGenerator", "IContentValidator", "IQualityAnalyzer",
    "IAIProvider", "IPromptBuilder", "IContentParser", "ICacheProvider",
    "IMetricsCollector", "IOnyxIntegration", "IGenerateBlogUseCase",
    "IGenerateBatchUseCase", "IAnalyzeContentUseCase", "IBlogPresenter",
    
    # Exceptions
    "BlogGenerationError", "ValidationError", "AIProviderError",
    "ContentParsingError", "QuotaExceededError",
    
    # Convenience Functions
    "create_blog_post", "analyze_blog_content", "get_system_health",
    "get_system_metrics"
]

# === INITIALIZATION ===

logger.info(f"Onyx Blog Posts System v{__version__} initialized")

# System validation on import (optional, can be disabled)
def _validate_system():
    """Validate system components are properly structured"""
    try:
        # Basic validation that key components can be imported
        from .interfaces import BlogType, BlogSpec
        from .core import BlogContentValidator
        from .adapters import OpenRouterAdapter
        from .factories import create_blog_system
        
        logger.debug("Blog post system components validated successfully")
        return True
        
    except ImportError as e:
        logger.warning(f"Blog post system validation warning: {e}")
        return False

# Validate on import (development only)
import os
if os.getenv("ONYX_VALIDATE_IMPORTS", "false").lower() == "true":
    _validate_system()

# === CONFIGURATION HINTS ===

# Recommended environment variables for production:
"""
# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Onyx Integration  
ONYX_URL=https://your-onyx-instance.com
ONYX_API_KEY=your_onyx_api_key_here

# Performance Settings
CACHE_MAX_SIZE=5000
CACHE_DEFAULT_TTL=7200
MAX_CONCURRENCY=8

# Feature Flags
ENABLE_CACHING=true
ENABLE_METRICS=true
ENABLE_ONYX_INTEGRATION=true

# Validation
ONYX_VALIDATE_IMPORTS=false
""" 