# Key Messages Feature - Optimized Version

## Overview

The Key Messages feature has been completely optimized with modern libraries and best practices for high-performance AI-powered message generation and analysis.

## Key Conventions

### 1. Code Style and Structure
- **Type Hints**: All functions must include complete type annotations
- **Async/Await**: Use async/await for all I/O operations
- **Error Handling**: Use structured exception handling with specific error types
- **Logging**: Use structured logging with `structlog` for better observability
- **Documentation**: All public methods must have docstrings with examples

### 2. Performance Optimization
- **Caching**: Multi-layer caching (Redis + Memory) with TTL
- **Connection Pooling**: HTTP clients with connection pooling and limits
- **Rate Limiting**: Implement rate limiting on all endpoints
- **Circuit Breakers**: Use circuit breakers for external API calls
- **Mixed Precision**: Enable mixed precision training when using GPU

### 3. ML and Deep Learning
- **Gradient Accumulation**: Use gradient accumulation for large batch sizes
- **Distributed Training**: Support for DistributedDataParallel (DDP)
- **Mixed Precision**: Automatic mixed precision with `torch.cuda.amp`
- **Model Optimization**: Use optimized models from Hugging Face
- **Experiment Tracking**: Integration with TensorBoard and Weights & Biases

### 4. Monitoring and Observability
- **Prometheus Metrics**: Comprehensive metrics for all operations
- **Health Checks**: Regular health checks for all components
- **Profiling**: Code profiling with cProfile and py-spy
- **Structured Logging**: JSON-formatted logs with correlation IDs

### 5. Configuration Management
- **Environment Variables**: Use pydantic-settings for configuration
- **Validation**: Validate all configuration values at startup
- **Defaults**: Provide sensible defaults for all settings
- **Environment-Specific**: Different configs for dev/staging/prod

### 6. Testing Conventions
- **Async Testing**: Use pytest-asyncio for async test functions
- **Fixtures**: Reusable test fixtures for common setup
- **Mocking**: Mock external dependencies in tests
- **Performance Testing**: Include performance benchmarks
- **Coverage**: Maintain high test coverage (>90%)

### 7. API Design
- **RESTful**: Follow REST conventions for API endpoints
- **Rate Limiting**: Implement rate limiting per endpoint
- **Error Responses**: Consistent error response format
- **Validation**: Use Pydantic for request/response validation
- **Documentation**: Auto-generated API documentation with OpenAPI

### 8. Database and Caching
- **Redis**: Use Redis for distributed caching
- **Connection Management**: Proper connection pooling and cleanup
- **TTL**: Set appropriate TTL for cached data
- **Fallbacks**: Graceful fallbacks when cache is unavailable

### 9. Security
- **Input Validation**: Validate all user inputs
- **Rate Limiting**: Prevent abuse with rate limiting
- **CORS**: Configure CORS appropriately
- **API Keys**: Support for API key authentication
- **HTTPS**: Use HTTPS in production

### 10. Deployment
- **Docker**: Containerized deployment
- **Health Checks**: Kubernetes health checks
- **Resource Limits**: Set appropriate resource limits
- **Monitoring**: Prometheus and Grafana integration
- **Logging**: Centralized logging with ELK stack

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Redis Cache    │    │   LLM Service   │
│                 │    │                 │    │                 │
│ - Rate Limiting │◄──►│ - Distributed   │    │ - OpenAI        │
│ - Validation    │    │ - TTL           │    │ - Anthropic     │
│ - Metrics       │    │ - Persistence   │    │ - Local Models  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Optimized      │    │  Background     │    │  Experiment     │
│  Service        │    │  Tasks (ARQ)    │    │  Tracking       │
│                 │    │                 │    │                 │
│ - Mixed Prec.   │    │ - Async Queue   │    │ - TensorBoard   │
│ - Circuit Br.   │    │ - Job Scheduler │    │ - Weights & Biases│
│ - Profiling     │    │ - Retry Logic   │    │ - Metrics       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Performance Optimizations

### 1. Caching Strategy
- **L1 Cache**: In-memory cache for frequently accessed data
- **L2 Cache**: Redis cache for distributed access
- **Cache Keys**: MD5 hash of request parameters
- **TTL**: Configurable TTL per cache level

### 2. HTTP Client Optimization
- **Connection Pooling**: Reuse connections with limits
- **HTTP/2**: Enable HTTP/2 for better performance
- **Timeouts**: Configurable timeouts per request type
- **Retry Logic**: Exponential backoff with circuit breaker

