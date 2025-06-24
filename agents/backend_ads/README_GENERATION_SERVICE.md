# Enhanced Generation Service

## Overview

The Enhanced Generation Service is a production-ready, modular, and highly optimized system for generating ads, brand kits, and custom content using AI/LLM technology. It includes comprehensive error handling, metrics, caching, batch operations, and observability features.

## 🚀 Key Features

### Core Functionality
- **Ads Generation**: Generate multiple ad variations from web text
- **Brand Kit Generation**: Create comprehensive brand kits with colors, fonts, and guidelines
- **Custom Content Generation**: Generate personalized content using custom prompts
- **Batch Processing**: Process multiple requests concurrently with controlled concurrency
- **Caching**: Redis-ready caching with TTL for improved performance

### Production Features
- **Prometheus Metrics**: Comprehensive monitoring and observability
- **Structured Logging**: Traceable operations with unique trace IDs
- **Input Validation & Sanitization**: Security-first approach with XSS protection
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Error Handling**: Custom exception classes with detailed error information
- **Timeout Support**: Configurable timeouts for all operations
- **Internationalization**: Multi-language error messages (ES/EN)

### Performance Optimizations
- **Async/Await**: Full asynchronous operation for high concurrency
- **Semaphore Control**: Controlled concurrency to prevent resource exhaustion
- **Efficient Serialization**: orjson for ultrafast JSON processing
- **Smart Caching**: Intelligent cache key generation and TTL management
- **Batch Operations**: Parallel processing with error isolation

## 📁 File Structure

```
agents/backend_ads/
├── generation_service.py      # Main generation service with all features
├── utils_generation.py        # Utility functions, validation, and helpers
├── test_generation_service.py # Comprehensive test suite
├── README_GENERATION_SERVICE.md # This documentation
└── llm_interface.py          # LLM integration layer
```

## 🛠 Installation & Dependencies

```bash
pip install fastapi uvicorn aiocache prometheus-client orjson pytest asyncio
```

### Required Dependencies
- `fastapi`: Web framework
- `aiocache`: Async caching (Redis support)
- `prometheus-client`: Metrics collection
- `orjson`: Fast JSON serialization
- `pytest`: Testing framework
- `asyncio`: Async programming support

## 📖 Usage Examples

### Basic Generation

```python
from generation_service import generate_ads, generate_brand_kit, generate_custom_content

# Generate ads
ads_result = await generate_ads(
    text="Your website content here...",
    trace_id="unique-trace-id",
    lang="en",
    timeout=30.0
)

if ads_result.success:
    print(f"Generated {len(ads_result.data)} ads in {ads_result.processing_time:.2f}s")
else:
    print(f"Error: {ads_result.error}")

# Generate brand kit
brand_result = await generate_brand_kit(
    text="Your brand description...",
    trace_id="unique-trace-id",
    lang="es"
)

# Generate custom content
custom_result = await generate_custom_content(
    prompt="Create a social media post",
    text="Your content source...",
    trace_id="unique-trace-id",
    lang="en"
)
```

### Batch Processing

```python
from generation_service import batch_generate_ads, batch_generate_brand_kits

# Batch ads generation
texts = ["Text 1", "Text 2", "Text 3", "Text 4", "Text 5"]
batch_result = await batch_generate_ads(
    texts=texts,
    trace_id="batch-trace-id",
    max_concurrency=3,  # Process 3 at a time
    timeout=60.0
)

print(f"Processed {batch_result.total_count} items")
print(f"Success: {batch_result.success_count}, Errors: {batch_result.error_count}")
print(f"Total time: {batch_result.total_processing_time:.2f}s")

# Check individual results
for i, result in enumerate(batch_result.results):
    if result.success:
        print(f"Item {i}: {len(result.data)} ads generated")
    else:
        print(f"Item {i}: Error - {result.error}")
```

### Advanced Configuration

