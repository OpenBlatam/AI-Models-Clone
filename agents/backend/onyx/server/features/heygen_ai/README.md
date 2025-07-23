# HeyGen AI FastAPI

Advanced AI-powered video generation and processing API built with FastAPI following industry best practices.

## 🚀 Features

- **AI Video Generation**: Create stunning videos from text prompts
- **Video Processing**: Upload and process existing videos with AI enhancement
- **User Management**: Complete authentication and user profile management
- **Real-time Processing**: Background task processing with status tracking
- **Analytics**: Comprehensive video and user analytics
- **RESTful API**: Well-designed REST API with OpenAPI documentation
- **Async Operations**: Non-blocking database and external API operations
- **Security**: JWT authentication, rate limiting, and input validation
- **Monitoring**: Request logging, error handling, and performance metrics

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [API Documentation](#api-documentation)
5. [Project Structure](#project-structure)
6. [Development](#development)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Contributing](#contributing)

## ⚡ Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- FFmpeg (for video processing)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd heygen-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
python main.py
```

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Application
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
WORKERS=1
LOG_LEVEL=info
RELOAD=true

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/heygen_ai

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
HEYGEN_API_KEY=your-heygen-api-key

# File Storage
STORAGE_TYPE=local  # or s3, gcs
STORAGE_PATH=./uploads
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-email-password

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://app.heygen.ai"]
```

## 🔧 Configuration

### Development

```bash
# Start development server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
# Start production server
ENVIRONMENT=production python main.py

# Or use gunicorn with uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Authentication

The API uses Bearer token authentication. Include your token in the Authorization header:

```
Authorization: Bearer your-token-here
```

### Example API Calls

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "accept_terms": true
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# Create a video (with authentication)
curl -X POST "http://localhost:8000/api/v1/videos" \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Amazing AI Video",
    "description": "A beautiful AI-generated video",
    "video_type": "ai_generated",
    "processing_options": {
      "style": "cinematic",
      "duration": 30,
      "background_music": true
    }
  }'
```

## 📁 Project Structure

```
heygen_ai/
├── api/
│   ├── models/                 # Pydantic data models
│   │   ├── __init__.py
│   │   ├── user.py            # User models
│   │   └── video.py           # Video models
│   ├── middleware/            # Custom middleware
│   │   ├── __init__.py
│   │   └── ...
│   └── routes/                # API routes
│       ├── __init__.py
│       ├── base.py            # Base route class
│       ├── users.py           # User routes
│       ├── videos.py          # Video routes
│       └── __main__.py        # Route registration
├── core/                      # Core functionality
│   ├── config.py             # Configuration management
│   ├── database.py           # Database setup
│   └── security.py           # Security utilities
├── services/                  # Business logic
│   ├── user_service.py       # User operations
│   ├── video_service.py      # Video operations
│   └── external_api.py       # External API integration
├── utils/                     # Utility functions
│   ├── validators.py         # Custom validators
│   ├── helpers.py            # Helper functions
│   └── decorators.py         # Custom decorators
├── tests/                     # Test suite
│   ├── test_models.py        # Model tests
│   ├── test_routes.py        # Route tests
│   └── test_services.py      # Service tests
├── alembic/                   # Database migrations
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
└── FASTAPI_BEST_PRACTICES_GUIDE.md  # Best practices guide
```

## 🛠️ Development

### Code Style

This project follows PEP 8 and uses several tools for code quality:

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Features

1. **Models**: Add Pydantic models in `api/models/`
2. **Routes**: Add route handlers in `api/routes/`
3. **Services**: Add business logic in `services/`
4. **Tests**: Add corresponding tests in `tests/`

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and database operations
- **End-to-End Tests**: Test complete user workflows

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
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
      - DATABASE_URL=postgresql+asyncpg://user:password@db/heygen_ai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=heygen_ai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure production database
- [ ] Set up Redis for caching
- [ ] Configure external API keys
- [ ] Set up file storage (S3/GCS)
- [ ] Configure CORS origins
- [ ] Set up monitoring and logging
- [ ] Configure SSL/TLS
- [ ] Set up backup strategy
- [ ] Configure rate limiting
- [ ] Set up CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages
- Add type hints to functions
- Handle errors gracefully

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [FASTAPI_BEST_PRACTICES_GUIDE.md](FASTAPI_BEST_PRACTICES_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Email**: support@heygen.ai

## 🔗 Related Projects

- [HeyGen AI Frontend](https://github.com/your-repo/heygen-ai-frontend)
- [HeyGen AI Mobile App](https://github.com/your-repo/heygen-ai-mobile)
- [HeyGen AI SDK](https://github.com/your-repo/heygen-ai-sdk)

---

Built with ❤️ using FastAPI and following industry best practices. 