### 3. ML Model Optimization
- **Mixed Precision**: FP16 for faster inference
- **Model Caching**: Cache loaded models in memory
- **Batch Processing**: Efficient batch processing
- **GPU Memory**: Optimize GPU memory usage

### 4. Database Optimization
- **Connection Pooling**: Efficient connection management
- **Query Optimization**: Optimized queries with indexes
- **Async Operations**: Non-blocking database operations
- **Connection Limits**: Prevent connection exhaustion

## Monitoring and Metrics

### Prometheus Metrics
- `key_messages_requests_total`: Total request count
- `key_messages_request_duration_seconds`: Request duration
- `key_messages_cache_hit_ratio`: Cache hit ratio
- `key_messages_active_connections`: Active connections
- `key_messages_gpu_memory_usage_mb`: GPU memory usage

### Health Checks
- Redis connectivity
- HTTP client status
- System resources (CPU, Memory)
- ML model availability

### Logging
- Structured JSON logs
- Correlation IDs for request tracking
- Performance metrics in logs
- Error context and stack traces

## Configuration

### Environment Variables
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_MAX_CONNECTIONS=20

# HTTP Configuration
HTTP_TIMEOUT_SECONDS=30
HTTP_MAX_CONNECTIONS=100

# Cache Configuration
CACHE_TTL_SECONDS=86400
CACHE_MEMORY_SIZE=1000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute

# ML Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
LLM_MAX_TOKENS=1000

# Monitoring
MONITORING_PROMETHEUS_ENABLED=true
MONITORING_STRUCTURED_LOGGING=true

# Performance
PERFORMANCE_MAX_BATCH_SIZE=50
PERFORMANCE_CONCURRENT_REQUESTS=10
```

## Usage Examples

### Basic Message Generation
```python
from onyx.server.features.key_messages.service import OptimizedKeyMessageService
from onyx.server.features.key_messages.models import KeyMessageRequest, MessageType, MessageTone

# Initialize service
async with OptimizedKeyMessageService() as service:
    # Generate message
request = KeyMessageRequest(
        message="Our new product revolutionizes the industry",
    message_type=MessageType.MARKETING,
    tone=MessageTone.PROFESSIONAL,
        keywords=["innovation", "revolution", "technology"]
)

response = await service.generate_response(request)
    print(response.data.response)
```

### Batch Processing
```python
# Batch processing with progress tracking
requests = [KeyMessageRequest(...) for _ in range(100)]
batch_request = BatchKeyMessageRequest(messages=requests, batch_size=50)

response = await service.generate_batch(batch_request)
print(f"Processed: {response.total_processed}")
print(f"Failed: {response.failed_count}")
```

### Health Monitoring
```python
# Check service health
health = await service.health_check()
print(f"Status: {health['status']}")
print(f"Redis: {health['checks']['redis']}")
print(f"System: {health['checks']['system']}")
```

## Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=onyx.server.features.key_messages --cov-report=html

# Run performance tests
pytest tests/ -m "performance" --benchmark-only

# Run profiling
python -m cProfile -o profile.prof test_integration.py
```

### Performance Benchmarks
```bash
# Run benchmarks
pytest test_integration.py::TestPerformanceOptimizations -v

# Memory profiling
python -m memory_profiler test_integration.py

# Line profiling
kernprof -l -v test_integration.py
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "onyx.server.features.key_messages.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: key-messages
spec:
  replicas: 3
  selector:
    matchLabels:
      app: key-messages
  template:
    metadata:
      labels:
        app: key-messages
    spec:
      containers:
      - name: key-messages
        image: key-messages:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## Troubleshooting

### Common Issues

1. **Redis Connection Issues**
   - Check Redis server status
   - Verify connection URL
   - Check network connectivity

2. **High Memory Usage**
   - Monitor cache size
   - Check for memory leaks
   - Adjust batch sizes

3. **Slow Response Times**
   - Check cache hit ratio
   - Monitor external API latency
   - Review rate limiting settings

4. **GPU Memory Issues**
   - Enable mixed precision
   - Reduce batch sizes
   - Monitor GPU memory usage

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Enable profiling
export KEY_MESSAGES_ENABLE_PROFILING=true

# Enable detailed metrics
export MONITORING_PROMETHEUS_ENABLED=true
```

## Contributing

1. Follow the coding conventions
2. Add tests for new features
3. Update documentation
4. Run performance benchmarks
5. Check code coverage

## License

This project is licensed under the MIT License. 