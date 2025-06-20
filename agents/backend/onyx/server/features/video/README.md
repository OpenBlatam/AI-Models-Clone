# Video Processing System

A high-performance, enterprise-grade video processing system with advanced parallel processing capabilities, designed for scalable video content analysis and viral content generation.

## 🚀 Features

- **Advanced Parallel Processing**: Multi-backend support (Threading, Multiprocessing, Joblib, Dask, Async)
- **Viral Content Generation**: AI-powered viral variant generation with audience targeting
- **Batch Processing**: Optimized for large-scale video processing
- **Enterprise Observability**: Built-in monitoring, logging, and metrics
- **Production Ready**: Error handling, retry logic, and circuit breakers
- **Modular Architecture**: Clean separation of concerns with specialized processors

## 📁 Project Structure

```
video/
├── models/                 # Data models with batch support
│   ├── video_models.py    # Video clip models
│   ├── viral_models.py    # Viral content models
│   └── __init__.py
├── processors/            # Processing engines
│   ├── video_processor.py # Video processing logic
│   ├── viral_processor.py # Viral content processing
│   └── __init__.py
├── utils/                # Utilities and helpers
│   ├── parallel_utils.py # Parallel processing utilities
│   ├── batch_utils.py    # Batch processing utilities
│   ├── validation.py     # Validation utilities
│   └── __init__.py
├── examples/             # Usage examples
│   ├── parallel_processing_examples.py
│   └── __init__.py
├── benchmarks/           # Performance benchmarks
│   ├── performance_benchmark.py
│   └── __init__.py
├── tests/               # Test suite
│   ├── test_parallel_processing.py
│   └── __init__.py
├── docs/                # Documentation
│   ├── parallel_processing_guide.md
│   └── __init__.py
└── __init__.py
```

## 🏃‍♂️ Quick Start

### Basic Video Processing

```python
from onyx.server.features.video.processors.video_processor import create_high_performance_processor
from onyx.server.features.video.models.video_models import VideoClipRequest

# Create processor
processor = create_high_performance_processor()

# Generate requests
requests = [
    VideoClipRequest(
        youtube_url="https://youtube.com/watch?v=example",
        language="en",
        max_clip_length=60
    )
    for _ in range(100)
]

# Process in parallel
results = processor.process_batch_parallel(requests)
```

### Viral Content Generation

```python
from onyx.server.features.video.processors.viral_processor import create_high_performance_viral_processor

# Create viral processor
viral_processor = create_high_performance_viral_processor()

# Generate viral variants
viral_results = viral_processor.process_batch_parallel(
    requests,
    n_variants=5,
    audience_profile={'age': '18-35', 'interests': ['tech', 'gaming']}
)
```

## 🔧 Configuration

### Parallel Processing Configuration

```python
from onyx.server.features.video.utils.parallel_utils import ParallelConfig, BackendType

# Custom configuration
config = ParallelConfig(
    max_workers=16,
    chunk_size=1000,
    timeout=60.0,
    backend=BackendType.PROCESS,
    use_uvloop=True,
    use_numba=True
)

# Create processor with custom config
processor = VideoClipProcessor(config)
```

### Backend Selection

The system automatically selects the optimal backend based on:
- **Data size**: Small → Threading, Large → Multiprocessing
- **Operation type**: I/O-bound → Async, CPU-bound → Multiprocessing
- **Available resources**: CPU cores, memory, network

```python
# Auto-backend selection
results = processor.process_batch_parallel(requests)

# Manual backend selection
results = processor.process_batch_parallel(requests, backend=BackendType.PROCESS)
```

## 📊 Performance

### Benchmarks

Run comprehensive performance benchmarks:

```python
from onyx.server.features.video.benchmarks.performance_benchmark import run_comprehensive_benchmark

# Run all benchmarks
results = run_comprehensive_benchmark()
```

### Performance Metrics

Typical performance characteristics:

- **Small batches (10-50 items)**: 100-500 items/second
- **Medium batches (50-500 items)**: 200-1000 items/second
- **Large batches (500+ items)**: 500-2000 items/second
- **Viral processing**: 50-200 variants/second

### Memory Usage

- **Base memory**: ~50MB
- **Per 1000 items**: ~100MB additional
- **Viral variants**: ~50MB per 100 variants

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest agents/backend/onyx/server/features/video/tests/

# Run specific test file
pytest agents/backend/onyx/server/features/video/tests/test_parallel_processing.py

# Run with coverage
pytest --cov=onyx.server.features.video tests/
```

### Test Coverage

The test suite covers:
- ✅ Unit tests for all processors
- ✅ Integration tests for parallel processing
- ✅ Async processing tests
- ✅ Error handling and edge cases
- ✅ Performance benchmarks
- ✅ Configuration validation

## 📖 Examples

### Basic Examples

```python
from onyx.server.features.video.examples.parallel_processing_examples import (
    example_basic_parallel_processing,
    example_backend_comparison,
    example_viral_processing
)

