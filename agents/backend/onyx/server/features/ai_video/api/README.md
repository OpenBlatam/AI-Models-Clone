# AI Video Generation API

A scalable FastAPI application for AI video generation using the latest technologies and best practices.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Async Processing**: Background task processing for video generation
- **Rate Limiting**: Built-in rate limiting and quota management
- **Caching**: Redis-based caching for improved performance
- **Authentication**: JWT-based authentication system
- **Monitoring**: Comprehensive metrics and health checks
- **Security**: Security headers and input validation
- **Documentation**: Auto-generated OpenAPI documentation

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r api/requirements.txt

# Start Redis (required for caching and job management)
redis-server

# Run the API server
python -m api.fastapi_app
```

### Usage

1. **Start the server**:
   ```bash
   uvicorn api.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Health check**:
   ```bash
   curl http://localhost:8000/health
   ```

## API Endpoints

### Video Generation

#### Generate Video
```http
POST /api/v1/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "prompt": "A beautiful sunset over the ocean",
  "num_frames": 16,
  "height": 512,
  "width": 512,
  "fps": 8,
  "guidance_scale": 7.5,
  "num_inference_steps": 50
}
```

#### Get Job Status
```http
GET /api/v1/job/{job_id}
Authorization: Bearer <token>
```

#### Download Video
```http
GET /api/v1/video/{video_id}
Authorization: Bearer <token>
```

#### Batch Generation
```http
POST /api/v1/batch
Content-Type: application/json
Authorization: Bearer <token>

{
  "requests": [
    {
      "prompt": "Video 1",
      "num_frames": 16
    },
    {
      "prompt": "Video 2", 
      "num_frames": 24
    }
  ]
}
```

#### List User Jobs
```http
GET /api/v1/jobs?status=completed&limit=10&offset=0
Authorization: Bearer <token>
```

#### Cancel Job
```http
DELETE /api/v1/job/{job_id}
Authorization: Bearer <token>
```

### Health Checks

#### Basic Health Check
```http
GET /health
```

#### Readiness Check
```http
GET /health/ready
```

#### Liveness Check
```http
GET /health/live
```

### Admin Endpoints

#### System Metrics
```http
GET /admin/metrics
Authorization: Bearer <admin_token>
```

#### User Quota
```http
GET /admin/users/{user_id}/quota
Authorization: Bearer <admin_token>
```

#### Model Configuration
```http
GET /admin/model/config
Authorization: Bearer <admin_token>
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=24

# Rate Limiting
RATE_LIMIT=100
RATE_LIMIT_WINDOW=3600

# Quota
DAILY_QUOTA=50
MONTHLY_QUOTA=1000

# Model
MODEL_NAME=text-to-video-ms-1.7b
MODEL_CACHE_DIR=./models
```

### Configuration File

Create `config.yaml`:

```yaml
app:
  name: "AI Video Generation API"
  version: "1.0.0"
  debug: false

database:
  url: "postgresql+asyncpg://user:pass@localhost/dbname"
  pool_size: 20
  max_overflow: 30

redis:
  url: "redis://localhost:6379/0"
  pool_size: 10

security:
  secret_key: "your-secret-key"
  jwt_algorithm: "HS256"
  jwt_expiration_hours: 24

rate_limiting:
  requests_per_hour: 100
  burst_size: 10

quota:
  daily_limit: 50
  monthly_limit: 1000

model:
  name: "text-to-video-ms-1.7b"
  cache_dir: "./models"
  max_frames: 64
  max_resolution: "1024x1024"

monitoring:
  enable_metrics: true
  enable_tracing: true
  log_level: "INFO"
```

## Architecture

### Components

1. **FastAPI App** (`fastapi_app.py`): Main application with middleware and routing
2. **Models** (`models.py`): Pydantic models for request/response validation
3. **Dependencies** (`dependencies.py`): Dependency injection and business logic
4. **Middleware** (`middleware.py`): Custom middleware for logging, security, etc.
5. **Routes** (`routes.py`): API endpoint definitions

### Middleware Stack

1. **RequestLoggingMiddleware**: Comprehensive request/response logging
2. **MetricsMiddleware**: API metrics collection
3. **RateLimitMiddleware**: Rate limiting per user
4. **CacheMiddleware**: Response caching
5. **SecurityMiddleware**: Security headers
6. **PerformanceMiddleware**: Performance monitoring
7. **CORSMiddleware**: Cross-origin resource sharing
8. **GZipMiddleware**: Response compression
9. **TrustedHostMiddleware**: Host validation

### Background Processing

The API uses FastAPI's `BackgroundTasks` for video generation:

```python
@api_router.post("/generate")
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(process_video_generation, request, job_id, user['user_id'])
    return VideoGenerationResponse(job_id=job_id, status="queued")
```

## Security

### Authentication

JWT-based authentication with the following features:

- Token expiration
- Refresh tokens
- Role-based access control
- Secure token storage

### Rate Limiting

Per-user rate limiting with:

- Configurable limits
- Burst protection
- Redis-based storage
- Automatic cleanup

### Input Validation

Comprehensive input validation using Pydantic:

- Request model validation
- Custom validators
- Error messages
- Type checking

### Security Headers

Automatic security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `Referrer-Policy`

## Monitoring

### Metrics

The API collects various metrics:

- Request counts by endpoint
- Response status codes
- Processing times
- Error rates
- User activity

### Health Checks

Multiple health check endpoints:

- Basic health check
- Readiness check (dependencies)
- Liveness check (application)

### Logging

Structured logging with:

- Request/response logging
- Error tracking
- Performance metrics
- User activity

## Performance

### Caching

Redis-based caching for:

- API responses
- User sessions
- Job status
- Model outputs

### Async Processing

- Async/await throughout
- Background task processing
- Non-blocking I/O
- Connection pooling

### Optimization

- Response compression
- Efficient serialization
- Memory management
- Database optimization

## Testing

### Unit Tests

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=api tests/
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db/dbname
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=dbname
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  redis:
    image: redis:7-alpine
```

### Production

For production deployment:

1. Use a production ASGI server (Gunicorn + Uvicorn)
2. Set up reverse proxy (Nginx)
3. Configure SSL/TLS
4. Set up monitoring and alerting
5. Use environment-specific configurations
6. Implement proper logging
7. Set up backup and recovery

## Development

### Code Style

The project uses:

- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

```bash
# Format code
black api/

# Sort imports
isort api/

# Lint code
flake8 api/

# Type check
mypy api/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License. 