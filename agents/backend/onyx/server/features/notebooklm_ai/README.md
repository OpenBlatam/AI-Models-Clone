# NotebookLM AI - FastAPI Application

Production-ready FastAPI application with best practices for data models, path operations, and middleware.

## Features

- ✅ **FastAPI Best Practices**: Following official documentation guidelines
- ✅ **Pydantic v2**: Modern data validation and serialization
- ✅ **Async Operations**: Non-blocking I/O throughout
- ✅ **Security**: OWASP security headers and input validation
- ✅ **Performance**: Connection pooling, caching, and monitoring
- ✅ **Monitoring**: Prometheus metrics and health checks
- ✅ **Docker**: Production-ready containerization
- ✅ **Database**: PostgreSQL with proper schema
- ✅ **Cache**: Redis for performance optimization

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd notebooklm_ai

# Start all services
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f app
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/notebooklm_ai"
export REDIS_URL="redis://localhost:6379"

# Run the application
python run.py
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Generate Single Image
```bash
POST /api/v1/diffusion/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "prompt": "A beautiful sunset over mountains",
  "negative_prompt": "blurry, low quality",
  "pipeline_type": "text_to_image",
  "model_type": "stable-diffusion-v1-5",
  "num_inference_steps": 50,
  "guidance_scale": 7.5,
  "width": 512,
  "height": 512,
  "seed": 42,
  "batch_size": 1
}
```

### Generate Batch Images
```bash
POST /api/v1/diffusion/generate-batch
Content-Type: application/json
Authorization: Bearer <token>

{
  "requests": [
    {
      "prompt": "A beautiful sunset",
      "width": 512,
      "height": 512
    },
    {
      "prompt": "A futuristic city",
      "width": 768,
      "height": 512
    }
  ]
}
```

### Upload Image
```bash
POST /api/v1/diffusion/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <image_file>
```

### Metrics
```bash
GET /metrics
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `notebooklm_ai` | Application name |
| `APP_VERSION` | `1.0.0` | Application version |
| `DEBUG` | `false` | Debug mode |
| `DATABASE_URL` | `postgresql://user:pass@localhost/db` | Database connection URL |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `API_TIMEOUT` | `30` | API timeout in seconds |
| `MAX_CONNECTIONS` | `100` | Maximum database connections |
| `RATE_LIMIT_PER_MINUTE` | `60` | Rate limit per minute |
| `HOST` | `0.0.0.0` | Host to bind to |
| `PORT` | `8000` | Port to bind to |
| `LOG_LEVEL` | `info` | Logging level |

## Architecture

### Data Models
- **Pydantic v2**: Modern validation with computed fields
- **Type Safety**: Full type hints and validation
- **JSON Schema**: Automatic OpenAPI documentation

### Middleware
- **Request ID**: Unique request tracing
- **Logging**: Structured request/response logging
- **Performance**: Prometheus metrics collection
- **Security**: OWASP security headers

### Services
- **Database**: Async PostgreSQL with connection pooling
- **Cache**: Redis for performance optimization
- **Diffusion**: Business logic for image generation

### Dependencies
- **Authentication**: JWT-based authentication
- **Rate Limiting**: Redis-based rate limiting
- **Health Checks**: Comprehensive system monitoring

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality
```bash
# Install development dependencies
pip install black isort flake8 mypy

# Format code
black .
isort .

# Lint code
flake8 .
mypy .
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks
pre-commit run --all-files
```

## Monitoring

### Prometheus Metrics
- HTTP request counts and duration
- Database connection metrics
- Cache hit/miss rates
- Custom business metrics

### Health Checks
- Database connectivity
- Redis connectivity
- GPU availability
- Model loading status

### Logging
- Structured JSON logging
- Request correlation with IDs
- Performance metrics
- Error tracking

## Security

### Headers
- Content-Type Options
- Frame Options
- XSS Protection
- Referrer Policy
- Permissions Policy

### Validation
- Input sanitization
- File type validation
- Size limits
- Rate limiting

### Authentication
- JWT tokens
- Bearer authentication
- User validation

## Performance

### Optimization
- Async/await throughout
- Connection pooling
- Caching strategies
- Parallel processing

### Monitoring
- Request duration tracking
- Memory usage monitoring
- Database query optimization
- Cache performance metrics

## Deployment

### Docker
```bash
# Build image
docker build -t notebooklm_ai .

# Run container
docker run -p 8000:8000 notebooklm_ai
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# Scale application
docker-compose up -d --scale app=3
```

### Production
- Use reverse proxy (nginx)
- Enable HTTPS
- Set up monitoring
- Configure backups
- Use secrets management

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run code quality checks
6. Submit a pull request

## License

This project is licensed under the MIT License. 