# Run examples
example_basic_parallel_processing()
example_backend_comparison()
example_viral_processing()
```

### Advanced Examples

```python
# Custom parallel configuration
example_custom_configuration()

# Performance monitoring
example_performance_monitoring()

# Async processing
await example_async_processing()
```

## 🔍 Monitoring & Observability

### Performance Metrics

```python
# Get processing statistics
stats = processor.get_processing_stats()

# Monitor real-time performance
for metric in processor.get_performance_metrics():
    print(f"{metric.name}: {metric.value}")
```

### Logging

```python
import structlog

# Structured logging
logger = structlog.get_logger()
logger.info("Processing batch", batch_size=len(requests))
```

### Metrics Export

```python
# Export to monitoring systems
processor.export_metrics_to_prometheus()
processor.export_metrics_to_datadog()
```

## 🛠️ Advanced Usage

### Custom Processors

```python
from onyx.server.features.video.processors.video_processor import VideoClipProcessor

class CustomVideoProcessor(VideoClipProcessor):
    def process(self, request: VideoClipRequest) -> VideoClipResponse:
        # Custom processing logic
        return super().process(request)
```

### Batch Utilities

```python
from onyx.server.features.video.utils.batch_utils import (
    batch_encode_videos,
    batch_validate_videos,
    batch_filter_videos
)

# Batch operations
encoded_data = batch_encode_videos(video_results)
valid_videos = batch_filter_videos(video_results, lambda v: v.success)
```

### Parallel Utilities

```python
from onyx.server.features.video.utils.parallel_utils import (
    parallel_map,
    HybridParallelProcessor
)

# Custom parallel processing
results = parallel_map(my_function, data, backend=BackendType.PROCESS)

# Hybrid processor
processor = HybridParallelProcessor()
results = processor.map(my_function, data)
```

## 🚨 Error Handling

### Robust Error Handling

```python
# Automatic retry with exponential backoff
processor = create_high_performance_processor(
    max_retries=3,
    retry_delay_seconds=1,
    exponential_backoff=True
)

# Custom error handling
def custom_error_handler(error: Exception, request: VideoClipRequest):
    logger.error(f"Failed to process {request.youtube_url}: {error}")
    return VideoClipResponse(error=str(error))

processor.set_error_handler(custom_error_handler)
```

### Circuit Breaker

```python
# Circuit breaker for external services
processor = create_high_performance_processor(
    circuit_breaker_enabled=True,
    failure_threshold=5,
    recovery_timeout_seconds=60
)
```

## 📈 Best Practices

### 1. Backend Selection
- **I/O Operations**: Use Async or Threading
- **CPU Operations**: Use Multiprocessing or Joblib
- **Large Datasets**: Use Dask or Distributed
- **Unknown Workload**: Use Auto-selection

### 2. Batch Sizing
- Start with small batches (10-50 items)
- Increase batch size based on performance
- Monitor memory usage
- Use chunking for very large datasets

### 3. Error Handling
- Always implement error handlers
- Use circuit breakers for external services
- Implement retry logic with backoff
- Log errors with context

### 4. Monitoring
- Monitor processing time per item
- Track success/failure rates
- Monitor memory usage
- Set up alerts for performance degradation

### 5. Resource Management
- Set appropriate worker limits
- Monitor CPU and memory usage
- Use connection pooling for external services
- Implement graceful shutdown

## 🔧 Troubleshooting

### Common Issues

1. **Memory Issues**
   ```python
   # Reduce batch size
   processor = create_high_performance_processor(chunk_size=100)
   
   # Enable garbage collection
   processor = create_high_performance_processor(enable_gc=True)
   ```

2. **Timeout Issues**
   ```python
   # Increase timeout
   processor = create_high_performance_processor(timeout=120.0)
   
   # Use async for I/O operations
   results = await processor.process_batch_async(requests)
   ```

3. **Performance Issues**
   ```python
   # Profile performance
   stats = processor.get_processing_stats()
   
   # Try different backends
   results = processor.process_batch_parallel(requests, backend=BackendType.PROCESS)
   ```

### Debug Mode

```python
# Enable debug mode
processor = create_high_performance_processor(debug=True)

# Get detailed logs
logs = processor.get_debug_logs()
for log in logs:
    print(f"{log.timestamp}: {log.message}")
```

## 📚 Documentation

- [Parallel Processing Guide](docs/parallel_processing_guide.md) - Comprehensive guide to parallel processing
- [API Reference](docs/api_reference.md) - Complete API documentation
- [Performance Tuning](docs/performance_tuning.md) - Performance optimization guide

## 🤝 Contributing

When contributing to the video processing system:

1. Follow the established patterns
2. Add comprehensive tests
3. Update documentation
4. Run performance benchmarks
5. Ensure backward compatibility

## 📄 License

This project is part of the Onyx server features and follows the same licensing terms. 