```python
from generation_service import generate_ads
from utils_generation import RateLimiter

# Custom rate limiter
rate_limiter = RateLimiter(max_requests=50, window_seconds=60)

# Generate with custom metrics callback
def metrics_callback(func_name, success, error=None, processing_time=None):
    print(f"{func_name}: {'SUCCESS' if success else 'ERROR'} - {processing_time:.2f}s")

result = await generate_ads(
    text="Your content...",
    trace_id="custom-trace",
    lang="en",
    timeout=45.0,
    metrics_cb=metrics_callback
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Cache configuration
CACHE_TTL_SECONDS=120
REDIS_URL=redis://localhost:6379

# Rate limiting
MAX_REQUESTS_PER_MINUTE=100
RATE_LIMIT_WINDOW=60

# Timeouts
DEFAULT_TIMEOUT=30.0
BATCH_TIMEOUT=60.0

# Concurrency
MAX_CONCURRENT_GENERATIONS=5
```

### Cache Configuration

```python
from aiocache import caches

# Configure Redis cache
caches.set_config({
    'default': {
        'cache': "aiocache.RedisCache",
        'endpoint': "127.0.0.1",
        'port': 6379,
        'timeout': 1,
        'serializer': {
            'class': "aiocache.serializers.JsonSerializer"
        }
    }
})
```

## 📊 Monitoring & Metrics

### Prometheus Metrics

The service automatically exposes the following metrics:

- `generation_requests_total`: Total requests by type and status
- `generation_latency_seconds`: Processing time histograms
- `generation_cache_hits_total`: Cache hit counts
- `generation_cache_misses_total`: Cache miss counts
- `active_generations`: Currently active generation count

### Getting Statistics

```python
from generation_service import get_generation_stats

stats = get_generation_stats()
print(f"Active generations: {stats['active_generations']}")
print(f"Total requests: {stats['total_requests']}")
print(f"Cache stats: {stats['cache_stats']}")
```

### Logging

Structured logging with trace IDs:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Logs will include:
# - Event type (start/success/error/timeout/cancelled)
# - Trace ID for request tracking
# - Processing time
# - Error details when applicable
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest test_generation_service.py -v

# Run specific test categories
pytest test_generation_service.py::TestInputValidation -v
pytest test_generation_service.py::TestBatchOperations -v
pytest test_generation_service.py::TestPerformance -v

# Run with coverage
pytest test_generation_service.py --cov=generation_service --cov=utils_generation
```

### Test Categories

- **Input Validation**: Text sanitization, length validation, URL validation
- **Generation Functions**: Individual generation operations
- **Batch Operations**: Concurrent processing and error handling
- **Error Handling**: Custom exceptions and error scenarios
- **Performance**: Concurrency and timing tests
- **Integration**: End-to-end workflow tests

## 🔒 Security Features

### Input Sanitization

- **HTML Tag Removal**: Strips potentially harmful HTML tags
- **Script Removal**: Removes JavaScript and other executable content
- **Control Character Filtering**: Removes non-printable characters
- **Whitespace Normalization**: Consistent text formatting

### Validation

- **Length Limits**: Configurable min/max length validation
- **Type Checking**: Ensures proper data types
- **URL Validation**: Secure URL parsing and validation
- **Batch Size Limits**: Prevents resource exhaustion

### Rate Limiting

- **Per-User Limits**: Individual user request tracking
- **Time Windows**: Configurable time-based limits
- **Automatic Cleanup**: Expired entries are automatically removed

## 🚀 Performance Optimizations

### Caching Strategy

- **Intelligent Keys**: Hash-based cache keys for consistency
- **TTL Management**: Configurable time-to-live values
- **Redis Ready**: Seamless Redis integration for distributed caching
- **Fallback Support**: Memory cache when Redis unavailable

### Concurrency Control

- **Semaphore Limits**: Prevents resource exhaustion
- **Async Processing**: Non-blocking operations
- **Error Isolation**: Individual failures don't affect batch
- **Timeout Protection**: Prevents hanging operations

### Serialization

- **orjson**: Ultrafast JSON serialization
- **Efficient Models**: Optimized data structures
- **Minimal Overhead**: Reduced processing time

## 🔧 Error Handling

### Custom Exceptions

```python
from generation_service import (
    GenerationError,
    ValidationError,
    LLMError,
    TimeoutError
)

try:
    result = await generate_ads(text="...")
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Trace ID: {e.trace_id}")
except LLMError as e:
    print(f"LLM error: {e.message}")
except TimeoutError as e:
    print(f"Operation timed out: {e.message}")
```

### Error Response Format

```python
{
    "success": False,
    "error": "Error message",
    "trace_id": "unique-trace-id",
    "error_code": "ERROR_TYPE",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🌐 Internationalization

### Supported Languages

- **Spanish (es)**: Default language
- **English (en)**: Alternative language

### Error Messages

```python
# Spanish errors
"Texto demasiado corto."
"Error al generar contenido: respuesta vacía o error de LLM."

# English errors
"Text too short."
"Error generating content: empty response or LLM error."
```

## 📈 Best Practices

### Performance

1. **Use Batch Operations**: For multiple items, use batch functions
2. **Configure Concurrency**: Set appropriate max_concurrency values
3. **Enable Caching**: Use Redis for production caching
4. **Monitor Metrics**: Track performance with Prometheus

### Error Handling

1. **Always Check Success**: Verify result.success before using data
2. **Handle Timeouts**: Set appropriate timeout values
3. **Log Trace IDs**: Use trace IDs for debugging
4. **Graceful Degradation**: Handle partial batch failures

### Security

1. **Validate Inputs**: Always validate and sanitize user input
2. **Use Rate Limiting**: Prevent abuse with rate limits
3. **Monitor Logs**: Watch for suspicious patterns
4. **Update Dependencies**: Keep dependencies current

### Monitoring

1. **Track Metrics**: Monitor request counts and latencies
2. **Set Alerts**: Alert on high error rates or latency
3. **Log Analysis**: Use structured logs for debugging
4. **Cache Monitoring**: Track cache hit/miss ratios

## 🔄 Migration Guide

### From Basic Service

If migrating from a basic generation service:

1. **Update Imports**: Import new functions and classes
2. **Handle Return Types**: Update to use GenerationResult/BatchResult
3. **Add Error Handling**: Implement try/catch for custom exceptions
4. **Configure Metrics**: Set up Prometheus monitoring
5. **Update Tests**: Use new test patterns and fixtures

### Example Migration

```python
# Old way
ads = await generate_ads_old(text)

# New way
result = await generate_ads(text, trace_id="unique-id")
if result.success:
    ads = result.data
else:
    handle_error(result.error)
```

## 🤝 Contributing

### Development Setup

1. **Clone Repository**: Get the latest code
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Run Tests**: `pytest test_generation_service.py -v`
4. **Check Coverage**: Ensure high test coverage
5. **Follow Style**: Use consistent code formatting

### Adding Features

1. **Write Tests**: Add comprehensive test coverage
2. **Update Documentation**: Document new features
3. **Add Metrics**: Include relevant Prometheus metrics
4. **Handle Errors**: Implement proper error handling
5. **Performance**: Ensure optimal performance

## 📄 License

This enhanced generation service is part of the Blatam Academy project and follows the same licensing terms.

## 🆘 Support

For issues, questions, or contributions:

1. **Check Documentation**: Review this README and inline docs
2. **Run Tests**: Ensure all tests pass
3. **Check Logs**: Use trace IDs for debugging
4. **Monitor Metrics**: Check Prometheus for performance issues
5. **Create Issues**: Report bugs with detailed information

---

**Version**: 2.0.0  
**Last Updated**: January 2024  
**Maintainer**: Blatam Academy Team 